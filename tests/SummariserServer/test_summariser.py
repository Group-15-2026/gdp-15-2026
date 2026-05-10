import sys
import asyncio
import pytest
from collections import Counter
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch, call

# Stub spacy before any import that pulls it in transitively via extraction.py.
sys.modules.setdefault("spacy", MagicMock())

from geo_agent.SummariserServer.summariser import extract_events, ExtractEventsResult
from geo_agent.Entities.Article import Article, Source, ClaimEntry
from geo_agent.Entities.Actors import Actor, ActorType
from geo_agent.Entities.Events import Event


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _article(title: str = "Test Article", source: str = "BBC") -> Article:
    return Article(
        article_title=title,
        publication_time=datetime(2026, 1, 15, 12, 0),
        source=Source(source_name=source),
    )

def _claim(text: str = "Some claim", opinion: float = 7.0) -> ClaimEntry:
    return ClaimEntry(claim=text, opinion=opinion)

def _actor(name: str = "USA", actor_type: ActorType = ActorType.country) -> Actor:
    return Actor(name=name, actor_type=actor_type)

def _event(text: str = "Missile strike on military base") -> Event:
    return Event(event=text)

def _run(coro):
    return asyncio.run(coro)

P = "geo_agent.SummariserServer.summariser"


def _patch_all(*, claims_side_effect, actors_return, classify_side_effect,
               events_side_effect, combine_return):
    """Return a context manager that patches all five pipeline dependencies."""
    return (
        patch(f"{P}.extract_article_claims", AsyncMock(side_effect=claims_side_effect)),
        patch(f"{P}.extract_actors",         MagicMock(return_value=actors_return)),
        patch(f"{P}.classify_article_actors", AsyncMock(side_effect=classify_side_effect)),
        patch(f"{P}.extract_article_events", AsyncMock(side_effect=events_side_effect)),
        patch(f"{P}.combine_all_events",     AsyncMock(return_value=combine_return)),
    )


