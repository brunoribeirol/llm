#!/usr/bin/env python3
"""Validate the study pages: balanced tags, working relative links, parsable inline scripts.

Usage:
    python3 scripts/check_study_pages.py

Standard library only. Inline scripts are syntax-checked with ``node --check`` when Node.js
is installed; otherwise that check is reported as skipped. Exits non-zero on any problem.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
STUDY_DIR = ROOT / "study"

VOID_TAGS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "source",
        "track",
        "wbr",
    }
)


class PageParser(HTMLParser):
    """Collect unbalanced tags, link targets, element ids and inline scripts."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.problems: list[str] = []
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.scripts: list[str] = []
        self.questions = 0
        self.declared_totals: dict[str, int] = {}
        self._in_inline_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        for name in ("href", "src"):
            if attributes.get(name):
                self.links.append(attributes[name])
        if (
            tag == "details"
            and "q" in (attributes.get("class") or "").split()
            and attributes.get("id")
        ):
            self.questions += 1
        if attributes.get("data-progress-for"):
            self.declared_totals[attributes["data-progress-for"]] = int(
                attributes.get("data-total") or 0
            )
        if tag in VOID_TAGS:
            return
        self.stack.append(tag)
        if tag == "script" and "src" not in attributes:
            self._in_inline_script = True
            self.scripts.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_TAGS:
            return
        if tag == "script":
            self._in_inline_script = False
        if not self.stack or self.stack[-1] != tag:
            line, _ = self.getpos()
            expected = self.stack[-1] if self.stack else "nothing open"
            self.problems.append(
                f"line {line}: </{tag}> closes while <{expected}> is open"
            )
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
            return
        self.stack.pop()

    def handle_data(self, data: str) -> None:
        if self._in_inline_script:
            self.scripts[-1] += data


def check_links(
    page: Path, parser: PageParser, pages: dict[Path, PageParser]
) -> list[str]:
    problems = []
    for link in parser.links:
        parts = urlsplit(link)
        if parts.scheme or link.startswith("//"):
            continue
        target = (page.parent / unquote(parts.path)).resolve() if parts.path else page
        if not target.exists():
            problems.append(f"broken link: {link}")
        elif (
            parts.fragment
            and target in pages
            and parts.fragment not in pages[target].ids
        ):
            problems.append(f"missing anchor: {link}")
    return problems


def check_scripts(parser: PageParser, node: str | None) -> list[str]:
    if node is None:
        return []
    problems = []
    for index, source in enumerate(parser.scripts, start=1):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".js", encoding="utf-8", delete=False
        ) as handle:
            handle.write(source)
        try:
            proc = subprocess.run(
                [node, "--check", handle.name],
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            Path(handle.name).unlink(missing_ok=True)
        if proc.returncode != 0:
            detail = proc.stderr.strip().splitlines()
            problems.append(
                f"inline script {index} does not parse: {detail[-1] if detail else 'syntax error'}"
            )
    return problems


def main() -> int:
    paths = sorted(STUDY_DIR.glob("*.html"))
    if not paths:
        print(f"No study pages found in {STUDY_DIR}")
        return 1

    pages: dict[Path, PageParser] = {}
    for path in paths:
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8"))
        parser.close()
        if parser.stack:
            parser.problems.append(
                f"unclosed tags at end of file: {', '.join(parser.stack)}"
            )
        pages[path.resolve()] = parser

    node = shutil.which("node")
    failed = False
    for path, parser in pages.items():
        problems = (
            parser.problems
            + check_links(path, parser, pages)
            + check_scripts(parser, node)
        )
        for lesson, total in parser.declared_totals.items():
            target = (STUDY_DIR / f"{lesson}.html").resolve()
            if target in pages and pages[target].questions != total:
                problems.append(
                    f"data-total for {lesson} is {total}, page has {pages[target].questions} questions"
                )
        status = "FAIL" if problems else "ok"
        print(
            f"{status:4}  {path.relative_to(ROOT)}  ({len(parser.links)} links, {parser.questions} questions)"
        )
        for problem in problems:
            print(f"        {problem}")
        failed = failed or bool(problems)

    if node is None:
        print("note: node not found; inline script syntax was not checked")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
