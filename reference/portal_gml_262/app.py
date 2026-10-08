"""Authenticated interactive teaching portal, built from the course's original scripts."""
from collections import defaultdict
from html import escape
from pathlib import Path
import re

import streamlit as st

from auth import require_user, logout_button, render_account_admin, render_password_settings
from course import load_course, materials_for_role
from downloads import download_link
from demos import demo_available, demo_count, demo_html, demo_script
from progress import export_notebook, import_notebook
from flowcharts import (COURSE_MAP, STUDY_MAP, MECHANISMS, chart_html, css as flowchart_css,
                        lesson_mechanisms, mechanism_for, overview, standalone_html)

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="LLM · Do Transformer aos Agentes", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
:root {--course-green:#146952;--course-ink:#173347}
.stApp {background:#fffdf8;color:var(--course-ink)}
[data-testid="stSidebar"] {background:#edf4f0;border-right:1px solid #d6e1db}
.block-container {padding-top:2.2rem;max-width:1450px}
h1,h2,h3 {letter-spacing:-.025em;color:#173347}
h1 {font-size:2.7rem!important;line-height:1.15!important}
.course-kicker {color:#146952;font-size:.76rem;font-weight:750;letter-spacing:.15em;text-transform:uppercase;margin-bottom:12px}
.course-lead {color:#586b78;font-size:1.1rem;max-width:880px;line-height:1.7}
.course-tag {display:inline-block;background:#eaf5ef;color:#146952;padding:5px 11px;border-radius:18px;font-size:.8rem;margin:3px 5px 3px 0}
.course-rule {height:4px;background:linear-gradient(90deg,#146952 0%,#146952 44%,#204dc1 44%,#204dc1 77%,#e5af48 77%);border-radius:4px;margin:22px 0 30px}
.course-quote {background:#fff5df;border-left:4px solid #c88c2f;padding:15px 19px;line-height:1.7;margin:16px 0}
[data-testid="stMetric"] {background:#f1f6f3;border:1px solid #d6e1db;border-radius:12px;padding:14px 18px}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:12px}
button[kind="primary"] {background:#146952;border-color:#146952}
@media(max-width:700px){h1{font-size:2rem!important}.block-container{padding-top:4.5rem}}
</style>""", unsafe_allow_html=True)
st.html('<style>' + flowchart_css() + '</style>')

# Authenticate before reading or rendering any course material.
user = require_user()
teacher = user["role"] == "teacher"
lessons = load_course()
by_id = {lesson["id"]: lesson for lesson in lessons}
st.session_state.setdefault("completed", set())
st.session_state.setdefault("notes", {})


def open_lesson(lesson_id):
    if "pagina" in st.query_params:
        del st.query_params["pagina"]
    st.query_params["aula"] = str(lesson_id)
    st.query_params["etapa"] = "0"
    st.query_params["modo"] = "demo"


def selected_lesson():
    try:
        return int(st.query_params.get("aula", ""))
    except (TypeError, ValueError):
        return None


def plain_title(text):
    return re.sub(r"\*|`", "", text).strip()


def render_catalog():
    st.markdown('<div class="course-kicker">Graduação em Ciência da Computação · 60 horas</div>', unsafe_allow_html=True)
    st.title("Do Transformer aos Agentes de IA")
    st.markdown('<p class="course-lead">Um curso para explorar por dentro. Percorra as explicações, altere os experimentos e acompanhe o caminho do primeiro token até um sistema de agentes avaliado.</p><div class="course-rule"></div>', unsafe_allow_html=True)
    a, b, c, d = st.columns(4)
    a.metric("Encontros", "31")
    b.metric("Laboratórios", "8")
    c.metric("Etapas de estudo", str(sum(len(x["steps"]) for x in lessons)))
    d.metric("Concluídas nesta sessão", str(len(st.session_state.completed)))
    st.write("")
    st.button("Como usar o portal →", on_click=open_guide, key="catalog_guide")
    with st.expander("O mapa do curso · do texto ao sistema avaliado"):
        st.html(chart_html(COURSE_MAP))
    search = st.text_input("Encontre uma aula", placeholder="Busque por tokenização, LoRA, RAG, agentes…", key="catalog_search")
    modules = defaultdict(list)
    for lesson in lessons:
        if not search or search.casefold() in f'{lesson["title"]} {lesson["module"]} {lesson["id"]:02d}'.casefold():
            modules[lesson["module"]].append(lesson)
    if not modules:
        st.info("Nenhuma aula corresponde à busca.")
    for module, items in modules.items():
        st.subheader(module)
        for start in range(0, len(items), 3):
            columns = st.columns(3)
            for col, lesson in zip(columns, items[start:start + 3]):
                with col, st.container(border=True):
                    done = " · concluída" if lesson["id"] in st.session_state.completed else ""
                    st.caption(f'AULA {lesson["id"]:02d} · {lesson["duration"]} MIN{done}')
                    st.markdown(f'**{lesson["title"]}**')
                    st.caption(f'{len(lesson["steps"])} etapas de estudo · {kind_label(lesson["kind"])}')
                    if demo_available(lesson["id"]):
                        st.caption(f'Demonstração completa · {demo_count(lesson["id"])} etapas visuais')
                    st.button("Explorar aula →", key=f'open_{lesson["id"]}', on_click=open_lesson, args=(lesson["id"],), width="stretch")
    st.caption("A recepção é extra-classe. As aulas 01 a 30 compõem as 60 horas da disciplina.")


def kind_label(kind):
    return {"teorica": "Teoria e demonstração", "laboratorio": "Laboratório", "pratica": "Laboratório", "avaliacao": "Avaliação", "apresentacao": "Projetos", "recepcao": "Recepção"}.get(kind, kind)


def open_guide():
    st.query_params.clear()
    st.query_params["pagina"] = "como-usar"


def render_guide():
    st.markdown('<div class="course-kicker">Comece por aqui</div>', unsafe_allow_html=True)
    st.title("Como usar o portal")
    st.write("Conheça os recursos e monte seu percurso de estudo, da primeira aula ao projeto final.")
    guide = (ROOT / "COMO-USAR.md").read_text(encoding="utf-8")
    download_link("Baixar guia de uso (.md)", guide, "como-usar-portal-llm.md", "text/markdown")
    with st.expander("Uma sessão de estudo · ver o fluxograma"):
        st.html(chart_html(STUDY_MAP))
    # The same text is available in the portal and in the downloadable guide.
    st.markdown(guide.split("\n", 1)[1])
    left, right = st.columns(2)
    left.button("Começar pela recepção →", on_click=open_lesson, args=(0,), width="stretch")
    right.button("Explorar a primeira aula →", on_click=open_lesson, args=(1,), width="stretch")


def render_flowcharts(lesson):
    st.subheader("Fluxogramas desta aula")
    st.caption("Siga as setas, compare as ramificações e observe as condições de retorno. Clique no título de uma etapa para recolher ou expandir a explicação.")
    charts = [("Percurso da aula", overview(lesson["id"]))] + [(MECHANISMS[key]["title"], MECHANISMS[key]) for key in lesson_mechanisms(lesson["id"])]
    selected = st.selectbox("Escolha um fluxograma", range(len(charts)), format_func=lambda i: charts[i][0], key=f'flowchart_{lesson["id"]}')
    data = charts[selected][1]
    st.html(chart_html(data))
    download_link("Baixar este fluxograma (.html)", standalone_html(data), f'fluxograma-aula-{lesson["id"]:02d}-{selected}.html', "text/html")


def render_materials(lesson):
    st.subheader("Materiais desta aula")
    if demo_available(lesson["id"]):
        download_link("Demonstração interativa completa (.html)", demo_html(lesson["id"], user["role"]), f'demonstracao-aula-{lesson["id"]:02d}.html', "text/html")
        if teacher:
            download_link("Roteiro de fala da demonstração (.md)", demo_script(lesson["id"], "teacher"), f'roteiro-demonstracao-aula-{lesson["id"]:02d}.md', "text/markdown")
    count = 0
    base = (ROOT / "content").resolve()
    for item in materials_for_role(lesson, user["role"]):
        candidate = (base / item["path"]).resolve()
        if not candidate.is_relative_to(base) or not candidate.is_file():
            continue
        download_link(item.get("label", candidate.name), candidate.read_bytes(), candidate.name, item.get("mime", "text/plain"))
        count += 1
    if not count:
        st.info("Use as etapas desta aula e as atividades do laboratório interativo.")
    if teacher:
        with st.expander("Plano completo da aula · professor"):
            st.markdown(lesson["plan"])
        if lesson.get("script"):
            with st.expander("Roteiro de fala completo · professor"):
                st.markdown(lesson["script"])


def render_notebook(lesson):
    st.subheader("Meu caderno")
    st.caption("As anotações e conclusões ficam nesta sessão. Baixe seu caderno para guardá-las e importe o arquivo quando voltar.")
    lesson_key = str(lesson["id"])
    note = st.text_area("O que observei, o que calculei, o que ainda quero investigar", value=st.session_state.notes.get(lesson_key, ""), max_chars=10000, height=230, key=f'note_{lesson_key}')
    st.session_state.notes[lesson_key] = note
    def update_completion():
        if st.session_state[f'complete_{lesson_key}']:
            st.session_state.completed.add(lesson["id"])
        else:
            st.session_state.completed.discard(lesson["id"])

    st.checkbox("Concluí esta aula", value=lesson["id"] in st.session_state.completed, key=f'complete_{lesson_key}', on_change=update_completion)
    download_link("Baixar meu caderno (.json)", export_notebook(st.session_state.completed, st.session_state.notes), "meu-caderno-llm.json", "application/json")
    if message := st.session_state.pop("notebook_notice", None):
        st.success(message)
    if error := st.session_state.pop("notebook_error", None):
        st.error(error)

    def restore_from_form():
        # A widget callback runs before the next script render. Updating here
        # also replaces the values already held by the browser's text inputs.
        try:
            completed, notes = import_notebook(st.session_state.notebook_import)
        except ValueError as exc:
            st.session_state.notebook_error = str(exc)
            return
        st.session_state.completed = completed
        st.session_state.notes = notes
        for key in list(st.session_state):
            if key.startswith("note_") and key[5:].isdigit():
                st.session_state[key] = notes.get(key[5:], "")
            elif key.startswith("complete_") and key[9:].isdigit():
                st.session_state[key] = int(key[9:]) in completed
        st.session_state.notebook_notice = "Caderno restaurado. Suas anotações e aulas concluídas foram atualizadas."

    with st.expander("Restaurar caderno de uma sessão anterior"):
        with st.form("restore_notebook"):
            st.text_area("Abra o arquivo .json em um editor e cole seu conteúdo aqui", max_chars=200000, key="notebook_import")
            st.form_submit_button("Importar anotações", on_click=restore_from_form)


def render_walkthrough(lesson, presentation):
    steps = lesson["steps"]
    if not steps:
        st.info("Explore a atividade interativa e os materiais desta aula.")
        return
    try:
        index = max(0, min(int(st.query_params.get("etapa", "0")), len(steps) - 1))
    except (TypeError, ValueError):
        index = 0
    selected = st.selectbox("Ir para uma etapa", range(len(steps)), index=index, format_func=lambda i: f'{i+1:02d} · {plain_title(steps[i]["title"])}', key=f'jump_{lesson["id"]}_{index}')
    if selected != index:
        st.query_params["etapa"] = str(selected)
        st.rerun()
    step = steps[index]
    st.progress((index + 1) / len(steps), text=f'Etapa {index + 1} de {len(steps)}')
    st.subheader(plain_title(step["title"]))
    with st.container(border=True):
        st.markdown(step.get("student_body", step["body"]))
    if key := mechanism_for(lesson["id"], step["title"]):
        with st.expander("Fluxograma desta explicação · " + MECHANISMS[key]["title"], expanded=True):
            st.html(chart_html(MECHANISMS[key]))
    if step.get("board"):
        with st.expander("No quadro branco", expanded=presentation):
            st.markdown(step["board"])
    if step.get("question"):
        st.info(step["question"], icon="💬")
        if step.get("answer"):
            with st.expander("Conferir raciocínio"):
                st.markdown(step["answer"])
    if teacher and not presentation:
        with st.expander("Roteiro do professor · fala e condução"):
            st.markdown(step["body"])
    previous, center, following = st.columns([1, 2, 1])
    if previous.button("← Anterior", disabled=index == 0, width="stretch"):
        st.query_params["etapa"] = str(index - 1)
        st.rerun()
    center.caption("Leia, antecipe o resultado e confira na demonstração interativa.")
    if following.button("Próxima →", disabled=index == len(steps) - 1, width="stretch"):
        st.query_params["etapa"] = str(index + 1)
        st.rerun()


def render_lesson(lesson):
    st.markdown(f'<div class="course-kicker">Aula {lesson["id"]:02d} · {escape(lesson["module"])}</div>', unsafe_allow_html=True)
    st.title(lesson["title"])
    st.markdown(f'<span class="course-tag">{lesson["duration"]} minutos</span><span class="course-tag">{escape(kind_label(lesson["kind"]))}</span><span class="course-tag">{len(lesson["steps"])} etapas</span>', unsafe_allow_html=True)
    if lesson.get("objectives"):
        with st.expander("O que você será capaz de fazer"):
            for objective in lesson["objectives"]:
                st.markdown(f"- {objective}")
    presentation = st.toggle("Modo apresentação · ampliar a leitura e ocultar as notas do professor", key="presentation_mode")
    if presentation:
        st.markdown('<style>[data-testid="stSidebar"]{display:none}.stMarkdown p,.stMarkdown li{font-size:1.15rem}</style>', unsafe_allow_html=True)
    views = {"aula": "Passo a passo", "demo": "Demonstração interativa", "fluxogramas": "Fluxogramas", "materiais": "Materiais", "caderno": "Meu caderno"}
    view_key = st.query_params.get("modo", "demo")
    default_view = list(views).index(view_key) if view_key in views else 0
    view = st.radio("Como explorar", list(views.values()), index=default_view, horizontal=True, key=f'view_{lesson["id"]}', label_visibility="collapsed")
    st.query_params["modo"] = next(key for key, label in views.items() if label == view)
    st.divider()
    if view == "Passo a passo":
        render_walkthrough(lesson, presentation)
    elif view == "Demonstração interativa":
        if demo_available(lesson["id"]):
            st.caption(f'{demo_count(lesson["id"])} etapas visuais · navegação livre · controles para explorar cada mecanismo. Use a rolagem interna para ver a etapa completa.')
            st.iframe(demo_html(lesson["id"], user["role"], presentation), height=1120)
        else:
            st.info("A demonstração completa desta aula está sendo preparada. O experimento complementar está disponível abaixo.")
        if st.toggle("Abrir experimento complementar em Python", key=f'experiment_open_{lesson["id"]}'):
            from experiments import render_experiment
            render_experiment(lesson["id"])
    elif view == "Materiais":
        render_materials(lesson)
    elif view == "Fluxogramas":
        render_flowcharts(lesson)
    else:
        render_notebook(lesson)
    st.divider()
    left, middle, right = st.columns([1, 2, 1])
    if lesson["id"] > 0:
        left.button("← Aula anterior", on_click=open_lesson, args=(lesson["id"] - 1,), width="stretch")
    middle.caption("Observe → formule uma hipótese → altere um controle → explique o resultado.")
    if lesson["id"] < 30:
        right.button("Próxima aula →", on_click=open_lesson, args=(lesson["id"] + 1,), width="stretch")


with st.sidebar:
    st.markdown("### ◈ LLM por dentro")
    st.caption("DO TRANSFORMER AOS AGENTES")
    st.write(user.get("name") or user["email"])
    st.caption("Professor" if teacher else "Estudante")
    st.button("Como usar o portal", on_click=open_guide, key="sidebar_guide", width="stretch")
    if st.button("⌂ Todas as aulas", width="stretch"):
        st.query_params.clear()
        st.rerun()
    current = selected_lesson()
    choices = [None] + list(by_id)
    navigation = st.selectbox("Navegar pelo curso", choices, index=choices.index(current) if current in choices else 0, format_func=lambda i: "Selecione uma aula" if i is None else f'{i:02d} · {by_id[i]["title"]}', key=f'course_nav_{current}')
    if navigation is not None and navigation != current:
        open_lesson(navigation)
        st.rerun()
    st.divider()
    st.caption("SEU PERCURSO NESTA SESSÃO")
    st.progress(len(st.session_state.completed) / 31, text=f'{len(st.session_state.completed)} de 31 encontros')
    st.caption("Guarde anotações e conclusão em Meu caderno.")
    st.divider()
    if teacher and st.button("Gerenciar turma", width="stretch"):
        st.query_params.clear()
        st.query_params["pagina"] = "contas"
        st.rerun()
    if st.button("Minha conta", width="stretch"):
        st.query_params.clear()
        st.query_params["pagina"] = "minha-conta"
        st.rerun()
    logout_button()

lesson_id = selected_lesson()
if st.query_params.get("pagina") == "como-usar":
    render_guide()
elif teacher and st.query_params.get("pagina") == "contas":
    render_account_admin()
elif st.query_params.get("pagina") == "minha-conta":
    render_password_settings()
elif lesson_id in by_id:
    render_lesson(by_id[lesson_id])
else:
    render_catalog()
st.caption("Grandes Modelos de Linguagem · Material didático do curso · Experimentos locais e simplificados, sem chamadas a APIs de IA.")
