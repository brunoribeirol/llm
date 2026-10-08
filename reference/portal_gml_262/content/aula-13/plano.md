---
aula: 13
titulo: "SFT e fine-tuning eficiente: LoRA e QLoRA"
modulo: "3 — Treinamento: pré-treino, SFT e PEFT"
tipo: teorica
semana: 7
duracao_min: 120
versao: v2
---

# Aula 13 — SFT e fine-tuning eficiente: LoRA e QLoRA

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** A aula é conduzida por três sintomas observáveis — o modelo que
> continua a lista em vez de responder, o fine-tuning que não cabe na placa, e o modelo que
> depois do ajuste esqueceu o que fazia antes. O fundamento matemático aparece **enunciado e
> lido** no fluxo, com a derivação completa no apêndice do deck (itens A.1 a A.7). Carga
> horária, numeração e objetivos de aprendizagem permanecem os da V1; o que muda é a ordem de
> apresentação e onde a conta é feita. O índice do apêndice está ao fim deste plano.

## 1. Objetivo da aula

Fechar a distância entre o que a fábrica da Aula 12 entrega — um completador de texto — e um assistente utilizável, mostrando que essa transformação é um problema de **comportamento**, não de conhecimento, e que ela custa uma fração ínfima do pré-treino quando se treina o adaptador certo em vez do modelo inteiro. Ao final, o aluno decide entre prompting, RAG e fine-tuning com um critério explícito em vez de por reflexo.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Explicar** por que um modelo pré-treinado continua texto em vez de responder, e **justificar** por que esse comportamento é a consequência correta do objetivo de pré-treino e não um defeito.
2. **Descrever** o que o SFT muda e o que ele não muda: a mesma perda de próximo token, sobre dados de instrução formatados por um template de chat com tokens especiais de papel.
3. **Identificar** os dois riscos do SFT — esquecimento catastrófico e overfitting em dataset pequeno — pelos sintomas observáveis de cada um.
4. **Calcular** o número de parâmetros treináveis de uma configuração LoRA (`r · (d_in + d_out)` por módulo) e **expressá-lo** como fração do modelo base.
5. **Explicar** por que a inicialização `B = 0` faz o modelo adaptado começar idêntico ao base, e por que os adaptadores podem ser fundidos sem custo de latência na inferência.
6. **Distinguir** quantização para inferência de quantização para treino, e **descrever** o que o QLoRA congela em 4 bits e o que mantém em precisão alta.
7. **Aplicar** o framework de decisão prompting × RAG × fine-tuning a um caso novo, nomeando o que a alavanca escolhida resolve, o que ela não resolve e o que nenhuma das três resolve.

*(Idênticos aos da V1. A reorganização não altera o que o aluno deve saber fazer; ela altera de onde ele parte para chegar lá — dos sintomas em vez das definições.)*

## 3. Teoria aplicada

Os três sintomas que abrem a aula são verificáveis, e cada um é fechado por um conceito específico:

| Sintoma | O que se observa | Fecha em |
|---|---|---|
| **1 — o modelo continua a lista** | `"Qual a capital da França?"` → `"…e a capital da Itália? Qual a capital da Alemanha?"` | Conceitos 1 a 3 (SFT e template) |
| **2 — o treino não cabe** | fine-tuning completo de um 7 B pede 112 GB de estado; a placa tem 24 GB, e a T4 do Colab tem 16 | Conceitos 7 a 11 (LoRA, QLoRA) → **A.5** |
| **3 — o modelo esqueceu** | depois do ajuste, 100% de aderência ao formato treinado **e** erro em conta que antes acertava | Conceito 5 (esquecimento) |

### Bloco 1 (00:10–00:55) — Do completador ao assistente: SFT e seus riscos

**Conceito 1 — O sintoma 1: o pré-treinado não está errado.**
*Comportamento observável:* diante de `"Qual a capital da França?"`, uma continuação de altíssima probabilidade é `"Qual a capital da Alemanha? Qual a capital da Itália?"` — porque no corpus essa string quase sempre aparece dentro de uma lista de exercícios, não dentro de um diálogo. É exatamente o gancho com que a Aula 12 fechou: a fábrica entrega um completador de texto.
*A causa:* o modelo está fazendo exatamente o que foi treinado para fazer. O que falta não é conhecimento — a probabilidade que ele atribui a `Paris` depois de `"a capital da França é"` é altíssima. Falta a convenção de que, diante de uma pergunta, o papel dele é responder.
*Analogia do instrutor:* é um ator que decorou a peça inteira, todas as falas de todos os personagens, e nunca foi informado de qual papel ele interpreta. Ele sabe o texto; ele não sabe a vez dele.
*Erro conceitual comum:* concluir que o modelo-base "é pior". Ele não é pior nem melhor — é um objeto diferente, e para algumas coisas (continuação de código, densidade de log-verossimilhança, uso como base de fine-tuning) o base é o objeto **certo**. Cartões de modelo marcam isso explicitamente, e usar base onde se queria instruct é um dos erros de setup mais frequentes.

**Conceito 2 — SFT: mesma perda, dado diferente.**
Supervised fine-tuning continua a minimizar a entropia cruzada do próximo token — a mesma perda do Lab 2 e da Aula 12. Muda o dado: pares instrução-resposta escritos ou curados por humanos, tipicamente entre dezenas de milhares e alguns milhões de exemplos. A quantidade é irrisória perto do pré-treino: partes por milhão do total de tokens.
*Analogia:* o pré-treino é a graduação inteira; o SFT é a semana de integração que ensina onde bater o ponto.
*Erro conceitual comum:* achar que o SFT ensina fato novo. Com quatro ou cinco ordens de grandeza menos tokens que o pré-treino, o que o SFT move é **comportamento** — formato, papel, disposição a responder, aderência a instrução. Fato novo, quando entra, entra frágil e o modelo mistura com o que já tinha. Esse é o fundamento do framework de decisão do Bloco 2.

