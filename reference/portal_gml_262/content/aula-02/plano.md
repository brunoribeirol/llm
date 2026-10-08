---
aula: 2
titulo: "Tokenização"
modulo: "1 — Fundamentos: do texto ao Transformer"
tipo: teorica
semana: 1
duracao_min: 120
versao: v2
---

# Aula 2 — Tokenização

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos versionáveis
> (tabela de fertilidade medida, folha de diagnóstico de custo), não conversas descartáveis com um
> chatbot. O roteiro de fala vive em `roteiro.md`; a especificação dos slides em
> `instructions-slides.md`.

> **Rebalanceamento V2.** O fluxo abre por uma **fatura**: dois times, o mesmo produto e o mesmo
> modelo, e a conta de um deles um terço maior. Do sintoma saem outros três — palavra longa em
> seis pedaços, código truncado por indentação, e a dívida da Aula 1 sobre perplexidade — e os
> quatro têm a mesma causa. A mudança estrutural: **os merges do BPE não são mais executados no
> quadro**. O fluxo enuncia o algoritmo, mostra a lista que ele produz e a segmentação
> resultante; a execução completa está em **A.1**, com cinco rodadas em vez de três, o empate e a
> codificação de uma palavra nova — e a **demo roda o mini-BPE ao vivo**, imprimindo a mesma
> lista. A execução saiu do quadro e virou medição. Carga horária, numeração e objetivos de
> aprendizagem permanecem os da V1.

## 1. Objetivo da aula

Mostrar que o token não é um dado da natureza e sim uma decisão de engenharia — tomada antes do
treino, congelada no modelo — e que essa decisão define custo de API, tamanho útil da janela de
contexto, qualidade em português e a própria comparabilidade da perplexidade entre modelos. O
aluno sai capaz de **diagnosticar um sintoma de custo ou de janela** e dizer que conta o
confirmaria.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Justificar** por que nem palavra nem caractere serve como unidade de entrada, nomeando o
   custo específico de cada extremo (vocabulário aberto e OOV de um lado, comprimento de sequência
   do outro).
2. **Enunciar** o algoritmo do BPE e **explicar** o que ele produz — uma lista ordenada de merges,
   aplicada na ordem em que foi aprendida — e **prever** a segmentação de uma palavra nova a
   partir de uma lista dada (execução completa em A.1).
3. **Distinguir** BPE, WordPiece e Unigram pelo critério de decisão de cada um, e **separar**
   SentencePiece (implementação) de Unigram (algoritmo) (fundamentos em A.2 e A.3).
4. **Relacionar** tamanho de vocabulário, comprimento de sequência e custo da atenção, e
   **dizer em que regime** encurtar a sequência dá ganho quadrático e em que regime dá ganho
   linear (contagem em A.5).
5. **Medir** a fertilidade de um tokenizador em português e em inglês sobre o mesmo texto e
   **interpretar** a razão em dinheiro e em janela de contexto, sabendo qual das duas médias usar
   (formalização em A.4).
6. **Explicar** por que a perplexidade de dois modelos só é comparável sob o mesmo tokenizador, e
   **dizer quanto** ela muda — uma potência, não um fator — e qual normalização torna a comparação
   honesta (conta em A.6).

*(Idênticos aos da V1 em escopo. O que mudou foi o verbo do item 2: de "executar o algoritmo do
BPE à mão sobre um mini-corpus" para "enunciar o algoritmo e prever a segmentação a partir de uma
lista dada" — a execução permanece cobrada e disponível em A.1, e continua sendo tarefa do
desafio pós-aula. O item 4 ganhou a segunda metade, que é a honestidade sobre os dois regimes; o
item 6 ganhou o "quanto".)*

## 3. Teoria aplicada

Cada conceito abaixo é apresentado pelo comportamento que o motiva, com o fundamento matemático
nomeado e a derivação remetida ao apêndice.

### Bloco 1 (00:10–00:55) — Por que o token existe e como ele é construído

