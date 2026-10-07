---
aula: 7
titulo: "Transformer II: posição, normalização e o bloco moderno"
modulo: "1 — Fundamentos: do texto ao Transformer"
tipo: teorica
semana: 4
duracao_min: 120
versao: v2
---

# Aula 7 — Transformer II: posição, normalização e o bloco moderno

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (medição, diagrama do bloco, anotação de diagnóstico), não conversas
> descartáveis com um chatbot. O roteiro de fala vive em `roteiro.md`; a especificação dos
> slides em `instructions-slides.md`.

> **Rebalanceamento V2.** Cada peça do bloco entra por um sintoma observável: o modelo que não
> distingue ordem, o que produz lixo além do comprimento de treino, a pilha que diverge ao
> ganhar profundidade, a instabilidade que some ao trocar duas linhas de lugar. A matemática
> entra como fundamento nomeado, com a derivação completa no apêndice do deck (itens A.1 a
> A.6). Os objetivos de aprendizagem, a carga horária e a numeração permanecem os da V1 — o
> que muda é a ordem de apresentação e onde a derivação é feita. Em particular, a derivação do
> RoPE, que na V1 era conduzida no quadro, virou uma **medição** que imprime o mesmo número
> dentro e fora do comprimento de treino; a demonstração está em A.2, mais completa do que era.

## 1. Objetivo da aula

Fechar o buraco que a Aula 6 deixou aberto — a self-attention, exatamente como foi montada,
trata a frase como um saco de tokens — e sair da aula com o **bloco Transformer moderno**
montado peça por peça, cada peça justificada pelo sintoma que ela conserta: onde a posição
entra (RoPE), por que o residual existe, qual norma se usa, onde ela entra e o que o
feed-forward faz. É a aula que transforma o mecanismo da Aula 6 na coisa que o aluno vai
implementar no Lab 2 — e que o deixa capaz de **diagnosticar** qual peça está no lugar errado
a partir de como o treino falha.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Reconhecer** o sintoma da invariância a permutação (`Attention(P X) = P · Attention(X)`) e
   **explicar** por que a máscara causal não resolve isso e por que no encoder o problema
   aparece puro.
2. **Distinguir** as três estratégias de codificação posicional — senoidal, aprendida e RoPE —
   pelo ponto exato do cálculo em que cada uma injeta a posição, e **prever** o modo de falha
   de cada uma (fundamento em A.1 e A.2).
3. **Explicar** por que rotacionar Q e K faz o score depender de `m − n` e não de `m` e `n`
   isoladamente, **justificar** por que a rotação não se aplica a V, e **interpretar** a
   medição que mostra o mesmo score dentro e fora do comprimento de treino (demonstração em
   A.2).
4. **Justificar** a conexão residual pelo termo identidade na derivada de `y = x + f(x)` e
   **prever** o que acontece com uma pilha profunda sem ela (derivação em A.3).
5. **Comparar** LayerNorm com RMSNorm e pré-norm com pós-norm, apontando o que cada troca
   compra em estabilidade e o que ela custa (derivações em A.4 e A.5).
6. **Montar** o bloco Transformer moderno na ordem correta e **calcular** a divisão de
   parâmetros entre atenção e feed-forward em função de `d_model`, incluindo o efeito de dobrar
   `d_model` (contagem em A.6).

*(Idênticos aos da V1. O que mudou foi o verbo dominante: de "demonstrar" para "reconhecer",
"diagnosticar" e "justificar" — a demonstração permanece disponível e cobrada como fundamento
da justificativa.)*

## 3. Teoria aplicada

Cada conceito abaixo é apresentado pelo comportamento que o motiva, com o fundamento
matemático nomeado e a derivação remetida ao apêndice.

### Bloco 1 (00:10–00:55) — Posição: três lugares onde injetar, e três modos de falha

**Conceito 1 — O sintoma que a Aula 6 deixou na tela.**
*Comportamento observável:* na Demo 4 da Aula 6, embaralhar os tokens não alterou a saída de
cada um. Consequência: "o cachorro morde o homem" e "o homem morde o cachorro" produzem as
mesmas representações.
*Fundamento:* a invariância a permutação é propriedade demonstrável do mecanismo; a
demonstração está no deck da Aula 6 (item A.6 daquele apêndice) e não se repete aqui.
*Erro conceitual comum:* tratar como bug de implementação. Propriedade não se corrige com `if`.

