"""Content, role separation and safe embedding of the complete demonstrations."""
import json
import re

import pytest

from demos import DEMO_ROOT, demo_available, demo_count, demo_html, demo_script, load_demo

NEW_LESSONS = [i for i in range(31) if i != 6]


@pytest.mark.parametrize("lesson", NEW_LESSONS)
def test_complete_lesson_has_specific_content_and_valid_controls(lesson):
    data = load_demo(lesson)
    assert data["id"] == lesson
    assert len(data["steps"]) >= (8 if lesson in {0, 17, 30} else 12)
    assert len({step["title"] for step in data["steps"]}) == len(data["steps"])
    assert len({step["view"] for step in data["steps"]}) >= 5
    assert len(data["nodes"]) >= 3
    assert len(data["controls"]) >= 2
    keys = {c["key"] for c in data["controls"]}
    assert len(keys) == len(data["controls"])
    for control in data["controls"]:
        assert control["type"] in {"range", "select", "text", "checkbox"}
        if control["type"] == "range":
            assert control["min"] <= control["value"] <= control["max"]
            assert control.get("step", 1) > 0
        if control["type"] == "select":
            assert control["value"] in [o["value"] for o in control["options"]]
    for step in data["steps"]:
        assert 0 <= step["focus"] < len(data["nodes"])
        for field in ("explanation", "action", "board", "speech", "question", "answer"):
            assert len(step[field]) >= (8 if field == "board" else 20), (lesson, step["title"], field)
        assert set(step.get("controls", [])) <= keys


@pytest.mark.parametrize("lesson", NEW_LESSONS)
def test_student_html_omits_teacher_data_and_is_standalone(lesson):
    assert demo_available(lesson)
    student = demo_html(lesson, "student")
    teacher = demo_html(lesson, "teacher")
    projection = demo_html(lesson, "teacher", presentation=True)
    pattern = r'<script id="demo-data" type="application/json">(.*?)</script>'
    student_data = json.loads(re.search(pattern, student, re.S).group(1))
    teacher_data = json.loads(re.search(pattern, teacher, re.S).group(1))
    projection_data = json.loads(re.search(pattern, projection, re.S).group(1))
    assert not student_data["teacher"] and teacher_data["teacher"]
    assert projection_data["presentation"] and not projection_data["teacher"]
    assert all("speech" not in step and "board" not in step for step in student_data["steps"])
    assert all("speech" not in step for step in projection_data["steps"])
    assert all(step["speech"] for step in teacher_data["steps"])
    assert not re.search(r'<script[^>]+src=', student)
    assert "__DEMO_" not in student
    assert len(demo_script(lesson, "teacher")) > 3000


def test_notes_are_removed_before_serialization_not_only_hidden(monkeypatch):
    data = {"id": 1, "title": "Teste", "subtitle": "Teste", "nodes": ["A"], "controls": [],
            "steps": [{"title": "Etapa", "speech": "PRIVATE-SPEECH-CANARY", "board": "PRIVATE-BOARD-CANARY",
                       "explanation": "</script><script>INJECTED()</script>", "focus": 0}]}
    monkeypatch.setattr("demos.load_demo", lambda lesson: data)
    student = demo_html(1, "student")
    assert "PRIVATE-SPEECH-CANARY" not in student
    assert "PRIVATE-BOARD-CANARY" not in student
    assert "</script><script>INJECTED()" not in student
    assert data["steps"][0]["speech"] == "PRIVATE-SPEECH-CANARY"


def test_invalid_roles_and_ids_cannot_export_notes():
    with pytest.raises(ValueError):
        demo_script(2, "student")
    with pytest.raises(ValueError):
        demo_html(2, "anonymous")
    with pytest.raises(ValueError):
        load_demo(-1)
    with pytest.raises(ValueError):
        load_demo("../../accounts")
    assert demo_count(6) == 20


def test_transformer_original_still_available():
    html = demo_html(6, "teacher")
    assert "O Transformer, peça por peça." in html
    assert "window.lessonSnapshot" in html
