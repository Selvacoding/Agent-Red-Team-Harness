
import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SERVER_PATH = PROJECT_ROOT / "targets" / "mcp_agents" / "server.py"


async def run_mcp_server_test(
    vulnerable: bool,
    require_confirmation: bool = False,
    trusted_confirmation: bool = False,
    model_confirmation: bool = False,
):
    env = os.environ.copy()
    env["MCP_VULNERABLE"] = str(vulnerable).lower()
    env["MCP_REQUIRE_DELETE_CONFIRMATION"] = str(
        require_confirmation
    ).lower()
    env["MCP_TRUSTED_DELETE_CONFIRMATION"] = str(
        trusted_confirmation
    ).lower()

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
        env=env,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            tool_names = {tool.name for tool in tools_result.tools}

            assert tool_names == {
                "search_customer",
                "get_customer",
                "delete_customer",
            }

            search_result = await session.call_tool(
                "search_customer",
                {"query": "Alice"},
            )
            search_data = json.loads(search_result.content[0].text)

            assert search_data["customers"][0]["name"] == "Alice"

            get_result = await session.call_tool(
                "get_customer",
                {"customer_id": 102},
            )
            get_data = json.loads(get_result.content[0].text)

            assert get_data["customer"]["name"] == "Bob"

            delete_result = await session.call_tool(
                "delete_customer",
                {
                    "customer_id": 102,
                    "confirmation": model_confirmation,
                },
            )
            delete_data = json.loads(delete_result.content[0].text)

            if require_confirmation and not trusted_confirmation:
                assert delete_data["authorized"] is False
                assert delete_data["executed"] is False
            else:
                assert delete_data["authorized"] is vulnerable
                assert delete_data["executed"] is vulnerable


def test_mcp_server_protected_mode():
    asyncio.run(
        run_mcp_server_test(vulnerable=False)
    )


def test_mcp_server_vulnerable_mode():
    asyncio.run(
        run_mcp_server_test(vulnerable=True)
    )


def test_model_confirmation_cannot_authorize_deletion():
    """A model-generated confirmation must not authorize deletion."""

    asyncio.run(
        run_mcp_server_test(
            vulnerable=True,
            require_confirmation=True,
            trusted_confirmation=False,
            model_confirmation=True,
        )
    )


def test_trusted_host_confirmation_allows_configured_deletion():
    """Trusted host configuration can authorize deletion."""

    asyncio.run(
        run_mcp_server_test(
            vulnerable=True,
            require_confirmation=True,
            trusted_confirmation=True,
            model_confirmation=False,
        )
    )
