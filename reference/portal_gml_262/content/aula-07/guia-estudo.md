# Transformer II: posição, normalização e o bloco moderno

## Slide 1 · O sintoma que a Aula 6 deixou na tela · 00:00–00:05

Boa noite, pessoal. Eu vou começar exatamente onde a gente parou, porque a aula passada
terminou com um defeito na tela.

Na última demo eu embaralhei os tokens da frase e rodei de novo. E a saída de cada token não
mudou — idêntica, a menos de permutação. Vocês viram isso acontecer.

Deixa eu traduzir o que aquilo custa. Do jeito como o mecanismo está, "o cachorro morde o
homem" e "o homem morde o cachorro" produzem exatamente as mesmas representações. As mesmas.
Não é um caso raro nem um erro de treino: é o que a fórmula faz, sempre. E isso é fatal para
qualquer tarefa que dependa de ordem — que é praticamente toda tarefa de linguagem.

Então a aula de hoje tem duas metades, e as duas são consertos. Na primeira eu conserto a
posição: como se enfia "onde cada token está" dentro de um mecanismo que só sabe comparar
pares. Na segunda eu conserto o treino: por que aquele bloco, empilhado quarenta vezes, não
treinaria sem duas coisas que eu ainda não mostrei. No fim da aula o bloco moderno está
montado, e ele é literalmente o que vocês vão implementar no Lab 2.

> Ideia central: "O mecanismo que a gente montou na aula passada não sabe que ordem existe. E isso não se corrige com if."

## Slide 2 · Por que a intuição sozinha erra aqui · 00:05–00:10

Antes de eu mostrar as soluções, deixa eu gastar a objeção que metade da sala está formulando
agora, porque ela é boa.

"Mas a máscara causal não resolve isso? Ela já não diz que o token 3 vem depois do token 1?"

Não resolve, e o motivo é sutil. A máscara diz **quem pode ser lido** por quem — ela apaga
metade da matriz. Ela não diz **onde** cada token está, nem quanta distância separa dois
tokens que ela permitiu. Dois tokens visíveis são, entre si, indistinguíveis quanto à
distância que os separa.

E tem um caso que encerra a discussão de uma vez: no encoder não existe máscara nenhuma. Lá o
problema aparece puro, sem nada para disfarçar.

A segunda intuição errada é mais sutil: "com dados suficientes o modelo aprende a ordem". Não
aprende. Não tem nada na entrada que codifique ordem para ele aprender — é como pedir que o
modelo aprenda a cor de um texto que chegou em preto e branco.

Então o que a gente precisa é **injetar** posição em algum ponto do cálculo. E o resto do
primeiro bloco é a história de três lugares diferentes onde a área tentou injetar.

> Ideia central: "Máscara é sobre permissão de leitura. Posição é sobre distância. São duas coisas diferentes, e só uma delas está no mecanismo."

## Slide 3 · A primeira resposta: um código somado na entrada · 00:10–00:17

Primeira tentativa, a do paper original, e ela é engenhosa. Em vez de ensinar a rede a contar,
dar a ela um código de posição pronto e somar no embedding do token, antes da primeira camada.

O código é um vetor de senos e cossenos com frequências geometricamente espaçadas. Está no
slide: seno nas dimensões pares, cosseno nas ímpares, e a frequência caindo geometricamente
com o índice do par. A entrada da rede passa a ser o embedding do token mais o código da
posição.

A analogia que eu uso é um relógio com muitos ponteiros em velocidades diferentes. O ponteiro
rápido distingue vizinhos imediatos; o lento distingue começo, meio e fim da frase. Combinados,
dão um código único para cada posição.

E tem uma propriedade embutida que é o motivo de a construção ser essa, e não outra: o produto
interno entre duas codificações depende **só da distância** entre elas, não de onde elas estão.
A codificação da posição 5 comparada com a da 8 dá o mesmo número que a da 1000 comparada com
a da 1003. Isso é o que abre a porta para a rede extrair distância relativa de um código que é
absoluto — e daqui a pouco eu vou medir isso na tela em vez de afirmar.

