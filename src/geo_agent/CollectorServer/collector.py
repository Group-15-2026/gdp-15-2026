from mcp.server.fastmcp import FastMCP

from ..Entities.Article import Article
from news import get_daily_articles

collector_mcp = FastMCP(name="Collector MCP Server")

# XX Note to implementer: the following resource and tool should largely just wrap NewsAPI

# Get more detailed news on a particular topic
# Duplicates possible
@collector_mcp.tool()
def search_news(topics: list[str], start_date: str, end_date: str) -> list[Article]:
    return NotImplemented

# Collect top articles for processing
# Returns top articles for that day, from business, science, and tech categories
# Duplicates possible
@collector_mcp.resource("files:///articles/top")
def collect_articles() -> list[Article]:
    return get_daily_articles()

if __name__ == "__main__":
    collector_mcp.run()
