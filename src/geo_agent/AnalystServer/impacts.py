from ..Entities.Article import Article
from ..Entities.Actors import Actor
from ..Entities.Events import Event, _Impact, _Severity

from ollama import AsyncClient
from pydantic import BaseModel
import asyncio

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

# TODO This should probably use the event class directly
class EventJustificationOutput(BaseModel):
    economic_impact_justification: str
    financial_market_impact_justification: str
    security_impact_justification: str
    diplomatic_impact_justification: str


# Assume articles and claims are populated.
async def event_impact_serverity(event: Event) -> Event:
    assert (event.source_articles != None)

    all_related_claims = []

    for article in event.source_articles:
        assert (article.claims != None)

        all_related_claims += article.claims

    economic_impact_severity = _Severity.no_impact
    financial_market_impact_severity = _Severity.no_impact
    security_impact_severity = _Severity.no_impact
    diplomatic_impact_severity = _Severity.no_impact

    # TODO: extract structured indicators from article titles and claims using an LLM:
    raise NotImplementedError()


    # TODO: rules based system to these indicators to get an overall severity ranking:
    raise NotImplementedError()


    # set severity values
    event.economic_impact.severity = economic_impact_severity
    event.financial_market_impact.severity = financial_market_impact_severity
    event.security_impact.severity = security_impact_severity
    event.diplomatic_impact.severity = diplomatic_impact_severity

    return event

# ! This fails silently if the first 5 attempts don't succeed. This is part of why it's important to transition to the ChatHistory Class
# TODO The below should be updated to use the ChatHistory class, instead of calling ollama directly
# Assume impact scores already populated in events.
async def get_justification(event: Event) -> Event:
    global ollama_client
    if ollama_client is None:
        ollama_client = AsyncClient()

    user_query = f"<event>{event.event}</event>"
    user_query += f" <economic_impact_severity>{event.economic_impact.severity}</economic_impact_severity>"
    user_query += f" <financial_market_impact_severity>{event.financial_market_impact.severity}</financial_market_impact_severity>"
    user_query += f" <security_impact_severity>{event.security_impact.severity}</security_impact_severity>"
    user_query += f" <diplomatic_impact_severity>{event.diplomatic_impact.severity}</diplomatic_impact_severity>"

    for _ in range(5):
        try:
            response = await ollama_client.chat(
                model='gemma4:e4b',
                messages=[
                    {'role': 'system', 'content': system_prompt_event_classification},
                    {'role': 'user', 'content': user_query}
                ],
                format=EventJustificationOutput.model_json_schema(),
            )

            output = EventJustificationOutput.model_validate_json(response.message.content or "")
        except:
            response = await ollama_client.chat(
                model='gemma4:e4b',
                messages=[
                    {'role': 'system', 'content': system_prompt_event_classification},
                    {'role': 'user', 'content': user_query}
                ],
                format=EventJustificationOutput.model_json_schema(),
            )

            output = EventJustificationOutput.model_validate_json(response.message.content or "")
        else:
            event.economic_impact.justification = output.economic_impact_justification
            event.diplomatic_impact.justification = output.diplomatic_impact_justification
            event.financial_market_impact.justification = output.financial_market_impact_justification
            event.security_impact.justification = output.security_impact_justification
            break
    
    return event