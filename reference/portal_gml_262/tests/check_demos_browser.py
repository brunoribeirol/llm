"""Exercise every demonstration in a real browser without real accounts or APIs."""
import json
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from demos import demo_count, demo_html, load_demo


def main():
    output = ROOT / "verification"
    output.mkdir(exist_ok=True)
    errors = []
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1380, "height": 1150})
        page.on("pageerror", lambda error: errors.append(str(error)))
        selected = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else list(range(31))
        for lesson in selected:
            page.set_content(demo_html(lesson, "student"))
            page.locator("#next").wait_for()
            assert len(page.evaluate("window.lesson.steps")) == demo_count(lesson)
            for step in range(demo_count(lesson)):
                page.evaluate("index => window.lesson.go(index)", step)
                assert page.locator("#title").inner_text().strip()
                assert len(page.locator("#visual").inner_text()) > 20
                assert page.locator("#flowchart .learning-flow").count() == 1
                assert len(page.locator("#flowchart .lf-stage").all()) >= 4
            page.evaluate("window.lesson.go(0)")
            page.locator("#next").click()
            assert page.evaluate("window.lessonSnapshot.step") == 1
            if lesson != 6:
                assert not page.locator("#teacher").count()
                data = load_demo(lesson)
                # A control change updates the snapshot through actual DOM input events.
                control = next(c for c in data["controls"] if c["type"] == "range")
                field = page.locator("#control-" + control["key"])
                field.focus()
                before = page.evaluate("window.lessonSnapshot.step")
                field.press("ArrowRight")
                assert page.evaluate("window.lessonSnapshot.step") == before  # no unintended navigation
                new_value = float(field.input_value())
                assert new_value != control["value"] or new_value == control["max"]
                assert page.evaluate("key => window.lessonSnapshot.state[key]", control["key"]) == new_value
                page.locator("#reset").click()
                assert page.evaluate("key => window.lessonSnapshot.state[key]", control["key"]) == control["value"]
                # Navigate using the diagram's phase buttons, including the
                # nested overview when a mechanism is shown for this step.
                page.locator("#flowchart-box > summary").click()
                if page.locator("#overview-box").is_visible():
                    page.locator("#overview-box > summary").click()
                button = page.locator("[data-flow-focus='5']").last
                button.click()
                assert load_demo(lesson)["steps"][page.evaluate("window.lessonSnapshot.step")]["focus"] == 5
                assert page.locator("#flowchart-box").evaluate("el => el.open")
            else:
                page.locator("#flowchart-box > summary").click()
                page.evaluate("window.lesson.go(13)")
                assert "Encoder–decoder" in page.locator("#flowchart").inner_text()
            if lesson in {2, 13, 18, 21, 23, 27}:
                page.screenshot(path=str(output / f"demo-{lesson:02d}.png"), full_page=True)
            page.set_viewport_size({"width": 390, "height": 844})
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 2"), f"Mobile overflow: {lesson}"
            if lesson == 18:
                page.screenshot(path=str(output / "demo-mobile.png"), full_page=True)
            page.set_viewport_size({"width": 1380, "height": 1150})
            if lesson != 6:
                page.set_content(demo_html(lesson, "teacher"))
                page.evaluate("window.lesson.go(0)")
                assert page.locator("#speech").inner_text() == load_demo(lesson)["steps"][0]["speech"]
                page.locator("#presentation").click()
                assert not page.locator("#teacher").is_visible()
                page.locator("#presentation").click()
                assert page.locator("#teacher").is_visible()
            results.append({"lesson": lesson, "steps": demo_count(lesson), "mobile": "pass"})
            print(f"Aula {lesson:02d}: navegação, controles e mobile OK", flush=True)
        assert not errors, errors
        browser.close()
    filename = "demos-browser.json" if len(results) == 31 else "demos-browser-partial.json"
    (output / filename).write_text(json.dumps({"lessons": results, "javascript_errors": errors}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
