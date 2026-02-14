import os
import shutil
import pytest
import hashlib
from backend.app.services.storage import VectorStorage
from backend.app.services.ingestion import IngestionService

@pytest.fixture
def vector_storage(tmp_path):
    db_path = tmp_path / "chromadb"
    return VectorStorage(persistence_path=str(db_path))

def test_vector_storage_isolation(vector_storage):
    project1 = "project_1"
    project2 = "project_2"
    
    chunks1 = [
        {"id": "c1", "content": "print('hello')", "metadata": {"file_path": "a.py", "v": 1}}
    ]
    chunks2 = [
        {"id": "c1", "content": "print('world')", "metadata": {"file_path": "a.py", "v": 1}}
    ]
    
    vector_storage.save_chunks(project1, chunks1)
    vector_storage.save_chunks(project2, chunks2)
    
    # Query project 1
    res1 = vector_storage.query_code(project1, "hello")
    assert len(res1) == 1
    assert "hello" in res1[0]["content"]
    
    # Query project 2 for same text should not find it if it's completely different
    res2 = vector_storage.query_code(project2, "hello")
    # It might find it with high distance if using cosine and short text, 
    # but the content should be "world"
    if res2:
        assert "world" in res2[0]["content"]

def test_vector_storage_overwrite(vector_storage):
    project_id = "overwrite_test"
    
    chunks1 = [{"id": "id1", "content": "version 1", "metadata": {"v": 1}}]
    vector_storage.save_chunks(project_id, chunks1)
    
    # Clear and overwrite
    vector_storage.clear_all(project_id)
    vector_storage.delete_collection(project_id)
    
    chunks2 = [{"id": "id1", "content": "version 2", "metadata": {"v": 2}}]
    vector_storage.save_chunks(project_id, chunks2)
    
    res = vector_storage.query_code(project_id, "version")
    assert len(res) == 1
    assert "version 2" in res[0]["content"]
    
    coll = vector_storage.get_collection(project_id)
    assert coll.count() == 1
