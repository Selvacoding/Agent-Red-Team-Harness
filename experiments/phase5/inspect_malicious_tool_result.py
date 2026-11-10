import asyncio

from targets.mcp_agents.client import MCPClient


async def inspect_result(malicious: bool):
    client = MCPClient(
        poisoned_description=False,
        allow_delete=False,
        malicious_tool_result=malicious,
    )

    async with client.connect():
        result = await client.call_tool(
            "get_customer",
            {"customer_id": 102},
        )

    print(f"\nMalicious result enabled: {malicious}")
    print("=" * 50)
    print(result)


async def main():
    await inspect_result(malicious=False)
    await inspect_result(malicious=True)


if __name__ == "__main__":
    asyncio.run(main())
