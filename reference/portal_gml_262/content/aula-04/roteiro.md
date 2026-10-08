---
aula: 4
titulo: "Laboratório 1: Tokenizadores e embeddings"
tipo: laboratorio
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 4 de 30 (V2)

## Como usar este roteiro

A prosa deste documento é **fala em primeira pessoa**: é o que eu digo em sala, na ordem em que digo.
Não é resumo do conteúdo — é o texto falado. Posso ler quase literalmente ou usar como trilho e
improvisar em cima.

As linhas marcadas com 🗣️ são as **frases-âncora**: as que eu cravo, quase palavra por palavra, porque
mudam o ritmo ou fecham um ponto. Cada slide tem uma.

As notas marcadas com **Bastidor** são operacionais e **não são faladas em voz alta** — são lembretes do
que abrir na tela, onde a turma costuma travar, o que responder se alguém perguntar algo específico.
Neste lab elas carregam também os erros de execução que eu já sei que vão aparecer.

Este é o primeiro laboratório da disciplina, então o relógio manda mais do que nas teóricas: quinze
minutos de setup e contexto, vinte de live coding meu, sessenta e cinco de checkpoints com a turma
executando, dez de recolhimento. A Parte 2 é o meu live coding; a Parte 3 é a condução dos quatro
checkpoints.

> **O que muda nesta versão.** Este é um lab, e num lab a matemática **é** a prática. Por isso eu **não
> reordenei nada** — setup, demo e os quatro checkpoints continuam nos mesmos minutos. Duas mudanças, e
> só duas. Primeira: quando eu lanço um checkpoint, eu **abro pelo que a tela vai imprimir** quando
> estiver certo, e só depois digo o que fazer. Segunda: o deck ganhou um apêndice com o fundamento
> formal por trás de cada checkpoint (A.1 a A.5), e eu **cito o item** quando lanço o checkpoint, em uma
> frase, sem interromper a prática. Eu não conduzo derivação em sala. Se a turma pedir, a **Parte 4**
> deste roteiro tem o que fazer, o tempo de cada uma e o que sacrificar em troca.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · Abertura: Lab 1 — do texto ao vetor · 00:00–00:04

Boa noite, pessoal. Hoje é o primeiro laboratório da disciplina, e ele fecha o Módulo 1 na parte
prática: nas duas últimas aulas eu afirmei um monte de coisa sobre token e sobre vetor, e hoje a gente
mede todas elas.

Antes de qualquer coisa, uma informação que economiza a cota de vocês: **este lab roda em CPU**. Nenhuma
célula daqui pede GPU. Se alguém já foi no menu de ambiente de execução e selecionou acelerador, dá para
desligar sem medo — o primeiro lab que precisa de GPU de verdade é o Lab 2, na Aula 9, quando a gente
treina um GPT pequeno. Hoje o gargalo é download de tokenizador, não computação.

E deixa eu dizer o que a gente sai daqui com. Vocês saem com quatro tokenizadores reais medidos no mesmo
texto, com a razão de tokens entre português e inglês calculada num corpus paralelo — o número que vira
dinheiro na conta de API — e com um Word2Vec treinado por vocês, em português, cujos vizinhos vocês vão
olhar e julgar.

Uma nota rápida sobre este deck, e depois eu não falo mais disso: ele tem um apêndice, com cinco itens,
organizados por checkpoint. É a conta por trás de cada número que vocês vão produzir hoje. Ninguém
precisa disso para fazer o lab. Duas das seis questões-guia ficam muito melhores com ele — e eu vou
dizer quais, daqui a dois slides.

> 🗣️ "Nas duas últimas aulas eu afirmei. Hoje vocês medem — e uma das coisas que vocês vão medir é onde a minha afirmação não se sustenta."

> **Nota:** Bastidor: abrir com o notebook do aluno já projetado, na célula de instalação, sem rodar
> ainda. Repetir o aviso de CPU olhando para a turma — todo semestre alguém queima cota de GPU num lab
> que não usa GPU. Se a sala perguntar sobre o link do notebook, ele está no portal da disciplina e o
> caminho é `aulas/aula-04/codigo/`. A menção ao apêndice tem que caber em trinta segundos: se virar
> dois minutos de meta-conversa sobre o material, eu perdi tempo de bancada.

### Slide 2 · Recap: as Aulas 2 e 3 viram código hoje · 00:04–00:08

Deixa eu amarrar as duas aulas anteriores em quatro frases, porque cada checkpoint de hoje é uma delas
virando medição.

Aula 2: não existe "o" token. Existe um vocabulário aprendido de um corpus por um algoritmo — BPE
juntando os pares mais frequentes, WordPiece juntando pelo ganho de verossimilhança, Unigram podando um
vocabulário grande. E a consequência era prática: o mesmo conteúdo custa mais tokens em português do que
em inglês, e isso é dinheiro e é janela de contexto. Hoje isso é o Checkpoint 1 e o Checkpoint 2.

Aula 3: o significado não está no símbolo, está na posição dele num espaço vetorial. E aquela posição é
subproduto — a gente treina um classificador de contexto que ninguém quer usar, joga o classificador
fora e guarda a matriz. Hoje isso é o Checkpoint 3, onde vocês treinam essa matriz com as próprias mãos,
e o Checkpoint 4, onde vocês olham a geometria dela.

E eu deixei duas coisas em aberto na aula passada. A primeira foi de propósito e continua aberta: o
`banco` com um vetor só, que é assunto da Aula 6 e não de hoje. A segunda é a pergunta dirigida — quais
analogias vão falhar num corpus pequeno, e por quê. Hoje ninguém precisa responder isso de cabeça. Hoje
a resposta sai com dado, no Checkpoint 4, e ela é a parte mais valiosa do entregável.

> 🗣️ "Aula 2 me deu a régua, Aula 3 me deu o mapa. Hoje a gente mede a sala com a régua e desenha o mapa."

> **Nota:** Bastidor: quatro minutos, cronometrados. A tentação aqui é reexplicar BPE — não reexplicar;
> quem faltou pega o `plano.md` da Aula 2. Se alguém perguntar a diferença entre WordPiece e BPE,
> responder em uma frase (critério de merge: frequência × verossimilhança) e seguir, porque o Checkpoint
> 1 mostra a diferença na prática melhor que eu no quadro. A álgebra do critério do WordPiece está em
> A.2 da Aula 2, e é para lá que eu mando quem insistir.

