# Laboratório 2: Mini-GPT do zero em PyTorch

## Slide 1 · Abertura: hoje vocês constroem a coisa · 00:00–00:05

Boa noite, pessoal. Hoje é o dia que eu prometi na primeira aula.

Nas últimas quatro aulas a gente fez um caminho longo. Na Aula 5 eu mostrei a RNN e o gargalo do vetor de contexto fixo. Na Aula 6 a gente pegou `softmax(QKᵀ/√d_k)V` e usou ela para explicar três defeitos reais de modelo. Na Aula 7 a gente montou o bloco moderno — pré-norm, residual, feed-forward. E na Aula 8 eu argumentei que a família decoder-only venceu porque o objetivo é o mais simples que existe e o sinal de treino é o mais denso: cada posição da sequência é um exemplo supervisionado de graça.

Isso tudo foi slide. Hoje vira código, e vira código escrito por vocês, não copiado de biblioteca. Em duas horas vocês vão ter um Transformer decoder-only funcionando, treinado, gerando texto, com perplexidade medida. Dois milhões e setecentos mil parâmetros que vocês montaram na unha.

Uma nota rápida sobre este deck, e depois eu não falo mais disso: ele tem um apêndice, com cinco itens, um por checkpoint. É a conta por trás de cada coisa que vocês vão digitar hoje. Ninguém precisa disso para fazer o lab. Todo mundo vai querer isso quando for escrever as respostas das questões-guia.

> Ideia central: "Até agora vocês acreditaram na fórmula porque eu escrevi ela no quadro. Depois de hoje vocês vão saber que ela funciona, porque foram vocês que digitaram."

## Slide 2 · Setup e os números deste lab · 00:05–00:11

Antes de qualquer coisa, os números — porque eu quero que ninguém passe a aula com medo de estourar quota ou queimar a GPU.

O modelo tem seis camadas, seis cabeças, dimensão de embedding cento e noventa e dois, e contexto de cento e vinte e oito caracteres. Isso dá da ordem de dois milhões e setecentos mil parâmetros. O corpus tem cerca de um megabyte, ou seja, um milhão de caracteres, e a tokenização é em nível de caractere: o vocabulário são os noventa e poucos símbolos distintos que aparecem no texto. O treino são dois mil passos com lote de sessenta e quatro, e isso leva da ordem de três a cinco minutos na T4 do free tier.

Três a cinco minutos. Não é hora, não é noite inteira. Foi dimensionado assim de propósito, porque um lab em que o treino demora quarenta minutos é um lab em que vocês não experimentam nada.

E esse dois vírgula sete milhões não é chute meu. Cada bloco custa doze vezes a dimensão ao quadrado em parâmetros, e a distribuição dentro do bloco surpreende: dois terços estão no feed-forward, não na atenção. A atenção é a estrela conceitual e a minoria numérica. A conta inteira, até o número que vai aparecer na tela de vocês no Checkpoint 3, está no apêndice A.3.

E para quem não pegar GPU hoje — vai acontecer com alguém, o free tier é o free tier — tem uma variante CPU na célula de configuração: dimensão noventa e seis, quatro camadas, contexto sessenta e quatro, quinhentos passos. Roda em poucos minutos no processador e serve para os cinco checkpoints. A comparação do último checkpoint continua valendo, porque ela é interna: vocês comparam suas execuções entre si, não com o vizinho.

> Ideia central: "Dois milhões e setecentos mil parâmetros, um megabyte de corpus, três a cinco minutos de treino. Este lab foi dimensionado para vocês experimentarem, não para esperarem."

## Slide 3 · O mapa: cinco checkpoints e o entregável · 00:11–00:15

Deixa eu desenhar o mapa das próximas duas horas, porque a pior coisa num lab é não saber onde a gente está.

Cinco checkpoints, e eu vou apresentar cada um pelo que ele imprime na tela quando está certo — porque é assim que vocês vão saber que terminaram, e não pela sensação de ter terminado.

O primeiro é a atenção causal: quando estiver certo, a célula do teste imprime `Checkpoint 1 OK`, e cada linha da matriz de pesos soma exatamente um. O segundo é multi-head: imprime `Checkpoint 2 OK`, e com uma cabeça só a saída bate dígito por dígito com a função do primeiro. O terceiro é o bloco completo: aparecem dois números, a contagem de parâmetros na ordem de dois vírgula sete milhões e a loss antes de treinar em torno de quatro e meio. O quarto é treinar, gerar e medir: uma curva de loss descendo, quinhentos caracteres de texto e um número de perplexidade. E o quinto é uma tabela de quatro linhas mais um parágrafo dizendo o que a medição não prova.

Do primeiro ao segundo, vocês têm trinta minutos e eu circulo pela sala. Depois do intervalo, do terceiro ao quinto, trinta e cinco minutos.

