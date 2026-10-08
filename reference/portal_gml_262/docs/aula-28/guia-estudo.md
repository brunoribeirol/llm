# Laboratório 8: Harness de avaliação do projeto

## Slide 1 · Abertura: hoje a avaliação do projeto de vocês vira número · 00:00–00:05

Boa noite, pessoal. Semana passada eu fiz uma aula inteira sobre por que "esse modelo é bom?" é uma pergunta mal formada, e eu terminei com uma lista de camadas e a regra da menor camada que explica a falha. Hoje aquilo vira código, e vira código sobre o projeto de vocês — não sobre exemplo meu.

Deixa eu recuperar as quatro coisas da Aula 27 que hoje eu vou cobrar em função Python. Primeira: a falha se manifesta na resposta final e quase sempre mora numa camada abaixo — o chunk que não foi recuperado, o argumento com formato errado, o loop que parou cedo. Segunda: rubrica é instrumento, e nível descrito por adjetivo não discrimina. Terceira: acordo bruto engana, e o kappa desconta o acaso. Quarta: juiz não calibrado é um número sem procedência.

Hoje vocês constroem o harness que mede tudo isso no sistema de vocês. E tem uma diferença deste lab para os sete anteriores: o que sai daqui não é um notebook que eu corrijo e vocês arquivam. O que sai daqui **entra na entrega final da Aula 30**. Eu vou pedir este relatório de novo em duas semanas, com o sistema de vocês dentro dele.

Uma nota rápida e depois eu não falo mais disso: este deck tem apêndice, com cinco itens. Cada métrica que vocês vão escrever hoje tem lá a fórmula, a leitura e o caso em que ela mente. E o quinto item é a conta que eu prometi na semana passada e não fiz: por que zero vírgula setenta e um e zero vírgula setenta e oito em vinte casos são o mesmo número, e qual é o teste certo quando os dois sistemas rodaram nos mesmos casos. Quem for escrever a seção de limitações do relatório vai precisar dele.

> Ideia central: "Este é o único lab do curso cujo produto vocês vão me entregar duas vezes: hoje como lab, e na Aula 30 como parte do projeto. Ele não é descartável."

## Slide 2 · Este lab é um template, não um script · 00:05–00:10

Uma diferença estrutural que eu preciso explicar antes de vocês abrirem qualquer arquivo. Nos sete labs anteriores todo mundo rodava o mesmo código sobre o mesmo dado. Hoje não dá: vocês têm projetos diferentes. Uma equipe está fazendo RAG sobre regulamento, outra tem agente de triagem de issues, outra fez fine-tuning com avaliação comparativa. Não existe script único que sirva.

Então o que eu entreguei é um **template parametrizável**. Seis arquivos. Cinco deles não sabem nada sobre o projeto de vocês — métricas, juiz, calibração, runner e relatório são iguais para todo mundo. O sexto, o `adaptador.py`, é a única peça que muda. Ele expõe uma função, `executar`, que recebe uma entrada e devolve sempre o mesmo dicionário: resposta, fontes citadas, ranking, trajetória, por que parou, e se recusou.

E tem duas regras nesse contrato que eu vou cobrar. Primeira: **uma chamada por caso de teste**. Todas as camadas saem da mesma execução. Se vocês chamarem o sistema de novo para calcular outra métrica, e o gerador de vocês tiver temperatura, o `recall@k` vai se referir a uma execução e a nota do juiz a outra — e a tabela deixa de ser sobre um sistema.

Segunda: camada que não existe no projeto devolve lista vazia. O harness então **tira aquela camada do denominador**, em vez de contar zero. E eu quero ser preciso sobre por que isso não é detalhe de implementação: zero e "não se aplica" produzem **denominadores diferentes**, e denominador errado gera número errado com aparência de número certo. É a mesma distinção que, daqui a pouco, vai tirar os casos fora do escopo do denominador do recall. Está em A.1, com o número: contar três casos fora do escopo como zero derruba um recall real de zero vírgula oitenta para zero vírgula sessenta e oito, sem que nada no retriever tenha mudado.

> Ideia central: "Cinco arquivos são iguais para todas as equipes. Um é de vocês. Esse um chama-se adaptador, e ele é a razão de este lab caber em projetos que não se parecem."

## Slide 3 · O mapa: cinco checkpoints, e o harness roda antes de o sistema entrar · 00:10–00:15

Deixa eu desenhar as duas horas, e eu vou apresentar cada checkpoint pelo que ele imprime na tela — porque é assim que vocês vão saber que terminaram, e não pela sensação de ter terminado.

