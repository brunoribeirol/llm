---
aula: 20
titulo: "Laboratório 5: Pipeline RAG completo"
modulo: "5 — RAG, Ferramentas e Agentes de IA"
tipo: laboratorio
semana: 10
duracao_min: 120
versao: v2
---

# Aula 20 — Laboratório 5: Pipeline RAG completo

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2 — §6-bis (laboratórios).** O roteiro prático **não foi reordenado**: a
> sequência dos seis checkpoints é a que funciona no teclado, minuto a minuto. O que mudou é que
> cada checkpoint agora abre pelo **que a tela imprime quando está certo** — a linha
> `Checkpoint N OK` com o que o teste conferiu, ou a tabela que o notebook gera — antes de dizer o
> que implementar. O apêndice é organizado **por checkpoint**, com três itens: as quatro métricas
> calculadas sobre as 18 consultas **deste** lab (CP6), a assimetria entre `recall@3` e
> `recall@10` no reranking e a ordem de depuração que ela impõe (CP4 e CP6), e quantas consultas
> rotuladas seriam necessárias para a diferença medida não ser ruído (CP6). As definições das
> métricas, o BM25, o RRF e o teorema do teto **não são rederivados aqui** — eles estão no
> apêndice da Aula 19 e o fluxo aponta para lá. Carga horária, numeração e objetivos inalterados.
> O notebook em `codigo/` **não muda**.

## 1. Objetivo da aula

Construir as nove etapas da Aula 18 com o retrieval híbrido e o reranking da Aula 19 num pipeline único que roda de ponta a ponta — e, sobretudo, **medir** esse pipeline: `recall@k` das três estratégias sobre um conjunto de 15 a 20 consultas rotuladas, e a mesma tabela antes e depois do reranking. O entregável desta aula é um número, não uma demonstração.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Fatiar** um corpus em chunks com metadados de fonte e seção, e **inspecionar** a distribuição de tamanhos para detectar dispositivo cortado no meio.
2. **Indexar** os chunks com um modelo de embedding leve em Chroma (ou FAISS, ou matriz densa) e **recuperar** por similaridade de cosseno com `top-k` parametrizável.
3. **Fundir** o ranking denso com o ranking BM25 por Reciprocal Rank Fusion, e **verificar** que a fusão não depende de calibrar escala de score.
4. **Reordenar** os candidatos do primeiro estágio com um cross-encoder e **dimensionar** o custo em número de inferências por consulta.
5. **Gerar** uma resposta que cita as fontes recuperadas e **validar** por código que toda citação existe no contexto entregue ao modelo.
6. **Medir** `recall@k`, `precision@k` e MRR sobre um conjunto de 15 a 20 consultas rotuladas, **comparar** as três estratégias e **demonstrar** que o reranking mexe em `recall@3` e **não** mexe no `recall@k_ret`.

*(Idênticos aos da V1.)*

## 3. Teoria aplicada

Este é um laboratório: a teoria está nas Aulas 18 e 19. O que segue são os **contratos de execução** do lab — e eles são conteúdo, porque decidem se o número que sai da tabela do Checkpoint 6 significa alguma coisa. A grade de laboratório da §3 do contrato organiza os blocos.

### Os seis checkpoints, pelo que cada um imprime

| CP | Relógio | O que faz | **O que a tela imprime quando está certo** | Apêndice |
|---|---|---|---|---|
| 1 | 00:35–00:48 | chunking com metadados | `Checkpoint 1 OK — 20 chunks, metadado íntegro, prefixo presente` | — |
| 2 | 00:48–01:05 | índice e retrieval denso | `Checkpoint 2 OK — 20 vetores em <backend>` + o `Art. 42` no top-3 da consulta de controle | — |
| 3 | 01:15–01:24 | BM25 e `combinar_rrf` | `Checkpoint 3 OK — RRF confere no caso calculado à mão` + as duas posições do alvo lado a lado | — |
| 4 | 01:24–01:32 | `reordenar` com cross-encoder | `Checkpoint 4 OK — 10 inferências em N,NNs` + a tabela "posição antes / posição depois" | A.2 |
| 5 | 01:32–01:40 | responder citando as fontes | `Checkpoint 5 OK — 4 casos de citação verificados (<motor>)` | — |
| 6 | 01:40–01:50 | 18 consultas rotuladas | **as duas tabelas**, com `Δ recall@3` marcado `EMPÍRICO` e `recall@10 idêntico? True` marcado `GARANTIDO` | A.1 · A.2 · A.3 |

**Entregável:** notebook executado + as duas tabelas + o arquivo do conjunto rotulado. Cinco dos seis checkpoints não chamam modelo de linguagem nenhum.

