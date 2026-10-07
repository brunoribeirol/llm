---
aula: 5
titulo: "Modelos sequenciais e o nascimento da atenção"
tipo: teorica
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 5 de 30 (V2)

## Como usar este roteiro

A prosa deste documento é **fala em primeira pessoa**: é o que eu digo em sala, na ordem em
que digo. Não é resumo do conteúdo — é o texto falado.

As linhas marcadas com 🗣️ são as **frases-âncora**: as que eu cravo, quase palavra por
palavra. As notas marcadas com **Bastidor** são operacionais e **não são faladas em voz
alta**.

> **O que muda nesta versão.** A aula é conduzida pelos sintomas: abro por uma curva de
> qualidade que cai com o comprimento da frase, uso três defeitos observáveis para chegar à
> arquitetura, e a derivação fica no apêndice do deck (A.1 a A.6). Eu **não** derivo no
> quadro. Se a turma pedir, a **Parte 4** deste roteiro tem a condução pronta, com o tempo
> que cada derivação consome e o que sacrificar em troca.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · O sintoma: a tradução que piora com o comprimento · 00:00–00:05

Boa noite, pessoal. Vou começar por um defeito, e não por uma arquitetura.

No Lab 1, vocês fecharam o caminho texto → token → vetor e viram o limite do embedding
estático: `banco` recebia o mesmo vetor em frases diferentes. Hoje a frase entra de verdade
na computação. A pergunta muda: como carregar contexto ao longo de uma sequência — e o que
essa escolha cobra em memória, treinamento e hardware?

Imaginem um tradutor automático de 2014, desses que já funcionavam bem o suficiente para ir
para produção. Ele traduz "o gato dorme" impecavelmente. Aí eu dou uma frase de quarenta
palavras, com o sujeito no começo e o verbo principal no fim, e ele desmonta: perde o final,
ou perde o começo, ou troca quem concorda com quem.

Isso sozinho seria anedota. O que transforma em diagnóstico é a curva que está no slide. No
eixo horizontal, o comprimento da frase de origem. No vertical, a qualidade da tradução
medida. E a forma é o que interessa: plana até uns trinta, e daí em diante caindo — e
continuando a cair. O erro não é aleatório. Ele é **função do comprimento da entrada**.

Quando o erro acompanha o comprimento, a arquitetura vira uma suspeita forte — mas ainda não
é um diagnóstico fechado. Poucos exemplos longos no treino também produziriam uma curva
parecida. O que convence no artigo é a comparação controlada: mesmo conjunto de dados e mesmo
procedimento de treino, modelo básico contra modelo com atenção. A diferença acompanha a
arquitetura.

> 🗣️ "Uma curva não fecha o diagnóstico. Ela aponta a suspeita — e o experimento comparativo decide."

> **Nota:** Bastidor: a figura é a Figura 2 de Bahdanau et al. (1409.0473) e ela volta na
> Medição 3 da demo. Abrir pela curva e **não** nomear seq2seq ainda — o nome só vale a pena
> depois que a turma quiser saber o que produz uma curva com essa forma.

### Slide 2 · Por que a intuição sozinha erra aqui · 00:05–00:10

Antes de eu contar a resposta, deixa eu gastar a resposta errada, porque ela é a primeira
que vem à cabeça de todo mundo — inclusive à minha.

O modelo comprime a frase inteira num resumo interno. Se ele erra em frases longas, a
intuição diz: o resumo é pequeno demais, então é só aumentar. Faz sentido e pode ajudar. Mas
isso compra **espaço**; não compra o direito de consultar novamente as posições da entrada,
nem encurta o caminho que a informação percorre.

O limite estrutural continua: existe **um** resumo, de tamanho fixo, para uma entrada de
tamanho variável — e, depois de formado, ele é tudo o que sobra para o decoder. Aumentar o
vetor desloca um limite de capacidade; não transforma memória em consulta.

A segunda intuição errada é "treina mais". Essa eu vou desmontar no slide quatro, porque ela
esbarra numa coisa mais interessante: existe um sinal de treino que simplesmente não chega
aonde precisa chegar.

A analogia que eu vou usar a aula inteira: é a diferença entre uma prova de memória e uma
prova com consulta. O conteúdo é o mesmo. O que muda é o direito de olhar a fonte na hora de
responder.

> 🗣️ "Falta acesso, não espaço. Comprar um caderno maior não resolve um problema de não poder olhar a fonte."

> **Nota:** Bastidor: se alguém da turma propuser "aumentar o vetor" espontaneamente aqui, é o
> melhor cenário — usar a proposta da pessoa e responder com a curva deslocada. Vale muito
> mais do que eu antecipar a objeção sozinho.

### Slide 3 · O conceito em uso: ler em ordem e carregar um resumo · 00:10–00:16

Então vamos olhar a arquitetura que produz essa curva. Ela dominou a área de 1990 a 2016 e é
mais simples que a fama dela.

A ideia é ler em ordem. Um token por vez, e carregando comigo um único vetor de estado que
resume tudo o que já passou. A regra está no slide, e ela é uma linha:

`h_t = f(h_(t-1), x_t)`, que na forma clássica é `h_t = tanh(W_h h_(t-1) + W_x x_t + b)`.

