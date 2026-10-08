---
aula: 2
titulo: "Tokenização"
tipo: teorica
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 2 de 30 (V2)

## Como usar este roteiro

A prosa deste documento é **fala em primeira pessoa**: é o que eu digo em sala, na ordem em que
digo. Não é resumo do conteúdo — é o texto falado. Posso ler quase literalmente ou usar como
trilho e improvisar em cima.

As linhas marcadas com 🗣️ são as **frases-âncora**: as que eu cravo, quase palavra por palavra,
porque mudam o ritmo ou fecham um ponto. Cada slide tem uma.

As notas marcadas com **Bastidor** são operacionais e **não são faladas em voz alta** — são
lembretes do que abrir na tela, onde a turma costuma travar, o que responder se alguém perguntar
algo específico.

> **O que muda nesta versão.** A aula abre por uma **fatura**: dois times, o mesmo produto, e a
> conta de um deles um terço maior. Do sintoma saem os outros três — palavra longa em seis
> pedaços, código truncado por indentação, e a dívida da Aula 1 sobre perplexidade.
>
> E tem uma mudança que muda o ritmo do primeiro bloco: eu **não executo mais os merges do BPE no
> quadro**. Na V1 eu gastava dez minutos contando pares à mão. Na V2 eu anuncio o que o algoritmo
> faz, mostro a lista que ele produziu e a segmentação resultante, e a **demo roda o mini-BPE ao
> vivo** e imprime a mesma lista. A execução com as contagens de cada rodada está em **A.1**, com
> cinco merges em vez de três, o desempate e a codificação de uma palavra nova. Se a turma pedir
> as contagens, a **Parte 4** tem a condução.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · O sintoma: a mesma feature, duas faturas · 00:00–00:04

Boa noite, pessoal. Semana passada eu fechei a aula dizendo que tudo em NLP foi reescrito como
uma coisa só: prever o próximo token. E eu passei uma hora e meia falando de token sem nunca
definir o que é um token.

Hoje eu conserto isso, e eu vou começar por uma história que acontece de verdade.

Imaginem dois times na mesma empresa, com o mesmo produto. Um atende clientes em inglês, o outro
atende em português. Mesmo modelo, mesmo prompt de sistema, mesma temperatura, mesmo código.
Fim do mês, a fatura do time que atende em português é visivelmente maior. E não é só a fatura:
a janela de contexto dele estoura primeiro, com documentos do mesmo tamanho.

Ninguém trocou de modelo. Ninguém mexeu em parâmetro. O que mudou foi a **contagem de tokens**
do mesmo conteúdo — e essa contagem foi decidida por alguém, antes do treino do modelo, e
congelada dentro dele.

> 🗣️ "Ninguém mudou o modelo. Alguém decidiu, antes do treino, o que conta como um token — e essa decisão está na fatura todo mês."

> **Nota:** Bastidor: não abrir o terminal ainda; a demo é só depois do intervalo, e o número da
> razão PT/EN é medido lá. **Não antecipar valor nenhum** — o slide não tem número de propósito.
> Se o cache dos tokenizadores não foi preparado na véspera, começar o download agora em segundo
> plano: o script leva alguns minutos na primeira execução e a demo do slide 9 não pode esperar.

### Slide 2 · Quatro sintomas, uma causa · 00:04–00:10

E essa fatura não é o único sintoma. Deixa eu botar quatro na mesa, porque os quatro têm o mesmo
culpado.

Primeiro é o que eu acabei de contar: o mesmo conteúdo custa mais em português, em dinheiro e em
janela.

Segundo, e vocês vão ver na tela depois do intervalo: `inconstitucionalissimamente` sai em seis
pedaços num tokenizador e em dois no outro. Mesma palavra, mesma língua, dois tokenizadores.

Terceiro, e esse é o que mais irrita na prática: um arquivo Python bem indentado gasta uma
fração nada desprezível do orçamento de contexto em espaço em branco. O sintoma que vocês vão
ver é o assistente truncando o arquivo antes do fim, num arquivo que tem menos palavras que um
documento que caberia inteiro.

E o quarto é dívida da aula passada. Eu deixei uma pergunta dirigida na leitura do Jurafsky: por
que a perplexidade de dois modelos só é comparável se o tokenizador for o mesmo? Quem chegou a
uma resposta? … A resposta completa é o último slide de hoje, e ela está escrita no apêndice
deste deck, em A ponto seis, com a conta e um exemplo numérico. Mas eu já adianto a forma da
coisa: perplexidade é medida **por token**, e se dois modelos não concordam sobre o que é um
token, eles não estão dividindo pela mesma coisa.

Os quatro têm a mesma causa, e a tese de hoje é essa: o token não é um dado da natureza. É uma
decisão de engenharia congelada antes do treino, e ela não muda depois.

Plano da aula: primeiro bloco, de onde o token vem e como ele é construído. Segundo bloco, o que
essa decisão custa — em compute, em dinheiro, em janela de contexto e em português.

> 🗣️ "Perplexidade é medida por token. Se dois modelos não concordam sobre o que é um token, eles não estão dividindo pela mesma coisa."

> **Nota:** Bastidor: esperar de verdade a resposta da turma no item 4, uns 15 segundos de
> silêncio. Se ninguém tiver feito a leitura, não constranger a sala — seguir dizendo que a
> resposta fecha no último slide. Se alguém acertar, anotar o nome e usar a resposta dele no
> slide 14. Deixar os quatro cartões na tela enquanto anuncio o plano.

### Slide 3 · Por que a intuição não basta: "então usa palavra" · 00:10–00:18

Vamos pelo caminho ingênuo, que é o que qualquer um de nós escreveria primeiro. Se eu vou
transformar texto em números, a unidade óbvia é a palavra: eu monto uma lista de todas as
palavras da língua, dou um número para cada uma, e pronto. Isso quebra por três motivos, e os
três são independentes.

Primeiro motivo: o vocabulário de uma língua viva é **aberto**. Nome próprio entra todo dia,
neologismo entra todo dia, URL, hashtag, identificador de variável, erro de digitação. Não
existe lista fechada. É como um dicionário impresso tentando acompanhar a internet — no dia em
que ele sai da gráfica, já falta palavra.