### Bloco 1 (00:35–01:05) — Do texto bruto ao ranking recuperável

**Conceito 1 — Chunk sem metadado é chunk anônimo, e resposta sem fonte é resposta não auditável.**
Cada chunk carrega `fonte`, `capitulo`, `dispositivo` (o `Art. 42` ou o `§ 1º`) e `titulo`. Esses campos servem a três coisas ao mesmo tempo: o prefixo contextual que entra no texto vetorizado (chunking contextual da Aula 18), a citação que aparece na resposta do Checkpoint 5, e o rótulo que o conjunto de consultas do Checkpoint 6 usa como gabarito.
*Observável que motiva:* o teste do CP1 conta 20 chunks a partir de 16 dispositivos e falha nominalmente quem devolveu 16 — parágrafo é chunk próprio.
*Analogia do instrutor:* metadado é a etiqueta na caixa do arquivo morto. Sem etiqueta a caixa continua guardando o documento, e continua inútil.
*Erro conceitual comum:* guardar o metadado num dicionário paralelo indexado por posição e depois reordenar a lista de chunks. O texto e a etiqueta se desencontram, o `recall@k` do Checkpoint 6 sai plausível e errado. No notebook o chunk é um único dicionário — texto e metadado no mesmo objeto, sempre.

**Conceito 2 — A fronteira do corte é uma decisão de conteúdo, não de contagem.**
O corpus embutido é um regulamento com artigos e parágrafos. O dispositivo é a unidade semântica natural: cortar em 500 caracteres fixos parte `§ 2º` no meio e produz um chunk que responde metade da pergunta. O notebook implementa as duas estratégias e manda comparar — corte por dispositivo e corte por janela fixa com sobreposição.
*Erro conceitual comum:* concluir "dispositivo é sempre melhor". Em corpus sem estrutura marcada (transcrição, página web, ticket), não existe dispositivo para cortar — e aí a janela fixa com sobreposição é a única opção. A decisão sai da medição do Checkpoint 6, não da preferência.

**Conceito 3 — O índice é um detalhe de implementação; o espaço vetorial não é.**
Chroma, FAISS e uma matriz `numpy` com produto escalar dão o mesmo resultado neste tamanho de corpus. O que não é detalhe: consulta e documento têm de ser vetorizados **pelo mesmo modelo**, com a mesma normalização. Com vetores normalizados, produto escalar é cosseno — e é por isso que o notebook normaliza na ingestão e na consulta.
*Analogia:* trocar de banco vetorial é trocar de armário. Trocar de modelo de embedding no meio é medir metade das peças em centímetro e metade em polegada.
*Erro conceitual comum:* reindexar com um modelo e consultar com outro depois de reiniciar a sessão do Colab. O sistema não reclama; ele devolve vizinhos aleatórios com cosseno alto.

- **Fundamento:** com `‖u‖ = ‖v‖ = 1`, o produto escalar `u·v` **é** o cosseno do ângulo entre os dois — é essa identidade que autoriza o notebook a trocar uma chamada de similaridade por uma multiplicação de matriz.
  → o cosseno, a normalização L2 e o que o treino contrastivo muda estão derivados no apêndice da Aula 19 e da Aula 18; nada disso se repete aqui

**Conceito 4 — RRF funde posição, e por isso não precisa de calibração.**
O `combinar_rrf` do Checkpoint 3 recebe duas listas de índices ordenados e devolve uma. Nenhum score entra na conta: `RRF(d) = Σ_i 1/(k + rank_i(d))`, com `k = 60`. É a diferença entre somar pontos de duas etapas de um campeonato e somar segundos de provas em pistas diferentes.
*Erro conceitual comum:* passar para o RRF a lista de scores em vez da lista de posições. O resultado é numérico, ordenado e sem sentido — o teste do checkpoint compara com um caso pequeno calculado à mão exatamente para pegar isso.

- **Fundamento:** a soma `Σ_i 1/(k + rank_i(d))` é invariante a qualquer transformação monotônica dos scores, porque só as posições entram nela; e o `k = 60` é o que controla o quanto o primeiro lugar vale a mais que o segundo.
  → derivação completa, com o efeito de `k` sobre o peso relativo das posições: **A.3 da Aula 19**

### Bloco 2 (01:15–01:50) — Reranking, citação e a medida

