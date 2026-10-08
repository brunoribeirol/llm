---
aula: 19
titulo: "RAG II: retrieval híbrido, reranking e métricas"
modulo: "5 — RAG, Ferramentas e Agentes de IA"
tipo: teorica
semana: 10
duracao_min: 120
versao: v2
---

# Aula 19 — RAG II: retrieval híbrido, reranking e métricas

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** Esta aula já era conduzida pela aplicação na V1 e por isso muda pouco:
> abre por um sintoma medido, as fórmulas entram lidas por partes e o exercício já era de
> diagnóstico. O transporte para a V2 preserva blocos, tempos e objetivos, e acrescenta o apêndice
> com o fundamento formal que estava disperso — **A.1** (BM25, `k₁` e `b`), **A.2** (as quatro
> métricas, com exemplo numérico completo), **A.3** (RRF e o que o `k = 60` controla) e **A.4** (a
> demonstração de que `recall@k_final ≤ recall@k_ret`) — mais os ponteiros no fluxo. Carga horária,
> numeração e objetivos de aprendizagem inalterados.

## 1. Objetivo da aula

Fechar o ponto cego da Aula 18 — a busca por significado não acha termo exato — e transformar "meu RAG responde mal" num diagnóstico com número: qual estratégia de recuperação, com qual reranking, medida por qual métrica, e por que `recall@k` é a primeira coisa a olhar antes de mexer em prompt ou trocar de modelo.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Prever** qual estratégia — densa, esparsa (BM25) ou híbrida — vence numa consulta dada, a partir da presença de identificador, código, nome próprio raro ou paráfrase.
2. **Explicar** os dois parâmetros do BM25 (`k₁` de saturação de frequência e `b` de normalização por comprimento) e **justificar** por que somar scores de BM25 e cosseno diretamente é incorreto.
3. **Aplicar** Reciprocal Rank Fusion para fundir dois rankings e **argumentar** por que fundir por posição é mais robusto que fundir por score.
4. **Distinguir** bi-encoder de cross-encoder pelo momento em que a consulta encontra o documento, e **dimensionar** o custo de reranking em número de inferências por consulta.
5. **Calcular** `recall@k`, `precision@k`, MRR e nDCG@k a partir de uma lista de resultados rotulados, e **defender** por que `recall@k` do primeiro estágio é o teto do sistema inteiro.
6. **Nomear** três modos de falha de RAG — chunk mal cortado, contexto irrelevante competindo com a instrução e injeção de prompt via documento recuperado — e **apontar** em que etapa do pipeline cada um nasce.

## 3. Teoria aplicada

### Bloco 1 (00:10–00:55) — Duas famílias de recuperação e a fusão das duas

**Conceito 1 — O ponto cego do denso: identificador, código e nome próprio raro.**
O vetor de um chunk é uma média comprimida do significado do trecho. Uma sequência como `PRG-2025-014` ou `Art. 42` carrega quase nenhum significado distribuído: ou o tokenizador a quebra em pedaços que aparecem em milhares de outros contextos, ou o termo é raro demais para o modelo de embedding ter aprendido geometria útil para ele. Resultado: a consulta "o que diz o edital PRG-2025-014?" recupera *qualquer* edital, com cosseno alto e confiança total.
*Analogia do instrutor:* pedir a busca semântica para achar um número de processo é como pedir a alguém que leu o livro inteiro para lembrar em que página estava a vírgula. Ela entendeu o livro; ela não indexou o símbolo.
*Erro conceitual comum:* achar que o problema é o modelo de embedding ser pequeno. Modelo maior melhora paráfrase, não casamento exato de símbolo raro — o casamento exato não é o que a função de perda contrastiva otimiza.

**Conceito 2 — BM25: a busca de vinte anos atrás que ainda ganha metade das consultas.**
Recuperação esparsa representa consulta e documento como vetores do tamanho do vocabulário, quase todos zeros. O score do BM25 (Robertson & Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond*, 2009) soma, sobre os termos da consulta:

```
score(q,d) = Σ_t IDF(t) · [ f(t,d)·(k₁+1) ] / [ f(t,d) + k₁·(1 − b + b·|d|/avgdl) ]
IDF(t)     = ln( (N − n(t) + 0,5) / (n(t) + 0,5) + 1 )
```

