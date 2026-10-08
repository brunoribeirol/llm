# Avaliação de LLMs e de sistemas com LLMs

## Slide 1 · Abertura: quatro semanas no prompt errado · 00:00–00:05

Boa noite, pessoal. Aula 27 de 30. A gente está a três aulas do fim, e essa é a aula que amarra o curso.

Eu vou começar contando um prejuízo.

Uma equipe de RAG recebe a queixa mais comum que existe: "a resposta está errada". E ela faz o que todo mundo faz, inclusive eu: mexe no prompt. Reescreve a instrução de sistema. Adiciona exemplos. Padroniza o formato de saída. Testa um modelo maior. Quatro semanas nisso, com a sensação honesta de estar trabalhando.

No fim das quatro semanas, alguém — por acaso — liga o log do ranking recuperado por consulta. E descobre que, em quase metade dos casos, **o documento certo não estava entre os cinco que entraram no contexto**.

Deixa eu ser claro sobre o que isso significa. Nenhuma quantidade de prompt conserta um contexto que não tem a informação. O modelo não estava respondendo mal: ele estava respondendo bem sobre o texto errado. E as quatro semanas foram gastas na única camada do sistema que não estava quebrada.

Na aula passada a gente falou de segurança e de avaliação de agentes, e o argumento de lá foi que a falha pode estar em qualquer etapa da trajetória — por isso a gente registra a trajetória inteira e não só a resposta final. Repararam que aquilo não era um argumento sobre agentes? Era um argumento sobre avaliação, disfarçado de agente. Hoje eu generalizo para qualquer coisa que tenha um LLM dentro.

E tem a dívida. Na primeira aula desta disciplina eu falei uma coisa e pedi para vocês guardarem: o modelo foi unificado — uma interface de texto, prever o próximo token, todas as tarefas de NLP na mesma caixa — mas as métricas não foram unificadas junto. Eu chamei isso de dívida de avaliação e disse que a Aula 27 pagaria. Hoje é a Aula 27, e o que vocês acabaram de ouvir é o juro dela.

> Ideia central: "A camada onde a dor aparece quase nunca é a camada onde o defeito mora — e quatro semanas é o preço de descobrir isso tarde."

## Slide 2 · Por que a intuição sozinha não basta · 00:05–00:10

Agora eu quero desmontar a pergunta que a equipe da história estava fazendo sem perceber, e que eu ouço toda semana: "professor, esse modelo é bom?"

Essa pergunta não tem resposta. E não é porque falta informação — é porque ela está mal formada.

A intuição responde assim: roda o sistema em alguns casos, olha as respostas, dá uma nota. Três vírgula oito de cinco. Parece razoável, e é inútil. Num sistema de verdade não existe "o LLM" para avaliar. Existe um modelo base, existe um prompt de sistema que alguém escreveu, existe um retriever que escolhe o que entra no contexto, existe um conjunto de ferramentas com assinaturas, existe um loop que decide quando parar, existe uma resposta final renderizada na tela, e existe um produto que alguém usa ou abandona. São sete coisas. Aquele três vírgula oito é a média de sete coisas diferentes.

E média de camadas não localiza defeito. É exatamente por isso que a equipe da história podia iterar por quatro semanas com o número parado: ela tinha um termômetro sem escala. Ele subia e descia e não dizia onde mexer.

Eu gosto de uma analogia de oficina. "O carro está ruim" e "o carro puxa para a direita a partir de oitenta" são duas frases sobre o mesmo carro. A segunda tem oficina. A primeira tem só opinião.

> Ideia central: "Uma nota global sobe e desce e não diz onde mexer. Ela é um termômetro sem escala."

## Slide 3 · As sete camadas, e a regra de ouro · 00:10–00:18

Então vamos colocar as sete camadas no quadro, porque é esse desenho que vocês vão usar no Lab 8 e no relatório do projeto.

De baixo para cima: **modelo** — os pesos, medidos por benchmark. **Prompt** — a instrução de sistema, medida por variação controlada. **Retriever** — o que entra no contexto, medido por recall e precisão em k. **Ferramenta** — a chamada e os argumentos, medida por taxa de chamada válida e de argumento correto. **Resposta final** — o que o usuário lê, medida por rubrica, juiz ou factualidade. **Trajetória** — a sequência de passos, medida por taxa de sucesso e passos até a parada. E **produto** — se alguém volta amanhã, medido por retorno e abandono.

Agora a regra, e essa é a tese da aula: eu avalio **a menor camada que explica a falha**. Menor no sentido de mais barata de medir, mais determinística, mais perto da causa.

E olhem o slide 1 de novo com esse desenho na mão. O número que faltava à equipe era o recall arroba cinco do retriever. Um número. Que custa um log e nenhuma anotação humana. Quatro semanas de trabalho contra uma linha de instrumentação que ninguém tinha escrito.

É bissecção de bug, pessoal. Ninguém depura um sistema distribuído lendo só a mensagem de erro que apareceu no front-end.

E tem o erro simétrico, que eu quero nomear antes que vocês caiam nele: descer demais. Se o retriever traz o dispositivo certo em noventa e cinco por cento dos casos e a resposta continua errada, insistir em recall é fugir do problema. A regra é a menor camada **que explica**, não a menor camada que existe.

> Ideia central: "Avalie a menor camada que explica a falha. Menor que isso é fuga; maior que isso é ruído."

## Slide 4 · [Exercício] De que camada é essa falha? · 00:18–00:26

Vou passar oito minutos com vocês trabalhando, em dupla, porque esse reflexo não se aprende me ouvindo.

Quatro falhas no slide, escritas como o usuário reportaria. Para cada uma eu quero três coisas: a menor camada que explica, a métrica com denominador que mede essa camada, e — essa é a terceira e é a que ninguém pensa — que dado precisaria estar registrado para essa métrica ser calculável depois do fato.

