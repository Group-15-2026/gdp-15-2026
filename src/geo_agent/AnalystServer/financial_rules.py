from __future__ import annotations

import logging 
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "financial_rules.yaml"

# --------------------------------------------------------------
# Event type organisation 
# order matters - detect event type returns first match
# ordered it in order of severity
# --------------------------------------------------------------

EVENT_TYPE_KEYWORDS: list[tuple[str, list[str]]] = [
    (
        "military_escalation",
        [
            "airstrike", "missile", "troops", "military", "forces",
            "invasion", "combat", "weapon", "warship", "artillery",
            "offensive", "bombing", "shelling", "attack", "strike",            
        ],
    ),
    (
        "sanctions",
        [
            "sanction", "embargo", "ban", "restrict", "blacklist",
            "freeze assets", "export control", "asset freeze",
            "financial restriction", "travel ban",
        ],
    ),
    (
        "trade_dispute",
        [
            "tariff", "trade war", "import duty", "trade deal",
            "wto", "protectionism", "trade barrier", "counter-tariff",
            "trade restriction", "customs duty",
        ],
    ),
    (
        "election", 
        [
            "election", "vote", "ballot", "polling", "referendum", 
            "president", "prime minister", "general election", 
            "snap election", "electoral",
        ],
    ),
    (
        "natural_disaster",
        [
            "earthquake", "flood", "tsunami", "hurricane", "typhoon",
            "wildfire", "drought", "famine", "cyclone", "volcanic",
        ],
    ),
    (
        "energy_shock",
        [
            "oil price", "gas price", "opec", "pipeline", "energy crisis", 
            "refinery", "lng", "energy supply", "power outage",
            "fuel shortage", 
        ],
    ),
    (
        "coup_or_instability",
        [
            "coup", "protest", "unrest", "riot", "overthrow",
            "martial law", "civil war", "insurrection", "uprising",
            "political crisis",
        ],
    ),
    (
        "diplomatic_change",
        [
            "peace deal", "ceasefire", "agreement", "normalisation",
            "accord", "treaty", "summit", "diplomatic relations",
            "peace talks", "reconciliation",
        ],
    ),
]

# -------------------------------------------------------------------------
# Commodity keyword list 
# all commodities checked independently
# -------------------------------------------------------------------------

COMMODITY_KEYWORDS: dict[str, list[str]] = {
    "oil": [
        "oil", "crude", "brent", "wti", "petroleum",
    ],
    "natural_gas": [
        "natural gas", "lng", "gas pipeline", "gas price",
    ],
    "wheat": [
        "wheat", "grain", "bread", "cereal", "food price",
    ],
    "semiconductors": [
        "chip", "semiconductor", "wafer", "fab", "tsmc", "nvidia",
    ],
    "lithium": [
        "lithium", "battery", "ev battery", "electric vehicle",
    ],
    "gold": [
        "gold", "bullion", "safe haven",
    ],
    "copper": [
        "copper", "base metal",
    ],
    "uranium": [
        "uranium", "nuclear fuel", "enrichment", "reactor",
    ],
}

# -------------------------------------------------------------------------
# event type -> article 
# mapping it to enum values in Article.py
# -------------------------------------------------------------------------

_EVENT_TYPE_TO_ARTICLE_TYPE: dict[str, str] = {
    "military_escalation":      "conflict",
    "sanctions":                "politics",
    "trade_dispute":            "finance",
    "election":                 "politics",
    "natural_disaster":         "tragedy",
    "energy_shock":             "finance",
    "coup_or_instability":      "conflict",
    "diplomatic_breakthrough":  "politics", 
}


# -------------------------------------------------------------------------
# config loader - want to erad YAML file once per process
# -------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_config() -> dict:
    logger.info(f"Loading financial rules config from {CONFIG_PATH}")
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    logger.info("Financial rules config loaded successfully.")
    return config

def classify_financial_impact(region:str, text: str) -> dict:
    config = _load_config()
    lower_text = text.lower()

    #1: detect event type
    event_type = _detect_event_type(lower_text)
    logger.debug(f"Detected event_type: {event_type!r}")

    #2: region -> sectors
    region_sectors: list[str] = (
        config.get("region_to_sectors", {}).get(region, [])
        or config["region_to_sectors"].get("Global", [])
    )

    #3: event type -> asset classes
    asset_classes: list[str] = []
    if event_type:
        asset_classes = (
            config.get("event_type_to_asset_class", {}).get(event_type, [])
        )
    
    #4: commodity detection 
    commodities_mentioned = _detect_commodities(lower_text)
    commodity_sectors: list[str] = []
    for commodity in commodities_mentioned:
        commodity_sectors.extend(
            config.get("commodity_to_sectors", {}).get(commodity, [])
        )
    logger.debug(f"Commodities detected: {commodities_mentioned}")

    #5: merge + deduplicate
    all_sectors = list(dict.fromkeys(region_sectors + commodity_sectors))

    #6: narrative prompt for LLM
    narrative_prompt = _build_narrative_prompt(
        region, event_type, all_sectors, asset_classes, commodities_mentioned
    )

    return {
        "event_type":               event_type,
        "affected_sectors":         all_sectors,
        "affected_asset_classes":   asset_classes,
        "commodities_mentioned":    commodities_mentioned,
        "narrative_prompt":         narrative_prompt,
    }

def event_type_to_article_type(event_type: Optional[str]) -> str:
    if not event_type:
        return "politics"
    return _EVENT_TYPE_TO_ARTICLE_TYPE.get(event_type, "politics")

def _detect_event_type(lower_text: str) -> Optional[str]:

    for event_type, keywords in EVENT_TYPE_KEYWORDS:
        if any(kw in lower_text for kw in keywords):
            return event_type
    return None

def _detect_commodities(lower_text: str) -> list[str]:
    return [
        commodity
        for commodity, keywords in COMMODITY_KEYWORDS.items()
        if any(kw in lower_text for kw in keywords)
    ]

def _build_narrative_prompt(
        region: str,
        event_type: Optional[str],
        sectors: list[str],
        asset_classes: list[str],
        commodities: list[str],

) -> str:
    parts = [f"Region: {region}."]

    if event_type:
        parts.append(f"Event type: {event_type.replace('_', ' ')}.")

    if sectors:
        parts.append(f"Exposed sectors: {', '.join(sectors[:4])}.")
    
    if asset_classes:
        parts.append(f"Relevant asset classes: {', '.join(asset_classes[:3])}.")

    if commodities:
        parts.append(f"Commodities involved: {', '.join(commodities)}.")

    parts.append(
        "Write one concise sentence describing the likely financial market implication" \
        ". Do not add new sectors or asset classes not listed above."
    )
    return " ".join(parts)
    
