import networkx as nx
import json
import os
from typing import List, Dict, Optional, Any
from pathlib import Path
from ..schemas import GraphNode, GraphEdge, NodeType, EdgeType, GraphData, FileStructure, ImportInfo, ClassInfo, FunctionInfo

class GraphService:
    def __init__(self, base_path: str = "backend/data/graphs"):
        self.base_path = base_path
        # Cache for multiple projects: project_id -> nx.DiGraph
        self.graphs: Dict[str, nx.DiGraph] = {}
        # Cache for multiple projects: project_id -> {module_path: file_path}
        self.file_maps: Dict[str, Dict[str, str]] = {}
        
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path, exist_ok=True)

    def _get_graph_path(self, project_id: str) -> str:
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in project_id)
        return os.path.join(self.base_path, f"{safe_id}.json")

    def _get_or_create_graph(self, project_id: str) -> nx.DiGraph:
        """Retrieves graph from memory or loads it."""
        if project_id not in self.graphs:
            self.load_graph(project_id)
        return self.graphs[project_id]

    def _get_file_map(self, project_id: str) -> Dict[str, str]:
        if project_id not in self.file_maps:
            self.file_maps[project_id] = {}
        return self.file_maps[project_id]

    def load_graph(self, project_id: str):
        """Loads the graph from JSON storage and rebuilds the file_map."""
        path = self._get_graph_path(project_id)
        graph = nx.DiGraph()
        file_map = {}
        
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    # Reconstruct graph from JSON
                    for node in data.get("nodes", []):
                        graph.add_node(node["id"], **node)
                        # Rebuild file_map if it's a file node
                        if node.get("type") == NodeType.FILE:
                            file_path = node.get("attributes", {}).get("path")
                            if file_path:
                                self._update_file_map_entry(file_map, file_path)
                                
                    for edge in data.get("edges", []):
                        graph.add_edge(edge["source"], edge["target"], **edge)
            except Exception as e:
                print(f"Error loading graph for {project_id}: {e}")
        
        self.graphs[project_id] = graph
        self.file_maps[project_id] = file_map

    def save_graph(self, project_id: str):
        """Persists the graph to JSON storage."""
        if project_id not in self.graphs:
            return

        path = self._get_graph_path(project_id)
        graph = self.graphs[project_id]
        
        # Convert graph to serializable format
        nodes_data = []
        for n, attrs in graph.nodes(data=True):
            nodes_data.append({
                "id": n,
                "type": attrs.get("type"),
                "attributes": attrs.get("attributes", {})
            })
            
        edges_data = []
        for u, v, attrs in graph.edges(data=True):
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
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def delete_graph(self, project_id: str):
        """Deletes the graph file, the tree file, and clears memory."""
        # 1. Delete Graph JSON
        graph_path = self._get_graph_path(project_id)
        if os.path.exists(graph_path):
            os.remove(graph_path)
            
        # 2. Delete Tree JSON
        tree_path = os.path.join(self.base_path, f"{project_id}_tree.json")
        if os.path.exists(tree_path):
            os.remove(tree_path)

        # 3. Clear Memory
        if project_id in self.graphs:
            del self.graphs[project_id]
        if project_id in self.file_maps:
            del self.file_maps[project_id]

    def _update_file_map_entry(self, file_map: Dict[str, str], file_path: str):
        """Helper to update a specific file_map dict."""
        # Normalize path separators
        normalized_path = file_path.replace(chr(92), "/")
        
        # Remove extension
        if normalized_path.endswith(".py"):
            module_path = normalized_path[:-3].replace("/", ".")
            file_map[module_path] = file_path
            
            # Also handle __init__.py case: backend.app.__init__ -> backend.app
            if module_path.endswith(".__init__"):
                package_path = module_path[:-9]
                file_map[package_path] = file_path

    def update_dependency_graph(self, project_id: str, structure: FileStructure):
        """
        Adds a file node and its constituent class/function nodes to the graph.
        Does NOT build import edges (call build_edges later).
        """
        graph = self._get_or_create_graph(project_id)
        file_map = self._get_file_map(project_id)
        
        file_path = structure.file_path
        self._update_file_map_entry(file_map, file_path)
        
        # 1. Add File Node
        graph.add_node(
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
            graph.add_node(
                class_id, 
                type=NodeType.CLASS, 
                attributes=cls.model_dump()
            )
            graph.add_edge(file_path, class_id, type=EdgeType.DEFINES)
            
            # Store inheritance info (resolved later or lazily)
            # For now, just store 'bases' in attributes, which is already done by model_dump()

        # 3. Add Function Nodes
        for func in structure.functions:
            func_id = f"{file_path}::{func.name}"
            graph.add_node(
                func_id, 
                type=NodeType.FUNCTION, 
                attributes=func.model_dump()
            )
            graph.add_edge(file_path, func_id, type=EdgeType.DEFINES)

    def _resolve_import(self, project_id: str, current_file: str, import_info: ImportInfo) -> Optional[str]:
        """
        Resolves an import to a file path (node ID) using the file_map.
        """
        file_map = self._get_file_map(project_id)
        module = import_info.module
        
        if import_info.type == "stdlib":
            return None
            
        target_file = None
        
        if import_info.type == "local_absolute":
            # Direct lookup
            target_file = file_map.get(module)
            
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
                target_file = file_map.get(candidate_module)

        return target_file

    def build_edges(self, project_id: str):
        """
        Re-scans all file nodes and rebuilds IMPORT edges based on the current file_map.
        Should be called after batch ingestion.
        """
        graph = self._get_or_create_graph(project_id)
        
        # Iterate over all nodes
        # Use list(graph.nodes) to avoid runtime error if graph changes (though it shouldn't here)
        for node_id, attrs in list(graph.nodes(data=True)):
            if attrs.get("type") == NodeType.FILE:
                imports_data = attrs.get("attributes", {}).get("imports", [])
                for imp_data in imports_data:
                    imp = ImportInfo(**imp_data)
                    target_file = self._resolve_import(project_id, node_id, imp)
                    
                    if target_file and graph.has_node(target_file):
                        # Avoid self-loops if any
                        if target_file != node_id:
                            graph.add_edge(node_id, target_file, type=EdgeType.IMPORTS)
        
        self.save_graph(project_id)

    def compute_node_importance(self, project_id: str) -> Dict[str, float]:
        """
        Computes the importance of each node using PageRank (or similar centrality).
        Returns a dict of node_id -> score.
        """
        graph = self._get_or_create_graph(project_id)
        if graph.number_of_nodes() == 0:
            return {}

        try:
            # Pagerank is good for "global importance"
            # We might want 'reverse pagerank' to see what is most depended upon (Utils)?
            # Or standard pagerank to see what 'uses' the most things? 
            # Actually, standard Pagerank: "Important nodes are referenced by other important nodes".
            # For code, if A imports B, A depends on B. B is a dependency.
            # If we want "High Level Modules" (Entry points), they have high OUT-degree, low IN-degree.
            # If we want "Core Utils", they have high IN-degree.
            
            # For the Codemap, we want to sort by "Logical Priority".
            # Usually Entry Points (API) -> Domain Logic -> Utilities.
            # This aligns with Topological Sort somewhat.
            
            # Let's use a simple heuristic for now: In-Degree Centrality
            # (How many files import me?)
            scores = nx.in_degree_centrality(graph)
            return scores
        except Exception as e:
            print(f"Error computing graph importance: {e}")
            return {n: 0.0 for n in graph.nodes()}

    def classify_node_layer(self, file_path: str) -> int:
        """
        Returns layer index:
        0: Docs (README, .md)
        1: API/Entry (main.py, api/, cli/)
        2: Core Logic (services/, core/, managers/)
        3: Data/Utils (models/, schemas/, utils/, lib/, common/)
        4: Others
        """
        lower_path = file_path.lower()
        
        # Layer 0: Documentation
        if lower_path.endswith('.md') or 'docs/' in lower_path:
            return 0
            
        # Layer 1: Entry Points
        if 'api/' in lower_path or 'routes' in lower_path or 'main.py' in lower_path or 'cli/' in lower_path or 'app.py' in lower_path:
            return 1
            
        # Layer 3: Low level (checked before Layer 2 to catch schemas/models first)
        if 'models/' in lower_path or 'schemas' in lower_path or 'utils/' in lower_path or 'lib/' in lower_path or 'common/' in lower_path or 'types' in lower_path or 'dto' in lower_path:
            return 3
            
        # Layer 2: Core Logic (Default for code files not in above)
        if 'services/' in lower_path or 'core/' in lower_path or 'managers/' in lower_path or 'logic/' in lower_path:
            return 2
            
        return 4

    def build_module_tree(self, project_id: str):
        """
        Constructs a hierarchical JSON tree of the project structure,
        sorted by topological importance/layers.
        Saves to <project_id>_tree.json.
        """
        graph = self._get_or_create_graph(project_id)
        file_nodes = [n for n, attrs in graph.nodes(data=True) if attrs.get("type") == NodeType.FILE]
        
        importance_scores = self.compute_node_importance(project_id)
        
        # 1. Build basic directory tree structure
        tree_root = {"id": "root", "name": "root", "type": "folder", "children": []}
        
        # Helper to find/create folder path
        def get_folder_node(path_parts, current_node):
            if not path_parts:
                return current_node
            
            part = path_parts[0]
            existing = next((c for c in current_node["children"] if c["name"] == part and c["type"] == "folder"), None)
            
            if not existing:
                new_folder = {"id": f"{current_node['id']}/{part}", "name": part, "type": "folder", "children": []}
                current_node["children"].append(new_folder)
                existing = new_folder
            
            return get_folder_node(path_parts[1:], existing)

        # 2. Populate Tree
        for file_path in file_nodes:
            parts = file_path.split("/")
            filename = parts[-1]
            folder_parts = parts[:-1]
            
            parent = get_folder_node(folder_parts, tree_root)
            
            layer = self.classify_node_layer(file_path)
            score = importance_scores.get(file_path, 0)
            
            file_node = {
                "id": file_path,
                "name": filename,
                "type": "file",
                "layer": layer,
                "importance": score,
                "children": [] # Can add classes/functions here later if needed
            }
            parent["children"].append(file_node)

        # 3. Recursive Sort
        def sort_node(node):
            # Sort children:
            # Folders first, then Files? Or mixed?
            # Let's keep Folders and Files mixed but sorted by importance logic.
            # But usually users expect Folders at top or alphabetical.
            # Let's do: Folders (Alphabetical), then Files (Sorted by Layer ASC, then Importance DESC)
            
            folders = [c for c in node["children"] if c["type"] == "folder"]
            files = [c for c in node["children"] if c["type"] == "file"]
            
            folders.sort(key=lambda x: x["name"])
            
            # Sort files: Layer 0 -> 1 -> 2 -> 3. Inside layer: Importance High -> Low.
            files.sort(key=lambda x: (x["layer"], -x["importance"]))
            
            node["children"] = folders + files
            
            for child in node["children"]:
                if child["type"] == "folder":
                    sort_node(child)

        sort_node(tree_root)
        
        # Save Tree
        tree_path = os.path.join(self.base_path, f"{project_id}_tree.json")
        with open(tree_path, 'w') as f:
            json.dump(tree_root, f, indent=2)
