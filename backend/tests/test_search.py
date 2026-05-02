import pytest

from app.config import get_settings
from app.services.search import web_search


@pytest.mark.asyncio
async def test_search_provider_unavailable_fallback(monkeypatch):
    monkeypatch.setenv("WEB_SEARCH_PROVIDER", "none")
    get_settings.cache_clear()
    try:
        assert await web_search("latest ai news") == []
    finally:
        get_settings.cache_clear()