**Conceito 3 — Template de chat e tokens especiais de papel: o formato é a interface.**
*Comportamento observável, medido na demo:* mesmo arquivo de pesos, mesma máquina, mesma pergunta — e comportamento diferente, só porque quatro tokens especiais foram ligados e desligados.
Um diálogo não é texto solto: é uma sequência de turnos com papéis. Para representar isso num modelo que só vê tokens, adiciona-se um **template de chat** com tokens especiais que delimitam papel e turno — algo da forma `<|im_start|>system … <|im_end|>`, `<|im_start|>user … <|im_end|>`, `<|im_start|>assistant`. O template é a **interface** treinada: o modelo aprendeu a produzir a resposta *depois* do token que abre o turno do assistente. Inferência fora do template do treino faz o modelo cair de volta no comportamento de continuação — que é o sintoma 1 reaparecendo por outra porta.
*Analogia:* é o cabeçalho de um protocolo. HTTP sem o `\r\n\r\n` não é HTTP mais permissivo — é lixo.
*Erro conceitual comum:* concatenar `"Usuário: … Assistente:"` à mão e concluir que o modelo é ruim. O modelo é bom e está sendo chamado fora do protocolo dele. Cada família tem o seu template, e usar o de outra família degrada a qualidade de um jeito que parece problema de modelo.

**Conceito 4 — Comportamento de segurança começa no SFT.**
Recusar pedidos danosos, dizer que não sabe, pedir esclarecimento em vez de adivinhar — nada disso emerge do pré-treino, porque nada disso é o próximo token mais provável. Entra como **dado**: exemplos em que a resposta correta é uma recusa fundamentada, ou uma admissão de incerteza. O SFT estabelece o piso desse comportamento; a Aula 15 mostra por que só o SFT não basta — imitar bons exemplos não ensina o que evitar quando o caso não estava no conjunto.
*Erro conceitual comum:* tratar segurança como filtro externo ("um classificador na saída"). Filtro externo existe e é complementar, mas o comportamento de recusa que se vê num assistente moderno é, em boa parte, comportamento treinado — e por isso é vulnerável às mesmas fragilidades de qualquer generalização.

**Conceito 5 — O sintoma 3: esquecimento catastrófico.**
*Comportamento observável:* o modelo passa a acertar perfeitamente o formato pedido **e** passa a errar coisas que acertava antes — soma errado, perde qualidade num segundo idioma, esquece um fato factual que estava lá. Nenhum erro é levantado; a curva de perda do treino continua descendo bonito.
*A causa:* atualizar **todos** os pesos com um dado muito mais estreito que o de origem melhora dentro da distribuição nova e piora fora dela.
*Analogia:* é regravar em cima de uma fita. A faixa nova entra bem; o que estava embaixo não volta.
*Erro conceitual comum:* medir o fine-tuning só na tarefa-alvo. Sem um conjunto de controle **fora** do domínio treinado, o esquecimento é invisível — e é exatamente por isso que ele é chamado de catastrófico e não de "ruim". LoRA mitiga isso estruturalmente: com a base congelada, o que se aprende vive num delta pequeno e removível, e desligar o adaptador restaura o modelo original bit a bit. O que sustenta esse "bit a bit" é a inicialização de `B` em zero.
*Fundamento:* `ΔW = 0` no passo zero, e o adaptado é idêntico ao base. → **A.2**

**Conceito 6 — Overfitting em dataset pequeno: o que 100 exemplos podem e não podem.**
*Comportamento observável:* a perda de treino desce, a de validação para de descer ou sobe, e o modelo começa a devolver respostas do conjunto de treino levemente disfarçadas.
Os controles são os de sempre — divisão treino/validação, parada antecipada, taxa de aprendizado modesta, poucas épocas — e um específico do gênero: **inspecionar as gerações**, porque a perda de validação não captura repetição literal.
*Erro conceitual comum:* concluir que o fine-tuning funcionou porque a perda de treino caiu bonito. A perda de treino cair é o que ela faz. O sinal útil é a perda de validação junto com a leitura de amostras — e é isso que o Lab 4 vai pedir explicitamente na comparação antes × depois. O Checkpoint 4 do lab tem um item de apêndice dedicado ao que a curva de treino **não** permite concluir.

### Bloco 2 (01:05–01:50) — PEFT: LoRA, QLoRA e a decisão de qual alavanca puxar

**Conceito 7 — O sintoma 2: o fine-tuning completo não cabe.**
*Comportamento observável:* `CUDA out of memory` numa placa de 24 GB, treinando um modelo de 7 B cujos pesos ocupam 14 GB — a placa tem espaço para o modelo e não tem espaço para treiná-lo. Na T4 de 16 GB do Colab, o mesmo acontece com um modelo de 1,5 B.
*A causa:* atualizar todos os pesos exige os 16 bytes por parâmetro da Aula 12 — peso, gradiente, cópia mestre e os dois momentos do Adam. Para um 7 B são 112 GB de estados antes de qualquer ativação; para 1,54 B, 24,6 GB.
*Fundamento:* a conta de memória das três configurações — completo, LoRA e QLoRA — lado a lado, para o mesmo modelo. → **A.5**
*Erro conceitual comum:* achar que o problema é o tamanho do modelo. O problema é o tamanho do **aparato de treino**: os pesos em bf16 de 1,54 B ocupam 3,1 GB e cabem folgados. O que não cabe são os outros 14 bytes por parâmetro que existem só porque se quer atualizar todo mundo.

