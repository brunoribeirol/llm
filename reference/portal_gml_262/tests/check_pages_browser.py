"""Verify the static portal locally or at a supplied public URL."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def check(base):
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(base, wait_until="networkidle")
        assert page.locator(".card:visible").count() == 31
        page.locator("#search").fill("xxxxxxxxxxx")
        assert page.locator(".card:visible").count() == 0
        assert page.locator("#empty").is_visible()
        page.locator("#search").fill("")
        page.locator("#module").select_option(index=1)
        assert 0 < page.locator(".card:visible").count() < 31
        page.locator("#module").select_option(index=0)
        page.locator(".card").nth(2).click()
        page.locator("#notes").fill("Hipótese de teste: alterar a tokenização muda o custo.")
        page.reload(wait_until="networkidle")
        assert "Hipótese de teste" in page.locator("#notes").input_value()
        with page.expect_download() as download:
            page.locator("#export-notes").click()
        exported = json.loads(Path(download.value.path()).read_text(encoding="utf-8"))
        assert exported["lesson"] == "2" and "Hipótese" in exported["notes"]
        page.locator("#notes").fill("")
        page.locator("#import-notes").set_input_files({"name": "notes.json", "mimeType": "application/json", "buffer": json.dumps(exported).encode()})
        page.wait_for_function("document.querySelector('#notes').value.includes('Hipótese')")
        for link in page.locator("#materiais a[download]").all():
            response = page.request.get(base + "aula-02/" + link.get_attribute("href"))
            assert response.ok, link.get_attribute("href")
        for number in range(31):
            response = page.goto(f"{base}aula-{number:02d}/demo.html", wait_until="load")
            assert response.ok
            page.locator("#next").wait_for()
            before = page.locator("#title").text_content() if number != 6 else None
            page.locator("#next").click()
            if before:
                assert page.locator("#title").text_content() != before
        page.set_viewport_size({"width": 390, "height": 844})
        for path in ("", "aula-02/index.html", "aula-06/index.html"):
            page.goto(base + path, wait_until="networkidle")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), path
        output = ROOT / "verification"
        output.mkdir(exist_ok=True)
        page.goto(base, wait_until="networkidle")
        page.screenshot(path=str(output / "pages-mobile.png"), full_page=True)
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.screenshot(path=str(output / "pages-desktop.png"), full_page=True)
        browser.close()
    assert not errors, errors
    print("PASS: 31 demos, catalog filters, downloads, notebook persistence/export/import, mobile layout, no JS errors")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        check(sys.argv[1].rstrip("/") + "/")
    else:
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
        Thread(target=server.serve_forever, daemon=True).start()
        try:
            check(f"http://127.0.0.1:{server.server_port}/docs/")
        finally:
            server.shutdown()
            server.server_close()
