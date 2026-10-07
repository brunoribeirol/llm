---
aula: 14
titulo: "Laboratório 4: Fine-tuning com LoRA/QLoRA"
modulo: "3 — Treinamento: pré-treino, SFT e PEFT"
tipo: laboratorio
semana: 7
duracao_min: 120
versao: v2
---

# Aula 14 — Laboratório 4: Fine-tuning com LoRA/QLoRA

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2 — §6-bis (laboratórios).** O roteiro prático **não foi reordenado**: a
> sequência dos cinco checkpoints é a que funciona no teclado, minuto a minuto. O que mudou é que
> cada checkpoint agora abre pelo **que a célula imprime quando está certo** — a linha
> `Checkpoint N OK`, o número que sai, a verificação que o teste fez — antes de dizer o que
> implementar. O apêndice é organizado **por checkpoint**, com três itens: a conta de memória da
> T4 que explica por que este `r` cabe (CP1, CP2 e CP3), o que a curva de perda permite e **não**
> permite concluir (CP4), e por que a comparação antes × depois em cinco prompts é ilustração e
> não medição (CP5). Carga horária, numeração e objetivos inalterados. **O notebook em `codigo/`
> não muda.**

## 1. Objetivo da aula

Transformar as contas da Aula 13 em um adaptador que existe: carregar um modelo aberto de ~1,5 B quantizado em 4 bits no Colab gratuito, treinar uma LoRA sobre 100 exemplos de instrução em português, e provar com os mesmos prompts antes e depois que menos de 1% dos parâmetros treináveis muda o comportamento do modelo — inclusive fechando, com número, a coluna de "fora do espaço de rótulos" que a turma mediu e não conseguiu zerar no Lab 3.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Carregar** um modelo causal aberto com quantização NF4 de 4 bits via `BitsAndBytesConfig` e **medir** a memória de GPU efetivamente ocupada pelos pesos.
2. **Formatar** um conjunto de instruções com `apply_chat_template` e **inspecionar** a string tokenizada, identificando os tokens especiais de papel e o token que abre o turno do assistente.
3. **Configurar** LoRA com `peft.LoraConfig` e **conferir** a saída de `print_trainable_parameters()` contra a conta `r · (d_in + d_out)` feita à mão na Aula 13.
4. **Treinar** o adaptador com `Trainer`, acumulação de gradiente e recomputação de ativações, e **registrar** perda de treino, perda de validação, memória de pico e tempo.
5. **Comparar** o modelo antes e depois nos **mesmos** prompts, separando ganho de **formato** de ganho de **acerto**, e **medir** esquecimento com um conjunto de controle fora do domínio treinado.
6. **Salvar e recarregar apenas o adaptador**, e **declarar** o tamanho do arquivo do adaptador ao lado do tamanho do modelo base.
7. **Declarar a proveniência** de cada número do relatório: modelo, base quantizada ou não, dispositivo, número de passos e tamanho do conjunto.

*(Idênticos aos da V1.)*

## 3. Teoria aplicada

Este é um laboratório: a teoria foi dada ontem, na Aula 13. O que segue são os **contratos de execução** do lab — e eles são conteúdo, porque decidem se o número que sai significa algo.

### Os cinco checkpoints, pelo que cada um imprime

| CP | Relógio | O que faz | **O que a tela imprime quando está certo** | Apêndice |
|---|---|---|---|---|
| 1 | 00:35–00:50 | carregar em 4 bits + linha de base dos 8 prompts | `Checkpoint 1 OK` + a memória decomposta em corpo × embedding + `ANTES` com 8 entradas | A.1 |
| 2 | 00:50–01:05 | 100 exemplos com o template de chat | `Checkpoint 2 OK` + um exemplo formatado com os tokens de papel visíveis + o histograma de comprimentos | A.1 |
| 3 | 01:15–01:25 | `LoraConfig` + treináveis conferidos à mão | `Checkpoint 3 OK` + `treináveis: 9.232.384` + a diferença entre a conta e a biblioteca em % | A.1 |
| 4 | 01:25–01:38 | treinar 90 passos | duas curvas no mesmo gráfico + `pico de memória` + `tempo total` + `Checkpoint 4 OK` | A.2 |
| 5 | 01:38–01:50 | antes × depois, controle e adaptador | `Checkpoint 5 OK` + a tabela de 2 colunas + a tabela de controle + `TOTAL do adaptador: xx MB` | A.3 |

**Entregável:** notebook executado + **o adaptador salvo** + campo de proveniência.

### Bloco 1 (00:35–01:05) — Carregar em 4 bits e preparar o dado

