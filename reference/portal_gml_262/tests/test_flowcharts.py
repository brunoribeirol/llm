"""Verify coverage, contextual placement and safe offline rendering."""
import json
import re
from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

from course import load_course
from demos import demo_html, load_demo
from flowcharts import (MECHANISMS, chart, chart_html, lesson_mechanisms,
                        mechanism_for, node, overview, standalone_html)

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("lesson", range(31))
def test_each_lesson_has_a_map_and_all_associations_resolve(lesson):
    data = overview(lesson)
    assert all(stage["text"] for stage in data["stages"])
    assert len(data["stages"]) == 6
    assert set(lesson_mechanisms(lesson)) <= MECHANISMS.keys()
    steps = load_course()[lesson]["steps"]
    if lesson != 6:
        demo = load_demo(lesson)
        assert all(any(s["focus"] == i for s in demo["steps"]) for i in range(len(demo["nodes"])))
        steps = steps + demo["steps"]
    for step in steps:
        key = mechanism_for(lesson, step["title"])
        assert key is None or key in lesson_mechanisms(lesson)


def test_distinct_processes_with_similar_terms_do_not_get_confused():
    assert mechanism_for(10, "Top-k fixa quantidade, top-p fixa massa") == "decode"
    assert mechanism_for(10, "Acompanhe o roteamento top-k") == "moe"
    assert mechanism_for(6, "Encoder, decoder e cross-attention") == "seq2seq"
    assert mechanism_for(8, "MQA e GQA: cortar o KV cache pela raiz") == "kv"
    assert mechanism_for(19, "Documentos são dados, não instruções") == "security"
    assert mechanism_for(24, "Pipeline com dependências") is None
    assert mechanism_for(2, "Encerramento") is None
    assert mechanism_for(0, "Slide 12 · O calendário completo · projetado durante o setup") is None


def test_content_is_escaped_in_every_rendered_field():
    payload = '<script>alert("x")</script>'
    data = chart(payload, payload, [node(payload, payload, [payload], payload)], payload)
    html = chart_html(data, focus=0, navigable=True)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    offline = standalone_html(data)
    assert '<html lang="pt-BR">' in offline
    assert not re.search(r'<(?:script|link)[^>]+(?:src|href)=', offline)


@pytest.mark.parametrize("role", ["student", "teacher"])
def test_offline_demo_includes_contextual_diagrams_without_external_renderer(role):
    html = demo_html(18, role)
    data = json.loads(re.search(r'<script id="demo-data" type="application/json">(.*?)</script>', html, re.S)[1])
    for step in data["steps"]:
        if step["flowchart"]:
            assert step["flowchart"] in data["flowcharts"]["mechanisms"]
    assert len(data["flowcharts"]["overview"]) == 6
    transformer = demo_html(6, role)
    assert 'id="flowchart-box"' in transformer
    assert "window.renderTransformerFlow?.()" in transformer
    assert "__DEMO_" not in transformer


def test_guide_navigation_and_lesson_map_view():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90)
    identity = {"email": "student@example.edu", "name": "Estudante", "role": "student"}
    with patch("auth.require_user", return_value=identity), patch("auth.logout_button"):
        app.run()
        app.button(key="catalog_guide").click().run()
        assert app.query_params["pagina"] == ["como-usar"]
        assert app.title[0].value == "Como usar o portal"
        assert any("O caderno fica apenas na sessão atual" in m.value for m in app.markdown)
        next(b for b in app.button if b.label == "Começar pela recepção →").click().run()
        assert app.query_params["aula"] == ["0"]
        app.radio(key="view_0").set_value("Fluxogramas").run()
        assert app.selectbox(key="flowchart_0").value == 0
        assert not app.exception
        app.button(key="sidebar_guide").click().run()
        assert "aula" not in app.query_params
        assert app.title[0].value == "Como usar o portal"


@pytest.mark.parametrize("lesson", range(31))
def test_every_lesson_map_view_loads(lesson):
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90)
    app.query_params.update(aula=str(lesson), modo="fluxogramas")
    identity = {"email": "student@example.edu", "role": "student"}
    with patch("auth.require_user", return_value=identity), patch("auth.logout_button"):
        app.run()
        assert not app.exception
        assert app.radio(key=f"view_{lesson}").value == "Fluxogramas"
        if lesson_mechanisms(lesson):
            app.selectbox(key=f"flowchart_{lesson}").select(1).run()
            assert not app.exception
