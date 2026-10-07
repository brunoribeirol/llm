"""Package the authored V2 course. Run from anywhere: python scripts/build_content.py.

No network, third-party PDFs, notebook outputs, or credentials are copied.
Solution code is available only in the separately authorized teacher archive.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import re
import sys
import zipfile

PORTAL = Path(__file__).resolve().parents[1]
SOURCE = PORTAL.parent / "v2" / "aulas"
sys.path.insert(0, str(PORTAL))
from course import extract_objectives, parse_steps, split_frontmatter  # noqa: E402


EXAM_STEPS = [
    {"title": "O que a avaliação verifica", "student_body": "A avaliação individual cobre as aulas 1 a 16. O objetivo é usar fundamentos para diagnosticar comportamentos, interpretar experimentos e justificar escolhas de arquitetura.\n\nOrganize a revisão em quatro ações: explicar um mecanismo; interpretar uma evidência; propor uma intervenção; indicar como verificar se ela funcionou.", "board": "Sintoma → hipótese → evidência → intervenção → verificação", "question": "Você consegue explicar uma decisão de arquitetura e indicar uma medição que poderia refutá-la?"},
    {"title": "Mapa de revisão dos fundamentos", "student_body": "Retome tokenização e custo (aulas 2–4), contexto e atenção (5–8), treinamento do mini-GPT (9), escala e decodificação (10–11), pré-treinamento e adaptação (12–14), alinhamento e raciocínio (15–16).\n\nPara cada tema, use o experimento da respectiva aula: registre uma previsão antes de mover o controle, observe a saída e explique a diferença. Uma fórmula deve vir acompanhada de suas hipóteses e dimensões.", "board": "Texto → tokens → vetores → atenção → logits → distribuição\n\nPré-treino → SFT → preferências / recompensa verificável", "question": "Em que etapa do sistema cada técnica atua, e que problema ela deixa sem resolver?"},
    {"title": "Como sustentar uma resposta", "student_body": "Uma resposta técnica liga uma afirmação a uma razão e a uma evidência. Explicite as condições do argumento: mesma tokenização para certas comparações, mesmo orçamento computacional para outras, separação entre treino e teste.\n\nAo interpretar uma métrica, identifique unidade, denominador, conjunto de avaliação e incerteza. Ao propor uma melhoria, indique também seu custo e como medi-la. Ao usar matemática, nomeie as variáveis e mostre a dimensão do resultado.", "board": "Afirmação + mecanismo + hipótese + evidência + limitação", "question": "Qual observação faria você mudar sua conclusão?"},
    {"title": "Regras e organização da sessão", "student_body": "A prova é individual, escrita, sem consulta e sem ferramentas de IA. A sessão de 120 minutos reserva 10 minutos para orientações, 100 para execução e 10 para recolhimento. Siga os avisos e as orientações oficiais do professor.\n\nReserve tempo para ler, resolver e revisar. Quando não concluir uma conta, registre seu caminho e suas hipóteses de maneira legível. A justificativa faz parte da resposta.", "board": "Ler → planejar → responder → revisar", "question": "Seu registro permite que outra pessoa acompanhe o raciocínio?"},
    {"title": "Depois da avaliação: da representação ao sistema", "student_body": "Ao receber a devolutiva, classifique os pontos a revisar: conceito, interpretação de evidência, decisão sob restrições ou formalização. Retorne à demonstração correspondente e refaça a explicação.\n\nA partir da aula 18, o curso passa a construir sistemas: recuperação de evidências, ferramentas, agentes, segurança e avaliação. Forme a equipe e levante domínios para o projeto conforme as orientações da disciplina.", "board": "Fundamentos → RAG → ferramentas → agentes → avaliação", "question": "Que informação um sistema poderia buscar em documentos sem alterar os pesos do modelo?"},
]


def portal_html(text: str) -> str:
    """An iframe has no public sibling files; direct users to authenticated downloads."""
    text = re.sub(r'<a href="(?!https?://|#)[^"]+">.*?</a>', "", text)
    text = text.replace("Aprofundamentos e referências locais: .", "Aprofundamentos: consulte a aba Materiais do portal.")
    text = text.replace('</button></div></header>', '</button><span class="small">Arquivos para download na aba Materiais do portal.</span></div></header>')
    return text


def student_transformer(text: str) -> str:
    """Remove teacher strings from JavaScript, not merely from the visible interface."""
    for field in ("speech", "board"):
        text, count = re.subn(rf"{field}:'(?:\\.|[^'\\])*'", f"{field}:''", text)
        if count != 20:
            raise ValueError(f"Expected 20 {field} fields in the Transformer, found {count}.")
    replacement = '<aside class="teacher"><div class="eyebrow">Confira sua compreensão</div><blockquote id="speech" hidden></blockquote><span id="board" hidden></span><details><summary id="question"></summary><p class="answer" id="answer"></p></details></aside>'
    text, count = re.subn(r'<aside class="teacher">.*?</aside>', replacement, text, count=1, flags=re.S)
    if count != 1:
        raise ValueError("The Transformer teacher panel was not found.")
    text = text.replace("uma pequena experiência e a explicação do professor", "uma pequena experiência e uma pergunta de compreensão")
    text = text.replace("No modo projeção, as falas ficam ocultas.", "No modo projeção, a navegação lateral fica oculta.")
    return text


def code_archives(number: int, target: Path) -> list[dict]:
    """Package source code without executing it; preserve separation of solutions."""
    code = SOURCE / f"aula-{number:02d}" / "codigo"
    if not code.exists():
        code = PORTAL.parent / "aulas" / f"aula-{number:02d}" / "codigo"
    if not code.exists():
        return []
    files = []
    for path in sorted(code.rglob("*")):
        relative = path.relative_to(code)
        if not path.is_file() or path.suffix not in {".py", ".ipynb", ".txt", ".md", ".csv", ".json"}:
            continue
        if any(part.startswith(".") or part in {"__pycache__", "venv", "node_modules"} for part in relative.parts):
            continue
        text = path.read_text(encoding="utf-8-sig")
        if path.suffix == ".ipynb":
            notebook = json.loads(text)
            notebook["metadata"] = {k: v for k, v in notebook.get("metadata", {}).items() if k in {"kernelspec", "language_info"}}
            for cell in notebook["cells"]:
                cell["metadata"] = {}
                if cell.get("cell_type") == "code":
                    cell["outputs"] = []
                    cell["execution_count"] = None
            text = json.dumps(notebook, ensure_ascii=False, indent=1)
        # Stop instead of publishing code containing a literal provider credential.
        if re.search(r"(?:sk-[A-Za-z0-9_-]{24,}|hf_[A-Za-z0-9]{24,}|AIza[A-Za-z0-9_-]{30,})", text):
            raise ValueError(f"Revise credencial literal antes de publicar: {path.name}")
        private = bool(re.search(r"solu[cç][aã]o|gabarito|respostas|solution", relative.as_posix(), re.I))
        files.append((relative.as_posix(), text.encode("utf-8"), private))
    result = []
    for role, label in (("student", "Notebooks e scripts do aluno"), ("teacher", "Código e soluções do professor")):
        included = [item for item in files if role == "teacher" or not item[2]]
        if not included or (role == "teacher" and not any(item[2] for item in files)):
            continue
        memory = io.BytesIO()
        with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, data, _ in included:
                archive.writestr("codigo/" + name, data)
            provenance = code.relative_to(PORTAL.parent).as_posix()
            archive.writestr("LEIA-ME.txt", f"Material original: {provenance}\nNotebooks sem saídas salvas. Execute em um ambiente próprio, seguindo o roteiro da aula.\nAs dependências deste laboratório são independentes das dependências do portal.\n")
        data = memory.getvalue()
        name = f"codigo-{role}.zip"
        (target / name).write_bytes(data)
        result.append({"name": label, "label": label, "mime": "application/zip", "role": role,
                       "path": f"aula-{number:02d}/{name}", "derived_from": provenance,
                       "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return result


def main() -> None:
    output = PORTAL / "content"
    output.mkdir(parents=True, exist_ok=True)
    lessons = []
    for number in range(31):
        source = SOURCE / f"aula-{number:02d}"
        target = output / source.name
        target.mkdir(exist_ok=True)
        plan = (source / "plano.md").read_text(encoding="utf-8")
        meta, plan_body = split_frontmatter(plan)
        if int(meta["aula"]) != number:
            raise ValueError(f"Número inconsistente em {source}")
        materials = []

        def package(name: str, label: str, role: str = "teacher", transform=None) -> None:
            src = source / name
            if not src.exists():
                return
            source_data = src.read_bytes()
            data = transform(src.read_text(encoding="utf-8")).encode("utf-8") if transform else source_data
            (target / name).write_bytes(data)
            mime = {".md": "text/markdown", ".html": "text/html"}.get(src.suffix, "application/octet-stream")
            materials.append({"name": label, "label": label, "mime": mime, "path": f"{source.name}/{name}", "role": role,
                              "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
            if transform:
                materials[-1]["derived_from"] = f"{source.name}/{name}"
                materials[-1]["source_sha256"] = hashlib.sha256(source_data).hexdigest()

        package("plano.md", "Plano completo do professor")
        package("roteiro.md", "Roteiro integral de fala")
        package("instructions-slides.md", "Especificação dos slides")
        if number == 17:
            package("gabarito.md", "Gabarito reservado da avaliação")
            steps = [{**s, "body": s["student_body"], "section": "Preparação e orientação",
                      "stage": "practice", "questions": [s["question"]]} for s in EXAM_STEPS]
        else:
            script = (source / "roteiro.md").read_text(encoding="utf-8")
            steps = parse_steps(script)
        if number == 6:
            # The HTML includes an instructor mode, so its downloadable original is reserved.
            package("transformer-arquitetura-interativa.html", "Transformer completo — versão do professor", transform=portal_html)
            package("encoder-decoder-visual.html", "Encoder e decoder — demonstração", transform=portal_html)
            student_file = "transformer-arquitetura-estudante.html"
            student_data = student_transformer((target / "transformer-arquitetura-interativa.html").read_text(encoding="utf-8")).encode("utf-8")
            (target / student_file).write_bytes(student_data)
            materials.append({"name": "Transformer completo — versão de estudo", "label": "Transformer completo — versão de estudo",
                              "mime": "text/html", "role": "student", "path": f"{source.name}/{student_file}",
                              "derived_from": f"{source.name}/transformer-arquitetura-interativa.html",
                              "bytes": len(student_data), "sha256": hashlib.sha256(student_data).hexdigest()})
            package("roteiro-de-fala-demonstracao-transformer.md", "Fala passo a passo da demonstração Transformer")
            package("aula-quadro-branco.md", "Aula para o quadro branco")
        materials.extend(code_archives(number, target))
        (target / "steps.json").write_text(json.dumps(steps, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        student_guide = "# " + meta["titulo"] + "\n\n" + "\n\n".join(
            "## " + s["title"] + "\n\n" + s["student_body"] for s in steps
        ) + "\n"
        guide_file = target / "guia-estudo.md"
        guide_file.write_text(student_guide, encoding="utf-8")
        guide_bytes = guide_file.read_bytes()
        materials.insert(0, {"name": "Guia de estudo da aula", "label": "Guia de estudo da aula", "mime": "text/markdown", "path": f"{source.name}/guia-estudo.md",
                             "role": "student", "bytes": len(guide_bytes),
                             "sha256": hashlib.sha256(guide_bytes).hexdigest()})
        lessons.append({"id": number, "title": meta["titulo"], "module": meta["modulo"],
                        "kind": meta["tipo"], "duration": meta["duracao_min"],
                        "objectives": extract_objectives(plan_body), "materials": materials,
                        "source": f"v2/aulas/{source.name}", "step_count": len(steps)})
    manifest = {"schema_version": 1, "title": "Grandes Modelos de Linguagem: do Transformer aos Agentes de IA",
                "source": "Materiais autorais da revisão V2", "lessons": lessons}
    (output / "catalog.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Packaged {len(lessons)} lessons and {sum(x['step_count'] for x in lessons)} detailed steps.")


if __name__ == "__main__":
    main()
