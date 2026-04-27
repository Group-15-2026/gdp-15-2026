import datetime as dt
from functools import partial
import json
import logging
import os

from dotenv import load_dotenv, find_dotenv
from itertools import chain
from newsapi.newsapi_client import NewsApiClient

from news.convert import to_article, to_datetime
from news.index import index_top_by_category, index_top_by_source, index_weekly_by_topic, index_range_by_topic

from sqlmodel import Session
from src.db.database import engine
from geo_agent.Entities.Article import Article, _Source, ArticleDB

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

def _range_by_topic(topic, from_dt, to_dt):
    from_str = from_dt.strftime("%Y-%m-%d")
    to_str = to_dt.strftime("%Y-%m-%d")

    results = newsapi.get_everything(q=topic, from_param=from_str, to=to_str, language='en')
    
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
    raw = _fetch_from(index, _top_by_category)

    id_prefix = index.get_file_id()
    articles = [to_article(r, f"{id_prefix}-{i+1}") for i, r in enumerate(raw)]

    add_articles_to_db(articles)

    return articles

# from is start, to is end
def get_articles_about(topics, start_str, end_str):
    start_dt, end_dt = to_datetime(start_str), to_datetime(end_str)
    indices = [index_range_by_topic(topic, start_dt, end_dt) for topic in topics]

    api_access = partial(_range_by_topic, from_dt=start_dt, to_dt=end_dt)

    raws = [_fetch_from(index, partial(api_access, index.get_topic())) for index in indices]
    id_prefixes = [index.get_file_id() for index in indices]
    articles = list(chain.from_iterable([to_article(r, f"{id_prefixes[j]}-{i+1}") for i, r in enumerate(raw)] for j, raw in enumerate(raws)))

    add_articles_to_db(articles)

    return articles

def add_articles_to_db(articles: list[Article]) -> None:
    # could try to do something to prevent the same article being inserted multiple times
    with Session(engine) as session:
        for article in articles:
            # Add the source to the database if it exists
            if article.source:
                session.add(article.source)
            
            # Create ArticleDB with both database fields and the source relationship
            article_db = ArticleDB(
                article_id=article.article_id,
                article_title=article.article_title,
                publication_time=article.publication_time,
                source_id=article.source_id,
                source=article.source,
                text_body=article.text_body
            )
            session.add(article_db)
        session.commit()

if __name__ == "__main__":
    my_article = Article(article_title="Article title", publication_time=dt.datetime.now(), source=_Source(source_name='cnn'), text_body="Placeholder text body")
    add_articles_to_db([my_article])
    # print(get_articles_about(["cars", "dogs"], "2026-04-01", "2026-04-24"))
    # print(get_daily_articles())
    # print(get_articles_about(["donald trump"], "2026-04-01", "2026-04-24"))