**Conceito 1 — Quantizar não é só "menos memória": é escolher o que não quantizar.**
*O que a tela imprime:* três linhas de decomposição — corpo do transformer em 4 bits (≈ 0,6 GiB), embeddings e cabeça de saída em 16 bits (≈ 0,43 GiB), total na ordem de 1,0 a 1,2 GiB — e, abaixo, a conta ingênua `1,5e9 × 0,5 byte = 0,70 GiB` marcada como **não explicando o total**.
`BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=COMPUTE_DTYPE)` comprime as matrizes de peso dos blocos, e **não** comprime a tabela de embeddings nem a cabeça de saída. Com vocabulário de ~152 mil tokens e `d_model = 1536`, o embedding sozinho tem ~233 M de parâmetros em 16 bits, ~0,43 GiB, que não encolhe.
*Erro de medição comum:* comparar o número impresso com a conta ingênua e concluir que a quantização falhou. Não falhou — a diferença é o embedding, e o tamanho do embedding é consequência direta do tokenizador: é a Aula 2 reaparecendo com fatura de VRAM.
- **Fundamento:** a decomposição impressa é a conta de memória de **A.5 da Aula 13** aplicada a este modelo e a esta placa, com a linha do embedding que a conta genérica não tem.
  → derivação completa, com o orçamento inteiro da T4 e a tabela de sensibilidade: **Apêndice A.1** (slide 11)

**Detalhe de hardware que é conteúdo — o `compute_dtype` depende da GPU que o Colab entregou.**
A Aula 12 explicou por que `bf16` virou padrão. Mas `bf16` só existe a partir da arquitetura Ampere, e a T4 do Colab gratuito é Turing. O notebook resolve com `torch.cuda.is_bf16_supported()` e define `COMPUTE_DTYPE` — `bfloat16` quando há suporte, `float16` na T4 — usando o mesmo valor no `bnb_4bit_compute_dtype` e nas flags `bf16`/`fp16` do `TrainingArguments`.
*Erro de execução comum:* fixar `torch.bfloat16` no código porque foi o que a aula teórica recomendou. Numa T4 isso ou falha ou cai silenciosamente para fp32, e o treino fica lento sem motivo aparente.

**Conceito 2 — A linha de base tem de ser capturada antes, nos mesmos prompts.**
*O que a tela imprime:* oito blocos `PROMPT / ANTES`, e o teste conferindo que `ANTES` tem 8 entradas não vazias e que duas chamadas de `responder()` devolvem a **mesma** string.
O notebook roda os cinco prompts de teste e os três de controle **antes** de qualquer treino e guarda as respostas em variável. Depois do treino, o modelo antigo não existe mais na sessão.
*Erro de medição comum:* treinar primeiro e tentar reconstruir a linha de base de memória; ou recarregar o base depois com outros parâmetros de decodificação e comparar duas coisas diferentes. Por isso a função de geração é determinística (greedy) e fixa em um único lugar.

**Conceito 3 — Os prompts de controle existem para tornar o esquecimento visível.**
*O que a tela imprime:* a tabela de controle com `ANTES (ok=...)` e `DEPOIS (ok=...)` para uma multiplicação, uma tradução curta e uma pergunta factual — mais o aviso impresso de que a verificação por substring é **grosseira de propósito** e que as respostas devem ser lidas.
Eles não têm nada a ver com a tarefa e é exatamente por isso que estão lá: são o instrumento para observar o esquecimento catastrófico do Conceito 5 da Aula 13.
*Erro de medição comum:* medir só na tarefa-alvo. Com LoRA o risco é menor (a base está congelada e o delta é removível), mas menor não é zero.
- **Fundamento:** três prompts têm resolução de 33 pontos percentuais. O conjunto de controle é uma **peneira de catástrofe**, não uma medição de esquecimento — e a diferença entre as duas coisas é o que separa um relatório honesto de um otimista.
  → o que 3 e 5 prompts licenciam afirmar: **Apêndice A.3** (slide 13)

**Conceito 4 — O template de chat é o que transforma um par em um exemplo de treino.**
*O que a tela imprime:* a string formatada em `repr()`, com `<|im_start|>` e `<|im_end|>` visíveis, os três papéis presentes, e as duas linhas do alvo (`Categoria:` e `Resposta:`). O teste confere exatamente isso.
O dado bruto é um par `{comentario, resposta}`. O exemplo de treino é a string que sai de `apply_chat_template`. O modelo aprende a produzir a resposta **depois** do token que abre o turno do assistente; se o formato do treino não é o mesmo da inferência, o adaptador aprende a responder a um prompt que nunca vai chegar.
*Erro de execução comum:* montar a string à mão com `f"Usuário: {x}\nAssistente: {y}"`. Passa neste checkpoint e explode no Checkpoint 5. O notebook obriga a imprimir um exemplo formatado, com os tokens visíveis, exatamente para tornar isso impossível de passar batido.

**Conceito 5 — Simplificação declarada: treina-se a sequência inteira, não só a resposta.**
A prática de produção mascara os tokens do prompt no rótulo (`labels = -100` nas posições da instrução) para que a perda seja calculada apenas sobre a resposta. Este notebook **não** faz isso, de propósito, e a simplificação está declarada numa célula de markdown; o mascaramento é a primeira extensão opcional do §8.
*Erro conceitual comum:* aprender esta versão simplificada como se fosse a única — e, pior, ler a queda da perda como se ela medisse a tarefa. Boa parte dos tokens de cada exemplo é o **prompt de sistema, idêntico nos 100 exemplos**; aprender a prever uma constante move a perda e não move a tarefa.
- **Fundamento:** a perda é a entropia cruzada média **por token sobre a sequência inteira**, e a composição da sequência decide o que a queda significa.
  → a decomposição da sequência e o que a curva não permite concluir: **Apêndice A.2** (slide 12)

