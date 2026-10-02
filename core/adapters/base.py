from abc import ABC, abstractmethod

from core.models.agent import AgentResult


class AgentAdapter(ABC):

    @abstractmethod
    def run(self, user_input: str) -> AgentResult:
        """Send input to the target agent."""
        pass