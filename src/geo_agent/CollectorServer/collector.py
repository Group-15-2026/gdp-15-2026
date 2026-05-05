from ..Entities.Article import Article

from db.database import create_tables
from news import get_daily_articles, get_articles_about

from datetime import datetime
from mcp.server.fastmcp import FastMCP

from utils import setup_server_logging

setup_server_logging("collector")

collector_mcp = FastMCP(name="Collector MCP Server")

# Get more detailed news on a particular topic
# Duplicates possible
# start_date is distant date, end_date is recent date
@collector_mcp.tool()
def search_news(topics: list[str], start_date: datetime, end_date: datetime) -> list[Article]:
    '''
    Searches news sites for articles on particular topics, within a restricted date range.
    '''
    return get_articles_about(topics, start_date, end_date)

# Collect top articles for processing
# Returns top articles for that day, from business, science, and tech categories
# Duplicates possible
@collector_mcp.tool()
def collect_articles() -> list[Article]:
    '''
    Fetches and returns the web articles from the last day, on the topics of business, science and tech. 

    This should only be called ONCE, as no new articles will be acquired from multiple calls.
    '''    
    return get_daily_articles()

if __name__ == "__main__":
    create_tables()
    collector_mcp.run()
