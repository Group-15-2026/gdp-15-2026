import asyncio
import logging

from geo_agent.OrchestratorClient.orchestrator import create_mcp_client, create_mcp_agent, TASK_PROMPT
from utils import setup

async def main():
    setup()
    logger = logging.getLogger(__name__)
    logger.info("Utilities setup successful.")

    # TODO This is currently just test code to demonstrate execution of a simple prompt - may need updating
    # |-> see the TASK_PROMPT in orchestrator.py for more details

    client = create_mcp_client()
    logger.info("MCP Servers created successfully")

    agent = create_mcp_agent(client)
    logger.info("Orchestrator Agent connected to MCP client successfully")

    logger.info(f"Orchestrator Agent given prompt: {TASK_PROMPT}")
    response = await agent.run(TASK_PROMPT)
    logger.info(f"Orchestrator Agent generated response: {response}")

    await client.close_all_sessions()
    logger.info("MCP Servers shutdown successfully")

if __name__ == "__main__":
    asyncio.run(main())