**Conceito 8 — LoRA: treinar um delta de baixo posto sobre pesos congelados.**
A ideia tem uma linha:

```
h = W₀·x  +  (α / r) · B · A · x        A ∈ ℝ^(r×d_in),  B ∈ ℝ^(d_out×r),  r ≪ min(d_in, d_out)
```

`W₀` fica **congelado**. Treina-se apenas `A` e `B`, cujo produto é uma matriz do mesmo formato de `W₀` mas de posto no máximo `r`. Três detalhes que não são detalhe:
(i) `A` é inicializada aleatória e `B` com **zeros**, de modo que `ΔW = 0` no passo zero e o modelo adaptado começa exatamente igual ao base — o treino nunca parte de um modelo estragado. → **A.2**
(ii) o fator `α/r` desacopla a escala do efeito do valor de `r`, o que permite variar `r` sem reajustar a taxa de aprendizado. → **A.3**
(iii) na inferência, `W' = W₀ + (α/r)·BA` pode ser **fundido** nos pesos, e a partir daí o custo de latência é exatamente zero — diferente de adaptadores em série, que acrescentam camadas e latência. → **A.3**
*Por que posto baixo basta:* a hipótese, sustentada empiricamente pelo artigo, é que a **atualização** necessária para adaptar um modelo já competente tem posto intrínseco baixo. Não se está ensinando uma capacidade nova; está-se reorientando capacidades que já existem, e essa reorientação vive num subespaço pequeno. → **A.1**
*Analogia:* o modelo base é um piano afinado. LoRA não constrói outro piano — é uma partitura fina que diz quais teclas enfatizar.
*Erro conceitual comum:* aumentar `r` esperando ganho monotônico. Postos maiores dão mais capacidade ao delta e mais chance de decorar o conjunto pequeno; em datasets de instrução modestos, `r` entre 8 e 32 costuma ser suficiente, e o que mais muda o resultado é **quais módulos** recebem adaptador, não o valor de `r`.

**Conceito 9 — A conta que é o ponto pedagógico: quantos parâmetros de fato.**
*Número que a aula produz:* **0,60%**. Por módulo adaptado, LoRA acrescenta `r · (d_in + d_out)` parâmetros treináveis. No modelo de referência do Lab 4 (`d_model = 1536`, 28 camadas, adaptadores nas sete projeções de cada camada, `r = 8`), isso dá 329.728 por camada e **9.232.384** no modelo — 0,60% de 1,54 B. Em bytes de disco, o adaptador tem ~18 MB em bf16 contra ~3,1 GB do base: um servidor mantém uma base em memória e troca N adaptadores em tempo de execução, um por cliente ou por tarefa.
*Fundamento:* a contagem por módulo, a tabela completa dos sete módulos, a conferência de que os módulos adaptados somam 1,31 B dos 1,54 B do modelo, e o ponto em que aumentar `r` deixa de economizar parâmetro. → **A.1**
*Erro conceitual comum:* confundir "0,6% dos parâmetros treináveis" com "0,6% do custo de treino". O forward e o backward atravessam o modelo **inteiro** — o que se economiza é memória, não computação. A conta em FLOPs está em **A.5** e o número é ~2/3 do custo completo, não 0,6%.

**Conceito 10 — Quantização: duas finalidades que se confundem.**
Quantizar é representar pesos com menos bits. As duas finalidades são diferentes e é aqui que a turma mistura:
- **Para inferência:** reduz permanentemente a memória e melhora a vazão. Formatos de 8 e 4 bits (int8, GPTQ, AWQ, as variantes GGUF que a turma usou no Ollama) trocam um pouco de qualidade por caber na máquina. A degradação é real, medível, e cresce quando se desce abaixo de 4 bits.
- **Para treino:** o peso quantizado é o que está **congelado**. Ele é desquantizado por bloco na hora de calcular e nunca é atualizado; o gradiente atravessa esse peso para chegar ao adaptador, que vive em precisão alta. Não se está treinando em 4 bits — está-se treinando *em cima* de algo armazenado em 4 bits.

*Fundamento:* por que o gradiente pode atravessar um peso quantizado sem estimador de passagem direta, e qual é exatamente a lista do que o QLoRA mantém em precisão alta. → **A.4**. E, antes disso, **o que a operação é**: o mapeamento afim `FP32 → INT8` nos dois esquemas padrão — *absmax*, simétrico, uma constante, para pesos; **ponto-zero**, assimétrico, duas constantes, para ativações pós-ReLU, onde ele compra um bit de resolução por não assumir simetria onde não há. Com o erro `ε = X − (X_quant)_dequant`, seu limite de meio passo, e a taxonomia **PTQ × QAT**. → **A.6**
*Erro conceitual comum:* supor que treinar sobre base quantizada quantiza o que se aprendeu. O adaptador sai em precisão alta; a base é que está comprimida. E o corolário prático: um adaptador treinado contra uma base de 4 bits foi otimizado *contra aquela base* — fundi-lo numa base em bf16 funciona, mas não é matematicamente equivalente, e a comparação honesta reporta em qual base o número foi medido.

