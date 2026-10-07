---
aula: 9
titulo: "Laboratório 2: Mini-GPT do zero em PyTorch"
modulo: "1 — Fundamentos: do texto ao Transformer"
tipo: laboratorio
semana: 5
duracao_min: 120
versao: v2
---

# Aula 9 — Laboratório 2: Mini-GPT do zero em PyTorch

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2 — aula de laboratório (§6-bis do contrato).** Num lab a matemática **é**
> a prática. Inverter "aplicação antes de teoria" aqui seria redundante: o lab já é aplicação
> integral. Por isso o **roteiro prático não foi reordenado** — setup, demo e os cinco
> checkpoints permanecem na ordem que funciona em bancada. Três mudanças:
> (i) cada checkpoint **abre pelo comportamento esperado**, o que a tela imprime quando está
> certo, antes de nomear a fórmula a implementar; (ii) o deck ganhou um **apêndice matemático**
> com um item por checkpoint (A.1 a A.5), que reúne o fundamento formal de tudo que o aluno
> digita, mais **A.6** — o protocolo de depuração para quando o treino não desce, que é o modo
> de falha dominante deste lab; (iii) cada checkpoint cita o item correspondente, em uma linha,
> sem interromper a prática. Carga horária, numeração, checkpoints, entregável e objetivos de
> aprendizagem permanecem os da V1.

## 1. Objetivo da aula

Transformar a fórmula das Aulas 6 e 7 em código que roda: implementar atenção causal e um Transformer decoder-only na mão, treinar um modelo de linguagem de ~2,7 M de parâmetros em corpus de ~1 MB, gerar texto e medir perplexidade — para que o aluno pare de acreditar na arquitetura e passe a saber que ela funciona porque ele mesmo a montou. E, ao lado disso, sair com o **fundamento formal do que digitou disponível para consulta**, de modo que a pergunta "por que isso funciona?" tenha resposta escrita quando ela aparecer, uma semana depois, na hora de responder às questões-guia.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Implementar** scaled dot-product attention com masking causal em PyTorch a partir da fórmula `softmax(QKᵀ/√d_k)V`, e **verificar** a causalidade por teste automatizado.
2. **Construir** multi-head attention por reshape de tensores — cabeças como dimensão de lote, sem laço em Python.
3. **Montar** um bloco Transformer pré-norm completo (residual + LayerNorm + feed-forward) e **empilhá-lo** num decoder-only com embedding posicional aprendido.
4. **Treinar** o modelo em corpus pequeno com AdamW e **gerar** texto por amostragem autorregressiva com controle de temperatura.
5. **Medir** perplexidade por caractere com `PPL = exp(loss)` e **justificar** por que ela não é comparável com a perplexidade de um tokenizador de subword.
6. **Comparar** configurações de hiperparâmetros (cabeças, camadas, contexto) pela loss de validação e **enunciar** o que uma única execução não permite concluir.

*(Idênticos aos da V1. O que a V2 acrescenta é a rastreabilidade: cada um dos seis resultados
tem, no apêndice do deck, o item que o fundamenta — 1 → A.1, 2 → A.2, 3 → A.3, 5 → A.4,
6 → A.5.)*

## 3. Teoria aplicada

Este é um lab: a teoria já foi dada nas Aulas 6, 7 e 8. O que segue são os conceitos que o código materializa, o **comportamento observável** que denuncia cada um quando é mal entendido, e **onde está a derivação** que o sustenta.

**Convenção da V2 neste plano:** cada conceito abre pelo sintoma de implementação — o que aparece na tela — e fecha com o ponteiro para o item do apêndice. A ordem dos blocos e dos checkpoints é a da V1, intocada.

### Bloco 1 (00:35–01:05) — Da fórmula ao tensor: atenção causal e multi-head

