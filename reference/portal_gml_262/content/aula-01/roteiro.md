---
aula: 1
titulo: "Apresentação da disciplina; panorama de LLMs; tarefas e métricas de NLP"
tipo: teorica
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 1 de 30 (V2)

## Como usar este roteiro

A prosa deste documento é **fala em primeira pessoa**: é o que eu digo em sala, na ordem em
que digo. Não é resumo do conteúdo — é o texto falado. Posso ler quase literalmente ou usar
como trilho e improvisar em cima.

As linhas marcadas com 🗣️ são as **frases-âncora**: as que eu cravo, quase palavra por
palavra, porque mudam o ritmo ou fecham um ponto. Cada slide tem uma.

As notas marcadas com **Bastidor** são operacionais e **não são faladas em voz alta** — são
lembretes do que abrir na tela, onde a turma costuma travar, o que responder se alguém
perguntar algo específico.

> **O que muda nesta versão.** O **contrato migrou inteiro para a Aula 0** — a sessão de
> recepção de 60 min da semana zero. Avaliação, composição da prova, política de uso de IA,
> arco dos oito labs e projeto final: nada disso é apresentado aqui. O que sobra é **uma linha
> de ponteiro de 30 segundos** no slide 1, apontando para o documento de uma página que está no
> canal da turma. Não é recapitulação, é apontamento — eu digo a linha e sigo. Os sete slides
> de contrato que a versão anterior tinha saíram, e os ~15 minutos que eles custavam foram
> **integralmente para métricas de NLP**. O Bloco 2 agora é 45 min só de métricas, e o ganho
> está em quatro lugares: a turma **calcula** a matriz de confusão de três detectores em dupla
> em vez de ver o resultado pronto (slide 8); BLEU e ROUGE ganham um exemplo numérico feito no
> quadro, com ordenações opostas (slide 10); a perplexidade ganha **slide próprio**, porque ela
> volta na Aula 2 e no Lab 2 (slide 11); e a quebra da métrica de referência ganha um segundo
> caso, com número (slide 12). A abertura ganhou um slide de sintoma: duas frases de relatório,
> as duas verdadeiras, as duas enganosas — e o Bloco 2 é a aula pagando essa dívida. A álgebra
> continua em A.1 a A.5 e eu **não** derivo no quadro; se a turma pedir, a **Parte 4** deste
> roteiro tem a condução pronta.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · Abertura · 00:00–00:04

Boa noite, pessoal. Sejam bem-vindos a Grandes Modelos de Linguagem: do Transformer aos
Agentes de IA.

Vou começar pelo fim, para vocês saberem onde a gente vai chegar. Na última aula desta
disciplina, vocês vão estar aqui na frente apresentando um sistema que vocês construíram —
com um modelo de linguagem dentro, com ferramentas que ele chama, e com números que provam
que funciona. Não um slide dizendo que funciona: números.

E uma coisa administrativa, em trinta segundos, porque eu não vou voltar nela. O contrato desta
disciplina — como vocês são avaliados, o que a prova cobra, a política de uso de IA, o arco dos
oito labs e o projeto final — eu apresentei na sessão de recepção, e está no **documento de uma
página** que está no canal da turma. Quem não estava lá tem até a próxima aula para ler; é uma
página. Eu não vou repetir aquilo aqui, porque hoje eu quero o tempo para outra coisa — e a
outra coisa começa no próximo slide.

> 🗣️ "Sessenta horas. No fim delas vocês não vão ter *aprendido sobre* LLM. Vocês vão ter construído um."

> **Nota:** Bastidor: começar com o slide de título já projetado e a sala em silêncio. Esta
> primeira fala tem que ser dita de pé, longe do computador — a sala julga a disciplina nos
> primeiros noventa segundos. Não abrir o Colab ainda. O ponteiro do contrato é **trinta
> segundos e não volta**: se alguém puxar assunto de nota ou de prova aqui, a resposta é "está
> na página do canal, e eu respondo no fim da aula" — porque o tempo que essa conversa consome
> é exatamente o tempo que eu tirei dela para dar ao Bloco 2. Se muita gente faltou à recepção,
> anotar isso e mandar a página por mensagem no fim da aula; ainda assim não repetir em sala.

### Slide 2 · Duas frases verdadeiras — e as duas erradas · 00:04–00:10

Agora deixa eu botar na tela as duas frases que organizam esta aula inteira.

A primeira: "o detector de fraude atingiu noventa e nove por cento de acurácia no conjunto de
teste". A segunda: "nosso modelo tem perplexidade quatro — bem melhor que o baseline publicado,
que reporta vinte".

Essas duas frases são de relatório real. Eu já vi as duas. E olhem o que eu vou afirmar: as
duas estão **certas**. Não tem erro de cálculo em nenhuma das duas, ninguém mentiu, ninguém
arredondou a favor. E as duas levam a uma decisão errada.

A primeira frase pode estar descrevendo um modelo que nunca achou uma fraude na vida dele. A
segunda pode estar descrevendo um modelo que é **pior** que o baseline com que ele está sendo
comparado, e não melhor. As duas coisas não são pegadinha — são o caso comum, e é por isso que
a segunda metade desta aula é inteira sobre isso.

Eu não vou responder nenhuma das duas agora. A primeira vocês vão responder com as próprias
mãos daqui a uma hora e sete minutos, com uma matriz de confusão preenchida em dupla. A segunda
eu respondo às uma e trinta e três, e ela vale um slide só para ela. Até lá, esses dois cartões
ficam com um espaço em branco embaixo, e a aula é a dívida.

> 🗣️ "Um número de avaliação sem o denominador não é informação — é decoração."

> **Nota:** Bastidor: este é o sintoma que abre a aula e é a única promessa que o deck faz.
> **Não resolver nenhuma das duas aqui** — antecipar a primeira queima o exercício do slide 8,
> que é a peça nova da V2. Se alguém já souber a resposta (acontece, e é ótimo sinal), anotar o
> nome e devolver a palavra a essa pessoa no slide 8, dizendo que ela vai conduzir a correção.
> Os marcadores de horário nos cartões são de propósito: eles fazem a turma perceber que a aula
> tem uma estrutura de dívida e pagamento, não uma lista de tópicos.

### Slide 3 · De ELIZA ao ChatGPT: cinco saltos · 00:10–00:23

Bom, pessoal. Antes das métricas, a história — porque cada salto desta área resolveu uma coisa
que o anterior não resolvia, e entender isso organiza tudo o que vem nas próximas vinte e nove
aulas.

Salto um, regras. ELIZA, 1966, do Weizenbaum. Casamento de padrão e reescrita: o usuário
digita "estou triste com minha mãe" e o programa devolve "fale mais sobre sua mãe". Zero
modelo de língua, e ainda assim as pessoas se apegavam à ELIZA — a secretária do Weizenbaum
pedia privacidade para conversar com o programa. Isso é a primeira lição da área, e ela vale
para hoje: a ilusão de compreensão é barata.

