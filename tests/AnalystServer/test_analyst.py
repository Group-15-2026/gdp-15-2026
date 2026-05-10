import asyncio
import json
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from geo_agent.Entities.Events import Event, Impact, Severity
from geo_agent.Entities.Article import Article, Source
from geo_agent.AnalystServer.financial_rules import (
    classify_financial_impact,
    event_type_to_article_type,
    _detect_event_type,
    _detect_commodities,
    _build_narrative_prompt,
)
from geo_agent.AnalystServer.impacts import (
    EventSeverityResponseMarker,
    EventJustificationResponseMarker,
)
from geo_agent.AnalystServer.analyst import get_final_report_instructions


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _event(text: str, fin_sev: Severity = Severity.low) -> Event:
    e = Event(
        event=text,
        source_articles=[Article(
            article_title="Test Article",
            publication_time=datetime.now(),
            source=Source(source_name="Test"),
        )],
    )
    e.set_impacts(Severity.low, "", fin_sev, "", Severity.low, "", Severity.low, "")
    return e


def _severity_json(n: int = 1) -> str:
    return json.dumps([{
        "economic_impact_severity": "low",
        "financial_markets_impact_severity": "medium",
        "security_impact_severity": "high",
        "diplomatic_impact_severity": "no_impact",
    }] * n)


def _justification_json(n: int = 1) -> str:
    return json.dumps([{
        "economic_impact_justification": "Some economic reason.",
        "financial_market_impact_justification": "Some financial reason.",
        "security_impact_justification": "No material impact identified.",
        "diplomatic_impact_justification": "Some diplomatic reason.",
    }] * n)


# ─────────────────────────────────────────────────────────────────────────────
# _detect_event_type
# ─────────────────────────────────────────────────────────────────────────────

class TestDetectEventType:
    def test_military_escalation(self):
        assert _detect_event_type("troops mobilized at border") == "military_escalation"

    def test_sanctions(self):
        assert _detect_event_type("new sanction imposed on russia") == "sanctions"

    def test_trade_dispute(self):
        assert _detect_event_type("us imposes tariff on chinese goods") == "trade_dispute"

    def test_election(self):
        assert _detect_event_type("presidential election held in france") == "election"

    def test_natural_disaster(self):
        assert _detect_event_type("earthquake hits turkey") == "natural_disaster"

    def test_energy_shock(self):
        assert _detect_event_type("opec cuts oil production") == "energy_shock"

    def test_coup_or_instability(self):
        assert _detect_event_type("coup overthrows government") == "coup_or_instability"

    def test_diplomatic_change(self):
        assert _detect_event_type("peace deal signed between warring factions") == "diplomatic_change"

    def test_military_takes_priority_over_energy(self):
        # military_escalation is higher in the keyword list than energy_shock
        assert _detect_event_type("missile strike on oil refinery") == "military_escalation"

    def test_no_match_returns_none(self):
        assert _detect_event_type("sports tournament results announced") is None

    def test_empty_string_returns_none(self):
        assert _detect_event_type("") is None


# ─────────────────────────────────────────────────────────────────────────────
# _detect_commodities
# ─────────────────────────────────────────────────────────────────────────────

class TestDetectCommodities:
    def test_oil_keyword(self):
        assert "oil" in _detect_commodities("crude oil prices rise sharply")

    def test_natural_gas_keyword(self):
        assert "natural_gas" in _detect_commodities("natural gas prices spike in europe")

    def test_semiconductor_via_tsmc(self):
        assert "semiconductors" in _detect_commodities("tsmc expands chip production capacity")

    def test_gold_via_safe_haven(self):
        assert "gold" in _detect_commodities("investors flee to safe haven assets")

    def test_multiple_commodities(self):
        result = _detect_commodities("oil price rises as wheat supply disrupted")
        assert "oil" in result
        assert "wheat" in result

    def test_no_commodities(self):
        assert _detect_commodities("diplomatic talks resume in geneva") == []

    def test_returns_list(self):
        assert isinstance(_detect_commodities("any text"), list)


# ─────────────────────────────────────────────────────────────────────────────
# classify_financial_impact
# ─────────────────────────────────────────────────────────────────────────────

