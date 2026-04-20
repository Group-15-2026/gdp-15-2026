import json
import logging
import os
import sys
import time

from dotenv import load_dotenv, find_dotenv
from newsapi import NewsApiClient

from utils import get_project_root

logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())

newsapi_key = os.getenv("NEWSAPI_KEY")
if not newsapi_key:
    logger.error("Missing NEWSAPI_KEY. Set it in your .env file. See .env.example for an example.")
    raise

newsapi = NewsApiClient(api_key = newsapi_key)


# In: headlines as python dictionary
# Out: location of headlines archive file
def save_headlines(headlines):
    ROOT = get_project_root()

    # Converts python dictionary headlines into json
    headlines_json = json.dumps(headlines, indent=4)
    timestr_txt = time.strftime("%Y-%m-%d--%H%M%S") + ".txt"
    archive_file = ROOT / "data" / (timestr_txt)
    latest_file = ROOT / "data" / "latest.txt"

    archive = open(archive_file, "w")
    latest = open(latest_file, "w")
    archive.write(headlines_json)
    latest.write(headlines_json)
    archive.close()
    latest.close()

    return archive_file
    

# Fetch top headlines from NewsAPI and return location of permanent file containing headlines JSON
def fetch_top():
    logger.info("Attempting to fetch top headlines from NewsAPI.")
    headlines = newsapi.get_top_headlines(language='en',
                                          sources='bbc-news,cnn,the-wall-street-journal,bloomberg')
    logger.info("Top headlines successfully fetched from NewsAPI.")
    archive_file = save_headlines(headlines)
    logger.info(f"Successfully saved top headlines to {archive_file}.")
    return archive_file

if __name__ == "__main__":
    fetch_top()
