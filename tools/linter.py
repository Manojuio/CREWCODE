import subprocess
from tools.filesystem import read_file

def run_pylint(filepath: str) -> str:
    try:
        result = subprocess.run(
            ["pylint", filepath, "--score=n"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Linter error: {e}"