**Conceito 11 — QLoRA: a combinação que fez isso caber no Colab.**
Dettmers et al. juntaram três coisas: **NF4** (um tipo de dado de 4 bits com quantis desenhados para pesos aproximadamente normais, aplicado por bloco), **dupla quantização** (quantizar também as constantes de quantização, economizando fração de bit por parâmetro) e **otimizadores paginados** (mover estados do otimizador para memória do host nos picos, em vez de estourar). Com isso, a base de um modelo de 1,54 B ocupa ~0,79 GB em vez de ~3,1 GB, e sobra GPU para ativações e para o adaptador.
*Números que a turma vai medir amanhã:* base de 1,54 B em NF4 ≈ 0,79 GB; adaptador `r = 8` ≈ 18 MB; pico de treino no Lab 4 na casa de poucos gigabytes com lote 1, acumulação de gradiente e recomputação de ativações ligada.
*Fundamento:* como os 16 níveis do NF4 são escolhidos e quanto exatamente a dupla quantização economiza. → **A.4**. A conta de memória que compara as três configurações e mostra que a economia é de 26×. → **A.5**. Por que o bloco é de 64 e não do tensor inteiro: um único *outlier* em `2,0` num bloco que vive em `[−0,1; 0,1]` multiplica por **7** o erro de todos os vizinhos — o bloco pequeno é o que confina o estrago. → **A.6**
*Erro conceitual comum:* atribuir a QLoRA um ganho de qualidade. QLoRA é uma técnica de **viabilidade**: ela faz caber. A qualidade tende a ficar próxima do LoRA em base não quantizada, e a comparação sem declarar a base é a mesma falha de proveniência que o Lab 3 cobrou.

**Conceito 12 — O framework de decisão: prompting × RAG × fine-tuning.**
Este é o conceito que volta na Aula 18 e no projeto final, e ele merece ser decorado como tabela:

| Alavanca | Resolve | **Não** resolve | Custo | Latência de mudança |
|---|---|---|---|---|
| **Prompting** | formato leve, tom, tarefa nova sem dado, instrução pontual | conhecimento que o modelo não tem; consistência em escala; custo de tokens por requisição | ~zero de treino; tokens em toda chamada | minutos |
| **RAG** | conhecimento privado ou que muda; fato com citação e fonte auditável | comportamento, estilo, aderência a esquema; qualidade limitada pelo recuperador | infraestrutura de índice e ingestão | horas (reindexar) |
| **Prompt otimizado** | o mesmo que prompting, **com consistência em escala** — o otimizador reescreve a instrução contra uma métrica em vez de você reescrever no olho | conhecimento ausente; e exige **conjunto rotulado e métrica automática**, sem os quais não há o que otimizar | dezenas a poucos milhares de execuções de avaliação; zero GPU de treino | horas |
| **Fine-tuning** | comportamento, formato rígido, estilo, jargão de domínio, encurtar prompt | injetar fato que muda; garantir factualidade; auditar a origem da resposta | GPU + dados curados + avaliação | dias (retreinar) |

E o que **nenhuma das três** resolve: garantir que a resposta esteja correta. Isso exige medição (Aula 27) e, quando o fato é verificável, uma ferramenta que verifique (Aula 21).
*O erro clássico, que eu quero nomeado em voz alta:* tentar injetar por fine-tuning um fato que muda — preço, política vigente, catálogo, tabela de horários. Fine-tuning não é banco de dados: o fato entra fraco, mistura com o antigo, não tem fonte citável e fica errado na semana seguinte. Fato que muda entra por recuperação ou por ferramenta. Fine-tuning entra quando o problema é **como** o modelo responde, não **o que** ele sabe.
*Terceiro erro, e é o que a quarta linha da tabela existe para matar:* ler a tabela como uma **escada de poder**, em que prompting é o degrau fraco e treinar peso é o forte. Não é, e agora há resultado publicado que derruba: o **GEPA** (ICLR 2026) otimiza **só o texto do prompt** e supera o **GRPO** — o algoritmo da Aula 16, que treina peso — em 6% na média e até 20%, usando **até 35× menos execuções**. Escrever prompt à mão é fraco; otimizar prompt contra uma métrica não é. O pré-requisito, que é o que restringe a alavanca, é o mesmo do Lab 8: conjunto rotulado e métrica automática. → **A.7**
*Segundo erro, mais sutil:* usar as três como se fossem exclusivas. Sistemas reais combinam — fine-tuning para o formato e o jargão, RAG para o fato, prompting para o ajuste fino do turno. O framework existe para escolher **por onde começar**, não para escolher uma só.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura pelos três sintomas | Recap da Aula 12 pelo que a fábrica **entregou** (um completador de texto); os três sintomas do dia projetados juntos, cada um verificável; o anúncio de que os três se fecham hoje e o segundo se fecha por uma conta de memória |
| 00:10 | 45 min | Bloco 1 — Do completador ao assistente | Sintoma 1 fechado: o pré-treinado não está errado; **demo "os mesmos pesos, dois comportamentos" (10 min)**; SFT como mesma perda com dado de instrução; template de chat como protocolo; comportamento de segurança como dado; **sintoma 3 nomeado** (esquecimento catastrófico e o conjunto de controle que o torna visível); overfitting em 100 exemplos e os sinais |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — PEFT e a decisão | **Sintoma 2 fechado:** a conta de memória do fine-tuning completo (A.5); LoRA (`ΔW = BA`, `B = 0`, `α/r`, fusão sem latência, por que posto baixo basta); a conta dos treináveis (**0,60%** e o adaptador de ~18 MB); quantização para inferência × para treino; QLoRA (NF4, dupla quantização, otimizador paginado); framework prompting × RAG × fine-tuning; **exercício de decisão em dupla (5 min)** |
| 01:50 | 10 min | Fechamento | Síntese: fine-tuning compra forma, não fato; o mapa do Lab 4 de amanhã com os números esperados; um item do apêndice nomeado (A.5, a conta que fecha o sintoma 2); ponte para a Aula 14; leituras (LoRA 2106.09685, QLoRA 2305.14314) |

