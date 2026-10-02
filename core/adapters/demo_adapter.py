from core.adapters.base import AgentAdapter
from core.models.agent import AgentResult
from targets.demo_agents.agent import DemoAgent


class DemoAgentAdapter(AgentAdapter):
    def __init__(self):
        self.agent = DemoAgent()

    def run(self, user_input: str) -> AgentResult:
        return self.agent.run(user_input)