Segundo motivo, e esse é nosso, é do português: morfologia. `Correr`, `corri`, `correríamos`,
`correndo`, `corrida` — cinco entradas na lista, sem nenhuma relação declarada entre elas. O
modelo teria que aprender de exemplos que essas cinco coisas têm a ver uma com a outra, gastando
parâmetro para redescobrir uma conjugação que qualquer aluno de sexto ano sabe. E `casa`,
`casinha`, `casarão`, `casebre` — mais quatro.

Terceiro: Zipf. Um punhado de palavras cobre metade de qualquer texto e a cauda é imensa. O que
cai fora da lista vira `UNK`, aquele token de "palavra desconhecida", e `UNK` é destruição de
informação: o modelo recebe um buraco onde estava o nome do cliente.

E aqui é onde a maioria das pessoas trava, então deixa eu antecipar a pergunta: por que não
fazer o vocabulário simplesmente maior? Porque duas coisas somam. A cauda não termina — sempre
vai ter uma palavra nova. E cada item de vocabulário custa `d` parâmetros na matriz de embedding
e uma linha a mais no softmax de saída. Vocabulário de um milhão de palavras é uma matriz
gigantesca cheia de vetores treinados com três exemplos cada.

> 🗣️ "Palavra não serve porque a lista nunca fecha. E quando ela não fecha, o que sobra é `UNK` — um buraco no meio da frase que o modelo não tem como preencher."

> **Nota:** Bastidor: se alguém perguntar de stemming ou lematização, responder que resolve parte
> da morfologia e cria outro problema — perde informação de tempo e pessoa, e não resolve nome
> próprio nem URL. Não abrir esse fio, custa 5 min e não muda o argumento.

### Slide 4 · O outro extremo: caractere · 00:18–00:25

Se a palavra é grande demais, vamos ao outro extremo: caractere. Umas dezenas de símbolos,
vocabulário mínimo, e a propriedade mais bonita de todas — **zero OOV**. Qualquer string que
existir é representável. Nunca mais um `UNK`.

Parece resolvido, e não é. O problema é comprimento. Uma frase de vinte palavras tem umas cem,
cento e vinte posições em caractere. A sequência fica quatro, cinco vezes mais longa para dizer
exatamente a mesma coisa. É a diferença entre ler uma frase e ler a mesma frase soletrada: a
informação é idêntica, o esforço não.

E comprimento cobra em dois lugares. O primeiro é capacidade: o modelo gasta camadas aprendendo
ortografia — que `q` vem com `u`, que `ç` não abre palavra em português — antes de sobrar
capacidade para semântica. Ele aprende a soletrar antes de aprender a significar.

O segundo é compute. A atenção compara cada posição com todas as outras posições, então o termo
de atenção cresce com o **quadrado** do número de posições. Eu vou detalhar isso depois do
intervalo, com o número na tela. E eu vou adiantar uma honestidade que a versão anterior desta
aula não dizia: existem **dois** termos de custo por camada, um que cresce com `n` e um que
cresce com `n²`, e qual deles domina depende de comparar `n` com a dimensão do modelo. A
contagem completa está em A ponto cinco.

Agora, uma honestidade: caractere não é sempre pior. Em correção ortográfica, em transliteração,
em línguas escritas sem espaço entre palavras, granularidade fina é competitiva. E existe um
nível ainda abaixo do caractere, o byte, que é a base do tokenizador do GPT — isso é o slide 8.

> 🗣️ "Caractere resolve o OOV e cria um problema pior: a sequência fica cinco vezes mais longa, e o termo de atenção é quadrático no comprimento."

> **Nota:** Bastidor: **não** derivar a contagem aqui — é o slide 10, e a contagem termo a termo
> está em A.5. Se alguém pedir a conta agora, prometer para depois do intervalo e cumprir. A
> menção aos dois termos é nova na V2 e é importante: sem ela, o slide 10 promete metade do custo
> num regime em que a promessa não se sustenta.

### Slide 5 · Subword: o compromisso · 00:25–00:29

Então a gente tem dois extremos e os dois são ruins. Palavra: sequência curta, vocabulário
infinito. Caractere: vocabulário mínimo, sequência longa. A saída é não escolher nenhum dos dois.

A unidade que venceu é o **pedaço de palavra** — subword — e a sacada é que o tamanho do pedaço
não é fixo: ele é decidido pela frequência no corpus. Palavra que aparece muito ganha um token
só. Palavra rara é decomposta em pedaços que o vocabulário já conhece. `Casa` é um token;
`casarão` são quatro.

E olha o que isso compra: o vocabulário é **fixo**, tipicamente entre trinta e cento e vinte e
oito mil itens, e ainda assim o OOV desaparece — porque no pior caso a palavra desce até os
símbolos base, que estão todos no vocabulário. Vocabulário fechado, cobertura aberta.

É compressão com dicionário, essencialmente. O que repete ganha um código curto; o que não
repete é gasto pedaço por pedaço. E agora a pergunta que interessa: quem decide quais pedaços
entram no dicionário?

> 🗣️ "Palavra frequente vira um token, palavra rara vira pedaços. Vocabulário fechado, cobertura aberta — é isso que subword compra."

> **Nota:** Bastidor: slide curto, quatro minutos, é uma dobradiça entre os dois extremos e o
> algoritmo. Não gastar mais que isso — o tempo pertence ao slide 6 e à demo. Se a turma parecer
> confortável, cortar para três.

### Slide 6 · O que o BPE produz: uma lista ordenada de merges · 00:29–00:38

O algoritmo se chama Byte Pair Encoding — BPE — e veio do Sennrich, Haddow e Birch em 2015, que
é a leitura de hoje. Ele tem quatro operações, e eu vou dizer as quatro em quatro frases.

O vocabulário inicial é o conjunto de símbolos base — caracteres, ou bytes. Conta-se todos os
pares adjacentes de símbolos, ponderando pela frequência de cada palavra. Funde-se o par mais
frequente, criando um símbolo novo. E repete até chegar no tamanho de vocabulário escolhido.

