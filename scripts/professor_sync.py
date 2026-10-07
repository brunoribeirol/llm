#!/usr/bin/env python3
"""Mirror the professor's course portal and watch their GitHub profile for new material.

Usage:
    python3 scripts/professor_sync.py            # sync the mirror, update state, print a report
    python3 scripts/professor_sync.py --check    # report only; write nothing

Standard library only. Network access goes through the ``git`` and ``curl`` binaries,
which honor the system proxy and certificate settings.

The mirror is additive: a file that disappears upstream is reported and kept locally,
because the whole point is to still have the material if the portal goes offline.
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

OWNER = "victorhwfreire"
REPO = "portal_gml_262"
REPO_URL = f"https://github.com/{OWNER}/{REPO}.git"
SITE_URL = f"https://{OWNER}.github.io/{REPO}/index.html"
API_REPOS_URL = f"https://api.github.com/users/{OWNER}/repos?per_page=100&sort=pushed"

ROOT = Path(__file__).resolve().parent.parent
MIRROR_DIR = ROOT / "reference" / REPO
STATE_FILE = ROOT / "reference" / "sync-state.json"

# Teacher-only files (lab solutions and the exam answer key) are kept, but in a separate
# tree: they are for checking finished work afterwards, and must not surface while the
# mirror is searched to study for graded work.
TEACHER_DIR = ROOT / "reference" / "teacher-only" / REPO
TEACHER_ONLY_NAMES = frozenset({"codigo-teacher.zip", "gabarito.md"})

MAX_LISTED = 25


def run(cmd: list[str], cwd: Path | None = None) -> bytes:
    """Run a command and return stdout; raise RuntimeError with stderr on failure."""
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, check=False)
    if proc.returncode != 0:
        detail = (
            proc.stderr.decode(errors="replace").strip()
            or f"exit code {proc.returncode}"
        )
        raise RuntimeError(f"{cmd[0]} failed: {detail}")
    return proc.stdout


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"mirror": {}, "repos": {}}


def remote_head() -> str:
    out = run(["git", "ls-remote", REPO_URL, "HEAD"]).decode().split()
    if not out:
        raise RuntimeError("git ls-remote returned no HEAD")
    return out[0]


def sync_mirror(old_sha: str | None, write: bool) -> dict:
    """Export upstream HEAD into MIRROR_DIR and return what was added, changed and kept."""
    result: dict = {
        "added": [],
        "changed": [],
        "teacher_only": [],
        "kept": [],
        "commits": [],
    }
    tmp = Path(tempfile.mkdtemp(prefix="portal-sync-"))
    try:
        clone = tmp / "repo"
        run(["git", "clone", "--quiet", REPO_URL, str(clone)])

        log_range = ["-5"]
        if (
            old_sha
            and subprocess.run(
                ["git", "cat-file", "-e", f"{old_sha}^{{commit}}"],
                cwd=clone,
                capture_output=True,
            ).returncode
            == 0
        ):
            log_range = [f"{old_sha}..HEAD"]
        log = run(
            ["git", "log", "--date=short", "--pretty=%h %ad %s", *log_range], cwd=clone
        )
        result["commits"] = log.decode(errors="replace").splitlines()

        archive = run(["git", "archive", "--format=tar", "HEAD"], cwd=clone)
        upstream: set[Path] = set()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar:
                # Upstream content is untrusted: regular files only, no path escapes.
                path = PurePosixPath(member.name)
                if not member.isfile() or path.is_absolute() or ".." in path.parts:
                    continue
                teacher_only = path.name in TEACHER_ONLY_NAMES
                base = TEACHER_DIR if teacher_only else MIRROR_DIR
                target = base.joinpath(*path.parts)
                upstream.add(target)
                data = tar.extractfile(member).read()
                if teacher_only:
                    result["teacher_only"].append(member.name)
                    if target.exists() and target.read_bytes() == data:
                        continue
                elif target.exists():
                    if target.read_bytes() == data:
                        continue
                    result["changed"].append(member.name)
                else:
                    result["added"].append(member.name)
                if write:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)

        if MIRROR_DIR.exists():
            result["kept"] = sorted(
                str(p.relative_to(MIRROR_DIR))
                for p in MIRROR_DIR.rglob("*")
                if p.is_file() and p.name != ".DS_Store" and p not in upstream
            )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return result


def check_profile(known: dict) -> tuple[dict, list[str], list[str]]:
    """Return (current repos, new repo names, repo names with pushes since the last sync)."""
    raw = run(
        [
            "curl",
            "-sS",
            "-m",
            "30",
            "-H",
            "Accept: application/vnd.github+json",
            API_REPOS_URL,
        ]
    )
    payload = json.loads(raw)
    if not isinstance(payload, list):
        raise RuntimeError(
            f"GitHub API: {payload.get('message', 'unexpected response')}"
        )
    current = {
        r["name"]: {
            "pushed_at": r["pushed_at"],
            "description": r.get("description") or "",
            "url": r["html_url"],
        }
        for r in payload
    }
    new = [n for n in current if n not in known]
    updated = [
        n
        for n in current
        if n in known and current[n]["pushed_at"] > known[n]["pushed_at"]
    ]
    return current, new, updated


def site_status() -> str:
    return run(
        [
            "curl",
            "-sS",
            "-L",
            "-m",
            "20",
            "-o",
            "/dev/null",
            "-w",
            "%{http_code}",
            SITE_URL,
        ]
    ).decode()


def print_list(title: str, items: list[str]) -> None:
    if not items:
        return
    print(f"  {title} ({len(items)}):")
    for item in items[:MAX_LISTED]:
        print(f"    - {item}")
    if len(items) > MAX_LISTED:
        print(f"    ... and {len(items) - MAX_LISTED} more")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check", action="store_true", help="report only; write nothing"
    )
    args = parser.parse_args()
    write = not args.check

    state = load_state()
    old_sha = state["mirror"].get("sha")
    failed = False

    print(f"== Portal mirror ({OWNER}/{REPO}) ==")
    try:
        head = remote_head()
        if head == old_sha and MIRROR_DIR.exists() and TEACHER_DIR.exists():
            print(
                f"  Up to date at {head[:7]} (last synced {state['mirror'].get('synced_at', 'unknown')})."
            )
        else:
            report = sync_mirror(old_sha, write)
            first_sync = old_sha is None
            verb = "Synced" if write else "Would sync"
            print(f"  {verb} {(old_sha or 'nothing')[:7]} -> {head[:7]}.")
            print_list("Upstream commits", report["commits"])
            if first_sync:
                print(
                    f"  Files mirrored: {len(report['added']) + len(report['changed'])}"
                )
            else:
                print_list("New files", report["added"])
                print_list("Changed files", report["changed"])
            print_list("Removed upstream, kept locally", report["kept"])
            print(
                f"  Teacher-only files stored under reference/teacher-only/: "
                f"{len(report['teacher_only'])}"
            )
            if write:
                state["mirror"] = {
                    "sha": head,
                    "synced_at": datetime.now(timezone.utc).isoformat(
                        timespec="seconds"
                    ),
                }
    except RuntimeError as exc:
        failed = True
        print(f"  Upstream unreachable; the local mirror was left untouched. ({exc})")

    print(f"\n== GitHub profile ({OWNER}) ==")
    try:
        current, new, updated = check_profile(state["repos"])
        if not state["repos"]:
            print(
                f"  First run: recorded {len(current)} public repositories as the baseline."
            )
        elif not new and not updated:
            print("  No new repositories and no new pushes since the last sync.")
        for name in new if state["repos"] else []:
            print(
                f"  NEW      {name}  {current[name]['url']}  {current[name]['description']}"
            )
        for name in updated:
            print(
                f"  UPDATED  {name}  pushed {current[name]['pushed_at'][:10]}  {current[name]['url']}"
            )
        if write:
            state["repos"] = current
    except (RuntimeError, json.JSONDecodeError) as exc:
        failed = True
        print(f"  Profile check failed. ({exc})")

    print("\n== Live site ==")
    try:
        code = site_status()
        print(
            f"  {SITE_URL} -> HTTP {code}"
            + ("" if code == "200" else "  <-- NOT OK, rely on the mirror")
        )
    except RuntimeError as exc:
        failed = True
        print(f"  Site check failed. ({exc})")

    if write:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