**Conceito 1 — A fórmula é a receita; o shape é a unidade de medida.**
*Comportamento observável:* o teste falha na primeira verificação, ou — pior — passa e a loss não desce. `q @ k.transpose(-2, -1)` transforma `(B, T, d_head)` e `(B, T, d_head)` em `(B, T, T)`: a matriz de pesos é quadrada em **posições**, não em dimensão de embedding.
*Analogia do instrutor:* a fórmula é a receita e o shape é a unidade de medida — trocar grama por quilo dá um bolo com a mesma receita e resultado irreconhecível.
*Erro conceitual comum:* transpor o eixo errado. Com `T == d_head` por acidente, o shape sai certo e o resultado sai errado, sem erro nenhum do PyTorch. É por isso que o teste do Checkpoint 1 usa `T=5` e `d_head=8`: shapes diferentes fazem o erro estourar.
*Fundamento:* `S[b,i,j] = Σ_m q[b,i,m]·k[b,j,m]`, com análise de dimensões e a razão formal da escolha de `T ≠ d_head` no teste. → **A.1**

**Conceito 2 — A máscara entra antes do softmax, com `-inf`, não depois com zero.**
*Comportamento observável:* a linha de pesos deixa de somar 1 e a saída da posição 0 muda quando o último token muda — as duas verificações que o teste do CP1 faz explicitamente. Nenhuma exceção é levantada.
*Analogia:* é a diferença entre não convidar alguém para a votação e convidar, contar o voto no total e depois riscar o nome.
*Erro conceitual comum:* `pesos = softmax(escores); pesos = pesos * mask`. O teste de causalidade — mexer no último token e conferir que a saída da posição 0 não muda — existe para pegar exatamente isso.
*Fundamento:* a soma unitária por linha e a invariância da posição 0 são **consequências** da ordem, com a álgebra das três coisas que quebram na ordem invertida. → **A.1** (remetendo a **A.3 da Aula 6**)

**Conceito 3 — O `√d_k` só aparece quando `d_head` cresce.**
*Comportamento observável:* com `d_head = 8` num teste de brinquedo, dividir ou não dividir muda pouco. Com `d_head = 32` (o `192/6` da configuração de referência), o softmax satura e o gradiente que chega em Q e K encolhe.
*Erro conceitual comum:* dividir por `d_k` em vez de `√d_k` (compressão extra de 5,657×), ou por `√n_embd` em vez de `√d_head` (compressão extra de `√6 ≈ 2,449×`). O modelo treina — pior, e sem avisar. Este é o caso mais insidioso do lab, e o teste com `n_head=1` **não** o pega.
*Fundamento:* `Var(q·k) = d_head`, logo desvio-padrão `√d_head`; e o fator numérico exato de cada um dos dois erros de divisor. → **A.1** (variância derivada em **A.2 da Aula 6**)

**Conceito 4 — Multi-head é reshape, não laço.**
*Comportamento observável:* o teste de equivalência com `n_head=1` bate dígito por dígito, ou não bate. Quando não bate, o embaralhamento está nos `view`.
*Analogia:* é o mesmo que rodar seis experimentos independentes no mesmo `for` vetorizado — a GPU não sabe que são cabeças, para ela é lote maior.
*Erro conceitual comum:* esquecer o `contiguous()` (o PyTorch reclama e o aluno resolve — erro simpático), ou esquecer o `transpose` da volta e chamar `view` sobre `(B, n_head, T, d_head)`, o que dá **shape certo com cabeças e posições trocadas de lugar**, sem erro nenhum.
*Fundamento:* a concatenação das cabeças é exatamente `transpose` + `contiguous` + `view`; o caminho dos strides em memória, o exemplo numérico do embaralhamento silencioso, e a verificação de que o custo total não cresce (`3C²` de parâmetros e `O(T²·C)` de atenção, independentemente de `h`). → **A.2** (remetendo a **A.4 da Aula 6**)

### Bloco 2 (01:15–01:50) — Do bloco ao modelo treinado e medido

**Conceito 5 — O residual é uma estrada, e a norma não pode estar em cima dela.**
*Comportamento observável:* sem o `x +`, o modelo **não quebra** — ele treina, a loss desce devagar e estagna acima de 2,5 nats/caractere, contra ~1,5 com o residual. É o sintoma que mais gera "meu learning rate está errado" quando o problema é estrutural.
*Erro conceitual comum:* escrever `x = attn(ln1(x))`, sem o `x +`.
*Fundamento:* `∂y/∂x = (I + J_g)(I + J_f)` — a expansão sobre `N` blocos contém um caminho puramente identidade, que não pode encolher. Sem residual, o gradiente vira um **produto** de `N` jacobianas: com `‖J‖ ≈ 0,8` e seis camadas, `0,8⁶ ≈ 0,26`. E a razão de a loss estagnar especificamente perto de 2,5, e não em qualquer valor. → **A.3** (comparação pré-norm × pós-norm em **A.5 da Aula 7**)

