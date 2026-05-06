from geo_agent.Entities.Events import Event
from geo_agent.AnalystServer.analyst import analyse_events

from utils import setup

import asyncio
from pydantic import TypeAdapter

async def main():
    setup()

    # TODO: get a good full output from summariser MCP server with actors included in the events
    # currently using SampleEventsOutputProcessed.txt 
    loader = TypeAdapter(list[Event])
    result: list[Event]
    with open(r"tests\Analyst Server\SampleEventsOutputProcessed.txt", encoding='utf-8') as fp:
        f = fp.read()
        result = loader.validate_json(f)

    # small_sample = result[:3]

    [processed_events] = await asyncio.gather(
        analyse_events(result)
    )

    for event in processed_events:
        print()
        print(f"The event << {event.event} >> has the following impacts:")

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
