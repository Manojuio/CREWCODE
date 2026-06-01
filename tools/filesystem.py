import os
from config.settings import MAX_FILE_READ_CHARS

def read_file(filepath: str) -> str:
    """Read a file with truncation. Returns error string on failure."""
    try:
        if not os.path.isfile(filepath):
            return f"Error: '{filepath}' is not a file."
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if len(content) > MAX_FILE_READ_CHARS:
            return content[:MAX_FILE_READ_CHARS] + "\n... [truncated]"
        return content
    except Exception as e:
        return f"Error reading file: {e}"

def list_dir(path: str = ".") -> str:
    try:
        items = os.listdir(path)
        output = []
        for item in sorted(items):
            full = os.path.join(path, item)
            prefix = "[DIR]" if os.path.isdir(full) else "[FILE]"
            output.append(f"{prefix} {item}")
        return "\n".join(output) if output else "Directory empty."
    except Exception as e:
        return f"Error listing directory: {e}"