No slide, do lado direito de cada checkpoint, tem um código tipo A ponto um, A ponto dois. É o item do apêndice deste deck com a matemática daquele checkpoint. Ninguém precisa disso hoje. Está ali porque, quando vocês forem escrever as questões-guia em casa, a pergunta "por que isso funciona?" vai aparecer, e eu quero que ela tenha para onde ir.

E o que vocês me entregam: o notebook executado com as saídas visíveis, três amostras de texto gerado de configurações diferentes, a tabela de experimentos do checkpoint cinco preenchida, as respostas das cinco questões-guia, e a declaração de uso de IA. Prazo de uma semana. Notebook sem saída não é avaliável — se eu abrir e não tiver nada impresso, eu não tenho evidência de que rodou.

Uma coisa sobre os testes automáticos: eles não estão ali para dar nota, estão ali porque erro de shape em atenção é silencioso. Dá para escrever uma atenção errada que roda, não levanta exceção nenhuma, e treina — pior, mais devagar, e vocês nunca descobrem por quê. Os testes são o meu jeito de fazer o erro gritar.

> Ideia central: "Erro de shape em atenção não estoura, ele degrada. Os testes deste notebook existem para fazer o erro gritar em vez de sussurrar."

## Slide 4 · [Demo] Live coding: scaled dot-product attention do zero · 00:15–00:35

Vinte minutos agora comigo escrevendo, e vocês só olhando. Depois eu solto vocês.

Eu vou escrever a atenção do zero, com tensores minúsculos — lote um, quatro posições, dimensão três — pequeno o bastante para eu imprimir a matriz inteira e a gente ler os números um por um. Nada disso precisa de GPU.

O que vocês vão ver na tela é a fórmula da Aula 6 virando oito linhas de PyTorch. A tradução é quase mecânica, e é exatamente por isso que ela é perigosa: os dois lugares onde ela quebra são um eixo de transposição e a ordem entre máscara e softmax. Os dois estão detalhados em A.1, com o motivo de o teste de vocês usar cinco posições e dimensão oito, e não dois números iguais.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> Ideia central: "Quatro posições, dimensão três. Pequeno de propósito: eu quero que a gente leia a matriz de pesos com o olho, número por número, antes de confiar nela em cento e vinte e oito posições."

## Slide 5 · [Checkpoint 1] Atenção causal · 00:35–00:50

Agora é a vez de vocês. Quinze minutos no Checkpoint 1.

Antes de falar do que implementar, eu vou dizer como vocês sabem que acabou. Quando estiver certo, a célula do teste imprime `Checkpoint 1 OK`, e ela vai ter conferido cinco coisas. A matriz de pesos tem shape lote por T por T. **Cada linha soma exatamente um.** Todo o triângulo superior está em zero. A saída da posição zero **não muda** quando o último token muda. E o modo sem máscara volta a ser bidirecional.

Guardem essas cinco, porque quando o teste falhar ele diz qual das cinco caiu, e cada uma aponta para um erro diferente.

Agora o que implementar. A função está no notebook com cinco TODOs numerados, e a assinatura já está escrita: entra `q`, `k`, `v` e uma máscara opcional, sai a saída e a matriz de pesos. Os cinco TODOs são exatamente os cinco passos que eu acabei de fazer na tela — escores, escala, máscara, softmax, agregação.

Duas coisas que eu quero cravar antes de soltar. Primeira: a máscara entra **antes** do softmax, com menos infinito. Não é multiplicar por zero depois. Se vocês zeram depois, as posições do futuro já entraram no denominador da normalização — a linha para de somar um e o futuro vazou por dentro da conta. Segunda: a escala é `raiz de d_k`, e `d_k` aqui é a dimensão **da cabeça**, não a dimensão do embedding.

Aquela quarta verificação, a de mexer no último token e conferir que a posição zero não muda, é a minha favorita do lab: é um teste de derivada escrito como diferença finita. Se a saída da posição zero mudou, informação do futuro atravessou, e o teste diz isso com essas palavras. Por que ela é consequência da ordem entre máscara e softmax, e não coincidência, está em A.1.

*[A condução completa está na Parte 3 deste roteiro.]*

> Ideia central: "Máscara antes do softmax, com menos infinito. Zerar depois do softmax é convidar o futuro para a votação, contar o voto dele e só então riscar o nome."

## Slide 6 · [Checkpoint 2] Multi-head · 00:50–01:05

Quinze minutos no Checkpoint 2.

Como vocês sabem que acabou: a célula imprime `Checkpoint 2 OK`, depois de conferir duas coisas. O shape da saída continua sendo lote por T por dimensão de embedding. E — essa é a esperta — com **uma cabeça só**, a saída bate dígito por dígito com a função que vocês escreveram no Checkpoint 1, alimentada com os mesmos pesos. Com uma cabeça, multi-head **é** a atenção simples. Se não bate, o embaralhamento está nos `view`.

