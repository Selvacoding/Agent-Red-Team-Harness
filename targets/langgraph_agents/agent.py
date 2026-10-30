from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from core.models.agent import AgentResult
from targets.langchain_agents.tools import create_customer_tools


class LangGraphCustomerAgent:
    def __init__(
        self,
        vulnerable: bool = False,
        model_name: str = "llama3.2:latest",
    ):
        self.model_name = model_name
        self.execution_log = []

        if vulnerable:
            from targets.langchain_agents.vulnerable_policies import (
                is_tool_allowed,
            )
        else:
            from targets.langchain_agents.policies import is_tool_allowed

        self.tools = create_customer_tools(
            is_tool_allowed=is_tool_allowed,
            execution_log=self.execution_log,
        )

        self.model = ChatOllama(
            model=self.model_name,
            temperature=0,
        ).bind_tools(self.tools)

        graph = StateGraph(MessagesState)

        graph.add_node("agent", self.call_model)
        graph.add_node("tools", ToolNode(self.tools))

        graph.add_edge(START, "agent")

        graph.add_conditional_edges(
            "agent",
            tools_condition,
        )

        graph.add_edge("tools", "agent")

        self.graph = graph.compile()

    def call_model(self, state: MessagesState):
        response = self.model.invoke(state["messages"])
        return {"messages": [response]}

    def run(self, user_input: str) -> AgentResult:
        self.execution_log.clear()

        result = self.graph.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            }
        )

        messages = result.get("messages", [])
        response = ""

        if messages:
            content = messages[-1].content
            response = (
                content if isinstance(content, str) else str(content)
            )

        executions = list(self.execution_log)
        last_execution = executions[-1] if executions else None

        return AgentResult(
            response=response,
            tool_execution=last_execution,
            tool_executions=executions,
        )
