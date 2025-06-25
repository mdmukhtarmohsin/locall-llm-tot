import re
from pathlib import Path
import json
from datetime import datetime

def save_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def append_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            try:
                arr = json.load(f)
            except:
                arr = []
    else:
        arr = []
    arr.append(obj)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(arr, f, ensure_ascii=False, indent=2)

def parse_answer_from_text(text: str) -> str:
    pattern = re.compile(r"Answer:\s*(.*)", re.IGNORECASE)
    matches = pattern.findall(text)
    if matches:
        return matches[-1].strip()
    else:
        lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
        return lines[-1] if lines else ''

def current_timestamp():
    return datetime.now().isoformat()