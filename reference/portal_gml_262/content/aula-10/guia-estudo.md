# Do Transformer ao LLM: escala, MoE, decodificação e prompting

## Slide 1 · Abertura: quatro chamados, um modelo, nenhum bug · 00:00–00:10

Boa noite, pessoal. Hoje eu vou começar de um jeito diferente: com quatro chamados de suporte.

Imaginem que vocês são o time responsável por um sistema com LLM em produção, e nesta semana
chegaram estes quatro na fila. Todos do mesmo modelo. Nenhum deles é bug de código.

Primeiro: "o mesmo prompt responde bem com temperatura zero vírgula sete e devolve lixo com um
vírgula quatro. Ninguém alterou o modelo."

Segundo: "com temperatura zero o modelo entrou em loop — repetiu a mesma frase até bater o
limite de tokens."

Terceiro: "o cartão do modelo diz quarenta e sete bilhões de parâmetros, mas na inferência ele
custa como um de treze bilhões. O número está errado?"

Quarto: "contexto de cento e vinte e oito mil tokens, o documento cabe inteiro, e o modelo
ignora justamente o que está no meio dele."

*[Pausa. Deixo os quatro na tela sem responder nenhum.]*

Nenhum desses quatro se resolve retreinando o modelo. Nenhum é bug. Os quatro têm causa
conhecida, nome próprio e uma conta associada — e as quatro contas são a aula de hoje.

Duas horas atrás vocês estavam terminando o Lab 2, com um Transformer de dois milhões e
setecentos mil parâmetros escrito por vocês. A arquitetura de um modelo de fronteira é a
mesma. O que separa os dois é escala — e um punhado de decisões que acontecem depois que o
treino acabou. O terceiro chamado é sobre escala. Os outros três são sobre decisões.

Aviso de honestidade: esta é a aula mais densa do semestre, e está na ementa com essas
palavras. Amanhã é o Lab 3, e ele existe para consolidar o que a gente vê hoje. Se algo passar
rápido, volta amanhã no teclado de vocês.

> Ideia central: "Quatro defeitos, um modelo, nenhum bug. Todos os quatro são consequências de decisões que alguém tomou e não anotou."

## Slide 2 · O ticket 3: quando o tamanho não prevê o custo · 00:10–00:16

Vou pegar o terceiro chamado primeiro, porque ele é o que abre a primeira metade da aula.

A pessoa que abriu o chamado está certa nas duas metades da frase dela. O modelo **tem**
quarenta e sete bilhões de parâmetros. E ele **custa** como um de treze bilhões por token. As
duas coisas são verdade ao mesmo tempo, e o cartão não está errado.

Isso já é suficiente para matar a métrica que quase todo mundo usa. Contar parâmetros não
prevê custo, não prevê qualidade e não prevê memória. É como medir carro por cilindrada.

O que prevê é um triângulo de três eixos que precisam ser lidos juntos: parâmetros, que é
capacidade; tokens de treino, que é experiência; e computação, que é o produto dos dois com o
tempo de máquina.

Para calibrar: o mini-GPT de vocês tem dois vírgula sete milhões de parâmetros e um megabyte
de corpus. O GPT-3, que é a leitura de hoje, tem cento e setenta e cinco bilhões de parâmetros
e trezentos bilhões de tokens. A razão em parâmetros é da ordem de sessenta e cinco mil vezes,
e mesmo assim "é o mesmo modelo só que maior" é a leitura errada.

A analogia que eu uso é motor, combustível e estrada. Um motor de Fórmula 1 com dois litros de
gasolina não vai longe. Um tanque cheio num cortador de grama também não. E qual a proporção
certa entre motor e combustível é a pergunta que a Aula 12 responde com dado experimental.

> Ideia central: "Um número de parâmetros sozinho não prevê custo nem qualidade. É por isso que o chamado T3 não é erro de cartão."

## Slide 3 · O orçamento em uma linha · 00:16–00:24

Agora a conta que todo mundo que trabalha com isso sabe de cor.

O custo de treinar um modelo denso, em operações de ponto flutuante, é aproximadamente seis
vezes o número de parâmetros vezes o número de tokens de treino. E o custo de gerar **um**
token é aproximadamente dois vezes o número de parâmetros.

*[Leio as duas linhas apontando cada termo.]*

Em português: treinar custa proporcional a capacidade vezes experiência. Gerar um token custa
proporcional só à capacidade que está ativa naquele token — e guardem essa palavra "ativa",
porque ela é a resposta do chamado três, dois slides à frente.

Aplicando no GPT-3: seis vezes um vírgula setenta e cinco vezes dez à décima primeira, vezes
três vezes dez à décima primeira. Dá três vírgula um vezes dez à vigésima terceira FLOPs. E
esse é o número que o próprio artigo reporta. A conta de guardanapo bate com o artigo.

Agora a assimetria, que eu quero na cabeça de vocês porque ela explica a economia inteira
desta área: treinar é caríssimo e acontece **uma vez**. Inferir é barato por token e acontece
um trilhão de vezes. Toda decisão de produto que a gente vai ver no resto do curso mora nessa
assimetria.