Aí sempre vem a objeção legítima: "somar não estraga o embedding? Não seria melhor concatenar?"
A rede aprende a usar subespaços diferentes para as duas informações. Somar é decisão de
engenharia — custa zero dimensão extra — e não uma verdade matemática. Concatenar funciona;
gasta dimensão.

> Ideia central: "Em vez de ensinar a rede a contar, o paper de 2017 deu um relógio de vários ponteiros para cada posição."

## Slide 4 · A segunda resposta, e o sintoma que ela produz · 00:17–00:24

Segunda tentativa, a mais óbvia de todas: em vez de calcular o código, aprender ele. Uma
tabela de vetores, um por posição, treinada junto com o resto. A soma na entrada é idêntica;
o que muda é que o código deixou de ser função e virou parâmetro.

Funciona bem. E produz um sintoma que é bonito de diagnosticar, então deixa eu descrever ele
como sintoma antes de dar o nome.

O cenário: um modelo responde bem em prompts curtos, e a partir de um certo comprimento passa
a produzir texto incoerente. Sempre o **mesmo** comprimento, em qualquer assunto. Não degrada
suavemente: quebra. E se você tiver sorte, aparece um `IndexError` no log.

A causa é que a tabela tem 4096 linhas e alguém pediu a linha 4097. Não é que o modelo fique
ruim naquela posição — é que não existe entrada na tabela. A posição 4097 não foi treinada
mal: ela não existe.

E tem um segundo teto, mais sutil, que explica por que a extrapolação já é ruim bem antes do
limite: não há nenhuma noção de distância embutida. O modelo tem que aprender, a partir de
vetores arbitrários e independentes, que a posição 31 é vizinha da 30 — e ele aprende isso
separadamente para cada par de posições que apareceu nos dados.

A comparação que eu faço é régua contra gaveta de etiquetas. A senoidal é uma régua: a marca
4097 é calculável, existe por construção, e a distância entre duas marcas é propriedade da
régua. A aprendida é uma gaveta de etiquetas numeradas: a etiqueta 31 existe porque alguém
imprimiu, e ela não sabe nada sobre a 30.

E aqui tem uma lição que vale para além desta aula: a intuição de que "aprendido é melhor
porque é aprendido" falhou. Neste caso, mais parâmetro comprou menos generalização.

> Ideia central: "Senoidal é uma régua: a marca 4097 é calculável. Aprendida é uma gaveta de etiquetas: a 4097 existe se alguém imprimiu."

## Slide 5 · A terceira resposta: a posição entra dentro do score · 00:24–00:35

Terceira tentativa, que é o centro da aula e o que os modelos modernos fazem. E ela começa
com uma mudança de lugar: as duas anteriores injetam posição na **entrada**, antes da primeira
camada. Esta não toca na entrada. Ela age dentro da atenção, depois da projeção, sobre Q e K —
e não sobre V.

A operação é uma rotação. Cada par de dimensões do vetor é tratado como um vetorzinho 2D, e a
posição `m` gira esse par por um ângulo proporcional a `m`, com a velocidade angular caindo
geometricamente com o índice do par — a mesma família de frequências das senoidais, agora
usada como velocidade de giro em vez de valor de tabela.

E agora o resultado que decide a aula, que está na terceira linha do slide: quando eu faço o
produto interno de um vetor girado por `m` vezes theta com outro girado por `n` vezes theta,
os ângulos absolutos **se cancelam** e sobra a diferença. Deixa eu dizer isso na língua da
aula passada: o **score de atenção** — aquele número dentro do softmax que decide o quanto o
token `m` presta atenção no token `n` — passa a depender de `m` menos `n`. Posição relativa
apareceu dentro do score, sem nenhum parâmetro novo e sem tocar no conteúdo.

A analogia são dois ponteiros de relógio girando em velocidades diferentes. Não interessa onde
cada ponteiro está no mostrador. Interessa o ângulo entre eles — e o ângulo entre eles só
depende de quantas horas separam os dois.

E é por isso também que não se aplica rotação em V. V é o conteúdo que vai ser agregado e
somado. Girar o conteúdo faria o que o token carrega depender da posição absoluta dele, e é
exatamente isso que a gente não quer.

