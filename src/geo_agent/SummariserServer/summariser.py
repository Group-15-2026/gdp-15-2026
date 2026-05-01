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

@summariser_mcp.tool()
async def extract_claims(articles: list[Article]) -> list[Article]:
    '''
    Extracts the claims made by different articles, rate the opinion of a given article on the claims
    that it makes, and then update the article objects with the newly extracted and processed claims.
    '''
    for article in articles:
        claims: list[ClaimEntry] = await extract_article_claims(article)
        article.claims = claims
    return articles

@summariser_mcp.tool()
def tag_article_categories(articles: list[Article]) -> list[Article]:
    raise NotImplementedError()

@summariser_mcp.tool()
async def extract_actors_and_events(articles: list[Article]) -> tuple[list[Actor], list[Event]]:
    # TODO Update this docstring to be consistent with the changed Entity behaviours (specifically whether the event objects have full 'actor' and 'source_articles' fields)
    '''
    Extracts the geopolitical actors and events from a list of articles, classifies the actors, and
    updates the events with information on the actors and articles that they reference. The updated
    articles, actors and events are then returned.

    You should only pass in article objects that have been outputted by the 'collect_articles' or 
    'search_news' tools in the 'summariser' mcp server, NOT articles that have already been processed.
    '''

    # Extract actors + events
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
