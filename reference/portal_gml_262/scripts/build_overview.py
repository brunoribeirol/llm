"""Generate a reviewable table of the actual packaged lessons and experiments."""
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from course import load_course
from experiments import EXPERIMENTS

tree = ast.parse((ROOT / "experiments.py").read_text(encoding="utf-8"))
titles = {}
for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == "_intro":
                titles[node.name] = ast.literal_eval(child.args[0])
                break

rows = ["# Mapa das aulas do portal", "", "31 encontros, 552 etapas de estudo e 31 experimentos locais. A aula 06 inclui também a demonstração completa de 20 etapas em HTML.", "", "Cada aula oferece explicação por etapas, atividade manipulável, orientação de demonstração, fórmula ou registro para o quadro e uma pergunta com explicação. Os roteiros docentes completos ficam disponíveis ao professor. Os experimentos são simplificações didáticas; não executam treinamento de modelos grandes.", "", "| Aula | Tema | Etapas | Experimento |", "|---|---|---:|---|"]
for lesson in load_course():
    rows.append(f"| {lesson['id']:02d} | {lesson['title']} | {len(lesson['steps'])} | {titles[EXPERIMENTS[lesson['id']].__name__]} |")
rows += ["", "A recepção é extra-classe. A aula 17 contém orientação e exercício novo de prática para o aluno; prova oficial e gabarito são reservados ao professor. A rubrica interativa da aula 30 serve para ensaio e não substitui os critérios oficiais da disciplina.", ""]
(ROOT / "MAPA-DAS-AULAS.md").write_text("\n".join(rows), encoding="utf-8")
