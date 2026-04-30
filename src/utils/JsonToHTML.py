import json
import html
import sys
from typing import Any, Dict, List, Optional


def esc(value: Any) -> str:
    """Escape values for safe HTML output."""
    return html.escape("" if value is None else str(value))


def severity_badge(severity: Optional[str]) -> str:
    """Render a small badge for low/medium/high severity."""
    sev = (severity or "").strip().lower()
    css_class = {
        "low": "sev-low",
        "medium": "sev-medium",
        "high": "sev-high",
    }.get(sev, "sev-unknown")
    label = sev if sev else "unknown"
    return f'<span class="badge {css_class}">{esc(label.title())}</span>'


def format_number(value: Any, decimals: int = 1) -> str:
    """Format numeric values safely."""
    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"


def render_actor_summary(actor: Dict[str, Any]) -> str:
    """Render actor update summary section."""
    linked_themes = actor.get("linked_themes") or []
    themes_html = ""
    if linked_themes:
        themes_html = "".join(
            f'<li>{esc(theme)}</li>' for theme in linked_themes
        )
    else:
        themes_html = "<li>None</li>"

    return f"""
    <section class="card">
      <h2>Actor Update Summary</h2>
      <div class="grid two-col">
        <div><strong>Name</strong><br>{esc(actor.get("name", "N/A"))}</div>
        <div><strong>Actor Type</strong><br>{esc(actor.get("actor_type", "N/A"))}</div>
        <div><strong>Impact</strong><br>{format_number(actor.get("impact"))}</div>
        <div><strong>Public Opinion</strong><br>{format_number(actor.get("public_opinion"))}</div>
        <div><strong>Controversy</strong><br>{format_number(actor.get("controversy"))}</div>
        <div><strong>Mentions Weight</strong><br>{int(actor.get("mentions_weight"))}%</div>
      </div>

      <div class="subsection">
        <h3>Linked Themes</h3>
        <ul>{themes_html}</ul>
      </div>
    </section>
    """


def render_impact_block(title: str, impact: Dict[str, Any]) -> str:
    """Render one event impact block."""
    severity = impact.get("severity")
    justification = impact.get("justification", "No material impact identified.")
    return f"""
    <div class="impact-block">
      <div class="impact-header">
        <h4>{esc(title)}</h4>
        {severity_badge(severity)}
      </div>
      <p>{esc(justification)}</p>
    </div>
    """


def render_event_summary(event: Dict[str, Any]) -> str:
    """Render event summary section."""
    return f"""
    <section class="card">
      <h2>Event Summary</h2>
      <div class="grid one-col">
        <div><strong>Event</strong><br>{esc(event.get("event", "N/A"))}</div>
        <div><strong>Controversy</strong><br>{format_number(event.get("controversy"))}</div>
      </div>

      <div class="subsection">
        <h3>Impact Assessment</h3>
        {render_impact_block("Economic Impact", event.get("economic_impact", {}))}
        {render_impact_block("Financial Market Impact", event.get("financial_market_impact", {}))}
        {render_impact_block("Security Impact", event.get("security_impact", {}))}
        {render_impact_block("Diplomatic Impact", event.get("diplomatic_impact", {}))}
      </div>
    </section>
    """


def detect_payload_type(data: Dict[str, Any]) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Detect whether input is:
    - actor only
    - event only
    - combined wrapper with actor_update_summary / event_summary
    """
    actor = None
    event = None

    if "actor_update_summary" in data:
        actor = data["actor_update_summary"]
    elif {"name", "actor_type", "impact", "public_opinion", "controversy", "mentions_weight"}.issubset(data.keys()):
        actor = data

    if "event_summary" in data:
        event = data["event_summary"]
    elif {"event", "controversy", "economic_impact", "financial_market_impact", "security_impact", "diplomatic_impact"}.issubset(data.keys()):
        event = data

    return {"actor": actor, "event": event}


def json_to_html(data: Dict[str, Any], title: str = "Analyst Report") -> str:
    """Convert supported JSON payload into a complete HTML document."""
    payload = detect_payload_type(data)
    actor = payload["actor"]
    event = payload["event"]

    sections: List[str] = []

    if actor:
        sections.append(render_actor_summary(actor))
    if event:
        sections.append(render_event_summary(event))

    if not sections:
        raise ValueError(
            "Unsupported JSON structure. Expected actor summary, event summary, or combined object."
        )

    body = "\n".join(sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 24px;
      background: #f5f7fb;
      color: #1f2937;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
    }}
    h1 {{
      margin-bottom: 24px;
    }}
    .card {{
      background: #ffffff;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    }}
    .grid {{
      display: grid;
      gap: 16px;
    }}
    .two-col {{
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }}
    .one-col {{
      grid-template-columns: 1fr;
    }}
    .subsection {{
      margin-top: 20px;
    }}
    ul {{
      margin: 8px 0 0 20px;
    }}
    .impact-block {{
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 14px;
      margin-bottom: 12px;
      background: #fafafa;
    }}
    .impact-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
    }}
    .impact-header h4 {{
      margin: 0;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: bold;
    }}
    .sev-low {{
      background: #dcfce7;
      color: #166534;
    }}
    .sev-medium {{
      background: #fef3c7;
      color: #92400e;
    }}
    .sev-high {{
      background: #fee2e2;
      color: #991b1b;
    }}
    .sev-unknown {{
      background: #e5e7eb;
      color: #374151;
    }}
    .footer-note {{
      margin-top: 24px;
      font-size: 13px;
      color: #6b7280;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>{esc(title)}</h1>
    {body}
    
  </div>
</body>
</html>
"""


def convert_json_file_to_html(input_json_path: str, output_html_path: str, title: str = "Analyst Report") -> None:
    """Read JSON file and write HTML file."""
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    html_output = json_to_html(data, title=title)

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_output)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python JsonToHTML.py input.json output.html")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_json_file_to_html(input_file, output_file)    

    print("HTML written to", sys.argv[2])