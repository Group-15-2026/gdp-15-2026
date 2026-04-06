import os
import sys
import logging

from dotenv import load_dotenv, find_dotenv
from mcp.server.fastmcp import FastMCP

from ..Entities.Article import Article

# Set up logging
logging.basicConfig(
    level = logging.DEBUG, # Most detailed info for development
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# XX Note: move this ^^^ to Main.py later

logger = logging.getLogger(__name__) # global logger named src.geo_agent.CollectorServer

# Read from .env into os.environ
# find_dotenv searches through parent dirs for .env
load_dotenv(find_dotenv())

newsapi_key = os.getenv("NEWSAPI_KEY")
if not newsapi_key:
    logger.error("Missing NEWSAPI_KEY. Set it in your .env file. See .env.example for an example.")
    raise # propogate exception

collector_mcp = FastMCP(name="Collector MCP Server")

# XX Note to implementer: the following resource and tool should largely just wrap NewsAPI

# Get more detailed news on a particular topic
@collector_mcp.tool()
def search_news(topics: list[str], start_date: str, end_date: str) -> list[Article]:
    return NotImplemented

# Collect top articles for processing
# XX Note: I'm not convinced a .resource is the right thing here. I think a .tool is needed
@collector_mcp.resource("files://articles/top")
def collect_articles() -> list[Article]:
    return NotImplemented

# XX Note: may or may not be necessary depending on how MCP client is implemented
if __name__ == "__main__":
    collector_mcp.run()