A ideia central cabe numa frase: multi-head não é um laço, é um reshape.

Seis cabeças não são seis módulos rodando em sequência. É a mesma operação com uma dimensão extra na frente: o tensor sai de lote-por-posição-por-canal e vira lote-por-cabeça-por-posição-por-canal-da-cabeça. E aí a cabeça se comporta como se fosse lote — a GPU nem sabe que aquilo é uma cabeça de atenção, para ela é só um lote maior. É por isso que multi-head é praticamente de graça em tempo de execução.

A viagem de ida é `view` e `transpose`. A viagem de volta é `transpose`, `contiguous` e `view` outra vez, para reconstituir os canais na ordem certa, seguido da projeção de saída — aquele `W_O` da Aula 6 que quase todo mundo esquece que existe.

Sobre o `contiguous`: o `transpose` não move um byte de memória, ele só troca os metadados do tensor. Depois disso, os passos em memória deixam de estar na ordem dos eixos, e o `view` — que também não move nada — não tem como reinterpretar aquilo. O `contiguous` é o que copia a memória na ordem certa. E o erro **perigoso** deste checkpoint não é esquecer o `contiguous`, que estoura; é esquecer o `transpose` da volta, o que dá o shape certo com as cabeças e as posições trocadas de lugar, sem erro nenhum. Tem um exemplo numérico de oito números em A.2 que mostra isso acontecendo.

*[A condução completa está na Parte 3 deste roteiro.]*

> Ideia central: "Multi-head não é um laço sobre cabeças. É a mesma conta com uma dimensão extra, e a cabeça vira lote — é por isso que ela é quase de graça."

## Slide 7 · [Checkpoint 3] O bloco completo · 01:15–01:27

Voltando do intervalo. Doze minutos, e agora as peças da Aula 7 entram.

Como vocês sabem que acabou: **dois números na tela.** A contagem de parâmetros na ordem de dois milhões e setecentos mil. E a loss **antes de treinar**, que tem de estar em torno de quatro e meio.

Esse segundo número é o diagnóstico que vale ouro, então deixa eu explicar de onde ele sai. Um modelo recém-inicializado não sabe nada, logo ele deveria estar chutando uniformemente entre os noventa e poucos símbolos do vocabulário. Chute uniforme sobre noventa símbolos custa logaritmo natural de noventa, que é quatro vírgula cinco. Se der muito diferente disso, tem bug — e é infinitamente melhor descobrir agora do que depois de dois mil passos. Loss inicial muito **acima** de quatro e meio quer dizer que o modelo já está confiante em algo errado; muito **abaixo** quer dizer que ele está vendo o alvo, ou que vocês aplicaram softmax duas vezes. As duas leituras estão em A.4.

Três classes. `FeedForward` é a mais simples do lab e a que tem mais parâmetros: expande de cento e noventa e dois para setecentos e sessenta e oito, passa por GELU, volta. Dois terços dos parâmetros do bloco estão aí, como eu disse no começo da aula.

`Block` é o pré-norm da Aula 7: `x` recebe `x` mais atenção da norma de `x`, e depois `x` recebe `x` mais feed-forward da norma de `x`. O `x` mais, na frente, é o que permite empilhar seis camadas sem cuidado especial nenhum de inicialização. A norma fica **dentro** do ramo; o residual é uma estrada limpa que atravessa o bloco inteiro.

E o motivo pelo qual isso importa, em uma frase: com o `x +`, o gradiente tem um caminho que atravessa a pilha inteira sem passar por transformação nenhuma. Sem o `x +`, o gradiente vira um produto de seis fatores, e produto de fatores menores que um encolhe rápido. A conta com números — inclusive por que a loss estagna especificamente perto de dois e meio, e não em qualquer lugar — está em A.3.

E `MiniGPT` junta tudo: embedding de token mais embedding de posição — posição aprendida, que é o mais simples dos três esquemas da Aula 7 — pilha de blocos, norma final, e a cabeça linear que projeta de volta no vocabulário.

*[A condução completa está na Parte 3 deste roteiro.]*

> Ideia central: "Antes de treinar, a loss tem de ser o logaritmo do tamanho do vocabulário. Um modelo não treinado que não está no chute uniforme é um modelo com bug."

## Slide 8 · [Checkpoint 4] Treinar, gerar, medir perplexidade · 01:27–01:42

Quinze minutos, e é o checkpoint da recompensa: aqui sai texto.

Como vocês sabem que acabou: **três coisas na tela.** Uma curva de loss decrescente com a validação acompanhando o treino. Uma amostra de quinhentos caracteres que **parece** português sem **ser** português. E a perplexidade impressa ao lado do teto trivial, que é o tamanho do vocabulário.

