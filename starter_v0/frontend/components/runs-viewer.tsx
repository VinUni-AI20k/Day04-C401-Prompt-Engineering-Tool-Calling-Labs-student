"use client";

import { useEffect, useState } from "react";
import { RefreshCw, AlertCircle, ChevronDown, ChevronRight, CheckCircle2, XCircle, Wrench, ShieldAlert } from "lucide-react";

interface RunDetail {
  fileName: string;
  runId: string;
  version: string;
  suite: string;
  provider: string;
  model: string;
  generatedAt: string;
  summary: {
    total_cases: number;
    measured_cases: number;
    passed_cases: number;
    case_accuracy: number;
    tool_routing_accuracy?: number;
    argument_accuracy?: number;
    multiturn_accuracy?: number;
    failure_counts?: Record<string, number>;
    observed_mismatch_counts?: Record<string, number>;
  } | null;
  results: Array<{
    id: string;
    phase: string;
    suite: string;
    input: any;
    expect: any;
    result: {
      passed: boolean;
      routing_correct?: boolean;
      args_correct?: boolean;
      actual_tool_calls?: Array<{ name: string; args: Record<string, any> }>;
      actual_text?: string | null;
      observed_mismatch?: string | null;
      failures?: string[];
    };
    tool_results?: Array<{
      tool: string;
      args: Record<string, any>;
      result: any;
    }>;
  }>;
}

function renderInputPreview(input: any): string {
  if (typeof input === "string") {
    return input;
  }
  if (Array.isArray(input)) {
    const firstUser = input.find((t: any) => t.role === "user");
    return firstUser ? `${firstUser.content} (${input.length} turns)` : `[Multi-turn: ${input.length} turns]`;
  }
  return String(input || "");
}

