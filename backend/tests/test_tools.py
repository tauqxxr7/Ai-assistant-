import pytest

from app.services.memory import MemoryStore
from app.services.tools import ToolRegistry


def test_tool_schema_rejects_extra_properties():
    registry = ToolRegistry(memory=MemoryStore("sqlite:///:memory:"))
    with pytest.raises(Exception):
        registry.validate("web_search", {"query": "hello", "extra": True})


def test_tool_schema_validation_failure_for_missing_required_arg():
    registry = ToolRegistry(memory=MemoryStore("sqlite:///:memory:"))
    with pytest.raises(Exception):
        registry.validate("extract_page_content", {})


@pytest.mark.asyncio
async def test_memory_tool_roundtrip():
    registry = ToolRegistry(memory=MemoryStore("sqlite:///:memory:"))
    saved = await registry.call("save_memory", {"key": "tone", "value": "prefers concise answers"})
    results = await registry.call("retrieve_memory", {"query": "concise"})
    assert saved["key"] == "tone"
    assert results[0]["value"] == "prefers concise answers"
