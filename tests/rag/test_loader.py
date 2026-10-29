import pytest

from targets.rag.loader import load_text_file
from targets.rag.documents import load_document_from_file


def test_load_text_file_reads_content(tmp_path):
    file_path = tmp_path / "policy.md"
    content = "# Customer Policy\n\nCustomer lookup requires a valid request."

    file_path.write_text(content, encoding="utf-8")

    assert load_text_file(str(file_path)) == content


def test_load_text_file_supports_unicode(tmp_path):
    file_path = tmp_path / "unicode.txt"
    content = "Customer support – வாடிக்கையாளர் சேவை – café"

    file_path.write_text(content, encoding="utf-8")

    assert load_text_file(str(file_path)) == content


def test_load_text_file_handles_empty_file(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("", encoding="utf-8")

    assert load_text_file(str(file_path)) == ""


def test_load_text_file_raises_for_missing_file(tmp_path):
    file_path = tmp_path / "missing.md"

    with pytest.raises(FileNotFoundError):
        load_text_file(str(file_path))


def test_load_document_from_file_wraps_loaded_content(tmp_path):
    file_path = tmp_path / "policy.md"
    content = "# Support Policy\n\nCustomer data requires authorization."

    file_path.write_text(content, encoding="utf-8")

    document = load_document_from_file("test-policy", str(file_path))

    assert document["id"] == "test-policy"
    assert document["content"] == content