Daqui a pouco eu meço isso. O número que vai aparecer na tela é este: o score de dois tokens
separados por uma distância de dois vale zero vírgula seis sete seis oito seis nove quando eles
estão nas posições 3 e 1, e vale exatamente o mesmo quando estão nas posições 5000 e 4998.

> Ideia central: "Não interessa onde cada ponteiro está no mostrador. Interessa o ângulo entre eles — e o ângulo só depende da distância."

## Slide 6 · Por que RoPE venceu, e o que ele não resolve · 00:35–00:43

Deixa eu enfileirar as quatro razões, porque juntas elas explicam por que uma ideia de 2021
virou padrão de fato.

Primeira: entrega posição **relativa**, e entrega dentro do score, que é justamente o lugar
onde a comparação entre dois tokens acontece. Não é um sinal que precisa atravessar a rede
para ser útil; ele é usado onde nasce.

Segunda: custa **zero parâmetro** treinável. É rotação determinística, calculada na hora. Não
tem tabela para aprender e não tem tabela para estourar — o sintoma do slide anterior
simplesmente não existe.

Terceira, e essa é subestimada: a rotação é aplicada em **cada camada**. Nas duas abordagens
anteriores a posição é injetada uma vez, na entrada, e tem que sobreviver a trinta blocos de
mistura. Aqui ela é reinjetada em todo bloco.

Quarta: dá uma alavanca de engenharia para esticar a janela de contexto reescalando as
frequências, coisa que uma tabela aprendida não permite de jeito nenhum.

E agora eu preciso ser honesto sobre a quarta, porque é a parte que a internet exagera.
Reescalar as frequências **estica** a janela. Não faz o modelo *usar* bem o que entrou nela.
Janela grande e memória confiável são duas coisas diferentes, e a diferença tem nome, tem
experimento e tem aula: é a Aula 10. Hoje a afirmação para de pé em "dá a alavanca". Não em
"resolve contexto longo".

> Ideia central: "Posição relativa, zero parâmetro, reinjetada em toda camada. É difícil competir com isso — e ainda assim não é a mesma coisa que usar bem o contexto."

## Slide 7 · [Demo] Medir a posição · 00:43–00:55

Chega de afirmação. Doze minutos medindo as três estratégias lado a lado.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> Ideia central: "Quinze linhas de NumPy. Uma das três estratégias devolve o mesmo número dentro e fora do comprimento de treino — e é essa que os modelos modernos usam."

## Slide 8 · O sintoma da profundidade: a pilha que diverge · 01:05–01:12

Voltando. O Bloco 1 foi sobre posição; o Bloco 2 é sobre as peças que fazem esse bloco
**treinar**. E eu vou continuar pelo mesmo caminho: sintoma primeiro.

Sintoma: a mesma receita — mesmos dados, mesma taxa de aprendizado, mesmo otimizador — treina
com doze blocos e diverge com quarenta e oito. E, antes de divergir, tem um detalhe que
denuncia a causa: as primeiras camadas mal se movem. O sinal de erro chega lá como ruído.

Isso é exatamente o problema da Aula 5, num eixo diferente. Lá o gradiente atravessava um
produto de fatores ao longo do **tempo**; aqui ele atravessa um produto de fatores ao longo da
**profundidade**. Com quarenta blocos e um fator típico de zero vírgula oito por bloco, o
produto é zero vírgula oito elevado a quarenta, que é da ordem de dez elevado a menos quatro. O
sinal que chega na primeira camada é quatro ordens de grandeza menor que o da última.

A correção é uma linha, e está no slide: `y = x + f(x)`. Somar a entrada de volta.

O que isso muda: a derivada da saída em relação à entrada passa a ter **dois termos** — um que
atravessa o ramo `f`, e um termo **identidade**, que não multiplica nada e não encolhe nada. O
gradiente tem duas rotas de volta, e uma delas é direta. Lá na Aula 5 a solução foi um gate
multiplicativo; aqui é uma soma.

E tem um efeito colateral que quase ninguém menciona e que eu acho o ponto mais bonito: com
residual, um bloco que aprende `f = 0` é um bloco **inofensivo**. Ele deixa passar. E a
possibilidade de um bloco ser inofensivo é o que permite empilhar quarenta sem medo — cada
bloco novo é uma saída opcional, não um pedágio.

