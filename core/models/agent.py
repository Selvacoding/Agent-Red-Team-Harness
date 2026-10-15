from dataclasses import dataclass
from typing import Any


@dataclass
class ToolExecution:
    tool_name: str
    arguments: dict[str, Any]
    result: Any
    authorized: bool
    executed: bool

@dataclass
class RAGExecution:
    query: str
    retrieved_documents: list[dict]

@dataclass
class AgentResult:
    response: str
    tool_execution: ToolExecution | None = None
    rag_execution: RAGExecution | None = None