### Bloco 2 (01:15–01:50) — Treinar, medir e empacotar

**Conceito 6 — `print_trainable_parameters()` só vale se o aluno souber conferir.**
*O que a tela imprime:* `treináveis: 9.232.384 · fração estimada do modelo: 0,6xx%`, a linha `minha conta` ao lado da linha `biblioteca`, a `diferença: 0,00%`, e a contagem de módulos LoRA criados conferida contra `7 × 28 = 196`.
O notebook pede que o aluno recalcule o valor à mão, a partir das dimensões lidas de `model.config` — não copiadas do quadro. Um `print` que o aluno não sabe reproduzir não é conhecimento.
*Erro de medição comum:* estranhar o denominador. Com base em 4 bits, a contagem de "todos os parâmetros" depende de como a biblioteca conta pesos empacotados; o notebook corrige multiplicando o total por 2 no perfil quantizado, e diz isso em comentário. A defesa é a conta à mão, que não depende de versão de biblioteca.
- **Fundamento:** a contagem `r · (d_in + d_out)` por módulo e a tabela dos sete módulos estão em **A.1 da Aula 13** e **não se repetem aqui**. O que este lab acrescenta é o que essa contagem custa em memória nesta placa.
  → **Apêndice A.1** (slide 11)

**Conceito 7 — Os três interruptores que fazem o treino caber.**
`gradient_accumulation_steps = 4` (lote efetivo 4 com lote físico 1), `gradient_checkpointing` (recomputação de ativações — a opção que a Aula 12 explicou) e `optim="paged_adamw_8bit"` (estados do otimizador em 8 bits, com paginação). Junto com `model.config.use_cache = False` durante o treino, que desliga o KV cache — inútil no treino e caro em memória.
*Erro de execução comum:* deixar `use_cache = True` e ignorar o aviso, ou ligar `gradient_checkpointing` sem `prepare_model_for_kbit_training` e ver o gradiente não fluir.
- **Fundamento:** os três interruptores atacam parcelas **diferentes** do orçamento, e só uma delas é a que aperta nesta configuração. Saber qual é o que transforma um `OOM` de tentativa e erro em diagnóstico.
  → o orçamento decomposto e a regra de diagnóstico do `OOM`: **Apêndice A.1** (slide 11)

**Conceito 8 — A comparação antes × depois tem duas colunas, não uma.**
*O que a tela imprime:* quatro números — acerto de categoria antes e depois, aderência ao formato antes e depois — e as cinco comparações completas `ANTES / DEPOIS` lado a lado.
Como no Lab 3: **acerto** da categoria e **aderência ao formato**. O ponto pedagógico é que fine-tuning com 100 exemplos move principalmente a segunda; o acerto de categoria melhora pouco ou nada, porque o acerto depende de capacidade e a capacidade não mudou.
*Erro de medição comum:* reportar uma coluna só e concluir "o fine-tuning melhorou o modelo". Melhorou o **formato**. E o segundo erro, mais sutil e mais grave: declarar a melhoria de acurácia como resultado quando o conjunto tem **cinco** itens.
- **Fundamento:** com `n = 5`, a menor diferença representável é 20 pontos percentuais, e no cenário mais favorável possível — os cinco prompts mudando de lado na mesma direção — o resultado **ainda não** é distinguível do acaso ao nível de 5%.
  → a conta completa, e o que este conjunto licencia afirmar: **Apêndice A.3** (slide 13)

**Conceito 9 — O adaptador é um artefato pequeno e independente.**
*O que a tela imprime:* a lista de arquivos do diretório com o tamanho de cada um, o `TOTAL do adaptador` em MB, e a comparação da saída do modelo em memória com a do modelo recarregado (`idênticas: True`).
`save_pretrained(dir)` grava **só** os pesos LoRA e a configuração. E o recarregamento é a prova: base pública mais o arquivo pequeno reconstrói o modelo adaptado.
*Erro de execução comum:* chamar `save_pretrained` no objeto errado e gravar gigabytes — o teste falha acima de 200 MB; ou recarregar sem a mesma configuração de quantização. O notebook recarrega com a **mesma** `BitsAndBytesConfig` e imprime a ressalva de que fundir numa base de 16 bits funciona e não é equivalente.

**Conceito 10 — Proveniência: o número não existe sem o contexto que o produziu.**
Cada tabela do relatório carrega modelo, dispositivo, se a base estava quantizada, número de passos, tamanho do conjunto e tempo. É a mesma exigência do Lab 3, com um eixo novo: **a base**. Um resultado obtido no modo de fallback sem GPU, com um modelo menor, é ilustrativo — e tem de estar escrito que é.
*Erro de medição comum:* comparar o resultado próprio (base de 1,5 B em 4 bits, 90 passos, 100 exemplos, 5 prompts de teste) com número publicado de artigo. Não é a mesma medida e não é comparável.