**Conceito 5 — O reranker reordena o que chegou; ele não busca.**
`k_ret = 10` candidatos do híbrido, `k_final = 3` entregues ao gerador, 10 inferências de cross-encoder por consulta. A consequência que o Checkpoint 6 torna visível em número: o `recall@3` **muda** e o `recall@10` fica **idêntico** — porque o conjunto dos 10 candidatos é o mesmo antes e depois. Duas leituras diferentes na mesma tabela, e a distinção é a lição: a igualdade do `recall@10` é **garantida**; a direção do `recall@3` é **empírica** — sobe com um cross-encoder de verdade e pode **cair** com o reranker de brinquedo do modo degradado, porque ordenar por sobreposição de termos é pior que a ordem do RRF. Reranker ruim estraga a vitrine; nenhum reranker mexe no estoque.
*Erro conceitual comum:* atribuir ao reranker um ganho de `recall@10`. Se esse número mudou, o pipeline mudou em outro lugar — o candidato entrou por outra via. O segundo erro é o espelho do primeiro: ver o `recall@3` cair e concluir "meu código está errado", quando o que se mediu foi um reranker ruim fazendo exatamente o que um reranker ruim faz.

- **Fundamento:** o `recall@k_ret` do primeiro estágio é um **teto** para o sistema inteiro, porque o conjunto entregue ao gerador é um subconjunto do conjunto de candidatos. Nenhuma escolha de reranker, prompt, temperatura ou modelo gerador levanta esse teto.
  → a demonstração e a condição de igualdade estão em **A.4 da Aula 19**. O que este lab acrescenta é a leitura da **tabela deles**: por que a coluna `recall@10` não pode mover, por que a `recall@3` pode mover nos dois sentidos, e qual é a ordem de depuração que essas duas frases impõem: **Apêndice A.2** (slide 13)

**Conceito 6 — Citar é verificável por código.**
A resposta do Checkpoint 5 traz `[fonte: Art. 42]` ao fim de cada afirmação. O notebook valida por regex se todo identificador citado está entre os `k_final` chunks que entraram no prompt. Duas falhas distintas aparecem aqui: citar um documento que existe no corpus mas não estava no contexto (o modelo respondeu de memória) e citar um identificador que não existe em lugar nenhum (o modelo inventou a etiqueta).
*Analogia:* é a diferença entre citar um livro que você leu, citar um livro que você não abriu e citar um livro que não existe. As três acontecem, e só a primeira é aceitável.
*Erro conceitual comum:* medir citação "olhando" a resposta. Com 18 consultas, olhar não escala e o olho é complacente — a taxa de citação válida é uma função, e ela roda.

**Conceito 7 — Sem gerador ainda dá para fazer o lab; sem medida não dá.**
O acesso a um modelo por API é opcional neste lab: existe um modo offline com resposta extrativa, que monta a resposta a partir das frases recuperadas e cita normalmente. Os Checkpoints 1 a 4 e o 6 não chamam LLM nenhum. Isso é deliberado — a parte avaliada do lab é a recuperação medida, e ela não depende de quota.
*Erro conceitual comum:* achar que a resposta extrativa é "o lab pela metade". A resposta extrativa é um gerador honesto de baixa fluência: ela mostra que o problema difícil do RAG está antes da geração.

**Conceito 8 — Quinze a vinte consultas, escritas antes de ver o sistema.**
O conjunto rotulado é o instrumento de medida, e ele tem um requisito de composição: pelo menos um terço em paráfrase (sem termo em comum com o documento) e pelo menos três com identificador, código ou nome próprio. O conjunto embutido tem 18 consultas — 12 paráfrases, 3 com identificador e 3 mistas, cada uma com exatamente um dispositivo relevante. Escrever as consultas **depois** de brincar com o sistema produz um conjunto que o sistema já acerta — o viés mais comum e mais difícil de detectar em avaliação de RAG.
*Erro conceitual comum:* reportar `recall@5 = 0,83` sem dizer quantas consultas há. Com 18 consultas, cada uma vale 5,6 pontos percentuais: uma diferença de 0,05 entre duas estratégias é uma consulta — e o próprio notebook imprime esse aviso embaixo da Tabela 2.

- **Fundamento:** com um relevante por consulta, `recall@k` é a fração das consultas em que o dispositivo certo entrou no top-`k`, o melhor `precision@3` possível é `1/3` **por construção**, e o MRR pune a posição de forma hiperbólica. As três não são intercambiáveis: elas respondem a perguntas diferentes sobre a mesma lista.
  → as definições, a identidade que liga recall e precision e o exemplo resolvido estão em **A.2 da Aula 19**; a aplicação às **18 consultas deste lab**, com a resolução do instrumento e o cálculo das três métricas linha a linha: **Apêndice A.1** (slide 12)
- **Fundamento:** a diferença entre duas estratégias só é distinguível do acaso quando um número mínimo de consultas muda de lado — e esse número é maior que a diferença que a tabela costuma mostrar.
  → quantas consultas rotuladas seriam necessárias, com a conta feita sobre `|Q| = 18`: **Apêndice A.3** (slide 14)

