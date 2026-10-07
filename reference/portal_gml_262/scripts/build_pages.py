"""Export the public student edition to docs/ for GitHub Pages.

Run from any directory: python scripts/build_pages.py
Only explicitly selected student materials enter the Pages artifact.
The original Streamlit app and its authentication remain independent.
"""
from html import escape
import json
from pathlib import Path
import shutil
import sys

import markdown

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from demos import demo_html
from course import material_path, split_frontmatter

OUTPUT = ROOT / "docs"
ASSETS = ROOT / "pages"


def render(text):
    return markdown.markdown(text, extensions=["fenced_code", "tables", "sane_lists"])


def page(title, body, prefix="", lesson_id=""):
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Aulas, demonstrações interativas e materiais de Grandes Modelos de Linguagem.">
<title>{escape(title)} · GML 2026.2</title>
<link rel="stylesheet" href="{prefix}assets/site.css">
<script defer src="{prefix}assets/site.js"></script>
<script>window.MathJax={{tex:{{inlineMath:[['$','$'],['\\\\(','\\\\)']],displayMath:[['$$','$$'],['\\\\[','\\\\]']]}}}};</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>
</head><body data-lesson="{lesson_id}">
<a class="skip" href="#main">Pular para o conteúdo</a>
<header class="topbar"><a class="brand" href="{prefix}index.html"><span class="brand-icon">G</span> GML <span class="muted">2026.2</span></a><a href="{prefix}index.html">Todas as aulas ↗</a></header>
<main id="main">{body}</main>
<footer>Grandes Modelos de Linguagem · Do Transformer aos Agentes de IA<br>Materiais de estudo e demonstrações interativas.</footer>
</body></html>'''


def build(output=OUTPUT):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "assets").mkdir(exist_ok=True)
    for name in ("site.css", "site.js"):
        shutil.copyfile(ASSETS / name, output / "assets" / name)
    (output / ".nojekyll").write_text("", encoding="utf-8")
    catalog = json.loads((ROOT / "content/catalog.json").read_text(encoding="utf-8"))
    lessons = catalog["lessons"]
    modules = list(dict.fromkeys(lesson["module"] for lesson in lessons))
    options = ''.join(f'<option value="{escape(m, quote=True)}">{escape(m)}</option>' for m in modules)
    cards = []
    for index, lesson in enumerate(lessons):
        number = lesson["id"]
        slug = f"aula-{number:02d}"
        title = lesson["title"]
        folder = output / slug
        folder.mkdir(exist_ok=True)
        (folder / "demo.html").write_text(demo_html(number, "student"), encoding="utf-8")
        cards.append(f'''<a class="card" data-title="{escape(title, quote=True)}" data-module="{escape(lesson['module'], quote=True)}" href="{slug}/index.html">
<div class="card-top"><span>AULA {number:02d}</span><span>{lesson['duration']} min</span></div>
<h2>{escape(title)}</h2><p>{escape(lesson['module'])}</p><span class="card-link">Explorar aula <span aria-hidden="true">↗</span></span></a>''')
        objectives = ''.join(f'<li>{render(item)}</li>' for item in lesson["objectives"])
        materials = []
        guide = ""
        for material in lesson["materials"]:
            if material["role"] != "student":
                continue
            source = material_path(material["path"])
            shutil.copyfile(source, folder / source.name)
            materials.append(f'<a class="button secondary" download href="{escape(source.name, quote=True)}">↓ {escape(material["label"])}</a>')
            if source.name == "guia-estudo.md":
                _, text = split_frontmatter(source.read_text(encoding="utf-8"))
                guide = render(text)
        steps = json.loads((ROOT / "content" / slug / "steps.json").read_text(encoding="utf-8"))
        reading = ''.join(f'<details><summary>{escape(step["title"])}</summary><div class="prose">{render(step["student_body"])}</div></details>' for step in steps)
        neighbors = []
        if index:
            neighbors.append(f'<a class="button secondary" href="../aula-{lessons[index-1]["id"]:02d}/index.html">← Aula anterior</a>')
        if index + 1 < len(lessons):
            neighbors.append(f'<a class="button" href="../aula-{lessons[index+1]["id"]:02d}/index.html">Próxima aula →</a>')
        body = f'''<section class="lesson-hero"><p class="eyebrow">AULA {number:02d} / {escape(lesson['module'])}</p><h1>{escape(title)}</h1>