É isso. Quatro operações, e nenhuma delas é difícil. O que eu quero mostrar não é a execução — é
o **resultado**.

Peguem um corpus de quatro palavras: `casa` cinco vezes, `casas` três, `casinha` duas,
`casarão` uma. Depois de três rodadas, o algoritmo aprendeu esta lista, nesta ordem: `a` mais
`s` virando `as`; depois `c` mais `as` virando `cas`; depois `cas` mais `a` virando `casa`.

E a segmentação que sai disso: `casa` é um token único. `casas` é `cas` mais `as`. E `casinha`
continua em cinco pedaços — `cas`, `i`, `n`, `h`, `a`. Que é exatamente o comportamento que a
gente pediu no slide anterior: frequente inteiro, raro em pedaços.

Agora as duas consequências, que valem mais que o algoritmo. A primeira, e ela é a fonte de
metade da confusão sobre tokenizador: **o modelo treinado é a lista ordenada de merges**. É
isso. Não tem inteligência, não tem análise linguística. Codificar um texto novo é pegar os
símbolos base e aplicar aquela lista. Treino é uma vez; codificação é sempre.

A segunda: a **ordem** importa. Se o terceiro merge viesse antes do primeiro, a segmentação de
várias palavras mudaria. É por isso que a lista é ordenada e por que o tokenizador viaja como
arquivo junto com o modelo, em vez de ser reconstruído a partir do corpus.

Eu não vou fazer as contagens no quadro. Elas estão em A ponto um, com cinco rodadas em vez de
três, com o que acontece quando dá empate, e com a codificação de uma palavra que não estava no
corpus — `casinhas`, que sai em cinco tokens mesmo com `casas` custando um. E daqui a vinte
minutos eu **rodo** esse mini-BPE na frente de vocês e ele imprime exatamente essa lista. Vale
mais ver o algoritmo produzir a lista do que me ver contar par por par.

> 🗣️ "O tokenizador treinado não é um dicionário de palavras. É uma lista ordenada de merges — e codificar um texto novo é aplicar essa lista na ordem."

> **Nota:** Bastidor: **este era o slide de dez minutos de quadro na V1.** Agora são nove
> minutos com o resultado, as duas consequências e o ponteiro, e a execução virou a medição 4 da
> demo. As duas perguntas que sempre vêm: (a) "e se a palavra não estiver na lista?" — refazer a
> distinção treino × codificação, é sempre essa confusão; (b) "por que `casarão` corta em
> `casa`+`r`+`ã`+`o`, cortando o radical?" — porque o critério é frequência, não morfologia, e
> isso é limitação real, não bug. Se pedirem as contagens rodada por rodada: Parte 4, item 1.
> Implementações de verdade marcam a fronteira de palavra com `</w>` ou `▁` para poder
> detokenizar; eu omito para o exemplo não poluir, e o script da demo omite igual para bater com
> A.1.

### Slide 7 · Três algoritmos, três critérios de decisão · 00:38–00:46

BPE não é o único. Tem outros dois que vocês vão encontrar em todo modelo aberto, e a diferença
entre eles está no **critério de decisão**.

WordPiece, que é o do BERT, é da mesma família — funde pares — mas escolhe diferente. Em vez do
par mais frequente, ele funde o par que mais aumenta a verossimilhança do corpus, o que na
prática dá a frequência do par dividida pelo produto das frequências individuais. Repararam no
denominador? Ele normaliza pela frequência de cada peça. O BPE prefere pares **frequentes**; o
WordPiece prefere pares que se **atraem** — que aparecem juntos mais do que apareceriam por acaso
se fossem independentes.

E deixa eu dar um exemplo em português, porque ele deixa a diferença óbvia. Pensem no par `d`
mais `e` e no par `q` mais `u`. `De` é muitíssimo mais frequente. Mas `d` e `e` são frequentes
separados também — ver os dois juntos não é informação nenhuma, é o que se esperaria. Já o `q`
em português praticamente **não existe** sem `u`. O BPE funde `de`, porque conta mais. O
WordPiece funde `qu`, porque `qu` é uma regularidade da língua e `de` é uma coincidência de
frequência. Os dois estão certos; eles otimizam coisas diferentes. A conta que mostra que esse
critério **sai** da verossimilhança, com os números dos dois pares, está em A ponto dois.

E o WordPiece marca continuação de palavra com dois sinais de cerquilha: `casinha` sai como
`cas` e `##inha`, e o `##` diz "eu não começo palavra, eu continuo a anterior".

Unigram, do Kudo, é o mais interessante porque vai na direção contrária. Ele começa com um
vocabulário **grande** de candidatos e vai **podando**: em cada rodada, remove os itens cuja
remoção custa menos verossimilhança. BPE constrói de baixo para cima colando; Unigram esculpe de
cima para baixo removendo. E ele tem uma propriedade que os outros não têm: a segmentação é
probabilística. O mesmo texto admite várias segmentações com probabilidades diferentes, então dá
para **amostrar** a segmentação durante o treino — isso se chama subword regularization e
funciona como aumento de dados. Como ele escolhe a melhor segmentação sem enumerar todas, e qual
é o critério exato da poda, está em A ponto três.

E SentencePiece é a coisa que mais gera confusão, então deixa eu ser explícito: SentencePiece
não é um algoritmo, é uma **implementação**. Ela treina direto no texto cru, sem pré-tokenizar
por espaço, e representa o espaço como aquele caractere de sublinhado que vocês vão ver na saída
da demo. Isso dá duas coisas: detokenização exata — dá para voltar ao texto original sem
ambiguidade — e suporte a línguas que não separam palavras por espaço. E o mais importante:
SentencePiece implementa BPE **e** Unigram. Quando o cartão do modelo diz "usa SentencePiece",
ele não disse qual algoritmo está rodando.

> 🗣️ "BPE cola de baixo para cima, Unigram poda de cima para baixo. E SentencePiece não é algoritmo nenhum — é a implementação que roda os dois."

