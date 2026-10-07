---
aula: 5
titulo: "Modelos sequenciais e o nascimento da atenção"
modulo: "1 — Fundamentos: do texto ao Transformer"
tipo: teorica
semana: 3
duracao_min: 120
versao: v2
---

# Aula 5 — Modelos sequenciais e o nascimento da atenção

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (medição, anotação de diagnóstico), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** O fluxo da aula é conduzido por três sintomas observáveis —
> tradução que degrada com o comprimento, modelo que não aprende dependência longa, GPU
> ociosa no treino; a matemática entra como fundamento nomeado, com a derivação completa no
> apêndice do deck (itens A.1 a A.6). Os objetivos de aprendizagem, a carga horária e a
> numeração permanecem os da V1 — o que muda é a ordem de apresentação e onde a derivação é
> feita.

## 1. Objetivo da aula

Fazer o aluno sair capaz de **diagnosticar** três limitações de modelos recorrentes a partir
de comportamento observável e, sobretudo, de distinguir qual mecanismo ataca qual limitação.
O LSTM melhora o caminho da memória e do gradiente; a atenção de Bahdanau remove o gargalo do
contexto fixo ao trocar compressão por acesso, mas **mantém encoder e decoder recorrentes**; o
Transformer da Aula 6 é que retira a recorrência e libera o paralelismo no treino. A aula fecha
reconhecendo os papéis Query, Key e Value sem fingir que a formulação de 2014 já é a de 2017.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Ler** a recorrência `h_t = f(h_(t-1), x_t)` e **explicar** por que a ordem dos tokens
   altera a saída e por que o número de parâmetros não depende do comprimento (fundamento em
   A.1).
2. **Diagnosticar** um modelo que não aprende dependências longas a partir do produto de
   fatores no caminho de volta, e **distinguir** o problema de otimização do problema de
   capacidade (derivação em A.2).
3. **Identificar** quais das três dívidas estruturais (dependência longa, gradiente, ausência
   de paralelismo) o LSTM ataca e quais ele deixa intactas, e **justificar** o veredito de
   cada uma (equações em A.3).
4. **Diagnosticar** o gargalo do vetor de contexto fixo em uma arquitetura seq2seq a partir da
   curva de qualidade × comprimento, e **prever** em que tipo de entrada ele falha primeiro
   (argumento em A.4).
5. **Interpretar** um vetor de contexto de Bahdanau a partir de scores de alinhamento dados —
   dizer para onde o modelo olhou, o que mudaria se os scores mudassem de escala — e
   **calcular** `α_(t,j)` e `c_t` quando pedido (derivação e exemplo numérico em A.5).
6. **Mapear** os papéis Query, Key e Value sobre a atenção aditiva — consulta derivada do
   estado do decoder, chave derivada de cada estado do encoder e valor lido desse estado — e
   **distinguir** esse mapeamento conceitual das projeções matriciais da Aula 6 (A.6).

*(Idênticos aos da V1. O que mudou foi o verbo dominante: de "derivar" e "calcular" para
"diagnosticar" e "justificar" — a derivação permanece disponível e cobrada como fundamento da
justificativa.)*

## 3. Teoria aplicada

Cada conceito abaixo é apresentado pelo comportamento que o motiva, com o fundamento
matemático nomeado e a derivação remetida ao apêndice.

### Bloco 1 (00:10–00:55) — Três sintomas e três causas que não devem ser confundidas

**Conceito 1 — O sintoma que abre a aula: erro que cresce com o comprimento.**
*Comportamento observável:* um tradutor de 2014 acerta frases curtas e desmonta em frases
longas; a curva de qualidade × comprimento é plana até cerca de 30 palavras e cai a partir
daí. O erro é **função do comprimento da entrada**.
*Leitura diagnóstica:* a curva torna o gargalo arquitetural uma hipótese forte, não uma prova
isolada. Antes de concluir, controla-se a distribuição de comprimentos no treino e compara-se
o mesmo protocolo com e sem atenção. É esse controle que o artigo fornece.
*Erro conceitual comum:* tratar um sintoma como diagnóstico fechado. Poucos exemplos longos no
treino também podem produzir queda; o teste comparativo separa as hipóteses.

