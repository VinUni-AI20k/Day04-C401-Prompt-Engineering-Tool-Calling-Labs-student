from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version
from agent import ResearchAgent
from chat import run_model_tool_loop

# Initialize environment
ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

app = FastAPI(title="Research Agent Interface", description="Day 04 Research Agent Lab Web UI")

# Setup directories
STATIC_DIR = ROOT / "static"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# Mount static and templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = []
    provider: str = "gemini"
    version: str = "v3"
    model: str | None = None


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    # Load version log if available to display metadata on UI
    version_log_path = ARTIFACTS_DIR / "version_log.csv"
    versions = []
    if version_log_path.exists():
        try:
            lines = version_log_path.read_text(encoding="utf-8").splitlines()
            if len(lines) > 1:
                headers = lines[0].split(",")
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split(",")
                        if len(parts) >= len(headers):
                            versions.append(dict(zip(headers, parts)))
        except Exception:
            pass
            
    return templates.TemplateResponse(
        request,
        "index.html",
        {"versions": versions, "default_version": "v3"}
    )


@app.post("/api/chat")
async def post_chat(payload: ChatRequest):
    try:
        # Load system prompt and tools based on the selected version
        system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        tools_path = ARTIFACTS_DIR / "tools.yaml"
        
        if not system_prompt_path.exists():
            raise HTTPException(status_code=500, detail="System prompt file not found")
        if not tools_path.exists():
            raise HTTPException(status_code=500, detail="Tools configuration file not found")
            
        system_prompt = system_prompt_path.read_text(encoding="utf-8")
        tool_declarations = load_tool_declarations(tools_path)
        openai_tools = to_openai_tools(tool_declarations)
        
        # Build provider
        provider_name = payload.provider.lower()
        try:
            provider = make_provider(provider_name)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        selected_model = payload.model or getattr(provider, "default_model", None)
        artifact_version = build_artifact_version(payload.version, system_prompt_path, tools_path)
        
        # Prepare messages
        # We keep history pairs User/Assistant
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        # Trim history if too long (last 10 messages)
        history_window = payload.history[-10:] if payload.history else []
        for msg in history_window:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        # Append current user text
        messages.append({"role": "user", "content": payload.message})
        
        # Run model-tool loop
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=payload.model,
            max_tool_rounds=4
        )
        
        response_payload = {
            "status": result["status"],
            "assistant_text": result["assistant_text"],
            "rounds": result["rounds"],
            "tool_events": result["tool_events"],
            "artifact_version": artifact_version.artifact_version,
            "model": selected_model
        }
        return JSONResponse(content=response_payload)
        
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {str(exc)}")


@app.get("/api/runs")
async def get_runs():
    runs_dir = ROOT / "runs"
    runs_info = []
    if runs_dir.exists():
        for file in runs_dir.glob("*.json"):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                runs_info.append({
                    "run_id": data.get("run_id"),
                    "version": data.get("version"),
                    "suite": data.get("suite"),
                    "provider": data.get("provider"),
                    "generated_at": data.get("generated_at"),
                    "summary": data.get("summary", {})
                })
            except Exception:
                pass
    return JSONResponse(content=runs_info)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
