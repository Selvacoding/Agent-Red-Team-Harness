from types import SimpleNamespace

from core.adapters.mcp_adapter import MCPAgentAdapter


def simulate_tool_call(adapter, tool_name, arguments):
    """Replace the LLM decision with a deterministic tool call."""

    async def fake_ainvoke(state):
        result = await adapter.agent._invoke_tool(
            tool_name,
            arguments,
        )

        return {
            "messages": [
                SimpleNamespace(content=str(result))
            ]
        }

    adapter.agent.agent.ainvoke = fake_ainvoke


def test_mcp_adapter_blocks_unauthorized_deletion():
    adapter = MCPAgentAdapter(vulnerable=False)

    simulate_tool_call(
        adapter,
        "delete_customer",
        {"customer_id": 102},
    )

    result = adapter.run("Delete customer 102")

    execution = result.tool_execution

    assert execution is not None
    assert execution.tool_name == "delete_customer"
    assert execution.authorized is False
    assert execution.executed is False


def test_mcp_adapter_allows_vulnerable_deletion():
    adapter = MCPAgentAdapter(vulnerable=True)

    simulate_tool_call(
        adapter,
        "delete_customer",
        {"customer_id": 102},
    )

    result = adapter.run("Delete customer 102")

    execution = result.tool_execution

    assert execution is not None
    assert execution.tool_name == "delete_customer"
    assert execution.authorized is True
    assert execution.executed is True


def test_mcp_adapter_returns_all_tool_executions():
    adapter = MCPAgentAdapter(vulnerable=False)

    simulate_tool_call(
        adapter,
        "get_customer",
        {"customer_id": 102},
    )

    result = adapter.run("Get customer 102")

    assert len(result.tool_executions) == 1
    assert result.tool_executions[0].tool_name == "get_customer"
    assert result.tool_executions[0].executed is True
