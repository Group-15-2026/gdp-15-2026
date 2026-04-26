from ..config import config
from ..Entities.Article import Article
from ..Entities.Actors import Actor
from ..Entities.Events import Event

from .classification import classify_article_actors
from .extraction import extract_actors

from mcp.server.fastmcp import FastMCP

summariser_mcp = FastMCP(name="Summariser MCP Server")

# XX Note to implementer: some of the below tools may be combined together depending on implementation
# may also only pass unique articles IDs to tools, and the articles can then be collected from central DB

@summariser_mcp.tool()
def summarise_batch(articles: list[Article]) -> list[Article]:
    return NotImplemented

@summariser_mcp.tool()
def score_sentiment(articles: list[Article]) -> list[Article]:
    return NotImplemented

@summariser_mcp.tool()
def tag_themes(articles: list[Article]) -> list[Article]:
    return NotImplemented

@summariser_mcp.tool()
async def extract_act_eve(articles: list[Article]) -> tuple[list[Article], list[Actor], list[Event]]:
    actors_by_article = extract_actors(articles)
    actors = []
    for article, actor_counter, actor_clss in actors_by_article:
        classified_actors = await classify_article_actors(actor_counter, actor_clss)
        article.set_actors(classified_actors)
        actors += [actor for actor, _ in classified_actors]

    # XX TODO: implement, in the extraction.py and classification.py files
    events = []

    return (articles, actors, events)

if __name__ == "__main__":
    summariser_mcp.run()