Três leituras dessa linha. Primeira: `h_t` é o resumo comprimido de tudo o que veio antes.
Segunda, e é a economia da coisa: é a **mesma** matriz aplicada em todos os passos. Cinco
tokens ou quinhentos, o número de parâmetros é igual; muda só quantas vezes eu aplico a
função. Para quem programa, isso é um `reduce`: `h` é o acumulador, `x_t` é o elemento, e a
função de combinação foi aprendida em vez de escrita por mim.

Terceira leitura, e essa é a que a turma costuma entender errado, então eu cravo: a rede
**não guarda** os tokens anteriores em lugar nenhum. Ela guarda um vetor de tamanho fixo que
foi sobrescrito a cada passo. O token de dez posições atrás só existe na medida em que
sobreviveu a dez sobrescritas.

> 🗣️ "É um `reduce` sobre a frase, com a função de combinação aprendida. Só isso. O resto da aula é consequência."

> **Nota:** Bastidor: desenhar a rede desenrolada no quadro **antes** de a fórmula aparecer —
> quatro caixas em linha, a seta horizontal do estado, as setas verticais dos tokens. Quem
> não tem ML entende o desenho e reconhece a fórmula depois, nunca o contrário. O
> desenrolamento escrito, a contagem de parâmetros e a prova de que a ordem importa estão em
> A.1; eu não vou ao quadro com nada disso.

### Slide 4 · Sintoma 2: o modelo que esquece o sujeito · 00:16–00:23

Segundo sintoma, e ele é mais específico do que "o modelo esquece".

O padrão que se observa é este: o modelo acerta a concordância entre palavras vizinhas, e
**nunca** aprende a concordância entre palavras separadas por quarenta posições. Não é que
erre de vez em quando — é que aquela dependência nunca entra. E enquanto isso a loss desce
bonito, sem `NaN`, sem divergência, sem nada no log.

Pausa de base, porque eu não vou assumir que todo mundo já fez Aprendizagem de Máquina. A
*loss* é um número que mede o erro do modelo. O gradiente diz em que direção e com que força
cada peso deve mudar para reduzir esse erro. Retropropagação é o procedimento que leva esse
sinal do fim do cálculo para o começo usando a regra da cadeia.

Numa RNN, esse caminho de volta atravessa um fator por passo. Em muitas direções, multiplicar
muitos fatores atenua o sinal; em outras, pode amplificá-lo. O comportamento exato depende
dos pesos e das ativações, mas a dependência exponencial do número de passos é o problema.

Deixa eu fazer a conta aqui na calculadora, na frente de vocês, porque número na lousa vale
mais que a palavra "exponencial". Zero vírgula nove elevado a dez: zero vírgula trinta e
cinco, ainda dá para trabalhar. A cinquenta: cinco milésimos. A cem: três vezes dez elevado
a menos cinco. E do outro lado, um vírgula um elevado a cinquenta já é cento e dezessete, e a
cem passa de treze mil.

Agora o ponto que muita gente mistura: capacidade e otimização são perguntas diferentes.
Mantido o ganho por passo, aumentar só a dimensão não remove o expoente `T`. Um modelo maior
pode ter mais capacidade e continuar sem receber sinal útil nos primeiros passos. A solução
precisa mexer no **caminho** do gradiente.

> 🗣️ "A rede consegue representar a dependência longa. O que ela não consegue é aprendê-la — o sinal de treino morre no caminho de volta."

> **Nota:** Bastidor: **não** escrever a regra da cadeia no quadro. Na V1 eu abria por ela e
> perdia a turma sem ML nos primeiros dois minutos. Agora a ordem é sintoma → número na
> calculadora → nome do fundamento, e a álgebra completa, com a norma do produto e o papel da
> `tanh`, está em A.2. Quem pedir a conta: Medição 1 da demo, que mostra o produto acontecendo
> em NumPy. Se insistirem na álgebra: Parte 4, item 1.

### Slide 5 · Sintoma 3: a GPU que fica ociosa · 00:23–00:28

Terceiro sintoma, e esse é econômico — é o que decidiu a história da área.

O cenário: o treino leva horas, o time compra uma GPU quatro vezes mais rápida, e o tempo por
época cai quinze por cento. Quinze. E a utilização da placa, se alguém for medir, fica baixa
o tempo inteiro.

A causa está numa palavra da fórmula do slide três: `h_t` **exige** `h_(t-1)`. Exige. Não é
preferência de implementação, é a definição da arquitetura. Então o treino tem `T` etapas
obrigatoriamente sequenciais, e não existe quantidade de núcleos paralelos que compre tempo
aqui. É uma linha de montagem com uma estação só: comprar dez fábricas não acelera um carro
que precisa passar por quinhentos postos em ordem.

E deixa eu ser preciso sobre a confusão que sempre aparece aqui: essa dívida é no **treino**,
não na geração. Gerar texto é sequencial em qualquer arquitetura, inclusive no Transformer —
a palavra `n+1` depende da palavra `n` em todo mundo. O que a recorrência impede é o
paralelismo no treino, onde a frase inteira já é conhecida de antemão e poderia ser
processada de uma vez.

