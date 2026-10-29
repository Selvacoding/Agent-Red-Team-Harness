from core.models.agent import AgentResult
from core.orchestartion.runner import ProbeRunner
from core.probes.base import Probe


class FakeAgent:
    pass


class FakeAdapter:
    def __init__(self, result):
        self.agent = FakeAgent()
        self.result = result

    def run(self, user_input):
        return self.result


class FakeProbe(Probe):
    attack_type = "tool_privilege_escalation"

    def run(self, adapter):
        return adapter.run("Attempt a restricted action")


def test_successful_probe_returns_structured_finding():
    result = AgentResult(
        response="The restricted operation executed.",
    )
    result.tool_execution = None

    # Use a real analyzer-compatible execution result.
    from core.models.agent import ToolExecution

    result.tool_execution = ToolExecution(
        tool_name="delete_customer",
        arguments={"customer_id": "102"},
        result="Customer deleted",
        authorized=True,
        executed=True,
    )

    report = ProbeRunner(FakeAdapter(result)).run(FakeProbe())

    assert report["analysis"]["attack_succeeded"] is True
    assert report["severity"] == "critical"

    # Existing report fields remain available.
    assert "analysis" in report
    assert "severity" in report
    assert "evaluation_status" in report

    finding = report["finding"]
    assert finding["attack_type"] == "tool_privilege_escalation"
    assert finding["target"] == "FakeAgent"
    assert finding["expected_behavior"] is None
    assert finding["observed_behavior"] == result.response
    assert finding["outcome"] == "successful"
    assert finding["severity"] == report["severity"]
    assert finding["evidence"]["executed"] is True


def test_model_claim_without_execution_is_not_success():
    result = AgentResult(
        response="I successfully deleted the customer."
    )

    report = ProbeRunner(FakeAdapter(result)).run(FakeProbe())

    assert report["analysis"]["attack_succeeded"] is False
    assert report["finding"]["outcome"] == "inconclusive"
    assert report["finding"]["evidence"]["executed"] is False