export function RunsViewer() {
  const [runs, setRuns] = useState<RunDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string>("");
  const [expandedCaseId, setExpandedCaseId] = useState<string>("");

  const fetchRuns = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/runs");
      if (!res.ok) throw new Error("Failed to fetch runs");
      const json = await res.json();
      setRuns(json);
      if (json.length > 0) {
        setSelectedRunId(json[0].runId);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center font-mono text-xs text-[#3c3a39]">
        <RefreshCw className="size-4 animate-spin text-[#ff7300] mr-2" />
        /loading-evaluation-runs-logs...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-600 flex items-center gap-2">
        <AlertCircle className="size-4 shrink-0" />
        <span>Error: {error}</span>
      </div>
    );
  }

  const activeRun = runs.find((r) => r.runId === selectedRunId) || runs[0];

  return (
    <div className="flex min-h-0 flex-1 gap-4 h-full">
      {/* Sub Sidebar: List of runs */}
      <aside className="w-64 flex flex-col rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] shadow-sm shrink-0">
        <div className="p-3 border-b border-[rgba(11,9,7,0.08)] bg-[#f7f7f5]/30 flex justify-between items-center">
          <div>
            <span className="font-mono text-[9px] font-bold text-[#ff7300] uppercase tracking-wider block">
              /run-history
            </span>
            <span className="text-[10px] text-[rgba(11,9,7,0.5)]">
              Evaluation outputs index
            </span>
          </div>
          <button
            onClick={fetchRuns}
            className="flex size-6 items-center justify-center rounded-lg border border-[rgba(11,9,7,0.1)] bg-[#fefcf5] hover:bg-[#eaeae2] text-[#3c3a39]"
            title="Refresh runs list"
          >
            <RefreshCw className="size-3" />
          </button>
        </div>

        <div className="flex-1 overflow-auto p-2.5 space-y-1">
          {runs.map((run) => {
            const isSelected = selectedRunId === run.runId;
            const accuracy = run.summary ? Math.round(run.summary.case_accuracy * 100) : 0;
            return (
              <button
                key={run.runId}
                onClick={() => {
                  setSelectedRunId(run.runId);
                  setExpandedCaseId("");
                }}
                className={`w-full flex flex-col rounded-lg border p-2.5 text-left transition-all ${
                  isSelected
                    ? "border-[#3c3a39] bg-[#eaeae2]/40"
                    : "border-transparent bg-transparent hover:bg-[#eaeae2]/10"
                }`}
                type="button"
              >
                <div className="flex items-center justify-between w-full">
                  <span className="text-[11px] font-bold text-[#ff272d]">
                    {run.version} ({run.suite})
                  </span>
                  <span className="font-mono text-[10px] font-bold text-[#2677ff]">
                    {accuracy}%
                  </span>
                </div>
                <p className="text-[9px] text-[rgba(11,9,7,0.5)] truncate mt-1">
                  Model: {run.model.split("/").pop()}
                </p>
                <p className="text-[8px] text-[rgba(11,9,7,0.4)] font-mono truncate mt-0.5">
                  {run.generatedAt.replace("T", " ")}
                </p>
              </button>
            );
          })}
        </div>
      </aside>

      {/* Main Content Area */}
      <section className="flex-1 rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] p-5 shadow-sm overflow-auto space-y-5">
        {activeRun ? (
          <div className="space-y-5">
            {/* Run Detail Header */}
            <div className="rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-5 shadow-xs flex justify-between items-start">
              <div>
                <span className="font-mono text-[9px] font-bold text-[#817fff] uppercase tracking-wider">
                  /evaluation-run-details
                </span>
                <h3 className="text-sm font-bold text-[#3c3a39] mt-0.5">{activeRun.runId}</h3>
                <p className="text-[10px] text-[rgba(11,9,7,0.5)] mt-1.5 leading-4">
                  Provider: <code className="font-mono bg-[#eaeae2] px-1 rounded">{activeRun.provider}</code> · 
                  Model: <code className="font-mono bg-[#eaeae2] px-1 rounded">{activeRun.model}</code>
                </p>
              </div>
              <span className="font-mono text-[9px] text-[rgba(11,9,7,0.4)]">
                {activeRun.generatedAt.replace("T", " ")}
              </span>
            </div>

            {/* Metrics cards */}
            {activeRun.summary && (
              <div className="space-y-3">
                <h4 className="font-mono text-[9px] font-bold uppercase text-[rgba(11,9,7,0.4)] tracking-wider">
                  /accuracy-scores
                </h4>
                <div className="grid grid-cols-4 gap-3">
                  <AccuracyCard label="Case Accuracy" value={activeRun.summary.case_accuracy} />
                  <AccuracyCard label="Tool Routing" value={activeRun.summary.tool_routing_accuracy ?? 0} />
                  <AccuracyCard label="Arguments" value={activeRun.summary.argument_accuracy ?? 0} />
                  <AccuracyCard label="Multi-turn" value={activeRun.summary.multiturn_accuracy ?? 0} />
                </div>
              </div>
            )}

            {/* Cases list */}
            <div className="space-y-2">
              <h4 className="font-mono text-[10px] font-bold uppercase text-[#ff7300] tracking-wider">
                /test-cases-results ({activeRun.results.length})
              </h4>
              <div className="divide-y divide-[rgba(11,9,7,0.06)] rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] overflow-hidden">
                {activeRun.results.map((item) => {
                  const isExpanded = expandedCaseId === item.id;
                  const passed = item.result.passed;
                  return (
                    <div key={item.id} className="bg-[#fefcf5]">
                      {/* Accordion header */}
                      <button
                        onClick={() => setExpandedCaseId(isExpanded ? "" : item.id)}
                        className="w-full flex items-center justify-between px-4 py-3.5 hover:bg-[rgba(11,9,7,0.02)] transition-colors text-left"
                        type="button"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          {passed ? (
                            <CheckCircle2 className="size-4.5 text-emerald-500 shrink-0" />
                          ) : (
                            <XCircle className="size-4.5 text-red-500 shrink-0" />
                          )}
                          <div className="min-w-0">
                            <span className="font-mono text-xs font-bold text-[#3c3a39]">
                              {item.id}
                            </span>
                            <span className="block text-[11px] text-[rgba(11,9,7,0.5)] truncate mt-0.5">
                              {renderInputPreview(item.input)}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {!passed && item.result.observed_mismatch && (
                            <span className="rounded bg-red-100 border border-red-200/50 px-1.5 py-0.5 font-mono text-[9px] font-bold text-red-600">
                              {item.result.observed_mismatch}
                            </span>
                          )}
                          <ChevronDown
                            className={`size-4 text-[rgba(11,9,7,0.4)] transition-transform ${
                              isExpanded ? "rotate-180" : ""
                            }`}
                          />
                        </div>
                      </button>

                      {/* Accordion body */}
                      {isExpanded && (
                        <div className="border-t border-[rgba(11,9,7,0.06)] p-4 bg-[#fffcf6]/50 space-y-4 text-xs">
                          {/* Mismatches and errors */}
                          {!passed && item.result.failures && item.result.failures.length > 0 && (
                            <div className="rounded-lg border border-red-200/60 bg-red-50/50 p-3 flex gap-2 text-red-700">
                              <ShieldAlert className="size-4.5 shrink-0 mt-0.5 text-red-500" />
                              <div className="space-y-1">
                                <span className="font-bold text-[11px]">Observed Failures:</span>
                                <ul className="list-disc pl-4 space-y-0.5 text-[11px]">
                                  {item.result.failures.map((fail, i) => (
                                    <li key={i}>{fail}</li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          )}

                          {/* Tool call Comparison */}
                          <div className="grid md:grid-cols-2 gap-4">
                            {/* Expected */}
                            <div className="rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-3 space-y-2">
                              <span className="font-mono text-[9px] font-bold uppercase text-[rgba(11,9,7,0.4)] block">
                                /expected-tool-calls
                              </span>
                              {item.expect.tool_calls && item.expect.tool_calls.length > 0 ? (
                                item.expect.tool_calls.map((call: any, idx: number) => (
                                  <div key={idx} className="font-mono text-[10px] bg-[#f7f7f5] p-2 rounded">
                                    <span className="font-bold text-[#2677ff]">{call.name}</span>
                                    <pre className="text-[9px] text-[rgba(11,9,7,0.6)] mt-1 max-h-24 overflow-auto">
                                      {JSON.stringify(call.args, null, 2)}
                                    </pre>
                                  </div>
                                ))
                              ) : (
                                <span className="text-[10px] italic text-neutral-400">No tools expected (refusal/meta response)</span>
                              )}
                            </div>

                            {/* Actual */}
                            <div className="rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-3 space-y-2">
                              <span className="font-mono text-[9px] font-bold uppercase text-[rgba(11,9,7,0.4)] block">
                                /actual-model-tool-calls
                              </span>
                              {item.result.actual_tool_calls && item.result.actual_tool_calls.length > 0 ? (
                                item.result.actual_tool_calls.map((call: any, idx: number) => (
                                  <div key={idx} className="font-mono text-[10px] bg-[#f7f7f5] p-2 rounded">
                                    <span className="font-bold text-[#ff272d]">{call.name}</span>
                                    <pre className="text-[9px] text-[rgba(11,9,7,0.6)] mt-1 max-h-24 overflow-auto">
                                      {JSON.stringify(call.args, null, 2)}
                                    </pre>
                                  </div>
                                ))
                              ) : (
                                <span className="text-[10px] italic text-neutral-400">No tools called</span>
                              )}
                            </div>
                          </div>

                          {/* Tool outputs trace */}
                          {item.tool_results && item.tool_results.length > 0 && (
                            <div className="space-y-2">
                              <span className="font-mono text-[9px] font-bold uppercase text-[rgba(11,9,7,0.4)] block">
                                /execution-trace-log
                              </span>
                              <div className="space-y-2">
                                {item.tool_results.map((tr, i) => (
                                  <div key={i} className="rounded-lg border border-[rgba(11,9,7,0.06)] bg-[#fefcf5] p-3 space-y-2">
                                    <div className="flex items-center justify-between font-mono text-[10px]">
                                      <span className="font-bold text-[#3c3a39] flex items-center gap-1">
                                        <Wrench className="size-3 text-[#ff7300]" />
                                        {tr.tool}
                                      </span>
                                      <span className="text-[8px] text-neutral-400">round {i+1}</span>
                                    </div>
                                    <div className="grid md:grid-cols-2 gap-3 text-[10px] font-mono">
                                      <div>
                                        <span className="text-[8px] text-[rgba(11,9,7,0.4)] uppercase">Arguments</span>
                                        <pre className="bg-[#f7f7f5] p-1.5 rounded mt-0.5 overflow-auto max-h-32">
                                          {JSON.stringify(tr.args, null, 2)}
                                        </pre>
                                      </div>
                                      <div>
                                        <span className="text-[8px] text-[rgba(11,9,7,0.4)] uppercase">Result</span>
                                        <pre className="bg-[#f7f7f5] p-1.5 rounded mt-0.5 overflow-auto max-h-32">
                                          {JSON.stringify(tr.result, null, 2)}
                                        </pre>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-xs text-neutral-500 font-mono">/select-a-run-file-from-the-list...</p>
        )}
      </section>
    </div>
  );
}

function AccuracyCard({ label, value }: { label: string; value: number }) {
  const percentage = Math.round(value * 100);
  return (
    <div className="rounded-xl border border-[rgba(11,9,7,0.06)] bg-[#fffcf6] p-3 text-center shadow-xs">
      <span className="block font-mono text-[8px] uppercase tracking-wider text-[rgba(11,9,7,0.4)]">
        {label}
      </span>
      <span className="block text-md font-bold mt-1 text-[#3c3a39]">
        {percentage}%
      </span>
      <div className="h-1 w-full bg-[#eaeae2] rounded-full overflow-hidden mt-2">
        <div 
          className="h-full bg-[#ff7300] rounded-full transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