> Ideia central: "O gradiente ganha dois caminhos de volta, e um deles é a identidade. Esse não se dilui em quarenta camadas."

## Slide 9 · Qual norma: LayerNorm × RMSNorm · 01:12–01:19

Segunda peça, e ela entra também por um sintoma, só que um sintoma que o slide anterior criou.

Olha o que a conexão residual faz com a escala: a cada bloco, a ativação recebe uma soma. E
somas acumulam — a magnitude do vetor cresce ao longo da pilha. Se ninguém controla isso, o
treino fica instável, e as camadas de cima passam a operar numa faixa numérica completamente
diferente das de baixo.

A resposta é normalizar. A LayerNorm normaliza **por amostra**, sobre as dimensões do próprio
vetor: subtrai a média das dimensões, divide pelo desvio, e depois reescala e desloca com dois
parâmetros aprendidos. Está no slide.

Deixa eu cravar uma distinção que a prova cobra: isso **não é BatchNorm**. A estatística vem
das dimensões de **um** vetor, não de exemplos diferentes do lote. Nenhuma amostra olha para
outra — e é por isso que a norma é indiferente ao tamanho do batch e funciona igual quando eu
gero um token só, em inferência, com lote de tamanho um. Sem essa propriedade, geração
autorregressiva não funcionaria.

E aí veio o RMSNorm, que é a LayerNorm com duas coisas removidas: a subtração da média e o
viés. Sobra a divisão pela raiz do valor quadrático médio. O que se economiza dá para contar:
metade dos parâmetros da norma, e uma redução a menos sobre o vetor. O que se perde: a
invariância a deslocamento — a LayerNorm devolve o mesmo resultado se eu somar uma constante a
todas as componentes, o RMSNorm não. E na prática a qualidade é equivalente, que é para onde
os LLMs abertos convergiram.

A leitura que eu faço: se o que atrapalhava o treino era a *magnitude* do vetor, e não onde
estava o centro dele, então centrar era trabalho que ninguém tinha cobrado.

> Ideia central: "LayerNorm centra e escala. RMSNorm só escala — e descobriu-se que centrar não estava pagando a própria conta."

## Slide 10 · Onde a norma entra muda o treino · 01:19–01:27

Terceira peça, e essa é a que mais gente lê como detalhe de gosto sem ser.

Sintoma: um time troca duas linhas de lugar e a instabilidade some. Mesmos dados, mesma taxa de
aprendizado, mesmo tamanho de modelo. Só a ordem de duas operações mudou.

As duas ordens estão no slide. No original de 2017: soma primeiro, normaliza depois — é o
pós-norm. No moderno: normaliza a entrada do ramo, e a soma residual fica por fora — é o
pré-norm.

A diferença prática está no caminho residual. No pós-norm, a soma passa pela norma — então
aquela autoestrada do slide anterior é reescalada a cada camada, e o gradiente que volta não
chega tão limpo quanto o termo identidade prometia. Consequência conhecida: pilha profunda em
pós-norm exige aquecimento cuidadoso do learning rate para não divergir nos primeiros passos.
No pré-norm, a norma entra dentro do ramo e o caminho residual fica limpo da entrada da pilha
até a saída. Treina com muito menos truque.

O preço existe e é justo mencionar: em modelos rasos o pós-norm costuma dar um resultado
ligeiramente melhor. Só que ninguém treina modelo raso hoje, e foi por isso que a escolha se
inverteu quando a profundidade cresceu.

E tem um detalhe que falta em quase todo diagrama que vocês vão encontrar por aí, e que vale
anotar porque é `TODO` do Lab 2: com pré-norm é **obrigatório** colocar uma norma final depois
do último bloco, antes da cabeça de saída. A razão é direta — a última soma residual não passou
por norma nenhuma, e ela carrega a escala acumulada de quarenta blocos. Esquecida, essa norma
faz o treino divergir sem mensagem de erro.

> Ideia central: "Mesmas peças, ordem diferente: uma pilha precisa de aquecimento na unha para não explodir, a outra simplesmente treina."

## Slide 11 · Onde estão dois terços dos pesos · 01:27–01:34

