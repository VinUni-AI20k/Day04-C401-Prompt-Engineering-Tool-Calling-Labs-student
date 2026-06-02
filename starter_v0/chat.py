from __future__ import annotations

import argparse
import json
import os
import re
import sys
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


APP_HTML = r"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Lumi Research Chat</title>
  <style>
    :root {
      --ink: #17202a;
      --muted: #6b7280;
      --glass: rgba(255, 255, 255, .72);
      --line: rgba(23, 32, 42, .12);
      --mint: #5eead4;
      --lime: #d9f99d;
      --sun: #fde68a;
      --rose: #fb7185;
      --sky: #60a5fa;
      --shadow: 0 28px 80px rgba(17, 24, 39, .18);
      --soft: 0 14px 34px rgba(17, 24, 39, .10);
      font-family: "Segoe UI Variable Text", "Aptos", "Trebuchet MS", sans-serif;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at 8% 12%, rgba(94, 234, 212, .58), transparent 29%),
        radial-gradient(circle at 88% 8%, rgba(253, 230, 138, .74), transparent 31%),
        radial-gradient(circle at 78% 88%, rgba(251, 113, 133, .38), transparent 30%),
        linear-gradient(135deg, #f8fbff 0%, #eefcf5 42%, #fff7df 75%, #fff1f6 100%);
      overflow: hidden;
    }

    body::before {
      content: "";
      position: fixed;
      width: 460px;
      height: 460px;
      left: -160px;
      bottom: -160px;
      border-radius: 50%;
      background: repeating-radial-gradient(circle, rgba(23, 32, 42, .08) 0 2px, transparent 2px 18px);
      opacity: .45;
      animation: drift 16s ease-in-out infinite;
    }

    button, textarea, input { font: inherit; }
    button { border: 0; cursor: pointer; }

    .shell {
      position: relative;
      display: grid;
      grid-template-columns: 290px minmax(0, 1fr) 310px;
      gap: 18px;
      width: min(1420px, calc(100vw - 32px));
      height: min(900px, calc(100vh - 32px));
      margin: 16px auto;
      padding: 18px;
      border: 1px solid rgba(255, 255, 255, .72);
      border-radius: 34px;
      background: rgba(255, 255, 255, .42);
      box-shadow: var(--shadow);
      backdrop-filter: blur(24px);
      animation: enter .55s cubic-bezier(.2, .8, .2, 1) both;
    }

    .side, .chat, .panel {
      border: 1px solid rgba(255, 255, 255, .68);
      background: var(--glass);
      box-shadow: var(--soft);
      backdrop-filter: blur(22px);
    }

    .side, .panel {
      border-radius: 26px;
      padding: 18px;
      overflow: hidden;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 18px;
    }

    .logo {
      display: grid;
      width: 50px;
      height: 50px;
      place-items: center;
      border-radius: 18px;
      font-size: 24px;
      font-weight: 950;
      background: conic-gradient(from 180deg, var(--mint), var(--lime), var(--sun), var(--rose), var(--sky), var(--mint));
      box-shadow: 0 18px 34px rgba(45, 212, 191, .25);
    }

    .eyebrow {
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      font-weight: 850;
      letter-spacing: .12em;
      text-transform: uppercase;
    }

    h1, h2, h3 { margin: 0; letter-spacing: -.045em; }
    h1 { font-size: 25px; }

    .primary {
      width: 100%;
      padding: 15px 16px;
      border-radius: 18px;
      color: #132018;
      font-weight: 900;
      background: linear-gradient(135deg, var(--lime), var(--mint));
      box-shadow: 0 16px 30px rgba(45, 212, 191, .24);
      transition: transform .18s ease;
    }

    .primary:hover { transform: translateY(-2px); }

    .label {
      display: flex;
      justify-content: space-between;
      margin: 24px 0 12px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
      letter-spacing: .08em;
      text-transform: uppercase;
    }

    .chip {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,255,255,.62);
      color: var(--ink);
      font-size: 12px;
      font-weight: 850;
    }

    .preset {
      display: block;
      width: 100%;
      margin-bottom: 10px;
      padding: 13px;
      border-radius: 18px;
      text-align: left;
      color: var(--ink);
      background: rgba(255,255,255,.55);
      border: 1px solid transparent;
      transition: background .18s ease, transform .18s ease, border-color .18s ease;
    }

    .preset:hover {
      transform: translateX(3px);
      background: rgba(255,255,255,.88);
      border-color: var(--line);
    }

    .preset strong { display: block; margin-bottom: 4px; }
    .preset span { color: var(--muted); font-size: 12px; line-height: 1.35; }

    .mood {
      margin-top: 18px;
      padding: 17px;
      border-radius: 22px;
      color: white;
      background:
        radial-gradient(circle at 90% 10%, rgba(94, 234, 212, .45), transparent 42%),
        linear-gradient(145deg, #17202a, #26384a);
    }

    .mood p { margin: 8px 0 0; color: rgba(255,255,255,.74); font-size: 13px; line-height: 1.45; }

    .chat {
      display: grid;
      grid-template-rows: auto 1fr auto;
      overflow: hidden;
      border-radius: 30px;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      padding: 20px 22px;
      border-bottom: 1px solid var(--line);
      background: rgba(255,255,255,.55);
    }

    .bot {
      display: flex;
      align-items: center;
      gap: 14px;
      min-width: 0;
    }

    .orb {
      position: relative;
      display: grid;
      width: 54px;
      height: 54px;
      flex: 0 0 auto;
      place-items: center;
      border-radius: 20px;
      font-size: 24px;
      font-weight: 950;
      background: conic-gradient(from 40deg, var(--mint), var(--lime), var(--sun), var(--rose), var(--sky), var(--mint));
    }

    .orb::after {
      content: "";
      position: absolute;
      right: -2px;
      bottom: -2px;
      width: 14px;
      height: 14px;
      border: 3px solid white;
      border-radius: 50%;
      background: #22c55e;
    }

    .bot h2 { font-size: clamp(22px, 3vw, 30px); }
    .bot p { margin: 5px 0 0; color: var(--muted); font-size: 13px; font-weight: 700; }

    .status {
      white-space: nowrap;
      padding: 10px 13px;
      border-radius: 999px;
      color: #233116;
      font-size: 13px;
      font-weight: 900;
      background: linear-gradient(135deg, rgba(217, 249, 157, .95), rgba(253, 230, 138, .86));
    }

    .messages {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 24px;
      overflow-y: auto;
    }

    .divider {
      align-self: center;
      padding: 8px 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      color: var(--muted);
      background: rgba(255,255,255,.62);
      font-size: 12px;
      font-weight: 850;
    }

    .msg {
      display: grid;
      grid-template-columns: 42px minmax(0, 1fr);
      gap: 12px;
      max-width: 78%;
      animation: pop .28s ease both;
    }

    .msg.user {
      grid-template-columns: minmax(0, 1fr) 42px;
      align-self: flex-end;
    }

    .avatar {
      display: grid;
      width: 42px;
      height: 42px;
      place-items: center;
      border-radius: 15px;
      font-weight: 950;
      background: linear-gradient(135deg, var(--mint), var(--lime));
    }

    .msg.user .avatar { order: 2; background: linear-gradient(135deg, var(--rose), var(--sun)); }
    .msg.user .bubble { order: 1; color: white; background: linear-gradient(135deg, #17202a, #29465b); border-top-right-radius: 8px; }

    .bubble {
      padding: 15px 17px;
      border-radius: 22px;
      border-top-left-radius: 8px;
      background: rgba(255,255,255,.82);
      box-shadow: 0 12px 28px rgba(17, 24, 39, .08);
      line-height: 1.56;
      white-space: pre-wrap;
    }

    .typing {
      display: inline-flex;
      gap: 5px;
      padding: 14px 16px;
      border-radius: 18px;
      background: rgba(255,255,255,.82);
      box-shadow: 0 12px 28px rgba(17, 24, 39, .08);
    }

    .typing span {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--muted);
      animation: bounce .9s ease-in-out infinite;
    }

    .typing span:nth-child(2) { animation-delay: .12s; }
    .typing span:nth-child(3) { animation-delay: .24s; }

    .composer-area {
      padding: 16px 20px 20px;
      border-top: 1px solid var(--line);
      background: rgba(255,255,255,.54);
    }

    .composer {
      display: grid;
      grid-template-columns: 1fr 52px;
      gap: 10px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: rgba(255,255,255,.86);
      box-shadow: 0 18px 36px rgba(17, 24, 39, .08);
    }

    textarea {
      width: 100%;
      min-height: 52px;
      max-height: 132px;
      padding: 14px 10px;
      resize: none;
      border: 0;
      outline: 0;
      background: transparent;
      color: var(--ink);
    }

    .send {
      display: grid;
      width: 52px;
      height: 52px;
      place-items: center;
      border-radius: 18px;
      color: #132018;
      font-size: 22px;
      font-weight: 950;
      background: linear-gradient(135deg, var(--mint), var(--lime));
      transition: transform .18s ease;
    }

    .send:hover { transform: translateY(-2px) rotate(-4deg); }

    .hint {
      display: flex;
      justify-content: space-between;
      margin: 10px 8px 0;
      color: var(--muted);
      font-size: 12px;
      font-weight: 760;
    }

    .panel h2 { font-size: 24px; margin-bottom: 16px; }

    .metric {
      padding: 16px;
      border-radius: 20px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,.58);
      margin-bottom: 12px;
    }

    .metric strong { display: block; font-size: 24px; letter-spacing: -.04em; }
    .metric span { color: var(--muted); font-size: 12px; font-weight: 850; }

    .tips {
      padding: 16px;
      border-radius: 22px;
      border: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(253,230,138,.7), rgba(255,255,255,.6));
      line-height: 1.45;
    }

    .tips p { margin: 8px 0 0; color: var(--muted); font-size: 13px; }

    @keyframes enter { from { opacity: 0; transform: translateY(16px) scale(.985); } to { opacity: 1; transform: none; } }
    @keyframes pop { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
    @keyframes bounce { 0%, 80%, 100% { transform: translateY(0); opacity: .45; } 40% { transform: translateY(-5px); opacity: 1; } }
    @keyframes drift { 50% { transform: translate(28px, -22px) rotate(10deg); } }

    @media (max-width: 1080px) {
      .shell { grid-template-columns: 250px minmax(0, 1fr); }
      .panel { display: none; }
    }

    @media (max-width: 760px) {
      body { overflow: auto; }
      .shell {
        grid-template-columns: 1fr;
        width: calc(100vw - 16px);
        height: calc(100vh - 16px);
        margin: 8px;
        padding: 9px;
        border-radius: 24px;
      }
      .side { display: none; }
      .chat { border-radius: 22px; }
      .topbar { padding: 15px; align-items: flex-start; }
      .status { display: none; }
      .messages { padding: 16px 13px; }
      .msg { max-width: 93%; }
      .hint { display: none; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <aside class="side">
      <div class="brand">
        <div class="logo">L</div>
        <div>
          <p class="eyebrow">Lumi AI</p>
          <h1>Research Chat</h1>
        </div>
      </div>
      <button class="primary" id="newChat">+ Tạo chat mới</button>
      <div class="label">Prompt nhanh <span class="chip">4 mẫu</span></div>
      <button class="preset" data-prompt="Tóm tắt chủ đề này thật ngắn gọn, có bullet rõ ràng."><strong>Tóm tắt nhanh</strong><span>Rút ý chính, dễ đọc, dễ học.</span></button>
      <button class="preset" data-prompt="Hãy tìm thông tin bằng tool nếu cần, sau đó trả lời có nguồn."><strong>Tìm có nguồn</strong><span>Hợp với bài research/tool calling.</span></button>
      <button class="preset" data-prompt="Giải thích như dạy người mới bắt đầu, từng bước một."><strong>Dạy dễ hiểu</strong><span>Giải thích chậm, không nặng thuật ngữ.</span></button>
      <button class="preset" data-prompt="Cho tôi kế hoạch hành động 5 bước cho vấn đề này."><strong>Lập kế hoạch</strong><span>Biến ý tưởng thành việc làm được.</span></button>
      <div class="mood">
        <h3>Creative + Clear</h3>
        <p>Giao diện ưu tiên dễ đọc, phản hồi nhanh, có trạng thái kết nối và không làm người dùng bị ngợp.</p>
      </div>
    </aside>

    <section class="chat">
      <header class="topbar">
        <div class="bot">
          <div class="orb">✦</div>
          <div>
            <h2>Lumi đang sẵn sàng</h2>
            <p>Nhập câu hỏi, Lumi sẽ gọi model/provider phía Python.</p>
          </div>
        </div>
        <div class="status" id="status">Đã kết nối</div>
      </header>

      <div class="messages" id="messages">
        <div class="divider">Hôm nay · Web UI</div>
        <article class="msg bot">
          <span class="avatar">L</span>
          <div class="bubble">Chào bạn, mình là Lumi. Giao diện mới đã sẵn sàng: trẻ trung, sáng, dễ dùng và có thể kết nối với provider/API của bài lab.</div>
        </article>
      </div>

      <footer class="composer-area">
        <form class="composer" id="composer">
          <textarea id="input" rows="1" placeholder="Nhập tin nhắn... Enter để gửi, Shift + Enter để xuống dòng"></textarea>
          <button class="send" type="submit" aria-label="Gửi">➜</button>
        </form>
        <div class="hint">
          <span>Enter để gửi · Shift + Enter để xuống dòng</span>
          <span id="providerLabel">Provider: đang tải...</span>
        </div>
      </footer>
    </section>

    <aside class="panel">
      <p class="eyebrow">Dashboard</p>
      <h2>Trạng thái bot</h2>
      <div class="metric"><strong id="turns">0</strong><span>Lượt trò chuyện</span></div>
      <div class="metric"><strong id="latency">--</strong><span>Thời gian phản hồi</span></div>
      <div class="metric"><strong id="model">Model</strong><span>Đang sử dụng</span></div>
      <div class="tips">
        <strong>Gợi ý dùng tốt</strong>
        <p>Hãy hỏi rõ mục tiêu, định dạng mong muốn và nguồn cần dùng. Nếu tool được cấu hình, bot sẽ gọi tool ở backend.</p>
      </div>
    </aside>
  </main>

  <script>
    const messages = document.querySelector("#messages");
    const composer = document.querySelector("#composer");
    const input = document.querySelector("#input");
    const statusEl = document.querySelector("#status");
    const turnsEl = document.querySelector("#turns");
    const latencyEl = document.querySelector("#latency");
    const modelEl = document.querySelector("#model");
    const providerLabel = document.querySelector("#providerLabel");
    const presets = document.querySelectorAll("[data-prompt]");
    const newChat = document.querySelector("#newChat");

    let history = [];
    let turns = 0;

    function escapeHtml(text) {
      return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function appendMessage(text, type = "user") {
      const item = document.createElement("article");
      item.className = `msg ${type}`;
      const avatar = document.createElement("span");
      avatar.className = "avatar";
      avatar.textContent = type === "user" ? "T" : "L";
      const bubble = document.createElement("div");
      bubble.className = "bubble";
      bubble.innerHTML = escapeHtml(text);
      if (type === "user") item.append(bubble, avatar);
      else item.append(avatar, bubble);
      messages.append(item);
      messages.scrollTop = messages.scrollHeight;
    }

    function showTyping() {
      const item = document.createElement("article");
      item.className = "msg bot";
      item.id = "typing";
      item.innerHTML = '<span class="avatar">L</span><div class="typing"><span></span><span></span><span></span></div>';
      messages.append(item);
      messages.scrollTop = messages.scrollHeight;
    }

    function removeTyping() {
      document.querySelector("#typing")?.remove();
    }

    async function loadMeta() {
      try {
        const res = await fetch("/api/meta");
        const meta = await res.json();
        modelEl.textContent = meta.model || "Default";
        providerLabel.textContent = `Provider: ${meta.provider} · ${meta.model || "default"}`;
      } catch {
        providerLabel.textContent = "Provider: chưa kết nối";
      }
    }

    async function sendMessage(text) {
      const message = text.trim();
      if (!message) return;

      appendMessage(message, "user");
      input.value = "";
      input.style.height = "auto";
      statusEl.textContent = "Đang nghĩ...";
      showTyping();
      const start = performance.now();

      try {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message, history })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "API error");
        removeTyping();
        appendMessage(data.reply || "(Không có phản hồi)", "bot");
        history.push({ role: "user", content: message }, { role: "assistant", content: data.reply || "" });
        history = history.slice(-10);
        turns += 1;
        turnsEl.textContent = String(turns);
        latencyEl.textContent = `${Math.round(performance.now() - start)}ms`;
        statusEl.textContent = "Đã kết nối";
      } catch (error) {
        removeTyping();
        appendMessage(`Lỗi kết nối: ${error.message}. Kiểm tra .env, provider và terminal nhé.`, "bot");
        statusEl.textContent = "Cần kiểm tra";
      }
    }

    composer.addEventListener("submit", (event) => {
      event.preventDefault();
      sendMessage(input.value);
    });

    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage(input.value);
      }
    });

    input.addEventListener("input", () => {
      input.style.height = "auto";
      input.style.height = `${Math.min(input.scrollHeight, 132)}px`;
    });

    presets.forEach((button) => button.addEventListener("click", () => sendMessage(button.dataset.prompt)));

    newChat.addEventListener("click", () => {
      history = [];
      turns = 0;
      turnsEl.textContent = "0";
      messages.innerHTML = '<div class="divider">Chat mới</div><article class="msg bot"><span class="avatar">L</span><div class="bubble">Mình đã mở một cuộc trò chuyện mới. Bạn muốn bắt đầu với chủ đề gì?</div></article>';
    });

    loadMeta();
  </script>