Salto dois, estatística. Modelos de n-gramas, tradução estatística, anos 90 e 2000. A língua
deixa de ser regra e passa a ser distribuição de probabilidade estimada por contagem. Vou
gastar um minuto extra aqui porque isso sustenta duas coisas mais adiante: sustenta a ideia de
próximo-token no fechamento e sustenta a perplexidade, que é a métrica que eu vou dar no slide
onze. A ideia é literalmente contar: quantas vezes "banco de" foi seguido de "dados" no corpus,
dividido por quantas vezes "banco de" apareceu. Funciona muito melhor que regra, e bate num
teto duro: esparsidade. A maioria das sequências de cinco palavras que vocês vão dizer hoje
nunca apareceu em nenhum corpus, e a contagem para elas é zero.

Salto três, representações densas. Word2Vec, 2013. Em vez de contar palavras, aprender vetores
para elas — e a semântica vira geometria. Palavras parecidas ficam próximas. Isso é a Aula 3
inteira. O teto aqui é que o vetor é estático: "banco" tem um vetor só, e ele tem que servir
para o banco do rio e para o banco que guarda dinheiro.

Salto quatro, atenção e Transformer. Atenção em tradução neural, 2014; o Transformer, 2017.
Aqui está o coração do curso: um mecanismo que resolve dependência longa e paralelismo ao
mesmo tempo. Aulas 5, 6 e 7, e vocês constroem ele à mão no Lab 2.

Salto cinco, escala e instrução. GPT-3 em 2020 mostra que um modelo grande o suficiente
aprende tarefa nova só de ver exemplos no prompt, sem treinar. E aí o ajuste por instrução e
por preferência transforma um completador de texto num assistente. Aulas 10 a 16.

E olha o padrão, que é a coisa que eu quero que sobreviva deste slide: cada salto trocou
trabalho humano por dados e computação. De escrever regra, para contar frequência, para
aprender representação, para aprender a própria função de comparação.

> 🗣️ "ChatGPT não foi um salto de arquitetura — a arquitetura é de 2017. Foi um salto de interface e de alinhamento."

> **Nota:** Bastidor: se a turma tiver poucos alunos com ML, gastar o tempo extra no salto dois
> — a intuição de "probabilidade estimada por contagem" é o que faz `PPL = exp(loss)` do slide
> 11 fazer sentido em vez de virar fórmula solta. A anedota da ELIZA é a parte descartável se o
> relógio apertar; o padrão do fim do slide não é. Este slide ganhou três minutos em relação à
> versão anterior porque o contrato saiu, mas o ganho principal da aula não está aqui — está no
> Bloco 2, e é bom não se acomodar neste slide.

### Slide 4 · Por que LLM virou infraestrutura · 00:23–00:33

Uma pergunta legítima: por que uma disciplina inteira sobre isso? Deep learning tem dez
subáreas.

Três propriedades que se combinaram. A primeira: uma interface única de texto substituiu N
modelos especializados. Antes, cada tarefa era um projeto — dataset próprio, modelo próprio,
deploy próprio. A segunda, que é a mais econômica: o custo marginal de tentar uma tarefa nova
caiu de "montar um dataset rotulado" para "escrever um prompt". Isso é uma mudança de ordem
de grandeza em quanto custa experimentar. E a terceira: a mesma pilha serve produto,
ferramenta interna e automação.

Agora, a consequência que interessa para esta disciplina. Se ficou barato fazer o modelo
funcionar, o gargalo se mudou de lugar. Ele saiu da modelagem e foi para dois lugares:
**avaliação** — como eu sei que funciona? — e **engenharia de sistema** — como eu ponho isso
em produção sem que exploda?

E é por isso que os Módulos 5, 6 e 7 desta disciplina existem, e é por isso que eles ocupam
quase metade do curso. É também por isso que a segunda metade da aula de hoje é quarenta e
cinco minutos de métrica, e não vinte. Se o gargalo da área é avaliação, uma aula honesta gasta
o tempo onde o gargalo está.

> 🗣️ "Ficou fácil fazer funcionar na demo. O difícil virou saber se funciona — e é aí que esta disciplina passa metade do tempo."

> **Nota:** Bastidor: dados de mercado e faixa salarial da praça são `[definir na oferta]` —
> trazer números atualizados de Recife/Brasil na semana da aula, não estimativa de cabeça. Se
> não tiver dado confiável, dizer isso à turma em vez de inventar. A frase sobre os quarenta e
> cinco minutos de métrica é o que justifica o desenho da aula em voz alta: vale dizer.

### Slide 5 · [Demo] Um modelo, quatro tarefas · 00:33–00:45

Eu acabei de afirmar que uma interface substituiu N modelos. Deixa eu mostrar isso funcionando,
e não só afirmar. E no fim eu vou fazer duas contas no quadro que valem para o bloco todo
depois do intervalo.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> 🗣️ "Quatro tarefas que dez anos atrás eram quatro projetos de mestrado. Zero treino, uma caixa de texto."

> **Nota:** Bastidor: a demo roda em navegador, sem código — parte da turma ainda está
> decidindo matrícula e não tem ambiente montado. Passos detalhados na Parte 2. Se o free tier
> falhar, usar as capturas de tela da véspera. O passo insubstituível é o das duas contagens de
> n-gramas no quadro: são os números que sustentam os slides 10 e 12, e eles não dependem de
> rede. A demo tem doze minutos agora, três mais que na versão anterior, e os três minutos vão
> todos para as contas — não para mais tarefas no chat.

### Slide 6 · A taxonomia pela forma da saída · 00:45–00:55

O que vocês acabaram de ver foram quatro tarefas, e elas caem em três famílias. E o critério
que define a família não é o domínio — é a **forma da saída**.

Família um, classificação de sequência: entra texto, sai um rótulo. Sentimento, intenção,
detecção de idioma, tópico. Uma resposta para o documento inteiro.

Família dois, rotulagem de tokens: entra texto, sai um rótulo por token. Reconhecimento de
entidade nomeada, classe gramatical, análise sintática. A saída tem o mesmo tamanho da
entrada.

Família três, geração: entra texto, sai texto de tamanho livre. Tradução, pergunta e
resposta, sumarização, código.

Deixa eu traduzir isso para vocês, que são gente de computação: é a diferença entre uma
função que retorna um enum, uma que retorna uma lista do mesmo tamanho da entrada, e uma que
retorna uma string de tamanho livre. É a assinatura da função que define a família.

E notaram uma coisa na demo? A extração de entidades — que é família dois, rotulagem — eu
resolvi pedindo JSON para um modelo generativo. Ou seja: a família da *tarefa* continua a
mesma, mas o modelo que resolve virou um só. Guardem isso, porque é a tese que eu fecho no
último slide.

