from ..Entities.Article import Article
from ..Entities.Actors import Actor, ActorType
from ..Entities.Events import Event

from collections import Counter
from mcp.server.fastmcp import FastMCP
import spacy

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

nlp = None
relevant_entity_labels = {"GPE", "LAW", "MONEY", "NORP", "ORG", "PERSON"}
simple_map = {
    "GPE": ActorType.country,
    "ORG": ActorType.company,
    "PERSON": ActorType.celebrity,  # XX actually inaccurate as well as simple
}
def classify_actor(name: str, label: str) -> ActorType:
    # XX This is very simple - simpler than the MVP
    # XX The task 'Event categorisation (prompt engineering) implementation' should extend it
    return simple_map.get(label, ActorType.other)

@summariser_mcp.tool()
def extract_act_eve(articles: list[Article]) -> tuple[list[Article], list[Actor], list[Event]]:
    global nlp
    
    # Extract Actors
    # XX extract article_texts using SQL DB
    # XX for now, the MVP adds an extra field to address this
    article_texts = [article.text_body for article in articles]

    actors = Counter()
    actor_types = {}
    if nlp is None:         # avoid memory intensive load unless necessary
        nlp = spacy.load(
            "en_core_web_trf",
            disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]   # remove memory/compute intensive, unused parts  
        )
    with nlp.memory_zone():     # avoid leaking/storing new vocab between batches
        for doc, article in zip(nlp.pipe(article_texts, batch_size=50), articles):
            doc_actors = Counter()
            for ent in doc.ents:
                if ent.label_ in relevant_entity_labels:
                    key = (ent.text, ent.label_)
                    if key not in actor_types:
                        actor_types[key] = classify_actor(*key)
                    doc_actors[(ent.text, actor_types[key])] += 1
            article.set_actors(doc_actors)
            actors += doc_actors
    
    actors_objs = []
    for actor in actors:
        (name, type_) = actor
        actors_objs.append(Actor(name=name, actor_type=type_))

    # Extract Events
    # XX Still to be implemented
    events = []

    return (articles, actors_objs, events)

# XX Note: may or may not be necessary depending on how MCP client is implemented
if __name__ == "__main__":
    summariser_mcp.run()