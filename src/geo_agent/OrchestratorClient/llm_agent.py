# XX Note to implementer: Give a local LLM power to connect to an MCP client, and own the sequencing decisions required
# Consider adding an mcp structured prompt to the final summariser server (or each) to guide the LLM at each stage

# XX: System prompts should also be defined here

import asyncio
from langchain_ollama.chat_models import ChatOllama
from mcp_use import MCPAgent, MCPClient, set_debug

# Avoid printing messy logs
set_debug(0)

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

MODEL = "gemma4:e4b"

SYSTEM_PROMPT = "" # XX to complete
TASK_PROMPT = "What news can you find on the topic of 'trade' from the 28/03/2026 to the 29/03/2026?"

async def run_task():
    client = MCPClient.from_dict(CONFIG)
    llm = ChatOllama(model=MODEL, base_url="http://localhost:11434")
    
    # Wire the LLM to the client
    agent = MCPAgent(llm=llm, client=client, system_prompt=SYSTEM_PROMPT, max_steps=20)

    # Give prompt to the agent
    result = await agent.run(TASK_PROMPT)

    # Always clean up running MCP sessions
    await client.close_all_sessions()

    return result

# XX TODO: stop logs being displayed