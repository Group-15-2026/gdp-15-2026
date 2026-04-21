import datetime as dt
import json
import logging
import os

from dotenv import load_dotenv, find_dotenv
from itertools import chain
from newsapi import NewsApiClient

from news.convert import to_article, to_datetime
from news.index import index_top_by_category, index_top_by_source, index_weekly_by_topic

logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())

newsapi_key = os.getenv("NEWSAPI_KEY")
if not newsapi_key:
    logger.error("Missing NEWSAPI_KEY. Set it in your .env file. See .env.example for an example.")
    raise

newsapi = NewsApiClient(api_key = newsapi_key)

# Warn if results shows error, return false if there's an error, true if all is good
def _check_status(results):
    if results['status'] == "error":
        logger.warning(f"Error {results['code']} fetching articles: {results['message']}")
        return False
    return True

def _top_by_source():
    s = 'bbc-news,cnn,the-wall-street-journal,bloomberg'
    results = newsapi.get_top_headlines(language='en', sources=s)
    return results['articles']

def _top_by_category():
    def fetch_category(c):
        results = newsapi.get_top_headlines(language='en', category=c)
        return results

    categories = ["business", "science", "technology"]
    results = [x for x in [fetch_category(c) for c in categories] if _check_status(x)]

    articles = list(chain.from_iterable(r["articles"] for r in results))
    return articles

def _weekly_by_topic(topic, oldest_str):
    results = newsapi.get_everything(q=topic, from_param=oldest_str, language='en')
    return results['articles']

def _range_by_topic(topic, start_time_dt, end_time_dt):
    from_str = start_time_dt.strftime("%Y-%m-%d")
    to_str = end_time_dt.strftime("%Y-%m-%d")

    results = newsapi.get_everything(q=t, from_param=from_str, to_param=to_str, language='en')
    
    return results['articles']


# Attempts to get the daily articles from the data directory, fetches them from NewsAPI otherwise
def _fetch_from(index, api_access):
    file_path = index.get_file_path()
    logger.info(f"Attempting to fetch articles from {file_path}")
    try:
        with open(file_path, "r") as f:
            articles = json.load(f)
        logger.info("Articles fetched successfully.")
    except:
        logger.info("Articles not cached. Attempting to fetch from NewsAPI.")
        articles = api_access()
        logger.info("Articles fetched successfully.")
        file_path = index.save(articles)
        logger.info(f"Articles successfully saved to {file_path}.")
    if len(articles) == 0:
        logger.warning("Warning: 0 articles found.")
    return articles

def get_daily_articles():
    fetch_time = dt.date.today()
    index = index_top_by_category(fetch_time)
    raw = _fetch_from(index, _top_by_category, fetch_time)

    id_prefix = index.get_file_id(fetch_time)
    articles = [to_article(r, f"{id_prefix}-{i+1}") for i, r in enumerate(raw)]

    return articles

def get_articles_about(topics, start_date_str, end_date_str):
    start_time_dt, end_time_dt = to_datetime(start_date_str), to_datetime(end_date_str)
    indices = [index_range_by_topic(t, start_time_dt, end_time_dt) for t in topics]

    def api_access():
        return _range_by_topic(topic, start_time_dt, end_time_dt)

    raw = _fetch_from(index, api_access)

    id_prefix = index.get_file_id(fetch_time)
    articles = [to_article(r, f"{id_prefix}-{i+1}") for i, r in enumerate(raw)]

    return articles


if __name__ == "__main__":
    print(get_articles_about("cars"))