*Comparação com a V1: o quadro de aritmética do LoRA passou de ~6 min de soma conduzida para 2 min de leitura de um módulo e da razão; a tabela dos sete módulos e a conferência de que eles somam 1,31 B dos 1,54 B foram para A.1, mais detalhadas do que estavam. Os minutos liberados foram para a abertura pelos três sintomas e para a correção do exercício de decisão, que na V1 vivia comprimida em 2 min.*

## 4. Demonstração guiada

**"Os mesmos pesos, dois comportamentos" — 10 min (00:10–00:20), navegador e quadro. Por isso esta aula não tem pasta `codigo/`.**

A demonstração tem duas metades: a primeira fecha o sintoma 1 mostrando que o template de chat é a interface, usando o modelo que a turma já tem do Lab 3; a segunda produz o número do Bloco 2.

Passos em alto nível:

1. Abrir o cartão de um modelo aberto pequeno no Hugging Face e mostrar que a mesma família publica duas variantes: a base e a *instruct*. Ler em voz alta o aviso do cartão da base — que ela não foi ajustada para seguir instruções e não deve ser usada como assistente.
2. No Ollama local, enviar `"Qual a capital da França?"` pelo caminho de **chat** (com template aplicado) e mostrar a resposta bem-comportada.
3. Enviar exatamente o mesmo texto pelo caminho de **completion cru**, com o template desligado (`raw`), e mostrar o modelo voltando a continuar texto — mais perguntas, uma lista, um parágrafo qualquer. Mesmos pesos, comportamento diferente: a diferença está nos tokens de papel. **É o sintoma 1 reproduzido ao vivo, e o fecho dele na mesma tela.**
4. Abrir o `tokenizer_config.json` do modelo (ou o campo de template no cartão) e projetar a string do template. Apontar os delimitadores de turno e o token que **abre** o turno do assistente — é depois dele que o modelo aprendeu a responder.
5. No quadro, a conta do LoRA para **um** módulo: uma projeção `1536 × 1536` tem 2.359.296 pesos; o adaptador com `r = 8` tem `8 × (1536 + 1536) = 24.576`. Ler a razão: cerca de 1% daquele módulo.
6. Escrever os dois totais já conferidos — 329.728 por camada, 9.232.384 no modelo — e fazer a única divisão da aula: `9.232.384 / 1,54 × 10⁹ = 0,60%`. A soma dos sete módulos está na tabela do slide e em A.1; o quadro faz um módulo e a razão, não a soma inteira.
7. Fechar mostrando, na página de um repositório de adaptador LoRA no Hugging Face, o tamanho do arquivo do adaptador — dezenas de megabytes — ao lado do tamanho do modelo base. É o mesmo argumento da conta, agora em bytes de disco.

**Número que a demo produz.** **0,60%** — a fração de parâmetros treináveis de uma configuração LoRA `r = 8` sobre as sete projeções do modelo de referência. O número é citado de volta em três lugares do fluxo: no **slide 11**, onde ele é o título; no **slide 13**, onde é ele que explica por que sobra placa depois da base em NF4; e no **slide 16**, no mapa do Lab 4, onde o Checkpoint 3 imprime exatamente essa porcentagem e o aluno confere contra a conta feita à mão. Um `print` que o aluno não sabe conferir não é conhecimento — é fé, e a demo existe para que a conferência de amanhã tenha com o que ser conferida.

Insumos preparados antes da aula: o modelo do Ollama já baixado na máquina do instrutor; capturas de tela das duas chamadas (chat e cru) feitas na véspera, para o caso de a máquina ou a rede falharem; o template do tokenizador salvo num arquivo de texto local; a conta do LoRA já conferida no papel, porque errar essa divisão na frente da turma custa o slide seguinte.

## 5. Hands-on

**Componente prático da unidade — exercício de decisão em dupla, "qual alavanca?" (5 min, 01:45–01:50).**

Quatro casos projetados. Para cada um, a dupla escreve: (a) a alavanca primária — prompting, RAG ou fine-tuning; (b) uma frase dizendo o que essa alavanca resolve no caso; (c) uma frase dizendo o que ela **não** resolve e de onde vem a solução dessa parte.

1. Um assistente precisa responder perguntas sobre o regulamento da universidade, citando o artigo exato.
2. O modelo acerta a classificação mas responde em prosa livre; a integração exige um rótulo puro, sempre, sem exceção. (É literalmente a segunda coluna que a turma mediu no Lab 3.)
3. O sistema precisa escrever laudos em português técnico de um domínio, com o jargão e a estrutura do setor.
4. O preço dos produtos muda toda semana e o assistente precisa informá-lo corretamente.

*Critério de conclusão observável:* as quatro linhas preenchidas, com a alavanca nomeada e a coluna "não resolve" preenchida em todas — é essa coluna que vale. Nomear a alavanca sem preencher a terceira coluna não fecha o exercício.

*Correção* conduzida em 3 min no fechamento, com atenção ao caso 4: a resposta certa não é nenhuma das três isoladamente — é ferramenta ou consulta a fonte viva (Aula 21), e quem escreveu "fine-tuning" acabou de cometer o erro clássico na frente de si mesmo, que é o melhor lugar para cometê-lo.

