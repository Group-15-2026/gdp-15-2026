from ..Entities.Article import Article
from ..Entities.Actors import Actor
from ..Entities.Events import Event

from mcp.server.fastmcp import FastMCP

analyst_mcp = FastMCP(name="Analyst MCP Server")

# TODO : Implement the two tools below, and add informative docstrings for each

@analyst_mcp.tool()
def group_articles(articles: list[Article]) -> dict[str, list[Article]]:
    return NotImplemented

@analyst_mcp.tool()
def analyse_events(events: list[Event]) -> list[Event]:
    return NotImplemented

# ! Note to implementer: this is slightly different from the arch. diagram, but is probably the easiest implementation
# TODO : The LLM should be instructed to produce a report in the desired output format (e.g. JSON / HTML)
@analyst_mcp.prompt()
def gen_report() -> str:
    return NotImplemented

if __name__ == "__main__":
    analyst_mcp.run()