# Laboratório 3: Decodificação e prompting na prática

## Slide 1 · Abertura: ontem eu afirmei, hoje vocês medem · 00:00–00:05

**[Projeto a lista das quatro alavancas da Aula 10, em cinza]**

Ontem eu afirmei quatro coisas com um script de brinquedo: temperatura, `top-k`, `top-p` e prompting. Eu mostrei o efeito de cada uma numa distribuição embutida.

Hoje vocês medem, com modelo de verdade do outro lado, e em três eixos: **qualidade, custo em tokens e latência**.

> Ideia central: "Ontem eu afirmei. Hoje vocês medem — e medir tem três colunas, não uma."

E uma coisa que muda de hoje em diante: a função que vocês vão escrever para medir tokens e tempo não morre neste lab. Ela volta no Lab 5, no Lab 8 e no projeto final. É o artefato mais durável de hoje.

---

## Slide 2 · Os três modos: offline, Ollama, API · 00:05–00:10

**[Abro a célula de configuração no notebook]**

Este notebook roda em três modos, e vocês escolhem aqui. **Offline**: distribuições embutidas, determinístico, sem rede — funciona com o Wi-Fi caído. **Ollama**: modelo local pequeno na máquina de vocês. **API**: provedor com free tier.

E todo resultado que sai carrega **o modo em que foi produzido**. Esse é o campo de proveniência, e ele é obrigatório no relatório.

> Ideia central: "Número sem proveniência é opinião com casas decimais. Todo resultado de hoje diz em que modo nasceu."

Por que três? Porque esta aula tem que acontecer com a rede caindo, com a quota estourando e com a sala inteira batendo no mesmo provedor. O modo offline garante que os Checkpoints 1 e 4 rodem em qualquer circunstância.

---

## Slide 3 · O mapa: cinco checkpoints e o mini-relatório · 00:10–00:15

**[Projeto a trilha e vou apontando estação por estação]**

Cinco checkpoints, e eu vou apresentar cada um **pelo que a tela imprime quando está certo** — porque é assim que vocês vão saber que terminaram.

Checkpoint 1, até dez para as onze: as quatro funções de decodificação e a grade três por três. A tela imprime `Checkpoint 1 OK` e nove saídas.

Checkpoint 2: classificação zero-shot contra few-shot. Imprime `Checkpoint 2 OK` e três linhas com duas métricas.

Checkpoint 3, depois do intervalo: chain-of-thought em dez problemas. Duas linhas e uma divisão.

Checkpoint 4: a tabela dos três eixos, quatro linhas **geradas por código**.

Checkpoint 5: modelo local contra modelo de API, tabela mais um parágrafo.

**[Aponto o cartão do entregável]**

E o entregável: notebook mais **meia página**.

> Ideia central: "Cinco checkpoints e meia página. A meia página é a parte difícil, porque nela vocês têm de escolher — e escolher com número na mão é o que esta disciplina treina."

**[Aponto a coluna cinza com os `A.n`]**

Essa coluninha aí do lado é ponteiro de estudo, não tarefa de hoje. Cada checkpoint tem um item de apêndice com a conta por trás do número dele. Ninguém precisa disso agora — e todo mundo vai querer isso na hora de escrever a meia página.

---

## Slide 4 · [Demo] Uma pergunta, seis decodificações · 00:15–00:35

**[Passo para a Parte 2]**

Os passos estão na Parte 2. O que eu digo antes de trocar de tela:

> Ideia central: "Se a saída muda e os pesos não mudaram, a mudança está inteira do lado de fora do modelo."

---

## Slide 5 · [Checkpoint 1] Decodificação implementada e medida · 00:35–00:50

**[Projeto o critério de conclusão antes de qualquer coisa]**

Checkpoint 1. Quando estiver certo, a tela imprime uma linha: `Checkpoint 1 OK`.

E para imprimir isso, o teste vai ter conferido cinco coisas. Eu vou ler as cinco, porque cada uma aponta para um erro diferente — e são erros que o Python aceita sem reclamar.

Um: a temperatura **não** muda o ranking dos tokens. Ela age no logit, e só reescala.

