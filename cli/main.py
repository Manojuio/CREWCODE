
import argparse
import sys
import os
from orchestrator.graph import run_crewcode

def parse_args():
    parser = argparse.ArgumentParser(description="CrewCode - Multi‑agent bug hunter")
    parser.add_argument("query", nargs="?", default="hunt bugs", help="Your request")
    parser.add_argument("--path", default=".", help="Project root")
    parser.add_argument("--fix", action="store_true", help="Enable automatic fixing (with approval)")
    return parser.parse_args()

def main():
    args = parse_args()
    if not os.path.isdir(args.path):
        print(f"Error: path '{args.path}' not found")
        sys.exit(1)
    
    print("\n🚀 CrewCode – Hierarchical Bug Hunting System")
    print(f"📂 Project: {os.path.abspath(args.path)}")
    print("🔄 Stages: Inspector → Test Engineer → Debugger → Reviewer")
    if not args.fix:
        print("⚠️  Fix mode disabled (use --fix to enable). Will only inspect and generate tests.")
    else:
        print("🔧 Fix mode enabled – will attempt to apply patches (requires patch command)")
    print("-"*50)

    state = run_crewcode(args.path, args.query, enable_fixer=args.fix)

    # --- Print findings from Inspector ---
    findings = state.get("findings", [])
    if findings:
        print("\n🐞 BUGS FOUND (Inspector):")
        for f in findings:
            print(f"  [{f['severity']}] {f['file']}:{f['line']} – {f['type']}")
    else:
        print("\n✅ No bugs found by Inspector.")

    # --- Optionally print test outputs (if any) ---
    test_outputs = state.get("test_outputs", [])
    if test_outputs and args.fix:
        print("\n🧪 Test Engineer generated tests (first 3):")
        for out in test_outputs[:3]:
            print(f"  Test for {out.get('file', 'unknown')}: output snippet = {out.get('test_output', '')[:100]}...")

    print("\n📋 Final report:\n", state.get("final_report", "No report"))
    print(f"✅ Done. {len(findings)} initial findings.")

if __name__ == "__main__":
    main()