O laço de treino é o laço mais banal de PyTorch: pega lote, calcula loss, zera gradiente, backward, step. Dois mil passos, AdamW com taxa três por dez elevado a menos quatro, e um log a cada duzentos e cinquenta passos com treino e validação.

Sobre a avaliação, uma coisa que eu não vou deixar passar: a estimativa de validação usa `model.eval()` e a média de várias dezenas de lotes. Não é o `loss.item()` do último lote de treino. Dropout ligado durante a avaliação injeta ruído e enviesa a estimativa para cima, e um lote só tem variância grande demais para comparar coisa alguma. Isso parece detalhe e é o embrião do erro de avaliação que a gente vai perseguir até a Aula 27.

Depois vem a geração, que é um laço com três armadilhas: cortar o contexto nos últimos cento e vinte e oito tokens, senão o embedding posicional não tem índice para aquela posição; pegar **só o último passo de tempo** dos logits; e amostrar com `multinomial` depois de aplicar a temperatura.

E a perplexidade: exponencial da loss de validação. Deixa eu dizer o que esse número é, porque a definição importa. Perplexidade é a média **geométrica** do inverso das probabilidades que o modelo deu aos símbolos certos. Média geométrica, e não aritmética, porque probabilidades ao longo de uma sequência se multiplicam. E a leitura é: o número efetivo de símbolos entre os quais o modelo hesita. O teto trivial é o tamanho do vocabulário — um modelo que chuta uniformemente entre noventa símbolos tem perplexidade noventa. Se a de vocês passar de noventa, não é modelo fraco, é bug.

Agora a armadilha que eu anunciei na Aula 1 e expliquei na Aula 2, com número de vocês na tela: essa perplexidade é **por caractere**. Ela não é comparável com nenhum número publicado de modelo de subword. E eu quero ser específico sobre o tamanho do estrago, porque "não é comparável" soa como detalhe. Um modelo com perplexidade quatro por caractere tem perplexidade duzentos e cinquenta e seis por subword, se um subword vale em média quatro caracteres. É o **mesmo modelo**, com dois números que diferem por um fator de sessenta. A conta que converte um no outro, e a única normalização que é honesta — bits por caractere —, estão em A.4.

Última coisa, e é expectativa: o texto que vai sair não vai fazer sentido. Com dois milhões e setecentos mil parâmetros e um megabyte de corpus, o alvo é morfologia e ortografia plausíveis — palavras que parecem português, pontuação nos lugares certos, estrutura de diálogo se o corpus tiver diálogo. Semântica não está no orçamento. Se o texto de vocês parece português e não é português, o modelo está certo e o lab deu certo.

> Ideia central: "O alvo de hoje é texto que *parece* português sem *ser* português. Se saiu isso, funcionou — semântica não cabe em dois milhões e setecentos mil parâmetros."

E uma última, que é sobre o que fazer quando **não** sai. Se a curva de alguém está plana, a pergunta não é quantos passos faltam. É se o laço está conectado. Isso não se responde com paciência, se responde com um teste: pega **um lote só** e treina trezentas vezes em cima dele. Dois milhões e setecentos mil parâmetros contra oito mil e cento e noventa e dois tokens são trezentos e trinta parâmetros por token a decorar — se esse modelo não decora esse lote, não falta dado nem passo, tem defeito. E o patamar em que a loss trava diz qual: parada em quatro e meio desde o começo, o gradiente não está chegando; parada em dois e meio, ele chega mas não atravessa a pilha; `nan`, explodiu. O protocolo inteiro, com os cinco culpados na ordem de custo, está em A.6.

> Ideia central: "Curva plana não é falta de passo, é falta de conexão. E isso se testa em um minuto: um lote, trezentas vezes. Se ele não decora oito mil tokens com dois milhões e setecentos mil parâmetros, o problema não é o treino."

## Slide 9 · [Checkpoint 5] Variar hiperparâmetros e comparar · 01:42–01:50

Oito minutos e o último checkpoint. Aqui vocês viram cientistas por oito minutos.

Como vocês sabem que acabou: **duas coisas no notebook.** A tabela de quatro linhas preenchida. E um parágrafo que diz qual variável mexeu mais **e o que a medição não prova**. A segunda parte é a que vale.

A função `run_experiment` treina quinhentos passos e devolve parâmetros, loss de validação, perplexidade e tempo. Quatro execuções: a referência, uma com uma cabeça só, uma com duas camadas, e uma com contexto trinta e dois. Uma variável por vez — é a única forma de a comparação querer dizer algo.

E agora a parte que é a lição de método mais importante do lab. Quinhentos passos e uma semente só não sustentam conclusão forte, e eu quero que vocês saibam **por quê**, não só que é assim. A loss que vocês medem é o efeito da configuração mais o efeito da semente, somados. Uma execução por linha não separa os dois termos — e não é questão de fazer a conta melhor, é que a informação não está na tabela.

