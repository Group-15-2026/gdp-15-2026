from datetime import datetime

from dateutil import parser

from geo_agent.Entities.Article import Article, _Source

def _to_source(raw):
    MISSING_SOURCE = _Source(source_id="missing-source", source_name="Missing Source")
    id, name = raw['id'], raw['name']
    s = _Source(source_id=id, source_name=name) if id and name else MISSING_SOURCE
    return s

def to_datetime(time_str):
    return parser.parse(time_str)

# raws are Python dicts following NewsAPI style
def to_article(raw, id):
    a = Article(
        article_id=id,
        article_title=raw['title'],
        publication_time=to_datetime(raw['publishedAt']),
        source=_to_source(raw['source']),
        text_body=f"Summary: {raw['description']}. Snippet: {raw['content']}"
    )
    return a
