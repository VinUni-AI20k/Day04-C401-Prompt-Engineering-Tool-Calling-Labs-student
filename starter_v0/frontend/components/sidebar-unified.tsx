"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MessageSquare,
  GraduationCap,
  Users,
  FileText,
  PanelLeftClose,
  PanelLeft,
  PlusCircle,
  MessageCircle,
  Settings,
  HelpCircle,
  Plus,
  Activity,
} from "lucide-react";
import type { ChatSession } from "@/lib/types";

const mockSessions: ChatSession[] = [
  {
    id: "session-cohort",
    title: "Cohort Diagnostics",
    lastMessage: "Chẩn đoán cohort RAG...",
    timestamp: Date.now() - 1000 * 60 * 5,
    messageCount: 3,
  },
  {
    id: "session-student",
    title: "Student Analysis",
    lastMessage: "Phân tích chỉ số STU003...",
    timestamp: Date.now() - 1000 * 60 * 30,
    messageCount: 2,
  },
  {
    id: "session-security",
    title: "Security Test",
    lastMessage: "Ignore instructions...",
    timestamp: Date.now() - 1000 * 60 * 60,
    messageCount: 1,
  },
];

export function SidebarUnified({
  activeSessionId,
  onSelectSession,
  onNewChat,
  isCollapsed: controlledIsCollapsed,
  onToggleCollapse: controlledOnToggleCollapse,
}: {
  activeSessionId?: string;
  onSelectSession?: (id: string) => void;
  onNewChat?: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}) {
  const pathname = usePathname() || "";
  const [localIsCollapsed, setLocalIsCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState<string>("chat");
  const [sessions, setSessions] = useState<ChatSession[]>(mockSessions);

  const isCollapsed = controlledIsCollapsed !== undefined ? controlledIsCollapsed : localIsCollapsed;
  const toggleCollapse = controlledOnToggleCollapse || (() => setLocalIsCollapsed(!localIsCollapsed));

  // Dynamic session tracking
  useEffect(() => {
    if (activeSessionId && !sessions.some((s) => s.id === activeSessionId)) {
      const newSession: ChatSession = {
        id: activeSessionId,
        title: activeSessionId.startsWith("session-new") ? "New Diagnostic Chat" : "Dynamic Session",
        lastMessage: "Chuyện trò mới chưa lưu...",
        timestamp: Date.now(),
        messageCount: 0,
      };
      setSessions((prev) => [...prev, newSession]);
    }
  }, [activeSessionId, sessions]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const updateActiveTab = () => {
        const path = window.location.pathname;
        if (path.includes("/app")) {
          setActiveTab("chat");
        } else if (path.includes("/students")) {
          const params = new URLSearchParams(window.location.search);
          const tab = params.get("tab");
          if (tab === "version-logs") {
            setActiveTab("version-logs");
          } else if (tab === "eval-cases") {
            setActiveTab("eval-cases");
          } else if (tab === "prompt-tools") {
            setActiveTab("prompt-tools");
          } else if (tab === "runs") {
            setActiveTab("runs");
          } else {
            setActiveTab("version-logs");
          }
        }
      };

      updateActiveTab();
      // Also update when url changes
      window.addEventListener("popstate", updateActiveTab);
      return () => window.removeEventListener("popstate", updateActiveTab);
    }
  }, [pathname]);

  const navItems = [
    {
      id: "chat",
      label: "AI Chat Assistant",
      href: "/u/0/app",
      icon: MessageSquare,
      isActive: activeTab === "chat",
    },
    {
      id: "version-logs",
      label: "Version Logs (CSV)",
      href: "/u/0/students?tab=version-logs",
      icon: GraduationCap,
      isActive: activeTab === "version-logs",
    },
    {
      id: "eval-cases",
      label: "Evaluation Cases",
      href: "/u/0/students?tab=eval-cases",
      icon: Users,
      isActive: activeTab === "eval-cases",
    },
    {
      id: "prompt-tools",
      label: "Prompt & Tools Config",
      href: "/u/0/students?tab=prompt-tools",
      icon: FileText,
      isActive: activeTab === "prompt-tools",
    },
    {
      id: "runs",
      label: "Evaluation Runs",
      href: "/u/0/students?tab=runs",
      icon: Activity,
      isActive: activeTab === "runs",
    },
  ];

  return (
    <aside
      className="flex flex-col rounded-2xl border border-[rgba(11,9,7,0.12)] bg-[#fffcf6] shadow-sm h-full w-full lg:min-h-0"
    >
      {/* Toggler & Hamburger */}
      <div className="flex items-center justify-between p-3 border-b border-[rgba(11,9,7,0.08)] bg-[#f7f7f5]/30">
        {!isCollapsed && (
          <span className="font-mono text-[10px] font-bold text-[#ff7300] tracking-wider uppercase ml-1">
            /gaptutor
          </span>
        )}
        <button
          onClick={toggleCollapse}
          className={`flex size-8 items-center justify-center rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#fefcf5] text-[#3c3a39] hover:bg-[#eaeae2] transition-colors ${
            isCollapsed ? "mx-auto" : ""
          }`}
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          type="button"
        >
          {isCollapsed ? <PanelLeft className="size-4" /> : <PanelLeftClose className="size-4" />}
        </button>
      </div>

      {/* Main Navigation links */}
      <div className="p-2 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.id}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl border text-xs font-semibold transition-all ${
                item.isActive
                  ? "border-[#3c3a39] bg-[#3c3a39] text-[#fefcf5] shadow-sm"
                  : "border-transparent text-[rgba(11,9,7,0.6)] hover:text-[#3c3a39] hover:bg-[#eaeae2]/30"
              } ${isCollapsed ? "justify-center px-0" : ""}`}
              title={isCollapsed ? item.label : ""}
            >
              <Icon className={`size-4 ${item.isActive ? "text-[#79deeb]" : ""}`} />
              {!isCollapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </div>

      {/* Divider */}
      <div className="border-t border-[rgba(11,9,7,0.08)] mx-2 my-1" />

      {/* Recent Sessions list */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className={`px-3 py-2 flex items-center justify-between ${isCollapsed ? "justify-center" : ""}`}>
          {!isCollapsed && (
            <span className="font-mono text-[9px] font-bold uppercase tracking-wider text-[rgba(11,9,7,0.4)]">
              /recent-sessions
            </span>
          )}
          {onNewChat && (
            <button
              onClick={onNewChat}
              className="flex items-center justify-center size-5 rounded-md border border-[rgba(11,9,7,0.15)] bg-[#fefcf5] hover:bg-[#eaeae2] text-[#3c3a39] transition-colors"
              title="New Chat Session"
            >
              <Plus className="size-3" />
            </button>
          )}
        </div>

        <div className="flex-1 overflow-auto px-2 pb-2 space-y-1">
          {sessions.map((session) => {
            const isSelected = activeSessionId === session.id;
            return (
              <button
                key={session.id}
                className={`w-full flex items-center gap-2.5 rounded-xl border p-2 text-left transition-all ${
                  isCollapsed ? "justify-center px-0" : ""
                } ${
                  isSelected
                    ? "border-[#3c3a39]/30 bg-[#eaeae2]/30 shadow-xs"
                    : "border-transparent hover:bg-[#eaeae2]/20"
                }`}
                onClick={() => onSelectSession && onSelectSession(session.id)}
                title={isCollapsed ? session.title : ""}
                type="button"
              >
                <div
                  className={`flex size-7 shrink-0 items-center justify-center rounded-lg border ${
                    isSelected
                      ? "bg-[#3c3a39] text-[#fefcf5] border-[#3c3a39]"
                      : "bg-[#fefcf5] border-[rgba(11,9,7,0.08)] text-[rgba(11,9,7,0.4)]"
                  }`}
                >
                  <MessageCircle className="size-3.5" />
                </div>
                {!isCollapsed && (
                  <div className="min-w-0 flex-1">
                    <p className="text-[11px] font-bold text-[#3c3a39] truncate">
                      {session.title}
                    </p>
                    <p className="text-[9px] text-[rgba(11,9,7,0.4)] truncate mt-0.5">
                      {session.lastMessage}
                    </p>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Footer Settings */}
      <div className={`p-2 border-t border-[rgba(11,9,7,0.08)] bg-[#f7f7f5]/20 ${isCollapsed ? "flex flex-col items-center gap-1.5" : "flex items-center justify-between px-3"}`}>
        <div className="flex items-center gap-2">
          <div className="size-6 rounded-full bg-[#eaeae2] border border-[rgba(11,9,7,0.1)] flex items-center justify-center text-[10px] font-bold text-[#3c3a39]">
            M
          </div>
          {!isCollapsed && <span className="text-[10px] font-bold text-[#3c3a39]">Mentor Pro</span>}
        </div>
        <div className="flex gap-1.5">
          <button className="text-[rgba(11,9,7,0.4)] hover:text-[#3c3a39]" title="Settings">
            <Settings className="size-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}
