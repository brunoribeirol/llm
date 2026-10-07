from pathlib import Path
import hashlib
import re
import sys
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course import (extract_cues, extract_objectives, load_course, markdown_sections, material_path, materials_for_role,
                    parse_steps, split_frontmatter, student_text)


def test_all_31_lessons_have_substantive_content_and_unique_ids():
    lessons = load_course()
    assert [lesson["id"] for lesson in lessons] == list(range(31))
    assert sum(lesson["duration"] for lesson in lessons if lesson["id"] > 0) == 3600
    for lesson in lessons:
        assert lesson["objectives"], lesson["id"]
        assert len(lesson["steps"]) >= 5, lesson["id"]
        assert sum(len(step["student_body"]) for step in lesson["steps"]) >= 1800
        assert all(step["title"] and step["body"] for step in lesson["steps"])
        assert all(step["student_body"].strip() for step in lesson["steps"])


def test_fenced_code_heading_is_not_a_step():
    script = "## Parte 1\n### Uma etapa\nTexto.\n```python\n## comment\n### still a comment\nprint(1)\n```\n### Outra\nFim."
    steps = parse_steps(script)
    assert [s["title"] for s in steps] == ["Uma etapa", "Outra"]
    assert "### still a comment" in steps[0]["body"]


def test_frontmatter_and_unicode_survive():
    metadata, body = split_frontmatter('---\naula: 6\ntitulo: "Atenção"\n---\n\n# Seção')
    assert metadata == {"aula": 6, "titulo": "Atenção"}
    assert body == "# Seção"


def test_backstage_multiline_block_removed_but_formula_kept():
    text = "Conceito.\n\n> **Nota:** Bastidor: esperar.\n> Não projetar isto.\n\n$$QK^T$$\n\n> 🗣️ Ideia pública."
    result = student_text(text)
    assert "Bastidor" not in result
    assert "Não projetar" not in result
    assert "$$QK^T$$" in result
    assert "Ideia pública" in result


def test_exam_public_content_does_not_contain_actual_exam_or_answer_key():
    exam = load_course()[17]
    assert "Q1 —" in exam["plan"]  # Real paper is retained for the teacher.
    public = "\n".join(s["student_body"] for s in exam["steps"])
    for secret in ["1.480", "consensus@10", "Q7", "causa mais provável", "gabarito.md"]:
        assert secret not in public
    files = materials_for_role(exam, "student")
    assert len(files) == 1 and files[0]["path"].endswith("guia-estudo.md")
    assert any(m["path"].endswith("gabarito.md") for m in materials_for_role(exam, "teacher"))
    assert materials_for_role(exam, "anonymous") == []


def test_packaged_materials_integrity_and_no_external_papers():
    for lesson in load_course():
        for material in lesson["materials"]:
            data = material_path(material["path"]).read_bytes()
            assert len(data) == material["bytes"]
            assert hashlib.sha256(data).hexdigest() == material["sha256"]
            assert not material["path"].lower().endswith(".pdf")
            assert material["mime"] == {".md": "text/markdown", ".html": "text/html", ".zip": "application/zip"}[Path(material["path"]).suffix]
            assert material["label"].strip()


def test_material_path_rejects_directory_traversal():
    with pytest.raises(ValueError):
        material_path("../course.py")


def test_instructor_source_is_packaged_verbatim():
    root = Path(__file__).resolve().parents[2]
    for lesson in load_course():
        source = root / "v2" / "aulas" / f"aula-{lesson['id']:02d}" / "roteiro.md"
        if source.exists():
            assert source.read_text(encoding="utf-8") == lesson["script"]


def test_all_original_packaged_materials_are_exact_copies():
    root = Path(__file__).resolve().parents[2] / "v2" / "aulas"
    if not root.exists():
        pytest.skip("Source checkout is not part of the standalone deploy package.")
    for lesson in load_course():
        for material in lesson["materials"]:
            if material["path"].endswith("guia-estudo.md") or "derived_from" in material:
                if "source_sha256" in material:
                    assert hashlib.sha256((root / material["derived_from"]).read_bytes()).hexdigest() == material["source_sha256"]
                continue
            assert material_path(material["path"]).read_bytes() == (root / material["path"]).read_bytes()


def test_objectives_do_not_capture_revision_notes_after_the_list():
    plan = "## 2. Resultados esperados\n\nAo final:\n\n1. Explicar\n   a atenção.\n2. Calcular vetores.\n\n*(Nota de revisão V1.)*\n\n## 3. Conteúdo\nTexto."
    assert extract_objectives(plan) == ["Explicar a atenção.", "Calcular vetores."]
    assert all("Idênticos aos da V1" not in objective for lesson in load_course() for objective in lesson["objectives"])


def test_question_cue_does_not_include_its_answer():
    cues = extract_cues("Vamos comparar. Por que usar uma máscara? Porque tokens futuros não estão disponíveis.")
    assert cues["question"] == "Por que usar uma máscara?"
    assert "Porque" not in cues["question"]


def test_student_transformer_does_not_contain_teacher_speech_data():
    teacher = material_path("aula-06/transformer-arquitetura-interativa.html").read_text(encoding="utf-8")
    student = material_path("aula-06/transformer-arquitetura-estudante.html").read_text(encoding="utf-8")
    for field in ("speech", "board"):
        assert len(re.findall(rf"{field}:''", student)) == 20
        original_values = re.findall(rf"{field}:'((?:\\.|[^'\\])*)'", teacher)
        assert len(original_values) == 20
        assert all(value not in student for value in original_values)
    assert 'id="question"' in student and 'id="answer"' in student
    assert 'id="speech" hidden' in student and 'id="board" hidden' in student
    assert "Confira sua compreensão" in student
    assert not re.search(r'<a href="(?!https?://|#)', student)
    assert not re.search(r'<a href="(?!https?://|#)', teacher)


def test_student_code_archives_exclude_solutions_and_notebook_outputs():
    import json
    archives = [m for lesson in load_course() for m in lesson["materials"] if m["path"].endswith("codigo-student.zip")]
    assert len(archives) >= 8
    for material in archives:
        with zipfile.ZipFile(material_path(material["path"])) as archive:
            for name in archive.namelist():
                assert not re.search(r"solu[cç][aã]o|gabarito|solution", name, re.I)
                if name.endswith(".ipynb"):
                    notebook = json.loads(archive.read(name))
                    for cell in notebook["cells"]:
                        assert not cell.get("outputs")