*Extensão opcional, para quem terminar antes:* refazer a contagem de parâmetros treináveis com `r = 16` e com adaptadores **só** nas quatro projeções de atenção, e dizer qual das duas mudanças move mais o número. **Gabarito em A.1**, na tabela de variações — é o cálculo que na V1 era tarefa obrigatória de casa e aqui vira aprofundamento com resposta escrita.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Ollama indisponível** na máquina da sala (modelo não baixado, rede da sala) | Chamada não responde nos primeiros 30 s | Capturas de tela das duas chamadas (chat × cru) feitas na véspera; a segunda metade da demo é no quadro e não depende de máquina nenhuma |
| **A demo do caminho cru não muda o comportamento** — modelo instruct muito robusto responde mesmo sem template | As duas saídas ficam parecidas | Dizer isso em voz alta e usar como conteúdo: o SFT foi forte o suficiente para sobreviver ao template errado, e o efeito completo aparece na variante **base**, cujo cartão está aberto no passo 1. Não insistir mais de 60 s |
| **A turma pedir a derivação em aula** | "por que `B` em zero e não as duas aleatórias?"; "de onde vem o `α/r`?" | A Parte 4 do roteiro tem as quatro conduções, com o custo em minutos e a versão de 30 segundos de cada uma. Fazer no máximo **uma**, e só se o Bloco 2 estiver adiantado |
| **Turma sentir que "faltou rigor"** | Comentário de que a aula ficou superficial | Projetar o índice do apêndice por 30 s: sete itens, e o A.5 é a conta comparativa de memória que a Aula 12 já apontava. O rigor não saiu, mudou de lugar — e agora é consultável |
| **"Mas o que é quantizar, exatamente?"** no meio do Conceito 11 | Pergunta legítima, e ela revela que a turma vinha usando "4 bits" como rótulo | Responder em uma frase — *trocar a régua: em vez de guardar o número, guardar em qual das 256 marcas ele caiu, mais a régua* — e apontar **A.6**, que tem as duas constantes derivadas e a regra de escolha. **Não** abrir em sala: são cinco minutos que saem do framework de decisão, que é o clímax |
| **Turma confunde SFT com pré-treino** ("então é só treinar mais?") | Perguntas sobre quantos tokens de SFT são necessários | A comparação de ordens de grandeza está no Conceito 2 e tem número: partes por milhão do total de tokens do pré-treino. Insistir na consequência — o que muda é comportamento, não conhecimento |
| **A conta do LoRA sai errada no quadro** | Aritmética travando ao vivo | Na V2 o quadro faz **um** módulo e a divisão final; a soma dos sete está no slide e em A.1. Se travar, ir direto ao total e à razão `9,2 M / 1,54 B` — a razão é o que importa |
| **Turma quer decidir `r` "ótimo"** | Discussão longa sobre hiperparâmetro | Resposta honesta e curta: para dataset de instrução modesto, `r` de 8 a 32 e o que mais muda é quais módulos recebem adaptador. Empurrar a curiosidade para a extensão opcional do exercício, cujo gabarito está em A.1, e para o Lab 4, que mede |
| **Bloco 2 estourar o tempo** | 01:38 e ainda em QLoRA | Cortar dupla quantização e otimizador paginado, que são detalhe de implementação e estão escritos em A.4, e **proteger** o framework de decisão do Conceito 12 — ele volta na Aula 18, no projeto final e na prova. O exercício em dupla pode virar tarefa de casa |
| **Expectativa de "fine-tuning resolve alucinação"** | Alguém propõe treinar o modelo nos documentos da empresa para ele "saber" o conteúdo | É o erro que o framework existe para nomear; a tabela do Conceito 12 responde e a Aula 18 (RAG I) desenvolve. Não deixar passar sem nomear em voz alta, porque é a proposta de projeto final que mais aparece |

## 7. Artefatos produzidos

- **Folha do exercício de decisão:** quatro casos × alavanca × o que resolve × o que **não** resolve. É o artefato central da aula na V2, e é o instrumento que o aluno leva para a proposta do projeto final na Aula 22.
- Anotação da conta do LoRA: o módulo feito no quadro, os dois totais e a fração em porcentagem — a mesma conta que o aluno vai conferir contra a saída de `print_trainable_parameters()` no Lab 4.
- **Tabela do framework de decisão** copiada com as três colunas (resolve, não resolve, custo).
- Anotação do template de chat do modelo escolhido, com os tokens de papel destacados — insumo direto do Checkpoint 2 do Lab 4.
- *(Opcional, extensão)* a contagem refeita com `r = 16` e com adaptadores só na atenção, conferida contra a tabela de variações de A.1.
- Nenhum arquivo de código nesta aula: a demonstração é de navegador e quadro, e o código do Módulo 3 vive no notebook da Aula 14.

## 8. Desafio pós-aula

Não avaliado, e curto de propósito — o Lab 4 é amanhã.