Esse terceiro item é o que separa quem já sofreu de quem vai sofrer, e é literalmente a história do slide 1. Métrica que precisa de um log que o sistema não guarda é métrica que não existe. Se a equipe de vocês não loga o ranking recuperado por consulta, não tem recall arroba k — tem só a lembrança de que pareceu ruim.

*[A condução completa está na Parte 3 deste roteiro.]*

> Ideia central: "Métrica que precisa de um log que vocês não guardam é métrica que não existe. Ela é uma intenção."

## Slide 5 · O número que subiu e não quer dizer nada · 00:26–00:32

Segundo sintoma, e esse é o mais caro dos quatro, porque ele não produz paralisia como o primeiro: ele produz **decisão errada com aparência de evidência**.

Uma equipe troca o retriever. Roda o conjunto de teste. A taxa de acerto vai de zero vírgula setenta e um para zero vírgula setenta e oito. Sete pontos percentuais. A equipe registra "o reranker melhorou o sistema em sete pontos", mantém a mudança, e segue.

O conjunto de teste tem vinte casos.

Deixa eu traduzir. Com vinte casos, cada caso vale cinco pontos percentuais. Sete pontos é **um caso e meio** mudando de lado. A equipe trocou um componente do sistema, com todo o custo de latência e de manutenção que isso traz, porque um caso e meio virou.

E não é que o número seja falso. Ele foi medido corretamente. O problema é que a incerteza de uma proporção medida em vinte casos é grande o suficiente para que zero vírgula setenta e um e zero vírgula setenta e oito sejam, para todos os efeitos, o mesmo número. Os intervalos de confiança se sobrepõem folgadamente.

Vocês já viram esse argumento nesta disciplina, com outra roupa. No Lab 2, na Aula 9, o checkpoint cinco pedia um parágrafo dizendo o que a medição não provava — porque quinhentos passos com uma semente não distinguem duas configurações. Lá o ruído era da semente. Aqui é da amostra. A estrutura do erro é idêntica: um número que se moveu, e ninguém perguntou quanto ele se moveria sozinho.

A conta que dimensiona isso — o intervalo de confiança de uma proporção, e qual é o teste certo para comparar dois sistemas nos **mesmos** casos — é conteúdo do Lab 8 e está no apêndice de lá. O que eu quero que saia daqui hoje é uma regra de higiene: **o `n` vai do lado de todo número**. Sem denominador, uma taxa é uma opinião com vírgula.

> Ideia central: "Com vinte casos, cada caso vale cinco pontos percentuais. 'Melhorou sete pontos' é 'um caso e meio mudou de lado'."

## Slide 6 · Avaliação humana: a rubrica é o instrumento · 00:32–00:39

Então vamos ao humano, que é onde toda avaliação séria ancora.

E eu quero desfazer uma ideia: avaliação humana não é "pedir opinião para uma pessoa". Opinião de uma pessoa não é dado. O que transforma opinião em dado são três decisões, e as três são de projeto.

Primeira, a **unidade** anotada. O que é uma linha da planilha? A resposta inteira? Cada afirmação dentro da resposta? O par ordenado de duas respostas? Isso muda tudo, inclusive quanto custa anotar.

Segunda, a **escala**, e aqui eu vou ser dogmático: níveis descritos por comportamento observável, nunca por adjetivo. "Cita o dispositivo correto e não adiciona informação ausente da fonte" — isso discrimina, duas pessoas leem e chegam no mesmo lugar. "Boa" não discrimina. E escala de um a dez é ilusão de precisão: ninguém distingue seis de sete de forma reprodutível. Três ou quatro níveis com âncora textual dão acordo muito maior que dez níveis sem âncora.

Terceira, **mais de um anotador** sobre um subconjunto sobreposto. Um anotador sozinho não tem contra quem errar. Ele é internamente consistente por construção e isso não significa nada.

A rubrica é o teste unitário do julgamento humano. Se duas pessoas rodam o mesmo caso e chegam em respostas diferentes, quem está mal escrito é o teste — não as pessoas.

> Ideia central: "Se dois anotadores discordam, o problema é a rubrica. Rubrica ruim não mede pessoa, mede humor."

## Slide 7 · Acordo de 84% e kappa de 0,11 · 00:39–00:48

Agora o número. Duas pessoas da equipe anotaram cinquenta casos. Como eu digo se elas concordam?

A resposta ingênua é acordo bruto: a fração de casos em que as duas deram o mesmo rótulo. E deu oitenta e quatro por cento. Oitenta e quatro por cento de acordo entre dois anotadores parece um bom número para colocar num relatório.

Não é. E eu vou dizer por quê antes de mostrar a fórmula.

O conjunto de vocês é desbalanceado. Um sistema que já funciona razoavelmente acerta a maioria das vezes — digamos noventa por cento. Agora imaginem dois anotadores preguiçosos, que marcam "correta" no automático, sem ler nada. Qual seria o acordo bruto **deles**? Em torno de oitenta e um por cento. Oitenta e um por cento de acordo sem ninguém ter olhado uma resposta.

Então dos oitenta e quatro por cento que a equipe mediu, a maior parte já era explicada pelo simples fato de os dois marcarem quase sempre a mesma coisa. Descontando isso, sobra pouquíssimo. O número que sobra tem nome — kappa de Cohen — e ele dá **zero vírgula onze**.

*[Projeto a fórmula e leio, apontando cada termo.]*

Kappa é acordo observado menos acordo esperado por acaso, dividido por um menos o acordo esperado por acaso. E o acordo esperado é uma soma sobre as classes, do produto de quanto cada anotador usa aquele rótulo.

A leitura que eu quero que fique é essa: o numerador é o acordo que **sobrou**, e o denominador é o acordo que **estava disponível** para ser conquistado. Kappa é a fração do acordo conquistável que foi de fato conquistada. Onze por cento.

A leitura prática são três casos. Kappa perto de zero é o mesmo que sortear. Kappa alto com acordo alto é acordo de verdade. E acordo alto com kappa baixo é o sinal vermelho: a tarefa está desbalanceada e a anotação não está medindo nada. Para mais de dois anotadores o análogo é o kappa de Fleiss, mesma ideia.

