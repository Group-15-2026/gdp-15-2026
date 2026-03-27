from ..Entities.Article import Article
from ..Entities.Actors import Actor
from ..Entities.Events import Event

from mcp.server.fastmcp import FastMCP

analyst_mcp = FastMCP(name="Analyst MCP Server")

# XX Note to implementer: may only pass unique articles IDs to tools, and the articles can then be collected from central DB

@analyst_mcp.tool()
def group_articles(articles: list[Article]) -> dict[str, list[Article]]:
    return NotImplemented

@analyst_mcp.tool()
def analyse_events(events: list[Event]) -> list[Event]:
    return NotImplemented

# XX Note to implementer: this is slightly different from the arch. diagram, but is probably the easiest implementation
# the LLM should be instructed to produce a report in the desired output format (e.g. JSON / HTML)
@analyst_mcp.prompt()
def gen_report() -> str:
    return NotImplemented