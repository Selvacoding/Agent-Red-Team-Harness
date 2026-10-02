from dataclasses import dataclass
from typing import Any


@dataclass
class ToolExecution:
    tool_name: str
    arguments: dict[str, Any]
    result: Any
    authorized: bool


@dataclass
class AgentResult:
    response: str
    tool_execution: ToolExecution | None = None
