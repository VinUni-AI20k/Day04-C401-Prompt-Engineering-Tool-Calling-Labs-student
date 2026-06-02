"use client";

import {
  Bot,
  CheckCircle2,
  ChevronDown,
  Copy,
  Loader2,
  PanelRight,
  Send,
  ShieldAlert,
  Wrench,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { traces, type AgentTrace } from "@/lib/mock-traces";
import type { ChatMessage, SimulatedStep } from "@/lib/types";

type BackendTraceStep = Omit<SimulatedStep, "status"> & {
  status?: "success" | "failed" | "timeout";
};

type DiagnoseResponse = {
  summary: string;
  steps?: BackendTraceStep[];
};

const stepIcons = {
  thought: Bot,
  tool: Wrench,
  observation: CheckCircle2,
  final: CheckCircle2,
  error: ShieldAlert,
};

export function ChatPanelInteractive({
  activeSessionId,
  onTraceUpdate,
}: {
  activeSessionId: string;
  onTraceUpdate?: (trace: any) => void;
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isMockMode, setIsMockMode] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const currentSessionIdRef = useRef(activeSessionId);

  // Load initial session messages or restore from localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("gaptutor_messages_" + activeSessionId);
      if (saved) {
        try {
          const parsed = JSON.parse(saved) as ChatMessage[];
          if (parsed && parsed.length > 0) {
            setMessages(parsed);
            currentSessionIdRef.current = activeSessionId;
            return;
          }
        } catch (e) {
          console.error("Failed to parse saved messages", e);
        }
      }
    }

    let initialMsg: ChatMessage[] = [];
    if (activeSessionId === "session-cohort") {
      const trace = traces.find((t) => t.id === "success-cohort-diagnostic")!;
      initialMsg = [
        {
          id: "msg-user-1",
          role: "user",
          content: trace.query,
          timestamp: Date.now() - 1000 * 60 * 5,
        },
        {
          id: "msg-assistant-1",
          role: "assistant",
          content: trace.steps.find((s) => s.kind === "final")?.content ?? trace.summary,
          timestamp: Date.now() - 1000 * 60 * 4,
          thinkingSteps: trace.steps.map((s) => ({
            id: s.id,
            title: s.title,
            kind: s.kind as SimulatedStep["kind"],
            content: s.content,
            toolName: s.toolName,
            status: "completed",
            durationMs: s.durationMs,
          })),
        },
      ];
    } else if (activeSessionId === "session-student") {
      initialMsg = [
        {
          id: "msg-user-2",
          role: "user",
          content: "Hãy phân tích concept_mastery của học viên STU003 (Lê Minh C).",
          timestamp: Date.now() - 1000 * 60 * 30,
        },
        {
          id: "msg-assistant-2",
          role: "assistant",
          content: "Học viên Lê Minh C (STU003) thuộc nhóm 'Needs Foundation' với điểm trung bình concept là 34.2%. Yếu nhất ở Agentic Loops (25%) và Reasoning (30%). Cần được hỗ trợ 1-1 khẩn cấp.",
          timestamp: Date.now() - 1000 * 60 * 29,
          thinkingSteps: [
            {
              id: "stu-t-1",
              title: "Load student info",
              kind: "thought",
              content: "Đọc query và nhận dạng ID học viên STU003.",
              status: "completed",
            },
            {
              id: "stu-tool-1",
              title: "Fetch Student Details",
              kind: "tool",
              toolName: "get_student_by_id",
              content: "Tool lấy chi tiết học viên từ database.",
              status: "completed",
              durationMs: 45,
            },
          ],
        },
      ];
    } else if (activeSessionId === "session-security") {
      const trace = traces.find((t) => t.id === "security-blocked")!;
      initialMsg = [
        {
          id: "msg-user-3",
          role: "user",
          content: trace.query,
          timestamp: Date.now() - 1000 * 60 * 60,
        },
        {
          id: "msg-assistant-3",
          role: "assistant",
          content: trace.summary,
          timestamp: Date.now() - 1000 * 60 * 59,
          thinkingSteps: trace.steps.map((s) => ({
            id: s.id,
            title: s.title,
            kind: s.kind as SimulatedStep["kind"],
            content: s.content,
            toolName: s.toolName,
            status: "completed",
            durationMs: s.durationMs,
          })),
        },
      ];
    } else {
      initialMsg = [
        {
          id: "msg-welcome",
          role: "assistant",
          content: "Xin chào! Tôi là GapTutor AI Agent. Bạn hãy đặt câu hỏi để tôi chẩn đoán thông tin của cohort hoặc học viên nhé.",
          timestamp: Date.now(),
        }
      ];
    }
    setMessages(initialMsg);
    currentSessionIdRef.current = activeSessionId;
  }, [activeSessionId]);

  // Save messages to localStorage whenever they change, isolated by activeSessionId
  useEffect(() => {
    if (
      typeof window !== "undefined" &&
      messages.length > 0 &&
      currentSessionIdRef.current === activeSessionId
    ) {
      localStorage.setItem("gaptutor_messages_" + activeSessionId, JSON.stringify(messages));
    }
  }, [messages, activeSessionId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const runLocalTraceSimulation = (userText: string, assistantMsgId: string) => {
    let sourceTrace: AgentTrace = traces[0];
    if (userText.toLowerCase().includes("ignore") || userText.toLowerCase().includes("system prompt")) {
      sourceTrace = traces.find((trace) => trace.id === "security-blocked") || traces[1];
    } else if (userText.toLowerCase().includes("timeout") || userText.toLowerCase().includes("slow")) {
      sourceTrace = traces.find((trace) => trace.id === "timeout-fallback") || traces[2];
    }

    const allSteps = sourceTrace.steps.map((step) => ({
      id: step.id,
      title: step.title,
      kind: step.kind as SimulatedStep["kind"],
      content: step.content,
      toolName: step.toolName,
      status: "pending" as const,
      durationMs: step.durationMs,
      input: step.input,
      output: step.output,
      errorCode: step.errorCode,
    }));
    let stepIndex = 0;

    const runSimulation = () => {
      if (stepIndex < allSteps.length) {
        const stepToActivate = allSteps[stepIndex];
        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id !== assistantMsgId) return msg;
            const updatedSteps = [...(msg.thinkingSteps || [])];
            const stepCopy: SimulatedStep = {
              ...stepToActivate,
              status: stepToActivate.kind === "tool" ? "running" : "completed",
            };
            const existingIdx = updatedSteps.findIndex((step) => step.id === stepCopy.id);
            if (existingIdx >= 0) {
              updatedSteps[existingIdx] = stepCopy;
            } else {
              updatedSteps.push(stepCopy);
            }
            return { ...msg, thinkingSteps: updatedSteps };
          })
        );

        if (stepToActivate.kind === "tool") {
          setTimeout(() => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId
                  ? {
                      ...msg,
                      thinkingSteps: (msg.thinkingSteps || []).map((step) =>
                        step.id === stepToActivate.id ? { ...step, status: "completed" as const } : step
                      ),
                    }
                  : msg
              )
            );
            stepIndex++;
            setTimeout(runSimulation, 600);
          }, 800);
        } else {
          stepIndex++;
          setTimeout(runSimulation, 800);
        }
      } else {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  content: sourceTrace.steps.find((step) => step.kind === "final")?.content ?? sourceTrace.summary,
                  isSimulating: false,
                }
              : msg
          )
        );
        if (onTraceUpdate) {
          onTraceUpdate(sourceTrace);
        }
      }
    };

    setTimeout(runSimulation, 400);
  };

  const handleSend = async () => {
    if (!inputValue.trim() || isTyping) return;

    const userText = inputValue;
    setInputValue("");

    const userMessage: ChatMessage = {
      id: `msg-user-${Date.now()}`,
      role: "user",
      content: userText,
      timestamp: Date.now(),
    };
    const assistantMsgId = `msg-assistant-${Date.now()}`;
    const initialAssistantMsg: ChatMessage = {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      timestamp: Date.now(),
      thinkingSteps: [],
      isSimulating: true,
    };

    setMessages((prev) => [...prev, userMessage, initialAssistantMsg]);
    setIsTyping(true);

    if (isMockMode) {
      runLocalTraceSimulation(userText, assistantMsgId);
      setIsTyping(false);
      return;
    }

    try {
      const response = await fetch("/api/diagnose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: "session-03", query: userText }),
      });
      const data = await response.json() as DiagnoseResponse & {
        error_code?: string;
        message?: string;
        task_id?: string;
        telemetry?: {
          total_execution_time_ms?: number;
          prompt_tokens?: number;
          completion_tokens?: number;
          estimated_cost_usd?: number;
        };
      };

      if (!response.ok) {
        const message = data.message ?? "Không thể chạy chẩn đoán.";
        const code = data.error_code ?? "DIAGNOSE_ERROR";
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  content: message,
                  isSimulating: false,
                  thinkingSteps: [
                    {
                      id: `error-${Date.now()}`,
                      title: code,
                      kind: "error",
                      content: message,
                      status: "completed",
                      errorCode: code,
                    },
                  ],
                }
              : msg
          )
        );
        return;
      }

      const backendSteps: SimulatedStep[] = (data.steps ?? []).map((step) => ({
        id: step.id,
        title: step.title,
        kind: step.kind,
        content: step.content,
        toolName: step.toolName,
        status: mapBackendStepStatus(step.status),
        durationMs: step.durationMs,
        input: step.input,
        output: step.output,
        errorCode: step.errorCode,
      }));

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? {
                ...msg,
                content: data.summary,
                thinkingSteps: backendSteps,
                isSimulating: false,
              }
            : msg
        )
      );

      if (onTraceUpdate) {
        onTraceUpdate({
          id: data.task_id,
          query: userText,
          summary: data.summary,
          latencyMs: data.telemetry?.total_execution_time_ms ?? 100,
          promptTokens: data.telemetry?.prompt_tokens ?? 0,
          completionTokens: data.telemetry?.completion_tokens ?? 0,
          costUsd: data.telemetry?.estimated_cost_usd ?? 0.0,
          steps: data.steps ?? [],
        });
      }
    } catch {
      runLocalTraceSimulation(userText, assistantMsgId);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <section className="flex flex-col h-full rounded-2xl border border-[rgba(11,9,7,0.12)] bg-[#fffcf6] shadow-sm lg:min-h-0">
      <div className="flex items-center justify-between border-b border-[rgba(11,9,7,0.12)] px-5 py-4 bg-[#f7f7f5]/40">
        <div>
          <h2 className="text-sm font-bold text-[#3c3a39]">GapTutor AI Chat</h2>
          <p className="font-mono text-xs text-[#2677ff] font-semibold">
            /interactive-agent-diagnostics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsMockMode(!isMockMode)}
            className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 font-mono text-[10px] font-bold shadow-sm transition-all cursor-pointer ${
              isMockMode
                ? "border-amber-500/30 bg-amber-500/10 text-amber-600 hover:bg-amber-500/20"
                : "border-emerald-500/30 bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20"
            }`}
            type="button"
          >
            <span className={`size-1.5 rounded-full ${isMockMode ? "bg-amber-500 animate-pulse" : "bg-emerald-500 animate-pulse"}`} />
            {isMockMode ? "Sandbox Mock Mode" : "Live API Mode"}
          </button>
          <div className="flex items-center gap-2 rounded-full border border-[rgba(11,9,7,0.12)] bg-[#fefcf5] px-3 py-1.5 font-mono text-[10px] text-[rgba(11,9,7,0.5)] font-semibold shadow-sm">
            <PanelRight className="size-3.5 text-[#2677ff]" />
            /interactive
          </div>
        </div>
      </div>

      <div className="flex-1 space-y-5 overflow-auto p-5">
        {messages.map((msg) => (
          <div key={msg.id} className="space-y-4">
            {msg.role === "user" ? (
              <div className="flex justify-end">
                <div className="max-w-[min(80%,680px)] rounded-2xl rounded-br-none border border-transparent bg-[#3c3a39] px-4 py-3 text-sm leading-6 text-[#fefcf5] shadow-sm">
                  {msg.content}
                </div>
              </div>
            ) : (
              <div className="flex items-start gap-3">
                <div className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-[#f7f7f5] border border-[rgba(11,9,7,0.1)]">
                  <Bot className="size-4 text-[rgba(11,9,7,0.7)]" />
                </div>
                <div className="min-w-0 flex-1 space-y-4">
                  {msg.thinkingSteps && msg.thinkingSteps.length > 0 && (
                    <ThinkingBlock steps={msg.thinkingSteps} />
                  )}
                  {msg.isSimulating ? (
                    <div className="flex items-center gap-2 rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#f7f7f5] px-4 py-3 text-sm text-[rgba(11,9,7,0.6)]">
                      <Loader2 className="size-4 animate-spin text-[#ff272d]" />
                      <span>Thinking & evaluating cohort telemetry...</span>
                    </div>
                  ) : (
                    msg.content && (
                      <div className="max-w-3xl rounded-2xl rounded-tl-none border border-[rgba(11,9,7,0.08)] bg-[#f7f7f5] px-4 py-3 text-sm leading-6 text-[#3c3a39] prose max-w-none">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
        {isTyping && messages[messages.length - 1]?.role === "user" && (
          <div className="flex items-start gap-3">
            <div className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-[#f7f7f5] border border-[rgba(11,9,7,0.1)]">
              <Bot className="size-4 text-[rgba(11,9,7,0.7)]" />
            </div>
            <div className="flex items-center gap-2 rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#f7f7f5] px-4 py-3 text-sm text-[rgba(11,9,7,0.6)]">
              <Loader2 className="size-4 animate-spin text-[#ff272d]" />
              <span>Initiating core LLM agent engine...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-[rgba(11,9,7,0.1)] p-4 bg-[#fffcf6]">
        <div className="flex items-end gap-3 rounded-2xl border border-[rgba(11,9,7,0.1)] bg-[#fefcf5] p-3 focus-within:border-[rgba(11,9,7,0.25)] transition-colors">
          <textarea
            className="min-h-12 flex-1 resize-none bg-transparent text-sm leading-6 text-[#3c3a39] outline-none placeholder:text-[rgba(11,9,7,0.4)]"
            placeholder="Type a query or trigger fallback/security tests..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isTyping}
          />
          <button
            aria-label="Send message"
            className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-[#3c3a39] text-[#fefcf5] hover:opacity-90 transition-opacity disabled:opacity-40"
            onClick={handleSend}
            disabled={!inputValue.trim() || isTyping}
            type="button"
          >
            <Send className="size-4" />
          </button>
        </div>
      </div>
    </section>
  );
}

function mapBackendStepStatus(status: BackendTraceStep["status"]): SimulatedStep["status"] {
  return status === "failed" || status === "timeout" ? "completed" : "completed";
}

function ThinkingBlock({ steps }: { steps: SimulatedStep[] }) {
  const [open, setOpen] = useState(true);

  return (
    <div className="max-w-4xl overflow-hidden rounded-2xl border border-[rgba(11,9,7,0.1)] bg-[#fffcf6]">
      <button
        aria-expanded={open}
        className="flex min-h-12 w-full items-center justify-between gap-3 px-4 py-3 text-left text-sm text-[#3c3a39] transition-colors hover:bg-[rgba(11,9,7,0.02)]"
        onClick={() => setOpen((current) => !current)}
        type="button"
      >
        <span className="flex items-center gap-2">
          <Bot className="size-4 text-[rgba(11,9,7,0.5)]" />
          <span className="font-mono text-xs text-[rgba(11,9,7,0.6)]">/agent-reasoning-trail</span>
          <span className="rounded-full border border-[rgba(11,9,7,0.1)] bg-[#f7f7f5] px-2 py-0.5 text-[10px] text-[rgba(11,9,7,0.5)]">
            {steps.length} blocks
          </span>
        </span>
        <ChevronDown
          className={`size-4 text-[rgba(11,9,7,0.5)] transition-transform ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>
      {open && (
        <div className="space-y-3 border-t border-[rgba(11,9,7,0.1)] p-3 bg-[#fefcf5]">
          {steps.map((step) =>
            step.kind === "tool" ? (
              <InlineToolCallBlock key={step.id} step={step} />
            ) : (
              <InlineThinkingLine key={step.id} step={step} />
            )
          )}
        </div>
      )}
    </div>
  );
}

