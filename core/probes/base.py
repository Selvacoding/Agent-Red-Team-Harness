from abc import ABC, abstractmethod

from core.adapters.base import AgentAdapter
from core.models.agent import AgentResult


class Probe(ABC):
    attack_type: str = "unknown"
    is_attack: bool = True

    @abstractmethod
    def run(self, adapter: AgentAdapter) -> AgentResult:
        """Execute this security probe against the target agent."""
        pass