**Conceito 9 — "Montei um chatbot que responde" não cumpre o critério deste lab.**
Vale dizer isto por escrito, porque é o desvio mais frequente: um notebook que recebe pergunta e devolve texto bonito, sem tabela de `recall@k`, sem conjunto rotulado e sem comparação antes/depois do reranking, **não atende ao entregável** — nem aqui, nem no item de rigor quantitativo do projeto final. O produto desta aula é o relatório de métricas; a resposta em linguagem natural é a parte fácil e a menos avaliada.
*Erro conceitual comum:* tratar a tabela como apêndice do sistema. Ela é o sistema, do ponto de vista da nota.

**Conceito 10 — Esta base é reusada como ferramenta do agente no Lab 7.**
A função `buscar(consulta, k)` construída aqui é exatamente a assinatura que o agente da Aula 25 vai chamar como uma de suas ferramentas, e o índice persistido em disco é o que ele vai abrir. Por isso o notebook salva o índice e a função de busca num módulo importável, e não deixa tudo solto em células.
*Erro conceitual comum:* deixar a busca amarrada a variáveis globais definidas em dez células diferentes. No Lab 7 isso não importa; no Lab 6 e no projeto, importa.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 15 min | Setup do ambiente + contexto | Recap da Aula 19 (duas famílias, RRF, o teto do `recall@k_ret`); abrir o notebook no Colab; instalar as dependências e baixar o modelo de embedding; o corpus embutido de 16 dispositivos e o `CAMINHO_CORPUS` parametrizável para o corpus do projeto; o mapa dos seis checkpoints **pelo que cada um imprime**; o entregável — e a frase de que chatbot que responde não conta |
| 00:15 | 20 min | Demonstração guiada (live coding) | O pipeline mínimo em nove linhas, na frente da turma: corpus → chunk → embedding → matriz → consulta → `top-3`; imprimir os três vizinhos de uma paráfrase e de um identificador para reviver o ponto cego da Aula 19; mostrar o mesmo chunk com e sem prefixo contextual; medir `recall@1` de duas consultas à mão. Termina de propósito sem BM25 e sem reranking |
| 00:35 | 30 min | Checkpoints 1–2 (aluno executando) | CP1: `fatiar_por_dispositivo` com metadados e inspeção visual dos chunks; CP2: indexar em Chroma/FAISS/matriz e `buscar_denso` com `top-k` |
| 01:05 | 10 min | Intervalo | — |
| 01:15 | 35 min | Checkpoints 3–6 | CP3: BM25 e `combinar_rrf`; CP4: `reordenar` com cross-encoder e a conta de inferências; CP5: `responder` citando fontes e `validar_citacoes`; CP6: as 18 consultas rotuladas, `recall@k` das três estratégias e a tabela antes/depois do reranking |
| 01:50 | 10 min | Recolhimento | O que entregar (notebook executado, as duas tabelas, o conjunto rotulado, respostas às questões-guia, declaração de uso de IA), prazo de uma semana, critério; aviso de que o Lab 7 reusa esta base como ferramenta do agente; ponte para a Aula 21 |

## 4. Demonstração guiada

**Live coding "o RAG mínimo em nove linhas" — 20 min, `codigo/lab-05-rag-completo.ipynb` (células novas ao fim, apagadas depois).**

O objetivo não é adiantar checkpoint: é mostrar que o pipeline inteiro da Aula 18 caberia em nove linhas — e que é exatamente por caber em nove linhas que ninguém mede. Roda em CPU, com o corpus embutido, sem chave de API.

Passos em alto nível:

1. Imprimir três dos 16 dispositivos do corpus embutido e mostrar a estrutura: `fonte`, `capitulo`, `dispositivo`, `titulo`, `texto`.
2. Fatiar de forma ingênua — um chunk por dispositivo, sem prefixo contextual — e mostrar a lista de 16 strings.
3. Vetorizar os 16 chunks com o modelo multilíngue pequeno, imprimir o shape da matriz e conferir que as normas são 1.
4. Consultar com uma paráfrase ("posso desistir de uma matéria depois do início das aulas?"), imprimir o `top-3` com cosseno. Acerta.
5. Consultar com um identificador ("o que diz o edital PRG-2025-014?"), imprimir o `top-3`. Erra — e é o ponto cego da Aula 19 aparecendo no código deles, não no meu slide.
6. Ligar o prefixo contextual (`Regulamento · CAPÍTULO III · Art. 42 — Do trancamento:`) nos mesmos 16 chunks, reindexar e repetir a consulta 5. Comparar as duas saídas: melhora, e não resolve.
7. Escrever à mão o `recall@1` das duas consultas: `1/2`. Duas linhas de código, e é a semente do Checkpoint 6.
8. Fechar dizendo o que ficou de fora — BM25, fusão, reranking, citação e o conjunto de 18 consultas — e que é isso o lab.

