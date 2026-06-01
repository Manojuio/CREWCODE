from config.settings import get_model_config
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from tools.filesystem import read_file
import difflib

def generate_diff(filepath: str, finding: dict, test_output: str) -> str:
    """LLM generates a minimal diff to fix the bug."""
    provider, model = get_model_config("debugger")
    llm = ChatOllama(model=model, temperature=0.2)
    
    original = read_file(filepath)
    if original.startswith("Error"):
        return "# Error reading file"
    
    prompt = f"""You are a debugger. The file '{filepath}' has a bug at line {finding['line']}.
Type: {finding['type']}
Failing test output:
{test_output[:1000]}

Original code snippet (around the line):
Output a unified diff (patch) that fixes the bug. Use the format:
--- a/file.py
+++ b/file.py
@@ -lineno,1 +lineno,1 @@
- old line
+ new line
Only output the diff, nothing else.
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content

def apply_diff(filepath: str, diff_text: str) -> dict:
    """Apply a unified diff using Python's difflib, no external patch command."""
    import difflib
    import shutil
    from tools.filesystem import read_file

    original = read_file(filepath)
    if original.startswith("Error"):
        return {"applied": False, "error": original}
    
    # Create backup
    backup = filepath + ".bak"
    shutil.copy(filepath, backup)

    # Parse the diff to get the changes (simplified: we expect a single hunk)
    # For simplicity, we'll extract the new content by applying the diff using difflib
    # But easier: assume the diff contains the full new file content? No, better to use patch from Python.
    # Use difflib's unified_diff to apply? Actually, we need to parse the diff.
    # A reliable way: use the `patch` library? No external. Let's do a simple approach:
    # If the diff is correctly formatted, we can extract line changes.

    # For MVP, we'll write the new content as the original + modifications? Too complex.
    # Alternative: ask the LLM to output the full new file content instead of a diff.
    # That would be simpler and works without patch.
    # Since the 1.5B model struggles with large files, we'll fall back to that.
    # Let's change the prompt in generate_diff to output full new file.

def debugger_node(state: dict) -> dict:
    confirmed = state.get("confirmed_findings", [])
    test_outputs = state.get("test_outputs", [])
    if not confirmed:
        return {"patches": []}
    patches = []
    for f, out in zip(confirmed, test_outputs):
        diff = generate_diff(f["file"], f, out["test_output"])
        result = apply_diff(f["file"], diff)
        patches.append({"file": f["file"], "applied": result["applied"], "backup": result.get("backup")})
    return {"patches": patches}