E de onde vem o seis? De contar operações por parâmetro e por token: dois no forward, quatro
no backward. A atualização do otimizador não entra nessa contagem, e o motivo é bonito — ela
não escala com o número de tokens. A contagem completa, com a atualização contabilizada e
descartada com justificativa, está em A.1 da Aula 12. Ali essa conta é o objeto; aqui ela é
ferramenta.

> Ideia central: "Uma conta de guardanapo separa o que se paga uma vez do que se paga para sempre — e é a segunda que decide produto."

## Slide 4 · A restrição que virou arquitetura · 00:24–00:31

Uma linha de aritmética que muda a conversa. Cento e setenta e cinco bilhões de parâmetros, em
precisão de dezesseis bits, são dois bytes cada. Trezentos e cinquenta gigabytes. Só os pesos:
sem gradiente, sem estado de otimizador, sem ativação.

Não existe acelerador no mercado que segure isso sozinho. Então o modelo tem que ser fatiado
entre placas só para **existir**, antes de qualquer discussão sobre velocidade.

E aqui está o ponto que eu quero cravar: isso não é problema de infraestrutura, é problema de
arquitetura. Metade das ideias de arquitetura dos últimos cinco anos é resposta a restrição de
memória e de banda, não a restrição de qualidade. Multi-query e grouped-query attention, da
Aula 8, existem para encolher o cache. FlashAttention, que é Aula 12, existe para não escrever
uma matriz na memória lenta. Mixture of Experts, que é o próximo slide, existe para ter mais
parâmetros sem pagar mais computação por token.

Quando alguém disser que arquitetura de rede neural é matemática pura, eu queria que essa
lista viesse à cabeça. É matemática pura rodando em hardware com hierarquia de memória, e o
hardware manda mais do que a gente admite.

> Ideia central: "Trezentos e cinquenta gigabytes só de peso. O modelo não cabe numa placa — e é essa frase que explica metade das arquiteturas modernas."

## Slide 5 · MoE: a peça trocada que fecha o ticket 3 · 00:31–00:42

Voltando ao bloco Transformer que vocês escreveram no Lab 2. Ele tem atenção, normalização,
residual e o feed-forward — aquele `Sequential` de expansão quatro vezes com GELU no meio.

Mixture of Experts troca **uma peça só**: o feed-forward. Atenção, normalização e residual
ficam idênticos. No lugar de um FFN, o bloco passa a ter `E` cópias dele — os experts — mais
uma camada linear pequena chamada roteador, que olha o vetor de cada token e decide para quais
`k` experts aquele token vai.

E daí nasce a distinção que fecha o chamado três: **parâmetros totais** versus **parâmetros
ativos por token**. Total é o que ocupa memória. Ativo é o que custa computação. Num modelo
denso os dois números são iguais; num MoE eles divergem por uma ordem de grandeza ou mais.

Olhem o chamado de novo. Um modelo com oito especialistas e roteamento para dois: quase todos
os parâmetros estão no feed-forward, e ele ativa um quarto deles por token. O cartão diz
quarenta e sete bilhões, que é memória. A conta de inferência usa treze, que é computação. As
duas coisas são verdade, e ninguém errou nada.

*[Marco o ticket 3 como fechado na tela.]*

O Switch Transformer, que é a segunda leitura de hoje, levou isso até um vírgula seis trilhão
de parâmetros totais com roteamento para **um** expert. Um trilhão e meio de parâmetros, custo
por token de um modelo muito menor.

A analogia que funciona é hospital. Sessenta e quatro especialistas na folha de pagamento e
uma triagem na porta. O hospital inteiro custa caro de manter — isso é memória. Cada paciente
vê um médico — isso é computação por token.

E a mecânica do roteador, com dimensões, a renormalização dos gates e a razão de o gate
multiplicar a saída do expert, está em A.4.

> Ideia central: "Ticket 3 fechado: o cartão fala de memória e a fatura fala de computação. Confundir os dois é o erro de leitura mais comum da área."

## Slide 6 · O defeito característico do MoE: ninguém supervisiona o roteador · 00:42–00:55

Agora o problema bonito, e ele é um quinto chamado que eu vou dar de graça — porque é o que
aparece na fila de quem **treina** um MoE, não de quem usa.

Sintoma: o treino roda, a perda desce, e um histograma de carga por especialista mostra três
barras enormes e sessenta rentes ao zero. O modelo ocupa memória de sessenta e quatro
especialistas e usa três.

Por que isso acontece? Porque ninguém ensina o roteador a rotear. Não existe rótulo dizendo
"este token é de matemática, manda para o expert sete". O roteador aprende junto, pelo mesmo
gradiente, e isso fecha um laço quase inevitável: quem recebe mais tokens no começo recebe
mais gradiente, fica melhor mais rápido, e o roteador — que está minimizando a perda — passa a
mandar ainda mais tokens para ele. No limite, três experts fazem tudo e sessenta são peso
morto que ocupa memória e nunca aprendeu nada.

Isso tem nome: colapso de roteamento. É o modo de falha característico de MoE, e é a razão
pela qual a técnica demorou a pegar.

