from fastapi import APIRouter, HTTPException, Query
from ..schemas import IngestRequest
from ..services.ingestion import IngestionService
from ..services.storage import VectorStorage
from ..services.graph import GraphService
from ..services.search import SearchService

router = APIRouter()
ingestion_service = IngestionService()
storage_service = VectorStorage() 
graph_service = GraphService()
search_service = SearchService()

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
    Semantic search + Codemap tree overlay.
    Returns the module tree with search hits injected.
    """
    try:
        # New Search Service Logic
        result = search_service.search(project_id, q, limit)
        return result
    except Exception as e:
        # Fallback to simple vector search if something fails (or just raise)
        print(f"Search Error: {e}")
        try:
             results = storage_service.query_code(project_id, q, n_results=limit)
             return {"results": results, "fallback": True}
        except Exception as inner_e:
             raise HTTPException(status_code=500, detail=str(inner_e))

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