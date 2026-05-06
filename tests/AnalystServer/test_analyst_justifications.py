from geo_agent.Entities.Article import Article, Source
from geo_agent.Entities.Events import Event, Impact, Severity
from geo_agent.AnalystServer.analyst import impact_justifications

from utils import setup

import asyncio
from datetime import datetime


# Simple test of the impact severity justifications system for events

async def main():
    setup()

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
        source_articles = [article3]
    )

    # required as we are only judging the justification generator
    event1.set_impacts(Severity.no_impact, "", Severity.no_impact, "", Severity.no_impact, "", Severity.low, "")
    event2.set_impacts(Severity.no_impact, "", Severity.no_impact, "", Severity.low, "", Severity.no_impact, "")
    event3.set_impacts(Severity.high, "", Severity.high, "", Severity.medium, "", Severity.low, "")
    

    [processed_events] = await asyncio.gather(
        impact_justifications([event1,event2,event3])
    )

    for event in processed_events:
        assert event.economic_impact
        assert event.financial_market_impact
        assert event.security_impact
        assert event.diplomatic_impact
        print(f"The event <<{event.event}>> has the following impacts:")

        print(f"economic impact severity: {event.economic_impact.severity}" )
        print(f"    ...reason given: {event.economic_impact.justification}" )
        print(f"financial market impact severity: {event.financial_market_impact.severity}" )
        print(f"    ...reason given: {event.financial_market_impact.justification}" )
        print(f"security impact severity: {event.security_impact.severity}" )
        print(f"    ...reason given: {event.security_impact.justification}" )
        print(f"diplomatic impact severity: {event.diplomatic_impact.severity}" )
        print(f"    ...reason given: {event.diplomatic_impact.justification}" )


if __name__ == "__main__":
    asyncio.run(main())
