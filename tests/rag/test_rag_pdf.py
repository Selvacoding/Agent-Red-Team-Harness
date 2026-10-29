
from pathlib import Path
from types import SimpleNamespace

import fitz
import pytest

from targets.rag import agent as rag_agent_module
from targets.rag.agent import RAGAgent
from targets.rag.vector_store import vector_store


@pytest.fixture
def pdf_file(tmp_path):
    """Create a temporary PDF containing customer deletion policy text."""
    path = tmp_path / "customer_policy.pdf"

    with fitz.open() as pdf:
        page = pdf.new_page()
        page.insert_text(
            (72, 72),
            "Customer Deletion Policy\n"
            "Customers can request account deletion by contacting support.",
        )
        pdf.save(path)

    return path


@pytest.fixture
def mocked_agent_services(monkeypatch):
    """Mock only embeddings, retrieval, and the LLM response."""
    monkeypatch.setattr(
        "targets.rag.vector_store.create_embedding",
        lambda text: [1.0, 0.0, 0.0],
    )

    retrieved_documents = []

    def fake_retrieve(query):
        return retrieved_documents

    def fake_chat(**kwargs):
        return SimpleNamespace(
            message=SimpleNamespace(
                content="Customers can request deletion through support."
            )
        )

    monkeypatch.setattr(rag_agent_module, "retrieve", fake_retrieve)
    monkeypatch.setattr(rag_agent_module, "chat", fake_chat)

    yield retrieved_documents

    vector_store.clear()


def test_agent_indexes_pdf_with_page_and_source_metadata(
    pdf_file,
    mocked_agent_services,
):
    RAGAgent(
        document_id="customer-policy-pdf",
        document_path=str(pdf_file),
    )

    assert vector_store
    assert all(
        chunk["document_id"] == "customer-policy-pdf"
        for chunk in vector_store
    )
    assert any(
        chunk["metadata"].get("page") == 1
        for chunk in vector_store
    )
    assert any(
        chunk["metadata"].get("source") == pdf_file.name
        for chunk in vector_store
    )
    assert any(
        "Customers can request account deletion"
        in chunk["content"]
        for chunk in vector_store
    )


def test_agent_returns_response_for_pdf_question(
    pdf_file,
    mocked_agent_services,
):
    retrieved_documents = mocked_agent_services
    expected_documents = [
        {
            "id": "customer-policy-pdf_chunk_0",
            "document_id": "customer-policy-pdf",
            "content": (
                "Customers can request account deletion "
                "by contacting support."
            ),
            "metadata": {
                "source": pdf_file.name,
                "page": 1,
            },
            "score": 0.95,
        }
    ]
    retrieved_documents.extend(expected_documents)

    agent = RAGAgent(
        document_id="customer-policy-pdf",
        document_path=str(pdf_file),
    )

    result = agent.run("What is the customer deletion policy?")

    assert result.response == (
        "Customers can request deletion through support."
    )
    assert result.rag_execution.query == (
        "What is the customer deletion policy?"
    )
    assert result.rag_execution.retrieved_documents == expected_documents


def test_agent_rejects_unsupported_pdf_path(
    tmp_path,
    mocked_agent_services,
):
    unsupported_path = tmp_path / "policy.docx"
    unsupported_path.write_text("Not a PDF", encoding="utf-8")

    with pytest.raises(ValueError):
        RAGAgent(
            document_id="unsupported-policy",
            document_path=str(unsupported_path),
        )
