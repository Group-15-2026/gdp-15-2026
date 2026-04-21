from datetime import datetime
import logging

from dateutil import parser

from geo_agent.Entities.Article import Article

def to_source(raw):
    MISSING_SOURCE = dict(source_id="missing-source", source_name="Missing Source")
    id, name = raw['id'], raw['name']
    s = dict(source_id=id, source_name=name) if id and name else MISSING_SOURCE
    return s

# raws are Python dicts following NewsAPI style
def to_article(raw, id):
    a = Article(
        article_id=id,
        article_title=raw['title'],
        publication_time=parser.parse(raw['publishedAt']),
        source=to_source(raw['source']),
        text_body=f"Summary: {raw['description']}. Snippet: {raw['content']}"
    )
    return a
