import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
import shutil
import sys

# Ensure backend path is in sys.path for imports
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.ingestion import IngestionService

class TestIngestionStats(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Mock git before it's used in IngestionService.__init__ if needed
        # But here we focus on ingest_directory
        with patch('git.Repo.clone_from'):
            self.service = IngestionService()
            # Mock storage to avoid actual DB operations
            self.service.storage = MagicMock()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_file(self, filename, content):
        path = os.path.join(self.test_dir, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path

    def test_ingestion_stats_calculation(self):
        # 1. 创建 1 个代码文件 (2 个 chunks)
        self.create_file("app.py", "def func1(): pass\ndef func2(): pass")
        
        # 2. 创建 2 个文档文件 (各 1 个 chunk)
        self.create_file("docs/intro.md", "# Intro")
        self.create_file("docs/usage.txt", "Usage guide")

        # 执行统计
        stats = self.service.ingest_directory(self.test_dir)

        # 验证文件计数
        self.assertEqual(stats['files_processed'], 3)
        self.assertEqual(stats['code_files'], 1)
        self.assertEqual(stats['doc_files'], 2)

        # 验证 Chunk 计数
        self.assertEqual(stats['code_chunks'], 2)
        self.assertEqual(stats['doc_chunks'], 2)
        self.assertEqual(stats['chunks_generated'], 4)

    def test_ignore_logic(self):
        # 验证被忽略的文件不计入统计
        self.create_file(".git/config", "git stuff")
        self.create_file("node_modules/package/index.js", "npm stuff")
        self.create_file("valid.py", "def ok(): pass")

        stats = self.service.ingest_directory(self.test_dir)

        self.assertEqual(stats['files_processed'], 1)
        self.assertEqual(stats['code_files'], 1)

if __name__ == '__main__':
    unittest.main()