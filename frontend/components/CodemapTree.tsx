"use client";

import { useState } from "react";
import { Folder, FolderOpen, File, FileText, ChevronRight, ChevronDown, Zap } from "lucide-react";
import { CodemapNode } from "@/lib/types";

interface CodemapTreeProps {
  node: CodemapNode;
  level?: number;
}

export default function CodemapTree({ node, level = 0 }: CodemapTreeProps) {
  // Auto-expand if active (contains hits)
  const [isOpen, setIsOpen] = useState(node.is_active || level === 0);
  const [showChunks, setShowChunks] = useState(false);

  const hasChildren = node.children && node.children.length > 0;
  const isFile = node.type === "file";
  
  // Indent based on level
  const paddingLeft = level * 1.5;

  const toggleOpen = () => {
    if (hasChildren) setIsOpen(!isOpen);
    if (isFile && node.is_hit) setShowChunks(!showChunks);
  };

  // Color coding for layers (optional visual cue)
  const layerColors = [
    "text-amber-400", // 0: Docs
    "text-blue-400",  // 1: API
    "text-purple-400",// 2: Core
    "text-slate-400", // 3: Utils
    "text-slate-500"  // 4: Other
  ];
  const iconColor = node.layer !== undefined ? layerColors[node.layer] || "text-slate-400" : "text-slate-400";

  return (
    <div className="select-none">
      <div 
        onClick={toggleOpen}
        className={`
          flex items-center gap-2 py-1.5 px-2 hover:bg-slate-800/50 rounded cursor-pointer transition-colors
          ${node.is_hit ? "bg-teal-900/20" : ""}
          ${node.is_active && !node.is_hit ? "text-slate-200" : "text-slate-400"}
        `}
        style={{ paddingLeft: `${paddingLeft + 0.5}rem` }}
      >
        {/* Expand Icon */}
        <div className="w-4 h-4 flex items-center justify-center text-slate-600">
          {hasChildren && (
            isOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />
          )}
        </div>

        {/* Type Icon */}
        <div className={iconColor}>
          {isFile ? (
            node.name.endsWith(".md") ? <FileText className="w-4 h-4" /> : <File className="w-4 h-4" />
          ) : (
            isOpen ? <FolderOpen className="w-4 h-4 text-slate-500" /> : <Folder className="w-4 h-4 text-slate-600" />
          )}
        </div>

        {/* Name */}
        <span className={`text-sm ${node.is_hit ? "font-semibold text-teal-300" : ""}`}>
          {node.name}
        </span>

        {/* Badges */}
        {node.is_hit && (
          <div className="ml-auto flex items-center gap-2">
             <span className="text-[10px] bg-teal-950 text-teal-400 px-1.5 py-0.5 rounded border border-teal-900/50 flex items-center gap-1">
               <Zap className="w-3 h-3" />
               Match
             </span>
             {node.matched_chunks && (
                 <span className="text-[10px] text-slate-500">
                    {node.matched_chunks.length} chunks
                 </span>
             )}
          </div>
        )}
      </div>

      {/* Children */}
      {isOpen && hasChildren && (
        <div className="border-l border-slate-800/50 ml-4">
          {node.children!.map((child) => (
            <CodemapTree key={child.id} node={child} level={level + 1} />
          ))}
        </div>
      )}

      {/* Code Chunks (if file hit and expanded) */}
      {showChunks && node.matched_chunks && (
        <div className="ml-8 mt-1 space-y-2 mb-2 border-l-2 border-teal-500/20 pl-4">
          {node.matched_chunks.map((chunk) => (
             <div key={chunk.id} className="bg-slate-900/50 border border-slate-800 rounded p-3 text-xs font-mono text-slate-400 overflow-x-auto">
                 <div className="flex justify-between text-[10px] text-slate-500 mb-1 border-b border-slate-800 pb-1">
                     <span>Lines {chunk.metadata.start_line}-{chunk.metadata.end_line}</span>
                     <span>Relevance: {chunk.distance?.toFixed(2)}</span>
                 </div>
                 <pre>{chunk.content}</pre>
             </div>
          ))}
        </div>
      )}
    </div>
  );
}