Três ideias dentro dessa fórmula: termo raro pesa mais (IDF); a décima ocorrência de um termo vale menos que a segunda (saturação, controlada por `k₁ ≈ 1,2–2,0`); documento longo não ganha vantagem só por ser longo (normalização por comprimento, controlada por `b ≈ 0,75`, com `b = 0` desligando a normalização).
*Fundamento:* os três fatores da fórmula, com `S(f,K) = f(k₁+1)/(f + k₁K)` crescente e concava em `f`, teto assintótico `k₁+1`, e `K(d) = 1 − b + b·|d|/avgdl`. → **A.1**
*Analogia:* é o índice remissivo no fim do livro. Ele não entende nada e acha o símbolo em tempo constante.
*Erro conceitual comum:* tratar BM25 como legado. Ele é a linha de base que muitos sistemas densos não batem em consulta com termo técnico, e é barato: um índice invertido cabe em memória num corpus que exigiria GPU para vetorizar.

**Conceito 3 — Onde o esparso falha, e por que os dois erros são complementares.**
BM25 casa string. "Posso desistir de uma matéria?" não contém "trancamento" nem "disciplina": zero termos em comum, score zero, e nenhum stemming resolve sinônimo. O denso acerta essa e erra a do identificador; o esparso faz o oposto. As duas famílias erram em conjuntos de consulta quase disjuntos — e é exatamente isso que torna a combinação valiosa, e não apenas "duas é melhor que uma".
*Erro conceitual comum:* concluir que híbrido é sempre melhor por ser "mais completo". Híbrido é melhor quando os erros são complementares; se as duas estratégias erram nas mesmas consultas, fundir não recupera nada e só custa latência. Isso se verifica medindo, não supondo.

**Conceito 4 — Fusão: por que somar scores é errado e RRF é o padrão.**
O cosseno vive em `[−1, 1]`; o score do BM25 não tem teto e depende do corpus, da consulta e do tamanho do documento. Somar os dois — ou fazer `α·denso + (1−α)·esparso` sem normalizar — deixa a escala de um dominar o outro por acidente, e o `α` que funciona num corpus não transfere para outro. A alternativa robusta ignora o score e usa só a **posição**: Reciprocal Rank Fusion (Cormack, Clarke & Buettcher, SIGIR 2009):

```
RRF(d) = Σ_i 1 / (k + rank_i(d)),   k = 60 por convenção
```

Documento em 1º num ranking e ausente no outro ainda pontua; documento razoável nos dois ranking sobe. O `k = 60` amortece o topo: a diferença entre a posição 1 e a 2 deixa de ser 55 vezes maior que entre a 10 e a 11 (cai para 1,3×).
*Fundamento:* `RRF(d) = Σ_i 1/(k + rank_i(d))`; o ponto de empate `r* = k + 2` mostra que `k` é, literalmente, quantas posições de discordância o sistema tolera. → **A.3**
*Analogia:* é apuração por colocação, não por tempo — como somar pontos de duas etapas de um campeonato em vez de somar segundos de provas em pistas diferentes.
*Erro conceitual comum:* normalizar min-max os scores de cada ranking e somar. Funciona quando os dois rankings têm distribuições parecidas e quebra quando uma consulta não tem nenhum bom resultado esparso — o min-max estica ruído até o topo.

### Bloco 2 (01:05–01:50) — Reranking, métricas e os modos de falha

**Conceito 5 — Bi-encoder × cross-encoder: quando a consulta encontra o documento.**
O bi-encoder da Aula 18 codifica consulta e documento **separadamente**; eles só se encontram no produto escalar do fim. Isso permite pré-computar todo o acervo offline, e é o que torna a busca viável. O cross-encoder concatena os dois numa entrada só — `[CLS] consulta [SEP] documento [SEP]` — e deixa a atenção cruzar os tokens da consulta com os tokens do documento em todas as camadas, produzindo um único score de relevância (Nogueira & Cho, *Passage Re-ranking with BERT*, arXiv 1901.04085). Ganha precisão porque vê interação termo a termo; perde escalabilidade porque **nada pode ser pré-computado**: `N` documentos custam `N` inferências por consulta.
*Analogia:* o bi-encoder é o resumo que cada candidato escreve sobre si mesmo antes da entrevista; o cross-encoder é a entrevista, com a vaga na mão do entrevistador. Um serve para filtrar mil; o outro serve para decidir entre cinco.
*Erro conceitual comum:* querer trocar o bi-encoder pelo cross-encoder no primeiro estágio. Com 50 mil chunks, isso é 50 mil inferências por pergunta — não é uma questão de otimizar, é uma ordem de grandeza errada.

