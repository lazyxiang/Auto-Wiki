import pytest
import json
import os
from unittest.mock import MagicMock, patch
from backend.app.services.search import SearchService

# Mock data
MOCK_TREE = {
    "id": "root",
    "type": "folder",
    "children": [
        {
            "id": "backend/app",
            "type": "folder",
            "children": [
                {"id": "backend/app/main.py", "type": "file", "layer": 1, "importance": 0.5},
                {"id": "backend/app/utils.py", "type": "file", "layer": 3, "importance": 0.1}
            ]
        },
        {"id": "README.md", "type": "file", "layer": 0, "importance": 1.0}
    ]
}

MOCK_VECTOR_RESULTS = [
    {
        "id": "chunk1",
        "distance": 0.2,
        "metadata": {"file_path": "backend/app/main.py", "start_line": 10}
    },
    {
        "id": "chunk2",
        "distance": 0.3,
        "metadata": {"file_path": "README.md", "start_line": 1}
    }
]

@pytest.fixture
def search_service():
    service = SearchService()
    service.storage = MagicMock()
    service.graph_service = MagicMock()
    return service

def test_search_marking(search_service):
    # Setup mocks
    search_service.storage.query_code.return_value = MOCK_VECTOR_RESULTS
    
    # Mock file reading for tree
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        # Configure json.load to return our mock tree
        with patch("json.load", return_value=MOCK_TREE):
            with patch("os.path.exists", return_value=True):
                 # Run search
                 result = search_service.search("test_project", "query")
                 
                 tree = result["tree"]
                 
                 # Verify structure
                 assert tree["is_active"] == True # Root should be active
                 
                 # Verify README hit
                 readme = next(c for c in tree["children"] if c["id"] == "README.md")
                 assert readme["is_active"] == True
                 assert readme.get("is_hit") == True
                 assert readme["search_score"] == 0.3
                 
                 # Verify Folder active
                 backend = next(c for c in tree["children"] if c["id"] == "backend/app")
                 assert backend["is_active"] == True
                 
                 # Verify main.py hit
                 main_py = next(c for c in backend["children"] if c["id"] == "backend/app/main.py")
                 assert main_py["is_active"] == True
                 assert main_py.get("is_hit") == True
                 
                 # Verify utils.py NOT hit
                 utils_py = next(c for c in backend["children"] if c["id"] == "backend/app/utils.py")
                 assert utils_py.get("is_active") is None