Dois: cada filtro devolve uma distribuição que soma um. `top-k` e `top-p` renormalizam depois de cortar.

Três: com `p` igual a zero vírgula nove, sobre a distribuição zero vírgula cinquenta, trinta, quinze, cinco — sobram **três** tokens. O token que **cruza** a linha entra.

Quatro, e essa é contraintuitiva: o nucleus com temperatura dois é **maior ou igual** ao nucleus com temperatura zero vírgula cinco.

Cinco: greedy três vezes dá idêntico; amostragem com três sementes dá diferente.

**[Aponto as quatro assinaturas com os TODOs]**

O que implementar, na ordem: temperatura nos **logits**, `top-k`, `top-p` com o critério de **atingir** o `p`, e amostrar sobre o que sobrou. Depois do teste verde, a grade três por três.

> Ideia central: "Top-p mantém o menor conjunto que **atinge** p. O token que cruza a linha entra."

---

## Slide 6 · [Checkpoint 2] Few-shot e o colapso de formato · 00:50–01:05

**[Projeto o critério]**

Checkpoint 2. A tela imprime `Checkpoint 2 OK`, e o teste vai ter conferido uma aritmética: em cada condição, **acertos mais erros mais fora-do-espaço igual a vinte**.

Essa identidade existe por um motivo. Ela impede que "fora do espaço de rótulos" desapareça dentro de "erro".

**[Aponto as duas saídas contrastadas no slide]**

Olhem estas duas respostas. Uma é uma frase longa, em prosa, explicando o que o comentário significa. A outra é a palavra `bug`, sozinha. Se o rótulo certo era `dúvida`, as duas estão erradas — e dão a **mesma acurácia**.

Mas são dois problemas de engenharia completamente diferentes. Errar o rótulo se resolve com exemplos. Responder em prosa livre se resolve com restrição de formato.

> Ideia central: "Errar o rótulo e responder em prosa livre dão a mesma acurácia e são dois problemas diferentes. É por isso que a tabela tem duas colunas."

Três condições, vinte comentários, espaço fechado em `bug`, `dúvida`, `elogio`, `recurso`, temperatura zero. E ao lado da tabela, uma frase de vocês: **qual das duas colunas o few-shot mexeu mais**.

---

*Intervalo · 01:05–01:15*

---

## Slide 7 · [Checkpoint 3] Chain-of-thought e o preço do raciocínio · 01:15–01:27

**[Projeto o critério, que aqui são duas linhas e uma divisão]**

Checkpoint 3, e é onde mora o achado deste lab.

Dez problemas, duas condições — resposta direta e chain-of-thought —, formato final obrigatório `Resposta:` seguido do número. E três colunas: acurácia, mediana de tokens de saída, e **falhas de formato** contadas separadamente.

Depois, a divisão: quantos tokens extras o raciocínio custou, quantos pontos de acurácia ele comprou, e a razão entre os dois.

**[Aponto o campo `tokens_por_ponto`]**

E aqui está a parte importante. Se o `delta_pontos` for zero ou negativo, esse campo vem **nulo de propósito**, com a leitura impressa junto: o raciocínio custou tokens sem comprar nada nestes problemas, com este backend.

Isso é **resultado**, não falha. Se acontecer com vocês, vocês encontraram o achado mais valioso do lab.

> Ideia central: "Chain-of-thought é hora extra paga em token de saída — às vezes para somar dois mais dois."

---

## Slide 8 · [Checkpoint 4] A tabela dos três eixos · 01:27–01:40

**[Projeto o cabeçalho real da tabela do notebook]**

Checkpoint 4. O critério aqui não é uma linha de OK: é que **existe uma tabela markdown impressa pela função do notebook**. Não digitada.

Quatro abordagens — zero-shot, few-shot, chain-of-thought, e CoT com few-shot — e as colunas: tokens de entrada, tokens de saída, se a contagem é exata ou estimada, latência mediana, **dispersão**, e custo por mil requisições.

Três exigências de método, e elas não são sugestão.

