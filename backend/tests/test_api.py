from fastapi.testclient import TestClient

from app.main import app, get_memory
from app.services.memory import MemoryStore


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_memory_create_list_delete_api(tmp_path):
    store = MemoryStore(f"sqlite:///{tmp_path / 'memories.db'}")
    app.dependency_overrides[get_memory] = lambda: store
    client = TestClient(app)
    try:
        created = client.post("/api/memories", json={"key": "style", "value": "concise"}).json()
        assert created["id"] == 1

        listed = client.get("/api/memories").json()
        assert listed["memories"][0]["key"] == "style"

        deleted = client.delete("/api/memories/1")
        assert deleted.status_code == 200
        assert client.get("/api/memories").json()["memories"] == []
    finally:
        app.dependency_overrides.clear()
