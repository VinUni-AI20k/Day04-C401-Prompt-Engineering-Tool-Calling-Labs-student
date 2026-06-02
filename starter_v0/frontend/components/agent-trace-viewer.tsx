"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { SidebarUnified } from "./sidebar-unified";
import { ChatPanelInteractive } from "./chat-panel-interactive";
import { TraceRailInteractive } from "./trace-rail-interactive";
import { Activity, PanelRight } from "lucide-react";

export function AgentTraceViewer() {
  const [activeSessionId, setActiveSessionId] = useState("session-cohort");
  const [showRightPanel, setShowRightPanel] = useState(true);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [customTrace, setCustomTrace] = useState<any>(null);

  // Reset custom trace when changing sessions
  useEffect(() => {
    setCustomTrace(null);
  }, [activeSessionId]);

  // Resize states
  const [sidebarWidth, setSidebarWidth] = useState(280);
  const [rightPanelWidth, setRightPanelWidth] = useState(390);
  const [isResizingSidebar, setIsResizingSidebar] = useState(false);
  const [isResizingRight, setIsResizingRight] = useState(false);

  const handleNewChat = () => {
    setActiveSessionId(`session-new-${Date.now()}`);
  };

  const startResizeSidebar = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizingSidebar(true);
  };

  const startResizeRight = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizingRight(true);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isResizingSidebar) {
        // limit width between 180px and 450px
        const newWidth = Math.max(180, Math.min(450, e.clientX - 16));
        setSidebarWidth(newWidth);
      }
      if (isResizingRight) {
        // limit width between 250px and 600px
        const newWidth = Math.max(250, Math.min(600, window.innerWidth - e.clientX - 16));
        setRightPanelWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizingSidebar(false);
      setIsResizingRight(false);
    };

    if (isResizingSidebar || isResizingRight) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizingSidebar, isResizingRight]);

  return (
    <main className={`mx-auto flex min-h-dvh w-full max-w-[1600px] flex-col gap-4 px-4 py-4 lg:h-dvh lg:overflow-hidden bg-[#f2efe4] ${
      isResizingSidebar || isResizingRight ? "select-none" : ""
    }`}>
      <Header showRightPanel={showRightPanel} onToggleRightPanel={() => setShowRightPanel(!showRightPanel)} />
      <section className="flex min-h-0 flex-1 gap-1 transition-all duration-300">
        {/* Left Sidebar wrapper */}
        <div style={{ width: isCollapsed ? 72 : sidebarWidth }} className="flex shrink-0 h-full">
          <SidebarUnified
            activeSessionId={activeSessionId}
            onSelectSession={setActiveSessionId}
            onNewChat={handleNewChat}
            isCollapsed={isCollapsed}
            onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
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

        {/* Middle Panel - Chat */}
        <div className="flex-1 min-w-0 h-full">
          <ChatPanelInteractive activeSessionId={activeSessionId} onTraceUpdate={setCustomTrace} />
        </div>

        {/* Resizer for Right Panel */}
        {showRightPanel && (
          <div
            onMouseDown={startResizeRight}
            className={`w-2 hover:bg-[#ff7300]/20 active:bg-[#ff7300]/40 cursor-col-resize transition-colors flex items-center justify-center shrink-0 rounded-md ${
              isResizingRight ? "bg-[#ff7300]/30" : ""
            }`}
            title="Drag to resize telemetry panel"
          >
            <div className="w-[1px] h-8 bg-[rgba(11,9,7,0.12)]" />
          </div>
        )}

        {/* Right Panel - Trace */}
        {showRightPanel && (
          <div style={{ width: rightPanelWidth }} className="flex shrink-0 h-full">
            <TraceRailInteractive activeSessionId={activeSessionId} customTrace={customTrace} />
          </div>
        )}
      </section>
    </main>
  );
}

function Header({
  showRightPanel,
  onToggleRightPanel,
}: {
  showRightPanel: boolean;
  onToggleRightPanel: () => void;
}) {
  return (
    <header className="flex items-center justify-between rounded-2xl border border-transparent bg-[#3c3a39] px-6 py-4 shadow-md">
      <div>
        <p className="font-mono text-xs font-semibold uppercase tracking-[0.22em] text-[#ffc753]/90">
          /gaptutor-agent-lab
        </p>
        <h1 className="mt-1 text-xl font-bold tracking-tight text-[#fefcf5] md:text-2xl">
          Chatbot with inline thinking & telemetry trace
        </h1>
      </div>
      <div className="flex items-center gap-3">
        <Link
          href="/u/0/students"
          className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 font-mono text-xs text-[#eaeae2] hover:bg-white/10 hover:text-white transition-all shadow-sm"
        >
          <Activity className="size-4 text-[#79deeb]" />
          /view-eval-terminal
        </Link>
        <button
          onClick={onToggleRightPanel}
          className="flex size-8 items-center justify-center rounded-full border border-white/10 bg-white/5 text-[#eaeae2] hover:bg-white/10 hover:text-white transition-all shadow-sm"
          title={showRightPanel ? "Collapse right panel" : "Expand right panel"}
          type="button"
        >
          <PanelRight className={`size-4 ${showRightPanel ? "text-[#79deeb]" : "text-neutral-400"}`} />
        </button>
      </div>
    </header>
  );
}
