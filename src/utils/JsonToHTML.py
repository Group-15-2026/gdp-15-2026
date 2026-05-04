import json
import html
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_RAW_FULL = (Path(__file__).parent.parent / "Templates" / "report_template.html").read_text(encoding="utf-8")
_T = {m.group(1): m.group(2).strip() for m in re.finditer(r'<template id="(\w+)">(.*?)</template>', _RAW_FULL, re.DOTALL)}
_RAW = re.sub(r'\n\s*<template id="\w+">.*?</template>', '', _RAW_FULL, flags=re.DOTALL)


def esc(v: Any) -> str:
    return html.escape("" if v is None else str(v))


def fmt(v: Any, d: int = 1) -> str:
    try:
        return f"{float(v):.{d}f}"
    except (TypeError, ValueError):
        return "N/A"


def fill(name: str, **kwargs) -> str:
    t = _T[name]
    for k, v in kwargs.items():
        t = t.replace(f"<!--{k}-->", v)
    return t


def render_badge(severity: Optional[str]) -> str:
    sev = (severity or "").strip().lower()
    css = {"low": "sev-low", "medium": "sev-medium", "high": "sev-high"}.get(sev, "sev-unknown")
    return fill("badge", CSS_CLASS=css, LABEL=esc(sev.title() if sev else "unknown"))


def render_impact(title: str, impact: Dict[str, Any]) -> str:
    return fill("impact_block",
        TITLE=esc(title),
        BADGE=render_badge(impact.get("severity")),
        JUSTIFICATION=esc(impact.get("justification", "No material impact identified.")))


def render_event(event: Dict[str, Any]) -> str:
    summary = event.get("summary")
    links = event.get("source_links") or []
    source_items = "".join(fill("source_item", HREF=esc(l), LABEL=esc(l)) for l in links)
    impacts = "".join(render_impact(title, event.get(key, {})) for title, key in [
        ("Economic Impact",         "economic_impact"),
        ("Financial Market Impact", "financial_market_impact"),
        ("Security Impact",         "security_impact"),
        ("Diplomatic Impact",       "diplomatic_impact"),
    ])
    return fill("event_card",
        EVENT=esc(event.get("event", "N/A")),
        CONTROVERSY=fmt(event.get("controversy")),
        SUMMARY_BLOCK=fill("summary_block", SUMMARY=esc(summary)) if summary else "",
        SOURCES_BLOCK=fill("sources_block", ITEMS=source_items) if links else "",
        IMPACTS=impacts)


# def render_actor(actor: Dict[str, Any]) -> str:
#     themes = actor.get("linked_themes") or []
#     theme_items = "".join(fill("list_item", TEXT=esc(t)) for t in themes) or fill("list_item", TEXT="None")
#     return fill("actor_card",
#         NAME=esc(actor.get("name", "N/A")),
#         ACTOR_TYPE=esc(actor.get("actor_type", "N/A")),
#         IMPACT=fmt(actor.get("impact")),
#         PUBLIC_OPINION=fmt(actor.get("public_opinion")),
#         CONTROVERSY=fmt(actor.get("controversy")),
#         MENTIONS_WEIGHT=str(int(actor.get("mentions_weight"))),
#         THEME_ITEMS=theme_items)


def render_themes(themes: List[str]) -> str:
    if not themes:
        return ""
    return fill("themes_card", ITEMS="".join(fill("list_item", TEXT=esc(t)) for t in themes))


def json_to_html(data: Dict[str, Any], title: str = "Analyst Report") -> str:
    if "events" in data and isinstance(data["events"], list):
        sections = [render_event(e) for e in data["events"]]
        sections.append(render_themes(data.get("themes") or []))
        body = "\n".join(sections)
    else:
        raise ValueError("Unsupported JSON structure.")

    return _RAW.replace("<!--TITLE-->", esc(title)).replace("<!--BODY-->", body)


def convert_json_file_to_html(input_json_path: str, output_html_path: str, title: str = "Analyst Report") -> None:
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(json_to_html(data, title=title))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python JsonToHTML.py input.json output.html")
        sys.exit(1)
    convert_json_file_to_html(sys.argv[1], sys.argv[2])
    print("HTML written to", sys.argv[2])