Cinco checkpoints. O primeiro é o conjunto de teste: quando estiver certo, o terminal imprime a distribuição por categoria e `Checkpoint 1 OK`. O segundo são as métricas por camada: `Checkpoint 2 OK`, com os testes de mesa passando. O terceiro é o juiz com rubrica: `Checkpoint 3 OK`, com a nota e o motivo de cada caso. O quarto é a calibração: acordo bruto, kappa, e a lista de desacordos. O quinto é rodar tudo: o arquivo `relatorio-avaliacao.md` existe, com as seis seções. Antes do intervalo, os dois primeiros. Depois, os três últimos, que são mais curtos.

Mas antes de tudo isso tem um passo zero, e eu vou fazer ele junto com vocês agora. Vou rodar `python rodar.py --testes` sem ter ligado sistema nenhum. O adaptador vem com um **stub**: um sistema de mentira que recusa toda pergunta e não recupera nada. E o harness roda inteiro com ele. O relatório sai quase todo em zero.

Isso é de propósito, por dois motivos. Um: quem está com o pipeline do projeto quebrado hoje **não perde este lab**. Todos os cinco checkpoints são avaliáveis com o stub, e o sistema de verdade entra na semana que vem. Dois: rodar o harness vazio primeiro é a única forma de saber que o instrumento está de pé antes de medir alguma coisa com ele.

E tem um detalhe engraçado no stub que eu quero que vocês vejam quando rodarem: ele recusa tudo, então ele **acerta todos os casos fora do escopo**. Se vocês olharem só a métrica de recusa correta com o denominador dos casos fora do escopo, ele tira cem por cento. Um sistema completamente inútil com uma métrica perfeita. É lição de graça sobre por que eu exijo a tabela inteira e não uma nota — e a conta dos dois denominadores possíveis, três sobre vinte e três sobre três, está em A.3.

No slide, do lado direito de cada checkpoint, tem um código tipo A ponto um. É o item do apêndice com a fórmula daquela métrica. Ninguém precisa disso para fechar o checkpoint. Está ali porque, quando vocês forem escrever o relatório, a pergunta "o que esse número quer dizer?" vai aparecer.

> Ideia central: "O stub recusa tudo e por isso acerta cem por cento dos casos fora do escopo. Um sistema inútil com uma métrica ótima — é exatamente por isso que eu não aceito nota única."

## Slide 4 · [Demo] O harness rodando num sistema de referência · 00:15–00:35

Agora eu vou fazer o que vocês vão fazer, mas num sistema que eu já tenho: um mini-RAG que é um recorte do Lab 5, sobre o regulamento acadêmico fictício. Gerador extrativo, determinístico, sem LLM nenhum. E com **defeitos plantados de propósito** — eu deixei o limiar de recusa mal ajustado e o retrieval é léxico puro, então ele quebra em paráfrase. Se os números saíssem todos em cem por cento, o exemplo não ensinaria nada.

A narração passo a passo está na Parte 2 deste roteiro. Os quatro momentos em que eu paro e faço questão de ler o número em voz alta: o `recall@1` de 0,74 com `n = 17` e não 20; a taxa de inversão do pairwise em 0% — que é propriedade do meu juiz determinístico e não virtude do sistema; o kappa de 0,67 com acordo bruto de 0,83; e a tabela por categoria, com `fato_simples` em zero por cento de falha e `parafrase` em cem por cento.

E três desses quatro números só se lê certo sabendo de onde eles vêm, então eu vou dizer de onde na hora. O dezessete é porque os três casos fora do escopo não declaram fonte relevante e por isso não entram naquele denominador. A precisão em três posições vai sair em zero vírgula trinta e um, e isso **não é defeito**: quando existe uma fonte relevante e eu olho três posições, o teto da precisão é um terço, ou seja zero vírgula trinta e três. Zero vírgula trinta e um é noventa e três por cento do máximo possível. E a inversão em zero por cento é propriedade do instrumento, porque meu juiz deriva o pairwise de uma nota absoluta e por construção não pode se contradizer. As três leituras estão em A.1 e em A.2 da Aula 27.

Essa última tabela, a por categoria, é o coração da demo. A aprovação global do sistema é 65%. Parece medíocre e uniforme. Não é: ele é perfeito no fácil e catastrófico numa categoria específica. Uma nota global de 65% não me diz onde mexer. A tabela por categoria me diz.

> Ideia central: "Sessenta e cinco por cento de aprovação global. Parece um sistema mediano em tudo. Não é: ele acerta cem por cento do fácil e erra cem por cento das paráfrases. A nota global escondeu o diagnóstico inteiro."

## Slide 5 · Checkpoint 1 — O conjunto que discrimina · 00:35–00:50

Primeiro checkpoint. Como vocês sabem que acabou: `python casos.py` imprime a distribuição por categoria e a linha `Checkpoint 1 OK`, depois de o validador conferir vinte casos, três categorias, três fora do escopo, nenhum `TODO` sobrando e nenhuma fonte que não existe no corpus de vocês.

Vinte casos ou mais, do sistema de vocês, em `casos.py`. Os três exemplos do template podem ir para o lixo — eles estão ali só para mostrar o formato dos campos.

