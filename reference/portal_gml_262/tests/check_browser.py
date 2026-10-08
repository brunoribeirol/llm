"""Real browser checks with disposable accounts and a localhost-only server."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification"
URL = "http://127.0.0.1:18541"
# Test-only credentials: never stored in the deployed application database.
INITIAL = "Temporary-browser-check-2026"
PERSONAL = "Personal-browser-check-2026"
STUDENT_INITIAL = "Temporary-student-check-2026"
STUDENT_PERSONAL = "Personal-student-check-2026"


def login(page, email, password):
    page.get_by_label("E-mail", exact=True).fill(email)
    page.get_by_label("Senha", exact=True).fill(password)
    page.get_by_role("button", name="Entrar", exact=True).click()


def change_password(page, previous, current):
    page.get_by_label("Senha atual", exact=True).fill(previous)
    page.get_by_label("Nova senha", exact=True).fill(current)
    page.get_by_label("Confirme a nova senha", exact=True).fill(current)
    page.get_by_role("button", name="Salvar nova senha", exact=True).click()
    page.get_by_role("button", name="Explorar aula", exact=False).first.wait_for()


def lesson(page, number):
    page.get_by_role("button", name="Todas as aulas", exact=False).click()
    page.get_by_role("button", name="Explorar aula", exact=False).nth(number).click()
    page.get_by_text("Demonstração interativa", exact=True).click()


def main():
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="portal-browser-") as directory:
        temporary = Path(directory).resolve()
        assert temporary.parent == Path(tempfile.gettempdir()).resolve()
        environ = dict(os.environ)
        environ.pop("VERCEL", None)
        environ.update(DATABASE_URL="sqlite:///" + str(temporary / "accounts.db"), PORTAL_ENV="development", PORTAL_ADMIN_EMAIL="professor@example.edu", PORTAL_ADMIN_PASSWORD=INITIAL, PORTAL_ADMIN_NAME="Professor de teste")
        with (OUT / "browser-server.log").open("w", encoding="utf-8") as log:
            process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--server.address=127.0.0.1", "--server.port=18541", "--server.headless=true"], cwd=ROOT, env=environ, stdout=log, stderr=log)
            try:
                for _ in range(60):
                    try:
                        with urlopen(URL + "/_stcore/health", timeout=1) as response:
                            if response.status == 200:
                                break
                    except OSError:
                        time.sleep(.3)
                with sync_playwright() as p:
                    browser = p.chromium.launch(channel="msedge", headless=True)
                    context = browser.new_context(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
                    page = context.new_page()
                    page.set_default_timeout(90000)
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto(URL)
                    try:
                        page.get_by_role("heading", name="Entre para continuar").wait_for()
                    except Exception:
                        page.screenshot(path=str(OUT / "startup-failure.png"))
                        raise RuntimeError("Startup did not finish: " + page.locator("body").inner_text()[:1000])
                    assert not page.get_by_role("button", name="Explorar aula", exact=False).count()
                    page.screenshot(path=str(OUT / "entrada.png"))
                    login(page, "professor@example.edu", INITIAL)
                    change_password(page, INITIAL, PERSONAL)
                    assert page.get_by_role("button", name="Explorar aula", exact=False).count() == 31
                    page.screenshot(path=str(OUT / "catalogo.png"))
                    page.get_by_role("button", name="Como usar o portal", exact=True).click()
                    page.get_by_role("heading", name="Como usar o portal", exact=True).wait_for()
                    assert page.locator(".learning-flow").count() == 1
                    guide_frame = page.frame_locator('iframe[title="st.iframe"]').first
                    with page.expect_download() as guide_info:
                        guide_frame.get_by_role("link").click()
                    guide_text = Path(guide_info.value.path()).read_text(encoding="utf-8")
                    assert "O caderno fica apenas na sessão atual" in guide_text
                    page.screenshot(path=str(OUT / "como-usar.png"))
                    page.get_by_role("button", name="Gerenciar turma", exact=True).click()
                    page.get_by_label("Nome", exact=True).fill("Estudante de teste")
                    page.get_by_label("E-mail da nova conta", exact=True).fill("student@example.edu")
                    page.get_by_label("Senha temporária", exact=True).fill(STUDENT_INITIAL)
                    page.get_by_role("button", name="Criar conta", exact=True).click()
                    page.get_by_text("Conta criada.", exact=False).wait_for()
                    page.screenshot(path=str(OUT / "gerenciar-turma.png"))

                    student_context = browser.new_context(viewport={"width": 1300, "height": 1000})
                    student = student_context.new_page()
                    student.set_default_timeout(90000)
                    student.goto(URL)
                    login(student, "student@example.edu", STUDENT_INITIAL)
                    change_password(student, STUDENT_INITIAL, STUDENT_PERSONAL)
                    assert not student.get_by_role("button", name="Gerenciar turma", exact=True).count()
                    lesson(student, 6)
                    frame = student.frame_locator('iframe[title="st.iframe"]').first
                    frame.locator("#next").wait_for()
                    frame.locator("#next").click()
                    assert frame.locator("#counter").inner_text().startswith("2 /")
                    assert frame.locator("#speech").inner_text() == ""
                    student.screenshot(path=str(OUT / "transformer.png"))

                    lesson(page, 2)
                    bpe_frame = page.frame_locator('iframe[title="st.iframe"]').first
                    bpe_frame.get_by_role("slider").first.wait_for()
                    bpe_frame.get_by_role("slider").first.press("ArrowRight")
                    page.screenshot(path=str(OUT / "tokenizacao.png"))
                    lesson(page, 18)
                    rag_frame = page.frame_locator('iframe[title="st.iframe"]').first
                    rag_frame.get_by_role("slider").first.wait_for()
                    rag_frame.locator("#next").click()
                    assert rag_frame.locator("#counter").inner_text().startswith("2 /")
                    page.screenshot(path=str(OUT / "rag.png"))
                    page.get_by_text("Fluxogramas", exact=True).click()
                    page.get_by_role("heading", name="Fluxogramas desta aula").wait_for()
                    page.get_by_role("combobox", name="Escolha um fluxograma", exact=True).click()
                    page.get_by_role("option", name="RAG: do acervo à resposta com fontes", exact=True).click()
                    page.get_by_role("heading", name="RAG: do acervo à resposta com fontes", exact=True).wait_for()
                    page.screenshot(path=str(OUT / "fluxogramas-portal.png"))
                    chart_frame = page.frame_locator('iframe[title="st.iframe"]').first
                    with page.expect_download() as chart_info:
                        chart_frame.get_by_role("link").click()
                    chart_text = Path(chart_info.value.path()).read_text(encoding="utf-8")
                    assert "RAG: do acervo à resposta com fontes" in chart_text
                    page.set_viewport_size({"width": 390, "height": 844})
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 2")
                    page.screenshot(path=str(OUT / "fluxogramas-portal-mobile.png"))
                    page.set_viewport_size({"width": 1440, "height": 1100})
                    page.get_by_text("Materiais", exact=True).click()
                    page.get_by_role("heading", name="Materiais desta aula").wait_for()
                    download_frame = page.frame_locator('iframe[title="st.iframe"]').first
                    with page.expect_download() as download_info:
                        download_frame.get_by_role("link").click()
                    download = download_info.value
                    assert download.suggested_filename == "demonstracao-aula-18.html"
                    assert download.failure() is None

                    page.get_by_text("Meu caderno", exact=True).click()
                    page.get_by_label("O que observei, o que calculei, o que ainda quero investigar", exact=True).fill("Recuperar documentos antes de responder.")
                    page.get_by_text("Concluí esta aula", exact=True).click()
                    expect(page.get_by_label("Concluí esta aula", exact=True)).to_be_checked()
                    page.get_by_text("1 de 31 encontros", exact=True).wait_for()
                    notebook_frame = page.frame_locator('iframe[title="st.iframe"]').first
                    with page.expect_download() as notebook_info:
                        notebook_frame.get_by_role("link").click()
                    notebook = json.loads(Path(notebook_info.value.path()).read_text(encoding="utf-8"))
                    assert notebook["notes"]["18"] == "Recuperar documentos antes de responder."
                    assert 18 in notebook["completed"]
                    page.get_by_text("Restaurar caderno de uma sessão anterior", exact=True).click()
                    page.get_by_label("Abra o arquivo .json em um editor e cole seu conteúdo aqui", exact=True).fill(json.dumps({"version": 1, "completed": [2, 18], "notes": {"18": "Anotação restaurada."}}))
                    page.get_by_role("button", name="Importar anotações", exact=True).click()
                    page.get_by_label("O que observei, o que calculei, o que ainda quero investigar", exact=True).wait_for()
                    expect(page.get_by_label("O que observei, o que calculei, o que ainda quero investigar", exact=True)).to_have_value("Anotação restaurada.")

                    page.get_by_role("button", name="Gerenciar turma", exact=True).click()
                    page.get_by_role("combobox", name="Conta a gerenciar", exact=True).click()
                    page.get_by_role("option", name="Estudante de teste", exact=False).click()
                    page.get_by_role("button", name="Bloquear acesso", exact=True).click()
                    page.get_by_text("Acesso atualizado.", exact=False).wait_for()
                    student.get_by_role("button", name="Todas as aulas", exact=False).click()
                    student.get_by_role("heading", name="Entre para continuar").wait_for()
                    assert not student.get_by_role("button", name="Explorar aula", exact=False).count()
                    login(student, "student@example.edu", STUDENT_PERSONAL)
                    student.get_by_text("E-mail ou senha inválidos.", exact=True).wait_for()
                    student_context.close()

                    page.get_by_role("button", name="Todas as aulas", exact=False).click()
                    page.set_viewport_size({"width": 390, "height": 844})
                    page.screenshot(path=str(OUT / "mobile.png"))
                    assert not page.locator('[data-testid="stException"]').count()
                    assert not errors, errors
                    browser.close()
                    (OUT / "browser-result.json").write_text(json.dumps({"identity": "real password login with disposable SQLite accounts", "checks": ["anonymous gate", "teacher login", "mandatory password change", "create student", "student role", "catalog and navigation", "guide and download", "flowchart selection and offline download", "mobile flowchart", "BPE controls", "Transformer iframe navigation and teacher data removal", "RAG controls", "inline authorized download", "notebook export and import", "account blocking and session revocation", "mobile"], "javascript_errors": errors}, indent=2), encoding="utf-8")
                    print("Browser checks passed; screenshots in verification/.")
            finally:
                process.terminate()
                process.wait(timeout=15)


if __name__ == "__main__":
    main()
