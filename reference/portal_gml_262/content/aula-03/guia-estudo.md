# Embeddings e representações vetoriais

## Slide 1 · O sintoma: a busca que não acha o documento que está lá · 00:00–00:05

Boa noite, pessoal. Vou começar com uma falha que provavelmente já aconteceu com vocês.

Um time indexou dez mil documentos internos e montou uma busca. Alguém digita `médico` e o sistema
devolve zero resultados. Só que existe na base um documento inteiro sobre atendimento — ele fala de
`clínico`, de `doutor`, de `ambulatório`, do começo ao fim.

E aqui está a parte que interessa: **o sistema não errou a conta**. Ele calculou a semelhança entre a
consulta e aquele documento, achou zero, e estava certo. Dada a representação que ele recebeu, a
semelhança **é** zero. Nenhuma palavra da consulta aparece literalmente lá, e a representação que ele
tinha não sabe fazer mais nada além de comparar palavras literais.

Guardem esse zero. Ele vai aparecer medido, na tela, daqui a quarenta minutos.

> Ideia central: "O sistema não errou a conta. A conta deu zero porque a representação não tem onde guardar semelhança."

## Slide 2 · Três sintomas, uma causa · 00:05–00:10

Deixa eu amarrar isso com a aula passada e mostrar o plano de hoje.

Na Aula 2 a gente passou duas horas cortando texto em pedaços, e o resultado foi uma lista de
inteiros: `4021`, `8977`, `312`. Eu fechei aquela aula dizendo uma coisa que parece anticlímax — o ID
quatro mil e vinte e um não é parecido com o quatro mil e vinte e dois, e não é menor que ele em
nenhum sentido útil. É um endereço, não uma quantidade. E endereço não se soma.

A busca do slide anterior é o primeiro sintoma disso. Hoje eu tenho três, e eu quero os três na tela
ao mesmo tempo.

O primeiro é a busca que acabei de contar. O segundo: a palavra `banco`. Banco onde eu guardo
dinheiro e banco onde eu me sento na praça vão receber **um** vetor só, um para os dois. O terceiro:
aquela analogia famosa, rei menos homem mais mulher dá rainha. Ela funciona no modelo que eu vou
baixar hoje na frente de vocês, e ela vai **falhar** no modelo que vocês treinarem quarta-feira, no
Lab 1.

E eu vou ser honesto sobre o placar antes de começar. Dois desses três eu resolvo hoje. O do `banco`
eu **não** resolvo — ele fica aberto, de propósito, e ele é a razão pela qual as Aulas 5, 6 e 7
existem. Eu prefiro anunciar isso agora do que fingir no fim.

> Ideia central: "O ID quatro mil e vinte e um não é parecido com o quatro mil e vinte e dois. É um endereço, não um número — e endereço não se soma."

## Slide 3 · Por que a intuição não basta: "é só usar o índice" · 00:10–00:17

A primeira reação diante do slide 1 é sempre a mesma, e eu quero gastar ela antes que ela custe caro.

A reação é: o problema é o tamanho. Cinquenta mil dimensões para carregar um inteiro é desperdício,
então comprime, usa hashing, usa índice esparso. Vamos ver o que isso resolve.

A representação por índice tem um nome: one-hot. Vocabulário de tamanho V, cada palavra vira um vetor
de V posições, com um `1` na posição dela e zero em todo o resto. E ela tem dois problemas — um chato
e um fatal.

O chato é a esparsidade, e é esse que a intuição atacou. Desperdício de memória se resolve com
engenharia.

O fatal é a ortogonalidade, e esse não se resolve assim. Dois vetores one-hot distintos têm produto
interno zero, **sempre**, por construção — o `1` de um cai exatamente onde o outro tem zero. Produto
interno zero significa cosseno zero. Ou seja: neste espaço, `gato` e `gatinho` estão exatamente tão
longe quanto `gato` e `parafuso`. Todas as palavras equidistantes de todas as outras palavras.

E olha o que isso faz com o aprendizado. Se o modelo viu mil frases com `médico` e nenhuma com
`clínico`, não existe **nada** na representação em que ele possa se apoiar para transferir uma coisa
para a outra. Os parâmetros de `médico` e os de `clínico` são independentes por construção. Isso é o
slide 1 escrito de outra forma.

E sobre hashing, para fechar: se duas palavras caem em posições diferentes, elas continuam ortogonais
e o cosseno continua zero — a memória caiu e a semelhança continua ausente. Se elas colidem, ficam
**idênticas**, cosseno um. E quem decide a colisão é a função de hash, não o sentido: `gato` pode
colidir com `parafuso` e não com `gatinho`. Hashing troca "nenhuma semelhança" por "semelhança
arbitrária".

