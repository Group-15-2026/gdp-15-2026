from geo_agent.config import config
from geo_agent.OrchestratorClient.orchestrator import TASK_PROMPT, create_mcp_client, create_mcp_agent

#import pytest
import asyncio

# XX TODO: add unit tests. Currently just seeing if the code runs

async def run_task():
    client = create_mcp_client()
    agent = create_mcp_agent(client)

    # Give prompt to the agent
    result = await agent.run(TASK_PROMPT)

    # Always clean up running MCP sessions
    await client.close_all_sessions()

    return result

async def main():
    result = await run_task()    
    print("\nResult:", result)

if __name__ == "__main__":
    asyncio.run(main())