A forma de descobrir quanto vale o termo da semente é barata: rodem a **mesma** configuração duas vezes, mudando só a semente, e olhem a distância entre os dois números. Se der quatro centésimos, então qualquer diferença menor que uns nove centésimos entre duas linhas da tabela não é evidência de nada. A conta que produz esse fator, e os três confundimentos que estão escondidos nas quatro linhas da tabela — contexto menor vê menos texto, menos camadas é menos parâmetro, e quinhentos passos é medir no transiente — estão em A.5.

Essa é a razão de o Lab 8 existir, e A.5 é literalmente o item deste apêndice que volta lá, virando intervalo de confiança e teste pareado.

> Ideia central: "Uma variável por vez, e uma frase dizendo o que a sua medição *não* prova. Quinhentos passos com uma semente não sustentam conclusão nenhuma — e saber disso vale mais que a tabela."

## Slide 10 · Recolhimento: o que entregar e a ponte para a Aula 10 · 01:50–02:00

Deixa eu fechar e mandar vocês para casa.

O que vocês têm agora, e eu quero que isso fique registrado: vocês implementaram atenção causal, multi-head por reshape, um bloco pré-norm com residual e feed-forward, empilharam seis deles, treinaram um modelo de linguagem e mediram perplexidade. Isso é o Transformer da Aula 6 e da Aula 7 inteiro, sem uma única linha de biblioteca de alto nível. A arquitetura que roda o ChatGPT é essa, com mais zeros.

A entrega: notebook executado com as saídas visíveis, três amostras geradas de configurações diferentes, a tabela do checkpoint cinco, as respostas das cinco questões-guia e a declaração de uso de IA. Uma semana. E das cinco questões, as duas que eu vou ler com mais atenção são a da perplexidade por caractere e a do que uma execução única *não* permite concluir. As duas estão respondidas com rigor no apêndice — A.4 e A.5 — e eu digo isso abertamente, porque a resposta que eu quero não é a que se decora, é a que se entende.

*[Projeto o índice do apêndice por vinte segundos: A.1 atenção causal, A.2 multi-head, A.3 bloco e residual, A.4 perplexidade, A.5 o que uma execução não prova.]*

Agora a ponte, e ela é a pergunta óbvia: se é a mesma arquitetura, por que o meu modelo escreve isso e o ChatGPT escreve aquilo? A resposta tem três partes, e nenhuma delas é arquitetura. É escala — parâmetros e tokens de treino, com uma teoria de quanto de cada um. É dado — um megabyte contra trilhões de tokens curados. E é pós-treino — todo o Módulo 3 e 4 da disciplina.

Na próxima aula a gente ataca a primeira parte: o que significa "grande" em modelo grande de linguagem, o que é Mixture of Experts, e as alavancas de decodificação que hoje vocês usaram como um parâmetro chamado `temperature` sem pensar muito. Aquele parâmetro tem uma aula inteira atrás dele. Aula 10, Do Transformer ao LLM.

> Ideia central: "Vocês acabaram de construir a mesma arquitetura que roda os modelos de fronteira. A diferença é escala, dado e pós-treino — e é exatamente aí que a disciplina vai a partir da próxima aula."

---

## Parte 2 — Demonstração guiada

Vinte minutos, live coding, tensores minúsculos. O objetivo não é adiantar o Checkpoint 1 — é fazer a turma ver a matriz de pesos com os próprios olhos antes de confiar nela em cento e vinte e oito posições. Eu escrevo em células novas, no fim do notebook, e depois apago: o TODO do aluno continua sendo o TODO do aluno.

Insumos da véspera: o notebook rodado de ponta a ponta na GPU da oferta com o tempo real anotado, e o corpus num arquivo local.

**1.** **[Abro uma célula nova e crio `q`, `k`, `v` com `torch.manual_seed(0)`, shapes `(1, 4, 3)`]** Vou usar lote um, quatro posições e dimensão três. Absurdamente pequeno, e é o ponto: eu quero imprimir a matriz inteira e a gente ler número por número. Olha os shapes na saída — um, quatro, três, para os três tensores.

**2.** **[Escrevo `escores = q @ k.transpose(-2, -1)` e imprimo o shape]** Agora o produto escalar de cada query com cada key. Olha o shape que saiu: um, quatro, quatro. Quadrado em **posições**, não em dimensão de embedding. Essa é a primeira coisa que eu quero que fique na cabeça de vocês, porque é o erro número um do checkpoint: quatro por quatro é posição contra posição. E menos dois, menos um são os dois últimos eixos — se vocês escreverem zero, um, vocês trocam lote com posição.

