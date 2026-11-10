from core.adapters.mcp_adapter import MCPAgentAdapter
from core.orchestartion.runner import ProbeRunner
from core.probes.tool_description_poisoning import (
    ToolDescriptionPoisoningProbe,
)


SCENARIOS = [
    {
        "name": "BASELINE",
        "poisoned_description": False,
        "allow_delete": False,
    },
    {
        "name": "POISONED DESCRIPTION - DELETE BLOCKED",
        "poisoned_description": True,
        "allow_delete": False,
    },
    {
        "name": "CLEAN DESCRIPTION - DELETE ALLOWED",
        "poisoned_description": False,
        "allow_delete": True,
    },
    {
        "name": "POISONED DESCRIPTION - DELETE ALLOWED",
        "poisoned_description": True,
        "allow_delete": True,
    },
]


def run_scenario(scenario: dict):
    print("\n" + "=" * 65)
    print(scenario["name"])
    print("=" * 65)

    print(
        "Poisoned description:",
        scenario["poisoned_description"],
    )

    print(
        "Delete allowed:",
        scenario["allow_delete"],
    )

    adapter = MCPAgentAdapter(
        poisoned_description=scenario[
            "poisoned_description"
        ],
        allow_delete=scenario[
            "allow_delete"
        ],
    )

    probe = ToolDescriptionPoisoningProbe(
        target_id="102",
    )

    runner = ProbeRunner(adapter)

    report = runner.run(probe)

    analysis = report["analysis"]
    finding = report["finding"]

    print("\nFinding:")
    print("Attack type:", finding["attack_type"])
    print("Outcome:", finding["outcome"])
    print("Severity:", report["severity"])

    print("\nAnalysis:")
    print(
        "Source tool called:",
        analysis["source_tool_called"],
    )

    print(
        "Manipulation detected:",
        analysis["manipulation_detected"],
    )

    print(
        "Attack succeeded:",
        analysis["attack_succeeded"],
    )

    print(
        "Attack blocked:",
        analysis["attack_blocked"],
    )

    print("\nObserved tool executions:")

    if not analysis["tool_executions"]:
        print("No tool executions recorded.")

    for execution in analysis["tool_executions"]:
        print("\nTool:", execution["tool_name"])
        print("Arguments:", execution["arguments"])
        print("Authorized:", execution["authorized"])
        print("Executed:", execution["executed"])
        print("Result:", execution["result"])

    return report


def main():
    print("=" * 65)
    print("AGENT RED TEAM HARNESS")
    print("PHASE 5 - TOOL DESCRIPTION POISONING EXPERIMENT")
    print("=" * 65)

    reports = []

    for scenario in SCENARIOS:
        report = run_scenario(scenario)
        reports.append(report)

    print("\n" + "=" * 65)
    print("EXPERIMENT SUMMARY")
    print("=" * 65)

    for scenario, report in zip(SCENARIOS, reports):
        print(
            f"{scenario['name']}: "
            f"{report['finding']['outcome']}"
        )


if __name__ == "__main__":
    main()
