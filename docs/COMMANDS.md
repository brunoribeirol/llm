# Project Commands

Automatically detected commands are managed by Agent Workspace. Keep human notes outside the managed block.

## Automatically detected

## Project-specific notes

- `python3 scripts/professor_sync.py` — sync the portal mirror and check the professor's GitHub
  profile (`--check` writes nothing). Needs network access to GitHub.
- `python3 scripts/check_study_pages.py` — validate study pages; run after editing `study/`.
- `ruff check scripts/ && ruff format scripts/` — lint and format the tooling.
- `scripts/build_av1_pdf.sh` — render `av1/final/avaliacao01_bruno_ribeiro.html` to PDF with
  headless Chrome. Run from the repository root, outside the agent sandbox (the sandbox blocks
  Chrome's local socket).

<!-- agent-workspace:v8:commands:start -->
No commands were detected from supported manifests. Add confirmed project-specific commands below.
<!-- agent-workspace:v8:commands:end -->
