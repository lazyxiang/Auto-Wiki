import hashlib
import os
from typing import List, Dict, Any, Optional, Tuple, Union
from .parser import CodeParser
from backend.app.schemas import FileStructure

class CodeChunker:
    def __init__(self):
        self.parser = CodeParser()

    def chunk_file(self, file_path: str, rel_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Legacy wrapper for backward compatibility.
        """
        chunks, _ = self.chunk_and_structure(file_path, rel_path)
        return chunks

    def chunk_and_structure(self, file_path: str, rel_path: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Optional[FileStructure]]:
        """
        Reads a file, chunks it, and extracts AST structure.
        Returns (chunks, structure). Structure is None for non-code files.
        """
        if not os.path.exists(file_path):
            # Should maybe raise or return empty
            return [], None
            
        path_for_id = rel_path if rel_path else file_path

        # Check for text files first
        if self._is_text_file(file_path):
            chunks = self.chunk_text(file_path, rel_path=path_for_id)
            return chunks, None

        # Fallback to code parsing
        language = self.parser.get_language_from_ext(file_path)
        if not language:
            return [], None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except UnicodeDecodeError:
            print(f"Skipping binary or non-utf8 file: {file_path}")
            return [], None

        # Get Structure (new method)
        structure = self.parser.extract_structure(code, language, path_for_id)
        
        # Get Definitions for chunking (using legacy logic or structure?)
        # For now, use legacy definition extraction to preserve chunking logic exactly
        # Ideally, we map structure -> chunks.
        root_node = self.parser.parse_code(code, language)
        definitions = self.parser.extract_definitions(root_node, language, code)
        
        chunks = []
        for d in definitions:
            chunk = self._create_chunk(d, file_path, path_for_id, language)
            chunks.append(chunk)
            
        return chunks, structure

    def chunk_text(self, file_path: str, chunk_size: int = 1000, overlap: int = 200, rel_path: str = None) -> List[Dict[str, Any]]:
        """
        Chunks text files with overlap. Calculates start/end lines.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            print(f"Skipping binary or non-utf8 file: {file_path}")
            return []
            
        path_for_id = rel_path if rel_path else file_path
        chunks = []
        start = 0
        text_len = len(text)
        
        # Pre-calculate line offsets for efficient lookup
        # lines_indices[i] = char index where line i starts
        lines_indices = [0]
        for i, char in enumerate(text):
            if char == '\n':
                lines_indices.append(i + 1)
        
        while start < text_len:
            end = start + chunk_size
            chunk_content = text[start:end]
            
            # Create a deterministic ID based on RELATIVE path
            chunk_id = hashlib.md5(f"{path_for_id}:text:{start}".encode('utf-8')).hexdigest()
            
            # Calculate line numbers
            start_line = self._get_line_number(start, lines_indices)
            end_line = self._get_line_number(end, lines_indices)

            chunks.append({
                "id": chunk_id,
                "content": chunk_content,
                "metadata": {
                    "name": os.path.basename(file_path),
                    "type": "documentation",
                    "file_path": path_for_id, # Store relative path directly
                    "language": "text", 
                    "start_line": start_line,
                    "end_line": end_line
                }
            })
            
            start += (chunk_size - overlap)
            
        return chunks

    def _get_line_number(self, char_index: int, lines_indices: List[int]) -> int:
        """Binary search or simple scan to find line number."""
        # Simple scan is fine for now, or bisect if needed for huge files
        # 1-based line number
        for i, idx in enumerate(lines_indices):
            if idx > char_index:
                return i 
        return len(lines_indices)

    def _create_chunk(self, definition: Dict[str, Any], abs_path: str, rel_path: str, language: str) -> Dict[str, Any]:
        """Format a definition into a storage-ready chunk."""
        content = definition['code']
        # Create a deterministic ID based on path + name + type
        unique_str = f"{rel_path}:{definition['type']}:{definition['name']}"
        chunk_id = hashlib.md5(unique_str.encode('utf-8')).hexdigest()

        return {
            "id": chunk_id,
            "content": content,
            "metadata": {
                "name": definition['name'],
                "type": definition['type'],
                "file_path": rel_path, # Store relative path
                "language": language,
                "start_line": definition['start_line'],
                "end_line": definition['end_line']
            }
        }

    def _is_text_file(self, file_path: str) -> bool:
        """Simple check for text/docs extensions."""
        text_exts = {'.md', '.txt', '.rst', '.adoc'}
        _, ext = os.path.splitext(file_path)
        return ext.lower() in text_exts
