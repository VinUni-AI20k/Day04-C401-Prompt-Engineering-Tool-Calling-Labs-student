"""Streamlit UI for the Research Agent — wraps the same agent loop as chat.py."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

# Ensure starter_v0 is on sys.path so relative imports work
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools

load_lab_env(ROOT)

ARTIFACTS_DIR = ROOT / "artifacts"

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="🔬 Research Agent", page_icon="🔬", layout="wide")
st.title("🔬 Research Agent Chat")

# ── Sidebar settings ─────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"])
    model_override = st.text_input("Model override (blank = default)", value="")
    max_tool_rounds = st.slider("Max tool rounds", 1, 8, 4)
    history_window = st.slider("History window (pairs)", 1, 10, 5)

    st.divider()
    st.header("🛠️ Registered Tools")
    tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    for td in tool_declarations:
        st.markdown(f"**{td['name']}** — {td.get('description', '')[:80]}…")

    st.divider()
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.session_state.tool_log = []
        st.rerun()


# ── Helper functions (mirrored from chat.py) ─────────────────────────────────
def json_text(value: Any, *, max_chars: int | None = None) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if max_chars and len(text) > max_chars:
        return text[:max_chars] + "\n...<truncated>"
    return text


def execute_tool_call(call) -> dict[str, Any]:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {"tool": call.name, "args": call.args, "result": {"error": "unknown_tool"}}
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


def tool_results_message(events: list[dict[str, Any]]) -> dict[str, str]:
    return {
        "role": "user",
        "content": (
            "TOOL_RESULTS_JSON:\n"
            f"{json_text(events, max_chars=24000)}\n\n"
            "Use only these tool results. If the user asked for a digest and the items are ready, "
            "call the formatting tool. Otherwise answer the user directly with cited sources when available."
        ),
    }


def assistant_tool_message(response_text: str | None, calls) -> dict[str, str]:
    call_summary = [{"name": c.name, "args": c.args} for c in calls]
    content = response_text or "I will call the selected tool(s)."
    return {"role": "assistant", "content": f"{content}\n\nTOOL_CALLS_JSON:\n{json_text(call_summary)}"}


# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_log" not in st.session_state:
    st.session_state.tool_log = []

# ── Render chat history ──────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if user_input := st.chat_input("Nhập câu hỏi..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build messages for the model
    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    openai_tools = to_openai_tools(tool_declarations)

    # Trim history
    hist = st.session_state.messages[:]
    if len(hist) > history_window * 2:
        hist = hist[-history_window * 2:]

    messages_for_model = [{"role": "system", "content": system_prompt}] + hist

    # Run agent loop
    with st.chat_message("assistant"):
        status_area = st.empty()
        tool_expander = st.expander("🔧 Tool calls", expanded=False)

        try:
            provider = make_provider(provider_name)
            model = model_override or None

            working_messages = list(messages_for_model)
            final_text = ""

            for round_idx in range(1, max_tool_rounds + 1):
                status_area.info(f"⏳ Round {round_idx}/{max_tool_rounds}...")
                response = provider.complete(working_messages, openai_tools, model=model, temperature=0.0)
                calls = response.tool_calls

                if not calls:
                    final_text = response.text or ""
                    break

                # Execute tools
                working_messages.append(assistant_tool_message(response.text, calls))
                events = []
                for call in calls:
                    with tool_expander:
                        st.code(f"🔧 {call.name}({json.dumps(call.args, ensure_ascii=False)})", language="json")
                    event = execute_tool_call(call)
                    events.append(event)
                    st.session_state.tool_log.append(event)

                    with tool_expander:
                        result_preview = json_text(event["result"], max_chars=500)
                        st.code(result_preview, language="json")

                    # Check for clarification
                    result = event.get("result", {})
                    if isinstance(result, dict) and result.get("awaiting_user"):
                        final_text = result.get("question", "Bạn bổ sung thêm thông tin nhé.")
                        break

                if final_text:
                    break

                working_messages.append(tool_results_message(events))
            else:
                if not final_text:
                    final_text = f"Đã chạy {max_tool_rounds} vòng tool. Kiểm tra log để biết chi tiết."

            status_area.empty()
            st.markdown(final_text)

        except Exception as exc:
            status_area.empty()
            final_text = f"❌ Error: {type(exc).__name__}: {exc}"
            st.error(final_text)

    st.session_state.messages.append({"role": "assistant", "content": final_text})
