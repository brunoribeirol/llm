"""Audit contextual placement against the actual packaged lesson titles."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from course import load_course
from demos import load_demo, demo_count
from flowcharts import MECHANISMS, mechanism_for, lesson_mechanisms


def main():
    rows = []
    details = []
    total_text = total_demo = 0
    for lesson in load_course():
        number = lesson["id"]
        text = [(step["title"], mechanism_for(number, step["title"])) for step in lesson["steps"]]
        matches = [(title, key) for title, key in text if key]
        if number == 6:
            demo_matches = 18  # two entry/position stages show the overview
        else:
            demo_matches = sum(bool(mechanism_for(number, step["title"])) for step in load_demo(number)["steps"])
        total_text += len(matches)
        total_demo += demo_matches
        rows.append(f'| {number:02d} | {lesson["title"]} | {len(matches)}/{len(text)} | {demo_matches}/{demo_count(number)} |')
        details.append(f'\n## Aula {number:02d}\n\nMapas disponíveis: percurso da aula' + ''.join('; ' + MECHANISMS[key]["title"] for key in lesson_mechanisms(number)) + '.\n')
        for title, key in matches:
            details.append(f'- {title} → **{MECHANISMS[key]["title"]}**')
        if not matches:
            details.append('O percurso permanece disponível na área Fluxogramas. Não foi inserido um mecanismo em títulos sem correspondência clara.')
    report = f'''# Mapa dos fluxogramas

31 mapas de percurso, {len(MECHANISMS)} mapas de mecanismos e 2 mapas de orientação (curso e sessão de estudo).

Há mapas de mecanismos junto a **{total_text} etapas de texto** e **{total_demo} etapas visuais**. As demais etapas visuais têm o percurso da aula. Os mapas são reutilizados quando o mesmo mecanismo reaparece; essas contagens indicam inserções, não diagramas distintos.

As setas do percurso representam ordem de estudo. Os mapas de mecanismos descrevem fluxo de dados, alternativas, paralelismo ou ciclos, conforme indicado. Os mapas não usam falas privadas do professor nem gabaritos. A aula 06 preserva seu player e distingue bloco original com pós-normalização de variante com pré-normalização.

| Aula | Assunto | Texto com mecanismo / total | Demonstração com mecanismo / total |
| --- | --- | --- | --- |
''' + '\n'.join(rows) + '\n\n## Manutenção\n\nEdite `flowcharts.py` e `demos/flowcharts.css`. Ao alterar títulos de etapas, confira suas associações e execute `python scripts/build_flowchart_map.py` para atualizar este relatório. O guia de uso tem uma fonte única em [COMO-USAR.md](COMO-USAR.md).\n' + '\n'.join(details) + '\n'
    (ROOT / "FLUXOGRAMAS.md").write_text(report, encoding="utf-8")
    print(f'{len(MECHANISMS) + 33} mapas; {total_text} inserções no texto; {total_demo} inserções de mecanismos nas demonstrações.')


if __name__ == "__main__":
    main()