### Grade temporal

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 15 min | Setup do ambiente + contexto | Recap da Aula 13 pelo **número** (0,60% e a conta que produz ele); abrir o notebook no Colab e confirmar GPU; rodar a célula de diagnóstico e o `pip install`; ler os números esperados declarados no notebook; o mapa dos cinco checkpoints **pelo que cada um imprime** e o entregável |
| 00:15 | 20 min | Demonstração guiada (live coding) | Carregar em 4 bits e imprimir a memória decomposta; escrever `responder` determinística e rodar **um** prompt no base; `apply_chat_template` num exemplo e ler os tokens na tela; `LoraConfig` e `print_trainable_parameters`, com a conta de ontem escrita no quadro ao lado; **um** passo de treino. Termina de propósito sem o laço |
| 00:35 | 30 min | **CP1** (00:35–00:50) e **CP2** (00:50–01:05) | CP1: carregar em 4 bits, medir a memória decomposta, capturar `ANTES` dos 5 de tarefa e 3 de controle; CP2: formatar os 100 exemplos, dividir 88/12, inspecionar um exemplo tokenizado |
| 01:05 | 10 min | Intervalo | — |
| 01:15 | 35 min | **CP3** (01:15–01:25), **CP4** (01:25–01:38), **CP5** (01:38–01:50) | CP3: `LoraConfig`, `get_peft_model`, treináveis e a conferência à mão; CP4: treinar 90 passos, as duas curvas, pico e tempo; CP5: antes × depois com as duas colunas, os 3 de controle, salvar o adaptador, medir e recarregar |
| 01:50 | 10 min | Recolhimento | O que entregar, prazo de uma semana, critério; **um item do apêndice nomeado** (A.3, que é a resposta da questão-guia 5); ponte para a Aula 15 e aviso sobre a prova da Aula 17 |

## 4. Demonstração guiada

**Live coding — 20 min (00:15–00:35), no Colab do instrutor com GPU, em células novas.**

O instrutor executa o caminho completo em miniatura: carrega, mede, gera uma vez, formata um exemplo, configura LoRA, dá **um** passo de treino. O objetivo não é adiantar os checkpoints — é que a turma veja cada peça funcionando isolada antes de encadeá-las.

Passos em alto nível:

1. Rodar a célula de diagnóstico: GPU, memória total, perfil escolhido, números esperados.
2. Carregar o modelo com `BitsAndBytesConfig` de 4 bits NF4 e imprimir a memória alocada.
3. Decompor na tela: corpo em 4 bits, embedding em 16 bits, total — e apontar que a conta ingênua **não** explica o total, o que amarra com a Aula 2.
4. Escrever a função `responder(modelo, prompt)` na frente da turma: monta as mensagens, aplica o template, gera com `do_sample=False`, decodifica só os tokens novos.
5. Rodar **um** dos cinco prompts de teste no modelo base e ler a resposta em voz alta. É a linha de base aparecendo: o modelo entende o pedido e responde em prosa, fora do formato.
6. Pegar um exemplo do conjunto embutido e imprimir `apply_chat_template(..., tokenize=False)`. Projetar a string com os tokens especiais visíveis e apontar o token que abre o turno do assistente.
7. Montar a `LoraConfig` com `r=8`, `lora_alpha=16`, os sete módulos-alvo, e chamar `get_peft_model` seguido de `print_trainable_parameters()`. Ler o número na tela.
8. Escrever no quadro, ao lado, a conta de ontem: `329.728 × 28 = 9.232.384`, `0,60%`. Deixar as duas coisas visíveis juntas.
9. Rodar **um** único passo de treino e mostrar o valor da perda. Comentar que o número absoluto não diz nada — o que vai dizer é a curva dos 90 passos, que é o Checkpoint 4.
10. Parar aqui, de propósito, e apagar as células da demo.

**Número que a demo produz.** **9.232.384 treináveis, 0,60%** — o mesmo número que o quadro da Aula 13 produziu, agora impresso por uma biblioteca. É o par "número na tela + conta no quadro" que faz a demo, e ele é citado de volta em três lugares do fluxo: no **slide 7**, onde o Checkpoint 3 exige que a conta à mão bata com o `print` dentro de 1%; no **slide 8**, porque é esse número que decide a parcela `16·N_a` do orçamento de memória do treino; e no **slide 10**, no recolhimento, quando o instrutor pede a alguém que aponte na própria tela a linha em que os módulos-alvo são declarados e diga quantos adaptadores isso criou. O segundo número da demo é a **memória decomposta** — corpo em 4 bits contra embedding em 16 —, que é o observável do Checkpoint 1 e o insumo do Apêndice A.1.

Insumos preparados antes da aula: o notebook rodado de ponta a ponta na GPU da oferta, com **memória de pico e tempo real anotados** — esses dois números vão para o slide de setup; o notebook rodado também no perfil de CPU, para o instrutor saber quanto tempo o fallback leva de verdade; um adaptador já treinado e salvo no Drive do instrutor, para o caso de alguém não conseguir treinar e precisar seguir para o Checkpoint 5.

## 5. Hands-on

O hands-on é a aula. Cinco checkpoints, cada um abrindo pelo observável.

