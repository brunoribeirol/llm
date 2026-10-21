# Current State

_Last updated: 2026-10-20_

## Last confirmed working state

- `study/index.html` (hub) and `study/aula-01.html` … `aula-08.html` pass `scripts/check_study_pages.py`.
- `reference/portal_gml_262/` mirrors the professor's portal at upstream commit `389264e`.
  The 8 teacher-only files are stored apart in `reference/teacher-only/portal_gml_262/`.
  Not re-synced on 2026-10-12: the agent sandbox had no network access to GitHub.
- AV1 deliverable: `av1/final/avaliacao01_bruno_ribeiro.pdf` (5 A4 pages, selectable text,
  built 2026-10-12 18:27 from `av1/final/avaliacao01_bruno_ribeiro.html` with
  `scripts/build_av1_pdf.sh`). The user reported on 2026-10-13 that it was handed in.
- All work up to the AV1 close-out is on `main`: PR #3 (`feat/av1-final-dossier`) was merged on
  2026-10-13 as merge commit `91222e7`; the grade followed in PR #5 (`docs/av1-grade`), merged
  on 2026-10-20 as `2161177`.

## Recently changed

- 2026-10-20: AV1 graded 9.93, as reported by the user; the professor gave no feedback.
  Recorded in `av1/README.md`, and the study hub's AV1 block now shows it.
- 2026-10-13: AV1 handed in, as reported by the user. Whether it went on paper, as a PDF
  upload or both was not recorded. Grade and feedback are pending.
- 2026-10-12: AV1 closed. The user tried the coaching route for cases 1 and 2 (their answers,
  assembled in `av1/draft/dossie.md`), then, short on time before a job interview, had claude.ai
  draft the full dossier and chose that text as the deliverable. In this repository the agent
  reviewed that draft against the rubric and the course material, typeset it word for word as
  `av1/final/avaliacao01_bruno_ribeiro.html`, and at the user's request added the class line,
  corrected one clause of case 8 (window attention reduces the compared position pairs, as in
  lesson 8, instead of bounding the cache), replaced the em dashes in headings and reference
  lines with colons, and inserted the AI-use statement the user wrote. The statement says that
  Claude drafted the initial answers and Claude Code supported study, review and formatting.
- 2026-10-12: added `scripts/build_av1_pdf.sh` (headless Chrome, A4, page numbers). It has to
  run outside the agent sandbox, which blocks Chrome's local socket.
- 2026-10-12: removed iCloud conflict copies: 202 `name 2` files, 35 empty `name 2` folders,
  `.git/index 2`, `.git/index 3` and one stale `avaliacao01_bruno_ribeiro 2.pdf`. Every removed
  file was byte-identical to its original, except the PDF, which was an older render.
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

AV1 is handed in. The workspace is back to its standing job: a study page for each new lesson
(9 onward). AV1 is closed: graded 9.93, no feedback from the professor.

## Validation evidence

Run on 2026-10-20, after the hub's AV1 line changed: `python3 scripts/check_study_pages.py` →
9 pages `ok`. The hub was not opened in a browser.

Run on 2026-10-12:

- `python3 scripts/check_study_pages.py` → 9 pages `ok`.
- `ruff check scripts/` and `ruff format --check scripts/` → clean.
- `sh -n scripts/build_av1_pdf.sh` → syntax ok; the user ran the script three times outside the
  sandbox, and the last two runs ended with `wrote …pdf` and `Pages: 5`.
- Final PDF inspected: 5 pages, page 1 (identification) and pages 4–5 viewed, text extracted
  with `pdftotext`; class line, case 8 correction and AI-use statement present; no em dashes.
- Print HTML compared word by word with the claude.ai PDF by a scratch script before the
  requested edits: the only differences were the header lines.
- **Not verified:** the twelve external references in the dossier were not opened in this
  session; they exist to the agent's knowledge. `shellcheck` is not installed. The study pages
  were still not reviewed in a browser by the agent.

## Known risks and constraints

- AV1's dossier declared that Claude drafted the initial answers and ran past the suggested
  length in every case (221–319 words against 100–180). It was graded 9.93 with no feedback, so
  neither point can be read as accepted or penalized in general. Read the AV2 statement on both.
- The repository sits in iCloud-synced `~/Documents`. Bulk writes and regenerated files leave
  `name 2` conflict copies, including inside `.git/`. Check with
  `find . \( -name '* 2' -o -name '* 2.*' \)` after large write sessions.
- Lesson 8 has no slide PDF in `class/slides/`; its page is built from the portal guide and
  its slide numbers follow the guide. Recheck citations when the PDF arrives.
- Slide numbers on the pages are PDF page numbers. For lessons 5, 6 and 7 the number printed
  on the slide differs (noted in each page's header).
- Lesson 4 has no slide deck (it is Lab 1); the page cites the lab notebook and the portal guide.
- `reference/teacher-only/` is git-ignored by design: those files exist only on this machine.
- Inside the agent sandbox, commits (GPG signing), `gh`, headless Chrome, writes to the
  Obsidian vault and branch switches that touch `.claude/skills/` or `.claude/agents/` fail;
  the user runs those with the `!` prefix. `git fetch` works when the command is allowed to
  reach `github.com`, and a pull request can be merged through the user's Chrome (done for
  PR #3 on 2026-10-13).

## Next steps

1. User fills the "checked by me" column of `av1/ai-usage-log.md` (every row is still
   `pending`).
2. Get the lesson 8 slides and recheck that page's citations.
3. Lessons 9–30: build each page as the course reaches it (the portal mirror already has the
   guides). Run `python3 scripts/professor_sync.py` first, from outside the sandbox.
4. Consider moving the repository out of `~/Documents` to stop the iCloud conflict copies.

## Do not touch without explicit scope

- `av1/final/`: the deliverable as handed in on 2026-10-13. Do not edit or rebuild it.
- `av1/draft/dossie.md`: the user's own text. Review it; do not write or rewrite answers in it.
- `reference/teacher-only/`: kept for the user's after-the-fact checking. Do not open unless
  the user explicitly asks for a specific file.