A correção é uma perda auxiliar de balanceamento de carga. Além da perda de linguagem normal,
o treino minimiza um segundo termo que penaliza distribuição desigual, com um peso pequeno.
Para quem não vem de aprendizagem de máquina: uma perda é um número que o treino tenta
diminuir; somar duas perdas é pedir para o treino cuidar de duas coisas ao mesmo tempo, e o
peso diz qual das duas importa mais.

E tem um número dessa perda auxiliar que eu quero que vocês levem, porque ele é o que aparece
no painel de treino: **ela vale um quando a carga está perfeitamente balanceada, e vale `E` no
colapso total.** Então o valor medido é uma leitura direta de desbalanceamento — num modelo de
sessenta e quatro experts, se essa perda estiver em oito, a carga efetiva está concentrada em
cerca de um oitavo deles. Não precisa de gráfico. A conta dos dois casos-limite está em A.4.

Tem um segundo mecanismo, que é de engenharia e não de otimização: o fator de capacidade. Cada
expert tem um teto de tokens por lote, porque a memória é alocada estaticamente. O que passa
do teto é simplesmente descartado — o token segue pela conexão residual sem passar por expert
nenhum. Isso se chama token dropping, e é um dos poucos lugares em aprendizagem profunda onde
a resposta para "e se não couber?" é literalmente "então não processa".

Uma coisa que eu quero clara sobre a perda auxiliar: ela não está lá para melhorar a qualidade
do texto. Ela está lá para o modelo ser **treinável**. A qualidade que ela protege é a dos
experts que, sem ela, nunca receberiam gradiente nenhum.

> Ideia central: "Deixado sozinho, o roteador elege três favoritos e joga o resto do modelo no lixo — e a perda de linguagem não reclama."

## Slide 7 · [Transição] O treino acabou. Alguém ainda precisa escolher o token. · 01:05–01:07

Voltando. Primeira metade da aula: os pesos, e um chamado fechado. Daqui para frente os pesos
estão congelados e eu não vou tocar em nenhum deles.

E mesmo assim eu tenho quatro alavancas que mudam completamente o comportamento do modelo. A
primeira é como eu escolho o próximo token a partir da distribuição — decodificação, e é ela
que responde os chamados um e dois. A segunda é o que eu escrevo no prompt. A terceira é o que
eu ponho no contexto e onde — chamado quatro. E a quarta é como eu sirvo o modelo.

O modelo devolve uma distribuição de probabilidade sobre o vocabulário inteiro. Ele não
devolve texto. Quem transforma distribuição em texto é um algoritmo que **eu** escolho.

> Ideia central: "O modelo não gera texto. Ele gera uma distribuição. Texto é o que o *meu* algoritmo faz com ela."

## Slide 8 · O ticket 2: o modelo que repete a mesma frase para sempre · 01:07–01:12

Chamado dois: com temperatura zero, o modelo entrou em loop.

*[Projeto a saída em loop, com a frase repetida quatro vezes.]*

Deixa eu explicar o que aconteceu, porque a explicação é mais interessante que o bug. Com
temperatura zero, a regra de escolha é `argmax`: a cada passo, o token de maior probabilidade.
Isso é decodificação gulosa, e ela tem duas propriedades boas — é barata e é determinística.
Se vocês precisam de reprodutibilidade, é isso que vocês querem.

Só que ela é **local e determinística**, e as duas coisas juntas produzem exatamente o que
está na tela. Se o estado que condiciona a escolha volta a ser o mesmo, a escolha volta a ser
a mesma, e o ciclo se fecha. Não tem aleatoriedade nenhuma envolvida — é o contrário: é a
ausência total de aleatoriedade que prende o modelo no ciclo. Nada na regra local tem como
perceber que o texto está preso.

E o loop é o sintoma extremo de um problema mais fundo: a sequência formada pelas escolhas
mais prováveis passo a passo **não é**, em geral, a sequência mais provável no total. Um token
com sessenta por cento de probabilidade pode levar a um beco em que toda continuação é ruim,
enquanto um de quarenta por cento abriria um caminho melhor três tokens à frente.

*[Aponto a árvore no slide.]* Esta árvore tem a conta: o ramo de zero vírgula seis leva a duas
continuações de zero vírgula cinco, então zero vírgula trinta. O ramo de zero vírgula quatro
leva a uma de zero vírgula nove: zero vírgula trinta e seis. Greedy pega o primeiro. O melhor
é o segundo.

É descer uma montanha sempre pelo passo mais íngreme disponível. Você chega a **um** vale. Não
necessariamente ao vale — e, no pior caso, anda em círculo dentro dele.

E uma imprecisão que eu ouço muito: dizer que greedy é "temperatura zero". No limite é
verdade, e a derivação desse limite está em A.1. Mas a frase esconde o ponto: o problema de
greedy não é ruído de amostragem. É horizonte. Baixar a temperatura não conserta miopia — só
congela a escolha míope, e é literalmente o que o chamado dois mostra.

*[Marco o ticket 2 como fechado.]*

O escore de sequência escrito, a normalização por comprimento e o exemplo numérico desta
árvore estão em A.3.