> 🗣️ "O que matou a recorrência não foi qualidade. Foi ela não deixar você gastar dinheiro para ir mais rápido."

> **Nota:** Bastidor: se a turma tem gente de infraestrutura, é aqui que ela entra na aula —
> vale deixar a pergunta acontecer. Este sintoma é o que motiva economicamente as Aulas 6 a 8,
> e a Aula 6 vai comprar exatamente esse paralelismo pagando com memória.

### Slide 6 · O que o gating do LSTM compra · 00:28–00:34

A resposta de 1997 para o segundo sintoma é o LSTM, e o que ela tem de bom cabe num sinal de
mais.

A ideia: além do estado que já existia, uma segunda memória — a célula, `c_t` — e três
válvulas aprendidas que decidem o que fazer com ela. Está no slide, em duas linhas. As
válvulas são sigmoides, e é por isso que elas funcionam como válvula: a saída fica entre zero
e um, então zero fecha e um deixa passar inteiro. Uma decide o que apagar, outra o que
escrever, a terceira o que exportar.

E agora a linha que importa mais que todas: `c_t = f_t ⊙ c_(t-1) + i_t ⊙ g_t`. O **sinal de
mais**. A célula nova é a célula velha, filtrada, mais o que entrou de novo. Isso significa
que existe um caminho de `c_(t-1)` até `c_t` que não passa por multiplicação de matriz — e
como o gradiente volta pelo mesmo caminho por onde a informação foi, ele ganhou uma rodovia
aditiva para atravessar quinhentos passos.

Agora a parte que a V1 desta aula não dizia com clareza, e eu quero dizer: o LSTM **não
resolveu** o desaparecimento do gradiente. Quando as válvulas fecham, o decaimento volta
inteiro. O que ele fez foi tirar o problema das mãos da álgebra e pôr nas mãos da rede — que
agora pode decidir manter a porta aberta nos canais em que a dependência longa importa. Isso
é enorme e é diferente de resolver.

Minha analogia: a rede simples reescreve o caderno inteiro a cada página. O LSTM tem um
caderno de anotações e três decisões por página — o que rasurar, o que anotar de novo, o que
mostrar para fora.

E um alerta que eu vou repetir na aula que vem sobre cabeças de atenção, então já fica
plantado: as portas não são regras programadas. Ninguém escreveu "esta porta guarda o
sujeito". São camadas densas com sigmoide, treinadas pelo gradiente da tarefa final.

E deixa eu fechar a dívida que ficou da Aula 3. Lembram do `banco`? Em 2018, o ELMo
popularizou representações em que o vetor de cada palavra é construído a partir dos estados
de LSTMs nos dois sentidos. O vetor de `banco` muda com a frase. **Sem atenção.**

Isso separa duas ideias que parecem sinônimas e não são. Contextualizar é fazer a
representação depender da frase; uma RNN já faz isso. Atender é dar ao passo atual acesso
ponderado a um conjunto de estados. Bahdanau vai acrescentar esse acesso, mas ainda com RNNs
dos dois lados. Só o Transformer vai retirar a recorrência e liberar paralelismo no treino.

> 🗣️ "O LSTM não resolveu o gradiente. Ele deu à rede o poder de decidir quando não estragá-lo."

> 🗣️ "Contextualizar, consultar e paralelizar são três coisas diferentes. Hoje a gente separa as três."

> **Nota:** Bastidor: **não** escrever as seis equações no quadro. Elas estão em A.3, completas
> — com a derivada do caminho da célula, a premissa sob a qual ela vale e o truque de
> inicializar o viés da porta de esquecimento em 1. É mais LSTM do que a V1 tinha. Se pedirem:
> Parte 4, item 2.

### Slide 7 · O placar das três dívidas · 00:34–00:38

Quatro minutos para o slide mais importante do primeiro bloco, que é o placar.

O LSTM funcionou. Tradução comercial de 2015, reconhecimento de fala, autocompletar de
teclado — tudo isso era LSTM. Então por que a área abandonou em dois anos? Porque sobraram
três dívidas, e o veredito de cada uma é diferente.

Dívida um, dependência longa: **aliviada**. Melhorou muito, não acabou. O token 1 e o token
500 continuam separados por 499 passos de computação.

Dívida dois, gradiente: **contida**. Recorte de gradiente segura o lado que explode, e o lado
que desaparece ficou sob a mão da rede. É engenharia de contenção.

Dívida três, paralelismo: **intacta**. Nada do que o LSTM faz muda o fato de `h_t` exigir
`h_(t-1)`. Ela não foi nem discutida — e é ela que quebra a arquitetura.

Guardem o placar. Daqui a pouco eu volto a ele com uma quarta coluna: a atenção de Bahdanau
remove o resumo fixo e cria acesso curto, mas deixa essa terceira dívida intacta. A Aula 6 é
que muda o veredito do paralelismo.

> 🗣️ "Duas dívidas foram renegociadas. A terceira não foi nem discutida — e é ela que quebra a arquitetura."

> **Nota:** Bastidor: se o tempo estourou no Bloco 1, cortar detalhe do LSTM — nunca este
> slide. As três dívidas são o enunciado do problema que as Aulas 6, 7 e 8 respondem, e o
> aluno que sai sem elas decora o Transformer em vez de entendê-lo.

