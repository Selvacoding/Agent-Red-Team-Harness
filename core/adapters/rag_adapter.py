import os

from core.adapters.base import AgentAdapter
from core.models.agent import AgentResult
from targets.rag.agent import RAGAgent
from targets.rag.storage import ChromaVectorStore


class RAGAgentAdapter(AgentAdapter):
    """RAG adapter with opt-in persistent Chroma storage."""

    def __init__(self):
        backend = os.getenv("RAG_STORAGE_BACKEND", "memory").lower()
        self.persistent_store = None

        if backend == "chroma":
            self.persistent_store = ChromaVectorStore(
                collection_name=os.getenv(
                    "RAG_CHROMA_COLLECTION",
                    "rag-agent",
                ),
                persist_directory=os.getenv(
                    "RAG_CHROMA_PATH",
                    ".local-data/chroma",
                ),
            )
        elif backend != "memory":
            raise ValueError(
                "RAG_STORAGE_BACKEND must be 'memory' or 'chroma'"
            )

        self.agent = RAGAgent(
            document_id="customer-policy",
            document_path="targets/rag/data/customer_policy.md",
            persistent_store=self.persistent_store,
        )

    def run(self, user_input: str) -> AgentResult:
        return self.agent.run(user_input)
