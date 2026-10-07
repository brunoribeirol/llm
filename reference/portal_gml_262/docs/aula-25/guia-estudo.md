# Laboratório 7: Construindo um agente autônomo

## Slide 1 · Abertura: hoje o agente é seu · 00:00–00:05

Boa noite, pessoal. Chegamos no lab mais importante do Módulo 5.

Deixa eu costurar de onde a gente vem. Na Aula 21 e no Lab 6 vocês deram mãos ao modelo: ele pede, o host executa, e vocês escreveram o host. Na Aula 23 eu dei a definição operacional de agente — modelo, ferramentas, loop, objetivo, critério de parada — e mostrei um loop de quarenta linhas para desmistificar. Na Aula 24 a gente foi cético com multiagente e eu fechei com "princípios antes de ferramentas", prometendo que o loop vem antes do framework.

Hoje eu cumpro a promessa. Vocês vão escrever o loop ReAct na mão: o contrato de formato, o parsing da ação, o despacho, a memória da trajetória, as paradas e o limite de passos. E o agente vai usar três ferramentas, e uma delas é **a base que vocês construíram no Lab 5** — aquele índice que vocês mediram o recall na Aula 20 vira uma linha do catálogo de ferramentas do agente de vocês.

No fim da aula vocês têm um agente que funciona, três trajetórias gravadas em JSON, e a análise escrita de uma delas: onde ele acertou, onde ele vacilou, quanto custou.

> Ideia central: "Na Aula 23 eu mostrei um loop de agente e disse que ele era pequeno. Hoje vocês vão descobrir que ele é pequeno *e* que as quatro coisas que mais dão errado nele são invisíveis."

---

## Slide 2 · Setup, o modo offline e os números deste lab · 00:05–00:11

Antes de qualquer código, duas coisas: o ambiente e um aviso que eu não quero que ninguém perca.

O ambiente é o mais leve do semestre. Os checkpoints 1 a 4 rodam com biblioteca padrão do Python, zero dependência, zero GPU. O que existe na pasta são três módulos auxiliares que eu já escrevi: `ferramentas.py` com as três ferramentas, `corpus_regulamento.py` com o acervo, e `llm.py`, que é o acesso ao modelo. O que é de vocês hoje é o **loop** — as ferramentas eu dei de graça de propósito, para o tempo de sala inteiro ir para o ciclo.

Agora o aviso. Se vocês tiverem chave de API, o `llm.py` chama o provedor de verdade; a chave entra por `getpass` e nunca é escrita no notebook. Se não tiverem — e a rede desta sala é o que é — ele cai num **simulador roteirado determinístico**, com semente vinte e cinco, que responde no formato ReAct segundo uma política que eu escrevi à mão. Ele roda sem internet e responde sempre igual, o que faz os testes serem reprodutíveis.

E é aqui que eu quero ser muito explícito, porque é a confusão que eu mais vejo: **o simulado serve para depurar o loop de vocês, não para avaliar o agente**. Ele não mede capacidade de modelo nenhum. Se vocês mudarem o prompt de sistema no modo offline, nada muda — o simulador não lê prompt. Toda conclusão do tipo "o agente escolheu bem a ferramenta" só vale com chave. O que o modo offline afere é se o **seu** loop está correto, e é para isso que ele existe.

Os números: três ferramentas, orçamento de seis passos, três perguntas de referência. E cinco checkpoints em duas horas.

**[Aponto o número seis do `max_passos`]**

E um comentário sobre esse seis, porque ele vai voltar no Checkpoint 4. Ele não é chute nem é superstição. Nas três perguntas de referência, o agente gasta três, dois e dois passos. O teto é o dobro do máximo observado — que é exatamente a regra que eu vou cobrar de vocês no projeto: o orçamento sai da distribuição medida, não do pior caso imaginado.

> Ideia central: "O simulador é um banco de testes do loop de vocês, não um modelo sob avaliação. Ele responde sempre igual — e é exatamente por isso que ele é útil."

---

## Slide 3 · O mapa: cinco checkpoints e o entregável · 00:11–00:15

Deixa eu desenhar o mapa, porque a pior coisa num lab é não saber onde a gente está. E eu vou apresentar cada checkpoint **pelo que ele imprime quando está certo**, porque é assim que vocês vão saber que terminaram.

Checkpoint um: o contrato. O prompt de sistema com três partes, o parser da ação e o despacho. Imprime `Checkpoint 1 OK`.

Checkpoint dois: o loop — memória, observação, três paradas e o limite de passos. Imprime `Checkpoint 2 OK`, e o teste dele cobre sete situações. Esses dois são os trinta minutos antes do intervalo.

Depois do intervalo, três checkpoints em trinta e cinco minutos. Checkpoint três: plugar o `chunks.json` do Lab 5 — imprime `Checkpoint 3 OK` mais a linha da fonte do corpus com o nome do arquivo de vocês.