### Slide 3 · O entregável e o critério · 00:08–00:12

Como todo lab desta disciplina, o que vale é o artefato. O entregável é o notebook **executado** — com as
saídas visíveis, não com as células limpas — mais as respostas de seis questões-guia que estão no próprio
notebook, mais a declaração de uso de IA.

Prazo: uma semana. E eu repito a política, porque hoje é o primeiro lab: os oito labs valem trinta por
cento da nota, e eu **descarto a menor nota** de vocês. Isso não é para relaxar hoje — é para que uma
semana ruim não decida o semestre.

Duas coisas que eu corrijo com rigor, e é melhor vocês saberem antes. A primeira: notebook sem saída
volta para reexecução, porque eu não corrijo código que eu não vi rodar. A segunda, e essa é a que
surpreende: eu quero o **resultado real**, inclusive o feio. No Checkpoint 4 a maioria das analogias de
vocês vai falhar. Analogia que falhou entra na tabela como falha, com a explicação. Quem reexecutar o
treino dez vezes até achar o caso bonito e me entregar só ele perde ponto em vez de ganhar.

E agora o que eu prometi no slide 1. Das seis questões-guia, duas separam nota de verdade: a **dois**, que
pergunta o que a razão entre português e inglês significa **e o que ela não permite concluir**, e a
**três**, que pergunta por que as analogias falham. As duas estão respondidas com rigor no apêndice deste
deck, em A ponto dois e A ponto cinco. Eu estou dizendo isso abertamente porque a resposta que eu quero
não é a que se decora — é a que se entende.

> 🗣️ "Analogia que falhou entra na tabela como falha. O que eu avalio não é o resultado bonito — é a explicação do resultado que apareceu."

> **Nota:** Bastidor: projetar a rubrica interna do lab (os cinco itens de 20%) e ficar uns segundos em
> silêncio para a turma fotografar. Se perguntarem se pode fazer em dupla: na aula sim, na entrega não —
> o notebook é individual, e quem não tem conta ou ambiente hoje trabalha em dupla e entrega o próprio
> arquivo depois. Nomear as duas questões-guia em voz alta é a única meta-conversa sobre o apêndice que
> vale o tempo dela.

### Slide 4 · Setup do ambiente · 00:12–00:15

Agora três minutos de máquina. Vou pedir para a turma abrir o notebook e rodar a primeira célula **já**,
antes de eu explicar qualquer coisa — porque ela instala as bibliotecas e baixa quatro tokenizadores, e
eu prefiro que esse download aconteça enquanto eu falo do que enquanto vocês esperam.

Um aviso sobre essa célula, e ele é o erro número um deste lab: ela fixa `gensim` na versão quatro ponto
três ponto três e `scipy` abaixo de um ponto catorze, e depois de instalar **o runtime precisa ser
reiniciado**. Se não reiniciar, o import do gensim quebra com uma mensagem sobre `triu` que não tem nada
a ver com o que vocês fizeram — é uma função de álgebra linear que o scipy removeu na versão um ponto
treze e que o gensim ainda chama. E a mensagem de erro não menciona versão nenhuma, o que faz a pessoa
procurar no lugar errado. Reiniciar o ambiente de execução e rodar de novo resolve. Eu deixei isso escrito
na capa do notebook em letra grande, porque metade da sala vai esbarrar nisso.

A segunda célula é de imports e de duas constantes, e eu quero destacar uma delas agora para não ter que
consertar depois: `PRECO_HIPOTETICO_POR_1K_TOKENS`, com valor zero vírgula cinquenta e o comentário "a
definir na oferta". Isso é **hipótese declarada do exercício**. Não é preço de provedor nenhum, e ninguém
sai daqui citando esse número como se fosse tabela de mercado. O que o exercício ensina é a aritmética,
não a tabela de um fornecedor.

A terceira célula carrega os quatro tokenizadores e imprime o tamanho do vocabulário de cada um — quatro
números diferentes, e essa é a primeira medição do dia.

> 🗣️ "Se o import do gensim reclamar de uma função chamada `triu`, não é culpa de vocês: é o runtime que precisa reiniciar depois da instalação."

> **Nota:** Bastidor: circular a sala nesses três minutos olhando telas em vez de falar. Erros que
> aparecem aqui: (1) esqueceram de reiniciar o runtime; (2) Colab desconectado por inatividade desde
> antes da aula; (3) rede da instituição bloqueando o Hugging Face — nesse caso, hotspot do celular
> resolve e vale dizer isso em voz alta. Não avançar para o live coding com mais de dois ou três alunos
> travados: melhor gastar um minuto extra aqui do que perder o CP1. A frase sobre o preço hipotético é
> dita **uma vez** e com ênfase; esse é o número que vaza para relatório depois.

### Slide 5 · [Demo] Live coding: o caminho completo em 20 minutos · 00:15–00:35

Antes de vocês trabalharem, eu vou fazer o caminho inteiro na frente de vocês, num notebook em branco,
digitando. São vinte minutos e não é para adiantar os checkpoints — é para que nenhum de vocês trave em
sintaxe depois.

O que eu vou mostrar é o espinho dorsal: um tokenizador, uma frase em português, as peças que saem, a
conta de fertilidade, um Word2Vec treinado em poucos milhares de sentenças e três vizinhos semânticos.
Vinte linhas de código para o caminho texto → tokens → vetores completo.

E eu vou produzir três números na frente de vocês, que eu vou anotar no quadro e deixar lá: as duas
fertilidades da mesma frase em português, e o tempo de treino em segundos. Guardem os três, porque eles
voltam como critério de conclusão do Checkpoint 1 e do Checkpoint 3.

*[O live coding completo, passo a passo, está na Parte 2 deste roteiro.]*

> 🗣️ "Vinte linhas para ir de texto a vetor. O trabalho de hoje não é o caminho — é medir o caminho."

> **Nota:** Bastidor: digitar de verdade, não colar. O valor pedagógico está em errar na frente deles e
> consertar. Não abrir o notebook do aluno para essa demo — notebook em branco, para ficar claro que o
> caminho é curto. Capturas de tela de cada passo prontas na véspera se a rede cair. Passos na Parte 2.
> Anotar as duas fertilidades e o tempo no canto do quadro e **não apagar** até o fim do CP3.