E deixa eu antecipar a pergunta: não, eu não vou dar uma tabela de "kappa aprovado". Essas faixas que circulam são convenção editorial, não lei. O que importa é comparar o kappa do juiz de vocês com o kappa entre **dois humanos** na mesma tarefa. Se dois humanos concordam com kappa de sessenta, exigir noventa do juiz é exigir do juiz mais do que a própria definição da tarefa entrega.

A tabela dois por dois que produz o zero vírgula onze, a derivação do acordo esperado a partir das marginais, o caso simétrico em que o mesmo acordo bruto dá kappa de zero vírgula sessenta e oito, e o kappa ponderado para escalas ordinais — que é o que vocês vão usar no Lab 8, com três níveis — estão em A.1.

> Ideia central: "Oitenta e quatro por cento de acordo e kappa de onze centésimos. Eles não concordaram — eles coincidiram."

## Slide 8 · A dívida da Aula 1: BLEU e ROUGE em geração aberta · 00:48–00:55

Bom, agora eu pago a conta que eu abri na Aula 1.

Lembram do BLEU e do ROUGE? BLEU é precisão de n-gramas contra uma referência, com penalidade de brevidade. ROUGE é revocação de n-gramas da referência, ou a maior subsequência comum. Os dois são baratos, determinísticos e não precisam de juiz nenhum. E os dois têm uma premissa embutida que quase ninguém enuncia: **existe uma referência, e ela é aproximadamente única**.

*[Projeto as fórmulas e leio o que cada peça compra.]*

Cada peça daquela fórmula existe para tapar um jeito específico de burlar a métrica. A precisão com corte existe porque, sem ela, responder "o o o o o o" contra uma referência que tem um "o" daria precisão perfeita. A média ser geométrica, e não aritmética, existe para que um n-grama de ordem alta zerado zere a nota inteira — palavras certas na ordem errada não é uma tradução parcialmente boa. E a penalidade de brevidade existe porque, sem ela, responder uma palavra só teria precisão máxima.

Em geração aberta a premissa cai. Se existem cinquenta respostas boas e mutuamente diferentes, sobreposição de n-gramas com uma delas mede estilo, não qualidade. E as duas falhas são simétricas, o que é o pior cenário possível para uma métrica.

Deixa eu dar os dois casos com números, porque eles são o argumento inteiro. Referência: "o prazo de trancamento é de trinta dias". Primeiro candidato: "o aluno tem um mês para solicitar o trancamento" — está **certo**, trinta dias é um mês. BLEU perto de zero, porque quase nenhum bigrama coincide. Segundo candidato: "o prazo de trancamento é de treze dias" — está **errado**, trocou trinta por treze, que é o único erro que importava. BLEU em torno de zero vírgula oitenta e sete, porque oito dos nove unigramas coincidem.

Uma resposta certa tira zero. Uma resposta errada tira quase dez. A métrica erra nas duas direções, e errar nas duas direções é pior que errar sistematicamente numa só, porque nem dá para corrigir o viés.

Essa é a dívida. A gente unificou a interface — tudo virou texto entrando e texto saindo — e as métricas continuaram atadas às tarefas antigas, onde a saída era canônica.

Mas atenção, porque a conclusão preguiçosa aqui é péssima. Não é "então métrica automática não serve". BLEU e ROUGE continuam sendo a métrica **certa** onde a saída é canônica e curta: tradução com referência profissional, sumarização extrativa com resumo de ouro, conversão de formato, extração estruturada. E é a mesma regra do slide 3: métrica determinística na camada em que a saída é canônica; juiz e humano na camada em que ela não é.

As fórmulas por extenso — o corte de contagem, a penalidade de brevidade com a verificação nos extremos, e a medida F do ROUGE-L — estão em A.3.

> Ideia central: "A dívida da Aula 1 é esta: o modelo virou um, e as métricas continuaram sendo N. O resto da aula é o que a área inventou para fechar esse buraco."

## Slide 9 · LLM-as-judge: pairwise × rubrica · 01:05–01:11

Voltando. Se referência não serve e humano não escala, a área foi para o caminho óbvio: usar um modelo como juiz.

E tem duas formas, com propriedades bem diferentes. Vou separar as duas porque escolher errado aqui é o erro mais comum do Lab 8.

**Pairwise:** eu mostro duas saídas para a mesma entrada e pergunto qual é melhor. É mais fácil para o juiz, porque comparar é mais fácil que pontuar — e isso vale para humano também. Produz sinal bom para *ordenar* sistemas. E não produz nota absoluta: pairwise nunca responde "está bom o suficiente?". Ele responde "é melhor que aquele".

**Rubrica, ou pointwise:** eu dou os critérios e peço nota por critério. Isso produz nota absoluta, comparável entre execuções, e rastreável — eu sei qual critério caiu. O preço é que é muito mais sensível à redação da rubrica, e tem uma tendência chata de comprimir tudo no topo da escala, com todo mundo tirando quatro de cinco.

A imagem que eu uso: pairwise é campeonato, rubrica é prova com gabarito. Campeonato ordena, prova aprova. E aí fica claro o erro: usar campeonato para decidir se o sistema está pronto para produção. O campeonato só sabe dizer que o time A é melhor que o time B — inclusive quando os dois são ruins.

E eu quero acrescentar um terceiro formato, porque a Aula 26 já pediu ele sem dar o nome. Esses dois julgam a **saída final**. Só que um sistema com agente não produz uma saída, produz uma **trajetória** — e eu fechei a Aula 26 dizendo justamente "registrem trajetórias, não só respostas".

Existe um juiz que lê a trajetória. Chama Agent-as-a-Judge, e ele emite julgamento **intermediário**, passo a passo, em vez de olhar só o fim. Num conjunto de cinquenta e cinco tarefas reais de desenvolvimento, decompostas em trezentos e sessenta e cinco requisitos, ele bate o LLM-as-judge com folga e chega na confiabilidade da linha de base **humana**.