### Slide 8 · Onde memória e acesso se concentram · 00:38–00:43

Agora eu monto a arquitetura concreta onde as três se encontram, porque é dela que sai a
curva com que eu abri a aula. Tradução automática, 2014.

Duas redes. A primeira, o encoder, lê a frase em português inteira e não produz saída nenhuma
— só atualiza o estado dela, palavra por palavra. Quando a frase acaba, eu pego o último
estado e chamo de `c`. A segunda rede, o decoder, começa a partir de `c` e escreve a frase em
inglês, uma palavra por vez.

`c = h_T`. Está no slide, e é a linha que define o problema. O significado inteiro da origem
— cinco palavras ou cinquenta — tem que caber num vetor de dimensão fixa. E o decoder, dali
para frente, **não tem mais acesso à frase de origem**.

Olha o que se encontra nessa ponte. Primeiro, memória: a capacidade de `c` é constante
enquanto a entrada cresce. Segundo, acesso: a posição `j` só influencia a saída depois de
atravessar uma cadeia longa até `c` e depois o decoder. A terceira dívida, o paralelismo, não
mora no vetor `c`; ela atravessa os dois blocos porque ambos são recorrentes. Essa distinção
vai impedir a gente de atribuir à atenção de 2014 um ganho que só aparece em 2017.

> 🗣️ "A curva com que eu abri a aula é o retrato de um vetor de tamanho fixo tentando carregar uma entrada de tamanho variável."

> **Nota:** Bastidor: desenhar as duas redes no quadro com o `c` no meio e **circular o `c` com
> força** — a demo existe para destruir esse círculo. Deixar o desenho de pé até o slide 10. O
> argumento formal (contagem de bits, o comprimento `n*` a partir do qual duas frases colidem
> no mesmo `c`, e o comprimento do caminho) está em A.4.

### Slide 9 · [Demo] Medir os três sintomas · 00:43–00:55

Chega de afirmação. Doze minutos medindo.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> 🗣️ "Nenhuma das três medições é ilustração. As três são a evidência dos slides que eu acabei de dar."

> **Nota:** Bastidor: a Medição 2 — a compressão em quatro números — é a que **não** se corta,
> porque é a única que a turma produz com as próprias mãos. Se o tempo apertar, a Medição 1
> vira leitura da saída salva. Intervalo de 10 min depois deste slide: anunciar a duração e
> cumprir, porque o Bloco 2 é o coração da aula.

### Slide 10 · Acesso em vez de compressão · 01:05–01:17

Voltando. O desenho do seq2seq ainda está no quadro com o `c` circulado. Agora eu apago
aquele círculo.

Bahdanau, Cho e Bengio, 2014. O artigo muda **uma** coisa, pequena de escrever e enorme de
consequência: em vez de um `c` para a frase toda, existe um `c_t` para cada passo do decoder.

As três linhas estão no slide e eu vou ler cada uma, sem mexer em nenhuma.

Primeira: `e_(t,j) = vᵀ tanh(W s_(t-1) + U h_j)`. Isso **compara**. De um lado, onde eu estou
na tradução; do outro, o que tem na posição `j` da origem. O resultado é um número: quão
relevante é aquela posição para o que eu estou escrevendo agora.

Segunda: `α_(t,j) = exp(e_(t,j)) / Σ_k exp(e_(t,k))`. Isso transforma comparações em
**orçamento**. Os pesos ficam positivos e somam um. Cada palavra que o decoder vai escrever
ganha cem por cento de atenção para distribuir sobre as posições da origem.

Terceira: `c_t = Σ_j α_(t,j) h_j`. Isso **lê** a origem segundo aquele orçamento. Média
ponderada de todos os estados do encoder. Nenhum é escolhido de verdade, nenhum é descartado
de verdade.

E agora a consequência que resolve o gargalo do slide 1: depois que os estados `h_j` existem,
o decoder alcança qualquer um deles por uma aresta de atenção. O caminho de `h_j` ao contexto
do passo `t` tem comprimento **um**. Não é que a ponte ficou maior. Os estados do encoder
ficam todos na mesa, disponíveis, e o modelo aprende como ponderá-los.

Um cuidado, porque a turma sempre extrapola: em 2014 isso **não** substitui a recorrência. Os
`h_j` continuam saindo de uma RNN, um por posição, sequencialmente. A atenção aqui é acessório
da recorrência. O caminho de `x_j` até `h_j` e a produção dos estados do decoder ainda têm
passos recorrentes. A tese de que atenção basta para retirar a recorrência é de 2017.

> 🗣️ "Prova de memória contra prova com consulta. O conteúdo é o mesmo; o que muda é o direito de olhar a fonte na hora de responder."

> **Nota:** Bastidor: ler as três linhas apontando cada termo e **não derivar**. A derivação
> completa, com exemplo numérico e com a demonstração de que `c_t` é combinação convexa dos
> `h_j`, está em A.5 — e é mais detalhada do que o que eu fazia no quadro na V1. Se perguntarem
> "não fica caro?": sim, `n` comparações por passo, e é esse custo que vira `O(n²)` na Aula 6.
> Marcar a pergunta e devolver lá.

