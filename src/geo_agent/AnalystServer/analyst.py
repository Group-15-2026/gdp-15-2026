from ..Entities.Article import Article
from ..Entities.Actors import Actor
from ..Entities.Events import Event, _Impact, _Severity

from .impacts import event_impact_serverity, get_justification

import asyncio
from mcp.server.fastmcp import FastMCP

analyst_mcp = FastMCP(name="Analyst MCP Server")


@analyst_mcp.tool()
def group_articles(articles: list[Article]) -> dict[str, list[Article]]:
    raise NotImplementedError()



@analyst_mcp.tool()
async def analyse_events(events: list[Event]) -> list[Event]:                                     #
    '''
    Calculates the: economic impact, financial market impact, security impact and diplomatic impact
    of each of the events from its source articles. Updates the events with with these impacts and
    returns the updated events.

    You should only pass in event objects that have been outputted by the 'extract_events' tool in 
    the 'summariser' mcp server, NOT events that have already been processed.
    '''
        
    analysed_events = []
    for event in events:
        scored_event = await event_impact_serverity(event)
        completed_event = await get_justification(scored_event)
        analysed_events.append(completed_event)

    return analysed_events

# TODO : The LLM should be instructed to produce a report in the desired output format (e.g. JSON / HTML)
@analyst_mcp.prompt()
def gen_report() -> str:
    raise NotImplementedError()

if __name__ == "__main__":
    analyst_mcp.run()
