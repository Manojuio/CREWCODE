from tools.linter import run_pylint
import difflib
from tools.filesystem import read_file

def reviewer_node(state: dict) -> dict:
    patches = state.get("patches", [])
    if not patches:
        return {"final_report": "No changes to review."}
    
    report = []
    for p in patches:
        if not p["applied"]:
            report.append(f"Patch for {p['file']} failed to apply.")
            continue
        # Run linter
        lint_out = run_pylint(p["file"])
        if "Your code has been rated at" in lint_out:
            report.append(f"Linter OK for {p['file']}")
        else:
            report.append(f"Linter issues in {p['file']}:\n{lint_out[:500]}")
        # Show diff
        original = read_file(p["backup"])
        new = read_file(p["file"])
        diff = difflib.unified_diff(original.splitlines(), new.splitlines(),
                                     fromfile=f"a/{p['file']}", tofile=f"b/{p['file']}")
        diff_text = "\n".join(diff)
        report.append(f"Diff for {p['file']}:\n{diff_text[:1000]}")
    
    # Ask user for final approval (human‑in‑the‑loop)
    print("\n📝 Reviewer report:\n" + "\n".join(report))
    answer = input("\nApply all these changes permanently? (y/n): ").strip().lower()
    if answer != 'y':
        # Rollback all backups
        for p in patches:
            import shutil
            if p.get("backup"):
                shutil.copy(p["backup"], p["file"])
        return {"final_report": "Changes rejected and rolled back."}
    # Keep changes
    for p in patches:
        if p.get("backup"):
            import os
            os.unlink(p["backup"])   # remove backup if approved
    return {"final_report": "Changes approved and applied."}