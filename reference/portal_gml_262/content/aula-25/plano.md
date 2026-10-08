---
aula: 25
titulo: "Laboratório 7: Construindo um agente autônomo"
modulo: "5 — RAG, Ferramentas e Agentes de IA"
tipo: laboratorio
semana: 13
duracao_min: 120
versao: v2
---

# Aula 25 — Laboratório 7: Construindo um agente autônomo

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2 — §6-bis (laboratórios).** O roteiro prático **não foi reordenado**: os cinco
> checkpoints estão na ordem que funciona no teclado. O que mudou é que cada checkpoint abre pelo
> **que a tela imprime quando está certo** — a linha `Checkpoint N OK` com o que o teste conferiu, ou
> os arquivos que precisam existir em disco — antes de dizer o que implementar. O apêndice é
> organizado **por checkpoint**, com três itens: a contabilidade da trajetória com os números que as
> três trajetórias gravadas **de fato produziram** (CP4), por que o crescimento do contexto é
> superlinear no custo (CP2 e CP4), e as três condições de parada com o que cada uma protege (CP2).
> A derivação do custo acumulado do laço **não é refeita aqui** — ela está em A.1 da Aula 23, e o
> fluxo aponta para lá. Carga horária, numeração e objetivos inalterados. O notebook em `codigo/`
> **não muda**.

## 1. Objetivo da aula

Transformar as cinco peças da Aula 23 — modelo, ferramentas, loop, objetivo, critério de parada — em um agente ReAct escrito na mão, com três ferramentas reais (busca no acervo do Lab 5, calculadora e busca simulada), trajetória registrada e custo medido por passo; e só depois reimplementá-lo num framework, para que o aluno saiba exatamente o que está delegando quando adota a conveniência.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Escrever** um prompt de sistema que carrega objetivo, catálogo de ferramentas e contrato de formato, e **justificar** por que a proibição de o modelo emitir `Observation:` é parte do contrato.
2. **Implementar** o parsing de ação ReAct em texto puro de modo que formato inválido volte como observação em vez de levantar exceção, e **demonstrar** com teste que o parser rejeita ação malformada.
3. **Construir** o loop com as três paradas — orçamento de passos, resposta final sustentada por observação e detecção de repetição sem progresso — e **provocar** cada uma delas com um defeito roteirado.
4. **Reaproveitar** o índice construído no Lab 5 (Aula 20) como ferramenta do agente, trocando o corpus embutido pelo próprio `chunks.json` sem alterar a assinatura da ferramenta.
5. **Registrar** a trajetória completa em JSON — pensamento, ação, argumentos, observação, decisão e tokens por passo — e **analisar** uma execução por escrito, apontando onde o agente acertou, onde vacilou e quanto custou.
6. **Comparar** o loop escrito na mão com a mesma lógica em um framework de grafo de estado, **nomeando** qual peça o framework assume e qual continua sendo do programador.

*(Idênticos aos da V1.)*

## 3. Teoria aplicada

Este é um lab: a teoria foi dada nas Aulas 21, 23 e 24. O que segue são os conceitos que o código materializa, e o erro silencioso que cada um produz quando é mal entendido. A grade de laboratório da §3 do contrato organiza os blocos.

### Os cinco checkpoints, pelo que cada um imprime

| CP | Relógio | O que faz | **O que a tela imprime quando está certo** | Apêndice |
|---|---|---|---|---|
| 1 | 00:35–00:48 | contrato, parser, despacho | `Checkpoint 1 OK` — as três partes do prompt e os quatro casos malformados | — |
| 2 | 00:48–01:05 | o loop, a memória, as três paradas | `Checkpoint 2 OK` — sete situações, incluindo a observação **não** devolvida | **A.3** · A.2 |
| 3 | 01:15–01:24 | a base do Lab 5 como ferramenta | `Checkpoint 3 OK` + a linha da fonte do corpus nomeando o `chunks.json` do aluno | — |
| 4 | 01:24–01:38 | trajetória em JSON, custo, análise | **três arquivos** `trajetoria_p1..p3.json` + a tabela de custo com o acumulado crescendo | **A.1 · A.2** |
| 5 | 01:38–01:50 | o mesmo agente num framework | a tabela das 3 perguntas nas 2 arquiteturas + as 3 respostas escritas | — |

**Entregável:** notebook executado + as três trajetórias + a tabela de custo + a **análise escrita de uma trajetória** (o item que separa as notas) + a tabela do CP5.

### Bloco 1 (00:35–01:05) — O contrato de formato e o loop

