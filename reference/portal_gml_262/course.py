"""Course catalog and Markdown segmentation; no Streamlit dependency.

The original instructor scripts remain verbatim in content/. Public reading
versions are derived at build time and deliberately omit backstage directions.
Authentication/authorization must precede serving any catalog or material.
"""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re
from typing import Any

import yaml

CONTENT_DIR = Path(__file__).resolve().parent / "content"


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"\A\ufeff?---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
    if not match:
        return {}, text
    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise ValueError("O cabeçalho da aula deve ser um mapa YAML.")
    return metadata, text[match.end():].strip()


def markdown_sections(text: str) -> list[dict[str, Any]]:
    """Split headings while preserving fenced code and every body line."""
    sections: list[dict[str, Any]] = []
    current = {"level": 0, "title": "", "lines": []}
    fence: str | None = None
    for line in text.splitlines():
        fence_match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            current["lines"].append(line)
            continue
        heading = re.match(r"^(#{1,3})\s+(.+?)\s*#*\s*$", line) if fence is None else None
        if heading:
            sections.append({"level": current["level"], "title": current["title"],
                             "body": "\n".join(current["lines"]).strip()})
            current = {"level": len(heading.group(1)), "title": heading.group(2), "lines": []}
        else:
            current["lines"].append(line)
    sections.append({"level": current["level"], "title": current["title"],
                     "body": "\n".join(current["lines"]).strip()})
    return sections


def student_text(text: str) -> str:
    """Remove complete explicit instructor-note paragraphs, retaining equations/code."""
    blocks = re.split(r"\n\s*\n", text.strip())
    output: list[str] = []
    fence = False
    for block in blocks:
        is_code = fence or bool(re.match(r"\s*(```|~~~)", block))
        if len(re.findall(r"(?m)^\s*(?:```|~~~)", block)) % 2:
            fence = not fence
        teacher_note = re.search(
            r"(?:\*\*)?(?:Bastidor|Nota ao (?:professor|instrutor)|"
            r"Orientaç(?:ão|ões) (?:ao|para o) (?:professor|instrutor)|"
            r"instructor-only)(?:\*\*)?\s*:?", block, re.I
        )
        if teacher_note and not is_code:
            continue
        output.append(block.replace("🗣️", "Ideia central:"))
    return "\n\n".join(output).strip()


def extract_objectives(plan: str) -> list[str]:
    for section in markdown_sections(plan):
        if re.search(r"resultados (?:de aprendizagem|esperados)", section["title"], re.I):
            items: list[str] = []
            current: list[str] = []
            blank = False
            for line in section["body"].splitlines():
                item = re.match(r"^\d+\.\s+(.+)$", line)
                if item:
                    if current:
                        items.append(" ".join(current))
                    current = [item.group(1).strip()]
                    blank = False
                elif not line.strip():
                    blank = True
                elif current:
                    # An unindented paragraph after a blank line belongs to
                    # the section, not to the final numbered objective.
                    if blank and not line[:1].isspace():
                        break
                    current.append(line.strip())
                    blank = False
            if current:
                items.append(" ".join(current))
            return items
    return []


def extract_cues(body: str) -> dict[str, Any]:
    """Use source evidence for board prompts and questions; never fabricate an answer."""
    student = student_text(body)
    anchors = re.findall(r"(?m)^>\s*(?:Ideia central:|🗣️)\s*(.+)$", student)
    math = re.findall(r"\$\$(.*?)\$\$|\\\[(.*?)\\\]", student, re.S)
    board = "\n\n".join(anchors[:2])
    if math:
        board += ("\n\n" if board else "") + "\n\n".join("$$" + (a or b).strip() + "$$" for a, b in math[:2])
    questions: list[str] = []
    for block in re.split(r"\n\s*\n", student):
        if "?" in block and not re.match(r"\s*(```|~~~|\|)", block):
            flat = re.sub(r"\s+", " ", block).strip(" >")
            # Ask the actual interrogative sentence, not the paragraph containing
            # both the question and the explanation of its answer.
            for match in re.finditer(r"(?:^|(?<=[.!?])\s+)([^.!?]*\?)", flat):
                question = match.group(1).strip(' >“"')
                question = re.sub(r"^(?:Ideia central:|Pergunta(?: à turma)?):?\s*", "", question, flags=re.I)
                if 10 <= len(question) <= 350 and question not in questions:
                    questions.append(question)
    return {"board": board, "questions": questions[:3], "question": questions[0] if questions else ""}


def parse_steps(script: str) -> list[dict[str, Any]]:
    _, body = split_frontmatter(script)
    result = []
    group = "Aula"
    for section in markdown_sections(body):
        level, title, text = section["level"], section["title"], section["body"]
        if level == 2:
            group = title
        if level < 2 or "como usar" in title.lower() or not text.strip("\n -"):
            continue
        # H2 part introductions are useful steps, but empty part labels are not.
        stage = "explanation"
        if re.search(r"apêndice|se perguntarem", group, re.I):
            stage = "appendix"
        elif re.search(r"hands-on|setup|protocolo", group, re.I):
            stage = "practice"
        elif re.search(r"demonstração", group, re.I):
            stage = "demonstration"
        clean = student_text(text)
        result.append({"title": title, "body": text, "student_body": clean,
                       "section": group, "stage": stage, **extract_cues(text)})
    return result


@lru_cache(maxsize=1)
def load_course() -> list[dict[str, Any]]:
    index = json.loads((CONTENT_DIR / "catalog.json").read_text(encoding="utf-8"))
    lessons = []
    for entry in index["lessons"]:
        lesson_dir = CONTENT_DIR / f"aula-{entry['id']:02d}"
        lesson = dict(entry)
        lesson["plan"] = (lesson_dir / "plano.md").read_text(encoding="utf-8")
        lesson["script"] = (lesson_dir / "roteiro.md").read_text(encoding="utf-8") if (lesson_dir / "roteiro.md").exists() else ""
        lesson["steps"] = json.loads((lesson_dir / "steps.json").read_text(encoding="utf-8"))
        lessons.append(lesson)
    return lessons


def material_path(relative_path: str) -> Path:
    """Resolve only existing packaged files inside the content root."""
    root = CONTENT_DIR.resolve()
    candidate = (root / relative_path).resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        raise ValueError("Material indisponível.")
    return candidate


def materials_for_role(lesson: dict[str, Any], role: str) -> list[dict[str, Any]]:
    if role not in {"student", "teacher"}:
        return []
    return [m for m in lesson.get("materials", []) if m["role"] == "student" or role == "teacher"]
