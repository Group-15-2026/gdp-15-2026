from ..Entities.Article import Article
from ..Entities.Actors import Actor
from ..Entities.Events import Event

from .impacts import impact_serverities, impact_justifications

import asyncio
from mcp.server.fastmcp import FastMCP

analyst_mcp = FastMCP(name="Analyst MCP Server")


@analyst_mcp.tool()
def group_articles(articles: list[Article]) -> dict[str, list[Article]]:
    raise NotImplementedError()



@analyst_mcp.tool()
async def analyse_events(events: list[Event]) -> list[Event]:
    '''
    Calculates the: economic impact, financial market impact, security impact and diplomatic impact
    of each of the events from its source articles. Updates the events with with these impacts and
    returns the updated events.

    You should only pass in event objects that have been outputted by the 'extract_events' tool in 
    the 'summariser' mcp server, NOT events that have already been processed.
    '''
    from .financial_rules import classify_financial_impact
    from ..Entities.Events import Severity
    
    scored_events = await impact_serverities(events)

    for event in scored_events:
        classification = classify_financial_impact("Global", event.event)
        event_type = classification["event_type"]
        
        high_types = {"military_escalation", "energy_shock", "sanctions"}
        med_types = {"trade_dispute", "coup_or_instability", "diplomatic_change"}
        
        if event_type in high_types:
            rule_severity = Severity.high
        elif event_type in med_types:
            rule_severity = Severity.medium
        elif event_type is not None:
            rule_severity = Severity.low
        else:
            rule_severity = Severity.no_impact
            
        if event.financial_market_impact:
            event.financial_market_impact.severity = rule_severity 
    
    analysed_events = await impact_justifications(scored_events)

    return analysed_events

# TODO : The LLM should be instructed to produce a report in the desired output format (e.g. JSON / HTML)
@analyst_mcp.prompt()
def gen_report() -> str:
    raise NotImplementedError()

if __name__ == "__main__":
    analyst_mcp.run()
