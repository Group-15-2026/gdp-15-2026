from ..Articles.Article import Article

from mcp.server.fastmcp import FastMCP

collector_mcp = FastMCP(name="Collector MCP Server")

# XX Note to implementer: the following resource and tool should largely just wrap 

# Collect top articles for processing
@collector_mcp.resource("files://articles/top")
def collect_top_articles() -> list[Article]:
    return NotImplemented

# Get more detailed news on a particular topic
@collector_mcp.resource("files://articles/{start_date}-{end_date}")
def search_news(start_date: str, end_date: str) -> list[Article]:
    return NotImplemented

@collector_mcp.prompt()
def collect_articles() -> list[Article]:
    return NotImplemented