### Slide 6 · [Checkpoint 1] Quatro tokenizadores, três textos · 00:35–00:50

Agora são vocês. Quinze minutos no Checkpoint 1.

Antes de falar do que fazer, eu vou dizer como vocês sabem que acabou. Quando estiver certo, a tela tem
**duas coisas**. A primeira é uma tabela com **doze linhas** — quatro tokenizadores vezes três textos — e
a coluna de fertilidade preenchida em todas as doze. Doze, não quatro: fertilidade é propriedade do par
tokenizador e texto, e é por isso que a tabela é uma matriz e não uma lista. A segunda é a decomposição
das palavras longas em português: as peças de cada uma, nos quatro vocabulários, com a contagem ao lado.

Se vocês têm a tabela e não têm a coluna de fertilidade, vocês têm uma lista de contagens que não compara
nada, porque os três textos têm tamanhos diferentes.

Agora o que fazer. Quatro tokenizadores: o GPT-2 com BPE byte-level, o BERT inglês com WordPiece, o BERT
português da Neuralmind — também WordPiece, mas com vocabulário aprendido em português — e o
XLM-RoBERTa, que é Unigram sobre SentencePiece, multilíngue. Três textos: um parágrafo técnico em
português, o mesmo parágrafo em inglês, e um trecho de código com indentação.

E tem uma parte do checkpoint que é a mais reveladora: quebrar uma palavra longa em português e olhar as
peças. Quando vocês virem o que o BPE do GPT-2 faz com `inconstitucionalmente`, e o que o WordPiece
treinado em português faz com a mesma palavra, a Aula 2 inteira vai ficar óbvia de um jeito que o meu
slide não conseguiu. E se alguém quiser saber por que a diferença é tão grande, a resposta curta é UTF-8:
letra acentuada ocupa dois bytes, e num BPE byte-level isso vira dois símbolos base antes de qualquer
merge. A conta está em A ponto um.

*[A condução completa está na Parte 3 deste roteiro.]*

> 🗣️ "Um tokenizador treinado em português quebra `inconstitucionalmente` em pedaços que são morfemas. Um treinado em inglês quebra em pedaços que não são nada."

> **Nota:** Bastidor: circular. Erros comuns na Parte 3. O `xlm-roberta-base` é o download mais pesado
> dos quatro — se alguém estiver esperando, sugerir que comece a tabela com os três que já baixaram e
> complete depois. A pergunta que resolve metade dos casos em cinco segundos: "onde está a sua coluna de
> fertilidade?". Se alguém contar `input_ids` de `tokenizer(texto)` sem `add_special_tokens=False`, a
> tabela infla dois tokens **só nos três tokenizadores que usam token especial** — o viés é assimétrico e
> inverte a comparação; A.1 tem o número (17% de erro numa frase curta).

### Slide 7 · [Checkpoint 2] A razão PT/EN e a conta do custo · 00:50–01:05

Quinze minutos no Checkpoint 2, e esse é o checkpoint que eu mais quero que vocês levem para fora daqui,
porque ele é o único que fala a língua de quem paga a conta.

Como vocês sabem que acabou: **três blocos na tela e um parágrafo no notebook.** O primeiro bloco é, por
tokenizador, os tokens do lado português, os do lado inglês, a razão média e o desvio — e o número de
pares usados, que são vinte. O segundo é a projeção de custo. O terceiro é quantos pares cabem em oito
mil cento e noventa e dois tokens em cada idioma, com a perda em porcentagem. E o parágrafo tem três
linhas, sendo que a terceira é obrigatória e é a que vale nota: o que estes números **não** permitem
concluir.

Agora, o que fazer é rodar duas células. Mas eu quero avisar de uma armadilha que o próprio notebook arma,
e é o ponto deste checkpoint.

Ele imprime **duas médias diferentes**, em células diferentes. A coluna que se chama "razão média" é a
média das razões par a par: para cada par, divide português por inglês, e depois tira a média das vinte
divisões. A coluna de sobrepreço, na célula seguinte, sai de outra conta: soma todos os tokens do lado
português, soma todos do lado inglês, e divide os dois totais. Essas duas contas **dão números
diferentes**, e só uma delas é a da fatura.

Qual? A da fatura é a razão dos totais, porque a conta de API é proporcional ao total de tokens. A outra
serve para caracterizar o tokenizador, e para isso ela é a certa — com desvio e com o número de pares ao
lado. Quem reportar a média das razões como "quanto o português custa mais" está reportando um número que
não é o da fatura. A demonstração de que a razão dos totais é a média **ponderada pelo comprimento**, e um
contraexemplo com dois pares em que os dois números dão um vírgula cinco e um vírgula catorze, estão em A
ponto dois.

E a segunda coisa que A ponto dois resolve, que eu vou só enunciar: em dinheiro a relação é linear, em
janela ela é inversa. Razão de um vírgula trinta e três significa trinta e três por cento mais caro e
**vinte e cinco** por cento menos conteúdo na janela. Não é o mesmo número, e sai da mesma razão.

*[A condução completa está na Parte 3 deste roteiro.]*

> 🗣️ "Esse número é a razão pela qual o mesmo produto custa mais para atender em português. Não é opinião: é a divisão de duas contagens — e existem duas divisões possíveis."

> **Nota:** Bastidor: se alguém perguntar preço real de API, a resposta honesta é que preço muda toda
> hora e que a constante do notebook é didática; quem quiser o número atual consulta a página do provedor
> na hora. **Não estimar de cabeça.** Corrigir em voz alta e para a sala inteira quem tratar a constante
> como preço real. A formalização da fertilidade e a conta da janela estão em A.4 da Aula 2; A.2 daqui é
> o que é específico deste notebook. Intervalo de 10 min imediatamente depois deste checkpoint — anunciar
> o horário de volta em voz alta e escrever no canto do quadro.

### Slide 8 · [Checkpoint 3] Word2Vec em português com gensim · 01:15–01:32

Voltando. Dezessete minutos no Checkpoint 3, e aqui vocês param de usar modelo de outra pessoa e treinam
o seu.

