import os
import json
import csv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def read_runs():
    runs_dir = BASE_DIR / "runs"
    if not runs_dir.exists():
        return []
    
    run_details = []
    # Filter files ending with .json
    for filename in os.listdir(runs_dir):
        if not filename.endswith(".json"):
            continue
            
        file_path = runs_dir / filename
        try:
            stat = file_path.stat()
            mtime = int(stat.st_mtime * 1000) # milliseconds
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            try:
                data = json.loads(content)
            except Exception:
                data = {}
                
            run_details.append({
                "fileName": filename,
                "mtime": mtime,
                "runId": data.get("run_id", filename.replace(".json", "")),
                "version": data.get("version", "unknown"),
                "suite": data.get("suite", "unknown"),
                "provider": data.get("provider", "unknown"),
                "model": data.get("model", "unknown"),
                "generatedAt": data.get("generated_at", datetime.fromtimestamp(stat.st_mtime).isoformat()),
                "summary": data.get("summary", None),
                "results": data.get("results", [])
            })
        except Exception as e:
            # Skip files that can't be read
            print(f"Error reading run file {filename}: {e}")
            
    # Sort descending by mtime
    run_details.sort(key=lambda x: x["mtime"], reverse=True)
    return run_details

def read_eval_cases():
    data_dir = BASE_DIR / "data"
    if not data_dir.exists():
        return {}
        
    result = {}
    for filename in os.listdir(data_dir):
        if not filename.endswith(".json"):
            continue
            
        file_path = data_dir / filename
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            try:
                result[filename] = json.loads(content)
            except Exception:
                result[filename] = {"error": "Failed to parse JSON"}
        except Exception:
            result[filename] = {"error": f"Failed to read file"}
            
    return result

def read_version_log():
    file_path = BASE_DIR / "artifacts" / "version_log.csv"
    if not file_path.exists():
        return {"headers": [], "rows": []}
        
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows_list = list(reader)
            
        if not rows_list:
            return {"headers": [], "rows": []}
            
        headers = [h.strip() for h in rows_list[0]]
        rows = []
        for row in rows_list[1:]:
            row_dict = {}
            for i, h in enumerate(headers):
                row_dict[h] = row[i].strip() if i < len(row) else ""
            rows.append(row_dict)
            
        return {"headers": headers, "rows": rows}
    except Exception as e:
        print(f"Error reading version log: {e}")
        return {"headers": [], "rows": []}

def read_prompt_tools():
    artifacts_dir = BASE_DIR / "artifacts"
    
    system_prompt = ""
    try:
        with open(artifacts_dir / "system_prompt.md", "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except Exception:
        pass

    tools_yaml = ""
    try:
        with open(artifacts_dir / "tools.yaml", "r", encoding="utf-8") as f:
            tools_yaml = f.read()
    except Exception:
        pass

    report_md = ""
    try:
        with open(artifacts_dir / "REPORT.md", "r", encoding="utf-8") as f:
            report_md = f.read()
    except Exception:
        pass

    runbook_md = ""
    try:
        with open(artifacts_dir / "PERSON1_RUNBOOK.md", "r", encoding="utf-8") as f:
            runbook_md = f.read()
    except Exception:
        pass

    return {
        "systemPrompt": system_prompt,
        "toolsYaml": tools_yaml,
        "reportMd": report_md,
        "runbookMd": runbook_md
    }
