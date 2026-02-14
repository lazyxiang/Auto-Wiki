from fastapi import APIRouter, HTTPException, Query
from app.schemas import IngestRequest
from app.services.ingestion import IngestionService
from app.services.storage import VectorStorage
from app.services.graph import GraphService

router = APIRouter()
ingestion_service = IngestionService()
storage_service = VectorStorage() 
graph_service = GraphService()

@router.post("/ingest")
def trigger_ingestion(request: IngestRequest):
    """
    Triggers ingestion from a GitHub repository URL.
    Returns the project_id which must be used for subsequent queries.
    """
    try:
        stats = ingestion_service.ingest_project(repo_url=request.repo_url)
        return {"status": "success", "stats": stats}
    except Exception as e:
        print(f"Ingestion Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
def search_code(q: str, project_id: str = Query(..., description="The project ID returned from ingestion"), limit: int = 5):
    """
    Semantic search for code and documentation chunks within a specific project.
    """
    try:
        results = storage_service.query_code(project_id, q, n_results=limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
def clear_database(project_id: str = Query(..., description="The project ID to clear")):
    """
    Deletes all indexed data and dependency graphs for a specific project.
    """
    try:
        storage_count = storage_service.clear_all(project_id)
        storage_service.delete_collection(project_id)
        graph_service.delete_graph(project_id)
        return {"status": "success", "deleted_count": storage_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_stats(project_id: str = Query(..., description="The project ID")):
    """
    Get current database statistics for a project.
    """
    try:
        return storage_service.get_stats(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))