**Conceito 2 — Por que a intuição erra: "a máscara já dá ordem".**
A máscara diz **quem pode ser lido** por quem; não diz **onde** cada token está nem quanta
distância separa dois tokens permitidos. E no encoder não há máscara nenhuma.
*Segundo erro comum:* "com dados suficientes o modelo aprende a ordem". Não há nada na entrada
que codifique ordem para ser aprendido.

**Conceito 3 — Primeira injeção: um código calculado, somado na entrada.**
As três linhas enunciadas: seno nas dimensões pares, cosseno nas ímpares, frequências
geometricamente espaçadas, e a soma no embedding antes da primeira camada.
*Fundamento:* deslocar por `k` é uma transformação linear fixa, e `PE(pos)·PE(pos+k)` não
depende de `pos` — a semelhança entre duas codificações é função **apenas** da distância.
→ **A.1**
*Número medido na demo:* com `d = 64` e `k = 3`, o produto interno vale `25.587028547` para
`pos = 0, 5, 100, 1000` — os quatro iguais até a nona casa.
*Erro conceitual comum:* achar que somar "polui" o embedding e que o certo seria concatenar.
Somar custa zero dimensão extra; é decisão de engenharia, não verdade matemática.

**Conceito 4 — Segunda injeção: uma tabela aprendida, e o sintoma dela.**
*Comportamento observável:* o modelo responde bem em prompts curtos e quebra a partir de um
comprimento **fixo**, sempre o mesmo, em qualquer assunto — às vezes com `IndexError` no log.
Não degrada: quebra.
*Causa:* a tabela tem `L_max` linhas e alguém pediu `L_max + 1`. Segundo teto, mais sutil:
nenhuma noção de distância embutida — a rede aprende separadamente cada par de posições visto
nos dados.
*Fundamento:* o que se perde ao trocar código calculado por código tabelado, propriedade a
propriedade. → **A.1**
*Erro conceitual comum:* concluir que "aprendida é melhor porque é aprendida". Aqui mais
parâmetro comprou menos generalização.

**Conceito 5 — Terceira injeção: a posição dentro do score (RoPE).**
Muda o **lugar**: as duas anteriores injetam na entrada; esta age dentro da atenção, depois da
projeção, sobre Q e K — e nunca sobre V. Cada par de dimensões é girado por um ângulo
proporcional à posição.
*Fundamento:* a matriz de rotação é ortogonal e `R(α)ᵀR(β) = R(β−α)`, logo o produto interno
de dois vetores girados depende só de `m − n`. Girar V faria o conteúdo agregado depender da
posição absoluta. → **A.2**
*Número medido na demo:* score `0.676869` para os pares `(3,1)`, `(10,8)`, `(500,498)` e
`(5000,4998)` — mesma distância, mesmo número, dentro e **fora** do comprimento de treino.
Sem rotação, todos dariam `0.600000`.
*Erro conceitual comum:* aplicar RoPE no embedding de entrada, como substituto do código
somado. Não é: é rotação sobre Q e K de **cada camada**, depois de projetar.

**Conceito 6 — Por que RoPE venceu, e o que ele não resolve.**
Quatro razões: relativa e no lugar certo; zero parâmetro treinável; reinjetada em cada camada;
alavanca para estender a janela reescalando as frequências.
*Nota de honestidade:* reescalar **estica** a janela e não faz o modelo usar bem o que entrou
nela. Janela grande e memória confiável são coisas diferentes — a distinção é da Aula 10. As
duas famílias de reescala estão descritas em **A.2**.

### Bloco 2 (01:05–01:50) — O que faz o bloco treinar

**Conceito 7 — O sintoma da profundidade e a conexão residual.**
*Comportamento observável:* a mesma receita treina com 12 blocos e diverge com 48; antes de
divergir, as primeiras camadas mal se movem.
*Causa:* é o produto de fatores da Aula 5, agora ao longo da profundidade. Com fator típico
`0.8` e 40 blocos, `0.8^40 ≈ 1.3·10⁻⁴`.
*Correção enunciada:* `y = x + f(x)`. A derivada passa a ter dois termos, e um deles é a
identidade — que não multiplica nada e não encolhe nada.
*Fundamento:* ao compor `N` blocos, a expansão do produto contém um caminho puramente
identidade; e a variância do fluxo residual cresce com a profundidade, o que obriga a
normalização. → **A.3**
*Erro conceitual comum:* ver o residual como truque de otimização. Ele muda **o que a camada
tem de aprender**: um delta, não a função inteira — e um bloco que aprende `f = 0` é
inofensivo.

