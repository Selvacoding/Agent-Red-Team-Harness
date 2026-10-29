from types import SimpleNamespace

import pytest

from targets.rag import agent as rag_agent_module
from targets.rag.agent import RAGAgent


@pytest.fixture
def agent_dependencies(monkeypatch):
    """Mock indexing, retrieval, and Ollama so tests run locally and deterministically."""
    indexed_documents = []
    retrieved_documents = []

    def fake_add_document_to_vector_store(
        document_id,
        path,
        chunk_size=200,
        overlap=50,
    ):
        indexed_documents.append(
            {
                "document_id": document_id,
                "path": path,
            }
        )

    def fake_retrieve(query):
        return retrieved_documents

    def fake_chat(**kwargs):
        return SimpleNamespace(
            message=SimpleNamespace(
                content="Customers can request deletion through support."
            )
        )

    monkeypatch.setattr(
        rag_agent_module,
        "add_document_to_vector_store",
        fake_add_document_to_vector_store,
    )
    monkeypatch.setattr(rag_agent_module, "retrieve", fake_retrieve)
    monkeypatch.setattr(rag_agent_module, "chat", fake_chat)

    return indexed_documents, retrieved_documents


def test_agent_indexes_the_supplied_document(agent_dependencies):
    indexed_documents, _ = agent_dependencies

    RAGAgent(
        document_id="customer-policy",
        document_path="targets/rag/data/customer_policy.md",
    )

    assert indexed_documents == [
        {
            "document_id": "customer-policy",
            "path": "targets/rag/data/customer_policy.md",
        }
    ]


def test_run_returns_response_and_retrieved_documents(agent_dependencies):
    _, retrieved_documents = agent_dependencies

    retrieved_documents.extend(
        [
            {
                "id": "chunk-1",
                "content": "Customers can request deletion through support.",
                "metadata": {"source": "customer-policy"},
                "score": 0.95,
            }
        ]
    )

    agent = RAGAgent(
        document_id="customer-policy",
        document_path="targets/rag/data/customer_policy.md",
    )

    result = agent.run("What is the customer deletion policy?")

    assert result.response == (
        "Customers can request deletion through support."
    )
    assert result.rag_execution.query == (
        "What is the customer deletion policy?"
    )
    assert result.rag_execution.retrieved_documents == retrieved_documents


def test_run_passes_user_query_to_retriever(
    agent_dependencies,
    monkeypatch,
):
    _, _ = agent_dependencies
    received_queries = []

    def fake_retrieve(query):
        received_queries.append(query)
        return []

    monkeypatch.setattr(rag_agent_module, "retrieve", fake_retrieve)

    agent = RAGAgent(
        document_id="customer-policy",
        document_path="targets/rag/data/customer_policy.md",
    )

    agent.run("How can I delete my account?")

    assert received_queries == ["How can I delete my account?"]