Só que tem um detalhe que essa unificação não resolveu, e é o assunto do bloco depois do
intervalo. Cada uma dessas três famílias foi construída ao longo de décadas com **métricas
próprias**, e essas métricas não foram unificadas junto com os modelos. Dez minutos de
intervalo, e quando a gente voltar eu passo quarenta e cinco minutos só nisso.

> 🗣️ "A família não é o assunto do texto. É a assinatura da função: enum, lista do mesmo tamanho, ou string livre."

> **Nota:** Bastidor: aqui a turma frequentemente pergunta "e recomendação? e busca?". Resposta
> honesta: são tarefas de sistema, não de NLP puro — busca aparece na Aula 19 como
> recuperação. Não abrir esse fio agora. Anunciar o intervalo **junto com** o que vem depois:
> a turma volta mais rápido quando sabe que o bloco seguinte é uma coisa só, e não uma lista.

### Slide 7 · O detector de fraude com 99% de acurácia que nunca achou uma fraude · 01:05–01:12

Voltando. Primeira frase da abertura, e a hora de pagar.

Vou escrever um detector de fraude aqui, na frente de vocês, e ele tem uma linha:
`return False`. Não é fraude, nunca. Esse é o modelo inteiro.

Agora suponham que a fraude seja um por cento do volume, que é uma ordem de grandeza
realista. Acurácia desse modelo: noventa e nove por cento. Revocação: zero. Ele nunca achou
uma fraude na vida dele, e nunca vai achar. É literalmente a primeira frase do slide dois, e
ela era verdadeira.

E aqui está a parte que eu quero que fique, porque ela é mais forte do que "acurácia engana
em dado desbalanceado". Num problema em que a classe positiva tem prevalência `π`, o
classificador que não faz nada já entrega `um menos π` de acurácia. **De graça.** Com um por
cento de prevalência, a régua não é cinquenta por cento — é noventa e nove. Ler "noventa e
nove por cento de acurácia" sem saber a prevalência é ler um número sem denominador, e o
intervalo onde a informação vive tem largura de um ponto percentual.

As quatro métricas saem todas das quatro células da matriz de confusão, e eu vou desenhar
ela no quadro. Acurácia é acerto sobre total. Precisão é verdadeiro positivo sobre tudo que
eu **chamei** de positivo. Revocação é verdadeiro positivo sobre tudo que **era** positivo.
Notaram que os denominadores são coisas diferentes? Um é escolha do modelo, o outro é fato
do mundo. É por isso que precisão e revocação não são simétricas.

A analogia que eu uso é arbitragem de futebol. Precisão: das vezes que eu apitei, quantas
eram falta de verdade? Revocação: das faltas que houve, quantas eu apitei? Dá para ser
preciso e omisso — apitar só o que é óbvio. Dá para ter revocação alta e ser um desastre —
apitar tudo.

Agora, eu vou preencher **uma** linha dessa matriz no quadro: a do detector que retorna falso.
Zero verdadeiro positivo, zero falso positivo, cem falsos negativos, nove mil e novecentos
verdadeiros negativos. As outras duas linhas eu deixo em branco de propósito, porque quem vai
preencher é vocês.

> 🗣️ "Noventa e nove por cento de acurácia num problema de um por cento de prevalência é o piso, não o teto. A métrica não mentiu — eu escolhi a métrica errada."

> **Nota:** Bastidor: desenhar a matriz de confusão 2x2 no quadro, não no slide, e preencher
> **só** a linha do trivial ao vivo — `VP` e `FP` em zero, e a coluna vazia sendo o argumento.
> As outras duas linhas são o exercício do slide 8, e é isso que muda nesta versão: na anterior
> eu projetava a tabela dos três modelos resolvida e a turma via o resultado. Agora ela calcula.
> **Não** falar de média harmônica nem de `F_β` aqui — isso é o slide 9, que agora tem slide
> próprio. Guardar giz antes da aula. A tabela conferida está em A.1 e serve de gabarito para
> a correção do slide 8.

### Slide 8 · [Exercício 1] A matriz na mão: três detectores, seis números · 01:12–01:19

Sete minutos com vocês trabalhando, em dupla.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> 🗣️ "Seis divisões. E no fim eu quero saber qual dos três detectores vai para produção — e o que a acurácia disse sobre essa escolha."

> **Nota:** Bastidor: enunciado e correção na Parte 3, sub-bloco 1. Cronometrar de verdade —
> 4 min de dupla, 3 de correção. Este é o exercício que a V2 acrescentou com os minutos que o
> contrato liberou, e a regra de ouro é: a inversão da ordenação tem que ser **descoberta** pela
> sala, não anunciada por mim. Se eu falar antes, o exercício vira aritmética. Gabarito em A.1.

### Slide 9 · F₁ é média harmônica — e o peso é decisão de produto · 01:19–01:24

Vocês acabaram de ver que precisão e revocação medem coisas diferentes. A pergunta óbvia é:
dá para juntar as duas num número só? Dá, e o número é o `F₁`. E a forma como ele junta é o
que interessa.

Olhem esse detector: precisão um inteiro, revocação zero vírgula zero um. Ele apita raramente
e acerta sempre que apita. Se eu tirar a média normal, a aritmética, esse sistema vale zero
vírgula cinco — metade da nota, para um detector que perde noventa e nove por cento dos casos.
`F₁` dá zero vírgula zero dois.

`F₁` é a média **harmônica** de precisão e revocação. Eu não vou derivar por que harmônica e
não aritmética, mas eu vou dizer a consequência, que é o que importa: a harmônica é dominada
pelo **menor** dos dois. E é isso que a gente quer, porque um sistema que acha um por cento
dos casos não é um sistema mediano — é um sistema ruim, e a métrica tem que dizer isso.

E agora o alerta, porque muita gente sai da graduação com isso errado: `F₁` não é "a métrica
certa" universal. Olhem esses três números, todos do **mesmo** sistema, com precisão zero
vírgula trinta e revocação zero vírgula noventa: `F₀,₅` dá zero vírgula trezentos e quarenta e
seis; `F₁` dá zero vírgula quatrocentos e cinquenta; `F₂` dá zero vírgula seiscentos e quarenta
e três. Os três estão certos. O que muda é o `β`, que é quanto eu decidi que revocação importa
mais que precisão.

Em triagem médica, um falso negativo custa uma vida e um falso positivo custa um exame a mais
— então `β` maior que um. Em moderação de conteúdo, censurar indevidamente é caro — então `β`
menor que um. E aqui está a frase que eu quero que vocês levem: esses custos **não estão no
conjunto de dados**. Não existe como aprendê-los do dado. Escolher o peso é decisão de produto,
e reportar `F₁` sem justificar é assumir em silêncio que os dois erros custam o mesmo.

