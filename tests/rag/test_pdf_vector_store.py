import pytest
import pymupdf

import targets.rag.vector_store as vs


def fake_embedding(text):
    """Deterministic embeddings for isolated vector-store tests."""
    text = text.lower()

    if "deletion" in text or "administrator" in text:
        return [0.0, 1.0, 0.0]

    if "support" in text or "legitimate" in text:
        return [1.0, 0.0, 0.0]

    return [0.0, 0.0, 1.0]


@pytest.fixture(autouse=True)
def isolate_vector_store(monkeypatch):
    monkeypatch.setattr(vs, "create_embedding", fake_embedding)
    vs.vector_store.clear()

    yield

    vs.vector_store.clear()


def create_policy_pdf(path):
    """Create a two-page policy PDF in pytest's temporary directory."""
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Customer Support Policy\n\n"
        "Customer information can be retrieved only "
        "for legitimate support requests.",
    )

    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Customer Deletion Policy\n\n"
        "Customer deletion requires explicit "
        "authorization from an administrator.",
    )

    document.save(str(path))
    document.close()


def test_add_pdf_to_vector_store_indexes_pages(tmp_path):
    pdf_path = tmp_path / "customer_policy.pdf"
    create_policy_pdf(pdf_path)

    vs.add_document_to_vector_store(
        document_id="customer-policy-pdf",
        path=str(pdf_path),
        chunk_size=200,
        overlap=20,
    )

    assert len(vs.vector_store) == 2

    assert all(
        item["document_id"] == "customer-policy-pdf"
        for item in vs.vector_store
    )

    assert {item["metadata"]["page"] for item in vs.vector_store} == {1, 2}

    assert all(
        item["metadata"]["source"] == "customer_policy.pdf"
        for item in vs.vector_store
    )

    assert all(item["embedding"] for item in vs.vector_store)


def test_pdf_chunks_have_unique_ids(tmp_path):
    pdf_path = tmp_path / "customer_policy.pdf"
    create_policy_pdf(pdf_path)

    vs.add_document_to_vector_store(
        document_id="customer-policy-pdf",
        path=str(pdf_path),
        chunk_size=200,
        overlap=20,
    )

    ids = [item["id"] for item in vs.vector_store]

    assert len(ids) == len(set(ids))


def test_search_retrieves_customer_deletion_policy(tmp_path):
    pdf_path = tmp_path / "customer_policy.pdf"
    create_policy_pdf(pdf_path)

    vs.add_document_to_vector_store(
        document_id="customer-policy-pdf",
        path=str(pdf_path),
        chunk_size=200,
        overlap=20,
    )

    results = vs.search(
        "What is the customer deletion policy?",
        top_k=2,
    )

    assert results
    assert any(
        "Customer Deletion Policy" in result["content"]
        for result in results
    )

    deletion_result = next(
        result
        for result in results
        if "Customer Deletion Policy" in result["content"]
    )

    assert deletion_result["metadata"]["page"] == 2
    assert deletion_result["document_id"] == "customer-policy-pdf"
    assert "score" in deletion_result


def test_search_returns_no_results_for_empty_vector_store():
    results = vs.search("What is the customer deletion policy?")

    assert results == []