> **Nota:** Bastidor: se o tempo estiver apertado, comprimir este slide ao critério de cada um —
> frequência, verossimilhança, poda — e cortar o exemplo do `##`. O que **não** pode cair é a
> distinção SentencePiece × Unigram, porque isso aparece em cartão de modelo e o aluno vai
> encontrar na semana do Lab 1. E não derivar o `score` do WordPiece: dizer que ele sai da
> verossimilhança, dar o exemplo do `qu`, e remeter a A.2. Se insistirem, Parte 4, item 2.

### Slide 8 · Byte-level BPE: o fim do UNK e o preço do acento · 00:46–00:55

Falta uma peça, e ela é a que o GPT usa. O GPT-2 fez uma troca esperta: em vez de partir de
caracteres Unicode, ele parte dos **256 bytes**.

A consequência é radical. Byte é byte: emoji é sequência de bytes, ideograma é sequência de
bytes, um arquivo corrompido é sequência de bytes. Tudo é representável, sempre. O vocabulário
do GPT-2 **não tem** um token `UNK`, porque ele não precisa de um. Isso é uma propriedade forte,
e é por isso que essa variante virou padrão em modelo generativo.

Mas tem preço, e o preço tem a ver com UTF-8. Em UTF-8, ASCII cabe em um byte só — `c`, `a`, `s`
custam um byte cada. Letra acentuada custa **dois**. `ç` são dois bytes, `ã` são dois bytes, `õ`
são dois bytes. Então antes de qualquer merge, `ção` já entra como cinco símbolos base, não três.

E aí vem a parte que decide o assunto do Bloco 2. Se os merges foram aprendidos num corpus
majoritariamente inglês, não existe merge para `ção` — a sequência de bytes fica exposta, sem
nada que a colapse. É como um teclado ASCII em que o acento é uma combinação de duas teclas: dá
para escrever tudo, mas cada acento custa duas batidas.

E eu quero cortar um mal-entendido antes que ele nasça: o problema não é o byte-level. Um BPE
byte-level treinado em corpus português tem merges para `ção`, para `mente`, para `ções`, e fica
competitivo. O que encarece o português não é a técnica — é a composição do corpus onde os
merges foram aprendidos. Isso é a diferença entre culpar a ferramenta e culpar quem a calibrou,
e é o que a demo depois do intervalo vai medir.

> 🗣️ "O vocabulário do GPT-2 não tem `UNK` porque ele não precisa: tudo é byte. O preço é que, em UTF-8, cada acento nosso custa dois bytes antes de qualquer merge."

> **Nota:** Bastidor: depois deste slide vai o intervalo de 10 min. Aproveitar o intervalo para
> deixar o script já aberto no terminal e rodar uma vez em silêncio, confirmando que os quatro
> tokenizadores carregam do cache. Se algum falhar, saber antes de voltar qual vai faltar na tela.

### Slide 9 · [Demo] Um texto, quatro tokenizadores · 01:05–01:17

Voltando. Antes do intervalo eu afirmei que o mesmo texto custa mais em português. Agora eu vou
medir isso na frente de vocês, com tokenizadores reais, e o número que aparecer é o número que a
gente vai usar no exercício. E no fim eu rodo o mini-BPE do slide 6, para vocês verem a lista de
merges saindo de um laço em vez de sair da minha boca.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> 🗣️ "Eu não vou dizer quanto o português custa mais caro — eu vou medir na tela e a gente anota o número que aparecer."

> **Nota:** Bastidor: doze minutos, script `codigo/demo-tokenizacao.py`, passos detalhados na
> Parte 2. Fonte do terminal grande antes de começar — a turma do fundo precisa ler os tokens,
> não só a contagem. Se algum tokenizador não carregar, o script avisa e segue; comentar em voz
> alta que isso é o `try/except` funcionando e não um erro da demo. A medição 2 é a evidência
> dos slides 12 e 13 e é a que **não** se corta. A medição 4 (mini-BPE) roda offline e é a
> última a cair, porque na V2 ela substitui o quadro do slide 6.

### Slide 10 · A alavanca mais barata: 30% menos tokens · 01:17–01:26

Agora a conta que eu prometi antes do intervalo.

Vocabulário e comprimento são grandezas inversas, e cada extremo paga em lugar diferente.
Vocabulário grande dá sequência curta e paga em **parâmetro**: a matriz de embedding tem `|V|`
vezes `d` entradas, o softmax de saída calcula um logit por item em cada posição, e os itens
raros ficam com poucos exemplos para treinar um vetor decente. Vocabulário pequeno dá sequência
longa e paga na **atenção**, cujo termo cresce com o quadrado do número de tokens.

E olha o número que faz a diferença ficar concreta. Suponham que um tokenizador melhor para
português encurte a sequência em trinta por cento. O termo de atenção vai para zero vírgula sete
ao quadrado, que é zero vírgula quarenta e nove. Trinta por cento menos tokens é cinquenta e um
por cento menos compute de atenção — por uma decisão tomada antes de o treino começar, que não
custa uma linha de código a mais no modelo.

Agora a honestidade que a versão anterior desta aula não tinha, e que eu quero que vocês levem
porque ela é o tipo de coisa que separa quem entendeu de quem decorou. Esses cinquenta e um por
cento valem para o **termo de atenção**. E o termo de atenção só domina o custo quando o número
de tokens é grande em relação à dimensão do modelo. Em contexto curto, quem domina é o
feed-forward, e o ganho de encurtar a sequência é **linear**, não quadrático — trinta por cento,
não cinquenta e um.

O que sobra dos dois casos: trinta por cento de economia garantida, e até cinquenta e um no
termo de atenção quando o contexto é longo. Continua sendo a alavanca mais barata que existe. A
contagem termo a termo, com a razão que decide qual dos dois domina, está em A ponto cinco — e
ela também tem a conta da memória, que é o limite que estoura primeiro.

E o erro que eu quero desarmar antes de sair daqui: quase todo mundo assume que o custo é linear
no número de tokens. Ele é linear no **preço de API**, porque a fatura conta token. E é
quadrático no **compute da atenção** em contexto longo. São duas curvas diferentes, e é a segunda
que decide se contexto longo é viável — motivo pelo qual a Aula 8 vai falar de atenção eficiente.