**Conceito 1 — O prompt de sistema é o contrato, e ele tem exatamente três partes.**
Objetivo, catálogo de ferramentas e formato da ação — e o formato inclui como encerrar. Nada mais entra ali. O catálogo não é documentação para humano: é o texto que o modelo lê para escolher a ferramenta, e por isso a descrição de ferramenta **é prompt**, exatamente como no Lab 6.
*Analogia do instrutor:* é a interface de um plugin. Se a especificação de formato é ambígua, o plugin roda e devolve lixo bem formatado.
*Erro conceitual comum:* pôr conhecimento de domínio no prompt de sistema. Cada frase de domínio ali é uma frase que o agente não vai buscar na ferramenta — e o objetivo do lab é justamente que ele busque.
*Nota de custo, e ela é do apêndice:* o prompt de sistema é reenviado em **toda** chamada. Nas trajetórias de referência ele responde por mais de três quartos dos tokens de entrada, e é por isso que "cada frase a mais no sistema" é uma decisão de custo (ver **A.2**).

**Conceito 2 — A proibição de o modelo escrever `Observation:` não é detalhe de estilo.**
Em ReAct de texto puro, se o modelo não é interrompido, ele continua a completar o padrão e **inventa a própria observação**. A partir daí o loop raciocina sobre um resultado que ferramenta nenhuma produziu, e a resposta final vem com aparência de evidência. Duas defesas: a instrução explícita no prompt e a sequência de parada (`stop`) na chamada da API.
*Analogia:* é o aluno que preenche o gabarito da prova e também a folha de correção.
*Erro conceitual comum:* achar que o `stop` é otimização de custo. Ele é correção: sem ele, a observação passa a ser gerada pelo próprio modelo.

**Conceito 3 — Parsing que aceita ação malformada é o primeiro erro silencioso do lab.**
Um parser permissivo — que aceita `Action:` sem `Action Input:`, ou que faz `eval` de um JSON quebrado, ou que casa o nome da ferramenta em qualquer lugar do texto — produz chamada com argumento vazio, e a ferramenta devolve erro genérico. O agente então "conserta" o argumento por tentativa e erro, gastando passos, e o diagnóstico fica impossível: a trajetória mostra tentativas, não o defeito.
*Erro conceitual comum:* fazer o parser levantar exceção quando o formato está errado. Exceção derruba a trajetória inteira; o certo é devolver o erro **como observação**, porque erro de formato é informação que o modelo consegue corrigir na volta seguinte. O `teste_checkpoint_1` cobre os quatro casos: prosa sem formato, JSON quebrado, `Action Input` ausente e nome de ferramenta com cerca de código.

**Conceito 4 — A memória de curto prazo é a lista de mensagens, e a observação tem de voltar para ela.**
Registrar a observação na trajetória e esquecer de anexá-la a `mensagens` é o erro mais bonito do lab: nada quebra, nenhum teste de formato falha, e o agente **esquece o que a ferramenta respondeu**. O sintoma é a mesma ação repetida com o mesmo argumento, volta após volta, porque do ponto de vista do modelo a pergunta continua sem resposta.
*Analogia:* é anotar o resultado do exame no prontuário e mandar o paciente repetir o exame, porque quem lê é outra pessoa.
*Erro conceitual comum:* confundir os dois registros. `mensagens` é a memória que **o modelo lê**; `trajetoria` é o registro que **o humano audita** (Aula 26). Os dois existem, e servem a leitores diferentes.

**Conceito 5 — O limite de passos é decisão de produto, não defensividade.**
`max_passos` fixa o teto de custo e o teto de espera do usuário. Sem ele, um agente que não converge não trava: ele cobra. E, como o prompt cresce a cada volta, o custo em tokens não é linear nos passos — a trajetória inteira é reenviada, e o último passo é o mais caro de todos. É a conta da Aula 23, agora com número na tela.
*Observável que motiva:* o `max_passos = 6` do notebook contra a distribuição observada nas três perguntas de referência — 3, 2 e 2 passos. O teto é o dobro do máximo observado, que é a regra deste conceito aplicada aos dados do próprio lab.
*Erro conceitual comum:* dimensionar `max_passos` pelo pior caso imaginado. O número certo vem da distribuição observada: rode as perguntas típicas, veja quantos passos elas gastam, e ponha o teto um pouco acima — e trate o estouro como caso a investigar, não como falha do usuário.

- **Fundamento:** o custo em tokens enviados numa trajetória de `n` voltas tem um termo linear (o prompt fixo, reenviado `n` vezes) e um termo **quadrático** (a trajetória acumulada, reenviada a cada volta). O `max_passos` é a inversão dessa soma contra um teto de orçamento.
  → a derivação completa está em **A.1 da Aula 23** e não é refeita aqui; o que este lab acrescenta é a **medição**: os `p₀` e `d` reais das três trajetórias gravadas, em qual dos dois regimes este agente vive, e qual otimização compensa nesse regime: **Apêndice A.2** (slide 12)

