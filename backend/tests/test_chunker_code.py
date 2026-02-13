import unittest
import os
import tempfile
import shutil
from app.services.chunker import CodeChunker

class TestChunkerCode(unittest.TestCase):
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

    def test_python_code_chunking(self):
        content = """
class MyClass:
    def method_a(self):
        pass

def top_level_func():
    return True
"""
        path = self.create_test_file("app.py", content)
        # Pass rel_path as if we are ingesting from root
        chunks = self.chunker.chunk_file(path, rel_path="app.py")
        
        self.assertTrue(len(chunks) >= 2)
        
        # Verify metadata
        self.assertEqual(chunks[0]['metadata']['language'], 'python')
        self.assertEqual(chunks[0]['metadata']['file_path'], 'app.py') # Should be relative
        
        # Verify lines are present
        self.assertIsNotNone(chunks[0]['metadata']['start_line'])
        self.assertIsNotNone(chunks[0]['metadata']['end_line'])

    def test_unsupported_file_returns_empty(self):
        path = self.create_test_file("data.bin", "\x00\x01\x02")
        chunks = self.chunker.chunk_file(path, rel_path="data.bin")
        self.assertEqual(len(chunks), 0)

if __name__ == '__main__':
    unittest.main()