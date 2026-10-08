# llm

Study workspace for the course *Grandes Modelos de Linguagem: do Transformer aos Agentes de IA*
(CESAR, 2026.2, 30 lessons). It keeps the course material in one place, turns each lesson into
an explanatory study page, and tracks the graded work.

Start here: open [`study/index.html`](study/index.html) in a browser.

## Layout

| Path | What it holds |
|---|---|
| `study/` | Study pages written for this workspace: one HTML page per lesson plus the hub (`index.html`) |
| `class/` | Material received from the professor: `slides/`, `notebooks/`, `articles/`, `html/` |
| `booklet/` | Course booklet (`apostila.pdf`, 302 pages) |
| `labs/` | Graded labs, one folder per lab |
| `av1/` | Assessment 1: statement, plan and checklist, AI-usage log, the student's draft |
| `reference/portal_gml_262/` | Offline mirror of the professor's portal, kept by `scripts/professor_sync.py` |
| `reference/teacher-only/` | Teacher-only files from the portal repository; git-ignored, local only |
| `scripts/` | Workspace tooling (standard-library Python) |
| `docs/` | Project state and context for agent sessions |
| `.agents/skills/`, `.claude/` | Agent skills and subagents used to maintain this workspace |

## Commands

```bash
python3 scripts/professor_sync.py            # sync the portal mirror, check the professor's GitHub profile
python3 scripts/professor_sync.py --check    # same report, writes nothing
python3 scripts/check_study_pages.py         # validate study pages (tags, links, inline scripts)
```

Both scripts need only Python 3 plus `git` and `curl` on the PATH.

## How the study pages work

- Each page is built from the lesson's slides and the professor's study guide.
- A tag like `Aula 1 · slide 7` marks a statement that is in the professor's material and can
  be cited. Everything else is explanation written with AI support and must be checked against
  the material before it is used in an assessment.
- Pages are self-contained and open from disk. The mirrored portal also works offline at
  `reference/portal_gml_262/docs/index.html`.

## Agent tooling

| Kind | Name | Purpose |
|---|---|---|
| Skill | `study-page` | Build or update the study page for a lesson |
| Skill | `assessment-coach` | Explain, quiz and review drafts for a graded assessment without writing it |
| Skill | `professor-sync` | Run the mirror sync and interpret what is new |
| Subagent | `course-researcher` | Find where a concept is covered and return citable references |
| Subagent | `draft-reviewer` | Grade the student's draft against the rubric, read-only |

Canonical skill instructions live in `.agents/skills/`; `.claude/skills/` holds thin pointers.

## Material and provenance

The slides, booklet, notebooks and the mirrored portal belong to the professor and the
institution; they are kept here for personal study. Keep this repository private.

Teacher-only files from the portal repository (lab solutions and the exam answer key) are
stored apart in `reference/teacher-only/`, outside the mirror and git-ignored, so they stay on
this machine. They are for checking finished work afterwards, not for doing it, and the agent
tooling does not open them unless asked. `scripts/professor_sync.py` restores them on a fresh clone.
