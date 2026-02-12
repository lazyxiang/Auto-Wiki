import sys
import os
import json

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.chunker import CodeChunker

def test_chunking_self():
    print("Testing Chunker on itself...")
    
    # Path to the chunker.py file inside the container
    target_file = '/app/app/services/chunker.py'
    
    chunker = CodeChunker()
    chunks = chunker.chunk_file(target_file)
    
    print(f"Generated {len(chunks)} chunks from {target_file}")
    
    for chunk in chunks:
        meta = chunk['metadata']
        print(f"- [{meta['type']}] {meta['name']} ({chunk['id'][:8]})")
        
    # Verify we found the class and methods
    names = [c['metadata']['name'] for c in chunks]
    assert 'CodeChunker' in names
    assert 'chunk_file' in names
    assert '_create_chunk' in names
    
    print("Chunker Self-Test PASSED")

if __name__ == "__main__":
    try:
        test_chunking_self()
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
