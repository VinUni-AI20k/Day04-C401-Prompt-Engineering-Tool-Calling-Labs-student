"use client";

import { useEffect, useState } from "react";
import { RefreshCw, AlertCircle, ChevronRight, FileCode, FileText, CheckCircle2 } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface ArtifactData {
  systemPrompt: string;
  toolsYaml: string;
  reportMd: string;
  runbookMd: string;
}

export function PromptToolsViewer() {
  const [data, setData] = useState<ArtifactData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string>("system_prompt.md");

  const fetchArtifacts = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/prompt-tools");
      if (!res.ok) throw new Error("Failed to fetch artifacts");
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArtifacts();
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center font-mono text-xs text-[#3c3a39]">
        <RefreshCw className="size-4 animate-spin text-[#ff7300] mr-2" />
        /loading-prompt-and-tools-artifacts...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-600 flex items-center gap-2">
        <AlertCircle className="size-4 shrink-0" />
        <span>Error: {error || "Failed to load artifacts"}</span>
      </div>
    );
  }

  const files = [
    { id: "system_prompt.md", name: "system_prompt.md", type: "markdown", content: data.systemPrompt },
    { id: "tools.yaml", name: "tools.yaml", type: "yaml", content: data.toolsYaml },
    { id: "REPORT.md", name: "REPORT.md", type: "markdown", content: data.reportMd },
    { id: "PERSON1_RUNBOOK.md", name: "PERSON1_RUNBOOK.md", type: "markdown", content: data.runbookMd },
  ];

  const activeFile = files.find((f) => f.id === selectedFile) || files[0];

  return (
    <div className="flex min-h-0 flex-1 gap-4 h-full">
      {/* Sub Sidebar: List of artifacts */}
      <aside className="w-64 flex flex-col rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] shadow-sm shrink-0">
        <div className="p-3 border-b border-[rgba(11,9,7,0.08)] bg-[#f7f7f5]/30">
          <span className="font-mono text-[9px] font-bold text-[#ff7300] uppercase tracking-wider">
            /artifacts-list
          </span>
          <p className="text-[10px] text-[rgba(11,9,7,0.5)] mt-1">
            Các tệp cấu hình và tài liệu của dự án.
          </p>
        </div>

        <div className="flex-1 overflow-auto p-2.5 space-y-1">
          {files.map((file) => {
            const isSelected = selectedFile === file.id;
            const Icon = file.type === "markdown" ? FileText : FileCode;
            return (
              <button
                key={file.id}
                onClick={() => setSelectedFile(file.id)}
                className={`w-full flex items-center gap-2.5 rounded-lg border p-2.5 text-left transition-all ${
                  isSelected
                    ? "border-[#3c3a39] bg-[#eaeae2]/40"
                    : "border-transparent bg-transparent hover:bg-[#eaeae2]/10"
                }`}
                type="button"
              >
                <Icon className={`size-4 shrink-0 ${isSelected ? "text-[#ff7300]" : "text-[rgba(11,9,7,0.4)]"}`} />
                <div className="min-w-0 flex-1">
                  <p className="text-[11px] font-bold text-[#3c3a39] truncate">{file.name}</p>
                  <p className="text-[9px] text-[rgba(11,9,7,0.4)] truncate mt-0.5">
                    {file.type === "markdown" ? "Markdown Text" : "YAML Declaration"}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </aside>

      {/* Main Content Area */}
      <section className="flex-1 rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] p-5 shadow-sm overflow-auto">
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-[rgba(11,9,7,0.08)] pb-3">
            <div>
              <span className="font-mono text-[9px] font-bold text-[#817fff] uppercase tracking-wider">
                /artifact-viewer
              </span>
              <h3 className="text-sm font-bold text-[#3c3a39] mt-0.5">{activeFile.name}</h3>
            </div>
            <button
              onClick={fetchArtifacts}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] text-[10px] font-mono hover:bg-[#eaeae2]/30 transition-all text-[#3c3a39]"
            >
              <RefreshCw className="size-3" />
              Reload
            </button>
          </div>

          {!activeFile.content ? (
            <div className="rounded-xl border border-dashed border-[rgba(11,9,7,0.1)] p-8 text-center text-xs text-[rgba(11,9,7,0.4)] font-mono">
              /artifact-file-is-empty-or-not-found
            </div>
          ) : activeFile.type === "markdown" ? (
            <div className="prose max-w-none text-xs text-[#3c3a39] leading-6 bg-[#fefcf5] border border-[rgba(11,9,7,0.06)] rounded-xl p-5 overflow-auto">
              <ReactMarkdown>{activeFile.content}</ReactMarkdown>
            </div>
          ) : (
            <pre className="rounded-xl border border-[rgba(11,9,7,0.06)] bg-[#fefcf5] p-4 overflow-auto font-mono text-[11px] leading-5 text-[rgba(11,9,7,0.75)] max-h-[70vh]">
              <code>{activeFile.content}</code>
            </pre>
          )}
        </div>
      </section>
    </div>
  );
}
