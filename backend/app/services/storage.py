import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings

class VectorStorage:
    def __init__(self, persistence_path: str = None):
        if persistence_path is None:
            # Default to a path compatible with both Docker (/app/data) and Local (./data)
            persistence_path = os.getenv("CHROMA_DB_PATH", os.path.join(os.getcwd(), "data", "chromadb"))

        if not os.path.exists(persistence_path):
            os.makedirs(persistence_path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persistence_path)

    def _get_collection_name(self, project_id: str) -> str:
        """Generates a safe collection name from project_id."""
        # ChromaDB collection names must be alphanumeric, underscores, hyphens.
        # Ensure project_id is safe.
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in project_id)
        return f"autowiki_{safe_id}"

    def get_collection(self, project_id: str):
        """Retrieves or creates a collection for the given project."""
        name = self._get_collection_name(project_id)
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"} # Cosine similarity for code search
        )

    def delete_collection(self, project_id: str):
        """Deletes the collection for a project."""
        name = self._get_collection_name(project_id)
        try:
            self.client.delete_collection(name)
            print(f"Deleted collection: {name}")
        except Exception as e:
            # Collection might not exist, which is fine.
            # print(f"Collection {name} not found or error deleting: {e}")
            pass

    def save_chunks(self, project_id: str, chunks: List[Dict[str, Any]]):
        """
        Saves parsed code chunks to the project's collection.
        """
        if not chunks:
            return

        collection = self.get_collection(project_id)
        ids = [c["id"] for c in chunks]
        documents = [c["content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Upsert (update if exists, insert if new)
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        print(f"Saved {len(chunks)} chunks to Vector DB for project {project_id}.")

    def query_code(self, project_id: str, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search for code chunks within a project.
        """
        try:
            collection = self.client.get_collection(self._get_collection_name(project_id))
        except ValueError:
            return [] # Collection not found

        results = collection.query(
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

    def clear_all(self, project_id: str):
        """
        Deletes all entries in the collection for a project.
        """
        try:
            collection = self.client.get_collection(self._get_collection_name(project_id))
            count = collection.count()
            if count > 0:
                # Delete by matching all IDs (ChromaDB requirement for bulk delete)
                all_ids = collection.get()['ids']
                if all_ids:
                    collection.delete(ids=all_ids)
            return count
        except ValueError:
            return 0

    def get_stats(self, project_id: str):
        try:
            collection = self.client.get_collection(self._get_collection_name(project_id))
            return {
                "count": collection.count()
            }
        except ValueError:
            return {"count": 0}