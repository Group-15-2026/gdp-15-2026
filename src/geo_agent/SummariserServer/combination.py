from ..config import config
from ..Entities.Actors import Actor
from ..Entities.Events import Event, ActorEntry
from ..Entities.Validators import length_between
from ..LLMTools.chat_history import BaseResponseMarker, ChatHistory

from collections import Counter
import itertools
import logging
from ollama import AsyncClient
from pydantic import BaseModel, TypeAdapter, Field, AfterValidator
import random
from typing import Annotated, Any

logger = logging.getLogger(__name__)

# --------------------------------------- event-actor linking ---------------------------------------- #

# TODO May never implement 'identify_event_actors' ...
# ! NOT a priority?
# From the actors extracted from the article the event came from, identify the ones relevant to the event
async def identify_event_actors(event: Event, actors: list[Actor]) -> list[ActorEntry]:
    raise NotImplementedError()

# --------------------------------------- event-event linking ---------------------------------------- #

# Ollama LLM Setup
ollama_client = None

def union_actors(actor_lists: list[list[ActorEntry]]) -> list[ActorEntry]:
    output: Counter[ActorEntry] = Counter()
    for list_ in actor_lists:
        for actor in list_:
            output[actor] += actor.occurences   # sum occurences across inter-article actor duplicates
    return [ActorEntry(
        name = actor.name,
        actor_type = actor.actor_type,
        occurences = output[actor]
    ) for actor in output]

def union_lists(lists: list[list[Any]]) -> list[Any]:
    output = set()
    for list_ in lists:
        output = output.union(set(list_))
    return list(output)

# Combine multiple event objects (from different articles) into a single combined event object (referencing all source articles correctly)
def combine_dup_events(events: list[Event], target_event_name: str) -> Event:
    actors = union_actors([event.actors or [] for event in events])
    themes = union_lists([event.themes or [] for event in events])
    source_articles = union_lists([event.source_articles or [] for event in events])
    source_events = union_lists([event.source_events or [event.event] for event in events]) 

    return Event(
        event = target_event_name,

        actors = actors if actors else None,
        themes = themes if themes else None,
        source_articles = source_articles if source_articles else None,
        source_events = source_events
    )

# Type that represents the model's target output for combination
class CombineEventForm(BaseModel):
    source_events: Annotated[list[str], AfterValidator(length_between(1, None))] = Field(frozen=True)
    new_event: str = Field(frozen=True)

# Type that represents the model's target output for combination
EventCombineResponse = TypeAdapter(list[CombineEventForm])

# Class that evaluates the validity of the combination-LLM 's response
class EventCombineResponseMarker(BaseResponseMarker):
    max_word_count = config.EVENT_SIZE

    def __init__(self, events_by_names: dict[str, Event]):
        self.events_by_names = events_by_names
        self.validEventCombs: list[CombineEventForm] = []
        self.cur_batch_events: set[str] = set()

    def is_disjoint(self, event_combs: list[CombineEventForm]) -> bool:
        events = set(event for comb in self.validEventCombs for event in comb.source_events)
        for event_comb in event_combs:
            for source in event_comb.source_events:
                if source in events:
                    return False
                events.add(source)
        return True

    def mark(self, response: str) -> str | None:
        message = None

        try:
            output_obj = EventCombineResponse.validate_json(response)
        except Exception as e:
            message = "Your previous response failed to output correct JSON. Rewrite your previous response in valid JSON. " \
            f"based off of the following error: {e}."
        else:
            if not self.is_disjoint(output_obj):
                message = f"Your previous response failed to adhere to the instruction that a single event " \
                "should not be merged into different target events. The CombineEventForm objects should have " \
                "pairwise disjoint 'source_events' fields. Rewrite your last response to correct this issue. " \
                "Do not use reuse any events that you have previously merged!"
            else:
                renamed_events = []
                for event_comb in output_obj:
                    if any(event not in self.events_by_names for event in event_comb.source_events):
                        renamed_events.append(event_comb)
                    else:
                        self.validEventCombs.append(event_comb)  # extract correct objects
                        for event in event_comb.source_events:
                            self.cur_batch_events.remove(event)
                if len(renamed_events) > 0:
                    message = f"\nYour previous response failed to adhere to the strict instruction to copy " \
                    "events VERBATIM in the source_events field. Rewrite the following combination attempts " \
                    "using the verbatim event names listed previously in the source_events fields: " \
                    f"{renamed_events}. DO NOT rewrite any of the other merges from your last prompt. Only " \
                    "correct the merge-attempts in this message to use the correct source event names. The " \
                    f"events that you can reference as source_events are: {self.cur_batch_events}."

        return message
    
    def get_correct(self) -> str:
        response = EventCombineResponse.dump_json(self.validEventCombs).decode("utf-8")
        self.validEventCombs = []
        return response