**Conceito 6 — A loss é a entropia cruzada do próximo token, e cada posição é um exemplo.**
*Comportamento observável:* um lote de `64 × 128` produz 8.192 previsões supervisionadas de uma vez — é o sinal denso que a Aula 8 usou para explicar por que decoder-only venceu. E a loss **antes de treinar** tem de ser `ln(vocab_size) ≈ 4,5`.
*Erro conceitual comum:* achatar `logits` e `targets` de formas inconsistentes (a loss sai numérica e plausível, e o modelo aprende a prever o caractere errado); ou aplicar `softmax` antes de `F.cross_entropy`, que já inclui `log_softmax` (a loss sai estranhamente baixa desde o passo zero).
*Fundamento:* `L = −(1/N)·Σ log p_θ(x_n|c_n)`, e `L₀ = log|V|` para um modelo uniforme — o critério de conclusão do CP3 é um teorema, não um chute. As duas leituras do desvio (loss inicial acima e abaixo de `ln|V|`) estão escritas. → **A.4**

**Conceito 7 — Avaliar exige `model.eval()` e média de vários lotes.**
*Comportamento observável:* a loss de validação reportada de um lote só oscila entre execuções o bastante para inverter a ordem de duas configurações no CP5.
*Erro conceitual comum:* reportar `loss.item()` do último lote de treino como se fosse desempenho do modelo. É a versão em miniatura do erro de avaliação que o curso persegue até a Aula 27.
*Fundamento:* duas razões independentes e separáveis — dropout ativo enviesa a estimativa para cima; e a média de um lote único é uma amostra de uma variável aleatória, com variância que não some por ser grande. → **A.4** (nota de método) e **A.5**

**Conceito 8 — Perplexidade por caractere: `PPL = exp(loss)`.**
*Comportamento observável:* o número impresso ao lado do teto trivial (~90). Acima de 90 não é modelo fraco: é bug.
*Erro conceitual comum:* comparar essa perplexidade com o número publicado de um modelo de subword. A perplexidade é **por token**, e o token aqui é um caractere: mudar o tokenizador muda o denominador. É a armadilha anunciada na Aula 1 e explicada na Aula 2, agora com número próprio na tela.
*Fundamento:* `PPL` é a média **geométrica** do inverso das probabilidades, logo `PPL = exp(L)`; e a conversão `PPL_sub = PPL_car^r`, com `r` caracteres por subword — um modelo com `PPL_car = 4,0` tem `PPL_sub = 256`. A única normalização comparável é bits por caractere. → **A.4**

**Conceito 9 — Geração autorregressiva é um laço com três armadilhas.**
*Comportamento observável:* o texto sai — e sai lixo estruturado, o que confunde mais do que um erro explícito.
*As três:* cortar o contexto nos últimos `block_size` tokens (senão o embedding posicional não tem índice), pegar **só o último passo de tempo** dos logits, e amostrar com `multinomial` depois de aplicar a temperatura.
*Erro conceitual comum:* passar os logits inteiros `(B, T, vocab)` para o softmax e amostrar do passo errado.

**Conceito 10 — O que 2,7 M de parâmetros e 1 MB de corpus conseguem.**
*Comportamento observável:* palavras que parecem português, espaçamento e pontuação no lugar, estrutura de diálogo se o corpus tiver — e nenhuma semântica.
*Erro conceitual comum:* concluir "meu código está errado" porque o texto não faz sentido. O critério de sucesso do Checkpoint 4 é a curva de loss e a plausibilidade morfológica, não o significado.
*Fundamento:* a contagem `12·C² + 4C` por bloco, que produz os ~2,7 M e mostra que **dois terços dos parâmetros estão no feed-forward**, não na atenção. Se a contagem impressa divergir mais de ~5%, há uma peça a mais ou a menos. → **A.3**