> Ideia central: "Em one-hot, `gato` e `gatinho` estão tão longe quanto `gato` e `parafuso`. O problema não é o desperdício de memória — é a ausência total de semelhança."

## Slide 4 · A hipótese distribucional · 00:17–00:24

Então a pergunta virou: de onde eu tiro semelhança entre palavras, sem que ninguém escreva um
dicionário à mão?

A resposta da área tem setenta anos e cabe numa frase, do Firth, de 1957: uma palavra é conhecida
pelas companhias que ela mantém. A formulação mais técnica é do Harris, três anos antes: palavras que
ocorrem em distribuições parecidas de contexto têm sentidos parecidos.

Deixa eu mostrar que isso não é filosofia. Vou inventar uma palavra: *glorp*. "O barista serviu o
glorp fumegante." "Tomei um glorp antes da prova para acordar." "Prefiro o glorp sem açúcar."
Ninguém aqui nunca viu essa palavra na vida e todo mundo já sabe o campo semântico dela. Vocês não
usaram definição — usaram só as companhias.

E o que faz disso engenharia é que a frase é programável. Escrita direito, ela é uma afirmação sobre
distribuição: se a probabilidade de cada contexto, dada a palavra um, é parecida com a probabilidade
de cada contexto, dada a palavra dois, então os vetores das duas devem ficar próximos. Isso é um
critério. Dá para otimizar, dá para medir. O ancestral direto é contar coocorrência numa matriz
gigante e reduzir a dimensionalidade dela; o Word2Vec, que é o Bloco 2 de hoje, faz a mesma aposta
trocando contagem por predição.

Agora a parte desconfortável, que eu prefiro dizer agora do que consertar depois. A hipótese **não**
diz que sinônimos ficam próximos. Ela diz que palavras com contextos parecidos ficam próximas.
`quente` e `frio` aparecem quase exatamente nos mesmos contextos — "a água está", "o dia amanheceu".
Então eles ficam vizinhos no espaço. Antônimos vizinhos não são um bug da implementação: são
**predição correta** da hipótese, e é uma limitação real do método.

> Ideia central: "Uma palavra é conhecida pelas companhias que ela mantém. Isso não é uma bonita frase de linguística — é um critério que dá para programar."

## Slide 5 · Vetores densos: semântica como geometria · 00:24–00:30

Se o critério é proximidade, então eu preciso de um espaço onde proximidade exista. E a virada é
simples de enunciar: em vez de V dimensões binárias, eu uso d dimensões de número real, com d entre
cinquenta e mil e pouco. Cada palavra é um ponto nesse espaço.

Duas coisas mudam de uma vez. A primeira: cinquenta mil dimensões viraram cem ou trezentas, e todas
carregam informação. A segunda, que é a que interessa: passa a existir noção de perto e longe, e
noção de direção. O significado deixa de estar num símbolo e passa a estar numa posição.

E eu preciso ser explícito sobre uma coisa que decepciona todo mundo na primeira vez: nenhuma
dimensão isolada é interpretável. Não existe "a dimensão da realeza", não existe "a dimensão do
feminino". Se vocês olharem a coordenada trinta e sete de dez palavras, não vão achar padrão nenhum.
As direções semânticas existem, mas são combinações das dimensões, não as dimensões.

Uma pausa para quem não fez aprendizagem de máquina, porque eu vou usar a palavra "treinar" umas
quarenta vezes hoje. Treinar aqui significa: começar com esses números aleatórios, medir um erro numa
tarefa qualquer, e ajustar os números na direção que faz o erro cair — em passinhos, milhões de
vezes. Por hoje é isso, e o mecanismo formal é a Aula 12. E os números que estão sendo ajustados aqui
são as próprias coordenadas das palavras.

> Ideia central: "Cinquenta números por palavra, e nenhum deles tem nome. O significado não está em nenhuma dimensão — está na posição."

## Slide 6 · A régua: cosseno, e o que ela permite decidir · 00:30–00:37

Se palavra é ponto num espaço, eu preciso de uma régua. E a régua padrão da área não é a que vocês
esperariam.

A régua é o cosseno do ângulo entre os dois vetores: produto interno dividido pelo produto das
normas. Deixa eu ler a fórmula em voz alta, apontando cada pedaço. O numerador mede alinhamento —
quanto os dois apontam para o mesmo lado. O denominador joga fora o comprimento dos dois. O resultado
é um número entre menos um e um: um quando apontam na mesma direção, zero quando são perpendiculares,
menos um quando são opostos.