**Número que a demo produz.** Um só, e ele é minúsculo de propósito: `recall@1 = 1/2 = 0,50`, calculado à mão sobre **duas** consultas, no passo 7. Esse `0,50` é o instrumento inteiro do Checkpoint 6 em escala de brinquedo — gabarito, contagem e divisão —, e é o que permite dizer, sem slide de definição, que avaliar recuperação não exige framework nenhum: exige gabarito. Ele também é o primeiro exemplo de `|Q|` ridiculamente pequeno, o que torna natural anunciar o aviso de método que o notebook imprime no CP6: com `|Q| = 2`, cada consulta vale 50 pontos percentuais; com `|Q| = 18`, 5,6. O passo 5 produz o segundo observável da demo, qualitativo mas verificável: a consulta com identificador devolvendo o edital **errado** com cosseno alto e sem aviso nenhum.

Insumos preparados na véspera: o notebook rodado de ponta a ponta no Colab da oferta com o tempo de download do modelo anotado; o cache do modelo de embedding num arquivo `.zip` para distribuir se a rede da sala não aguentar 30 downloads simultâneos; a saída completa do notebook salva em texto.

## 5. Hands-on

Seis checkpoints, cada um abrindo pelo observável. O aluno trabalha no próprio notebook; o instrutor circula pedindo `print`, não perguntando se está funcionando.

**Checkpoint 1 · 00:35–00:48 — Chunking com metadados.**
Implementar `fatiar_por_dispositivo(documentos)` e `texto_para_indexar(chunk)`: um chunk por artigo ou parágrafo, com `fonte`, `capitulo`, `dispositivo`, `titulo` e `texto` no mesmo dicionário, e o prefixo contextual montado a partir dos metadados. Rodar a inspeção visual: três chunks impressos por extenso e o histograma de tamanhos.
*Critério de conclusão observável:* a tela imprime `Checkpoint 1 OK — 20 chunks, metadado íntegro, prefixo presente`. O teste conferiu cinco coisas: 20 chunks a partir dos 16 dispositivos (os quatro parágrafos viram chunks próprios), nenhum chunk sem `dispositivo`, nenhum `dispositivo` duplicado, nenhum chunk acima do limite de 900 caracteres, e o prefixo contextual presente em `texto_para_indexar` de todos.

**Checkpoint 2 · 00:48–01:05 — Índice e retrieval denso.**
Implementar `construir_indice(chunks)` e `buscar_denso(consulta, k)`. O notebook tenta Chroma, cai para FAISS e cai para matriz `numpy` — o aluno implementa a interface, não o banco. Vetorizar, normalizar, consultar.
*Critério de conclusão observável:* a tela imprime `Checkpoint 2 OK — 20 vetores em <backend>`. O teste conferiu que o índice tem o mesmo número de vetores que chunks, que `buscar_denso` devolve exatamente `k` resultados ordenados por score **decrescente** com o dicionário do chunk colado em cada um, e que a consulta de paráfrase de controle traz o `Art. 42` no `top-3`.

**Checkpoint 3 · 01:15–01:24 — BM25 e fusão híbrida.**
O BM25 vem pronto (é o da Aula 19, comentado). O TODO é `combinar_rrf(rankings, k=60)`: receber listas de **posições**, devolver uma lista fundida.
*Critério de conclusão observável:* a tela imprime `Checkpoint 3 OK — RRF confere no caso calculado à mão` e, abaixo, três linhas: o `top-5` denso, o `top-5` híbrido e a posição do alvo nos dois lado a lado (`Edital PRG-2025-014: #>5 no denso -> #1 no híbrido`). O teste exige o documento certo no **top-2 do híbrido, em posição igual ou melhor que no denso**, e confere a pontuação do caso pequeno contra `1/61 + 1/62`.

**Checkpoint 4 · 01:24–01:32 — Reranking com cross-encoder.**
Implementar `reordenar(consulta, candidatos)`: montar os pares `(consulta, texto_do_chunk)`, chamar o cross-encoder, ordenar por score.
*Critério de conclusão observável:* a tela imprime `Checkpoint 4 OK — 10 inferências em N,NNs` e, em seguida, a tabela de três colunas "posição antes · posição depois · dispositivo". O teste conferiu que a saída é uma **permutação exata** da entrada (mesmo tamanho, mesmo conjunto ordenado) e que o contador de inferências é igual a `k_ret = 10`.

