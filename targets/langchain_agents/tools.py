from langchain.tools import tool

from core.models.agent import ToolExecution
from targets.demo_agents import tools as customer_tools


def create_customer_tools(is_tool_allowed, execution_log):
    """Create LangChain tools with authorization and execution evidence."""

    @tool
    def search_customer(name: str) -> str:
        """Search for a customer by name."""

        tool_name = "search_customer"
        arguments = {"name": name}
        authorized = is_tool_allowed(tool_name)

        if authorized:
            result = customer_tools.search_customer(name=name)
        else:
            result = f"Tool '{tool_name}' is not authorized."

        execution_log.append(
            ToolExecution(
                tool_name=tool_name,
                arguments=arguments,
                result=result,
                authorized=authorized,
                executed=authorized,
            )
        )

        return str(result)

    @tool
    def get_customer(customer_id: str) -> str:
        """Get customer details using customer ID."""

        tool_name = "get_customer"
        arguments = {"customer_id": customer_id}
        authorized = is_tool_allowed(tool_name)

        if authorized:
            result = customer_tools.get_customer(
                customer_id=customer_id
            )
        else:
            result = f"Tool '{tool_name}' is not authorized."

        execution_log.append(
            ToolExecution(
                tool_name=tool_name,
                arguments=arguments,
                result=result,
                authorized=authorized,
                executed=authorized,
            )
        )

        return str(result)

    @tool
    def delete_customer(customer_id: str) -> str:
        """Delete a customer using customer ID."""

        tool_name = "delete_customer"
        arguments = {"customer_id": customer_id}
        authorized = is_tool_allowed(tool_name)

        if authorized:
            result = customer_tools.delete_customer(
                customer_id=customer_id
            )
        else:
            result = f"Tool '{tool_name}' is not authorized."

        execution_log.append(
            ToolExecution(
                tool_name=tool_name,
                arguments=arguments,
                result=result,
                authorized=authorized,
                executed=authorized,
            )
        )

        return str(result)

    return [
        search_customer,
        get_customer,
        delete_customer,
    ]