**Conceito 11 — O que uma execução com uma semente não permite concluir.**
*Comportamento observável:* duas execuções da **mesma** configuração, com sementes diferentes, dão losses distintas — tipicamente da ordem de 0,04 nat neste lab. Qualquer diferença entre linhas da tabela menor que isso não é evidência de nada.
*Erro conceitual comum:* ler a tabela do CP5 como um ranking.
*Fundamento:* `L(c,s) = μ(c) + ε(c,s)`; uma execução por configuração não separa os dois termos, e o desvio-padrão da diferença é `σ√2`. Mais os três confundimentos escondidos na tabela: `block_size=32` vê 4× menos tokens por passo, `n_layer=2` tem ~1/3 dos parâmetros, e 500 passos é medir no transiente. → **A.5**

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 15 min | Setup do ambiente + contexto | Recap da Aula 8 (decoder-only venceu; hoje ela vira código); abrir o notebook no Colab e ligar a GPU; baixar o corpus; os números do lab (~2,7 M de parâmetros, ~1 MB de corpus, 2000 passos, ordem de 3 a 5 min em T4) **e de onde eles saem** (`12·C²` por bloco, dois terços no feed-forward — A.3); o mapa dos cinco checkpoints **apresentado pelo que cada um imprime na tela**, com a coluna do item de apêndice correspondente; o entregável |
| 00:15 | 20 min | Demonstração guiada (live coding) | `scaled_dot_product_attention` escrita do zero na frente da turma: escores por produto escalar, escala `1/√d_k`, máscara triangular com `torch.tril` + `masked_fill(-inf)`, softmax, agregação de V; conferir que cada linha soma 1 e que a matriz é triangular; nomear os dois pontos de quebra (eixo de transposição e ordem máscara/softmax) com o ponteiro para A.1. Termina de propósito sem multi-head |
| 00:35 | 30 min | Checkpoints 1–2 (aluno executando) | CP1: atenção causal com os cinco TODOs e o teste de causalidade (abre pelas cinco verificações que o teste faz → A.1); CP2: `MultiHeadAttention` por reshape, com teste de shape e de equivalência com `n_head=1` (abre pelo `OK` e pela equivalência dígito a dígito → A.2) |
| 01:05 | 10 min | Intervalo | — |
| 01:15 | 35 min | Checkpoints 3–5 + extensões | CP3: `FeedForward`, `Block` pré-norm, `MiniGPT` e contagem de parâmetros (abre pelos dois números na tela → A.3); CP4: treino de 2000 passos, curva de loss, geração de 500 caracteres, perplexidade (abre pelas três coisas na tela → A.4); CP5: três configurações curtas de 500 passos variando cabeças, camadas e contexto (abre pela tabela **e** pelo parágrafo do que a medição não prova → A.5) |
| 01:50 | 10 min | Recolhimento | O que entregar (notebook executado, três amostras, tabela de experimentos, respostas às questões-guia, declaração de uso de IA), prazo de uma semana, critério; **índice do apêndice projetado por 20 s**, com a indicação de que as duas questões-guia que mais separam nota estão respondidas em A.4 e A.5; ponte para a Aula 10 |

*Comparação com a V1: a grade é a mesma, minuto a minuto. O que mudou é a forma de lançar cada
checkpoint (comportamento esperado primeiro) e ~90 segundos distribuídos em ponteiros para o
apêndice — tirados das explicações conceituais que a V1 fazia em voz alta e que agora estão
escritas com mais rigor no deck.*

## 4. Demonstração guiada

**Live coding de `scaled_dot_product_attention` — 20 min, do zero, com tensores minúsculos.**

O instrutor escreve a função na frente da turma, em células novas, com `B=1`, `T=4`, `d_head=3` — pequeno o bastante para imprimir a matriz inteira e ler os números na tela. Nada disso depende de GPU.

A demo continua sendo o coração operacional do lab, e na V2 ela ganha uma função extra: **é ela que produz os comportamentos que os checkpoints depois exigem**. Cada número lido na tela aqui é um critério de conclusão daqui a quinze minutos.

Passos em alto nível:

