# gdp-15-2026

Multi-Agent Geopolitical Intelligence Assistant (Project D)

  

## Project Architecture

![Architecture Diagram](https://github.com/isaacarch/gdp-15-2026/blob/main/Design%20Documentation/Architecture/NewGroupProjectArch_MCP_Final.svg)


## Running Project (whilst in development)
In order to use the local LLMs, ollama must be installed on your local computer, and running:
* You can run start ollama running by typing "ollama start" into a terminal. 
* Currently we are using the model "gemma4:e4b" in the orchestrator, so that must be installed (e.g. by running "ollama pull gemma4:e4b").
* Note: If your ollama installation isn't set up to use GPU acceleration (or you don't have enough VRAM), then the LLM may be quite slow. You can check whether your LLM is using the CPU, GPU, or a mixture, by running "ollama ps". If you want a quick cloud based alternative then, if you have an ollama account, you can use the model "gemma4:31b-cloud" by tweaking the variable "MODEL" in "src/geo_agent/OrchestratorClient/llm_agent.py". Note that there are a limited number of cloud compute credits per day/week, so this may slowly eat away at your free quota if running lots of tests.
* Eventually, this will be made easter via a batch or bash script, and/or packaging our python project as an executable .exe application, but for now we are just testing.
