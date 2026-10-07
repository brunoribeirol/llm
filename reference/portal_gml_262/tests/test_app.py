from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def run_as(role, lesson=None, view=None):
    app = AppTest.from_file(str(APP), default_timeout=90)
    if lesson is not None:
        app.query_params["aula"] = str(lesson)
    if view:
        app.session_state[f"view_{lesson}"] = view
    with patch("auth.require_user", return_value={"email": f"{role}@example.edu", "name": "Pessoa de teste", "role": role}), patch("auth.logout_button"):
        app.run()
    return app


def test_authenticated_catalog_contains_all_lessons():
    app = run_as("student")
    assert not app.exception
    assert len([b for b in app.button if b.label == "Explorar aula →"]) == 31


@pytest.mark.parametrize("lesson", range(31))
def test_every_lesson_walkthrough(lesson):
    app = run_as("student", lesson, "Passo a passo")
    assert not app.exception
    assert app.title
    assert not any("Roteiro do professor" in x.label for x in app.expander)


@pytest.mark.parametrize("lesson", range(31))
def test_every_lesson_experiment(lesson):
    app = run_as("student", lesson, "Demonstração interativa")
    assert not app.exception


def test_teacher_receives_private_script():
    app = run_as("teacher", 6, "Passo a passo")
    assert not app.exception
    assert any("Roteiro do professor" in x.label for x in app.expander)


def test_exam_student_has_no_teacher_materials():
    app = run_as("student", 17, "Materiais")
    assert not app.exception
    assert not any("professor" in x.label.casefold() or "gabarito" in x.label.casefold() for x in app.expander)


def test_invalid_lesson_falls_back_to_catalog():
    app = run_as("student", 1000)
    assert not app.exception
    assert len([b for b in app.button if b.label == "Explorar aula →"]) == 31


def test_opening_and_revisiting_lessons_defaults_to_full_demonstration():
    app = AppTest.from_file(str(APP), default_timeout=90)
    identity = {"email": "student@example.edu", "name": "Estudante", "role": "student"}
    with patch("auth.require_user", return_value=identity), patch("auth.logout_button"):
        app.run()
        app.button(key="open_2").click().run()
        assert app.radio(key="view_2").value == "Demonstração interativa"
        app.radio(key="view_2").set_value("Materiais").run()
        next(b for b in app.button if b.label == "Próxima aula →").click().run()
        assert app.radio(key="view_3").value == "Demonstração interativa"
        next(b for b in app.button if "Todas as aulas" in b.label).click().run()
        app.button(key="open_2").click().run()
        assert app.radio(key="view_2").value == "Demonstração interativa"
        assert not app.exception


def test_notebook_completion_and_restore_update_the_same_session():
    import json
    app = AppTest.from_file(str(APP), default_timeout=90)
    app.query_params["aula"] = "18"
    app.session_state["view_18"] = "Meu caderno"
    identity = {"email": "student@example.edu", "name": "Estudante", "role": "student"}
    with patch("auth.require_user", return_value=identity), patch("auth.logout_button"):
        app.run()
        app.checkbox(key="complete_18").set_value(True).run()
        assert 18 in app.session_state["completed"]
        app.text_area(key="note_18").set_value("Minha observação").run()
        assert app.session_state["notes"]["18"] == "Minha observação"
        app.text_area(key="notebook_import").set_value(json.dumps({"version": 1, "completed": [2, 18], "notes": {"18": "Restaurada"}})).run()
        next(button for button in app.button if button.label == "Importar anotações").click().run()
        assert not app.exception
        assert app.text_area(key="note_18").value == "Restaurada"
        assert app.session_state["completed"] == {2, 18}
