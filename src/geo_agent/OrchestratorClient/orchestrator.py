# XX Note to implementer: Give a local LLM power to connect to an MCP client, and own the sequencing decisions required
# Consider adding an mcp structured prompt to the final summariser server (or each) to guide the LLM at each stage

from ..config import config

from datetime import date, timedelta
from langchain_ollama.chat_models import ChatOllama
from mcp_use import MCPAgent, MCPClient, set_debug

# Avoid printing messy logs
set_debug(0)   # XX trial removing to see compatibility with logging

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
that you are connected to in order to produce this briefing report.

You have access to tools for fetching web articles, tools to summarise and process these articles, and finally
tools to help combine the information from multiple articles together into a single cohesive whole which can
then be formatted as the final report using one final tool.

You will work with 'Article', 'Actor' and 'Event' objects, that will be passed between the tools. Once an object
has been passed to a particular tool, it should NEVER be passed back to that same tool again. Some tools will
add fields to objects when they return them, so make sure to check what outputs you have been given by each
tool before planning your next step. 
'''

# XX Currently just a testing placeholder
today = date.today()
yesterday = today - timedelta(days=1)
TASK_PROMPT = f"What news can you find on the topic of 'trade' from the {yesterday} to the {today}? " \
               "Extract the key actors, and all events from all relevant news articles. Display the actors alongside " \
               "their classification, and the number of times that they are referenced in different articles. " \
               "Follow this with a list of all events extracted from the articles, alongside the title of the " \
               "articles that they were extracted from."

def create_mcp_agent(mcp_client, system_prompt=SYSTEM_PROMPT, num_ctx=128*1024, max_steps=50):
    llm = ChatOllama(
        model=config.MODEL, 
        base_url="http://localhost:11434",
        # XX TODO: adjust this depending on hardware the system is running on
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