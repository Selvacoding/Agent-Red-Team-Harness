from core.adapters.base import AgentAdapter
from core.models.agent import AgentResult
from core.probes.base import Probe
from targets.rag.documents import reset_documents
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
        reset_documents()
        reset_vector_store()

        poison_document(self.poisoned_content)
        return adapter.run(self.query)
