from .impacts import impact_serverities, impact_justifications
from .financial_rules import classify_financial_impact

from ..Entities.Article import Article
from ..Entities.Events import Event, Severity

from datetime import datetime
import logging
from markdown_pdf import MarkdownPdf, Section
from mcp.server.fastmcp import FastMCP
import os

from utils import setup_server_logging

setup_server_logging("analyst")

logger = logging.getLogger(__name__)

analyst_mcp = FastMCP(name="Analyst MCP Server")

@analyst_mcp.tool()
def group_articles(articles: list[Article]) -> dict[str, list[Article]]:
    raise NotImplementedError()

@analyst_mcp.tool()
async def analyse_events(events: list[Event]) -> list[Event]:
    '''
    Calculates the: economic impact, financial market impact, security impact and diplomatic impact
    of each of the events from its source articles. Updates the events with with these impacts and
    returns the updated events.

    You should only pass in event objects that have been outputted by the 'extract_events' tool in 
    the 'summariser' mcp server, NOT events that have already been processed.
    '''
        
    scored_events = await impact_serverities(events)

    for event in scored_events:
        classification = classify_financial_impact("Global", event.event)
        event_type = classification["event_type"]
        
        high_types = {"military_escalation", "energy_shock", "sanctions"}
        med_types = {"trade_dispute", "coup_or_instability", "diplomatic_change"}
        
        if event_type in high_types:
            if event.financial_market_impact:
                rule_severity = Severity.high
        elif event_type in med_types:
            if event.financial_market_impact:
                rule_severity = Severity.medium
        else:
            event.financial_rules_hint = classification 
            
    
    analysed_events = await impact_justifications(scored_events)

    return analysed_events

@analyst_mcp.tool()
def get_final_report_instructions() -> str:
    '''
    Fetch instructions on how to generate the final report, including format, structure and examples.
    '''
    return """Role: You are a Senior Geopolitical Risk Analyst and Event Curation Agent.

Task:

Event Selection:
Identify and select the top 5-10 most relevant and high-signal geopolitical events based on overall significance, impact severity, and global relevance.
Prioritize events with medium or high impact across multiple categories.

Event Enrichment:
For each selected event:
event: Use the original event description (cleaned if necessary).
summary: Write a 3-5 sentence concise analytical summary explaining context, actors, and implications.
source_links: Include 2-3 relevant article links if available. 
impact fields: Use the provided severity levels and justifications exactly as given. Do not modify or regenerate them.
financial_rules_context: if a <financial_rules_context> tag is present, use the listed asset classes and sectors to add precision to the Financial Market Impact justification sentence

Actor Identification:
Identify 3-5 key actors (countries, organizations, or individuals) across the selected events.
For each actor, provide a brief description of their role and relevance to the events (1-2 sentences).
Prioritize actors with the greatest influence or repeated presence across events.

Claim Extraction:
Identify 3-5 opinionated claims linking to blame or causation, and list the source that they came from. Focus on claims that have very high (>8) or very low (<-8) opinion scores.

Theme Extraction:
Identify 2-3 high-level themes that capture common patterns across the selected events (e.g., Great Power Competition, Energy Security, Regional Instability).

Summary:
Give a concise summary of how all of the news on events and actors link together. 

Output Format:
Call the 'format_final_report' tool with only the input of a structured Markdown document with the following sections:

News Overview / Introduction
2-3 sentences on the main themes covered in the selected events

Top Geopolitical Events
Event 1: [Event Title]
Summary: ...
Source Article Links: ...
Economic Impact: [severity] - justification
Financial Market Impact: [severity] - justification
Security Impact: [severity] - justification
Diplomatic Impact: [severity] - justification

(Repeat for each event)

Key Actors
Actor 1: Role and relevance
Actor 2: Role and relevance
Actor 3: Role and relevance
(3-5 actors total)

Key Themes
Theme 1
Theme 2
Theme 3 (optional)

Major Claims

[list of news sources referenced in the processed articles]

Formatting Requirements:

Highlight high-impact elements:
Use bold for all impacts and their severity ratings.
Add line breaks at the end of each segment of the event breakdowns.
Embed article urls as hyperlinks to the article titles.
Ensure clean, readable Markdown structure with consistent formatting.

Constraints:

ONLY pass the Markdown content to 'format_final_report'. No explanations or extra text.
Do not invent facts beyond the provided input.
Maintain consistency between severity labels and provided justifications.
Keep summaries analytical, not narrative or speculative."""

@analyst_mcp.tool()
def format_final_report(report: str) -> str:
    '''
    Takes a final markdown report as input, and converts it into a final pdf report which is then saved for human review.
    '''
    pdf = MarkdownPdf()
    pdf.meta["title"] = "Daily Report"
    pdf.meta["author"] = "APEX:E3 | Oxford CS"
    
    #css = "table, th, td {border: 1px solid black;}"
    css = '''
table {
    border-collapse: collapse; 
    width: 100%;
    margin: 25px 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 14px;
    color: #222222;
}

th, td {
    border-bottom: 1px solid #eeeeee; 
    padding: 12px 15px;
    text-align: left;
}

th {
    background-color: #ffffff; 
    color: #000000;
    font-weight: 600;
    border-bottom: 2px solid #333333; 
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: 0.5px;
}

tr:last-of-type td {
    border-bottom: 2px solid #dddddd;
}
'''
    pdf.add_section(Section(report), user_css=css)

    now = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    fullFileName = f"Reports/archive/Daily Summary ({now}).pdf"

    # Specify the nested directory structure
    nested_directory = "Reports/archive"

    # Create nested directories
    try:
        os.makedirs(nested_directory)
        logger.info(f"Nested directories '{nested_directory}' created successfully")
    except FileExistsError:
        logger.error(f"One or more directories in '{nested_directory}' already exist")
    except PermissionError:
        logger.error(f"Permission denied: Unable to create '{nested_directory}'")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    pdf.save("Reports/Latest Report.pdf")
    pdf.save(fullFileName)

    logger.info("Reports saved successfully")

    return "Successfully generated and saved final pdf report"

if __name__ == "__main__":
    analyst_mcp.run()
