export interface SearchResult {
  id: string;
  content: string;
  metadata: {
    name: string;
    type: string;
    file_path: string;
    language: string;
    start_line: number;
    end_line: number;
  };
  distance: number;
}

export interface CodemapNode {
  id: string;
  name: string;
  type: "file" | "folder";
  children?: CodemapNode[];
  layer?: number;
  importance?: number;
  is_active?: boolean;
  is_hit?: boolean;
  search_score?: number;
  matched_chunks?: SearchResult[];
}

export interface SearchResponse {
  tree: CodemapNode;
  stats: {
    hits_found: number;
    vector_results: number;
  };
  fallback?: boolean;
  results?: SearchResult[];
}

export interface IngestStats {
  files_processed: number;
  chunks_generated: number;
  code_files: number;
  doc_files: number;
  code_chunks: number;
  doc_chunks: number;
  repo_url?: string;
}
