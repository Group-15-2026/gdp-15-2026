from ..config import config

from datetime import date, timedelta
from langchain_ollama.chat_models import ChatOllama
from mcp_use import MCPAgent, MCPClient

CONFIG = {
    "mcpServers": {
        "collector": {
            "command": "uv",
            "args": ["run", "python", "-m", "geo_agent.CollectorServer.collector"]
        },
        "summariser": {
            "command": "uv",
            "args": ["run", "python", "-m", "geo_agent.SummariserServer.summariser"]
        },
        "analyst": {
            "command": "uv",
            "args": ["run", "python", "-m", "geo_agent.AnalystServer.analyst"]
        }
    }
}

def create_mcp_client():
    return MCPClient.from_dict(CONFIG)

SYSTEM_PROMPT = '''
You are a geopolitical analyst agent, designed to look at recent world news, and create a concise morning 
briefing for a mid-level analyst at a financial services / policy organisation. You should use the tools 
that you are connected to in order to produce this briefing report. Always begin by looking at the documentation
and input / output types for each tool, so that you know how and when to use them.

You have access to the tools 'collect_articles' (which collects relevant articles from the last 24hrs), and
'search_news' (which allows for more specific news to be fetched on particular topics, over particular date ranges.
'collect_articles' should always be called as the very first step, to fetch recent articles. When required, 
'search_news' can be called to to get additional articles on specific topics. It may return some duplicates
compared to 'collect_articles', which should be ignored.

Once articles have been fetched, they should be passed to the 'extract_events' tool, to get the key actors and
events from the articles. These events can then be passed to the 'analyse_events' tool, to fill in additional
event fields regarding impacts and severities. Only once that has been done, should you call 
'gen_final_report_instructions' to get your specific instructions on generating the final report. Finally, 
you should call the 'format_final_report' tool with your final markdown report as in the input. The tool will
then format and save this, and return a success message. Once you have received the success message, you may 
finally consider the task to be complete.

You will work with 'Article', 'Actor' and 'Event' objects, that will be passed between the tools. Once an object
has been passed to a particular tool, it should NEVER be passed back to that same tool again. Some tools will
add fields to objects when they return them, so make sure to check what outputs you have been given by each
tool before planning your next step. 

If two tools may be called in parallel, then always attempt to call them in parallel, so long as none of the 
same input arguments are being passed to the methods that get called in parallel. 

You should begin each task by making a plan of your actions, with a checklist that you can check off. After
each reasoning step and tool call, update your checklist of tasks. Make sure that you complete all tasks
required before returning your final response.
'''

# TODO Currently just a testing placeholder - will need to properly cultivate once completed
today = date.today()
yesterday = today - timedelta(days=1)
TASK_PROMPT = f"What news can you find on the topic of 'trade' from the {yesterday} to the {today}? " \
               "Extract the key actors, and all events from all relevant news articles. Display the actors alongside " \
               "their classification, and the number of times that they are referenced in different articles. " \
               "Follow this with a list of all events extracted from the articles, alongside the title of the " \
               "articles that they were extracted from. Finally, output a list of all of the claims made by the different " \
               "articles, as well as an indication of how many articles back up or disagree with each claim."

def create_mcp_agent(mcp_client, system_prompt=SYSTEM_PROMPT, num_ctx=config.CONTEXT, max_steps=50):
    llm = ChatOllama(
        model=config.MODEL, 
        base_url="http://localhost:11434",
        num_ctx=num_ctx,        # extend context to allow the model to work with many articles
        reasoning=True
    )

    # Wire the LLM to the client
    agent = MCPAgent(
        llm=llm, 
        client=mcp_client, 
        system_prompt=system_prompt,
        max_steps=max_steps     # set the maximum number of tool calling steps the model can perform
    )

    return agent