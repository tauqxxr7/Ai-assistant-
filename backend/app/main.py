from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.schemas import ChatRequest, MemoryCreate, SearchRequest
from app.services.agent import AgentOrchestrator
from app.services.memory import MemoryStore
from app.services.search import web_search

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_memory() -> MemoryStore:
    return MemoryStore()


@app.get("/health")
def health():
    return {"ok": True, "service": settings.app_name, "environment": settings.environment}


@app.post("/api/chat")
async def chat(request: ChatRequest, memory: MemoryStore = Depends(get_memory)):
    agent = AgentOrchestrator(memory=memory)
    return StreamingResponse(agent.stream(request), media_type="text/event-stream")


@app.post("/api/search")
async def search(request: SearchRequest):
    results = await web_search(f"site:{request.domain} {request.query}" if request.domain else request.query)
    return {"results": [result.model_dump() for result in results]}


@app.get("/api/memories")
def memories(memory: MemoryStore = Depends(get_memory)):
    return {"memories": [item.model_dump(mode="json") for item in memory.list()]}


@app.post("/api/memories")
def create_memory(request: MemoryCreate, memory: MemoryStore = Depends(get_memory)):
    return memory.save(request.key, request.value).model_dump(mode="json")


@app.delete("/api/memories/{memory_id}")
def delete_memory(memory_id: int, memory: MemoryStore = Depends(get_memory)):
    if not memory.delete(memory_id):
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"deleted": True}
