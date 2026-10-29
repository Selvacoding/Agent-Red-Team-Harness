from core.adapters.demo_adapter import DemoAgentAdapter
from core.orchestartion.runner import ProbeRunner
from core.probes.tool_privilege import ToolPrivilegeEscalationProbe
from targets.demo_agents.agent import DemoAgent
from targets.demo_agents.tools import customers

probe = ToolPrivilegeEscalationProbe(
    target_tool="delete_customer",
    target_id="102",
)

for vulnerable in (False, True):
    # Reset shared demo data before each independent scenario.
    customers.clear()
    customers.update({
        "101": {
            "name": "Alice",
            "email": "alice@example.com",
            "status": "active",
        },
        "102": {
            "name": "Bob",
            "email": "bob@example.com",
            "status": "inactive",
        },
    })

    adapter = DemoAgentAdapter()
    adapter.agent = DemoAgent(vulnerable=vulnerable)

    print("\n" + "=" * 55)
    print("MODE:", "VULNERABLE" if vulnerable else "PROTECTED")
    print("=" * 55)

    report = ProbeRunner(adapter).run(probe)

    print("Analysis:", report["analysis"])
    print("Severity:", report["severity"])
    print("Evaluation status:", report["evaluation_status"])
    print("Customer 102 still exists:", "102" in customers)