**Conceito 6 — A arquitetura de dois estágios, e o teto que ela cria.**
O desenho padrão: recuperar `k_ret` candidatos barato (denso, BM25 ou híbrido), reordenar os `k_ret` com o cross-encoder, entregar `k_final` ao gerador. Números típicos de um sistema pequeno: `k_ret = 50`, `k_final = 5` — 50 inferências de reranking por consulta, na casa de dezenas de milissegundos em CPU com um modelo pequeno. A consequência que decide a depuração: **o reranking não inventa documento**. Se o trecho certo não está entre os 50, ele não vai aparecer entre os 5. O `recall@50` do primeiro estágio é o teto do sistema inteiro; o reranking só converte recall bruto em precisão no topo.
*Fundamento:* `F(q) ⊆ C(q)` ⇒ `recall@k_final ≤ recall@k_ret`, com a condição de igualdade e o corolário de que recall é cego a reordenação quando `k_final = k_ret`. → **A.4**
*Erro conceitual comum:* medir só o resultado final e atribuir ao reranker um ganho que veio do recuperador (ou uma perda que ele não causou). Medir as duas camadas separadamente é a única forma de saber onde mexer.

**Conceito 7 — As quatro métricas, e o que cada uma responde.**
Com um conjunto de consultas rotuladas — para cada consulta, quais chunks são relevantes:

```
recall@k    = |relevantes ∩ top-k| / |relevantes|
precision@k = |relevantes ∩ top-k| / k
MRR         = (1/|Q|) · Σ_q 1 / rank_q(primeiro relevante)
DCG@k       = Σ_{i=1..k} rel_i / log₂(i+1)     ;   nDCG@k = DCG@k / IDCG@k
```

`recall@k` pergunta "o material necessário chegou?"; `precision@k` pergunta "quanto do que chegou presta?"; MRR pergunta "quão em cima está o primeiro acerto?" e serve quando existe uma resposta certa só; nDCG pergunta "a ordem está boa?", aceitando relevância graduada (2 = responde, 1 = relacionado, 0 = irrelevante) e descontando por posição.
*Fundamento:* as quatro definições, a identidade `precision@k = recall@k · |R_q|/k` (que explica o teto de `0,2`), e `nDCG = DCG/IDCG`. → **A.2**
*Analogia:* recall é o estoque, precisão é a prateleira, MRR e nDCG são a vitrine.
*Erro conceitual comum:* reportar uma média sem dizer o `k` e sem dizer quantas consultas há. `recall@5 = 0,8` com 5 consultas rotuladas não distingue 0,8 de 0,6 — a variância de um conjunto minúsculo engole a diferença. É o mesmo erro de método do Lab 2, agora em recuperação.

**Conceito 8 — Por que `recall@k` é a primeira coisa a depurar.**
O gerador só pode responder com o que recebeu. Se o chunk certo não está no contexto, nenhuma escolha de prompt, temperatura ou modelo recupera a informação: o teto de qualidade da resposta já foi fixado na etapa 6 do pipeline. Daí a ordem de investigação de um RAG doente: (1) medir `recall@k` do primeiro estágio com o conjunto rotulado; (2) se o recall é baixo, o problema é chunking, modelo de embedding, idioma ou falta de BM25 — e nada disso se conserta no prompt; (3) só se o recall é alto e a resposta continua ruim é que a suspeita passa para reranking, montagem do contexto e geração.
*Fundamento:* a ordem de investigação é consequência da desigualdade do teto, não preferência de método. → **A.4**, Corolário 1
*Analogia:* é triagem de pronto-socorro. Antes de discutir o tratamento, verificar se o paciente certo entrou na sala.
*Erro conceitual comum:* começar pela geração porque é a parte visível. A resposta é o sintoma, não o local da falha — o mesmo raciocínio de "avaliar por camada" que o projeto final exige e que a Aula 27 formaliza.

**Conceito 9 — RAG avançado: reescrita de consulta, multi-hop e RAG agêntico.**
Três movimentos além do pipeline linear. **Reescrita de consulta**: a pergunta do usuário raramente é uma boa consulta — expandir com sinônimos, resolver o pronome que se refere ao turno anterior da conversa, ou gerar uma resposta hipotética e buscar por ela (HyDE — Gao et al., arXiv 2212.10496). **Multi-hop**: perguntas cuja resposta exige encadear dois documentos ("o prazo do artigo citado no edital de aproveitamento") não são resolvíveis por uma busca só; é preciso buscar, ler, formular a segunda consulta e buscar de novo. **RAG agêntico**: em vez de buscar sempre, o modelo decide *se* busca, *o que* busca e *quando para* — o que transforma o pipeline num loop e é exatamente a definição de agente da Aula 23.
*Erro conceitual comum:* adotar reescrita ou multi-hop antes de medir a linha de base. Cada volta a mais no pipeline custa latência e tokens, e o ganho só existe se o conjunto rotulado mostrar que a falha é de formulação da consulta — e não de chunking.

