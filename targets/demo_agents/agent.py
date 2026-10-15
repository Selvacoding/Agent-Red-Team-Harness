from ollama import chat

from core.models.agent import AgentResult, ToolExecution
from targets.demo_agents.tools import (
    search_customer,
    get_customer,
    delete_customer,
)


class DemoAgent:
    def __init__(self, vulnerable: bool = False):
        self.model = "llama3.2:latest"

        if vulnerable:
            from targets.demo_agents.vulnerable_policies import (
                is_tool_allowed,
            )
        else:
            from targets.demo_agents.policies import (
                is_tool_allowed,
            )

        self.is_tool_allowed = is_tool_allowed

        self.tool_functions = {
            "search_customer": search_customer,
            "get_customer": get_customer,
            "delete_customer": delete_customer,
        }

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_customer",
                    "description": "Search for a customer by name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                        },
                        "required": ["name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_customer",
                    "description": (
                        "Get customer details using customer ID."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {"type": "string"},
                        },
                        "required": ["customer_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_customer",
                    "description": (
                        "Delete a customer using customer ID."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {"type": "string"},
                        },
                        "required": ["customer_id"],
                    },
                },
            },
        ]

    def run(self, user_input: str) -> AgentResult:
        messages = [
            {
                "role": "user",
                "content": user_input,
            }
        ]

        response = chat(
            model=self.model,
            messages=messages,
            tools=self.tools,
        )

        # Always follow the AgentResult contract.
        if not response.message.tool_calls:
            return AgentResult(
                response=response.message.content or "",
                tool_execution=None,
            )

        # This demo currently processes one tool call per turn.
        tool_call = response.message.tool_calls[0]
        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments

        print("Tool call:", tool_name, arguments)

        # Authorization must happen before tool execution.
        authorized = (
            tool_name in self.tool_functions
            and self.is_tool_allowed(tool_name)
        )

        executed = False

        if not authorized:
            result = f"Tool '{tool_name}' is not authorized."

        else:
            tool_function = self.tool_functions[tool_name]
            result = tool_function(**arguments)
            executed = True

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
            tools=self.tools,
        )

        return AgentResult(
            response=final_response.message.content or "",
            tool_execution=ToolExecution(
                tool_name=tool_name,
                arguments=arguments,
                result=result,
                authorized=authorized,
                executed=executed,
            ),
        )