E eu vou dizer o custo junto, porque é ele que decide: esse juiz **é um agente**. Cada julgamento é uma trajetória a mais. É mais caro e mais lento que uma chamada de juiz, e por isso ele **não** é o que eu recomendo para o Lab 8 de vocês. Mas saibam que ele existe, porque a pergunta "meu juiz olha só o fim?" é uma pergunta legítima sobre o instrumento de vocês.

> Ideia central: "Pairwise ordena, rubrica aprova. Se a pergunta de vocês é 'está pronto?', pairwise não responde."

> Ideia central: "Se o sistema produz trajetória e o juiz lê só o fim, o juiz está medindo menos do que o sistema faz."

## Slide 10 · O juiz que muda de opinião quando eu troco a ordem · 01:11–01:19

Terceiro sintoma, e esse é o que faz esta aula existir.

Vocês montam o juiz. Escrevem a rubrica com carinho. Colocam temperatura zero, para ser reprodutível. Rodam os doze pares e anotam os vencedores. Aí, por curiosidade, alguém roda de novo trocando qual das duas respostas aparece primeiro no prompt.

E o vencedor muda.

Não em todos. Numa fração. Mesmo par, mesmo prompt, mesma rubrica, mesma temperatura zero — e vencedor diferente porque a resposta B foi apresentada antes da A. Isso não é ruído de amostragem, porque com temperatura zero não há amostragem. É o instrumento.

Isso tem nome, é conhecido, é reprodutível, e — a parte boa — é **medível**. Três vieses importam para o projeto de vocês.

**Posição.** A saída apresentada primeiro tem vantagem sistemática. Não é sutil e não é pequena. O protocolo é simples e caro: julgar nas duas ordens, e quem inverteu vira empate. E o número que sai disso é a **taxa de inversão**, que é a coisa mais honesta que vocês podem colocar num relatório de avaliação — porque ela é o limite superior da confiança naquele número. Se vinte e cinco por cento dos pares invertem, então o acordo com o humano que vocês reportariam rodando só uma ordem pode variar em até vinte e cinco pontos dependendo de qual ordem vocês escolheram. E vocês escolheram sem saber.

E tem uma relação bonita que eu quero enunciar, porque a demo daqui a pouco vai confirmar na tela: a fração de vitórias de quem aparece primeiro é aproximadamente **meio mais metade da taxa de inversão**. Se a taxa de inversão for vinte e cinco por cento, a preferência pela primeira posição deve sair perto de sessenta e dois e meio por cento. As duas são a mesma informação. Medir uma estima a outra — e se elas não baterem, o problema está no conjunto, não no juiz.

**Verbosidade.** Resposta mais longa é lida como mais completa. Três protocolos: declarar concisão como critério explícito na rubrica, controlar o comprimento entre as saídas comparadas, e reportar a correlação entre vencer e ser mais longo. Se noventa por cento dos vencedores são os textos mais longos, o juiz de vocês está medindo tamanho.

**Autopreferência.** O juiz favorece texto gerado por ele mesmo ou pela própria família de modelos. O protocolo é escolher juiz de família diferente da do sistema avaliado, e nunca usar o mesmo modelo como gerador e como juiz sem declarar isso no relatório em letra grande.

Isso é viés de instrumento, pessoal. Ninguém publica medição de temperatura sem dizer que calibrou o termômetro. E deixa eu matar de uma vez a solução mágica que sempre aparece: não, temperatura zero não resolve. Temperatura zero dá reprodutibilidade, não ausência de viés. O juiz determinístico erra sempre igual — e é exatamente isso que eu vou mostrar agora.

> Ideia central: "Temperatura zero não conserta viés. Ela só garante que o juiz vai errar do mesmo jeito todas as vezes."

## Slide 11 · [Demo] O mesmo par, duas ordens, dois vencedores · 01:19–01:29

Os passos operacionais desta demo estão na Parte 2 deste roteiro. O que eu falo aqui é o enquadramento e a leitura dos números.

O experimento é o mais simples que existe. Doze pares de respostas sobre o regulamento acadêmico fictício do Lab 5 — o mesmo regulamento, para vocês reconhecerem o terreno. Cada par vai para o juiz duas vezes: uma na ordem A depois B, outra na ordem B depois A. Só isso. Se o juiz fosse uma função da qualidade das respostas, o vencedor seria o mesmo nas duas rodadas, porque a qualidade não mudou entre uma chamada e a outra.

E o juiz padrão desta demo é sintético, offline, determinístico. Eu quero ser honesto sobre o que isso é e o que não é: ele não mede modelo nenhum. Ele é uma função com quatro parcelas explícitas que eu escrevi — plausibilidade da resposta, bônus para quem aparece primeiro, bônus para quem escreve mais, e um ruído pequeno. Ele reproduz o **mecanismo**, com número reprodutível, sem depender da rede desta sala. Quem quiser o número de um juiz de verdade roda com `--modo api` e uma chave.

E tem uma distinção dentro dos dados que é o coração da demo. Cada par tem dois campos que parecem a mesma coisa e não são: `melhor`, que é o rótulo humano — qual resposta está *correta* conferida contra o regulamento; e a plausibilidade de cada resposta, que é o quanto ela *soa* certa para quem não tem o regulamento na mão. O juiz só vê a segunda coisa. Ele não tem a fonte. Isso não é um defeito da minha simulação — é a situação real de todo juiz que julga sem o documento na frente.

> Ideia central: "O juiz não vê a verdade. Ele vê o que parece verdade. Guardem essa frase para o slide da factualidade."

## Slide 12 · Calibrar antes de escalar · 01:29–01:35

Então o juiz é enviesado, e o número dele muda com a ordem. A pergunta certa não é "então descarto o juiz?". É: **quanto vale o número dele?** E isso é uma quantidade medível.

