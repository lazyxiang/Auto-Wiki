import json
import os
from typing import List, Dict, Any, Optional
from .storage import VectorStorage
from .graph import GraphService

class SearchService:
    def __init__(self):
        self.storage = VectorStorage()
        self.graph_service = GraphService()

    def search(self, project_id: str, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Performs a hybrid search:
        1. Vector search for semantic relevance.
        2. Overlays results onto the hierarchical module tree.
        3. Returns the tree with 'active' and 'score' attributes injected.
        """
        # 1. Vector Search (fetch more candidates to populate the map)
        vector_results = self.storage.query_code(project_id, query, n_results=limit * 3)
        
        # Create a lookup map: file_path -> {score, chunks}
        hits = {}
        for res in vector_results:
            path = res['metadata'].get('file_path')
            if not path:
                continue
                
            if path not in hits:
                hits[path] = {
                    "score": res['distance'], # Lower is better in Chroma usually, but let's just store it
                    "chunks": []
                }
            hits[path]["chunks"].append(res)

        # 2. Load Module Tree
        tree_path = os.path.join(self.graph_service.base_path, f"{project_id}_tree.json")
        if not os.path.exists(tree_path):
            return {"error": "Project tree not found. Please ingest project first."}
            
        with open(tree_path, 'r') as f:
            tree = json.load(f)

        # 3. Propagate Hits to Tree
        # We need to return a tree where relevant nodes are marked.
        # We also calculate a "relevance" for sorting if we were returning a list,
        # but for a tree, we just mark nodes.

        has_hits = self._mark_tree_recursive(tree, hits)
        
        return {
            "tree": tree,
            "stats": {
                "hits_found": len(hits),
                "vector_results": len(vector_results)
            }
        }

    def _mark_tree_recursive(self, node: Dict[str, Any], hits: Dict[str, Any]) -> bool:
        """
        Recursively marks nodes as 'active' if they or their children have hits.
        Returns True if this node or any child is active.
        """
        is_active = False
        
        # Check if this node itself is a hit (Files)
        if node["type"] == "file":
            if node["id"] in hits:
                is_active = True
                node["is_hit"] = True
                node["search_score"] = hits[node["id"]]["score"]
                node["matched_chunks"] = hits[node["id"]]["chunks"]
        
        # Check children (Folders)
        if "children" in node:
            for child in node["children"]:
                child_active = self._mark_tree_recursive(child, hits)
                if child_active:
                    is_active = True
        
        if is_active:
            node["is_active"] = True
            
        return is_active
