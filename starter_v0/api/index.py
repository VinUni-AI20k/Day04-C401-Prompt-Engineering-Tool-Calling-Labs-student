from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
from pathlib import Path

# Fix the import path so Vercel can run the backend from api folder
# Add the parent directory (starter_v0) into sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop

app = FastAPI(title="AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    provider: str = "gemini" 
    model: Optional[str] = None

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    root_dir = Path(__file__).parent.parent
    system_prompt_path = root_dir / "artifacts" / "system_prompt.md"
    tools_path = root_dir / "artifacts" / "tools.yaml"
    
    try:
        system_prompt = system_prompt_path.read_text(encoding="utf-8")
        tool_declarations = load_tool_declarations(tools_path)
        openai_tools = to_openai_tools(tool_declarations)
        
        provider = make_provider(req.provider)
        
        # Build messages context
        messages = [{"role": "system", "content": system_prompt}]
        for msg in req.messages:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=req.model,
            max_tool_rounds=4
        )
        
        return {
            "status": "success",
            "assistant_text": result.get("assistant_text", ""),
            "tool_events": result.get("tool_events", [])
        }
    except Exception as e:
        print(f"Error during API execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))
