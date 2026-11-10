from core.adapters.base import AgentAdapter
from core.models.agent import AgentResult
from targets.mcp_agents.agent import MCPCustomerAgent


class MCPAgentAdapter(AgentAdapter):
    def __init__(
        self,
        vulnerable: bool | None = None,
        poisoned_description: bool | None = None,
        allow_delete: bool | None = None,
        malicious_tool_result: bool = False,
        malicious_resource: bool = False,
        argument_manipulation: bool = False,
        multi_tool_chain: bool = False,
        require_delete_confirmation: bool = False,
        trusted_delete_confirmation: bool = False,
    ):
        self.agent = MCPCustomerAgent(
            vulnerable=vulnerable,
            poisoned_description=poisoned_description,
            allow_delete=allow_delete,
            malicious_tool_result=malicious_tool_result,
            malicious_resource=malicious_resource,
            argument_manipulation=argument_manipulation,
            multi_tool_chain=multi_tool_chain,
            require_delete_confirmation=require_delete_confirmation,
            trusted_delete_confirmation=trusted_delete_confirmation,
        )

    def run(self, user_input: str) -> AgentResult:
        return self.agent.run(user_input)
