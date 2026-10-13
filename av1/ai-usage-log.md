# AI usage log — AV1

Running record behind the AI-use statement that closes the dossier. One row per assisted step.
"Checked against" is filled by the student after verifying the content in the course material.

| Date | Tool | Used for | Checked or changed by me, against which material |
|---|---|---|---|
| 2026-10-07 | Claude Code | Organizing the course repository; mirroring the professor's portal; reading the AV1 statement into a plan and checklist (`av1/README.md`) | pending |
| 2026-10-07 | Claude Code | Study page for lesson 1 (`study/aula-01.html`), built from `class/slides/aula01.pdf` and the portal study guide; includes guiding questions for case 1, no drafted answer | pending |
| 2026-10-07 | Claude Code | Study pages for lessons 2-8 (`study/aula-02.html` to `aula-08.html`), built from the slide PDFs in `class/slides/`, the Lab 1 notebook and the portal study guides; each has guiding questions for its AV1 case, no drafted answer. Lesson 8 was built from the portal guide only (slide PDF missing) | pending |
| 2026-10-10 | Claude Code | Coaching session for the dossier: re-read the statement, set the work order for the remaining days, and walked through case 1 with guiding questions and pointers to lesson 1 (slides 7-9, 15-16). No answer text drafted by the AI | pending |
| 2026-10-11 | Claude Code | Concept briefings and guiding questions for cases 2, 3 and 4, taken from the study pages of lessons 2-4 (tokenization and fertility, static vs contextual embeddings, t-SNE and small-corpus limits). The student asked for generated answers; the AI declined and kept to explanation and review | pending |
| 2026-10-12 | Claude Code | Case 1: reviewed the student's chat answers, explained the false positive / false negative distinction and why accuracy stays high under class imbalance, then assembled the case text in `av1/draft/dossie.md` from the student's own sentences (grammar and clarity fixes, "falso positivo" corrected to "falso negativo", "acurácia das urgentes" replaced by the recall the student named, reference line added) | pending |
| 2026-10-12 | Claude Code | Concept briefings and the statement's questions for cases 2 to 8 in a single batch, taken from the study pages of lessons 2-8. The student asked again for ready answers; the AI declined and kept to explanation, with the case text to be assembled from the student's replies | pending |
| 2026-10-12 | Claude Code | Case 2: assembled the case text in `av1/draft/dossie.md` from the student's chat answers (grammar and clarity fixes, "modelo" corrected to "tokenizador", hedge added where the statement does not say which corpus trained the tokenizer, reference line added) | pending |
| 2026-10-12 | claude.ai (Claude Docs) | Per the student: drafted a full version of the eight cases and both variations from the statement, outside this repository (`~/Downloads/Avaliação 01 — Dossiê de diagnóstico conceitual.pdf`) | pending |
| 2026-10-12 | Claude Code | Reviewed that claude.ai draft against the rubric and the course material. Flagged: class ("turma") missing from the header, AI-use statement missing its second sentence, case 8 window-attention item framed differently from lesson 8, generic lesson references, length above the suggested range. No text rewritten | pending |
| 2026-10-12 | Claude Code | Typeset the claude.ai draft as `av1/final/avaliacao01_bruno_ribeiro.html` for PDF export: text transcribed word for word (checked by script against the original PDF), class line added, export byline removed, compact A4 layout. No answer content changed | pending |
| 2026-10-12 | Claude Code | Reviewed the AI-use statement the student rewrote in the print HTML and flagged that it describes AI as support for understanding and formatting, while this log records claude.ai drafting the answers. Asked to rewrite the case 8 window-attention sentence and declined; pointed to the line and to what lesson 8 says. Added `scripts/build_av1_pdf.sh` to render the PDF | pending |
| 2026-10-12 | Claude Code | At the student's repeated request, corrected one clause of case 8 in the print HTML: window attention now reads as reducing the number of compared position pairs (quadratic cost), as in lesson 8, instead of bounding the cache. Proposed wording for an AI-use statement that matches this log | pending |
| 2026-10-12 | Claude Code | Final formatting of the print HTML: inserted the AI-use statement as written by the student, replaced the em dashes in headings and reference lines with colons, removed a stale duplicate PDF, and checked the rendered PDF (5 pages, selectable text, all sections present) | pending |

## Statement draft

> Utilizei [ferramenta] para [finalidade]. Conferi ou alterei [partes] com base em [materiais].
