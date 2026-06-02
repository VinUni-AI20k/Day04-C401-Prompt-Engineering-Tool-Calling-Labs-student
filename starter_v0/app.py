from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent

# Load env before any other import
from env_loader import load_lab_env
load_lab_env(ROOT)

from providers import make_provider  # noqa: E402
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools  # noqa: E402
from agent import ResearchAgent  # noqa: E402

ARTIFACTS = ROOT / "artifacts"
SYSTEM_PROMPT_FILE = ARTIFACTS / "system_prompt.md"
TOOLS_FILE = ARTIFACTS / "tools.yaml"

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini"]
VERSIONS = ["v0", "v1", "v2", "v3", "v3new", "v4", "v5", "v6"]


def load_agent(provider_name: str) -> ResearchAgent:
    system_prompt = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
    declarations = load_tool_declarations(TOOLS_FILE)
    tools = to_openai_tools(declarations)
    provider = make_provider(provider_name)
    return ResearchAgent(provider, system_prompt=system_prompt, tools=tools)


def render_tool_call(call, result: dict) -> None:
    tool_name = call.name if hasattr(call, "name") else call.get("name", "unknown")
    with st.expander(f"🔧 `{tool_name}` — click to expand", expanded=False):
        st.markdown("**Args:**")
        args = call.args if hasattr(call, "args") else call.get("args", {})
        st.code(json.dumps(args, ensure_ascii=False, indent=2), language="json")
        st.markdown("**Result:**")
        items = result.get("result", result).get("items", [])
        if items:
            for item in items[:3]:
                title = item.get("title", "")
                url = item.get("url", "")
                summary = item.get("summary", "")[:200]
                source = item.get("source", "")
                st.markdown(f"- **{title}** ({source}){' — ' + summary if summary else ''}")
                if url:
                    st.markdown(f"  [{url}]({url})")
        else:
            st.code(json.dumps(result.get("result", result), ensure_ascii=False, indent=2)[:500], language="json")


def main() -> None:
    st.set_page_config(page_title="Research Agent", page_icon="🔍", layout="wide")
    st.title("🔍 Research Agent")
    st.caption("AI-powered research assistant with tool calling")

    # Sidebar config
    with st.sidebar:
        st.header("⚙️ Config")
        provider_name = st.selectbox("Provider", PROVIDERS, index=0)
        st.divider()
        st.markdown("**Tools loaded:**")
        for name in TOOL_FUNCTIONS:
            st.markdown(f"- `{name}`")
        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.history = []
            st.rerun()

    # Session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "history" not in st.session_state:
        st.session_state.history = []

    # Render existing messages
    for msg in st.session_state.messages:
        role = msg["role"]
        with st.chat_message(role):
            if role == "assistant":
                if msg.get("tool_calls"):
                    for tc, tr in zip(msg["tool_calls"], msg["tool_results"]):
                        render_tool_call(tc, tr)
                if msg.get("text"):
                    st.markdown(msg["text"])
            else:
                st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Nhập câu hỏi nghiên cứu...")
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.history.append({"role": "user", "content": user_input})

        # Run agent
        with st.chat_message("assistant"):
            with st.spinner("Đang xử lý..."):
                try:
                    agent = load_agent(provider_name)
                    run = agent.run(st.session_state.history)
                except Exception as exc:
                    st.error(f"Lỗi: {exc}")
                    st.stop()

            # Show tool calls
            tool_calls_data = []
            tool_results_data = []
            for tc, tr in zip(run.tool_calls, run.tool_results):
                render_tool_call(tc, tr)
                tool_calls_data.append({"name": tc.name, "args": tc.args})
                tool_results_data.append(tr)

            # Show text response
            if run.text:
                st.markdown(run.text)

        # Save to session
        st.session_state.messages.append({
            "role": "assistant",
            "tool_calls": run.tool_calls,
            "tool_results": run.tool_results,
            "text": run.text,
        })

        # Build assistant history message
        assistant_content = run.text or ""
        st.session_state.history.append({"role": "assistant", "content": assistant_content})


if __name__ == "__main__":
    main()