O procedimento é sempre o mesmo, e é o Checkpoint 4 do lab da semana que vem. Anotar à mão uma amostra do próprio conjunto de teste — quarenta a sessenta casos já dizem muito. Rodar o juiz nos mesmos casos. Medir a concordância com kappa, não com acordo bruto, pelo motivo do slide 7. Depois, e essa é a parte que ninguém faz: **olhar os desacordos um por um**. Na maioria das vezes o conserto não é trocar de modelo, é reescrever a rubrica — porque o desacordo revela que o critério estava ambíguo e o humano e o juiz o leram de formas diferentes.

E só depois disso o juiz é liberado para rodar nos quinhentos casos que ninguém tem tempo de anotar à mão.

O juiz é um estagiário. Ele não começa assinando laudo. Ele começa fazendo cinquenta laudos que alguém confere — e é a taxa de acerto naqueles cinquenta que define se ele pode assinar os outros.

Duas advertências. A primeira: a amostra de calibração não pode ser feita de casos fáceis. Se vocês calibrarem em casos óbvios, o kappa vai vir alto e não vai significar nada, porque a decisão do relatório final é tomada nos casos de fronteira. A amostra de calibração precisa doer.

A segunda é a que eu prometi no slide 7 e que vale para o resto da vida de vocês: existe um **teto**, e ele é o kappa entre dois humanos na mesma tarefa. Se dois integrantes da equipe anotarem a mesma amostra e concordarem com kappa de zero vírgula seis, nenhum juiz vai passar disso — porque zero vírgula seis é o quanto a própria definição da tarefa consegue entregar. Medir esse teto custa uma segunda anotação e muda o que vocês podem cobrar do juiz. É a extensão mais valiosa do Lab 8, e está em A.1.

> Ideia central: "Um juiz não calibrado não é uma métrica. É uma opinião com aparência de número — e essa é a pior coisa que pode entrar num relatório."

## Slide 13 · Factualidade: decompor em afirmações atômicas · 01:35–01:42

Agora um tipo de erro que juiz nenhum pega bem, e que é o erro que mais aparece em projeto de RAG: a resposta inventa fato.

E "essa resposta é factual?" é uma pergunta binária sobre um objeto que não é binário. Se o parágrafo tem seis afirmações e uma está errada, qual é a resposta? Meio? Sim com ressalva?

O procedimento correto é decompor. Primeiro, quebrar a resposta em **afirmações atômicas** — cada uma verificável isoladamente. Segundo, para cada afirmação, procurar suporte na fonte. Terceiro, rotular em três valores, não dois: *suportada*, *contradita*, ou *não verificável pela fonte*. E quarto, reportar a proporção de suportadas e, separada, a taxa de contraditas — que é a métrica que dói e a que vocês vão querer esconder.

E aqui está o motivo de serem duas métricas e não uma, porque isso é o que separa relatório bom de relatório confuso. As duas **não** são complementares, porque o terceiro rótulo existe. Uma resposta com três suportadas e três não verificáveis tem precisão de cinquenta por cento e zero contraditas: ela é **incompleta**. Uma resposta com três suportadas e três contraditas tem a mesma precisão de cinquenta por cento: ela é **falsa**. Reportar só o cinquenta por cento para as duas apaga a única distinção que decide o que consertar — a primeira é problema de escopo, a segunda é alucinação.

O ganho não é só de precisão da medida. É de localização do dano. Uma resposta com cinco afirmações suportadas e uma inventada é um problema completamente diferente de uma resposta inteiramente inventada, e nota global de um a cinco põe as duas no mesmo lugar. É diff por linha em vez de "o arquivo está diferente".

E olhem por que isso amarra na demo. Lembram dos dois pares em que o juiz sintético errou **nas duas ordens**? Inversão posicional não explica aqueles dois. Ele errou porque a resposta falsa era a mais plausível e ele não tinha o documento para conferir. Consistência não é acerto. Aquele erro só se conserta com verificação contra a fonte, afirmação por afirmação.

Uma distinção fina, para fechar: *não suportada pela fonte* não é o mesmo que *falsa*. A afirmação pode ser verdadeira no mundo e simplesmente ausente do documento. Num sistema que promete citação, isso ainda é defeito — mas é defeito de escopo, não alucinação, e o conserto é diferente.

E tem uma armadilha de agregação que eu não vou detalhar aqui e que vocês vão encontrar no Lab 8: somar todas as afirmações de todas as respostas num balaio só dá um número, e tirar a média das proporções de cada resposta dá **outro**. As duas contas, com um exemplo em que elas diferem em dezoito pontos percentuais, estão em A.4. O erro não é escolher uma; é não declarar qual foi usada.

> Ideia central: "Consistência não é acerto. Um juiz determinístico erra sempre igual, e nenhuma quantidade de rodadas descobre isso."

## Slide 14 · O modelo que lidera o leaderboard e é o pior no caso de vocês · 01:42–01:46

Quarto e último sintoma, e esse custa dinheiro de verdade.

A equipe precisa escolher um modelo. Abre o leaderboard, pega o primeiro colocado, integra. E no caso de uso dela — a papelada da secretaria acadêmica — ele é o pior dos três candidatos que ela tinha.

Três razões independentes, e cada uma sozinha já basta.

**Distribuição:** o benchmark tem a distribuição do benchmark; o produto tem a distribuição dos usuários. O modelo que lidera em raciocínio matemático pode ser o pior de todos em texto administrativo em português.

**Camada:** leaderboard mede o modelo, e o produto é o sistema. Isso é literalmente o slide 1 desta aula — na minha experiência trocar o retriever move o resultado final mais que trocar o modelo, e o leaderboard não tem coluna para retriever.

**Restrição:** latência, custo por requisição, limite de contexto, política de privacidade, disponibilidade na região. Nada disso é coluna de nenhum ranking, e é frequentemente o que decide a escolha.

