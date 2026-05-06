from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# TODO This needs expanding, and linking to the .env files

class Settings(BaseSettings):
    # Load device/user specific settings from .env
    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")

    # ! The below are the DEFAULT settings, but will be overwritten by any .env file

    MODEL : str = "gemma4:e4b"              # This model is the recommended local model (can also use gemma4:e2b)
    #//MODEL : str = "minimax-m2.5:cloud"      # This model is the recommended cloud model, however it uses a lot of the compute budget

    CONTEXT: int = 128 * 1024               # This context window size should allow for many articles and tool calls to be processed
    
    CONC_CLOUD_RATE: int = 4                # This is the number of concurrent cloud requests that you allow to be sent per second
    CONC_LOCAL_RATE: int = 16               # This should be the value that you have set OLLAMA_NUM_PARALLEL to (or slightly greater)

    # Control the batch size sent to LLM. Larger values should lead to better performance, but will be more error prone (especially with smaller LLMs with reduced context)
    S_ACT_BATCH_SIZE : int = 10
    A_EVE_BATCH_SIZE : int = 5
    S_EVENT_MERGE_BATCH_SIZE: int = 25

    # Control the number of words in an event or claim
    CLAIM_SIZE : int = 20
    EVENT_SIZE : int = 20

# Instantiate the settings globally
config = Settings()