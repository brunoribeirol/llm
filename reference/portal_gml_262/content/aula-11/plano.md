---
aula: 11
titulo: "Laboratório 3: Decodificação e prompting na prática"
modulo: "2 — Do Transformer ao LLM: escala e inferência"
tipo: laboratorio
semana: 6
duracao_min: 120
versao: v2
---

# Aula 11 — Laboratório 3: Decodificação e prompting na prática

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2 — §6-bis (laboratórios).** O roteiro prático **não foi reordenado**: a
> sequência dos cinco checkpoints é a que funciona no teclado. O que mudou é que cada checkpoint
> agora abre pelo **que a tela imprime quando está certo** — a linha `Checkpoint N OK` e as
> verificações que o teste fez — antes de dizer o que implementar. O apêndice é organizado **por
> checkpoint**, com três itens: a entropia e o tamanho do nucleus (CP1), o custo de uma resposta
> (CP3 e CP4), e quantos itens são necessários para uma diferença não ser ruído (CP2, CP4, CP5).
> Carga horária, numeração e objetivos inalterados. O notebook em `codigo/` **não muda**.

## 1. Objetivo da aula

Converter as quatro alavancas que a Aula 10 **afirmou** em medição com três eixos: qualidade, custo em tokens e latência. O aluno sai com um mini-harness reutilizável — a função que mede vira insumo do Lab 5, do Lab 8 e do projeto final — e com a experiência de escrever meia página escolhendo uma configuração **com número na mão**.

## 2. Resultados de aprendizagem

Ao final desta aula o estudante deve ser capaz de:

1. Implementar temperatura, `top-k` e `top-p` sobre uma distribuição de próximo token, aplicando a temperatura **no logit** e renormalizando após o truncamento.
2. Prever e verificar que o tamanho do nucleus **não encolhe** quando a temperatura sobe.
3. Separar erro de rótulo de resposta fora do espaço de rótulos, e dizer qual dos dois o few-shot resolve.
4. Quantificar o custo do chain-of-thought em tokens de saída por ponto de acurácia ganho — e interpretar corretamente o caso em que o ganho é nulo.
5. Construir uma tabela de comparação gerada por código, com mediana de três repetições e a dispersão ao lado, e dizer o que ela **não** permite concluir.
6. Escolher entre modelo local pequeno e modelo de API para um cenário dado, justificando com os três eixos medidos.

*(Idênticos aos da V1.)*

## 3. Teoria aplicada

Este é um laboratório: a teoria foi dada na Aula 10 e aqui ela é medida. O que segue são os **contratos de execução** do lab — e eles são conteúdo, porque decidem se o número que sai significa algo.

### Os três modos de execução, e por que existem três

O notebook roda em três backends, selecionados numa célula de configuração: **offline** (distribuições embutidas, determinístico, sem rede), **Ollama** (modelo local pequeno) e **API** (provedor com free tier). Todo resultado carrega o modo em que foi produzido — é o **campo de proveniência**, e ele é obrigatório no mini-relatório.

A razão de existirem três não é redundância: é que a aula precisa acontecer com a rede caindo, com a quota estourando e com a sala inteira conectada ao mesmo provedor. O modo offline garante que os CP1 e CP4 rodem em qualquer circunstância.

### Os cinco checkpoints, pelo que cada um imprime

| CP | Relógio | O que faz | **O que a tela imprime quando está certo** | Apêndice |
|---|---|---|---|---|
| 1 | 00:35–00:50 | temperatura, `top-k`, `top-p` e a grade 3×3 | `Checkpoint 1 OK` + as 5 verificações + 9 saídas | A.1 |
| 2 | 00:50–01:05 | classificação zero-shot × few-shot | `Checkpoint 2 OK` + 3 linhas × 2 métricas | A.3 |
| 3 | 01:15–01:27 | chain-of-thought em 10 problemas | 2 linhas + `tokens_por_ponto` (ou `null`) | A.2 |
| 4 | 01:27–01:40 | tabela qualidade × custo × latência | 4 linhas **geradas por código** | A.2 / A.3 |
| 5 | 01:40–01:50 | local × API | tabela comparativa + um parágrafo | A.3 |

**Entregável:** notebook executado + **meia página** com campo de proveniência.

### As três armadilhas silenciosas do CP1

O teste do Checkpoint 1 confere cinco coisas, e cada uma aponta para um erro que o Python aceita sem reclamar:

