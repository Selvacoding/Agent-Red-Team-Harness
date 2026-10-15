from core.adapters.base import AgentAdapter
from core.models.agent import AgentResult
from targets.rag.agent import RAGAgent


class RAGAgentAdapter(AgentAdapter):
    def __init__(self):
        self.agent = RAGAgent(
            document_id="customer-policy",
            document_path="targets/rag/data/customer_policy.md",
        )

    def run(self, user_input: str) -> AgentResult:
        return self.agent.run(user_input)
