"use client";

import { useEffect, useState } from "react";
import {
  Wrench,
  CheckCircle2,
  ShieldAlert,
  Bot,
  Clock3,
  MessageSquare,
  Activity,
  Cpu,
  ChevronRight,
} from "lucide-react";
import { traces, type AgentTrace } from "@/lib/mock-traces";

const stepIcons = {
  thought: Bot,
  tool: Wrench,
  observation: CheckCircle2,
  final: CheckCircle2,
  error: ShieldAlert,
};

export function TraceRailInteractive({
  activeSessionId,
  customTrace,
}: {
  activeSessionId: string;
  customTrace?: any;
}) {
  const [liveTranscript, setLiveTranscript] = useState<any>(null);

  // Listen for the latest live transcript from chat.py in real-time via Server-Sent Events (SSE)
  useEffect(() => {
    if (typeof window === "undefined") return;

    let eventSource: EventSource | null = null;
    try {
      const url = activeSessionId 
        ? `/api/transcripts/stream?session_id=${activeSessionId}`
        : "/api/transcripts/stream";
      eventSource = new EventSource(url);
      eventSource.onmessage = (event) => {
        try {
          const json = JSON.parse(event.data);
          if (json && !json.error) {
            setLiveTranscript(json);
          }
        } catch (e) {
          // ignore
        }
      };
    } catch (e) {
      // ignore
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [activeSessionId]);

  // Retrieve current active trace details (fallback if no live transcript is running)
  const activeTrace: AgentTrace = (() => {
    if (customTrace) {
      return customTrace;
    }
    if (activeSessionId === "session-security") {
      return traces.find((t) => t.id === "security-blocked") || traces[1];
    }
    if (activeSessionId === "session-student") {
      return traces.find((t) => t.id === "timeout-fallback") || traces[2];
    }
    return traces[0];
  })();

  const latestTurn = liveTranscript?.turns?.[liveTranscript.turns.length - 1];

  // Render live transcript telemetry if active
  if (liveTranscript) {
    return (
      <aside className="flex flex-col rounded-2xl border border-[rgba(11,9,7,0.12)] bg-[#fffcf6] p-4 shadow-sm h-full w-full lg:min-h-0 overflow-auto">
        {/* Header */}
        <div className="mb-4 flex items-start justify-between gap-3 border-b border-[rgba(11,9,7,0.08)] pb-3">
          <div className="min-w-0">
            <h2 className="text-sm font-bold text-[#3c3a39] flex items-center gap-1.5">
              <Activity className="size-4 text-emerald-500 animate-pulse" />
              Live Transcript Telemetry
            </h2>
            <p className="mt-1 font-mono text-[9px] text-[rgba(11,9,7,0.5)] truncate" title={liveTranscript.transcript_id}>
              /{liveTranscript.transcript_id}
            </p>
          </div>
          <Clock3 className="size-4 text-emerald-500 animate-spin shrink-0" />
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-4 gap-2 mb-4">
          <Metric label="Provider" value={liveTranscript.provider || "unknown"} />
          <Metric label="Model" value={liveTranscript.model ? liveTranscript.model.split("/").pop() : "unknown"} />
          <Metric label="Turns" value={String(liveTranscript.turns?.length || 0)} />
          <Metric label="Version" value={liveTranscript.version || "v3"} />
        </div>

        {/* Current Turn Summary */}
        <div className="rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-3 mb-4 space-y-2">
          <div className="flex justify-between items-center">
            <p className="font-mono text-[9px] uppercase tracking-wider text-[#ff7300] font-bold">
              /current-turn-status
            </p>
            {latestTurn && (
              <span className={`rounded-full px-2 py-0.5 text-[8px] font-mono uppercase font-bold border ${
                latestTurn.status === "answered"
                  ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-600"
                  : latestTurn.status === "waiting_for_user"
                  ? "border-amber-500/20 bg-amber-500/10 text-amber-600 animate-pulse"
                  : "border-blue-500/20 bg-blue-500/10 text-blue-600"
              }`}>
                {latestTurn.status}
              </span>
            )}
          </div>
          {latestTurn ? (
            <div>
              <p className="text-xs font-semibold text-[#3c3a39] line-clamp-2">
                User: "{latestTurn.user}"
              </p>
              {latestTurn.ended_at && (
                <p className="text-[8px] font-mono text-neutral-400 mt-1">
                  Duration: {latestTurn.started_at.split("T")[1]} → {latestTurn.ended_at.split("T")[1]}
                </p>
              )}
            </div>
          ) : (
            <p className="text-xs text-neutral-400 italic">No turns active in this session</p>
          )}
        </div>

        {/* Live execution steps */}
        <div className="space-y-2.5">
          <p className="font-mono text-[9px] uppercase tracking-wider text-[#2677ff] font-bold">
            /live-execution-steps ({latestTurn?.tool_events?.length || 0} events)
          </p>
          {latestTurn?.tool_events && latestTurn.tool_events.length > 0 ? (
            latestTurn.tool_events.map((event: any, index: number) => (
              <LiveStep key={index} index={index + 1} event={event} />
            ))
          ) : (
            <div className="text-center rounded-xl border border-dashed border-[rgba(11,9,7,0.1)] p-6 text-xs text-neutral-400 font-mono">
              /awaiting-agent-action...
            </div>
          )}
        </div>
      </aside>
    );
  }

  // Fallback to static mock traces (original behavior)
  return (
    <aside className="flex flex-col rounded-2xl border border-[rgba(11,9,7,0.12)] bg-[#fffcf6] p-4 shadow-sm h-full w-full lg:min-h-0 overflow-auto">
      <div className="mb-4 flex items-start justify-between gap-3 border-b border-[rgba(11,9,7,0.08)] pb-3">
        <div>
          <h2 className="text-sm font-bold text-[#3c3a39]">Trace telemetry</h2>
          <p className="mt-1 font-mono text-[10px] text-[rgba(11,9,7,0.5)]">
            /langsmith-run-details
          </p>
        </div>
        <Clock3 className="size-4 text-[rgba(11,9,7,0.4)]" />
      </div>

      <div className="grid grid-cols-4 gap-2 mb-4">
        <Metric label="Latency" value={`${activeTrace.latencyMs}ms`} warning={activeTrace.latencyMs > 5000} />
        <Metric label="Prompt" value={String(activeTrace.promptTokens)} />
        <Metric label="Output" value={String(activeTrace.completionTokens)} />
        <Metric label="Cost" value={activeTrace.costUsd !== undefined ? `$${activeTrace.costUsd.toFixed(6)}` : "$0.000000"} />
      </div>

      <div className="rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-3 mb-4">
        <p className="font-mono text-[10px] uppercase tracking-wider text-[#817fff] font-bold">
          /telemetry-summary
        </p>
        <p className="mt-2 text-sm leading-6 text-[#3c3a39] font-medium">{activeTrace.summary}</p>
      </div>

      <div className="space-y-2.5">
        <p className="font-mono text-[10px] uppercase tracking-wider text-[#ff7300] font-bold">
          /mini-trace-steps
        </p>
        {activeTrace.steps.map((step, index) => (
          <div key={step.id} className="rounded-xl border border-[rgba(11,9,7,0.06)] bg-[#fefcf5] p-3 shadow-sm">
            <div className="flex items-start gap-3">
              <div className="flex size-7 shrink-0 items-center justify-center rounded-full border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] text-xs text-[#3c3a39] font-mono">
                {index + 1}
              </div>
              <div className="min-w-0 flex-1">
                <div className="mb-1 flex items-center gap-2">
                  <Wrench className="size-3.5 text-[rgba(11,9,7,0.4)]" />
                  <p className="truncate text-sm font-semibold text-[#3c3a39]">{step.title}</p>
                </div>
                <p className="line-clamp-2 text-xs leading-5 text-[rgba(11,9,7,0.5)]">{step.content}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}

function Metric({
  label,
  value,
  warning = false,
}: {
  label: string;
  value: string;
  warning?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border p-2.5 bg-[#fefcf5] min-w-0 ${
        warning ? "border-[#ff272d]/30 bg-[#ff272d]/5 text-[#ff272d]" : "border-[rgba(11,9,7,0.06)]"
      }`}
    >
      <p className="font-mono text-[8px] uppercase tracking-wider text-[rgba(11,9,7,0.4)] truncate">/{label.toLowerCase()}</p>
      <p className={`mt-1 text-[11px] font-bold truncate ${warning ? "text-[#ff272d]" : "text-[#3c3a39]"}`}>{value}</p>
    </div>
  );
}

function LiveStep({ event, index }: { event: any; index: number }) {
  const [open, setOpen] = useState(false);
  const hasError = event.result && typeof event.result === "object" && event.result.error;

  return (
    <div className="rounded-xl border border-[rgba(11,9,7,0.06)] bg-[#fefcf5] shadow-xs overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-start gap-3 p-3 text-left hover:bg-[rgba(11,9,7,0.01)] transition-colors"
        type="button"
      >
        <div className="flex size-7 shrink-0 items-center justify-center rounded-full border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] text-xs text-[#3c3a39] font-mono">
          {index}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            {hasError ? (
              <ShieldAlert className="size-3.5 text-red-500 shrink-0" />
            ) : (
              <Wrench className="size-3.5 text-[#2677ff] shrink-0" />
            )}
            <p className="truncate text-xs font-bold font-mono text-[#3c3a39]">
              {event.tool}
            </p>
          </div>
          <p className="text-[10px] text-neutral-400 mt-0.5 truncate font-mono">
            {JSON.stringify(event.args)}
          </p>
        </div>
        <ChevronRight className={`size-3.5 text-neutral-400 shrink-0 mt-1 transition-transform ${open ? "rotate-90" : ""}`} />
      </button>

      {open && (
        <div className="border-t border-[rgba(11,9,7,0.06)] p-3 bg-[#f7f7f5]/30 space-y-2 text-[10px] font-mono overflow-x-auto">
          <div>
            <span className="text-[8px] text-neutral-400 uppercase">Arguments</span>
            <pre className="bg-[#fefcf5] p-2 rounded border border-[rgba(11,9,7,0.04)] overflow-auto max-h-32 mt-0.5">
              {JSON.stringify(event.args, null, 2)}
            </pre>
          </div>
          <div>
            <span className="text-[8px] text-neutral-400 uppercase">Result / Observation</span>
            <pre className={`p-2 rounded border overflow-auto max-h-48 mt-0.5 ${
              hasError ? "bg-red-50/50 border-red-200/50 text-red-700" : "bg-[#fefcf5] border-[rgba(11,9,7,0.04)]"
            }`}>
              {JSON.stringify(event.result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