Como vocês sabem que acabou: **quatro linhas na tela.** Qual das três fontes de corpus respondeu, com o
tamanho em megabytes. Quantas sentenças e quantos tokens de palavra. O tempo de treino em segundos. E o
tamanho do vocabulário depois do `min_count`. Mais o `most_similar` de três palavras escolhidas por
vocês, cada uma com um comentário de uma linha julgando a vizinhança.

Aquela terceira linha, o tempo de treino, é a materialização de uma frase que eu disse na Aula 3 —
embedding é subproduto barato. Vocês vão ver quantos segundos custa. E a quarta linha, o tamanho do
vocabulário, é a que mais importa para o Checkpoint 4, e eu vou explicar por quê.

São seis parâmetros na chamada: cem dimensões, janela cinco, `min_count` cinco, dez amostras negativas,
cinco épocas, skip-gram. Cada um desses números foi assunto da Aula 3, e agora eles são argumentos de uma
chamada de função. A tabela que diz onde cada um deles entra no objetivo está em A ponto três, e é a
leitura que eu recomendo antes de responder à questão-guia cinco.

Duas coisas de lá que eu vou dizer em voz alta porque são contraintuitivas.

A primeira é o `min_count`, que é a pegadinha honesta do checkpoint. Ele parece parâmetro de performance
e é decisão semântica: ele decide quais palavras **existem** no mapa. E a aritmética é a lei de Zipf —
subir o `min_count` corta **muitos tipos e poucas ocorrências**, porque a maior parte das palavras
distintas de qualquer corpus aparece pouquíssimas vezes. Os vetores que sobram ficam melhor estimados; as
palavras de domínio e os nomes próprios desaparecem. É trade-off, não ajuste.

A segunda é sobre o `seed` igual a quarenta e dois, que está na chamada. Ele **não** garante
reprodutibilidade aqui, porque `workers` é quatro: o gensim treina em várias threads sem sincronizar a
ordem das atualizações, e o resultado depende do escalonamento do sistema. Duas execuções idênticas dão
vetores diferentes. Se sobrarem dois minutos no fim, rodem a célula de treino duas vezes sem mudar nada e
comparem os vizinhos — é o experimento mais barato do lab, e é a primeira vez neste curso que vocês vão
ver um número se mover sozinho.

*[A condução completa está na Parte 3 deste roteiro.]*

> 🗣️ "`min_count` não é ajuste de performance. É a linha em que eu decido quais palavras existem no meu mapa."

> **Nota:** Bastidor: se o treino demorar mais de um minuto na máquina de alguém, o corpus veio grande
> demais — o notebook tem parâmetro de número máximo de sentenças e reduzir resolve. Se o gensim ainda
> estiver quebrado nesta altura (aluno que não reiniciou o runtime), mandar para a célula alternativa com
> `sklearn`: ela produz vetores piores mas destrava o CP4, que é o que importa para o entregável. Se
> alguém tiver vocabulário com poucas dezenas de entradas, passaram uma lista de strings em vez de uma
> lista de listas de tokens. O objetivo do skip-gram em si está em A.4 da Aula 3; A.3 daqui é sobre os
> hiperparâmetros.

### Slide 9 · [Checkpoint 4] PCA, t-SNE, vizinhos e analogias · 01:32–01:50

Dezoito minutos no último checkpoint, e é o que fecha o Módulo 1 inteiro.

Como vocês sabem que acabou: **duas coisas no notebook.** Primeira, dois gráficos lado a lado, com eixo
rotulado e legenda por grupo — um de PCA e um de t-SNE. Segunda, a tabela de quatro a seis analogias com
o resultado **real** de cada uma, e a linha final dizendo quantas acertaram no top-um.

Sobre os dois gráficos: eles existem porque mostram coisas diferentes, e a diferença tem consequência de
leitura. A PCA é uma projeção linear, e ela tem uma propriedade que dá segurança: a distância no gráfico
nunca é **maior** que a distância verdadeira. Então, num gráfico de PCA, se dois pontos aparecem longe,
eles estão longe. O contrário não vale: dois pontos podem estar colados na tela e separados nas noventa e
oito dimensões que a projeção jogou fora.

O t-SNE é o oposto. Ele preserva vizinhança local e distorce escala global, e não é acidente: a função
que ele minimiza pune muito quebrar uma vizinhança verdadeira e quase não pune inventar uma vizinhança
falsa. A consequência prática, e é o erro de leitura mais comum deste lab: num t-SNE, **a distância entre
dois aglomerados não quer dizer nada**. Nem o tamanho aparente de um aglomerado. Só a pertinência ao
aglomerado quer dizer. A prova das duas coisas — a contração da PCA e a assimetria do t-SNE — está em A
ponto quatro, com uma tabela de cinco afirmações dizendo qual gráfico autoriza qual.

Segundo, as analogias. Quatro a seis, com `most_similar` positivo e negativo, e o resultado real de cada
uma na tabela. E aqui eu volto na promessa da Aula 3: a maioria vai falhar.

Mas eu quero que vocês distingam duas coisas na coluna de resultado, porque elas não são a mesma. Se
aparecer `não`, a analogia rodou e o modelo errou. Se aparecer `fora do vocab`, **o teste não rodou** —
uma das palavras da entrada não tem vetor, porque o `min_count` a cortou. Confundir as duas na resposta da
questão-guia três é o erro que eu mais desconto. A tabela com as quatro razões estruturais da falha, e a
evidência que confirma cada uma, está em A ponto cinco — e a ordem de diagnóstico também: primeiro
disponibilidade, depois contagem, depois otimização, e só então conclusão sobre o método.

*[A condução completa está na Parte 3 deste roteiro.]*

> 🗣️ "Distância num t-SNE não significa nada. Aglomerado significa. Quem lê distância em t-SNE está lendo um artefato da projeção."

> **Nota:** Bastidor: aos 01:45, independentemente de onde a turma esteja, anunciar que faltam cinco
> minutos e que gráfico salvo já satisfaz metade do critério. Erro clássico: `perplexity` do t-SNE maior
> ou igual ao número de amostras — o notebook calcula um valor seguro, mas quem editou a lista de palavras
> pode quebrar isso, e o erro do sklearn é claro o suficiente. Quem terminar antes vai para as extensões,
> principalmente a do BPE próprio. Cortar na hora quem reexecuta o treino procurando a analogia bonita.