> Ideia central: "Ticket 2 fechado: greedy é descer a montanha sempre pelo passo mais íngreme. Você chega a *um* vale — e, no pior caso, anda em círculo dentro dele."

## Slide 9 · Beam search: acerta o alvo errado · 01:12–01:17

A correção óbvia da miopia é não escolher já: manter várias hipóteses vivas. É o beam search.
Ele mantém `B` candidatos, expande todos a cada passo, e fica com os `B` melhores por
probabilidade acumulada. Na árvore do slide anterior, com largura dois, ele acha o caminho de
zero vírgula trinta e seis.

E ele funciona muito bem — em tradução automática, em transcrição de fala, em qualquer tarefa
em que a resposta é essencialmente única. Foi lá que ele nasceu e é lá que ele deve morar.

Em geração aberta ele quebra de dois jeitos, e os dois têm nome.

O primeiro é viés por saídas curtas, e eu tenho o número. A probabilidade de uma sequência é o
produto das probabilidades dos tokens, e todo fator é menor que um. Comparem duas respostas.
Uma resposta genérica de cinco tokens, com zero vírgula sete de probabilidade cada: zero
vírgula sete elevado a cinco é zero vírgula cento e sessenta e oito. Uma resposta boa,
específica, de vinte tokens, com zero vírgula **nove** cada — cada token mais provável que os
da primeira: zero vírgula nove elevado a vinte é zero vírgula cento e vinte e dois.

A pior ganha. Não porque seja melhor em nada, mas porque tem menos fatores. É aritmética. E
existe normalização por comprimento como remendo, com um expoente que se ajusta à mão — e é
exatamente isso que ela é: um remendo com nome de hiperparâmetro. A conta com e sem
normalização está em A.3.

O segundo viés é pior e é mais interessante: viés por saídas genéricas. A sequência de maior
probabilidade sob um modelo de linguagem tende a ser a mais previsível. E o mais previsível é
o mais banal. Se eu pedir a resposta "mais provável" para uma pergunta aberta, o que eu recebo
é o equivalente textual de "depende".

E aqui está a medição que eu acho a mais bonita desta aula: texto humano **não maximiza
probabilidade**. Quando se mede a surpresa de um texto escrito por gente, ela não é mínima —
ela é irregular e claramente diferente de zero. Gente escreve com um nível de imprevisibilidade
estável. Então buscar o máximo de probabilidade é buscar uma coisa que não se parece com
escrita humana.

Isso derruba o pressuposto de que maximizar probabilidade maximiza qualidade. E quando esse
pressuposto cai, a alternativa deixa de ser buscar melhor — passa a ser **amostrar**.

> Ideia central: "Texto humano não é o texto mais provável. Então buscar a saída de máxima probabilidade é buscar uma coisa que não parece escrita por gente."

## Slide 10 · O ticket 1: a mesma configuração que funciona e não funciona · 01:17–01:23

Chamado um: o mesmo prompt responde bem com zero vírgula sete e devolve lixo com um vírgula
quatro.

Amostrar é sortear o próximo token pela distribuição em vez de pegar o máximo. E aí eu ganho
um botão para controlar quanta aleatoriedade eu quero, que é a temperatura. A conta é uma
linha: divide os logits por `T` antes do softmax.

Com `T` menor que um, a distribuição fica mais concentrada. Com `T` maior que um, achata. `T`
tendendo a zero recupera greedy — e portanto o chamado dois. `T` tendendo a infinito vai para
o uniforme sobre o vocabulário **inteiro**, inclusive tokens de controle e fragmentos de
subpalavra, e é por isso que temperatura muito alta não produz texto criativo: produz ruído.

Um detalhe de implementação que é erro clássico: a divisão acontece **nos logits**, antes do
softmax. Dividir a probabilidade depois do softmax não é a mesma operação — e o que ela faz é
mais engraçado do que estar errada: ela devolve a distribuição original, para qualquer `T`. O
parâmetro simplesmente não faz nada, e o código não reclama. A conta de três linhas que mostra
isso está em A.1, e vocês vão encontrar esse erro amanhã no Checkpoint 1.

E agora deixa eu desarmar a frase que todo mundo repete: "temperatura alta deixa o modelo mais
criativo". O que temperatura alta faz é transferir massa de probabilidade para a cauda da
distribuição. Acontece que a cauda contém, ao mesmo tempo, as escolhas interessantes e as
escolhas erradas. Não existe botão que separe as duas. Temperatura não é controle de
criatividade — é controle de **variância**, e a variância vem com o pacote completo.

Então o chamado um está resolvido, e a resposta é constrangedora: ninguém mexeu no modelo.
Alguém aumentou a variância e chamou isso de criatividade.

*[Marco o ticket 1 como fechado.]*

Última coisa, e é a que eu quero apontada com o dedo: olhem os quatro painéis. A **ordem** dos
candidatos é idêntica nos quatro. Temperatura não muda quem é o mais provável — muda o quanto
ele é mais provável. A demonstração de que o ranking é preservado está em A.1, e ela cabe em
três linhas.