**Conceito 8 — Qual norma: LayerNorm × RMSNorm.**
*Comportamento que a motiva:* a escala das ativações cresce a cada soma residual; sem controle,
o treino fica instável e camadas de cima e de baixo operam em faixas numéricas diferentes.
*As duas normas enunciadas.* O que a segunda economiza, contado: metade dos parâmetros da
norma e uma redução a menos por vetor. O que ela perde: a invariância a deslocamento.
*Fundamento:* as duas invariâncias demonstradas, o gradiente das duas (que é uma projeção
ortogonal à direção radial) e a contagem exata. → **A.4**
*Erro conceitual comum, e o mais frequente da aula:* confundir com BatchNorm. A estatística vem
das dimensões de **um** vetor; nenhuma amostra olha para outra, e é por isso que a norma
funciona igual com lote de tamanho 1 — condição necessária para geração autorregressiva.

**Conceito 9 — Onde a norma entra: pré-norm × pós-norm.**
*Comportamento observável:* trocar duas linhas de lugar faz a instabilidade sumir, sem mudar
dado, taxa de aprendizado ou tamanho de modelo.
*As duas escritas enunciadas:* `y = LN(x + f(x))` contra `y = x + f(LN(x))`.
*Fundamento:* nas duas ordens a derivada da pilha tem forma diferente — no pós-norm o fator da
norma multiplica o caminho identidade a cada camada; no pré-norm o caminho identidade atravessa
limpo. E o caso-limite que separa as duas de forma exata: com `f = 0`, o bloco pré-norm devolve
`x` e o pós-norm devolve `LN(x)`. → **A.5**
*Detalhe que falta em quase todo diagrama publicado:* com pré-norm a **norma final** depois do
último bloco é obrigatória, porque a última soma residual não passou por norma nenhuma.
Esquecida, faz o treino divergir sem mensagem de erro. É `TODO` do Lab 2.
*Erro conceitual comum:* achar que é detalhe de gosto. É a diferença entre uma pilha de 48
blocos que converge e uma que precisa de agenda de aquecimento.

**Conceito 10 — Feed-forward: onde estão dois terços dos pesos.**
A divisão de trabalho: a atenção **mistura** posições, o feed-forward **transforma** cada
posição isolada — sem olhar para nenhum vizinho. As duas variantes enunciadas (GELU de 2017 e
SwiGLU com gating).
*Contas lidas, não desenvolvidas:* atenção `4·d²`, feed-forward `8·d²`, bloco `≈ 12·d²`; com
`d = 1024`, 4,2 M contra 8,4 M, ≈ 12,6 M por bloco.
*Fundamento:* a contagem completa, a derivação de `d_ff = 8/3·d` a partir da paridade de
parâmetros, a SiLU com sua derivada e os FLOPs por token. → **A.6**
*Diagnóstico que sai da conta:* a contagem é **quadrática** em `d` — dobrar `d_model` multiplica
os parâmetros por quatro.
*Erro conceitual comum:* achar que o feed-forward mistura posições, ou que é "a parte boba do
bloco".

**Conceito 11 — O bloco consolidado, com o sintoma de cada troca.**
A tabela "2017 → hoje" ganha uma coluna: **qual sintoma motivou a troca**. Posição (lixo além
do comprimento de treino), onde a norma entra (divergência ao empilhar), qual norma (custo, sem
perda medida), feed-forward (qualidade a paridade de parâmetros), como a pilha é montada (o que
o modelo faz — Aula 8). E o que **não** mudou em oito anos: `softmax(QKᵀ/√d_k)V`, multi-head,
residual e feed-forward por posição.
*Erro conceitual comum:* ler a lista como "o Transformer foi superado". Foi endurecido, e a
prova é a primeira coluna ter sobrevivido.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas |
|---|---|---|---|
| 00:00 | 10 min | Abertura pelo sintoma | Retomada da Demo 4 da Aula 6 (tokens embaralhados, saída idêntica); por que a máscara causal não é posição; as duas metades da aula anunciadas como dois consertos |
| 00:10 | 45 min | Bloco 1 — três lugares onde injetar posição | Senoidal lida e a propriedade do produto interno; a tabela aprendida e o sintoma do comprimento fixo; RoPE e a posição dentro do score; por que venceu e o que não resolve; **demo com quatro medições (12 min)** |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — o que faz o bloco treinar | A pilha que diverge e a soma residual; qual norma e a confusão com BatchNorm; onde a norma entra e a norma final obrigatória; onde estão dois terços dos pesos; a tabela "2017 → hoje" com o sintoma de cada troca; **exercício de diagnóstico (8 min + 3 de correção, terminando com o bloco desenhado no quadro)** |
| 01:50 | 10 min | Fechamento | O bloco pronto; a pergunta sobre como a pilha é conectada; o fio do `O(n²)`; ponte para a Aula 8; leitura do RoFormer com pergunta dirigida |