### Slide 10 · Recolhimento e ponte para a Aula 5 · 01:50–02:00

Fechando. Três coisas no entregável: notebook executado com as saídas visíveis, as seis questões-guia
respondidas, e a declaração de uso de IA. Uma semana de prazo. E de novo, porque é o primeiro lab: a
menor nota dos oito é descartada, e notebook sem saída volta para reexecução antes de eu corrigir
conteúdo.

Deixa eu inventariar o que vocês têm agora, porque é bastante: quatro tokenizadores medidos no mesmo
texto com fertilidade, a razão entre português e inglês com desvio e com o número de pares, um Word2Vec
treinado por vocês, dois gráficos de projeção e uma tabela de analogias com o resultado que apareceu de
verdade. Isso é o Módulo 1 inteiro virando número.

*[Projeto o índice do apêndice por vinte segundos: A ponto um fertilidade, A ponto dois a razão e as duas
médias, A ponto três os hiperparâmetros dentro do objetivo, A ponto quatro PCA contra t-SNE, A ponto
cinco as analogias em corpus pequeno.]*

E das seis questões-guia, eu repito: as duas que eu vou ler com mais atenção são a dois e a três, e as
duas estão respondidas com rigor em A ponto dois e A ponto cinco.

Agora, o que a gente fez hoje e onde isso trava. Vocês transformaram texto em tokens, tokens em IDs e IDs
em vetores. E o vetor que vocês treinaram é **fixo**: a palavra tem um ID, o ID indexa uma linha de uma
matriz, e aquela linha é a mesma sempre. Foi por isso que eu passei a Aula 3 inteira insistindo no
`banco`: instituição e assento dividem uma linha de matriz, e a linha é a média confusa dos dois sentidos.

Na próxima aula a gente ataca isso pela primeira vez de verdade. Aula 5, Modelos sequenciais e o
nascimento da atenção: começa pelo modelo que lê a sequência em ordem e carrega estado — a rede recorrente
— mostra exatamente onde ele quebra quando a dependência é longa, e chega na atenção de Bahdanau, que é o
mecanismo que faz a representação de uma palavra depender do contexto em volta dela. É de lá que sai o
Transformer, três aulas depois.

> 🗣️ "Hoje cada palavra tem uma linha de matriz e ela é sempre a mesma. A Aula 5 é onde a representação começa a olhar em volta antes de decidir o que ela é."

> **Nota:** Bastidor: não estourar as duas horas. Se o CP4 atrasou, cortar a explicação do PCA × t-SNE do
> slide 9 e proteger este slide: a ponte para a Aula 5 é o que dá sentido ao módulo. Projetar o checklist
> e ficar em silêncio alguns segundos para a turma fotografar. Recolher o pulso da sala: perguntar quem
> chegou ao CP4 e anotar a proporção — se menos da metade chegou, o Lab 2 precisa de menos ambição.
> Lembrar em voz alta onde entregar e que a Aula 5 não tem lab; a leitura é o Bahdanau, arXiv 1409.0473.

---

## Parte 2 — Demonstração guiada

Vinte minutos, no Colab projetado, num notebook em branco. Eu digito — não colo. O objetivo não é
adiantar os checkpoints: é fazer o caminho texto → tokens → vetores inteiro na frente da turma, em poucas
linhas, para que ninguém trave em sintaxe depois. Na V2 a demo tem uma função extra: **os três números
que ela produz são critérios de conclusão dos checkpoints**, e eu anoto os três no quadro.

Insumos preparados na véspera: um parágrafo técnico em português e o equivalente em inglês num arquivo de
texto local, o notebook do aluno já aberto em outra aba, o cache dos quatro tokenizadores quente, e
capturas de tela de cada saída caso a rede caia.

**1.** **[Abro um notebook em branco e mostro o menu de ambiente de execução sem acelerador]** Primeiro eu
quero deixar visível que aqui não tem GPU selecionada. Esse lab é de CPU inteiro. O que vai demorar hoje é
download de tokenizador, não conta de matriz — e é bom vocês verem a diferença entre um lab de CPU e o
Lab 2, na Aula 9, que é o primeiro que pede acelerador de verdade.

**2.** **[Digito `from transformers import AutoTokenizer` e carrego o `gpt2`]** Uma linha para carregar um
tokenizador de produção. Isso que baixou agora é o vocabulário do GPT-2 — o resultado de rodar BPE sobre
um corpus enorme, majoritariamente em inglês. Não é código, é uma tabela de merges aprendida. É o artefato
da Aula 2 baixando na frente de vocês.

**3.** **[Tokenizo uma frase curta em português e imprimo os IDs]** Agora uma frase em português. O que sai
é uma lista de números inteiros, e é literalmente isso que o modelo vê — o modelo nunca viu uma letra na
vida. Só que essa lista de números não me diz nada sobre a decisão que foi tomada. Preciso de outra coisa.

**4.** **[Chamo `convert_ids_to_tokens` e imprimo as peças]** Aqui está a decisão. Olha os pedaços em que a
frase foi partida. Aquele caractere estranho no começo de algumas peças é como o byte-level BPE representa
o espaço — o espaço é parte do token. E olha as palavras em português que viraram três, quatro pedaços.
Cada pedaço é uma posição na sequência, e sequência é custo.

**5.** **[Carrego `neuralmind/bert-base-portuguese-cased` e tokenizo a mesma frase, imprimindo as duas
listas uma sob a outra]** Mesma frase, tokenizador treinado em português. Vou botar as duas listas de
peças uma embaixo da outra na saída, porque é a comparação que vale. Repararam? Onde o GPT-2 fez quatro
pedaços sem sentido, esse aqui fez dois que parecem morfema. Não é que um algoritmo é melhor — é que um
dos vocabulários viu português no treino e o outro não. E tem uma segunda razão, que eu não vou abrir
agora: acento em UTF-8 são dois bytes, e o GPT-2 trabalha em bytes. Está em A ponto um.

**6.** **[Calculo fertilidade das duas na mão, dividindo tokens por palavras separadas por espaço, e
anoto os dois números no quadro]** Contar tokens sozinho não compara nada, porque texto tem tamanhos
diferentes. Então divido: tokens sobre palavras. Isso é fertilidade, e é consumo por quilômetro em vez de
litros no tanque. Vou anotar os dois números aqui no quadro e eles ficam até o fim do próximo checkpoint —
no Checkpoint 1 vocês fazem essa conta para quatro tokenizadores e três textos, e aí a tabela conta a
história.

