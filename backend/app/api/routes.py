from fastapi import APIRouter, HTTPException
from app.schemas import IngestRequest
from app.services.ingestion import IngestionService
from app.services.storage import VectorStorage

router = APIRouter()
ingestion_service = IngestionService()
# We use a separate instance for search, but sharing the underlying DB path
storage_service = VectorStorage() 

@router.post("/ingest")
def trigger_ingestion(request: IngestRequest):
    """
    Triggers a full scan and ingestion of the specified directory.
    """
    try:
        stats = ingestion_service.ingest_directory(request.path)
        return {"status": "success", "stats": stats}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # In production, log the full error
        print(f"Ingestion Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
def search_code(q: str, limit: int = 5):
    """
    Semantic search for code chunks.
    """
    try:
        results = storage_service.query_code(q, n_results=limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
