import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str = "Live AI Assistant API"
    environment: str = "development"
    database_url: str = "sqlite:///./assistant.db"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str | None = None
    web_search_provider: str = "none"
    brave_search_api_key: str | None = None
    tavily_api_key: str | None = None
    user_agent: str = "LiveAIAssistant/1.0 (+responsible-crawler)"
    request_timeout_seconds: float = 12.0
    max_crawl_pages: int = 8


@lru_cache
def get_settings() -> Settings:
    return Settings(
        environment=os.getenv("ENVIRONMENT", "development"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./assistant.db"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        web_search_provider=os.getenv("WEB_SEARCH_PROVIDER", "none"),
        brave_search_api_key=os.getenv("BRAVE_SEARCH_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        user_agent=os.getenv("USER_AGENT", "LiveAIAssistant/1.0 (+responsible-crawler)"),
        request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "12.0")),
        max_crawl_pages=int(os.getenv("MAX_CRAWL_PAGES", "8")),
    )