<p class="lead">Explore o mecanismo, acompanhe o passo a passo e registre suas descobertas.</p></section>
<nav class="section-nav" aria-label="Nesta aula"><a href="#demonstracao">Demonstração</a><a href="#objetivos">Objetivos</a><a href="#leitura">Passo a passo</a><a href="#materiais">Materiais</a><a href="#caderno">Meu caderno</a></nav>
<section id="demonstracao"><div class="section-heading"><h2>Demonstração interativa</h2><a class="button secondary" href="demo.html" target="_blank" rel="noopener">Abrir em tela inteira ↗</a></div>
<iframe title="Demonstração da aula {number:02d}" src="demo.html" loading="lazy" allowfullscreen></iframe></section>
<section id="objetivos" class="panel"><p class="eyebrow">AO FINAL DESTA AULA</p><h2>O que você vai aprender</h2><ul class="objectives">{objectives}</ul></section>
<section id="leitura"><h2>Passo a passo</h2><div class="reading">{reading or '<p>Consulte o guia de estudo desta aula.</p>'}</div></section>
<section id="materiais" class="panel"><h2>Materiais de estudo</h2><div class="actions">{''.join(materials)}<a class="button secondary" download href="demo.html">↓ Demonstração offline</a></div>
<details><summary>Ler o guia de estudo</summary><article class="prose">{guide}</article></details></section>
<section id="caderno" class="panel"><p class="eyebrow">MEU CADERNO</p><h2>O que mudou na sua compreensão?</h2>
<label for="notes">Registre sua hipótese, o resultado observado e as dúvidas que ficaram.</label><textarea id="notes" rows="7" placeholder="Minha hipótese era… Ao alterar o controle, observei…"></textarea>
<p class="muted">As anotações ficam neste navegador. Exporte uma cópia para guardar ou levar a outro dispositivo.</p>
<div class="actions"><button id="export-notes">Exportar caderno</button><label class="button secondary" for="import-notes">Importar caderno</label><input id="import-notes" type="file" accept="application/json,.json"><span id="save-status" role="status"></span></div></section>
<nav class="actions neighbors" aria-label="Navegar entre aulas">{''.join(neighbors)}</nav>'''
        (folder / "index.html").write_text(page(title, body, "../", str(number)), encoding="utf-8")
    home = f'''<section class="hero"><p class="eyebrow">GRANDES MODELOS DE LINGUAGEM · 2026.2</p><h1>Entenda os mecanismos.<br><span>Construa com critério.</span></h1>
<p class="lead">Do primeiro token aos agentes de IA: um percurso de aulas, demonstrações e experimentos para entender os modelos por dentro.</p>
<div class="actions"><a class="button" href="aula-00/index.html">Começar o percurso →</a><a class="button secondary" href="#catalogo">Explorar as aulas</a></div>
<div class="stats"><span><strong>{len(lessons)}</strong> aulas</span><span><strong>{len(lessons)}</strong> demonstrações</span><span><strong>Seu ritmo</strong> de aprendizagem</span></div></section>
<section id="catalogo"><div class="section-heading"><div><p class="eyebrow">O PERCURSO COMPLETO</p><h2>Escolha sua próxima aula</h2></div><p id="result-count" role="status">{len(lessons)} aulas</p></div>
<div class="filters"><div><label for="search">Buscar por assunto</label><input id="search" type="search" placeholder="Tokenização, atenção, RAG…"></div><div><label for="module">Módulo</label><select id="module"><option value="">Todos os módulos</option>{options}</select></div></div>
<div class="grid">{''.join(cards)}</div><p id="empty" hidden>Nenhuma aula encontrada. Tente outro assunto ou módulo.</p></section>'''
    (output / "index.html").write_text(page("LLM por dentro", home), encoding="utf-8")
    print(f"Built {len(lessons)} lessons in {output}")


if __name__ == "__main__":
    build()