A pergunta certa aqui é: por que cosseno e não distância euclidiana, que é a régua que todo mundo
aprendeu? E a resposta é concreta, não estética. Num espaço de palavras treinado, a norma do vetor —
o comprimento dele — correlaciona com a frequência da palavra no corpus. Palavra frequente recebe
muito mais atualização e tende a ter vetor mais longo. Então se eu uso distância euclidiana, eu
misturo duas perguntas: "esses sentidos são parecidos?" e "essas palavras aparecem com frequência
parecida?". Cosseno joga a magnitude fora e mede só a direção. É a pergunta que eu quero fazer.

E tem um par de exemplos que fecha o argumento, e que está no slide. Dois vetores de mesma direção e
tamanhos bem diferentes têm cosseno um e distância seis. Dois vetores de mesmo tamanho a sessenta
graus têm cosseno meio e distância cinco. Olhem a inversão: pelo cosseno o primeiro par é o mais
parecido; pela distância euclidiana o **segundo** par é o mais próximo. As duas réguas discordam, e o
primeiro par é exatamente o caso de `casa` e `residência` num corpus em que uma aparece cem vezes
mais que a outra.

Duas armadilhas que eu vejo em prova todo semestre. A primeira: cosseno não é probabilidade. Zero
vírgula sete não é "setenta por cento parecido" — não existe essa leitura. A segunda, mais séria:
cosseno não é comparável entre espaços diferentes. A escala é interna a cada espaço treinado. O que
dá para comparar é ordenação dentro do mesmo espaço.

> Ideia central: "Cosseno mede direção e joga a magnitude fora. E é isso que eu quero, porque a magnitude conta frequência, não sentido."

## Slide 7 · Analogias: a relação virou direção — e o terceiro sintoma · 00:37–00:43

Agora o resultado que fez essa área virar notícia em 2013, e a ressalva que quase nunca vem junto.

A observação é: vetor de rei, menos vetor de homem, mais vetor de mulher, e o vetor mais próximo do
resultado é rainha. A leitura correta disso é a seguinte: uma *relação* virou uma *direção*. O
deslocamento "masculino para feminino" é um vetor no espaço, o mesmo vetor, e ele funciona partindo
de vários pontos diferentes. Como "duas quadras ao norte" num mapa: vale saindo de qualquer esquina.
E ninguém programou isso. Não existe regra de gênero escrita em lugar nenhum do treino.

Agora o terceiro sintoma do slide 2, que é a parte que a maioria dos cursos omite.

Primeiro: o protocolo padrão de avaliação de analogia **exclui as três palavras de entrada** da lista
de candidatos. Isso não é fraude, é convenção — mas ela é indispensável, e não por elegância. Sem a
exclusão, o candidato que ganha é quase sempre uma das próprias entradas, porque o deslocamento é
pequeno comparado com os vetores e o ponto de chegada fica perto de onde saiu.

Segundo: categorias inteiras falham. País e moeda, por exemplo, é notoriamente ruim — e eu vou tentar
essa na demo, sem prometer resultado.

Terceiro: o efeito enfraquece muito em corpus pequeno, que é exatamente o regime em que vocês vão
treinar no Lab 1.

E o erro de leitura que eu quero matar aqui: analogia não é prova de que o modelo raciocina. É uma
soma de três similaridades com um máximo — literalmente isso, e está escrito em A.5. O modelo não sabe
o que é um rei.

> Ideia central: "A analogia funciona porque a relação é uma direção no espaço. Não porque o modelo sabe o que é um rei."

## Slide 8 · [Demo] Agora medido, não afirmado · 00:43–00:55

Chega de eu afirmar. Vou rodar isso agora e vocês julgam.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> Ideia central: "Eu não escrevi nenhuma dessas relações. Elas caíram de contar quem aparece perto de quem."

## Slide 9 · Word2Vec: CBOW × skip-gram · 01:05–01:14

Voltando. Antes do intervalo eu mostrei o espaço já pronto. Agora a pergunta que importa: como é que
esses vetores foram parar nessas posições?

A resposta canônica é o Word2Vec, do Mikolov e colegas, 2013 — arXiv 1301.3781, e é a leitura de
hoje. Ele tem duas arquiteturas, e as duas são rasíssimas: uma tabela de vetores, uma multiplicação e
uma saída. Não tem profundidade nenhuma, e é parte do motivo de ter funcionado em escala em 2013.

