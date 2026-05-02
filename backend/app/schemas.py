from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, HttpUrl


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)


class Source(BaseModel):
    title: str | None = None
    url: str
    snippet: str | None = None


class Verification(BaseModel):
    confidence: Literal["low", "medium", "high"]
    what_was_verified: list[str] = Field(default_factory=list)
    what_could_not_be_verified: list[str] = Field(default_factory=list)


class ChatAnswer(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"] = "low"
    what_was_verified: list[str] = Field(default_factory=list)
    what_could_not_be_verified: list[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    domain: str | None = None


class SearchResult(BaseModel):
    title: str | None = None
    url: str
    snippet: str | None = None


class MemoryCreate(BaseModel):
    key: str = Field(min_length=1, max_length=160)
    value: str = Field(min_length=1)


class MemoryRecord(BaseModel):
    id: int
    key: str
    value: str
    created_at: datetime
    updated_at: datetime


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any]


class UrlRequest(BaseModel):
    url: HttpUrl
