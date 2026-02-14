import os
import pytest
from backend.app.services.graph_service import GraphService
from backend.app.schemas import FileStructure, ImportInfo, ClassInfo, FunctionInfo, NodeType, EdgeType

@pytest.fixture
def graph_service(tmp_path):
    # Use a temp path for graph storage
    storage = tmp_path / "graph_data.json"
    return GraphService(storage_path=str(storage))

def test_add_file_node(graph_service):
    structure = FileStructure(
        file_path="backend/app/main.py",
        classes=[ClassInfo(name="App", bases=[], start_line=1, end_line=10)],
        functions=[FunctionInfo(name="run", args=[], start_line=12, end_line=15)],
        imports=[ImportInfo(module="backend.app.services", type="local_absolute")]
    )
    
    graph_service.add_file_node(structure)
    
    assert graph_service.graph.has_node("backend/app/main.py")
    assert graph_service.graph.has_node("backend/app/main.py::App")
    assert graph_service.graph.has_node("backend/app/main.py::run")
    
    # Check DEFINES edges
    assert graph_service.graph.has_edge("backend/app/main.py", "backend/app/main.py::App")
    assert graph_service.graph.edges["backend/app/main.py", "backend/app/main.py::App"]["type"] == EdgeType.DEFINES

def test_import_resolution(graph_service):
    # Add target file
    target_structure = FileStructure(
        file_path="backend/app/services/parser.py",
        classes=[],
        functions=[],
        imports=[]
    )
    graph_service.add_file_node(target_structure)
    
    # Add source file that imports target
    source_structure = FileStructure(
        file_path="backend/app/main.py",
        classes=[],
        functions=[],
        imports=[
            ImportInfo(module="backend.app.services.parser", type="local_absolute"),
            ImportInfo(module=".services.parser", type="local_relative") # Assuming main.py is in backend/app
        ]
    )
    graph_service.add_file_node(source_structure)
    
    # Trigger edge building
    graph_service.build_edges()
    
    # Check IMPORTS edge
    assert graph_service.graph.has_edge("backend/app/main.py", "backend/app/services/parser.py")
    edge_data = graph_service.graph.edges["backend/app/main.py", "backend/app/services/parser.py"]
    assert edge_data["type"] == EdgeType.IMPORTS

def test_persistence(graph_service):
    structure = FileStructure(file_path="test.py")
    graph_service.add_file_node(structure)
    graph_service.save_graph()
    
    # Create new service pointing to same path
    new_service = GraphService(storage_path=graph_service.storage_path)
    assert new_service.graph.has_node("test.py")