event_combination_system_prompt = f'''
You are a geopolitical event aggregation expert. Given a batch of events, you must output a JSON list of 
CombineEventForm objects. They each must have a single 'source_events' field, which is a list of the events
that are duplicates of one another, and which are to be merged into a single event. The 'new_event' field 
indicates the name of the event that will be created from the merge - it should combine all aspects of the
event mentioned in all source events that are being merged, to be a fully informative stand alone event. 
You must repeat the input events that you wish to merge VERBATIM in 'source_events', so that they can be 
merged correctly. A separate tool will then merge them - DO NOT MERGE THEM YOURSELF. If an event in the 
input batch cannot be merged with any other events, just ignore it. 

Only input events which are about the exact same occurence should be merged. Do not just merge events which
share some of the same words. For example, "The USD devalues", and "The GBP devalues" are distinct events, 
and should NOT be merged. However "Today the US did X", and "The US did X today" SHOULD be merged, because
they are about the same event, they are simply worded differently.

When constructing the 'new_event' labels, do not simply concatenate the source events - instead produce 
a single, flowing event description which combines the narratives of each source event into one, complete
picture.

Finally, do not include any '```json' tags in your output, and make sure to return ONLY a JSON list (no 
enclosing '{{}}', or initial filler text). Always check this before producing your response.
'''.replace("\n", " ")

# Given all events, identify which ones can be combined. 'combine_dup_events' is then be used to actually perform this merging
async def combine_all_events(events: list[Event]) -> list[Event]:
    global ollama_client

    assert len(events) > 0, "Cannot combine an empty list of events"

    # setup link to LLM
    if ollama_client is None:
        logger.info("Attempting to set up new Ollama AsyncClient.")
        ollama_client = AsyncClient()
        logger.info("Ollama AsyncClient created successfully.")

    response_marker = EventCombineResponseMarker({event.event: event for event in events})
    chat_history = ChatHistory(
        ollama_client,
        model = config.MODEL,
        system_prompt=event_combination_system_prompt,
        json = EventCombineResponse.json_schema(),
        context = config.CONTEXT,
        allowed_attempts = "inf",
        response_marker = response_marker
    )

    i = 1
    still_merging = True
    final_batch_size: int | None = None     # finish with the full event list
    while still_merging:
        still_merging = False
        to_be_batched = list(response_marker.events_by_names.keys())
        random.shuffle(to_be_batched)   # shuffle randomly, to ensure we compare different events within a given batch
        for batch in itertools.batched(to_be_batched, final_batch_size or config.S_EVENT_MERGE_BATCH_SIZE):
            response_marker.cur_batch_events = set(batch)
            output = await chat_history.chat(
                f"Output any mergeable events from the following list of events: {batch}, or any events " \
                "that you have seen in a prior prompt, but not yet indicated to be merged. Don't be " \
                "afraid to return an empty list if no events are suitable for merging."
            )
            event_merges: list[CombineEventForm] = EventCombineResponse.validate_json(output)

            still_merging |= len(event_merges) > 0
            for merge in event_merges:
                # store the (output) merged events
                new_event = combine_dup_events([response_marker.events_by_names[event] for event in merge.source_events], merge.new_event)
                response_marker.events_by_names[new_event.event] = new_event

                logger.info(f"Merging the events {merge.source_events} into new event \"{merge.new_event}\"")

                # remove the events used as input to a merge
                for event in merge.source_events:
                    response_marker.events_by_names.pop(event)

            chat_history.clear_history()    # reset the chat history between iterations
        logger.info(f"Merged the {i}th iteration of events.")
        i += 1
        if (not still_merging) and not final_batch_size:
            still_merging = True
            final_batch_size = len(response_marker.events_by_names) # process all events (to make sure that no possible merges get missed)

    return list(response_marker.events_by_names.values())