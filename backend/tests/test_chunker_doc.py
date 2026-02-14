import unittest
import os
import tempfile
import shutil
from backend.app.services.chunker import CodeChunker

class TestChunkerDoc(unittest.TestCase):
    def setUp(self):
        self.chunker = CodeChunker()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_test_file(self, name, content):
        path = os.path.join(self.test_dir, name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path

    def test_markdown_chunking(self):
        content = "# Title\nThis is a test documentation for AutoWiki."
        path = self.create_test_file("README.md", content)
        chunks = self.chunker.chunk_file(path, rel_path="README.md")
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]['metadata']['type'], 'documentation')
        self.assertEqual(chunks[0]['metadata']['file_path'], 'README.md')
        
        # Verify line calculation
        # 1-based indexing check
        self.assertEqual(chunks[0]['metadata']['start_line'], 1) 
        # Content has 2 lines
        self.assertEqual(chunks[0]['metadata']['end_line'], 2)

    def test_text_sliding_window_lines(self):
        # Create multi-line text
        lines = [f"Line {i}" for i in range(1, 101)] # 100 lines
        content = "\n".join(lines)
        path = self.create_test_file("manual.txt", content)
        
        # Chunk with small size to split
        # Avg line len is ~6-7 chars. 100 lines ~ 700 chars.
        # Set chunk size 200, overlap 50.
        chunks = self.chunker.chunk_text(path, chunk_size=200, overlap=50, rel_path="manual.txt")
        
        self.assertTrue(len(chunks) > 1)
        
        first_chunk = chunks[0]
        self.assertEqual(first_chunk['metadata']['start_line'], 1)
        # Verify end line is reasonable
        self.assertTrue(first_chunk['metadata']['end_line'] > 1)
        
        second_chunk = chunks[1]
        # Overlap means start of 2nd chunk < end of 1st chunk
        self.assertTrue(second_chunk['metadata']['start_line'] < first_chunk['metadata']['end_line'])

if __name__ == '__main__':
    unittest.main()