**Conceito 6 — Parada que nunca dispara e parada que dispara cedo demais.**
Três paradas convivem no loop deste lab, e cada uma cobre um defeito diferente. **Orçamento** pega o loop que não converge. **Resposta final sustentada por observação** pega a parada precoce — a condição não é "o modelo escreveu `Final Answer`", é "o modelo escreveu `Final Answer` **e** existe pelo menos uma observação de ferramenta executada na trajetória". **Detecção de repetição** pega o agente preso: mesma ação, mesmo argumento, duas voltas seguidas. Uma parada que nunca dispara é indistinguível de não ter parada — e é por isso que o teste liga um defeito roteirado para cada uma delas.
*Erro conceitual comum:* contar como observação a mensagem que o próprio loop injetou (a cobrança de "responda com fundamento"). Se ela conta, a parada precoce passa a se autoautorizar na volta seguinte — o contador tem de somar só o que veio de ferramenta **executada**.

- **Fundamento:** as três paradas não são intercambiáveis nem redundantes. Só uma delas garante **terminação** para qualquer comportamento do modelo — o orçamento, porque é um contador que decresce independentemente do que o modelo faça. As outras duas são saídas antecipadas: uma protege a **qualidade** da resposta, a outra protege o **gasto** quando o agente está preso. E a segunda tem uma condição de correção precisa: o contador de observações tem de excluir as mensagens que o próprio loop injetou, senão a guarda autoriza exatamente o que ela existe para bloquear.
  → o enunciado formal de cada parada, o que cada uma protege, o que acontece na trajetória quando cada uma é removida, e a demonstração de que a variante permissiva do contador se autoautoriza: **Apêndice A.3** (slide 13)

### Bloco 2 (01:15–01:50) — A base do Lab 5, a trajetória e o framework

**Conceito 7 — A base do Lab 5 vira uma das ferramentas, e a assinatura não muda.**
Na Aula 20 o acervo era o assunto: chunking, embedding, recuperação híbrida, recall medido. Aqui ele é `buscar_regulamento(termo, k)` — uma linha do catálogo. O gancho é literal: se existir um `chunks.json` na pasta do lab (o arquivo que o notebook do Lab 5 gravou em `lab05_saida/`), o módulo `corpus_regulamento.py` o usa em lugar do corpus embutido, e o agente passa a consultar **a base do próprio aluno**. Quem trocar o corpo da busca pelo pipeline híbrido do Lab 5 também não muda nada para quem chama.
*Analogia:* é a diferença entre construir o motor e instalar o motor. O Lab 5 construiu; hoje ele é peça.
*Erro conceitual comum:* achar que uma base boa resolve o agente. A qualidade da recuperação limita o teto do agente e não conserta nenhuma das cinco peças — um agente com base excelente e parada mal projetada continua respondendo sem fundamento.
*Nota de custo:* base com chunks longos infla a observação, e a observação é o termo que multiplica o crescimento quadrático. Trocar o corpus embutido por uma base de chunks grandes muda o custo por passo de forma mensurável — e isso é achado para a análise do CP4, não bug (ver **A.2**).

**Conceito 8 — Registrar a resposta final não é registrar a trajetória.**
A falha de um agente pode estar em qualquer etapa: percepção da pergunta, escolha de ferramenta, argumento passado, interpretação da observação, decisão de parar. A resposta final é o último elo, e ela é fluente independentemente de onde a coisa quebrou. Por isso a trajetória gravada carrega, por passo: pensamento, ação, argumentos, observação, erro de formato se houve, o texto cru do modelo e os tokens de entrada e de saída.
*Erro conceitual comum:* logar só o que "interessa" e descartar o texto cru do modelo. É exatamente no texto cru que se vê que o modelo tentou emitir `Observation:`, ou que escreveu duas ações no mesmo turno.

**Conceito 9 — Custo por passo: onde o dinheiro sai.**
A tabela do Checkpoint 4 tem uma coluna por passo com tokens de entrada, tokens de saída e o acumulado. Dois padrões aparecem sempre: o prompt de sistema é a maior parcela **fixa**, e os tokens de entrada crescem monotonicamente porque a trajetória é reenviada. Daí duas otimizações honestas e baratas: truncar o texto integral devolvido pela ferramenta ao que basta para a citação, e encurtar o catálogo de ferramentas ao mínimo que preserve a escolha correta — que é uma mudança de prompt e, portanto, precisa ser medida.
*Observável que motiva:* nas três trajetórias de referência, **94% de todos os tokens** são de entrada. O modelo escreve pouco e lê muito.
*Erro conceitual comum:* somar os tokens de saída e concluir que a geração é o custo. Em agente, quase todo o custo é **entrada**.

