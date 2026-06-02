from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "opencode"]
VERSIONS = ["v0", "v1", "v2", "v3"]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def json_text(value, max_chars: int = 24000) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    return text[:max_chars] + "\n...<truncated>" if len(text) > max_chars else text


def execute_tool_call(call: ToolCall) -> dict:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {"tool": call.name, "args": call.args, "result": {"error": "unknown_tool"}}
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


def tool_results_message(events: list[dict]) -> dict:
    return {
        "role": "user",
        "content": (
            "TOOL_RESULTS_JSON:\n"
            f"{json_text(events)}\n\n"
            "Use only these tool results. If the user asked for a digest and the items are ready, "
            "call the formatting tool. Otherwise answer the user directly with cited sources when available."
        ),
    }


def assistant_tool_message(response_text: str | None, calls: list[ToolCall]) -> dict:
    call_summary = [{"name": c.name, "args": c.args} for c in calls]
    content = response_text or "I will call the selected tool(s)."
    return {"role": "assistant", "content": f"{content}\n\nTOOL_CALLS_JSON:\n{json_text(call_summary)}"}


def run_model_tool_loop(*, provider, messages, tools, model, max_tool_rounds=4):
    working_messages = list(messages)
    rounds = []
    all_tool_events = []

    for round_index in range(1, max_tool_rounds + 1):
        response = provider.complete(working_messages, tools, model=model, temperature=0.0)
        calls = response.tool_calls
        round_record = {
            "round": round_index,
            "assistant_text": response.text,
            "tool_calls": [{"name": c.name, "args": c.args} for c in calls],
            "tool_results": [],
        }

        if not calls:
            rounds.append(round_record)
            return {"status": "answered", "assistant_text": response.text or "", "rounds": rounds, "tool_events": all_tool_events}

        working_messages.append(assistant_tool_message(response.text, calls))
        non_clarification_events = []

        for call in calls:
            event = execute_tool_call(call)
            round_record["tool_results"].append(event)
            all_tool_events.append(event)

            result = event.get("result", {})
            if isinstance(result, dict) and result.get("awaiting_user"):
                question = result.get("question") or call.args.get("question") or "Please provide more info."
                rounds.append(round_record)
                return {"status": "waiting_for_user", "assistant_text": question, "rounds": rounds, "tool_events": all_tool_events}

            non_clarification_events.append(event)

        rounds.append(round_record)
        working_messages.append(tool_results_message(non_clarification_events))

    return {"status": "max_tool_rounds", "assistant_text": f"Stopped after {max_tool_rounds} tool rounds.", "rounds": rounds, "tool_events": all_tool_events}


def write_transcript(path: Path, transcript: dict):
    transcript["updated_at"] = now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


# --- Streamlit UI ---

st.set_page_config(page_title="Research Agent", page_icon="🔍", layout="wide")
st.title("🔍 Research Agent")

# Sidebar config
with st.sidebar:
    st.header("Config")
    provider_name = st.selectbox("Provider", PROVIDERS)
    version = st.selectbox("Version", VERSIONS)
    model = st.text_input("Model (optional)", placeholder="default")
    max_rounds = st.slider("Max tool rounds", 1, 8, 4)

    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.transcript_turns = []
        st.rerun()

    st.divider()
    st.caption("Artifacts")
    st.code(f"system_prompt.md\nversion: {version}")

# Init session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "transcript_turns" not in st.session_state:
    st.session_state.transcript_turns = []
if "provider" not in st.session_state or st.session_state.get("provider_name") != provider_name:
    try:
        st.session_state.provider = make_provider(provider_name)
        st.session_state.provider_name = provider_name
    except Exception as e:
        st.error(f"Provider init failed: {e}")
        st.stop()

# Load artifacts
system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
openai_tools = to_openai_tools(tool_declarations)
artifact_version = build_artifact_version(version, ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tools_used" in msg and msg["tools_used"]:
            with st.expander("🔧 Tool calls"):
                for t in msg["tools_used"]:
                    st.code(f"{t['name']}({json.dumps(t['args'], ensure_ascii=False)})", language="python")
                    st.json(t["result"])

# Chat input
if user_input := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build messages for model
    trim_window = 5
    history_msgs = st.session_state.history[-trim_window * 2:]
    model_messages = [
        {"role": "system", "content": system_prompt},
        *history_msgs,
        {"role": "user", "content": user_input},
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = run_model_tool_loop(
                    provider=st.session_state.provider,
                    messages=model_messages,
                    tools=openai_tools,
                    model=model or None,
                    max_tool_rounds=max_rounds,
                )
                assistant_text = result["assistant_text"]
                tools_used = []
                for r in result.get("rounds", []):
                    for i, tc in enumerate(r.get("tool_calls", [])):
                        tool_result = r["tool_results"][i]["result"] if i < len(r["tool_results"]) else {}
                        tools_used.append({"name": tc["name"], "args": tc["args"], "result": tool_result})

                st.markdown(assistant_text)
                if tools_used:
                    with st.expander("🔧 Tool calls"):
                        for t in tools_used:
                            st.code(f"{t['name']}({json.dumps(t['args'], ensure_ascii=False)})", language="python")
                            st.json(t["result"])

                st.session_state.messages.append({"role": "assistant", "content": assistant_text, "tools_used": tools_used})
                st.session_state.history.append({"role": "user", "content": user_input})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})

                # Transcript turn
                turn = {
                    "turn_index": len(st.session_state.transcript_turns) + 1,
                    "started_at": now_iso(),
                    "user": user_input,
                    "status": result.get("status", "answered"),
                    "assistant_text": assistant_text,
                    "rounds": result.get("rounds", []),
                    "tool_events": result.get("tool_events", []),
                }
                st.session_state.transcript_turns.append(turn)

            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}", "tools_used": []})

# Transcript download
if st.session_state.transcript_turns:
    st.sidebar.divider()
    st.sidebar.header("Transcript")
    transcript = {
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model or "default",
        "turns": st.session_state.transcript_turns,
        "created_at": now_iso(),
    }
    transcript_json = json.dumps(transcript, ensure_ascii=False, indent=2, default=str)
    st.sidebar.download_button(
        "📥 Download transcript",
        data=transcript_json,
        file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True,
    )
    st.sidebar.caption(f"Turns: {len(st.session_state.transcript_turns)}")