**Checkpoint 5 · 01:32–01:40 — Responder citando as fontes.**
Implementar `montar_prompt(consulta, chunks)` com as regras de citação e `validar_citacoes(resposta, chunks)`. Rodar em modo API (chave por `getpass`) ou em modo offline com resposta extrativa.
*Critério de conclusão observável:* a tela imprime `Checkpoint 5 OK — 4 casos de citação verificados (<motor>)`, seguido da resposta gerada e da linha `citações válidas: True`. O teste conferiu que o prompt contém os `k_final = 3` chunks com identificador e texto, que ele explica o formato `[fonte: …]`, e que `validar_citacoes` **aprova** a resposta bem formada e **reprova** a que cita documento fora do contexto e a que cita identificador inexistente.

**Checkpoint 6 · 01:40–01:50 — Conjunto rotulado e `recall@k` antes e depois.**
Usar as 18 consultas rotuladas embutidas — e substituir ou completar com as consultas do próprio corpus, se a equipe trouxe o dever da Aula 19. Implementar `recall_em_k`, `precision_em_k` e `mrr`, e rodar `avaliar()` sobre as quatro configurações: denso, BM25, híbrido, híbrido + reranking.
*Critério de conclusão observável:* **duas tabelas impressas pelo notebook**, mais três linhas de leitura. A Tabela 1 traz `|Q| = 18`, o vetorizador, o backend e o `k_rrf` no cabeçalho, e compara denso, BM25 e híbrido em `recall@1`, `recall@3`, `recall@5`, `precision@3` e MRR. A Tabela 2 traz `k_ret = 10`, `k_final = 3` e o reranker no cabeçalho, e imprime `Δ recall@3 = ±0,NNN (EMPÍRICO)` e `recall@10 idêntico? True (GARANTIDO)`. Abaixo, o aviso de método que o próprio notebook escreve — com `|Q| = 18`, uma consulta vale 5,6 pontos percentuais — e o recorte por tipo de consulta, em que o `recall@1` do denso nas consultas com identificador aparece perto de zero e o do BM25 perto de 1. É a Aula 19 medida pelo próprio aluno.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Download do modelo de embedding falha** ou trava com 30 máquinas na mesma rede | `sentence-transformers` levanta exceção, ou a célula fica minutos sem terminar | O notebook cai sozinho no `VetorizadorLexico` (TF-IDF de n-gramas de caractere, puro `numpy`) e avisa na tela; todos os seis checkpoints rodam nesse modo. O instrutor distribui o cache do modelo por pendrive/`.zip` para quem quiser o modelo real. O relatório **declara** qual vetorizador produziu os números |
| **Cross-encoder não carrega** (é o download maior do lab) | Exceção no `carregar_reranker` | O notebook usa o `reranker de brinquedo` documentado (score por sobreposição de termos), claramente rotulado na saída. A tabela do CP6 continua válida como comparação antes/depois, desde que o relatório diga qual reranker foi usado — e o `Δ recall@3` negativo passa a ser **resultado**, não bug (ver **A.2**) |
| **Chroma não instala** no Colab do dia | `pip install chromadb` falha ou conflita | Cai para FAISS; se FAISS falhar, cai para a matriz `numpy`, que não tem dependência nenhuma. A interface do CP2 é a mesma nos três casos, e o corpus tem 20 chunks — não há ganho de desempenho em jogo |
| **Sala sem rede** (nem pip, nem modelo, nem API) | Primeira célula de instalação falha | O caminho inteiro em `numpy` + BM25 + reranker de brinquedo + resposta extrativa não usa rede depois do notebook aberto. O único requisito é o `numpy`, que já vem no Colab. Se nem o Colab abrir: o instrutor distribui o notebook e o `requirements.txt` para execução local |
| **Aluno sem chave de API** para o CP5 | `getpass` vazio | Modo offline com resposta extrativa, que é o padrão do notebook. O CP5 é avaliado pela validação de citação, não pela fluência da resposta |
| **Chave de API vazando** no notebook entregue | Chave visível numa célula | A célula de chave usa `getpass` e não imprime; a nota do recolhimento avisa que chave hardcoded no notebook entregue é problema de segurança, e o instrutor confere isso na correção |
| **Turma em ritmos muito diferentes** | Metade ainda no CP2 aos 01:00 | CP1 e CP2 têm célula de solução comentada que o instrutor libera aos 00:48 e 01:05. Ninguém pode ficar travado antes do CP3, e o CP6 é o checkpoint que não pode faltar — se o tempo apertar, o CP5 vai para casa antes do CP6 |
| **Aluno mede com o corpus do projeto e não roda nada** (corpus enorme, PDF sujo) | Célula de ingestão do próprio corpus travada aos 00:50 | Regra dita em sala: **primeiro** fechar os seis checkpoints com o corpus embutido, **depois** trocar o `CAMINHO_CORPUS`. A troca é o desafio pós-aula, não o lab |
| **`recall@k` idêntico entre as três estratégias** | Três linhas iguais na tabela do CP6 | Sintoma quase sempre de conjunto rotulado mal composto (todas as consultas com termo em comum, ou todas paráfrases). Conferir a composição exigida no CP6 e acrescentar duas consultas com identificador |
| **`recall@10` diferente antes e depois do reranking** | A linha `recall@10 idêntico? False` | Não é ruído de medição: é defeito de pipeline. Alguma coisa fora do reranker mudou o conjunto de candidatos — tipicamente `reordenar` devolvendo os `k_final` cortados em vez da permutação completa. A ordem de conferência está em **A.2** |