- **Fundamento:** "custo do agente" não é um número: é uma contabilidade com três eixos — passos, tokens de entrada e saída acumulados, e custo por **tarefa resolvida**. O terceiro exige uma decisão de definição, porque o denominador depende de o que conta como tarefa resolvida — e declarar uma recusa honesta como resolução ou como falha muda o número e muda o incentivo.
  → a contabilidade completa das três trajetórias gravadas, número por número, com o custo por tarefa resolvida nos dois denominadores possíveis e o que a dispersão entre as três esconde: **Apêndice A.1** (slide 11)

**Conceito 10 — O modo offline serve para depurar o loop, não para avaliar o agente.**
O lab roda sem rede: sem `API_KEY`, `llm.py` cai num simulador roteirado determinístico com semente fixa. Ele responde no formato ReAct segundo uma política escrita à mão, sempre igual, e existe para que a sala funcione sem internet e para que os testes sejam reprodutíveis. Ele **não** mede capacidade de modelo nenhum. Toda conclusão do tipo "o agente escolheu bem a ferramenta" só vale no modo API; no modo offline o que se afere é o comportamento do **loop**.
*Erro conceitual comum:* comparar duas versões do prompt no modo offline e concluir que uma é melhor. O simulador não reage a prompt — a comparação de prompt exige chave.
*Consequência para o apêndice:* os números de **A.1** vêm do modo `simulador-roteirado(semente=25)`, e isso está declarado lá. Eles são exatos e reprodutíveis como contabilidade de **loop**; eles não são medida de modelo.

**Conceito 11 — Framework: controle × conveniência, com a comparação controlada.**
O Checkpoint 5 refaz o mesmo agente num grafo de estado. Para a comparação ser honesta, três coisas ficam idênticas: mesmo modelo, mesmas ferramentas, mesmo prompt de sistema. O que muda é quem guarda o estado e quem decide a próxima aresta. O que o framework entrega: estado declarado, roteamento explícito, pontos de interrupção e retentativa padronizada. O que ele **não** entrega: validação de argumento, tratamento de erro de ferramenta e critério de parada de domínio — isso continua sendo escrito à mão dentro dos nós.
*Erro conceitual comum:* medir a diferença em linhas de código. A pergunta que decide é a do Conceito 11 da Aula 24: eu consigo ler a trajetória inteira que esse framework produziu? Se não consigo, ele não serve para um sistema que eu vou avaliar.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 15 min | Setup do ambiente + contexto | Recap da Aula 24 (os quatro padrões, o teste de três perguntas, "princípios antes de ferramentas"); abrir o notebook e os três módulos auxiliares; o aviso do modo offline (simulador roteirado, semente 25 — depura o loop, não avalia o agente); os números do lab (3 ferramentas, `max_passos=6`, 3 perguntas de referência, zero dependência para os CP1–CP4); o mapa dos cinco checkpoints **pelo que cada um imprime** e o entregável |
| 00:15 | 20 min | Demonstração guiada (live coding) | O prompt de sistema escrito na frente da turma com as três partes; `parsear_acao` construída caso a caso contra quatro entradas ruins; a primeira volta do loop feita à mão em três linhas de REPL, com a observação anexada às mensagens; a demonstração para de propósito antes do `while` |
| 00:35 | 30 min | Checkpoints 1–2 (aluno executando) | CP1 (00:35–00:48): `SISTEMA`, `parsear_acao`, `executar` e o teste com as quatro entradas malformadas; CP2 (00:48–01:05): `loop_react` com a memória, a observação devolvida ao contexto e as três paradas, provocadas pelos defeitos roteirados |
| 01:05 | 10 min | Intervalo | — |
| 01:15 | 35 min | Checkpoints 3–5 + extensões | CP3 (01:15–01:24): plugar o `chunks.json` do Lab 5 e conferir a fonte do corpus; CP4 (01:24–01:38): gravar a trajetória em JSON, montar a tabela de custo por passo e escrever a análise de uma trajetória; CP5 (01:38–01:50): o mesmo agente em grafo de estado e a tabela de comparação |
| 01:50 | 10 min | Recolhimento | O que entregar (notebook executado, três trajetórias em JSON, tabela de custo, análise escrita de uma trajetória, tabela do CP5, respostas às questões-guia, declaração de uso de IA), prazo de uma semana, critério; ponte para a Aula 26 e aviso da Entrega 2 |

## 4. Demonstração guiada

**Live coding "o contrato e o parser" — 20 min, offline, sem dependência nenhuma.**

O instrutor escreve, em células novas, o prompt de sistema e o parser, e executa uma única volta do loop à mão. Nada disso depende de rede: o modelo é o simulador roteirado de `llm.py`. A demonstração termina deliberadamente **antes** do `while` — o loop é o Checkpoint 2.

Passos em alto nível:

1. Abrir `ferramentas.py` e imprimir `catalogo_em_texto()`: mostrar que o catálogo que o modelo lê são três linhas de texto, e que mudar uma palavra ali muda a escolha do modelo.
2. Escrever `SISTEMA` na tela, nomeando cada parte em voz alta: objetivo, catálogo interpolado, formato para agir, formato para encerrar, e as três regras (uma ação por vez, nunca escrever `Observation:`, não responder sem observação que sustente).
3. Chamar `llm.chamar_modelo` com o sistema e a pergunta do prazo de trancamento, e imprimir o texto cru devolvido. Ler as três linhas — `Thought:`, `Action:`, `Action Input:` — como um protocolo, não como prosa.
4. Escrever `parsear_acao` incrementalmente, testando contra quatro entradas na ordem: ação bem formada, prosa sem formato, `Action Input` com JSON quebrado, e nome de ferramenta entre cercas de código. Cada caso acrescenta uma linha à função.
5. Mostrar o que a função devolve em cada caso: sempre o mesmo dicionário, com `erro` preenchido em vez de exceção levantada. Cravar: erro de formato é observação, não crash.
6. Despachar a ação parseada com `executar` e imprimir a observação — o dicionário que a ferramenta devolveu.
7. Anexar a observação a `mensagens` como `Observation: {...}` e chamar o modelo de novo, na mão. A segunda resposta já é outra ação. Este é o loop, feito uma vez, sem `while`.
8. Comentar a linha do `append` da observação e repetir a chamada: o modelo emite **a mesma ação de novo**. Nomear o sintoma na hora — é o erro silencioso do Conceito 4, e é o que o Checkpoint 2 vai testar.
9. Parar aqui. O `while`, as três paradas e o orçamento são do aluno.

**Número que a demo produz.** Dois números pequenos, e os dois voltam no Checkpoint 4. O primeiro é o **tamanho da primeira chamada**: o `usage` (ou a estimativa impressa) da chamada que só tem sistema mais pergunta. Nas trajetórias de referência esse número fica entre **533 e 549 tokens de entrada**, e ele é o piso de custo de qualquer pergunta feita a este agente — o preço de existir, antes de o agente fazer nada. O segundo é o **tamanho da segunda chamada**, depois da observação anexada: nas referências ele sobe para 630 a 772, um acréscimo de 97 a 223 tokens dependendo de qual ferramenta respondeu. Os dois números na mesma tela estabelecem o fato central do Checkpoint 4 antes de o aluno escrever a tabela: a entrada cresce, e o quanto ela cresce é decidido pelo tamanho da observação. A demo tem ainda um observável qualitativo insubstituível: com o `append` da observação comentado, a segunda chamada devolve **a mesma ação, com o mesmo argumento** — o erro silencioso acontecendo na tela.

Insumos preparados na véspera: o notebook rodado de ponta a ponta nos dois modos (offline e, se houver chave, API), com os tempos e os números de tokens anotados; a saída dos quatro defeitos roteirados salva em texto, para o caso de a projeção falhar; `chunks.json` do Lab 5 do instrutor copiado para a pasta, para demonstrar o Checkpoint 3 com base real.

## 5. Hands-on

Cinco checkpoints, cada um abrindo pelo observável. O aluno trabalha no próprio notebook; o instrutor circula olhando tela.

**Checkpoint 1 · 00:35–00:48 — O contrato de formato, o parser e o despacho.**
Escrever `SISTEMA` com as três partes e as três regras; implementar `parsear_acao` devolvendo sempre `{pensamento, acao, argumentos, resposta_final, erro}` sem levantar exceção; implementar `executar`, que rejeita ferramenta desconhecida e argumento inválido como dicionário de erro.
*Critério de conclusão observável:* a célula `teste_checkpoint_1()` imprime `Checkpoint 1 OK`. O teste conferiu: as três partes do prompt (inclusive a proibição explícita de `Observation:`), o caminho feliz de ação e o de resposta final, os quatro casos malformados — prosa sem formato, JSON quebrado, `Action Input` ausente, nome de ferramenta com cerca de código —, e no despacho a ferramenta inexistente e o argumento inválido voltando como dicionário de erro em vez de exceção.

**Checkpoint 2 · 00:48–01:05 — O loop, a memória e as três paradas.**
Implementar `loop_react(pergunta, max_passos=6)`: montar `mensagens` com sistema e pergunta, chamar o modelo, acumular custo, parsear, registrar o passo na trajetória, executar a ferramenta, **anexar a observação a `mensagens`**, e implementar as três paradas — orçamento, resposta final com observação de ferramenta executada, repetição de assinatura.
*Critério de conclusão observável:* a célula `teste_checkpoint_2()` imprime `Checkpoint 2 OK`. O teste cobriu sete situações: duas ferramentas em sequência com citação e conta certa; uma ferramenta bastando; encerramento honesto quando o acervo não tem a resposta; repetição abortando; orçamento segurando antes do detector; formato inválido voltando como observação e o loop se recuperando; e o modo `devolver_observacao=False`, em que o agente esquece a observação e a trajetória termina em repetição — o erro silencioso do Conceito 4, exposto por teste.