> 🗣️ "Trinta por cento menos tokens é quarenta e nove por cento do custo de atenção — mas só onde a atenção domina. Fora dali o ganho é linear, e continua sendo a alavanca mais barata que existe."

> **Nota:** Bastidor: fazer `0,7² = 0,49` no quadro, é uma conta de dois segundos que a sala
> inteira acompanha. **Não** derivar a contagem de operações — está em A.5, com o ponto em que
> `n = d` e a razão vira 1. Se perguntarem de contexto de 1 milhão de tokens, dizer que atenção
> eficiente e KV cache são a Aula 8 e não abrir agora. Se alguém pedir a contagem, Parte 4,
> item 3.

### Slide 11 · Onde a frequência produz efeito colateral · 01:26–01:34

Três lugares onde a segmentação por frequência produz efeito colateral que vocês vão ver na
prática — e dois deles são sintomas que eu prometi no começo da aula.

Números, primeiro, e esse é o meu favorito porque ele explica um comportamento que todo mundo já
notou. Se `2024` aparece muito no corpus, ele vira um token só. Mas `2027` pode sair como `20`
mais `27`. Duas quantidades da mesma natureza recebem partições completamente diferentes, e o
modelo tenta fazer aritmética sobre pedaços arbitrários — é como pedir para alguém somar números
que foram cortados em lugares diferentes. Tokenizadores recentes forçam dígito isolado, ou
grupos de três, exatamente para regularizar isso.

Código, segundo, e é o sintoma três do slide dois. Indentação é uma sequência longa de espaços, e
se o vocabulário não tem tokens dedicados a runs de espaço em branco, cada nível de indentação
custa tokens. Um arquivo Python bem formatado, com classes e métodos aninhados, gasta uma fração
nada desprezível do orçamento de contexto em espaço em branco. O que vocês veem por fora é o
assistente truncando o arquivo pela metade — num arquivo que tem menos palavras que um documento
que caberia inteiro. Os tokenizadores dos modelos de código têm tokens para quatro, oito,
dezesseis espaços justamente por isso.

Terceiro, línguas com poucos recursos. O corpus onde os merges foram aprendidos é dominado pelo
inglês. Uma língua sub-representada não recebe merges longos, então ela é cortada em pedaços de
um ou dois caracteres — e essa é a mesma mecânica do português, só mais severa.

Isso é medir tudo com uma régua calibrada para outra coisa. A régua funciona; a leitura fica
grossa onde ela não foi feita para medir. E o erro que eu quero desarmar aqui: quando um modelo
vai mal numa língua ou erra uma soma, a reação automática é culpar o modelo. Parte do déficit
está no tokenizador, é diagnosticável **antes** de qualquer treino, e não se corrige com mais
dados.

> 🗣️ "Quando o modelo erra uma soma, parte da culpa pode ser de quem cortou o número em dois. Isso é diagnosticável antes de treinar qualquer coisa."

> **Nota:** Bastidor: os três casos já apareceram na tela na medição 3 da demo — **apontar de
> volta para o terminal** em vez de descrever. Se a demo falhou, este slide vira o substituto
> dela e ganha os minutos que sobraram.

### Slide 12 · Fertilidade: o número que vira dinheiro e janela · 01:34–01:42

Agora o slide que eu considero o mais útil desta aula para a vida profissional de vocês, e é o
que fecha o sintoma com que eu abri.

A medida se chama **fertilidade**: tokens por palavra. E sobre um par paralelo — o mesmo conteúdo
em português e em inglês — a razão de fertilidade de português sobre inglês dá acima de um nos
tokenizadores dos modelos comerciais. O número exato é o que a gente mediu na demo há vinte
minutos; está anotado no quadro e é ele que vale, não uma estimativa minha.

Três razões se somam para isso. A primeira: o corpus onde os merges foram aprendidos é
majoritariamente inglês, então os pedaços longos e úteis do português simplesmente não estão no
vocabulário. A segunda: em byte-level, cada letra acentuada entra como dois bytes, que é o slide
8. A terceira: as palavras do português são em média mais longas e mais flexionadas que as do
inglês.

E a consequência é dupla, e as duas metades são concretas. Em dinheiro: a cobrança é por token,
na entrada e na saída, então o mesmo conteúdo em português sai mais caro — todo mês, em toda
chamada. **É a fatura do slide um.** Em janela de contexto: a janela é medida em tokens, então
cabe menos conteúdo. Um documento em português consome mais janela do que a tradução dele em
inglês. É a mesma bagagem numa mala menor: não mudou o que vocês querem levar, mudou quanto cabe.

Um detalhe técnico que parece pedante e é o erro número um do Lab 1: existem **duas** maneiras
de calcular essa razão, e elas não dão o mesmo número. A média das razões par a par, e a razão
dos totais. A segunda é uma média ponderada pelo comprimento, então ela pesa mais os pares
longos. Para dinheiro, a razão dos totais é a certa, porque a fatura soma tokens. Para
caracterizar o tokenizador, a média das razões com desvio-padrão é mais informativa. Quem
calcula uma e interpreta como a outra escreveu um número que não mede o que ele acha que mede.
A conta das duas está em A ponto quatro.

E antes que alguém conclua a coisa errada: a resposta não é escrever tudo em inglês. Tem
contrapartida — o conteúdo em português é o que o usuário lê e o que o domínio exige, e manter
duas versões é custo de manutenção. A alavanca honesta é escolher modelo e tokenizador adequados
à língua, e **medir antes de decidir**. É exatamente o que vocês vão fazer no exercício, agora.

> 🗣️ "A janela é medida em tokens, não em palavras. O mesmo documento em português ocupa mais janela do que a tradução dele — é a mesma bagagem numa mala menor."

> **Nota:** Bastidor: o número da razão PT/EN tem que estar no quadro, escrito, desde a demo. Se
> a demo falhou e não há número medido, conduzir o exercício com a razão como variável simbólica
> `r` e deixar o valor como `[medir no Lab 1]` — **nunca inventar o número**. A distinção entre
> as duas médias é nova na V2 no fluxo: dizer em uma frase e remeter a A.4, sem fazer a álgebra.