A conta de três linhas que mostra que `F₁` é a harmônica, mais a família `F_β` com o `β²` como
razão de importância, está em A ponto dois deste deck.

> 🗣️ "Os três números estão certos. `F₁` não é a métrica certa — é a escolha de dizer que um falso negativo e um falso positivo custam o mesmo."

> **Nota:** Bastidor: este slide era um parágrafo dentro do slide de acurácia na versão
> anterior; agora tem cinco minutos e slide próprio, e é parte do que os minutos do contrato
> pagaram. **Não** derivar a média harmônica: os dois números (0,505 contra 0,0198) já provam o
> ponto sozinhos. O que não se abre mão de dizer em voz alta é `c_FN` e `c_FP` não estarem no
> dado. Se pedirem a derivação, Parte 4, item 1. A desigualdade `H ≤ G ≤ A` está conferida em
> A.2 e vale projetar se alguém disputar.

### Slide 10 · BLEU e ROUGE: um numerador, dois denominadores · 01:24–01:33

Geração é onde fica interessante, porque a saída não é um rótulo — é texto, e existem muitos
textos certos.

BLEU mede **precisão** de n-gramas: dos pedaços que eu gerei, quantos aparecem na referência?
ROUGE inverte, e a inversão é literalmente uma troca de denominador: mesmo numerador, dividido
pelos n-gramas da **referência**. Ela mede revocação, e é a métrica de sumarização porque em
resumo o pecado é omitir.

Mas eu não quero que vocês decorem isso. Eu quero que vocês vejam acontecer. Vou fazer a conta
no quadro, com uma referência e dois candidatos.

A referência é a frase que ficou aqui desde a demo: "o gato está sobre o tapete", seis palavras.
Candidato A, curto: "o gato no tapete", quatro palavras. Candidato B, prolixo: "o gato está
deitado sobre o grande tapete velho", nove palavras.

Contando os unigramas em comum. O candidato A tem três: "o", "gato", "tapete". O candidato B
tem seis: "o" duas vezes, "gato", "está", "sobre", "tapete".

Agora as duas divisões, e é aqui que a coisa acontece. Precisão do A: três sobre quatro, zero
vírgula setecentos e cinquenta. Precisão do B: seis sobre nove, zero vírgula seiscentos e
sessenta e sete. Pela precisão, **o A ganha**.

Revocação do A: três sobre seis, zero vírgula cinco. Revocação do B: seis sobre seis, **um
inteiro**. Pela revocação, o B ganha, e ganha com nota máxima.

Olhem o que acabou de acontecer no quadro. Mesmo par de frases, mesmo numerador. Duas
divisões, e as duas ordenaram os candidatos ao **contrário** uma da outra. Uma métrica pune
exatamente o que a outra premia. E o candidato B tem revocação perfeita dizendo três palavras
que a referência nem tem — "deitado", "grande", "velho" — porque revocação não pergunta o que
sobrou.

E é por isso que as duas métricas são remendadas. O BLEU leva uma penalidade de brevidade
multiplicada por fora, senão escrever pouco seria a estratégia ótima. O ROUGE reporta uma `F`
em vez da revocação sozinha, senão escrever muito seria a estratégia ótima. Cada uma é
corrigida do lado em que ela é degenerada — e nenhuma das duas deixa de contar forma.

A conta inteira do BLEU — as quatro ordens de n-grama, o truncamento de contagem, a penalidade
de brevidade, e um exemplo em que o BLEU-4 dá **exatamente zero** para uma tradução correta —
está em A ponto três, com os dois candidatos deste quadro conferidos. O ROUGE-L, que usa a
maior subsequência comum e é sensível à ordem sem exigir palavras adjacentes, está em A ponto
quatro.

> 🗣️ "Mesmo numerador, dois denominadores, duas ordenações opostas. O denominador é quem decide qual sistema ganha."

> **Nota:** Bastidor: as duas contas vão **no quadro**, com os números aparecendo um por um; a
> tabela projetada é gabarito para conferir, não para ler. Este exemplo é a peça que a V2
> acrescentou aqui: na versão anterior este slide era só as três fórmulas com as três perguntas.
> **Não derivar BLEU** — a média geométrica, o truncamento e a `BP` estão em A.3. O candidato B
> é o que a turma resiste a aceitar: vale insistir que ROUGE-1 dá **um inteiro** para um texto
> prolixo. Se pedirem o BLEU-4 zerado, Parte 4, item 2. E os dois números da demo, circulados
> no quadro desde 00:45, voltam aqui: é o mesmo mecanismo com texto real.

### Slide 11 · Perplexidade: a métrica que dispensa gabarito · 01:33–01:38

Segunda frase da abertura, e a hora de pagar.

Perplexidade é uma criatura diferente das outras duas: ela não compara com referência humana
nenhuma. Não tem gabarito. Ela mede a surpresa do modelo diante de um texto — se o modelo
achava cada palavra provável, perplexidade baixa.

E ela tem a forma mais prática que existe: perplexidade é `exp` do `loss`. Literalmente. Se a
sua perda de treino é entropia cruzada média por token, o número que aparece na tela a cada
época, exponenciado, é a perplexidade. Vocês vão ver isso com os próprios olhos no Lab 2.

A leitura é bonita e vale decorar: perplexidade doze quer dizer que o modelo está tão indeciso
quanto alguém escolhendo uniformemente entre doze opções. A unidade é **opções**, não erro. E
tem um teto trivial, do mesmo jeito que a acurácia tinha um piso: um modelo que chuta uniforme
sobre um vocabulário de tamanho `V` tem perplexidade exatamente `V`. Perplexidade maior que o
tamanho do vocabulário não é modelo ruim — é bug.

Agora a segunda frase do slide dois. "Perplexidade quatro, melhor que o baseline de vinte."
Deixa eu contar o que pode estar acontecendo ali. Perplexidade é medida **por token**. Se o
modelo de perplexidade quatro é um modelo de caractere, e cada subword do outro modelo vale
quatro caracteres em média, então o mesmo modelo, sobre o mesmo texto, tem perplexidade
duzentos e cinquenta e seis quando medida por subword. Duzentos e cinquenta e seis contra
vinte. A conclusão se inverte inteira.

E olhem que isso não é uma imprecisão de dez por cento: é uma **potência**. Perplexidade B
igual a perplexidade A elevado à razão entre os números de tokens. Por isso o remendo
intuitivo — "então eu divido pela razão de fertilidade" — não funciona: dividir corrige um
fator, e o problema é um expoente. Além disso muda o espaço de eventos: prever o próximo
caractere entre noventa opções e prever a próxima subword entre trinta e duas mil não são a
mesma tarefa. A comparação não fica imprecisa; ela fica sem sentido.