A primeira é o CBOW. Eu tapo uma palavra da frase, junto os vetores das palavras em volta — a média
deles — e peço que o modelo adivinhe qual palavra estava no buraco. É prova de lacuna. É rápido,
porque cada janela gera um exemplo só, e se comporta melhor nas palavras frequentes.

A segunda é o skip-gram, e ela é o inverso: eu dou a palavra central e peço que o modelo adivinhe cada
uma das palavras da vizinhança, uma por uma. É mais lento, porque cada janela gera vários pares, e é
melhor em palavras raras e em corpus pequeno — que, de novo, é o regime do lab de quarta.

E tem um terceiro botão que quase ninguém comenta e que muda muito o espaço resultante: o tamanho da
janela. Janela pequena, duas palavras para cada lado, captura palavras que ocupam o mesmo lugar na
frase — coisas substituíveis. Janela grande, dez para cada lado, captura palavras do mesmo assunto.
Com janela pequena, o vizinho de `Recife` tende a ser outra cidade. Com janela grande, tende a ser
`praia`, `frevo`, `porto`. Nenhuma das duas está errada; são espaços que respondem perguntas
diferentes.

> Ideia central: "CBOW pergunta 'que palavra cabe neste buraco?'. Skip-gram pergunta 'que companhias esta palavra costuma ter?'. Não é a mesma tarefa, e não dá o mesmo espaço."

## Slide 10 · O softmax de cem mil classes e a amostragem negativa · 01:14–01:23

Tem um problema de custo escondido no que eu acabei de descrever, e a solução dele é o truque de
engenharia mais bonito do artigo.

Quando eu digo "o modelo adivinha qual palavra estava no buraco", isso é uma classificação com uma
classe por palavra do vocabulário. Cem mil classes. E para transformar as pontuações em probabilidade
eu preciso do softmax, que normaliza sobre **todas** as classes — ou seja, para cada exemplo de
treino eu toco em todas as cem mil palavras.

Deixa eu dar a ordem de grandeza, porque ela não é uma constante ruim. Cem mil classes, dimensão cem,
um bilhão de pares de treino: só as exponenciais do denominador dão dez elevado a catorze operações
por época. Isso não fecha em orçamento nenhum.

A amostragem negativa reescreve a tarefa em vez de aproximar a conta. A pergunta deixa de ser "qual
das cem mil palavras é a certa?" e passa a ser: eu te dou um par palavra-e-contexto, e você me diz se
esse par é real, tirado do corpus, ou se eu o sorteei. Classificação binária. Para cada par real eu
sorteio k pares falsos — k na casa de cinco a vinte — de uma distribuição unigrama distorcida, com a
frequência elevada a três quartos, que é um jeito de não sortear `de` e `que` o tempo inteiro.

O objetivo por par está no slide, e eu vou ler em vez de derivar: log sigmoide do produto interno do
par real, mais a soma, sobre os k negativos, de log sigmoide do produto interno **negado**. Em
português: empurre o produto interno do par real para cima, empurre o dos k falsos para baixo.

E aqui está o número da aula. O custo por exemplo caiu de cem mil para k mais um. Com k igual a cinco,
de cem mil para seis — da ordem de **dezessete mil vezes menos trabalho** por exemplo de treino. É
esse número que transforma "bilhões de exemplos" de impossível em uma tarde de CPU.

Agora a leitura errada que eu quero desmontar. Amostragem negativa **não** é o softmax feito com
preguiça. Ela muda o objetivo — é outro problema de otimização. E dá para dizer de qual: no ponto
ótimo, o produto interno entre a palavra e o contexto é igual à informação mútua pontual daquele par
menos o log de k. Ou seja, esse treino **fatora implicitamente** uma matriz de coocorrência que ele
nunca chega a construir. Está em A.4, com a referência, e é uma das coisas mais bonitas do
material desta aula. Isso vai acontecer de novo várias vezes neste curso: trocar o objetivo por um
mais barato e descobrir que o barato é também o melhor.

> Ideia central: "Em vez de perguntar 'qual das cem mil palavras é a certa', eu pergunto 'este par é real ou eu sorteei?'. Cem mil viraram seis."

## Slide 11 · Tarefa-proxy: o objetivo de treino não é o produto · 01:23–01:31

Agora o slide mais importante da aula, e eu vou parar de andar para dizer isso.

Olha o que a gente acabou de montar. Um modelo que recebe uma palavra e prevê as palavras da
vizinhança. Eu pergunto a vocês: quem quer isso? Que produto é esse? Ninguém acorda de manhã querendo
um preditor de palavra de contexto. O modelo, em si, é inútil.