Checkpoint quatro, que é o coração da entrega, e ele **não imprime linha de OK**: o critério dele é que existam **três arquivos JSON em disco** e uma tabela de custo com o acumulado crescendo. Mais a análise escrita.

Checkpoint cinco: refazer o mesmo agente num framework de grafo e comparar — o critério é a tabela das três perguntas nas duas arquiteturas mais três respostas escritas.

O que vocês me entregam: o notebook executado com as saídas visíveis, as três trajetórias em JSON, a tabela de custo, a análise escrita, a tabela de comparação do cinco, as respostas das cinco questões-guia e a declaração de uso de IA. Uma semana de prazo.

E eu vou ser franco sobre o peso: o item que separa as notas neste lab não é nenhum teste verde. É a análise escrita. Um agente funcionando é o mínimo; saber ler a trajetória dele e dizer **em que etapa** ele vacilou é o que eu estou ensinando.

> Ideia central: "Agente funcionando é o mínimo deste lab. O que separa as notas é a análise escrita de uma trajetória — porque saber ler a trajetória é o que se leva daqui."

---

## Slide 4 · [Demo] Live coding: o contrato de formato e o parser · 00:15–00:35

Vinte minutos agora comigo escrevendo, e vocês só olhando. Depois eu solto vocês.

Eu vou escrever duas coisas na frente de vocês: o prompt de sistema, com as três partes nomeadas em voz alta, e o parser da ação, construído contra quatro entradas ruins, uma por vez. E no fim eu vou rodar **uma volta** do loop na mão, sem `while` — e depois vou comentar uma linha e mostrar o agente esquecendo o que a ferramenta respondeu.

E dois números vão aparecer na tela nessa volta, e eu quero que vocês guardem os dois. O primeiro é o tamanho da chamada que só tem sistema mais pergunta: nas minhas execuções ele fica em torno de quinhentos e quarenta tokens de entrada. Esse é o **piso** — é o que custa perguntar qualquer coisa a este agente, antes de ele fazer nada. O segundo é o tamanho da chamada seguinte, depois de eu anexar a observação: ele sobe. Quanto ele sobe é decidido por qual ferramenta respondeu, e essa é a semente da tabela do Checkpoint 4.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> Ideia central: "Eu vou escrever o parser contra as entradas erradas primeiro. Parser que só foi testado com a entrada certa é uma armadilha esperando o dia da apresentação."

---

## Slide 5 · [Checkpoint 1] Prompt de sistema, parsing e despacho · 00:35–00:48

Agora é a vez de vocês. Treze minutos no Checkpoint 1.

**[Projeto o critério de conclusão antes de qualquer coisa]**

Quando estiver certo, a tela imprime `Checkpoint 1 OK`. E para imprimir isso, o teste vai ter conferido as três partes do prompt — incluindo a proibição explícita de o modelo escrever `Observation:` — mais o caminho feliz da ação e o da resposta final, mais **quatro entradas malformadas**: prosa sem formato nenhum, JSON quebrado, `Action Input` ausente, e nome de ferramenta entre cercas de código. E, no despacho, ferramenta inexistente e argumento inválido voltando como dicionário de erro em vez de exceção.

**[Aponto os três TODOs]**

Três TODOs. O primeiro é o `SISTEMA`, e ele tem exatamente três partes: objetivo, catálogo de ferramentas interpolado do `ferramentas.py`, e formato — que inclui como encerrar. Mais as três regras: uma ação por vez, nunca escrever `Observation:`, e não usar `Final Answer` sem ter uma observação que sustente.

Aquela regra do meio é a que parece boba e não é. Se o modelo não é interrompido, ele completa o padrão sozinho e escreve a própria `Observation:` — e aí o loop de vocês passa a raciocinar sobre um resultado que ferramenta nenhuma produziu. Duas defesas: a regra no prompt e a sequência de parada na chamada da API, que já está no `llm.py`.

O segundo TODO é o `parsear_acao`. Ele devolve sempre o mesmo dicionário — pensamento, ação, argumentos, resposta final, erro — e ele **nunca levanta exceção**. Isso é decisão de projeto: erro de formato é informação, não crash. Se o parser estourar, a trajetória inteira morre e vocês perdem a única evidência que tinham.

O terceiro é o `executar`, que é o despacho: nome no registro, chamada, e erro de ferramenta desconhecida ou de argumento inválido voltando como dicionário.

*[A condução completa está na Parte 3 deste roteiro.]*

> Ideia central: "Erro de formato volta como observação, nunca como exceção. Parser que estoura derruba a trajetória — e a trajetória é a única evidência que a gente tem."

---

## Slide 6 · [Checkpoint 2] O loop: memória, observação e parada · 00:48–01:05

Dezessete minutos e o checkpoint mais importante dos cinco. Aqui vocês escrevem o loop.

**[Projeto o critério]**

