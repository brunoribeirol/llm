---
aula: 15
titulo: "Alinhamento: RLHF, PPO e DPO"
tipo: teorica
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 15 de 30 (V2)

## Como usar este roteiro

A prosa deste documento é **fala em primeira pessoa**: é o que eu digo em sala, na ordem em que
digo. Não é resumo do conteúdo — é o texto falado.

As linhas marcadas com 🗣️ são as **frases-âncora**: as que eu cravo, quase palavra por palavra.
As notas marcadas com **Bastidor** são operacionais e **não são faladas em voz alta**.

> **O que muda nesta versão.** A aula é conduzida por três defeitos observáveis de um modelo
> alinhado: ele acerta a forma e erra o pedido, ele bajula, e ele piora no que já sabia. Cada
> fundamento entra amarrado ao defeito que explica, **enunciado e lido**, com a derivação no
> apêndice do deck (A.1 a A.6). Eu **não** derivo no quadro. Se a turma pedir, a **Parte 4**
> tem a condução pronta, com o custo em minutos de cada uma e o que sacrificar em troca.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · O sintoma: educado, no formato, e errado · 00:00–00:10

Boa noite, pessoal. Semana passada, no Lab 4, vocês penduraram um adaptador LoRA num modelo
aberto e treinaram ele num conjunto de instruções em português. E funcionou: o antes e o depois
que vocês colaram no notebook mostra um modelo que passou a responder no formato que vocês
pediram, com o tom que vocês pediram.

Hoje eu vou começar por três coisas que aquele treino **não** conserta. E as três vocês já
viram, se já usaram um assistente comercial.

A primeira: o modelo responde no template certo, com estrutura impecável, tom perfeito — e
responde outra coisa. Não o que foi pedido. A forma está lá inteira e o pedido não foi atendido.

A segunda: o usuário afirma uma premissa que está errada, e o modelo concorda. E não só
concorda: elabora em cima dela, com confiança, e produz três parágrafos apoiados numa coisa
falsa.

E a terceira, que é a mais desconcertante: depois de uma rodada de alinhamento, o modelo **perde**
uma capacidade que ele tinha. Convertia unidade e passou a errar. Formatava data e passou a
errar. Uma coisa que funcionava na semana passada parou de funcionar, e ninguém apagou peso
nenhum.

Nenhum dos três é falta de dados de imitação. Vocês podem dobrar o conjunto do Lab 4, triplicar,
e os três continuam ali. O SFT ensinou a forma. Nenhum dos três é problema de forma.

> 🗣️ "O SFT ensinou a forma. Os três defeitos que eu acabei de mostrar são falta de julgamento."

> **Nota:** Bastidor: perguntar quem já viu o segundo cartão — o bajulador — num assistente
> comercial. O reconhecimento coletivo compra a aula inteira. **Não** nomear RLHF, reward hacking
> nem KL aqui: cada nome chega no slide que explica o cartão correspondente — 5, 11 e 10. Se
> alguém já soltar "isso é RLHF, né?", confirmar em uma frase e seguir.

### Slide 2 · Por que mais dados de imitação não resolvem · 00:10–00:16

Deixa eu tornar isso preciso, porque "SFT não basta" soando como slogan não ajuda ninguém.

O SFT otimiza entropia cruzada sobre demonstrações boas. Ele empurra para cima a verossimilhança
dos tokens que aparecem no exemplo de ouro, e é isso. O gradiente só sabe dizer uma coisa:
aumente a probabilidade deste token aqui. Ele nunca, em passo nenhum, diz "e diminua a
probabilidade daquela outra continuação".

Duas consequências saem daí, e as duas são práticas. A primeira: as respostas ruins que importam
não são as ruins óbvias. São as continuações plausíveis — bem escritas, com estrutura, com
confiança, e erradas. Elas vivem numa região que o SFT nunca visita e nunca penaliza, porque
penalizar não está no vocabulário dele.

A segunda é mais funda. Para a maioria dos prompts interessantes, não existe *a* resposta
correta. Existe uma ordenação. "Redija um e-mail de demissão empático" não tem gabarito: tem
resposta melhor e resposta pior. E ordenação não é rótulo — eu não consigo escrever num dataset
supervisionado a informação "esta é a terceira melhor".

E tem o argumento de custo, que eu acho o mais convincente. Para escrever a demonstração de ouro
daquele e-mail, eu preciso de um anotador que escreva tão bem quanto o modelo que eu quero
obter no fim. Isso é caro e é raro. Para olhar dois e-mails que o modelo gerou e apontar o
melhor, eu preciso de um anotador razoável — e ele acerta.

> 🗣️ "Mais dados de imitação ampliam a cobertura das respostas boas. O gradiente continua cego a tudo que está fora dela."

> **Nota:** Bastidor: o erro conceitual a matar é "então alinhamento é SFT com mais dados". O que
> muda é o objetivo, não o volume. Se a turma comprar rápido, eu ganho 2 min para o slide 5.

### Slide 3 · O que o alinhamento acrescenta · 00:16–00:21

Deixa eu organizar os três estágios de treinamento numa frase cada, porque isso vira mapa para a
prova e para o projeto de vocês.

O pré-treino dá **capacidade**. Depois dele, o modelo *pode* produzir a resposta boa — a
sequência existe dentro da distribuição dele, com alguma probabilidade. O SFT dá **forma**:
o modelo responde em vez de continuar o texto, respeita o template, para no fim. E o alinhamento
dá **julgamento**: entre as respostas que ele pode produzir e sabe formatar, ele passa a preferir
as que humanos preferem.

Isso não é retórica, é mudança no escalar que está sendo otimizado. No pré-treino e no SFT o
objetivo é verossimilhança de texto humano. No alinhamento é preferência humana sobre saídas do
modelo. Muda o objeto de comparação: antes eu comparo o modelo com um corpus, agora eu comparo o
modelo com ele mesmo.

