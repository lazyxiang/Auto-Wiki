"use client";

import { useState } from "react";
import { Search, Loader2, FolderOpen, Terminal } from "lucide-react";
import { searchCode, triggerIngest } from "@/lib/api";
import { SearchResult } from "@/lib/types";

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [ingestPath, setIngestPath] = useState("/app");
  const [ingesting, setIngesting] = useState(false);
  const [ingestStats, setIngestStats] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await searchCode(query);
      setResults(data);
    } catch (error) {
      console.error(error);
      alert("Search failed. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleIngest = async () => {
    if (!ingestPath.trim()) return;
    setIngesting(true);
    setIngestStats(null);
    try {
      const stats = await triggerIngest(ingestPath);
      setIngestStats(`Processed ${stats.files_processed} files, ${stats.chunks_generated} chunks.`);
    } catch (error) {
      console.error(error);
      alert("Ingestion failed. Check path and backend logs.");
    } finally {
      setIngesting(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans selection:bg-teal-500/30">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Header */}
        <header className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-teal-400 to-blue-500 bg-clip-text text-transparent">
              AutoWiki
            </h1>
            <p className="text-slate-400 mt-2">
              Semantic Code Search & Documentation Engine
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500 bg-slate-900 px-4 py-2 rounded-full border border-slate-800">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            System Online
          </div>
        </header>

        {/* Ingestion Section */}
        <section className="bg-slate-900/50 rounded-xl border border-slate-800 p-6">
          <h2 className="text-lg font-semibold flex items-center gap-2 mb-4 text-slate-200">
            <FolderOpen className="w-5 h-5 text-blue-400" />
            Ingest Repository
          </h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={ingestPath}
              onChange={(e) => setIngestPath(e.target.value)}
              placeholder="/app/codebase"
              className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-600"
            />
            <button
              onClick={handleIngest}
              disabled={ingesting}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
            >
              {ingesting ? <Loader2 className="w-4 h-4 animate-spin" /> : "Ingest"}
            </button>
          </div>
          {ingestStats && (
            <div className="mt-4 text-xs font-mono text-emerald-400 bg-emerald-950/30 px-3 py-2 rounded border border-emerald-900/50 inline-block">
              ✓ {ingestStats}
            </div>
          )}
        </section>

        {/* Search Section */}
        <section className="space-y-6">
          <form onSubmit={handleSearch} className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="w-5 h-5 text-slate-500 group-focus-within:text-teal-400 transition-colors" />
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for functions, classes, or logic (e.g., 'User authentication', 'Parser logic')..."
              className="w-full bg-slate-900 border border-slate-800 rounded-2xl pl-12 pr-4 py-4 text-lg focus:ring-2 focus:ring-teal-500/50 outline-none shadow-xl transition-all placeholder:text-slate-600"
            />
          </form>

          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 text-teal-500 animate-spin" />
            </div>
          ) : (
            <div className="grid gap-4">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="group bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-teal-500/30 hover:shadow-lg hover:shadow-teal-900/10 transition-all cursor-pointer"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-3">
                      <span className="bg-slate-800 text-teal-300 text-xs px-2 py-1 rounded border border-slate-700 font-mono">
                        {result.metadata.type}
                      </span>
                      <h3 className="font-semibold text-lg text-slate-200 group-hover:text-teal-400 transition-colors">
                        {result.metadata.name}
                      </h3>
                    </div>
                    <span className="text-xs text-slate-500 font-mono bg-slate-950 px-2 py-1 rounded">
                      {result.metadata.file_path.split("/").pop()}
                    </span>
                  </div>
                  
                  <div className="relative">
                    <pre className="text-xs md:text-sm text-slate-400 font-mono bg-slate-950/50 p-4 rounded-lg overflow-x-auto border border-slate-800/50 max-h-48 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                      <code>{result.content}</code>
                    </pre>
                    <div className="absolute bottom-2 right-2 flex gap-2">
                       <span className="text-[10px] text-slate-600 px-2 py-1 bg-slate-900 rounded border border-slate-800">
                          Lines {result.metadata.start_line}-{result.metadata.end_line}
                       </span>
                    </div>
                  </div>
                </div>
              ))}
              
              {results.length === 0 && query && !loading && (
                <div className="text-center py-12 text-slate-500">
                  No results found for "{query}"
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}