1. Criar `q`, `k`, `v` aleatórios de shape `(1, 4, 3)` com semente fixa, e imprimir os shapes antes de qualquer operação.
2. Calcular `escores = q @ k.transpose(-2, -1)` e mostrar que o shape virou `(1, 4, 4)` — quadrado em posições, não em dimensão de embedding. Nomear que `-2, -1` são os dois últimos eixos e que `0, 1` trocaria lote com posição.
3. Imprimir a matriz de escores crua e comentar o que cada célula significa: afinidade da query da linha com a key da coluna. Apontar que a diagonal não é privilegiada — atenção a si mesmo é aprendida, não imposta.
4. Dividir por `math.sqrt(d_head)` e mostrar a matriz encolhendo em amplitude; rodar o mesmo com `d_head=64` para exibir a saturação do softmax sem a divisão. *É a evidência do Conceito 3, e o ponteiro falado é A.2 da Aula 6 mais A.1 desta.*
5. Construir a máscara com `torch.tril(torch.ones(T, T, dtype=torch.bool))` e imprimi-la — o triângulo é o desenho do quadro da Aula 6 aparecendo como tensor.
6. Aplicar `escores.masked_fill(~mask, float("-inf"))` e imprimir: metade da matriz virou `-inf`. **Insubstituível:** é o passo que o Conceito 2 protege.
7. `pesos = F.softmax(escores, dim=-1)`, imprimir a matriz triangular resultante e checar `pesos.sum(-1)` — todos 1. A primeira linha é `[1, 0, 0, 0]`: o primeiro token só pode olhar para si mesmo. **Insubstituível:** é o critério de conclusão nº 2 do CP1 aparecendo em tela pela primeira vez.
8. `saida = pesos @ v`, conferir shape `(1, 4, 3)` de volta, nomear que a saída é combinação convexa dos values (logo sempre dentro da nuvem), e fechar comparando com `F.scaled_dot_product_attention` do PyTorch para mostrar que o resultado bate.
9. Parar aqui, de propósito: multi-head é o Checkpoint 2 e não vai ser entregue de graça.

**Números que a demo produz e que a aula usa como evidência (§7 do contrato):** a matriz `(1,4,4)` contra a expectativa errada de `(1,3,3)`; o peso máximo do softmax subindo de moderado para quase 1 quando `d_head` vai de 3 para 64 sem divisão; a soma exata de 1 em cada linha após a máscara; e a primeira linha `[1,0,0,0]`. Os quatro reaparecem como critérios de conclusão do CP1.

Insumos preparados na véspera: o notebook do aluno rodado de ponta a ponta na GPU da oferta, com o tempo real de treino anotado; o corpus baixado num arquivo local para o caso de a rede falhar.

## 5. Hands-on

**O componente prático da unidade é o próprio laboratório** (§6-bis e §7 do contrato). O trabalho da V2 foi explicitar os números que ele produz e amarrá-los aos critérios de conclusão — de modo que "terminei" seja uma observação e não uma sensação.

Cinco checkpoints, cada um com critério de conclusão observável **enunciado primeiro**. O aluno trabalha no próprio notebook; o instrutor circula.

**Checkpoint 1 — Atenção causal (00:35–00:50).**
*Ao final, a célula `teste_checkpoint_1()` imprime `Checkpoint 1 OK`.* O teste verifica cinco coisas: shape `(B,T,T)` na matriz de pesos, **cada linha somando exatamente 1**, ausência de peso no triângulo superior, **invariância da saída da posição 0** a mudanças no último token, e o modo sem máscara voltando a ser bidirecional.
*O que implementar:* os cinco TODOs de `scaled_dot_product_attention(q, k, v, mask=None)` — escores, escala `1/√d_k`, `masked_fill(-inf)`, softmax, agregação de V.
*Fundamento e derivação:* → **Apêndice A.1** (slide 11) — shapes em PyTorch, a razão formal de `T ≠ d_head` no teste, a álgebra dos dois erros de divisor, e por que a quarta verificação é um teste de derivada escrito como diferença finita.

**Checkpoint 2 — Multi-head (00:50–01:05).**
*Ao final, a célula `teste_checkpoint_2()` imprime `Checkpoint 2 OK`* — shape `(B, T, n_embd)` preservado e, com `n_head=1`, saída **idêntica dígito por dígito** à do Checkpoint 1 calculada com os mesmos pesos.
*O que implementar:* `MultiHeadAttention.forward` — projeção `qkv` combinada, split em q/k/v, reshape para `(B, n_head, T, d_head)`, chamada da função do CP1 com a máscara cortada em `T`, volta para `(B, T, C)` e projeção `W_O` com dropout.
*Fundamento e derivação:* → **Apêndice A.2** (slide 12) — strides, por que `contiguous()` é obrigatório, o exemplo numérico do embaralhamento silencioso, e a nota honesta de que o teste com `n_head=1` **não** pega o erro de ordem dos eixos.

