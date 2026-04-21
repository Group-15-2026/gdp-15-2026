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

logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())

newsapi_key = os.getenv("NEWSAPI_KEY")
if not newsapi_key:
    logger.error("Missing NEWSAPI_KEY. Set it in your .env file. See .env.example for an example.")
    raise

newsapi = NewsApiClient(api_key = newsapi_key)

# In: headlines as python dictionary, subdir as string
# Out: location of headlines archive file
def _save_headlines(headlines, subdir):
    DATA_DIR = get_data_dir()

    headlines_json = json.dumps(headlines, indent=4)
    timestr_txt = datetime.now().strftime("%Y-%m-%d") + ".txt"
    archive_file = DATA_DIR / subdir / timestr_txt
    latest_file = DATA_DIR / subdir / "latest.txt"

    with open(archive_file, "w") as f, open(latest_file, "w") as g:
        f.write(headlines_json)
        g.write(headlines_json)

    return archive_file

# Warn if results shows error, return false if there's an error, true if all is good
def _check_status(results):
    if results['status'] == "error":
        logger.warning(f"Error {results['code']} fetching headlines: {results['message']}")
        return False
    return True

# Fetch top headlines from NewsAPI and return location of permanent file containing headlines JSON
def _top_by_source():
    s = 'bbc-news,cnn,the-wall-street-journal,bloomberg'
    logger.info("Attempting to fetch top headlines from NewsAPI.")
    headlines = newsapi.get_top_headlines(language='en', sources=s)
    logger.info("Top headlines successfully fetched from NewsAPI.")
    archive_file = _save_headlines(headlines, "by-source")
    logger.info(f"Successfully saved top headlines to {archive_file}.")
    return archive_file

def _top_by_category():
    def fetch_category(c):
        results = newsapi.get_top_headlines(language='en', category=c)
        return results

    logger.info("Attempting to fetch top relevant headlines from NewsAPI.")

    categories = ["business", "science", "technology"]
    results = [x for x in [fetch_category(c) for c in categories] if _check_status(x)]

    combined_totalResults = sum([r["totalResults"] for r in results])
    combined_articles = list(chain.from_iterable(r["articles"] for r in results))

    headlines = dict(status="ok", totalResults=combined_totalResults, articles=combined_articles)
    if combined_totalResults == 0:
        logger.warning("Warning: 0 results fetched")

    archive_file = _save_headlines(headlines, "by-category")
    logger.info(f"Successefully saved top relevant headlines to {archive_file}.")
    return archive_file

# article codes:
# DC - daily by category; DS - daily by source
def generate_article_id(fetch_time, code, num):
    timestr = fetch_time.strftime("%Y%m%d")
    return f"{timestr}-{code}-{num}"

# dict of id, name (maybe None) -> dict of source_id, source_name (str)
def to_source(source):
    MISSING_SOURCE = dict(source_id="missing-source", source_name="Missing Source")
    id, name = source['id'], source['name']
    s = dict(source_id=id, source_name=name) if id and name else MISSING_SOURCE
    return s

# article dictionary -> Entities Article class
def to_article(article, id):
    title = article['title']
    publishedAt = parser.parse(article['publishedAt']) # recognises any format to convert to DateTime
    source = to_source(article['source'])
    body = f"Summary: {article['description']}. Snippet: {article['content']}"
    a = Article(
        article_id=id,
        article_title=title,
        publication_time=publishedAt,
        source=source,
        text_body=body
    )
    return a

# Attempts to get the daily articles from the data directory, fetches them from NewsAPI otherwise
def get_daily_articles():
    DATA_DIR = get_data_dir()
    fetch_time = datetime.now()
    file_name = fetch_time.strftime("%Y-%m-%d") + ".txt"
    file_path = DATA_DIR / "by-category" / file_name

    try:
        with open(file_path, "r") as f:
            results_json = f.read()
    except:
        archive_path = _top_by_category()
        with open(archive_path, "r") as f:
            results_json = f.read()

    results_dict = json.loads(results_json)
    id_prefix = fetch_time.strftime("%Y%m%d-DC-")
    articles_list = []
    for i in range(0, len(results_dict)):
        id = id_prefix + str(i+1)
        a = to_article(results_dict['articles'][i], id)
        articles_list.append(a)
    return articles_list

def get_daily_articles_about():
    pass

if __name__ == "__main__":
    print(get_daily_articles())
