from ..config import config
from ..Entities.Article import Article, _ClaimEntry
from ..Entities.Events import Event
from ..LLMTools.chat_history import BaseResponseMarker, ChatHistory

from collections import Counter
import logging
from ollama import AsyncClient
from pydantic import TypeAdapter
import spacy

logger = logging.getLogger(__name__)

# ----------------------------------------- actor extraction ----------------------------------------- #

# SpaCy NLP Setup
nlp = None
relevant_entity_labels = {"GPE", "LAW", "NORP", "ORG", "PERSON"}

# XX merge labels for duplicated actors (preferring anything other than 'other')

def extract_actors(articles: list[Article]) -> list[tuple[Article, Counter[str], dict[str, str]]]:
    global nlp
    
    # Extract Actors
    # XX extract article_texts using SQL DB
    # XX for now, the MVP adds an extra field to address this
    article_texts = (article.get_text_body() for article in articles)
    
    # avoid memory intensive load unless necessary
    if nlp is None:
        nlp = spacy.load(
            "en_core_web_trf",
            disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]   # remove memory/compute intensive, unused parts  
        )
    
    actors: list[tuple[Article, Counter[str], dict[str, str]]] = [] # (source_article_id, actor_counter) members

    # avoid leaking/storing new vocab between batches
    with nlp.memory_zone():
        for doc, article in zip(nlp.pipe(article_texts, batch_size=50), articles):
            doc_actors = Counter[str]()
            doc_actor_clss: dict[str, str] = {}
            for ent in doc.ents:
                if ent.label_ in relevant_entity_labels:
                    doc_actors[ent.text] += 1
                    if ent.text not in doc_actor_clss:
                        doc_actor_clss[ent.text] = ent.label_
                    # we will assume that different occurrences of the same actor in an article get the same spacy class (and so use first one as canonical)
            actors.append((article, doc_actors, doc_actor_clss))

    return actors

# ----------------------------------------- event extraction ----------------------------------------- #

# Ollama LLM Setup
ollama_client = None

event_extraction_system_prompt = f'''
You are a geopolitical event extraction agent. Given an article, you must output a JSON list of event
objects corresponding to events that the article covers as having occurred. The description of an event
should be 10 words or less, and as precise as possible, using geopolitical language. Only include events
which you believe to be relevant to geopolitics (it's okay if the link is strenuous), and do not include
any repeats of the same event. Only the 'event' field of each object in your output list should be 
populated. Do not include any '```json' tags in your output, and make sure to return a JSON list (no 
enclosing '{{}}').
'''.replace("\n", " ")

# type that represents the model's target output for extraction
EventExtractResponse = TypeAdapter(list[Event])

# Class that evaluates the validity of the classification-LLM 's response
class EventExtractResponseMarker(BaseResponseMarker):
    def __init__(self):
        self.max_word_count = 10

    def mark(self, response: str) -> str | None:
        message = None

        try:
            output_obj = EventExtractResponse.validate_json(response)
        except Exception as e:
            message = "Your previous response failed to output correct JSON. Rewrite your previous response in valid JSON."
        else:
            too_long = []
            for event in output_obj:
                if len(event.event.split(" ")) > self.max_word_count:
                    too_long.append(event.event)
            if len(too_long) > 0:
                message = f"Your previous response failed to adhere to the strict instruction that all event descriptions " \
                f"should be at most {self.max_word_count} words long. In particular, the following description were too long: " \
                f"{too_long}. Correct these overly long events in your previous response, leaving the events that are already " \
                "short enough unchanged."
        return message

async def extract_article_events(article: Article) -> list[Event]:
    global ollama_client

    # setup link to LLM
    if ollama_client is None:
        logger.info("Attempting to set up new Ollama AsyncClient.")
        ollama_client = AsyncClient()
        logger.info("Ollama AsyncClient created successfully.")

    response_marker = EventExtractResponseMarker()
    chat_history = ChatHistory(
        ollama_client,
        model = config.MODEL,
        system_prompt = event_extraction_system_prompt,
        json = EventExtractResponse.json_schema(),
        context = 4 * 1024,
        allowed_attempts = "inf",
        response_marker = response_marker
    )

    # extract article events
    text_body = article.get_text_body()
    output = await chat_history.chat(f"Extract the events in the article \"{article.article_title}\": {text_body}")
    events: list[Event] = EventExtractResponse.validate_json(output)
    
    return events

# ----------------------------------------- claim extraction ----------------------------------------- #

# type that represents the model's target output for extraction
ClaimExtractResponse = TypeAdapter(list[_ClaimEntry])

# Class that evaluates the validity of the classification-LLM 's response
class ClaimExtractResponseMarker(BaseResponseMarker):
    max_word_count = 10

    def mark(self, response: str) -> str | None:
        message = None

        try:
            output_obj = ClaimExtractResponse.validate_json(response)
        except Exception as e:
            message = "Your previous response failed to output correct JSON. Rewrite your previous response in valid JSON. " \
            f"based off of the following error: {e}."
        else:
            too_long = []
            for claim in output_obj:
                if len(claim.claim.split(" ")) > self.max_word_count:
                    too_long.append(claim.claim)
            if len(too_long) > 0:
                message = f"Your previous response failed to adhere to the strict instruction that all claims " \
                f"should be at most {self.max_word_count} words long. In particular, the following description were too long: " \
                f"{too_long}. Correct these overly long claims in your previous response, leaving the claims that are already " \
                "short enough unchanged."
        return message

claim_extraction_system_prompt = f'''
You are a geopolitical claim extraction agent. Given an article, you must output a JSON list of _ClaimEntry
JSON objects corresponding to claims that the article makes. Each claim should be 
{ClaimExtractResponseMarker.max_word_count} words or less, and as 
simply worded as possible. Each claim should get a rating from -10 to 10 scoring the article's 'opinion' on
the claim (10 = strongly agree, -10 = strongly disagree). Only include claims which you believe to be 
relevant to geopolitics (it's okay if the link is strenuous), and do not include any repeats of the same 
claim within a given article. Note that inverted claims are still the same claim (e.g. "X caused Y" vs 
"X did not cause Y"). Only include a claim if it is controversial or opinionated in some way: 
"dogs are animals" is not a controversial claim. Only the 'claim' and 'opinion' fields of each object 
in your output list should be populated. Do not include any '```json' tags in your output, and make sure 
to return a JSON list (no enclosing '{{}}').
'''.replace("\r\n", " ").replace("\n", " ")

async def extract_article_claims(article: Article) -> list[_ClaimEntry]:
    global ollama_client

    # setup link to LLM
    if ollama_client is None:
        logger.info("Attempting to set up new Ollama AsyncClient.")
        ollama_client = AsyncClient()
        logger.info("Ollama AsyncClient created successfully.")

    response_marker = ClaimExtractResponseMarker()
    chat_history = ChatHistory(
        ollama_client,
        model = config.MODEL,
        system_prompt = claim_extraction_system_prompt,
        json = ClaimExtractResponse.json_schema(),
        context = 4 * 1024,
        allowed_attempts = "inf",
        response_marker = response_marker
    )

    # extract article claims
    text_body = article.get_text_body()
    output = await chat_history.chat(f"Extract the claims in the article \"{article.article_title}\": {text_body}")
    claims: list[_ClaimEntry] = ClaimExtractResponse.validate_json(output)
    
    return claims