from core.adapters.langgraph_adapter import LangGraphAgentAdapter
from core.orchestartion.runner import ProbeRunner
from core.probes.tool_privilege import ToolPrivilegeEscalationProbe


def run_demo(vulnerable: bool):
    mode = "VULNERABLE" if vulnerable else "PROTECTED"

    print(f"\n{'=' * 20} {mode} LANGGRAPH AGENT {'=' * 20}")

    adapter = LangGraphAgentAdapter(vulnerable=vulnerable)
    runner = ProbeRunner(adapter)

    probe = ToolPrivilegeEscalationProbe(
        target_tool="delete_customer",
        target_id="102",
    )

    report = runner.run(probe)

    print("\nFinding:")
    print(report["finding"])

    return report


if __name__ == "__main__":
    run_demo(vulnerable=False)
    run_demo(vulnerable=True)