A normalização que compara de verdade é bits por caractere, que não depende da decisão do
tokenizador. Nos dois casos que eu acabei de dar, os dois modelos dão bits por caractere
igual a dois — porque é o mesmo modelo. E o modelo real de subword, o de perplexidade vinte,
dá um vírgula zero oito: ele é substancialmente **melhor**, e essa conclusão só aparece depois
de normalizar. A conta inteira, com a derivação de `exp(H)`, o teto trivial e a conversão,
está em A ponto cinco.

Guardem este slide, porque ele volta duas vezes: na Aula 2 a gente mede a fertilidade em
tokenizadores reais — que é exatamente aquela razão, medida em vez de estimada — e no Lab 2
vocês produzem esse número com as próprias mãos.

> 🗣️ "Perplexidade é por token. Trocar o tokenizador não deixa a comparação imprecisa — deixa sem sentido, e a diferença é uma potência, não um fator."

> **Nota:** Bastidor: este slide é novo no fluxo da V2 e é onde parte dos minutos do contrato
> foi. Ele existe porque a perplexidade é o único conceito desta aula que reaparece duas vezes
> no curso — Aula 2 (fertilidade) e Lab 2, Aula 9, Checkpoint 4 (`exp(loss)` medido). Dizer "por
> token" em voz alta é obrigatório: é o gancho literal do slide 2 da próxima aula. **Não**
> derivar `exp(H)`; se perguntarem, Parte 4, itens 3 e 4. Riscar o segundo cartão do slide 2 no
> fim deste slide — o gesto físico de fechar a dívida funciona.

### Slide 12 · Onde a métrica de referência quebra · 01:38–01:43

Agora o furo que organiza metade do curso.

Sobreposição de n-gramas pressupõe que existe uma resposta certa, ou poucas. Quando existem
muitas respostas boas e mutuamente diferentes, o que a métrica mede não é qualidade — é
estilo.

Três casos, e os dois primeiros com número. Caso um, a paráfrase. Referência: "o gato está
sobre o tapete". Candidato: "o gato está no tapete". Isso é português melhor que a referência,
e o BLEU-4 dá **zero**, porque nenhum 4-grama casa e a média geométrica morre com um fator
zero. A conta está em A ponto três.

Caso dois, e este é o que eu quero que doa. Candidato: "o felino está sobre o carpete". Aqui eu
paro e faço uma votação de mão levantada: quem aí acha que essa frase quer dizer a mesma coisa
que a referência? … Todo mundo, e é o que eu esperava — mesmo comprimento, dois sinônimos,
sentido idêntico. E olha o que as ordens de n-grama fazem com ela: unigramas,
quatro sobre seis; bigramas, dois sobre cinco; trigramas, um sobre quatro; 4-gramas, **zero sobre
três**. BLEU-4 igual a zero, e aqui nem tem a desculpa da brevidade, porque as duas frases têm
o mesmo tamanho.

E aí vocês perguntam: então usa ROUGE. Não salva. ROUGE-1 dá zero vírgula seiscentos e sessenta
e sete e o ROUGE-L dá o mesmo, porque as duas contam a mesma coisa que o BLEU conta — forma.
Trocar de métrica de sobreposição não resolve o problema do sinônimo, e A ponto quatro tem essa
conta conferida.

E aqui alguém sempre pergunta — e é a pergunta certa: então por que ninguém consertou isso?
Consertaram. Em dois mil e cinco, e a métrica chama METEOR. Ela faz três coisas que o BLEU não
faz: casa palavra por radical e por **sinônimo**, e não só por forma exata; pesa revocação acima
de precisão, porque deixar de dizer é pior que dizer a mais; e cobra a ordem por fora, contando em
quantos pedaços contíguos o casamento ficou partido. Nessa frase do felino e do carpete que
acabou de dar zero, o METEOR dá zero vírgula novecentos e noventa e oito.

Só que — e é por isso que eu conto isso aqui e não como curiosidade — o caso três continua de pé.

Caso três é o inverso, e ele é pior: uma resposta **errada** que reaproveita as palavras da
referência tira nota alta. A métrica é sensível à forma e cega ao conteúdo, nas duas direções. E o
METEOR não muda nada nisso: ele casa melhor, e casar melhor não é verificar. A sequência inteira
BLEU → METEOR → juiz-modelo é uma sequência de tentativas de afrouxar a exigência de casar
literalmente com uma referência fixa, e o salto de verdade só acontece quando a referência fixa é
abandonada. Isso é a Aula 27. A conta do METEOR nos dois casos deste slide está em A ponto seis.

> 🗣️ "Casar melhor não é verificar. METEOR resolve o sinônimo e não resolve a mentira — e é essa segunda metade que sobra para a Aula 27."

Então não dá para medir nada? Dá — mas medir é um problema de engenharia próprio, com métodos
próprios, e é por isso que existe uma aula inteira só disso na Aula 27: avaliação humana com
rubrica, acordo entre anotadores, LLM como juiz calibrado contra rótulo humano, decomposição de
resposta em afirmações atômicas.

Isso é o que a nossa área chama de dívida de avaliação. A gente ficou muito bom em gerar e
continua ruim em julgar.

> 🗣️ "A gente ficou excelente em gerar texto e continua ruim em julgar texto. Metade desta disciplina é sobre essa dívida."

> **Nota:** Bastidor: este é o gancho mais importante da aula para o arco do curso, e ele ganhou
> dois minutos na V2 para caber o caso dois. A votação por mão levantada **antes** de revelar o
> `p₄ = 0` é a peça inteira: a discordância entre o julgamento unânime da sala e o número da
> métrica é o argumento, e ela não funciona se eu der o número primeiro. Se o tempo estourou,
> cortar o exercício do slide 13 antes de cortar este slide.

### Slide 13 · [Exercício 2] Da tarefa à métrica · 01:43–01:50

Sete minutos, em dupla, e agora com tudo o que a gente construiu.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> 🗣️ "Cinco cenários. Família, métrica, e — a coluna que vale — uma falha que essa métrica não pegaria."

> **Nota:** Bastidor: enunciado e correção na Parte 3, sub-bloco 2. Cronometrar de verdade —
> 4 min de dupla, 3 de correção. Este exercício roda mais rápido que na versão anterior porque
> o vocabulário já está construído: o exercício do slide 8 nomeou o piso `1 − π` e o slide 9
> nomeou o peso assimétrico, então os cenários 1 e 4 se resolvem com o que a sala já disse em
> voz alta. Os cenários 1 e 5 são os que importam. A terceira coluna é o mesmo verbo dos
> quarenta e dois pontos de diagnóstico da prova — a composição da prova já foi dada na sessão
> de recepção, então aqui é só nomear o verbo, sem reapresentar pesos.

### Slide 14 · Fechamento: a tese do próximo-token · 01:50–02:00

Deixa eu juntar as peças e mandar vocês para casa com uma frase na cabeça.