> Ideia central: "Ticket 1 fechado: ninguém mexeu no modelo. Alguém aumentou a variância e chamou isso de criatividade."

## Slide 11 · [Exercício] Qual botão, e que evidência confirma · 01:23–01:31

Antes de soltar vocês, a régua de que vocês vão precisar, em duas linhas.

Temperatura sozinha tem um problema: mesmo com `T` baixo, a cauda continua tendo probabilidade
não nula, e amostragem repetida acaba pegando lixo. Então se trunca a distribuição antes de
sortear, e existem dois jeitos.

Top-k mantém os `k` tokens mais prováveis e renormaliza. O problema é que `k` é fixo e a
distribuição não é: numa posição em que o modelo está seguro, `k` igual a cinquenta admite
quarenta e nove candidatos ruins; numa posição genuinamente aberta, corta material bom.

Top-p, ou nucleus, muda o critério: mantém o **menor conjunto cuja probabilidade acumulada
atinge `p`**, e renormaliza. O tamanho passa a ser adaptativo. Top-k é cota fixa de
convidados; top-p é encher a sala até noventa por cento da lotação — quantas pessoas cabem
depende do tamanho delas.

E uma coisa que vale meia hora de depuração de vocês: truncar não é só cortar, é cortar **e
renormalizar**. Quem esquece a renormalização não zera nada — o vetor passa a somar menos que
um e o sorteio fica enviesado em silêncio.

Agora oito minutos, em dupla. Três chamados novos, e para cada um eu quero duas coisas: qual
parâmetro mexer, e **que medição confirmaria** o diagnóstico.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> Ideia central: "Top-k corta por posição. Top-p corta por massa. E como a distribuição muda a cada token, cortar por massa é a única das duas que se adapta."

## Slide 12 · [Demo] Uma distribuição, seis algoritmos · 01:31–01:38

Deixa eu mostrar tudo isso funcionando em números, com um script que roda em qualquer máquina,
sem rede e sem GPU.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> Ideia central: "Mesma distribuição, seis algoritmos, seis comportamentos completamente diferentes. E nenhum peso foi tocado."

## Slide 13 · Prompting e aprendizado em contexto · 01:38–01:43

Segunda alavanca sem tocar nos pesos: o que eu escrevo no prompt.

Zero-shot é descrever a tarefa em palavras. Few-shot é colocar exemplos já resolvidos dentro
do próprio prompt, antes da pergunta de verdade. E o que o GPT-3 mostrou — que é a leitura de
hoje — é que, acima de certa escala, o modelo resolve tarefas novas só de ver esses exemplos,
sem nenhuma atualização de peso. Isso ganhou o nome de aprendizado em contexto.

Eu tenho um problema com esse nome e vou ser explícito: nada é aprendido. Fechada a janela de
contexto, não sobrou nada. O peso é exatamente o mesmo que era antes. Few-shot não é aula — é
crachá. Você não ensinou nada ao modelo; você disse a ele em que papel ele está e qual é o
formato da resposta.

E tem um resultado da literatura que reforça isso e muda a prática: boa parte do ganho de
few-shot vem do **formato** e do espaço de rótulos apresentados, não do mapeamento correto
entre entrada e saída dos exemplos. Isso muda como se escolhe exemplo: cobrir bem o espaço de
rótulos e a formatação importa tanto quanto acertar cada exemplo.

Chain-of-thought é o caso particular em que eu peço os passos intermediários antes da resposta.
A intuição é direta: gerar mais tokens antes de responder é gastar mais computação naquela
resposta, e problemas de várias etapas se beneficiam. Hoje é visão inicial — a Aula 16 volta
com modelos treinados especificamente para isso.

E amanhã vocês descobrem quanto o chain-of-thought custa em token de saída, com número de
vocês. Adianto que a conta interessante não é o custo por resposta: é o custo por **acerto**,
e o CoT muda o denominador dessa conta. Está em A.2 do lab.

> Ideia central: "Aprendizado em contexto é um nome ruim. Nada foi aprendido — fechou a janela, não sobrou nada. Few-shot não é aula, é crachá."

## Slide 14 · O ticket 4: o documento cabe e não é lido · 01:43–01:46

Chamado quatro, o último: janela de cento e vinte e oito mil tokens, o documento cabe inteiro,
e o modelo ignora o que está no meio.

Terceira alavanca: o que entra no contexto — e **onde** dentro dele.

Janela grande garante que o texto **cabe**. Ela não garante que o texto seja **usado**.

O teste que popularizou isso se chama needle in a haystack: enfia-se uma frase-alvo num ponto
arbitrário de um contexto longo e pede-se que o modelo a recupere. O resultado típico é
sensibilidade posicional — a recuperação é boa quando a agulha está no começo ou no fim, e
pior quando ela está no meio. Que é exatamente o chamado.

*[Marco o ticket 4 como fechado.]*

A consequência de engenharia é a que interessa para o resto do curso: janela grande não
dispensa recuperação. É o oposto. Se a posição dentro do contexto muda o resultado, colocar
pouco e relevante vence colocar tudo. E isso é literalmente um dos argumentos que sustentam
RAG, que é o Módulo 5, Aulas 18 e 19.