### Slide 13 · [Exercício] Três faturas, três diagnósticos · 01:42–01:50

Oito minutos, em dupla, e agora vocês usam o número que a gente mediu.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> 🗣️ "Três sintomas de fatura. Para cada um eu quero a causa e a conta que confirma — e a do item dois é a que mais gente erra na vida real."

> **Nota:** Bastidor: enunciado e correção na Parte 3. O preço de API é hipótese declarada do
> exercício, `US$ 0,50 por milhão de tokens de entrada` — dizer isso em voz alta e
> explicitamente, para ninguém sair da sala citando esse número como preço de provedor. Na V2 os
> três itens abrem por sintoma e o cálculo é a evidência; a conta pura do prompt de 300 palavras
> nas duas línguas virou extensão opcional.

### Slide 14 · Fechamento: perplexidade é por token · 01:50–02:00

Deixa eu fechar o laço que a gente abriu na abertura, e que na verdade foi aberto na aula passada.

A pergunta era: por que a perplexidade de dois modelos só é comparável se o tokenizador for o
mesmo? A fórmula está na tela, e o `N` ali é o número de **tokens**. Duas coisas mudam quando eu
troco o tokenizador. A primeira é óbvia agora: `N` muda, porque o mesmo texto tem contagens de
token diferentes — a gente acabou de medir isso na tela. A segunda é mais profunda: a
distribuição está definida sobre o vocabulário **daquele** tokenizador. São espaços de eventos
diferentes. Prever pedaços curtos é uma tarefa diferente de prever pedaços longos.

Então os dois números não medem a mesma coisa, e não é que a comparação seja imprecisa — ela é
sem sentido. A comparação honesta normaliza por uma unidade que não depende da decisão do
tokenizador: bits por caractere, ou bits por byte. Aí sim dá para comparar modelos com
vocabulários diferentes.

E eu quero deixar marcado o erro de quem quase acerta: não dá para consertar dividindo a
perplexidade pela razão de fertilidade. A relação entre as duas perplexidades é uma **potência**,
não um fator — e A ponto seis tem a conta, com um exemplo em que o mesmo modelo tem perplexidade
quatro e perplexidade duzentos e cinquenta e seis. Um fator de sessenta e quatro que veio
inteirinho da escolha do tokenizador. Vale ler, porque esse é o tipo de erro que passa por
revisão.

Bom, o resumo de hoje em uma linha: o token é uma decisão de engenharia, ela é congelada antes
do treino, e ela define custo, janela, qualidade em português e comparabilidade de métrica.

E a próxima aula. O BPE resolveu o vocabulário aberto, e agora o texto chegou ao modelo como uma
sequência de inteiros. Só que inteiro não significa nada: o ID quatro mil e vinte e um não é
maior que o quatro mil e vinte, não é parecido com ele, não tem nada a ver com ele — a numeração
é a ordem em que os merges foram aprendidos. Então o que faz um inteiro significar algo? Isso é a
Aula 3, Embeddings e representações vetoriais, e é onde a semântica finalmente entra.

Para a semana: rodar o script da demo num texto de vocês e anotar a fertilidade; fazer cinco
merges de BPE no papel com palavras de um domínio de vocês, conferindo contra A ponto um; e a
leitura do Sennrich, `1508.07909`, que é o artigo que trouxe o BPE para NLP.

> 🗣️ "O token é uma decisão de engenharia congelada antes do treino. Ela define quanto vocês pagam, quanto texto cabe e se a métrica de dois modelos pode ser comparada."

> **Nota:** Bastidor: escrever a fórmula da perplexidade no quadro ao lado do número de
> fertilidade medido na demo — as duas coisas juntas fecham o argumento visualmente. Projetar o
> índice do apêndice por 20 s antes de encerrar: são seis itens, e vale dizer duas frases só —
> A.6 é a resposta escrita da pergunta dirigida da Aula 1, e A.1 é a execução do BPE que eu não
> fiz no quadro. Terminar 02:00. Se atrasou, cortar a recapitulação em uma linha e proteger a
> ponte para a Aula 3: sem a pergunta do "inteiro que não significa nada", a Aula 3 abre sem
> gancho.

---

## Parte 2 — Demonstração guiada

Doze minutos, script `codigo/demo-tokenizacao.py` rodando no terminal projetado. O objetivo é que
a turma veja as **peças**, e não só a contagem: o mesmo texto partido de quatro formas diferentes
na mesma tela. Os quatro tokenizadores foram baixados na véspera e estão no cache do Hugging
Face — a demo é ao vivo e não pode esperar download.

Na V2 a demo carrega uma função a mais: a medição 4 (o mini-BPE) **substitui o quadro** que a V1
usava no slide 6. Ela é a evidência de que a lista de merges sai de um laço de contagem, não de
uma afirmação minha.

**1.** **[Abro o script no editor e mostro só o topo, com os quatro nomes de modelo]** Antes de
rodar, deixa eu mostrar o que está aqui dentro. Quatro tokenizadores de verdade: o BPE byte-level
do GPT-2, o WordPiece do BERT em inglês, o WordPiece de um BERT treinado em português, e o
Unigram do XLM-R, que é multilíngue. Nenhum brinquedo, nenhuma simulação — é o mesmo código que
vocês vão usar no Lab 1.

**2.** **[Rodo a medição 1 e deixo os tokens literais na tela]** Aqui está o mesmo parágrafo, em
português, partido pelos quatro. Olha as peças, não a contagem. O GPT-2 está cortando os acentos
no meio — aquele caractere esquisito é meio caractere, é um byte solto de UTF-8. O BERT português
está com pedaços que parecem morfemas de verdade. E o XLM-R está com aquele sublinhado marcando
início de palavra, que é a marca do SentencePiece que eu falei no slide 7.

**3.** **[Aponto a mesma frase em inglês, logo abaixo]** E agora a mesma frase em inglês, nos
mesmos quatro. Repararam na diferença de comprimento da lista? É o mesmo conteúdo. A informação
é idêntica. A conta de token não é. Isso aqui é a fatura do slide 1, em forma de lista.