### Slide 11 · A evidência: uma legenda que ninguém escreveu · 01:17–01:28

Agora o resultado mais bonito do artigo, e ele é um efeito colateral.

Se eu empilho os vetores de peso de todos os passos, eu tenho uma matriz: cada linha é um
passo da geração, cada coluna é uma posição da origem, e cada linha soma um. Projetada como
mapa de calor, aparece uma diagonal — e uma diagonal num mapa de calor de tradução é um
alinhamento de palavras. É a Figura 3 do artigo, que está aqui na tela.

Olha a diagonal quebrando naquele bloco. Aquilo é um grupo nominal cuja ordem inverte entre
as duas línguas. O modelo aprendeu a atravessar em bloco: ele não traduz na ordem, ele sabe
voltar.

E aqui está o ponto que vale a aula inteira, então eu vou dizer devagar: **em nenhum momento
alguém deu rótulo de alinhamento para esse modelo**. O único sinal de treino foi a tradução
correta. O alinhamento apareceu porque era o caminho mais barato para acertar a tradução. É
uma legenda que ninguém escreveu.

E um cuidado de rigor, que volta na Aula 6 e na Aula 27: peso alto não é explicação causal. É
tentador ler a matriz como "ele traduziu assim porque olhou ali", e isso é uma inferência mais
forte do que o dado permite. Os autores foram cuidadosos e chamaram o resultado de alinhamento
*suave* — suave porque cada palavra de destino se liga a uma distribuição sobre as de origem,
nunca a uma só.

> 🗣️ "Ninguém ensinou alinhamento a esse modelo. Ele foi treinado para traduzir, e o alinhamento apareceu porque era o caminho mais barato para traduzir bem."

> **Nota:** Bastidor: 30 s de silêncio com a Figura 3 na tela antes de comentar — a turma
> precisa olhar a imagem. Se perguntarem "isso é interpretabilidade?", responder: é uma janela,
> não uma explicação, e a diferença é assunto da Aula 27.

### Slide 12 · Q, K, V: três papéis antes de três matrizes · 01:28–01:39

Agora eu reescrevo aquelas três linhas com outros nomes, e é a reescrita mais importante do
módulo. É por causa dela que esta aula existe antes da próxima.

O que a atenção faz tem a forma de uma **busca**. Existe uma consulta, existem itens
indexados, existe conteúdo devolvido. Se eu nomear os papéis com cuidado, a consulta é
`q_t = W_s s_(t-1)`, a parte transformada do estado do decoder. A chave de cada posição é
`k_j = U_h h_j`, a parte transformada do estado do encoder que entra na comparação. E o
valor é `v_j = h_j`, o conteúdo que entra na média ponderada.

Comparando com o dicionário que vocês usam em Python: em `d[k]` a comparação é igualdade
exata, o resultado é um item, e chave errada dá erro. Na atenção, a comparação é uma **função
aprendida** que devolve um número contínuo, e o resultado nunca é um item: é uma mistura de
todos, ponderada. Busca por relevância, não busca por chave.

O detalhe importante é mais sutil do que “K e V são iguais”. Os dois **partem** de `h_j`,
mas a chave passa por `U_h` dentro do score, enquanto o valor entra como `h_j` na soma. A
notação Q/K/V ainda é uma leitura funcional. Na aula seguinte ela vira três projeções
matriciais explícitas e um produto `QKᵀ`.

Duas perguntas ficam abertas. E se as projeções de query, key e value fossem explícitas e o
score aditivo virasse um produto interno calculado como matriz? E, mais radical: e se as
queries viessem da **própria sequência de entrada**, cada token consultando os outros da mesma
frase, sem uma RNN produzindo os estados? Essa segunda pergunta tem nome: self-attention.

> 🗣️ "Q, K e V começam como três papéis. No Transformer, eles viram três projeções explícitas da mesma entrada."

> **Nota:** Bastidor: escrever `Q`, `K`, `V` no quadro ao lado das três linhas do slide 10 e
> ligar com setas — a turma precisa ver o mapeamento, não ouvir. A passagem formal até
> `softmax(QKᵀ/√d_k)V`, com a tabela de correspondência e o que cada troca compra, está em
> A.6. Se o tempo estourou, o exercício do slide 13 encolhe; este slide não.

### Slide 13 · [Exercício] Diagnosticar, não calcular · 01:39–01:50

Oito minutos, em dupla. Três sintomas, e para cada um eu quero a causa e a evidência.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> 🗣️ "Nenhuma das três se resolve calculando. As três se resolvem sabendo o que a arquitetura descarta."

### Slide 14 · Fechamento: se a atenção dá acesso, para que serve a recorrência? · 01:50–02:00

Deixa eu juntar as peças e deixar vocês com uma pergunta na cabeça até quinta.

A gente começou com uma curva: qualidade que cai com o comprimento da frase. Atrás dela tinha
uma arquitetura que lê em ordem e carrega um resumo. O LSTM melhora memória e gradiente, mas
continua sequencial. No seq2seq básico, memória e acesso ainda apertam num vetor fixo. A
atenção de Bahdanau ataca **esse** ponto: troca compressão por acesso, produz um contexto por
passo e revela um alinhamento que ninguém supervisionou. O que ela não faz é retirar as RNNs.

