from core.adapters.mcp_adapter import MCPAgentAdapter
from core.orchestartion.runner import ProbeRunner
from core.probes.tool_privilege import ToolPrivilegeEscalationProbe


def run_demo(vulnerable: bool):
    mode = "VULNERABLE" if vulnerable else "PROTECTED"

    print(f"\n{'=' * 60}")
    print(f"{mode} MCP SECURITY TEST")
    print("=" * 60)

    adapter = MCPAgentAdapter(vulnerable=vulnerable)

    probe = ToolPrivilegeEscalationProbe(
        target_tool="delete_customer",
        target_id="102",
    )

    runner = ProbeRunner(adapter)
    report = runner.run(probe)

    print("\nFinding:")
    print(f"Attack type: {report['finding']['attack_type']}")
    print(f"Target: {report['finding']['target']}")
    print(f"Outcome: {report['finding']['outcome']}")
    print(f"Severity: {report['severity']}")

    print("\nEvidence:")
    for execution in report["analysis"]["tool_executions"]:
        print(f"Tool: {execution['tool_name']}")
        print(f"Arguments: {execution['arguments']}")
        print(f"Authorized: {execution['authorized']}")
        print(f"Executed: {execution['executed']}")
        print(f"Result: {execution['result']}")


def main():
    print("=" * 60)
    print("AGENT RED TEAM HARNESS - PHASE 5")
    print("=" * 60)

    run_demo(vulnerable=False)
    run_demo(vulnerable=True)


if __name__ == "__main__":
    main()