O que a gente queria era outra coisa. A gente queria a **matriz de embedding** — a tabela de vetores
que fica *dentro* dele, que numa visão ingênua é só um parâmetro interno do treino. O treino existiu
para forçar o modelo a organizar aquele espaço, porque só organiza bem o espaço quem captura de fato
quais palavras vivem em quais contextos. Terminado o treino, joga-se o modelo fora e leva-se a tabela.

E tem uma segunda propriedade aí, que é a que muda a escala do que é possível: esse treino é
auto-supervisionado. O rótulo — qual palavra estava perto — vem do próprio texto. Não tem anotador
humano, não tem dataset rotulado, não tem custo de rotulagem. Dá para treinar em qualquer quantidade
de texto que exista no mundo.

Deixa eu cravar o que isso tem a ver com o resto do curso, porque é a razão de este slide existir.
Quando a gente chegar na Aula 12 e eu disser que um LLM é pré-treinado para prever o próximo token,
alguém vai perguntar "mas prever o próximo token é útil?". Não é. É a mesma jogada de hoje, em escala
industrial: a tarefa não interessa, interessa o que o modelo tem que aprender para acertá-la. O
Word2Vec é essa ideia numa página; o GPT é essa ideia com trilhões de tokens.

> Ideia central: "O modelo que eu treinei é lixo. Eu queria a tabela de pesos que ficou dentro dele — e essa mesma jogada, escalada, é o que produz um LLM."

## Slide 12 · O sintoma que hoje não se resolve: `banco` · 01:31–01:39

E agora eu volto no segundo sintoma, o que eu marquei como aberto no começo da aula.

A palavra `banco`. Banco onde eu guardo dinheiro, banco onde eu me sento na praça, banco de dados,
banco de areia. No que a gente construiu hoje, `banco` tem **um** vetor. Um só. Ele é olhado numa
tabela pelo ID e devolvido igual, sempre.

E vocês viram isso acontecer, na Medição 4. Deixa eu rolar a tela de volta. Vizinhos de `bank`: tem
`banking`, tem `credit`, tem coisa de finanças — e tem `river`, tem `shore`, tem coisa de margem de
rio. Na mesma lista, porque é o mesmo vetor. Não é ruído: é o vetor sendo exatamente o que ele é. Um
compromisso entre dois sentidos que não têm nada a ver, parado numa região do espaço que não descreve
bem nenhum dos dois.

E o mesmo vale para `manga`, `ponto`, `letra`, `sela`. Português é cheio disso.

A pergunta que sempre vem é: treina mais? Aumenta a dimensão? Não resolve, e a razão é a interface,
não a capacidade. A operação é uma consulta a uma tabela por ID: entra um número, sai uma linha. **A
frase não participa da conta.** Nenhuma quantidade de dados conserta uma função que não recebe o
contexto como argumento — e A.3 tem isso escrito como equação: o que o método estima é a *mistura*
das duas distribuições de contexto, e nenhum d maior muda o alvo.

Então o conserto tem que ser outro: a representação da palavra precisa depender da frase em que ela
está. Isso muda a natureza do objeto — de tabela para função — e o mecanismo que faz exatamente isso
é a atenção. **É aqui que eu paro e não resolvo.** Este sintoma fica aberto hoje, e ele fecha na
Aula 6, com uma fórmula de uma linha que vocês vão ver escrita lá.

> Ideia central: "`banco` tem um vetor só, e ele fica num lugar que não descreve nem o banco de dinheiro nem o banco da praça. O problema não é falta de dados — é que a frase não entra na conta."

## Slide 13 · [Exercício] Decidir e diagnosticar, não calcular · 01:39–01:50

Oito minutos com vocês trabalhando, em dupla, e três de correção comigo.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> Ideia central: "Nenhum dos três itens pede uma conta. Os três pedem saber o que a geometria prevê."

## Slide 14 · Fechamento: de vetor estático a vetor contextual · 01:50–02:00

Deixa eu juntar as peças, e eu vou fechar pelo placar dos três sintomas.

Sintoma um, a busca que não achava o documento: **resolvido**. Significado virou posição, e cosseno é
a régua. Duas palavras com contextos parecidos ficam próximas, e a busca passa a poder recuperar
`clínico` quando alguém pede `médico`, sem ninguém cadastrar sinônimo à mão.

Sintoma três, a analogia que falha no corpus pequeno: **explicado**. Não é bug, e não é modelo ruim. A
direção da relação é uma média de estimativas ruidosas, o `min_count` corta a cauda onde as palavras
interessantes moram, e o protocolo exclui as entradas por uma razão que agora vocês sabem qual é. Isso
está em A.5 e é a resposta da pergunta dirigida de hoje.

