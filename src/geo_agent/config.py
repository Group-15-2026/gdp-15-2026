from pydantic_settings import BaseSettings

# XX Note that this needs expanding, and linking to the .env files

class Settings(BaseSettings):
    # XX should ideally pick based off of system capabilities
    MODEL : str = "gemma4:e4b"
    #MODEL : str = "qwen3:latest"      # XX small enough to run completely on my laptop integrated graphics for testing purposes

    #class Config:
    #    env_file = ".env"

# Instantiate the settings globally
config = Settings()