# 🐞 CrewCode – Hierarchical Multi-Agent Bug Hunting System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green)](https://langchain-ai.github.io/langgraph/)
[![Ollama](https://img.shields.io/badge/Ollama-0.5+-orange)](https://ollama.com)

CrewCode is an **autonomous, hierarchical multi-agent system** that hunts bugs in your code, writes failing tests, generates minimal patches, and safely applies fixes – all **locally** using open-source LLMs (Ollama). No cloud API keys required.

## 📖 Table of Contents

- [Architecture](#-architecture)
- [How It Works (Agent Flow)](#-how-it-works-agent-flow)
- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Examples](#-examples)
- [Customisation](#-customisation)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🧠 Architecture

CrewCode follows the proven **Hierarchical Review & Analysis** pattern. It consists of four specialised agents that work in sequence:

| Agent | Role | Tools | LLM Calls |
|-------|------|-------|------------|
| **Inspector** | Static analysis (regex patterns) | `read_file`, `list_dir` | ❌ No |
| **Test Engineer** | Generate failing pytest to confirm bug | `pytest`, LLM | ✅ Yes |
| **Debugger** | Produce minimal unified diff / patch | LLM, `apply_diff` (Python) | ✅ Yes |
| **Reviewer** | Lint, show diff, ask for human approval | `pylint`, `difflib` | ❌ No |

The system uses **LangGraph** for stateful orchestration and **Ollama** (default `qwen2.5-coder:1.5b`) for LLM tasks.

---

## 🔄 How It Works (Agent Flow)
User request (CLI)
│
▼
┌─────────────┐
│ Inspector │ Scans code for patterns (hardcoded keys, SQLi, unsafe eval, etc.)
└─────────────┘
│
▼ (findings)
┌─────────────┐
│Test Engineer│ For each finding → writes a pytest that should FAIL
└─────────────┘
│
▼ (confirmed findings + test outputs)
┌─────────────┐
│ Debugger │ Generates a unified diff (patch) that makes the test PASS
└─────────────┘
│
▼ (patch)
┌─────────────┐
│ Reviewer │ Lints the changed file, shows diff, asks for final approval
└─────────────┘
│
▼
File modified (with .bak backup) or rolled back

text

**Read‑only mode** (`--fix` not used) stops after the Test Engineer – no files are ever modified.

**Fix mode** (`--fix`) runs all four agents and **asks for your permission** before applying any change.

---

## ✨ Features

- 🔍 **Multi‑language static analysis** – Python, JavaScript, Java, Go, Ruby, PHP (extendable)
- 🧪 **Automatic test generation** – reproduces each bug with a failing pytest
- 🩹 **Minimal patch generation** – LLM produces small diffs, not whole‑file rewrites
- 🛡️ **Safe file modification** – creates `.bak` backups, shows diff preview, requires approval
- 🏃 **Incremental scanning** – SQLite cache speeds up repeated runs (optional)
- 💻 **Fully local** – works offline with Ollama (or optionally Groq/Gemini)
- ⚙️ **Customisable** – add your own regex patterns, change LLM providers, adjust limits

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- [Ollama](https://ollama.com/) installed and running
- (Optional) `patch` utility for applying diffs on Windows – install [Git for Windows](https://git-scm.com/) and add `C:\Program Files\Git\usr\bin` to your PATH.

### Steps

```bash
# Clone the repository
git clone https://github.com/Manojuio/CREWCODE.git
cd CREWCODE

# Create virtual environment and install dependencies
uv sync   # or: pip install -e .

# Pull the recommended Ollama model
ollama pull qwen2.5-coder:1.5b

# (Optional) Copy environment template and add your keys if using cloud providers
cp .env.example .env   # then edit .env
⚙️ Configuration
All settings are in config/settings.py. Key options:

AGENT_MODEL_MAP – assign each agent to an LLM provider (ollama, groq, gemini) and model name.

MAX_FILE_READ_CHARS – limit file content sent to LLM (default 10,000).

TOOL_TIMEOUT_SECONDS – timeout for shell commands.

For local‑only usage (no API keys), set all providers to ollama:

python
AGENT_MODEL_MAP = {
    "inspector":     ("ollama", "qwen2.5-coder:1.5b"),
    "test_engineer": ("ollama", "qwen2.5-coder:1.5b"),
    "debugger":      ("ollama", "qwen2.5-coder:1.5b"),
    "reviewer":      ("ollama", "qwen2.5-coder:1.5b"),
}
🚀 Usage
Basic scan (read‑only)
bash
crewcode "find bugs" --path /path/to/project
Or using uv run directly:

bash
uv run python -m cli.main "find bugs" --path /path/to/project
Output: List of bugs with severity, file, line, and type.

Full fix mode (with approval)
bash
crewcode "find and fix bugs" --fix --path /path/to/project
What happens:

Inspector finds issues.

Test Engineer writes a failing test for the first 3 issues.

Debugger generates a patch for each confirmed bug.

Reviewer shows the diff and asks: Apply this fix? (y/n)

If you approve, the file is patched and a .bak backup is saved.

Force a fresh scan (ignore cache)
Delete the database file:

bash
rm data/crewcode.db
📝 Examples
Scanning a test project
bash
crewcode "find issues" --path ./crewtest
Output:

text
🐞 BUGS FOUND (Inspector):
  [HIGH] crewtest/buggy.py:9 – Unsafe Eval
  [MEDIUM] crewtest/buggy.py:13 – Weak Crypto
  [MEDIUM] crewtest/buggy.py:5 – Sql Injection
  [LOW] crewtest/buggy.py:4 – Missing Return
  ...
✅ Done. 7 initial findings.
Fixing one bug interactively
bash
crewcode "fix unsafe eval" --fix --path ./crewtest
You will see a diff preview and be asked for confirmation.

🔧 Customisation
Add new bug patterns
Edit agents/inspector.py, add a new key to the PATTERNS dictionary:

python
"xss_vulnerability": [
    r'innerHTML\s*=\s*.*\$.*',
    r'\.html\(.*\+.*\)',
],
And add a corresponding severity mapping if needed.

Use a larger local model
If you have enough RAM (≥8GB), pull and use qwen2.5-coder:3b:

bash
ollama pull qwen2.5-coder:3b
Then change the model name in settings.py.

Disable incremental caching
Set is_file_changed to always return True in db/sqlite_client.py.

🧪 Troubleshooting
Problem	Solution
ImportError: cannot import name 'run_command'	Ensure tools/terminal.py contains the function run_command. Replace with the version from the repository.
FileNotFoundError: patch	Install Git for Windows (includes patch) or run without --fix.
LLM returns very short/empty fixes	The 1.5B model may struggle. Try a larger model or simplify the code.
No issues found but code has bugs	The regex patterns may not cover your specific cases. Extend PATTERNS in inspector.py.
Quota errors with Groq/Gemini	Switch to Ollama for all agents (see configuration).
📜 License
Distributed under the MIT License. See LICENSE file for more information.

🙏 Acknowledgements
LangGraph – stateful multi‑agent orchestration

Ollama – local LLM runtime

Qwen2.5-Coder – lightweight coding model

Built with ❤️ for local, private, automated bug hunting.