Sintoma dois, o `banco`: **aberto**. E fica aberto de propósito. Um vetor por palavra não dá conta de
palavra ambígua, e não tem conserto dentro deste paradigma, porque a frase não entra na função. Essa
trinca é o motivo pelo qual as próximas quatro aulas existem.

No meio de tudo isso, três ideias que sustentam a aula. A hipótese distribucional, que transformou
"sentido" num critério programável. O cosseno, que mede direção e ignora frequência. E a tarefa-proxy,
que é a ideia mais transferível de hoje: o modelo é descartável, o que se leva é a representação que
ele foi obrigado a construir.

Na quarta é o Lab 1, e é onde tudo isso vira código na mão de vocês: comparar o BPE do GPT com o
WordPiece do BERT no mesmo texto, medir a razão de tokens entre português e inglês num corpus
paralelo, treinar um Word2Vec pequeno em português com o gensim, e projetar o espaço em duas dimensões
para olhar os vizinhos e testar analogias. Quem rodou o script da demo hoje em casa chega no lab com o
modelo em cache e ganha quinze minutos de vida.

A leitura é o Mikolov — arXiv 1301.3781. E a pergunta dirigida, que é para chegar respondida no lab:
no artigo o corpus tem bilhões de palavras; no lab vocês vão treinar em poucos megabytes. Quais
analogias vão falhar nesse corpus pequeno, e por quê? Eu quero a hipótese escrita *antes* de rodar. E
dessa vez com uma vantagem: com A.5 ao lado, a hipótese de vocês pode citar mecanismo em vez de
adjetivo.

> Ideia central: "Hoje o significado virou posição. Falta ele virar função da frase — e é isso que a atenção faz, a partir da Aula 5."

---

## Parte 2 — Demonstração guiada

Doze minutos, rodando `codigo/demo-embeddings.py` no terminal ou no Colab. O modelo pré-treinado tem
de estar em cache antes da aula — o download é da ordem de cem megabytes e não se faz na frente da
turma. Na V2 a demo deixa de ser ilustração e passa a ser **a evidência dos três sintomas** com que eu
abri a aula.

Insumos da véspera: modelo em cache, o script rodado uma vez com a saída salva em texto, e o modo
`--offline` testado.

**1.** **[Abro o script no editor, com a tela dividida entre código e terminal]** Isso aqui tem quatro
medições e cada uma responde a um slide que a gente acabou de ver. A primeira não usa modelo nenhum, é
NumPy puro: eu monto os vetores one-hot de quatro palavras e imprimo a matriz de cossenos entre todos
os pares. E olha uma coisa no código: a função de cosseno está escrita à mão, com a fórmula do slide
6, exatamente para vocês verem que não tem mágica de biblioteca aqui.

**2.** **[Rodo a Medição 1 e aponto para a diagonal e para fora dela]** Olha o que saiu. Um na
diagonal, porque cada palavra é idêntica a si mesma. E zero em absolutamente todo o resto — `gato`
com `gatinho`, zero vírgula zero zero; `gato` com `parafuso`, zero vírgula zero zero. São doze pares
distintos e doze zeros. Aquele slide do one-hot que eu afirmei há vinte minutos está aqui medido, e
esse `0,00` é literalmente o número que a busca do slide 1 calculou.

**3.** **[Carrego o modelo pré-treinado a partir do cache]** Agora eu carrego um espaço de embeddings
que alguém treinou em bilhões de palavras de Wikipédia e notícias. Cem dimensões por palavra,
vocabulário na casa das centenas de milhares. Está em inglês — o modelo em português é o que vocês vão
treinar no lab.

**4.** **[Rodo a Medição 2 e leio as listas de vizinhos em voz alta]** Vizinhos de `king`. Vizinhos de
`python` — e olha a graça: aparece linguagem de programação e aparece cobra, porque a palavra é
ambígua e o corpus tem os dois. Guardem isso, que vai voltar. Vizinhos de `hospital`. Eu vou ler em voz
alta porque eu quero que vocês percebam uma coisa: não existe, em lugar nenhum desse pipeline, uma
pessoa que escreveu "cirurgião é parecido com hospital". Isso caiu de contar quem aparece perto de
quem.

**5.** **[Rodo a Medição 3 e mostro os três primeiros candidatos de cada analogia]** Agora as
analogias. A primeira é a de gênero, do slide 7 — a que costuma funcionar. O script imprime os três
candidatos mais próximos e marca se a palavra esperada apareceu. A segunda é de país e moeda, que é uma
categoria notoriamente ruim. Vou rodar as duas sem prometer resultado, porque eu não decorei o que
sai.