A tela vai imprimir `Checkpoint 2 OK`, e o teste vai ter conferido **sete** situações. Duas ferramentas em sequência, com citação e conta certa. Uma ferramenta bastando. Encerramento honesto quando o acervo não tem a resposta. Repetição abortando. Orçamento segurando antes de o detector de repetição agir. Formato inválido voltando como observação e o loop se recuperando na volta seguinte. E a sétima, que é a que eu mais quero que vocês vejam: o loop rodado com `devolver_observacao` igual a falso, em que o agente esquece a observação e a trajetória termina em repetição.

**[Aponto as duas estruturas lado a lado, com os leitores rotulados]**

A estrutura é: monta `mensagens` com sistema e pergunta, entra no `while`, chama o modelo, acumula o custo, parseia, registra o passo na trajetória, executa a ferramenta, **anexa a observação a `mensagens`**, e volta.

Duas estruturas convivem no loop e elas têm leitores diferentes. `mensagens` é a memória de curto prazo: é o que **o modelo lê** na volta seguinte. `trajetoria` é o registro estruturado: é o que **um humano audita** depois — e é literalmente o assunto da próxima aula. Se vocês confundirem as duas, ou o modelo esquece, ou o contexto explode.

E aí o erro que eu quero que vocês sintam na pele. Se vocês registram a observação na trajetória e esquecem de anexá-la a `mensagens`, **nada quebra**. Nenhum teste de formato falha. O agente simplesmente esquece o que a ferramenta respondeu, e o sintoma que aparece é a mesma ação repetida com o mesmo argumento, volta após volta. Do ponto de vista do modelo, a pergunta continua sem resposta — ele está fazendo a coisa certa. O bug é seu.

**[Aponto os três cadeados nas saídas do diagrama]**

Sobre as paradas: são três, e cada uma cobre um defeito diferente. Orçamento de passos pega o loop que não converge — e o limite de passos não é defensividade, é decisão de produto: ele fixa o teto de custo e o teto de espera do usuário. Resposta final pega o encerramento, mas com uma condição: não basta o modelo escrever `Final Answer`, tem que existir pelo menos uma observação de **ferramenta executada** na trajetória. Sem isso, é parada precoce — resposta plausível, sem fundamento, que é o erro perigoso da Aula 23. E o detector de repetição pega o agente preso: mesma ação, mesmo argumento, duas voltas seguidas.

E tem uma assimetria entre as três que vale nomear: só **uma** delas garante que o loop termina. O orçamento é um contador, e ele desce independentemente do que o modelo faça. As outras duas são saídas antecipadas: uma protege a qualidade da resposta, a outra protege o bolso quando o agente está preso. Quem remove o orçamento remove a única garantia de terminação que existe no código.

Um detalhe fino que quase todo mundo erra: a mensagem que o **próprio loop** injeta cobrando fundamento não pode contar como observação. Se contar, a parada precoce se autoautoriza na volta seguinte, e a proteção vira decoração.

*[A condução completa está na Parte 3 deste roteiro.]*

> Ideia central: "Uma parada que nunca dispara é indistinguível de não ter parada. É por isso que o teste liga um defeito para cada uma delas."

---

## Slide 7 · [Checkpoint 3] A base do Lab 5 vira ferramenta · 01:15–01:24

Voltando do intervalo. Nove minutos, e este checkpoint é o mais curto e o mais simbólico do lab.

**[Projeto o critério]**

O critério é `Checkpoint 3 OK` mais uma linha muito específica na tela: a fonte do corpus nomeando o `chunks.json` de vocês, com a contagem de chunks. E, na trajetória, ao menos um passo `buscar_regulamento` com `achados` não vazio sustentando a resposta.

Na Aula 20, no Lab 5, vocês montaram um pipeline de recuperação completo: chunking, embedding, busca híbrida, e mediram o recall dele. O acervo era o assunto da aula inteira.

Hoje ele é **uma linha do catálogo de ferramentas**: `buscar_regulamento`, termo e k. E o gancho é literal, não metafórico: se existir um `chunks.json` na pasta deste lab — o arquivo que o notebook do Lab 5 gravou em `lab05_saida/` — o `corpus_regulamento.py` usa ele em lugar do corpus embutido. Copiaram o arquivo, reexecutaram a célula de setup, e o agente passa a consultar a base de vocês.

E se vocês quiserem ir além: trocar o corpo da função `buscar` pelo pipeline híbrido do Lab 5 também não muda nada para quem chama. A assinatura é a mesma. Esse é todo o ponto — a ferramenta é uma fronteira, e do lado de fora dela o agente não sabe nem se importa se atrás tem BM25, embedding ou um `if`.

Quem não tiver o arquivo hoje, sem drama: o corpus embutido tem oito dispositivos e fecha os outros checkpoints. O que eu exijo é que vocês **declarem no notebook** com qual base os números foram produzidos. Isso é higiene de relatório e vai voltar em cima de vocês no projeto final.

Uma coisa que eu quero cravar antes de soltar: base boa não conserta agente. A qualidade da recuperação define o teto do que o agente consegue responder e não arruma nenhuma das cinco peças. Agente com base excelente e parada mal projetada continua respondendo sem fundamento, com mais fluência.