**Checkpoint 3 · 01:15–01:24 — A base do Lab 5 como ferramenta.**
Copiar o `chunks.json` gerado no Lab 5 (Aula 20) para a pasta do lab e reexecutar a célula de setup; conferir que `corpus_regulamento.FONTE_DO_CORPUS` passou a apontar para a base do aluno; rodar o agente numa pergunta que só o acervo responde.
*Critério de conclusão observável:* a célula `teste_checkpoint_3()` imprime `Checkpoint 3 OK`, a linha da fonte do corpus nomeia o `chunks.json` do aluno com a contagem de chunks (ou, na falta dele, imprime o aviso explícito de corpus embutido), e a trajetória mostra ao menos um passo `buscar_regulamento` com `achados` não vazio sustentando a resposta.

**Checkpoint 4 · 01:24–01:38 — Registrar e analisar a trajetória.**
Implementar `resumo_de_custo` (tabela passo · ação · tokens de entrada · tokens de saída · acumulado) e `registrar_trajetoria` (JSON completo em `lab07_saida/`); rodar as três perguntas de referência, gravar as três trajetórias e escrever, em célula de markdown, a **análise de uma delas** em quatro parágrafos: onde acertou, onde vacilou, quanto custou, o que isso muda no projeto final.
*Critério de conclusão observável:* três arquivos `trajetoria_p1.json`, `trajetoria_p2.json` e `trajetoria_p3.json` em disco, cada um com todos os campos por passo e com o bloco `custo` (`chamadas`, `tokens_entrada_total`, `tokens_saida_total`, `tokens_total`); a tabela de custo impressa com a coluna do acumulado **estritamente crescente**; e a análise escrita nomeando **em que etapa** o agente vacilou (percepção, escolha de ferramenta, argumento, interpretação da observação ou parada) — não "errou a resposta".

**Checkpoint 5 · 01:38–01:50 — O mesmo agente num framework.**
Reimplementar o loop como grafo de estado (nó do modelo, nó de ferramenta, aresta condicional com o critério de parada), mantendo idênticos o modelo, as ferramentas e o prompt; rodar as três perguntas e preencher a tabela de comparação; responder por escrito às três perguntas do notebook.
*Critério de conclusão observável:* tabela com as três perguntas nas duas arquiteturas (chamadas, tokens, parada) e as três respostas escritas — qual peça o framework assumiu, qual continuou sendo sua, e onde se lê a trajetória completa de uma execução no framework. **Sem rede o checkpoint continua entregável:** o gabarito imprime a instrução, e o entregável é a tabela de referência do instrutor mais as três respostas fundamentadas na leitura do código dos três nós.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Sala sem rede** ou free tier esgotado | Nenhuma chave funciona; `getpass` vazio | O lab foi desenhado para isso: sem `API_KEY`, `llm.py` cai no simulador roteirado determinístico (semente 25) e os CP1–CP4 rodam inteiros, com testes reprodutíveis. O aviso no topo do notebook diz que o simulado depura o loop e **não** avalia o agente |
| **Aluno sem o `chunks.json` do Lab 5** (faltou, perdeu, mudou de máquina) | `FONTE_DO_CORPUS` diz "corpus embutido" | O corpus embutido fictício tem oito dispositivos e fecha os CP1, CP2, CP4 e CP5. O CP3 é entregável com o embutido **declarando isso no notebook**; quem tiver o arquivo em nuvem baixa no intervalo |
| **`langgraph` não instala** (sem rede, conflito de versão) | `ImportError` no CP5 | O gabarito detecta a ausência, imprime a instrução e encerra com código 0. O entregável do CP5 passa a ser a tabela de referência do instrutor mais as três respostas escritas, feitas com a leitura dos três nós |
| **Agente entra em laço** na máquina de alguém com chave de API | Passos se repetindo, custo subindo | `max_passos=6` é o teto padrão e o detector de repetição aborta em duas repetições de assinatura. Se alguém elevou o teto para "ver acontecer", o roteiro manda voltar para 6 antes de gravar a trajetória — e **A.3** tem o número de quanto custaria não abortar |
| **Modelo da API não respeita o formato** ReAct em texto puro | `erro` de formato em todos os passos | O erro volta como observação e o loop se recupera na volta seguinte — é o comportamento projetado. Se persistir por três passos, trocar o modelo pela alternativa anotada na célula de configuração, ou seguir no simulador e dizer isso na análise |
| **Turma em ritmos muito diferentes** | Metade ainda no CP1 aos 00:48 | CP1 e CP2 têm célula de solução comentada que o instrutor libera aos 00:48 e 01:05 — ninguém trava antes do CP4, que é o coração do entregável. Quem termina antes recebe a extensão do §8 |
| **Erro silencioso da observação não devolvida** | Todos os testes de formato passam e o agente repete a mesma ação | É o caso que o `teste_checkpoint_2` provoca de propósito com `devolver_observacao=False`; o roteiro manda o aluno comparar as duas trajetórias em vez de mexer no prompt |
| **Confusão entre `mensagens` e `trajetoria`** | Aluno anexa a trajetória inteira ao contexto do modelo | Nomear os dois leitores em voz alta — `mensagens` é lido pelo modelo, `trajetoria` é lida por humano na Aula 26 — e apontar as duas estruturas lado a lado na tela |
| **Tabela de custo com acumulado não crescente** | A coluna `acum` cai em algum passo | Não é ruído: é defeito de contabilidade. Ou o acumulado está sendo reiniciado, ou os tokens do passo estão sendo sobrescritos em vez de somados. O crescimento monotônico da entrada é uma **consequência** do reenvio da trajetória (**A.2**), não um resultado empírico |

