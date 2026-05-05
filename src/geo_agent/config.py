from pydantic_settings import BaseSettings

# TODO This needs expanding, and linking to the .env files

class Settings(BaseSettings):
    # TODO should ideally pick based off of system capabilities
    MODEL : str = "gemma4:e2b"              # this model is the recommended local model (can also use gemma4:e2b)
    #//MODEL : str = "minimax-m2.5:cloud"      # this model is the recommended cloud model, however it uses a lot of the compute budget

    CONTEXT: int = 128 * 1024                # This context window size should allow for many articles and tool calls to be processed

    # Control the batch size sent to LLM. Larger values should lead to better performance, but will be more error prone (especially with smaller LLMs with reduced context)
    S_ACT_BATCH_SIZE : int = 10
    A_EVE_BATCH_SIZE : int = 5

# Instantiate the settings globally
config = Settings()