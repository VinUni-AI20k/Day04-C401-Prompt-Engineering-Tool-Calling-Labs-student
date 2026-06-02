import sys
import json
import time
from datetime import datetime
from typing import Any
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import run_model_tool_loop, trim_history

ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def run_session(session_name: str, dialogue_turns: list[str | dict[str, str]]) -> None:
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    
    provider = make_provider("openrouter")
    selected_model = getattr(provider, "default_model", None)
    artifact_version = build_artifact_version("v3", system_prompt_path, tools_path)
    
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"v3_openrouter_{session_name}_{timestamp}"
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": "openrouter",
        "model": selected_model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    
    print(f"\n==========================================")
    print(f"Starting simulated chat session: {session_name}")
    print(f"==========================================")
    
    history: list[dict[str, str]] = []
    turn_index = 0
    
    for turn_input in dialogue_turns:
        turn_index += 1
        user_text = turn_input if isinstance(turn_input, str) else turn_input.get("content", "")
        
        print(f"\nYou> {user_text}")
        
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(history, 5),
            {"role": "user", "content": user_text},
        ]
        
        turn_record: dict[str, Any] = {
            "turn_index": turn_index,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }
        
        # Free-tier rate limit sleeping between prompts to avoid 429
        print("Sleeping 13s to avoid rate limit...", flush=True)
        time.sleep(13)
        
        try:
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=None,
                max_tool_rounds=4,
            )
            turn_record.update(result)
            assistant_text = result["assistant_text"]
            print(f"\nAgent> {assistant_text}")
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": assistant_text})
        except Exception as exc:
            turn_record.update({
                "status": "provider_error",
                "error": f"{type(exc).__name__}: {str(exc)}",
            })
            print(f"\nERROR> {turn_record['error']}")
            
        turn_record["ended_at"] = now_iso()
        transcript["turns"].append(turn_record)
        
        # Write intermediate transcript
        TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        
    transcript["updated_at"] = now_iso()
    transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nSaved transcript to: {transcript_path}")


def main():
    # Session 1: Research AI today (web and twitter)
    run_session(
        "session1_normal_research",
        ["Tin AI hôm nay có gì nổi bật? Tìm trên web và Twitter giúp mình"]
    )
    
    # Session 2: Summarize article (requires URL clarification)
    run_session(
        "session2_missing_info",
        [
            "Tóm tắt bài này hộ mình",
            "À đây, link là https://openai.com/news"
        ]
    )
    
    # Session 3: Post to Telegram (requires confirmation clarification)
    run_session(
        "session3_confirm_action",
        [
            "Đăng bản tin AI hôm nay lên Telegram giúp mình",
            "Có, xác nhận gửi đi"
        ]
    )


if __name__ == "__main__":
    main()
