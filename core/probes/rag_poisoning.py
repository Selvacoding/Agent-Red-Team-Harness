
from uuid import uuid4

from core.adapters.base import AgentAdapter
from core.models.agent import AgentResult
from core.probes.base import Probe
from targets.rag.documents import reset_documents
from targets.rag.ingestion import ingest_text_content
from targets.rag.poison import poison_document
from targets.rag.vector_store import reset_vector_store


class RAGPoisoningProbe(Probe):
    attack_type = "rag_poisoning"

    def __init__(
        self,
        poisoned_content: str,
        query: str,
        expected_behavior: str,
    ):
        self.poisoned_content = poisoned_content
        self.query = query
        self.expected_behavior = expected_behavior

    def run(self, adapter: AgentAdapter) -> AgentResult:
        agent = getattr(adapter, "agent", None)

        # Generic Mock adapters fabricate attributes, so only trust a store
        # explicitly present on the agent's instance dictionary.
        agent_attributes = getattr(agent, "__dict__", {})
        persistent_store = agent_attributes.get("persistent_store")

        supports_persistence = (
            persistent_store is not None
            and callable(getattr(persistent_store, "add_chunks", None))
            and callable(getattr(persistent_store, "delete_document", None))
        )

        if not supports_persistence:
            # Preserve the existing in-memory experiment workflow.
            reset_documents()
            reset_vector_store()
            poison_document(self.poisoned_content)
            return adapter.run(self.query)

        # Use a unique ID to isolate each poisoning experiment.
        poison_id = f"poisoned-document-{uuid4().hex}"

        try:
            chunks = ingest_text_content(
                document_id=poison_id,
                content=self.poisoned_content,
            )

            for chunk in chunks:
                chunk["metadata"] = {
                    **chunk.get("metadata", {}),
                    "poisoned": True,
                    "experiment_document_id": poison_id,
                }

            persistent_store.add_chunks(chunks)
            return adapter.run(self.query)

        finally:
            # Attempt cleanup even when ingestion, insertion, or execution
            # raises an exception.
            persistent_store.delete_document(poison_id)
