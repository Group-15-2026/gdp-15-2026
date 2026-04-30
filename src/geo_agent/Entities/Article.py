from .Validators import Between10

from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Field as sqlField, SQLModel, Relationship

# pydantic is used to allow use of objects in mcp tools

class SourceDB(SQLModel, table=True):
    source_id: int | None = sqlField(default=None, primary_key=True)
    source_name: str
    articles: list["ArticleDB"] = Relationship(back_populates="source")

class Source(BaseModel):
    source_name: str

class ArticleType(StrEnum):
    conflict = "conflict"
    politics = "politics"
    tragedy = "tragedy"
    crime = "crime"
    product_review = "product review"
    advice = "advice"
    finance = "finance"

class _ClaimEntry(BaseModel):
    claim: str = Field(frozen=True)
    opinion: Between10 = Field(frozen=True)

class ArticleDB(SQLModel, table=True):
    article_id: int | None = sqlField(default=None, primary_key=True)
    article_title: str = sqlField()
    publication_time: datetime = sqlField()

    source_id: int | None = sqlField(default=None, foreign_key="_source.source_id")
    source: SourceDB | None = Relationship(back_populates="articles")

    url: str = sqlField(default="")

    text_body: str = sqlField()


# TODO May be ready to remove this 'session' stuff commented out below?
# load from database
#//article_db = session.get(ArticleDB, article_id)
#//article2 = Article2(**article_db.model_dump())

class Article(BaseModel):
    # Ensure validation is carried out when details are added later
    model_config = ConfigDict(validate_assignment=True)

    # Fixed fields set upon creation, and unchanged after that
    article_title: str = Field(frozen=True)
    publication_time: datetime = Field(frozen=True)
    source: Source = Field(frozen=True)

    # Fields to be filled in later
    initial_categories: list[ArticleType] | None = None
    claims: list[_ClaimEntry] | None = None
    themes: list[str] | None = None

    # TODO may need breaking up into different methods for filling in at different times (see set_actors)
    def set_processed_values(self,
                             initial_categories: list[str],
                             events: list[str],
                             claims: list[tuple[str, float]],
                             themes: list[str]) -> None:
        self.initial_categories = [ArticleType(at) for at in initial_categories]
        self.events = events
        self.claims = [_ClaimEntry(claim=c, opinion=o) for (c, o) in claims]
        self.themes = themes

    # TODO Link this to the database code
    def get_text_body(self) -> str:
        return NotImplemented