E um aviso de custo, que vale para o Checkpoint 4: se a base de vocês tem chunks longos, a observação fica grande, e observação grande é reenviada em todas as voltas seguintes. O custo por passo vai subir de forma visível na tabela. Isso é **achado**, não bug — e é material bom para a análise escrita.

> Ideia central: "O acervo que foi a aula inteira do Lab 5 hoje é uma linha do catálogo de ferramentas. Nada aqui é descartável — o semestre é um sistema sendo montado."

---

## Slide 8 · [Checkpoint 4] Registrar e analisar a trajetória · 01:24–01:38

Quatorze minutos, e este é o checkpoint que vale mais na nota.

**[Projeto o critério, que aqui não é linha de OK]**

O critério deste checkpoint são **três arquivos em disco** — `trajetoria_p1`, `p2` e `p3`, em JSON, cada um com todos os campos por passo e com o bloco de custo no fim — mais a tabela de custo impressa, com a coluna do acumulado **estritamente crescente**, mais a análise escrita.

Duas funções e um texto. A primeira função grava a trajetória completa em JSON: por passo, o pensamento, a ação, os argumentos, a observação, o erro de formato se houve, **o texto cru que o modelo devolveu**, e os tokens de entrada e de saída. A segunda monta a tabela de custo: passo, ação, tokens de entrada, tokens de saída, acumulado.

Por que o texto cru? Porque é lá que vocês vão ver que o modelo tentou escrever a própria `Observation:`, ou que ele emitiu duas ações no mesmo turno. Se vocês logam só o que "interessa", o defeito fica de fora exatamente quando ele importa.

**[Aponto a coluna do acumulado e a seta do último passo]**

Quando essa tabela sair, dois padrões aparecem sempre. O prompt de sistema é a maior parcela **fixa** do custo. E os tokens de entrada crescem monotonicamente, porque a trajetória inteira é reenviada a cada volta — o último passo é o mais caro de todos. E notem: aquele crescimento não é resultado experimental, é **consequência**. Se o acumulado de alguém não estiver crescendo, é defeito de contabilidade, não descoberta.

E tem uma coisa contraintuitiva aqui, que eu vou dar de graça porque ela muda como vocês vão ler a tabela: em agente, quase todo o custo é **entrada**. Nas três trajetórias que eu rodei, noventa e quatro por cento de todos os tokens são de entrada. O modelo escreve pouco e lê muito.

**[Aponto as cinco etapas em fila]**

E agora o texto, que é o entregável de verdade. Eu quero quatro parágrafos sobre **uma** trajetória. Onde o agente acertou. Onde ele vacilou. Quanto custou. E o que isso muda no projeto de vocês.

E tem um requisito na parte do "onde vacilou" que eu vou cobrar na correção: eu não aceito "errou a resposta". Eu quero **a etapa**. Foi percepção — ele entendeu outra pergunta? Foi escolha de ferramenta — chamou a errada? Foi argumento — chamou a certa com parâmetro ruim? Foi interpretação da observação — a ferramenta trouxe o dado certo e ele leu errado? Ou foi parada — encerrou cedo, ou não encerrou? Cinco etapas. Eu quero uma delas nomeada, o passo e a observação concretos citados, e a frase seguinte dizendo o que muda.

E no parágrafo do "quanto custou": eu quero número, não adjetivo. Passos, tokens de entrada, tokens de saída, e o custo por tarefa. E aí tem uma decisão que vocês vão ter de tomar e declarar, e eu adoro essa pergunta: a pergunta que o agente respondeu com "não encontrei essa informação" conta como tarefa resolvida ou como falha? Os dois números são diferentes, e a escolha do denominador decide se a métrica de vocês premia ou pune a recusa honesta. Está tudo trabalhado no A.1, com os números das minhas trajetórias.

Se a trajetória de vocês estiver limpa e não tiver vacilo nenhum, vale olhar melhor. Nas três perguntas de referência tem pelo menos um lugar em que o agente responde certo por menos razão do que parece.

> Ideia central: "Eu não aceito 'o agente errou'. Eu quero a etapa: percepção, ferramenta, argumento, interpretação ou parada. Cinco lugares onde a falha pode estar, e a resposta final é fluente em todos os cinco."

---

## Slide 9 · [Checkpoint 5] O mesmo agente num framework · 01:38–01:50

Doze minutos, o último checkpoint, e ele fecha a promessa da Aula 24: princípios antes de ferramentas.

**[Projeto o critério]**

O critério é a tabela das três perguntas nas duas arquiteturas — chamadas, tokens, parada — mais três respostas escritas. Quem não conseguir instalar a biblioteca entrega a tabela de referência que eu rodei na véspera mais as três respostas fundamentadas na leitura dos três nós.

Vocês vão refazer o mesmo agente como um grafo de estado. Três peças: um nó do modelo, um nó de ferramenta, e uma aresta condicional — que é onde o critério de parada mora num grafo.