1. **Diagnóstico próprio.** Dos três sintomas de abertura, escolher um e descrever, em cinco linhas, como você o **detectaria** num modelo que você mesmo ajustou: que número você olharia, e que valor desse número faria você concluir que o sintoma está presente. Para o sintoma 3 a resposta não é "olhar a perda de treino", e é por isso que ele é o mais interessante dos três.
2. **Confirmar o ambiente do Lab 4.** Abrir o Colab, confirmar que a GPU está disponível (`Runtime → Change runtime type → T4`) e que a conta do Hugging Face funciona. Quem não tiver GPU vai cair no modo de fallback do notebook e medir um resultado apenas ilustrativo — melhor descobrir hoje.
3. **A conta com outro `r` (extensão do exercício).** Refazer a contagem com `r = 16` e com adaptadores só nas quatro projeções de atenção. Trazer os dois números e conferir contra a tabela de variações de **A.1**. No lab, a saída de `print_trainable_parameters()` vai ser confrontada com a conta feita à mão, e é essa conferência que fecha o conceito.
4. **Leitura — Hu et al., *LoRA* (arXiv 2106.09685).** Ler a introdução e a seção do método. **Pergunta dirigida:** o artigo inicializa `B` com zeros e `A` aleatoriamente. O que aconteceria se as duas fossem inicializadas aleatoriamente, e por que essa escolha importa mais no primeiro passo do que no centésimo? **A resposta completa está em A.2**, e vale comparar o que você respondeu antes de ler.
5. **Leitura de apoio — Dettmers et al., *QLoRA* (arXiv 2305.14314)**, a seção que descreve NF4. **Pergunta dirigida:** NF4 é apresentado como ótimo para pesos aproximadamente normais. Que propriedade dos pesos de um modelo pré-treinado justifica essa suposição, e o que aconteceria com pesos de distribuição muito diferente? **Casos-limite em A.4.**

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. Ela alimenta três instrumentos com peso já definido na ementa:

- **Laboratório 4 — parte dos 30%** (Aula 14, entrega em uma semana). Os conceitos desta aula são pré-requisito direto: sem entender template de chat, o Checkpoint 2 não fecha; sem a conta do LoRA, o Checkpoint 3 é um `print` sem significado.
- **Prova — 30%** (Aula 17, cobre as Aulas 1 a 16), cuja composição é: diagnóstico e interpretação de comportamento **42** · justificativa de escolha **40** · conceito aplicado **8** · derivação **10**.
- **Projeto final — 40%** (marcos nas Aulas 22, 26 e 30). O framework do Conceito 12 é o filtro de viabilidade das propostas: é ele que separa o grupo que vai injetar fato por fine-tuning — e falhar — do grupo que vai colocar o fato em recuperação e o comportamento em adaptador.

A V2 muda **como** esta aula é cobrada, e vale explicitar contra essa distribuição. Os três sintomas de abertura são exatamente o formato dos 42 pontos de **diagnóstico**: dado um comportamento (o modelo continua a lista; o treino estoura numa placa que caberia o modelo; o modelo acerta o formato e erra a conta), identificar a causa. O framework do Conceito 12, a conta de memória de A.5 e a regra de escolha entre absmax e ponto-zero de A.6 são o material dos 40 pontos de **justificativa** — dizer "usaria QLoRA" sem a conta que mostra o que não cabe não é justificativa suficiente, e escolher um esquema de quantização sem olhar a forma da distribuição do tensor é escolher no chute. A contagem de treináveis é o formato dos 8 pontos de **conceito aplicado**. E os 10 pontos de **derivação** saem de A.1 a A.4: a contagem por módulo, o argumento de `B = 0`, o papel do `α/r`.

*Observável em sala, sem nota:* ao ser questionado no fechamento, o aluno diz de cabeça a ordem de grandeza da fração de parâmetros treináveis de uma configuração LoRA típica, e classifica um caso novo nas três alavancas nomeando o que ela **não** resolve.

## Apêndice matemático — índice

Cinco itens, slides 17 a 21 do deck. Material de estudo e consulta, autossuficiente — quem estuda por aqui sem ter assistido à aula reconstrói todas as contas.