**Checkpoint 1 · 00:35–00:50 — Carregar em 4 bits e capturar a linha de base.**
*Critério de conclusão observável:* a tela imprime `Checkpoint 1 OK`, e antes disso três linhas de memória decomposta (corpo, embedding, total) mais os oito blocos `PROMPT / ANTES`. O teste verifica quatro coisas: existem parâmetros de 4 bits, a memória dos pesos está na faixa `0,6–2,0 GiB`, `responder()` é determinística (duas chamadas idênticas) e não devolve o prompt de volta, e `ANTES` tem 8 entradas não vazias.
*O que implementar:* os TODOs de `carregar_modelo()` — `BitsAndBytesConfig` com NF4, dupla quantização e `compute_dtype = COMPUTE_DTYPE` — e de `responder()` — aplicar o template, gerar de forma determinística, decodificar só os tokens novos.

**Checkpoint 2 · 00:50–01:05 — Dataset de instruções e template de chat.**
*Critério de conclusão observável:* `Checkpoint 2 OK`, mais a string formatada impressa em `repr()` com `<|im_start|>` e `<|im_end|>` visíveis, mais a linha de comprimentos em tokens (mín · mediana · máx). O teste confere 100 textos não vazios, a divisão somando 100, os três papéis presentes, as duas linhas do alvo, e que **nenhum** exemplo atingiu `MAX_LEN` — porque um exemplo truncado ensina o modelo a parar no lugar errado.
*O que implementar:* formatar os 100 exemplos com `apply_chat_template`, dividir 88 treino / 12 validação, tokenizar com truncamento em `MAX_LEN`, e imprimir **um** exemplo formatado inteiro.

**Checkpoint 3 · 01:15–01:25 — LoRA e a conta dos treináveis.**
*Critério de conclusão observável:* `Checkpoint 3 OK`, e na tela `treináveis: 9.232.384`, a fração abaixo de 1%, a linha `minha conta` batendo com a linha `biblioteca` com `diferença: 0,00%`, e `196` módulos LoRA criados (`7 × 28`). O teste falha se a fração passar de 1%, se o número de módulos não for `7 × n_layers`, ou se a conta à mão divergir mais de 1%.
*O que implementar:* preencher a `LoraConfig`, chamar `prepare_model_for_kbit_training` **antes** de `get_peft_model`, e preencher a célula que recalcula os parâmetros à mão a partir das dimensões lidas de `model.config`.

**Checkpoint 4 · 01:25–01:38 — Treinar e registrar.**
*Critério de conclusão observável:* um gráfico com **duas** curvas (treino e validação) no mesmo eixo, as listas de perda impressas abaixo dele, e as quatro linhas `passos · tempo total · pico de memória · perda final de treino`. Depois, `Checkpoint 4 OK` — o teste confere que o histórico tem pelo menos dois pontos, que a perda final é menor que a inicial, que existe perda de validação registrada, e que o pico de memória foi medido.
*O que implementar:* preencher os `TrainingArguments` (lote 1, acumulação 4, `max_steps` do perfil, `learning_rate=2e-4`, `bf16`/`fp16` conforme o dispositivo, `gradient_checkpointing` conforme o perfil, avaliação a cada 30 passos) e rodar `trainer.train()`.

**Checkpoint 5 · 01:38–01:50 — Antes × depois, controle e adaptador.**
*Critério de conclusão observável:* `Checkpoint 5 OK`, mais três coisas na tela: a tabela de duas colunas com quatro números (acerto e formato, antes e depois), a tabela de controle com `ok=` antes e depois nos três prompts fora do domínio, e a lista de arquivos do adaptador com `TOTAL do adaptador: xx MB` e `idênticas: True` no recarregamento. O teste confere 8 entradas em `DEPOIS`, formato depois **maior** que antes, diretório existente com menos de 200 MB e arquivo `adapter_*` presente.
*O que implementar:* rodar os mesmos 8 prompts no modelo adaptado, montar as duas tabelas, salvar com `save_pretrained` no modelo **PEFT**, imprimir o tamanho, e recarregar base + adaptador num objeto novo.

