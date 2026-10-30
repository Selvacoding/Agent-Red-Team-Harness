from core.adapters.base import AgentAdapter
from core.models.agent import AgentResult
from targets.langchain_agents.agent import LangChainCustomerAgent


class LangChainAgentAdapter(AgentAdapter):
    def __init__(self, vulnerable: bool = False):
        self.agent = LangChainCustomerAgent(
            vulnerable=vulnerable,
        )

    def run(self, user_input: str) -> AgentResult:
        return self.agent.run(user_input)
