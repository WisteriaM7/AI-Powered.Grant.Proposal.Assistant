import json
import os
from datetime import datetime

MEMORY_DIR = "grant_memory"


def _safe_filename(topic: str) -> str:
    """Convert topic to a safe filename."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in topic)[:50]


def _memory_file(topic: str) -> str:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    return os.path.join(MEMORY_DIR, f"{_safe_filename(topic)}_memory.json")


def _versions_file(topic: str) -> str:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    return os.path.join(MEMORY_DIR, f"{_safe_filename(topic)}_versions.json")


def load_memory(topic: str) -> dict:
    """Load topic memory dict."""
    path = _memory_file(topic)
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_memory(topic: str, memory: dict):
    """Save topic memory dict."""
    with open(_memory_file(topic), "w") as f:
        json.dump(memory, f, indent=2)


def get_versions(topic: str) -> list:
    """Load all saved versions for a topic."""
    path = _versions_file(topic)
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def add_version(topic: str, version_type: str, content: str, rationale: str = ""):
    """Add a new version entry for a topic."""
    versions = get_versions(topic)
    version_number = len(versions) + 1
    entry = {
        "version": version_number,
        "type": version_type,          # "outline", "budget", "review"
        "content": content,
        "rationale": rationale,
        "timestamp": datetime.now().isoformat()
    }
    versions.append(entry)
    with open(_versions_file(topic), "w") as f:
        json.dump(versions, f, indent=2)
    return version_number


def list_topics() -> list:
    """List all topics that have memory saved."""
    if not os.path.exists(MEMORY_DIR):
        return []
    topics = []
    for fname in os.listdir(MEMORY_DIR):
        if fname.endswith("_memory.json"):
            # Reverse-engineer display name from filename
            topics.append(fname.replace("_memory.json", "").replace("_", " "))
    return sorted(topics)