</body>
</html>"""


ROOT = Path(__file__).resolve().parent
if ROOT.name.lower() == "web":
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

ARTIFACTS_DIR = ROOT / "artifacts"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def safe_json(value: Any, *, max_chars: int = 24000) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if len(text) > max_chars:
        return text[:max_chars] + "\n...<truncated>"
    return text


def trim_history(history: list[dict[str, str]], max_messages: int = 10) -> list[dict[str, str]]:
    return history[-max_messages:]


def safe_text(value: Any) -> str:
    return str(value or "").strip()


class ChatBackend:
    def __init__(self, provider_name: str, model: str | None, version: str, max_tool_rounds: int):
        self.provider_name = provider_name
        self.model = model
        self.version = version
        self.max_tool_rounds = max_tool_rounds
        self.system_prompt = (
            "Bạn là Lumi, một trợ lý AI thân thiện, rõ ràng, trẻ trung. "
            "Trả lời bằng tiếng Việt tự nhiên, dễ hiểu, ưu tiên hành động cụ thể."
        )
        self.tools: list[dict[str, Any]] = []
        self.provider: Any | None = None
        self.tool_functions: dict[str, Any] = {}
        self.ToolCall: Any | None = None
        self._load_lab_runtime()

    def _load_lab_runtime(self) -> None:
        load_dotenv(ROOT / ".env")
        try:
            from env_loader import load_lab_env
            from providers import make_provider
            from providers.base import ToolCall
            from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
        except Exception as exc:
            raise RuntimeError(
                "Không import được module bài lab. Hãy đặt file này trong starter_v0 hoặc starter_v0/web."
            ) from exc

        load_lab_env(ROOT)
        self.ToolCall = ToolCall
        self.tool_functions = TOOL_FUNCTIONS
        self.provider = make_provider(self.provider_name)
        if self.model is None:
            self.model = getattr(self.provider, "default_model", None)

        prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        tools_path = ARTIFACTS_DIR / "tools.yaml"
        if prompt_path.exists():
            self.system_prompt = prompt_path.read_text(encoding="utf-8")
        if tools_path.exists():
            declarations = load_tool_declarations(tools_path)
            self.tools = to_openai_tools(declarations)

    def execute_tool_call(self, call: Any) -> dict[str, Any]:
        func = self.tool_functions.get(call.name)
        if not func:
            return {
                "tool": call.name,
                "args": call.args,
                "result": {"error": "unknown_tool", "message": f"No local implementation for {call.name}"},
            }
        try:
            result = func(**call.args)
        except Exception as exc:
            result = {"error": type(exc).__name__, "message": str(exc)}
        return {"tool": call.name, "args": call.args, "result": result}

    def chat(self, user_message: str, history: list[dict[str, str]]) -> str:
        if self.provider is None:
            raise RuntimeError("Provider chưa sẵn sàng.")

        messages = [
            {"role": "system", "content": self.system_prompt},
            *trim_history(history),
            {"role": "user", "content": user_message},
        ]
        working_messages = list(messages)

        for _ in range(self.max_tool_rounds):
            response = self.provider.complete(working_messages, self.tools, model=self.model, temperature=0.0)
            calls = getattr(response, "tool_calls", []) or []
            text = safe_text(getattr(response, "text", ""))
            if not calls:
                return text or "Mình chưa tạo được phản hồi. Bạn thử hỏi lại rõ hơn một chút nhé."

            call_summary = [{"name": call.name, "args": call.args} for call in calls]
            working_messages.append({
                "role": "assistant",
                "content": f"{text or 'I will call the selected tool(s).'}\n\nTOOL_CALLS_JSON:\n{safe_json(call_summary)}",
            })

            events = [self.execute_tool_call(call) for call in calls]
            working_messages.append({
                "role": "user",
                "content": (
                    "TOOL_RESULTS_JSON:\n"
                    f"{safe_json(events)}\n\n"
                    "Use only these tool results. Answer the user directly with cited sources when available."
                ),
            })

        return "Mình đã chạy hết số vòng gọi tool. Bạn thử hỏi cụ thể hơn hoặc tăng --max-tool-rounds nhé."


class AppHandler(BaseHTTPRequestHandler):
    backend: ChatBackend

    def send_json(self, data: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/meta":
            self.send_json({
                "provider": self.backend.provider_name,
                "model": self.backend.model,
                "version": self.backend.version,
            })
            return
        if path not in {"/", "/index.html"}:
            self.send_error(404, "Not found")
            return
        body = APP_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/chat":
            self.send_error(404, "Not found")
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            message = safe_text(payload.get("message"))
            history = payload.get("history") or []
            if not message:
                self.send_json({"error": "Tin nhắn đang trống."}, status=400)
                return
            reply = self.backend.chat(message, history)
            self.send_json({"reply": reply, "updated_at": now_iso()})
        except Exception as exc:
            self.send_json({"error": f"{type(exc).__name__}: {exc}"}, status=500)

    def log_message(self, format: str, *args: Any) -> None:
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Beautiful web UI for the lab chatbot.")
    parser.add_argument("--provider", default=os.environ.get("CHATBOT_PROVIDER", "openai"))
    parser.add_argument("--model", default=os.environ.get("CHATBOT_MODEL"))
    parser.add_argument("--version", default=os.environ.get("CHATBOT_VERSION", "v1"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    parser.add_argument("--no-browser", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    backend = ChatBackend(
        provider_name=args.provider,
        model=args.model,
        version=args.version,
        max_tool_rounds=args.max_tool_rounds,
    )
    AppHandler.backend = backend
    server = ThreadingHTTPServer((args.host, args.port), AppHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"Lumi chatbot UI dang chay tai: {url}")
    print("Nhan Ctrl + C de dung server.")
    if not args.no_browser:
        webbrowser.open(url)
    server.serve_forever()


if __name__ == "__main__":
    main()
