from .Actors import Actor, ActorType
from .Article import Article
from .BaseModelClean import BaseModelClean as BaseModel
from .Validators import Between10p, Count

from enum import StrEnum
from pydantic import ConfigDict, Field

# pydantic is used to allow use of objects in mcp tools

class ActorEntry(BaseModel):
    # Ensure validation is carried out when details are added later
    model_config = ConfigDict(validate_assignment=True)

    name: str = Field(frozen=True)
    actor_type: ActorType = Field(frozen=True)
    occurences: Count = 1

    def __eq__(self, other) -> bool:
        if isinstance(other, ActorEntry):
            return self.name == other.name and self.actor_type == other.actor_type
        return False

    def __hash__(self) -> int:
        return hash((self.name, self.actor_type))

    def inc_count(self, amt: int | None = None) -> None:
        if amt is None: amt = 1
        elif amt <= 0: raise ValueError(f"Count cannot increase by value {amt} <= 0")
        self.occurences += amt

class Severity(StrEnum):
    no_impact = "no_impact"
    low = "low"
    medium = "medium"
    high = "high"

class Impact(BaseModel):
    severity: Severity
    justification: str

class Event(BaseModel):
    # Ensure validation is carried out when details are added later
    model_config = ConfigDict(validate_assignment=True)

    # Fixed fields set upon creation, and unchanged after that
    event: str = Field(frozen=True)

    # Fields to be filled in later
    actors: list[ActorEntry] | None = None
    themes: list[str] | None = None
    source_articles: list[Article] | None = None
    source_events: list[str] | None = None  # This is a list of all events which got merged into this single event

    controversy: Between10p | None = None
    economic_impact: Impact | None = None
    financial_market_impact: Impact | None = None
    security_impact: Impact | None = None
    diplomatic_impact: Impact | None = None

    def __eq__(self, other) -> bool:
        if isinstance(other, Event):
            return self.event == other.event
        return False

    def __hash__(self) -> int:
        return hash(self.event)

    def set_impacts(self,
                             e_sev: str, e_just: str,
                             f_sev: str, f_just: str,
                             s_sev: str, s_just: str,
                             d_sev: str, d_just: str) -> None:
        self.economic_impact = Impact(severity=Severity(e_sev), justification=e_just)
        self.financial_market_impact = Impact(severity=Severity(f_sev), justification=f_just)
        self.security_impact = Impact(severity=Severity(s_sev), justification=s_just)
        self.diplomatic_impact = Impact(severity=Severity(d_sev), justification=d_just)

    def set_controvercy(self, controversy: float) -> None:
        self.controversy = controversy

    def set_actors(self, actors: list[tuple[Actor, int]]) -> None:
        self.actors = []
        for actor, count in actors:
            self.actors.append(ActorEntry(
                name = actor.name, 
                actor_type = actor.actor_type, 
                occurences = count
            ))
