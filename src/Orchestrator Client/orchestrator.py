# XX Note to implementer: this can potentially be a lightweight local LLM (e.g. using ollama)
# it owns sequencing decisions, and is the only entity interacting with all three MCP servers
# it should typically call the servers in sequence (potentially using loops to gain extra context / 
#   find new articles).