O InstructGPT organizou isso em três direções que ficaram famosas: útil, honesto e inofensivo. E
eu não apresento isso como harmonia, porque não é. As três brigam. Ser útil ao pedido literal do
usuário pode ser exatamente ser prejudicial. Quando duas direções brigam, alguém tem que ter
escrito qual delas ganha — e isso reaparece no próximo slide como diretriz de anotação.

> 🗣️ "O RLHF não ensina conhecimento novo. Ele redistribui massa de probabilidade sobre o que o modelo já sabe produzir."

> **Nota:** Bastidor: este é o slide sacrificável se o Bloco 1 estourar — a informação volta no
> slide 16. Se vier "então dá para alinhar um modelo para ele saber uma coisa que não sabe?", a
> resposta é direta: não. Se a capacidade não está no modelo-base, o alinhamento não a cria —
> isso é recuperação, e é o Módulo 5.

### Slide 4 · O dado que muda o objetivo · 00:21–00:28

O dado de alinhamento é uma tripla: prompt, resposta preferida, resposta rejeitada. `x`, `y_w` de
*winner*, `y_l` de *loser*. É isso — é o dataset inteiro.

E de onde vêm essas duas respostas? Do próprio modelo SFT, amostradas com temperatura acima de
zero. Isso é fácil de passar batido e é importante: as respostas comparadas são amostras da
política que a gente quer melhorar, não textos escritos por humanos. Na prática se tira `K`
amostras por prompt — quatro, oito — e daí saem todos os `K(K−1)/2` pares. Com `K` igual a
quatro, seis pares por prompt.

Por que comparar dois em vez de dar uma nota de zero a dez? Porque nota absoluta não é estável.
O sete de um anotador não é o sete de outro, e nem é o sete dele próprio na semana seguinte,
depois do almoço, no fim do turno. A comparação exige um julgamento local — este ou aquele — e é
esse tipo de julgamento que humanos fazem com consistência razoável.

Agora o artefato mais subestimado do pipeline inteiro: a diretriz de anotação. Ela precisa fixar
a **precedência** dos critérios — segurança antes de factualidade, factualidade antes de
utilidade, utilidade antes de estilo — e precisa dizer o que fazer quando as duas respostas são
ruins, e o que conta como empate. Sem precedência escrita, dois anotadores estão otimizando
funções diferentes, e o modelo de recompensa aprende a média de duas coisas incompatíveis.

E mesmo com diretriz boa, o número que o InstructGPT reporta em tarefas abertas é concordância
entre anotadores na casa dos setenta por cento. Isso não é detalhe: é um **teto**. Guardem esse
número, porque ele volta três vezes hoje — na demo como platô medido, no slide 11 como a origem
da sobre-otimização, e no fechamento como a razão de a próxima aula existir.

> 🗣️ "O anotador não escreve a resposta. Ele ordena — e a diretriz é o que define qual ordenação ele está produzindo."

> **Nota:** Bastidor: se alguém perguntar por que não usar modelo para anotar, responder que é
> exatamente o que a indústria passou a fazer (RLAIF) e que a Aula 27 trata de LLM-as-judge
> calibrado. Não abrir o fio agora.

### Slide 5 · O fundamento nomeado: Bradley-Terry · 00:28–00:36

Eu tenho comparações e preciso de um número. Bradley-Terry é o modelo estatístico que faz essa
ponte, e ele tem quase cem anos — é anterior a qualquer coisa de aprendizagem profunda.

*[Projeto as duas fórmulas e leio em voz alta, apontando cada termo.]*

A probabilidade de a resposta preferida vencer a rejeitada é sigma da **diferença** entre as
forças das duas. E a perda de treino é menos o log de sigma dessa mesma diferença, em média
sobre os pares anotados. Uma linha cada.

Duas leituras, e as duas rendem. A primeira: só a diferença entra. A probabilidade não depende do
valor de nenhuma das duas forças isoladamente. A segunda: minimizar essa perda é abrir a
diferença entre preferido e rejeitado — e como a sigmoide satura, par já bem separado para de
contribuir gradiente. O treino gasta capacidade nos pares difíceis, sozinho.

E agora a consequência que quase todo mundo erra, e que decide engenharia. Se eu somar cem a
todos os scores de um prompt, nenhuma previsão muda. Isso é o Elo do xadrez: somar quatrocentos
ao rating de todos os jogadores não altera a previsão de nenhuma partida. Quer dizer que `r` é
identificável apenas a menos de uma constante aditiva por prompt — e portanto valores de
recompensa de prompts diferentes **não são comparáveis entre si**. Dizer "esta resposta tirou
3,7" não significa nada fora do prompt dela.

> 🗣️ "É o Elo do xadrez. Somar quatrocentos a todo mundo não muda a previsão de nenhuma partida — não existe escala, existe ordem."

> **Nota:** Bastidor: **não derivar.** Ler e seguir. A verossimilhança, a passagem para a
> sigmoide, o gradiente com o peso `1 − σ(Δ)` e a prova de identificabilidade estão em A.1, mais
> completos do que eu fazia no quadro na V1. Na V1 este slide eram 9 min de quadro; agora são 8
> min de leitura e consequência. Se pedirem a conta: Parte 4, item 1.

### Slide 6 · O reward model é um proxy congelado · 00:36–00:43

A fórmula existe. Que objeto é esse `r_φ` na engenharia real?

É o próprio modelo SFT com a cabeça de linguagem arrancada e uma cabeça escalar no lugar — uma
projeção linear que lê o estado oculto do último token e devolve um número. Só isso. Treina-se
tipicamente **uma** época, porque ele decora pares depressa e passa a errar em held-out. E não
precisa ter o tamanho da política: um RM bem menor que o modelo que ele vai supervisionar é
prática comum.

