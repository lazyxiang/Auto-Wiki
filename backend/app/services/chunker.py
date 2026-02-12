import hashlib
import os
from typing import List, Dict, Any
from .parser import CodeParser

class CodeChunker:
    def __init__(self):
        self.parser = CodeParser()

    def chunk_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Reads a file and splits it into semantic chunks (classes/functions).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        language = self.parser.get_language_from_ext(file_path)
        if not language:
            print(f"Skipping unsupported file: {file_path}")
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except UnicodeDecodeError:
            print(f"Skipping binary or non-utf8 file: {file_path}")
            return []

        root_node = self.parser.parse_code(code, language)
        if not root_node:
            return []

        definitions = self.parser.extract_definitions(root_node, language, code)
        
        chunks = []
        for d in definitions:
            chunk = self._create_chunk(d, file_path, language)
            chunks.append(chunk)
            
        return chunks

    def _create_chunk(self, definition: Dict[str, Any], file_path: str, language: str) -> Dict[str, Any]:
        """Format a definition into a storage-ready chunk."""
        content = definition['code']
        # Create a deterministic ID based on path + name + type (or content)
        # Using content ensures changes generate new IDs (or we can use path+name for stable IDs)
        # For a Wiki, stable IDs based on symbol name are better for linking, 
        # but content-based is better for vector search deduplication.
        # Let's use path + name + type for now to keep it stable-ish.
        unique_str = f"{file_path}:{definition['type']}:{definition['name']}"
        chunk_id = hashlib.md5(unique_str.encode('utf-8')).hexdigest()

        return {
            "id": chunk_id,
            "content": content,
            "metadata": {
                "name": definition['name'],
                "type": definition['type'],
                "file_path": file_path,
                "language": language,
                "start_line": definition['start_line'],
                "end_line": definition['end_line']
            }
        }