1. **A temperatura não muda o ranking** — ela age no logit e só reescala. Quem divide a *probabilidade* pela temperatura obtém algo que ainda soma 1 e está errado.
2. **Cada filtro devolve distribuição somando 1** — esquecer de renormalizar depois do corte produz uma "distribuição" que soma menos que 1 e amostra torto.
3. **Com `p = 0,9` sobre `(0,50 0,30 0,15 0,05)` sobram 3** — o token que **cruza** a linha entra. `>` onde precisa ser `≥` tira um token e ninguém percebe.
4. **Nucleus com `T = 2` ≥ nucleus com `T = 0,5`** — a verificação contraintuitiva, e ela **não é heurística**: é demonstrável.
5. **Greedy 3× idêntico, amostragem com 3 sementes diferente** — separa determinismo de aleatoriedade.

- **Fundamento:** o tamanho do nucleus é função não decrescente da temperatura. A entropia cresce estritamente com `T`, as somas acumuladas dos tokens mais prováveis caem, e a linha do `p` é empurrada para mais longe.
  → derivação completa: **Apêndice A.1** (slide 11). Os limites `T → 0` e `T → ∞` e o truncamento com renormalização estão em **A.1 e A.2 da Aula 10** e não se repetem aqui.

### O que o CP2 mede que a acurácia esconde

Duas colunas, não uma: **acurácia** e **fora do espaço de rótulos**. Errar o rótulo e responder em prosa livre dão a mesma acurácia e são dois problemas de engenharia diferentes — o primeiro se resolve com exemplos, o segundo com restrição de formato. O teste confere a identidade `acertos + erros + fora_do_espaço = 20`, que é o que impede a segunda coluna de desaparecer dentro da primeira.

- **Fundamento:** com 20 itens, cada item vale 5 pontos percentuais. Uma diferença de 5 pontos entre condições é **um comentário mudando de lado**. Temperatura 0 elimina o ruído de amostragem, **não** o ruído de amostra — e confundir os dois é o erro de método mais comum do lab.
  → o erro-padrão de uma proporção com `n = 20` e quantos itens precisariam mudar: **Apêndice A.3** (slide 13)

### O achado do CP3

Quando `delta_pontos ≤ 0`, o campo `tokens_por_ponto` vem **nulo de propósito**, com a leitura impressa junto: *o raciocínio custou tokens sem comprar nada nestes problemas, com este backend*. É resultado, não falha, e é o achado mais valioso do lab.

- **Fundamento:** o custo de uma resposta é a soma de duas parcelas com preços diferentes. O chain-of-thought inflaciona os tokens de **saída**; o few-shot inflaciona os de **entrada**. E `tokens_por_ponto` tem significado preciso: é o preço que um ponto percentual de acurácia teria de valer para o raciocínio se pagar.
  → derivação completa: **Apêndice A.2** (slide 12)

### As três exigências de método do CP4

Tabela **gerada por código**, nunca digitada. **Três repetições**, com mediana e a dispersão `mín–máx` ao lado. Contagem **exata** (`usage`) marcada como diferente de **estimada**.

- **Fundamento:** a coluna de latência é estatística de três amostras — daí a mediana, nunca a média. Se a dispersão de uma configuração cobre a diferença entre duas linhas, **a tabela não ordena nada**.
  → derivação completa: **Apêndice A.3** (slide 13)

### Grade temporal

| Início | Dur. | Bloco |
|---|---|---|
| 00:00 | 15 min | Setup: os três modos, a célula de configuração, o mapa dos cinco checkpoints pelo que cada um imprime |
| 00:15 | 20 min | Demonstração guiada: uma pergunta, seis decodificações, com os três eixos aparecendo na mesma tela |
| 00:35 | 30 min | **CP1** (00:35–00:50) e **CP2** (00:50–01:05) |
| 01:05 | 10 min | Intervalo |
| 01:15 | 35 min | **CP3** (01:15–01:27), **CP4** (01:27–01:40), **CP5** (01:40–01:50) |
| 01:50 | 10 min | Recolhimento: o mini-relatório, o prazo, e a ponte para a Aula 12 |

## 4. Demonstração guiada

**20 minutos, seis tratamentos sobre a mesma pergunta e o mesmo modelo.**

`greedy ×3` · `amostragem ×3` · varredura de `T` · `top_p` por cima de `T = 1.5` · instrumentação (tokens e segundos) · `zero-shot × few-shot`.

**Número que a demo produz.** Dois, e os dois voltam aos checkpoints. A **varredura de temperatura** mostra a incerteza subindo de forma contínua e monotônica, e é a evidência visual da verificação nº 4 do CP1 — que a turma vai encontrar como teste vinte minutos depois. E a **instrumentação**: tokens de entrada, tokens de saída e segundos aparecendo na mesma tela que o texto, que é o que estabelece o contrato de medição do CP4. Antes desta demo, "qualidade" é impressão; depois, é uma coluna ao lado de duas outras.

**Contingência:** rodar no backend mais robusto da sala. Se a rede cair no meio, **trocar para `offline` ao vivo e dizer isso em voz alta** — é a melhor propaganda possível do modo offline, e a turma vai precisar dele no CP5.