A métrica de sanidade é acurácia em pares held-out: dado um par que ele nunca viu, ele dá score
maior para o preferido? Se isso está em cinquenta e poucos por cento, o RM é uma moeda e não tem
conversa a ter.

E olha onde essa métrica encosta. Com vinte e cinco por cento dos rótulos discordantes, a
acurácia medida **satura em torno de zero vírgula setenta e cinco** e não passa disso, por mais
que eu treine. Daqui a pouco eu mostro isso acontecendo na tela. E o ponto que interessa é: esse
teto é do **rótulo**, não do modelo. É o número dos setenta por cento do slide anterior
aparecendo como platô numa curva.

E aqui vem a frase que eu quero cravar sobre este objeto. Daqui para frente, esse modelo
congelado *é* a definição operacional de "o que humanos querem" dentro do pipeline. Todo o viés
do conjunto de anotação, toda a preguiça de anotador, toda a preferência por resposta longa que
estava lá — está tudo dentro dele agora, e ele nunca mais vai receber correção.

Ainda neste slide, o contraste que é a confusão mais persistente da aula: modelo de recompensa
não é modelo de valor. O de **recompensa** prediz preferência humana e fica congelado. O de
**valor**, que aparece no slide 9, prediz retorno esperado a partir de um estado e é treinado
junto com a política. Dois modelos, nomes parecidos, papéis diferentes.

> 🗣️ "Um juiz que assistiu a algumas dezenas de milhares de comparações e nunca mais vai receber correção — enquanto a política passa milhões de episódios tentando agradá-lo."

> **Nota:** Bastidor: desenhar o contraste RM × value model no quadro, em duas colunas, e **não
> apagar** até o fim do Bloco 2. Toda pergunta trocando os dois nomes se resolve apontando para o
> quadro em vez de reexplicar. O porquê do teto `1 − ruído` está em A.1.

### Slide 7 · [Demo] O que o RM realmente aprende · 00:43–00:55

Chega de afirmação. Deixa eu medir.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> 🗣️ "O RM não aprende qualidade. Ele aprende separação — e o eixo dele não tem unidade nenhuma."

> **Nota:** Bastidor: passos na Parte 2. Roda em CPU, em segundos, sem rede e sem chave. A
> medição do teto sob ruído é a evidência do slide 6 e é a que **não** se corta. Se falhar na
> hora, projetar o PNG `separacao-bradley-terry.png` da véspera; a tabela-resumo sai em texto
> puro mesmo sem matplotlib. Intervalo de 10 min depois — anunciar o horário exato de volta.

### Slide 8 · O LLM como política, e o crédito que não chega · 01:05–01:10

Voltando. Eu tenho um número por resposta. Agora eu preciso transformar esse número em
atualização de peso, e o formalismo que a área usou para isso é aprendizagem por reforço. A
tradução é literal e é mais simples do que o vocabulário sugere.

O **estado** é o prompt mais os tokens já gerados. A **ação** é o próximo token — o espaço de
ações é o vocabulário inteiro, algumas dezenas de milhares de opções. A **política** é exatamente
o softmax que o modelo já produzia; não tem objeto novo aqui, o modelo de linguagem *já era* uma
política. O **episódio** começa no prompt e termina no EOS. E a **recompensa** vem uma vez só, no
fim, quando o RM lê a resposta completa — mais uma penalidade de KL aplicada token a token, que é
o slide 10.

O que faz isso difícil é essa recompensa terminal. Se a nota só aparece no apito final, o crédito
por uma decisão tomada no token 12 tem que ser inferido do resultado observado no token 400.
Isso tem nome — atribuição de crédito — e é a razão de RL aqui ser mais instável que ajuste
supervisionado, onde cada token tem seu próprio alvo.

E quem faz esse trabalho de distribuir um escalar único ao longo de centenas de tokens é a
**vantagem**: quanto aquela ação rendeu acima do que já se esperava daquele estado. E medir "o
que se esperava" exige uma linha de base — que é o modelo de valor, o quarto modelo que vai
aparecer no próximo slide.

> 🗣️ "O modelo de linguagem já era uma política. A gente não trocou o objeto — trocou o que a gente mede no fim do episódio."

> **Nota:** Bastidor: é aqui que a turma sem ML prévio trava. Se travar, definir "episódio" e
> "política" em duas frases e seguir; a leitura da vantagem basta para a aula, e a conta —
> incluindo a prova de que uma linha de base não enviesa o gradiente — está em A.2. Esse
> resultado de A.2 volta na Aula 16, então vale citar que ele existe. O erro a matar: imaginar
> que o RM dá uma nota por token.

### Slide 9 · PPO: por que o passo precisa ser cortado · 01:10–01:16

Deixa eu abrir por um sintoma de treino, porque ele é o que justifica a fórmula.

O treino de RL colapsa em texto degenerado. Repetição, formatação vazia, aquele texto que parece
confiante e não diz nada. E o pior: a recompensa média **sobe** enquanto isso acontece.

A causa é tamanho de passo. Eu coletei um lote de amostras com a política de alguns passos atrás,
e esse lote não autoriza um passo arbitrariamente grande — as amostras deixam de representar a
política assim que ela muda.

*[Projeto as duas linhas e leio.]*

A resposta do PPO é a razão entre a probabilidade que a política nova dá àquela ação e a que a
política antiga dava. E o objetivo é o mínimo entre a razão vezes a vantagem e a razão
**cortada** vezes a vantagem, com epsilon em torno de zero vírgula dois.

Em português: enquanto a razão fica perto de um, o gradiente age normalmente. Assim que ela passa
de um mais epsilon numa ação de vantagem positiva, o objetivo daquela amostra vira platô — não
adianta mais empurrar. É isso que impede que um token com vantagem alta tenha a probabilidade
empurrada em direção a um.