*Comparação com a V1: o quadro algébrico passou de ~15 min de condução (derivação do RoPE com
dois ângulos concretos, a derivada do residual, a conta `4d²` contra `8d²`) para 0 min de
derivação conduzida; esses minutos foram para a demo (de 7 para 12 min, agora com quatro
medições que comparam as três estratégias) e para o exercício de diagnóstico. A derivação
permanece integralmente disponível em A.1–A.6, mais detalhada do que estava — em particular, a
demonstração do RoPE ganhou as propriedades da matriz de rotação, a forma explícita por par, o
argumento formal de por que não em V e as duas famílias de reescala de janela.*

## 4. Demonstração guiada

**Demo "medir a posição" — 12 min (00:43–00:55), NumPy puro.**

Esta aula **não tem pasta `codigo/`**: a Medição 1 reaproveita
`../aula-06/codigo/demo-attention.py` e as demais são quinze linhas reproduzidas integralmente
na Parte 2 do roteiro, que podem ser coladas num arquivo ou digitadas no REPL. Nada depende de
rede.

Na V1 a demo desta aula rodava o script da Aula 6 duas vezes para exibir a invariância. Na V2
essa parte encolhe para trinta segundos de retomada, e o tempo vai para **comparar as três
estratégias de posição lado a lado** — que é o que o Bloco 1 discute:

1. **Medição 1 — sem posição (30 s).** `demo-attention.py --shuffle`: a saída de cada token é
   idêntica a menos de permutação. Recoloca o sintoma do slide 1 na tela.
2. **Medição 2 — senoidal (4 min).** `PE(pos)·PE(pos+3)` para `pos = 0, 5, 100, 1000`.
   **Número produzido:** `25.587028547` nas quatro posições, idêntico até a nona casa. E a
   mesma conta variando `k` desenha a curva de similaridade: `32.00, 30.92, 25.59, 21.05,
   15.67, 11.44` para `k = 0, 1, 3, 10, 50, 200`. O valor em `k = 0` é `d/2`, a norma ao
   quadrado de qualquer codificação — todas as posições têm o mesmo tamanho.
3. **Medição 3 — aprendida (1 min).** Tabela de 4096 linhas, acesso à linha 4096.
   **Comportamento produzido:** `IndexError: index 4096 is out of bounds`. É o sintoma do
   Conceito 4, sem metáfora.
4. **Medição 4 — RoPE (6 min).** Score de `q` na posição `m` contra `k` na posição `n`, para
   `(3,1)`, `(10,8)`, `(500,498)`, `(5000,4998)`, `(3,2)` e `(100,99)`. **Números produzidos:**
   `0.676869` nos quatro primeiros (distância 2, dentro e fora do comprimento de treino),
   `0.639233` nos dois últimos (distância 1), e `0.600000` sem rotação. É a evidência do
   Conceito 5, e substitui a derivação que a V1 fazia no quadro.

Insumos preparados na véspera: tudo rodado uma vez na máquina da sala, fonte do terminal
aumentada, e as quatro saídas capturadas em texto como reserva.

## 5. Hands-on

**Componente prático da unidade — exercício de diagnóstico (8 min de dupla + 3 de correção,
01:39–01:50).**

Substitui a montagem das seis peças na ordem certa da V1, que vira extensão opcional — mas a
correção termina com o bloco desenhado corretamente no quadro, porque é esse diagrama que vai
para o Lab 2. Três sintomas; para cada um, a dupla escreve **qual peça está no lugar errado ou
ausente** e **que evidência confirmaria**:

