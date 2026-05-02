from ..Entities.Article import Article
from ..Entities.Actors import Actor
from ..Entities.Events import Event, _Impact, _Severity

from .impacts import get_justification

import asyncio
from mcp.server.fastmcp import FastMCP

analyst_mcp = FastMCP(name="Analyst MCP Server")


# ! Note to implementer: may only pass unique articles IDs to tools, and the articles can then be collected from central DB

@analyst_mcp.tool()
def group_articles(articles: list[Article]) -> dict[str, list[Article]]:
    raise NotImplementedError()



@analyst_mcp.tool()
async def analyse_events(events: list[Event]) -> list[Event]:
    # TODO Need to implement impact scoring routine here.


    analysed_events = []
    for event in events:
        analysed_events.append(await get_justification(event))

    return analysed_events

# TODO : The LLM should be instructed to produce a report in the desired output format (e.g. JSON / HTML)
@analyst_mcp.prompt()
def gen_report() -> str:
    raise NotImplementedError()

if __name__ == "__main__":
    analyst_mcp.run()
