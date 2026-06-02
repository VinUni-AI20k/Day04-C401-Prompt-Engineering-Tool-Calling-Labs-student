from __future__ import annotations

from typing import Any
import requests
from tools._shared import TIMEOUT, err

def lookup_word(word: str = "") -> dict[str, Any]:
    if not word.strip():
        return {"tool": "dictionary", "error": "InvalidInput", "message": "Word parameter cannot be empty."}
    try:
        response = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.strip()}",
            timeout=TIMEOUT
        )
        if response.status_code == 404:
            return {"tool": "dictionary", "word": word, "status": "not_found", "message": "No definitions found for this word."}
        response.raise_for_status()
        data = response.json()
        
        meanings = []
        if isinstance(data, list) and len(data) > 0:
            entry = data[0]
            for meaning in entry.get("meanings", []):
                part_of_speech = meaning.get("partOfSpeech", "")
                definitions = []
                for d in meaning.get("definitions", []):
                    definitions.append({
                        "definition": d.get("definition", ""),
                        "example": d.get("example", "")
                    })
                meanings.append({
                    "part_of_speech": part_of_speech,
                    "definitions": definitions[:2]
                })
            return {"tool": "dictionary", "word": word, "status": "success", "meanings": meanings[:3]}
        return {"tool": "dictionary", "word": word, "status": "no_data"}
    except Exception as exc:
        return err("dictionary", exc)
