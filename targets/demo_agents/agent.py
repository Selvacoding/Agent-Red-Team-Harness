from ollama import chat

from targets.demo_agents.tools import (
    search_customer,
    get_customer,
    delete_customer,
)

from core.models.agent import AgentResult, ToolExecution


class DemoAgent:
    def __init__(self, vulnerable: bool = False):
        self.model = "llama3.2:latest"

        if vulnerable:
            from targets.demo_agents.vulnerable_policies import is_tool_allowed
        else:
            from targets.demo_agents.policies import is_tool_allowed

        self.is_tool_allowed = is_tool_allowed

    def run(self, user_input: str) -> AgentResult:
        messages = [
            {
                "role": "user",
                "content": user_input,
            }
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_customer",
                    "description": "Search for a customer by name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"}
                        },
                        "required": ["name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_customer",
                    "description": "Get customer details using customer ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {"type": "string"}
                        },
                        "required": ["customer_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_customer",
                    "description": "Delete a customer using customer ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {"type": "string"}
                        },
                        "required": ["customer_id"],
                    },
                },
            },
        ]

        response = chat(
            model=self.model,
            messages=messages,
            tools=tools,
        )

        if not response.message.tool_calls:
            return response.message.content

        tool_call = response.message.tool_calls[0]

        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments

        print("Tool call:", tool_name, arguments)

        # check authorization before executing the tool
        authorized = self.is_tool_allowed(tool_name)

        if not authorized:
            result = f"Tool '{tool_name}' is not authorized."

        else:
            if tool_name == "search_customer":
                result = search_customer(**arguments)

            elif tool_name == "get_customer":
                result = get_customer(**arguments)

            elif tool_name == "delete_customer":
                result = delete_customer(**arguments)

            else:
                result = "Unknown tool"

        print("Tool result:", result)

        messages.append(response.message)

        messages.append(
            {
                "role": "tool",
                "tool_name": tool_name,
                "content": str(result),
            }
        )

        final_response = chat(
            model=self.model,
            messages=messages,
            tools=tools,
        )

        return AgentResult(
            response=final_response.message.content,
            tool_execution=ToolExecution(
                tool_name=tool_name,
                arguments=arguments,
                result=result,
                authorized=authorized,
            ),
        )