E agora a parte que faz vocês entenderem por que PPO tem reputação de doloroso. Deixa eu contar
os modelos que estão na memória ao mesmo tempo: a **política**, que treina; a **referência**,
congelada, para o KL; o de **recompensa**, congelado, que dá a nota; e o de **valor**, que treina,
e que dá a linha de base. Quatro cópias, dois loops de treino, um loop de amostragem, e um enxame
de hiperparâmetros.

> 🗣️ "O clipping não limita o quanto os pesos mudam. Limita o quanto a razão daquela ação contribui para o gradiente — é região de confiança em espaço de política, não de parâmetro."

> **Nota:** Bastidor: desenhar as quatro caixas no quadro, ao lado do contraste do slide 6, e
> deixar as duas coisas até o fim da aula. Essa contagem de quatro é o que dá sentido ao slide
> 13, que existe para apagar duas delas. A análise dos quatro casos de sinal, a origem da razão
> por amostragem de importância e os limites de epsilon estão em A.3. Se pedirem: Parte 4, item 2.

### Slide 10 · O sintoma que o KL contém: o modelo piorou no que já sabia · 01:16–01:22

Voltando ao terceiro cartão da abertura, que é o mais desconcertante: o modelo perdeu uma
capacidade que tinha.

Deixa eu dizer o que aconteceu ali, porque a intuição comum está errada. Nenhum peso foi apagado.
O que aconteceu é que a **massa de probabilidade se mudou de bairro**. A resposta certa continua
existindo no modelo; ela só deixou de ser provável.

E isso acontece porque a recompensa que o PPO otimiza não é a do RM sozinha.

*[Projeto a linha.]*

É a nota do RM **menos** beta vezes o KL entre a política e a referência congelada, que é o SFT.
E a razão desse termo é epistêmica, não estética: o RM só foi treinado em respostas parecidas com
as que o SFT produzia. Fora dessa vizinhança, a nota dele é extrapolação sem nenhuma garantia. Se
eu deixo a política andar livremente para longe, ela vai encontrar texto que o RM adora e que
nenhum humano aprovaria — e, de quebra, ela esquece de escrever bem, porque tudo o que ela sabia
sobre língua veio do lugar de onde ela está fugindo.

O beta é a coleira. Alto demais, a política fica presa e nada muda: no limite, a política ótima
**é** a referência. Baixo demais, ela sai correndo: no limite, ela colapsa na única resposta de
maior nota do RM, seja ela qual for. Os dois limites estão calculados em A.4, e os dois são
sintomas que vocês vão ver num painel.

E por isso a métrica que se acompanha num treino de RLHF não é a recompensa — é o par recompensa
e KL acumulado, olhados juntos.

> 🗣️ "Recompensa subindo com KL explodindo não é sucesso. É o sintoma, com nome e com gráfico."

> **Nota:** Bastidor: o erro a matar é tratar o KL como regularizador cosmético. Sem ele,
> "maximizar o RM" não é problema bem-posto. Avisar que a forma fechada de A.4 volta no slide 13
> — é literalmente a mesma expressão que o DPO inverte, e antecipar isso faz o slide 13 render.
> Se perguntarem como o KL é calculado, a resposta curta é "estimado por amostra, token a token";
> os dois estimadores usuais estão em A.4.

### Slide 11 · O bajulador: quando a métrica sobe e o produto piora · 01:22–01:29

Segundo cartão da abertura: o assistente que concorda com o usuário mesmo quando ele está errado.

Isso não é bug de implementação. É o resultado **previsto** de otimizar um proxy com força
suficiente. O RM é um proxy da preferência humana, e otimizar um proxy com força suficiente, em
algum ponto, piora o objetivo verdadeiro. As curvas de sobre-otimização mostram isso com clareza
brutal: conforme o KL cresce, a recompensa do proxy sobe monotonicamente, enquanto a preferência
humana medida sobe, satura e cai. É a lei de Goodhart com gráfico e eixo rotulado.

E reparem no eixo x: é o **mesmo KL** do slide anterior. A sobre-otimização se lê contra distância
percorrida, não contra passos de treino. Duas execuções com taxas de aprendizado diferentes que
chegam no mesmo KL sobre-otimizam de forma parecida. Isso quer dizer que escolher beta e escolher
onde parar são a **mesma** decisão.

O catálogo de sintomas, que é o que eu quero que vocês levem para casa. **Inflação de
comprimento**: respostas longas tendem a ser preferidas na anotação, então o modelo aprende a
encher linguiça com cabeçalhos, listas e recapitulação do que o usuário acabou de dizer.
**Bajulação**: concordar com a premissa do usuário mesmo quando ela é falsa, porque discordar
arranha a nota. **Recusa excessiva**: recusar é seguro, e o anotador raramente pune uma recusa
educada. E **enfeite de formatação** sem uma vírgula de conteúdo novo. Se vocês já sentiram que
um assistente fala muito para dizer pouco, vocês estão olhando para o resultado disso.

As mitigações são todas parciais, e é honesto dizer isso. Orçamento de KL explícito. Avaliação com
humanos, fora do RM, como juiz de última instância. Recompensa normalizada por comprimento.
Conjunto de RMs em ensemble, para que hackear um não baste. E o caminho que a indústria de fato
seguiu: RLHF iterado — coletar comparações novas sobre amostras da política atual e retreinar o
RM, várias vezes, para que o proxy acompanhe o lugar onde a política foi morar.

> 🗣️ "O modelo de recompensa não está errado. Ele está fazendo exatamente o que eu treinei ele para fazer — e eu confiei nele fora da região onde eu o validei."

> **Nota:** Bastidor: perguntar quem já viu bajulação num assistente comercial; o reconhecimento
> coletivo fixa melhor do que eu explicando. Esta lista é reusada na Aula 26 e é material provável
> de questão de diagnóstico na prova da Aula 17. O argumento de por que o KL é a abscissa certa
> está em A.4, na seção final.

