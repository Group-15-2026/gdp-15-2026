from datetime import datetime

from dateutil import parser

from geo_agent.Entities.Article import Article, _Source, ArticleDB, SourceDB
from db.database import engine

import newspaper
from sqlmodel import select, Session

def _to_source(raw):
    MISSING_SOURCE = _Source(source_name="Missing Source")
    name = raw['name']
    s = _Source(source_name=name) if name else MISSING_SOURCE
    return s

def to_datetime(time_str):
    return parser.parse(time_str)

# raws are Python dicts following NewsAPI style
def to_article(raw, id):
    a = Article(
        article_title=raw['title'],
        publication_time=to_datetime(raw['publishedAt']),
        source=_to_source(raw['source']),
    )
    return a

def to_source_db(raw) -> tuple[_Source, SourceDB]:
    name = raw['name']
    if not name:
        name = "Missing Source"
    with Session(engine) as session:
        statement = select(SourceDB).where(SourceDB.source_name == name)
        results = session.exec(statement)
        query = results.first
        sourcedb: SourceDB
        if not query:
            sourcedb = query
        else:
            sourcedb = SourceDB(
                source_name=name
            )
            session.add(sourcedb)
            session.commit()
    source = _Source(
        source_name=name,
    )
    return (source, sourcedb)

def to_article_db(raw) -> tuple[Article, ArticleDB]:
    text_body = to_full_text(raw)
    source, sourcedb = to_source_db(raw['source'])
    
    article = Article(
        article_title=raw['title'],
        publication_time=to_datetime(raw['publishedAt']),
        source=source,
    )

    articledb = ArticleDB(
        article_title=raw['title'],
        publication_time=to_datetime(raw['publishedAt']),
        source_id=sourcedb.source_id,
        source=sourcedb,
        url=raw['url'],
        text_body=text_body,
    )
    return (article, articledb)

def to_full_text(raw):
    url = raw['url']
    if raw['source']['name'] in ['bbc-news','cnn']: # TODO These names may not be the true newsapi names for bbc and cnn, so we may never scrape! 
        first_article = newspaper.Article(url=url, language='en')
        first_article.download()
        first_article.parse()
        text_body = first_article.text
    else:
        text_body=f"Summary: {raw['description']}. Snippet: {raw['content']}"
    return text_body