Agora a pergunta que eu quero deixar com vocês, e ela é séria: se a atenção já dá ao decoder
acesso direto a qualquer posição da entrada, **para que ainda serve a recorrência?** Qual é o
trabalho que ela está fazendo ali que a atenção não faria? Em 2017, três anos depois de
Bahdanau, um grupo respondeu "nenhum" e escreveu um artigo cujo título é exatamente essa
resposta.

É a próxima aula. E vocês vão reconhecer as três linhas de hoje lá dentro, em outra ordem,
com outros nomes, e sem uma única recorrência.

Para casa, duas coisas. A leitura é Bahdanau, Cho e Bengio, arXiv 1409.0473, seções 1 a 3 e a
discussão da Figura 3 — e a pergunta dirigida é por que a Figura 3 é evidência de um
alinhamento aprendido **sem rótulo de alinhamento**. A segunda são cinco linhas sobre o que se
ganha ao transformar os papéis de query, key e value em projeções explícitas e fazer as
queries nascerem da própria sequência. Quem escrever essas cinco linhas já entrou na aula
que vem.

> 🗣️ "Em 2017 alguém respondeu 'para nada' — e o título do artigo é a resposta."

> **Nota:** Bastidor: **não** responder a pergunta — a tensão é o que faz a turma chegar na
> Aula 6 com apetite. Mostrar o apêndice projetado por 30 s antes de encerrar: seis itens, e
> mais matemática do que a V1 tinha no fluxo. Quem quiser rigor tem para onde ir. Acabar
> 02:00.

---

## Parte 2 — Demonstração guiada

Doze minutos, três medições. Duas rodam em NumPy puro, uma é de quadro. Nenhuma delas depende
de rede, e a essencial funciona com giz e nada mais. Na V2 a demo deixa de ilustrar a
arquitetura e passa a ser a **evidência** dos slides 4, 8 e 1 — nessa ordem.

Insumos preparados na véspera: as doze linhas da Medição 1 salvas num arquivo e já rodadas,
com a saída em texto; a frase longa escrita num papel na minha mão, para eu não improvisar no
quadro; e as Figuras 2 e 3 do paper de Bahdanau baixadas localmente.

### Medição 1 — o produto que decide o gradiente (3 min)

**1.** **[Abro `codigo/demo-gradiente-rnn.py`]** Isto aqui não é uma rede neural. É um caso
controlado que isola o produto repetido no caminho do gradiente. Eu uso uma transformação
diagonal `ganho · I` para que a norma depois de `T` passos seja exatamente `ganho^T`:

```python
import numpy as np
d = 32
for ganho in (0.9, 1.1):
    W = ganho * np.eye(d)
    for T in (10, 50, 200):
        J = np.eye(d)
        for _ in range(T):
            J = J @ W
        print(f"ganho={ganho}  T={T:3d}  norma={np.linalg.norm(J, 2):.3e}")
```

**2.** **[Rodo e leio a coluna da direita]** Ganho zero vírgula nove: `3,49·10⁻¹` em dez
passos, `5,15·10⁻³` em cinquenta, `7,06·10⁻¹⁰` em duzentos. Ganho um vírgula um:
`2,59`, `1,17·10²`, `1,90·10⁸`. São cerca de dezoito ordens de grandeza de diferença no fim,
com a mesma dimensão.

**3.** **[Volto ao slide 4]** Isto não prova que toda RNN terá exatamente esses números; numa
rede real, pesos e derivadas mudam a cada passo. O experimento isola a mecânica: um ganho
moderadamente diferente de um, repetido muitas vezes, muda a escala exponencialmente. E
reparem no que eu **não** mudei: a dimensão é 32 nas duas rodadas.

### Medição 2 — a compressão em quatro números (5 min)

**4.** **[Escrevo no quadro a frase longa que eu preparei]** Vou escrever uma frase aqui.
Comprida de propósito, com o sujeito no começo, o verbo principal no fim e duas orações
encaixadas no meio. Alguma coisa do tipo "A pesquisadora que orientou os três alunos que
publicaram o artigo sobre tradução automática no ano passado defendeu a tese em dezembro."

**5.** **[Proponho a tarefa de compressão e recolho propostas]** Essa frase inteira tem que
caber em **quatro números inteiros**. Quatro. O critério é de vocês — quantidade de palavras,
código de tema, qualquer esquema. Quem me dá quatro números? Vou anotar duas ou três propostas
aqui do lado.

**6.** **[Apago a frase e deixo só os quatro números]** Agora eu apago a frase. Sumiu. Ficaram
os quatro números de vocês, e eu vou pedir a tradução da frase para o inglês usando **só** o
que sobrou no quadro.

**7.** **[Espero a turma tentar e nomeio o que se perdeu]** Dá para recuperar o tema — tem
alguma coisa de pesquisa, de artigo, de tese. E não dá para recuperar quem era o sujeito, o
que concorda com o quê, qual oração estava encaixada em qual, nem a ordem em que as coisas
aconteceram. Essa é a parte que virou zero.

