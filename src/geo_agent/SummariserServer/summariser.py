from ..Entities.Article import Article, ClaimEntry
from ..Entities.Actors import Actor
from ..Entities.Events import Event

from .classification import classify_article_actors
from .combination import combine_all_events
from .extraction import extract_actors, extract_article_events, extract_article_claims

import asyncio
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from utils import setup_server_logging

setup_server_logging("summariser")

summariser_mcp = FastMCP(name="Summariser MCP Server")

class ExtractEventsResult(BaseModel):
    actors: list[Actor]
    events: list[Event]

@summariser_mcp.tool()
async def extract_events(articles: list[Article]) -> ExtractEventsResult:
    '''
    Extracts the geopolitical actors, claims and events from a list of articles, classifies the actors, and
    updates the events with information on the actors and articles that they reference. The updated
    actors and events are then returned.

    You should only pass in article objects that have been outputted by the 'collect_articles' or 
    'search_news' tools, NOT articles that have already been processed.

    Args:
        articles: The articles to process, and extract the events from. These should come from one of the 'collect_articles' or 'search_news' tools
    '''

    # Extract Article Claims (concurrently if possible)
    all_claims: list[list[ClaimEntry]] = await asyncio.gather(
        *(extract_article_claims(article) for article in articles)
    )
    for article, claims in zip(articles, all_claims):
        article.claims = claims

    # Extract Actors + Events
    actors_by_article = extract_actors(articles)
    actors = []
    events = []
    for article, actor_counter, actor_clss in actors_by_article:
        # Speed up processing by performing concurrent LLM calls
        [classified_actors, doc_events] = await asyncio.gather(
            classify_article_actors(actor_counter, actor_clss),
            extract_article_events(article)
        )
        
        actors += [actor for actor, _ in classified_actors]

        for event in doc_events:
            event.source_articles = [article]   # This is expanded below when we merge duplicates

            # TODO Link actors mentioned into the events (may never be implemented - see combination.py)
            # event.actors = identify_event_actors(event, doc_actors) # doc_actors = [actor for actor, _ in classified_actors]
        events += doc_events

    if len(events) > 0:
        events = await combine_all_events(events)

    return ExtractEventsResult(actors=actors, events=events)

if __name__ == "__main__":
    summariser_mcp.run()