**Checkpoint 3 — O bloco completo (01:15–01:27).**
*Ao final, a tela imprime dois números:* contagem da ordem de **2,7 M de parâmetros**, e loss **antes de treinar** próxima de `ln(vocab_size) ≈ 4,5`. Modelo recém-inicializado que não está no chute uniforme tem bug — e é infinitamente mais barato descobrir isso agora.
*O que implementar:* `FeedForward` (expansão 4×, GELU, dropout), o `forward` do `Block` em pré-norm com os dois residuais, e o `MiniGPT` (soma dos embeddings de token e posição, pilha de blocos, `ln_f`, `lm_head`, loss com `F.cross_entropy`).
*Fundamento e derivação:* → **Apêndice A.3** (slide 13) — o caminho aditivo do gradiente pelo residual, o contrafactual `0,8⁶ ≈ 0,26`, a razão de a loss estagnar em ~2,5 sem o `x +`, e a tabela de contagem que produz os 2,7 M peça por peça. A loss inicial `ln|V|` está em **A.4**.

**Checkpoint 4 — Treinar, gerar, medir perplexidade (01:27–01:42).**
*Ao final, a tela mostra três coisas:* curva de loss decrescente com validação acompanhando o treino, uma amostra de 500 caracteres que parece português sem ser português, e a perplexidade por caractere impressa ao lado do teto trivial (~90).
*O que implementar/rodar:* 2000 passos com AdamW `lr=3e-4`, curva de treino e validação, os TODOs de `generate`, amostra de 500 caracteres, `PPL = exp(val_loss)`.
*Fundamento e derivação:* → **Apêndice A.4** (slide 14) — dedução de `PPL = exp(L)` pela média geométrica, `L₀ = log|V|`, a conversão `PPL_sub = PPL_car^r` (com o exemplo 4,0 → 256), bits por caractere como a única normalização comparável, e a nota de método sobre `estimate_loss()`.

**Checkpoint 5 — Variar hiperparâmetros e comparar (01:42–01:50).**
*Ao final, existem duas coisas no notebook:* a tabela com as quatro execuções preenchida (parâmetros, loss de validação, perplexidade, tempo) **e** um parágrafo dizendo qual variável mais mexeu na loss e **o que a medição não prova**. A segunda parte é a que vale.
*O que rodar:* `run_experiment` em quatro execuções curtas de 500 passos — referência, `n_head=1`, `n_layer=2`, `block_size=32` — e três amostras geradas de configurações diferentes.
*Fundamento e derivação:* → **Apêndice A.5** (slide 15) — o modelo `L(c,s) = μ(c) + ε(c,s)`, o desvio-padrão `σ√2` da diferença, como estimar `σ` com duas execuções, os três confundimentos escondidos na tabela, e a ponte para o intervalo de confiança e o teste de McNemar do Lab 8.

