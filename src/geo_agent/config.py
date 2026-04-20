from pydantic_settings import BaseSettings

# XX Note that this needs expanding, and linking to the .env files

class Settings(BaseSettings):
    # XX should ideally pick based off of system capabilities
    #MODEL : str = "gemma4:e4b"              # this model is the recommended local model
    MODEL : str = "minimax-m2.7:cloud"     # this model is the recommended cloud model, however it uses a lot of the compute budget

    # Control the batch size sent to LLM. Larger values should lead to better performance, but will be more error prone (especially with smaller LLMs with reduced context)
    S_ACT_BATCH_SIZE : int = 10

    #class Config:
    #    env_file = ".env"

# Instantiate the settings globally
config = Settings()