from datetime import datetime
from dateutil import parser
import newspaper
from sqlmodel import select, Session

from geo_agent.Entities.Article import Article, Source, ArticleDB, SourceDB
from db.database import engine

def _to_source(raw):
    MISSING_SOURCE = Source(source_name="Missing Source")
    id, name = raw['id'], raw['name']
    s = Source(source_name=name) if id and name else MISSING_SOURCE
    return s

def to_datetime(time_str):
    return parser.parse(time_str)

# raws are Python dicts following NewsAPI style
def to_article(raw):
    a = Article(
        article_title=raw['title'] or "Missing Title",
        publication_time=to_datetime(raw['publishedAt'] or "Missing publication date"),
        source=_to_source(raw['source'] or "Missing source")
    )
    return a

def to_source_db(raw) -> tuple[Source, SourceDB]:
    name = raw['name']
    if not name:
        name = "Missing Source"
    with Session(engine) as session:
        statement = select(SourceDB).where(SourceDB.source_name == name)
        results = session.exec(statement)
        sourcedb = results.first()
        if not sourcedb:
            sourcedb = SourceDB(
                source_name=name
            )
            session.add(sourcedb)
            session.commit()
            session.refresh(sourcedb)
    source = Source(
        source_name=name,
    )
    return (source, sourcedb)

def to_article_db(raw) -> tuple[Article, ArticleDB]:
    text_body = to_full_text(raw)
    source, sourcedb = to_source_db(raw['source'])

    title = raw['title'] or "Missing title"
    publication_time = to_datetime(raw['publishedAt'] or "Missing publication date")

    article = Article(
        article_title=title,
        publication_time=publication_time,
        source=source
    )

    articledb = ArticleDB(
        article_title=title,
        publication_time=publication_time,
        source_id=sourcedb.source_id,
        source=sourcedb,
        url=raw['url'] or "Missing url",
        text_body=text_body
    )
    return (article, articledb)

def to_full_text(raw):
    url = raw['url']
    if raw['source']['id'] in ['bbc-news','cnn']: # Refer to "Initial Experiments"/news-api-test/newsapi-sources.json to get names of additional safesources to add.
        try:
            first_article = newspaper.Article(url=url, language='en')
            first_article.download()
            first_article.parse()
            text_body = first_article.text
        except:
            text_body=f"Summary: {raw['description']}. Snippet: {raw['content']}"
    else:
        text_body=f"Summary: {raw['description']}. Snippet: {raw['content']}"
    return text_body
