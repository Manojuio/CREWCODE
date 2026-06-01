import subprocess
from config.settings import TOOL_TIMEOUT_SECONDS

# List of dangerous command patterns (case‑insensitive)
BANNED_COMMANDS = [
    "rm -rf", "rmdir", "mkfs", "shutdown", "reboot",
    "del /f", "format", "dd if=", "> /dev/sda"
]

def run_command(command: str, cwd: str = ".") -> str:
    """
    Executes a shell command safely.
    Returns combined stdout/stderr and exit code.
    Banned commands are rejected without execution.
    """
    # Check for banned commands
    lower_cmd = command.lower()
    for banned in BANNED_COMMANDS:
        if banned in lower_cmd:
            return f"Error: Command rejected – contains banned pattern: '{banned}'"

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=TOOL_TIMEOUT_SECONDS,
            encoding='utf-8',
            errors='replace'
        )
        output = f"--- STDOUT ---\n{result.stdout}\n"
        output += f"--- STDERR ---\n{result.stderr}\n"
        output += f"--- EXIT CODE: {result.returncode} ---"
        return output

    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {TOOL_TIMEOUT_SECONDS} seconds."
    except FileNotFoundError:
        return f"Error: Command not found – '{command.split()[0]}' is not installed or not in PATH."
    except Exception as e:
        return f"Error executing command: {str(e)}"