from fastapi import FastAPI
from backend import file_readers

app = FastAPI(title="GapTutor Agent Trace UI Backend", version="1.0.0")

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "message": "Backend service is healthy"}

@app.get("/api/v1/runs")
async def get_runs():
    return file_readers.read_runs()

@app.get("/api/v1/eval-cases")
async def get_eval_cases():
    return file_readers.read_eval_cases()

@app.get("/api/v1/version-log")
async def get_version_log():
    return file_readers.read_version_log()

@app.get("/api/v1/prompt-tools")
async def get_prompt_tools():
    return file_readers.read_prompt_tools()
