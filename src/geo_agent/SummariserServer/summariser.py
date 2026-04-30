from ..Entities.Article import Article, _ClaimEntry
from ..Entities.Actors import Actor
from ..Entities.Events import Event

from .classification import classify_article_actors
from .extraction import extract_actors, extract_article_events, extract_article_claims

from mcp.server.fastmcp import FastMCP

summariser_mcp = FastMCP(name="Summariser MCP Server")

# XX Note to implementer: some of the below tools may be combined together depending on implementation
# may also only pass unique articles IDs to tools, and the articles can then be collected from central DB

@summariser_mcp.tool()
def summarise_batch(articles: list[Article]) -> list[Article]:
    return NotImplemented

@summariser_mcp.tool()
async def score_sentiment(articles: list[Article]) -> list[Article]:
    '''
    Extracts the claims made by different articles, rate the opinion of a given article on the claims
    that it makes, and then update the article objects with the newly extracted and processed claims.
    '''
    for article in articles:
        claims: list[_ClaimEntry] = await extract_article_claims(article)
        article.claims = claims
    return articles

@summariser_mcp.tool()
def tag_themes(articles: list[Article]) -> list[Article]:
    return NotImplemented

@summariser_mcp.tool()
async def extract_act_eve(articles: list[Article]) -> tuple[list[Actor], list[Event]]:
    # TODO Update this docstring to be consistent with the changed Entity behaviours (specifically whether the event objects have full 'actor' and 'source_articles' fields)
    '''
    Extracts the geopolitical actors and events from a list of articles, classifies the actors, and
    updates the articles with information on the actors and events that they reference. The updated
    articles, actors and events are then returned.

    You should only pass in article objects that have been outputted by the 'collect_articles' or 
    'search_news' tools in the 'summariser' mcp server, NOT articles that have already been processed.
    '''

    # Extract actors
    actors_by_article = extract_actors(articles)
    actors = []
    for article, actor_counter, actor_clss in actors_by_article:
        classified_actors = await classify_article_actors(actor_counter, actor_clss)
        #//article.set_actors(classified_actors)
        actors += [actor for actor, _ in classified_actors]

    # Extract events
    events = []
    # TODO Merge events between articles, and make sure the final events have the correct 'source_articles' field values
    for article in articles:
        doc_events = await extract_article_events(article)
        #//article.set_events(doc_events)
        for event in doc_events:
            event.source_articles = [article]
        events += [events]

    return (actors, events)

if __name__ == "__main__":
    summariser_mcp.run()