E para a comparação ser honesta, três coisas ficam **idênticas**: o mesmo modelo, as mesmas ferramentas, o mesmo prompt de sistema. Se eu troco qualquer uma delas, o que eu meço é a troca, não o framework.

O que o framework entrega: estado declarado em vez de variáveis locais, roteamento explícito, ponto de interrupção, retentativa padronizada. O que ele **não** entrega, e eu quero que vocês vejam isso no código: validação de argumento, tratamento de erro de ferramenta, e critério de parada de domínio. Isso continua sendo escrito por vocês, dentro dos nós. O framework organiza chamadas; ele não decide nada.

E uma coisa que a tabela vai mostrar e que vale comentar: se os tokens das duas arquiteturas baterem, isso é a **confirmação** de que a comparação está controlada. Se não baterem com o mesmo modelo, as mesmas ferramentas e o mesmo prompt, alguma coisa está diferente no que se manda — e o suspeito número um é o framework acrescentando texto ao prompt sem vocês pedirem.

Três perguntas escritas no fim: qual peça o framework assumiu, qual continuou sua, e — a que decide, e é o critério da Aula 24 — onde é que se lê a trajetória inteira de uma execução nesse framework? Se a resposta não estiver na documentação, isso é um achado sobre o framework, e vale escrever.

> Ideia central: "Mesmo modelo, mesmas ferramentas, mesmo prompt. Se os números baterem, a diferença entre as duas versões é só controle e conveniência — e essa é a comparação que eu quero que vocês saibam fazer."

---

## Slide 10 · Recolhimento e ponte para a Aula 26 · 01:50–02:00

Deixa eu fechar e mandar vocês para casa.

O que vocês têm agora, e eu quero que fique registrado: vocês escreveram um contrato de formato, um parser tolerante a falha, um loop com memória e três paradas, um limite de passos, três ferramentas plugadas — uma delas a base que vocês mesmos construíram — trajetórias gravadas em JSON, custo medido por passo, e a mesma coisa refeita num framework. Isso é um agente, inteiro, e é de vocês.

A entrega: notebook executado com as saídas visíveis, as três trajetórias em JSON, a tabela de custo, a análise escrita de uma trajetória, a tabela de comparação do CP5, as respostas das cinco questões-guia e a declaração de uso de IA. Uma semana. E das cinco questões, a que eu vou ler com mais atenção é a que pergunta o que aconteceria se vocês removessem exatamente a parada que disparou.

**[Projeto o índice do apêndice por 20 s]**

Três itens, e eu nomeio dois. O **A.1** é a contabilidade das três trajetórias de referência, número por número — passos, tokens, custo por tarefa resolvida — e é o gabarito de leitura para o parágrafo do "quanto custou". E o **A.3** é a tabela das três paradas: o que cada uma protege, e o que aparece na trajetória quando você remove cada uma. Essa é literalmente a resposta escrita da questão-guia que eu acabei de dizer que vou ler com mais atenção.

Agora a ponte, e ela é desconfortável de propósito. Vocês passaram duas horas dando autonomia a um programa: ele decide qual ferramenta chamar, com que argumento, e quando parar. E ele decide isso lendo texto. Vale parar um segundo no que vocês acabaram de construir: um sistema em que **o dado que volta da ferramenta entra no mesmo canal em que as instruções entram**. A observação que o `buscar_regulamento` devolveu foi para o contexto do modelo exatamente como a minha instrução foi.

O que acontece se alguém puser uma instrução dentro de um documento do acervo?

Isso é a próxima aula. Segurança e avaliação de agentes: injeção de prompt direta e indireta, exfiltração, ação irreversível, e as mitigações — junto com a outra metade, que é como se avalia um agente quando a falha pode estar em cinco etapas diferentes. Eu vou pegar o agente que vocês construíram hoje e sequestrar ele ao vivo, com um documento envenenado no acervo, e depois mostrar a mitigação funcionando.

E lembrete: a **Entrega 2 do projeto é na próxima aula**. Checkpoint, quinze minutos reservados. Eu vou querer ver o pipeline central de vocês rodando de ponta a ponta, mesmo simples e mesmo feio.

> Ideia central: "Vocês acabaram de construir um sistema em que o dado que volta da ferramenta entra no mesmo canal das instruções. Na próxima aula eu sequestro o agente de vocês com um documento do próprio acervo."

---

## Parte 2 — Demonstração guiada

Vinte minutos, live coding, tudo offline. O objetivo não é adiantar o Checkpoint 1 — é fazer a turma ver que o contrato de formato e o parser são pequenos, e sentir o erro silencioso da observação antes de escrever o loop. Eu escrevo em células novas no fim do notebook e apago depois: o TODO do aluno continua sendo o TODO do aluno.

Insumos da véspera: o notebook rodado nos dois modos com os números anotados; as saídas dos quatro defeitos roteirados salvas em texto; o meu `chunks.json` do Lab 5 na pasta.