**Entregável:** notebook executado + **o adaptador salvo** + as duas tabelas do CP5 + campo de proveniência + as cinco questões-guia + declaração de uso de IA. A questão-guia 5 — *o que os números deste notebook não provam* — é a que mais separa nota, e a resposta dela está escrita no **A.3**.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Colab sem GPU** para parte da turma | `torch.cuda.is_available()` devolve `False` | O notebook detecta e troca para o perfil `cpu`: modelo menor da **mesma família** (mesmo template de chat), `MAX_LEN` menor, menos passos. Todos os cinco checkpoints fecham; o notebook imprime que o resultado é **ilustrativo** e a proveniência registra o perfil |
| **Download do modelo lento** ou rede da sala saturada | Barra de download travada aos 00:20 | Não liberar download coletivo simultâneo: duas ondas. Quem não baixar em 5 min usa o perfil `cpu`. O modelo do instrutor já está em cache para a demo |
| **`bitsandbytes` incompatível** com o ambiente | `ImportError` ou erro de CUDA na `BitsAndBytesConfig` | A célula de instalação fixa faixas compatíveis e há um caminho sem quantização (`load_in_4bit=False`, base em 16 bits) que ainda cabe na T4 para 1,5 B — declarado como tal na proveniência. O conceito de LoRA fica preservado |
| **`OOM` durante o treino** | `CUDA out of memory` no Checkpoint 4 | Na ordem: reduzir `MAX_LEN` de 320 para 192, reduzir a acumulação, confirmar `gradient_checkpointing=True` e `use_cache=False`. **A ordem não é arbitrária** — a regra de diagnóstico está em A.1: se o `OOM` se move com `MAX_LEN` e não com `r`, são as ativações |
| **Sessão do Colab cai** no meio do treino | Runtime desconectado | O treino custa poucos minutos: reexecutar do topo é aceitável e o modelo está em cache. Quem perder duas vezes recebe do instrutor o adaptador pré-treinado e segue para o CP5, declarando isso |
| **Perda de treino não desce** | Curva plana após 30 passos | Conferir na ordem: `prepare_model_for_kbit_training` **antes** de `get_peft_model`; `target_modules` com nomes que existem (nome errado não levanta erro — o teste do CP3 pega); `learning_rate` não trocado para `2e-5` de fine-tuning completo. É o que a mensagem de falha do teste do CP4 lista |
| **Turma conclui "o fine-tuning não funcionou"** porque o acerto de categoria não subiu | Tabela do CP5 com formato perfeito e acerto igual | É o **resultado esperado** e é o ponto pedagógico: 100 exemplos movem formato, não capacidade. Ler em voz alta uma tabela dessas como achado; a questão-guia 3 pede exatamente essa interpretação |
| **Turma conclui o contrário — que o acerto melhorou** porque subiu de 60% para 80% | Uma linha de tabela com `n = 5` lida como medição | É o erro de método do lab, e é o que o A.3 existe para prevenir: com cinco prompts, 20 pontos percentuais é **um** prompt mudando de lado. Nomear em voz alta no recolhimento |
| **Turma em ritmos muito diferentes** | Metade ainda no CP1 aos 00:50 | Os CP1 e CP2 têm célula de solução comentada liberada aos 00:50 e 01:05; ninguém fica travado antes do CP3, que é o coração do lab. Quem termina antes recebe as extensões do §8 |
| **Chave ou token do Hugging Face no notebook entregue** | Célula com token em texto claro | O modelo é aberto e **não exige token**; a célula de login está comentada e documentada com `getpass`. Entrega com token visível vira defesa oral e o aluno é orientado a revogar o token na hora |

## 7. Artefatos produzidos

- `lab-04-lora-finetuning.ipynb` executado, com todas as saídas visíveis: `Checkpoint 1 OK` a `Checkpoint 5 OK`, a memória decomposta, o exemplo formatado com os tokens de papel, `treináveis: 9.232.384`, as duas curvas de perda e as duas tabelas do CP5.
- **Adaptador LoRA treinado** — o diretório salvo (`adapter_config.json` + `adapter_model.safetensors`), com o tamanho em MB registrado. É o entregável físico do lab e o primeiro modelo que o aluno entrega no curso.
- **Tabela antes × depois** dos 5 prompts, com as duas colunas e as respostas completas dos dois modelos lado a lado.
- **Tabela de controle** dos 3 prompts fora do domínio, antes e depois, com uma frase de leitura: houve esquecimento observável ou não?
- **Campo de proveniência** preenchido: modelo, perfil, base quantizada, `compute_dtype`, GPU, passos · lote · `MAX_LEN`, n de treino/validação, memória dos pesos, pico, tempo, treináveis e fração, tamanho do adaptador, data.
- Respostas às **cinco questões-guia** em células de markdown do próprio notebook.
- **Declaração de uso de IA.**
- Uma configuração de LoRA que funciona e que o aluno reusa no projeto final quando o problema for de **forma**.

## 8. Desafio pós-aula

**Este lab é o entregável avaliado da semana.** Prazo: uma semana após a aula. O que entra na entrega está no §7. Quem não terminou o CP5 em sala termina em casa; os checkpoints 1 a 4 são o núcleo obrigatório.

Extensões opcionais, não avaliadas, na ordem de retorno pedagógico:

1. **Mascarar o prompt no rótulo.** Implementar `labels = -100` nas posições da instrução, de modo que a perda seja calculada somente sobre a resposta. Retreinar com os mesmos hiperparâmetros e comparar a curva de validação e as duas colunas do CP5. **Pergunta dirigida:** o A.2 estima que boa parte da queda de perda observada vem do prompt de sistema, que é idêntico nos 100 exemplos. Sua curva mascarada confirma essa estimativa? E o que aconteceria se o prompt fosse dez vezes mais longo que a resposta?
2. **Varrer `r` e os módulos-alvo.** Três configurações curtas de 40 passos: `r = 8` nos sete módulos (a referência), `r = 32` nos sete módulos, e `r = 16` **só** nas quatro projeções de atenção. Registrar treináveis, perda de validação e aderência ao formato. **Pergunta dirigida:** a diferença que você mediu é maior que o ruído entre duas sementes? Rodar a referência duas vezes responde isso — é a régua de **A.5 da Aula 9**. E confira o pico de memória: ele mudou tanto quanto você esperava? O A.1 diz que não deveria.
3. **Fundir o adaptador e medir a latência.** `merge_and_unload()` sobre uma base em 16 bits, cronometrando a geração dos 5 prompts antes e depois. **Pergunta dirigida:** a latência mudou? E a saída do modelo fundido em 16 bits é idêntica à do adaptador sobre a base de 4 bits — e por que não? (A ressalva está em **A.3 da Aula 13**, casos-limite.)
4. **Testar a fronteira do conceito.** Acrescentar ao treino cinco exemplos que ensinam um **fato** inventado (um preço, uma data, um nome de política interna), retreinar, e perguntar o fato de dez formas diferentes. É a demonstração empírica do Conceito 12 da Aula 13: quantas das dez formas devolvem o fato certo, e o que isso diz sobre usar fine-tuning como banco de dados?
5. **Fechar a conta que o A.3 abre.** Usando a fórmula de tamanho de amostra do **A.3 do Lab 3 (Aula 11)**, calcular quantos prompts de teste seriam necessários para detectar, com precisão de ±10 pontos, a melhoria de acurácia que você observou. Comparar com os 5 que você usou. O número é a resposta honesta da questão-guia 5.
6. **Leitura — Hu et al., *LoRA* (arXiv 2106.09685), seção de resultados.** **Pergunta dirigida:** o artigo compara LoRA com fine-tuning completo e com adaptadores em série. Em qual dos eixos comparados o LoRA **não** ganha, e por que esse eixo importa menos em produção?