*Extensão de dois minutos, altamente recomendada e barata:* rodar a **configuração de referência uma segunda vez, mudando só a semente**. É o experimento mais formativo do lab: ele transforma a frase "isso não prova nada" em um número concreto, e é o que faz o parágrafo do CP5 sair honesto.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Colab sem GPU** disponível para parte da turma | `torch.cuda.is_available()` devolve `False` | A variante CPU está na célula de configuração (`n_embd=96`, `n_layer=4`, `block_size=64`, `batch_size=32`, 500 passos): treina em poucos minutos e serve para todos os checkpoints; a comparação do CP5 continua válida porque é interna à própria execução |
| **Corpus não baixa** (rede da sala, URL fora do ar) | Exceção nas duas tentativas de download | Fallback automático para o tinyshakespeare no próprio notebook; terceiro caminho de `files.upload()` documentado; instrutor traz o `.txt` num pendrive e distribui |
| **Sessão do Colab cai** no meio do treino | Runtime desconectado, variáveis perdidas | O treino de referência custa poucos minutos: reexecutar do topo é aceitável. Quem perder duas vezes usa a variante CPU/500 passos e entrega a análise com a configuração menor, dizendo isso no notebook |
| **Aluno sem conta Google** ou sem acesso ao Colab | Não consegue abrir o notebook | Rodar local com `requirements.txt` (CPU serve); em último caso, formar dupla no lab e entregar individualmente depois |
| **Treino divergindo** (loss `nan` ou subindo) | `nan` no primeiro log, ou loss acima de `ln(vocab_size)` | Conferir na ordem: divisão por `√d_k` presente, máscara aplicada antes do softmax, `zero_grad` dentro do laço, `lr` não alterado. Se persistir, reduzir `lr` para `1e-4` e seguir — a explicação vale mais que o ajuste fino |
| **Turma em ritmos muito diferentes** | Metade ainda no CP1 aos 00:50 | Os checkpoints 1 e 2 têm célula de solução comentada que o instrutor libera aos 00:50 e 01:05; ninguém fica travado antes do CP3, que é o coração do lab. Quem termina antes recebe a extensão do §8 |
| **Erro silencioso de shape** que não levanta exceção | Testes passam mas a loss não desce | Os testes dos CP1 e CP2 foram escritos com `T ≠ d_head` justamente para isso; se a loss não desce no CP4, o roteiro manda reexecutar os dois testes antes de mexer em hiperparâmetro |
| **A loss não desce no CP4** e os testes do CP1 e CP2 passam | Curva plana, ou estacionada em `≈ 4,50`, `≈ 2,5` ou `nan` | Aplicar o **protocolo de A.6**: treinar 300 passos sobre **um único lote** e ler o patamar. Duas verificações resolvem a maioria dos casos em menos de um minuto — a loss no passo 0 tem de valer `ln(90) ≈ 4,50`, e nenhum parâmetro pode ter `p.grad is None`. Só depois disso se toca em `lr`. A instrução "reexecute os testes" cobre a atenção; A.6 cobre a perda, os rótulos, o `backward` e a inicialização, que os testes não veem |
| **Aluno "conserta" mexendo em `lr` sem diagnóstico** | Vários valores de `lr` tentados em sequência, sem hipótese | É o reflexo errado e o mais comum: dá sensação de progresso sem tocar na causa. A ordem de A.6 é deliberada — perda, capacidade, gradiente, **depois** taxa. Cravar em sala: mexer em hiperparâmetro antes de saber que o gradiente chega é adivinhação, e adivinhação não cabe no relatório |
| **A turma pedir a derivação durante o lab** | "De onde vem esse raiz de d_k?" no meio do CP1 | Num lab, **a bancada tem prioridade**: resposta de uma frase mais o ponteiro para o item do apêndice, e a conversa continua na mesa de quem perguntou, não para a sala. A Parte 4 do roteiro tem cinco derivações prontas com o tempo de cada uma; a única janela realmente barata para conduzir alguma é os minutos em que o treino do CP4 roda sozinho |
| **Aluno achar que o apêndice é matéria nova para hoje** | "Isso vai cair na entrega?" | Cravar: o apêndice é material de consulta e de estudo; o que se entrega são os cinco checkpoints e as questões-guia. Duas das cinco questões ficam melhores com A.4 e A.5 ao lado, e isso é dito abertamente |

## 7. Artefatos produzidos

- `lab-02-mini-gpt.ipynb` executado, com todas as saídas visíveis: shapes, `Checkpoint 1 OK`, `Checkpoint 2 OK`, contagem de parâmetros, logs de treino e curva de loss.
- **Três amostras geradas** de 500 caracteres, de configurações diferentes, coladas no notebook.
- **Tabela de experimentos** do Checkpoint 5 preenchida: configuração, parâmetros, loss de validação, perplexidade por caractere, tempo.
- **O número da segunda semente** (extensão de dois minutos do §5): a loss da configuração de referência rodada duas vezes, que é a régua de ruído do próprio aluno. É o artefato novo da V2 e o que faz o parágrafo de análise deixar de ser retórico.
- Respostas às **cinco questões-guia** escritas em células de markdown do próprio notebook.
- **Declaração de uso de IA** — quais ferramentas, para quê, em duas linhas.
- Uma implementação de Transformer decoder-only que é do aluno, e que ele reusa como referência mental no resto do curso.

