import asyncio

from targets.mcp_agents.agent import MCPCustomerAgent


async def inspect_agent(vulnerable: bool):
    mode = "VULNERABLE" if vulnerable else "PROTECTED"

    agent = MCPCustomerAgent(vulnerable=vulnerable)

    async with agent.client.connect():
        await agent._sync_tool_descriptions()

        print(f"\n{mode} LANGCHAIN AGENT")
        print("=" * 50)

        for langchain_tool in agent.tools:
            print(f"\nTool: {langchain_tool.name}")
            print(f"Description: {langchain_tool.description}")


async def main():
    await inspect_agent(vulnerable=False)
    await inspect_agent(vulnerable=True)


if __name__ == "__main__":
    asyncio.run(main())
