"use client";

import { MessageSquarePlus, MessageCircle } from "lucide-react";
import type { ChatSession } from "@/lib/types";

const mockSessions: ChatSession[] = [
  {
    id: "session-cohort",
    title: "Cohort Diagnostics",
    lastMessage: "Chẩn đoán cohort RAG và đề xuất hỗ trợ...",
    timestamp: Date.now() - 1000 * 60 * 5,
    messageCount: 3,
  },
  {
    id: "session-student",
    title: "Student Analysis",
    lastMessage: "Phân tích chỉ số học viên STU003...",
    timestamp: Date.now() - 1000 * 60 * 30,
    messageCount: 2,
  },
  {
    id: "session-security",
    title: "Security Test",
    lastMessage: "Ignore previous instructions...",
    timestamp: Date.now() - 1000 * 60 * 60,
    messageCount: 1,
  },
];

import Link from "next/link";
import { MessageSquare, GraduationCap } from "lucide-react";

export function SessionSidebar({
  activeSessionId,
  onSelectSession,
  onNewChat,
}: {
  activeSessionId: string;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
}) {
  return (
    <aside className="flex flex-col rounded-2xl border border-[rgba(11,9,7,0.12)] bg-[#fffcf6] shadow-sm lg:min-h-0">
      {/* Decoupled Page Switcher */}
      <div className="p-2.5 border-b border-[rgba(11,9,7,0.12)] bg-[#fffcf6] rounded-t-2xl">
        <div className="grid grid-cols-2 gap-1 rounded-xl bg-[#fefcf5] border border-[rgba(11,9,7,0.06)] p-0.5 shadow-inner">
          <Link
            href="/u/0/app"
            className="flex items-center justify-center gap-1.5 py-1.5 text-xs font-semibold rounded-lg transition-all bg-[#3c3a39] text-[#fefcf5] shadow-sm"
          >
            <MessageSquare className="size-3.5" />
            <span>Chat App</span>
          </Link>
          <Link
            href="/u/0/students"
            className="flex items-center justify-center gap-1.5 py-1.5 text-xs font-semibold rounded-lg transition-all text-[rgba(11,9,7,0.5)] hover:text-[#3c3a39] hover:bg-[#eaeae2]/30"
          >
            <GraduationCap className="size-3.5" />
            <span>Students</span>
          </Link>
        </div>
      </div>

      <div className="flex items-center justify-between border-b border-[rgba(11,9,7,0.08)] px-4 py-4 bg-[#f7f7f5]/20">
        <div>
          <h2 className="text-sm font-bold text-[#3c3a39]">Sessions</h2>
          <p className="mt-0.5 font-mono text-[11px] text-[#817fff] font-medium">/chat-history</p>
        </div>
        <button
          aria-label="New chat"
          className="flex size-8 items-center justify-center rounded-xl border border-[rgba(11,9,7,0.15)] bg-[#fefcf5] text-[#3c3a39] shadow-sm transition-all hover:bg-[#eaeae2]"
          onClick={onNewChat}
          type="button"
        >
          <MessageSquarePlus className="size-4" />
        </button>
      </div>

      <div className="flex-1 space-y-1.5 overflow-auto p-3">
        {mockSessions.map((session) => (
          <button
            className={`group flex w-full items-start gap-3 rounded-xl border p-3 text-left transition-all ${
              activeSessionId === session.id
                ? "border-[#3c3a39] bg-[#eaeae2]/40 shadow-sm"
                : "border-[rgba(11,9,7,0.06)] bg-[#fffcf6] hover:border-[rgba(11,9,7,0.18)] hover:bg-[#f7f7f5]"
            }`}
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            type="button"
          >
            <div
              className={`mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-xl ${
                activeSessionId === session.id
                  ? "bg-[#3c3a39] text-[#fefcf5] shadow-sm"
                  : "bg-[#fefcf5] border border-[rgba(11,9,7,0.08)] text-[rgba(11,9,7,0.5)] group-hover:text-[#3c3a39]"
              }`}
            >
              <MessageCircle className="size-3.5" />
            </div>
            <div className="min-w-0 flex-1">
              <p
                className={`truncate text-sm font-semibold ${
                  activeSessionId === session.id ? "text-[#3c3a39]" : "text-[rgba(11,9,7,0.85)]"
                }`}
              >
                {session.title}
              </p>
              <p className="mt-1 line-clamp-1 text-[11px] leading-4 text-[rgba(11,9,7,0.65)] font-medium">
                {session.lastMessage}
              </p>
              <div className="mt-1.5 flex items-center gap-2">
                <span className="text-[10px] text-[rgba(11,9,7,0.45)]">
                  {formatTimeAgo(session.timestamp)}
                </span>
                <span className={`rounded-full border px-1.5 py-px text-[9px] font-medium bg-[#fefcf5] ${
                  activeSessionId === session.id ? "border-[#3c3a39]/30 text-[#3c3a39]" : "border-[rgba(11,9,7,0.1)] text-[rgba(11,9,7,0.5)]"
                }`}>
                  {session.messageCount} msgs
                </span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </aside>
  );
}

function formatTimeAgo(timestamp: number): string {
  const diff = Date.now() - timestamp;
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}
