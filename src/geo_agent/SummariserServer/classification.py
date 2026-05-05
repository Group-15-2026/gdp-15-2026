from ..config import config
from ..Entities.Actors import Actor, ActorType
from ..LLMTools.chat_history import BaseResponseMarker, ChatHistory

from collections import Counter
import itertools
import logging
from ollama import AsyncClient
from pydantic import TypeAdapter, BaseModel, Field

logger = logging.getLogger(__name__)

# --------------------------------------- actor classification --------------------------------------- #

# Ollama LLM Setup
ollama_client = None

classification_system_prompt = f'''
You are a geopolitical actor classification agent. Given a list of input actors and their
initial labels, you should classify each of the actors into one of {[role.value for role in ActorType]}, 
produce an appropriate Actor JSON object for each pair, and return a JSON list (no enclosing '{{}}') of these objects.
Examine the output schema format carefully, and note that you must fill in the 'name' and 'actor_type' fields only 
for each Actor object in the list. Do not use any '```json' tags in your output, only return the valid json list.
In general the initial label GPE should lead to a 'country' actor_type, ORG to a company, NORP a political party, and a PERSON
should be one of a politician, celebrity, ceo or other - use your best judgement however.
If you don't believe a name to be a valid actor, then you omit their associated object from the output list. If a
name which is a shortening of a previous name in your conversation history (or the batch list)
is encountered, then treat is as the full name, and give the same classification as
you gave previously. You will be given batches of up to 10 actor / label pairs at a time,
and must reply with only a JSON list with one object for each valid actor, which has keys for the valid actor names, and
the classifications that you have given them. The first thing that you should check is
whether each name refers to a previously processed actor, and if so, to recall the previous
classification, and use the extended name for the 'name' field in the relevant output object in the JSON list. 
This includes combining duplicates from within a single batch given in one prompt.
Always end by checking that the new actor_type field values are only one of the
following: {[role.value for role in ActorType]}, and NOT any of the initial labels passed in.
'''.replace("\n", " ")

# Remove bloat In 'Actor' that will only confuse the LLM
class ClassifiedActor(BaseModel):
    name: str = Field(frozen=True)
    actor_type: ActorType = Field(frozen=True)

    def to_full(self):
        return Actor(
            name=self.name, 
            actor_type=self.actor_type
        )

# type that represents the model's target output for batch classification
ActorClassBatchResponse = TypeAdapter(list[ClassifiedActor])

# Class that evaluates the validity of the classification-LLM 's response
class ActorClassResponseMarker(BaseResponseMarker):
    def __init__(self):
        #self.valid_names = set()
        self.validActors = []

    def mark(self, response: str) -> str | None:
        message = None

        try:
            output_obj = ActorClassBatchResponse.validate_json(response)
        except Exception as e:
            message = "Your previous response failed to output correct JSON. Rewrite your previous response in valid JSON. " \
            f"based off of the following error: {e}."
        # ! If the article has spelling mistakes, the LLM may never be able to output the mispelled actors. In general, the LLM does well enough that this anti-hallucination validation is not required at all, so it has been removed for now 
        else:
            for a in output_obj:
                self.validActors.append(a)        
        #else:
        #    erroneous = []
        #    for a in output_obj:
        #        if a.name not in self.valid_names:
        #            erroneous.append((a.name, a.actor_type.value, "Cannot invent new actor names!!!"))
        #        else:
        #            self.validActors.append(a)
        #    if len(erroneous) > 0:
        #        message = f"You cannot use the actor names {[name for (name, _, _) in erroneous]}, as they haven't appeared " \
        #        "before in the article. Rename the following list of actor tuples of format (name, ai label, error): " \
        #        f"{erroneous}, returning a JSON list of objects conforming to the output format defined in your system prompt. " \
        #        "You may ONLY use actor names from the set of actor names " \
        #        f"that have appeared so far, which is as follows: {self.valid_names}."
        
        return message
    
    def get_correct(self) -> str:
        response = ActorClassBatchResponse.dump_json(self.validActors).decode("utf-8")
        self.validActors = []
        return response
    
    #def reset(self):
    #    self.valid_names.clear()

# This function uses an independent client to the same local Ollama instance as the orchestrator (saving memory)
# It should be called on the complete set of raw actors for a single article (elements of 'extract_actors' output)
async def classify_article_actors(article_actors: Counter[str], article_actor_clss: dict[str, str]) -> list[tuple[Actor, int]]:
    global ollama_client

    # setup link to LLM
    if ollama_client is None:
        logger.info("Attempting to set up new Ollama AsyncClient.")
        ollama_client = AsyncClient()
        logger.info("Ollama AsyncClient created successfully.")

    response_marker = ActorClassResponseMarker()
    chat_history = ChatHistory(
        ollama_client, 
        model = config.MODEL,
        system_prompt = classification_system_prompt,
        json = ActorClassBatchResponse.json_schema(),
        context = config.CONTEXT,
        allowed_attempts = "inf",       # we need a valid JSON output, so must allow for infinite attempts
        response_marker = response_marker
    )
    
    # process actors in batches
    actors: Counter[str] = Counter()
    actor_lookup: dict[str, ClassifiedActor] = {}
    for batch in itertools.batched(article_actors, config.S_ACT_BATCH_SIZE):
        processed_batch = []
        for actor in batch:
            processed_batch.append((actor, article_actor_clss[actor]))
            #response_marker.valid_names.add(actor)
        output = await chat_history.chat(f"(Actor, Label) pairs: {processed_batch}")
        output_obj: list[ClassifiedActor] = ActorClassBatchResponse.validate_json(output)
        for actor in output_obj:
            actors[actor.name] += article_actors[actor.name]
            actor_lookup[actor.name] = actor
            
    return [(actor.to_full(), actors[name]) for name, actor in actor_lookup.items()]