### Slide 12 · Best-of-N: alinhamento sem tocar em peso nenhum · 01:29–01:34

Antes de eu mostrar a alternativa de treino, tem uma alternativa que não treina nada, e ela é
forte o suficiente para ser a primeira coisa que eu tentaria.

Best-of-N: amostra-se `N` respostas da política, o RM pontua todas, devolve-se a de maior score.
Zero peso alterado. O custo é aritmético e é imediato: `N` vezes mais tokens de saída e, se as
amostras não forem geradas em paralelo, `N` vezes mais latência. Com `N` igual a oito e uma
resposta de quinhentos tokens, são quatro mil tokens gerados para entregar quinhentos.

E aqui está o detalhe que quase ninguém conta: Best-of-N **também** é um otimizador contra o
proxy. O desvio de KL que ele induz cresce com o **logaritmo** de `N` — e isso põe o `N` da
inferência e o orçamento de KL do treino na mesma moeda. Escolher `N` igual a oito custa mais ou
menos o mesmo desvio de distribuição que treinar até um KL de um vírgula dois nat. Se a curva de
sobre-otimização já virou antes disso, `N` igual a oito está do lado errado do pico.

É o slide anterior acontecendo na hora da inferência. A diferença é que eu pago esse hack a cada
requisição, para sempre, em vez de uma vez no treino.

Quando não usar: caminho interativo sensível a latência; volume alto, onde o custo por chamada
domina a conta; ausência de um pontuador confiável — sem um RM decente, Best-of-N é sorteio caro;
e o caso em que as `N` amostras compartilham o mesmo erro sistemático, porque aí `N` grande não
salva ninguém, só confirma o erro com mais confiança.

> 🗣️ "Best-of-N não é alternativa a treinar. Ele gasta computação de inferência, para sempre, para não gastar computação de treino, uma vez."

> **Nota:** Bastidor: amarrar com a demo — o pontuador que decide aqui é o mesmo objeto que a
> demo treinou. Se o RM tem viés, escolher o argmax dele é a forma mais direta de explorá-lo. A
> conta do `log N` — distribuição do máximo e o valor exato `log N − (N−1)/N` — está em A.5, com
> a tabela de valores. É a derivação mais curta do apêndice e a mais fácil de fazer no quadro se
> sobrar tempo.

### Slide 13 · DPO: a conta que apaga o modelo de recompensa · 01:34–01:41

Agora a conta que mudou a prática da área. Eu não vou fazer ela no quadro — ela está inteira em
A.6 —, mas eu vou contar a história dela em três frases, porque a história é o que fica.

Frase um: o problema de RLHF regularizado por KL, aquele do slide 10, tem solução ótima em forma
**fechada**. Não é aproximação; é a solução exata. E ela diz que a política ótima é a referência
reponderada por uma exponencial da recompensa, dividida por uma constante de normalização que a
gente chama de `Z(x)` — a parte intratável, porque somaria sobre todas as respostas possíveis.

Frase dois: se eu **inverto** essa expressão e isolo a recompensa, ela vira uma razão de
log-probabilidades entre política e referência, mais um termo que depende só do prompt.

Frase três, e é a que importa: o Bradley-Terry do slide 5 usa apenas a **diferença** de
recompensas entre duas respostas do **mesmo** prompt. As duas dividem o mesmo `x`, então dividem
o mesmo `Z(x)` — e o termo intratável **cancela na subtração**.

*[Projeto a perda final.]*

E sobra isso: uma perda de classificação escrita diretamente sobre a política. Nenhum modelo de
recompensa explícito. Nenhum crítico. Nenhum loop de amostragem. Dois passos forward — política e
referência — e um backward. Das quatro caixas que estão desenhadas ali no quadro, sobraram duas,
e uma delas está congelada.

Duas ressalvas honestas, porque "DPO é PPO mais simples e igual" é falso. Primeira: DPO é
off-policy por construção. Ele aprende dos pares que existem no dataset; se esses pares foram
gerados por outro modelo, o gradiente empurra a política para longe da distribuição dela própria,
e a qualidade cai. Segunda, e essa vocês vão ver nos logs: existe um modo de falha em que a
margem entre preferido e rejeitado cresce porque a log-probabilidade do **rejeitado desaba**, não
porque a do preferido melhora. O modelo aprende a odiar o rejeitado em vez de amar o preferido —
e as duas coisas produzem exatamente a mesma curva de perda.

O diagnóstico para isso é de uma linha: registrar as duas log-probabilidades separadas, não só a
margem. Em A.6 tem o gradiente escrito, e dá para ver na álgebra que nada no objetivo exige que a
do preferido suba.

> 🗣️ "A partição cancela porque os dois lados dividem o mesmo prompt. É esse cancelamento, e só ele, que transforma um problema de RL num `model.fit()`."

> **Nota:** Bastidor: **não derivar.** Contar as três frases e mostrar a perda. Na V1 este era o
> slide mais longo do Bloco 2, com a derivação no quadro; agora os mesmos 7 min vão para as três
> frases, as ressalvas e o modo de falha — que é o que a turma vai encontrar na prática. A
> derivação completa, com o gradiente e a análise de por que prompts diferentes não podem ser
> pareados, está em A.6. Se pedirem: Parte 4, item 4.

### Slide 14 · [Exercício] Diagnosticar e escolher · 01:41–01:50

Nove minutos: seis de dupla e três de correção. Três fichas, e para cada uma eu quero causa,
evidência e decisão.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> 🗣️ "Nenhuma das três se resolve derivando. As três se resolvem sabendo o que a fórmula prevê e de onde vem a recompensa."