**7.** **[Chamo `carregar_corpus_pt` do notebook do aluno com poucos milhares de sentenças e mostro qual
fonte respondeu]** Agora eu preciso de corpus para treinar vetores. Essa função tenta três fontes em ordem
e me diz qual funcionou — olha a linha que ela imprimiu. Isso não é frescura de engenharia: rede de
instituição cai, dataset muda de nome, e eu não quero que o lab de vocês morra por causa disso. E se cair
na terceira, que é um mini-corpus embutido, ela avisa em letra maiúscula que os resultados vão ficar ruins
de propósito.

**8.** **[Tokenizo por espaço, treino `Word2Vec(sg=1)` com parâmetros pequenos, cronometro e anoto o tempo
no quadro]** Tokenização boba, por espaço, porque para Word2Vec isso basta. E o treino: skip-gram, cem
dimensões, cinco épocas. Vou cronometrar na frente de vocês. Olha o tempo — e vai para o quadro, ao lado
das fertilidades. Isso é a frase da Aula 3 ficando concreta: embedding é subproduto barato de uma tarefa
que ninguém queria resolver.

**9.** **[Chamo `most_similar` para três palavras — uma frequente, uma de domínio, uma rara]** Três
consultas. A primeira palavra é frequente e os vizinhos fazem sentido. A segunda é de domínio e os
vizinhos são razoáveis. E a terceira — olha o que aconteceu: ou os vizinhos são lixo, ou a palavra nem
está no vocabulário, porque o `min_count` cortou. Esse erro aí é o Checkpoint 4 de vocês inteiro,
antecipado em uma linha. E é a razão de a quarta linha do critério do Checkpoint 3 ser o tamanho do
vocabulário.

**10.** **[Fecho o notebook em branco e volto para o notebook do aluno na célula do Checkpoint 1]** Foi
isso. Vinte linhas para ir de texto a vetor, e três números no quadro. O que vocês vão fazer agora nos
checkpoints é o mesmo caminho com rigor: quatro tokenizadores em vez de dois, corpus paralelo em vez de uma
frase, gráfico com eixo rotulado em vez de `print`, e uma tabela de analogias em que a maioria vai falhar.

> **Nota de contingência:** Bastidor: se a rede cair no passo 2 ou 5, usar as capturas de tela da véspera e
> narrar em cima delas — a demo não pode consumir mais que os vinte minutos, e a turma precisa dos
> sessenta e cinco minutos de checkpoint. Se o `most_similar` do passo 9 devolver vizinhos bons até na
> palavra rara, não fingir que ficou ruim: comentar que o corpus daquela execução foi generoso e que no
> notebook deles pode ser diferente. Se o treino do passo 8 passar de um minuto, interromper e reduzir o
> número de sentenças ao vivo — mostrar que reduzir corpus é uma alavanca legítima. **Os passos
> insubstituíveis são o 6 e o 8:** sem os três números no quadro, o lançamento pelo observável dos CP1 e
> CP3 perde a âncora.

---

## Parte 3 — Hands-on

Sessenta e cinco minutos de trabalho da turma, em quatro checkpoints. Eu circulo a sala o tempo inteiro;
meu papel aqui é destravar erro de execução, não ensinar conceito novo. Cada checkpoint tem um critério de
conclusão observável e eu anuncio o tempo em voz alta na metade e a dois minutos do fim.

Uma regra minha nos quatro: eu anuncio o checkpoint **pelo que a tela vai imprimir**, não pelo que
implementar. Quem sabe o que espera reconhece o fim; quem só sabe o que digitar fica olhando para o código
sem saber se terminou.

**1.** **[Lanço o Checkpoint 1 — quatro tokenizadores, três textos, quinze minutos]** Quinze minutos, e o
alvo são duas coisas na tela: uma tabela de **doze linhas** com a coluna de fertilidade preenchida em
todas, e a decomposição das palavras longas nos quatro vocabulários. Quem terminar a tabela e ficar olhando
para ela sem escrever a interpretação não terminou o checkpoint.

*Bastidor — erros comuns:* (1) esquecer que fertilidade precisa de um contador de palavras — muita gente
imprime só tokens e a tabela não compara nada; a pergunta que resolve é "onde está a sua coluna de
fertilidade?"; (2) usar `tokenizer(texto)` e contar `input_ids` sem notar que o BERT adiciona `[CLS]` e
`[SEP]`, o que infla dois tokens **só nos três tokenizadores que usam token especial** — o viés é
assimétrico e **inverte** a comparação que é o objeto do checkpoint; A.1 tem o número, e vale mencionar em
voz alta quando o primeiro aluno perguntar; (3) o download do `xlm-roberta-base` é o mais pesado dos
quatro e trava alunos com rede ruim, então sugerir começar a tabela com três e completar depois; (4)
esperar que o BERT português ganhe em *todos* os textos — ele não ganha no código nem no inglês, e essa
surpresa é conteúdo, não erro.

*Como recolher:* aos 12 minutos eu peço em voz alta que a tabela esteja impressa. A conclusão observável é
a tabela na tela com as doze linhas e a decomposição da palavra longa. Pergunto para dois ou três alunos,
em voz alta, qual tokenizador ganhou no código — as respostas divergem e essa divergência abre a
questão-guia quatro sem eu precisar explicar nada. E se alguém perguntar por que o código dá números tão
diferentes, eu digo que a própria noção de "palavra" perde sentido ali e que a questão-guia quatro pergunta
pelo **número de tokens**, não pela fertilidade — o motivo está em A.1.

**2.** **[Lanço o Checkpoint 2 — corpus paralelo, razão PT/EN e projeção, quinze minutos]** Quinze
minutos, e o alvo são três blocos na tela mais um parágrafo de três linhas no notebook. Os três blocos: a
razão média com desvio e com o número de pares; a projeção de custo com a constante hipotética; e quantos
pares cabem em oito mil cento e noventa e dois tokens em cada idioma, com a perda. O parágrafo: o que os
números significam e o que eles **não** permitem concluir.