Quarta peça. Depois da atenção, cada posição passa por uma rede de duas camadas — e a palavra
que importa é **cada**: o feed-forward é aplicado posição por posição, independentemente, sem
olhar para nenhum vizinho. A divisão de trabalho do bloco é essa e vale decorar: a atenção
**mistura** posições, o feed-forward **transforma** cada uma isolada.

A versão de 2017 expande de `d` para quatro vezes `d`, aplica a não linearidade e volta. A
moderna é o SwiGLU, que acrescenta um ramo de **gating**: um ramo decide *o quê*, o outro
decide *quanto passa*, multiplicando elemento a elemento. São três matrizes em vez de duas.

E agora a conta, que é a parte que fixa o slide. Na atenção existem quatro matrizes `d` por
`d`: Q, K, V e a projeção de saída. Isso é quatro `d²`. No feed-forward de 2017, uma `d` por
`4d` e uma `4d` por `d`: oito `d²`. Ou seja: dois terços dos parâmetros do bloco estão no
feed-forward, a parte que não olha para nenhum vizinho. Com `d` igual a 1024, são 4,2 milhões
na atenção contra 8,4 milhões no feed-forward, uns 12,6 milhões por bloco.

Dois diagnósticos saem daí, e os dois valem mais que a conta. Primeiro: a contagem é
**quadrática** em `d`. Quem dobra o modelo de 1024 para 2048 esperando dobrar os parâmetros vai
encontrar o quádruplo. Segundo: aquele `8/3` estranho que vocês vão ver nas configurações de
modelo é o número que faz três matrizes custarem o mesmo que duas — é o preço da terceira
matriz do gating, pago sem inflar a contagem.

> Ideia central: "Dois terços dos pesos do bloco estão justamente na parte que não olha para nenhum vizinho."

## Slide 12 · O bloco moderno, consolidado · 01:34–01:39

Agora eu junto tudo, e este slide é a folha de referência que eu quero que vocês levem para o
Lab 2 e para a prova. Cinco trocas entre 2017 e hoje — e reparem que cada linha da tabela tem
uma coluna dizendo **qual sintoma motivou a troca**, que é o jeito de decorar sem decorar.

Posição: era senoidal somada na entrada, uma vez; hoje é rotação de Q e K dentro de cada
camada — e o sintoma foi o lixo além do comprimento de treino. Onde a norma entra: era
pós-norm; hoje é pré-norm mais a norma final — e o sintoma foi a divergência ao empilhar. Qual
norma: era LayerNorm; hoje é RMSNorm — e aqui o motivo foi custo, sem perda medida.
Feed-forward: era GELU com quatro `d`; hoje é SwiGLU com oito terços de `d`. E como a pilha é
montada: era encoder-decoder; hoje, para geração, é decoder-only — e essa última linha é a
única que muda o que o modelo **faz**, o que é justamente a aula da semana que vem.

O bloco inteiro cabe em duas linhas de pseudocódigo, que estão no slide. Duas normas, duas
somas, por bloco. É isso. Quarenta desses, uma norma final, uma projeção para o vocabulário, e
vocês têm um LLM.

Agora a parte que eu acho a mais impressionante da aula. Olha o que **não** mudou em oito anos:
`softmax(QKᵀ/√d_k)V`, multi-head, conexão residual e feed-forward por posição. Estão lá,
iguais. As cinco trocas foram todas de estabilidade e de custo — nenhuma foi no mecanismo.
Trocaram suspensão, câmbio e injeção; o motor é o de 2017.

> Ideia central: "Cinco trocas em oito anos e nenhuma delas foi no mecanismo. Trocaram a suspensão, não o motor."

## Slide 13 · [Exercício] Achar a peça errada · 01:39–01:50

Oito minutos, em dupla. Três sintomas, e para cada um eu quero a peça e a evidência.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> Ideia central: "Nenhuma das três se resolve derivando. As três se resolvem sabendo o que cada peça do bloco compra."

## Slide 14 · Fechamento: o bloco está pronto; falta decidir como conectá-lo · 01:50–02:00

Deixa eu fechar o arco de duas aulas.