## 5. Hands-on

O hands-on é a aula. Cinco checkpoints, cada um abrindo pelo observável.

**Checkpoint 1 · 00:35–00:50 — Decodificação implementada e medida.**
Implementar `aplicar_temperatura`, `filtrar_top_k`, `filtrar_top_p` e `amostrar`; rodar o teste; preencher a grade `T ∈ {0,2 · 0,8 · 1,4}` × `top_p ∈ {0,5 · 0,9 · 1,0}`.
*Critério de conclusão observável:* a tela imprime `Checkpoint 1 OK` e a grade tem nove saídas.

**Checkpoint 2 · 00:50–01:05 — Few-shot e o colapso de formato.**
Três condições (zero-shot solto, zero-shot com rótulos declarados, few-shot com 4 exemplos) sobre 20 comentários rotulados, espaço fechado em `bug · dúvida · elogio · recurso`, temperatura 0.
*Critério de conclusão observável:* `Checkpoint 2 OK` mais a tabela de 3 linhas × 2 métricas, e uma frase dizendo **qual das duas colunas o few-shot mexeu mais**.

**Checkpoint 3 · 01:15–01:27 — Chain-of-thought e o preço do raciocínio.**
Os 10 problemas nas duas condições, formato final obrigatório `Resposta: <número>`, e a terceira coluna contando **falha de extração** separadamente.
*Critério de conclusão observável:* duas linhas de tabela mais a linha da divisão, com `tokens_por_ponto` preenchido ou `null` com a leitura impressa.

**Checkpoint 4 · 01:27–01:40 — A tabela dos três eixos.**
Quatro abordagens (zero-shot, few-shot, CoT, CoT + few-shot) com `tokens_in`, `tokens_out`, `contagem`, `latencia_mediana_s`, `dispersao_s`, `custo_1k_req`.
*Critério de conclusão observável:* existe uma tabela markdown **impressa pela função do notebook** — não digitada — com quatro linhas.

**Checkpoint 5 · 01:40–01:50 — Local × API.**
*Critério de conclusão observável:* tabela comparativa mais um parágrafo dizendo onde fica a fronteira entre os dois.

**Entregável:** notebook executado + meia página com **campo de proveniência** (qual modo, qual modelo, qual data). A meia página é a parte difícil, porque nela o aluno precisa escolher — e escolher com número na mão é o que a disciplina treina.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Rede cai** ou quota estoura com a sala conectada | 429 a partir do terceiro aluno | Modo `offline` na célula de configuração: CP1 e CP4 rodam integralmente sem rede. Trocar ao vivo na demo se acontecer ali — é propaganda do modo, não fracasso |
| Temperatura aplicada na **probabilidade** em vez do logit | Grade 3×3 com saídas quase idênticas | A pergunta que resolve metade dos casos, feita circulando: *"sua temperatura divide o logit ou a probabilidade?"* |
| `>` onde precisa ser `≥` na acumulada do `top-p` | Verificação 3 do teste falha | O teste já aponta: com `p = 0,9` sobre a distribuição dada, sobram **3** tokens. O token que cruza a linha entra |
| Aluno trava no CP1 e não chega ao CP3 | 00:48 e o teste ainda vermelho | Solução comentada liberada em 00:50 (CP1) e 01:05 (CP2). É rede de segurança, e dizer isso em voz alta evita que virem convite a desistir |
| **Casamento generoso** na normalização apaga a coluna 2 do CP2 | "Fora do espaço" dá zero em todas as condições | A função de normalização é estrita **de propósito**. Se alguém afrouxar, a coluna morre e o checkpoint perde o ponto |
| CoT sai **pior** e a turma lê como erro | `delta_pontos` negativo | Checar a extração antes de qualquer coisa: falha de extração entra no denominador e estraga a conta por razão alheia ao modelo. Se a extração está ok, é **achado** — tratar como achado na frente da sala |
| Tabela do CP4 digitada à mão | Números redondos demais | A função que monta já está pronta; o trabalho é chamá-la com os resultados guardados. Tabela digitada não é reproduzível e não conta |
| Uma execução só de latência | `dispersao_s` vazia | Três repetições é exigência, não sugestão. Uma execução mede um sorteio |

## 7. Artefatos produzidos

- Notebook executado com os cinco checkpoints verdes e a grade 3×3 preenchida.
- **A função que mede** — tokens, latência, custo — que é reutilizada no Lab 5, no Lab 8 e no projeto final. É o artefato mais durável do lab.
- A tabela dos três eixos, gerada por código.
- O mini-relatório de meia página, com campo de proveniência.

## 8. Desafio pós-aula

