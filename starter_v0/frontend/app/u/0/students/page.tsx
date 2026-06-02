"use client";

import { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { MessageSquare } from "lucide-react";
import { SidebarUnified } from "@/components/sidebar-unified";
import { VersionLogViewer } from "@/components/version-log-viewer";
import { EvalCasesViewer } from "@/components/eval-cases-viewer";
import { PromptToolsViewer } from "@/components/prompt-tools-viewer";
import { RunsViewer } from "@/components/runs-viewer";

export function StudentsPageContent() {
  const searchParams = useSearchParams();
  const [tab, setTab] = useState<string>("version-logs");
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(280);
  const [isResizingSidebar, setIsResizingSidebar] = useState(false);

  const startResizeSidebar = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizingSidebar(true);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isResizingSidebar) {
        const newWidth = Math.max(180, Math.min(450, e.clientX - 16));
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizingSidebar(false);
    };

    if (isResizingSidebar) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizingSidebar]);

  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (tabParam === "version-logs") {
      setTab("version-logs");
    } else if (tabParam === "eval-cases") {
      setTab("eval-cases");
    } else if (tabParam === "prompt-tools") {
      setTab("prompt-tools");
    } else if (tabParam === "runs") {
      setTab("runs");
    } else {
      setTab("version-logs");
    }
  }, [searchParams]);

  const renderActiveView = () => {
    switch (tab) {
      case "version-logs":
        return <VersionLogViewer />;
      case "eval-cases":
        return <EvalCasesViewer />;
      case "prompt-tools":
        return <PromptToolsViewer />;
      case "runs":
        return <RunsViewer />;
      default:
        return <VersionLogViewer />;
    }
  };

  const getTitle = () => {
    switch (tab) {
      case "version-logs":
        return "Version Optimization Logs (CSV)";
      case "eval-cases":
        return "Evaluation Datasets Cases (JSON)";
      case "prompt-tools":
        return "System Prompt & Tools Configuration";
      case "runs":
        return "Model Test Runs Execution Reports";
      default:
        return "Optimization & Evaluation Terminal";
    }
  };

  return (
    <main
      className={`mx-auto flex min-h-dvh w-full max-w-[1600px] flex-col gap-4 px-4 py-4 lg:h-dvh lg:overflow-hidden bg-[#f2efe4] ${
        isResizingSidebar ? "select-none" : ""
      }`}
    >
      {/* Header */}
      <header className="flex items-center justify-between rounded-2xl border border-transparent bg-[#3c3a39] px-6 py-4 shadow-md">
        <div>
          <p className="font-mono text-xs font-semibold uppercase tracking-[0.22em] text-[#ff7300]">
            /research-agent-lab-terminal
          </p>
          <h1 className="mt-1 text-xl font-bold tracking-tight text-[#fefcf5] md:text-2xl">
            {getTitle()}
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/u/0/app"
            className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 font-mono text-xs text-[#eaeae2] hover:bg-white/10 hover:text-white transition-all shadow-sm"
          >
            <MessageSquare className="size-4 text-[#79deeb]" />
            /back-to-chat
          </Link>
        </div>
      </header>

      {/* Main Collapsible Layout */}
      <section className="flex min-h-0 flex-1 gap-1 transition-all duration-300">
        {/* COLUMN 1: COLLAPSIBLE UNIFIED SIDEBAR */}
        <div style={{ width: isCollapsed ? 72 : sidebarWidth }} className="flex shrink-0 h-full">
          <SidebarUnified
            isCollapsed={isCollapsed}
            onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
            onNewChat={() => {
              window.location.href = "/u/0/app";
            }}
          />
        </div>

        {/* Resizer for Left Sidebar */}
        {!isCollapsed && (
          <div
            onMouseDown={startResizeSidebar}
            className={`w-2 hover:bg-[#ff7300]/20 active:bg-[#ff7300]/40 cursor-col-resize transition-colors flex items-center justify-center shrink-0 rounded-md ${
              isResizingSidebar ? "bg-[#ff7300]/30" : ""
            }`}
            title="Drag to resize sidebar"
          >
            <div className="w-[1px] h-8 bg-[rgba(11,9,7,0.12)]" />
          </div>
        )}

        {/* Center Panel (Modular Viewer) */}
        <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
          {renderActiveView()}
        </div>
      </section>
    </main>
  );
}

export default function StudentsPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-screen w-screen items-center justify-center bg-[#f2efe4] font-mono text-sm text-[#3c3a39]">
          /loading-optimization-terminal...
        </div>
      }
    >
      <StudentsPageContent />
    </Suspense>
  );
}
