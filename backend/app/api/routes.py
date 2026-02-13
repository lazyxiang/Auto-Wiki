from fastapi import APIRouter, HTTPException
from app.schemas import IngestRequest
from app.services.ingestion import IngestionService
from app.services.storage import VectorStorage

router = APIRouter()
ingestion_service = IngestionService()
storage_service = VectorStorage() 

@router.post("/ingest")
def trigger_ingestion(request: IngestRequest):
    """
    Triggers ingestion from a GitHub repository URL.
    """
    try:
        stats = ingestion_service.ingest_project(repo_url=request.repo_url)
        return {"status": "success", "stats": stats}
    except Exception as e:
        print(f"Ingestion Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
def search_code(q: str, limit: int = 5):
    """
    Semantic search for code and documentation chunks.
    """
    try:
        results = storage_service.query_code(q, n_results=limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
def clear_database():
    """
    Deletes all indexed data in the vector database.
    """
    try:
        count = storage_service.clear_all()
        return {"status": "success", "deleted_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_stats():
    """
    Get current database statistics.
    """
    try:
        return storage_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))