## 8. Desafio pós-aula

**Este lab é o entregável avaliado da semana.** Prazo: uma semana após a aula. O que entra na entrega está no §7 acima — notebook executado, três amostras, tabela do CP5, respostas às questões-guia e declaração de uso de IA. Quem não terminou o CP5 em sala termina em casa; os checkpoints 1 a 4 são o núcleo obrigatório.

Extensão opcional, não avaliada, para quem quiser puxar o fio da Aula 7: trocar uma peça do bloco e medir. Duas escolhas boas — substituir o embedding posicional aprendido por senoidais, ou trocar `LayerNorm` por `RMSNorm` e `GELU` por `SwiGLU`. Em ambos os casos, rodar 500 passos com a peça antiga e 500 com a nova, mesma semente, e reportar a diferença na loss de validação. A pergunta dirigida é honesta: com este tamanho de modelo e corpus, a diferença que você mediu é maior que o ruído entre duas sementes? Rodar a referência duas vezes com sementes diferentes responde isso — e essa é a lição de método que o Lab 8 vai cobrar. **A conta que dimensiona "maior que o ruído" está em A.5.**

Leitura de apoio: Vaswani et al., *Attention Is All You Need* (arXiv 1706.03762), seções 3.2 e 3.3 — agora com o código na frente, o parágrafo do artigo fica curto. **Pergunta dirigida da V2:** a §3.2.2 descreve multi-head em três linhas de notação e não menciona `contiguous()`, strides nem ordem de eixos. Compare o que o artigo enuncia com o que **A.2** descreve como implementação, e diga em uma frase o que a notação matemática esconde do programador. Referência de formato: Karpathy, *nanoGPT* (repositório público), que é a inspiração declarada deste notebook.

## 9. Critérios de avaliação

Este lab **é avaliado** e compõe os **30%** dos laboratórios na média da disciplina, com a política da ementa — oito labs, entrega até uma semana, **descartando a menor nota**. Não há peso novo inventado aqui.

Distribuição da nota deste lab (idêntica à V1):

- **Checkpoints 1 a 4 concluídos com saída visível — 60%.** Os testes `Checkpoint 1 OK` e `Checkpoint 2 OK` impressos, contagem de parâmetros na ordem esperada, curva de loss decrescente e uma amostra gerada. Notebook sem saídas não é avaliável.
- **Checkpoint 5 e a tabela de experimentos — 15%.** Quatro execuções, tabela preenchida, e o parágrafo de análise com a ressalva sobre semente única.
- **Respostas às cinco questões-guia — 20%.** Avaliadas por precisão conceitual, não por extensão. A questão da perplexidade por caractere e a do que *não* se pode concluir de uma execução são as que separam as notas.
- **Declaração de uso de IA presente — 5%.** Ausência zera este item e habilita defesa oral.

**O que a V2 muda no *como* se corrige**, sem mexer nos pesos:

- **A resposta de perplexidade vale pela conta, não pela advertência.** "Não é comparável porque o tokenizador é diferente" é a resposta da V1 e vale parcialmente. A resposta completa converte: diz **quanto** muda (`PPL_sub = PPL_car^r`), dá um número, e nomeia a normalização que seria comparável. O material para isso está em **A.4** e é dito em sala.
- **A resposta sobre uma execução única vale pela régua, não pela ressalva.** "Uma semente não prova nada" é retórica. A resposta que separa nota apresenta a régua: qual é a variação entre duas sementes da própria configuração, e por que qualquer diferença abaixo dela é ruído. **A.5** e a extensão de dois minutos do §5 existem para tornar isso barato.
- **O apêndice é cobrável como fundamento de justificativa, nunca como derivação isolada.** Nenhuma questão-guia pede "derive". Elas pedem "explique por que" e "diga o que a medição não prova" — e é a existência do apêndice que torna razoável exigir uma resposta com mecanismo em vez de uma resposta com adjetivo.

*Observável em sala, sem nota:* ao ser questionado no recolhimento, o aluno aponta em que linha do próprio código a máscara é aplicada e explica por que ela vem antes do softmax — e, se pressionado, diz **qual das cinco verificações do teste** pegaria o erro se ele tivesse invertido a ordem. Apontar a linha é a V1; nomear o teste que a protege é a V2.
