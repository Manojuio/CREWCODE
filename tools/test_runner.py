import tempfile
import os
from tools.terminal import run_command

def run_pytest(test_code: str, project_root: str) -> dict:
    """Write a temporary pytest file, run it, return results."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(test_code)
        tmp_path = f.name
    try:
        result = run_command(f"pytest {tmp_path} -v", cwd=project_root)
        return {"passed": "passed" in result and "FAILED" not in result, "output": result}
    finally:
        os.unlink(tmp_path)