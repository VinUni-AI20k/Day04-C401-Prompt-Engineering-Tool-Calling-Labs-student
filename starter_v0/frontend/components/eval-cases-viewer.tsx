"use client";

import { useEffect, useState } from "react";
import { RefreshCw, AlertCircle, ChevronRight, CheckCircle2, Award, Terminal, Wrench } from "lucide-react";

interface EvalCase {
  id: string;
  phase: string;
  query?: string;
  turns?: Array<{ role: string; content: string }>;
  expect: {
    tool_calls?: Array<{ name: string; args: Record<string, any> }>;
    no_tool?: boolean;
    behavior?: string;
  };
  metadata?: {
    skill?: string;
    difficulty?: string;
    what_it_tests?: string;
  };
}

export function EvalCasesViewer() {
  const [data, setData] = useState<Record<string, EvalCase[]> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string>("");
  const [selectedCaseId, setSelectedCaseId] = useState<string>("");

  const fetchCases = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/eval-cases");
      if (!res.ok) throw new Error("Failed to fetch evaluation cases");
      const json = await res.json();
      setData(json);
      const files = Object.keys(json);
      if (files.length > 0) {
        setSelectedFile(files[0]);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center font-mono text-xs text-[#3c3a39]">
        <RefreshCw className="size-4 animate-spin text-[#ff7300] mr-2" />
        /loading-eval-cases...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-600 flex items-center gap-2">
        <AlertCircle className="size-4 shrink-0" />
        <span>Error: {error || "Failed to load evaluation cases"}</span>
      </div>
    );
  }

  const files = Object.keys(data);
  const activeFileData = data[selectedFile] as any;
  const activeCases: EvalCase[] = activeFileData
    ? (Array.isArray(activeFileData) ? activeFileData : activeFileData.cases || [])
    : [];
  const activeCase = activeCases.find((c) => c.id === selectedCaseId) || activeCases[0];

  const getDifficultyBadge = (difficulty?: string) => {
    if (!difficulty) return null;
    const colors: Record<string, string> = {
      easy: "border-emerald-500/20 bg-emerald-500/10 text-emerald-600",
      medium: "border-amber-500/20 bg-amber-500/10 text-amber-600",
      hard: "border-red-500/20 bg-red-500/10 text-red-600",
    };
    return (
      <span className={`rounded-full border px-2 py-0.5 text-[9px] font-mono font-bold uppercase ${colors[difficulty] || "border-neutral-500/20 bg-neutral-500/10 text-neutral-600"}`}>
        {difficulty}
      </span>
    );
  };

  return (
    <div className="flex min-h-0 flex-1 gap-4 h-full">
      {/* Sub Sidebar: List of files and cases */}
      <aside className="w-64 flex flex-col rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] shadow-sm shrink-0">
        <div className="p-3 border-b border-[rgba(11,9,7,0.08)] bg-[#f7f7f5]/30">
          <span className="font-mono text-[9px] font-bold text-[#ff7300] uppercase tracking-wider">
            /eval-datasets
          </span>
          <select
            className="w-full mt-2 rounded-lg border border-[rgba(11,9,7,0.12)] bg-[#fefcf5] p-2 text-xs font-semibold text-[#3c3a39] outline-none"
            value={selectedFile}
            onChange={(e) => {
              setSelectedFile(e.target.value);
              setSelectedCaseId("");
            }}
          >
            {files.map((file) => (
              <option key={file} value={file}>
                {file}
              </option>
            ))}
          </select>
        </div>

        <div className="flex-1 overflow-auto p-2.5 space-y-1">
          <span className="font-mono text-[8px] font-bold uppercase tracking-wider text-[rgba(11,9,7,0.4)] px-1.5 block mb-1">
            /cases ({activeCases.length})
          </span>
          {activeCases.map((c) => {
            const isSelected = selectedCaseId ? selectedCaseId === c.id : activeCases[0]?.id === c.id;
            return (
              <button
                key={c.id}
                onClick={() => setSelectedCaseId(c.id)}
                className={`w-full flex items-center justify-between rounded-lg border p-2 text-left transition-all ${
                  isSelected
                    ? "border-[#3c3a39] bg-[#eaeae2]/40"
                    : "border-transparent bg-transparent hover:bg-[#eaeae2]/10"
                }`}
                type="button"
              >
                <div className="min-w-0">
                  <p className="text-[11px] font-bold text-[#3c3a39] truncate">{c.id}</p>
                  <p className="text-[9px] text-[rgba(11,9,7,0.4)] truncate mt-0.5">
                    {c.query || (c.turns && c.turns[0]?.content) || "Multi-turn"}
                  </p>
                </div>
                <ChevronRight className="size-3 text-[rgba(11,9,7,0.3)] shrink-0" />
              </button>
            );
          })}
        </div>
      </aside>

      {/* Main Content Area */}
      <section className="flex-1 rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] p-5 shadow-sm overflow-auto space-y-5">
        {activeCase ? (
          <div className="space-y-5">
            {/* Case Header Card */}
            <div className="rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-5 shadow-xs flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[9px] font-bold text-[#817fff] uppercase tracking-wider">
                    /test-case-spec
                  </span>
                  {getDifficultyBadge(activeCase.metadata?.difficulty)}
                </div>
                <h3 className="text-md font-bold text-[#3c3a39] mt-1.5">{activeCase.id}</h3>
                {activeCase.metadata?.skill && (
                  <p className="text-[10px] text-[rgba(11,9,7,0.4)] font-mono mt-1">
                    Skill group: {activeCase.metadata.skill}
                  </p>
                )}
              </div>
              <span className="rounded-full bg-[#eaeae2] px-2.5 py-1 text-[10px] font-mono font-bold text-[rgba(11,9,7,0.6)]">
                Phase {activeCase.phase}
              </span>
            </div>

            {/* Test Description */}
            {activeCase.metadata?.what_it_tests && (
              <div className="rounded-xl border border-[rgba(11,9,7,0.06)] bg-[#f7f7f5] p-4 flex gap-3">
                <Award className="size-4 shrink-0 text-amber-500" />
                <div>
                  <h4 className="font-mono text-[9px] font-bold uppercase text-[rgba(11,9,7,0.4)]">
                    /what-it-tests
                  </h4>
                  <p className="text-xs text-[rgba(11,9,7,0.65)] mt-1 leading-5">
                    {activeCase.metadata.what_it_tests}
                  </p>
                </div>
              </div>
            )}

            {/* Input prompt / Multi-turns */}
            <div className="space-y-2">
              <h4 className="font-mono text-[10px] font-bold uppercase text-[#ff7300] tracking-wider">
                /user-input-query
              </h4>
              {activeCase.query ? (
                <div className="rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-4 font-mono text-xs text-[#3c3a39] leading-5">
                  {activeCase.query}
                </div>
              ) : (
                <div className="space-y-2.5">
                  {activeCase.turns?.map((turn, i) => (
                    <div
                      key={i}
                      className={`flex gap-3 items-start p-3.5 rounded-xl border ${
                        turn.role === "user"
                          ? "border-[rgba(11,9,7,0.08)] bg-[#fefcf5]"
                          : "border-transparent bg-[#eaeae2]/30"
                      }`}
                    >
                      <span className="font-mono text-[9px] font-bold uppercase tracking-wider text-[rgba(11,9,7,0.4)] mt-0.5 shrink-0 w-16">
                        {turn.role}
                      </span>
                      <p className="text-xs text-[#3c3a39] leading-5">{turn.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Expectations */}
            <div className="space-y-2">
              <h4 className="font-mono text-[10px] font-bold uppercase text-[#2677ff] tracking-wider">
                /expected-behavior
              </h4>
              <div className="rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-4 space-y-4">
                {activeCase.expect.no_tool ? (
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="size-5 text-emerald-500" />
                    <div>
                      <span className="block text-xs font-bold text-emerald-600">
                        No Tool Call Expected
                      </span>
                      <span className="block text-[10px] text-[rgba(11,9,7,0.5)] mt-0.5">
                        Behavior: {activeCase.expect.behavior || "Refuse or answer directly"}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <span className="block text-xs font-bold text-[rgba(11,9,7,0.8)] flex items-center gap-1.5">
                      <Wrench className="size-4 text-[#2677ff]" />
                      Expects local tool calls:
                    </span>
                    <div className="grid md:grid-cols-2 gap-3">
                      {activeCase.expect.tool_calls?.map((call, i) => (
                        <div
                          key={i}
                          className="rounded-lg border border-[rgba(11,9,7,0.06)] bg-[#fffcf6] p-3 space-y-2 shadow-2xs"
                        >
                          <span className="font-mono text-xs font-bold text-[#ff272d]">
                            {call.name}
                          </span>
                          {Object.keys(call.args).length > 0 ? (
                            <pre className="font-mono text-[10px] text-[rgba(11,9,7,0.6)] bg-[#f7f7f5] p-2 rounded max-h-32 overflow-auto">
                              <code>{JSON.stringify(call.args, null, 2)}</code>
                            </pre>
                          ) : (
                            <span className="block text-[10px] text-[rgba(11,9,7,0.4)] italic">
                              No explicit arguments (accepts any subset)
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-xs text-neutral-500 font-mono">/select-a-test-case-from-the-list...</p>
        )}
      </section>
    </div>
  );
}