Deixa eu cravar o ponto que decide a qualidade deste checkpoint, porque não é o número vinte. É **poder discriminativo**. Um caso que todas as versões do sistema acertam não carrega informação nenhuma: ele ocupa denominador e não separa nada. O teste mental é este — se eu trocar o retriever de vocês por outro, este conjunto consegue me dizer qual dos dois é melhor? Se não consegue, o conjunto é decoração.

E já que eu falei em denominador: com vinte casos, a menor diferença que o conjunto consegue exibir é um vigésimo, ou seja **cinco pontos percentuais**. Isso significa que vinte casos não distinguem zero vírgula setenta e um de zero vírgula setenta e oito — aquela história da semana passada. Vinte é o mínimo para ter uma tabela, não o suficiente para ranquear sistemas. Quem quiser o número exato de casos que seria preciso para resolver cinco pontos percentuais, está em A.5, e eu adianto que vocês não vão gostar.

Quatro construções que discriminam de verdade. A primeira é o **par de paráfrase**: a mesma pergunta escrita duas vezes, uma com o vocabulário da fonte e outra com o vocabulário do usuário. Se a primeira passa e a segunda falha, a falha é do retrieval, e o par prova isso sem mais nenhum instrumento. A segunda é o **fora do escopo com palavra armadilha**: uma pergunta plausível que a base não cobre, usando um termo que aparece na base em outro sentido — assim ela engana o retrieval em vez de só não casar. A terceira é o **multi-fonte**: a resposta correta exige combinar dois documentos, e isso separa "recuperou" de "sintetizou". A quarta é **regressão**: toda falha que vocês já viram vira caso. Bug que não entra no conjunto de teste volta.

E a regra de higiene: o caso se escreve **antes** de olhar a saída do sistema. Caso escrito depois de brincar com o sistema tende a ser escrito para passar. É o viés mais difícil de detectar em avaliação, porque ele produz números bonitos.

E vale passar `corpus_ids` para o validador — sem isso vocês perdem o erro mais comum daqui, que é escrever `Art. 42 §1` onde o corpus tem `Art. 42 § 1º`.

> Ideia central: "Vinte casos não é a meta, é o mínimo. A meta é um conjunto que consiga me dizer qual de duas versões do sistema de vocês é melhor. Se ele não consegue, ele é decoração com denominador."

## Slide 6 · Checkpoint 2 — Métricas por camada, com denominador visível · 00:50–01:05

Segundo checkpoint. Como vocês sabem que acabou: `python metricas.py` imprime `Checkpoint 2 OK`. Os testes comparam com casos pequenos calculados à mão — inclusive o caso de `relevantes` vazio, que é o que separa "sem fonte relevante" de "recall zero".

Seis funções, todas curtas — a maior tem quatro linhas. `citacao_valida` já vem escrita, como modelo do estilo.

Da camada de retrieval: `recall_em_k`, `precisao_em_k` e o `rr`, cuja média sobre os casos é o MRR. Da camada de resposta: `acerto_por_termos`, que é a métrica mais barata que existe e não passa por juiz nenhum; e `recusa_correta`, que é uma linha. Da trajetória: `trajetoria_bem_formada`, que é conjunção de três condições — passos dentro do orçamento, nenhum passo com `ok` falso, e parada por resposta ou recusa, nunca por limite de passos.

E antes de eu soltar vocês, uma leitura das três primeiras que faz elas pararem de parecer arbitrárias. Recall, precisão e `rr` têm **o mesmo numerador** — quantas fontes relevantes apareceram nas `k` primeiras. O que muda é por quanto se divide, e é a divisão que define a pergunta. O recall divide pelo que **existia**: o que eu deixei escapar? A precisão divide por `k`: quanto do que eu trouxe presta? E o `rr` não divide por nada — ele lê a **posição**, que é a informação que as outras duas jogam fora. Se o projeto de vocês tem reranker, o `rr` é a única das três que enxerga o que ele faz, porque reranker não muda o conjunto recuperado, muda a ordem. Isso está em A.1 e A.2, e vale ler antes de escrever o relatório.

Duas coisas que eu vou cobrar aqui e que não são sobre código.

A primeira: `recall@k` e MRR são calculados **só sobre os casos que declaram fonte relevante**. Os casos fora do escopo não têm fonte, então não entram nesse denominador. E não é convenção: com o conjunto vazio, o recall é zero sobre zero, que é indefinido. Se entrassem contando zero, o `recall` de vocês despencaria por uma razão que não tem nada a ver com recuperação. É por isso que o relatório imprime o `n` do lado de cada número.

A segunda: métrica sem denominador visível é metade de uma métrica. Com vinte casos, cada caso vale cinco pontos percentuais. Uma diferença de 0,05 entre duas versões do sistema de vocês é **um caso**. Sem o `n`, ninguém sabe se aquilo é resultado ou ruído.

