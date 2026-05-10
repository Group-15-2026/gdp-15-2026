from geo_agent.Entities.Events import Event
from geo_agent.SummariserServer.summariser import ExtractEventsResult
from geo_agent.SummariserServer.combination import combine_all_events

import asyncio
from utils import setup

def get_sample_events() -> list[Event]:
    raw = ""
    with open("tests/SummariserServer/SampleEventsOutputProcessed.json", "r", encoding="utf-8") as f:
        for line in f:
            raw += line
    return ExtractEventsResult.model_validate_json(raw).events

async def main():
    setup()

    events = get_sample_events()

    combined_events = await combine_all_events(events)

    for event in events:
        print(event.event, [a.article_title for a in (event.source_articles or [])])

    print("\n" * 10)

    for event in combined_events:
        print(event.event, event.source_events)

if __name__ == "__main__":
    asyncio.run(main())