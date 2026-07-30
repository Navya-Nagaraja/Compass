"""
Centralized application settings, loaded from environment variables.
Keeping all config in one typed object makes it easy to see every
external dependency the service has at a glance.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Compass"
    environment: str = "development"

    # LLM provider: "anthropic", "openai", or "mock" (no key needed, canned
    # responses so the app is demoable out of the box).
    llm_provider: str = "mock"
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    llm_model: str = "claude-sonnet-4-6"

    # Retrieval settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_store_path: str = "./data/vector_store"
    top_k: int = 4
    chunk_size: int = 800
    chunk_overlap: int = 120

    # CORS
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_prefix = "COMPASS_"


@lru_cache
def get_settings() -> Settings:
    return Settings()
