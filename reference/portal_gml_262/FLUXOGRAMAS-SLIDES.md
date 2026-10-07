# Fluxogramas nas instruções de slides

Fonte vigente: `v2/aulas/`. Cada arquivo tem orientações por slide e desenhos Mermaid completos, com cópia idêntica em `portal/content/` e download reservado ao professor.

A aula 17 ganhou um deck operacional V2: realização e entrega da prova, sem mapas de conteúdo ou gabarito. As demais aulas preservam os títulos e a numeração existentes.

| Aula | Slides com orientação | Desenhos incluídos |
| --- | --- | --- |
| 00 | 6 | 4 |
| 01 | 7 | 2 |
| 02 | 5 | 2 |
| 03 | 15 | 2 |
| 04 | 14 | 4 |
| 05 | 15 | 3 |
| 06 | 15 | 5 |
| 07 | 12 | 3 |
| 08 | 7 | 4 |
| 09 | 13 | 6 |
| 10 | 15 | 4 |
| 11 | 8 | 3 |
| 12 | 7 | 2 |
| 13 | 15 | 3 |
| 14 | 8 | 4 |
| 15 | 15 | 2 |
| 16 | 16 | 2 |
| 17 | 4 | 2 |
| 18 | 10 | 3 |
| 19 | 15 | 4 |
| 20 | 11 | 4 |
| 21 | 13 | 3 |
| 22 | 10 | 5 |
| 23 | 13 | 2 |
| 24 | 5 | 2 |
| 25 | 11 | 4 |
| 26 | 12 | 5 |
| 27 | 13 | 2 |
| 28 | 12 | 3 |
| 29 | 6 | 3 |
| 30 | 4 | 2 |

Total: **31 arquivos-fonte e 31 cópias do portal**, com **332 orientações por slide** e **99 desenhos incluídos** (há reutilização entre aulas).

Para atualizar as seções gerenciadas, execute `python portal/scripts/build_slide_flowcharts.py` na raiz do projeto. O script preserva o restante das instruções, atualiza bytes/hashes do catálogo e verifica idempotência antes de gravar.
