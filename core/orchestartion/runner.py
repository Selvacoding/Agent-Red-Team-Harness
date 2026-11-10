from core.adapters.base import AgentAdapter
from core.analyzers.response_analyzer import (
    analyze_rag_execution,
    analyze_tool_execution,
    analyze_tool_description_poisoning,
    analyze_malicious_tool_result,
    analyze_mcp_resource_injection,
    analyze_argument_manipulation,
    analyze_confused_deputy,
    analyze_multi_tool_chain,
)
from core.probes.base import Probe
from core.scoring.severity import calculate_severity
from core.scoring.repeatability import summarize_repeatability


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

        elif probe.attack_type == "tool_description_poisoning":
            analysis = analyze_tool_description_poisoning(
                result,
                source_tool=probe.source_tool,
                target_tool=probe.target_tool,
                target_id=probe.target_id,
            )

        elif probe.attack_type == "malicious_tool_result":
            analysis = analyze_malicious_tool_result(
                result,
                source_tool=probe.source_tool,
                target_tool=probe.target_tool,
                target_id=probe.target_id,
            )

        elif probe.attack_type == "mcp_resource_injection":
            analysis = analyze_mcp_resource_injection(
                result,
                source_tool=probe.source_tool,
                target_tool=probe.target_tool,
                target_id=probe.target_id,
            )

        elif probe.attack_type == "argument_manipulation":
            analysis = analyze_argument_manipulation(
                result,
                source_id=probe.source_id,
                manipulated_id=probe.manipulated_id,
                source_tool=probe.source_tool,
                target_tool=probe.target_tool,
            )

        elif probe.attack_type == "confused_deputy":
            analysis = analyze_confused_deputy(
                result,
                source_tool=probe.source_tool,
                target_tool=probe.target_tool,
                target_id=probe.target_id,
            )

        elif probe.attack_type == "multi_tool_chain":
            analysis = analyze_multi_tool_chain(
                result,
                expected_chain=probe.expected_chain,
                target_id=probe.target_id,
            )

        else:
            analysis = analyze_tool_execution(
                result,
                is_attack=probe.is_attack,
                attack_type=probe.attack_type,
                target_tool=getattr(probe, "target_tool", None),
            )

        evaluation_status = analysis.get(
            "evaluation_status",
            "completed",
        )

        # Derive the outcome from observed evidence, not model claims.
        if analysis.get("outcome") == "not_observed":
            outcome = "not_observed"
        elif evaluation_status == "inconclusive":
            outcome = "inconclusive"
        elif evaluation_status == "not_exposed":
            outcome = "not_exposed"
        elif analysis.get("attack_succeeded") is True:
            outcome = "successful"
        elif analysis.get("attack_blocked") is True:
            outcome = "blocked"
        else:
            outcome = "inconclusive"

        analysis["outcome"] = outcome

        # Preserve the existing severity behavior.
        if evaluation_status == "inconclusive":
            severity = "inconclusive"
        else:
            severity = calculate_severity(analysis)

        # Avoid accidentally treating dynamically fabricated mock
        # attributes as a real target agent.
        adapter_attributes = getattr(self.adapter, "__dict__", {})
        agent = adapter_attributes.get("agent")

        target = (
            type(agent).__name__
            if agent is not None
            else type(self.adapter).__name__
        )

        observed_behavior = analysis.get(
            "response",
            getattr(result, "response", ""),
        )

        # Keep structured execution/retrieval evidence separate
        # from the human-readable observed behavior.
        evidence = {
            key: value
            for key, value in analysis.items()
            if key not in {"response", "outcome"}
        }

        finding = {
            "attack_type": probe.attack_type,
            "target": target,
            "expected_behavior": getattr(
                probe,
                "expected_behavior",
                None,
            ),
            "observed_behavior": observed_behavior,
            "evidence": evidence,
            "outcome": outcome,
            "severity": severity,
        }

        # Retain existing report fields for backward compatibility.
        return {
            "analysis": analysis,
            "severity": severity,
            "evaluation_status": evaluation_status,
            "finding": finding,
        }

    def run_repeated(self, probe: Probe, trials: int = 3) -> dict:
        """Run a probe repeatedly and summarize outcome variance.

        Use only with probes whose repeated execution is safe for the
        target, or whose setup and cleanup isolate each trial.
        """
        if trials < 1:
            raise ValueError("trials must be at least 1")

        reports = [self.run(probe) for _ in range(trials)]

        return {
            "trials": reports,
            "repeatability": summarize_repeatability(reports),
        }