É escolher pneu por velocidade máxima quando o carro nunca passa de sessenta e o problema é chuva.

E o erro simétrico, que também aparece e é igualmente ruim: descartar benchmark como inútil. Benchmark serve — para triagem inicial de candidatos e para detectar regressão grosseira. Ele não é critério de aceitação. Ninguém aceita um sistema porque o modelo dele foi bem numa prova de múltipla escolha.

Uma ressalva que fecha o círculo com o slide 5: o conjunto de teste próprio de vocês também tem vinte casos. Ele é melhor que o leaderboard porque tem a distribuição certa, e ainda assim não distingue dois candidatos que ficam a sete pontos de distância. Escolher entre dois modelos próximos exige mais casos, ou um teste que aproveite o fato de eles rodarem nos mesmos casos.

> Ideia central: "Leaderboard é triagem, não critério de aceitação. Ninguém aceita um sistema porque o modelo dele foi bem numa prova de múltipla escolha."

## Slide 15 · O que o MMLU mede bem, e por que isso é pouco · 01:46–01:50

Falta nomear o instrumento do slide anterior, porque criticar leaderboard sem entender o que ele mede é barato.

MMLU — Hendrycks e colegas, *Measuring Massive Multitask Language Understanding*, arXiv 2009.03300. É múltipla escolha de quatro alternativas em cinquenta e sete áreas, de direito a física, com linha de base aleatória de vinte e cinco por cento. O formato é o que faz dele barato e comparável: gabarito único, correção automática, zero ambiguidade de referência. É o **oposto exato** do problema do slide 8 — lá a referência não era única e a métrica media estilo; aqui a referência é uma letra e não há o que interpretar.

E é exatamente por isso que ele mede pouco do que o sistema de vocês faz. Não tem geração aberta. Não tem ferramenta. Não tem trajetória. Não tem usuário. Ele mede conhecimento e raciocínio de escolha múltipla no modelo, e mede bem — o que é uma coisa muito menor do que "o sistema é bom".

E tem a ameaça estrutural, que é **contaminação de dados**. O benchmark é público. O pré-treino raspa a web. Ninguém garante que as questões não estão no corpus de treino. Os sintomas são reconhecíveis: salto grande num benchmark antigo sem salto correspondente em benchmark novo de dificuldade equivalente; ou desempenho que despenca quando as questões são parafraseadas ou as alternativas reordenadas.

E uma nota de justiça: contaminação na maioria dos casos não é fraude. É consequência de raspar a web em escala. O que não a torna nem um pouco menos fatal para a conclusão que alguém tirou daquele número.

Agora, tem uma defesa contra isso, e ela é bonita de tão banal. O BIG-bench, que é um benchmark colaborativo com mais de duzentas tarefas, marca **toda** tarefa de avaliação com uma sequência fixa de caracteres. Esta aqui: dois-seis-b-cinco-c-seis-sete-b, e por aí vai — um UUID, feio, sem significado nenhum. Ela existe por um motivo único: para que quem monta corpus de pré-treino consiga procurar por essa sequência e **jogar fora** tudo que a contém.

É uma solução de uma linha para um problema de bilhões de tokens. E eu mostro ela porque tem uma lição de engenharia embutida que vale mais que o truque: isso só funciona porque foi combinado **antes**. Depois que a web foi raspada, não tem o que filtrar. Contaminação é um problema que só se resolve no projeto do dado, nunca na análise do resultado.

> Ideia central: "A defesa contra contaminação é um UUID feio combinado antes de o dado existir. Depois que o corpus foi raspado, não tem o que filtrar — e é por isso que isso é decisão de projeto, não de análise."

> Ideia central: "Um benchmark público num corpus que raspou a web inteira. Contaminação aqui não é acusação, é a expectativa padrão."

## Slide 16 · Encerramento: a dívida quitada e o que a Aula 28 cobra · 01:50–02:00

Deixa eu fechar amarrando as duas pontas.

Na Aula 1 eu disse que o próximo-token unificou as tarefas e que as métricas ficaram para trás. Hoje vocês viram o buraco por dentro, e viram por quatro prejuízos concretos: quatro semanas ajustando a camada errada; um número que subiu sete pontos e era um caso e meio; um juiz que muda de vencedor quando eu troco a ordem; e um ranking que escolheu o pior modelo para o caso de uso.

E as quatro respostas. Referência mede estilo quando há muitas respostas boas. Humano não escala e precisa de rubrica e de kappa para virar dado. Juiz escala e tem viés de posição, de verbosidade e de autopreferência — e o número dele só vale a concordância que alguém mediu. Factualidade não é binária, é decomposição em afirmações verificadas contra fonte. E benchmark mede o modelo, não o sistema.

A dívida está paga, mas ela não foi paga com uma métrica nova. Foi paga com uma **regra**: avaliar a menor camada que explica a falha — com o `n` do lado de todo número. É essa regra que vocês levam.

E agora a parte que vale nota. Na próxima aula é o Laboratório 8, e ele é diferente de todos os outros sete: não existe um notebook único que eu entrego pronto, porque o objeto avaliado é o projeto de vocês, e cada projeto é diferente. O que eu entrego é um template parametrizável, e o que vocês constroem é o harness de avaliação do próprio sistema — conjunto de teste com vinte casos no mínimo, métrica por camada, juiz com rubrica, calibração do juiz contra amostra anotada por vocês mesmos, e análise de falhas com priorização.

E o produto do Lab 8 **não é** um lab que morre na entrega da semana. Ele integra a entrega final do projeto. É literalmente o item de trinta por cento da nota do projeto sendo construído em sala com eu circulando.

*[Projeto o índice do apêndice por vinte segundos.]*

Uma palavra sobre esses quatro itens do apêndice, porque eles não são enfeite: A.1 é o kappa que vocês vão implementar no Checkpoint 4, A.2 é a taxa de inversão que vocês vão reportar, A.3 é o que justifica não usar BLEU no projeto de vocês, e A.4 é a decomposição factual. Quem chegar na próxima aula com A.1 lido faz o Checkpoint 4 na metade do tempo.

