import os
import shutil
import uuid
from typing import List
import git
from .chunker import CodeChunker
from .storage import VectorStorage
from .graph_service import GraphService

class IngestionService:
    def __init__(self):
        self.chunker = CodeChunker()
        self.storage = VectorStorage()
        self.graph_service = GraphService()
        
    def ingest_project(self, repo_url: str):
        """
        Ingests a project by cloning from a git URL.
        """
        temp_id = str(uuid.uuid4())[:8]
        target_path = os.path.join(os.getcwd(), "temp_repos", temp_id)
        
        try:
            self._clone_repo(repo_url, target_path)
            stats = self.ingest_directory(target_path)
            stats["repo_url"] = repo_url
            return stats
        finally:
            if os.path.exists(target_path):
                shutil.rmtree(target_path)

    def _clone_repo(self, url: str, target_dir: str):
        """Clones a git repo to target_dir. Supports SSH."""
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        print(f"Cloning {url} to {target_dir}...")
        
        # Configure env to ignore strict host key checking for SSH
        # This allows cloning from github.com (or others) without pre-populating known_hosts in Docker
        env = os.environ.copy()
        env["GIT_SSH_COMMAND"] = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
        
        git.Repo.clone_from(url, target_dir, depth=1, env=env)
        print("Clone complete.")

    def ingest_directory(self, root_path: str):
        """
        Recursively scans a directory, chunks content, saves to Vector DB, and builds dependency graph.
        """
        abs_path = os.path.abspath(root_path)
        all_chunks = []
        file_count = 0
        code_files = 0
        doc_files = 0
        
        code_chunks_count = 0
        doc_chunks_count = 0
        
        # Clear existing graph if needed? 
        # For now, we append/overwrite if same path.
        
        for dirpath, dirnames, filenames in os.walk(abs_path):
            dirnames[:] = [d for d in dirnames if not self._is_ignored(d)]
            
            for filename in filenames:
                if self._is_ignored(filename):
                    continue
                    
                file_path = os.path.join(dirpath, filename)
                # Calculate relative path for stable ID generation
                rel_path = os.path.relpath(file_path, abs_path)
                
                # Pass rel_path to chunker
                chunks, structure = self.chunker.chunk_and_structure(file_path, rel_path=rel_path)
                
                # Update Graph
                if structure:
                    self.graph_service.update_dependency_graph(structure)
                
                if chunks:
                    all_chunks.extend(chunks)
                    file_count += 1
                    
                    # Count logic
                    is_doc_file = False
                    for c in chunks:
                        if c['metadata'].get('type') == 'documentation':
                            doc_chunks_count += 1
                            is_doc_file = True
                        else:
                            code_chunks_count += 1
                            
                    if is_doc_file:
                        doc_files += 1
                    else:
                        code_files += 1
                    
        if all_chunks:
            self.storage.save_chunks(all_chunks)
            
        # Build edges after all files are processed
        self.graph_service.build_edges()
            
        return {
            "files_processed": file_count,
            "code_files": code_files,
            "doc_files": doc_files,
            "chunks_generated": len(all_chunks),
            "code_chunks": code_chunks_count,
            "doc_chunks": doc_chunks_count,
            "graph_nodes": self.graph_service.graph.number_of_nodes(),
            "graph_edges": self.graph_service.graph.number_of_edges()
        }

    def _is_ignored(self, name: str) -> bool:
        """Simple ignore list."""
        ignored = {
            '.git', '__pycache__', 'node_modules', '.next', 'venv', '.venv', 
            '.DS_Store', 'dist', 'build', '.pytest_cache', 'data', 'temp_repos'
        }
        return name in ignored or name.startswith('.')