> Ideia central: "Ticket 4 fechado: ter o livro na mochila não é lembrar o que está na página trezentos e quarenta."

## Slide 15 · Serving: três gargalos, três respostas · 01:46–01:50

Quarta e última alavanca, e essa é sobre servir. Quatro minutos, visão geral — cada um destes
assuntos é uma disciplina inteira em outro lugar.

Primeiro, KV cache. Lá na Aula 6, quando a gente montou a atenção, eu apontei um desperdício:
gerar o token número mil recalcula chaves e valores dos novecentos e noventa e nove anteriores,
que não mudaram. A solução é óbvia depois de dita — guardar K e V de cada camada. É memoização.

O preço é memória, e a conta é feia. Num modelo de sete bilhões com trinta e duas camadas,
trinta e duas cabeças e dimensão cento e vinte e oito, em dezesseis bits, o cache custa da
ordem de meio megabyte **por token de contexto**. Oito mil tokens são quatro gigabytes — por
sequência. E aqui está o número que eu quero que vocês levem: os pesos desse modelo ocupam
catorze gigabytes, então com cerca de vinte e oito mil tokens de cache no total o cache
**empata com o modelo inteiro**. Vinte e oito usuários com mil tokens cada. É a conta que
está em A.6, e ela é a razão de MQA e GQA existirem.

Segundo, paged attention. Se o cache é o recurso escasso, o problema vira alocação de memória —
e a solução veio direto de sistemas operacionais: aloca-se o cache em blocos de tamanho fixo
com uma tabela de páginas, em vez de reservar contiguamente o pior caso de comprimento. Acaba
a fragmentação, e prefixos compartilhados entre requisições podem apontar para as mesmas
páginas.

Terceiro, decodificação especulativa. O gargalo da geração é ser sequencial. Então usa-se um
modelo rascunho, pequeno e rápido, para propor `γ` tokens de uma vez; o modelo grande verifica
os `γ` em **um** forward paralelo e aceita o maior prefixo compatível. E o ponto que eu quero
cravar: com o esquema de aceitação correto, a distribuição de saída é **idêntica** à do modelo
grande sozinho. Não é aproximação.

O número concreto, porque ele justifica a complexidade: com razão de aceitação zero vírgula
oito e quatro tokens propostos por rodada, saem em média três vírgula trinta e seis tokens por
verificação. Descontando o custo do rascunho, dá quase três vezes mais rápido. A aritmética
completa, com o teto e com o caso em que a especulativa fica **mais lenta**, está em A.5.

> Ideia central: "Decodificação especulativa não aproxima nada. A saída é exatamente a distribuição do modelo grande — o que se comprou foi paralelismo, não qualidade descontada."

## Slide 16 · Fechamento: quatro tickets, nenhum peso tocado · 01:50–02:00

Deixa eu fechar voltando aos quatro chamados com que eu abri.

*[Projeto os quatro, agora com a causa ao lado.]*

Chamado um, a qualidade que desaba entre zero vírgula sete e um vírgula quatro: temperatura
move variância, não criatividade, e a cauda vem inteira. A conta está em A.1.

Chamado dois, o loop em temperatura zero: `argmax` é uma regra local e determinística, e a
sequência das escolhas mais prováveis não é a sequência mais provável. A.3.

Chamado três, os quarenta e sete bilhões que custam como treze: parâmetros totais são memória,
parâmetros ativos são computação, e num MoE os dois números divergem. A.4.

Chamado quatro, a janela de cento e vinte e oito mil com o meio ignorado: caber não é ser
usado, e a posição dentro do contexto muda o resultado.

Nenhum dos quatro era bug. Nenhum se resolvia retreinando. Os quatro eram decisões.

E é essa a síntese da aula. A primeira metade foi escala: um triângulo de parâmetros, tokens e
computação, com a conta `C ≈ 6ND` fechando o orçamento; uma restrição de memória tão dura que
virou arquitetura; e Mixture of Experts como a resposta que separa totais de ativos, ao custo
de um roteador que colapsa se ninguém segurar.

A segunda metade foi quatro alavancas que mudam o comportamento com os pesos congelados.
Decodificação, prompting, contexto e serving.

A frase que eu quero que fique é essa: um modelo de linguagem em produção não é um arquivo de
pesos. É um arquivo de pesos mais um punhado de decisões, e essas decisões mudam qualidade,
custo e latência em ordens de grandeza. Quem só sabe treinar sabe metade.

Amanhã é o Lab 3, e ele existe para consolidar exatamente isso — mas medindo. Vocês vão variar
temperatura e top-p e comparar saída; rodar greedy contra amostragem; fazer few-shot numa
tarefa de classificação e chain-of-thought em matemática; contar quanto cada abordagem custa
em tokens; e comparar um modelo pequeno local com um modelo de API. O entregável é o notebook
mais um mini-relatório de qualidade contra custo contra latência.

Duas coisas para hoje à noite. As leituras: GPT-3, do Brown, com a pergunta de o que
exatamente aumenta com o número de exemplos no prompt se nenhum peso mudou; e Switch
Transformers, do Fedus, com a pergunta de por que rotear para um expert só. E o setup do lab:
chave de um provedor com free tier e o Ollama instalado com um modelo pequeno baixado.

