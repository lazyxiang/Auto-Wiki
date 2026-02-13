import { SearchResult, IngestStats } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function searchCode(query: string): Promise<SearchResult[]> {
  const res = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("Search failed");
  const data = await res.json();
  return data.results;
}

export async function triggerIngest(repoUrl: string): Promise<IngestStats> {
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

export async function clearDatabase(): Promise<{ deleted_count: number }> {
  const res = await fetch(`${API_URL}/api/clear`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Clear failed");
  return res.json();
}