Então o que eu preciso que cada equipe traga: o sistema rodando de ponta a ponta, mesmo simples — que é a Entrega 2 que vocês já fizeram; uma lista das camadas que o sistema tem; e um rascunho da rubrica, aquele do slide 6. Quem chegar com essas três coisas fecha os cinco checkpoints em sala. Quem chegar sem, gasta o primeiro bloco decidindo o que já podia estar decidido.

> Ideia central: "Semana que vem vocês não vão avaliar um modelo. Vocês vão avaliar a coisa que vocês construíram — e é esse número que vai no relatório final."

---

## Parte 2 — Demonstração guiada

Dez minutos, no terminal, com a pasta `codigo/` desta aula aberta. A demo é determinística no modo padrão: ela não depende da rede da sala e imprime os mesmos números em qualquer máquina. Eu rodo ao vivo por isso.

Na V2 esta demo ganhou uma função extra: além de mostrar o mecanismo do viés, ela **verifica na tela** a relação que eu enunciei no slide 10 — preferência pela primeira posição igual a meio mais metade da taxa de inversão. É a fórmula sendo conferida em vez de derivada.

**1.** **[Abro `demo-judge-bias.py` no editor e vou até a lista `PARES`]** Antes de rodar qualquer coisa eu quero mostrar o dado, porque a demo inteira vive de uma distinção que está aqui dentro. Cada par tem a pergunta, duas respostas, e dois campos que parecem a mesma coisa: `melhor`, que é o rótulo humano — qual das duas está correta conferida contra o regulamento — e a plausibilidade de cada resposta, que é o quanto ela soa certa para quem não tem o regulamento na mão. O juiz recebe só os textos. Ele nunca vê o `melhor`.

**2.** **[Rolo até os pares p03, p07 e p10]** E eu plantei três tipos de armadilha, de propósito. Nestes três a resposta errada é a mais longa e a mais autoritária — o p07 é o meu favorito, porque a resposta A admite honestamente que o regulamento não cobre a pergunta e a resposta B inventa um procedimento inteiro, com banca, prazo e contagem de dias úteis. Nos pares p02, p05 e p09 as duas respostas são equivalentes, e é aí que o bônus de posição decide sozinho. E nos pares p04 e p08 a resposta certa é a mais curta e mais seca de todas.

**3.** **[Rodo `python demo-judge-bias.py`]** Doze pares, vinte e quatro julgamentos, um segundo. Vou ler a tabela com vocês. Coluna do humano, coluna do vencedor quando A vem primeiro, coluna do vencedor quando B vem primeiro, e o veredito. Olha a linha do p02 — mesmo par, mesmo prompt, mesmo juiz, e o vencedor mudou porque eu troquei quem aparece primeiro.

**4.** **[Aponto o bloco de métricas e faço a conta de cabeça na frente da turma]** Taxa de inversão posicional: essa é a linha que essa demo existe para imprimir. Agora peguem a taxa de inversão e façam comigo: meio, mais metade dela. *[faço a conta em voz alta]* E agora olhem a linha de baixo, a preferência pela resposta em primeiro lugar. Bate. Não é coincidência: é a relação que eu enunciei no slide anterior, e a derivação dela está em A.2. Sem viés, essa linha seria cinquenta por cento e a inversão seria zero. E a terceira linha, preferência pela resposta mais longa, é o segundo viés aparecendo no mesmo experimento sem eu ter feito nada para provocá-lo.

**5.** **[Aponto as duas linhas de acordo com o humano]** Agora as duas linhas mais importantes do relatório. Acordo com o humano usando só a ordem A-B. Acordo com o humano usando só a ordem B-A. Dois números diferentes, para o mesmo juiz, o mesmo conjunto e a mesma rubrica. E a distância entre os dois é no máximo a taxa de inversão — isso é demonstrável e está em A.2. Qualquer relatório que rodou uma ordem só escolheu um desses dois números sem saber que estava escolhendo.

**6.** **[Rodo `python demo-judge-bias.py --protocolo`]** E aqui está o conserto barato: protocolo de dupla ordem. Julgo nas duas ordens, mantenho só os pares em que o vencedor não mudou, e trato o resto como empate. Olhem o preço, que a demo imprime junto: a cobertura cai para um menos a taxa de inversão, e o número de chamadas dobra. E os pares que eu joguei fora não são aleatórios: são exatamente os pares em que as duas respostas eram próximas, que são os informativos. Não existe conserto de graça.

**7.** **[Aponto o item 4 da lição impressa]** E agora o ponto que faz esta demo valer os dez minutos. Entre os pares em que o juiz **não** se contradisse, ele ainda discorda do humano em dois. E são os dois em que a resposta falsa era a mais plausível. Inversão posicional não explica esses dois. Nenhum protocolo de ordem conserta isso, porque não é problema de ordem: é o juiz pontuando plausibilidade porque ele não tem a fonte para conferir correção. Isso é o slide da factualidade, e é para lá que eu vou.

**8.** **[Se houver chave configurada, rodo `python demo-judge-bias.py --modo api`]** E se der, o mesmo experimento com um juiz de verdade. A chave sai de variável de ambiente ou de `getpass` — nunca do arquivo. Comparo a taxa de inversão do juiz real com a do sintético. Se o número real vier mais baixo, ótimo: é ele que vale, e o sintético serviu para mostrar o mecanismo.

---

## Parte 3 — Hands-on

Oito minutos, em dupla, no slide 4 — as quatro falhas de usuário e a atribuição de camada. O objetivo não é acertar a métrica: é forçar a tradução da queixa em linguagem natural para um número com denominador, e depois para um log que precisa existir.

**1.** **[Projeto as quatro falhas e formo as duplas]** Vou passar oito minutos com vocês trabalhando. Em dupla, e de preferência com alguém da própria equipe do projeto, porque o que sair daqui vai direto para o Lab 8. Quatro falhas no slide, escritas como o usuário reportaria. Para cada uma: a menor camada que explica, a métrica com denominador, e o dado que precisa estar logado para essa métrica existir.