**8.** **[Volto ao desenho do seq2seq e aponto o `c` circulado]** Isso tem nome e o nome está
no meu desenho: `c = h_T`. A diferença entre vocês e o modelo é que vocês tinham quatro
números e ele tem mil — o que muda a escala do problema e não muda a natureza dele. E existe
um comprimento a partir do qual duas frases diferentes colidem no mesmo vetor
necessariamente; a conta está em A.4, para quem quiser.

### Medição 3 — a curva e a matriz (4 min)

**9.** **[Projeto a Figura 2 do paper]** Esta é a curva com que eu abri a aula, agora com as
duas arquiteturas juntas. A do modelo com vetor de contexto fixo cai a partir de umas trinta
palavras e continua caindo. A do modelo com atenção fica plana até o fim do eixo. Mesma
tarefa, mesmos dados, mesma família de rede recorrente por baixo. A única diferença é o acesso.

**10.** **[Projeto a Figura 3 e fico em silêncio alguns segundos]** E este é o efeito
colateral. Cada linha é uma palavra que o modelo escreveu, cada coluna é uma palavra da
origem, o brilho é o peso, e cada linha soma um. Olha a diagonal.

**11.** **[Aponto o bloco onde a diagonal se quebra]** E aqui, onde ela se rompe e atravessa em
bloco: um grupo nominal cuja ordem inverte entre as línguas. O modelo aprendeu a voltar. É o
oposto exato dos quatro números.

> **Nota de contingência:** Bastidor: se o Python não subir, a saída da Medição 1 está salva em
> texto e a leitura dos números preserva o argumento inteiro. Se o projetor falhar, a Medição 3
> vira desenho à mão com um par curto PT→EN reservado, uma grade 5×5 com bolinhas de tamanhos
> diferentes. Os passos 4 a 8 não dependem de tela nenhuma e são a parte pedagogicamente
> essencial: se tudo falhar, fazer só eles. Se ninguém propuser números no passo 5, proponho eu
> mesmo um esquema qualquer — o ponto não é o esquema, é a perda.

---

## Parte 3 — Hands-on

Oito minutos de dupla, três de correção. O exercício da V1 era desenhar a grade de alinhamento
com lápis e papel; ele virou extensão opcional, e o obrigatório passou a ser diagnóstico —
porque o que a prova e o Lab 2 cobram é reconhecer a causa de um comportamento, não preencher
uma grade.

**1.** **[Projeto os três sintomas e formo as duplas]** Oito minutos, em dupla. Três situações,
e para cada uma eu quero duas coisas: a causa provável e **que evidência confirmaria**. A
segunda parte é a que vale.

Os três sintomas:

1. Um tradutor acerta manchetes e desmonta em parágrafos. O erro cresce com o comprimento, e a
   primeira coisa a quebrar é a concordância entre partes distantes. O treino já contém
   exemplos longos em quantidade comparável.
2. Um modelo recorrente acerta a concordância entre palavras vizinhas e **nunca** aprende a
   concordância entre palavras separadas por quarenta posições. A loss desce, não há `NaN`, e
   aumentar a dimensão do estado não mudou nada.
3. Um time trocou a GPU por outra quatro vezes mais rápida e o tempo por época caiu 15%. Mesmo
   modelo, mesmos dados, mesmo tamanho de lote; o profiler mostra uma cadeia de operações
   pequenas, cada uma esperando a anterior.

*Bastidor — respostas e erros comuns:* (1) vetor de contexto fixo, falta de acesso; a evidência
é plotar qualidade contra comprimento e ver a queda, e comparar com um modelo com atenção — a
curva plana é a confirmação. O erro comum é dizer "faltou dado de frase longa", que é
plausível e se descarta treinando com frases longas e vendo a curva continuar caindo. (2)
gradiente que desaparece; a evidência é medir a norma do gradiente que chega aos primeiros
passos, ou rodar a Medição 1 com a escala estimada da matriz; a correção mexe no caminho
(gating, ou atenção), não no tamanho. O erro comum é insistir em capacidade — e o enunciado já
diz que aumentar a dimensão não mudou nada, o que é a pista. (3) o gargalo é sequencial; a
evidência é medir a ocupação da GPU e o tempo por passo contra o comprimento da sequência — se
o tempo cresce linearmente com o comprimento e a placa fica ociosa, é dependência de dados, não
falta de FLOPs. O erro comum é culpar o carregamento de dados, hipótese honesta que se descarta
medindo a mesma coisa.

*Como recolher:* três minutos. Peço uma dupla para o sintoma 1 e forço a segunda parte — "como
você confirmaria?". Corrijo o 2 rápido, porque é o que sustenta a Aula 6. E uso o tempo que
sobrar no 3, ligando com o custo que a Aula 6 vai pagar. Fecho com: "reparem que nenhum dos
três pedia conta, e os três pediam saber o que a arquitetura descarta".

*Extensão para quem terminar antes (opcional):* desenhar a grade de alinhamento de um par
PT→EN com inversão de ordem — linhas somando 1, ao menos uma linha com peso repartido — e
calcular um `c_t` a partir de três scores dados, seguindo A.5. É o exercício que na V1 era
obrigatório e aqui vira aprofundamento.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a derivação
em aula. A regra geral é remeter ao apêndice e seguir; conduzir uma derivação só se sobrar
tempo, e anunciando que é conteúdo de consulta.