*Bastidor — erros comuns:* (1) o erro central deste checkpoint é **reportar a média das razões como
número de custo**. O notebook imprime as duas médias em células diferentes, e a de custo é a razão dos
totais; quem não percebe que escolheu uma delas não entendeu o que mediu, e vale provocar quem terminar
rápido com exatamente essa pergunta: "qual desses dois números é o da fatura?"; (2) esquecer o desvio e
reportar só a média, o que esconde que alguns pares são muito piores que outros — razão sem desvio e sem
`n` não é número; (3) tratar a constante de preço como preço real — corrigir na hora, em voz alta, para a
sala inteira, porque esse é o tipo de número que vaza para um relatório depois; (4) contar tokens do lado
inglês com tokenizador diferente do lado português, o que invalida a comparação inteira — o notebook
impede isso por construção, mas quem reescreveu o laço reintroduz; (5) escrever a terceira linha da
interpretação como "o corpus é pequeno" e parar aí, sem dizer o que isso implica para a generalização.

*Como recolher:* a conclusão observável é a razão média impressa **junto com o número de pares usados** e
a tabela de projeção preenchida. Aos 13 minutos eu anuncio o intervalo e escrevo o horário de volta no
quadro. Quem não terminou a interpretação escrita termina depois; a medição é o que precisa estar rodada
antes do intervalo. Se sobrar um minuto, eu digo em voz alta a assimetria — trinta e três por cento mais
caro é vinte e cinco por cento menos janela — e remeto a A.2, porque essa é metade da resposta da
questão-guia dois.

**3.** **[Lanço o Checkpoint 3 — Word2Vec skip-gram em português, dezessete minutos]** Dezessete minutos, e
o alvo são quatro linhas na tela: fonte do corpus, número de sentenças, tempo de treino, tamanho do
vocabulário. Mais três `most_similar` comentados. Skip-gram, cem dimensões, janela cinco, `min_count`
cinco, dez negativas, cinco épocas.

*Bastidor — erros comuns:* (1) o import do gensim quebrar com a mensagem sobre `triu` — é o runtime que
não foi reiniciado depois da instalação, e a solução é reiniciar e rodar de novo; mandar para a célula
alternativa com `sklearn` quem já perdeu tempo demais nisso; (2) passar para o `Word2Vec` uma lista de
strings em vez de uma lista de listas de tokens, o que treina caractere por caractere e produz vocabulário
absurdo — o sintoma é vocabulário com poucas dezenas de entradas; (3) escolher três palavras raras e
concluir que o método não funciona, quando o que aconteceu foi `min_count`; (4) corpus grande demais e
treino passando de um minuto — reduzir o número máximo de sentenças; (5) achar que `seed=42` garante
reprodutibilidade, quando `workers=4` torna o treino assíncrono — quem perguntar merece a resposta honesta,
e ela está em A.3.

*Como recolher:* a conclusão observável são as quatro linhas mais as três saídas de `most_similar` com
comentário escrito ao lado. Aos 14 minutos eu pergunto em voz alta quantos ficaram com vocabulário abaixo
de mil palavras — quem levantar a mão caiu no plano C do corpus e precisa saber disso **antes** de
interpretar o Checkpoint 4, porque muda a leitura da tabela de analogias. E se sobrarem dois minutos, eu
mando rodar a célula de treino uma segunda vez sem mudar nada: é a extensão mais barata e mais formativa
do lab.

**4.** **[Lanço o Checkpoint 4 — PCA, t-SNE, vizinhos e analogias, dezoito minutos]** Dezoito minutos, e é
o que fecha o módulo. O alvo são duas coisas no notebook: os dois gráficos com eixo rotulado e legenda por
grupo, e a tabela de quatro a seis analogias com o resultado real de cada uma. Eu repito, porque é o
ponto: analogia que falhou entra na tabela como falha.

*Bastidor — erros comuns:* (1) `perplexity` do t-SNE maior ou igual ao número de amostras — o notebook
calcula um valor seguro, mas quem editou a lista de palavras quebra isso, e o erro do sklearn é claro o
suficiente; (2) escolher palavras que não estão no vocabulário e receber `KeyError` — o notebook filtra,
mas quem reescreveu a lista precisa filtrar de novo; (3) gráfico sem eixo rotulado ou sem legenda, que é
reprovação de forma direta; (4) **ler distância entre aglomerados num t-SNE** — vale interromper a sala uma
vez para dizer isso alto, e a razão está em A.4: a função que o t-SNE minimiza quase não pune inventar
vizinhança; (5) reexecutar o treino várias vezes procurando a analogia que funciona — cortar na hora,
lembrando que a falha explicada vale mais; (6) confundir `não` com `fora do vocab` na coluna de resultado —
o segundo significa que o teste **não rodou**, e A.5 tem a ordem de diagnóstico.

*Como recolher:* aos 01:45 eu anuncio cinco minutos e digo que os dois gráficos salvos já satisfazem
metade do critério. A conclusão observável é o par de gráficos mais a tabela de analogias com resultado
real. Quem terminou vai para as extensões, e eu empurro principalmente a primeira — treinar um BPE próprio
em português com a biblioteca `tokenizers`, vocabulário de oito mil, e comparar a fertilidade com a do
GPT-2 no mesmo texto. Essa extensão é a que **isola** o efeito do corpus dos merges: mesmo algoritmo,
corpus diferente. É o melhor material que alguém pode levar para a discussão da Aula 5, e A.1 explica por
que ela isola.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a matemática por trás
de um checkpoint durante o lab. A regra num laboratório é mais rígida que numa aula teórica — **a bancada
tem prioridade**. Derivação em sala de lab custa minutos de quem está travado numa célula, e esses minutos
não voltam. A resposta padrão é uma frase de leitura conceitual mais o ponteiro para o item do apêndice, e
a conversa continua na mesa de quem perguntou, não para a sala.

> **Nota:** Bastidor: o custo de cada item abaixo sai do tempo de checkpoint, não de um bloco expositivo.
> A única janela realmente barata são os minutos em que o treino do CP3 roda sozinho — dois ou três
> minutos de tempo morto em que a sala está olhando uma barra de progresso. Se a pergunta vier de uma
> pessoa só, a resposta é individual, na mesa dela.