## 7. Artefatos produzidos

- `lab-07-agente-autonomo.ipynb` executado, com as saídas visíveis: `Checkpoint 1 OK` a `Checkpoint 4 OK`, as trajetórias impressas passo a passo e a tabela de custo.
- **Três trajetórias em JSON** em `lab07_saida/` (`trajetoria_p1.json`, `p2`, `p3`), cada uma com pensamento, ação, argumentos, observação, texto cru do modelo e tokens por passo.
- **Análise escrita de uma trajetória** — quatro parágrafos: onde acertou, onde vacilou (nomeando a etapa), quanto custou e o que muda no projeto final.
- **Tabela de custo por passo** do Checkpoint 4 e **tabela de comparação** do Checkpoint 5 (loop na mão × framework).
- Respostas às **cinco questões-guia** em células de markdown do próprio notebook.
- **Declaração de uso de IA** — quais ferramentas, para quê, em duas linhas.
- Um agente ReAct que é do aluno e que serve de esqueleto para o projeto final — e a base do Lab 5 agora integrada como ferramenta dele.

## 8. Desafio pós-aula

**Este lab é o entregável avaliado da semana.** Prazo: uma semana após a aula. O conteúdo da entrega está no §7. Quem não terminou o CP5 em sala termina em casa; os checkpoints 1 a 4 são o núcleo obrigatório, e a análise escrita do CP4 é o item que mais pesa.

Extensões opcionais, não avaliadas, na ordem de proveito:

1. **Uma quarta ferramenta que falha de propósito.** Acrescentar ao registro uma ferramenta que devolve erro em uma de cada duas chamadas e observar o que o agente faz: ele lê o erro e corrige, ou repete? Registrar as duas trajetórias e comparar. Isso antecipa metade da Aula 26.
2. **Medir o efeito de uma descrição de ferramenta.** Encurtar a descrição de `calcular` para "faz contas" e rodar as três perguntas **com chave de API** — no simulador não há efeito, e saber disso é parte do exercício. Reportar quantos passos e quantos tokens a mudança custou.
3. **Truncar a observação.** Limitar o texto do dispositivo devolvido a 300 caracteres e medir a economia em tokens de entrada no passo final, verificando se a citação sobreviveu. Antes de rodar: prever a economia usando a conta de **A.2**, e depois comparar a previsão com o medido. Se a previsão errar, o `d` estimado estava errado — e descobrir isso é o exercício.
4. **Refazer a conta do orçamento com os seus números.** Com o `p₀` e o `d` medidos na sua trajetória, resolver a desigualdade de **A.2** e responder: o `max_passos = 6` está apertado ou frouxo para o seu agente, e qual das duas otimizações do Conceito 9 compensa mais no regime em que ele vive?

Leitura de apoio: Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models* (arXiv 2210.03629) — reler a seção do formato agora que o parser é seu, e conferir quantas das decisões do artigo você tomou de forma diferente. **Pergunta dirigida:** no seu loop, qual das três paradas disparou em cada uma das três perguntas de referência, e o que aconteceria se você removesse essa parada exatamente? A resposta é a primeira coisa que a Aula 26 vai cobrar — e a tabela de remoção está em **A.3**.

## 9. Critérios de avaliação

Este lab **é avaliado** e compõe os **30%** dos laboratórios na média da disciplina, com a política da ementa — oito labs, entrega até uma semana, **descartando a menor nota**. Não há peso novo inventado aqui.

Distribuição da nota deste lab:

