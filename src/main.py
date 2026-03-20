# XX Note to implementer: this file should create an instance of the mcp orchestrator client, 
# instances of each MCP server, and connect the three together. It should then start / prompt the client
# and take care of storing / displaying the result.

# XX: it will also need to create the JSON tooling/MCP templates used to inform the LLM about the tools 
# that it can access. It may be cleanest to define these in the relevant MCP related files, and simply
# import them here.