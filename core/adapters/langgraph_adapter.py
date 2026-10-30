from core.adapters.base import AgentAdapter
from core.models.agent import AgentResult
from targets.langgraph_agents.agent import LangGraphCustomerAgent


class LangGraphAgentAdapter(AgentAdapter):
    def __init__(self, vulnerable: bool = False):
        self.agent = LangGraphCustomerAgent(
            vulnerable=vulnerable,
        )

    def run(self, user_input: str) -> AgentResult:
        return self.agent.run(user_input)