## 7. Artefatos produzidos

- `lab-05-rag-completo.ipynb` executado, com todas as saídas visíveis: os `Checkpoint N OK`, a inspeção dos chunks, o histograma de tamanhos, os rankings lado a lado e as duas tabelas finais.
- **Tabela 1 — comparação de estratégias:** denso, BM25 e híbrido em `recall@1`, `recall@3`, `recall@5`, `precision@3` e MRR, com `|Q|` e o vetorizador declarados.
- **Tabela 2 — efeito do reranking:** híbrido e híbrido + reranking em `recall@3` e `recall@10`, com o reranker declarado e a frase explicando a coluna que não mudou.
- **Recorte por tipo de consulta:** `recall@1` e `recall@3` das três estratégias separados em paráfrase, identificador e misto — a evidência de que os erros das duas famílias são complementares, medida no corpus do próprio aluno.
- **Conjunto de consultas rotuladas** (15 a 20 linhas, `pergunta ; dispositivo_relevante`) em arquivo próprio — o instrumento de medida que o projeto final vai herdar.
- **Índice persistido** e a função `buscar(consulta, k)` isolada num módulo importável — a peça que o Lab 7 (Aula 25) vai chamar como ferramenta do agente.
- Respostas às **cinco questões-guia** em células de markdown do próprio notebook.
- **Declaração de uso de IA** — quais ferramentas, para quê, em duas linhas.

## 8. Desafio pós-aula

**Este lab é o entregável avaliado da semana.** Prazo: uma semana após a aula. O conteúdo da entrega está no §7. Os Checkpoints 1 a 4 e o 6 são o núcleo obrigatório; o CP5 pode ser concluído em casa, inclusive em modo offline.

Extensão dirigida, e ela é o caminho natural do projeto: trocar o `CAMINHO_CORPUS` pelo corpus real da equipe e refazer as duas tabelas. Junto com isso, três perguntas para responder com número e não com opinião:

1. Trocando o corte por dispositivo pelo corte em janela fixa com sobreposição, o `recall@3` mudou em qual direção, e **em quantas consultas**? A segunda metade da pergunta é a que importa: o apêndice **A.3** dá o número mínimo de consultas que precisariam mudar de lado para a diferença não ser acaso.
2. Existe alguma consulta em que o híbrido é **pior** que a melhor das duas estratégias isoladas? Se sim, o que ela tem de particular?
3. Com `k_ret = 10` e `k_ret = 30`, o `recall@3` depois do reranking mudou? A resposta diz se o gargalo está no primeiro ou no segundo estágio — e o argumento formal disso é o Corolário 3 de **A.4 da Aula 19**.

Leitura de apoio: Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (arXiv 2005.11401), seções 2 e 4 — agora com o pipeline montado, o artigo vira curto. Complementar, para quem for atacar o corpus real: Reimers & Gurevych, *Sentence-BERT* (arXiv 1908.10084), pela discussão de por que o bi-encoder é treinado para similaridade e não para casamento de termo.

## 9. Critérios de avaliação

Este lab **é avaliado** e compõe os **30%** dos laboratórios na média da disciplina, com a política da ementa — oito labs, entrega até uma semana, **descartando a menor nota**. Não há peso novo inventado aqui.

Distribuição da nota deste lab:

- **Checkpoints 1 a 4 concluídos com saída visível — 40%.** Os quatro `Checkpoint N OK` impressos, a inspeção dos chunks, o ranking híbrido e a tabela de posição antes/depois do reranking. Notebook sem saídas não é avaliável.
- **Relatório de métricas do Checkpoint 6 — 35%.** As duas tabelas, com `k` declarado, `|Q|` declarado, vetorizador e reranker declarados, e a frase que explica por que o `recall@k_ret` não muda com reranking. **Esta é a parte que decide a nota do lab:** um notebook que responde perguntas com fluência e não traz as tabelas fica, por construção, abaixo da média — a exigência foi anunciada na Aula 19 e está no slide de abertura deste lab.
- **Checkpoint 5, citação validada — 10%.** Prompt com os chunks e seus identificadores, resposta com citação, e `validar_citacoes` rodando sobre os quatro casos de teste.
- **Respostas às cinco questões-guia — 10%.** Avaliadas por precisão conceitual, não por extensão. As duas que separam as notas: por que `recall@10` não muda depois do reranking, e por que escrever as consultas rotuladas depois de usar o sistema enviesa a medida.
- **Declaração de uso de IA presente — 5%.** Ausência zera este item e habilita defesa oral.

