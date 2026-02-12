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

export interface IngestStats {
  files_processed: number;
  chunks_generated: number;
}