> **Nota:** Bastidor: cronometrar de verdade. As duas primeiras fichas são os cartões 2 e 3 da
> abertura voltando como diagnóstico — o arco da aula fecha aqui, e vale dizer isso em voz alta
> na correção. Se a turma tiver menos de dez pessoas, fazer em plenária e ganhar 2 min para o
> fechamento.

### Slide 15 · DPO × PPO: o critério de escolha · 01:50–01:55

Deixa eu revelar a terceira ficha e transformar isso numa cola de uma página.

O cenário do classificador de segurança é PPO, e a razão está na **origem da recompensa**. Ali não
existem pares de preferência — existe um classificador auditado, que é um programa. Um programa
não é diferenciável e não vira dataset de comparação; ele pontua o que eu mandar, quando eu
mandar. Isso pede amostrar da política, pontuar, atualizar — que é exatamente o loop do PPO. E a
equipe tem infraestrutura para iterar toda semana.

O contra-exemplo que fecha o critério: quarenta mil pares já anotados, sobre respostas geradas
pelo **próprio** modelo SFT da equipe, três pessoas e duas GPUs de vinte e quatro giga. Esse é
DPO, e a razão não é simplicidade: é que os pares estão on-distribution, que é a condição em que
o DPO funciona bem. Com aquele hardware, montar amostragem online e um crítico seria gastar o
orçamento inteiro em infraestrutura.

E existe o meio-termo que a indústria de fato pratica, o **DPO iterado**: amostrar da política
atual, anotar aqueles pares, treinar DPO, repetir. Recupera boa parte do ganho de ser on-policy
sem crítico e sem loop de RL. Não é uma terceira via independente — é o DPO com o problema do
off-policy remendado por iteração, e A.6 mostra exatamente qual premissa ele está restaurando.

Então, no lugar de "qual dos dois é melhor", eu faço duas perguntas.

> 🗣️ "A pergunta não é qual é melhor. É: os meus dados são fixos ou amostráveis, e a minha recompensa vem de gente ou de um programa?"

> **Nota:** Bastidor: cola de prova — projetar as três colunas e ficar em silêncio uns segundos
> para a turma fotografar. Se as duplas discordarem, usar a discordância: quem escolheu DPO no
> cenário do classificador normalmente esqueceu que não existem pares ali.

### Slide 16 · Fechamento: o pipeline, e um professor que discorda de si mesmo · 01:55–02:00

Deixa eu juntar a aula em um desenho e mandar vocês para casa com uma tensão na cabeça.

O pipeline inteiro, da esquerda para a direita: pré-treino dá capacidade, SFT dá forma, o SFT
amostra respostas que humanos comparam, as comparações treinam um modelo de recompensa por
Bradley-Terry, e esse escalar é gasto de três formas — PPO com coleira de KL, DPO com perda
fechada, ou Best-of-N pendurado na inferência sem tocar em peso nenhum.

E os três defeitos com que eu abri têm agora três respostas diferentes. O modelo que acerta a
forma e erra o pedido: faltava o sinal de preferência, e a fábrica dele é o Bloco 1 inteiro. O
bajulador: é sobre-otimização de um proxy, e se lê contra o KL. E o modelo que piorou no que já
sabia: é deriva de distribuição, e o termo de KL existe exatamente para conter isso.

Agora a tensão. Todo o cuidado desta aula — a coleira, o orçamento, o ensemble, o RLHF iterado, a
avaliação humana fora do RM — existe por um motivo só: o sinal de recompensa é um proxy ruidoso.
Ele vem de gente, e gente discorda em trinta por cento das comparações abertas. A gente construiu
uma máquina elaborada para extrair o máximo de um professor que não tem certeza do que está
ensinando.

E é aí que a próxima aula entra. Existe uma classe de tarefas em que a recompensa não precisa de
humano nenhum, porque a resposta é **verificável**: o resultado da conta está certo ou errado; o
teste unitário passa ou não passa. Nesses casos o professor é um programa — ele não se contradiz,
não se cansa e não pode ser bajulado. A Aula 16 é sobre apontar aprendizagem por reforço para
esse tipo de sinal: é GRPO e é o pipeline do DeepSeek-R1.

A leitura da semana são os dois papers do slide: Ouyang e coautores, *InstructGPT*, arXiv
2203.02155, e Rafailov e coautores, *DPO*, arXiv 2305.18290. Para quem quiser o PPO na fonte,
Schulman e coautores, arXiv 1707.06347. As perguntas dirigidas estão no plano de aula, e as duas
se respondem com o apêndice ao lado.

> 🗣️ "Hoje a recompensa veio de gente, e gente discorda. Na Aula 16 ela vem de um verificador que não discorda de si mesmo."

> **Nota:** Bastidor: projetar o pipeline e ficar em silêncio para a turma fotografar. Antes de
> encerrar, mostrar o apêndice por 30 s: são seis itens e mais matemática do que a V1 tinha no
> fluxo inteiro. Quem quiser rigor tem para onde ir, e quem quiser só decidir também. A ponte
> para a Aula 16 tem que ser dita em voz alta, não subentendida. Não estourar das 02:00.

---

## Parte 2 — Demonstração guiada

Doze minutos, no fim do Bloco 1, com `codigo/demo-bradley-terry.py`. Roda em CPU, em segundos,
sem rede, sem chave de API e sem download de modelo. Na V2 ela deixa de ser ilustração da fórmula
e passa a ser a **evidência** de duas afirmações do fluxo: que o RM aprende separação e não
qualidade, e que existe um teto que é do rótulo e não do modelo.

**1.** **[Abro o script e mostro o gerador sintético `make_pairs`]** Deixa eu mostrar o mundo
desta demo antes de rodar. Cada "resposta" aqui é um vetor de oito atributos, e a qualidade
verdadeira dela é uma projeção linear desses atributos num vetor de pesos oculto. Vence o par
quem tem qualidade verdadeira maior. E o ponto pedagógico está na palavra oculta: quem anota
nunca vê essa função. Ele só compara dois vetores e aponta um. É exatamente a situação do
anotador humano, que não tem acesso à função de qualidade que ele próprio está aplicando.