Tabela **gerada por código**. Ninguém digita número em tabela: não é reproduzível.

**Três repetições**, com a mediana e a dispersão mínimo-máximo ao lado.

E contagem **exata** — do campo `usage` da API — marcada como diferente de **estimada**.

> Ideia central: "Uma execução não mede latência. Mede um sorteio."

**[Aponto a coluna de dispersão]**

E o motivo da coluna de dispersão estar destacada: se a dispersão de uma configuração cobre a diferença entre duas linhas, **essa tabela não ordena nada**. Ela parece ordenar, e não ordena.

---

## Slide 9 · [Checkpoint 5] Modelo local pequeno × modelo de API · 01:40–01:50

Último checkpoint. A tabela comparativa entre o modelo local pequeno e o de API, nos mesmos três eixos, e um parágrafo dizendo **onde fica a fronteira** entre os dois.

Não existe resposta certa aqui — existe resposta justificada. O parágrafo tem que dizer para qual tipo de tarefa o local basta, e o que faria vocês pagarem pela API.

> Ideia central: "A pergunta não é qual é melhor. É a partir de que ponto vale pagar — e vocês têm três colunas para responder isso."

---

## Slide 10 · Recolhimento: o mini-relatório e a ponte para a Aula 12 · 01:50–02:00

**[Projeto o formato do entregável]**

Notebook executado, mais meia página. E na meia página, três coisas: o campo de proveniência, uma configuração **escolhida** com a justificativa, e — a parte que eu mais vou ler — **o que a medição de vocês não permite concluir**.

> Ideia central: "Escrever o que o número não prova é mais difícil e vale mais que escrever o que ele prova."

**[Aponto a seta do diagrama para os labs futuros]**

E a função que vocês escreveram para medir tokens e tempo: guardem. Ela volta no Lab 5, quando a gente medir recuperação, e no Lab 8, quando cada equipe montar o harness do próprio projeto.

**[Projeto o índice do apêndice por 15 s]**

Três itens, um por checkpoint. E eu nomeio um: o **A.3** responde "quantos itens eu precisaria para essa diferença não ser ruído". Quem teve duas condições com acurácia parecida no Checkpoint 2 vai precisar dele para escrever a meia página honestamente.

Amanhã a gente vira a lente. Vocês passaram duas aulas do lado de fora do modelo, puxando alavancas. Amanhã a gente entra na fábrica que produziu ele — e a primeira coisa que a fábrica tem é um orçamento.

> Ideia central: "Hoje vocês mediram o que dá para mudar sem tocar nos pesos. Amanhã: quanto custou construir os pesos."

---

## Parte 2 — Demonstração guiada

Vinte minutos, seis tratamentos, mesma pergunta e mesmo modelo. O objetivo é que as três colunas de medição apareçam na mesma tela que o texto.

**1.** **[Rodo greedy três vezes seguidas]** Mesma pergunta, mesma configuração, três execuções. Olhem: saída idêntica, caractere por caractere. Determinismo.

**2.** **[Rodo amostragem três vezes]** Mesma pergunta, mesmo modelo, três execuções — e três saídas diferentes. Nada mudou nos pesos. A diferença está inteira no algoritmo que escolhe o token.

**3.** **[Faço a varredura de temperatura]** Agora a temperatura subindo. Olhem o que acontece: em zero vírgula dois a saída é previsível e repetitiva; em um vírgula cinco ela é criativa e às vezes incoerente. E o que está acontecendo por baixo é a **incerteza** da distribuição subindo de forma contínua.

**4.** **[Aplico `top_p` sobre `T = 1.5`]** Agora eu ponho `top_p` de zero vírgula nove por cima da temperatura alta. A saída volta a ficar utilizável — porque eu cortei a cauda que a temperatura tinha inflado. Os dois controles agem sobre **a mesma distribuição, em sequência**. Não são independentes, e é por isso que vocês vão varrer os dois numa grade e não um de cada vez.

**5.** **[Ligo a instrumentação]** E aqui está o que muda a partir de hoje. Mesma chamada, e agora com três números ao lado do texto: tokens de entrada, tokens de saída, segundos. Antes disso, "qualidade" era impressão. A partir daqui é uma coluna ao lado de duas outras.

