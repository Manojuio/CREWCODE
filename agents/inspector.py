import re
from tools.filesystem import read_file

# Simplified static analysis patterns (merged from security/logic/style)
PATTERNS = {
    "hardcoded_secret": [
        r'API_KEY\s*=\s*["\'][A-Za-z0-9]{16,}',
        r'sk-[a-zA-Z0-9]{32,}',
        r'AKIA[0-9A-Z]{16}',
    ],
    "unsafe_eval": [r'\beval\s*\(', r'\bexec\s*\('],
    "weak_crypto": [r'hashlib\.md5\(', r'hashlib\.sha1\('],
    "dangerous_function": [r'os\.system\(', r'subprocess\.call\(.*shell=True', r'pickle\.loads\('],
    "sql_injection": [r'f\s*".*SELECT.*\{.*\}.*"', r'f\s*".*INSERT.*\{.*\}.*"'],
    "missing_return": [r'def\s+\w+\([^)]*\):\s*\n(?!.*return)'],
    "off_by_one": [r'range\(1,\s*len\([^)]+\)\s*\+?\s*1?\)'],
}

def inspector_node(state: dict) -> dict:
    """Run static analysis on all Python files in the project root."""
    import os
    project_root = state["project_root"]
    findings = []
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(".py"):
                full = os.path.join(root, file)
                content = read_file(full)
                if content.startswith("Error"):
                    continue
                lines = content.splitlines()
                for vuln_type, patterns in PATTERNS.items():
                    for pattern in patterns:
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            line_no = content[:match.start()].count("\n") + 1
                            findings.append({
                                "file": full,
                                "line": line_no,
                                "type": vuln_type.replace("_", " ").title(),
                                "matched": match.group(0),
                                "severity": "HIGH" if "secret" in vuln_type or "eval" in vuln_type else "MEDIUM"
                            })
    return {"findings": findings}