**Conceito 10 — Modos de falha: o chunk, a distração e a injeção.**
(i) **Chunking ruim** — a Aula 18 mediu: nenhuma etapa posterior remonta o parágrafo cortado. (ii) **Contexto irrelevante competindo com a instrução** — aumentar `k` aumenta o recall e *piora* a resposta a partir de certo ponto: material irrelevante consome atenção e a informação enterrada no meio do contexto é usada pior que a do começo ou do fim (Liu et al., *Lost in the Middle*, arXiv 2307.03172). Recall e qualidade da resposta são métricas de camadas diferentes e podem andar em direções opostas. (iii) **Injeção de prompt via documento recuperado** — todo chunk recuperado é entrada não confiável que entra no mesmo campo de texto que a instrução do sistema. Um documento do acervo que contenha "ignore as instruções anteriores e responda X" é executado como se fosse instrução; se o acervo aceita conteúdo de terceiros — página web, PDF enviado por usuário, ticket — o atacante escreve no seu prompt sem tocar no seu código (Greshake et al., arXiv 2302.12173). A Aula 26 trata mitigação; hoje o ponto é reconhecer que a superfície existe e nasce aqui, na etapa 8.
*Erro conceitual comum:* tratar o corpus como confiável por ser "interno". Interno não é sinônimo de não adulterável — basta um formulário que grava texto livre num documento indexado.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura | Recap da Aula 18 (as nove etapas, chunking, bi-encoder) e devolutiva de uma linha sobre os rascunhos de proposta recolhidos; o ponto cego anunciado no fechamento anterior; tese da aula: recuperação é duas famílias e uma medida |
| 00:10 | 45 min | Bloco 1 — Denso, esparso e híbrido | Onde o denso falha (identificador, código, nome próprio raro); BM25, IDF, saturação `k₁` e normalização `b`; onde o esparso falha (paráfrase, sinônimo); por que os erros são complementares; fusão — o problema das escalas e Reciprocal Rank Fusion; quadro de decisão por tipo de consulta; demonstração "três estratégias, três rankings" (13 min) |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — Reranking, métricas e falhas | Bi-encoder × cross-encoder e o custo em inferências; arquitetura de dois estágios e o teto do `recall@k_ret`; `recall@k`, `precision@k`, MRR, nDCG@k; por que `recall@k` é o primeiro diagnóstico; RAG avançado (reescrita, HyDE, multi-hop, agêntico); modos de falha, com injeção de prompt via documento; exercício em dupla (8 min) |
| 01:50 | 10 min | Fechamento | Síntese: o recuperador fixa o teto, o reranker organiza a vitrine, a métrica diz onde mexer; ponte para a Aula 20 (Lab 5 — pipeline RAG completo e medido); leituras com pergunta dirigida |

## 4. Demonstração guiada

**Demo "três estratégias, três rankings" — 13 min, `codigo/demo-hibrido-reranking.py`.**

O objetivo é mostrar, com número na tela e sem gerador nenhum, que a mesma consulta muda de vencedor conforme a estratégia — e que a escolha certa depende da *forma* da consulta, não do domínio. O script estende o mini-corpus fictício de regulamento acadêmico da Aula 18 para dez artigos e editais, roda em CPU e não usa chave de API.

Passos em alto nível:

