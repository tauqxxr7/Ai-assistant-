from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from app.config import get_settings


class LLMClient:
    async def complete(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        settings = get_settings()
        if not settings.openai_api_key:
            return self._offline_answer(messages)
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{settings.openai_base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"},
                json={"model": settings.openai_model, "messages": messages, "temperature": temperature},
            )
            response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    async def stream_text(self, text: str) -> AsyncIterator[str]:
        for token in text.split(" "):
            yield token + " "

    @staticmethod
    def _offline_answer(messages: list[dict[str, str]]) -> str:
        prompt = messages[-1]["content"]
        return json.dumps(
            {
                "answer": (
                    "I can outline the answer, but no LLM API key is configured. "
                    "Configure OPENAI_API_KEY or an OpenAI-compatible endpoint for generated responses. "
                    f"Request received: {prompt[:220]}"
                ),
                "confidence": "low",
                "what_was_verified": [],
                "what_could_not_be_verified": ["No LLM API key was configured for final synthesis."],
            }
        )
