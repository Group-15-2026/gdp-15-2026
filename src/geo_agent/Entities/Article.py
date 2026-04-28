from .Actors import Actor, ActorType
from .Events import Event
from .Validators import Between10, Count

from collections import Counter
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field

# pydantic is used to allow use of objects in mcp tools

class _Source(BaseModel):
    source_id: str = Field(frozen=True)
    source_name: str = Field(frozen=True)

class ArticleType(StrEnum):
    conflict = "conflict"
    politics = "politics"
    tragedy = "tragedy"
    crime = "crime"
    product_review = "product review"
    advice = "advice"
    finance = "finance"

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

class _ClaimEntry(BaseModel):
    claim: str = Field(frozen=True)
    opinion: Between10 = Field(frozen=True)

class Article(BaseModel):
    # Ensure validation is carried out when details are added later
    model_config = ConfigDict(validate_assignment=True)

    # Fixed fields set upon creation, and unchanged after that
    article_id: str = Field(frozen=True)
    article_title: str = Field(frozen=True)
    publication_time: datetime = Field(frozen=True)
    source: _Source = Field(frozen=True)

    # XX This has been temporarily added for MVP, to avoid full DB
    text_body: str = Field(frozen=True)

    # Fields to be filled in later
    initial_categories: list[ArticleType] | None = None
    actors: list[_ActorEntry] | None = None
    events: list[str] | None = None
    claims: list[_ClaimEntry] | None = None
    themes: list[str] | None = None

    # XX may need breaking up into different methods for filling in at different times (see set_actors)
    def set_processed_values(self,
                             initial_categories: list[str],
                             actors: list[tuple[str, str, int]],
                             events: list[str],
                             claims: list[tuple[str, float]],
                             themes: list[str]) -> None:
        self.initial_categories = [ArticleType(at) for at in initial_categories]
        self.actors = [_ActorEntry(name=n, actor_type=ActorType(at), occurences=occ) for (n, at, occ) in actors]
        self.events = events
        self.claims = [_ClaimEntry(claim=c, opinion=o) for (c, o) in claims]
        self.themes = themes

    def set_actors(self, actors: list[tuple[Actor, int]]) -> None:
        self.actors = []
        for actor, count in actors:
            self.actors.append(_ActorEntry(
                name = actor.name, 
                actor_type = actor.actor_type, 
                occurences = count
            ))

    def set_events(self, events: list[Event]) -> None:
        self.events = [event.event for event in events]