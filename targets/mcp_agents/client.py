
import os
import sys
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(
        self,
        server_script: str | None = None,
        vulnerable: bool = False,
        poisoned_description: bool = False,
        allow_delete: bool = False,
        malicious_tool_result: bool = False,
        malicious_resource: bool = False,
        argument_manipulation: bool = False,
        multi_tool_chain: bool = False,
        require_delete_confirmation: bool = False,
        trusted_delete_confirmation: bool = False,
    ):
        if server_script is None:
            server_script = os.path.join(
                os.path.dirname(__file__),
                "server.py",
            )

        self.server_script = os.path.abspath(server_script)

        self.vulnerable = vulnerable
        self.poisoned_description = poisoned_description
        self.allow_delete = allow_delete
        self.malicious_tool_result = malicious_tool_result
        self.malicious_resource = malicious_resource
        self.argument_manipulation = argument_manipulation
        self.multi_tool_chain = multi_tool_chain
        self.require_delete_confirmation = (
            require_delete_confirmation
        )
        self.trusted_delete_confirmation = (
            trusted_delete_confirmation
        )

        self.exit_stack: AsyncExitStack | None = None
        self.session: ClientSession | None = None

        self._read_stream = None
        self._write_stream = None

    def _server_environment(self) -> dict[str, str]:
        """Build an isolated environment for the MCP server."""

        env = os.environ.copy()

        env["MCP_VULNERABLE"] = str(
            self.vulnerable
        ).lower()

        env["MCP_POISONED_DESCRIPTION"] = str(
            self.poisoned_description
        ).lower()

        env["MCP_ALLOW_DELETE"] = str(
            self.allow_delete
        ).lower()

        env["MCP_MALICIOUS_TOOL_RESULT"] = str(
            self.malicious_tool_result
        ).lower()

        env["MCP_MALICIOUS_RESOURCE"] = str(
            self.malicious_resource
        ).lower()

        env["MCP_ARGUMENT_MANIPULATION"] = str(
            self.argument_manipulation
        ).lower()

        env["MCP_MULTI_TOOL_CHAIN"] = str(
            self.multi_tool_chain
        ).lower()

        env["MCP_REQUIRE_DELETE_CONFIRMATION"] = str(
            self.require_delete_confirmation
        ).lower()

        env["MCP_TRUSTED_DELETE_CONFIRMATION"] = str(
            self.trusted_delete_confirmation
        ).lower()

        return env

    async def connect(self):
        """Start the MCP server and establish a client session."""

        if self.session is not None:
            return

        self.exit_stack = AsyncExitStack()

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_script],
            env=self._server_environment(),
        )

        try:
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )

            self._read_stream, self._write_stream = stdio_transport

            self.session = await self.exit_stack.enter_async_context(
                ClientSession(
                    self._read_stream,
                    self._write_stream,
                )
            )

            await self.session.initialize()

        except Exception:
            await self.exit_stack.aclose()
            self.exit_stack = None
            self.session = None
            raise

    async def list_tools(self) -> list:
        if self.session is None:
            raise RuntimeError("MCP client is not connected")

        result = await self.session.list_tools()
        return result.tools

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        if self.session is None:
            raise RuntimeError("MCP client is not connected")

        return await self.session.call_tool(
            tool_name,
            arguments,
        )

    async def read_resource(self, uri: str) -> str:
        if self.session is None:
            raise RuntimeError("MCP client is not connected")

        result = await self.session.read_resource(uri)

        contents = []

        for item in result.contents:
            text = getattr(item, "text", None)

            if text is not None:
                contents.append(text)
            else:
                contents.append(str(item))

        return "\n".join(contents)

    async def close(self):
        """Close the MCP session and subprocess."""

        if self.exit_stack is not None:
            await self.exit_stack.aclose()

        self.exit_stack = None
        self.session = None
        self._read_stream = None
        self._write_stream = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        await self.close()
