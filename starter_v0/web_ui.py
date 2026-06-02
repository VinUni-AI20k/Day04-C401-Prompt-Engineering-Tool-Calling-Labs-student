from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"

load_lab_env(ROOT)

PROVIDER_CACHE: dict[str, Any] = {}


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Research Agent</title>
  <style>
    :root {
      --bg: #ffffff;
      --panel: #f7f7f8;
      --panel-strong: #ececf1;
      --text: #202123;
      --muted: #6b7280;
      --line: #d9d9e3;
      --accent: #10a37f;
      --accent-strong: #0f8f72;
      --danger: #b42318;
      --shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * {
      box-sizing: border-box;
    }

    html, body {
      background: var(--bg);
      color: var(--text);
      height: 100%;
      margin: 0;
    }

    button, input, textarea, select {
      font: inherit;
    }

    .shell {
      display: grid;
      grid-template-columns: 292px minmax(0, 1fr);
      min-height: 100vh;
    }

    .sidebar {
      background: var(--panel);
      border-right: 1px solid var(--line);
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      padding: 12px;
    }

    .brand {
      align-items: center;
      display: flex;
      gap: 10px;
      margin: 2px 4px 12px;
    }

    .brand-mark {
      align-items: center;
      background: var(--text);
      border-radius: 7px;
      color: white;
      display: flex;
      font-size: 13px;
      font-weight: 700;
      height: 30px;
      justify-content: center;
      width: 30px;
    }

    .brand-title {
      font-size: 15px;
      font-weight: 700;
      line-height: 1.1;
    }

    .brand-subtitle {
      color: var(--muted);
      font-size: 12px;
      margin-top: 2px;
    }

    .new-chat {
      align-items: center;
      background: var(--text);
      border: 1px solid var(--text);
      border-radius: 7px;
      color: white;
      cursor: pointer;
      display: flex;
      font-weight: 650;
      gap: 8px;
      justify-content: center;
      min-height: 40px;
      padding: 9px 10px;
      width: 100%;
    }

    .new-chat:hover {
      background: #343541;
    }

    .settings {
      border-bottom: 1px solid var(--line);
      margin: 12px 0 10px;
      padding-bottom: 12px;
    }

    .field {
      margin-bottom: 9px;
    }

    .field label {
      color: var(--muted);
      display: block;
      font-size: 12px;
      margin-bottom: 4px;
    }

    .field input, .field select {
      background: white;
      border: 1px solid var(--line);
      border-radius: 6px;
      min-height: 34px;
      padding: 6px 8px;
      width: 100%;
    }

    .history-title {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0;
      margin: 5px 4px 7px;
      text-transform: uppercase;
    }

    .history {
      flex: 1;
      overflow-y: auto;
      padding-bottom: 8px;
    }

    .history-item {
      background: transparent;
      border: 1px solid transparent;
      border-radius: 7px;
      color: var(--text);
      cursor: pointer;
      margin-bottom: 4px;
      padding: 8px;
      text-align: left;
      width: 100%;
    }

    .history-item:hover {
      background: var(--panel-strong);
    }

    .history-item.active {
      background: white;
      border-color: var(--line);
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }

    .history-name {
      font-size: 14px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .history-meta {
      color: var(--muted);
      font-size: 12px;
      margin-top: 3px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .main {
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
      min-height: 100vh;
    }

    .topbar {
      align-items: center;
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      min-height: 58px;
      padding: 10px 22px;
    }

    .chat-title {
      font-size: 16px;
      font-weight: 700;
      max-width: 720px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .chat-meta {
      color: var(--muted);
      font-size: 12px;
      margin-top: 2px;
    }

    .status {
      background: #eefaf6;
      border: 1px solid #b8eadc;
      border-radius: 999px;
      color: #08745c;
      font-size: 12px;
      font-weight: 700;
      padding: 5px 9px;
      white-space: nowrap;
    }

    .messages {
      overflow-y: auto;
      padding: 18px 0 28px;
    }

    .message-row {
      border-bottom: 1px solid #f0f0f2;
      padding: 18px 24px;
    }

    .message {
      display: grid;
      gap: 14px;
      grid-template-columns: 34px minmax(0, 780px);
      margin: 0 auto;
      max-width: 900px;
    }

    .avatar {
      align-items: center;
      border-radius: 6px;
      display: flex;
      font-size: 12px;
      font-weight: 800;
      height: 30px;
      justify-content: center;
      width: 30px;
    }

    .avatar.user {
      background: #e8eefc;
      color: #244a9b;
    }

    .avatar.agent {
      background: #e8f7f2;
      color: #08745c;
    }

    .content {
      line-height: 1.55;
      min-width: 0;
      overflow-wrap: anywhere;
      white-space: pre-wrap;
    }

    .tool-strip {
      margin-top: 10px;
    }

    .tool-chip {
      background: white;
      border: 1px solid var(--line);
      border-radius: 999px;
      color: #374151;
      display: inline-block;
      font-size: 12px;
      font-weight: 650;
      margin: 0 5px 6px 0;
      padding: 3px 8px;
    }

    details {
      margin-top: 8px;
    }

    summary {
      color: var(--muted);
      cursor: pointer;
      font-size: 13px;
      font-weight: 650;
    }

    pre {
      background: #0f172a;
      border-radius: 7px;
      color: #e5e7eb;
      font-size: 12px;
      margin: 8px 0 0;
      overflow-x: auto;
      padding: 10px;
      white-space: pre-wrap;
    }

    .empty {
      margin: auto;
      max-width: 720px;
      padding: 64px 22px 20px;
      text-align: center;
    }

    .empty h1 {
      font-size: 32px;
      letter-spacing: 0;
      margin: 0 0 10px;
    }

    .empty p {
      color: var(--muted);
      font-size: 15px;
      line-height: 1.6;
      margin: 0 auto;
      max-width: 560px;
    }

    .composer-wrap {
      background: linear-gradient(to top, white 80%, rgba(255, 255, 255, 0));
      padding: 14px 20px 20px;
    }

    .composer {
      align-items: end;
      background: white;
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
      display: grid;
      gap: 10px;
      grid-template-columns: minmax(0, 1fr) auto;
      margin: 0 auto;
      max-width: 840px;
      padding: 10px;
    }

    .composer textarea {
      border: 0;
      max-height: 180px;
      min-height: 42px;
      outline: 0;
      padding: 9px 4px;
      resize: none;
      width: 100%;
    }

    .send {
      align-items: center;
      background: var(--accent);
      border: 0;
      border-radius: 7px;
      color: white;
      cursor: pointer;
      display: flex;
      font-size: 18px;
      font-weight: 800;
      height: 38px;
      justify-content: center;
      width: 38px;
    }

    .send:disabled {
      background: #a9d8cc;
      cursor: wait;
    }

    .error {
      color: var(--danger);
    }

    @media (max-width: 760px) {
      .shell {
        grid-template-columns: 1fr;
      }

      .sidebar {
        border-bottom: 1px solid var(--line);
        border-right: 0;
        min-height: auto;
        max-height: 42vh;
      }

      .message {
        grid-template-columns: 30px minmax(0, 1fr);
      }

      .topbar {
        padding: 10px 14px;
      }

      .message-row {
        padding: 16px 14px;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">RA</div>
        <div>
          <div class="brand-title">Research Agent</div>
          <div class="brand-subtitle">Tool-calling workspace</div>
        </div>
      </div>

      <button class="new-chat" id="newChat">+ New chat</button>

      <div class="settings">
        <div class="field">
          <label for="provider">Provider</label>
          <select id="provider">
            <option value="openrouter">openrouter</option>
            <option value="openai">openai</option>
            <option value="anthropic">anthropic</option>
            <option value="gemini">gemini</option>
          </select>
        </div>
        <div class="field">
          <label for="version">Version</label>
          <input id="version" autocomplete="off">
        </div>
        <div class="field">
          <label for="model">Model override</label>
          <input id="model" autocomplete="off" placeholder="optional">
        </div>
        <div class="field">
          <label for="historyWindow">History turns</label>
          <input id="historyWindow" type="number" min="0" max="20" step="1">
        </div>
        <div class="field">
          <label for="maxToolRounds">Tool rounds</label>
          <input id="maxToolRounds" type="number" min="1" max="10" step="1">
        </div>
      </div>

      <div class="history-title">Saved chats</div>
      <div class="history" id="history"></div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div>
          <div class="chat-title" id="chatTitle">New chat</div>
          <div class="chat-meta" id="chatMeta">Ready</div>
        </div>
        <div class="status" id="status">Live tools</div>
      </header>

      <section class="messages" id="messages"></section>

      <div class="composer-wrap">
        <form class="composer" id="composer">
          <textarea id="prompt" rows="1" placeholder="Message the research agent"></textarea>
          <button class="send" id="send" type="submit" aria-label="Send">></button>
        </form>
      </div>
    </main>
  </div>

  <script>
    const state = {
      currentId: null,
      transcripts: [],
      transcript: null,
      busy: false
    };

    const $ = (id) => document.getElementById(id);

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function api(path, options = {}) {
      const response = await fetch(path, {
        headers: {"Content-Type": "application/json"},
        ...options
      });
      const text = await response.text();
      const data = text ? JSON.parse(text) : null;
      if (!response.ok) {
        throw new Error(data?.error || response.statusText);
      }
      return data;
    }

    function settingsPayload() {
      return {
        provider: $("provider").value,
        version: $("version").value.trim() || "ui",
        model: $("model").value.trim() || null,
        history_window: Number($("historyWindow").value || 5),
        max_tool_rounds: Number($("maxToolRounds").value || 4)
      };
    }

    function titleFor(transcript) {
      const first = transcript?.turns?.find((turn) => turn.user);
      const value = first?.user || "New chat";
      return value.length > 48 ? value.slice(0, 47).trim() + "..." : value;
    }

    function setBusy(value) {
      state.busy = value;
      $("send").disabled = value;
      $("prompt").disabled = value;
      $("status").textContent = value ? "Running" : "Live tools";
    }

    function renderHistory() {
      const root = $("history");
      if (!state.transcripts.length) {
        root.innerHTML = '<div class="history-meta">No saved chats yet.</div>';
        return;
      }

      root.innerHTML = state.transcripts.map((item) => {
        const active = item.id === state.currentId ? " active" : "";
        const meta = [item.version, item.provider, `${item.turn_count} turns`].filter(Boolean).join(" | ");
        return `
          <button class="history-item${active}" data-id="${escapeHtml(item.id)}">
            <div class="history-name">${escapeHtml(item.title)}</div>
            <div class="history-meta">${escapeHtml(meta)}</div>
          </button>`;
      }).join("");

      root.querySelectorAll(".history-item").forEach((button) => {
        button.addEventListener("click", async () => {
          await loadTranscript(button.dataset.id);
        });
      });
    }

    function renderHeader() {
      const transcript = state.transcript;
      $("chatTitle").textContent = transcript ? titleFor(transcript) : "New chat";
      if (!transcript) {
        $("chatMeta").textContent = "Start a chat or open one from the sidebar";
        return;
      }
      const parts = [
        transcript.provider,
        transcript.model,
        transcript.artifact_version,
        `${transcript.turns?.length || 0} turns`
      ].filter(Boolean);
      $("chatMeta").textContent = parts.join(" / ");
    }

    function toolMarkup(turn) {
      const events = turn.tool_events || [];
      if (!events.length) return "";
      const chips = events.map((event) => `<span class="tool-chip">${escapeHtml(event.tool || "tool")}</span>`).join("");
      const raw = escapeHtml(JSON.stringify(events, null, 2));
      return `<div class="tool-strip">${chips}<details><summary>Tool details</summary><pre>${raw}</pre></details></div>`;
    }

    function messageRow(kind, text, extra = "") {
      const label = kind === "user" ? "You" : "AI";
      return `
        <div class="message-row">
          <div class="message">
            <div class="avatar ${kind}">${label}</div>
            <div>
              <div class="content">${escapeHtml(text)}</div>
              ${extra}
            </div>
          </div>
        </div>`;
    }

    function renderMessages() {
      const root = $("messages");
      const transcript = state.transcript;
      if (!transcript || !transcript.turns || !transcript.turns.length) {
        root.innerHTML = `
          <div class="empty">
            <h1>Research Agent</h1>
            <p>Ask for web research, social posts, article summaries, papers, policy lookup, or confirmed publishing. Chat history is saved in the sidebar.</p>
          </div>`;
        return;
      }

      root.innerHTML = transcript.turns.map((turn) => {
        const assistantText = turn.assistant_text || turn.error || "";
        return messageRow("user", turn.user || "") + messageRow("agent", assistantText, toolMarkup(turn));
      }).join("");
      root.scrollTop = root.scrollHeight;
    }

    async function refreshTranscripts() {
      state.transcripts = await api("/api/transcripts");
      renderHistory();
    }

    async function loadTranscript(id) {
      state.currentId = id;
      state.transcript = await api(`/api/transcripts/${encodeURIComponent(id)}`);
      renderHistory();
      renderHeader();
      renderMessages();
    }

    async function createTranscript() {
      const transcript = await api("/api/transcripts", {
        method: "POST",
        body: JSON.stringify(settingsPayload())
      });
      state.currentId = transcript.transcript_id;
      state.transcript = transcript;
      await refreshTranscripts();
      renderHeader();
      renderMessages();
      return transcript;
    }

    async function sendMessage(message) {
      if (!state.currentId) {
        await createTranscript();
      }

      setBusy(true);
      const optimistic = {
        ...(state.transcript || {}),
        turns: [...(state.transcript?.turns || []), {user: message, assistant_text: "Running agent and tools..."}]
      };
      state.transcript = optimistic;
      renderHeader();
      renderMessages();

      try {
        const transcript = await api(`/api/transcripts/${encodeURIComponent(state.currentId)}/messages`, {
          method: "POST",
          body: JSON.stringify({message})
        });
        state.transcript = transcript;
        await refreshTranscripts();
      } catch (error) {
        const turns = state.transcript.turns || [];
        turns[turns.length - 1].assistant_text = `ERROR: ${error.message}`;
      } finally {
        setBusy(false);
        renderHeader();
        renderMessages();
      }
    }

    function autosize(textarea) {
      textarea.style.height = "auto";
      textarea.style.height = Math.min(textarea.scrollHeight, 180) + "px";
    }

    async function init() {
      const defaults = await api("/api/defaults");
      $("provider").value = defaults.provider;
      $("version").value = defaults.version;
      $("model").value = defaults.model || "";
      $("historyWindow").value = defaults.history_window;
      $("maxToolRounds").value = defaults.max_tool_rounds;

      $("newChat").addEventListener("click", createTranscript);
      $("composer").addEventListener("submit", async (event) => {
        event.preventDefault();
        const value = $("prompt").value.trim();
        if (!value || state.busy) return;
        $("prompt").value = "";
        autosize($("prompt"));
        await sendMessage(value);
      });
      $("prompt").addEventListener("input", (event) => autosize(event.target));
      $("prompt").addEventListener("keydown", async (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
          event.preventDefault();
          $("composer").requestSubmit();
        }
      });

      await refreshTranscripts();
      if (state.transcripts.length) {
        await loadTranscript(state.transcripts[0].id);
      } else {
        renderHeader();
        renderMessages();
      }
    }

    init().catch((error) => {
      $("messages").innerHTML = `<div class="empty error"><h1>UI error</h1><p>${escapeHtml(error.message)}</p></div>`;
    });
  </script>
</body>
</html>
"""


def default_version() -> str:
    log_path = ARTIFACTS_DIR / "version_log.csv"
    if not log_path.exists():
        return "v3"
    lines = [line.strip() for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) < 2:
        return "v3"
    return lines[-1].split(",", 1)[0] or "v3"


def json_response(handler: BaseHTTPRequestHandler, payload: Any, status: int = 200) -> None:
    body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def html_response(handler: BaseHTTPRequestHandler, payload: str, status: int = 200) -> None:
    body = payload.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length") or 0)
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    return json.loads(raw.decode("utf-8"))


def transcript_path(transcript_id: str) -> Path:
    return TRANSCRIPTS_DIR / f"{safe_slug(transcript_id)}.transcript.json"


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def short_title(text: str, max_chars: int = 46) -> str:
    cleaned = " ".join(text.split())
    if not cleaned:
        return "Untitled chat"
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 1].rstrip() + "..."


def transcript_title(transcript: dict[str, Any]) -> str:
    for turn in transcript.get("turns", []):
        user_text = turn.get("user")
        if user_text:
            return short_title(str(user_text))
    return "New chat"


def list_transcripts() -> list[dict[str, Any]]:
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for path in TRANSCRIPTS_DIR.glob("*.transcript.json"):
        transcript = load_json(path)
        if not transcript:
            continue
        updated_at = transcript.get("updated_at") or transcript.get("created_at") or ""
        rows.append(
            {
                "id": transcript.get("transcript_id") or path.stem.replace(".transcript", ""),
                "title": transcript_title(transcript),
                "updated_at": updated_at,
                "provider": transcript.get("provider", ""),
                "version": transcript.get("version", ""),
                "turn_count": len(transcript.get("turns", [])),
            }
        )
    return sorted(rows, key=lambda item: item["updated_at"], reverse=True)


def get_provider(name: str) -> Any:
    if name not in PROVIDER_CACHE:
        PROVIDER_CACHE[name] = make_provider(name)
    return PROVIDER_CACHE[name]


def build_history(transcript: dict[str, Any], history_window: int) -> list[dict[str, str]]:
    history: list[dict[str, str]] = []
    for turn in transcript.get("turns", []):
        user_text = turn.get("user")
        assistant_text = turn.get("assistant_text")
        if user_text:
            history.append({"role": "user", "content": str(user_text)})
        if assistant_text:
            history.append({"role": "assistant", "content": str(assistant_text)})
    return trim_history(history, history_window)


def create_transcript(settings: dict[str, Any]) -> dict[str, Any]:
    provider_name = str(settings.get("provider") or "openrouter")
    version = str(settings.get("version") or default_version())
    model = settings.get("model") or None
    history_window = int(settings.get("history_window") or 5)
    max_tool_rounds = int(settings.get("max_tool_rounds") or 4)
    provider = get_provider(provider_name)
    selected_model = model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    write_transcript(transcript_path(transcript_id), transcript)
    return transcript


def process_message(transcript_id: str, user_text: str) -> dict[str, Any]:
    path = transcript_path(transcript_id)
    transcript = load_json(path)
    if not transcript:
        raise FileNotFoundError(f"Transcript not found: {transcript_id}")

    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(TOOLS_PATH)
    openai_tools = to_openai_tools(tool_declarations)
    provider = get_provider(str(transcript.get("provider") or "openrouter"))
    history_window = int(transcript.get("history_window") or 5)
    max_tool_rounds = int(transcript.get("max_tool_rounds") or 4)

    messages = [
        {"role": "system", "content": system_prompt},
        *build_history(transcript, history_window),
        {"role": "user", "content": user_text},
    ]
    turn_record: dict[str, Any] = {
        "turn_index": len(transcript.get("turns", [])) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=transcript.get("model"),
            max_tool_rounds=max_tool_rounds,
        )
        turn_record.update(result)
    except Exception as exc:
        turn_record.update(
            {
                "status": "provider_error",
                "assistant_text": f"{type(exc).__name__}: {str(exc)}",
                "error": f"{type(exc).__name__}: {str(exc)}",
            }
        )

    turn_record["ended_at"] = now_iso()
    transcript.setdefault("turns", []).append(turn_record)
    write_transcript(path, transcript)
    return transcript


class ResearchUIHandler(BaseHTTPRequestHandler):
    server_version = "ResearchAgentUI/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/":
            html_response(self, HTML)
            return

        if path == "/api/defaults":
            json_response(
                self,
                {
                    "provider": "openrouter",
                    "version": default_version(),
                    "model": "",
                    "history_window": 5,
                    "max_tool_rounds": 4,
                },
            )
            return

        if path == "/api/transcripts":
            json_response(self, list_transcripts())
            return

        if path.startswith("/api/transcripts/"):
            transcript_id = unquote(path.removeprefix("/api/transcripts/"))
            transcript = load_json(transcript_path(transcript_id))
            if not transcript:
                json_response(self, {"error": "Transcript not found"}, status=404)
                return
            json_response(self, transcript)
            return

        json_response(self, {"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        try:
            payload = read_json(self)
            if path == "/api/transcripts":
                json_response(self, create_transcript(payload), status=201)
                return

            if path.startswith("/api/transcripts/") and path.endswith("/messages"):
                middle = path.removeprefix("/api/transcripts/").removesuffix("/messages").strip("/")
                transcript_id = unquote(middle)
                message = str(payload.get("message") or "").strip()
                if not message:
                    json_response(self, {"error": "Message is required"}, status=400)
                    return
                json_response(self, process_message(transcript_id, message))
                return

            json_response(self, {"error": "Not found"}, status=404)
        except Exception as exc:
            message = html.escape(f"{type(exc).__name__}: {str(exc)}")
            json_response(self, {"error": message}, status=500)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local ChatGPT-style UI for the Research Agent.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), ResearchUIHandler)
    print(f"Research Agent UI: http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