**6.** **[Aponto a linha de `sim | NÃO` da segunda analogia]** E aqui está a parte mais útil da demo.
Essa falhou — o script imprimiu, com essas letras, que a palavra esperada **não** apareceu no top-3.
Isso não é o script quebrado: é o slide 7 acontecendo. Analogia é regularidade estatística, funciona em
algumas categorias e não em outras, e quem só viu o exemplo do rei e da rainha sai da graduação achando
que o método é sólido. Ele é útil e é frágil, as duas coisas. O terceiro sintoma da minha lista está
medido nessa linha.

**7.** **[Rodo a Medição 4, com os vizinhos de `bank`, conto em voz alta quantos são de cada campo e
deixo a lista na tela]** Última medição, e é a que eu vou cobrar de vocês daqui a meia hora. Vizinhos
de `bank`. Olha a lista e vamos contar juntos: quantos desses dez são de finanças e quantos são de
margem de rio? *[conto em voz alta e anoto os dois números no quadro]* Na mesma lista, porque é o mesmo
vetor. Essa lista fica na tela e eu volto nela no slide 12.

---

## Parte 3 — Hands-on

Oito minutos em dupla, três de correção, com os três itens projetados. O objetivo dos dois primeiros é
forçar a aplicação da hipótese distribucional contra a intuição; o do terceiro é ensaiar o diagnóstico
que o Lab 1 vai cobrar. O item 3 é novo na V2: na V1 eu pedia um jeito de separar os sentidos de
`banco` com o ferramental do dia, e a resposta honesta era "não dá" — a frustração era produtiva, mas
o aluno saía sem praticar diagnóstico.

**1.** **[Projeto os três itens e formo as duplas]** Oito minutos, em dupla. Três itens, e eu quero
resposta escrita nos três.

Item um: cinco pares de palavras. `médico` e `enfermeiro`. `gato` e `parafuso`. `quente` e `frio`.
`Recife` e `Fortaleza`. `comer` e `comida`. Ordenar do cosseno esperado mais alto ao mais baixo, com
uma frase de justificativa por par.

Item dois: duas tarefas — sugerir termos substituíveis num campo de busca, e agrupar documentos por
assunto. Para cada uma, janela pequena ou janela grande, com a justificativa.

Item três, e é o que vale mais: um time treinou embeddings próprios num corpus de poucos megabytes e as
analogias falham quase todas. O mesmo teste funciona no modelo baixado da internet. Eu quero **duas
causas prováveis** e, para cada uma, **que evidência do próprio notebook confirmaria**. A segunda
parte é a que vale.

*Como recolher:* oito minutos de dupla, três de correção conduzida por mim. Não corrijo tudo: peço
voluntário para a ordenação do item um e vou direto ao par de antônimos, que é onde a sala aprende. Do
item dois, corrijo só a tarefa de busca. E gasto os dois minutos finais no item três, forçando a
segunda coluna — a pergunta que eu repito para cada dupla é "e como você confirmaria isso no
notebook?". Fecho com a frase que emenda no slide 14: "reparem que nenhum dos três pedia conta, e o
terceiro é literalmente a questão-guia três do lab de quarta".

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a álgebra em aula.
A regra geral é remeter ao apêndice e seguir; conduzir uma derivação só se sobrar tempo, e anunciando
que é conteúdo de consulta.

**Item 1 — "Como é que se prova que one-hot não generaliza?" (A.1, ~3 min).**
A pergunta mais barata da aula e a que eu faço com mais gosto, porque a resposta é curta. Eu escrevo
no quadro o produto interno de dois one-hot como uma soma de V parcelas, mostro que cada parcela é um
produto de dois números que valem zero ou um, e que a parcela só é diferente de zero quando as duas
posições coincidem — o que só acontece se for a mesma palavra. Três linhas. E fecho com a consequência
que interessa: numa camada linear sobre entrada one-hot, a saída depende só da linha daquela palavra,
logo nenhum exemplo com `médico` altera um único número associado a `clínico`.
**Versão de 30 segundos:** "o `1` de um cai onde o outro tem zero, sempre — então o produto interno é
zero para qualquer par distinto, e os parâmetros de cada palavra são atualizados só por ela mesma."