**Conceito 2 — Por que a intuição erra: "é só aumentar o vetor".**
Aumentar a dimensão do resumo interno pode ajudar, mas compra **espaço**, não **acesso**. O
decoder continua recebendo um único resumo, de tamanho fixo, para uma entrada de tamanho
variável; e o caminho computacional entre posições distantes continua crescendo.
*Nota de condução:* este conceito existe para gastar a intuição da turma antes de a solução
aparecer. Se alguém propuser "aumentar" espontaneamente, usar a proposta da pessoa.

**Conceito 3 — O conceito em uso: ler em ordem e carregar um resumo.**
A recorrência enunciada e lida: `h_t = f(h_(t-1), x_t)`, na forma clássica
`h_t = tanh(W_h h_(t-1) + W_x x_t + b)`. Três leituras: resumo comprimido; mesma matriz em
todos os passos, logo parâmetros independentes do comprimento; ordem importa porque composição
de funções não comuta.
*Fundamento:* desenrolamento, contagem de parâmetros e a prova de que a ordem importa. → **A.1**
*Erro conceitual comum:* imaginar que a rede guarda os tokens anteriores. Ela guarda um vetor
sobrescrito a cada passo.

**Conceito 4 — Segundo sintoma: dependência longa que nunca é aprendida.**
*Comportamento observável:* o modelo acerta a concordância a três palavras e nunca aprende a
concordância a quarenta. Loss descendo, sem `NaN`, sem divergência.
*Base de ML em três frases:* a *loss* é um número que mede o erro; o gradiente diz em que
direção e com que intensidade cada peso deve mudar; a retropropagação leva esse sinal do fim
para o início aplicando a regra da cadeia.
*Números feitos na calculadora à vista da turma:* `0.9^10 ≈ 0.35`, `0.9^50 ≈ 5·10⁻³`,
`0.9^100 ≈ 3·10⁻⁵`; `1.1^50 ≈ 117`, `1.1^100 ≈ 1.4·10⁴`.
*Fundamento:* o gradiente que chega ao primeiro passo é um produto de `T−1` derivadas de um
passo, e a norma desse produto decai ou cresce exponencialmente em `T`. → **A.2**
*Erro conceitual comum:* tratar como falta de capacidade. Mantido o ganho por passo, aumentar
só a dimensão não remove o expoente `T`; é um problema de otimização, e a solução mexe no
caminho do gradiente.

**Conceito 5 — Terceiro sintoma: o treino que não acelera com hardware melhor.**
*Comportamento observável:* GPU quatro vezes mais rápida, 15% de ganho por época, ocupação
baixa. Causa: `h_t` exige `h_(t-1)`, logo `T` etapas obrigatoriamente sequenciais.
*Erro conceitual comum:* imaginar que a dívida é de inferência. Gerar é sequencial em qualquer
arquitetura; o que a recorrência impede é o paralelismo no **treino**, onde a sequência inteira
já é conhecida.

