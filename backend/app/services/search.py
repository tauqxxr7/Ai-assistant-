from __future__ import annotations

import httpx

from app.config import get_settings
from app.schemas import SearchResult


async def web_search(query: str) -> list[SearchResult]:
    settings = get_settings()
    provider = settings.web_search_provider.lower()
    if provider == "brave" and settings.brave_search_api_key:
        return await _brave(query, settings.brave_search_api_key)
    if provider == "tavily" and settings.tavily_api_key:
        return await _tavily(query, settings.tavily_api_key)
    return []


async def _brave(query: str, api_key: str) -> list[SearchResult]:
    async with httpx.AsyncClient(timeout=get_settings().request_timeout_seconds) as client:
        response = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": 8},
            headers={"Accept": "application/json", "X-Subscription-Token": api_key},
        )
        response.raise_for_status()
    payload = response.json()
    return [
        SearchResult(title=item.get("title"), url=item["url"], snippet=item.get("description"))
        for item in payload.get("web", {}).get("results", [])
        if item.get("url")
    ]


async def _tavily(query: str, api_key: str) -> list[SearchResult]:
    async with httpx.AsyncClient(timeout=get_settings().request_timeout_seconds) as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": 8, "search_depth": "advanced"},
        )
        response.raise_for_status()
    payload = response.json()
    return [
        SearchResult(title=item.get("title"), url=item["url"], snippet=item.get("content"))
        for item in payload.get("results", [])
        if item.get("url")
    ]