function InlineThinkingLine({ step }: { step: SimulatedStep }) {
  const Icon = stepIcons[step.kind] || Bot;

  return (
    <div className="flex gap-3 rounded-xl border border-[rgba(11,9,7,0.06)] bg-[#fffcf6] p-3">
      <Icon className="mt-0.5 size-4 shrink-0 text-[rgba(11,9,7,0.4)]" />
      <div className="min-w-0">
        <div className="mb-1 flex flex-wrap items-center gap-2">
          <span className="font-mono text-[10px] uppercase tracking-wider text-[rgba(11,9,7,0.4)]">
            {step.kind}
          </span>
          <span className="text-sm font-medium text-[#3c3a39]">
            {step.title}
          </span>
        </div>
        <div className="text-sm leading-6 text-[rgba(11,9,7,0.6)] prose max-w-none">
          <ReactMarkdown>{step.content}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

function InlineToolCallBlock({ step }: { step: SimulatedStep }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="overflow-hidden rounded-xl border border-[rgba(11,9,7,0.08)] bg-[#fffcf6] shadow-sm">
      <button
        aria-expanded={open}
        className="flex min-h-12 w-full items-center justify-between gap-3 px-3 py-2 text-left transition-colors hover:bg-[rgba(11,9,7,0.02)]"
        onClick={() => setOpen((current) => !current)}
        type="button"
      >
        <span className="flex min-w-0 items-center gap-3">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#f7f7f5]">
            {step.status === "running" ? (
              <Loader2 className="size-4 animate-spin text-[#ff7300]" />
            ) : (
              <Wrench className="size-4 text-[rgba(11,9,7,0.6)]" />
            )}
          </span>
          <span className="min-w-0">
            <span className="block truncate text-sm font-medium text-[#3c3a39]">
              {step.toolName ?? step.title}
            </span>
            <span className="block truncate text-xs text-[rgba(11,9,7,0.5)]">
              {step.status === "running" ? "Executing..." : step.content}
            </span>
          </span>
        </span>
        <span className="flex shrink-0 items-center gap-2">
          <span
            className={`rounded-full border px-2 py-0.5 text-[10px] capitalize ${
              step.status === "running"
                ? "border-[#ff7300]/30 bg-[#ff7300]/10 text-[#ff7300]"
                : "border-[#2677ff]/30 bg-[#2677ff]/10 text-[#2677ff]"
            }`}
          >
            {step.status}
          </span>
          <ChevronDown
            className={`size-4 text-[rgba(11,9,7,0.4)] transition-transform ${
              open ? "rotate-180" : ""
            }`}
          />
        </span>
      </button>
      {open && (
        <div className="grid gap-3 border-t border-[rgba(11,9,7,0.1)] p-3 md:grid-cols-2 bg-[#fefcf5]">
          {step.input !== undefined && (
            <JsonBlock label="Parameters" value={step.input} />
          )}
          {step.output !== undefined && (
            <JsonBlock label="Observation" value={step.output} />
          )}
        </div>
      )}
    </div>
  );
}

function JsonBlock({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="overflow-hidden rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#fffcf6]">
      <div className="flex items-center justify-between border-b border-[rgba(11,9,7,0.1)] px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-[rgba(11,9,7,0.5)] bg-[#f7f7f5]">
        {label}
        <Copy className="size-3.5 text-[rgba(11,9,7,0.4)]" />
      </div>
      <pre className="max-h-72 overflow-auto p-3 text-xs leading-5 text-[rgba(11,9,7,0.7)]">
        <code>{JSON.stringify(value, null, 2)}</code>
      </pre>
    </div>
  );
}
