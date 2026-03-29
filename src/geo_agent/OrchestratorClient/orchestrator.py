# XX Note to implementer: this can potentially be a lightweight local LLM (e.g. using ollama)
# it owns sequencing decisions, and is the only entity interacting with all three MCP servers
# it should typically call the servers in sequence (potentially using loops to gain extra context /
#   find new articles).

from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    @staticmethod
    def _set_server_params(path: str) -> StdioServerParameters:
        return StdioServerParameters(
            command="uv",
            args=["run", "python", "-m", path],
            env=None,
        )

    def __init__(self):
        self.servers = {
            "collector": MCPClient._set_server_params("src.geo_agent.CollectorServer.collector"),
            "summariser": self._set_server_params("src.geo_agent.SummariserServer.summariser"),
            "analyst": self._set_server_params("src.geo_agent.AnalystServer.analyst"),
        }
        self.exit_stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}

    # link the client to mcp servers
    async def connect_to_servers(self, show=True):
        for name, serverParams in self.servers.items():
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(serverParams))
            session = await self.exit_stack.enter_async_context(ClientSession(*stdio_transport))
            await session.initialize()
            self.sessions[name] = session
            tools = (await session.list_tools()).tools
            if show:
                print(f"\n{name.title()} Server Connected — tools: {[t.name for t in tools]}")

    # used to access sessions for calling tools 
    async def get_session(self, name: str) -> ClientSession:
        return self.sessions[name]

    # close open server context sessions when finished
    async def cleanup(self):
        await self.exit_stack.aclose()