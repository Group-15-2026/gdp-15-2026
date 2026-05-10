import os
import sys
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Inject stubs for modules with heavy external dependencies before any import
# that would pull them in transitively.  These are patched at the module level
# so collector.py's own `from news import …` and `from db.database import …`
# lines resolve against the stubs instead of the real implementations.
_news_stub = MagicMock()
sys.modules.setdefault("news", _news_stub)
sys.modules.setdefault("news.access", _news_stub)
sys.modules.setdefault("news.convert", _news_stub)
sys.modules.setdefault("news.index", _news_stub)

_db_stub = MagicMock()
sys.modules.setdefault("db", _db_stub)
sys.modules.setdefault("db.database", _db_stub)

os.environ.setdefault("NEWSAPI_KEY", "test_key")

from geo_agent.CollectorServer.collector import search_news, collect_articles
from geo_agent.Entities.Article import Article, Source


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _article(title: str = "Test Article", source: str = "Test Source") -> Article:
    return Article(
        article_title=title,
        publication_time=datetime(2026, 1, 15, 12, 0, 0),
        source=Source(source_name=source),
    )


# ─────────────────────────────────────────────────────────────────────────────
# collect_articles
# ─────────────────────────────────────────────────────────────────────────────

class TestCollectArticles:
    def test_returns_articles_from_get_daily_articles(self):
        articles = [_article("Article 1"), _article("Article 2")]
        with patch("geo_agent.CollectorServer.collector.get_daily_articles", return_value=articles):
            result = collect_articles()
        assert result == articles

    def test_calls_get_daily_articles_exactly_once(self):
        with patch("geo_agent.CollectorServer.collector.get_daily_articles", return_value=[]) as mock:
            collect_articles()
        mock.assert_called_once_with()

    def test_returns_empty_list_when_no_articles(self):
        with patch("geo_agent.CollectorServer.collector.get_daily_articles", return_value=[]):
            result = collect_articles()
        assert result == []

    def test_returns_list(self):
        with patch("geo_agent.CollectorServer.collector.get_daily_articles", return_value=[]):
            result = collect_articles()
        assert isinstance(result, list)

    def test_propagates_exception(self):
        with patch("geo_agent.CollectorServer.collector.get_daily_articles",
                   side_effect=RuntimeError("API error")):
            with pytest.raises(RuntimeError, match="API error"):
                collect_articles()

    def test_returns_all_articles_unchanged(self):
        articles = [_article(f"Article {i}") for i in range(5)]
        with patch("geo_agent.CollectorServer.collector.get_daily_articles", return_value=articles):
            result = collect_articles()
        assert len(result) == 5
        assert result is articles


# ─────────────────────────────────────────────────────────────────────────────
# search_news
# ─────────────────────────────────────────────────────────────────────────────

class TestSearchNews:
    _start = datetime(2026, 1, 1)
    _end = datetime(2026, 1, 7)

    def test_returns_articles_from_get_articles_about(self):
        articles = [_article("Result")]
        with patch("geo_agent.CollectorServer.collector.get_articles_about", return_value=articles):
            result = search_news(["trade"], self._start, self._end)
        assert result == articles

    def test_passes_topics_start_end_to_get_articles_about(self):
        topics = ["trade", "sanctions"]
        with patch("geo_agent.CollectorServer.collector.get_articles_about", return_value=[]) as mock:
            search_news(topics, self._start, self._end)
        mock.assert_called_once_with(topics, self._start, self._end)

    def test_single_topic_forwarded(self):
        with patch("geo_agent.CollectorServer.collector.get_articles_about", return_value=[]) as mock:
            search_news(["oil"], self._start, self._end)
        assert mock.call_args[0][0] == ["oil"]

    def test_multiple_topics_forwarded(self):
        topics = ["oil", "gas", "coal"]
        with patch("geo_agent.CollectorServer.collector.get_articles_about", return_value=[]) as mock:
            search_news(topics, self._start, self._end)
        assert mock.call_args[0][0] == topics

    def test_start_and_end_dates_forwarded(self):
        start = datetime(2026, 3, 1)
        end = datetime(2026, 3, 31)
        with patch("geo_agent.CollectorServer.collector.get_articles_about", return_value=[]) as mock:
            search_news(["topic"], start, end)
        _, call_start, call_end = mock.call_args[0]
        assert call_start == start
        assert call_end == end

    def test_returns_empty_list_when_no_results(self):
        with patch("geo_agent.CollectorServer.collector.get_articles_about", return_value=[]):
            result = search_news(["nonexistent"], self._start, self._end)
        assert result == []

    def test_returns_multiple_articles(self):
        articles = [_article(f"Result {i}") for i in range(4)]
        with patch("geo_agent.CollectorServer.collector.get_articles_about", return_value=articles):
            result = search_news(["topic"], self._start, self._end)
        assert len(result) == 4

    def test_propagates_exception(self):
        with patch("geo_agent.CollectorServer.collector.get_articles_about",
                   side_effect=ConnectionError("network down")):
            with pytest.raises(ConnectionError, match="network down"):
                search_news(["topic"], self._start, self._end)

    def test_returns_articles_unchanged(self):
        articles = [_article("A"), _article("B")]
        with patch("geo_agent.CollectorServer.collector.get_articles_about", return_value=articles):
            result = search_news(["topic"], self._start, self._end)
        assert result is articles