> Ideia central: "Com vinte casos, cada caso vale cinco pontos percentuais. Uma melhora de cinco por cento é um caso. Por isso o `n` vai do lado de cada número no relatório — sempre."

## Slide 7 · Checkpoint 3 — A rubrica é o instrumento · 01:15–01:25

Voltando do intervalo, três checkpoints e eles são curtos.

Terceiro. Como vocês sabem que acabou: `python judge.py` imprime `Checkpoint 3 OK` com a nota **e o motivo** de cada caso de teste, e a `ADVERTENCIA_JUIZ` sem nenhum `TODO` sobrando.

A rubrica do domínio de vocês, em `judge.py`. Três critérios, três níveis — zero, um, dois. Três níveis porque três é o teto do que duas pessoas conseguem distinguir de forma reprodutível; escala de um a dez é ilusão de precisão, ninguém separa seis de sete duas vezes seguidas do mesmo jeito.

E o nível descrito por **comportamento observável**, nunca por adjetivo. "Cita o dispositivo correto e não adiciona informação ausente da fonte" discrimina. "Boa" não discrimina. Eu sei que isso soa como detalhe de redação. Não é: é o que vai decidir o kappa de vocês no próximo checkpoint, daqui a dez minutos.

E eu quero explicar o mecanismo dessa frase, porque ela costuma soar como ameaça vaga. A rubrica define **quais rótulos existem e com que frequência cada um é usado** — ou seja, a distribuição. E é a distribuição que decide quanto do acordo entre vocês e o juiz é explicado por puro acaso. Rubrica com um nível que quase nunca é usado produz distribuição desbalanceada, e aí acordo alto convive com kappa baixo **por construção**, sem que ninguém tenha feito nada de errado no juiz. Está em A.4, com a conta.

Os três critérios que estão no template — correção, ancoragem e escopo — servem para sistema com citação de fonte. Se o projeto de vocês é outra coisa, um tutor socrático, um agente de triagem, um analisador de dados, os três critérios **saem** e entra o que decide qualidade no domínio de vocês — mantendo a forma: três critérios, três níveis, âncora observável.

Duas rotas de juiz. A heurística é determinística, offline, sem chave, e roda na sala inteira ao mesmo tempo sem estourar quota de ninguém. A rota LLM faz a mesma coisa por HTTP, com a chave saindo de variável de ambiente ou `getpass`, temperatura zero, e caindo para a heurística caso por caso quando a chamada falha. O lab fecha na rota offline. A rota LLM é extensão.

E vocês vão preencher a `ADVERTENCIA_JUIZ`: uma frase dizendo **quem julgou**. Se foi o heurístico, o relatório diz que é heurístico e não é LLM. Se foi um modelo, diz modelo, família e temperatura. Número de juiz sem procedência não vale nada — isso é da Aula 27 e vale nota aqui.

> Ideia central: "Nível descrito por adjetivo não discrimina. Isso parece detalhe de redação e é o que vai decidir o kappa de vocês dez minutos depois."

## Slide 8 · Checkpoint 4 — Calibrar o juiz e reportar a concordância · 01:25–01:37

Quarto checkpoint, e é o que eu mais quero que saia daqui.

Como vocês sabem que acabou: o terminal imprime o acordo bruto, o kappa e a lista de desacordos — **e** existe uma linha escrita por desacordo, dizendo se o conserto é na rubrica, no juiz ou no sistema. Kappa baixo não reprova o checkpoint. Kappa sem inspeção de desacordo, sim.

Um juiz só vale o que a concordância dele com humano vale.

Procedimento, na ordem, e a ordem importa. Um: vocês anotam à mão uma amostra do próprio conjunto — dez casos no mínimo, doze é o que eu recomendo, e **incluindo os de fronteira**. Dois: rodam o juiz nos mesmos casos. Três: montam a matriz de confusão. Quatro: calculam acordo bruto **e** kappa. Cinco: olham cada desacordo, um por um, e escrevem a decisão.

A ordem importa porque a anotação vem primeiro. Anotar depois de ver a nota do juiz não é calibração, é concordar com ele. E a amostra precisa dos casos difíceis: calibrar em casos fáceis dá kappa alto e inútil, porque é exatamente na fronteira que o juiz vai decidir o resultado do relatório.

O kappa é aquela conta da Aula 27: acordo observado menos acordo esperado por acaso, dividido por um menos o esperado. A leitura que eu quero que fique é a mesma de lá — o numerador é o acordo que **sobrou** e o denominador é o acordo que **estava disponível**, então kappa é a fração do acordo conquistável que foi conquistada. No meu exemplo o acordo bruto é 0,83 e o kappa é 0,67: dois terços do que dava para conquistar.

Duas coisas que a V2 acrescenta aqui e que vocês vão precisar.

