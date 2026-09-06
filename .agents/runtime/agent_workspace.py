#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

VERSION = "8.2.1"

DESTRUCTIVE_PATTERNS = [
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+clean\s+-[^\n]*\b[fdxX]",
    r"\bgit\s+push\b[^\n]*(?:--force(?:-with-lease)?|-f)\b",
    r"\brm\s+-[^\n]*r[^\n]*f[^\n]*\s+/(?:\s|$)",
    r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:sh|bash|zsh)\b",
]

# Paths that an agent should never retrieve through shell/file tools.  This is a
# secondary deterministic guard.  Claude sandbox credentials and Codex
# filesystem denies are the primary enforcement boundaries.
SENSITIVE_PATH_PATTERNS = [
    r"(?<![A-Za-z0-9_.-])\.env(?!\.(?:example|sample|template)(?:\b|\.))(?:\.[A-Za-z0-9_.-]+)?(?:\b|$)",
    r"(?:^|[/\\])\.ssh(?:[/\\]|$)",
    r"(?:^|[/\\])id_(?:rsa|ed25519)(?:\.pub)?(?:\b|$)",
    r"(?:^|[/\\])\.aws[/\\]credentials(?:\b|$)",
    r"(?:^|[/\\])\.config[/\\]gcloud[/\\]application_default_credentials\.json(?:\b|$)",
    r"(?:^|[/\\])credentials(?:\.json)?(?:\b|$)",
    r"(?:^|[/\\])[^/\\\s]+\.pem(?:\b|$)",
    r"(?:^|[/\\])\.netrc(?:\b|$)",
    r"(?:^|[/\\])\.npmrc(?:\b|$)",
    r"(?:^|[/\\])\.pypirc(?:\b|$)",
]

# Shell environment dumps are disproportionately likely to expose unrelated
# credentials.  They are easy for the user to run manually when truly needed.
# `env`/`printenv` are flagged whenever invoked (with or without arguments);
# `set` is only flagged bare (no flags/arguments), since `set -e`/`set -eu`/
# `set -o pipefail` are common, safe shell-hardening idioms that print
# nothing -- only a bare `set` dumps every shell variable, including
# exported secrets. Found via independent Codex cross-review (2026-08-30):
# the prior pattern flagged `set -eu` as a false positive.
ENV_DUMP_PATTERN = re.compile(r"(^|[;&|]\s*)(?:(?:env|printenv)(?:\s|$)|set\s*(?:[;&|]|$))", re.I)
SECRET_ENV_REFERENCE = re.compile(
    r"\$(?:\{)?[A-Za-z_][A-Za-z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL)[A-Za-z0-9_]*(?:\})?",
    re.I,
)


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def atomic_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def run(cmd: list[str], cwd: Path, timeout: float = 1.0) -> str:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
        return p.stdout.strip() if p.returncode == 0 else ""
    except Exception:
        return ""


def classify(prompt: str) -> tuple[str, str, list[str]]:
    text = prompt.lower()
    complex_words = (
        "architecture",
        "arquitetura",
        "migration",
        "migração",
        "authentication",
        "autenticação",
        "authorization",
        "security",
        "segurança",
        "database schema",
        "breaking change",
        "production",
        "deploy",
        "multi-agent",
        "refactor across",
        "monorepo",
    )
    medium_words = (
        "refactor",
        "implement",
        "implemente",
        "feature",
        "bug",
        "test",
        "review",
        "endpoint",
        "api",
        "database",
        "sql",
    )
    reasons: list[str] = []
    if any(word in text for word in complex_words) or len(prompt) > 2200:
        reasons.append("high-risk or cross-cutting task signal")
        return "complex", "high", reasons
    if any(word in text for word in medium_words) or len(prompt) > 700:
        reasons.append("multi-step implementation or review signal")
        return "standard", "medium", reasons
    reasons.append("small/local task signal")
    return "trivial", "low", reasons


def deny(reason: str) -> dict[str, Any]:
    # Current Claude Code and Codex both accept this PreToolUse shape.
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def sensitive_reference(text: str) -> bool:
    if not text:
        return False
    return any(re.search(pattern, text, re.I) for pattern in SENSITIVE_PATH_PATTERNS)


def unsafe_shell(command: str) -> str | None:
    if not command:
        return None
    for pattern in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, command, re.I):
            return "Blocked destructive or unreviewed remote-script command."
    if sensitive_reference(command):
        return "Blocked shell access to a sensitive credential path. Use an example/template file instead."
    if ENV_DUMP_PATTERN.search(command):
        return "Blocked broad environment dump because it can expose credentials. Inspect a known non-secret variable explicitly instead."
    if SECRET_ENV_REFERENCE.search(command):
        return "Blocked direct shell expansion of a likely secret environment variable."
    return None


