import os
import pytest
import shutil
from backend.app.services.graph import GraphService
from backend.app.schemas import FileStructure, ImportInfo, ClassInfo, FunctionInfo, NodeType, EdgeType

@pytest.fixture
def graph_service_instance(tmp_path):
    # Use a temp directory for graphs
    base_path = tmp_path / "graphs"
    return GraphService(base_path=str(base_path))

def test_project_isolation(graph_service_instance):
    project1 = "project_a"
    project2 = "project_b"
    
    struct1 = FileStructure(
        file_path="main.py",
        classes=[ClassInfo(name="A", bases=[], start_line=1, end_line=5)],
        functions=[],
        imports=[]
    )
    
    struct2 = FileStructure(
        file_path="main.py",
        classes=[ClassInfo(name="B", bases=[], start_line=1, end_line=5)],
        functions=[],
        imports=[]
    )
    
    # Update project 1
    graph_service_instance.update_dependency_graph(project1, struct1)
    graph_service_instance.save_graph(project1)
    
    # Update project 2
    graph_service_instance.update_dependency_graph(project2, struct2)
    graph_service_instance.save_graph(project2)
    
    # Check project 1 content
    g1 = graph_service_instance._get_or_create_graph(project1)
    assert g1.has_node("main.py")
    assert g1.has_node("main.py::A")
    assert not g1.has_node("main.py::B")
    
    # Check project 2 content
    g2 = graph_service_instance._get_or_create_graph(project2)
    assert g2.has_node("main.py")
    assert g2.has_node("main.py::B")
    assert not g2.has_node("main.py::A")

def test_graph_persistence_and_reload(graph_service_instance):
    project_id = "persist_test"
    struct = FileStructure(
        file_path="service.py",
        classes=[],
        functions=[FunctionInfo(name="compute", args=[], start_line=1, end_line=3)],
        imports=[]
    )
    
    graph_service_instance.update_dependency_graph(project_id, struct)
    graph_service_instance.save_graph(project_id)
    
    # Create new instance pointing to same base path
    new_instance = GraphService(base_path=graph_service_instance.base_path)
    new_instance.load_graph(project_id)
    
    g = new_instance._get_or_create_graph(project_id)
    assert g.has_node("service.py")
    assert g.has_node("service.py::compute")

def test_graph_overwrite(graph_service_instance):
    project_id = "overwrite_test"
    
    # Version 1
    struct1 = FileStructure(file_path="old.py")
    graph_service_instance.update_dependency_graph(project_id, struct1)
    graph_service_instance.save_graph(project_id)
    
    # Overwrite - typically handled by IngestionService by calling delete_graph first
    graph_service_instance.delete_graph(project_id)
    
    # Version 2
    struct2 = FileStructure(file_path="new.py")
    graph_service_instance.update_dependency_graph(project_id, struct2)
    graph_service_instance.save_graph(project_id)
    
    g = graph_service_instance._get_or_create_graph(project_id)
    assert g.has_node("new.py")
    assert not g.has_node("old.py")

def test_import_resolution_cross_file(graph_service_instance):
    project_id = "import_test"
    
    # Target file
    target = FileStructure(file_path="utils.py")
    graph_service_instance.update_dependency_graph(project_id, target)
    
    # Source file
    source = FileStructure(
        file_path="main.py",
        imports=[ImportInfo(module="utils", type="local_absolute")]
    )
    graph_service_instance.update_dependency_graph(project_id, source)
    
    graph_service_instance.build_edges(project_id)
    
    g = graph_service_instance._get_or_create_graph(project_id)
    assert g.has_edge("main.py", "utils.py")
    assert g.edges["main.py", "utils.py"]["type"] == EdgeType.IMPORTS