**3.** **[Imprimo a matriz de escores crua]** Cada célula desta matriz é a afinidade da query da linha com a key da coluna. A diagonal é cada token consigo mesmo. E repararam que não tem nada de especial na diagonal? Ela não é a maior. Não existe nada na fórmula obrigando um token a gostar de si mesmo — isso é aprendido, se for útil.

**4.** **[Divido por `math.sqrt(d_head)`, imprimo, e depois refaço com `d_head=64` para comparar]** Agora a escala. Divido por raiz de três, e a matriz encolhe em amplitude. Com dimensão três isso parece cosmético — e é. Deixa eu mostrar por que não é cosmético de verdade: mesma conta com dimensão sessenta e quatro, sem dividir. Olha o softmax disso: uma célula com peso quase um e o resto quase zero. O softmax saturou, e onde ele satura o gradiente que volta para Q e K é quase nada. A Aula 6 explicou por quê, e a conta de variância está em A.2 de lá; aqui está o número.

**5.** **[Construo `mask = torch.tril(torch.ones(T, T, dtype=torch.bool))` e imprimo]** A máscara. Olha o triângulo — é literalmente o desenho que eu fiz no quadro na Aula 6, agora como tensor booleano. Verdadeiro onde a posição pode olhar, falso onde ela não pode.

**6.** **[Aplico `escores.masked_fill(~mask, float("-inf"))` e imprimo]** E agora o passo que mais gente erra: menos infinito **antes** do softmax. Olha a matriz: metade dela virou menos infinito. Não zero — menos infinito, porque o que eu quero é que o softmax mande essas células para zero **enquanto normaliza**, não depois de normalizar.

**7.** **[Rodo `pesos = F.softmax(escores, dim=-1)`, imprimo a matriz e a soma por linha]** Softmax na última dimensão. Olha o resultado: matriz triangular, e a soma de cada linha é exatamente um. E olha a primeira linha: um, zero, zero, zero. O primeiro token não tem passado nenhum, então ele só pode olhar para si mesmo — e essa é a razão de o primeiro token de qualquer sequência ser o mais mal representado de todos.

**8.** **[Calculo `saida = pesos @ v`, confiro o shape e comparo com `F.scaled_dot_product_attention`]** Agora a agregação: pesos vezes valores, e o shape volta para um, quatro, três. Cada posição agora é uma média ponderada dos valores que ela pôde ver — uma combinação convexa, então a saída está sempre dentro da nuvem de valores, nunca fora. E para vocês não acharem que eu fiz mágica, deixa eu chamar a implementação nativa do PyTorch com `is_causal` ligado e comparar: bate. A função que eu escrevi em oito linhas é a mesma coisa que a biblioteca faz.

**9.** **[Fecho o notebook de demo sem escrever o multi-head]** E eu paro aqui, de propósito. Multi-head é o Checkpoint 2 e é de vocês. Eu já dei a dica que importa: é a mesma conta com uma dimensão extra.

---

## Parte 3 — Hands-on

Cinco checkpoints. Eu circulo pela sala olhando tela, não esperando pergunta — quem tem erro de shape não levanta a mão, porque não sabe que está errado. A pergunta que resolve metade dos casos em cinco segundos é sempre a mesma: qual o shape desse tensor aí?

Uma regra minha nos cinco: eu anuncio o checkpoint **pelo que a tela vai imprimir**, não pela fórmula. Quem sabe o que espera reconhece o fim; quem só sabe o que digitar fica olhando para o código sem saber se terminou.

**1.** **[Lanço o Checkpoint 1 — atenção causal, 00:35–00:50]** Quinze minutos, e o alvo é a linha `Checkpoint 1 OK` impressa. Os cinco TODOs da função `scaled_dot_product_attention` são os cinco passos que eu acabei de fazer na tela, na mesma ordem. Quando terminarem, a célula do teste roda sozinha e imprime o OK — ou falha dizendo qual das cinco verificações não passou.

*Como recolher:* aos 00:47 eu pergunto quantos têm o `Checkpoint 1 OK` impresso, por mão levantada. Se for menos de dois terços, eu paro a sala e resolvo o TODO 3 na tela — só o TODO 3, o da máscara, porque é onde o conceito mora. Aos 00:50 eu libero a célula de solução comentada deste checkpoint e sigo, porque o Checkpoint 2 depende desta função e ninguém pode ficar travado aqui.

**2.** **[Lanço o Checkpoint 2 — multi-head, 00:50–01:05]** Quinze minutos, e o alvo é `Checkpoint 2 OK` — shape preservado e equivalência dígito por dígito com uma cabeça só. Agora a classe `MultiHeadAttention`. A projeção `qkv` já está criada no construtor, e ela devolve os três de uma vez — o `split` separa na ordem q, k, v. A máscara já está registrada como buffer, e ela tem de ser cortada em `T` antes de usar, porque o lote pode ser mais curto que o `block_size`.