**Conceito 1 — O sintoma: a mesma feature, duas faturas.**
*Comportamento observável:* dois times com o mesmo produto, o mesmo modelo, o mesmo prompt de
sistema. O que atende em português tem fatura maior e estoura a janela de contexto primeiro, com
documentos do mesmo tamanho. Ninguém mudou nada no código.
*Causa:* a contagem de tokens do mesmo conteúdo é diferente, e ela foi decidida antes do treino.
*Erro conceitual comum:* atribuir a diferença à qualidade do modelo em português. É outra
afirmação, e ela não explica a fatura — a fatura é uma divisão de duas contagens.

**Conceito 2 — Quatro sintomas, uma causa.**
Os quatro comportamentos que a aula explica: (a) o mesmo conteúdo mais caro em português, em
dinheiro e em janela; (b) `inconstitucionalissimamente` em seis pedaços num tokenizador e dois no
outro; (c) arquivo Python truncado antes do fim porque a indentação consome o orçamento de
contexto; (d) a dívida da Aula 1 — perplexidade só comparável sob o mesmo tokenizador.
*Tese:* o token é decisão de engenharia congelada antes do treino.
*Nota de condução:* deixar os quatro cartões na tela ao anunciar o plano da aula. O item (d) é o
gancho literal da Aula 1 e a resposta é o slide 14 mais **A.6**.

**Conceito 3 — Por que não palavras.**
Três motivos independentes. **Vocabulário aberto**: nomes próprios, neologismos, URLs, hashtags,
identificadores e erros de digitação entram todo dia; nenhuma lista fechada os cobre.
**Morfologia**: `correr`, `corri`, `correríamos`, `correndo`, `corrida` seriam cinco itens sem
relação declarada. **Zipf**: cauda praticamente infinita; o que cai fora vira `UNK`, que apaga
informação de forma irreversível.
*Analogia do instrutor:* é como um dicionário impresso tentando acompanhar a internet. No dia em
que ele sai da gráfica já falta palavra.
*Erro conceitual comum:* achar que basta um vocabulário "grande o suficiente". A cauda não
termina, e cada item novo custa `d` parâmetros na matriz de embedding mais uma linha no softmax
de saída — para uma palavra que continua com três exemplos de treino.

**Conceito 4 — Por que não caracteres.**
Resolve o vocabulário aberto de graça: dezenas de símbolos, zero OOV, qualquer string
representável. O preço é comprimento — o mesmo texto fica 4 a 5 vezes mais longo. Duas
consequências: o modelo gasta capacidade aprendendo ortografia antes de chegar a semântica; e
comprimento é caro, porque o termo de atenção cresce com o quadrado do número de posições.
*Analogia:* é a diferença entre ler uma frase e ler a mesma frase soletrada.
*Fundamento:* o custo por camada tem **dois** termos, `O(n·d²)` e `O(n²·d)`, e qual domina depende
da razão `n/d`. → **A.5**
*Erro conceitual comum:* concluir que caractere é sempre pior. Em correção ortográfica,
transliteração e línguas sem espaço, granularidade fina é competitiva — e a variante byte-level,
base dos tokenizadores do GPT, é um nível abaixo do caractere.

**Conceito 5 — Subword: o compromisso.**
A unidade passa a ser o pedaço de palavra, com tamanho decidido pela frequência. Palavra
frequente fica inteira; palavra rara se decompõe em pedaços conhecidos. `|V|` fixo (30 k a 128 k)
e OOV eliminado, porque no pior caso a palavra desce até os símbolos base.
*Analogia:* é compressão com dicionário. O que repete ganha um código curto; o que não repete é
gasto pedaço por pedaço.
*Erro conceitual comum:* imaginar que o tokenizador segmenta por morfema. Ele segmenta por
estatística de corpus, e as duas coisas coincidem só quando o corpus é grande e a língua é bem
representada nele.