1. Uma pilha de 48 blocos diverge nos primeiros 200 passos. A mesma receita, com 12 blocos,
   treina até o fim. Sem `NaN` antes da divergência, e as primeiras camadas mal se movem.
2. Um modelo responde bem em prompts curtos e produz texto incoerente assim que o prompt passa
   de um certo comprimento — sempre o mesmo comprimento, em qualquer assunto.
3. Um time aplicou a rotação posicional em Q, K **e** V. O modelo treina, e a representação de
   uma mesma frase muda conforme ela aparece no começo ou no fim do prompt.

*Respostas esperadas:* (1) pós-norm em pilha profunda — confirma-se medindo a norma do
gradiente por camada e trocando para pré-norm mantendo todo o resto; (2) posicional aprendido
estourando a tabela — confirma-se lendo o comprimento máximo na configuração e testando uma
posição imediatamente antes e outra depois, observando que a quebra é abrupta; (3) rotação
aplicada em V — confirma-se repetindo a mesma sentença em duas posições do prompt e comparando
as representações.

*Critério de conclusão observável:* a dupla nomeia a peça **e** propõe uma medição que a
confirmaria. Nomear sem propor evidência não fecha o exercício.

*Correção (3 min):* o instrutor monta no quadro o bloco pré-norm completo — duas normas, duas
somas, a bifurcação dupla de `x`, RoPE marcado apenas sobre Q e K, e a norma final depois do
último bloco. Se ninguém tiver marcado as duas somas, desenhar **errado** de propósito na
primeira tentativa: o conserto ao vivo fixa melhor que o desenho pronto.

*Extensão para quem terminar antes (opcional):* com `d_model = 1024`, calcular quantos
parâmetros ficam na atenção e quantos no feed-forward; depois refazer com `d_model = 2048` e
constatar o fator quatro. É a conta que na V1 era feita no quadro e aqui vira aprofundamento;
está em A.6, junto com os FLOPs por token.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Turma trava no RoPE** | Silêncio no Conceito 5, ou perguntas sobre números complexos | Não subir para a álgebra: descer para a Medição 4 e ler os números. Quatro pares com a mesma distância devolvendo o mesmo score convence mais rápido que a demonstração. **Nunca** introduzir notação complexa — ela não é necessária para o argumento e perde metade da sala |
| **A turma pedir a derivação em aula** | "Prova que só depende de `m − n`?" no Conceito 5 | A Parte 4 do roteiro tem cinco itens com o tempo de cada um. O item 1 (A.2) custa 5 min e cabe se o Bloco 1 estiver adiantado; o item 4 (o `8/3`) custa 3 min e é o de melhor razão convencimento/minuto |
| **Turma sentir que "faltou rigor"** | Comentário de que a aula ficou superficial | Mostrar o apêndice projetado por 30 s: seis itens, com a demonstração do RoPE inteira, as duas normas derivadas e a expansão do produto residual — mais matemática do que a V1 tinha. O rigor não saiu, mudou de lugar |
| **Python indisponível** | Erro ao rodar | As quatro saídas estão salvas em texto; a leitura dos números preserva o argumento. Contingência de quadro para a Medição 4: dois vetores unitários, mesma rotação aplicada nos dois, produto escalar invariante — isso todo mundo aceita |
| **Álgebra Linear não fresca:** a derivada do residual não comunica | Turma parada no Conceito 7 | Explicar sem derivada: "o gradiente tem dois caminhos de volta, e um deles é direto — esse não some". O número `0.8^40 ≈ 1.3·10⁻⁴` faz o trabalho sozinho |
| **Tempo estourar no Bloco 1** | 00:45 e ainda no Conceito 5 | Comprimir o Conceito 4 para 2 min (o teto do comprimento é o único item indispensável) e cortar a Medição 3. O que **não** se corta: o Conceito 5 e a Medição 4 |
| **Discussão sobre contexto longo puxa a aula para fora do escopo** | Perguntas sobre janelas de 100k ou 1M tokens | Responder que reescalar RoPE dá a alavanca mas não garante uso da janela, e que a distinção é da Aula 10; anotar a pergunta no quadro e seguir. Esse fio consome 15 min se deixarem |
| **Pedido de números concretos** ("qual modelo usa o quê, com qual `d_ff`") | Perguntas de comparação entre modelos | Não estimar de cabeça: as configurações são públicas nos arquivos de configuração dos modelos abertos e ficam como `[definir na oferta]` para a semana da aula |
| **Confusão com BatchNorm** | Perguntas de quem veio de visão computacional | Desenhar a grade `batch × dimensões` e circular a linha contra a coluna. Trinta segundos. A.4 tem as consequências práticas listadas |

