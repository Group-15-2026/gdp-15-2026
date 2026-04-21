from datetime import datetime
import logging

from utils import get_data_dir

logger = logging.getLogger(__name__)

# In: articles as python dictionary, subdir as string
# Out: location of articles archive file
def _save_articles(articles, subdir):
    DATA_DIR = get_data_dir()

    articles_json = json.dumps(articles, indent=4)
    timestr_txt = datetime.now().strftime("%Y-%m-%d") + ".txt"
    archive_file = DATA_DIR / subdir / timestr_txt
    latest_file = DATA_DIR / subdir / "latest.txt"

    with open(archive_file, "w") as f, open(latest_file, "w") as g:
        f.write(articles_json)
        g.write(articles_json)

    logger.info(f"Saved articles to {archive_file} and {latest_file}")

    return archive_file

def save_top_by_category(articles):
    return _save_articles(articles, "by-category")

def save_top_by_source(articles):
    return _save_articles(articles, "by-source")

def _get_file_name(time_dt):
    time_str = time_dt.strftime("%Y-%m-%d")
    file_name = f"{time_str}.txt"
    return file_name

def get_top_by_category_path(time_dt):
    DATA_DIR = get_data_dir()
    file_name = _get_file_name(time_dt)
    file_path = DATA_DIR / "by-category" / file_name
    return file_path