As quatro falhas:

1. "Perguntei o prazo de trancamento fora do período e ele respondeu sobre trancamento total."
2. "A resposta cita o Art. 42, mas o Art. 42 não diz isso."
3. "O agente ficou dando voltas e parou sem responder."
4. "Está tudo certo, mas ninguém da secretaria usou depois da primeira semana."

*Como recolher:* cinco minutos de dupla, três de correção conduzida por mim. Não corrijo os quatro casos. Peço voluntário para o caso 1 porque é o que dá confiança **e porque ele fecha o slide 1** — a dupla acaba de reconstruir sozinha o número que a equipe da história não tinha. Gasto o tempo bom no caso 2 porque é o conceitualmente rico, e fecho no caso 4. Peço que a anotação das quatro linhas fique no repositório da equipe — ela é insumo do Checkpoint 2 do Lab 8, quando cada equipe tiver que escolher as métricas por camada do próprio sistema.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a derivação em aula. A regra geral é remeter ao apêndice e seguir; conduzir uma derivação só se sobrar tempo, e anunciando que é conteúdo de consulta.

**Item 1 — "Como é que 84% vira 0,11?" (A.1, ~5 min).**
A pergunta mais provável da aula, e a mais legítima — na V1 eu fazia essa conta no quadro por padrão. Se eu decidir fazer, é a tabela dois por dois: quarenta e um casos em que os dois disseram correta, quatro e quatro de desacordo, um em que os dois disseram incorreta. Acordo observado, quarenta e dois em cinquenta, zero vírgula oitenta e quatro. Marginais: os dois anotadores dizem "correta" em quarenta e cinco de cinquenta, ou seja noventa por cento. Acordo esperado: noventa por noventa mais dez por dez, dá zero vírgula oitenta e dois. E kappa é dois centésimos sobre dezoito centésimos, que dá zero vírgula onze. Cinco linhas.
Se não houver tempo nem para isso, a resposta curta é: "oitenta e dois dos oitenta e quatro pontos já eram explicados pelo fato de os dois dizerem 'correta' em nove de cada dez casos; sobraram dois pontos de dezoito disponíveis". A tabela completa e o caso balanceado estão em A.1.

**Item 2 — "Como eu sei que 0,71 e 0,78 são o mesmo número?" (Lab 8, ~3 min).**
Pergunta boa e a que eu mais quero adiar, porque a conta é do Lab 8 e lá ela vira código. A resposta de trinta segundos que resolve em sala: "com vinte casos, o erro-padrão de uma proporção perto de zero vírgula setenta é da ordem de dez pontos percentuais; sete pontos de diferença é menos que isso". Se a turma insistir por mais, eu escrevo a raiz de p vezes um menos p sobre n e ponho os números — e aviso que o teste **certo** não é esse, porque os dois sistemas rodaram nos mesmos casos e isso pede um teste pareado. Aí eu paro e remeto ao apêndice do Lab 8. Esse item é o que eu mais gosto de deixar em aberto: ele faz a turma chegar na Aula 28 querendo a resposta.

**Item 3 — "De onde vem esse meio mais metade da inversão?" (A.2, ~6 min).**
Raramente perguntam, e quando perguntam vale muito. Eu escrevo o modelo: cada resposta tem um escore, e quem aparece primeiro ganha um bônus fixo. Se a diferença de escore for maior que o bônus, o mesmo vence nas duas ordens; se for menor, vence quem aparece primeiro. Logo a taxa de inversão é a fração de pares em que a diferença é menor que o bônus. E a preferência pela primeira posição é a metade da soma de duas probabilidades que, sob simetria, colapsam na mesma — daí meio mais metade da inversão. Seis minutos, e o preço é o slide 15 inteiro.
Se não houver tempo, o argumento honesto é: a demo verificou a relação numericamente na frente de vocês, e a derivação está em A.2 — mas verificação numa amostra não é demonstração, e eu digo isso explicitamente.

**Item 4 — "Por que a média do BLEU é geométrica?" (A.3, ~4 min).**
Aparece quando alguém já usou BLEU em outra disciplina. A resposta curta: para que um n-grama de ordem alta zerado zere a nota inteira — palavras certas na ordem errada não é uma tradução parcialmente boa. Se eu quiser gastar quatro minutos, escrevo o produto das precisões elevadas aos pesos, mostro que com um `p` igual a zero o produto zera enquanto a média aritmética não zeraria, e menciono a suavização que existe justamente porque frases curtas têm `p₄` zero por construção. A penalidade de brevidade, com a verificação nos extremos, está em A.3.

**Item 5 — "Micro ou macro na precisão factual?" (A.4, ~3 min).**
Costuma vir de quem já está pensando no relatório. Resposta curta com o número: somar todas as afirmações num balaio só e somar as proporções de cada resposta dão resultados diferentes quando as respostas têm comprimentos diferentes — no exemplo de A.4, zero vírgula cinquenta e sete contra zero vírgula setenta e cinco, nos mesmos dados. A pergunta "que fração das afirmações do meu sistema é confiável" pede a primeira; "que fração das minhas respostas é boa" pede a segunda. O erro não é escolher: é não declarar.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 16 da Parte 1 — os quatro prejuízos e as quatro respostas, a dívida da Aula 1 quitada, a regra da menor camada com o `n` do lado de todo número, o índice do apêndice projetado por vinte segundos, as três coisas que cada equipe traz para o Lab 8, e a leitura do MMLU com a pergunta dirigida.

> Ideia central: "A dívida da Aula 1 não foi paga com uma métrica nova. Foi paga com uma regra: avaliar a menor camada que explica a falha. Semana que vem essa regra vira código, e o código é do projeto de vocês."

---

*Roteiro do Instrutor · Aula 27 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