> Ideia central: "Um LLM em produção não é um arquivo de pesos. É um arquivo de pesos mais um punhado de decisões — e essas decisões movem qualidade, custo e latência em ordem de grandeza."

---

## Parte 2 — Demonstração guiada

Sete minutos, script `codigo/demo-decodificacao.py`, Python puro, sem dependência externa, sem
rede e sem GPU. A escolha é deliberada: esta aula é longa demais para gastar três minutos com
quota de API, e a matemática de decodificação não precisa de modelo de verdade para ser vista —
precisa de uma distribuição e de um terminal.

O script embute duas distribuições de próximo token, uma concentrada e uma achatada, e a árvore
de probabilidades do slide 8. Tudo o que aparece na tela é conta feita na hora.

**1.** **[Rodo `python demo-decodificacao.py` e paro no primeiro bloco]** Isto aqui é uma
distribuição de próximo token com dez candidatos, ordenada, com um histograma em ASCII do lado.
Olha o formato: dois ou três candidatos dominam e existe uma cauda longa de coisas improváveis
mas não impossíveis. Esse formato é a razão de existir de tudo o que vem a seguir.

**2.** **[Mostro o bloco de temperatura com T = 0,2 · 0,7 · 1,0 · 1,5 lado a lado]** Quatro
temperaturas, mesma distribuição de partida. Em zero vírgula dois, o primeiro candidato come
quase tudo. Em um vírgula cinco, as barras ficam quase do mesmo tamanho. E a coisa que eu
aponto com o dedo: a **ordem** dos candidatos é idêntica nas quatro colunas. Temperatura não
muda quem é o mais provável — muda o quanto ele é mais provável. Isso é o chamado um na tela.

**3.** **[Mostro o bloco de top-k com k = 3]** Top-k igual a três. Sobraram os três primeiros,
e o script imprime a renormalização: as probabilidades foram divididas pela soma dos três para
voltar a somar um. Olha o que aconteceu com o terceiro colocado — ele tinha zero vírgula quinze
e agora tem zero vírgula vinte e um. Quarenta e um por cento mais provável do que era, e nada
mudou no modelo. Truncar não é só cortar: é redistribuir.

**4.** **[Mostro o bloco de top-p com p = 0,9 nas duas distribuições]** Agora o argumento
inteiro a favor do nucleus, e este é o passo insubstituível da demo. Na distribuição
concentrada, top-p de zero vírgula nove fecha o conjunto com pouquíssimos tokens. Na
distribuição achatada — mesma linha de código, mesmo parâmetro — o conjunto explode. O `k`
fixo não teria feito isso: ele teria cortado material bom no segundo caso ou admitido lixo no
primeiro. É o mesmo parâmetro se comportando diferente porque a distribuição é diferente — e é
a resposta do terceiro chamado do exercício, medida.

**5.** **[Rodo o bloco de busca sobre a árvore embutida]** Aqui está a árvore que eu desenhei
no quadro no slide 8. O script roda busca gulosa e busca em feixe com largura três e imprime a
probabilidade conjunta de cada caminho. E olha o resultado: o beam encontra a sequência de
maior probabilidade conjunta, que é a curta e genérica. Ele fez o trabalho dele corretamente. O
problema é que o trabalho dele não é o que eu queria.

**6.** **[Rodo o bloco de amostragem cinco vezes com semente fixa e depois greedy cinco vezes]**
Últimos trinta segundos. Cinco amostragens: cinco saídas diferentes. Cinco decodificações
gulosas: cinco saídas idênticas. É a mesma distribuição nos dois casos. Reprodutibilidade e
diversidade são a mesma escolha vista de dois lados, e escolher uma custa a outra.

**7.** **[Volto ao topo do arquivo e mostro as constantes de configuração]** E eu fecho onde eu
quero que o Lab 3 comece: essas quatro constantes no topo do arquivo são as quatro alavancas da
aula. Este script está na pasta da aula e é o ponto de partida de amanhã — o notebook do lab faz
exatamente isso, mas com um modelo de verdade do outro lado e com medição de tokens e de
latência.

---

## Parte 3 — Hands-on

Cinco minutos de dupla, três de correção, dentro do slide 11. O exercício da V1 era calcular o
nucleus à mão; ele virou extensão opcional, e o obrigatório passou a ser decisão: qual botão
mexer, e que evidência confirma.

**1.** **[Projeto os três chamados e formo as duplas]** Cinco minutos, em dupla. Três chamados
novos, e para cada um eu quero duas coisas: qual parâmetro vocês mexem, e **que medição
confirmaria** que o diagnóstico está certo. A segunda parte é a que vale.

Os três chamados:

1. Um resumidor devolve texto correto e chatíssimo, sempre com a mesma estrutura de frase.
   Configuração atual: `T = 0,3`, `top_p = 1,0`.
2. Um gerador de descrições de produto acerta nove de dez e na décima inventa um atributo que
   não existe. Configuração atual: `T = 1,3`, `top_p = 1,0`.
