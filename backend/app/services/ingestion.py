import os
from typing import List
from .chunker import CodeChunker
from .storage import VectorStorage

class IngestionService:
    def __init__(self):
        self.chunker = CodeChunker()
        self.storage = VectorStorage()
        
    def ingest_directory(self, root_path: str):
        """
        Recursively scans a directory, chunks code, and saves to Vector DB.
        """
        if not os.path.exists(root_path):
            raise FileNotFoundError(f"Directory not found: {root_path}")

        all_chunks = []
        file_count = 0
        
        print(f"Starting ingestion for: {root_path}")
        
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Basic ignore logic (can be improved with pathspec)
            # Modify dirnames in-place to skip ignored directories
            dirnames[:] = [d for d in dirnames if not self._is_ignored(d)]
            
            for filename in filenames:
                if self._is_ignored(filename):
                    continue
                    
                file_path = os.path.join(dirpath, filename)
                
                # Chunk file
                chunks = self.chunker.chunk_file(file_path)
                if chunks:
                    all_chunks.extend(chunks)
                    file_count += 1
                    
        # Save all chunks (in a real app, do batching)
        if all_chunks:
            self.storage.save_chunks(all_chunks)
            
        return {
            "files_processed": file_count,
            "chunks_generated": len(all_chunks)
        }

    def _is_ignored(self, name: str) -> bool:
        """Simple ignore list."""
        ignored = {
            '.git', '__pycache__', 'node_modules', '.next', 'venv', '.venv', 
            '.DS_Store', 'dist', 'build', '.pytest_cache', 'data'
        }
        return name in ignored or name.startswith('.')
