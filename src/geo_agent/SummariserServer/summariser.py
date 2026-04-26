from ..config import config
from ..Entities.Article import Article
from ..Entities.Actors import Actor, ActorType
from ..Entities.Events import Event

from collections import Counter
import json
from mcp.server.fastmcp import FastMCP
from ollama import AsyncClient
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

# ---------------------------------------------- extract_act_eve ------------------------------------------- #

'''
# SpaCy NLP Setup
nlp = None
relevant_entity_labels = {"GPE", "LAW", "NORP", "ORG", "PERSON"}

# Ollama LLM Setup
ollama_client = None
classification_system_prompt = [
    {"role": "system", "content": 
        "You are a geopolitical actor classification agent. Given a list of input actors and their "
        f"initial labels, you should classify each of the actors into one of {[role.value for role in ActorType]}, and nothing else!"
        "In general the label GPE should lead to a 'country' classification, ORG to a company, NORP a political party, and a PERSON "
        "should be one of a politician, celebrity, ceo or other - use your best judgement however."
        "If you don't believe a name to be a valid actor, then you omit them from the output. If a "
        "name which is a shortening of a previous name in your conversation history (or the batch list) "
        "is encountered, then treat is as the full name, and give the same classification as "
        "you gave previously. You will be given batches of up to 10 actor / label pairs at a time, "
        "and must reply with only a JSON object where the keys are the valid actor names, and the keys "
        "are the classifications that you have given them. The first thing that you should check is "
        "whether each name refers to a previously processed actor, and if so, to recall the previous "
        "classification. Always end by checking that the keys are only one of the "
        f"following: {[role.value for role in ActorType]}, and NOT any of the labels passed in."
    }
]

# The tool acts as an independent client to the same local Ollama instance as the orchestrator  (saving memory)
async def classify_actor(
        batch: list[tuple[str, str]], 
        history: list[dict[str, str]] = classification_system_prompt
    ) -> list[tuple[str, ActorType]]:

    async def get_response(messages: list[dict[str, str]], new_message: str, record=True) -> str:
        global ollama_client

        if ollama_client is None:
            ollama_client = AsyncClient()

        messages.append(
            {
                "role": "user", 
                "content": new_message
            }
        )
        response = await ollama_client.chat(
            model=config.MODEL, 
            messages=history,
            format="json",
            options={
                "num_ctx": 8 * 1024     # extend context to allow the whole article, and history to be read
            }
        )
        output = response.message.content or "{}"
        if record:
            messages.append(
                {"role": "assistant", "content": output}
            )
        return output
    
    output = await get_response(history, f"(Actor, Label) pairs: {batch}", record=False)

    # allow the model to try and correct itself
    allowed_names = set(name for name, label in batch)
    output_list : list[tuple[str, ActorType]] = []
    history_copy = history.copy()   # avoid clogging context with mistakes
    history_copy.append(
        {"role": "assistant", "content": output}
    )
    while True:
        try:
            output_dict = json.loads(output)
        except Exception as e:
            message=f"Your previous response failed to output correct JSON. Rewrite your previous response in valid JSON."
            output = await get_response(history_copy, message)
        else:        
            erroneous = []
            for k, v in output_dict.items():
                try:
                    assert k in allowed_names, "Cannot invent new actor names!!!"
                    v2 = ActorType(v)
                except Exception as e:
                    erroneous.append((k, v, repr(e)))
                else:
                    output_list.append((k, v2))
            if len(erroneous) > 0:
                message = f"Your previous response didn't adhere to the strict instruction to only classify actors as one of " \
                f"{[role.value for role in ActorType]}. Reclassify the following list of tuples of format (name, ai label, error): " \
                f"{erroneous}, returning a JSON object with keys of the actor names, and values of their classifications."

                #print(f"\n\n{history_copy}\n\n{output}\n\n{erroneous}\n\n")     # XX testing

                output = await get_response(history_copy, message)
            else: 
                # update the conversation context with the correct response
                history.append(
                    {
                        "role": "assistant",
                        "content": json.dumps(dict((k, v.value) for (k, v) in output_list))
                    }
                )
                break
            
    return output_list
'''

@summariser_mcp.tool()
async def extract_act_eve(articles: list[Article]) -> tuple[list[Article], list[Actor], list[Event]]:
    '''
    global nlp
    
    # Extract Actors
    # XX extract article_texts using SQL DB
    # XX for now, the MVP adds an extra field to address this
    article_texts = [article.text_body for article in articles]
    
    # avoid memory intensive load unless necessary
    if nlp is None:
        nlp = spacy.load(
            "en_core_web_trf",
            disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]   # remove memory/compute intensive, unused parts  
        )
    
    actors = Counter()

    # avoid leaking/storing new vocab between batches
    with nlp.memory_zone():
        for doc, article in zip(nlp.pipe(article_texts, batch_size=50), articles):
            doc_actors = Counter()
            actor_types = {}
            actor_batch = []
            classifier_convo_context = classification_system_prompt
            for ent in doc.ents:
                if ent.label_ in relevant_entity_labels:
                    # check classification cache first
                    if ent.text not in actor_types:
                        actor_batch.append((ent.text, ent.label_))
                        if len(actor_batch) == config.S_ACT_BATCH_SIZE:
                            batch = await classify_actor(actor_batch, history=classifier_convo_context)
                            actor_batch = []
                        else:
                            continue        # wait to process on a future iteration
                    else: 
                        batch = [(ent.text, actor_types[ent.text])]
                    for actor_tuple in batch:
                        doc_actors[actor_tuple] += 1
            if len(actor_batch) > 0:
                batch = await classify_actor(actor_batch, history=classifier_convo_context)
                for actor_tuple in batch:
                    doc_actors[actor_tuple] += 1
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
    '''

    from .classification import classify_article_actors
    from .extraction import extract_actors

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