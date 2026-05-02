from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator

from app.schemas import SearchResult
from app.services.crawler import extract_page_content, open_url
from app.services.memory import MemoryStore
from app.services.robots import parse_robots_txt
from app.services.search import web_search
from app.services.sitemap import fetch_sitemap


TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "web_search": {"type": "object", "properties": {"query": {"type": "string", "minLength": 1}}, "required": ["query"], "additionalProperties": False},
    "open_url": {"type": "object", "properties": {"url": {"type": "string", "format": "uri"}}, "required": ["url"], "additionalProperties": False},
    "fetch_sitemap": {"type": "object", "properties": {"domain": {"type": "string", "minLength": 1}}, "required": ["domain"], "additionalProperties": False},
    "parse_robots_txt": {"type": "object", "properties": {"domain": {"type": "string", "minLength": 1}}, "required": ["domain"], "additionalProperties": False},
    "extract_page_content": {"type": "object", "properties": {"url": {"type": "string", "format": "uri"}}, "required": ["url"], "additionalProperties": False},
    "save_memory": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}}, "required": ["key", "value"], "additionalProperties": False},
    "retrieve_memory": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"], "additionalProperties": False},
}


class ToolRegistry:
    def __init__(self, memory: MemoryStore | None = None) -> None:
        self.memory = memory or MemoryStore()

    def validate(self, name: str, arguments: dict[str, Any]) -> None:
        if name not in TOOL_SCHEMAS:
            raise ValueError(f"Unknown tool: {name}")
        Draft202012Validator(TOOL_SCHEMAS[name]).validate(arguments)

    async def call(self, name: str, arguments: dict[str, Any]) -> Any:
        self.validate(name, arguments)
        if name == "web_search":
            return [item.model_dump() for item in await web_search(arguments["query"])]
        if name == "open_url":
            return await open_url(arguments["url"])
        if name == "fetch_sitemap":
            return [item.__dict__ for item in await fetch_sitemap(arguments["domain"])]
        if name == "parse_robots_txt":
            return (await parse_robots_txt(arguments["domain"])).__dict__
        if name == "extract_page_content":
            return (await extract_page_content(arguments["url"])).__dict__
        if name == "save_memory":
            return self.memory.save(arguments["key"], arguments["value"]).model_dump(mode="json")
        if name == "retrieve_memory":
            return [item.model_dump(mode="json") for item in self.memory.retrieve(arguments["query"])]
        raise ValueError(f"Tool not implemented: {name}")


def search_results_to_sources(results: list[SearchResult]) -> list[dict[str, str | None]]:
    return [result.model_dump() for result in results]
