import os
import shutil
import pytest
import tempfile
from backend.app.services.chunker import CodeChunker

@pytest.fixture
def chunker():
    return CodeChunker()

@pytest.fixture
def temp_dir():
    dir_path = tempfile.mkdtemp()
    yield dir_path
    shutil.rmtree(dir_path)

def create_test_file(directory, name, content):
    path = os.path.join(directory, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path

# --- Code Chunking Tests ---

def test_python_code_chunking(chunker, temp_dir):
    content = """
class MyClass:
    def method_a(self):
        pass

def top_level_func():
    return True
"""
    path = create_test_file(temp_dir, "app.py", content)
    # Pass rel_path as if we are ingesting from root
    chunks, structure = chunker.chunk_and_structure(path, rel_path="app.py")
    
    assert len(chunks) >= 2
    
    # Verify metadata
    assert chunks[0]['metadata']['language'] == 'python'
    assert chunks[0]['metadata']['file_path'] == 'app.py' # Should be relative
    
    # Verify lines are present
    assert chunks[0]['metadata']['start_line'] is not None
    assert chunks[0]['metadata']['end_line'] is not None

def test_unsupported_file_returns_empty(chunker, temp_dir):
    path = create_test_file(temp_dir, "data.bin", "\x00\x01\x02")
    chunks, structure = chunker.chunk_and_structure(path, rel_path="data.bin")
    assert len(chunks) == 0
    assert structure is None

def test_chunk_and_structure_integration(chunker, temp_dir):
    content = """
import os
class Test:
    pass
"""
    path = create_test_file(temp_dir, "test_struct.py", content)
    chunks, structure = chunker.chunk_and_structure(path, rel_path="test_struct.py")
    
    assert len(chunks) > 0
    assert structure is not None
    assert structure.file_path == "test_struct.py"
    assert structure.classes[0].name == "Test"
    assert len(structure.imports) == 1

# --- Documentation Chunking Tests ---

def test_markdown_chunking(chunker, temp_dir):
    content = "# Title\nThis is a test documentation for AutoWiki."
    path = create_test_file(temp_dir, "README.md", content)
    chunks, structure = chunker.chunk_and_structure(path, rel_path="README.md")
    
    assert len(chunks) == 1
    assert chunks[0]['metadata']['type'] == 'documentation'
    assert chunks[0]['metadata']['file_path'] == 'README.md'
    
    # Verify line calculation
    # 1-based indexing check
    assert chunks[0]['metadata']['start_line'] == 1
    # Content has 2 lines
    assert chunks[0]['metadata']['end_line'] == 2
    assert structure is None # Docs don't have code structure

def test_text_sliding_window_lines(chunker, temp_dir):
    # Create multi-line text
    lines = [f"Line {i}" for i in range(1, 101)] # 100 lines
    content = "\n".join(lines)
    path = create_test_file(temp_dir, "manual.txt", content)
    
    # Chunk with small size to split
    # Avg line len is ~6-7 chars. 100 lines ~ 700 chars.
    # Set chunk size 200, overlap 50.
    chunks = chunker.chunk_text(path, chunk_size=200, overlap=50, rel_path="manual.txt")
    
    assert len(chunks) > 1
    
    first_chunk = chunks[0]
    assert first_chunk['metadata']['start_line'] == 1
    # Verify end line is reasonable
    assert first_chunk['metadata']['end_line'] > 1
    
    second_chunk = chunks[1]
    # Overlap means start of 2nd chunk < end of 1st chunk
    assert second_chunk['metadata']['start_line'] < first_chunk['metadata']['end_line']