**6.** **[Comparo zero-shot com few-shot]** Último tratamento. Mesma tarefa, com e sem quatro exemplos no prompt. Olhem a saída **e** olhem os tokens de entrada. O few-shot melhorou o formato e **custou** — e o Checkpoint 2 vai medir exatamente as duas coisas.

---

## Parte 3 — Hands-on

Cinco checkpoints. Circular olhando tela é mais eficiente que esperar pergunta — em lab, quem está travado geralmente não levanta a mão.

**1.** **[Lanço o Checkpoint 1 — decodificação, até 00:50]** As quatro funções e a grade. O critério é `Checkpoint 1 OK` na tela.

**2.** **[Lanço o Checkpoint 2 — few-shot, até 01:05]** Três condições, duas métricas, e a identidade da soma igual a vinte.

**3.** **[Lanço o Checkpoint 3 — chain-of-thought, até 01:27]** Dez problemas, duas condições, três colunas mais a divisão.

**4.** **[Lanço o Checkpoint 4 — a tabela, até 01:40]** Quatro abordagens, tabela gerada por código, três repetições.

**5.** **[Lanço o Checkpoint 5 — local × API, até 01:50]** Tabela comparativa e um parágrafo sobre a fronteira.

---

## Parte 4 — Apêndice: se perguntarem

Em laboratório eu **não conduzo derivação no quadro** — o tempo é do teclado. O que esta parte traz são as respostas de trinta segundos, mais o que fazer se a pergunta for boa demais para despachar.

**Item 1 — "Por que o nucleus não encolhe quando a temperatura sobe?" (A.1, 30 s).**
A pergunta mais provável, e ela vem do teste. **Resposta curta:** "temperatura maior espalha a massa, e massa espalhada demora mais para acumular zero vírgula nove — então a linha do `p` é empurrada para mais longe e entram mais tokens." Se insistirem, a demonstração está em A.1, com a entropia crescendo estritamente em `T` e as acumuladas caindo. **Não** conduzir no quadro agora.

**Item 2 — "Esse `tokens_por_ponto` significa o quê exatamente?" (A.2, 30 s).**
Boa pergunta e vale responder bem, porque o número vai para o relatório. **Resposta curta:** "é o preço que um ponto percentual de acurácia teria de valer para o chain-of-thought se pagar. Se vocês gastaram trezentos tokens extras para ganhar dois pontos, cada ponto custou cento e cinquenta tokens — e a pergunta de engenharia é se um ponto vale isso no caso de uso de vocês." A conta completa, com as duas parcelas de preço diferente, está em A.2.

**Item 3 — "Quantos itens eu precisaria para essa diferença ser real?" (A.3, 30 s).**
A pergunta que eu **quero** que apareça, porque é a que faz o relatório ficar honesto. **Resposta curta:** "com vinte itens, cada um vale cinco pontos percentuais — então uma diferença de cinco pontos é literalmente um comentário mudando de lado. O A.3 tem o erro-padrão e o número de itens que você precisaria." Se a pergunta vier no CP2, é o melhor momento possível: a pessoa está com o número na tela.

**Item 4 — "Por que mediana e não média na latência?" (A.3, 20 s).**
**Resposta curta:** "porque a distribuição de latência tem cauda longa — uma requisição lenta puxa a média e não puxa a mediana. E com três amostras, a média de três é frágil demais para reportar sozinha; é por isso que vai a dispersão ao lado."

---

## Recolhimento · 01:50–02:00

O recolhimento está redigido como fala no Slide 10 da Parte 1 — o formato do entregável com os três itens da meia página, a nota de que a função de medição é reutilizada nos Labs 5 e 8, os quinze segundos de índice do apêndice nomeando o A.3, e a ponte para a Aula 12.

> Ideia central: "Hoje vocês mediram o que dá para mudar sem tocar nos pesos. Amanhã: quanto custou construir os pesos."

---

*Roteiro do Instrutor · Aula 11 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
