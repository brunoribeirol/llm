"""Export instructor scripts and the demonstration map from authored content."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from course import load_course
from demos import demo_count, demo_script


def main():
    target = ROOT / "demos" / "roteiros"
    target.mkdir(exist_ok=True)
    lessons = load_course()
    rows = []
    for lesson in lessons:
        number = lesson["id"]
        (target / f"roteiro-demonstracao-aula-{number:02d}.md").write_text(demo_script(number, "teacher"), encoding="utf-8")
        rows.append(f'| {number:02d} | {lesson["title"]} | {demo_count(number)} |')
    total = sum(demo_count(lesson["id"]) for lesson in lessons)
    text = f"""# Demonstrações completas do curso

31 demonstrações, {total} etapas visuais. Cada aula abre diretamente na demonstração interativa. O percurso de 20 etapas da aula 06 foi preservado.

Cada percurso contém visualizações próprias do tema, controles, explicação, orientação para observar os resultados e pergunta com resposta. O professor também recebe fala sugerida e orientação para o quadro. Os valores são calculados localmente ou identificados como simulações didáticas.

As 552 etapas de estudo originais continuam na aba **Passo a passo**. Os experimentos Python continuam como complementos abaixo de cada demonstração.

| Aula | Tema | Etapas visuais |
|---|---|---:|
""" + "\n".join(rows) + """

## Como demonstrar

1. Abra uma aula: a demonstração completa é a tela inicial.
2. Navegue pela lista lateral ou pelos botões Voltar e Avançar.
3. Leia a previsão/pergunta, altere os controles e compare os valores.
4. Use Restaurar controles para repetir a experiência inicial.
5. Para projetar, ative Modo projeção na demonstração ou Modo apresentação no portal.
6. Em Materiais, baixe o HTML autônomo e, no perfil professor, o roteiro da demonstração.

Os roteiros separados estão em `demos/roteiros/roteiro-demonstracao-aula-NN.md`. A versão HTML do estudante é gerada sem os dados de fala e quadro do professor. A aula 17 é revisão inédita, sem a prova oficial ou seu gabarito; a aula 30 ensaia a apresentação, sem substituir os critérios oficiais.

## Autoria e manutenção

- Conteúdo: `demos/lessons/NN.json`.
- Cálculos e visualizações: `demos/simulators-foundations.js`, `simulators-training.js`, `simulators-systems.js`.
- Apresentação compartilhada: `demos/player.html`, `player.css`, `player.js`, `helpers.js`.
- Integração e separação de perfis: `demos.py`.
- Atualização deste mapa e dos roteiros: `python scripts/build_demo_scripts.py`, executado na pasta portal.

Após editar o conteúdo JSON, reinicie o Streamlit para renovar o cache do catálogo de demonstrações.
"""
    (ROOT / "DEMONSTRACOES.md").write_text(text, encoding="utf-8")
    print(f"31 roteiros exportados; {total} etapas visuais.")


if __name__ == "__main__":
    main()