## 9. Critérios de avaliação

Este lab **é avaliado** e compõe os **30%** dos laboratórios na média da disciplina, com a política da ementa — oito labs, entrega até uma semana, **descartando a menor nota**. Não há peso novo inventado aqui.

Distribuição da nota deste lab:

- **Checkpoints 1 a 4 concluídos com saída visível — 50%.** `Checkpoint 1 OK` a `Checkpoint 4 OK` impressos, memória decomposta, exemplo formatado com os tokens visíveis, `treináveis` e fração, as **duas** curvas de perda no mesmo gráfico. Notebook sem saídas não é avaliável.
- **Checkpoint 5 completo — 20%.** Tabela antes × depois com as **duas** colunas, tabela de controle preenchida, adaptador salvo com o tamanho registrado, e recarregamento conferido. A tabela de controle vale metade deste item: sem ela, não há como afirmar nada sobre esquecimento.
- **Conferência da conta do CP3 — 10%.** A conta à mão dos parâmetros treináveis, com as dimensões lidas da configuração do modelo, batendo com a contagem da biblioteca. Item que existe para impedir que o `print` seja aceito por fé.
- **Respostas às cinco questões-guia — 15%.** Avaliadas por precisão conceitual, não por extensão. As duas que separam as notas são a **3** (por que o formato melhorou mais que o acerto) e a **5** (o que os números deste lab **não** provam, com ao menos um item sobre o tamanho do conjunto de teste). A resposta da 5 está em **A.3**, e quem responder "poucos dados" sem número não pontua.
- **Campo de proveniência e declaração de uso de IA — 5%.** Proveniência incompleta ou declaração ausente zera este item e habilita defesa oral.

**Nota sobre a prova.** O conteúdo deste lab é cobrado na prova da Aula 17, cuja composição é diagnóstico e interpretação **42** · justificativa **40** · conceito aplicado **8** · derivação **10**. O CP4 e o CP5 são exatamente o formato das questões de interpretação: uma tabela de resultados reais e a pergunta é o que ela **permite** e o que **não permite** afirmar. Quem leu a queda da perda de treino como prova de que a tarefa melhorou, ou leu 60% → 80% em cinco prompts como melhoria, erra a mesma coisa na prova.

*Observável em sala, sem nota:* ao ser questionado no recolhimento, o aluno aponta na própria tela a linha em que os módulos-alvo do LoRA são declarados e diz, de cabeça, quantos adaptadores isso criou no modelo e por quê.

## Apêndice matemático — índice

Três itens, slides 11 a 13 do deck, **organizados por checkpoint** conforme a §6-bis. Material de estudo e consulta, autossuficiente — lido em casa com o notebook executado ao lado e o relatório por escrever.

