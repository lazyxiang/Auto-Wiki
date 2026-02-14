import networkx as nx
import json
import os
from typing import List, Dict, Optional, Any
from pathlib import Path
from backend.app.schemas import GraphNode, GraphEdge, NodeType, EdgeType, GraphData, FileStructure, ImportInfo, ClassInfo, FunctionInfo

class GraphService:
    def __init__(self, storage_path: str = "backend/data/graph_data.json"):
        self.storage_path = storage_path
        self.graph = nx.DiGraph()
        self.file_map: Dict[str, str] = {} # Map module path (dot-notation) to file path
        self._load_graph()

    def _load_graph(self):
        """Loads the graph from JSON storage and rebuilds the file_map."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    # Reconstruct graph from JSON
                    for node in data.get("nodes", []):
                        self.graph.add_node(node["id"], **node)
                        # Rebuild file_map if it's a file node
                        if node.get("type") == NodeType.FILE:
                            path = node.get("attributes", {}).get("path")
                            if path:
                                self._update_file_map(path)
                                
                    for edge in data.get("edges", []):
                        self.graph.add_edge(edge["source"], edge["target"], **edge)
            except Exception as e:
                print(f"Error loading graph: {e}")
                self.graph = nx.DiGraph()
                self.file_map = {}
        else:
            self.graph = nx.DiGraph()
            self.file_map = {}

    def save_graph(self):
        """Persists the graph to JSON storage."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # Convert graph to serializable format
        nodes_data = []
        for n, attrs in self.graph.nodes(data=True):
            nodes_data.append({
                "id": n,
                "type": attrs.get("type"),
                "attributes": attrs.get("attributes", {})
            })
            
        edges_data = []
        for u, v, attrs in self.graph.edges(data=True):
            edges_data.append({
                "source": u,
                "target": v,
                "type": attrs.get("type"),
                "attributes": attrs.get("attributes", {})
            })

        data = {
            "nodes": nodes_data,
            "edges": edges_data
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _update_file_map(self, file_path: str):
        """
        Updates the internal mapping of module paths to file paths.
        e.g. "backend/app/main.py" -> "backend.app.main"
        """
        # Normalize path separators
        normalized_path = file_path.replace(chr(92), "/")
        
        # Remove extension
        if normalized_path.endswith(".py"):
            module_path = normalized_path[:-3].replace("/", ".")
            self.file_map[module_path] = file_path
            
            # Also handle __init__.py case: backend.app.__init__ -> backend.app
            if module_path.endswith(".__init__"):
                package_path = module_path[:-9]
                self.file_map[package_path] = file_path

    def add_file_node(self, structure: FileStructure):
        """
        Adds a file node and its constituent class/function nodes to the graph.
        Does NOT build import edges (call build_edges later).
        """
        file_path = structure.file_path
        self._update_file_map(file_path)
        
        # 1. Add File Node
        self.graph.add_node(
            file_path, 
            type=NodeType.FILE, 
            attributes={
                "path": file_path,
                "imports": [imp.model_dump() for imp in structure.imports]
            }
        )
        
        # 2. Add Class Nodes
        for cls in structure.classes:
            class_id = f"{file_path}::{cls.name}"
            self.graph.add_node(
                class_id, 
                type=NodeType.CLASS, 
                attributes=cls.model_dump()
            )
            self.graph.add_edge(file_path, class_id, type=EdgeType.DEFINES)
            
            # Store inheritance info (resolved later or lazily)
            # For now, just store 'bases' in attributes, which is already done by model_dump()

        # 3. Add Function Nodes
        for func in structure.functions:
            func_id = f"{file_path}::{func.name}"
            self.graph.add_node(
                func_id, 
                type=NodeType.FUNCTION, 
                attributes=func.model_dump()
            )
            self.graph.add_edge(file_path, func_id, type=EdgeType.DEFINES)

    def _resolve_import(self, current_file: str, import_info: ImportInfo) -> Optional[str]:
        """
        Resolves an import to a file path (node ID) using the file_map.
        """
        module = import_info.module
        
        if import_info.type == "stdlib":
            return None
            
        target_file = None
        
        if import_info.type == "local_absolute":
            # Direct lookup
            target_file = self.file_map.get(module)
            
        elif import_info.type == "local_relative":
            # Resolve relative path
            # current_file: backend/app/services/graph_service.py
            # module: .parser  (from .parser import ...)
            
            # 1. Determine current package
            current_file_path = Path(current_file)
            current_package_parts = list(current_file_path.parent.parts)
            
            # 2. Count dots in module (e.g., ..utils -> 2 dots)
            dots = 0
            for char in module:
                if char == ".":
                    dots += 1
                else:
                    break
            
            relative_module_name = module[dots:]
            
            # 3. Go up (dots - 1) levels. 
            # If dots=1 (.), same dir. If dots=2 (..), parent dir.
            if dots > 0:
                # remove 'dots-1' levels from stack
                for _ in range(dots - 1):
                    if current_package_parts:
                        current_package_parts.pop()
                
                # 4. Construct target module path
                target_parts = current_package_parts
                if relative_module_name:
                     target_parts.append(relative_module_name)
                
                # Reconstruct generic module path to lookup in file_map
                # We need to match how we stored keys in file_map (backend.app...)
                # But relative resolution relies on file system structure more than module names
                # Let's try to reconstruct the file path directly
                
                # Assume root is where execution started? No, file_path is relative to root.
                target_path_prefix = Path(*target_parts)
                
                # Try finding this path in our file_map values
                # This is inefficient. Better to construct the module path string.
                # Assuming current_file is relative to project root, e.g. "backend/app/..."
                
                # Construct candidate module path
                candidate_module = ".".join(target_parts)
                target_file = self.file_map.get(candidate_module)

        return target_file

    def build_edges(self):
        """
        Re-scans all file nodes and rebuilds IMPORT edges based on the current file_map.
        Should be called after batch ingestion.
        """
        # Iterate over all nodes
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("type") == NodeType.FILE:
                imports_data = attrs.get("attributes", {}).get("imports", [])
                for imp_data in imports_data:
                    imp = ImportInfo(**imp_data)
                    target_file = self._resolve_import(node_id, imp)
                    
                    if target_file and self.graph.has_node(target_file):
                        # Avoid self-loops if any
                        if target_file != node_id:
                            self.graph.add_edge(node_id, target_file, type=EdgeType.IMPORTS)
        
        self.save_graph()