Na Aula 6 a gente construiu o **mecanismo**: a fórmula da atenção, as cabeças, a máscara. Hoje
a gente construiu o **bloco**: posição por rotação de Q e K, duas somas residuais, duas normas,
um feed-forward com gating. Está pronto e está completo — o que vocês têm no caderno agora é a
peça de Lego de que todo LLM moderno é feito.

E cada peça entrou aqui por um sintoma. Isso não foi estilo de aula: é assim que essas peças
entraram na literatura. Ninguém acordou querendo inventar o pré-norm; alguém tentou empilhar e
divergiu.

É exatamente aqui que aparece a última pergunta em aberto. Se o bloco é o mesmo, o que faz um
modelo ser bom em classificar e outro ser bom em escrever? A resposta não está no bloco. Está
em **como a pilha de blocos é conectada** e no que cada arquitetura deixa cada token enxergar:
só o passado, o texto inteiro, ou dois textos em sequência. Três formas de montar as mesmas
peças, três coisas diferentes que o modelo sabe fazer.

E tem um segundo fio para a semana que vem. A gente estabeleceu na Aula 6 que a atenção custa
`O(n²)`. Enquanto a janela era de 512 tokens, isso era nota de rodapé; com janelas grandes,
virou o problema central de engenharia. Aula 8: famílias de modelos e atenção eficiente.

Para a semana, duas coisas. A leitura é o RoFormer, de Su e coautores, arXiv 2104.09864, as
seções de formulação e de propriedades. A pergunta dirigida está no slide: em que ponto exato
do cálculo do score a posição entra, e por que isso entrega posição relativa sem nenhum
parâmetro novo? E o exercício de três linhas: um vetor de duas dimensões, girado por dois
ângulos, conferindo à mão que o produto escalar só depende da diferença. A conta está feita em
A.2, com os números da demo — mas fazer com a própria mão é diferente de ler.

> Ideia central: "O bloco está pronto. O que decide se o modelo classifica ou escreve não é o bloco — é como a gente empilha e o que cada token pode enxergar."

---

## Parte 2 — Demonstração guiada

Doze minutos, quatro medições. Na V1 esta aula rodava o script da Aula 6 duas vezes para
mostrar a invariância; na V2 essa parte encolheu para trinta segundos de retomada, e o tempo
foi para medir **as três estratégias de posição lado a lado** — que é o que o Bloco 1 discute.

As quinze linhas abaixo podem ser coladas num arquivo ou digitadas no REPL; dependem só de
NumPy. **Esta aula não tem pasta `codigo/` própria**: a Medição 1 reaproveita
`../aula-06/codigo/demo-attention.py`.

Preparação na véspera: rodar tudo uma vez na máquina da sala, aumentar a fonte do terminal, e
capturar as saídas em texto como reserva.

## Medição 1 — sem posição (30 s)

**1.** **[Rodo o script da Aula 6 com `--shuffle`]** Trinta segundos só para recolocar o
sintoma na tela: mesmo script da aula passada, tokens embaralhados, e a saída de cada token
idêntica a menos de permutação. É o slide 1.

## Medição 2 — senoidal: o produto interno só depende da distância (4 min)

**2.** **[Digito e rodo]** Agora a primeira estratégia, medida:

```python
import numpy as np
d, k = 64, 3
i = np.arange(0, d, 2)
w = 10000.0 ** (-i / d)
def PE(pos):
    v = np.empty(d); v[0::2] = np.sin(w * pos); v[1::2] = np.cos(w * pos); return v
for pos in (0, 5, 100, 1000):
    print(f"pos={pos:5d}   PE(pos) . PE(pos+{k}) = {PE(pos) @ PE(pos + k):.9f}")
```

**3.** **[Leio a coluna da direita]** Quatro posições completamente diferentes — zero, cinco,
cem, mil — e o mesmo número nas quatro: 25,587028547. Até a nona casa decimal. O produto
interno entre duas codificações **não sabe onde elas estão**; ele só sabe que estão a três
posições de distância. É a propriedade que eu afirmei no slide 3, medida.

**4.** **[Rodo a mesma conta variando `k`]** E variando a distância, com `pos` fixo: 32 para
distância zero, 30,9 para um, 25,6 para três, 21,1 para dez, 15,7 para cinquenta, 11,4 para
duzentos. É uma curva de similaridade que decai com a distância — e o 32 do começo é `d` sobre
2, que é a norma ao quadrado de qualquer codificação. Todas as posições têm o mesmo tamanho;
nenhuma é "maior" que outra.

