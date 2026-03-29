from ..Entities.Article import Article
from ..Entities.Actors import Actor
from ..Entities.Events import Event

from mcp.server.fastmcp import FastMCP

summariser_mcp = FastMCP(name="Summariser MCP Server")

# XX Note to implementer: some of the below tools may be combined together depending on implementation
# may also only pass unique articles IDs to tools, and the articles can then be collected from central DB

@summariser_mcp.tool()
def summarise_batch(articles: list[Article]) -> list[Article]:
    return NotImplemented

@summariser_mcp.tool()
def score_sentiment(articles: list[Article]) -> list[Article]:
    return NotImplemented

@summariser_mcp.tool()
def tag_themes(articles: list[Article]) -> list[Article]:
    return NotImplemented

@summariser_mcp.tool()
def extract_act_eve(articles: list[Article]) -> tuple[list[Actor], list[Event]]:
    return NotImplemented

# XX Note: may or may not be necessary depending on how MCP client is implemented
if __name__ == "__main__":
    summariser_mcp.run()