## 7. Artefatos produzidos

- **Tabela de diagnóstico** do exercício: três sintomas × peça × evidência que confirma —
  fotografada ou digitada no repositório pessoal. É o artefato central da aula na V2.
- **Diagrama do bloco decoder-only pré-norm** desenhado à mão durante a correção, com as duas
  normas, as duas somas residuais, a bifurcação dupla de `x`, RoPE marcado sobre Q e K e a
  norma final. É literalmente o Checkpoint 3 do Lab 2.
- Saída das quatro medições, com os números que sustentam os Conceitos 3, 4 e 5 —
  em particular `0.676869` repetido nas posições 3 e 5000, que é a evidência de que a posição
  virou relativa.
- Tabela "2017 → hoje" com a coluna de sintomas, copiada ou fotografada do slide 12 — folha de
  referência para o Lab 2 e para a prova.
- *(Opcional, extensão)* a contagem de parâmetros para `d_model = 1024` e `2048`.

## 8. Desafio pós-aula

Não avaliado. Três itens, na ordem:

1. **Diagnóstico próprio.** Descrever um comportamento anômalo de treino ou de inferência — real
   ou plausível — e dizer qual peça do bloco explicaria: posição, residual, qual norma, onde a
   norma entra, ou o feed-forward. Cinco linhas, com a medição que confirmaria.
2. **Leitura com o apêndice ao lado.** Su et al., *RoFormer: Enhanced Transformer with Rotary
   Position Embedding* (arXiv 2104.09864), seções de formulação e de propriedades. **Pergunta
   dirigida:** em que ponto exato do cálculo do score a posição entra no RoPE, e por que isso
   entrega posição *relativa* sem acrescentar nenhum parâmetro treinável? Comparar o que o
   artigo afirma com a derivação de **A.2** e com os números da Medição 4 — as três coisas
   concordam?
3. **Verificação à mão.** Um vetor de duas dimensões, a rotação aplicada para duas posições `m`
   e `n` com um `θ` qualquer, conferindo que o produto escalar depende só de `m − n`. Três
   linhas de trigonometria. A conta está feita em A.2 com os números da demo, mas fazer com a
   própria mão é diferente de ler.

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. Os pesos são os da ementa e não são reinventados
aqui: **laboratórios 30%** (oito labs, entregável individual, prazo de uma semana, descartando
a menor nota), **prova 30%** (individual, escrita, Aula 17, cobrindo as Aulas 1 a 16) e
**projeto final 40%** (marcos nas Aulas 22, 26 e 30).

O que muda na V2 é **como** o conteúdo desta aula é cobrado:

- **Prova (AV1).** Esta aula aparece principalmente como **diagnóstico e justificativa de
  escolha**: dado um sintoma de treino (divergência ao empilhar, quebra num comprimento fixo,
  representação que muda com a posição no prompt), identificar a peça responsável e justificar
  com o fundamento correto. A demonstração de que o score depende de `m − n` permanece cobrável,
  em no máximo um item, e mesmo assim ancorada num porquê — por exemplo, explicar o que
  quebraria se a rotação fosse aplicada também a V. A contagem de parâmetros é cobrada como
  decisão de projeto: dado um orçamento, dizer o que cabe.
- **Lab 2 (Aula 9).** O bloco montado aqui é **exatamente** o que será implementado à mão no
  Checkpoint 3. Quem sai desta aula com o diagrama correto no caderno — duas normas, duas
  somas, RoPE só em Q e K, norma final — implementa o checkpoint sem consultar nada. Quem sai
  sem a norma final encontra um treino que diverge sem mensagem de erro, que é o modo de falha
  descrito em A.5.

*Observáveis em sala, sem nota:* (a) na correção do exercício, o aluno nomeia a peça **e**
propõe uma medição que a confirmaria — propor a medição é o que distingue quem entendeu o
fundamento de quem decorou o sintoma; (b) questionado no fechamento, o aluno explica em uma
frase por que a atenção precisa de posição e por que a máscara causal não substitui isso; (c)
dado um `d_model`, o aluno diz quantos parâmetros ficam na atenção e quantos no feed-forward, e
o que acontece ao dobrar `d_model`.
