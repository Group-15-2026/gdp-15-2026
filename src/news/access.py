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
from news.convert import to_source, to_article, get_id_top_by_category
from news.save import save_top_by_category, save_top_by_source, get_top_by_category_path

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
    logger.info("Attempting to fetch top articles from NewsAPI.")
    articles = newsapi.get_top_headlines(language='en', sources=s)
    logger.info("Top headlines successfully fetched from NewsAPI.")
    archive_file = save_top_by_source(articles)
    logger.info(f"Successfully saved top articles to {archive_file}.")
    return archive_file

def _top_by_category():
    def fetch_category(c):
        results = newsapi.get_top_headlines(language='en', category=c)
        return results

    logger.info("Attempting to fetch top relevant articles from NewsAPI.")

    categories = ["business", "science", "technology"]
    results = [x for x in [fetch_category(c) for c in categories] if _check_status(x)]

    combined_totalResults = sum([r["totalResults"] for r in results])
    combined_articles = list(chain.from_iterable(r["articles"] for r in results))

    articles = dict(status="ok", totalResults=combined_totalResults, articles=combined_articles)
    if combined_totalResults == 0:
        logger.warning("Warning: 0 results fetched")

    archive_file = save_top_by_category(articles)
    return archive_file

# Attempts to get the daily articles from the data directory, fetches them from NewsAPI otherwise
def get_daily_articles():
    fetch_time = datetime.now()
    file_path = get_top_by_category_path(fetch_time)

    try:
        with open(file_path, "r") as f:
            results_json = f.read()
    except:
        archive_path = _top_by_category()
        with open(archive_path, "r") as f:
            results_json = f.read()

    results_dict = json.loads(results_json)
    articles_list = []

    for i in range(0, len(results_dict)):
        r = results_dict['articles'][i]

        id = get_id_top_by_category(fetch_time, i)
        title = r['title']
        time_str = r['publishedAt']
        source = to_source(r['source']['id'], r['source']['name'])
        body = f"Summary: {r['description']}. Snippet: {r['content']}"

        a = to_article(id, title, time_str, source, body)
        articles_list.append(a)

    return articles_list

def get_daily_articles_about():
    pass

if __name__ == "__main__":
    print(get_daily_articles())