**4.** **[Rodo a medição 2, com a tabela de fertilidade e a razão PT/EN]** Aqui está a medida
limpa: tokens por palavra, por tokenizador, por língua. E na última coluna a razão português
sobre inglês, com desvio. Esse número aqui — eu vou escrever ele no quadro agora, porque é ele
que vocês vão usar no exercício em quinze minutos. Duas coisas para notar. Primeira: o BERT
português comparado com o GPT-2 na mesma coluna é a prova de que o problema não é a técnica, é o
corpus onde os merges foram aprendidos. Segunda: repararam que eu estou reportando o desvio junto
com a média? Sem o desvio, eu não sei se o pior par é um vírgula quatro ou três vírgula zero — e
é o pior par que estoura a janela, não a média.

**5.** **[Rodo a medição 3, com os casos difíceis]** Agora os casos patológicos, todos na mesma
tela. A palavra longa, `inconstitucionalissimamente`, e quantos pedaços ela virou em cada um — é
o sintoma dois do slide dois, medido. Um número de quatro dígitos, e onde cada tokenizador
escolheu cortar. Um trecho de código Python com indentação, e quanto a indentação está custando —
sintoma três. E um emoji, que no GPT-2 passa liso por ser byte-level e nos outros pode virar
coisa estranha.

**6.** **[Rodo a medição 4, o mini-BPE treinado do zero]** E para fechar, o slide 6 virando
código. Este é um BPE escrito à mão em quarenta linhas, treinando no mesmo mini-corpus do slide —
`casa`, `casas`, `casinha`, `casarão`. Olha os merges saindo na ordem: `a` mais `s`, depois `c`
mais `as`, depois `cas` mais `a`. É exatamente a lista que eu anunciei no slide 6, e ela saiu de
um laço de contagem de pares adjacentes. Não tem mágica nenhuma no tokenizador.

**7.** **[Aponto a saída da medição 4 e a comparo com o slide 6 projetado ao lado]** E aqui está
a razão de eu não ter feito isso no quadro. Na tela eu tenho as contagens de cada rodada
impressas, e eu tenho a segmentação final das quatro palavras. Quem quiser acompanhar rodada por
rodada, com o desempate e com a codificação de uma palavra nova, tem isso escrito em A ponto um —
com cinco merges em vez de três. O que eu ganhei aqui foi tempo de bancada e um número na tela em
vez de uma conta na minha letra.

> **Nota de contingência:** Bastidor: se um tokenizador não carregar, o `try/except` avisa qual
> falhou e o script segue com os outros — comentar em voz alta que isso é proposital, e não um
> erro. Se a rede caiu inteira e nada carrega, a **medição 4 roda offline**, sem dependência de
> rede: fazer só ela e usar as capturas de tela da véspera para as medições 1 a 3. A medição 2 é
> a única cujo número é insubstituível — sem a fertilidade medida, o exercício da Parte 3 roda com
> a razão como variável simbólica `r` e o valor fica `[medir no Lab 1]`. Aumentar a fonte do
> terminal antes de começar: a turma do fundo precisa ler os tokens, não só o total.

---

## Parte 3 — Hands-on

Oito minutos, em dupla, com os três itens projetados. Na V1 este exercício eram três contas; na
V2 são três **sintomas de fatura**, e a conta é a evidência que confirma o diagnóstico. O
objetivo não mudou: fazer a decisão de tokenizador sair do plano abstrato e virar uma linha de
orçamento.

**1.** **[Projeto os três itens e anuncio a hipótese de preço]** Vou passar oito minutos com
vocês trabalhando, em dupla, e agora com o número que a gente mediu na demo. Uma coisa importante
antes: o preço que está no slide, cinquenta centavos de dólar por milhão de tokens de entrada, é
**hipótese deste exercício**. Não é o preço de nenhum provedor real. Ninguém sai daqui citando
esse número como se fosse tabela — o que vale é a aritmética, não o valor.

Para cada um dos três sintomas, eu quero duas coisas: a causa provável, e **que conta
confirmaria**. A segunda parte é a que vale.

Os três sintomas:

1. Um time atende em português e em inglês, mesmo produto, mesmo modelo. A fatura do lado
   português é visivelmente maior, e ninguém mudou nada no código.
2. Uma conversa de suporte com vinte turnos custou **muito** mais que vinte vezes um turno. O
   time dimensionou o orçamento por "custo de um turno vezes número de turnos" e errou por mais
   de uma ordem de grandeza.
3. Um assistente com janela de oito mil tokens funciona bem em texto corrido e **trunca**
   arquivos de código pela metade — mesmo em arquivos que têm menos palavras que documentos que
   caberiam inteiros.

*Bastidor — respostas e erros comuns:* (1) fertilidade maior em português; a conta que confirma é
contar tokens dos dois lados do mesmo conteúdo com o mesmo tokenizador e tirar a razão dos
**totais** — e a resposta completa tem a frase sobre a contrapartida de escrever em inglês, custo
de manutenção e fidelidade ao domínio. O erro comum é dizer "o modelo é pior em português", que é
outra afirmação e não explica a fatura. (2) o histórico é reenviado a cada chamada, então o custo
é a **soma dos prefixos**: `1+2+…+20 = 210` blocos de histórico, mais de dez vezes a estimativa
ingênua. Quase todo mundo responde "vinte vezes" por reflexo, e é o erro que aparece na fatura de
verdade. (3) indentação em runs de espaço, sem tokens dedicados a espaço em branco; a conta que
confirma é tokenizar o mesmo arquivo com um tokenizador de código e com um de texto e comparar. O
erro comum é usar a regra de bolso de quatro caracteres por token, que foi calibrada em inglês
jornalístico e não vale nem para português nem para código — e A.4 diz por quê.