A primeira: a rubrica de vocês tem três níveis **ordenados**, e o kappa simples trata "eu dei zero, o juiz deu dois" e "eu dei um, o juiz deu dois" como desacordos igualmente graves. Não são. Existe kappa **ponderado**, que penaliza proporcionalmente à distância, e a implementação de referência aceita os dois. O que eu cobro é que vocês digam qual usaram — os números diferem, e comparar o ponderado de uma equipe com o simples de outra é comparar coisas diferentes. Fórmula em A.4.

A segunda, e essa muda o que vocês podem cobrar de si mesmos: existe um **teto**. Se dois integrantes da equipe anotarem a mesma amostra e concordarem com kappa de zero vírgula seis, nenhum juiz vai passar de zero vírgula seis nessa tarefa — porque zero vírgula seis é o quanto a própria definição da tarefa entrega. Um juiz com zero vírgula cinquenta e cinco contra teto de zero vírgula sessenta está em noventa e dois por cento do teto e é excelente. O mesmo zero vírgula cinquenta e cinco contra teto de zero vírgula noventa é ruim. Mesmo número, conclusões opostas. Medir o teto custa uma segunda anotação e está nas extensões.

E agora o que eu **não** vou cobrar: eu não vou cobrar kappa alto. Kappa baixo é diagnóstico, não fracasso — quase sempre significa que a rubrica está mal escrita, e reescrever a rubrica é o conserto certo. O que eu cobro é uma linha escrita por desacordo.

E um padrão de leitura que vale para sempre: **desacordos que se agrupam por mecanismo apontam para a rubrica; desacordos espalhados sem padrão apontam para o juiz.** No meu exemplo os dois desacordos têm a mesma causa — a resposta cita o dispositivo certo e não responde a pergunta feita. Dois desacordos com a mesma causa não são dois erros. São um erro de redação, cometido duas vezes.

> Ideia central: "Eu não vou cobrar kappa alto de ninguém. Kappa baixo é diagnóstico da rubrica. O que eu cobro é uma linha escrita por cada desacordo, dizendo o que vocês vão consertar."

## Slide 9 · Checkpoint 5 — Falha na menor camada, e conserto por prioridade · 01:37–01:47

Quinto e último. Como vocês sabem que acabou: o arquivo `relatorio-avaliacao.md` existe, com as seis seções, e o `teste_checkpoint_5` passa. Ele falha de propósito se o sistema declara camada de retrieval e o relatório não tem `recall@`, ou se não tem kappa.

A peça que vocês implementam é a `classificar_falha`, e ela é a Aula 27 virando `if`. A ordem de teste é de baixo para cima, e a **primeira** condição que dispara é a camada da falha. Primeiro escopo: respondeu o que devia recusar, ou recusou o que a base cobre. Depois retrieval: a fonte certa não entrou no top-k. Depois geração: a fonte certa entrou e o fato não saiu. Depois citação. Por último trajetória. Uma resposta errada porque o documento não foi recuperado é falha de **retrieval** — contar isso como falha de geração produz o conserto errado, e vocês vão passar uma semana mexendo em prompt para consertar um problema de índice.

Depois vocês preenchem o custo por camada: um, dois ou três. Barato, médio, caro. No projeto de vocês, não em abstrato. E a prioridade é impacto dividido por custo, onde impacto é a fração de casos que a camada explica.

Esse número não é objetivo, e eu não estou fingindo que é — o custo é palpite informado de vocês. O valor do exercício é **obrigar a escrever o palpite**, porque a alternativa real, quando ninguém escreve, é consertar o que é divertido em vez do que dói. No meu exemplo a camada de maior prioridade é o escopo: um limiar de recusa mal ajustado, o conserto mais barato do relatório inteiro e o de maior impacto. Ninguém escolheria isso por gosto. A tabela escolheu.

E uma ressalva sobre a tabela, que é nova e que eu quero que vocês escrevam na seção de limitações. O impacto de cada camada é uma **proporção medida em vinte casos**. Uma camada com quatro casos e outra com três estão, para todos os efeitos, empatadas — e a tabela ordena as duas como se houvesse hierarquia. A ordem da tabela de prioridade só é confiável quando as diferenças entre camadas são maiores que a resolução do conjunto. Em A.5 tem a conta que diz qual é essa resolução, e tem também o teste certo para quando vocês forem comparar a versão consertada com a versão de hoje — que é um teste **pareado**, porque os dois sistemas rodam nos mesmos casos, e essa é a informação que a comparação ingênua joga fora.

E o relatório é **saída do código**. Ninguém redige à mão. É por isso que ele é reexecutável na semana que vem, quando o sistema de vocês tiver mudado.

> Ideia central: "A tabela de prioridade existe para vocês consertarem o que dói, e não o que é divertido de consertar. No meu exemplo o primeiro da fila é um limiar mal ajustado. Ninguém escolheria isso por gosto."

## Slide 10 · O critério: número por camada, e o que não conta · 01:47–01:50