A gente viu três famílias de tarefa, cada uma com métricas próprias, construídas ao longo de
décadas. E a gente viu, na demo, um único modelo resolvendo todas as três sem treino nenhum —
só mudando a caixa de texto.

Isso aconteceu porque as tarefas de NLP foram todas reescritas como uma coisa só: prever o
próximo token. Classificação é gerar a palavra do rótulo. Extração é gerar um JSON. Tradução
é gerar em outro idioma. Uma interface, e é essa unificação que fez a área explodir.

Mas ela cobrou um preço, e o preço é o que eu quero que vocês levem: as métricas *não* foram
unificadas junto. A gente unificou o modelo e ficou com um problema de avaliação fragmentado
e mais difícil que antes. E as duas frases com que eu abri a aula são a prova disso — as duas
eram verdadeiras, e as duas precisaram de quarenta e cinco minutos de métrica para virarem
informação.

Na próxima aula a gente desce um nível: antes de prever o próximo token, alguém precisa
decidir o que é um token. Isso parece detalhe de implementação e não é — é uma decisão que
define custo de API, tamanho de janela de contexto, e por que modelos são piores em português
do que em inglês. E é a decisão que faz aquela conta da perplexidade do slide onze existir.
Aula 2, Tokenização.

Ah, e três coisas para a semana: criar as contas do checklist — Google para o Colab, Hugging
Face, e um provedor de API com free tier; escolher um número de avaliação que vocês já leram na
vida e escrever cinco linhas dizendo que denominador ele tinha e que falha ele não pegava; e a
leitura do Jurafsky com a pergunta dirigida no slide. A pergunta é: por que perplexidade só é
comparável com o mesmo tokenizador? E dessa vez com uma vantagem: a resposta está escrita em A
ponto cinco deste deck, com a conta e com um exemplo numérico. Quem ler A ponto cinco chega na
Aula 2 com metade do caminho andado.

> 🗣️ "A gente unificou o modelo e não unificou as métricas. Esse desequilíbrio é o assunto das próximas vinte e nove aulas."

> **Nota:** Bastidor: projetar o índice do apêndice por vinte segundos antes do checklist —
> cinco itens, e dizer só uma frase: a resposta da pergunta dirigida é o A.5. Depois projetar
> o checklist de setup e ficar 30 s em silêncio para a turma fotografar; funciona muito melhor
> que mandar por e-mail. Se alguém tiver dúvida de nota, prazo ou política de IA, é agora, na
> saída, individualmente — e a resposta é a página do canal. Não estourar o horário: acabar
> 02:00 na primeira aula é sinal de que o resto do semestre respeita o relógio.

---

## Parte 2 — Demonstração guiada

Esta demo roda em doze minutos, no navegador, sem código. É deliberado: na primeira aula parte
da sala ainda está decidindo matrícula e ninguém tem ambiente montado. O objetivo não é
ensinar a ferramenta — é provar a afirmação "uma interface substituiu N modelos" na frente
deles, e produzir **dois números medidos** que os slides 10 e 12 usam como evidência.

Os quatro primeiros passos são os mesmos da versão anterior e levam seis minutos. Os passos 6 a
8 — a contagem no quadro — ganharam três minutos, e é aí que a demo virou instrumento em vez
de ilustração.

Insumos preparados na véspera, num arquivo de texto local para copiar e colar sem depender de
rede: um comentário de app em português com três ou quatro linhas, a tradução de referência
desse comentário escrita por mim, e um parágrafo longo para sumarizar.

**1.** **[Abro o chat de um modelo de free tier, com o painel de parâmetros visível mas sem
tocar em nada]** Vou usar um modelo pequeno de free tier aqui, e vou deixar esse painel de
parâmetros à mostra de propósito — temperatura, top-p, essas coisas. Não vou tocar em nenhum
deles hoje. Guardem que eles existem, porque na Aula 10 e no Lab 3 a gente descobre que esses
botões mudam o comportamento do modelo sem mudar uma vírgula dos pesos.

**2.** **[Colo o comentário de app em português e peço o sentimento em uma palavra]** Primeiro
pedido: um comentário real de app, e eu quero o sentimento em uma palavra só. Olha a resposta.
Isso é a família um, classificação de sequência — entrou texto, saiu um rótulo. Dez anos atrás
isso era um classificador treinado num dataset rotulado à mão.

**3.** **[Sobre o mesmo texto, peço extração de entidades em JSON: pessoa, organização,
local]** Mesmo texto, pedido diferente: agora quero as entidades em JSON — pessoa,
organização, lugar. Notaram o que aconteceu? Isso é família dois, rotulagem de tokens, que
é uma tarefa de saída estruturada. E eu resolvi ela pedindo texto. O modelo gerou um JSON.

**4.** **[Peço a tradução do comentário para o inglês]** Terceiro: traduz para o inglês.
Família três, geração. Nenhum treino, mesmo modelo, terceira tarefa.

**5.** **[Colo o parágrafo longo e peço resumo em uma frase]** Quarto: um parágrafo longo,
resumido em uma frase. Ainda família três, ainda o mesmo modelo, ainda zero treino.

**6.** **[Escrevo no quadro a minha tradução de referência e a saída do modelo, uma embaixo da
outra]** Agora a parte que interessa, e é a parte que eu mais quero que sobreviva se a rede
cair. Eu escrevi a minha tradução desse comentário ontem, antes de ver a do modelo. Vou botar
as duas no quadro, uma embaixo da outra. E a pergunta que eu quero fazer para a sala antes de
contar nada é simples: a tradução do modelo está boa? … Ótimo, a sala disse que está boa.
Guardem esse julgamento, porque em dez minutos ele vai discordar de um número.

**7.** **[Circulo as sobreposições no quadro, palavra por palavra]** Vou contar à mão: quantos
unigramas em comum? … Quantos bigramas? … Pronto, esse é o numerador. E agora vem a parte que
eu quero fazer devagar, porque ela é o slide 10 inteiro em duas linhas de quadro.

**8.** **[Escrevo as duas frações, uma embaixo da outra, com os denominadores rotulados]**
Primeira divisão: esse numerador dividido pelos n-gramas da tradução **do modelo**. Vou
escrever o denominador com nome, "n-gramas do candidato". Isso é uma precisão, e é o coração do
BLEU. Segunda divisão: o **mesmo** numerador, dividido pelos n-gramas da **minha** tradução.
Denominador com nome: "n-gramas da referência". Isso é uma revocação, e é o coração do ROUGE.
Dois números diferentes, e o numerador nunca mudou. A sala julgou essa tradução boa, e a
precisão de n-gramas dela é medíocre — isso é o BLEU castigando uma tradução boa na frente de
vocês.

