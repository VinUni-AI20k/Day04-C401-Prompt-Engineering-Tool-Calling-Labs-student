from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from chat import (
    json_text,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)


INDEX_HTML = r"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Research Agent Test UI</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #667085;
      --line: #d9dee8;
      --accent: #0f766e;
      --accent-2: #1d4ed8;
      --danger: #b42318;
      --soft: #eef6f5;
      --shadow: 0 16px 34px rgba(16, 24, 40, 0.08);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        linear-gradient(180deg, rgba(15, 118, 110, 0.09), rgba(247, 248, 251, 0) 260px),
        var(--bg);
      color: var(--ink);
    }
    button, input, select, textarea { font: inherit; }
    button {
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      height: 38px;
      padding: 0 12px;
      border-radius: 6px;
      cursor: pointer;
    }
    button:hover { border-color: #aeb8c8; }
    button.primary {
      background: var(--accent);
      border-color: var(--accent);
      color: white;
      min-width: 96px;
    }
    button:disabled {
      opacity: .62;
      cursor: not-allowed;
    }
    .shell {
      display: grid;
      grid-template-rows: auto 1fr;
      min-height: 100vh;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      padding: 16px 22px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.86);
      backdrop-filter: blur(10px);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 230px;
    }
    .mark {
      width: 34px;
      height: 34px;
      border-radius: 7px;
      display: grid;
      place-items: center;
      background: var(--accent);
      color: #fff;
      font-weight: 800;
      letter-spacing: 0;
      box-shadow: 0 8px 18px rgba(15, 118, 110, 0.25);
    }
    h1 {
      margin: 0;
      font-size: 17px;
      line-height: 1.2;
      letter-spacing: 0;
    }
    .subtitle {
      color: var(--muted);
      font-size: 12px;
      margin-top: 2px;
    }
    .controls {
      display: grid;
      grid-template-columns: 138px 210px 82px 82px 92px auto;
      gap: 10px;
      align-items: end;
      width: min(920px, 100%);
    }
    label {
      display: grid;
      gap: 4px;
      color: var(--muted);
      font-size: 12px;
    }
    input, select, textarea {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      outline: none;
    }
    input, select {
      height: 38px;
      padding: 0 10px;
    }
    input:focus, select:focus, textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14);
    }
    main {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 390px;
      gap: 0;
      min-height: 0;
    }
    .chat {
      display: grid;
      grid-template-rows: 1fr auto;
      min-width: 0;
      min-height: 0;
    }
    .messages {
      overflow: auto;
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .empty {
      margin: auto;
      max-width: 680px;
      color: var(--muted);
      text-align: center;
      line-height: 1.6;
    }
    .samples {
      display: flex;
      gap: 8px;
      justify-content: center;
      flex-wrap: wrap;
      margin-top: 14px;
    }
    .samples button { color: var(--accent-2); }
    .bubble {
      width: min(820px, 100%);
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: 0 8px 20px rgba(16, 24, 40, 0.05);
      white-space: pre-wrap;
      line-height: 1.5;
    }
    .bubble.user {
      align-self: flex-end;
      background: #e8f3ff;
      border-color: #bdd7ff;
    }
    .bubble.agent {
      align-self: flex-start;
    }
    .bubble.error {
      border-color: #f3b7af;
      color: var(--danger);
      background: #fff5f4;
    }
    .meta {
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 6px;
      display: flex;
      justify-content: space-between;
      gap: 12px;
    }
    .composer {
      padding: 16px 22px 20px;
      border-top: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.86);
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
    }
    textarea {
      min-height: 54px;
      max-height: 150px;
      resize: vertical;
      padding: 12px;
      line-height: 1.45;
    }
    aside {
      border-left: 1px solid var(--line);
      background: #fbfcfe;
      min-height: 0;
      display: grid;
      grid-template-rows: auto 1fr;
    }
    .side-head {
      padding: 16px;
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }
    .side-title {
      font-size: 14px;
      font-weight: 700;
    }
    .status {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--soft);
      color: var(--accent);
      font-size: 12px;
      white-space: nowrap;
    }
    .inspect {
      overflow: auto;
      padding: 16px;
    }
    details {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      margin-bottom: 10px;
      overflow: hidden;
    }
    summary {
      cursor: pointer;
      padding: 10px 12px;
      font-size: 13px;
      font-weight: 700;
      color: #344054;
      background: #f5f7fb;
    }
    pre {
      margin: 0;
      padding: 12px;
      white-space: pre-wrap;
      word-break: break-word;
      font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      color: #26323f;
    }
    .path {
      font-size: 12px;
      color: var(--muted);
      word-break: break-all;
      padding: 0 2px 12px;
    }
    @media (max-width: 980px) {
      header { align-items: stretch; flex-direction: column; }
      .controls { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      main { grid-template-columns: 1fr; }
      aside { min-height: 360px; border-left: 0; border-top: 1px solid var(--line); }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div class="brand">
        <div class="mark">RA</div>
        <div>
          <h1>Research Agent Test UI</h1>
          <div class="subtitle">Nhóm 4</div>
        </div>
      </div>
      <div class="controls">
        <label>Provider
          <select id="provider">
            <option value="gemini" selected>gemini</option>
            <option value="openrouter">openrouter</option>
            <option value="openai">openai</option>
            <option value="anthropic">anthropic</option>
          </select>
        </label>
        <label>Model
          <input id="model" value="gemini-3.1-flash-lite">
        </label>
        <label>Version
          <input id="version" value="v0">
        </label>
        <label>History
          <input id="historyWindow" type="number" min="0" max="20" value="5">
        </label>
        <label>Rounds
          <input id="maxToolRounds" type="number" min="1" max="8" value="4">
        </label>
        <button id="resetBtn" title="Start a fresh transcript">Reset</button>
      </div>
    </header>
    <main>
      <section class="chat">
        <div id="messages" class="messages">
          <div class="empty">
            Nhập một yêu cầu research để kiểm tra routing, arguments, tool results và transcript.
            <div class="samples">
              <button data-sample="Tweet mới nhất của Sam Altman là gì?">Sam Altman tweets</button>
              <button data-sample="Tin tức AI hôm nay có gì nổi bật?">AI news today</button>
              <button data-sample="Tóm tắt bài này hộ mình">Missing URL</button>
              <button data-sample="Đăng bản tin này lên Telegram giúp mình">Send boundary</button>
            </div>
          </div>
        </div>
        <form id="composer" class="composer">
          <textarea id="message" placeholder="Nhập prompt test..." required></textarea>
          <button id="sendBtn" class="primary" type="submit">Send</button>
        </form>
      </section>
      <aside>
        <div class="side-head">
          <div class="side-title">Run Inspector</div>
          <span id="status" class="status">idle</span>
        </div>
        <div id="inspect" class="inspect">
          <div class="path">Transcript sẽ xuất hiện sau lượt đầu tiên.</div>
        </div>
      </aside>
    </main>
  </div>
  <script>
    const els = {
      provider: document.getElementById('provider'),
      model: document.getElementById('model'),
      version: document.getElementById('version'),
      historyWindow: document.getElementById('historyWindow'),
      maxToolRounds: document.getElementById('maxToolRounds'),
      resetBtn: document.getElementById('resetBtn'),
      messages: document.getElementById('messages'),
      inspect: document.getElementById('inspect'),
      status: document.getElementById('status'),
      form: document.getElementById('composer'),
      message: document.getElementById('message'),
      sendBtn: document.getElementById('sendBtn')
    };
    let sessionId = crypto.randomUUID();
    let hasMessages = false;

    function clearEmpty() {
      if (!hasMessages) {
        els.messages.innerHTML = '';
        hasMessages = true;
      }
    }
    function addBubble(role, text, extra = '') {
      clearEmpty();
      const node = document.createElement('div');
      node.className = `bubble ${role}`;
      node.innerHTML = `<div class="meta"><span>${role === 'user' ? 'You' : role === 'error' ? 'Error' : 'Agent'}</span><span>${new Date().toLocaleTimeString()}</span></div>${escapeHtml(text || '')}${extra}`;
      els.messages.appendChild(node);
      els.messages.scrollTop = els.messages.scrollHeight;
    }
    function escapeHtml(value) {
      return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;');
    }
    function setStatus(text) {
      els.status.textContent = text;
    }
    function renderInspector(payload) {
      const turn = payload.turn || {};
      const rounds = turn.rounds || [];
      const events = turn.tool_events || [];
      els.inspect.innerHTML = `
        <div class="path">${escapeHtml(payload.transcript_path || '')}</div>
        <details open>
          <summary>Turn</summary>
          <pre>${escapeHtml(JSON.stringify({
            status: turn.status,
            provider: payload.provider,
            model: payload.model,
            artifact_version: payload.artifact_version,
            assistant_text: turn.assistant_text
          }, null, 2))}</pre>
        </details>
        <details open>
          <summary>Tool Calls & Results (${events.length})</summary>
          <pre>${escapeHtml(JSON.stringify(events, null, 2))}</pre>
        </details>
        <details>
          <summary>Rounds (${rounds.length})</summary>
          <pre>${escapeHtml(JSON.stringify(rounds, null, 2))}</pre>
        </details>
      `;
    }
    async function sendMessage(text) {
      addBubble('user', text);
      els.sendBtn.disabled = true;
      setStatus('running');
      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            session_id: sessionId,
            message: text,
            provider: els.provider.value,
            model: els.model.value.trim() || null,
            version: els.version.value.trim() || 'ui',
            history_window: Number(els.historyWindow.value || 5),
            max_tool_rounds: Number(els.maxToolRounds.value || 4)
          })
        });
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload.error || response.statusText);
        }
        addBubble('agent', payload.assistant_text || '');
        renderInspector(payload);
        setStatus(payload.status || 'done');
      } catch (error) {
        addBubble('error', error.message);
        setStatus('error');
      } finally {
        els.sendBtn.disabled = false;
        els.message.focus();
      }
    }
    els.form.addEventListener('submit', (event) => {
      event.preventDefault();
      const text = els.message.value.trim();
      if (!text) return;
      els.message.value = '';
      sendMessage(text);
    });
    els.message.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter' || event.shiftKey || event.ctrlKey || event.altKey || event.metaKey) return;
      event.preventDefault();
      if (els.sendBtn.disabled) return;
      els.form.requestSubmit();
    });
    els.resetBtn.addEventListener('click', () => {
      sessionId = crypto.randomUUID();
      hasMessages = false;
      els.messages.innerHTML = document.querySelector('.empty') ? els.messages.innerHTML : `<div class="empty">
        Nhập một yêu cầu research để kiểm tra routing, arguments, tool results và transcript.
        <div class="samples">
          <button data-sample="Tweet mới nhất của Sam Altman là gì?">Sam Altman tweets</button>
          <button data-sample="Tin tức AI hôm nay có gì nổi bật?">AI news today</button>
          <button data-sample="Tóm tắt bài này hộ mình">Missing URL</button>
          <button data-sample="Đăng bản tin này lên Telegram giúp mình">Send boundary</button>
        </div>
      </div>`;
      els.inspect.innerHTML = '<div class="path">Transcript sẽ xuất hiện sau lượt đầu tiên.</div>';
      setStatus('idle');
    });
    document.addEventListener('click', (event) => {
      const button = event.target.closest('[data-sample]');
      if (!button) return;
      els.message.value = button.dataset.sample;
      els.message.focus();
    });
  </script>
