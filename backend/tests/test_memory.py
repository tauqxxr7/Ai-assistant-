from app.services.memory import MemoryStore


def test_memory_store_save_retrieve_delete():
    store = MemoryStore("sqlite:///:memory:")
    record = store.save("project", "live assistant")
    assert record.id == 1
    assert store.retrieve("assistant")[0].key == "project"
    assert store.delete(record.id)
    assert store.list() == []
