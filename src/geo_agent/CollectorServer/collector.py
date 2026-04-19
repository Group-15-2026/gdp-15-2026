from mcp.server.fastmcp import FastMCP

from ..Entities.Article import Article

collector_mcp = FastMCP(name="Collector MCP Server")

# XX Note to implementer: the following resource and tool should largely just wrap NewsAPI

# Get more detailed news on a particular topic
@collector_mcp.tool()
def search_news(topics: list[str], start_date: str, end_date: str) -> list[Article]:
    return NotImplemented

# Collect top articles for processing
@collector_mcp.resource("files:///articles/top")
def collect_articles() -> list[Article]:
    return NotImplemented

if __name__ == "__main__":
    collector_mcp.run()