*Como recolher:* o teste de equivalência com `n_head=1` é o recolhimento — ele compara dígito por dígito com a função do Checkpoint 1. Aos 01:03 eu pergunto quem tem os dois `OK` impressos. Aos 01:05 eu libero a solução deste checkpoint junto com o intervalo, porque a segunda metade do lab não existe sem ele. Quem já terminou os dois, eu mando adiantar o `FeedForward`, que é a classe mais fácil do lab.

**3.** **[Lanço o Checkpoint 3 — o bloco completo, 01:15–01:27]** Doze minutos, e o alvo são os dois números: parâmetros na ordem de 2,7 M e loss inicial em torno de 4,5. Três classes. `FeedForward` é um `Sequential` de quatro linhas. O `forward` do `Block` são duas linhas, e as duas começam com `x = x +`. E o `MiniGPT` são quatro TODOs: somar os dois embeddings, passar pelos blocos e pela cabeça, e calcular a loss achatando lote e tempo juntos.

*Como recolher:* dois números na tela. Primeiro, a contagem de parâmetros: na configuração de referência tem de dar da ordem de dois milhões e setecentos mil, e se divergir mais de cinco por cento a tabela de A.3 diz qual peça está sobrando ou faltando. Segundo, e esse é o diagnóstico que vale ouro, a loss antes de treinar: com noventa e poucos símbolos no vocabulário, ela tem de estar em torno de quatro e meio, que é o logaritmo natural do tamanho do vocabulário. Quem não está no chute uniforme tem bug, e é melhor descobrir antes dos dois mil passos.

**4.** **[Lanço o Checkpoint 4 — treinar, gerar, medir, 01:27–01:42]** Quinze minutos, e a maior parte deles é o treino rodando. O alvo são as três coisas: curva, amostra, perplexidade ao lado do teto trivial. Enquanto roda, eu quero as duas células seguintes já lidas: o `generate`, que tem três TODOs, e a da perplexidade.

*Como recolher:* a curva de loss com treino e validação juntos, uma amostra de quinhentos caracteres colada no notebook, e a perplexidade impressa ao lado do teto trivial. Eu leio uma amostra minha, ruim, da véspera, antes de as deles saírem — calibrar expectativa é parte do recolhimento. Se a loss de alguém não desceu, a ordem de investigação é: reexecutar o teste do Checkpoint 1, reexecutar o do 2, conferir o `x +` do bloco, e só então olhar hiperparâmetro. Se alguém comparar a própria perplexidade com número publicado, a resposta é a conta de A.4, dita em dez segundos.

**5.** **[Lanço o Checkpoint 5 — variar e comparar, 01:42–01:50]** Oito minutos. O alvo são as duas coisas: tabela de quatro linhas e o parágrafo do que a medição não prova. Quatro execuções de quinhentos passos: referência, uma cabeça, duas camadas, contexto trinta e dois. Uma variável por vez.

*Como recolher:* a tabela com quatro linhas e o parágrafo com a ressalva. Se o tempo estourou, este checkpoint vai para casa e eu digo isso explicitamente — os quatro primeiros são o núcleo obrigatório. Fecho com a pergunta que eu quero na cabeça deles na Aula 11: como vocês saberiam se a diferença que mediram é maior que o ruído entre duas sementes? E a resposta operacional, que cabe em uma frase: rodando a mesma configuração duas vezes.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a matemática por trás de um checkpoint durante o lab. A regra geral num laboratório é mais rígida que numa aula teórica — **a bancada tem prioridade**. Derivação em sala de lab custa minutos de quem está travado no TODO 3, e esses minutos não voltam. A resposta padrão é uma frase de leitura conceitual mais o ponteiro para o item do apêndice.

**Item 1 — "Por que raiz de d_k, e não d_k?" (A.2 da Aula 6 + A.1 desta, ~5 min).**
A pergunta mais provável do lab, e ela costuma vir no CP1. A resposta curta, de dez segundos, é: "o produto escalar é uma soma de `d_k` termos, e a variância de uma soma de termos independentes é a soma das variâncias — logo `d_k`, e o desvio-padrão é a raiz". Se eu decidir fazer no quadro, são três linhas: soma de `d_k` termos independentes, cada um com variância 1, variância da soma igual a `d_k`, desvio-padrão `√d_k`. E fecho mostrando que dividir por `√d_k` devolve a variância para 1. A parte específica **deste** lab é o que acontece quando o divisor está errado — dividir por `d_k` comprime por 5,657 a mais, dividir por `√n_embd` comprime por `√6` a mais — e essa parte está em A.1, com os números. Se não houver tempo nem para as três linhas, a Medição 2 da demo da Aula 6 já mostrou o efeito medido, e eu remeto a ela.