**1.** **[Abro `ferramentas.py` e imprimo `catalogo_em_texto()`]** Antes do prompt, olha aqui o que o modelo vai ler sobre as ferramentas. São três linhas de texto. Não é documentação para vocês — é o texto que o modelo lê para decidir qual ferramenta chamar. Repararam que a descrição do `calcular` diz "passe a conta pronta, nunca a pergunta em português"? Aquela frase está ali porque sem ela o modelo passa a pergunta inteira e a ferramenta rejeita. Descrição de ferramenta é prompt, e isso é do Lab 6.

**2.** **[Escrevo o `SISTEMA` na tela, parte por parte, dizendo o nome de cada uma]** Agora o contrato. Primeira parte: objetivo — responder com fonte verificável, citando o dispositivo, e fazendo conta com a ferramenta em vez de de cabeça. Segunda parte: o catálogo, interpolado do arquivo que eu acabei de mostrar. Terceira parte: formato, e ele tem duas formas — uma para agir, com `Thought`, `Action` e `Action Input`; outra para encerrar, com `Thought` e `Final Answer`. E três regras no fim. E olhem o tamanho disso: esse texto todo vai em **toda** chamada, e é ele que faz o piso de quinhentos e quarenta tokens que eu vou mostrar daqui a pouco.

**3.** **[Aponto a regra do meio: nunca escrever `Observation:`]** Esta regra parece burocracia e não é. Se eu não interromper o modelo, ele completa o padrão sozinho: escreve a ação **e** escreve a observação que ele imagina que a ferramenta devolveria. E aí o loop passa a raciocinar sobre um resultado que ferramenta nenhuma produziu, com a mesma fluência. Duas defesas: esta regra, e a sequência de parada na chamada da API — que está lá no `llm.py`, na constante `PARADAS`. Aquele `stop` não é economia de token, é correção.

**4.** **[Chamo `llm.chamar_modelo` com o sistema e a pergunta do trancamento, e imprimo o texto cru]** Olha o que voltou. Três linhas: pensamento, ação, entrada da ação. Isso não é prosa, é protocolo — e é por isso que o parser é um parser e não uma interpretação. E olha o número de tokens de entrada desta chamada: quinhentos e quarenta e nove, na minha execução. Anotem esse número no canto do caderno — é o piso.

**5.** **[Escrevo `parsear_acao` incrementalmente, testando contra quatro entradas, na ordem]** Agora eu escrevo o parser, mas eu vou escrever ele contra as entradas **erradas** primeiro. Entrada um, bem formada: tira o pensamento, tira o nome da ação, tira o JSON. Entrada dois, prosa sem formato nenhum: o modelo escreveu um parágrafo bonito e nenhuma linha `Action:`. Entrada três, JSON quebrado. Entrada quatro, o nome da ferramenta entre crases de markdown, porque modelo adora fazer isso.

**6.** **[Imprimo o dicionário devolvido em cada um dos quatro casos]** E olha o padrão: a função devolve **sempre** o mesmo dicionário, com as mesmas cinco chaves. Nos casos ruins, a chave `erro` está preenchida. Ela nunca levanta exceção. Isso é decisão de projeto e eu quero justificar: erro de formato é uma coisa que o modelo consegue corrigir na volta seguinte, se ele for informado. Exceção não informa ninguém — ela derruba a trajetória, que é a única evidência que a gente tem.

**7.** **[Despacho a ação parseada com `executar` e imprimo a observação]** Ação parseada, agora despacha. O `executar` procura o nome no registro e chama. Olha a observação que voltou: um dicionário com os dispositivos achados e a fonte. Repararam que o Art. 42 tem o prazo de trinta dias corridos? Esse número vai virar conta no passo seguinte. E olhem o **tamanho** dessa observação, porque é ele que vai decidir quanto a próxima chamada custa.

**8.** **[Anexo a observação a `mensagens` como `Observation: {…}` e chamo o modelo de novo, na mão]** E agora o loop, feito uma vez, sem `while`. Eu anexo a resposta do modelo como mensagem do assistente, anexo a observação como mensagem do usuário com o prefixo `Observation:`, e chamo o modelo de novo. Olha a segunda resposta: outra ação, `calcular`, com trinta menos doze. Ele leu a observação, tirou o prazo de lá e montou a conta. Isso é o ciclo da Aula 23 acontecendo em três linhas de código. E olha o segundo número de entrada, ao lado do primeiro: quinhentos e quarenta e nove virou setecentos e setenta e dois. Duzentos e vinte e três tokens a mais, e eles são a observação que eu acabei de anexar. A pergunta é a mesma; o que cresceu foi o histórico.

**9.** **[Comento a linha do `append` da observação e repito a chamada]** Agora o passo que eu mais quero que vocês vejam. Eu vou comentar **uma linha** — a que anexa a observação a `mensagens` — e chamar de novo. Olha o que voltou: `buscar_regulamento`, com o mesmo argumento. Outra vez. Nada quebrou, nenhum erro apareceu, o parser está perfeito. O agente simplesmente não sabe que a ferramenta respondeu, porque quem respondeu foi para um lugar que ele não lê. Do ponto de vista dele, ele está fazendo a coisa certa. E é por isso que "meu agente fica repetindo" quase nunca é problema de prompt.