class TestClassifyFinancialImpact:
    def test_returns_all_keys(self):
        result = classify_financial_impact("Global", "trade war escalates")
        assert set(result.keys()) == {
            "event_type", "affected_sectors", "affected_asset_classes",
            "commodities_mentioned", "narrative_prompt",
        }

    def test_military_event_type(self):
        result = classify_financial_impact("Global", "missile strikes on military base")
        assert result["event_type"] == "military_escalation"

    def test_known_region_populates_sectors(self):
        result = classify_financial_impact("East Asia", "diplomatic summit held")
        assert len(result["affected_sectors"]) > 0

    def test_unknown_region_falls_back_to_global(self):
        result_unknown = classify_financial_impact("Antarctica", "trade talks")
        result_global = classify_financial_impact("Global", "trade talks")
        assert result_unknown["affected_sectors"] == result_global["affected_sectors"]

    def test_no_event_type_yields_empty_asset_classes(self):
        result = classify_financial_impact("Global", "sports tournament results announced")
        assert result["event_type"] is None
        assert result["affected_asset_classes"] == []

    def test_commodity_mention_adds_sectors(self):
        result = classify_financial_impact("Global", "crude oil supply disrupted")
        assert "oil" in result["commodities_mentioned"]
        assert any(s in result["affected_sectors"] for s in ("energy", "airlines", "petrochemicals"))

    def test_sectors_are_deduplicated(self):
        result = classify_financial_impact("Global", "crude oil prices surge")
        assert len(result["affected_sectors"]) == len(set(result["affected_sectors"]))

    def test_narrative_prompt_is_non_empty_string(self):
        result = classify_financial_impact("Global", "missile strike")
        assert isinstance(result["narrative_prompt"], str)
        assert len(result["narrative_prompt"]) > 0


# ─────────────────────────────────────────────────────────────────────────────
# event_type_to_article_type
# ─────────────────────────────────────────────────────────────────────────────

class TestEventTypeToArticleType:
    def test_military_maps_to_conflict(self):
        assert event_type_to_article_type("military_escalation") == "conflict"

    def test_sanctions_maps_to_politics(self):
        assert event_type_to_article_type("sanctions") == "politics"

    def test_trade_dispute_maps_to_finance(self):
        assert event_type_to_article_type("trade_dispute") == "finance"

    def test_none_defaults_to_politics(self):
        assert event_type_to_article_type(None) == "politics"

    def test_unmapped_type_defaults_to_politics(self):
        assert event_type_to_article_type("completely_unknown_type") == "politics"


# ─────────────────────────────────────────────────────────────────────────────
# _build_narrative_prompt
# ─────────────────────────────────────────────────────────────────────────────

class TestBuildNarrativePrompt:
    def test_includes_region(self):
        result = _build_narrative_prompt("Middle East", None, [], [], [])
        assert "Middle East" in result

    def test_includes_event_type_when_present(self):
        result = _build_narrative_prompt("Global", "military_escalation", [], [], [])
        assert "military escalation" in result

    def test_omits_event_type_when_none(self):
        result = _build_narrative_prompt("Global", None, [], [], [])
        assert "Event type" not in result

    def test_includes_sectors(self):
        result = _build_narrative_prompt("Global", None, ["energy", "defence"], [], [])
        assert "energy" in result and "defence" in result

    def test_ends_with_writing_instruction(self):
        result = _build_narrative_prompt("Global", None, [], [], [])
        assert "financial market implication" in result.lower()

    def test_caps_sectors_at_four(self):
        sectors = ["aaa", "bbb", "ccc", "ddd", "eee", "fff"]
        result = _build_narrative_prompt("Global", None, sectors, [], [])
        assert "eee" not in result and "fff" not in result


# ─────────────────────────────────────────────────────────────────────────────
# EventSeverityResponseMarker
# ─────────────────────────────────────────────────────────────────────────────

class TestEventSeverityResponseMarker:
    def test_valid_json_returns_none(self):
        marker = EventSeverityResponseMarker()
        assert marker.mark(_severity_json()) is None

    def test_valid_json_accumulates_events(self):
        marker = EventSeverityResponseMarker()
        marker.mark(_severity_json(3))
        assert len(marker.validEvents) == 3

    def test_invalid_json_returns_error_string(self):
        marker = EventSeverityResponseMarker()
        result = marker.mark("not json at all")
        assert isinstance(result, str) and len(result) > 0

    def test_invalid_json_stores_nothing(self):
        marker = EventSeverityResponseMarker()
        marker.mark("{invalid}")
        assert len(marker.validEvents) == 0

    def test_invalid_severity_value_returns_error(self):
        bad = json.dumps([{
            "economic_impact_severity": "extreme",
            "financial_markets_impact_severity": "low",
            "security_impact_severity": "low",
            "diplomatic_impact_severity": "low",
        }])
        marker = EventSeverityResponseMarker()
        assert marker.mark(bad) is not None

    def test_get_correct_returns_parseable_json(self):
        marker = EventSeverityResponseMarker()
        marker.mark(_severity_json(2))
        result = marker.get_correct()
        parsed = json.loads(result)
        assert len(parsed) == 2

    def test_get_correct_clears_state(self):
        marker = EventSeverityResponseMarker()
        marker.mark(_severity_json(1))
        marker.get_correct()
        assert len(marker.validEvents) == 0