def _run_pipeline(articles, *, claims=None, actors_by_article=None,
                  classified=None, doc_events=None, combined=None):
    """
    Run extract_events with sensible defaults for every dependency mock.
    Returns (result, mocks) where mocks is a dict keyed by short name.
    """
    n = len(articles)
    claims           = claims or [[] for _ in articles]
    actors_by_article = actors_by_article or [(a, Counter(), {}) for a in articles]
    classified       = classified or [[]] * n
    doc_events       = doc_events or [[]] * n
    all_doc_events   = [e for evts in doc_events for e in evts]
    combined         = combined if combined is not None else all_doc_events

    claim_mock    = AsyncMock(side_effect=claims)
    actors_mock   = MagicMock(return_value=actors_by_article)
    classify_mock = AsyncMock(side_effect=classified)
    events_mock   = AsyncMock(side_effect=doc_events)
    combine_mock  = AsyncMock(return_value=combined)

    with patch(f"{P}.extract_article_claims",  claim_mock), \
         patch(f"{P}.extract_actors",           actors_mock), \
         patch(f"{P}.classify_article_actors",  classify_mock), \
         patch(f"{P}.extract_article_events",   events_mock), \
         patch(f"{P}.combine_all_events",        combine_mock):
        result = _run(extract_events(articles))

    return result, {
        "claims": claim_mock, "actors": actors_mock,
        "classify": classify_mock, "events": events_mock, "combine": combine_mock,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ExtractEventsResult
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractEventsResult:
    def test_empty_lists(self):
        r = ExtractEventsResult(actors=[], events=[])
        assert r.actors == [] and r.events == []

    def test_stores_actors_and_events(self):
        actors = [_actor()]
        events = [_event()]
        r = ExtractEventsResult(actors=actors, events=events)
        assert r.actors == actors
        assert r.events == events

    def test_serialises_to_json(self):
        r = ExtractEventsResult(actors=[_actor()], events=[_event()])
        data = r.model_dump()
        assert "actors" in data and "events" in data


# ─────────────────────────────────────────────────────────────────────────────
# extract_events — return type and empty input
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractEventsReturnType:
    def test_returns_extract_events_result(self):
        result, _ = _run_pipeline([])
        assert isinstance(result, ExtractEventsResult)

    def test_empty_articles_gives_empty_actors_and_events(self):
        result, _ = _run_pipeline([])
        assert result.actors == [] and result.events == []

    def test_empty_articles_skips_combine(self):
        _, mocks = _run_pipeline([])
        mocks["combine"].assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# extract_events — claim extraction
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractEventsClaims:
    def test_claim_extractor_called_once_per_article(self):
        articles = [_article("A"), _article("B"), _article("C")]
        _, mocks = _run_pipeline(articles)
        assert mocks["claims"].call_count == 3

    def test_claims_set_on_article(self):
        article = _article()
        claims = [_claim("Tariffs imposed", 8.0)]
        _run_pipeline([article], claims=[claims])
        assert article.claims == claims

    def test_claims_set_independently_per_article(self):
        a1, a2 = _article("A"), _article("B")
        c1 = [_claim("Claim A", 5.0)]
        c2 = [_claim("Claim B", -3.0)]
        _run_pipeline([a1, a2], claims=[c1, c2])
        assert a1.claims == c1
        assert a2.claims == c2

    def test_empty_claims_set_on_article(self):
        article = _article()
        _run_pipeline([article], claims=[[]])
        assert article.claims == []


# ─────────────────────────────────────────────────────────────────────────────
# extract_events — actor extraction
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractEventsActors:
    def test_extract_actors_called_with_full_article_list(self):
        articles = [_article("A"), _article("B")]
        _, mocks = _run_pipeline(articles)
        mocks["actors"].assert_called_once_with(articles)

    def test_actor_appears_in_result(self):
        article = _article()
        actor = _actor("Germany", ActorType.country)
        actors_by_article = [(article, Counter(), {})]
        result, _ = _run_pipeline(
            [article],
            actors_by_article=actors_by_article,
            classified=[[(actor, 3)]],
            doc_events=[[]],
        )
        assert actor in result.actors

    def test_actors_accumulated_from_all_articles(self):
        a1, a2 = _article("A"), _article("B")
        actor1 = _actor("USA", ActorType.country)
        actor2 = _actor("China", ActorType.country)
        actors_by_article = [(a1, Counter(), {}), (a2, Counter(), {})]
        result, _ = _run_pipeline(
            [a1, a2],
            actors_by_article=actors_by_article,
            classified=[[(actor1, 1)], [(actor2, 2)]],
            doc_events=[[], []],
        )
        assert actor1 in result.actors
        assert actor2 in result.actors

    def test_classify_called_once_per_article(self):
        articles = [_article("A"), _article("B")]
        _, mocks = _run_pipeline(articles)
        assert mocks["classify"].call_count == 2


# ─────────────────────────────────────────────────────────────────────────────
# extract_events — event extraction and source_articles
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractEventsEvents:
    def test_event_extractor_called_once_per_article(self):
        articles = [_article("A"), _article("B")]
        _, mocks = _run_pipeline(articles)
        assert mocks["events"].call_count == 2

    def test_source_articles_set_on_event(self):
        article = _article()
        event = _event("US sanctions Iran")
        actors_by_article = [(article, Counter(), {})]
        _run_pipeline(
            [article],
            actors_by_article=actors_by_article,
            classified=[[]],
            doc_events=[[event]],
            combined=[event],
        )
        assert event.source_articles == [article]

    def test_source_articles_set_to_originating_article(self):
        a1, a2 = _article("A"), _article("B")
        e1 = _event("Event from A")
        e2 = _event("Event from B")
        actors_by_article = [(a1, Counter(), {}), (a2, Counter(), {})]

        combine_mock = AsyncMock(return_value=[e1, e2])
        events_mock  = AsyncMock(side_effect=[[e1], [e2]])
        claim_mock   = AsyncMock(side_effect=[[], []])
        actors_mock  = MagicMock(return_value=actors_by_article)
        classify_mock = AsyncMock(side_effect=[[], []])

        with patch(f"{P}.extract_article_claims",  claim_mock), \
             patch(f"{P}.extract_actors",           actors_mock), \
             patch(f"{P}.classify_article_actors",  classify_mock), \
             patch(f"{P}.extract_article_events",   events_mock), \
             patch(f"{P}.combine_all_events",        combine_mock):
            _run(extract_events([a1, a2]))

        assert e1.source_articles == [a1]
        assert e2.source_articles == [a2]


# ─────────────────────────────────────────────────────────────────────────────
# extract_events — event combination
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractEventsCombination:
    def test_combine_called_when_events_exist(self):
        article = _article()
        event = _event("Trade war escalates")
        actors_by_article = [(article, Counter(), {})]
        _, mocks = _run_pipeline(
            [article],
            actors_by_article=actors_by_article,
            classified=[[]],
            doc_events=[[event]],
            combined=[event],
        )
        mocks["combine"].assert_called_once()

    def test_combine_not_called_when_no_events(self):
        article = _article()
        actors_by_article = [(article, Counter(), {})]
        _, mocks = _run_pipeline(
            [article],
            actors_by_article=actors_by_article,
            classified=[[]],
            doc_events=[[]],
        )
        mocks["combine"].assert_not_called()

    def test_result_uses_combined_events_not_raw(self):
        article = _article()
        raw   = _event("Original event wording")
        merged = _event("Merged precise event")
        actors_by_article = [(article, Counter(), {})]
        result, _ = _run_pipeline(
            [article],
            actors_by_article=actors_by_article,
            classified=[[]],
            doc_events=[[raw]],
            combined=[merged],
        )
        assert merged in result.events
        assert raw not in result.events

    def test_all_raw_events_passed_to_combine(self):
        a1, a2 = _article("A"), _article("B")
        e1 = _event("Event One")
        e2 = _event("Event Two")
        actors_by_article = [(a1, Counter(), {}), (a2, Counter(), {})]

        combine_mock  = AsyncMock(return_value=[e1, e2])
        events_mock   = AsyncMock(side_effect=[[e1], [e2]])
        claim_mock    = AsyncMock(side_effect=[[], []])
        actors_mock   = MagicMock(return_value=actors_by_article)
        classify_mock = AsyncMock(side_effect=[[], []])

        with patch(f"{P}.extract_article_claims",  claim_mock), \
             patch(f"{P}.extract_actors",           actors_mock), \
             patch(f"{P}.classify_article_actors",  classify_mock), \
             patch(f"{P}.extract_article_events",   events_mock), \
             patch(f"{P}.combine_all_events",        combine_mock):
            _run(extract_events([a1, a2]))

        passed_events = combine_mock.call_args[0][0]
        assert e1 in passed_events
        assert e2 in passed_events

    def test_no_events_result_in_empty_events_list(self):
        article = _article()
        actors_by_article = [(article, Counter(), {})]
        result, _ = _run_pipeline(
            [article],
            actors_by_article=actors_by_article,
            classified=[[]],
            doc_events=[[]],
        )
        assert result.events == []