Três minutos sobre o critério, porque este é o lab em que o desvio é mais fácil e mais tentador.

Eu vou repetir por escrito o que está no plano: **"o sistema respondeu bem em oito de dez perguntas" não é resultado.** Sem número por camada, sem denominador declarado e sem a concordância do juiz medida, o relatório perde o item de rigor — mesmo que o sistema funcione perfeitamente na demo da Aula 30. Isso não é rigor burocrático meu. É que "respondeu bem" não localiza defeito, e vocês têm duas semanas para consertar coisas.

E tem o desvio simétrico, que é mais sofisticado e igualmente ruim: número **sem** denominador. "O reranker melhorou o sistema em sete pontos" sem dizer que o `n` é vinte não é um resultado — é uma frase. Com vinte casos, sete pontos é um caso e meio, e eu vou perguntar exatamente isso na apresentação.

O que decide a nota, em ordem de peso: o relatório com uma linha por camada e o `n` de cada métrica; a calibração com kappa calculado e desacordo inspecionado; e os checkpoints com saída visível. O harness que roda e não gera relatório fica abaixo da média, por construção.

> Ideia central: "'O sistema respondeu bem' não é resultado. É impressão. E número sem denominador é impressão com vírgula."

## Slide 11 · Recolhimento e ponte para a Aula 29 · 01:50–02:00

Fecha o terminal por um minuto. Deixa eu fazer o inventário do que vocês têm agora, porque é bastante.

Vocês têm um conjunto de teste rotulado do próprio sistema, com casos que discriminam. Têm métricas implementadas em três camadas, com denominador declarado. Têm uma rubrica de três níveis observáveis e um juiz que a aplica em duas rotas. Têm o kappa desse juiz contra anotação humana de vocês, com os desacordos lidos. E têm uma fila de consertos ordenada por impacto sobre custo. Isso é um plano de trabalho para as próximas duas semanas, e ele saiu de uma medição e não de opinião.

O que eu recolho, prazo de uma semana: o harness executável com os cinco módulos preenchidos, o `relatorio-avaliacao.md` gerado pelo código, o arquivo da anotação humana com o nome de quem anotou e uma linha por desacordo, as respostas das cinco questões-guia, e a declaração de uso de IA.

E o aviso que importa: este relatório é o **mesmo** que eu vou pedir na Aula 30, com o sistema de verdade ligado e a fila de consertos já trabalhada. Quem entregar hoje com o stub entrega de novo com o sistema. O harness não muda; o objeto medido muda.

*[Projeto o índice do apêndice por vinte segundos.]*

E uma indicação de leitura que não é opcional para quem quer nota cheia no relatório: o A.5. Ele é a conta que eu prometi na Aula 27 e não fiz — por que vinte casos não distinguem zero vírgula setenta e um de zero vírgula setenta e oito, quantos casos seriam precisos, e por que o teste certo para comparar a versão de hoje com a versão consertada é o teste de McNemar, que só olha os casos em que os dois sistemas discordam. A seção de limitações do relatório de vocês sai muito melhor com ele lido.

Semana que vem são as duas últimas aulas. Na Aula 29 eu vou fazer a recapitulação do curso inteiro — do token à atenção, ao pré-treino, ao alinhamento, ao raciocínio, ao RAG, aos agentes, à avaliação — e eu vou mostrar em que aula cada peça foi construída, para vocês reconhecerem o próprio percurso. E depois eu abro as fronteiras: modelos que geram texto sem ser da esquerda para a direita, imagem como forma de comprimir contexto, dados sintéticos comendo a própria cauda, e a fronteira do custo. Na Aula 30 vocês apresentam.

> Ideia central: "Na Aula 1 eu disse que no fim vocês iam apresentar um sistema construído por vocês, com números que provam que funciona. Os números começaram a existir hoje."

---

## Parte 2 — Demonstração guiada

Vinte minutos, `codigo/solucao/harness-solucao.py`, offline, só biblioteca padrão. O sistema avaliado é um mini-RAG de referência — recorte do Lab 5 sobre o regulamento acadêmico fictício, gerador extrativo determinístico, com defeitos plantados. Eu rodo por etapa, nunca tudo de uma vez.

**1.** **[Abro `harness-solucao.py` no editor e leio o cabeçalho projetado]** Eu começo pelo mapa que está no topo do arquivo: cinco checkpoints, cinco blocos de código, e a linha que eu quero que fique — o adaptador é a única peça que muda de projeto para projeto. E eu digo em voz alta o que este arquivo não é: não é o entregável de ninguém. O que se copia daqui é a estrutura, nunca os casos.

**2.** **[Rolo até o `CORPUS` e leio um dispositivo]** Seis dispositivos de um regulamento fictício. Eu aviso que é fictício, porque a turma pergunta. E aponto o `executar` logo abaixo: recupera por score léxico, escolhe a frase mais relevante, cita o dispositivo. Trinta linhas. Um RAG honesto e ruim — que é exatamente o que eu quero para demonstrar avaliação.

