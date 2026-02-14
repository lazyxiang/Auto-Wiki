import os
import shutil
import pytest
import tempfile
from unittest.mock import MagicMock, patch
from backend.app.services.ingestion import IngestionService

@pytest.fixture
def ingestion_service(tmp_path):
    # Use patch to mock git and internal services to avoid side effects
    with patch('git.Repo.clone_from') as mock_clone:
        service = IngestionService()
        
        # Mock storage and graph services
        service.storage = MagicMock()
        service.graph_service = MagicMock()
        
        # Mock internal graph stats
        service.graph_service._get_or_create_graph.return_value = MagicMock()
        service.graph_service._get_or_create_graph.return_value.number_of_nodes.return_value = 10
        service.graph_service._get_or_create_graph.return_value.number_of_edges.return_value = 5
        
        yield service

@pytest.fixture
def test_repo_dir(tmp_path):
    d = tmp_path / "repo"
    d.mkdir()
    return d

def create_file(directory, name, content):
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return str(path)

def test_ingestion_stats_calculation(ingestion_service, test_repo_dir):
    # 1. Create 1 code file (2 chunks)
    create_file(test_repo_dir, "app.py", "def func1(): pass\ndef func2(): pass")
    
    # 2. Create 2 doc files (1 chunk each)
    create_file(test_repo_dir, "docs/intro.md", "# Intro")
    create_file(test_repo_dir, "docs/usage.txt", "Usage guide")

    # Execute
    project_id = "test_proj"
    stats = ingestion_service.ingest_directory(str(test_repo_dir), project_id)

    # Verify Counts
    assert stats['files_processed'] == 3
    assert stats['code_files'] == 1
    assert stats['doc_files'] == 2

    assert stats['code_chunks'] == 2
    assert stats['doc_chunks'] == 2
    assert stats['chunks_generated'] == 4
    
    # Verify Interactions
    # app.py should trigger update_dependency_graph
    ingestion_service.graph_service.update_dependency_graph.assert_called()
    ingestion_service.graph_service.build_edges.assert_called_once_with(project_id)
    
    # Verify stats include graph info
    assert stats['graph_nodes'] == 10
    assert stats['graph_edges'] == 5

def test_ignore_logic(ingestion_service, test_repo_dir):
    # Verify ignored files
    create_file(test_repo_dir, ".git/config", "git stuff")
    create_file(test_repo_dir, "node_modules/package/index.js", "npm stuff")
    create_file(test_repo_dir, "valid.py", "def ok(): pass")

    project_id = "test_ignore"
    stats = ingestion_service.ingest_directory(str(test_repo_dir), project_id)

    assert stats['files_processed'] == 1
    assert stats['code_files'] == 1

def test_ingest_project_flow(ingestion_service):
    # Test the high-level flow with mocked cloning
    repo_url = "https://github.com/fake/repo.git"
    
    # Mock ingest_directory to return dummy stats
    ingestion_service.ingest_directory = MagicMock(return_value={"files_processed": 5})
    
    stats = ingestion_service.ingest_project(repo_url)
    
    assert stats['repo_url'] == repo_url
    assert 'project_id' in stats
    project_id = stats['project_id']
    
    # Verify cleanup calls
    ingestion_service.storage.delete_collection.assert_called_with(project_id)
    ingestion_service.graph_service.delete_graph.assert_called_with(project_id)