| Item | O que estabelece | Apontado do |
|---|---|---|
| **A.1** | A decomposição de baixo posto `ΔW = BA`: por que o produto tem posto no máximo `r` (a informação atravessa um gargalo de dimensão `r`), a contagem `r · (d_in + d_out)` por módulo derivada, a tabela completa dos sete módulos do modelo de referência com a soma por camada, a **conferência de que os módulos adaptados somam 1,31 B dos 1,54 B do modelo** (o resto é embedding), a fração 0,60%, a redundância de `r²` da parametrização, o ponto de equilíbrio `r < d_in·d_out/(d_in+d_out)` acima do qual o adaptador deixa de economizar, e a **tabela de variações que é o gabarito da extensão do exercício** (`r = 16`; só atenção). | slides 10 e 11 |
| **A.2** | Por que `B = 0` faz o adaptado começar **idêntico** ao base, e por que isso não congela o treino: no passo zero o gradiente de `B` é diferente de zero (porque `A` é aleatória) e o de `A` é zero, e a assimetria é o mecanismo. O que aconteceria com **as duas aleatórias** — a magnitude da perturbação injetada em cada módulo, o efeito composto ao longo de 28 camadas, e a distorção dos momentos do Adam calibrados sobre gradientes iniciais grandes. O que aconteceria com **as duas em zero** (ponto estacionário: o adaptador nunca sai do zero). E o invariante que realmente importa — `ΔW = 0` no passo zero —, do qual `B = 0` é a forma mais barata. | slides 8 (mitigação estrutural) e 10 |
| **A.3** | O fator `α/r`: o que ele desacopla e o que ele **não** desacopla. `ΔW` como `α` vezes a *média* de `r` termos de posto 1, e por isso a norma do delta não cresce com `r`; o que isso compra na prática (trocar `r` sem reajustar a taxa de aprendizado) e por que é heurística de escala, não teorema. As convenções `α = r` e `α = 2r`. A redundância entre `s` e a norma de `A`, `B`. O caso-limite `α = 0`, que é configuração morta e não adaptador fraco. Por que `α/√r` (rsLoRA) é proposto para `r` grande. E a fusão `W' = W₀ + s·BA` — exata, latência zero, reversível — com a ressalva de fundir sobre base quantizada. | slide 10 |
| **A.4** | Quantização NF4 e a lista exata do que o QLoRA mantém em precisão alta. Como os 16 níveis do NF4 são construídos por quantis de uma normal, com **zero exatamente representável** e por que isso importa. O custo real em bits por peso: 4,5 com constante fp32 por bloco de 64, **4,127** com dupla quantização, e a economia de 0,373 bit/peso convertida em MB. Por que o gradiente atravessa o peso quantizado **sem** estimador de passagem direta — o peso desquantizado é constante no grafo, e ninguém deriva em relação a ele. Casos-limite: outlier no bloco, pesos não normais (resposta à pergunta dirigida do QLoRA), fusão numa base bf16 que não é a base treinada, e o que acontece abaixo de 4 bits. | slides 12 e 13 |
| **A.5** | **A conta de memória das três configurações lado a lado**, para 1,54 B e para 7 B: fine-tuning completo (`16·N`), LoRA sobre base bf16 (`2·N + 16·N_a`) e QLoRA (`0,516·N + 16·N_a`), com os números que fecham o sintoma 2 — 112 GB contra 3,9 GB para o mesmo 7 B, uma razão de 29×. Mais o que a conta **não** inclui e é o que realmente estoura: as ativações, lineares em lote × contexto e quadráticas em contexto no termo da atenção. E a conta em **FLOPs**, que mostra que LoRA economiza no máximo 1/3 da computação e não 99,4% — o número que desfaz o erro conceitual do Conceito 9. Casos-limite: `r` grande, troca de otimizador, otimizador paginado, e N adaptadores servidos sobre uma base. | slides 9 e 13 |
| **A.6** | **O que quantizar é, mecanicamente** — o item que A.4 pressupõe e que a V1 não tinha em lugar nenhum. O mapeamento afim `FP32 → INT8` nos dois esquemas padrão, com as constantes derivadas: *absmax* (`c = 127/max|X|`, simétrico, uma constante) e **ponto-zero** (`s = 255/(max−min)`, `z = −round(s·min)−128`, assimétrico, duas constantes). A regra de escolha por **forma da distribuição** — absmax para pesos, que são centrados em zero; ponto-zero para ativações pós-ReLU, onde ele compra **um bit de resolução de graça** (`m/255` contra `m/127`). O erro `ε = X − (X_quant)_dequant`, seu limite de meio passo, e a leitura de que quantizar-e-desquantizar **não** é a identidade. O número que fixa a sensibilidade a *outliers*: um único valor em `2,0` num bloco que vive em `[−0,1; 0,1]` multiplica por **7** o erro de todos os vizinhos e engrossa a grade em **20×** — que é a justificativa quantitativa dos blocos de 64 do QLoRA e da separação de *outliers* do `LLM.int8()`. Fecha com **PTQ × QAT** e com a resposta de que o QLoRA não é nenhum dos dois: é PTQ aplicada a um artefato que será usado como constante, e é isso que autoriza o gradiente a atravessá-lo. Casos-limite: tensor todo zero, distribuição já simétrica, um valor dominante, e por que abaixo de 4 bits a grade uniforme deixa de servir. | slide 12 |
| **A.7** | **A quarta alavanca: o prompt como objeto otimizável.** O item que impede a leitura da tabela do Conceito 12 como escada de poder. Dado um sistema com prompts, um conjunto rotulado e uma métrica automática, um otimizador procura no espaço dos textos de instrução — sem tocar em peso. O mecanismo do **GEPA** em quatro passos: executar e registrar a trajetória inteira (raciocínio, chamadas e saídas de ferramenta, resultado); **refletir em linguagem natural** sobre ela para atribuir crédito ao módulo culpado; propor uma reescrita e admiti-la só se melhorar num minilote; e **amostrar da fronteira de Pareto** — a melhor candidata *por instância*, não a melhor global — para não travar em ótimo local. Os números em seis tarefas: **+6% sobre o GRPO na média e até +20%, com até 35× menos execuções**; +10% sobre o MIPROv2. A tese, que é a mesma do sinal denso da Aula 8 num nível acima: recompensa escalar extrai um bit por execução, reflexão sobre a trajetória extrai um parágrafo. As **três condições** sem as quais não se aplica (conjunto rotulado, métrica barata, trajetória legível) e os três lugares onde ela não é a resposta (conhecimento ausente, encurtar prompt, estender capacidade). Casos-limite: conjunto pequeno e sobreajuste do conjunto de otimização; métrica mal especificada produzindo *reward hacking* sem RL nenhum; sistema de módulo único. | slide 14 |

**Referência cruzada, nos dois sentidos.** A **A.4 da Aula 12** decompõe os 16 bytes por parâmetro nos quatro consumidores e a **A.5 da Aula 12** trata o custo de comunicação de cada paralelismo; as duas apontam para cá quando dizem que *a conta comparativa completa está em A.5 da Aula 13*. Este apêndice não redereiva os 16 bytes — ele os usa como insumo declarado e acrescenta as duas colunas que só existem porque a base pode ser congelada e comprimida. Para a frente, o **A.1 do Lab 4 (Aula 14)** aplica A.5 ao caso concreto da T4 do Colab e responde por que o `r` escolhido cabe.
