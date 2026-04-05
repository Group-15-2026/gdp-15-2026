# XX Note to implementer: Give a local LLM power to connect to an MCP client, and own the sequencing decisions required
# Consider adding an mcp structured prompt to the final summariser server (or each) to guide the LLM at each stage

# XX: System prompts should also be defined here

import asyncio
import os
from langchain_ollama.chat_models import ChatOllama
from mcp_use import MCPAgent, MCPClient

# Get the server script path (same directory as this file)
#current_dir = os.path.dirname(os.path.abspath(__file__))
#server_path = os.path.join(current_dir, "demo_server.py")

'''
"collector": self._set_server_params("src.geo_agent.CollectorServer.collector"),
            "summariser": self._set_server_params("src.geo_agent.SummariserServer.summariser"),
            "analyst": self._set_server_params("src.geo_agent.AnalystServer.analyst"),
'''

# Describe which MCP servers you want.
CONFIG = {
    "mcpServers": {
        "collector": {
            "command": "uv",
            "args": ["run", "python", "-m", "geo_agent.CollectorServer.collector"]
        },
        "summariser": {
            "command": "uv",
            "args": ["run", "python", "-m", "geo_agent.SummariserServer.summariser"]
        },
        "analyst": {
            "command": "uv",
            "args": ["run", "python", "-m", "geo_agent.AnalystServer.analyst"]
        }
    }
}

async def main():
    client = MCPClient.from_dict(CONFIG)
    llm = ChatOllama(model="gemma4:e4b", base_url="http://localhost:11434")
    
    # Wire the LLM to the client
    agent = MCPAgent(llm=llm, client=client, max_steps=20)

    # Give prompt to the agent
    result = await agent.run("What news can you find on the topic of 'trade' from the 28/03/2026 to the 29/03/2026?")
    print("\nResult:", result)

    # Always clean up running MCP sessions
    await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(main())