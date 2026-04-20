# XX Note to implementer: this file should create an instance of the mcp orchestrator client,
# instances of each MCP server, and connect the three together. It should then start / prompt the client
# and take care of storing / displaying the result.

# XX: it will also need to create the JSON tooling/MCP templates used to inform the LLM about the tools
# that it can access. It may be cleanest to define these in the relevant MCP related files, and simply
# import them here.

from geo_agent.OrchestratorClient.orchestrator import create_mcp_client, create_mcp_agent, TASK_PROMPT
from utils import setup_logging

import asyncio
import logging

async def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Logging started successfully")

    # XX currently just test code to demonstrate execution of a simple prompt

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
