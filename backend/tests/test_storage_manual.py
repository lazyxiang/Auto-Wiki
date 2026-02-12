import sys
import os
import shutil

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.storage import VectorStorage

def test_vector_storage():
    print("Testing Vector Storage...")
    
    # Use a separate test path to avoid messing with real data
    test_db_path = "/app/data/test_chroma"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)
        
    storage = VectorStorage(persistence_path=test_db_path)
    
    # Create dummy chunks
    chunks = [
        {
            "id": "1",
            "content": "def calculate_sum(a, b): return a + b",
            "metadata": {"name": "calculate_sum", "type": "function", "language": "python"}
        },
        {
            "id": "2",
            "content": "class UserManager: def get_user(self, id): pass",
            "metadata": {"name": "UserManager", "type": "class", "language": "python"}
        },
        {
            "id": "3",
            "content": "function login(username, password) { return true; }",
            "metadata": {"name": "login", "type": "function", "language": "javascript"}
        }
    ]
    
    print("Saving chunks...")
    storage.save_chunks(chunks)
    
    stats = storage.get_stats()
    print(f"Collection count: {stats['count']}")
    assert stats['count'] == 3
    
    print("Querying 'sum'...")
    results = storage.query_code("sum", n_results=1)
    print(f"Top result: {results[0]['metadata']['name']}")
    assert results[0]['id'] == "1"
    
    print("Querying 'user'...")
    results = storage.query_code("user management", n_results=1)
    print(f"Top result: {results[0]['metadata']['name']}")
    assert results[0]['id'] == "2"

    print("Vector Storage Test PASSED")

if __name__ == "__main__":
    try:
        test_vector_storage()
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