</body>
</html>
"""


SESSIONS: dict[str, dict[str, Any]] = {}


def build_context(provider_name: str, version: str, model: str | None) -> dict[str, Any]:
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(tools_path))
    provider = make_provider(provider_name)
    selected_model = model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
    return {
        "provider": provider,
        "provider_name": provider_name,
        "model": model,
        "selected_model": selected_model,
        "system_prompt": system_prompt,
        "tools": tools,
        "artifact_version": artifact_version,
        "system_prompt_path": str(system_prompt_path),
        "tools_path": str(tools_path),
    }


def session_state(session_id: str, context: dict[str, Any], history_window: int, max_tool_rounds: int) -> dict[str, Any]:
    state = SESSIONS.get(session_id)
    if state:
        return state
    transcript_id = "_".join([
        safe_slug("ui"),
        safe_slug(context["provider_name"]),
        datetime.now().strftime("%Y%m%dT%H%M%S%f"),
    ])
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(context["artifact_version"]),
        "provider": context["provider_name"],
        "model": context["selected_model"],
        "system_prompt": context["system_prompt_path"],
        "tools": context["tools_path"],
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "source": "ui_server",
        "turns": [],
    }
    state = {
        "history": [],
        "transcript": transcript,
        "transcript_path": transcript_path,
        "turn_index": 0,
    }
    SESSIONS[session_id] = state
    return state


def handle_chat(payload: dict[str, Any]) -> dict[str, Any]:
    message = str(payload.get("message") or "").strip()
    if not message:
        raise ValueError("message is required")

    provider_name = str(payload.get("provider") or "gemini")
    model = payload.get("model")
    model = str(model).strip() if model else None
    version = str(payload.get("version") or "ui")
    history_window = int(payload.get("history_window") or 5)
    max_tool_rounds = int(payload.get("max_tool_rounds") or 4)
    session_id = str(payload.get("session_id") or safe_slug(datetime.now().isoformat()))

    context = build_context(provider_name, version, model)
    state = session_state(session_id, context, history_window, max_tool_rounds)
    state["turn_index"] += 1

    messages = [
        {"role": "system", "content": context["system_prompt"]},
        *trim_history(state["history"], history_window),
        {"role": "user", "content": message},
    ]
    turn_record: dict[str, Any] = {
        "turn_index": state["turn_index"],
        "started_at": now_iso(),
        "user": message,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    result = run_model_tool_loop(
        provider=context["provider"],
        messages=messages,
        tools=context["tools"],
        model=model,
        max_tool_rounds=max_tool_rounds,
    )
    turn_record.update(result)
    turn_record["ended_at"] = now_iso()
    state["history"].append({"role": "user", "content": message})
    state["history"].append({"role": "assistant", "content": result["assistant_text"]})
    state["transcript"]["turns"].append(turn_record)
    write_transcript(state["transcript_path"], state["transcript"])

    return {
        "session_id": session_id,
        "status": result["status"],
        "assistant_text": result["assistant_text"],
        "provider": provider_name,
        "model": context["selected_model"],
        "artifact_version": context["artifact_version"].artifact_version,
        "transcript_path": str(state["transcript_path"]),
        "turn": turn_record,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "ResearchAgentUI/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))

    def send_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self) -> None:
        body = INDEX_HTML.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self.send_html()
            return
        if path == "/api/health":
            self.send_json({"ok": True, "time": now_iso()})
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/chat":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length") or "0")
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            self.send_json(handle_chat(payload))
        except Exception as exc:
            self.send_json({"error": f"{type(exc).__name__}: {exc}"}, status=HTTPStatus.BAD_REQUEST)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Research Agent browser UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Research Agent UI: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