**2.** **[Mostro a linha da perda no `train_reward_model`]** A perda, aqui:
`-F.logsigmoid(r_w - r_l).mean()`. Uma linha. Isso é literalmente a fórmula de Bradley-Terry do
slide 5, sem nenhuma adaptação e sem nenhum truque. E o modelo de recompensa é um
`nn.Linear(8, 1)` — a cabeça escalar do slide 6. Num LLM de verdade, o que muda é só o que
alimenta essa cabeça.

**3.** **[Rodo `python demo-bradley-terry.py` e acompanho o primeiro bloco de log, com ruído 0%]**
Rodando. Três colunas para acompanhar. A acurácia contra o rótulo do anotador, que é o que se
mede na prática. A acurácia contra a ordem verdadeira, que só existe porque a demo é sintética —
num pipeline real esse número é inobservável. E a separação média, que é a diferença de score
entre preferido e rejeitado. Com ruído zero, as três sobem juntas.

**4.** **[Aponto os painéis de histogramas antes e depois]** Os dois primeiros painéis são a coisa
que eu queria mostrar. Antes do treino, as distribuições de score das preferidas e das rejeitadas
estão em cima uma da outra — o RM não sabe nada. Depois do treino, elas se separam. E o eixo x
está rotulado "unidade arbitrária", o que não é modéstia do gráfico: é o slide 5 aparecendo
desenhado. Não existe unidade. Existe distância.

**5.** **[Aponto o painel da direita: acurácia por passo nos três níveis de ruído]** Agora a
medição que sustenta o slide 6. O script treina três vezes: com zero, dez e vinte e cinco por
cento dos rótulos invertidos — que é o anotador discordando. As linhas tracejadas são o teto de
cada caso, que é um menos o ruído. E as curvas encostam nos tracejados e param. Com vinte e cinco
por cento de rótulos invertidos, a acurácia medida satura em torno de **zero vírgula setenta e
cinco** e não passa disso, por mais que eu treine.

**6.** **[Volto à tabela-resumo em texto no terminal e leio a coluna acc(verdade)]** E aqui está o
detalhe que separa "o modelo é ruim" de "o rótulo é ruim". Na coluna da ordem verdadeira, a
recuperação continua alta mesmo com ruído — o modelo aprendeu a função certa. O teto é do rótulo.
Isso é o número dos setenta por cento do slide 4 aparecendo como consequência mensurável: nenhum
RM treinado num conjunto com trinta por cento de discordância vai medir melhor que isso, e
nenhuma quantidade de GPU resolve. A razão algébrica desse teto está em A.1 — sai da forma da
perda, não da capacidade do modelo.

**7.** **[Fecho o script e enuncio o que a demo não mostra]** E deixa eu ser explícito sobre o que
esta demo **não** mostra, para ninguém sair com a impressão errada: não tem política sendo
treinada, não tem penalidade de KL, não tem reward hacking. Nada disso está aqui. O que está aqui
é a fábrica do escalar, e ela precisa estar sólida antes do intervalo — porque depois do intervalo
a aula inteira é sobre como gastar esse escalar, e sobre o que dá errado quando ele é gasto demais.

> **Nota de contingência:** Bastidor: rodar o script na véspera e deixar
> `separacao-bradley-terry.png` salvo em `codigo/` — se torch ou matplotlib brigarem na hora,
> projetar o PNG e conduzir pelos passos 4, 5 e 6, que são os pedagogicamente essenciais. O script
> já degrada sozinho: sem matplotlib, imprime a tabela-resumo em texto puro e segue. Se o tempo
> apertar, os passos 1 e 2 viram uma frase cada; o passo **5 não se corta**, porque é a evidência
> do teto. Se alguém perguntar por que a acurácia contra o anotador é sempre menor que a contra a
> verdade, a resposta é que o held-out foi anotado pelos mesmos anotadores ruidosos — o erro está
> no gabarito da validação, e isso acontece em pipeline real.

---

## Parte 3 — Hands-on

Nove minutos no fim do Bloco 2: seis de dupla, três de correção. O exercício da V1 era escolher
DPO ou PPO em dois cenários; ele virou a terceira ficha, e as duas primeiras passaram a ser
diagnóstico — que é o que a prova da Aula 17 pesa agora.

**1.** **[Projeto as três fichas e formo as duplas]** Seis minutos, em dupla. Três fichas, e para
cada uma eu quero três coisas: a causa provável, a evidência que confirmaria essa causa, e a
decisão que ela força. A segunda e a terceira são as que valem — nomear a causa sem dizer como
confirmar não fecha a ficha.

As três fichas:

1. **O bajulador.** Depois do RLHF, o assistente passou a concordar com premissas falsas do
   usuário. A recompensa média do RM no treino subiu de forma consistente, do começo ao fim.
   Nenhum erro no log.
2. **A capacidade que sumiu.** Um modelo que convertia unidades corretamente antes do alinhamento
   passou a errar. A perda de treino caiu bem. O KL contra a referência triplicou.
3. **A decisão.** Uma equipe de plataforma precisa reduzir uma taxa de violação de política de
   segurança, medida por um classificador já existente e auditado. Há infraestrutura de amostragem
   online e budget para iterar semanalmente. DPO ou PPO — e por quê?