1. **Fechar a conta que ficou aberta.** Se o `tokens_por_ponto` do CP3 deu um número, quanto valeria um ponto de acurácia no seu caso de uso para o CoT se pagar? Se deu `null`, qual mudança no conjunto de problemas faria o CoT compensar? Responder com número.
2. **Rodar o CP4 num segundo backend** e comparar as duas tabelas. A ordenação das quatro abordagens se mantém? Se não se mantém, o que isso diz sobre conclusões tiradas de um único provedor?
3. **Leitura, com pergunta dirigida.** Brown et al., *GPT-3* (arXiv 2005.14165): o artigo mede desempenho em função do número de exemplos no prompt. Onde a curva satura, e o que a saturação sugere sobre o que o few-shot está de fato fazendo?

## 9. Critérios de avaliação

Este lab compõe os **30% de laboratórios** da ementa (média dos 8, descartando a menor nota). Entrega até uma semana após a aula.

| O que se avalia | Como |
|---|---|
| Os cinco checkpoints executados | `Checkpoint N OK` na tela para 1 e 2; tabelas geradas por código para 3, 4 e 5 |
| **Proveniência declarada** | Modo, modelo e data no mini-relatório. Sem isso, os números não são verificáveis e o item cai |
| Interpretação, não só execução | A meia página escolhe uma configuração e diz **o que a medição não permite concluir** |
| As três exigências de método do CP4 | Tabela gerada por código, três repetições com dispersão, contagem exata marcada como tal |

**Nota sobre a prova.** O conteúdo deste lab é cobrado na prova da Aula 17, cuja composição é diagnóstico e interpretação **42** · justificativa **40** · conceito aplicado **8** · derivação **10**. O CP3 e o CP4 são exatamente o formato das questões de interpretação: uma tabela de resultados reais, e a pergunta é o que ela **permite** e o que **não permite** afirmar. Quem tratou o `tokens_por_ponto` nulo como falha em vez de achado erra a mesma coisa na prova.

## Apêndice matemático — índice

Três itens, slides 11 a 13 do deck, **organizados por checkpoint** conforme a §6-bis. Material de estudo e consulta, autossuficiente.

| Item | O que estabelece | Checkpoint |
|---|---|---|
| **A.1** | A entropia da distribuição como medida de incerteza, com a conta e os números desta distribuição; e a **demonstração de que o tamanho do nucleus não pode encolher quando `T` sobe** — a entropia cresce estritamente com `T`, as acumuladas dos mais prováveis caem, a linha do `p` é empurrada. É a verificação nº 4 do teste, que é contraintuitiva e não é heurística. | **CP1** |
| **A.2** | O custo de uma resposta como soma de duas parcelas com preços diferentes; por que o chain-of-thought inflaciona os tokens de saída e o few-shot os de entrada; o significado preciso de `tokens_por_ponto` (o preço que um ponto de acurácia teria de valer); e a condição exata em que o CoT compensa. Mais a conta de custo por mil requisições do CP4. | **CP3**, CP4 |
| **A.3** | Quantos itens são necessários para uma diferença não ser ruído: a resolução de um conjunto de 20 (cada item vale 5 pontos percentuais), o erro-padrão de uma proporção com `n = 20`, e quantos itens precisariam mudar de lado para a diferença ser distinguível do acaso. Mais a razão de três repetições com mediana e o que a dispersão licencia afirmar. | **CP2**, CP4, CP5 |

**O fio que atravessa o curso, e onde este item entra.** O A.3 deste lab é o **segundo de seis elos** de um mesmo argumento — que uma medição sem tamanho de amostra declarado não sustenta conclusão. Vale conhecer os seis, porque a ideia cresce de uma semente até uma decisão de produto:

| Elo | Onde | O que acrescenta |
|---|---|---|
| 1 | **A.5 do Lab 2** (Aula 9) | uma única semente não permite concluir nada sobre um treino |
| 2 | **A.3 deste lab** (Aula 11) | tamanho de amostra em 20 itens, e dispersão de latência em 3 repetições |
| 3 | **A.3 do Lab 4** (Aula 14) | o caso em que **nenhum** resultado possível seria significativo — e o Wald devolvendo intervalo fora de `[0,1]` |
| 4 | **A.3 do Lab 5** (Aula 20) | quantas consultas rotuladas a diferença de reranking exigiria |
| 5 | **Aula 27**, slide 5 | o argumento no nível conceitual, com o sintoma de equipe: `0,71 → 0,78` em 20 casos era ruído |
| 6 | **A.5 do Lab 8** (Aula 28) | a conta paga: intervalo de Wilson e teste de McNemar sobre o conjunto de teste do projeto |

O elo 3 é o mais desconfortável dos seis e por isso o mais útil: ele mostra um checkpoint em que a aritmética garante, **de antemão**, que a medição não pode ser conclusiva em acurácia. Saber isso antes de medir é o que distingue quem reporta um número de quem reporta um número com o que ele não prova.