**Item 2 — "Por que a máscara não pode vir depois do softmax?" (A.1, ~4 min).**
Vale fazer se muita gente errar, porque é o erro conceitual do lab. Eu escrevo a soma de uma linha nos dois casos: com a máscara antes, a linha soma um; com a máscara depois, soma um menos a massa que foi para o futuro. E o ponto que mais convence, e que eu não abro mão de dizer mesmo que não escreva nada: no caso errado, o denominador do softmax **ainda tem** as exponenciais do futuro dentro dele — então o futuro influenciou os pesos do passado, e zerar depois só esconde isso. A álgebra completa e as três consequências estão em A.1, remetendo a A.3 da Aula 6.

**Item 3 — "Por que `contiguous()`?" (A.2, ~4 min).**
Pergunta legítima e frequente no CP2. Resposta curta: "`transpose` não move memória, só troca os metadados; depois disso os passos em memória ficam fora da ordem dos eixos e o `view`, que também não move memória, não tem como reinterpretar aquilo". Se eu quiser gastar quatro minutos, o que rende é o **exemplo numérico** de A.2 — oito números, duas cabeças, duas posições — mostrando que o caminho errado produz shape certo com conteúdo permutado. Esse exemplo vale mais que qualquer explicação sobre strides, e eu projeto o item do apêndice em vez de reescrever no quadro.

**Item 4 — "De onde vêm os 2,7 M?" (A.3, ~3 min).**
A mais barata das cinco e a que eu faço com mais gosto, porque produz o número que está na tela deles. Escrevo `12·C²` por bloco, quebro em `4C²` de atenção e `8C²` de feed-forward, multiplico por seis, somo os embeddings. A tabela completa está em A.3 e eu projeto em vez de escrever, se o quadro estiver ocupado. O gancho que fica: dois terços dos parâmetros estão na peça mais boba do bloco.

**Item 5 — "Como eu saberia se a diferença da minha tabela é real?" (A.5, ~5 min).**
A pergunta mais valiosa que pode aparecer neste lab, e a que eu mais quero que apareça — se ela vier, eu **abro espaço**, tirando dos minutos finais do CP5. Eu escrevo: loss medida igual efeito da configuração mais efeito da semente; uma execução por linha não separa os dois; a variância da diferença é duas vezes a variância da semente, logo o desvio-padrão da diferença é `√2` vezes o da semente; e uma diferença só vale alguma coisa se for grande em relação a isso. Fecho mandando rodar a referência com uma segunda semente, que custa quinhentos passos e responde a pergunta empiricamente. A conta com números, os três confundimentos da tabela e a ponte para o Lab 8 estão em A.5.

**Item 6 — "A minha loss não desce, o que eu faço?" (A.6, ~3 min).**
Não é bem uma pergunta de derivação, é a pergunta de bancada mais frequente do lab — mas ela entra nesta lista porque a resposta boa é um **protocolo**, e não um palpite, e a diferença entre as duas coisas é o que separa o profissional do amador. **Esta é a única da lista que eu conduzo para a sala inteira**, e não na mesa de quem perguntou: se uma pessoa travou nisso, há outras cinco. Eu faço na ordem. Primeiro pergunto quanto vale a loss no passo zero — se não for quatro e meio, achei o problema, e foram dez segundos: é a perda ou o deslocamento dos rótulos. Se for quatro e meio, mando rodar trezentos passos num lote só e me dizer onde a curva trava. Aí eu escrevo três números no quadro, que é tudo de que preciso: travou em quatro e meio, o gradiente não está chegando; travou em dois e meio, ele chega mas não atravessa a pilha; `nan`, a taxa está alta. O que eu **não** faço, em hipótese nenhuma, é sugerir um valor de `lr` — porque no dia em que eu sugerir, a turma inteira aprende que depurar é chutar hiperparâmetro, e essa lição dura mais que o curso. Se sobrar tempo, o que mais rende é a armadilha: máscara vazada faz o teste de um lote ficar **mais fácil**, não mais difícil, então uma loss que despenca em cinquenta passos é suspeita e não é motivo de comemoração. Isso amarra de volta no Checkpoint 1 e costuma render um "ah" audível na sala. O protocolo inteiro está em A.6.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 10 da Parte 1 — o inventário do que a turma construiu, o checklist de entrega com prazo de uma semana, o índice do apêndice projetado por vinte segundos, e a ponte para a Aula 10 pela pergunta "se é a mesma arquitetura, por que o resultado é tão diferente?".

> Ideia central: "Vocês construíram hoje a mesma arquitetura dos modelos de fronteira, com dois milhões e setecentos mil parâmetros. O que falta é escala, dado e pós-treino — e é para lá que a disciplina vai a partir da próxima aula."

---

*Roteiro do Instrutor · Aula 9 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