**9.** **[Circulo os dois números e deixo os dois no quadro até o fim da aula]** Esses dois
números ficam aí, com os denominadores escritos do lado. Eles voltam no slide de BLEU e ROUGE
e voltam no slide da dívida de avaliação. E se alguém quiser a conta completa, com as quatro
ordens de n-grama e a penalidade de brevidade, ela está no apêndice A ponto três com dois
exemplos resolvidos.

> **Nota de contingência:** Bastidor: se o free tier estourar quota ou a rede cair, usar as
> capturas de tela feitas na véspera — as quatro tarefas já estão fotografadas. Os passos 6 a
> 9 (a contagem no quadro) não dependem de rede e são a parte pedagogicamente essencial: se
> tudo falhar, fazer só eles com os textos impressos, e sobra tempo. Se o modelo devolver JSON
> malformado no passo 3, não consertar — comentar que formato estruturado é um problema real e
> que a Aula 21 trata disso com schema de ferramenta. O passo 6 tem uma armadilha de condução:
> a pergunta "está boa?" tem que ser feita **antes** de qualquer contagem, senão o julgamento
> da sala já vem contaminado pelo número.

---

## Parte 3 — Hands-on

Esta aula tem **dois** exercícios em dupla, os dois no Bloco 2, os dois de sete minutos. O
primeiro é a peça que a V2 acrescentou com os minutos que o contrato liberou: a turma calcula a
matriz de confusão em vez de ver a tabela resolvida. O segundo é o exercício de diagnóstico que
já existia, e ele fica mais rápido porque o primeiro construiu o vocabulário.

### Sub-bloco 1 — Exercício 1 · A matriz na mão (slide 8, 01:12–01:19)

**1.** **[Projeto a tabela com as células da matriz preenchidas e as três métricas em branco]**
Sete minutos com vocês, em dupla. Na tela está a matriz de confusão de três detectores de
fraude, avaliados no mesmo conjunto: dez mil transações, cem fraudes de verdade. As quatro
células estão dadas para os três. A primeira linha, a do `return False`, eu já resolvi como
exemplo de leitura. As outras duas estão em branco.

O que eu quero de cada dupla são **seis números**: acurácia, precisão e revocação do
conservador, e as mesmas três do agressivo. É divisão, não tem pegadinha nas contas. E depois
dos seis números eu quero uma frase: qual dos três detectores vai para produção numa triagem de
fraude, e o que a acurácia disse sobre essa escolha.

A tabela na tela:

```
modelo                     VP    FP    FN     VN   | acurácia  precisão  revocação
trivial (return False)      0     0   100  9.900   |  0,9900       —        0,00
conservador                20     5    80  9.895   |     ?         ?          ?
agressivo                  90   900    10  9.000   |     ?         ?          ?
```

*Bastidor — erros comuns:* a confusão mais frequente é trocar o denominador de precisão pelo de
revocação — dividir por `VP + FN` quando queria `VP + FP`. É exatamente o erro que o slide 7
antecipou ("um denominador é escolha do modelo, o outro é fato do mundo") e vale nomear assim
na correção, não como "erro de conta". A segunda é somar as quatro células e não conferir com
`N`: quem confere pega o próprio erro. A terceira é travar em `precisão(trivial) = 0/0` — isso
é achado legítimo, está nos casos-limite de A.1, e a resposta é que a convenção das bibliotecas
é devolver zero com aviso. E tem uma dupla, sempre, que responde a pergunta (b) com
"conservador", porque ele tem a melhor acurácia dos três: essa resposta é ouro para a correção.

*Como recolher:* quatro minutos de dupla, três de correção. A ordem da correção importa e não
é negociável: **primeiro** os seis números, escritos no quadro por voluntários; **depois** a
pergunta (b); e **só então** eu nomeio o resultado. O que a sala tem que dizer sozinha é que o
agressivo tem a **pior** acurácia dos três — zero vírgula novecentos e nove contra zero vírgula
novecentos e noventa do que não faz nada — e é o único que serve, porque acha noventa das cem
fraudes. Se eu anuncio isso antes, o exercício vira aritmética. Fecho voltando ao slide 2 e
riscando o primeiro cartão: "essa frase era verdadeira, e agora vocês sabem o que ela não
disse". Gabarito conferido, com as contas linha por linha, em A.1.

### Sub-bloco 2 — Exercício 2 · Da tarefa à métrica (slide 13, 01:43–01:50)

**2.** **[Projeto os cinco cenários e refaço as duplas]** Sete minutos, em dupla, e de
preferência trocando de parceiro — a metade da sala que já viu aprendizagem de máquina vai ser
útil para a metade que não viu. Cinco cenários no slide. Para cada um eu quero três coisas: a
família da tarefa, a métrica primária, e uma falha que essa métrica **não** pegaria.

Os cinco cenários:

1. Roteador de tickets de suporte em doze filas, com uma fila crítica que é dois por cento do
   volume.
2. Extração de número de processo e nome das partes em petições jurídicas.
3. Tradução português-inglês de descrições de produto de e-commerce.
4. Detector de discurso de ódio em comentários, com revisão humana depois.
5. Assistente que responde perguntas sobre o regulamento da universidade, citando a fonte.

*Bastidor — erros comuns:* no cenário 1, a dupla escreve "acurácia" por reflexo e não vê o
desbalanceamento da fila crítica — mas agora eu tenho uma vantagem que a versão anterior não
tinha: a sala calculou o piso `1 − π` com as próprias mãos meia hora antes, e basta apontar
para o quadro. A resposta boa menciona **macro** em vez de micro, que é o que A.1 formaliza. No
2, confundem a família: a saída é estruturada, é rotulagem, mesmo quando resolvida por geração;
a falha que a métrica não pega é o número de processo com um dígito trocado, que casa quase
todos os caracteres. No 3, a dupla escreve BLEU e a terceira coluna se preenche sozinha — é o
caso do sinônimo, que acabou de sair do quadro com número. No 4, esquecem que a revisão humana
a jusante muda a métrica: com humano depois, revocação alta importa mais que precisão, porque o
custo do falso positivo é um humano lendo — e isso é `β` maior que 1, que é A.2 e foi dito em
voz alta no slide 9. No 5, a dupla procura uma métrica de referência e não acha nenhuma que
sirva — e essa frustração é o objetivo do cenário.

