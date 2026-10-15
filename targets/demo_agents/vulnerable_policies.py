ALLOWED_TOOLS = {
    "search_customer",
    "get_customer",
    "delete_customer",
}


def is_tool_allowed(tool_name: str) -> bool:
    return tool_name in ALLOWED_TOOLS