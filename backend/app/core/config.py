"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """DClaw Research application settings."""

    app_env: str = "dev"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8098

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_research"
    )
    sync_database_url: str = (
        "postgresql://postgres:postgres@localhost:5432/dclaw_research"
    )
    redis_url: str = "redis://localhost:6379/0"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:32b"
    ollama_embed_model: str = "nomic-embed-text"

    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"

    firecrawl_api_key: str = ""
    searxng_url: str = ""
    jina_api_key: str = ""

    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.celery_broker_url is None:
            self.celery_broker_url = self.redis_url
        if self.celery_result_backend is None:
            self.celery_result_backend = self.redis_url


settings = Settings()