**3.** **[Rodo `python harness-solucao.py --etapa 1`]** Vinte casos, validador passando. Eu leio três em voz alta: o `c01` e a paráfrase dele, e um fora do escopo. No fora do escopo eu paro e mostro a armadilha — a pergunta usa uma palavra que existe na base em outro sentido, e é por isso que ela engana o retrieval em vez de simplesmente não casar.

**4.** **[Rodo `--etapa 2` e vou linha por linha na tabela]** Aqui eu paro em duas linhas. `recall@1 = 0,74` com `n = 17`: dezessete e não vinte, porque os três casos fora do escopo não declaram fonte relevante e não entram nesse denominador — e não é convenção, é que zero sobre zero não existe. E `precision@3 = 0,31`: baixo **por construção**, porque quando existe uma fonte relevante e eu olho três posições, o teto da precisão é um terço, ou seja 0,333. Zero vírgula trinta e um é noventa e três por cento do máximo atingível. Precisão baixa aqui não é defeito, é aritmética — e é o tipo de leitura que separa relatório de planilha. Se alguém quiser a fórmula do teto, está em A.1.

**5.** **[Rodo `--etapa 3`]** A rubrica com os três critérios, a nota de cada caso e os sete reprovados com o motivo. Eu desço até a taxa de inversão do pairwise e ela sai em 0%. Aí eu paro de propósito: esse zero **não** é virtude do sistema, é propriedade do instrumento. Um juiz determinístico que deriva o pairwise de uma nota absoluta não pode inverter — está demonstrado em A.2 da Aula 27. Com LLM-as-judge esse número é diferente de zero, e a demo da Aula 27 mostrou isso na tela.

**6.** **[Rodo `--etapa 4`]** Matriz de confusão, acordo bruto 0,83, kappa 0,67. Eu comparo os dois números em voz alta — a diferença é o acaso que o kappa desconta, e nesse conjunto o acaso explica cinquenta por cento, contra oitenta e dois por cento no exemplo desbalanceado da semana passada. A diferença entre os dois casos é a distribuição dos rótulos, e é isso que a rubrica controla. Depois eu abro os dois desacordos, `c08` e `c20`, com a resposta completa na tela, e conduzo a decisão: nos dois o juiz aprovou e o humano reprovou porque a resposta cita o dispositivo certo e **não responde a pergunta feita**. Meu critério de correção não distingue essas duas coisas. Dois desacordos com a mesma causa não são dois erros: são um erro de redação cometido duas vezes. O conserto é na rubrica, e eu digo qual palavra eu mudaria.

**7.** **[Rodo `--etapa 5`]** Falhas por camada, falhas por categoria, tabela de prioridade. Eu vou direto para a tabela por categoria e leio as duas linhas extremas: `fato_simples` com zero por cento de falha, `parafrase` com cem por cento. E cravo o ponto: a aprovação global é 65%, e ela escondeu isso inteiro. Depois a prioridade — escopo em primeiro lugar, quatro casos, custo um. O conserto mais barato e o de maior impacto, escolhido pela tabela e não pelo gosto. E a ressalva, que eu digo sempre: quatro casos contra três casos é diferença de um caso em vinte, e isso não ordena nada com segurança. A tabela é um ponto de partida, não um veredito.

**8.** **[Abro `relatorio-avaliacao.md` no editor e rolo as seis seções]** Este arquivo foi escrito pelo código. Eu não digitei nada nele. É por isso que eu consigo rodar de novo na semana que vem, com o sistema consertado, e comparar. Relatório redigido à mão não é reexecutável — e avaliação que não é reexecutável não serve para medir progresso.

**9.** **[Abro `lab-08-harness-avaliacao/adaptador.py` ao lado]** Fecho mostrando o que muda: `SISTEMA`, com a descrição honesta do que está sendo avaliado, e `executar_meu_sistema`, com o esqueleto comentado para RAG, para agente e para projeto sem retrieval. E a última linha do arquivo, que é o passo zero de todos: trocar `executar = executar_stub`.

---

## Parte 3 — Hands-on

Cinco checkpoints mais o passo zero. O trabalho é **em equipe de projeto**: o harness é da equipe, não individual. Eu circulo do CP1 ao CP5 e a minha pergunta padrão em cada mesa é a mesma — "que número dessa tabela vocês vão consertar primeiro?".

Uma regra minha nos cinco: eu lanço cada checkpoint **pela linha que o terminal vai imprimir**, não pela função a escrever. Quem sabe o que espera reconhece o fim; quem só sabe o que digitar fica olhando para o editor sem saber se terminou.

