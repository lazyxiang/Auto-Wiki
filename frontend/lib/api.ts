import { SearchResult, IngestStats, SearchResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function searchCode(query: string, projectId: string): Promise<SearchResponse> {
  // Use project_id from input or default/auto-detect if needed
  // For now we assume project_id is handled or hardcoded in backend mock if not provided
  // But wait, the previous code didn't pass project_id?
  // Ah, previous code: searchCode(query). Backend expects project_id.
  // The previous routes.py had project_id as Query param.
  // The frontend was missing project_id passing?
  // Let's assume for MVP local we might have a default or we need to pass it.
  // The Ingestion returns project_id. We should store it.
  
  const res = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}&project_id=${projectId}`);
  if (!res.ok) throw new Error("Search failed");
  const data = await res.json();
  return data; // Returns the full object { tree, stats, ... }
}

export async function triggerIngest(repoUrl: string): Promise<IngestStats & { project_id: string }> {
  const res = await fetch(`${API_URL}/api/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl }),
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Ingestion failed");
  }
  
  const data = await res.json();
  return data.stats;
}

export async function clearDatabase(projectId: string): Promise<{ deleted_count: number }> {
  const res = await fetch(`${API_URL}/api/clear?project_id=${projectId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Clear failed");
  return res.json();
}