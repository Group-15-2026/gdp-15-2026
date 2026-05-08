# gdp-15-2026

Multi-Agent Geopolitical Intelligence Assistant (Project D)

## Project Architecture
![Architecture Diagram](https://github.com/isaacarch/gdp-15-2026/blob/main/Design%20Documentation/Architecture/GDP.svg)

## Running The Project
### Initial Installation Instructions
1. Clone the repository locally
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), and run `uv sync` to set up the virtual environment
3. Run `uv run -- spacy download en_core_web_trf` to install the NLP Model in use
4. Install [ollama](https://ollama.com/download)
5. Download your chosen ollama model using `ollama pull [model name]` (see [Selecting your LLM](#selecting-your-llm) below for advice on which model to pick)
6. Set up a [newsapi](https://newsapi.org/) account, and get an API key
7. Create a ".env" file in the top level of your local repository, and add the line `NEWSAPI_KEY=[your api key]`
8. Configure any other environment variables in the ".env" file / ollama (see [Environment Variable Tuning](#environment-variable-tuning) below for more information), including pointing the project to your chosen LLM (downloaded in step 5)
9. **Run the project** using `uv run src/main.py` (this may take a while). Ollama must be running in the background on your PC for this to work - the `ollama ps` command which displays the models currently loaded on your system will automatically start the ollama server in the background if it was not already running.
10. View the generated report in the top level "Reports/" folder - there will be both a "Latest Report.pdf", and an archive of all previously generated reports with timestamps. If you need to understand the tool calling decisions that the orchestrator made, then you can view logs, broken down by MCP server, in the "logs/" folder

### Selecting your LLM
There are countless Large Language Models available on ollama, and the exact choice will depend on your hardware. Whatever your choice however, a model with tool calling abilities is a must (otherwise it won't be able to use the project's MCP servers), and a model with thinking/reasoning capabilities is strongly advised. Models should also have support for a context window of size at least 128K tokens. Some of my top recommendations are listed below:
* **Qwen3.6:35b**: A very powerful local model which excels in tool calling, if your hardware can handle it then this model will be perfect. It can take 23-27GB of memory however, so will require a powerful GPU (e.g. RTX 3090 or better).
* **Minimax-m2.5:cloud**: Currently the most powerful cloud model available on Ollama without a paid subscription, if your hardware isn't up to a heavy-weight local model, this is a highly recommended alternative. There is a limited quota of free cloud compute, however you should be able to run this project end to end at least 15 times per month on the free quota. If you have a paid ollama subscription, then the newer **minimax-m2.7:cloud** model is even more capable, you will also have access to other cutting edge models like **kimi-k2.6**, and **deepseek-v4**.
* **Gemma4:31b**: Whilst this model is highly efficient and powerful, its thought/reasoning tags sometimes get mixed up with tool calls, leading to unreliable performance. Watch this space however - google may yet fix these issues.
* **Qwen3.5:9b**: A more midrange model with good tool calling performance, this model will work on smaller GPUs (7-10GB VRAM).
* **Gemma4:e4b**: For its size, this model is exceptionally capable, however it suffers from the same tool calling issues as its larger sibling above.

A side note - the MCP servers here can be taken and directly linked to Claude Code, or any other industry LLMs with support for custom MCP integration. This will replace the top level orchestrator with your chosen claude agent (which could also be from ollama), however the LLM calls made within the tools would still use ollama. They have much less work to do however, and so would work well with very small models, like gemma4:e4b, or even models with no tool calling skills (so long as they can output structured JSON).

### Environment Variable Tuning
There are two kinds of environment variables that can be set - project environment variables, and Ollama environment variables:

#### Project Environment Variables
These are set in the ".env" file. Other than `NEWSAPI_KEY`, they each have a default value set in src/geo_agent/config.py, but they can all be overwritten:
* `MODEL` selects the specific ollama model being used (default `gemma4:e4b`).
* `CONTEXT` selects the size of the context window (in tokens) of the LLM instances used in the project. It defaults to 128K (`131072`), and any lower than this will tend to prevent the LLM from staying focused and completing the task. It is not recommended to change this down, but if you have suitable hardware (and a compatible model) then it can be increased (e.g. to 256K).
* `CONC_CLOUD_RATE` selects the maximum number of ollama api calls that the project will perform per second, in order to avoid surpassing the rate limits that ollama impose. It defaults to 4, but the project will catch any rate errors that come from increasing it further, so you are free to experiment with larger values (particularly if you have a paid ollama subscription, with higher usage limits). Note that this variable does not impact locally run models (those that don't end in ":cloud") at all.
* `CONC_LOCAL_RATE` selects the maximum number of connections that can be established with your local LLM at any one time, and it is recommended that this should be set to exactly the value of your `OLLAMA_NUM_PARALLEL` ollama environment variable (see [Ollama Environment Variables](#ollama-environment-variables) below).
* `S_ACT_BATCH_SIZE` selects the batch size of extracted actors to be sent to the LLM for classification. It defaults to 10, but you may wish to increase or decrease it depending on the capability of your chosen LLM. Smaller LLMs may struggle with larger batches, but with larger LLMs the project will run faster with larger batch sizes.
* `A_EVE_BATCH_SIZE` is similar to the above, and is responsible for selecting the batch size of the events that will be sent to the LLM for impact justification generation. It defaults to 5, but otherwise should be increased or decreased as above.
* `S_EVENT_MERGE_BATCH_SIZE` is the final batch size - it selects the number of events that should be offered to the LLM for 'merging' at any one time. It defaults to 25, and it is highly recommended not to decrease it below this, as it will lead to the event extraction being much slower. You may experiment with increasing it however. 
* `CLAIM_SIZE` is the maximum number of words that a claim extracted from an article can be. Longer claims will be more detailed and precise, but may generalise to the wider news context less well.
* `EVENT_SIZE` is the maximum number of words that a first order event (i.e. extracted directly from an article, and not merged with any other events) can be. Longer events give the LLM more information when merging events, and so tend to lead to higher quality events in the final report. Events should not be made *too* large however, as this may lead to them becoming hyper-specific.

#### Ollama Environment Variables
There are a number of system environment variables which can be set to configure how ollama behaves. Since the performance of ollama is the main determining factor in how quickly the project will run, it is worth taking some time to adjust these before running the project. Note that these environment variables only affect locally running models, so if you are using a cloud model, then you can ignore them.

How you set the environment variables depends on your system, and how ollama is running. On windows, MacOS, and linux systems where ollama isn't running as a background service, you can simply stop ollama, set the environment variables in your usual way, and then start ollama again. If you exported the variables in a particular terminal, then you should run `ollama serve` to start the ollama server there with the specific temporary environment variables.

If you want to increase the performance of your LLM installation, then the below variables may be useful:
* `OLLAMA_NUM_PARALLEL` controls how many parallel prompts can be processed by the same local model. Whilst it can't work miracles and achieve linear speed ups, it can help to increase inference throughput, and is highly recommended if you can afford the associated memory overhead (the context window needs to be duplicated for each parallel run, which can increase memory usage significantly for large context windows). The value that you select here should be mirrored by the `CONC_LOCAL_RATE` project variable (see [Project Environment Variables](#project-environment-variables) above), otherwise the increased throughput won't be utilised by the project, but you'll still use up more memory.
* `OLLAMA_VULKAN` is a binary flag which can be used to force ollama to use GPUs which aren't natively supported (e.g. integrated graphics). It is worth noting that on many systems, due to precision format mismatches, if the model has to use both integrated graphics *and* the CPU (you can see the exact split by running `ollama ps`) due to insufficient memory being allocated to the GPU (note that Windows hard caps the GPUs shared memory at 50% of the system memory), then the LLM may be completely non-functional, and return absolute garbage. To avoid this, set this variable with care, and make sure to check if there is a CPU/GPU split by using `ollama ps`.
* `OLLAMA_MAX_LOADED_MODELS` won't effect the project in its current state, however if it were adapted (very very minor few line alterations) to use different LLM models in different components, then you would need this variable to prevent ollama from performing model thrashing (constantly swapping different LLMs in and out of memory) - it allows the system to hold X different models in memory at once (provided that your hardware can afford it - this would typically require a dedicated GPU with ample VRAM).

If you want to reduce the memory usage of your LLM installation, then the below variables may be useful:
* By setting `OLLAMA_FLASH_ATTENTION=1` and `OLLAMA_KV_CACHE_TYPE=q4_0`, you can potentially reduce the amount of memory that a given LLM requires to run. Quantisation can model accuracy very slightly, but also decreases memory usage significantly (including the memory used for the context window, which is particularly helpful if `OLLAMA_NUM_PARALLEL` is causing multiple context windows to be stored). I would recommend these variables to be set regardless of your system, because even on high end hardware, the memory reductions will allow you to make other changes (e.g. even bigger models or context windows) that wouldn't have been possible otherwise.