## Medição 3 — aprendida: o teto que é um erro de índice (1 min)

**5.** **[Rodo três linhas]** A segunda estratégia, e ela cabe em três linhas:

```python
E = np.random.default_rng(0).normal(size=(4096, 64))   # tabela treinada: uma linha por posição
print("posição 4095:", E[4095].shape)
print("posição 4096:", E[4096].shape)                  # IndexError
```

**6.** **[Mostro a exceção na tela]** `IndexError: index 4096 is out of bounds`. É o sintoma do
slide 4, sem metáfora nenhuma. A posição não é mal representada: ela não existe.

## Medição 4 — RoPE: o mesmo score dentro e fora do treino (6 min)

**7.** **[Digito e rodo]** E a terceira, que é a que decide a aula:

```python
def rot(v, ang):
    c, s = np.cos(ang), np.sin(ang)
    return np.array([c*v[0] - s*v[1], s*v[0] + c*v[1]])

q, kv, theta = np.array([1.0, 0.0]), np.array([0.6, 0.8]), 0.05
print(f"sem RoPE, qualquer posição:  {q @ kv:.6f}")
for m, n in [(3, 1), (10, 8), (500, 498), (5000, 4998), (3, 2), (100, 99)]:
    print(f"m={m:5d} n={n:5d}  m-n={m-n:2d}  score={rot(q, m*theta) @ rot(kv, n*theta):.6f}")
```

**8.** **[Leio as quatro primeiras linhas]** Olha os quatro primeiros pares. Distância dois em
todos, e o score é 0,676869 nos quatro. Nas posições 3 e 1, e nas posições 5000 e 4998. O
modelo foi treinado com quatro mil de contexto e a conta na posição cinco mil devolve
exatamente o mesmo número — porque não tem tabela, tem rotação, e a rotação existe para
qualquer ângulo.

**9.** **[Aponto as duas últimas linhas]** E as duas últimas, com distância um: 0,639233 nas
duas. Distância diferente, número diferente; mesma distância, mesmo número. É literalmente a
definição de posição relativa, e ela apareceu dentro do score.

**10.** **[Comparo com a primeira linha]** E a primeira linha é o contrafactual: sem rotação, o
score é 0,6 em todos os casos. A informação de distância simplesmente não estava lá.

---

## Parte 3 — Hands-on

Oito minutos de dupla, três de correção. O exercício da V1 era montar as seis peças do bloco na
ordem certa; ele virou extensão opcional, e o obrigatório passou a ser diagnóstico — mas a
correção termina com o bloco desenhado na ordem certa no quadro, porque é esse diagrama que vai
para o Lab 2.

**1.** **[Projeto os três sintomas e formo as duplas]** Oito minutos, em dupla. Três situações,
e para cada uma eu quero duas coisas: qual peça do bloco está no lugar errado ou ausente, e
**que evidência confirmaria**. A segunda parte é a que vale.

Os três sintomas:

1. Uma pilha de 48 blocos diverge nos primeiros 200 passos de treino. A mesma receita, com 12
   blocos, treina até o fim. Não há `NaN` antes da divergência, e as primeiras camadas mal se
   movem.
2. Um modelo responde bem em prompts curtos e produz texto incoerente assim que o prompt passa
   de um certo comprimento — sempre o mesmo comprimento, em qualquer assunto.
3. Um time aplicou a rotação posicional em Q, K **e** V. O modelo treina, e a representação de
   uma mesma frase muda conforme ela aparece no começo ou no fim do prompt.

*Como recolher:* três minutos. Peço uma dupla para o sintoma 1 e forço a segunda parte — "como
você confirmaria?". Corrijo o 3 com o desenho: vou ao quadro e monto o bloco pré-norm inteiro,
com as duas normas, as duas somas, a bifurcação dupla do `x`, o RoPE marcado só sobre Q e K, e
a norma final depois do último bloco. Esse desenho é o artefato da aula e é literalmente o
Checkpoint 3 do Lab 2. Se ninguém marcar as duas somas, desenho **errado** de propósito na
primeira tentativa — o conserto ao vivo fixa melhor que o desenho pronto.

