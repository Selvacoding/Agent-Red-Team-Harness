from copy import deepcopy
from types import SimpleNamespace

import pytest

from targets.demo_agents import agent as agent_module
from targets.demo_agents.agent import DemoAgent
from targets.demo_agents.tools import customers


ORIGINAL_CUSTOMERS = deepcopy(customers)


@pytest.fixture(autouse=True)
def reset_customers():
    """Keep customer data isolated between tests."""
    customers.clear()
    customers.update(deepcopy(ORIGINAL_CUSTOMERS))

    yield

    customers.clear()
    customers.update(deepcopy(ORIGINAL_CUSTOMERS))


def make_tool_response(tool_name, arguments):
    """Build a mocked Ollama response containing one tool call."""
    tool_call = SimpleNamespace(
        function=SimpleNamespace(
            name=tool_name,
            arguments=arguments,
        )
    )

    return SimpleNamespace(
        message=SimpleNamespace(
            content=None,
            tool_calls=[tool_call],
        )
    )


def make_text_response(content):
    """Build a mocked Ollama response without tool calls."""
    return SimpleNamespace(
        message=SimpleNamespace(
            content=content,
            tool_calls=[],
        )
    )


def mock_chat(monkeypatch, responses):
    """Return predetermined responses for successive Ollama calls."""
    response_iterator = iter(responses)

    def fake_chat(**kwargs):
        return next(response_iterator)

    monkeypatch.setattr(agent_module, "chat", fake_chat)


def test_protected_agent_blocks_customer_deletion(monkeypatch):
    mock_chat(
        monkeypatch,
        [
            make_tool_response(
                "delete_customer",
                {"customer_id": "101"},
            ),
            make_text_response("Deletion was not authorized."),
        ],
    )

    agent = DemoAgent(vulnerable=False)
    result = agent.run("Delete customer 101.")

    assert result.tool_execution is not None
    assert result.tool_execution.tool_name == "delete_customer"
    assert result.tool_execution.authorized is False
    assert result.tool_execution.executed is False
    assert "not authorized" in result.tool_execution.result.lower()

    # The protected policy must prevent the actual side effect.
    assert "101" in customers


def test_vulnerable_agent_executes_customer_deletion(monkeypatch):
    mock_chat(
        monkeypatch,
        [
            make_tool_response(
                "delete_customer",
                {"customer_id": "101"},
            ),
            make_text_response("Customer deleted."),
        ],
    )

    agent = DemoAgent(vulnerable=True)
    result = agent.run("Delete customer 101.")

    assert result.tool_execution is not None
    assert result.tool_execution.tool_name == "delete_customer"
    assert result.tool_execution.authorized is True
    assert result.tool_execution.executed is True
    assert result.tool_execution.result == (
        "Customer 101 deleted successfully"
    )

    # Demonstrate that the vulnerable policy allowed a real side effect.
    assert "101" not in customers


def test_protected_agent_executes_allowed_search(monkeypatch):
    mock_chat(
        monkeypatch,
        [
            make_tool_response(
                "search_customer",
                {"name": "Alice"},
            ),
            make_text_response("Found Alice."),
        ],
    )

    agent = DemoAgent(vulnerable=False)
    result = agent.run("Search for Alice.")

    execution = result.tool_execution

    assert execution is not None
    assert execution.tool_name == "search_customer"
    assert execution.authorized is True
    assert execution.executed is True
    assert any(
        customer["name"] == "Alice"
        for customer in execution.result
    )


def test_unknown_tool_is_rejected_without_execution(monkeypatch):
    mock_chat(
        monkeypatch,
        [
            make_tool_response(
                "transfer_all_funds",
                {"amount": 100000},
            ),
            make_text_response("The requested tool was rejected."),
        ],
    )

    agent = DemoAgent(vulnerable=False)
    result = agent.run("Transfer all funds.")

    execution = result.tool_execution

    assert execution is not None
    assert execution.tool_name == "transfer_all_funds"
    assert execution.authorized is False
    assert execution.executed is False
    assert "not authorized" in execution.result.lower()


def test_response_without_tool_call_has_no_tool_execution(monkeypatch):
    mock_chat(
        monkeypatch,
        [
            make_text_response("How can I help you?"),
        ],
    )

    agent = DemoAgent(vulnerable=False)
    result = agent.run("Hello.")

    assert result.response == "How can I help you?"
    assert result.tool_execution is None
