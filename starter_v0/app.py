"""
Streamlit UI for the Research Agent.
Run:  streamlit run app.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

# ── paths & env ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

# Re-use the core loop from chat.py so behaviour stays identical to CLI.
from chat import (
    execute_tool_call,
    assistant_tool_message,
    tool_results_message,
    write_transcript,
    now_iso,
    safe_slug,
    json_text,
    trim_history,
)


# ── helpers ──────────────────────────────────────────────────────────────────
PROVIDERS = ["openrouter", "openai", "anthropic", "gemini"]

PROVIDER_DEFAULT_MODELS = {
    "openrouter": "openai/gpt-4o-mini",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "gemini": "gemini-2.0-flash",
}


def init_session_state() -> None:
    """Ensure every key we read later already exists."""
    defaults = {
        "messages": [],          # chat history displayed in UI
        "raw_history": [],       # raw user/assistant pairs for context window
        "turn_index": 0,
        "transcript": None,
        "transcript_path": None,
        "provider_obj": None,
        "openai_tools": None,
        "system_prompt": None,
        "artifact_version": None,
        "provider_name": None,
        "model": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def build_transcript(version: str, provider_name: str, model: str) -> dict:
    ts = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    tid = "_".join([safe_slug(version), safe_slug(provider_name), ts])
    path = ROOT / "transcripts" / f"{tid}.transcript.json"
    av = st.session_state.artifact_version
    transcript = {
        "transcript_id": tid,
        **artifact_version_dict(av),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
        "tools": str(ARTIFACTS_DIR / "tools.yaml"),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, path


# ── run the agent (adapted from chat.run_model_tool_loop) ────────────────────
def run_agent(user_text: str) -> str:
    """Send *user_text* through the model↔tool loop and return the assistant reply."""
    provider = st.session_state.provider_obj
    tools = st.session_state.openai_tools
    model = st.session_state.model
    system_prompt = st.session_state.system_prompt
    max_tool_rounds = st.session_state.get("max_tool_rounds", 4)
    history_window = st.session_state.get("history_window", 5)

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.raw_history, history_window),
        {"role": "user", "content": user_text},
    ]

    working_messages = list(messages)
    all_tool_events: list[dict] = []

    for round_idx in range(1, max_tool_rounds + 1):
        response = provider.complete(working_messages, tools, model=model, temperature=0.0)
        calls = response.tool_calls

        # display assistant text (if any) in the chat
        if response.text:
            st.chat_message("assistant").markdown(response.text)

        if not calls:
            # no tool calls → final answer
            return response.text or ""

        # show each tool call in an expander
        for call in calls:
            with st.expander(f"🔧 `{call.name}`({json.dumps(call.args, ensure_ascii=False, sort_keys=True)})", expanded=False):
                event = execute_tool_call(call)
                all_tool_events.append(event)
                st.json(event["result"])

                # detect clarification tool
                result = event.get("result", {})
                if isinstance(result, dict) and result.get("awaiting_user"):
                    question = result.get("question") or call.args.get("question") or "Bạn bổ sung thêm thông tin nhé."
                    return question

        # feed non-clarification events back to the model
        non_clar = [e for e in all_tool_events if not (
            isinstance(e.get("result"), dict) and e["result"].get("awaiting_user")
        )]
        working_messages.append(assistant_tool_message(response.text, calls))
        working_messages.append(tool_results_message(non_clar))

    return f"Stopped after {max_tool_rounds} tool rounds."


# ── Streamlit layout ─────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(page_title="Research Agent", page_icon="🔬", layout="wide")
    init_session_state()

    # ── sidebar: config ──────────────────────────────────────────────────────
    with st.sidebar:
        st.title("⚙️ Config")

        provider_name = st.selectbox("Provider", PROVIDERS, index=0)
        default_model = PROVIDER_DEFAULT_MODELS.get(provider_name, "")
        model = st.text_input("Model", value=default_model, help="Leave blank for provider default.")
        version = st.text_input("Version label", value="v0", help="e.g. v0, v1, v2 — used in transcript filenames.")
        system_prompt_path = st.text_input("System prompt", value=str(ARTIFACTS_DIR / "system_prompt.md"))
        tools_yaml_path = st.text_input("Tools YAML", value=str(ARTIFACTS_DIR / "tools.yaml"))

        st.divider()
        history_window = st.slider("History window (pairs)", 0, 20, 5)
        max_tool_rounds = st.slider("Max tool rounds", 1, 10, 4)
        st.session_state["history_window"] = history_window
        st.session_state["max_tool_rounds"] = max_tool_rounds

        st.divider()
        if st.button("🔄 New chat", use_container_width=True):
            # save current transcript before reset
            if st.session_state.transcript and st.session_state.transcript_path:
                write_transcript(st.session_state.transcript_path, st.session_state.transcript)
            for k in ["messages", "raw_history", "turn_index", "transcript", "transcript_path"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        if st.button("✅ Initialise / Apply", use_container_width=True, type="primary"):
            try:
                sp = Path(system_prompt_path).read_text(encoding="utf-8")
                td = load_tool_declarations(Path(tools_yaml_path))
                ot = to_openai_tools(td)
                prov = make_provider(provider_name)
                av = build_artifact_version(version, Path(system_prompt_path), Path(tools_yaml_path))

                st.session_state.system_prompt = sp
                st.session_state.provider_obj = prov
                st.session_state.openai_tools = ot
                st.session_state.artifact_version = av
                st.session_state.provider_name = provider_name
                st.session_state.model = model or getattr(prov, "default_model", None)

                # build transcript
                transcript, tpath = build_transcript(version, provider_name, model)
                st.session_state.transcript = transcript
                st.session_state.transcript_path = tpath

                st.success(f"Ready — artifact_version=`{av.artifact_version}`")
            except Exception as exc:
                st.error(f"Init failed: {exc}")

        # show transcript info
        if st.session_state.transcript_path:
            st.caption(f"Transcript: `{st.session_state.transcript_path.name}`")

    # ── main area: chat ──────────────────────────────────────────────────────
    st.title("🔬 Research Agent")
    st.caption("Prompt Engineering & Tool Calling Lab — Day04 C401")

    # not yet initialised
    if st.session_state.provider_obj is None:
        st.info("👈 Configure and click **Initialise / Apply** in the sidebar to start chatting.")
        return

    # display existing messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # user input
    user_text = st.chat_input("Nhập tin nhắn…")
    if not user_text:
        return

    # display user message
    st.session_state.messages.append({"role": "user", "content": user_text})
    st.chat_message("user").markdown(user_text)

    # run agent
    st.session_state.turn_index += 1
    try:
        reply = run_agent(user_text)
    except Exception as exc:
        reply = f"❌ Error: `{type(exc).__name__}: {exc}`"

    # display assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").markdown(reply)

    # update raw history for context window
    st.session_state.raw_history.append({"role": "user", "content": user_text})
    st.session_state.raw_history.append({"role": "assistant", "content": reply})

    # append turn to transcript & save
    if st.session_state.transcript is not None:
        st.session_state.transcript["turns"].append({
            "turn_index": st.session_state.turn_index,
            "started_at": now_iso(),
            "ended_at": now_iso(),
            "user": user_text,
            "status": "answered",
            "assistant_text": reply,
        })
        st.session_state.transcript["updated_at"] = now_iso()
        write_transcript(st.session_state.transcript_path, st.session_state.transcript)


if __name__ == "__main__":
    main()
