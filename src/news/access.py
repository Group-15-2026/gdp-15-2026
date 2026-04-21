import json
import logging
import os
import sys
from datetime import datetime

from dateutil import parser
from dotenv import load_dotenv, find_dotenv
from itertools import chain
from newsapi import NewsApiClient

from geo_agent.Entities.Article import Article
from utils import get_data_dir
from news.convert import to_source, to_article
from news.save import index_top_by_category, index_top_by_source, index_weekly_by_topic

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

# Fetch top articles from NewsAPI and return location of permanent file containing articles JSON
def _top_by_source():
    s = 'bbc-news,cnn,the-wall-street-journal,bloomberg'
    articles = newsapi.get_top_headlines(language='en', sources=s)
    return articles

def _top_by_category():
    def fetch_category(c):
        results = newsapi.get_top_headlines(language='en', category=c)
        return results

    categories = ["business", "science", "technology"]
    results = [x for x in [fetch_category(c) for c in categories] if _check_status(x)]

    combined_totalResults = sum([r["totalResults"] for r in results])
    combined_articles = list(chain.from_iterable(r["articles"] for r in results))

    if combined_totalResults == 0:
        logger.warning("Warning: 0 results found.")

    articles = dict(status="ok", totalResults=combined_totalResults, articles=combined_articles)
    return articles

def _fetch_from(index, api_acces, fetch_time):
    file_path = index.get_file_path(fetch_time)
    logger.info(f"Attempting to fetch articles from {file_path}")
    try:
        with open(file_path, "r") as f:
            articles = json.load(f)
    except:
        logger.info("Articles not cached. Attempting to fetch from NewsAPI.")
        results = api_access()
        logger.info("Results fetched successfully.")
        articles = results['articles']
        file_path = index.save(articles, fetch_time)
        logger.info(f"Articles successfully saved to {file_path}")
    if len(articles) == 0:
        logger.warning("Warning: 0 articles found.")
    return articles

# Attempts to get the daily articles from the data directory, fetches them from NewsAPI otherwise
def get_daily_articles():
    index = index_top_by_category()
    fetch_time = datetime.now()
    articles_raw = _fetch_from(index, _top_by_category, fetch_time)

    id_prefix = index.get_file_id(time_dt)
    articles = []

    for i in range(0, len(articles_raw)):
        r = articles_raw[i]

        id = f"{id_prefix}-{i}"
        title = r['title']
        time_str = r['publishedAt']
        source = to_source(r['source']['id'], r['source']['name'])
        body = f"Summary: {r['description']}. Snippet: {r['content']}"

        a = to_article(id, title, time_str, source, body)
        articles.append(a)

    return articles

def get_daily_articles_about(topic):
    fetch_time = datetime.now()


if __name__ == "__main__":
    print(get_daily_articles())
