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
        article_title = "I made 'serious mistake' advising Starmer to appoint Mandelson, PM's ex-top adviser says",
        publication_time = datetime.now(),
        source = Source(
            source_name = "BBC News"
        )
    )
    event1 = Event(
        event = "Foreign Office official ousted regarding security clearance decision.",
        source_articles = [article1]
    )
    article2 = Article(
        article_title = "Protests may need to be stopped in some cases, PM suggests",
        publication_time = datetime.now(),
        source = Source(
            source_name = "BBC News"
        )
    )
    event2 = Event(
        event = "two Jewish men were stabbed in Golders Green, north London",
        source_articles = [article2]
    )
    article3 = Article(
        article_title = "The US has warned shipping companies they could face sanctions if they pay Iran for safe passage through the Strait of Hormuz",
        publication_time = datetime.now(),
        source = Source(
            source_name = "BBC News"
        )
    )
    event3 = Event(
        event = "US threatens shipping firms with sanctions if they pay Iran tolls",
        source_articles = [article2]
    )

        # won't be necessary once the full analyst function is implemented
    event1.diplomatic_impact.severity = _Severity.low
    event1.economic_impact.severity = _Severity.no_impact
    event1.financial_market_impact.severity = _Severity.no_impact
    event1.security_impact.severity = _Severity.no_impact
    event2.diplomatic_impact.severity = _Severity.no_impact
    event2.economic_impact.severity = _Severity.no_impact
    event2.financial_market_impact.severity = _Severity.no_impact
    event2.security_impact.severity = _Severity.low
    event3.diplomatic_impact.severity = _Severity.low
    event3.economic_impact.severity = _Severity.high
    event3.financial_market_impact.severity = _Severity.high
    event3.security_impact.severity = _Severity.medium


    [processed_events] = await asyncio.gather(
        analyse_events([event1,event2,event3])
    )

    for event in processed_events:
        print(f"The event <<{event.event}>> has the following impacts:")

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
