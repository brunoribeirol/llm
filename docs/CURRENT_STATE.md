# Current State

_Last updated: 2026-10-07_

## Last confirmed working state

- `study/index.html` (hub) and `study/aula-01.html` … `aula-08.html` pass `scripts/check_study_pages.py`.
- `reference/portal_gml_262/` mirrors the professor's portal at upstream commit `389264e`.
  The 8 teacher-only files are stored apart in `reference/teacher-only/portal_gml_262/`.
  `scripts/professor_sync.py --check` reports up to date.
- The session's work is committed on branch `feat/study-workspace` (local: not pushed, not
  merged). `main` is still at `af71f91` (2026-09-06).

## Recently changed

- 2026-10-07: study pages for lessons 2–8 written in the lesson 1 format; hub and
  `av1/README.md` case map updated; AI-usage log extended.
- 2026-10-07: at the user's request the sync script now keeps teacher-only files
  (`codigo-teacher.zip`, `gabarito.md`) under `reference/teacher-only/` instead of dropping
  them. Skills and subagents are told not to open them unless the user asks for a specific file.
- 2026-10-07: workspace organized around study pages. Added `study/`, `scripts/`, `reference/`,
  `av1/README.md`, `av1/ai-usage-log.md`, `av1/draft/dossie.md`, three skills
  (`study-page`, `assessment-coach`, `professor-sync`), two subagents
  (`course-researcher`, `draft-reviewer`), and a real `README.md`.

## Current objective

AV1 (*Dossiê de diagnóstico conceitual*, lessons 1–8), due **2026-10-13**, printed. All eight
lessons now have a study page with a bridge to their case. The next step is the user's: study,
then draft the eight cases and two variations in `av1/draft/dossie.md`. Plan and checklist:
`av1/README.md`.

## Validation evidence

- `python3 scripts/check_study_pages.py` → 9 pages `ok` (balanced tags, 240 links and anchors,
  inline scripts via `node --check`, self-test counts against the hub).
- Scratch smoke test (Node, DOM stub built from each page's markup): every page's scripts ran
  and every event handler fired without exceptions; computed values match the professor's
  numbers (e.g. accuracy 0,9090 for the aggressive detector, 10,9 pages at fertility 1,5,
  KV cache 4,0 GiB per 8.192-token conversation).
- `python3 scripts/professor_sync.py` and `--check` → mirror up to date, site HTTP 200.
- `ruff check scripts/` and `ruff format scripts/` → clean.
- **Not verified:** the pages were never rendered in a browser in this session. The sandbox
  blocks `open` and local port binding, and the Chrome extension refuses `file://` URLs.
  Layout and visual quality are unreviewed.

## Known risks and constraints

- Lesson 8 has no slide PDF in `class/slides/`; its page is built from the portal guide and
  its slide numbers follow the guide. Recheck citations when the PDF arrives.
- Slide numbers on the pages are PDF page numbers. For lessons 5, 6 and 7 the number printed
  on the slide differs (noted in each page's header).
- Lesson 4 has no slide deck (it is Lab 1); the page cites the lab notebook and the portal guide.
- The AV1 announcement says printed; the statement PDF says PDF upload by 23:59. Unconfirmed.
- 2026-10-12 is a national holiday: printing must be arranged earlier.
- `feat/study-workspace` is not pushed: the new material still exists only on this machine.
  `reference/teacher-only/` is git-ignored by design and never leaves it.

## Next steps

1. User reviews the pages in a browser and reports format or content problems.
2. User drafts the cases; review with `assessment-coach` / `draft-reviewer`.
3. Push `feat/study-workspace` and open a pull request into `main`.
4. Get the lesson 8 slides and recheck that page's citations.
5. Lessons 9–30: build each page as the course reaches it (the portal mirror already has the guides).

## Do not touch without explicit scope

- `av1/draft/dossie.md`: the user's own text. Review it; do not write or rewrite answers in it.
- `reference/teacher-only/`: kept for the user's after-the-fact checking. Do not open unless
  the user explicitly asks for a specific file.
