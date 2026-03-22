"""Command history management — persisted to ~/.macrun_history as JSON."""

import json
import os

HISTORY_PATH = os.path.expanduser("~/.macrun_history")
MAX_HISTORY = 20


def load_history():
    """Load command history from disk. Returns list of strings, most recent first."""
    try:
        with open(HISTORY_PATH, "r") as f:
            data = json.load(f)
            return data.get("commands", [])[:MAX_HISTORY]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return []


def save_history(commands):
    """Write command list to disk, truncating to MAX_HISTORY."""
    with open(HISTORY_PATH, "w") as f:
        json.dump({"commands": commands[:MAX_HISTORY]}, f, indent=2)


def add_to_history(command):
    """Add a command to history (deduplicated, most recent first)."""
    command = command.strip()
    if not command:
        return
    commands = load_history()
    # Remove duplicates
    commands = [c for c in commands if c != command]
    commands.insert(0, command)
    save_history(commands[:MAX_HISTORY])


def get_completions(prefix):
    """Return history entries matching prefix (case-insensitive)."""
    prefix_lower = prefix.lower()
    return [c for c in load_history() if c.lower().startswith(prefix_lower)]


def clear_history():
    """Remove all history."""
    save_history([])