def session_log(project: Path, payload: dict[str, Any]) -> None:
    """Write only lightweight, non-prompt session metadata.

    This is intentionally best-effort. Durable knowledge belongs in workspace-save,
    not in SessionEnd, because SessionEnd is advisory and can fail when a project is
    deleted or moved while a client is open.
    """
    state = project / ".agents/state"
    profile = load_json(state / "project-profile.json", {})
    vault_path = os.environ.get("AGENT_WORKSPACE_VAULT", "").strip()
    if not vault_path:
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        config_path = config_home / "agent-workspace" / "config.json"
        try:
            if config_path.exists():
                vault_path = str(load_json(config_path, {}).get("vault_path", "")).strip()
        except Exception:
            vault_path = ""
    if not vault_path:
        return
    vault = Path(vault_path).expanduser()
    if not vault.exists():
        return
    slug = str(profile.get("vault_slug") or profile.get("slug") or project.name)
    out = vault / "session-logs" / slug
    out.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().astimezone().strftime("%Y-%m-%d-%H%M%S")
    branch = run(["git", "branch", "--show-current"], project, 0.8)
    changes = run(["git", "status", "--short", "--untracked-files=no"], project, 0.9)
    lines = [
        "---",
        f'title: "Automatic session close - {project.name}"',
        "type: session-log",
        f'project: "{slug}"',
        f'created: "{dt.datetime.now().astimezone().isoformat(timespec="seconds")}"',
        "status: automatic-metadata",
        "---",
        "",
        f"# Automatic session close - {project.name}",
        "",
        "> Lightweight metadata only. Use `workspace-save` for curated durable state.",
        "",
        "## Repository",
        "",
        f"- Path: `{project}`",
        f"- Branch: `{branch or 'unknown'}`",
        f"- End reason: `{payload.get('reason', 'unknown')}`",
        "",
        "## Tracked changes at close",
        "",
        "```text",
        changes[:4000] if changes else "No tracked working-tree changes detected.",
        "```",
        "",
        "## Related",
        "",
        f"- [[projects/{slug}/Home|Project Home]]",
        "",
    ]
    try:
        (out / f"{stamp}.md").write_text("\n".join(lines))
    except OSError:
        pass


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    event = str(payload.get("hook_event_name") or "")
    cwd = Path(payload.get("cwd") or os.getcwd()).resolve()
    root_text = run(["git", "rev-parse", "--show-toplevel"], cwd, 0.8)
    project = Path(root_text).resolve() if root_text else cwd
    state = project / ".agents/state"
    state.mkdir(parents=True, exist_ok=True)

    if event == "UserPromptSubmit":
        prompt = str(payload.get("prompt") or "")
        level, risk, reasons = classify(prompt)
        # Never persist the raw prompt. Hash is enough to correlate duplicate hook
        # events without turning local state or the Vault into a prompt archive.
        policy = {
            "version": VERSION,
            "level": level,
            "risk": risk,
            "reasons": reasons,
            "updated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "prompt_hash": hashlib.sha256(prompt.encode("utf-8", errors="replace")).hexdigest()[:24],
        }
        atomic_json(state / "task-policy.json", policy)
        if level == "complex":
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "UserPromptSubmit",
                            "additionalContext": (
                                "Agent Workspace classified this task as complex/high-risk. "
                                "Read the task policy, identify contracts and validation before editing, "
                                "and use a work plan when the change is cross-cutting."
                            ),
                        }
                    }
                )
            )
        return

    if event == "PreToolUse":
        tool_input = payload.get("tool_input") or {}
        if not isinstance(tool_input, dict):
            tool_input = {}
        command = str(tool_input.get("command") or "")
        path_text = " ".join(
            str(tool_input.get(key) or "")
            for key in ("file_path", "path", "notebook_path")
        )
        # apply_patch and some local function tools carry paths inside command/input.
        serialized = json.dumps(tool_input, ensure_ascii=False)

        reason = unsafe_shell(command)
        if reason:
            print(json.dumps(deny(reason)))
            return
        if sensitive_reference(path_text) or (not command and sensitive_reference(serialized)):
            print(json.dumps(deny("Blocked access to a sensitive credential file.")))
            return
        return

    if event == "SessionEnd":
        # Avoid filling the Vault with empty/trivial closes. Save a lightweight
        # automatic record only when work was non-trivial or tracked files changed.
        policy = load_json(state / "task-policy.json", {})
        tracked = run(["git", "status", "--short", "--untracked-files=no"], project, 0.8)
        if tracked or str(policy.get("level", "trivial")) in {"standard", "complex"}:
            session_log(project, payload)
        return


if __name__ == "__main__":
    main()
