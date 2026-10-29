import pytest
import pymupdf

from targets.rag.pdf_loader import load_pdf, chunk_pdf_pages


def create_pdf(path, page_texts):
    """Create a temporary PDF containing the supplied page text."""
    document = pymupdf.open()

    for text in page_texts:
        page = document.new_page()
        if text:
            page.insert_text((72, 72), text)

    document.save(str(path))
    document.close()


def test_load_pdf_extracts_text_and_uses_one_based_page_numbers(tmp_path):
    pdf_path = tmp_path / "policy.pdf"
    create_pdf(
        pdf_path,
        [
            "Customer Support Policy\nCustomer lookup is permitted.",
            "Customer Deletion Policy\nAdministrator approval is required.",
        ],
    )

    pages = load_pdf(str(pdf_path))

    assert len(pages) == 2
    assert [page["page"] for page in pages] == [1, 2]
    assert all(page["source"] == "policy.pdf" for page in pages)
    assert "Customer Support Policy" in pages[0]["text"]
    assert "Customer Deletion Policy" in pages[1]["text"]


def test_load_pdf_returns_empty_text_for_blank_page(tmp_path):
    pdf_path = tmp_path / "blank.pdf"
    create_pdf(pdf_path, [""])

    pages = load_pdf(str(pdf_path))

    assert len(pages) == 1
    assert pages[0]["page"] == 1
    assert pages[0]["text"].strip() == ""


def test_chunk_pdf_pages_preserves_page_and_source_metadata():
    pages = [
        {
            "page": 1,
            "source": "policy.pdf",
            "text": "# Support Policy\n\nCustomer lookup is permitted.",
        },
        {
            "page": 2,
            "source": "policy.pdf",
            "text": "# Deletion Policy\n\nAdministrator approval is required.",
        },
    ]

    chunks = chunk_pdf_pages(pages, chunk_size=200, overlap=20)

    assert len(chunks) == 2
    assert chunks[0]["metadata"] == {
        "source": "policy.pdf",
        "page": 1,
        "chunk_index": 0,
    }
    assert chunks[1]["metadata"] == {
        "source": "policy.pdf",
        "page": 2,
        "chunk_index": 0,
    }
    assert chunks[0]["section"] == "Support Policy"
    assert chunks[1]["section"] == "Deletion Policy"


def test_chunk_pdf_pages_does_not_merge_content_across_pages():
    pages = [
        {"page": 1, "source": "policy.pdf", "text": "First page content."},
        {"page": 2, "source": "policy.pdf", "text": "Second page content."},
    ]

    chunks = chunk_pdf_pages(pages)

    assert len(chunks) == 2
    assert "First page content." in chunks[0]["content"]
    assert "Second page content." in chunks[1]["content"]
    assert chunks[0]["metadata"]["page"] == 1
    assert chunks[1]["metadata"]["page"] == 2


def test_chunk_pdf_pages_skips_empty_pages():
    pages = [
        {"page": 1, "source": "policy.pdf", "text": ""},
        {"page": 2, "source": "policy.pdf", "text": "Useful policy content."},
    ]

    chunks = chunk_pdf_pages(pages)

    assert len(chunks) == 1
    assert chunks[0]["metadata"]["page"] == 2
    assert chunks[0]["content"] == "Useful policy content."


def test_load_pdf_raises_for_missing_file(tmp_path):
    missing_path = tmp_path / "missing.pdf"

    with pytest.raises((FileNotFoundError, RuntimeError, ValueError)):
        load_pdf(str(missing_path))


def test_load_pdf_raises_for_malformed_pdf(tmp_path):
    malformed_path = tmp_path / "malformed.pdf"
    malformed_path.write_text("This is not a PDF.", encoding="utf-8")

    with pytest.raises((RuntimeError, ValueError)):
        load_pdf(str(malformed_path))
