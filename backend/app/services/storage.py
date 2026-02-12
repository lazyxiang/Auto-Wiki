import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings

class VectorStorage:
    def __init__(self, persistence_path: str = "/app/data/chromadb"):
        self.client = chromadb.PersistentClient(path=persistence_path)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="autowiki_code",
            metadata={"hnsw:space": "cosine"} # Cosine similarity for code search
        )

    def save_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Saves parsed code chunks to ChromaDB.
        """
        if not chunks:
            return

        ids = [c["id"] for c in chunks]
        documents = [c["content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Upsert (update if exists, insert if new)
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        print(f"Saved {len(chunks)} chunks to Vector DB.")

    def query_code(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search for code chunks.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        # Reformat results
        formatted_results = []
        if results['ids']:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
        
        return formatted_results

    def get_stats(self):
        return {
            "count": self.collection.count()
        }