**Item 2 — "Por que cosseno e não distância euclidiana?" (A.2, ~4 min).**
A pergunta mais provável do Bloco 1 e a mais legítima. Se eu decidir gastar os quatro minutos, o que
rende **não** é a derivação da fórmula: é o par de contraexemplos. Eu escrevo dois vetores de mesma
direção e tamanhos oito e dois, e dois vetores de tamanho cinco a sessenta graus. Calculo cosseno e
distância nos dois casos — um e seis contra meio e cinco — e mostro que as duas réguas **ordenam ao
contrário**. Depois digo por que o primeiro caso é o caso do espaço de palavras: palavra frequente
recebe mais atualização e fica com norma maior.
**Versão de 30 segundos:** "a norma conta frequência, e frequência não é sentido — a euclidiana mistura
as duas coisas e o cosseno separa. O contraexemplo numérico está em A.2, e lá também está o caso em
que as duas coincidem: vetores normalizados."

**Item 3 — "De onde vem esse objetivo da amostragem negativa?" (A.4, ~6 min).**
A derivação mais caçada do Bloco 2, e a mais caro. Se houver tempo, eu conduzo em três movimentos: o
softmax normalizando sobre V e o custo disso; a troca da pergunta para "real ou sorteado", com a
sigmoide entrando como probabilidade de uma decisão binária; e o objetivo com os k termos negativos,
lendo cada termo como um atrator e k repulsores. **Não** faço o ponto ótimo no quadro — a conta da PMI
deslocada é a parte mais bonita e a mais lenta, e está escrita em A.4 com a referência.
**Versão de 30 segundos:** "trocar 'qual das cem mil' por 'este par é real ou sorteado' derruba o custo
de cem mil para seis por exemplo. E não é aproximação do softmax: no ótimo, o produto interno vira a
informação mútua pontual menos o log de k — é fatoração implícita de uma matriz de coocorrência, e
está em A.4."

**Item 4 — "Por que o expoente três quartos?" (A.4, ~2 min).**
A resposta honesta é a mais curta: é escolha empírica do artigo, e não existe derivação. O que eu posso
fazer em dois minutos é mostrar **o que ele faz**: pego duas palavras com frequências que diferem por
um fator cem e mostro que, elevando a três quartos, o fator cai para trinta e um e meio. A palavra
comum continua sendo sorteada mais, mas três vezes menos desproporcionalmente.
**Versão de 30 segundos:** "não tem derivação — o artigo testou e funcionou melhor que os extremos. O
efeito é comprimir as razões de frequência: um fator cem vira um fator trinta e um. A conta está em
A.4."

**Item 5 — "Por que a analogia funciona, então?" (A.5, ~5 min).**
Vale fazer se sobrar tempo, porque desmonta a mística e prepara o Lab 1. Eu escrevo o objetivo como um
máximo de cosseno contra `b menos a mais c`, e mostro que, com vetores normalizados, ele se abre em
uma soma de três cossenos, porque a norma do alvo não depende do candidato. E aí a mágica acaba: o que
o método faz é procurar quem é mais parecido com `b`, mais parecido com `c` e menos parecido com `a`.
Fecho com a consequência que quase ninguém conhece: sem excluir as três entradas, o vencedor é uma
delas, porque o `cos` de um vetor consigo mesmo é um inteiro no escore.
**Versão de 30 segundos:** "é uma soma de três similaridades com um máximo, não uma inferência. E o
protocolo tem que excluir as três palavras da entrada, senão o vencedor é uma delas. Está em A.5, com
a decomposição escrita."

## Ordem de sacrifício

Se a aula atrasar: corto primeiro a **Medição 2 da demo** (as listas de vizinhos viram leitura da saída
salva), depois encolho a **tarefa-proxy** de 8 para 5 min mantendo só a frase-âncora e a ponte com a
Aula 12, e só então mexo no **exercício**, reduzindo de três itens para o item 1 e o item 3.
**Não corto** a Medição 1 — sem o `0,00` medido a abertura fica sendo afirmação minha. **Não corto** a
Medição 4 nem o slide 12: sem eles o `banco` não fica na cabeça de ninguém, e o gancho da Aula 6 morre
com a aula. E **não corto** o item 3 do exercício, porque ele é a questão-guia 3 do Lab 1 ensaiada.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 14 da Parte 1 — o placar dos três sintomas (resolvido,
explicado, aberto), as três ideias que sustentam a aula, a ponte para a Aula 4 (Laboratório 1:
Tokenizadores e embeddings) e a leitura de Mikolov et al. com a pergunta dirigida sobre corpus pequeno,
agora respondível com mecanismo por causa de A.5.

> Ideia central: "Hoje a gente transformou palavra em ponto e sentido em distância. Quarta-feira vocês fazem isso com as próprias mãos, em português — e vão descobrir no corpus de vocês tudo o que um corpus pequeno não consegue aprender."

---

*Roteiro do Instrutor · Aula 3 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