**Nota sobre a prova.** A prova da Aula 17 já foi aplicada; a composição dela é diagnóstico e interpretação **42** · justificativa de escolha **40** · conceito aplicado **8** · derivação **10**. Vale registrar porque o CP6 é exatamente o formato da parte de 42 pontos: uma tabela de resultados reais, e a pergunta é o que ela **permite** e o que **não permite** afirmar. Quem lê `recall@10 idêntico? True` como erro de medição erra a mesma coisa nessa parte da prova, e quem lê `Δ recall@3` negativo como bug de código erra a outra metade.

Observável em sala, sem nota: ao ser questionado no recolhimento, o aluno aponta na própria tabela a coluna que o reranking não pode melhorar e explica por quê, sem usar a palavra "modelo" na explicação.

## Apêndice matemático — índice

Três itens, slides 12 a 14 do deck, **organizados por checkpoint** conforme a §6-bis. Material de estudo e consulta, autossuficiente: quem estuda por aqui sem ter feito o lab consegue reconstruir todas as contas.

| Item | O que estabelece | Checkpoint |
|---|---|---|
| **A.1** | As quatro métricas calculadas sobre **as 18 consultas deste lab**, não em abstrato: com exatamente **um** dispositivo relevante por consulta, `recall@k` é a fração das consultas cujo dispositivo entrou no top-`k`, o `precision@3` tem teto aritmético de `1/3`, e o MRR é a média dos recíprocos das posições. Uma tabela de 18 linhas resolvida por extenso, com os três números finais e a leitura conjunta. Mais a resolução do instrumento: `1/18 = 5,6` pontos percentuais por consulta. As **definições** estão em A.2 da Aula 19 e não se repetem — aqui é a aplicação aos dados deles. | **CP6** |
| **A.2** | Por que o reranking move o `recall@3` e **não** move o `recall@k_ret`: a decomposição da diferença em consultas que subiram e consultas que desceram, a razão de a coluna `recall@10` ser uma identidade e não uma medição, e o caso em que o `Δ recall@3` sai **negativo** com o reranker de brinquedo. Fecha com a **ordem de depuração** que essas duas frases impõem: teto primeiro, ordenação depois, gerador por último — e com o cálculo de quantas inferências cada escolha de `k_ret` custa. O teorema do teto está em A.4 da Aula 19; aqui ele é lido na tabela do aluno. | **CP4**, CP6 |
| **A.3** | Quantas consultas rotuladas seriam necessárias para a diferença medida antes/depois do reranking ser distinguível de ruído: a resolução de `1/18`, o erro-padrão de uma proporção com `n = 18`, o teste pareado sobre as consultas **discordantes** (as duas configurações rodam nas mesmas 18 consultas) e a tabela de `n` necessário por precisão desejada. Conclui com o número que o relatório precisa: quantas consultas têm de mudar de lado, e por que 18 servem para **ver um fenômeno** e não para **ordenar estratégias**. | **CP6** |

**As três referências cruzadas que amarram o curso.** O A.3 deste lab é o terceiro elo de um fio, e os três elos são o **mesmo argumento** com o ruído vindo de fontes diferentes: no **A.5 do Lab 2 (Aula 9)** o ruído vem da **semente**, e a régua é o desvio entre duas execuções da mesma configuração; no **A.3 do Lab 3 (Aula 11)** o ruído vem da **amostra de prompts** — 20 comentários, 10 problemas —, e lá aparece o resultado que este item reusa: com pareamento, uma diferença só é distinguível do acaso se ao menos 6 itens mudarem de lado na mesma direção; **aqui** o ruído vem da **amostra de consultas**, e a novidade é que as duas configurações comparadas são o mesmo sistema antes e depois de um estágio, o que torna o pareamento não uma escolha de método mas um fato da arquitetura; e o **A.5 do Lab 8 (Aula 28)** paga a conta completa, com intervalo de Wilson e teste de McNemar sobre o conjunto de teste do projeto. A **Aula 27** é onde o argumento é feito no nível conceitual. Quem seguir os quatro na ordem vê a mesma ideia crescendo de uma semente até uma decisão de produto.