| Item | O que estabelece | Checkpoint |
|---|---|---|
| **A.1** | **A conta de memória desta placa, e por que o `r` escolhido cabe.** A decomposição que o CP1 imprime, explicada linha a linha: por que a quantização de 4 bits **não** comprime o embedding, e por que a conta ingênua `1,5e9 × 0,5 byte` erra por ~0,33 GiB. Depois o orçamento inteiro do treino na T4 — pesos, adaptador com estados em 8 bits paginados, ativações com recomputação, e o **tensor de logits**, que é a maior parcela de ativação e é consequência direta do vocabulário. Uma **tabela de sensibilidade** mostrando o que cada alavanca move: `r` de 8 a 256, `MAX_LEN` de 320 a 2048, lote de 1 a 8, recomputação ligada e desligada. A conclusão é contraintuitiva e é o ponto do item: **`r` não é a restrição** — a memória toleraria `r` duas ordens de grandeza maior, e `r = 8` foi escolhido por causa dos 100 exemplos, não da placa. Mais a **regra de diagnóstico do `OOM`** que justifica a ordem de correção do §6. Aplica **A.5 da Aula 13** a este caso concreto e usa a contagem de **A.1 da Aula 13** sem repeti-la. | **CP1**, CP2, CP3 |
| **A.2** | **O que a curva de perda permite e não permite concluir.** A perda é a entropia cruzada média **por token sobre a sequência inteira** — e a sequência é, em boa parte, o prompt de sistema, **idêntico nos 100 exemplos**. A decomposição da sequência em tokens de sistema, de comentário e de resposta, com a estimativa de quanto da queda observada pode vir de memorizar uma constante. O que a curva **licencia**: que o gradiente chega ao adaptador (um diagnóstico de encanamento, e é exatamente o que o teste do CP4 afirma), e que não há divergência. O que ela **não** licencia: que a tarefa melhorou; comparação de valores absolutos entre execuções com `MAX_LEN` diferente ou com mascaramento diferente; comparação entre modelos com tokenizadores diferentes; e "não houve overfitting", porque 90 passos são ~4 épocas sobre 88 exemplos e três pontos de validação sobre `n = 12` não estabelecem tendência. O que seria necessário para concluir mais, item por item. E a **moldura que nomeia o diagnóstico**: viés e variância lidos **do par** `(L_treino, L_val)` e não de cada uma isolada, com a tabela de sintomas — treino alta e validação junto é **subajuste**; treino baixa e validação muito acima é **sobreajuste**; e a distância entre as duas, não o valor de uma delas, é o que nomeia o problema. Com `n = 88`, 4 épocas e `r = 8`, este lab é **estruturalmente propenso a variância** — capacidade não falta, dado falta —, o que torna a previsão a fazer antes de olhar a curva. Onde fica o botão do compromisso aqui: o posto `r`, e não o tamanho do modelo, que está congelado. E por que **parada antecipada** não está no notebook, apesar de ser o remédio padrão: 3 pontos de validação disparariam por ruído, e passos fixos mantêm as comparações entre duplas comparáveis. | **CP4** |
| **A.4** | **Achar o exemplo ruim entre os 88: auto-influência.** Com `n = 88`, um rótulo errado desloca o modelo de forma mensurável e nada no lab avisa — a curva não avisa (A.2 explica por quê), o teste do CP4 não avisa, e o CP5 dilui. O procedimento: a auto-influência de um exemplo é `TracIn(x,x) = η·‖∇L(x)‖²`, ou seja **a norma do gradiente ao quadrado e mais nada**; ordena-se os 88 por ela e **leem-se os dez primeiros à mão**. Custo: 88 passes para trás sobre o adaptador, da ordem de uma época. A correção obrigatória em texto — dividir por `T(x)`, porque a norma cresce com o comprimento e a lista bruta é a lista dos exemplos mais **longos**. A leitura correta: auto-influência alta é **atipicidade**, e rótulo errado é só uma das causas — por isso o último passo é humano, e apagar os dez primeiros sem ler remove justamente os casos difíceis. E a condição que invalida o método: se houver rótulos errados demais, o modelo aprende o padrão errado e a lista **se inverte**. | **CP2** |
| **A.3** | **Por que cinco prompts é ilustração e não medição.** A resolução do instrumento com `n = 5`: 20 pontos percentuais, quatro vezes mais grossa que a do Lab 3. O erro-padrão de uma proporção com `n = 5`, e o ponto exato em que o intervalo de Wald **sai de [0,1]** — que é onde a premissa (iii) do A.3 do Lab 3 cai e onde o intervalo de Wilson passa a ser obrigatório. A comparação pareada: no cenário mais favorável possível, com **todos os cinco** prompts mudando de lado na mesma direção, o `p`-valor exato bilateral é `2·(0,5)⁵ = 0,0625` — **ainda acima de 0,05**. Nenhum resultado possível neste conjunto atinge o nível de 5%. E a distinção que salva o lab: cinco prompts licenciam afirmar que **a forma da saída mudou** (afirmação categórica, verificável por leitura) e não licenciam afirmar que **a taxa de acerto subiu** (afirmação sobre proporção). Mais os 3 prompts de controle como peneira de catástrofe, o tamanho de amostra necessário, e a redação honesta para o relatório. | **CP5** |

**O fio estatístico do curso — o terceiro elo, nos dois sentidos.** Este A.3 é o **terceiro** de quatro itens que fazem a mesma pergunta com fontes de ruído diferentes. *Para trás:* **A.5 da Aula 9 (Lab 2)** estabeleceu que uma semente não permite concluir nada e deu a régua `σ√2`; **A.3 da Aula 11 (Lab 3)** trocou a semente pela **amostra de prompts**, mostrou que com `n = 20` cada item vale 5 pontos percentuais e que são necessários **ao menos 6 itens discordantes** para a diferença ser distinguível do acaso. *Aqui*, o `n` cai para **5** e a conclusão endurece: nem o resultado máximo possível chega ao nível de 5% — e o intervalo de Wald, que lá era "a versão otimista", aqui devolve limites fora de `[0,1]`, o que torna a aproximação inutilizável. *Para a frente:* **A.5 da Aula 28 (Lab 8)** paga as duas dívidas que este item deixa em aberto — o **intervalo de Wilson**, que é o que se usa quando o Wald falha, e o **teste de McNemar** no caso geral, do qual o `2·(0,5)ᵐ` usado aqui é o caso particular com uma célula vazia. A **Aula 27** é onde o problema é enunciado no nível conceitual. Quem seguir os quatro na ordem vê a mesma ideia crescendo de uma semente até uma decisão de produto.
