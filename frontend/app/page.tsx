"use client";

import { useState } from "react";
import { Search, Loader2, Github, Trash2, FileText, Code } from "lucide-react";
import { searchCode, triggerIngest, clearDatabase } from "@/lib/api";
import { SearchResult } from "@/lib/types";

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Ingestion state
  const [repoUrl, setRepoUrl] = useState("");
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
    if (!repoUrl.trim()) {
      alert("Please enter a GitHub repository URL");
      return;
    }

    setIngesting(true);
    setIngestStats(null);
    try {
      const stats = await triggerIngest(repoUrl);
      setIngestStats(
        `Ingested ${stats.files_processed} files (${stats.code_files} code, ${stats.doc_files} docs) ` +
        `generating ${stats.chunks_generated} chunks (${stats.code_chunks} code, ${stats.doc_chunks} docs).`
      );
      setRepoUrl(""); 
    } catch (error: any) {
      console.error(error);
      alert(`Ingestion failed: ${error.message}`);
    } finally {
      setIngesting(false);
    }
  };

  const handleClear = async () => {
    if (!confirm("Are you sure you want to clear all indexed data? This cannot be undone.")) return;
    try {
      const { deleted_count } = await clearDatabase();
      alert(`Successfully cleared ${deleted_count} chunks.`);
      setResults([]);
      setIngestStats(null);
    } catch (error) {
      alert("Failed to clear database.");
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
              Semantic Search & Ingestion for GitHub Projects
            </p>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={handleClear}
              className="text-xs text-slate-500 hover:text-red-400 flex items-center gap-1 transition-colors bg-slate-900 px-3 py-1.5 rounded-md border border-slate-800"
            >
              <Trash2 className="w-3 h-3" /> Clear DB
            </button>
            <div className="flex items-center gap-2 text-xs text-slate-500 bg-slate-900 px-4 py-2 rounded-full border border-slate-800">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              System Online
            </div>
          </div>
        </header>

        {/* Ingestion Section */}
        <section className="bg-slate-900/50 rounded-xl border border-slate-800 p-6">
          <h2 className="text-lg font-semibold flex items-center gap-2 mb-4 text-slate-200">
            <Github className="w-5 h-5 text-blue-400" />
            Import GitHub Repository
          </h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/username/project.git"
              className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-600"
            />
            <button
              onClick={handleIngest}
              disabled={ingesting}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 min-w-[140px] justify-center"
            >
              {ingesting ? <Loader2 className="w-4 h-4 animate-spin" /> : "Start Import"}
            </button>
          </div>
          {ingestStats && (
            <div className="mt-4 text-xs font-mono text-emerald-400 bg-emerald-950/30 px-3 py-2 rounded border border-emerald-900/50 inline-block animate-in fade-in slide-in-from-top-2">
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
              placeholder="Search code or documentation..."
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
                  className="group bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-teal-500/30 hover:shadow-lg hover:shadow-teal-900/10 transition-all"
                >
                  {/* Metadata Header */}
                  <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`p-1.5 rounded-md border ${
                        result.metadata.type === 'documentation' 
                        ? 'bg-amber-950/30 border-amber-900/50 text-amber-400' 
                        : 'bg-teal-950/30 border-teal-900/50 text-teal-400'
                      }`}>
                        {result.metadata.type === 'documentation' ? <FileText className="w-4 h-4"/> : <Code className="w-4 h-4"/>}
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-200 group-hover:text-teal-400 transition-colors">
                          {result.metadata.name}
                        </h3>
                        <p className="text-[10px] text-slate-500 font-mono mt-0.5">
                          {result.metadata.file_path}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                       <span className="text-[10px] text-slate-400 font-mono bg-slate-800 px-2 py-1 rounded border border-slate-700">
                          Lines {result.metadata.start_line} - {result.metadata.end_line}
                       </span>
                    </div>
                  </div>
                  
                  {/* Content Area */}
                  <div className="relative">
                    <pre className={`text-xs md:text-sm text-slate-400 font-mono bg-slate-950/50 p-4 rounded-lg border border-slate-800/50 max-h-40 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent ${
                      result.metadata.type === 'documentation' ? 'whitespace-pre-wrap' : 'overflow-x-auto'
                    }`}>
                      <code>{result.content}</code>
                    </pre>
                  </div>
                </div>
              ))}
              
              {results.length === 0 && query && !loading && (
                <div className="text-center py-12 text-slate-500">
                  No matches found for "{query}"
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}