*Extensão para quem terminar antes (opcional):* com `d_model = 1024`, calcular quantos
parâmetros ficam na atenção e quantos no feed-forward, e depois refazer com `d_model = 2048`
para ver o fator quatro. É a conta que na V1 eu fazia no quadro e aqui vira aprofundamento;
está em A.6, com os FLOPs por token.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a derivação
em aula. A regra geral é remeter ao apêndice e seguir; conduzir uma derivação só se sobrar
tempo, e anunciando que é conteúdo de consulta.

**Item 1 — "Prova que o produto escalar só depende de `m − n`?" (A.2, ~5 min).**
A pergunta mais provável da aula, e a mais legítima — na V1 ela era a aula. Eu escrevo o
produto interno como produto matricial, uso que a transposta de uma rotação é a rotação
inversa, e junto os dois ângulos numa rotação só: sobra `R((n−m)θ)`. Três linhas. Se quiserem
número em vez de álgebra, faço com dois ângulos concretos, 30° e 50°, e mostro o produto
escalar dando o cosseno de 20°. **Nunca** introduzir número complexo — o paper usa, o quadro
não precisa, e a notação complexa perde metade da turma em trinta segundos.

**Item 2 — "Por que seno e cosseno, e não qualquer função?" (A.1, ~6 min).**
Se perguntarem a construção senoidal. Eu escrevo o par seno/cosseno de uma frequência, aplico
as identidades de soma de arcos e mostro que deslocar por `k` é multiplicar por uma matriz que
depende só de `k`. Depois faço o produto interno de duas codificações e mostro que os termos
colapsam numa soma de cossenos da diferença. É bonito e custa caro; só faço se o Bloco 1
estiver adiantado, porque o RoPE usa a mesma ideia de forma mais limpa. Se não houver tempo, a
Medição 2 já mostra o resultado medido.

**Item 3 — "Como o `I` salva o gradiente?" (A.3, ~4 min).**
Vale fazer se a turma tiver Álgebra Linear fresca. Eu escrevo a derivada de um bloco, depois o
produto sobre `N` blocos, e **expando** o produto: aparece um termo identidade puro, que
atravessa a pilha sem multiplicar nada. O ponto que convence é o contrafactual: sem residual é
um produto, e `0.8^40` é `10⁻⁴`. Se a turma não tiver a base, não fazer — "duas rotas de volta,
uma delas direta" entrega o mesmo em quinze segundos.

**Item 4 — "De onde vem esse 8/3?" (A.6, ~3 min).**
Barato e satisfatório. Duas matrizes de largura `4d` dão `8d²`; três matrizes de largura `d_ff`
dão `3·d·d_ff`; igualando, `d_ff = 8/3·d`. Uma linha e meia no quadro. Se eu tiver que escolher
um item desta parte para fazer, é este — é o de melhor razão entre convencimento e minuto.

**Item 5 — "Por que a norma final é obrigatória?" (A.5, ~4 min).**
Se alguém perguntar no slide 10, e vale a pena porque é `TODO` do Lab 2. Eu escrevo as duas
ordens, mostro que no pré-norm a última operação é uma soma que ninguém normalizou, e ligo com
a variância que cresce ao longo da pilha. O argumento que mais convence é o caso-limite: com
`f = 0`, o bloco pré-norm devolve `x` intacto e o pós-norm devolve `LN(x)` — ou seja, no
pós-norm nem um bloco que não faz nada é inofensivo. A.5 tem os dois desenvolvimentos.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 14 da Parte 1 — a síntese do arco de duas aulas
(mecanismo na Aula 6, bloco na Aula 7), o fato de cada peça ter entrado por um sintoma, a
pergunta em aberto sobre como a pilha é conectada, o fio do custo `O(n²)`, a ponte para a Aula
8 e a leitura de Su et al. com a pergunta dirigida.

> Ideia central: "Hoje a gente terminou a peça de Lego. Semana que vem a gente descobre que existem três jeitos de montar as mesmas peças — e que eles produzem modelos que fazem coisas diferentes."

---

*Roteiro do Instrutor · Aula 7 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