*Como recolher:* quatro minutos de dupla, três de correção conduzida por mim. Não corrijo os
cinco: peço voluntário para o 1 e **forço a terceira coluna**, corrijo o 4 em trinta segundos
pelo lado do peso assimétrico (a sala já tem o vocabulário do slide 9), e uso o resto no
cenário 5. No 5, a resposta honesta é que nenhuma métrica clássica resolve — precisa de
verificação de factualidade e de atribuição de fonte, que é Aula 27 e é parte do que o projeto
final de vários grupos vai enfrentar. Encerro dizendo isso: "esse cenário não tem resposta com
o ferramental de hoje, e é por isso que ele está aqui". E emendo com a frase que nomeia o
verbo: "repararam que nenhum dos cinco pedia derivação, e que os cinco pediam saber o que a
métrica não vê? É isso que vale quarenta e dois pontos na prova — e os pesos estão na página do
canal, não vou repetir".

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a
derivação em aula. A regra geral é remeter ao apêndice e seguir. Nesta aula em particular a
regra é mais rígida que nas outras, e por um motivo que mudou nesta versão: o Bloco 2 agora é
quarenta e cinco minutos de métricas com **dois** exercícios cronometrados dentro, e não tem
folga nenhuma. Qualquer derivação aqui compete com um dos dois exercícios ou com o gancho da
dívida de avaliação.

> **Nota:** Bastidor: o custo de qualquer item abaixo sai do Bloco 2, e no Bloco 2 as três
> coisas insubstituíveis são o exercício da matriz (slide 8), o slide 12 (dívida de avaliação) e
> as duas contagens no quadro. A ordem de sacrifício, se eu decidir gastar tempo com uma
> derivação: primeiro o exercício 2 (slide 13, os cinco cenários), depois a anedota da ELIZA no
> slide 3, depois um minuto do slide 4. **Não corto** o exercício 1, o slide 11 nem o slide 12 —
> sem o exercício 1 a aula volta a ser a versão que mostrava o resultado pronto, sem o 11 a Aula
> 2 perde o gancho, e sem o 12 o arco do curso perde o slide que ele mais reutiliza. Se a
> pergunta vier de uma pessoa só, a resposta é individual, no fim da aula, e não para a sala.

**Item 1 — "Por que média harmônica, e não a média normal?" (A.2, ~4 min).**
A pergunta mais provável do bloco de métricas, e a mais barata de responder bem — e agora ela
tem endereço, porque o slide 9 é dela. Eu não preciso derivar a média harmônica: eu preciso dos
dois números que já estão na tela. Precisão um inteiro, revocação zero vírgula zero um. Média
aritmética: zero vírgula cinco. Média harmônica: dois vezes zero vírgula zero um dividido por
um vírgula zero um, que dá zero vírgula zero dois. E digo a frase: a harmônica é dominada pelo
menor dos dois, e é isso que eu quero. Se sobrar tempo, acrescento a desigualdade das médias —
harmônica menor ou igual a geométrica menor ou igual a aritmética, com igualdade só quando os
dois são iguais, e a geométrica desse par é zero vírgula um, conferida em A.2. A derivação
algébrica de `F_β` como média harmônica ponderada, com `β²` sendo a razão de importância,
está em A.2 e eu remeto.

**Item 2 — "Como o BLEU dá zero para uma tradução boa?" (A.3, ~6 min).**
Na versão anterior isso era um item de contingência; agora eu **já faço** a versão curta no
slide 12, com dois casos e os números das quatro ordens. Então esta contingência mudou de
natureza: ela só se justifica se a turma quiser ver a **penalidade de brevidade** entrar na
conta, que é a parte que eu não faço em sala. Se vier, eu escrevo a `BP` para o par curto do
slide 10 — candidato de quatro palavras contra referência de seis, `exp` de um menos seis sobre
quatro, que dá zero vírgula seis. E aí eu mostro o que é bonito: com a `BP`, o BLEU **volta** a
preferir o candidato prolixo, e é literalmente para isso que a penalidade existe. O quadro
completo dos dois candidatos, com precisão, revocação, `BP` e BLEU-1, está em A.3.

**Item 3 — "De onde vem `PPL = exp(H)`?" (A.5, ~4 min).**
Aparece quando alguém já viu entropia em outra disciplina, e agora aparece mais, porque o slide
11 enuncia `PPL = exp(loss)` e alguém sempre quer saber se `loss` e `H` são a mesma coisa. São.
Três linhas: perplexidade é a média geométrica do inverso das probabilidades; tira o log dos
dois lados; o log da média geométrica é a média dos logs, que é menos a entropia cruzada média
por token — que é exatamente o que a função de perda minimiza; exponencia e pronto. E fecho com
a leitura, que é o que vale: perplexidade é o número efetivo de opções entre as quais o modelo
hesita, e um modelo uniforme sobre `|V|` símbolos tem perplexidade exatamente `|V|`. As duas
ressalvas práticas — média por token e não por lote, e padding mascarado fora da média — estão
em A.5 e valem dizer, porque são o bug do Lab 2.

**Item 4 — "Então quanto muda a perplexidade se eu trocar o tokenizador?" (A.5, ~4 min).**
A pergunta que eu mais quero que apareça, porque ela é o gancho da Aula 2. Se vier, eu abro
espaço tirando do exercício 2. Escrevo que a entropia é menos o log da verossimilhança do texto
dividido pelo número de tokens; que o numerador é o mesmo texto nos dois casos; logo as duas
entropias diferem pela razão dos números de tokens. Exponenciando, a perplexidade de um é a
do outro **elevada** à razão. E dou o número: um modelo com perplexidade quatro por caractere,
com quatro caracteres por subword, tem perplexidade duzentos e cinquenta e seis por subword —
o mesmo modelo, dois números que diferem por um fator de sessenta e quatro. Se não houver
tempo, a versão de dez segundos é "é uma potência, não um fator" e o ponteiro para A.5.

**Item 5 — "E em multiclasse, com doze filas, como isso funciona?" (A.1, ~3 min).**
Aparece na correção do exercício 2, no cenário 1, e aparece mais nesta versão porque a sala
acabou de calcular uma matriz 2×2 e quer saber o que muda com `K` classes. Resposta em três
linhas: a matriz vira `K × K`, as métricas são calculadas por classe (uma contra o resto) e
depois agregadas — e a agregação é a decisão. Micro soma as células de todas as classes antes
de dividir, e por isso é dominado pelas classes frequentes; macro tira a média dos `F₁` por
classe, e por isso dá o mesmo peso a uma fila com cinquenta mil tickets e a uma com duzentos.
Num roteador de doze filas com uma fila crítica a dois por cento, o micro-F₁ fica alto e o
macro-F₁ fica baixo, e a fila que importa é a que só aparece no macro. As duas fórmulas estão
em A.1 e eu remeto.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 14 da Parte 1 — síntese da tese do
próximo-token, o desequilíbrio entre modelo unificado e métricas fragmentadas, as duas frases
da abertura fechadas, o índice do apêndice projetado por vinte segundos, ponte para a Aula 2
(Tokenização) e as três tarefas da semana.

> 🗣️ "Sessenta horas a partir de agora, vocês vão ter construído um sistema com um modelo de linguagem dentro e números que provam que ele funciona. Semana que vem a gente começa pelo começo: o que é um token."

---

*Roteiro do Instrutor · Aula 1 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