**10.** **[Fecho o notebook de demo sem escrever o `while`]** E eu paro aqui, de propósito. O `while`, as três paradas e o limite de passos são de vocês. Eu já dei a dica que importa: a observação tem que voltar.

---

## Parte 3 — Hands-on

Cinco checkpoints. Eu circulo pela sala olhando tela, não esperando pergunta — e neste lab isso é mais importante que nos outros, porque os quatro erros que a gente caça hoje são silenciosos. Ninguém diz "esqueci de devolver a observação". A pessoa diz "está repetindo".

**1.** **[Lanço o Checkpoint 1 — contrato, parser e despacho, 00:35–00:48]** Treze minutos. O critério é a linha `Checkpoint 1 OK`. Três TODOs: o `SISTEMA` com três partes e três regras, o `parsear_acao` que nunca levanta exceção, e o `executar` que trata ferramenta desconhecida e argumento inválido como erro de dicionário. Quando terminarem, a célula do teste roda e imprime o OK — ou falha dizendo qual das verificações não passou.

*Como recolher:* aos 00:46 eu pergunto quantos têm o `Checkpoint 1 OK` impresso, por mão levantada. Se for menos de dois terços, eu paro a sala e resolvo na tela **só o TODO do parser**, e só a parte do `Action Input`, porque é onde a maioria trava. Aos 00:48 eu libero a célula de solução comentada e sigo, porque o CP2 depende disso e ninguém pode ficar preso aqui.

**2.** **[Lanço o Checkpoint 2 — o loop, 00:48–01:05]** Dezessete minutos, e é o coração técnico do lab. O critério é `Checkpoint 2 OK`, com as sete situações do teste. O `loop_react` com a memória, a observação devolvida, as três paradas e o limite de passos. E uma ajuda antes de soltar: o caminho mais rápido é escrever o loop **sem** parada nenhuma primeiro, rodar, ver o orçamento estourar, e só então acrescentar as paradas uma por uma. Ver o defeito antes de escrever a defesa é a metade do aprendizado.

*Como recolher:* o teste é o recolhimento — sete situações, e a sétima roda o loop com a observação deliberadamente não devolvida. Aos 01:03 eu pergunto quem tem os dois `OK`. Quem já terminou, eu mando ler o `llm.py` e achar a constante `PARADAS`, e me dizer por que ela existe. Aos 01:05 eu libero a solução junto com o intervalo. Se aparecer a pergunta "por que três paradas", resposta curta da Parte 4 e o ponteiro para o A.3.

**3.** **[Lanço o Checkpoint 3 — a base do Lab 5 como ferramenta, 01:15–01:24]** Nove minutos, e é logística mais do que código. O critério é `Checkpoint 3 OK` mais a linha da fonte do corpus nomeando o arquivo deles. Copiar o `chunks.json` do Lab 5 para a pasta deste lab, reexecutar a célula de setup, conferir a linha da fonte do corpus, e rodar o agente na pergunta da monitoria — que só o acervo responde.

*Como recolher:* a linha da fonte do corpus impressa e o `Checkpoint 3 OK`. Quem estiver com o corpus embutido, eu peço que escreva a frase de declaração na hora, na célula de markdown, e sigo — não vale gastar cinco minutos procurando arquivo em nuvem. Fecho perguntando à sala: se eu trocar a busca por termos pelo pipeline híbrido de vocês, o que muda para o agente? A resposta certa é "nada", e ela é o ponto.

**4.** **[Lanço o Checkpoint 4 — registrar e analisar, 01:24–01:38]** Quatorze minutos, e é o checkpoint que vale mais. O critério são os três JSON em disco, a tabela de custo com o acumulado crescendo, e o texto. Duas funções — a tabela de custo e a gravação em JSON — e a análise escrita de **uma** das três trajetórias.

*Como recolher:* três JSON em disco, a tabela de custo com o acumulado crescendo, e o texto. Eu leio em voz alta um parágrafo da minha análise de referência — só o do "onde vacilou" — para calibrar o nível. E eu circulo perguntando uma coisa só: qual etapa? Se a resposta for "a resposta", eu devolvo as cinco etapas e sigo. Se alguém tiver acumulado não crescente, é bug de contabilidade e eu digo isso na hora: o crescimento é consequência, não medição.

**5.** **[Lanço o Checkpoint 5 — o mesmo agente num framework, 01:38–01:50]** Doze minutos. O critério é a tabela das três perguntas nas duas arquiteturas mais as três respostas escritas. Quem tem `langgraph` instalado roda o grafo e preenche a tabela; quem não tem vai direto para a variante de leitura. Não gastem esses doze minutos com `pip`.

