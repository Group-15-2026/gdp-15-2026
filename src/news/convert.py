from datetime import datetime

from dateutil import parser

from geo_agent.Entities.Article import Article, Source, ArticleDB, SourceDB

import newspaper
from sqlmodel import select, Session
from src.db.database import engine

def _to_source(raw):
    MISSING_SOURCE = Source(source_name="Missing Source")
    name = raw['name']
    s = Source(source_name=name) if name else MISSING_SOURCE
    return s

def to_datetime(time_str):
    return parser.parse(time_str)

# raws are Python dicts following NewsAPI style
def to_article(raw, id):
    text_body = to_full_text(raw)
    name = raw['name']
    # with Session(engine) as session:
    #     statement = select(SourceDB).where(SourceDB.source_name == name)
    #     results = session.exec(statement)
    #     results.first
    

    a = Article(
        article_title=raw['title'],
        publication_time=to_datetime(raw['publishedAt']),
        source=_to_source(raw['source']),
    )

    return a

def to_full_text(raw):
    url = raw['url']
    if raw['source_id'] in ['bbc','cnn']:
        first_article = newspaper.Article(url=url, language='en')
        first_article.download()
        first_article.parse()
        text_body = first_article.text
    else:
        text_body=f"Summary: {raw['description']}. Snippet: {raw['content']}"
    return text_body
