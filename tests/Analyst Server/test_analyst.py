from geo_agent.Entities.Article import Article, Source
from geo_agent.Entities.Events import Event, _Impact, _Severity
from geo_agent.AnalystServer.analyst import analyse_events

from utils import setup

import asyncio
from datetime import datetime
import types
#import pytest

# TODO: add unit tests. Currently just seeing if the code runs

async def main():
    setup()

    # TODO: get a good full output from summariser MCP server with events that point to their sources
    article1 = Article(
        article_title = "",
        publication_time = datetime.now(),
        source = Source(
            source_name = "Bob's Newsagents"
        )
    )

    articles = [article1]

    event1 = Event(
        event = "Foreign Office official ousted regarding security clearance decision.",
        source_articles = articles
    )

    # won't be necessary once the full analyst function is implemented
    event1.diplomatic_impact.severity = _Severity.medium
    event1.economic_impact.severity = _Severity.no_impact
    event1.financial_market_impact.severity = _Severity.no_impact
    event1.security_impact.severity = _Severity.low
    events = [event1]

    
    [processed_events] = await asyncio.gather(
        analyse_events(events)
    )

    for event in processed_events:
        print(f"The event <<{event}>> has the following impacts:")

        print(f"economic impact severity: {event.economic_impact.severity}" )
        print(f"    ...reason given: {event.economic_impact.justification}" )
        print(f"financial market impact severity: {event.financial_market_impact.severity}" )
        print(f"    ...reason given: {event.financial_market_impact.justification}" )
        print(f"security impact severity: {event.security_impact.severity}" )
        print(f"    ...reason given: {event.security_impact.justification}" )
        print(f"diplomatic impact severity: {event.diplomatic_impact.severity}" )
        print(f"    ...reason given: {event.diplomatic_impact.justification}" )

        # TODO: also test controversy
        # print(event.controversy)


if __name__ == "__main__":
    asyncio.run(main())