*Como recolher:* a tabela com as três perguntas nas duas arquiteturas e as três respostas escritas. Se o tempo estourou, este checkpoint vai para casa e eu digo isso explicitamente — os quatro primeiros são o núcleo. Fecho com a pergunta que eu quero na cabeça deles na Aula 26: se vocês só tivessem a resposta final de cada uma dessas execuções, e não a trajetória, o que vocês **não** conseguiriam dizer sobre o agente?

---

## Parte 4 — Apêndice: se perguntarem

Em laboratório eu **não conduzo derivação no quadro** — o tempo é do teclado. O que esta parte traz são as respostas de trinta segundos, com o custo em minutos da versão longa caso a sala esteja adiantada, e o item que responde por escrito.

**Item 1 — "Por que os tokens de entrada crescem a cada passo? Isso não é bug?" (A.2, 30 s · 3 min no quadro).**
A pergunta mais provável do lab, e ela é ótima porque a resposta é uma consequência e não uma medição. **Resposta curta:** "não é bug, é o desenho. O modelo não guarda estado entre chamadas: em cada volta o loop de vocês reenvia a lista de mensagens **inteira**. Então a chamada três manda o sistema, a pergunta, e tudo o que aconteceu nas voltas um e dois. Por isso o último passo é sempre o mais caro, e por isso o total de tokens enviados cresce mais rápido que o número de passos. Se o acumulado de alguém **não** estiver crescendo, aí sim é bug — de contabilidade." A derivação está em **A.1 da Aula 23**; o que este lab acrescenta, com os números medidos, está em **A.2**. Se a sala estiver adiantada, três minutos no quadro escrevendo as três chamadas uma embaixo da outra fecham a questão para sempre.

**Item 2 — "Quanto custa esse agente, afinal?" (A.1, 30 s).**
Aparece quando a tabela sai. **Resposta curta:** "nas minhas três trajetórias de referência: sete chamadas no total, quatro mil quinhentos e oitenta e três tokens de entrada e duzentos e noventa e quatro de saída. Noventa e quatro por cento é entrada — em agente o modelo lê muito e escreve pouco. Isso dá em torno de mil e seiscentos tokens por tarefa resolvida, e a faixa entre a mais barata e a mais cara é de mil duzentos e sessenta e oito a dois mil duzentos e quarenta e três: quase o dobro. Reportar a média sem a faixa esconde um fator de dois." E a pergunta que eu devolvo: a pergunta que o agente respondeu com "não encontrei" conta como resolvida? O número muda de mil e seiscentos para dois mil e quatrocentos dependendo da resposta, e a escolha decide se a métrica premia ou pune a recusa honesta. Tudo em **A.1**.

**Item 3 — "Três paradas não é exagero? O orçamento não resolve tudo?" (A.3, 30 s · 4 min no quadro).**
Aparece no CP2 e é a melhor pergunta que o lab recebe. **Resposta curta:** "o orçamento é a única que garante que o loop termina — as outras duas não são redundância, são propósitos diferentes. Sem a parada de resposta fundamentada, o agente responde bonito sem ter olhado nada, e o orçamento não pega isso porque ele para **antes** de estourar. Sem o detector de repetição, o agente preso queima o orçamento inteiro em vez de abortar na segunda volta — nos números deste lab, é a diferença entre dois mil e cinco mil e trezentos tokens gastos para não responder nada. Cada parada cobre um defeito que as outras duas não veem." A tabela completa, com o que aparece na trajetória quando cada uma é removida, está em **A.3**.

## Ordem de sacrifício

Se o lab atrasar: o **CP5 vai para casa** primeiro — ele é o de menor peso (10%) e a variante de leitura é entregável sozinha. Depois, corto as etapas 5 e 6 da demo pela metade, porque o parser incremental pode ser lido do slide. **Não corto** a etapa 9 da demo, que é o `append` comentado e a repetição acontecendo na tela — sem ela o Checkpoint 2 vira adivinhação. E **não corto o CP4 em nenhuma hipótese**: ele vale 40% da nota entre as trajetórias e a análise escrita, e é o único item deste lab que não tem substituto em casa, porque a calibragem do nível esperado acontece quando eu leio a minha análise de referência em voz alta. Se for preciso escolher entre o CP5 e dez minutos a mais no CP4, o CP5 perde.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 10 da Parte 1 — o inventário do que a turma construiu, o checklist de entrega com prazo de uma semana, os vinte segundos de índice do apêndice nomeando o A.1 e o A.3, o aviso da Entrega 2 do projeto na próxima aula, e a ponte para a Aula 26 pela observação de que o dado que volta da ferramenta entra no mesmo canal das instruções.

> Ideia central: "Vocês construíram um agente que decide o que chamar e quando parar, lendo texto. Na próxima aula eu mostro o que acontece quando alguém escreve uma instrução dentro de um documento do acervo — e como a gente se defende, sabendo que não resolve."

---

*Roteiro do Instrutor · Aula 25 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
