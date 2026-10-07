"""Complete, offline demonstrations. The caller must authenticate first.

Instructor notes are removed before serializing student HTML, not hidden by CSS.
Only read-only curriculum data is cached; roles are explicit on every render.
"""
from functools import lru_cache
from html import escape
import json
from pathlib import Path
from flowcharts import chart_html, css as flowchart_css, mechanism_for, MECHANISMS, overview, transformer_flowcharts

ROOT = Path(__file__).resolve().parent
DEMO_ROOT = ROOT / "demos"


def demo_available(lesson_id: int) -> bool:
    if lesson_id == 6:
        return True
    group = "foundations" if lesson_id < 11 else "training" if lesson_id < 21 else "systems"
    return (DEMO_ROOT / "lessons" / f"{lesson_id:02d}.json").is_file() and (DEMO_ROOT / f"simulators-{group}.js").is_file()


def load_demo(lesson_id: int) -> dict:
    if type(lesson_id) is not int or lesson_id not in range(31) or lesson_id == 6:
        raise ValueError("Demonstração fora do catálogo.")
    path = DEMO_ROOT / "lessons" / f"{lesson_id:02d}.json"
    return _read_demo(lesson_id, path.stat().st_mtime_ns)


@lru_cache(maxsize=62)
def _read_demo(lesson_id: int, modified_ns: int) -> dict:
    data = json.loads((DEMO_ROOT / "lessons" / f"{lesson_id:02d}.json").read_text(encoding="utf-8"))
    if data["id"] != lesson_id:
        raise ValueError("Identificador de demonstração inconsistente.")
    return data


def demo_count(lesson_id: int) -> int:
    return 20 if lesson_id == 6 else len(load_demo(lesson_id)["steps"])


def demo_html(lesson_id: int, role: str, presentation: bool = False) -> str:
    if role not in {"student", "teacher"}:
        raise ValueError("Perfil sem acesso à demonstração.")
    if lesson_id == 6:
        filename = "transformer-arquitetura-interativa.html" if role == "teacher" and not presentation else "transformer-arquitetura-estudante.html"
        return transformer_flowcharts((ROOT / "content" / "aula-06" / filename).read_text(encoding="utf-8"))
    data = json.loads(json.dumps(load_demo(lesson_id), ensure_ascii=False))
    data["teacher"] = role == "teacher" and not presentation
    data["presentation"] = bool(presentation)
    data["flowcharts"] = {
        "overview": [chart_html(overview(lesson_id), focus=i, navigable=True) for i in range(len(data["nodes"]))],
        "mechanisms": {key: chart_html(value) for key, value in MECHANISMS.items()
                       if any(mechanism_for(lesson_id, step["title"]) == key for step in data["steps"])},
    }
    for step in data["steps"]:
        step["flowchart"] = mechanism_for(lesson_id, step["title"])
    if not data["teacher"]:
        for step in data["steps"]:
            step.pop("speech", None)
            step.pop("board", None)
    # Escape HTML parser terminators, including any literal </script> in text.
    serialized = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    group = "foundations" if lesson_id < 11 else "training" if lesson_id < 21 else "systems"
    template = (DEMO_ROOT / "player.html").read_text(encoding="utf-8")
    replacements = {
        "__DEMO_TITLE__": escape(data["title"]),
        "__DEMO_DATA__": serialized,
        "__DEMO_CSS__": (DEMO_ROOT / "player.css").read_text(encoding="utf-8") + flowchart_css(),
        "__DEMO_HELPERS__": (DEMO_ROOT / "helpers.js").read_text(encoding="utf-8"),
        "__DEMO_SIMULATORS__": (DEMO_ROOT / f"simulators-{group}.js").read_text(encoding="utf-8"),
        "__DEMO_PLAYER__": (DEMO_ROOT / "player.js").read_text(encoding="utf-8"),
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    return template


def demo_script(lesson_id: int, role: str) -> str:
    if role != "teacher":
        raise ValueError("O roteiro de condução é exclusivo do professor.")
    if lesson_id == 6:
        return (ROOT / "content" / "aula-06" / "roteiro-de-fala-demonstracao-transformer.md").read_text(encoding="utf-8")
    data = load_demo(lesson_id)
    lines = [f"# Aula {lesson_id:02d} — {data['title']}", "", data["subtitle"], "",
             "Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.", "",
             "## Preparação", "", "Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.", ""]
    for control in data["controls"]:
        lines.append(f"- **{control['label']}**: valor inicial `{control['value']}`.")
    for index, step in enumerate(data["steps"], 1):
        lines.extend(["", f"## {index:02d}. {step['title']}", "", "### Fala sugerida", "", step["speech"], "",
                      "### Na demonstração", "", step["action"], "", "### No quadro branco", "", step["board"], "",
                      "### Pergunta à turma", "", step["question"], "", "### Resposta e transição", "", step["answer"], ""])
        if index < len(data["steps"]):
            lines.append(f"Avance para **{data['steps'][index]['title']}** e relacione o resultado observado ao próximo mecanismo.")
    return "\n".join(lines)