1. Mostrar o corpus embutido — dez trechos curtos de um regulamento **fictício**, cada um com identificador canônico (`Art. 42`, `Edital PRG-2025-014`) — e as três consultas de teste: uma paráfrase pura, uma com identificador, e uma mista.
2. Construir os dois recuperadores: denso (modelo multilíngue pequeno, com queda automática para vetorizador léxico se o download falhar) e BM25 implementado no próprio script, com `k₁` e `b` visíveis como constantes.
3. Consulta 1 — paráfrase ("dá para desistir de uma matéria depois que as aulas começaram?"): imprimir o top-3 denso e o top-3 BM25 lado a lado. O denso acerta; o BM25 devolve algo com score baixo ou zero por não haver termo em comum.
4. Consulta 2 — identificador ("o que diz o edital PRG-2025-014?"): mesma tabela. Agora inverte — o BM25 crava o documento certo e o denso traz "um edital qualquer" com cosseno alto.
5. Rodar a fusão RRF sobre as duas consultas e mostrar que o híbrido fica em primeiro nas duas, sem que ninguém tenha ajustado peso.
6. Alterar `k` do RRF de 60 para 1 na frente da turma e reexecutar: o topo passa a ser dominado pelo primeiro colocado de um dos rankings. O parâmetro deixa de ser detalhe.
7. Consulta 3 — mista, e o reranking: se o cross-encoder multilíngue carregar, reordenar os 8 candidatos do híbrido e mostrar a mudança de ordem com o score do reranker ao lado do RRF; se não carregar, o script avisa e imprime só o estágio 1, e o argumento do custo (`N` inferências por consulta) é feito no quadro.
8. Fechar imprimindo `recall@1` e `recall@3` das três estratégias sobre as consultas rotuladas do próprio script — três linhas de tabela que são a maquete do que o aluno constrói no Lab 5.

**Número que a demo produz, e que a aula usa como evidência:** a tabela de `recall@1` e `recall@3`
das **três estratégias** (denso, BM25, híbrido) sobre as três consultas rotuladas do próprio
script — três linhas de tabela, impressas no passo 8. Esse número é a maquete exata do entregável
do Lab 5, e é ele que sustenta duas afirmações do fluxo que sem medição seriam opinião: que o
vencedor troca conforme a forma da consulta (slides 3 e 5) e que o híbrido fica em primeiro nas
duas consultas sem ninguém ter ajustado peso (slide 6). O passo 6 produz um segundo número
observável: ao trocar o `k` do RRF de 60 para 1, o topo do ranking muda na tela — é `r* = k + 2`
acontecendo (**A.3**).

Insumos preparados antes da aula: o script rodado na véspera com a saída salva em texto, para o caso de a rede da sala não permitir o download dos modelos.

## 5. Hands-on

**Exercício em dupla — "medir à mão" (8 min, 01:42–01:50).**

Projetar uma tabela pronta com o resultado de três consultas num sistema fictício: para cada consulta, os cinco chunks recuperados em ordem, marcados com `R` (relevante) ou `—`. Cada dupla entrega quatro números e uma frase:

1. `recall@3` e `recall@5` do conjunto (as três consultas juntas).
2. MRR das três consultas.
3. Qual consulta se beneficiaria de reranking e qual **não** se beneficiaria de jeito nenhum — com a justificativa em uma frase.
4. Para a consulta que o reranking não salva: o que fazer, em uma frase.

O desenho da tabela é o ponto pedagógico: a consulta 1 tem o relevante na posição 4 (reranking resolve, o material já está lá); a consulta 2 não tem nenhum relevante no top-5 (reranking é inútil — o problema é do primeiro estágio, e a resposta é chunking, embedding ou BM25); a consulta 3 tem o relevante em 1º (nada a fazer).

Critério de conclusão observável: a dupla entrega os quatro itens preenchidos, e pelo menos duas duplas leem em voz alta a justificativa do item 3. A frase que o instrutor persegue na correção é "o reranking não inventa documento".

