# XX Note: This module shouldn't know NewsAPI even exists
# so nothing here should require knowledge of how NewsAPI formats things

from datetime import datetime
import logging

from dateutil import parser

from geo_agent.Entities.Article import Article
from utils import get_data_dir

def _get_article_id(fetch_time, num, code):
    num_offset = num + 1
    time_str = fetch_time.strftime("%Y%m%d")
    return f"{time_str}-{code}-{num_offset}"

def get_id_top_by_category(fetch_time, num):
    return _get_article_id(fetch_time, num, "DC")

def get_id_top_by_source(fetch_time, num):
    return _get_article_id(fetch_time, num, "DS")

def to_source(id, name):
    MISSING_SOURCE = dict(source_id="missing-source", source_name="Missing Source")
    s = dict(source_id=id, source_name=name) if id and name else MISSING_SOURCE
    return s

# source has already had to_source run on it
def to_article(id, title, time_str, source, body):
    time_dt = parser.parse(time_str)
    a = Article(
        article_id=id,
        article_title=title,
        publication_time=time_dt,
        source=source,
        text_body=body
    )
    return a
