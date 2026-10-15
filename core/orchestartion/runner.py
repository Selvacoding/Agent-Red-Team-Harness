from core.adapters.base import AgentAdapter
from core.analyzers.response_analyzer import (
    analyze_rag_execution,
    analyze_tool_execution,
)
from core.probes.base import Probe
from core.scoring.severity import calculate_severity


class ProbeRunner:
    def __init__(self, adapter: AgentAdapter):
        self.adapter = adapter

    def run(self, probe: Probe) -> dict:
        result = probe.run(self.adapter)

        if probe.attack_type == "rag_poisoning":
            analysis = analyze_rag_execution(
                result,
                expected_behavior=probe.expected_behavior,
            )
        else:
            analysis = analyze_tool_execution(
                result,
                is_attack=probe.is_attack,
                attack_type=probe.attack_type,
            )

        severity = calculate_severity(analysis)

        return {
            "analysis": analysis,
            "severity": severity,
        }
