from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# Resolve .env from the project root (crawl4ai-project/) regardless of cwd.
# backend/app/core/config.py  →  parents[3] = crawl4ai-project/
_ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    notion_token: str = Field(..., env="NOTION_TOKEN")
    notion_database_id: str = Field(..., env="NOTION_DATABASE_ID")
    ollama_model: str = Field(default="llama3.2:1b", env="OLLAMA_MODEL")
    brew_base_url: str = Field(default="https://app.brewcontent.ai", env="BREW_BASE_URL")

    model_config = {
        "env_file": str(_ROOT_ENV),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