**[Extensões — 01:47–01:50, para quem terminou]**
Três, em ordem de valor: rodar `--juiz llm` com chave por `getpass` e comparar os dois kappas; implementar `taxa_inversao` e reportar; e o mais interessante — dois integrantes anotam a mesma amostra independentemente e calculam o kappa **humano-humano**. Se ele der 0,6, nenhum juiz vai passar de 0,6 nessa tarefa, e isso muda o que se pode cobrar do juiz. A leitura completa desse teto está em A.4.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a conta por trás de uma métrica durante o lab. A regra num laboratório é mais rígida que numa aula teórica — **a bancada tem prioridade**. Cada minuto de derivação em sala sai de quem está travado no `rr`, e esses minutos não voltam. A resposta padrão é uma frase de leitura mais o ponteiro para o item do apêndice.

**Item 1 — "Por que 17 e não 20?" (A.1, ~2 min).**
A pergunta mais frequente do lab, e ela vem na demo. Resposta de trinta segundos, que basta em 90% dos casos: "os três casos fora do escopo não têm fonte relevante, então o recall deles seria zero sobre zero — indefinido, não zero; contá-los como zero derrubaria o recall por uma razão que não tem nada a ver com recuperação". Se eu quiser gastar dois minutos, escrevo os dois números: recall real de 0,80 com denominador 17 contra 0,68 com denominador 20 — doze pontos percentuais fabricados pelo denominador. Está em A.1.

**Item 2 — "Por que a precisão está tão baixa?" (A.1, ~2 min).**
Vem sempre no `precision@3 = 0,31`. Resposta: "porque o teto é um terço". Se eu quiser desenvolver, escrevo `precision@k ≤ min(|R|, k)/k` e ponho os números: com uma fonte relevante e três posições, o máximo é 0,333, e 0,31 é noventa e três por cento do máximo. O gancho que fica: precisão em `k` só é comparável contra o próprio teto, ou entre duas versões do mesmo sistema com o mesmo `k`.

**Item 3 — "Por que meu kappa está baixo se o acordo está alto?" (A.4, ~4 min).**
A pergunta do CP4, e a mais importante das cinco. Resposta curta: "porque a distribuição dos seus rótulos é desbalanceada, então o acaso já explica quase todo o acordo". Se eu decidir conduzir, faço a comparação dos dois exemplos que a turma já viu: na Aula 27, marginais de noventa/dez davam `p_e = 0,82` e kappa de 0,11; no meu exemplo de hoje, marginais mais equilibradas dão `p_e = 0,50` e kappa de 0,67 com acordo até menor. **Mesma fórmula, distribuições diferentes, conclusões opostas.** Quatro minutos, e o preço é o Slide 10 comprimido à frase-âncora. A conta completa está em A.4.

**Item 4 — "Como eu sei que a diferença que eu medi é real?" (A.5, ~6 min).**
A pergunta que eu mais quero que apareça, porque ela é a que a Aula 27 deixou plantada. Se ela vier, eu **abro espaço**. Eu escrevo o erro-padrão de uma proporção — raiz de `p` vezes um menos `p` sobre `n` — e ponho `p = 0,71` e `n = 20`: dá zero vírgula dez. Dez pontos percentuais de erro-padrão para uma diferença declarada de sete. A diferença é menor que um erro-padrão da própria medição. E fecho com o número que dói: para resolver cinco pontos percentuais com confiança de noventa e cinco por cento seriam precisos cerca de trezentos e vinte casos.
Se sobrar fôlego, o segundo tempo é o McNemar: quando os dois sistemas rodam nos mesmos casos, os casos em que os dois acertam e os dois erram não carregam informação nenhuma; a informação está só nos discordantes, e o teste pergunta se o saldo entre eles é distinguível de uma moeda. Com dois casos de saldo, o `p`-valor é 0,50. Tudo em A.5, com as duas contas feitas.

**Item 5 — "Kappa simples ou ponderado?" (A.4, ~3 min).**
Vem de quem tem rubrica de três níveis e leu a documentação. Resposta: "com níveis ordenados, o simples trata 'zero contra dois' e 'um contra dois' como igualmente graves, e eles não são; o ponderado penaliza pela distância". A fórmula com pesos lineares está em A.4. O que eu cravo, e é o que vale nota: **os dois números são diferentes, então o relatório tem de dizer qual foi usado** — comparar o ponderado de uma equipe com o simples de outra é comparar coisas diferentes.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 11 da Parte 1 — o inventário do que a equipe tem em mãos, o checklist de entrega com prazo de uma semana, o aviso de que este mesmo relatório volta na Aula 30 com o sistema de verdade ligado, o índice do apêndice com a indicação de leitura do A.5, e a ponte para a Aula 29 pelas duas metades dela: a recapitulação do stack inteiro com o mapa de em que aula cada peça foi construída, e as fronteiras da área.

> Ideia central: "Vocês entraram nesta sala com um sistema e uma impressão sobre ele. Vocês saem com uma tabela. A diferença entre as duas coisas é a disciplina inteira."

---

*Roteiro do Instrutor · Aula 28 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
