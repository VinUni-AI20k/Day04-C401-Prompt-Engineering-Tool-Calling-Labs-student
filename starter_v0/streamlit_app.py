from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


PROVIDERS = ["anthropic", "openai", "openrouter", "gemini"]


def reset_chat() -> None:
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.transcript = None
    st.session_state.transcript_path = None
    st.session_state.config_key = None


def init_state() -> None:
    defaults = {
        "history": [],
        "turns": [],
        "transcript": None,
        "transcript_path": None,
        "config_key": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_runtime(provider_name: str, version: str, model_override: str | None) -> dict[str, Any]:
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    provider = make_provider(provider_name)
    selected_model = model_override or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)

    return {
        "system_prompt_path": system_prompt_path,
        "tools_path": tools_path,
        "system_prompt": system_prompt,
        "tools": to_openai_tools(tool_declarations),
        "provider": provider,
        "selected_model": selected_model,
        "model_arg": model_override,
        "artifact_version": artifact_version,
    }


def ensure_transcript(
    *,
    provider_name: str,
    version: str,
    selected_model: str | None,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
    artifact_version: Any,
) -> None:
    config_key = (provider_name, version, selected_model, history_window, max_tool_rounds)
    if st.session_state.transcript is not None:
        return

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])
    transcript_path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"
    st.session_state.transcript_path = transcript_path
    st.session_state.config_key = config_key
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def write_current_transcript(turn_record: dict[str, Any]) -> None:
    st.session_state.turns.append(turn_record)
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])

    with st.chat_message("assistant"):
        if turn.get("status") == "provider_error":
            st.error(turn.get("error", "Provider error"))
        else:
            st.markdown(turn.get("assistant_text") or "")

        rounds = turn.get("rounds", [])
        if rounds:
            for round_record in rounds:
                label = f"Tool round {round_record.get('round', '?')}"
                with st.expander(label):
                    st.write("Tool calls")
                    st.json(round_record.get("tool_calls", []))
                    st.write("Tool results")
                    st.json(round_record.get("tool_results", []))


def main() -> None:
    st.set_page_config(page_title="Research Agent", layout="wide")
    init_state()

    st.title("Research Agent")
    st.caption("Tool-calling research assistant UI for the Day04 lab.")

    with st.sidebar:
        st.header("Settings")
        provider_name = st.selectbox("Provider", PROVIDERS, index=0)
        version = st.text_input("Version", value="v3")
        model_input = st.text_input("Model override", value="")
        model_override = model_input.strip() or None
        history_window = st.number_input("History window", min_value=0, max_value=20, value=5, step=1)
        max_tool_rounds = st.number_input("Max tool rounds", min_value=1, max_value=10, value=4, step=1)
        if st.button("Reset chat", use_container_width=True):
            reset_chat()
            st.rerun()

    runtime = load_runtime(provider_name, version, model_override)
    current_key = (provider_name, version, runtime["selected_model"], history_window, max_tool_rounds)
    if st.session_state.config_key and st.session_state.config_key != current_key:
        st.warning("Settings changed. Click Reset chat to start a new transcript with these settings.")

    for turn in st.session_state.turns:
        render_turn(turn)

    user_text = st.chat_input("Ask the research agent...")
    if not user_text:
        if st.session_state.transcript_path:
            st.caption(f"Transcript: `{st.session_state.transcript_path}`")
        return

    ensure_transcript(
        provider_name=provider_name,
        version=version,
        selected_model=runtime["selected_model"],
        system_prompt_path=runtime["system_prompt_path"],
        tools_path=runtime["tools_path"],
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
        artifact_version=runtime["artifact_version"],
    )

    messages = [
        {"role": "system", "content": runtime["system_prompt"]},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]
    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.spinner("Running agent..."):
        try:
            result = run_model_tool_loop(
                provider=runtime["provider"],
                messages=messages,
                tools=runtime["tools"],
                model=runtime["model_arg"],
                max_tool_rounds=max_tool_rounds,
            )
            turn_record.update(result)
            st.session_state.history.append({"role": "user", "content": user_text})
            st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
        except Exception as exc:
            turn_record.update({
                "status": "provider_error",
                "error": f"{type(exc).__name__}: {str(exc)}",
            })

    turn_record["ended_at"] = now_iso()
    write_current_transcript(turn_record)
    st.rerun()


if __name__ == "__main__":
    main()