**Conceito 6 — O que o BPE produz: uma lista ordenada de merges.**
*O que o fluxo apresenta:* as quatro operações nomeadas (símbolos base, contagem ponderada de
pares adjacentes, fusão do mais frequente, repetição até `|V|`) e o **resultado** sobre o
mini-corpus `casa`×5 · `casas`×3 · `casinha`×2 · `casarão`×1 — a lista `a+s → as`, `c+as → cas`,
`cas+a → casa`, e a segmentação: `casa` = 1 token, `casas` = `cas│as`, `casinha` = 5 pedaços.
*As duas consequências que valem mais que o algoritmo:* **treino é uma vez, codificação é
sempre**; e a **ordem** da lista importa, porque codificar é aplicar os merges na ordem em que
foram aprendidos.
*Fundamento:* a execução rodada a rodada, com as contagens completas, o empate da rodada 5, a
codificação de `casinhas` (5 tokens, contra `casas` com 1) e o custo de treino e de codificação.
→ **A.1**
*Comportamento observável que substitui o quadro:* a **medição 4 da demo** roda um BPE de 40
linhas no mesmo mini-corpus e imprime a mesma lista. O algoritmo produzindo a lista na tela vale
mais que o instrutor contando pares.
*Erros conceituais comuns:* confundir treino com codificação ("e se a palavra não estiver na
lista?"); e esperar morfologia — `casarão` sai como `casa`+`r`+`ã`+`o`, cortando o radical,
porque o critério é frequência. É limitação real, não bug.

**Conceito 7 — WordPiece e Unigram/SentencePiece: três critérios de decisão.**
**WordPiece** funde o par que mais aumenta a verossimilhança, o que equivale a maximizar
`score(A,B) = freq(AB)/(freq(A)·freq(B))` — prefere pares que se **atraem**, não os que só são
frequentes; marca continuação com `##`. **Unigram** começa grande e **poda** os itens cuja remoção
custa menos verossimilhança; a segmentação é probabilística, o que permite amostrar segmentações
(subword regularization). **SentencePiece** é implementação: treina no texto cru, representa o
espaço como `▁`, detokeniza exato, e roda **BPE e Unigram**.
*Comportamento observável do contraste:* em português, BPE fundiria `d+e` (4.000 ocorrências) e
WordPiece fundiria `q+u` (900) — porque `q` praticamente não existe sem `u`, e `d` e `e` são
frequentes separados. Os dois estão certos; otimizam coisas diferentes.
*Fundamento:* o `score` do WordPiece **sai** da log-verossimilhança sob um modelo unigrama e é
`c(AB)` vezes a informação mútua pontual do par. → **A.2**
*Fundamento:* o Unigram define `P(s) = Π p(x_i)` e `P(w) = Σ_s P(s)`, acha a melhor segmentação
por programação dinâmica em `O(|w|·L)` e treina por maximização de verossimilhança com poda por
`loss(x) = L(V) − L(V\{x})`. → **A.3**
*Erro conceitual comum:* tratar SentencePiece e Unigram como sinônimos. "O modelo usa
SentencePiece" não informa qual algoritmo está rodando.

**Conceito 8 — Byte-level BPE: o fim do UNK.**
O GPT-2 trocou os símbolos base de caracteres Unicode para os **256 bytes**. Nada é OOV, nunca —
e o vocabulário não tem `UNK`. O preço aparece em UTF-8: ASCII cabe em um byte, letra acentuada
ocupa dois, então `ção` entra como 5 símbolos base antes de qualquer merge. Se os merges vieram
de corpus inglês, não há merge para `ção` e a sequência de bytes fica exposta.
*Analogia:* é a diferença entre um teclado com todas as teclas da língua e um teclado ASCII em
que o acento é uma combinação de duas teclas.
*Erro conceitual comum:* concluir que byte-level é sempre mais caro em português. O que encarece
é a **composição do corpus** onde os merges foram aprendidos — um BPE byte-level treinado em
português é competitivo. É a ponte para o Bloco 2.

### Bloco 2 (01:05–01:50) — O que a decisão custa

**Conceito 9 — A alavanca mais barata: 30% menos tokens.**
*Comportamento observável:* encurtar a sequência em 30% deixa o termo de atenção em
`0,7² = 0,49` — praticamente metade — e a fatura de API em 70%.
*A honestidade que a V1 não trazia:* o ganho quadrático vale onde o termo de atenção domina, e
ele só domina quando `n` é grande em relação a `d`. Com `d = 4.096`: `n = 2.048` → o feed-forward
domina; `n = 32.768` → a atenção domina. Em contexto curto o ganho é **linear**, não quadrático.
*Fundamento:* `custo por camada ≈ c₁·n·d² + c₂·n²·d`, e a razão entre os termos é `n/d`;
encurtar por um fator `ρ` multiplica o primeiro termo por `ρ` e o segundo por `ρ²`. → **A.5**
*Erro conceitual comum:* supor que o custo é linear no número de tokens. É linear no **preço de
API** e quadrático no **compute da atenção em contexto longo** — duas curvas diferentes, e a
segunda é a que decide se contexto longo é viável.

**Conceito 10 — Onde a frequência produz efeito colateral.**
**Números:** `2024` pode ser 1 token e `2027` sair como `20`+`27` — aritmética sobre pedaços
arbitrários; mitigação é forçar dígito isolado ou grupos de três. **Código:** runs de indentação
custam tokens se o vocabulário não tem tokens de espaço em branco, e o sintoma observável é o
assistente **truncando o arquivo antes do fim**. **Línguas com poucos recursos:** corpus dos
merges dominado pelo inglês → pedaços de 1–2 caracteres → fertilidade alta.
*Analogia:* é medir tudo com uma régua calibrada para outra coisa.
*Erro conceitual comum:* atribuir ao modelo o déficit que é do tokenizador. Parte do déficit é
diagnosticável **antes** de qualquer treino e não se corrige com mais dados.

**Conceito 11 — Fertilidade: o número que vira dinheiro e janela.**
*Comportamento observável, medido na demo:* fertilidade = tokens por palavra; razão PT/EN acima
de 1 nos tokenizadores comerciais, com o valor **medido ao vivo** e anotado no quadro.
Três causas somadas: corpus dos merges majoritariamente inglês; acentos em dois bytes em
byte-level; palavras mais longas e mais flexionadas.
*Consequências:* em dinheiro, a relação é **linear** — razão 1,33 é 33% a mais na fatura. Em
janela, a relação é **inversa** — fertilidade 33% maior tira 25% das páginas, não 33%.
*Fundamento:* fertilidade é propriedade do **par** tokenizador × texto; e a média das razões par
a par **não é** a razão dos totais — a segunda é uma média ponderada pelo comprimento. Para
dinheiro, use a razão dos totais; para caracterizar o tokenizador, a média com desvio. → **A.4**
*Erros conceituais comuns:* concluir que se deve escrever tudo em inglês (tem custo de manutenção
e de fidelidade ao domínio); reportar a razão sem desvio e sem `n`; e usar a regra de bolso "1
token ≈ 4 caracteres", que foi calibrada em inglês.

**Conceito 12 — Aritmética de tokens e a resposta da Aula 1.**
Quatro consequências práticas: entrada e saída cobradas por token, com preços distintos; numa
conversa de múltiplos turnos o histórico é reenviado a cada chamada, então o custo cresce como a
**soma dos prefixos** (`1+2+…+20 = 210` blocos, não 20); a janela é medida em tokens; e a regra
de bolso engana em português.
E a pergunta da Aula 1 se fecha:
```
PPL = exp(−(1/N) Σ log P(tᵢ | t₍<ᵢ₎))     com N = número de tokens
```
Duas coisas mudam ao trocar o tokenizador: `N`, e o **espaço de eventos** — `P` está definida
sobre o vocabulário daquele tokenizador. Logo não é comparação imprecisa: é comparação sem
sentido.
*Fundamento:* o que é invariante entre tokenizadores é `log P(texto)`; o que não é invariante é o
denominador. Com o mesmo texto, `PPL_B = PPL_A^r` — uma **potência**, não um fator. A
normalização comparável é bits por caractere ou por byte. → **A.6**
*Erro conceitual comum:* achar que basta reescalar a perplexidade pela razão de fertilidade. Não
basta: a relação é exponencial, e mesmo corrigida a tarefa por passo mudou.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura pelo sintoma | **A fatura: dois times, o mesmo produto, a conta um terço maior**; os quatro sintomas com a mesma causa (fatura, palavra longa, código truncado, e a dívida da Aula 1 sobre perplexidade); tese: o token é decisão de engenharia congelada antes do treino |
| 00:10 | 45 min | Bloco 1 — Por que o token existe e como é construído | Por que não palavras (vocabulário aberto, morfologia, Zipf, `UNK`); por que não caracteres (comprimento, ortografia antes de semântica, os **dois** termos de custo); subword como compromisso; **o BPE enunciado pelo que ele produz** — a lista ordenada de merges e a segmentação, sem executar no quadro (A.1); WordPiece (verossimilhança, o exemplo `de` × `qu`, `##`) e Unigram/SentencePiece (poda, `▁`, segmentação probabilística); byte-level BPE e o fim do `UNK` |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — O que a decisão custa | **Demo com quatro medições (12 min)**, incluindo o mini-BPE que imprime a lista do slide 6; a alavanca de 30% e os dois regimes de custo; casos difíceis (números, código, línguas com poucos recursos); fertilidade PT×EN medida ao vivo, dinheiro e janela, e as duas médias; **exercício de diagnóstico de três faturas (5 min + 3 de correção)** |
| 01:50 | 10 min | Fechamento | Perplexidade é por token — resposta à pergunta da Aula 1; bits por caractere como normalização honesta; **índice do apêndice projetado (20 s)**; leitura (Sennrich et al.); ponte para a Aula 3 (Embeddings) |

*Comparação com a V1: os ~10 min de quadro executando os merges do BPE caíram para 0 min de
execução conduzida — o slide 6 passou a apresentar o resultado e as duas consequências em 9 min, e
a execução virou a medição 4 da demo (que a V1 já tinha, mas usava como confirmação redundante do
quadro). Os minutos liberados foram para a abertura pelo sintoma (10 min em vez de 10 de recap
seco) e para a honestidade dos dois regimes de custo no slide 10. A derivação permanece
integralmente disponível em A.1–A.6, com cinco merges em vez de três.*

## 4. Demonstração guiada

**Demo "um texto, quatro tokenizadores" — 12 min (01:05–01:17), `codigo/demo-tokenizacao.py`
projetado e executado ao vivo.**

O objetivo é que a turma veja as **peças**, não apenas a contagem: o mesmo texto partido de quatro
formas diferentes na mesma tela. Na V2 a demo ganha uma função a mais: a medição 4 **substitui o
quadro** que a V1 usava no slide 6.

1. **Medição 1 — as peças.** Carregar quatro tokenizadores reais via Hugging Face — BPE
   byte-level do GPT-2, WordPiece do BERT inglês, WordPiece do BERT português e Unigram/
   SentencePiece do XLM-R — e tokenizar um parágrafo em português e o equivalente em inglês,
   imprimindo os **tokens literais** de cada um. O acento cortado no meio pelo GPT-2 é visível a
   olho.
2. **Medição 2 — o número que vira dinheiro.** Tabela de fertilidade (tokens por palavra) por
   tokenizador e por língua, e a razão PT/EN **com desvio-padrão e com o número de pares usados**.
   O instrutor lê em voz alta o número que aparecer e o anota no quadro — o valor não está escrito
   em nenhum slide. **Esta é a evidência dos slides 12 e 13 e a que não se corta.**
3. **Medição 3 — os casos difíceis.** Na mesma tela: `inconstitucionalissimamente`, um número de
   quatro dígitos, um trecho de código Python com indentação (com a contagem de tokens gastos em
   espaço) e um emoji. São os sintomas 2 e 3 do slide 2, medidos.
4. **Medição 4 — o mini-BPE do zero.** Treinar um BPE de ~40 linhas sobre o mini-corpus do slide
   6, imprimindo as contagens de cada rodada, os merges na ordem aprendida e a segmentação final
   de cada palavra. **É o substituto do quadro:** a lista de merges sai de um laço de contagem, na
   frente da turma, em vez de sair da letra do instrutor.

**Números que a demo produz e que a aula usa como evidência (§7 do contrato):** a razão PT/EN com
desvio e com `n` (slides 12 e 13); a contagem de tokens gastos em indentação num arquivo Python
(slide 11); e a lista de merges `a+s`, `c+as`, `cas+a` impressa pelo mini-BPE, idêntica à do slide
6 (fecha o Conceito 6 sem quadro).

Preparação obrigatória na véspera: rodar o script uma vez com rede boa para que os quatro
tokenizadores fiquem no cache do Hugging Face. A demo é ao vivo e o download não pode acontecer em
sala.

## 5. Hands-on

**Componente prático da unidade — exercício de diagnóstico "três faturas" (5 min de dupla + 3 de
correção, 01:42–01:50).**

Substitui as três contas da V1. Três sintomas de custo; para cada um, a dupla escreve a causa
provável e **que conta confirmaria**. O preço de API é **hipótese declarada do exercício** —
`US$ 0,50 por milhão de tokens de entrada` — e não corresponde a nenhum provedor real; o valor da
oferta é `[definir na oferta]`.

1. **A fatura assimétrica.** Um time atende em português e em inglês com o mesmo produto e o mesmo
   modelo. A fatura do lado português é visivelmente maior, e ninguém mudou nada no código.
2. **A conversa que estourou o orçamento.** Uma conversa de 20 turnos custou muito mais que 20
   vezes um turno. O time dimensionou por "custo de um turno × número de turnos" e errou por mais
   de uma ordem de grandeza.
3. **O arquivo truncado.** Um assistente com janela de 8 k tokens funciona bem em texto corrido e
   trunca arquivos de código pela metade — mesmo em arquivos com menos palavras que documentos que
   caberiam inteiros.

*Respostas esperadas:* (1) fertilidade maior em português; a conta que confirma é a razão dos
**totais** de tokens sobre corpus paralelo com o mesmo tokenizador, e a resposta completa nomeia a
contrapartida de escrever em inglês. (2) o histórico é reenviado a cada chamada, logo o custo é a
**soma dos prefixos**: `1+2+…+20 = 210` blocos, mais de dez vezes a estimativa ingênua. (3)
indentação em runs de espaço sem tokens dedicados; a conta que confirma é tokenizar o mesmo
arquivo com um tokenizador de código e com um de texto e comparar.

*Critério de conclusão observável:* a dupla nomeia a causa **e** propõe a conta que a confirmaria.
Nomear sem propor a conta não fecha o exercício.

*Extensão para quem terminar antes (opcional):* as contas que na V1 eram obrigatórias — o prompt
de sistema de 300 palavras nas duas línguas com a razão medida, e a decisão de escrevê-lo em
inglês mantendo as respostas em português; e quantas páginas de 500 palavras cabem numa janela de
8 k tokens em cada idioma, com a armadilha de que fertilidade 33% maior tira **25%** das páginas,
não 33% (a conta está em A.4).

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Download dos tokenizadores** falha ou demora na hora da demo | A primeira chamada de `AutoTokenizer` fica pendurada | Cache preparado na véspera; o script tem `try/except` por tokenizador e segue com os que carregarem; em último caso, capturas de tela das quatro saídas feitas na véspera |
| **Rede/projetor indisponíveis** | — | A **medição 4 (mini-BPE) roda offline** e é a que sustenta o Conceito 6; o Bloco 1 inteiro é executável sem tela. Se nada rodar, aí sim os três merges vão ao quadro (Parte 4, item 1) — é o plano C, não o plano A |
| **A turma sentir falta dos merges no quadro** | "Você não vai fazer as contas?" no slide 6 | Resposta pronta: a demo roda em 20 min e imprime as contagens, e A.1 tem cinco rodadas em vez de três, com o empate e a codificação de palavra nova. Se insistirem, Parte 4 item 1 — **uma** rodada completa, não as três |
| **Turma trava no BPE** — confunde treino com codificação | Perguntas do tipo "e se a palavra não estiver na lista?" | Refazer a distinção separadamente: primeiro a lista ordenada de merges (treino, uma vez), depois aplicar a lista numa palavra nova (codificação, sempre). O exemplo `casinhas` de A.1 resolve isso com um número |
| **Discussão sobre "então é melhor escrever em inglês"** consome o Bloco 2 | Debate na sala após o slide 12 | Reconhecer a contrapartida em uma frase (custo de manutenção e fidelidade ao domínio), remeter a decisão ao Lab 1 e ao projeto final, e seguir |
| **Pedido de número de preço real** de provedor | "Quanto custa mesmo o token no provedor X?" | Não estimar: o preço é `[definir na oferta]` e o exercício roda com preço hipotético declarado; o que a aula ensina é a aritmética, não a tabela de um fornecedor |
| **Alguém contestar os "51% de economia"** | "Isso não vale para contexto curto" | Dar o ponto — é exatamente o que o slide 10 diz na V2. A razão `n/d` decide o regime, e A.5 tem a conta com `d = 4.096` instanciada em três comprimentos |
| **Tempo estourar no Bloco 1** | 00:48 e ainda no slide 6 | Comprimir o slide 7 para o critério de decisão de cada algoritmo (frequência × verossimilhança × poda) e cortar o exemplo do `##`; o slide 8 é curto e **não** pode cair, porque sustenta o argumento do português |
| **A turma pedir a derivação em aula** | "De onde vem esse score do WordPiece?" | Parte 4 do roteiro, cinco itens com o tempo de cada. Ordem de sacrifício: primeiro o exercício, depois o slide 11 (que a medição 3 sustenta sozinha), e **nunca** a medição 2 da demo nem o slide 12 |

## 7. Artefatos produzidos

- **Tabela de fertilidade preenchida** com os números medidos na demonstração: tokens por palavra
  em PT e em EN para os quatro tokenizadores, a razão PT/EN, **o desvio-padrão e o número de pares
  usados**. É o artefato central da aula — e a razão é o insumo do Checkpoint 2 do Lab 1.
- **Folha de diagnóstico de custo:** três sintomas × causa × conta que confirma, fotografada ou
  digitada no repositório pessoal. É o artefato novo da V2, no lugar da folha de três contas.
- Anotação da lista de merges impressa pelo mini-BPE, com a segmentação final de `casa`, `casas`,
  `casinha` e `casarão` — conferida contra a lista do slide 6 e contra A.1.
- Contagem de tokens gastos em indentação no trecho de código da medição 3.
- `codigo/demo-tokenizacao.py` disponível para o aluno reexecutar em casa — é o ponto de partida
  do Checkpoint 1 do Lab 1 (Aula 4).
- *(Opcional, extensão)* folha com as duas contas de orçamento — prompt de sistema nas duas
  línguas e páginas por janela — seguindo A.4.

## 8. Desafio pós-aula

Não avaliado. Três itens, na ordem:

1. **Medição própria.** Rodar `demo-tokenizacao.py` sobre um texto do próprio aluno (um artigo, um
   trecho de código, uma conversa) e anotar a fertilidade em PT e em EN, **com desvio e com o
   número de amostras**. Essa medição alimenta o Checkpoint 2 do Lab 1.
2. **BPE na mão, com gabarito.** Escolher quatro palavras de um domínio próprio com frequências
   plausíveis e executar cinco merges do BPE no papel, escrevendo a lista ordenada e as contagens
   de cada rodada. Depois conferir se o mini-BPE do script produz a mesma lista — e comparar o
   procedimento com **A.1**, que é a mesma execução resolvida passo a passo. Se der empate em
   alguma rodada, dizer como você desempatou e por que duas implementações corretas poderiam
   discordar.
3. **Leitura.** Sennrich, Haddow & Birch, *Neural Machine Translation of Rare Words with Subword
   Units*, arXiv 1508.07909 — o artigo que trouxe o BPE para NLP. Complementar: Kudo &
   Richardson, *SentencePiece*, arXiv 1808.06226. **Pergunta dirigida:** o BPE resolveu o
   vocabulário aberto, mas o que chega ao modelo é um inteiro — o ID 4021 não é "maior" nem "mais
   parecido" com nada. O que faz um inteiro significar algo? A resposta é a Aula 3.

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. Ela alimenta dois instrumentos, com os pesos da ementa
— que não são reinventados aqui:

- **Laboratórios — 30%.** Os Checkpoints 1 e 2 do Lab 1 (Aula 4) cobram diretamente o conteúdo de
  hoje: comparar BPE do GPT com WordPiece do BERT sobre o mesmo texto, e medir a razão PT/EN num
  corpus paralelo. Quem sai desta aula sabendo **qual das duas médias** calcular entra no lab sem
  o erro nº 1 do Checkpoint 2.
- **Prova — 30%.** Aula 17, sobre as Aulas 1 a 16, com a distribuição **42 diagnóstico ·
  40 justificativa · 8 conceito aplicado · 10 derivação**. Desta aula, o conteúdo aparece
  principalmente como **diagnóstico e justificativa**: dada uma tabela de dois tokenizadores,
  refutar a conclusão de que "perplexidade menor = modelo melhor" e propor a normalização correta;
  dado um sintoma de custo ou de janela, nomear a causa e a conta que confirma; justificar a
  escolha de tokenizador para um sistema em português. A execução de merges aparece, se aparecer,
  como o item de conceito aplicado — nunca como o item de derivação.
- **Projeto final — 40%.** Todo grupo que trabalhar com documentos em português vai enfrentar a
  aritmética de tokens no orçamento de contexto e de custo. A decisão de tokenizador e a medição
  de fertilidade — **com desvio e com tamanho de amostra** — são material legítimo da seção de
  avaliação quantitativa.

**O que a V2 muda no *como* se cobra o conteúdo desta aula:**

- **A resposta sobre perplexidade vale pela conta, não pela advertência.** "Não é comparável
  porque o tokenizador é diferente" é a resposta da V1 e vale parcialmente. A resposta completa diz
  **quanto** muda — `PPL_B = PPL_A^r`, uma potência — dá um número, e nomeia bits por caractere.
  O material está em **A.6** e é dito em sala.
- **A resposta sobre a razão PT/EN vale pela escolha da média.** Dizer "português custa mais" é
  retórica. A resposta que separa nota diz qual das duas médias foi usada, por que aquela, e o
  desvio junto. **A.4** existe para tornar isso barato.
- **A resposta sobre o custo `O(n²)` vale pelo regime.** "Encurtar 30% economiza 51%" é a resposta
  incompleta. A resposta completa nomeia a razão `n/d` e diz em que regime o ganho é quadrático e
  em que regime é linear. **A.5** tem a contagem.

*Observável em sala, sem nota:* ao ser questionado no fechamento, o aluno aplica uma lista de
merges dada a uma palavra nova **e** diz por que dois valores de perplexidade não são comparáveis
nomeando o que é invariante (`log P(texto)`) e o que não é (o denominador). Dizer que "não é
comparável" é a V1; nomear o invariante é a V2.
