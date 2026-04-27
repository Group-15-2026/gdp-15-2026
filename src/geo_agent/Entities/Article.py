from .Actors import Actor, ActorType
from .Validators import Between10, Count

from collections import Counter
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field

# pydantic is used to allow use of objects in mcp tools

from sqlmodel import Field as sqlField, SQLModel, Relationship, Enum, Column, JSON
from typing import List, Optional

class _Source(SQLModel, table=True):
    source_id: int | None = sqlField(default=None, primary_key=True)
    source_name: str
    articles: List["ArticleDB"] = Relationship(back_populates="source")

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

class ArticleDB(SQLModel, table=True):
    article_id: int | None = sqlField(default=None, primary_key=True)
    article_title: str = sqlField()
    publication_time: datetime = sqlField()

    source_id: int | None = sqlField(default=None, foreign_key="_source.source_id")
    source: _Source | None = Relationship(back_populates="articles")

    # XX This has been temporarily added for MVP, to avoid full DB
    text_body: str = sqlField()

class Article(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True, validate_assignment=True)
    # Database fields (mirrored from ArticleDB, but as plain Pydantic fields)
    article_id: int | None = None
    article_title: str
    publication_time: datetime
    source_id: int | None = None
    source: _Source | None = None
    text_body: str
    
    # Fields to be filled in later - these are NOT stored in the database
    initial_categories: List[ArticleType] | None = None
    actors: List[_ActorEntry] | None = None
    events: List[str] | None = None
    claims: List[_ClaimEntry] | None = None
    themes: List[str] | None = None


# load from database
# article_db = session.get(ArticleDB, article_id)
# article2 = Article2(**article_db.model_dump())

# Deprecated
class ArticleX(BaseModel):
    # Ensure validation is carried out when details are added later
    # model_config = ConfigDict(validate_assignment=True)

    # Fixed fields set upon creation, and unchanged after that
    article_id: int | None = sqlField(default=None, primary_key=True)
    article_title: str = sqlField()
    publication_time: datetime = Field()

    source_id: int | None = sqlField(default=None, foreign_key="_source.source_id")
    # source: _Source | None = Relationship(back_populates="articles")

    # XX This has been temporarily added for MVP, to avoid full DB
    text_body: str = sqlField()

    # Fields to be filled in later
    _initial_categories: list[ArticleType] | None = None
    _actors: list[_ActorEntry] | None = None
    _events: list[str] | None = None
    _claims: list[_ClaimEntry] | None = None
    _themes: list[str] | None = None

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
        for actor in actors:
            (name, label) = actor
            self.actors.append(_ActorEntry(name=name, actor_type=ActorType(label), occurences=actors[actor]))
