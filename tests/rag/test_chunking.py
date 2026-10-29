import pytest

from targets.rag.chunking import chunk_text, split_large_paragraph


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == "" or chunk_text("") == []


def test_whitespace_only_text_returns_no_chunks():
    assert chunk_text("   \n\n   ") == []


def test_short_text_produces_one_chunk():
    result = chunk_text("Customer deletion requires admin approval.")

    assert len(result) == 1
    assert result[0]["content"] == "Customer deletion requires admin approval."
    assert result[0]["section"] == "Uncategorized"


def test_chunk_preserves_section_heading():
    result = chunk_text(
        "# Deletion Policy\n\nOnly administrators can delete customers."
    )

    assert len(result) == 1
    assert result[0]["section"] == "Deletion Policy"
    assert "Only administrators can delete customers." in result[0]["content"]


def test_multiple_sections_remain_separate():
    result = chunk_text(
        "# Deletion Policy\n\nOnly administrators can delete customers."
        "\n\n# Lookup Policy\n\nSupport agents can look up customers.",
        chunk_size=200,
    )

    assert len(result) == 2
    assert result[0]["section"] == "Deletion Policy"
    assert result[1]["section"] == "Lookup Policy"


def test_long_paragraph_is_split_into_chunks():
    text = " ".join(f"word{i}" for i in range(20))

    result = chunk_text(text, chunk_size=25, overlap=0)

    assert len(result) > 1
    assert all(len(chunk["content"]) <= 25 for chunk in result)


def test_split_large_paragraph_preserves_all_words():
    paragraph = "alpha beta gamma delta epsilon zeta"

    chunks = split_large_paragraph(paragraph, chunk_size=12)

    reconstructed_words = " ".join(chunks).split()

    assert reconstructed_words == paragraph.split()


def test_chunk_text_rejects_nonpositive_chunk_size():
    with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
        chunk_text("some text", chunk_size=0)


@pytest.mark.parametrize("overlap", [-1, 10])
def test_chunk_text_rejects_invalid_overlap(overlap):
    with pytest.raises(ValueError, match="overlap must be between"):
        chunk_text("some text", chunk_size=10, overlap=overlap)


def test_chunk_size_boundary():
    text = "12345 67890"

    result = chunk_text(text, chunk_size=len(text), overlap=0)

    assert len(result) == 1
    assert result[0]["content"] == text