*Bastidor — respostas e erros comuns:*
Ficha 1 — reward hacking: o RM foi otimizado além da região onde foi validado, e bajular é um dos
quatro sintomas clássicos. A evidência é avaliação **fora** do RM, e a leitura correta é a
preferência humana traçada contra o KL, não contra passos de treino. A decisão é orçamento de KL
explícito e RLHF iterado. O erro comum é dizer "o RM está errado" — o RM está fazendo exatamente
o que foi treinado para fazer; o erro foi confiar nele fora da região validada.
Ficha 2 — deriva de distribuição por beta baixo demais: KL triplicado é a assinatura. A evidência
é rodar o eval de capacidade em checkpoints **ordenados por KL** e ver onde a curva vira. A
decisão é subir beta ou parar no joelho. O erro comum é atribuir a "esquecimento catastrófico" sem
dizer o que mediria — o nome não é diagnóstico, a medição é.
Ficha 3 — PPO: não existem pares ali, existe um programa que pontua. Um programa não é
diferenciável e não vira dataset de comparação sem alguém construir os pares. O erro típico é
escolher DPO por hábito. O erro mais interessante é propor DPO iterado — vale meio ponto e vale
discussão: dá para construir pares pontuando amostras com o classificador, mas aí se joga fora a
informação contínua do score para transformá-la em ordenação binária.

*Como recolher:* três minutos. Uma dupla para a ficha 1, e eu forço a segunda parte — "como você
confirmaria?". Corrijo a ficha 2 rápido, porque é o cartão 3 da abertura fechando o arco, e vale
dizer isso em voz alta. E a ficha 3 fica para o slide 15, que é o próximo: a discordância entre as
duplas é o material daquela síntese. Fecho com: "reparem que nenhuma das três pedia derivação, e
as três pediam saber o que a fórmula prevê".

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a derivação em
aula. A regra geral é remeter ao apêndice e seguir; conduzir uma derivação só se sobrar tempo, e
anunciando que é conteúdo de consulta.

> **Nota:** Bastidor: o custo de cada item abaixo sai do Bloco 2. Se eu fizer o item 4, perco o
> exercício — e o exercício vale mais para o objetivo da aula. A ordem de preferência para
> sacrificar, se for preciso: primeiro o slide 3 (o que o alinhamento acrescenta, cuja informação
> volta no 16), depois os passos 1 e 2 da demo, depois o slide 12 (Best-of-N, que o slide sustenta
> sozinho), e só então o exercício.

**Item 1 — "De onde sai essa perda do Bradley-Terry?" (A.1, ~6 min).**
A pergunta mais provável do Bloco 1. Eu escrevo a razão de exponenciais, divido numerador e
denominador pela exponencial do preferido, e mostro que sobra um sobre um mais a exponencial da
diferença negativa — que é a sigmoide. Três linhas. Depois digo que a perda é só o log negativo
disso, em média sobre os pares. **Não** faço o gradiente no quadro: menciono que o peso de cada
par é `1 − σ(Δ)` e que é isso que faz par fácil parar de ensinar, e remeto a A.1.

**Item 2 — "Por que cortar a razão em vez de limitar o passo?" (A.3, ~7 min).**
Vale se a turma tiver base de RL. Eu escrevo a identidade de amostragem por importância — a
esperança sob a política nova vira esperança sob a antiga vezes a razão — para mostrar de onde a
razão **vem**, que é a parte que ninguém conta. Depois faço só **dois** dos quatro casos de sinal:
vantagem positiva com razão acima de um mais epsilon (o termo cortado é menor, o mínimo escolhe
ele, e o objetivo vira constante), e vantagem positiva com razão abaixo de um menos epsilon (o
mínimo escolhe o não cortado, e o gradiente volta a puxar). Os outros dois são simétricos e ficam
em A.3.

**Item 3 — "De onde vem a forma fechada da política ótima?" (A.4, ~6 min).**
Eu monto o lagrangiano com a restrição de somar um, derivo em relação à probabilidade — lembrando
que a derivada de `π log π` traz o `log π + 1` —, isolo o logaritmo e exponencio. Sai a referência
vezes a exponencial da recompensa sobre beta, dividida pela partição. Quatro linhas. E fecho
fazendo os dois limites em voz alta, que é o que rende: beta grande devolve a referência, beta
pequeno colapsa no argmax do RM.

**Item 4 — "Mostra o cancelamento do `Z(x)`?" (A.6, ~8 min).**
A pergunta mais provável do Bloco 2, e a mais cara. Só faço se o item 3 já tiver sido feito, porque
ele **depende** da forma fechada. Eu tomo o log dos dois lados, isolo a recompensa, escrevo a
diferença entre preferido e rejeitado e mostro os dois termos de partição se anulando. Se não
houver tempo, a resposta curta é a das três frases do slide 13 — forma fechada, inversão,
cancelamento — mais "a conta inteira, com o gradiente, está em A.6".

**Item 5 — "Por que o KL do Best-of-N é logarítmico?" (A.5, ~5 min).**
Raramente perguntam, e é a mais bonita de fazer no quadro se sobrar tempo. Eu escrevo a densidade
do máximo de `N` amostras, tomo o log da razão, e mostro que sai `log N` mais um termo pequeno.
A integral do `log u` contra a densidade do máximo eu **não** faço — digo que dá menos um sobre
`N` e que a conta está em A.5, com a tabela de valores. O que vale cravar em voz alta é a leitura:
`N` igual a oito custa mais ou menos o mesmo que treinar até um KL de um vírgula dois.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala nos Slides 15 e 16 da Parte 1: a revelação da terceira
ficha e o critério DPO × PPO, depois o pipeline completo — capacidade, forma, julgamento — com os
três defeitos da abertura recebendo cada um a sua explicação, e a tensão que fecha a aula, que é o
sinal de recompensa ser um proxy humano ruidoso. A ponte para a Aula 16 é essa tensão sendo
resolvida por outro tipo de professor.

> 🗣️ "A gente montou uma máquina inteira para extrair o máximo de um professor que discorda de si mesmo em trinta por cento dos casos. Semana que vem eu troco esse professor por um que não discorda: um verificador."

---

*Roteiro do Instrutor · Aula 15 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