- **Checkpoints 1 a 3 concluídos com saída visível — 45%.** `Checkpoint 1 OK`, `Checkpoint 2 OK` e `Checkpoint 3 OK` impressos, e a fonte do corpus declarada (base do Lab 5 ou corpus embutido, dito no notebook). Notebook sem saídas não é avaliável.
- **Checkpoint 4 — trajetórias gravadas e tabela de custo — 20%.** Os três JSON em disco com todos os campos por passo, e a tabela com o acumulado de tokens.
- **Análise escrita de uma trajetória — 20%.** É o item que separa as notas. Avaliada por três coisas: nomear **a etapa** em que o agente vacilou (percepção, ferramenta, argumento, interpretação, parada); citar o passo e a observação concretos da própria trajetória; e a consequência para o projeto ser uma mudança verificável, não uma intenção.
- **Checkpoint 5 — comparação com framework — 10%.** Tabela preenchida e as três respostas escritas, com a nomeação de qual peça continuou sendo do programador. Aceito sem `langgraph` instalado, na forma descrita no §5.
- **Declaração de uso de IA presente — 5%.** Ausência zera este item e habilita defesa oral.

**Nota sobre a prova.** A prova da Aula 17 já foi aplicada; a composição dela é diagnóstico e interpretação **42** · justificativa de escolha **40** · conceito aplicado **8** · derivação **10**. Registra-se aqui porque a análise escrita deste lab é o exercício mais próximo da parte de 42 pontos que o curso oferece: uma trajetória real na mão, e a pergunta é o que ela **permite** e o que **não permite** afirmar sobre o agente. Quem escreve "o agente errou" em vez de nomear a etapa erra a mesma coisa naquela parte da prova.

Observável em sala, sem nota: ao ser questionado no recolhimento, o aluno aponta em que linha do próprio loop a observação volta para `mensagens`, e diz o que acontece na trajetória quando essa linha é comentada.

## Apêndice matemático — índice

Três itens, slides 11 a 13 do deck, **organizados por checkpoint** conforme a §6-bis. Material de estudo e consulta, autossuficiente. Os números vêm das **três trajetórias gravadas** que acompanham o gabarito (`codigo/.../solucao/lab07_saida/`), no modo `simulador-roteirado(semente=25)` — são medições reais e reprodutíveis do loop, e estão declaradas como tais.

| Item | O que estabelece | Checkpoint |
|---|---|---|
| **A.1** | A **contabilidade da trajetória**, com os números que as três trajetórias de referência de fato produziram: passos (3, 2, 2), chamadas (7 no total), tokens de entrada e de saída acumulados (4 583 e 294), a fração de entrada (**94%** de tudo), e o custo por **tarefa resolvida** nos dois denominadores possíveis (1 626 ou 2 439 tokens, dependendo de a recusa honesta contar como resolução). Fecha com o que a média entre as três esconde: a dispersão de 1 268 a 2 243 tokens por tarefa, um fator de 1,8. | **CP4** |
| **A.2** | Por que o crescimento do contexto ao longo do loop é **superlinear no custo**: cada iteração relê a trajetória inteira, então os tokens enviados crescem com o quadrado dos passos enquanto o número de chamadas cresce linearmente. A derivação está em A.1 da Aula 23 e **não é refeita**; o que este item faz é **medir**: os `p₀` e `d` reais das três trajetórias, a descoberta de que `d` **não é constante** (38 a 223 tokens, dependendo da ferramenta), o cruzamento em que o termo quadrático passa o linear (`n ≈ 9`), e a conclusão contraintuitiva de que, no regime deste agente (`n ≤ 6`), encurtar o prompt de sistema paga mais que truncar a observação — com o número que mostra quando isso se inverte. | **CP2**, CP4 |
| **A.3** | As **três condições de parada**, enunciadas formalmente, com o que cada uma protege, qual delas garante terminação (só o orçamento), o que aparece na trajetória quando cada uma é removida, e o custo em tokens de cada remoção com os números de A.1. Inclui a demonstração de que a variante permissiva do contador de observações — a que aceita a mensagem injetada pelo próprio loop — **autoriza exatamente o que existe para bloquear**, e a análise de qual parada disparou em cada uma das três trajetórias gravadas. | **CP2** |

**Continuidade.** Este apêndice é o terceiro elo do fio de custo do bloco de agentes, e ele **fecha** o fio: o **A.1 do Lab 6 (Aula 22)** escreveu a conta pela primeira vez, com `p₀` e `d` **estimados**, para justificar o `MAX_PASSOS = 4` daquele notebook; a **Aula 23**, no item A.1 dela, generalizou a conta e desenvolveu a latência e as três táticas de controle de trajetória; **aqui** os `p₀` e `d` deixam de ser estimativa e passam a ser leitura de arquivo, e o resultado é uma surpresa útil — este agente vive no regime em que o **prompt fixo** domina, não a observação. O contraste entre a estimativa do Lab 6 e a medição deste lab é, ele mesmo, a lição: a estrutura da conta se prevê, os coeficientes se medem. O fio de método é o mesmo do fio estatístico dos Labs 2, 3, 5 e 8 — a diferença entre um número que se afirma e um número que se mede.