> **Nota:** Bastidor: o custo de cada item abaixo sai do bloco em que ele acontece. A ordem de
> preferência para sacrificar, se for preciso: primeiro a Medição 3 da demo (as figuras
> sustentam-se projetadas, sem narração longa), depois o slide 11 reduzido a 5 min, e só então
> o exercício de diagnóstico. O que **não** se sacrifica: os slides 7, 10 e 12.

### "De onde vem esse produto que some?" → **A.2** · 6 min no quadro

A pergunta mais provável do Bloco 1. Eu escrevo a regra da cadeia ao longo do tempo em uma
linha, mostro que a derivada de um passo é uma matriz diagonal vezes a **mesma** `W_h` em todo
passo, e concluo que a norma do produto é limitada por uma base elevada a `T−1`. Três linhas.
Fecho com os números da calculadora, que eles já viram.

**Versão de 30 segundos:** “O sinal de treino atravessa um fator por passo. Repetir um ganho
um pouco menor que 1 o apaga; repetir um ganho um pouco maior o explode. A.2 mostra a regra da
cadeia e a Medição 1 isola o efeito.”

### "Escreve o LSTM inteiro?" → **A.3** · 7 min no quadro

Custa caro e raramente compensa em aula. Se eu fizer, escrevo as seis equações e derivo só a
linha da célula, mostrando que o fator que se propaga é `diag(f_t)` — diagonal e dependente do
dado, contra a matriz cheia e fixa da rede simples. O ponto que vale o tempo é o produto das
portas de esquecimento: se `f = 0.5`, `0.5^20` já é `10⁻⁶`, e é daí que sai o truque de
inicializar o viés da porta em 1.

**Versão de 30 segundos:** “A equação decisiva é `c_t = f_t⊙c_(t-1) + i_t⊙g_t`: o sinal de
mais cria um caminho direto, e `f_t` decide quanto desse caminho permanece aberto. As seis
equações e a ressalva sobre caminhos indiretos estão em A.3.”

### "Por que aumentar o vetor não basta?" → **A.4** · 5 min no quadro

Vale fazer com a premissa explícita. Eu digo que a contagem de bits é um experimento mental
sob precisão finita e não uma prova de que toda frase precisa de um código exclusivo. Ela
mostra que a capacidade é limitada; não explica sozinha a queda observada. O argumento mais
forte é o comprimento do caminho: aumentar `d` não encurta uma única aresta entre a posição
antiga e a saída. A.4 traz os dois argumentos e os limites de cada um.

**Versão de 30 segundos:** “Um vetor maior compra capacidade. Ele não devolve ao decoder o
direito de consultar a entrada nem encurta o caminho da informação. A.4 separa formalmente
espaço de acesso.”

### "Calcula um `c_t` no quadro?" → **A.5** · 4 min no quadro

Barato e convence. Três scores — 2, 1 e meio —, as três exponenciais, a soma, os três pesos:
0.63, 0.23 e 0.14. Depois eu dobro os três scores e refaço: o peso máximo salta de 0.63 para
0.84 sem que a ordem tenha mudado. É a amplificação do softmax medida em dois minutos, e é
exatamente o que vai justificar o `√d_k` na aula que vem. Se eu tiver que escolher um item
desta parte para fazer, é este.

**Versão de 30 segundos:** “O softmax transforma scores em pesos positivos que somam 1; o
contexto é a média ponderada dos estados. A.5 resolve `e=(2,1,0,5)` e mostra por que mudar a
escala torna a distribuição mais concentrada.”

### "Qual é a ponte de Bahdanau até `softmax(QKᵀ/√d_k)V`?" → **A.6** · 6 min no quadro

Eu escrevo a forma genérica da atenção e separo papéis de fórmulas. Em Bahdanau,
`q_t = W_s s_(t-1)`, `k_j = U_h h_j`, `v_j = h_j`, com score
`v_aᵀ tanh(q_t + k_j)`. No Transformer, Q/K/V viram projeções explícitas, o score vira produto
interno escalado e todas as queries podem ser calculadas em matriz. É uma passagem entre duas
instâncias da mesma família, não uma igualdade literal. A tabela completa está em A.6.

**Versão de 30 segundos:** “Os dois mecanismos comparam uma consulta com posições e misturam
valores. Bahdanau usa score aditivo entre estados recorrentes; o Transformer usa projeções
Q/K/V e produto interno matricial. Mesma família de operação, instâncias diferentes.”

### Ordem de sacrifício

Se a aula atrasar, corto primeiro a narração longa da Medição 3, depois reduzo o slide 11 a
cinco minutos e, só então, encurto a correção do exercício. **Não corto** o placar do slide 7,
a distinção “acesso sem paralelismo” do slide 10 nem o mapeamento cuidadoso do slide 12.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 14 da Parte 1 — a síntese dos quatro elos
(curva → três dívidas → vetor fixo → acesso), a pergunta aberta sobre para que serve a
recorrência, a ponte para a Aula 6 e as duas tarefas da semana.

> 🗣️ "Hoje a gente trocou compressão por acesso e ganhou o alinhamento de graça. Quinta a gente joga a recorrência fora e descobre que não precisava dela."

---

*Roteiro do Instrutor · Aula 5 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
