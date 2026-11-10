import asyncio

from targets.mcp_agents.client import MCPClient


async def inspect_tools(vulnerable: bool) -> None:
    mode = "VULNERABLE" if vulnerable else "PROTECTED"

    print("\n" + "=" * 50)
    print(f"{mode} MCP TOOL DESCRIPTIONS")
    print("=" * 50)

    client = MCPClient(
        vulnerable=vulnerable,
        poisoned_description=vulnerable,
        allow_delete=vulnerable,
    )

    try:
        await client.connect()

        tools = await client.list_tools()

        for tool in tools:
            print(f"\nTool: {tool.name}")
            print(f"Description: {tool.description}")

    finally:
        await client.close()


async def main() -> None:
    await inspect_tools(vulnerable=False)
    await inspect_tools(vulnerable=True)


if __name__ == "__main__":
    asyncio.run(main())