**Conceito 6 — O que o gating do LSTM compra.**
As duas linhas enunciadas: `f_t, i_t, o_t = σ(W · [h_(t-1), x_t])` e
`c_t = f_t ⊙ c_(t-1) + i_t ⊙ g_t`. O sinal de mais cria um caminho de `c_(t-1)` a `c_t` que não
passa por multiplicação de matriz.
*O que se ganha, dito com precisão:* o LSTM **não elimina** o desaparecimento — ele o põe sob
controle da rede, que pode manter a porta aberta nos canais onde a dependência longa importa.
*Fundamento:* as seis equações completas e a derivada do caminho da célula, que é
`diag(f_t)` — diagonal e dependente do dado. → **A.3**
*Erro conceitual comum:* achar que as portas são regras programadas ("esta porta guarda o
sujeito"). São camadas densas com sigmoide; é o mesmo alerta que volta na Aula 6 sobre cabeças.

*Consequência histórica que fecha a dívida da Aula 3:* o **ELMo** (Peters et al., arXiv
1802.05365, 2018) popularizou
representações contextuais produzidas por LSTMs bidirecionais: o vetor de `banco` muda com a
frase, sem usar atenção. A conclusão correta é lógica, não cronológica: **contextualizar e
atender são operações diferentes**. A recorrência já contextualiza; Bahdanau acrescenta
acesso direto aos estados do encoder; o Transformer acrescentará contextualização por
self-attention sem recorrência, permitindo paralelismo no treino.

**Conceito 7 — O placar: quem resolve o quê.**

| Limitação | RNN simples | LSTM | Bahdanau (RNN + atenção) | Transformer (ponte para a Aula 6) |
|---|---|---|---|---|
| Memória/gradiente em longas distâncias | frágil | melhora, não elimina | cria um caminho curto até cada estado do encoder; a recorrência continua dentro deles | cria caminhos curtos entre posições |
| Vetor de contexto fixo no seq2seq | gargalo | gargalo permanece | **remove o gargalo**: um `c_t` por passo | não depende de um único resumo |
| Paralelismo no treino | não | não | **não**: encoder e decoder seguem recorrentes | **sim** dentro de cada sequência de treino |

O quadro evita a frase errada “a atenção resolveu tudo”. Bahdanau resolve o problema de
**acesso** que o artigo se propôs a resolver; o salto de paralelismo pertence à Aula 6.
*Nota de condução:* se o tempo estourar, cortar detalhe do LSTM — nunca este conceito. Sem as
três dívidas, o aluno decora o Transformer em vez de entendê-lo.

**Conceito 8 — Onde memória e acesso se concentram: `c = h_T`.**
*Comportamento observável:* é esta arquitetura que produz a curva do Conceito 1. O decoder
parte do último estado do encoder e não tem mais acesso à origem.
*Fundamento:* sob uma hipótese explícita de precisão finita, a capacidade da ponte é fixa
(`d·b` bits) enquanto o número de entradas possíveis cresce; além disso, o comprimento do
caminho da posição `j` até o passo `t` é `(n−j)+t`.
→ **A.4**
*Erro conceitual comum:* propor aumentar `d`. Isso desloca o limite de capacidade linearmente e
não muda um único termo do comprimento do caminho. Falta acesso, não espaço.

### Bloco 2 (01:05–01:50) — Acesso em vez de compressão

**Conceito 9 — Atenção de Bahdanau: um contexto por passo.**
As três linhas enunciadas e lidas, sem manipulação: score de alinhamento, softmax sobre as
posições, média ponderada. A consequência que resolve o Conceito 1: o caminho entre a posição
`j` da origem e o passo `t` do destino passa a ter comprimento **1**.
*Fundamento:* derivação das três etapas, prova de que `c_t` é combinação convexa dos `h_j`,
exemplo numérico e a razão de a mistura suave ser treinável. → **A.5**
*Erro conceitual comum:* achar que a atenção substitui o encoder. Em 2014 não substitui: os
`h_j` continuam saindo de uma RNN. A tese de que ela basta é de 2017.
*Limite que deve ficar explícito:* o acesso do decoder a cada `h_j` fica curto, mas produzir
os `h_j` ainda é recorrente. Bahdanau melhora dependências e remove o vetor fixo; não libera o
paralelismo que aparece no slide 5.

**Conceito 10 — A matriz de alinhamento como evidência.**
Linhas são passos do decoder, colunas são posições do encoder, cada linha soma 1. A diagonal
predominante e o bloco onde ela se rompe. **Nenhum rótulo de alinhamento foi usado no treino**
— o único sinal foi a tradução correta.
*Erro conceitual comum:* ler a matriz como explicação causal. Peso alto é correlação com a
decisão, não a razão dela; por isso os autores dizem alinhamento *suave*. A mesma cautela vale
para cabeças na Aula 6 e é assunto da Aula 27.

**Conceito 11 — Q, K, V: três papéis antes de três matrizes.**
Na notação funcional, a consulta é derivada do estado do decoder (`q_t = W_s s_(t-1)`), a
chave é derivada de cada anotação do encoder (`k_j = U_h h_j`) e o valor lido é a própria
anotação (`v_j = h_j`). O score aditivo ainda aplica `v_aᵀ tanh(q_t + k_j)`; portanto isso é
um **mapeamento de papéis**, não a identidade `QKᵀ` do Transformer.
*Fundamento:* a passagem da família de atenção aditiva para a atenção por produto interno —
projeções Q/K/V explícitas, cálculo matricial e self-attention — com o que cada troca compra.
→ **A.6**
*Erro conceitual comum:* dizer que Key e Value “são o mesmo vetor” sem nuance. Ambos partem de
`h_j`, mas a chave já passa por `U_h` dentro do score; o valor usado na soma é `h_j`.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas |
|---|---|---|---|
| 00:00 | 10 min | Abertura pelo sintoma | A curva de qualidade × comprimento; por que "aumentar o vetor" desloca a curva sem mudar a forma; a tese da aula |
| 00:10 | 45 min | Bloco 1 — três sintomas, três causas | A recorrência lida; pausa de base sobre loss/gradiente; o modelo que esquece o sujeito e os números da calculadora; a GPU ociosa; o que o gating compra; o placar comparativo; `c = h_T`; **demo com três medições (12 min)** |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — acesso em vez de compressão | As três linhas de Bahdanau lidas termo a termo; o caminho de comprimento 1; a matriz de alinhamento como evidência sem rótulo; Q/K/V e as duas perguntas abertas; **exercício de diagnóstico (8 min + 3 de correção)** |
| 01:50 | 10 min | Fechamento | A síntese em quatro elos; a pergunta aberta sobre a recorrência; ponte para a Aula 6; leitura com o apêndice ao lado |

*Comparação com a V1: o quadro algébrico passou de ~18 min de condução (regra da cadeia, três
fórmulas da atenção escritas e desenvolvidas, mapeamento Q/K/V) para 0 min de derivação
conduzida; esses minutos foram para a demo (de 6 para 12 min, agora com três medições) e para
o exercício de diagnóstico. A derivação permanece integralmente disponível em A.1–A.6, mais
detalhada do que estava.*

## 4. Demonstração guiada

**Demo "medir os três sintomas" — 12 min (00:43–00:55), quadro + NumPy.**

O script reproduzível da Medição 1 vive em `codigo/demo-gradiente-rnn.py`; as outras duas
medições são de quadro e de projetor. Nada depende de rede ou de biblioteca de deep learning.

Na V2 a demo deixa de ilustrar a arquitetura e passa a ser **a evidência** dos Conceitos 4, 8 e
1 — nessa ordem:

1. **Medição 1 — o produto que decide o gradiente (3 min).** O script multiplica `T` vezes uma
   transformação diagonal cujo ganho é exatamente 0,9 ou 1,1 e imprime a norma para
   `T = 10, 50, 200`. **Números produzidos:** `0,9^200 ≈ 7,1·10⁻¹⁰` e
   `1,1^200 ≈ 1,9·10⁸`: dezoito ordens de grandeza de diferença, com a mesma dimensão. A
   construção é deliberadamente simples para isolar o produto; ela não pretende simular uma
   RNN completa.
2. **Medição 2 — a compressão em quatro números (5 min).** No quadro: frase longa preparada, a
   turma comprime em quatro inteiros, a frase é apagada, e a turma tenta traduzir só com os
   quatro números. **Comportamento observável:** o tema é recuperado, a estrutura não. É a
   evidência do Conceito 8, e é a única medição que a turma produz com as próprias mãos.
3. **Medição 3 — a curva e a matriz (4 min).** Figura 2 de Bahdanau et al. (qualidade ×
   comprimento, com e sem atenção — uma curva cai a partir de ~30 palavras, a outra fica plana)
   e Figura 3 (a matriz de alinhamento, com o bloco onde a diagonal se rompe). Fecha o Conceito
   1 e abre o Conceito 10.

Insumos preparados na véspera: a Medição 1 já rodada com a saída salva em texto; a frase longa
escrita num papel, para não improvisar no quadro; as Figuras 2 e 3 baixadas localmente; e um
par curto PT→EN com inversão de ordem, para o caso de a projeção falhar.

## 5. Hands-on

**Componente prático da unidade — exercício de diagnóstico (8 min de dupla + 3 de correção,
01:39–01:50).**

Substitui o desenho da grade de alinhamento da V1, que vira extensão opcional. Três sintomas
reais; para cada um, a dupla escreve a causa provável e **que evidência a confirmaria**:

1. Um tradutor acerta manchetes e desmonta em parágrafos; o erro cresce com o comprimento, e a
   primeira coisa a quebrar é a concordância entre partes distantes. O conjunto de treino já
   foi controlado para conter exemplos longos.
2. Um modelo recorrente acerta a concordância entre palavras vizinhas e nunca aprende a
   concordância a quarenta posições. Loss descendo, sem `NaN`, e aumentar a dimensão do estado
   não mudou nada.
3. Um time trocou a GPU por outra quatro vezes mais rápida e o tempo por época caiu 15%. Mesmo
   modelo, mesmos dados, mesmo lote; o profiler mostra muitas operações pequenas em série.

*Respostas esperadas:* (1) vetor de contexto fixo, falta de acesso — confirma-se comparando,
sob o mesmo treino, o modelo básico com um modelo com atenção; (2) gradiente que desaparece —
confirma-se medindo a norma do gradiente que chega aos primeiros passos, ou reproduzindo a
Medição 1 com a escala estimada da matriz recorrente; a correção mexe no caminho, não no
tamanho; (3) dependência sequencial — confirma-se medindo a ocupação da GPU e o tempo por passo
contra o comprimento da sequência.

*Critério de conclusão observável:* a dupla nomeia a causa **e** propõe uma medição que a
confirmaria. Nomear sem propor evidência não fecha o exercício.

*Extensão para quem terminar antes (opcional):* desenhar a grade de alinhamento de um par
PT→EN com inversão de ordem — linhas somando 1, ao menos uma linha com peso repartido e a
justificativa de uma célula fora da diagonal — e calcular um `c_t` a partir de três scores
dados, seguindo A.5. É o exercício que na V1 era obrigatório e aqui vira aprofundamento.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Turma sem base de ML** não acompanha "gradiente" | Silêncio ou perguntas básicas no Conceito 4 | Definição operacional em três frases: gradiente é a direção de ajuste de cada peso; o erro medido no fim precisa voltar até o começo; no caminho de volta ele atravessa um fator por passo. Rodar a Medição 1 e ler os números — o efeito é visível sem a álgebra, que está em A.2 |
| **A turma pedir a derivação em aula** | "De onde vem esse produto?" logo no Conceito 4 | A Parte 4 do roteiro tem cinco itens com o tempo de cada um. Fazer **só se sobrar tempo** e anunciando que é conteúdo de apêndice. O item mais barato e mais rentável é o 4 (calcular um `c_t` em 4 min) |
| **Turma sentir que "faltou rigor"** | Comentário de que a aula ficou superficial | Mostrar o apêndice projetado por 30 s: são 6 itens, com as seis equações do LSTM, a norma do produto de derivadas e o argumento de capacidade em bits — mais matemática do que a V1 tinha. O rigor não saiu, mudou de lugar |
| **Python ou projetor falharem** | Erro ao rodar, ou tela apagada | A Medição 1 tem saída salva em texto; a Medição 3 vira desenho à mão com o par curto PT→EN. Os passos da Medição 2 não dependem de tela nenhuma e são a parte essencial |
| **Turma quer pular para o Transformer** ("por que estudar RNN?") | Pergunta explícita nos primeiros 20 min | Resposta honesta e curta: o Transformer responde às limitações que ficam visíveis aqui; sem entender a pergunta, a arquitetura vira decoreba. A atenção aprendida nasce antes de 2017, e a Aula 6 transforma a ideia numa operação matricial sem recorrência |
| **Confusão entre atenção e alinhamento supervisionado** | Aluno pergunta onde estão os rótulos de alinhamento | Cravar o Conceito 10: não existem. O único rótulo foi a tradução; o alinhamento é subproduto. É o observável central da aula |
| **Confusão entre Bahdanau e paralelismo** | Aluno conclui que qualquer atenção elimina a recorrência | Voltar ao placar do Conceito 7: no artigo de 2014, `h_j` e `s_t` ainda são produzidos por RNNs. Acesso curto e execução paralela são propriedades diferentes |
| **Exercício de diagnóstico travar** | Duplas paradas sem escrever nada aos 4 min | Liberar a primeira causa (sintoma 1 = vetor fixo) como exemplo resolvido e deixar as duplas com os sintomas 2 e 3 |
| **Tempo estourar no Bloco 1** | 00:45 e ainda no Conceito 6 | Cortar a Medição 1 da execução ao vivo (vira leitura da saída salva) e comprimir o Conceito 6 às duas linhas do slide. O que **não** se corta: o Conceito 7 e a Medição 2 |

## 7. Artefatos produzidos

- **Tabela de diagnóstico** do exercício: três sintomas × causa × evidência que confirma —
  fotografada ou digitada no repositório pessoal. É o artefato central da aula na V2.
- Saída da Medição 1 executada, com as normas do produto para `T = 10, 50, 200` nos dois
  regimes de escala — o número que sustenta o Conceito 4 e que volta na Aula 7, quando o mesmo
  produto reaparecer ao longo da profundidade.
- Anotação das três linhas da atenção aditiva (`e_(t,j)`, `α_(t,j)`, `c_t`) com a leitura de
  cada uma em uma frase, escrita pelo próprio aluno — insumo direto da Aula 6 e do Lab 2.
- Lista das três dívidas com o veredito de cada uma depois do LSTM — material de revisão para
  a prova da Aula 17.
- *(Opcional, extensão)* grade de alinhamento preenchida e o cálculo de um `c_t` seguindo A.5.

## 8. Desafio pós-aula

Não avaliado. Três itens, na ordem:

1. **Diagnóstico próprio.** Descrever um comportamento anômalo que você já viu (ou que imagina
   plausível) num sistema que processa sequências, e dizer qual dos três fundamentos desta aula
   — compressão em vetor fixo, gradiente que não chega, ou dependência sequencial — o
   explicaria. Cinco linhas.
2. **Leitura com o apêndice ao lado.** Bahdanau, Cho & Bengio, *Neural Machine Translation by
   Jointly Learning to Align and Translate* (arXiv 1409.0473), seções 1 a 3 e a discussão da
   Figura 3. **Pergunta dirigida:** por que a Figura 3 é evidência de um alinhamento *aprendido
   sem rótulo de alinhamento*? O que exatamente foi supervisionado durante o treino, e o que
   apareceu como consequência? Comparar a Figura 2 do artigo com a curva do slide 1.
3. **Reflexão curta (cinco linhas).** Em Bahdanau, tanto a chave quanto o valor partem de
   `h_j`, mas a chave é transformada por `U_h` dentro do score e o valor entra como `h_j` na
   soma. O que se ganha ao tornar as três projeções explícitas e ao fazer as queries virem da
   própria sequência? Quem responder isso já entrou na Aula 6; **A.6** permite conferir.

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. Os pesos são os da ementa e não são reinventados
aqui: **laboratórios 30%** (oito labs, entregável individual, prazo de uma semana, descartando
a menor nota), **prova 30%** (individual, escrita, Aula 17, cobrindo as Aulas 1 a 16) e
**projeto final 40%** (marcos nas Aulas 22, 26 e 30).

O que muda na V2 é **como** o conteúdo desta aula é cobrado:

- **Prova (AV1).** Esta aula aparece principalmente como **diagnóstico e justificativa**: dado
  um sintoma (erro que cresce com o comprimento, dependência longa que não é aprendida, treino
  que não acelera), identificar a causa e justificar com o fundamento correto. O cálculo de um
  `c_t` a partir de scores dados permanece cobrável, em no máximo um item, e mesmo assim
  ancorado num porquê — por exemplo, dobrar os scores e explicar o que acontece com o peso
  máximo.
- **Lab 2 (Aula 9).** A atenção sai da fórmula e vira código. Quem sai desta aula sem entender
  que `α` é uma distribuição que soma 1 por linha não conclui o primeiro checkpoint.

*Observáveis em sala, sem nota:* (a) na correção do exercício, o aluno nomeia a causa **e**
propõe uma medição que a confirmaria; (b) explica que, depois de produzido `h_j`, a atenção
cria uma aresta direta até `c_t`, sem afirmar que a recorrência desapareceu; (c) distingue o
acesso de Bahdanau do paralelismo do Transformer.

## Apêndice matemático — índice

| Item | O que desenvolve | Apontado no fluxo |
|---|---|---|
| **A.1** | Recorrência desenrolada, compartilhamento de parâmetros e sensibilidade à ordem | Slide 3 |
| **A.2** | Regra da cadeia ao longo do tempo e regimes de gradiente que desaparece ou explode | Slide 4 |
| **A.3** | Equações do LSTM e caminho aditivo controlado pelas portas | Slide 6 |
| **A.4** | Limites do contexto fixo: capacidade sob precisão finita e comprimento de caminho | Slide 8 |
| **A.5** | Atenção aditiva: score, softmax, contexto, exemplo numérico e alinhamento suave | Slide 10 |
| **A.6** | Dos papéis funcionais de Bahdanau às projeções Q/K/V e à self-attention | Slide 12 |
