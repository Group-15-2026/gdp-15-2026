from ..config import config
from ..Entities.Article import Article
from ..Entities.Actors import Actor
from ..Entities.Events import Event, Impact, Severity
from ..LLMTools.chat_history import BaseResponseMarker, ChatHistory

from ollama import AsyncClient
import itertools
import logging
from pydantic import TypeAdapter, BaseModel
import asyncio

logger = logging.getLogger(__name__)


# Ollama LLM Setup
ollama_client = None
system_prompt_event_classification = """
Role: You are a Senior Geopolitical Risk Analyst and Event Classification Agent.

Input Data: All input fields are enclosed in tags.
    <event>: Description of the event.
    <economic_impact_severity>
    <financial_market_impact_severity>
    <security_impact_severity>
    <diplomatic_impact_severity>

Output Format: JSON object with only the following fields:
    economic_impact_justification
    financial_market_impact_justification
    security_impact_justification
    diplomatic_impact_justification
    
Task:
    Justification: Write a one-sentence justification (max 30 words) for the pre-determined severity of a specific geopolitical event based on the event text. 
    No Impact: If the severity level for a particular category is "no_impact", state "No material impact identified" for this category as your justification.
    Exclusivity: Output only the JSON object. Do not include introductory remarks, markdown prose, or "Here is your JSON."
    Format: Your response must be valid JSON.

Severity Level Guidance: 
    no_impact: The event has no relevance to this category.
    low: Localized impact, minor diplomatic friction, or temporary market volatility.
    medium: Regional impact, significant shifts in policy/trade, or prolonged instability.
    high: Global impact, systemic financial risk, large-scale conflict, or permanent alliance shifts.

Categories:
    Economic: Trade disruptions, sanctions, supply chain integrity, commodity price exposure, and GDP growth outlook.
    Financial Markets: Foreign exchange (FX) volatility, equity sector exposure, sovereign debt default risk, and central bank monetary policy shifts.
    Security: Military escalation/mobilization, terrorism, state-sponsored cyber threats, and regional physical stability.
    Diplomatic: Shifts in formal alliances, international organization responses (UN, NATO, EU, etc.), and the likelihood of new multilateral sanctions.
"""

# ? should this use the event class directly
class EventJustificationOutput(BaseModel):
    economic_impact_justification: str
    financial_market_impact_justification: str
    security_impact_justification: str
    diplomatic_impact_justification: str

JustificationBatchResponse = TypeAdapter(list[EventJustificationOutput])

# Class that evaluates the validity of the classification-LLM 's response
class EventJustificationResponseMarker(BaseResponseMarker):
    def __init__(self):
        self.validEvents = []

    def mark(self, response: str) -> str | None:
        message = None

        try:
            output_obj = JustificationBatchResponse.validate_json(response)
        except Exception as e:
            message = "Your previous response failed to output correct JSON. Rewrite your previous response in valid JSON. " \
            f"based off of the following error: {e}."
        else:
            # TODO: perform further validation on output_obj and if it fails set a meaningful message
            for ej in output_obj:
                self.validEvents.append(ej)
        return message
    
    def get_correct(self) -> str:
        response = JustificationBatchResponse.dump_json(self.validEvents).decode("utf-8")
        self.validEvents = []
        return response


# Assume impact scores already populated in events.
async def impact_justifications(events: list[Event]) -> list[Event]:
    global ollama_client
    # setup link to LLM
    if ollama_client is None:
        logger.info("Attempting to set up new Ollama AsyncClient.")
        ollama_client = AsyncClient()
        logger.info("Ollama AsyncClient created successfully.")

    response_marker = EventJustificationResponseMarker()
    chat_history = ChatHistory(
        ollama_client, 
        model = config.MODEL,
        system_prompt = system_prompt_event_classification,
        json = JustificationBatchResponse.json_schema(),
        context = config.CONTEXT,
        tools = [ollama_client.web_search, ollama_client.web_fetch], # ? should this be here
        allowed_attempts = "inf",       # we need a valid JSON output, so must allow for infinite attempts
        response_marker = response_marker
    )
    

    processed_events: list[Event] = []
    # process events in batches
    for batch in itertools.batched(events, config.A_EVE_BATCH_SIZE):
        processed_batch = []
        for event in batch:            
            assert event.economic_impact and event.financial_market_impact
            assert event.security_impact and event.diplomatic_impact
            user_query = f"<event>{event.event}</event>"
            user_query += f" <economic_impact_severity>{event.economic_impact.severity}</economic_impact_severity>"
            user_query += f" <financial_market_impact_severity>{event.financial_market_impact.severity}</financial_market_impact_severity>"
            user_query += f" <security_impact_severity>{event.security_impact.severity}</security_impact_severity>"
            user_query += f" <diplomatic_impact_severity>{event.diplomatic_impact.severity}</diplomatic_impact_severity>"

            processed_batch.append(user_query)
        output = await chat_history.chat(f"Event severity values: {processed_batch}")
        output_obj: list[EventJustificationOutput] = JustificationBatchResponse.validate_json(output)

        for (event, output) in zip(batch, output_obj):
            assert event.economic_impact and event.financial_market_impact
            assert event.security_impact and event.diplomatic_impact

            event.set_impacts(
                event.economic_impact.severity, output.economic_impact_justification,
                event.financial_market_impact.severity, output.financial_market_impact_justification,
                event.security_impact.severity, output.security_impact_justification,
                event.diplomatic_impact.severity, output.diplomatic_impact_justification
            )

            processed_events.append(event)

    return processed_events


# Assume articles and claims are populated.
async def impact_serverities(events: list[Event]) -> list[Event]:
    for event in events:
        assert (event.source_articles != None)

        all_related_claims = []

        for article in event.source_articles:
            assert (article.claims != None)

            all_related_claims += article.claims


        # TODO: extract structured indicators from article titles and claims using an LLM:
        raise NotImplementedError()


        # TODO: rules based system to these indicators to get an overall severity ranking:
        raise NotImplementedError()


        # set severity values
        event.economic_impact.severity = economic_impact_severity
        event.financial_market_impact.severity = financial_market_impact_severity
        event.security_impact.severity = security_impact_severity
        event.diplomatic_impact.severity = diplomatic_impact_severity

    return events