*Como recolher:* cinco minutos de dupla, três de correção conduzida por mim. Não corrijo os três:
peço voluntário para o item 1 e **forço a segunda parte** — "que conta você faria?" —, corrijo o
3 em trinta segundos, e uso o resto do tempo no item 2. No 2 eu desenho a soma `1+2+…+20` no
quadro e deixo a sala ver o `210` aparecer. Encerro com a frase que emenda no fechamento: "essa
conta é a diferença entre uma prova de conceito que custa centavos e um produto que custa mais do
que rende — e nenhum dos três pedia derivar nada; os três pediam saber que conta fazer".

*Extensão para quem terminar antes (opcional):* a conta que na V1 era obrigatória — um prompt de
sistema de 300 palavras, em português e em inglês, com a razão medida, e a decisão de escrever o
prompt de sistema em inglês mantendo as respostas em português. E, para quem quiser um item mais
duro: quantas páginas de 500 palavras cabem numa janela de 8 mil tokens nas duas línguas, com a
armadilha de que uma fertilidade 33% maior **não** tira 33% das páginas (tira 25%) — a conta está
em A.4.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a derivação em
aula. A regra geral é remeter ao apêndice e seguir; conduzir uma derivação só se sobrar tempo, e
anunciando que é conteúdo de consulta.

> **Nota:** Bastidor: nesta aula o item 1 é o mais provável de todos, porque na V1 eu **fazia** os
> merges no quadro e alguns alunos vão sentir falta. A resposta padrão é: "a demo vai rodar isso
> em vinte minutos e imprimir as contagens; e A.1 tem cinco rodadas em vez de três". Se eu
> decidir fazer no quadro, o custo sai do Bloco 2, e a ordem de sacrifício é: primeiro o exercício
> em dupla, depois o slide 11 (que a medição 3 da demo sustenta sozinha), e **nunca** a medição 2
> da demo nem o slide 12 — sem o número da razão PT/EN, o exercício não roda e o argumento da
> aula fica sem evidência.

**Item 1 — "Faz os merges no quadro" (A.1, ~7 min).**
A pergunta mais provável do dia. Eu escrevo o mini-corpus com as quatro frequências e faço **uma**
rodada completa de contagem — os dez pares, com as contribuições de cada palavra ponderadas, e o
`(a,s)` ganhando com catorze. Depois eu digo que as rodadas 2 e 3 seguem o mesmo procedimento,
mostro a lista final e paro. **Não** faço as três rodadas inteiras: uma rodada mostra o
mecanismo, e as outras duas só repetem o procedimento com números menores. Se sobrar apetite, o
que vale de verdade é a rodada 5 de A.1, que é onde aparece o **empate quádruplo** e a conclusão
de que duas implementações corretas do BPE podem produzir listas diferentes — e é por isso que o
tokenizador viaja como arquivo junto com o modelo. Essa é a melhor pergunta que pode sair deste
slide.

**Item 2 — "De onde vem esse score do WordPiece?" (A.2, ~5 min).**
Aparece quando alguém desconfia que a fórmula é arbitrária. Quatro linhas no quadro: a
log-verossimilhança do corpus sob um modelo unigrama; o que muda ao fundir um par; o ganho sendo
a contagem do par vezes o log da razão entre a probabilidade do par e o produto das
probabilidades; e o reconhecimento de que aquilo é informação mútua pontual. Fecho com o exemplo
do `de` contra o `qu` e os dois números. Se não houver tempo nem para as quatro linhas, a versão
de dez segundos é: "o denominador transforma *frequente* em *se atraem*, e `q` em português nunca
aparece sem `u`".

**Item 3 — "Cadê a conta do `n²`?" (A.5, ~5 min).**
Vale fazer se a turma vier de uma Aula 1 com muita gente de sistemas, porque é a conta que eles
sabem fazer. Escrevo os dois termos por camada — um proporcional a `n` vezes `d²` para as
projeções e o feed-forward, outro proporcional a `n²` vezes `d` para a atenção —, divido um pelo
outro e mostro que a razão é `n` sobre `d`. Aí instancio: com `d` igual a quatro mil e noventa e
seis, contexto de dois mil é o feed-forward dominando, e contexto de trinta e dois mil é a
atenção dominando. E fecho com o efeito de encurtar: o primeiro termo cai linearmente, o segundo
cai ao quadrado. É a única derivação desta aula que eu faço com gosto no quadro, porque ela é
curta e muda a conclusão do slide 10.

**Item 4 — "Por que as duas médias da razão PT/EN dão diferente?" (A.4, ~4 min).**
Pergunta de aluno atento, e vale muito porque é o erro nº 1 do Lab 1. Escrevo a razão dos totais,
substituo cada contagem de português pela razão vezes a contagem de inglês, e mostro que sai uma
média das razões **ponderada pelo comprimento do lado inglês**. Aí digo a consequência: para
dinheiro use a razão dos totais, porque a fatura soma tokens; para caracterizar o tokenizador use
a média das razões com desvio. Três linhas e a sala nunca mais erra isso.

**Item 5 — "Mostra a conta da perplexidade" (A.6, ~5 min).**
Se vier, ela vem no fechamento e eu já estou em cima do relógio — então a versão curta é
obrigatória. Escrevo que a entropia é menos o log da verossimilhança do texto dividido pelo
número de tokens; digo que o numerador é o mesmo texto nos dois casos; logo as duas entropias
diferem pela razão dos números de tokens; exponenciando, uma perplexidade é a outra **elevada** à
razão. E dou o número: quatro por caractere vira duzentos e cinquenta e seis por subword com
quatro caracteres por token. Se não houver tempo nem para isso, a frase é "é uma potência, não um
fator, e A.6 tem a conta com o exemplo" — e a Aula 3 abre na semana seguinte de qualquer forma.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 14 da Parte 1 — a fórmula da perplexidade com `N`
em tokens, por que dois valores não são comparáveis, bits por caractere como normalização
honesta, o índice do apêndice projetado por vinte segundos, e a ponte para a Aula 3 pelo inteiro
que ainda não significa nada.

> 🗣️ "O tokenizador entregou uma sequência de inteiros, e inteiro não significa nada — o ID quatro mil e vinte e um não é parecido com o quatro mil e vinte. Semana que vem: o que faz um número significar algo."

---

*Roteiro do Instrutor · Aula 2 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