**Item 1 — "Por que a média das razões não é igual à razão dos totais?" (A.2, ~4 min).**
A pergunta mais provável do lab, e a mais valiosa, porque é a questão-guia dois. Se eu decidir gastar os
quatro minutos, o que rende é o **contraexemplo com dois pares**, não a álgebra: escrevo um par com dez
tokens em português e cinco em inglês, e outro com trinta e trinta. A média das razões dá um vírgula
cinco; a razão dos totais dá quarenta sobre trinta e cinco, um vírgula catorze. Dois números, os mesmos
dados. E fecho dizendo qual é o da fatura e por quê: a conta de API soma tokens, então é a razão dos
totais.
**Versão de 30 segundos:** "a razão dos totais é a média das razões **ponderada pelo comprimento** — pares
longos pesam mais. Para dinheiro use a razão dos totais; para caracterizar o tokenizador, a média com
desvio. O contraexemplo com dois pares está em A.2."

**Item 2 — "Por que trinta e três por cento mais caro é vinte e cinco por cento menos janela?" (A.2, ~3 min).**
Barata e satisfatória. Eu escrevo que o custo é proporcional ao número de tokens, então a razão de custo é
a razão de tokens: mais trinta e três por cento. E que a quantidade de conteúdo que cabe numa janela fixa
é proporcional ao **inverso** dos tokens por unidade, então a razão de conteúdo é um sobre um vírgula
trinta e três, que é zero vírgula setenta e cinco — uma perda de vinte e cinco por cento. Duas
consequências, uma razão, formas diferentes.
**Versão de 30 segundos:** "preço escala com tokens, janela escala com o inverso de tokens. Trinta e três
por cento mais caro é `1 − 1/1,33 = 25%` menos conteúdo. A conta está em A.2, e a versão geral está em A.4
da Aula 2."

**Item 3 — "O que exatamente o `negative=10` faz?" (A.3, ~5 min).**
Pergunta legítima no CP3, e a resposta boa é contraintuitiva, então vale fazer se houver janela. Eu digo o
óbvio primeiro — dez negativos por positivo, custo de onze produtos internos em vez de cem mil — e depois
o que quase ninguém sabe: pelo resultado que está em A.4 da Aula 3, no ótimo o produto interno de um par
tende à informação mútua pontual **menos o log de k**. Com k igual a dez, isso é menos dois vírgula três.
Ou seja: `negative` fixa o **limiar de informatividade** a partir do qual um par conta como associação.
Subir k aumenta a exigência.
**Versão de 30 segundos:** "controla duas coisas: o custo, que é `k+1` em vez de `|V|`; e o limiar — o alvo
de todos os pares desce `log k`, então com dez negativos só pares com PMI acima de 2,3 recebem alvo
positivo. Está em A.3."

**Item 4 — "Por que a distância no t-SNE não vale?" (A.4, ~4 min).**
A pergunta mais importante do CP4 e a que eu mais quero que apareça, porque ela corrige o erro de leitura
do lab. Não preciso do quadro: eu projeto o item do apêndice e leio a parcela da divergência. Se dois
pontos são vizinhos no espaço original e ficam longe no gráfico, o custo é alto e o otimizador conserta.
Se dois pontos são distantes no original e ficam perto no gráfico, o custo é multiplicado por uma
probabilidade quase zero — o otimizador não é penalizado. Então quebrar vizinhança é caro e inventar
vizinhança é grátis: local confiável, global não. E a PCA é o contrário, porque projeção ortogonal só
encurta distância.
**Versão de 30 segundos:** "a função que o t-SNE minimiza pune muito quebrar uma vizinhança verdadeira e
quase não pune inventar uma falsa. Então aglomerado significa e distância entre aglomerados não significa.
Na PCA vale o inverso: longe é longe de verdade, perto pode não ser. A tabela de leitura está em A.4."

**Item 5 — "Por que a analogia falhou, se ela funciona no modelo da internet?" (A.5, ~5 min).**
A pergunta que fecha o lab, e se ela vier eu **abro espaço**, tirando dos minutos finais do CP4. Eu conduzo
pelo argumento de sinal contra ruído: o vetor estimado é o verdadeiro mais um erro, o deslocamento da
relação é a diferença dos verdadeiros mais a diferença dos erros, e a analogia sobrevive enquanto a
magnitude da relação for muito maior que o ruído. O ruído cresce quando as contagens caem; a magnitude da
relação não cresce com o corpus. E aí dou as ordens de grandeza: dez à nona palavras no artigo contra dez
à sexta aqui. Três ordens de grandeza.
**Versão de 30 segundos:** "a direção da relação é uma média de estimativas ruidosas, e em corpus pequeno o
ruído fica da ordem do sinal. Antes disso, confiram se a palavra esperada **tem vetor** — `fora do vocab`
não é falha do modelo, é o `min_count`. A tabela de razão × evidência está em A.5."

### Ordem de sacrifício

Se o lab atrasar: o **Checkpoint 4 encolhe primeiro** — os dois gráficos satisfazem metade do critério e a
tabela de analogias vai para casa, o que eu digo explicitamente. Depois encolho a **interpretação escrita
do CP2**, que também termina em casa, desde que a medição esteja rodada antes do intervalo. **Não
sacrifico** o CP1 nem o CP3: o CP1 é a base da tabela que o entregável exige e o CP3 é pré-requisito do
CP4 inteiro. E **não sacrifico** os três números da demo (as duas fertilidades e o tempo de treino): sem
eles, o lançamento pelo observável dos CP1 e CP3 fica sem âncora, e o lab volta a ser "implemente isto".

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 10 da Parte 1 — o inventário do que a turma mediu, o que
entregar, o prazo, o critério de reexecução, o índice do apêndice projetado por vinte segundos com A.2 e
A.5 indicados como as respostas das questões-guia 2 e 3, e a ponte para a Aula 5. O fio a puxar é o mesmo
do `banco` da Aula 3: hoje cada palavra tem uma linha fixa de matriz, e é essa fixidez que a Aula 5 começa
a desmontar.

> 🗣️ "Vocês saem daqui com texto virando número e número virando geometria. O que vocês não têm ainda é uma representação que muda quando o contexto muda — e é exatamente onde a Aula 5 começa."

---

*Roteiro do Instrutor · Aula 4 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
