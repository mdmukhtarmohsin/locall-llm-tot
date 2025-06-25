import json
from pathlib import Path

def load_tasks(domain: str, tasks_dir: Path):
    file_path = tasks_dir / f"{domain}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Task file not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data