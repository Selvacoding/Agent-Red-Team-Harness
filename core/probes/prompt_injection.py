from core.adapters.base import AgentAdapter
from core.models.agent import AgentResult
from core.probes.base import Probe


class PromptInjectionProbe(Probe):

    def __init__(self, payload: str):
        self.payload = payload

    def run(self, adapter: AgentAdapter) -> AgentResult:
        return adapter.run(self.payload)