3. Um time subiu `T` de um vírgula zero para dois vírgula zero e o `top_p = 0,9` "parou de
   cortar". Ninguém mexeu no `top_p`.

*Como recolher:* três minutos, e começo pelo terceiro chamado, não pelo primeiro. Peço uma
dupla que respondeu "cresce" e uma que respondeu "encolhe" e deixo as duas defenderem trinta
segundos cada. Depois dou o número: no exemplo de A.2, o nucleus vai de seis tokens em `T = 1`
para oito em `T = 2`, e cai para três em `T = 0,5`. Fecho apontando a consequência prática, que
é o que vai para o lab: temperatura e top-p **não** são controles independentes — mexer num muda
o efeito do outro, e é por isso que amanhã eles vão varrer os dois numa grade em vez de ajustar
um de cada vez.

*Extensão para quem terminar antes (opcional):* refazer a conta do nucleus à mão seguindo A.2,
com a distribuição de dez candidatos, em `T = 1` e `T = 2`. É o exercício que na V1 era
obrigatório e aqui vira aprofundamento — e o gabarito está no apêndice, completo.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a derivação
em aula. A regra geral é remeter ao apêndice e seguir; conduzir uma derivação só se sobrar
tempo, e anunciando que é conteúdo de consulta.

**Item 1 — "De onde vem o seis do `C ≈ 6ND`?" (A.1 da Aula 12, ~4 min).**
Pergunta boa e barata. Eu escrevo no quadro: no forward, cada parâmetro participa de uma
multiplicação e uma soma por token, dois FLOPs. No backward, preciso do gradiente em relação à
entrada e em relação ao peso, o que dá o dobro: quatro. Dois mais quatro, seis. E se
perguntarem da atualização do otimizador — que é a pergunta boa —, a resposta é que ela custa
por **parâmetro e por passo**, não por token, então ela não escala com `D` e sai da conta.
Escrevo essa razão e paro. A derivação completa é da Aula 12 de propósito.

**Item 2 — "Por que a sequência das escolhas mais prováveis não é a mais provável?" (A.3, ~5 min).**
A pergunta mais provável do Bloco 2. Eu faço no quadro a árvore do slide 8 com os três números,
calculo as duas conjuntas — zero vírgula trinta contra zero vírgula trinta e seis — e paro. Se
sobrar tempo dentro dos cinco minutos, acrescento a conta do viés por comprimento: zero vírgula
sete elevado a cinco contra zero vírgula nove elevado a vinte, e mostro que a pior ganha. Essas
duas contas juntas são A.3 inteiro em versão falada; a normalização por comprimento eu remeto.

**Item 3 — "Como a perda auxiliar do MoE sabe que está desbalanceado?" (A.4, ~6 min).**
É a mais caro da lista e a que eu mais gosto. Eu escrevo `L_aux = α·E·Σ f_i·P_i`, digo o que é
cada um — fração de tokens roteados e probabilidade média do roteador —, e faço os dois
casos-limite: com carga uniforme, cada termo é um sobre `E` ao quadrado, a soma é um sobre `E`,
vezes `E` dá um. Com colapso total, a soma é um, vezes `E` dá `E`. Escrevo "um no equilíbrio,
`E` no colapso" e paro. Se não houver os seis minutos, a versão de dez segundos é exatamente
essa última frase, e ela já é útil sozinha.

**Item 4 — "Por que a especulativa não muda a distribuição?" (A.5, ~5 min).**
Raramente perguntam, e quando perguntam vale. Eu escrevo a probabilidade de emitir um token
como a soma de dois casos — aceito e rejeitado — e mostro que o primeiro termo dá
`min(p, q)` e o segundo completa exatamente o que falta, `max(0, p − q)`, somando `p`. Três
linhas. Se não houver tempo, a resposta curta é: "a verificação é uma amostragem por rejeição
com distribuição residual construída de propósito para fechar a conta, e a prova de três linhas
está em A.5".

**Item 5 — "Quanto o KV cache custa mesmo?" (A.6, ~3 min).**
A mais barata das cinco, e ela produz um número que impressiona. Escrevo `2 · L · H_kv · d_h ·
b`, instancio com trinta e dois, trinta e dois, cento e vinte e oito e dois bytes, chego em meio
megabyte por token, multiplico por oito mil e comparo com os catorze gigabytes de peso. A frase
que fica: com vinte e oito mil tokens de cache no total, o cache empata com o modelo. O resto —
o efeito de GQA e o argumento de paged attention — está em A.6.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 16 da Parte 1 — os quatro chamados fechados com
a causa nomeada, a síntese das duas metades da aula, a frase de que um LLM em produção é pesos
mais decisões, o mapa do Lab 3 de amanhã, as duas leituras com pergunta dirigida e o checklist
de setup.

> Ideia central: "Eu abri com quatro defeitos e nenhum deles estava nos pesos. Amanhã, no Lab 3, vocês puxam as quatro alavancas — e medem o que cada uma custa em qualidade, em token e em milissegundo."

---

*Roteiro do Instrutor · Aula 10 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
