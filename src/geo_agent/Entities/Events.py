from .Actors import Actor, ActorType
from .Article import Article
from .Validators import Between10p, Count

from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field

# pydantic is used to allow use of objects in mcp tools

class _ActorEntry(BaseModel):
    # Ensure validation is carried out when details are added later
    model_config = ConfigDict(validate_assignment=True)

    name: str = Field(frozen=True)
    actor_type: ActorType = Field(frozen=True)
    occurences: Count = 1

    def inc_count(self, amt: int | None = None) -> None:
        if amt is None: amt = 1
        elif amt <= 0: raise ValueError(f"Count cannot increase by value {amt} <= 0")
        self.occurences += amt

class _Severity(StrEnum):
    no_impact = "no_impact"
    low = "low"
    medium = "medium"
    high = "high"

class _Impact(BaseModel):
    severity: _Severity = _Severity.no_impact
    justification: str = ""

class Event(BaseModel):
    # Ensure validation is carried out when details are added later
    model_config = ConfigDict(validate_assignment=True)

    # Fixed fields set upon creation, and unchanged after that
    event: str = Field(frozen=True)

    # Fields to be filled in later
    actors: list[_ActorEntry] | None = None
    themes: list[str] | None = None
    source_articles: list[Article] | None = None

    controversy: Between10p | None = None
    economic_impact: _Impact = _Impact()
    financial_market_impact: _Impact =  _Impact()
    security_impact: _Impact = _Impact()
    diplomatic_impact: _Impact =  _Impact()

    # TODO may need breaking up into different methods for filling in at different times
    def set_processed_values(self,
                             controversy: float,
                             e_sev: str, e_just: str,
                             f_sev: str, f_just: str,
                             s_sev: str, s_just: str,
                             d_sev: str, d_just: str) -> None:
        self.controversy = controversy
        self.economic_impact = _Impact(severity=_Severity(e_sev), justification=e_just)
        self.financial_market_impact = _Impact(severity=_Severity(f_sev), justification=f_just)
        self.security_impact = _Impact(severity=_Severity(s_sev), justification=s_just)
        self.diplomatic_impact = _Impact(severity=_Severity(d_sev), justification=d_just)

    def set_actors(self, actors: list[tuple[Actor, int]]) -> None:
        self.actors = []
        for actor, count in actors:
            self.actors.append(_ActorEntry(
                name = actor.name, 
                actor_type = actor.actor_type, 
                occurences = count
            ))
