# XX Note to implementer: this file should create an instance of the mcp orchestrator client,
# instances of each MCP server, and connect the three together. It should then start / prompt the client
# and take care of storing / displaying the result.

# XX: it will also need to create the JSON tooling/MCP templates used to inform the LLM about the tools
# that it can access. It may be cleanest to define these in the relevant MCP related files, and simply
# import them here.

from geo_agent.OrchestratorClient.orchestrator import MCPClient

import asyncio

async def main():
    # XX currently just test code to demonstrate the mcp client connecting to the servers
    client = MCPClient()
    try:
        await client.connect_to_servers()
        print("\nAll servers connected successfully")

        # XX Example: extract a server session and call a tool
        collectorSession = await client.get_session("collector")
        result = await collectorSession.call_tool("search_news", 
                                                  {
                                                    "topics":["trade"], 
                                                    "start_date":"28/03/2026",
                                                    "end_date":"29/03/2026"
                                                   }
                                                 )
        print(f"\n\nCollector Server returned: {result} for tool 'search_news'")

        # XX This is where the client would then be linked to the local LLM and used
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
