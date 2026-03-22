"""Command parsing, alias resolution, and execution logic."""

import os
import re
import subprocess
import shlex

from macrun.aliases import COMMAND_ALIASES, ALIAS_DISPLAY_NAMES


class ExecutionResult:
    """Result of executing a command."""
    def __init__(self, success, message=None, translated_from=None, translated_to=None,
                 info_message=None, output=None):
        self.success = success
        self.message = message              # error message if failed
        self.translated_from = translated_from  # original Windows command
        self.translated_to = translated_to      # macOS equivalent (for toast)
        self.info_message = info_message    # informational message to show
        self.output = output                # command output (for terminal cmds like sw_vers)


def execute(command):
    """Execute a command string. Returns an ExecutionResult."""
    command = command.strip()
    if not command:
        return ExecutionResult(False, "No command entered.")

    # 1. Check URL
    result = _try_url(command)
    if result:
        return result

    # 2. Check alias (exact match, case-insensitive)
    result = _try_alias(command)
    if result:
        return result

    # 3. Check file/folder path
    result = _try_path(command)
    if result:
        return result

    # 4. Fuzzy app match
    result = _try_app_search(command)
    if result:
        return result

    # 5. Shell command fallback
    return _try_shell(command)


def _try_url(command):
    """Detect and open URLs."""
    url_pattern = re.compile(
        r'^(https?://|ftp://)'  # explicit protocol
        r'|^[a-zA-Z0-9][-a-zA-Z0-9]*\.(com|org|net|io|dev|edu|gov|co|app|me|info|biz)(/|$)',
        re.IGNORECASE
    )
    if url_pattern.search(command):
        url = command
        if not re.match(r'^(https?://|ftp://)', command, re.IGNORECASE):
            url = "https://" + command
        try:
            subprocess.Popen(["open", url])
            return ExecutionResult(True)
        except Exception as e:
            return ExecutionResult(False, str(e))
    return None


def _try_alias(command):
    """Check command against the alias dictionary."""
    cmd_lower = command.lower().strip()

    # Try exact match first, then first-word match
    alias_val = COMMAND_ALIASES.get(cmd_lower)

    if alias_val is None and " " not in cmd_lower:
        # No match found at all
        pass
    elif alias_val is None:
        # Try matching the full command with spaces (e.g., "shutdown /s")
        alias_val = COMMAND_ALIASES.get(cmd_lower)

    if alias_val is None:
        return None

    # Handle tuple (command, info_message) or None (no equivalent)
    if isinstance(alias_val, tuple):
        mac_cmd, info_msg = alias_val
        if mac_cmd is None:
            return ExecutionResult(False, info_msg, info_message=info_msg)
        try:
            # Some commands need terminal output (like ifconfig)
            if _is_terminal_command(mac_cmd):
                return _run_terminal_command(mac_cmd, translated_from=cmd_lower,
                                           translated_to=mac_cmd, info_message=info_msg)
            subprocess.Popen(mac_cmd, shell=True)
            display_name = ALIAS_DISPLAY_NAMES.get(cmd_lower, mac_cmd)
            return ExecutionResult(True, translated_from=cmd_lower,
                                  translated_to=display_name, info_message=info_msg)
        except Exception as e:
            return ExecutionResult(False, str(e))

    # Simple string alias
    mac_cmd = alias_val
    if _is_terminal_command(mac_cmd):
        return _run_terminal_command(mac_cmd, translated_from=cmd_lower,
                                   translated_to=mac_cmd)
    try:
        subprocess.Popen(mac_cmd, shell=True)
        display_name = ALIAS_DISPLAY_NAMES.get(cmd_lower, mac_cmd)
        return ExecutionResult(True, translated_from=cmd_lower,
                              translated_to=display_name)
    except Exception as e:
        return ExecutionResult(False, str(e))


def _is_terminal_command(cmd):
    """Check if a command should show output in a terminal/dialog rather than just run."""
    terminal_cmds = {"ifconfig", "sw_vers", "system_profiler", "traceroute",
                     "netstat", "nslookup", "arp", "hostname", "whoami",
                     "screencapture"}
    first_word = cmd.split()[0] if cmd else ""
    return first_word in terminal_cmds


def _run_terminal_command(cmd, translated_from=None, translated_to=None, info_message=None):
    """Run a command and capture its output for display."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout or result.stderr or "(no output)"
        return ExecutionResult(True, translated_from=translated_from,
                              translated_to=translated_to, info_message=info_message,
                              output=output.strip())
    except subprocess.TimeoutExpired:
        return ExecutionResult(False, "Command timed out.")
    except Exception as e:
        return ExecutionResult(False, str(e))


def _try_path(command):
    """Try to open as a file/folder path."""
    # Expand ~ and environment variables
    if command.startswith(("~", "/", ".", "$")):
        expanded = os.path.expanduser(os.path.expandvars(command))
        if os.path.exists(expanded):
            try:
                subprocess.Popen(["open", expanded])
                return ExecutionResult(True)
            except Exception as e:
                return ExecutionResult(False, str(e))
        # Path-like but doesn't exist — still try `open` (might be a URL scheme)
        if command.startswith(("~", "/")):
            try:
                subprocess.Popen(["open", expanded])
                return ExecutionResult(True)
            except Exception as e:
                return ExecutionResult(False, f"Path not found: {command}")
    return None


def _try_app_search(command):
    """Fuzzy search for an application by name."""
    # Only try if the command looks like an app name (no spaces, no special chars)
    if "/" in command or "." in command:
        return None

    name = command.strip()

    # Try direct open -a first (handles exact names)
    try:
        result = subprocess.run(
            ["open", "-a", name],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return ExecutionResult(True)
    except (subprocess.TimeoutExpired, Exception):
        pass

    # Fuzzy search using mdfind
    try:
        result = subprocess.run(
            ["mdfind", f"kMDItemKind == 'Application' && kMDItemDisplayName == '*{name}*'c"],
            capture_output=True, text=True, timeout=5
        )
        apps = [line for line in result.stdout.strip().split("\n") if line.endswith(".app")]
        if apps:
            # Pick the best match — prefer shorter names (closer match)
            apps.sort(key=lambda a: len(os.path.basename(a)))
            best = apps[0]
            subprocess.Popen(["open", best])
            return ExecutionResult(True)
    except (subprocess.TimeoutExpired, Exception):
        pass

    return None


def _try_shell(command):
    """Run as a shell command (fallback)."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            output = result.stdout.strip() if result.stdout.strip() else None
            return ExecutionResult(True, output=output)
        else:
            error = result.stderr.strip() if result.stderr.strip() else f"Command failed with exit code {result.returncode}"
            return ExecutionResult(False, error)
    except subprocess.TimeoutExpired:
        return ExecutionResult(False, "Command timed out.")
    except Exception as e:
        return ExecutionResult(
            False,
            f"macOS cannot find '{command}'. Make sure you typed the name correctly, and then try again."
        )
