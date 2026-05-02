from __future__ import annotations

import json
import re
from collections.abc import AsyncIterator
from urllib.parse import urlparse

from app.schemas import ChatAnswer, ChatRequest, Source
from app.services.crawler import PageContent, domain_from_url, extract_page_content, sitemap_aware_pages
from app.services.llm import LLMClient
from app.services.memory import MemoryStore
from app.services.search import web_search


CURRENT_PATTERNS = re.compile(r"\b(latest|today|current|recent|now|updated|news|price|version|updates?)\b", re.I)
URL_PATTERN = re.compile(r"https?://[^\s]+|(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?")
MEMORY_SAVE_PATTERN = re.compile(r"\b(remember|save this|note that)\b", re.I)


class AgentOrchestrator:
    def __init__(self, memory: MemoryStore | None = None, llm: LLMClient | None = None) -> None:
        self.memory = memory or MemoryStore()
        self.llm = llm or LLMClient()

    async def answer(self, request: ChatRequest) -> ChatAnswer:
        statusless = await self._build_answer(request, lambda _: None)
        return statusless

    async def stream(self, request: ChatRequest) -> AsyncIterator[str]:
        async def emit(event: str, data: dict) -> str:
            return f"event: {event}\ndata: {json.dumps(data)}\n\n"

        statuses: list[str] = []

        def collect(status: str) -> None:
            statuses.append(status)

        yield await emit("status", {"label": "thinking"})
        answer = await self._build_answer(request, collect)
        for status in statuses:
            yield await emit("status", {"label": status})
        for chunk in await self._chunks(answer.answer):
            yield await emit("token", {"text": chunk})
        yield await emit("final", answer.model_dump())

    async def _chunks(self, text: str) -> list[str]:
        return [token + " " for token in text.split(" ")]

    async def _build_answer(self, request: ChatRequest, status) -> ChatAnswer:
        message = request.message.strip()
        remembered = self.memory.retrieve(message, limit=4)

        if MEMORY_SAVE_PATTERN.search(message):
            key = message[:80]
            self.memory.save(key=key, value=message)

        needs_web = bool(CURRENT_PATTERNS.search(message))
        domain = self._extract_domain(message)
        pages: list[PageContent] = []
        search_sources: list[Source] = []
        verified: list[str] = []
        missing: list[str] = []

        if domain:
            status("checking robots.txt")
            pages, verified, missing = await sitemap_aware_pages(domain, message)
            needs_web = True

        if needs_web and not pages:
            status("searching")
            results = await web_search(message)
            search_sources = [Source(title=result.title, url=result.url, snippet=result.snippet) for result in results]
            status("verifying")
            for result in results[:4]:
                try:
                    pages.append(await extract_page_content(result.url))
                except Exception as exc:  # noqa: BLE001
                    missing.append(f"{result.url} could not be opened: {exc}")
            if not results:
                missing.append("No search provider returned results. Configure BRAVE_SEARCH_API_KEY or TAVILY_API_KEY.")

        context = self._context(message, remembered, pages, search_sources, verified, missing)
        raw = await self.llm.complete(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a careful live AI assistant. Return strict JSON with keys: answer, confidence, "
                        "what_was_verified, what_could_not_be_verified. Do not invent citations. If current data "
                        "is unavailable, say so plainly."
                    ),
                },
                {"role": "user", "content": context},
            ]
        )
        return self._parse_answer(raw, pages, search_sources, verified, missing)

    def _parse_answer(
        self,
        raw: str,
        pages: list[PageContent],
        search_sources: list[Source],
        verified: list[str],
        missing: list[str],
    ) -> ChatAnswer:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"answer": raw, "confidence": "medium", "what_was_verified": [], "what_could_not_be_verified": []}

        source_map = {source.url: source for source in search_sources}
        for page in pages:
            source_map[page.url] = Source(title=page.title, url=page.url, snippet=page.text[:220])

        return ChatAnswer(
            answer=parsed.get("answer", ""),
            sources=list(source_map.values()),
            confidence=parsed.get("confidence", "low") if parsed.get("confidence") in {"low", "medium", "high"} else "low",
            what_was_verified=[*verified, *parsed.get("what_was_verified", [])],
            what_could_not_be_verified=[*missing, *parsed.get("what_could_not_be_verified", [])],
        )

    @staticmethod
    def _extract_domain(message: str) -> str | None:
        match = URL_PATTERN.search(message)
        if not match:
            return None
        candidate = match.group(0).rstrip(".,)")
        if not candidate.startswith(("http://", "https://")):
            candidate = f"https://{candidate}"
        parsed = urlparse(candidate)
        return f"{parsed.scheme}://{parsed.netloc}" if parsed.netloc else None

    @staticmethod
    def _context(
        message: str,
        memories,
        pages: list[PageContent],
        sources: list[Source],
        verified: list[str],
        missing: list[str],
    ) -> str:
        page_context = "\n\n".join([f"URL: {page.url}\nTITLE: {page.title}\nTEXT: {page.text[:3500]}" for page in pages])
        memory_context = "\n".join([f"- {item.key}: {item.value}" for item in memories])
        source_context = "\n".join([f"- {source.title}: {source.url} {source.snippet or ''}" for source in sources])
        return (
            f"User question: {message}\n\n"
            f"Relevant memory:\n{memory_context or 'None'}\n\n"
            f"Verified crawler/search notes:\n{'; '.join(verified) or 'None'}\n\n"
            f"Unverified or failed checks:\n{'; '.join(missing) or 'None'}\n\n"
            f"Search sources:\n{source_context or 'None'}\n\n"
            f"Page content:\n{page_context or 'None'}"
        )