*Gabarito completo, com a conta de cada número e o `nDCG@5` das três consultas:* **A.2**, seção "exemplo numérico completo". A justificativa formal da resposta do item 3 é **A.4**.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Download dos modelos falha** na demo (denso ou cross-encoder) | `sentence-transformers` levanta exceção de rede | O script cai sozinho no vetorizador léxico e avisa na tela; o BM25 e o RRF não dependem de download e sustentam os passos 3 a 6. O estágio de reranking vira argumento de quadro (custo em inferências) |
| **Turma trava na fórmula do BM25** | Perguntas sobre a derivação probabilística aos 00:22 | Não derivar. A leitura da fórmula é por partes — IDF, saturação, comprimento — e a promessa é explícita: o que se cobra é saber qual botão mexe em quê, não a derivação |
| **Confusão entre `precision@k` e `recall@k`** persiste | Respostas trocadas no exercício | Voltar ao caso concreto do slide: com 1 relevante e `k = 5`, `precision@5` máxima é 0,2 por construção — o número baixo não significa sistema ruim, significa métrica mal escolhida para a pergunta |
| **Discussão sobre "qual é o melhor modelo de embedding"** consome o Bloco 2 | Debate sobre leaderboards aos 01:10 | Cortar com o argumento da Aula 18: a decisão é do `recall@k` medido no corpus da equipe, e o Lab 5 da semana é exatamente onde isso é feito. Registrar a pergunta para o canal da turma |
| **Tempo estourar no Bloco 1** (fusão gera muita pergunta) | 00:50 e ainda em RRF | Cortar o passo 6 da demo (variar o `k` do RRF) e o quadro de decisão do slide 6, que estão no plano por escrito; proteger métricas e modos de falha, que são pré-requisito do Lab 5 |
| **Injeção de prompt vira discussão de segurança** de 20 min | Perguntas sobre ataques aos 01:41 | Reconhecer o interesse e devolver para a Aula 26, que é inteira sobre isso; hoje a exigência é só reconhecer que documento recuperado é entrada não confiável |
| **Alunos sem equipe formada** na Aula 18 | Aluno pergunta sobre a Entrega 1 | Encaminhar na abertura, junto com a devolutiva dos rascunhos: equipes pendentes se resolvem antes do Lab 5, porque o corpus do lab pode ser o do projeto |

## 7. Artefatos produzidos

- Folha do exercício "medir à mão" preenchida em dupla: `recall@3`, `recall@5`, MRR e as duas frases de diagnóstico.
- Anotação pessoal do **quadro de decisão** consulta → estratégia (paráfrase, identificador, misto) e do fluxo de dois estágios com `k_ret` e `k_final`.
- Rascunho de proposta da Aula 18 devolvido com comentário escrito do instrutor — insumo direto da Entrega 1 na Aula 22.
- `codigo/demo-hibrido-reranking.py` disponível no repositório da disciplina, com a saída da execução da aula.
- Nenhum entregável avaliado nesta aula.

## 8. Desafio pós-aula

Não avaliado, e desenhado para que o Lab 5 comece já com material próprio.

1. **Escrever as consultas rotuladas.** Cada equipe escreve de 15 a 20 perguntas reais sobre o corpus escolhido na Aula 18 e, para cada uma, anota qual documento (ou seção) contém a resposta. Esse arquivo é o instrumento de medida do Lab 5 e do projeto — e escrevê-lo antes de ver o sistema funcionando evita o viés de escrever a pergunta que o sistema já acerta. Recomendação de composição: pelo menos um terço em paráfrase e pelo menos três com identificador, código ou nome próprio.
2. **Prever o resultado.** Para cinco dessas consultas, anotar antes de medir: denso, BM25 ou híbrido? A previsão escrita é o que transforma a medição do Lab 5 em aprendizado em vez de tabela.
3. **Leitura.** Nogueira & Cho, *Passage Re-ranking with BERT* (arXiv 1901.04085) — seções 1 e 3. **Pergunta dirigida:** o artigo reordena os 1000 primeiros resultados de um BM25; num sistema com 5 mil chunks e resposta em menos de um segundo, quantos candidatos você reordenaria, e o que decide esse número? Complementar, para quem quiser puxar o fio dos modos de falha: Liu et al., *Lost in the Middle* (arXiv 2307.03172), e Greshake et al., *Indirect Prompt Injection* (arXiv 2302.12173) — este segundo volta inteiro na Aula 26.

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. Os pesos são os da ementa e não são reinventados aqui: labs 30% (descartando a menor nota), prova 30% (Aula 17), projeto final 40% (Aulas 22, 26 e 30).

O que esta aula fixa como critério para o que vem:

- **Lab 5 (Aula 20), avaliado dentro dos 30% dos laboratórios.** O relatório de métricas exigido lá usa as definições desta aula: `recall@k` com `k` declarado, número de consultas do conjunto rotulado declarado, e a comparação antes/depois do reranking na mesma tabela.
- **Projeto final — item "rigor da avaliação quantitativa" (30% da rubrica do projeto).** Métrica *por camada* significa, para quem usar RAG, medir a recuperação separada da resposta. Um projeto que reporta só a qualidade final não atende ao requisito, mesmo funcionando bem na demo.
- **Declaração de uso de IA** obrigatória em toda entrega, com responsabilidade integral pelo código — qualquer entrega pode virar defesa oral.

Observável em sala, sem nota: ao fim do exercício, a dupla identifica corretamente a consulta em que o reranking não ajuda e explica por quê, sem usar a palavra "modelo" na explicação.