# ─────────────────────────────────────────────────────────────────────────────
# EventJustificationResponseMarker
# ─────────────────────────────────────────────────────────────────────────────

class TestEventJustificationResponseMarker:
    def test_valid_json_returns_none(self):
        marker = EventJustificationResponseMarker()
        assert marker.mark(_justification_json()) is None

    def test_valid_json_accumulates_events(self):
        marker = EventJustificationResponseMarker()
        marker.mark(_justification_json(2))
        assert len(marker.validEvents) == 2

    def test_invalid_json_returns_error_string(self):
        marker = EventJustificationResponseMarker()
        result = marker.mark("not valid json")
        assert isinstance(result, str) and len(result) > 0

    def test_invalid_json_stores_nothing(self):
        marker = EventJustificationResponseMarker()
        marker.mark("bad")
        assert len(marker.validEvents) == 0

    def test_get_correct_returns_parseable_json(self):
        marker = EventJustificationResponseMarker()
        marker.mark(_justification_json(1))
        parsed = json.loads(marker.get_correct())
        assert len(parsed) == 1

    def test_get_correct_clears_state(self):
        marker = EventJustificationResponseMarker()
        marker.mark(_justification_json(1))
        marker.get_correct()
        assert len(marker.validEvents) == 0


# ─────────────────────────────────────────────────────────────────────────────
# get_final_report_instructions
# ─────────────────────────────────────────────────────────────────────────────

class TestGetFinalReportInstructions:
    def test_returns_non_empty_string(self):
        result = get_final_report_instructions()
        assert isinstance(result, str) and len(result) > 0

    def test_names_format_final_report_tool(self):
        assert "format_final_report" in get_final_report_instructions()

    def test_names_all_four_impact_categories(self):
        result = get_final_report_instructions()
        for category in ("Economic Impact", "Financial Market Impact", "Security Impact", "Diplomatic Impact"):
            assert category in result

    def test_is_deterministic(self):
        assert get_final_report_instructions() == get_final_report_instructions()


# ─────────────────────────────────────────────────────────────────────────────
# analyse_events — financial rules severity override (LLM calls mocked)
# ─────────────────────────────────────────────────────────────────────────────

class TestAnalyseEventsFinancialRules:
    """
    Tests the rule-based financial severity override logic in analyse_events.
    impact_serverities and impact_justifications are mocked so no LLM is needed.
    """

    def _run(self, events: list[Event]) -> list[Event]:
        from geo_agent.AnalystServer.analyst import analyse_events
        with patch("geo_agent.AnalystServer.analyst.impact_serverities",
                   new=AsyncMock(return_value=events)), \
             patch("geo_agent.AnalystServer.analyst.impact_justifications",
                   new=AsyncMock(side_effect=lambda evs: evs)):
            return asyncio.run(analyse_events(events))

    def test_military_escalation_overrides_financial_to_high(self):
        event = _event("troops launched missile strike on military base", Severity.low)
        result = self._run([event])
        assert result[0].financial_market_impact.severity == Severity.high

    def test_energy_shock_overrides_financial_to_high(self):
        event = _event("opec cuts oil production sending prices higher", Severity.low)
        result = self._run([event])
        assert result[0].financial_market_impact.severity == Severity.high

    def test_sanctions_overrides_financial_to_high(self):
        event = _event("us imposes new sanction on iran", Severity.low)
        result = self._run([event])
        assert result[0].financial_market_impact.severity == Severity.high

    def test_trade_dispute_overrides_financial_to_medium(self):
        event = _event("us imposes new tariff on chinese imports", Severity.low)
        result = self._run([event])
        assert result[0].financial_market_impact.severity == Severity.medium

    def test_coup_or_instability_overrides_financial_to_medium(self):
        event = _event("coup overthrows government", Severity.low)
        result = self._run([event])
        assert result[0].financial_market_impact.severity == Severity.medium

    def test_multiple_events_all_overridden(self):
        events = [
            _event("missile strike on military base", Severity.low),
            _event("us imposes tariff on eu goods", Severity.low),
        ]
        result = self._run(events)
        assert result[0].financial_market_impact.severity == Severity.high
        assert result[1].financial_market_impact.severity == Severity.medium

