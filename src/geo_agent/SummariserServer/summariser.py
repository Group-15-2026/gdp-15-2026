from ..Entities.Article import Article, ClaimEntry
from ..Entities.Actors import Actor
from ..Entities.Events import Event

from .classification import classify_article_actors
from .extraction import extract_actors, extract_article_events, extract_article_claims

import asyncio
from mcp.server.fastmcp import FastMCP

summariser_mcp = FastMCP(name="Summariser MCP Server")

# TODO Implement remaining tools, and add informative docstrings to the tools

@summariser_mcp.tool()
def summarise_batch(articles: list[Article]) -> list[Article]:
    raise NotImplementedError()

# TODO Integrate this into the extract_events tool as well
#@summariser_mcp.tool()
#def tag_article_categories(articles: list[Article]) -> list[Article]:
#    raise NotImplementedError()

@summariser_mcp.tool()
async def extract_events(articles: list[Article]) -> tuple[list[Actor], list[Event]]:
    # TODO Update this docstring to be consistent with the changed Entity behaviours (specifically whether the event objects have full 'actor' and 'source_articles' fields)
    '''
    Extracts the geopolitical actors, claims and events from a list of articles, classifies the actors, and
    updates the events with information on the actors and articles that they reference. The updated
    actors and events are then returned.

    You should only pass in article objects that have been outputted by the 'collect_articles' or 
    'search_news' tools, NOT articles that have already been processed.
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
    # TODO Merge events between articles, and make sure the final events have the correct 'source_articles' field values
    events = []
    for article, actor_counter, actor_clss in actors_by_article:
        # Speed up processing by performing concurrent LLM calls
        [classified_actors, doc_events] = await asyncio.gather(
            classify_article_actors(actor_counter, actor_clss),
            extract_article_events(article)
        )
        
        actors += [actor for actor, _ in classified_actors]

        # TODO Link actors mentioned into the events
        for event in doc_events:
            event.source_articles = [article]
        events += doc_events

    return actors, events

if __name__ == "__main__":
    summariser_mcp.run()
