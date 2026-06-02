from __future__ import annotations

import streamlit as st
import json
import re
import os
import hashlib
import yaml
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Any

# Resolve paths
ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"

# Load environment variables
from env_loader import load_lab_env
load_lab_env(ROOT)

from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version, artifact_version_dict, ArtifactVersion
from chat import execute_tool_call, now_iso, safe_slug, trim_history, assistant_tool_message, tool_results_message, write_transcript

def log_debug(message: str):
    log_path = Path("/home/henry/.gemini/antigravity/scratch/agent_debug.log")
    timestamp = datetime.now().isoformat()
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass

# Helper to calculate string hash
def calculate_string_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# Helper to load tool names and types dynamically
def parse_tools_list(tools_yaml: str) -> list[str]:
    try:
        data = yaml.safe_load(tools_yaml)
        return [t["name"] for t in data.get("tools", [])]
    except Exception:
        return []

# Set page layout & styling
st.set_page_config(
    page_title="Research Agent Playpen",
    page_icon="\U0001f916",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern premium design
st.markdown("""
<style>
    /* Styling for glassmorphism & gradients */
    .main-header {
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .badge {
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .badge-primary { background-color: #e0e7ff; color: #4338ca; }
    .badge-secondary { background-color: #f3f4f6; color: #374151; }
    .badge-success { background-color: #d1fae5; color: #065f46; }
    .badge-warning { background-color: #fef3c7; color: #92400e; }
    
    /* Interactive Card styling */
    .tool-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* System message background */
    .system-msg {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 0.75rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    
    /* Dark mode adjustments if detected */
    @media (prefers-color-scheme: dark) {
        .tool-card {
            background-color: #1e293b;
            border-color: #334155;
        }
        .system-msg {
            background-color: #064e3b;
            border-left-color: #10b981;
        }
        .sub-header {
            color: #94a3b8;
        }
    }
</style>
""", unsafe_allow_html=True)

# Background Agent Execution Thread
def run_agent_thread(
    provider_option: str,
    model_override: str,
    system_prompt: str,
    tools_yaml: str,
    messages: list[dict[str, str]],
    max_tool_rounds: int,
    history_window: int,
    result_holder: dict[str, Any]
):
    log_debug("--- Thread Started ---")
    log_debug(f"Provider: {provider_option}, Model Override: {model_override}")
    log_debug(f"Messages count: {len(messages)}")
    try:
        # Parse tools
        declarations = yaml.safe_load(tools_yaml)["tools"]
        openai_tools = to_openai_tools(declarations)
        log_debug("Tools parsed successfully.")

        log_debug(f"Calling make_provider({provider_option})")
        provider = make_provider(provider_option)
        model = model_override if model_override.strip() else None
        log_debug(f"Provider initialized. Default model: {getattr(provider, 'default_model', None)}. Override model: {model}")
        
        # Log key presence
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            log_debug(f"GEMINI_API_KEY is configured. Length: {len(api_key)}. Preview: {api_key[:6]}...{api_key[-4:]}")
        else:
            log_debug("GEMINI_API_KEY is NOT set in os.environ!")
        
        rounds = []
        all_tool_events = []
        working_messages = list(messages)
        
        for round_idx in range(1, max_tool_rounds + 1):
            if result_holder.get("aborted"):
                log_debug(f"Round {round_idx}: Aborted flag detected.")
                break
                
            result_holder["current_status_msg"] = f"\u23f3 **Round {round_idx}**: Requesting model response..."
            log_debug(f"Round {round_idx}: Calling provider.complete...")
            
            response = provider.complete(working_messages, openai_tools, model=model, temperature=0.0)
            
            log_debug(f"Round {round_idx}: provider.complete returned. Text: {response.text[:50] if response.text else 'None'}, Tool calls: {len(response.tool_calls)}")
                
            if result_holder.get("aborted"):
                log_debug(f"Round {round_idx}: Aborted flag detected after complete.")
                break
                
            calls = response.tool_calls
            round_record = {
                "round": round_idx,
                "assistant_text": response.text,
                "tool_calls": [{"name": call.name, "args": call.args} for call in calls],
                "tool_results": [],
            }
            
            if not calls:
                log_debug(f"Round {round_idx}: No tool calls generated. Exiting loop.")
                rounds.append(round_record)
                result_holder["status"] = "answered"
                result_holder["assistant_text"] = response.text or ""
                result_holder["rounds"] = rounds
                result_holder["tool_events"] = all_tool_events
                log_debug("Thread finished: answered.")
                return
                
            working_messages.append(assistant_tool_message(response.text, calls))
            non_clarification_events = []
            
            for call in calls:
                if result_holder.get("aborted"):
                    break
                    
                result_holder["current_status_msg"] = f"\U0001f527 **Round {round_idx}**: Running tool `{call.name}`..."
                log_debug(f"Round {round_idx}: Running tool: {call.name}({json.dumps(call.args, ensure_ascii=False)})")
                event = execute_tool_call(call)
                round_record["tool_results"].append(event)
                all_tool_events.append(event)
                
                result = event.get("result", {})
                log_debug(f"Round {round_idx}: Tool {call.name} returned: {json.dumps(result, ensure_ascii=False)[:100]}")
                
                if isinstance(result, dict) and result.get("awaiting_user"):
                    question = result.get("question") or call.args.get("question") or "B\u1ea1n b\u1ed5 sung th\xeam th\xf4ng tin nh\xe9."
                    rounds.append(round_record)
                    result_holder["status"] = "waiting_for_user"
                    result_holder["assistant_text"] = question
                    result_holder["rounds"] = rounds
                    result_holder["tool_events"] = all_tool_events
                    result_holder["clarify_details"] = {
                        "response_type": result.get("response_type", "text"),
                        "options": result.get("options", [])
                    }
                    log_debug("Thread paused: waiting_for_user (clarify).")
                    return
                    
                if call.name == "send" and isinstance(result, dict) and result.get("status") == "needs_confirmation":
                    rounds.append(round_record)
                    result_holder["status"] = "waiting_for_confirmation"
                    result_holder["assistant_text"] = f"B\u1ea1n c\xf3 \u0111\u1ed3ng \xfd g\u1eedi n\u1ed9i dung n\xe0y l\xean Telegram kh\xf4ng?\n\nN\u1ed9i dung: {call.args.get('text', '')}"
                    result_holder["rounds"] = rounds
                    result_holder["tool_events"] = all_tool_events
                    result_holder["send_text"] = call.args.get('text', '')
                    log_debug("Thread paused: waiting_for_confirmation (send).")
                    return
                    
                non_clarification_events.append(event)
                
            if result_holder.get("aborted"):
                break
                
            rounds.append(round_record)
            working_messages.append(tool_results_message(non_clarification_events))
            
        if result_holder.get("aborted"):
            result_holder["status"] = "aborted"
            log_debug("Thread terminated: aborted.")
            return
            
        result_holder["status"] = "max_tool_rounds"
        result_holder["assistant_text"] = f"Stopped after {max_tool_rounds} tool rounds."
        result_holder["rounds"] = rounds
        result_holder["tool_events"] = all_tool_events
        log_debug("Thread finished: max_tool_rounds.")
        
    except Exception as e:
        import traceback
        log_debug(f"Exception inside thread: {e}\n{traceback.format_exc()}")
        result_holder["status"] = "error"
        result_holder["error_msg"] = f"Exception inside execution thread: {str(e)}\n\n{traceback.format_exc()}"

def start_agent_execution(
    user_query: str,
    provider_option: str,
    model_override: str,
    system_prompt_val: str,
    tools_yaml_val: str,
    max_tool_rounds: int,
    history_window: int
):
    # Construct trimmed messages matching history_window
    history = []
    for msg in st.session_state.messages[:-1]: # exclude the newly appended user message
        if msg["role"] in ["user", "assistant"]:
            history.append({"role": msg["role"], "content": msg["content"]})
            
    trimmed = trim_history(history, history_window)
    messages = [
        {"role": "system", "content": system_prompt_val},
        *trimmed,
        {"role": "user", "content": user_query}
    ]

    st.session_state.result_holder = {
        "status": "running",
        "current_status_msg": "Initializing agent...",
        "rounds": [],
        "tool_events": [],
        "aborted": False
    }
    st.session_state.agent_running = True
    st.session_state.started_at = now_iso()
    st.session_state.user_query = user_query
    
    # Start thread
    thread = threading.Thread(
        target=run_agent_thread,
        args=(
            provider_option,
            model_override,
            system_prompt_val,
            tools_yaml_val,
            messages,
            max_tool_rounds,
            history_window,
            st.session_state.result_holder
        )
    )
    st.session_state.agent_thread = thread
    thread.start()

# Helper function to write to temp files for versioning if needed
def update_temp_files(prompt_val: str, tools_val: str) -> tuple[Path, Path]:
    temp_dir = ROOT / "runs" / ".temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    prompt_temp = temp_dir / "system_prompt_temp.md"
    tools_temp = temp_dir / "tools_temp.yaml"
    prompt_temp.write_text(prompt_val, encoding="utf-8")
    tools_temp.write_text(tools_val, encoding="utf-8")
    return prompt_temp, tools_temp

# Sidebar config setup
st.sidebar.title("\U0001f6e0\ufe0f Configuration")

# Provider selection helper
api_keys_status = {
    "Gemini": "GEMINI_API_KEY" in os.environ or os.getenv("GEMINI_API_KEY"),
    "OpenRouter": "OPENROUTER_API_KEY" in os.environ or os.getenv("OPENROUTER_API_KEY"),
    "OpenAI": "OPENAI_API_KEY" in os.environ or os.getenv("OPENAI_API_KEY"),
    "Anthropic": "ANTHROPIC_API_KEY" in os.environ or os.getenv("ANTHROPIC_API_KEY")
}

# Determine default provider
available_providers = []
for name, is_set in api_keys_status.items():
    if is_set:
        available_providers.append(name.lower())

if not available_providers:
    available_providers = ["gemini", "openrouter", "openai", "anthropic"]

provider_option = st.sidebar.selectbox(
    "Select API Provider",
    options=["gemini", "openrouter", "openai", "anthropic"],
    index=["gemini", "openrouter", "openai", "anthropic"].index(
        available_providers[0] if available_providers else "gemini"
    )
)

model_override = st.sidebar.text_input(
    "Model Override (Optional)",
    value="",
    placeholder="e.g. gemini-2.5-flash or leave blank for default"
)

version_label = st.sidebar.text_input(
    "Version Label",
    value="v3",
    help="Label used for versioning and transcripts, e.g. v0, v1, v2, v3"
)

max_tool_rounds = st.sidebar.slider(
    "Max Tool Rounds",
    min_value=1,
    max_value=10,
    value=4
)

history_window = st.sidebar.slider(
    "History Window Size",
    min_value=1,
    max_value=15,
    value=5,
    help="Number of user-assistant message pairs to keep in context window"
)

# Load defaults for system prompt and tools
default_prompt = ""
prompt_file_path = ARTIFACTS_DIR / "system_prompt.md"
if prompt_file_path.exists():
    default_prompt = prompt_file_path.read_text(encoding="utf-8")

default_tools_yaml = ""
tools_file_path = ARTIFACTS_DIR / "tools.yaml"
if tools_file_path.exists():
    default_tools_yaml = tools_file_path.read_text(encoding="utf-8")

st.sidebar.markdown("---")
st.sidebar.subheader("\U0001f4dd Live Artifact Editor")

system_prompt_val = st.sidebar.text_area(
    "System Prompt",
    value=default_prompt,
    height=200,
    help="Edit system instructions live. Use save buttons below to persist to files."
)

tools_yaml_val = st.sidebar.text_area(
    "Tools YAML",
    value=default_tools_yaml,
    height=200,
    help="Edit tool declarations live."
)

# Save buttons
col1, col2 = st.sidebar.columns(2)
if col1.button("\U0001f4be Save Prompt", help="Save changes to system_prompt.md"):
    try:
        prompt_file_path.write_text(system_prompt_val, encoding="utf-8")
        st.sidebar.success("Saved system_prompt.md!")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

if col2.button("\U0001f4be Save Tools", help="Save changes to tools.yaml"):
    try:
        tools_file_path.write_text(tools_yaml_val, encoding="utf-8")
        st.sidebar.success("Saved tools.yaml!")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

if st.sidebar.button("\U0001f9f9 Clear Chat History", type="secondary"):
    st.session_state.messages = []
    st.session_state.clarify_active = None
    st.session_state.send_confirmation_active = None
    st.session_state.transcript_id = None
    st.session_state.agent_running = False
    st.session_state.agent_thread = None
    st.session_state.result_holder = {}
    st.rerun()

# Build Version Object based on live edit values
p_temp, t_temp = update_temp_files(system_prompt_val, tools_yaml_val)
artifact_version = build_artifact_version(version_label, p_temp, t_temp)

# Main UI layout
st.markdown("<h1 class='main-header'>\U0001f916 Research Agent Interface</h1>", unsafe_allow_html=True)
st.markdown(
    f"<div class='sub-header'>Interactive web sandbox for running and testing prompt iterations.</div>",
    unsafe_allow_html=True
)

# Display active version metrics
st.markdown(
    f"""
    <div style='display:flex; flex-wrap:wrap; margin-bottom:1.5rem;'>
        <span class='badge badge-primary'>\U0001f3f7\ufe0f Version: {artifact_version.version}</span>
        <span class='badge badge-secondary'>\U0001f527 Hash Prompt: {artifact_version.prompt_hash[:12]}</span>
        <span class='badge badge-secondary'>\u2699\ufe0f Hash Tools: {artifact_version.tools_hash[:12]}</span>
        <span class='badge badge-success'>\U0001f50c Provider: {provider_option}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "clarify_active" not in st.session_state:
    st.session_state.clarify_active = None
if "send_confirmation_active" not in st.session_state:
    st.session_state.send_confirmation_active = None
if "transcript_id" not in st.session_state:
    st.session_state.transcript_id = None
if "agent_running" not in st.session_state:
    st.session_state.agent_running = False
if "agent_thread" not in st.session_state:
    st.session_state.agent_thread = None
if "result_holder" not in st.session_state:
    st.session_state.result_holder = {}
if "started_at" not in st.session_state:
    st.session_state.started_at = None
if "user_query" not in st.session_state:
    st.session_state.user_query = None

# Set up transcripts setup
transcripts_dir = ROOT / "transcripts"
if not st.session_state.transcript_id:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    st.session_state.transcript_id = "_".join([
        safe_slug(version_label),
        safe_slug(provider_option),
        timestamp,
    ])

transcript_path = transcripts_dir / f"{st.session_state.transcript_id}.transcript.json"

def get_base_transcript() -> dict[str, Any]:
    return {
        "transcript_id": st.session_state.transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_option,
        "model": model_override or None,
        "system_prompt": "live_edited",
        "tools": "live_edited",
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

# Read existing transcript if file exists
def load_or_init_transcript() -> dict[str, Any]:
    if transcript_path.exists():
        try:
            return json.loads(transcript_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return get_base_transcript()

# Update transcript in file
def save_transcript_turn(user_text: str, loop_result: dict[str, Any], turn_idx: int, started_at: str) -> None:
    transcript = load_or_init_transcript()
    
    turn_record = {
        "turn_index": turn_idx,
        "started_at": started_at,
        "user": user_text,
        "status": loop_result["status"],
        "assistant_text": loop_result["assistant_text"],
        "rounds": loop_result["rounds"],
        "tool_events": loop_result["tool_events"],
        "ended_at": now_iso()
    }
    
    transcript["turns"].append(turn_record)
    write_transcript(transcript_path, transcript)

# Render Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # If there are intermediate execution rounds for assistant, display them beautifully
        if msg["role"] == "assistant" and "rounds" in msg and msg["rounds"]:
            with st.expander("\U0001f6e0\ufe0f Tool Executions & Inner Dialogues", expanded=False):
                for r in msg["rounds"]:
                    st.markdown(f"### \U0001f504 Round {r['round']}")
                    if r.get("assistant_text"):
                        st.info(f"**Agent Thought:**\n{r['assistant_text']}")
                    
                    if r.get("tool_calls"):
                        st.markdown("**Tool Calls generated:**")
                        for tc in r["tool_calls"]:
                            st.code(f"Call {tc['name']}({json.dumps(tc['args'], ensure_ascii=False)})", language="python")
                    
                    if r.get("tool_results"):
                        st.markdown("**Execution Results:**")
                        for res in r["tool_results"]:
                            tool_name = res.get("tool")
                            tool_args = res.get("args")
                            tool_res = res.get("result")
                            
                            st.markdown(f"**`{tool_name}`** args: `{json.dumps(tool_args)}`:")
                            st.json(tool_res)
                    st.markdown("---")
        
        st.write(msg["content"])


# Polling and UI updates for running agent
if st.session_state.agent_running:
    # Render Stop Button in a nice prominent card
    if st.button("\U0001f6d1 Stop Agent", key="stop_agent_btn_active", type="primary", use_container_width=True):
        st.session_state.result_holder["aborted"] = True
        st.session_state.agent_running = False
        st.session_state.agent_thread = None
        st.warning("Agent execution stopped by user.")
        st.rerun()
        
    thread = st.session_state.agent_thread
    if thread and thread.is_alive():
        status_msg = st.session_state.result_holder.get("current_status_msg", "Processing...")
        st.info(f"\U0001f916 {status_msg}")
        # Wait a little and rerun to check again in the next cycle
        time.sleep(0.5)
        st.rerun()
        
    # Once the thread finishes
    st.session_state.agent_running = False
    res = st.session_state.result_holder
    
    if res.get("status") == "error":
        st.error(res.get("error_msg", "Unknown error"))
    elif res.get("status") == "aborted":
        st.warning("Agent execution was stopped.")
    else:
        # Process result
        turn_idx = len(st.session_state.messages) // 2 + 1
        save_transcript_turn(st.session_state.user_query, res, turn_idx, st.session_state.started_at)
        
        assistant_msg = {
            "role": "assistant",
            "content": res["assistant_text"],
            "rounds": res["rounds"]
        }
        st.session_state.messages.append(assistant_msg)
        
        if res["status"] == "waiting_for_user":
            st.session_state.clarify_active = res["clarify_details"]
        else:
            st.session_state.clarify_active = None
            
        if res["status"] == "waiting_for_confirmation":
            st.session_state.send_confirmation_active = {
                "text": res["send_text"]
            }
        else:
            st.session_state.send_confirmation_active = None
            
    st.rerun()

# ----------------- INPUT CONTROLS -----------------

# 1. Check if clarify tool is active
elif st.session_state.clarify_active:
    clarify_cfg = st.session_state.clarify_active
    st.warning("\u26a0\ufe0f **Agent needs clarification to proceed:**")
    
    if clarify_cfg["response_type"] == "yes_no":
        col1, col2 = st.columns(2)
        if col1.button("\u2705 Yes", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Yes"})
            st.session_state.clarify_active = None
            start_agent_execution("Yes", provider_option, model_override, system_prompt_val, tools_yaml_val, max_tool_rounds, history_window)
            st.rerun()
        if col2.button("\u274c No", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "No"})
            st.session_state.clarify_active = None
            start_agent_execution("No", provider_option, model_override, system_prompt_val, tools_yaml_val, max_tool_rounds, history_window)
            st.rerun()
            
    elif clarify_cfg["response_type"] == "choice" and clarify_cfg["options"]:
        # Render a button for each choice option
        st.markdown("**Please select an option:**")
        cols = st.columns(min(len(clarify_cfg["options"]), 4))
        for idx, option in enumerate(clarify_cfg["options"]):
            col = cols[idx % len(cols)]
            if col.button(option, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": option})
                st.session_state.clarify_active = None
                start_agent_execution(option, provider_option, model_override, system_prompt_val, tools_yaml_val, max_tool_rounds, history_window)
                st.rerun()
                
    else: # type text or fallback
        # Standard input text inside the warning
        with st.form("clarify_form"):
            response_text = st.text_input("Your Response:")
            submit_clarify = st.form_submit_button("Submit Response")
            if submit_clarify and response_text.strip():
                st.session_state.messages.append({"role": "user", "content": response_text})
                st.session_state.clarify_active = None
                start_agent_execution(response_text, provider_option, model_override, system_prompt_val, tools_yaml_val, max_tool_rounds, history_window)
                st.rerun()

# 2. Check if send confirmation is active
elif st.session_state.send_confirmation_active:
    send_cfg = st.session_state.send_confirmation_active
    st.info("\U0001f4e8 **Confirmation Required:** The agent wants to send a Telegram message.")
    st.code(send_cfg["text"], language="markdown")
    
    col1, col2 = st.columns(2)
    if col1.button("\u2705 Confirm Send", type="primary", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "C\xf3, h\xe3y g\u1eedi \u0111i"})
        st.session_state.send_confirmation_active = None
        start_agent_execution("C\xf3, h\xe3y g\u1eedi \u0111i", provider_option, model_override, system_prompt_val, tools_yaml_val, max_tool_rounds, history_window)
        st.rerun()
    if col2.button("\u274c Cancel / Decline", type="secondary", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Kh\xf4ng, \u0111\u1eebng g\u1eedi"})
        st.session_state.send_confirmation_active = None
        start_agent_execution("Kh\xf4ng, \u0111\u1eebng g\u1eedi", provider_option, model_override, system_prompt_val, tools_yaml_val, max_tool_rounds, history_window)
        st.rerun()

# 3. Standard Chat Input
else:
    user_query = st.chat_input("Enter your research query here...")
    if user_query:
        # Append user query to messages and rerun agent
        st.session_state.messages.append({"role": "user", "content": user_query})
        start_agent_execution(user_query, provider_option, model_override, system_prompt_val, tools_yaml_val, max_tool_rounds, history_window)
        st.rerun()

st.markdown("---")
if st.checkbox("\U0001f41e Show Debug Panel"):
    st.subheader("Session State Debugger")
    st.write("agent_running:", st.session_state.agent_running)
    st.write("result_holder:", st.session_state.result_holder)
    st.write("clarify_active:", st.session_state.clarify_active)
    st.write("send_confirmation_active:", st.session_state.send_confirmation_active)
    
    st.subheader("Agent Debug Log (agent_debug.log)")
    log_path = Path("/home/henry/.gemini/antigravity/scratch/agent_debug.log")
    if log_path.exists():
        try:
            logs = log_path.read_text(encoding="utf-8")
            lines = logs.splitlines()[-40:]
            st.code("\n".join(lines), language="text")
        except Exception as e:
            st.error(f"Error reading log: {e}")
    else:
        st.write("No debug logs found.")
