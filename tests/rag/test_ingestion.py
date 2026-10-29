from pathlib import Path

import pytest

from targets.rag.ingestion import (
    ingest_document,
    ingest_pdf_document,
    ingest_text_content,
    ingest_text_document,
)


def test_ingest_text_content_preserves_document_metadata():
    chunks = ingest_text_content(
        document_id="policy-1",
        content="# Security Policy\n\nOnly administrators can delete customers.",
        chunk_size=200,
        overlap=20,
    )

    assert len(chunks) == 1

    chunk = chunks[0]
    assert chunk["id"] == "policy-1-chunk-0"
    assert chunk["document_id"] == "policy-1"
    assert chunk["content"] == "Only administrators can delete customers."
    assert chunk["metadata"] == {
        "source": "policy-1",
        "section": "Security Policy",
        "chunk_index": 0,
    }


def test_ingest_text_document_matches_text_content():
    content = "# Lookup Policy\n\nSupport agents can look up customer records."

    direct_result = ingest_text_content("lookup-1", content)
    document_result = ingest_text_document("lookup-1", content)

    assert document_result == direct_result


def test_ingest_empty_text_returns_no_chunks():
    assert ingest_text_content("empty-policy", "") == []


@pytest.mark.parametrize(
    ("extension", "content"),
    [
        (".md", "# Access Policy\n\nAdmin access is required."),
        (".txt", "Admin access is required."),
    ],
)
def test_ingest_document_reads_text_files(tmp_path, extension, content):
    path = tmp_path / f"policy{extension}"
    path.write_text(content, encoding="utf-8")

    chunks = ingest_document(
        document_id="file-policy",
        path=str(path),
    )

    assert len(chunks) == 1
    assert chunks[0]["document_id"] == "file-policy"
    assert chunks[0]["metadata"]["source"] == "file-policy"
    assert chunks[0]["metadata"]["chunk_index"] == 0
    assert "Admin access is required." in chunks[0]["content"]


def test_ingest_document_rejects_unsupported_file_type(tmp_path):
    path = tmp_path / "policy.docx"
    path.write_text("Policy content", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported document type: .docx"):
        ingest_document("policy-1", str(path))


def test_ingest_document_rejects_missing_text_file(tmp_path):
    path = tmp_path / "missing.md"

    with pytest.raises(FileNotFoundError):
        ingest_document("policy-1", str(path))


def test_ingest_pdf_document_preserves_page_metadata(tmp_path):
    pymupdf = pytest.importorskip("pymupdf")

    pdf_path = tmp_path / "policy.pdf"
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Customer Support Policy\n\n"
        "Customer records may be accessed for legitimate support requests.",
    )

    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Customer Deletion Policy\n\n"
        "Only an administrator may authorize customer deletion.",
    )

    document.save(str(pdf_path))
    document.close()

    chunks = ingest_pdf_document(
        document_id="pdf-policy",
        path=str(pdf_path),
        chunk_size=200,
        overlap=20,
    )

    assert len(chunks) >= 2
    assert all(chunk["document_id"] == "pdf-policy" for chunk in chunks)

    assert [chunk["metadata"]["page"] for chunk in chunks] == [
        1,
        2,
    ]

    for index, chunk in enumerate(chunks):
        assert chunk["id"] == f"pdf-policy-chunk-{index}"
        assert chunk["metadata"]["source"] == pdf_path.name
        assert chunk["metadata"]["chunk_index"] == index
        assert chunk["metadata"]["section"]


def test_ingest_document_dispatches_pdf_files(tmp_path):
    pymupdf = pytest.importorskip("pymupdf")

    pdf_path = tmp_path / "dispatch.pdf"
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Dispatch PDF ingestion test.")
    document.save(str(pdf_path))
    document.close()

    chunks = ingest_document(
        document_id="dispatch-policy",
        path=str(pdf_path),
    )

    assert chunks
    assert chunks[0]["document_id"] == "dispatch-policy"
    assert chunks[0]["metadata"]["page"] == 1
