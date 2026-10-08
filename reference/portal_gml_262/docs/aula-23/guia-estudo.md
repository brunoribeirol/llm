# Agentes de IA: loops, planejamento e memória

## Slide 1 · Abertura: vocês já deram mãos ao modelo · 00:00–00:05

Boa noite, pessoal. Aula passada foi o Lab 6, e eu quero começar recuperando exatamente onde a gente parou, porque hoje é continuação direta.

No Lab 6 vocês escreveram o host do ciclo de ferramentas na mão: o schema que o modelo lê, a validação antes de despachar, o `REGISTRO` que amarra nome a função, o resultado voltando como mensagem `tool`, e a síntese. Depois vocês fizeram a mesma coisa pelo protocolo, com um cliente MCP e um servidor de vocês. E eu recolhi a Entrega 1 do projeto.

Só que tem uma coisa que o Lab 6 fez de propósito e eu não comentei: no fim do Checkpoint 2 vocês escreveram um `while`. Um `while` com orçamento de passos. Aquele laço de cinco linhas é a fronteira entre um programa que chama ferramenta e um agente — e a aula de hoje é sobre aquele laço.

> Ideia central: "No Lab 6 vocês deram mãos ao modelo. Hoje a gente dá um loop e um objetivo — e é isso, literalmente isso, que transforma tool calling em agente."

## Slide 2 · A definição operacional · 00:05–00:10

Deixa eu cravar uma definição antes de qualquer coisa, porque "agente" é uma das palavras mais gastas desta área e eu não quero passar duas horas discutindo vocabulário.

Agente é **modelo mais ferramentas mais loop mais objetivo mais critério de parada**. Cinco peças. Não é uma definição filosófica, é um checklist — e ele funciona pela subtração. Tira o loop: sobra o tool calling da Aula 21, uma ida e uma volta. Tira as ferramentas: sobra um modelo raciocinando sozinho, que é a cadeia de pensamento da Aula 13. Tira o objetivo: sobra um chat, que responde o que vem e não persegue nada. E tira o critério de parada: sobra uma conta de API crescendo enquanto vocês dormem.

Essa lista vai voltar três vezes hoje. Agora, como definição. No meio da aula, quando eu abrir um arquivo de quarenta linhas e apontar as cinco peças no código com o cursor. E no fim, como checklist que vocês vão aplicar ao projeto de vocês.

A analogia que eu uso é motor, carro e viagem. O modelo é o motor. As ferramentas são as rodas — sem elas o motor gira e nada anda. O loop é o acelerador. O objetivo é o destino. E o critério de parada é saber que chegou. Sem o último, o carro anda até o tanque acabar, e o tanque aqui é o cartão de crédito de alguém.

> Ideia central: "Agente é modelo, ferramentas, loop, objetivo e critério de parada. Cinco peças. Guardem essa lista, porque ela é o único slide que eu vou repetir três vezes hoje."

## Slide 3 · O ciclo: observar, planejar, agir, refletir · 00:10–00:18

Agora o que acontece dentro de uma volta do loop. Quatro momentos, e eu quero que vocês consigam identificar os quatro numa saída de terminal, porque no Lab 7 vocês vão ler exatamente isso.

**Observar** é ler o estado. Na primeira volta, o estado é a pergunta. Na terceira volta, o estado é a pergunta mais tudo o que as ferramentas devolveram até ali. **Planejar** é decidir o próximo passo — e num agente de texto isso é literalmente uma linha começando com "Thought". **Agir** é emitir a ação: nome da ferramenta, argumentos. E **refletir** é julgar o que voltou antes de decidir a próxima volta.

Essa última é a que a turma costuma achar mística, então deixa eu desmistificar agora. Refletir, em implementação, é uma pergunta a mais no prompt sobre o resultado que acabou de chegar. Não é um módulo novo, não é uma arquitetura nova, é um turno a mais de conversa. E por isso ela custa: cada reflexão é uma chamada de API que alguém paga.

A analogia mais honesta é o laço de vocês depurando código. Vocês leem o erro, formam uma hipótese, executam um teste, leem o resultado, e decidem se a hipótese sobreviveu. Ninguém chama isso de inteligência artificial quando é vocês fazendo. É o mesmo laço.

> Ideia central: "Refletir não é um módulo místico: é um turno a mais de conversa sobre o resultado que acabou de chegar. E turno a mais custa dinheiro."

## Slide 4 · ReAct: intercalar raciocínio e ação · 00:18–00:28

A leitura de hoje é um artigo de 2022 do Yao e colegas, o ReAct, e o achado dele é bonito de simples: raciocinar **e** agir alternadamente vence cada uma das duas coisas isoladamente.

Pensem no que dá errado em cada extremo. Só raciocinar é a cadeia de pensamento da Aula 13: o modelo produz um encadeamento lindo sobre fatos que ele não tem, e erra com convicção — cada passo do raciocínio é plausível e o conjunto está errado porque a premissa era inventada. Só agir é o oposto: o modelo dispara chamadas de ferramenta sem nunca articular por que aquela ferramenta e com que argumento, e quando o resultado volta ele não sabe o que fazer com ele.

Intercalando, duas coisas acontecem ao mesmo tempo. O pensamento condiciona a ação seguinte — se eu escrevi "eu preciso do prazo de trancamento, então vou buscar no regulamento", o argumento da busca sai melhor. E a observação corrige o pensamento seguinte — se a busca voltou vazia, o próximo pensamento não pode continuar como se ela tivesse funcionado. O formato é textual e repetitivo: pensamento, ação, entrada da ação, observação; pensamento, ação, entrada da ação, observação; e na última volta, em vez de ação, resposta final.

Agora eu preciso separar duas coisas que a turma junta, e essa separação é ponto de prova. ReAct **não** é o tool calling da Aula 21. São camadas diferentes. ReAct é o padrão de interação: raciocínio explícito intercalado com ação. Tool calling é o mecanismo de transporte da ação: o campo `tool_calls` no JSON da resposta. Dá para fazer ReAct em texto puro, com um modelo que não tem suporte nenhum a ferramentas, parseando "Action:" com uma expressão regular — e é exatamente isso que vocês vão fazer no Lab 7, de propósito, porque quem entende o padrão consegue implementá-lo em qualquer transporte.

> Ideia central: "ReAct é o padrão de interação; tool calling é o transporte. Vocês vão implementar ReAct em texto puro no Lab 7 justamente para essa diferença não virar decoreba."

## Slide 5 · Planejamento e decomposição · 00:28–00:36

Vamos falar de planejamento, porque metade do que se vende como "agente que planeja" é uma escolha entre duas coisas simples.

Primeira família: **plano antecipado**. O agente escreve a lista de subtarefas antes de agir e depois executa a lista. Isso é ótimo quando a tarefa tem estrutura previsível, e é ruim de um jeito específico: quando o primeiro resultado invalida o plano, o agente continua executando um plano morto. Segunda família: **plano emergente**. Cada passo é decidido com o que já se sabe naquele momento. Isso é robusto a surpresa, e a fraqueza é perder o fio em tarefa longa — na volta nove ele já não lembra por que começou.

Sistema maduro mistura os dois: um plano grosso no começo, revisado quando uma observação contradiz o plano. Isso é o que vocês fazem quando resolvem uma issue grande — vocês têm um roteiro na cabeça, e refazem o roteiro quando o teste revela outra coisa.

Mas o ponto que eu quero que fique é sobre decomposição, e ele é o mesmo fio da Aula 16. Decompor bem não é produzir subtarefas elegantes: é produzir subtarefas **verificáveis**. "Achar o artigo que fixa o prazo de trancamento" é verificável — ou o artigo apareceu, ou não. "Entender o regulamento" não é verificável, e por isso não é subtarefa, é desejo. Plano com sete etapas bonitas e nenhuma verificável é pior que três etapas grosseiras com critério de sucesso em cada uma.

> Ideia central: "Subtarefa boa não é subtarefa elegante: é subtarefa que dá para conferir se deu certo. O resto é desejo escrito em forma de lista."

## Slide 6 · Memória de curto prazo é a trajetória · 00:36–00:44

Agora memória, que é onde a maioria dos textos de blog erra feio. Existem duas memórias, e a de curto prazo não é um sistema — ela é a trajetória.

Concretamente: a memória de curto prazo do agente é a lista de mensagens que volta para o modelo a cada passo. Pergunta, pensamento, ação, observação, pensamento, ação, observação. É isso que dá continuidade ao raciocínio, e é isso que faz o agente saber, no passo 5, o que ele descobriu no passo 2.

E aqui está a consequência que ninguém coloca na conta: o custo por passo **não é constante**. O passo 6 reenvia tudo o que aconteceu nos passos 1 a 5. Se cada volta acrescenta mil tokens, o passo 6 manda cinco mil de histórico mais os novos. A trajetória é a memória e é a fatura.

Daí as três táticas, e são só três. **Truncar**: descartar observações antigas, o que é barato e perde informação. **Resumir**: comprimir o passado em algumas linhas, o que custa uma chamada a mais e perde detalhe. **Referenciar**: guardar o resultado grande em arquivo e manter no contexto só o caminho — "o resultado da busca está em `saida/busca_03.json`, com 40 linhas". Essa terceira é a que os agentes de programação usam mais, e é a que a turma menos pensa.

A analogia é a mesa de trabalho. Cabe muito papel, mas cada papel a mais deixa a mesa mais lenta de ler. E alguns papéis viram um resumo colado na borda.

> Ideia central: "A trajetória é a memória de curto prazo, e ela é a fatura. O passo seis não custa como o passo um — ele reenvia os cinco anteriores."

## Slide 7 · Memória de longo prazo · 00:44–00:50

Memória de curto prazo morre quando a trajetória termina. Longo prazo é o que sobrevive — e sobreviver, em engenharia, significa que alguém escreveu num lugar.

As formas usuais são três. Um arquivo de fatos aprendidos, que é a mais simples e a mais subestimada. Uma tabela de preferências ou de perfil do usuário. E um índice vetorial de episódios anteriores — que é, literalmente, o RAG do Módulo 5 apontado para o próprio histórico do agente em vez de para um acervo de documentos. Vocês já sabem construir isso: é o Lab 5.

Só que a decisão difícil não é ter memória de longo prazo. É duas outras: **o que promover** para ela, e **como recuperar** só o pedaço relevante depois. Sem critério de promoção, memória de longo prazo vira lixo acumulado que polui todo prompt futuro — e aí o agente fica pior com o tempo, não melhor, o que é um bug particularmente frustrante de diagnosticar.

E deixa eu marcar uma distinção que volta na Aula 26: gravar a trajetória inteira **não** é memória de longo prazo. Trajetória inteira serve para auditoria, e ela é obrigatória por outro motivo. Memória de longo prazo é o destilado da trajetória: um fato que se confirmou, uma preferência que o usuário expressou, um procedimento que funcionou. Coisa curta.

> Ideia central: "A pergunta não é se o agente tem memória de longo prazo. É o que ele promove para ela — porque sem critério de promoção, o agente piora com o tempo."

## Slide 8 · Reflexão e autocorreção — e o limite dela · 00:50–00:55

Último conceito antes do intervalo, e é o que mais me interessa que vocês levem com ressalva.

Pedir ao modelo que critique o próprio resultado antes de seguir funciona — e funciona **quando existe sinal externo para reagir**. A ferramenta devolveu erro: a autocrítica tem o que morder. O teste falhou com uma mensagem: tem o que morder. A busca voltou vazia: tem o que morder. Nesses casos, a reflexão é o mecanismo que transforma uma trajetória burra em uma trajetória que se corrige.

Agora, quando não existe sinal externo, a autocrítica tende a ser confirmatória. O modelo defende o que acabou de escrever com a mesma fluência com que defenderia o contrário, ou muda de opinião sem informação nova nenhuma. Isso é o mesmo fio da Aula 16, quando a gente viu que RL com recompensa verificável funciona em matemática e código porque existe professor automático. Verificação automática é o que transforma tentativa em aprendizado — no treino e também aqui, dentro de uma única trajetória.

Então a regra prática que eu quero cravar: montar uma etapa de "auto-avaliação" sem verificador e acreditar no resultado dela é enganar a si mesmo com passo extra e fatura extra. O agente diz "revisei e está correto" com a mesma fluência com que diria o contrário.

> Ideia central: "Autocrítica sem verificador é o modelo defendendo o que acabou de escrever. Com verificador, é o modelo consertando o que acabou de errar."

## Slide 9 · [Demo] O loop em 40 linhas · 01:05–01:18

Voltando. Antes do intervalo eu dei cinco peças e uma porção de conceitos. Agora eu vou abrir um arquivo e mostrar que isso é pequeno.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> Ideia central: "O que separa um chat de um agente são umas trinta linhas. Não é uma biblioteca, não é um framework — é um `while`, um `parse` e um dicionário de funções."

## Slide 10 · Agente × workflow determinístico · 01:18–01:28

Agora a decisão que vale dinheiro, e eu quero que ela fique como dois testes, nesta ordem.

**Primeiro teste: o caminho é conhecido?** Se a sequência de passos é a mesma sempre — extrair, validar, transformar, gravar — isso é um pipeline. Escrever um agente para executar um pipeline troca código previsível, testável e barato por sorteio caro. E eu vou ser direto: uma parte considerável do que hoje é vendido como agente é um pipeline com um LLM no meio, e ficaria melhor, mais rápido e mais barato escrito como pipeline.

**Segundo teste, e é ele que decide os casos difíceis: existe verificador para o passo intermediário?** Se dá para checar automaticamente se o passo deu certo — o teste passou, o JSON validou, a busca trouxe o dispositivo pedido, a soma fecha — então o loop pode explorar com segurança, porque o erro é detectado e corrigido dentro da própria trajetória. Sem verificador, o loop não explora: ele propaga erro com autoridade, e cada volta empilha convicção sobre uma base errada.

Isso é o critério da Aula 16 reaparecendo. Lá era treino: recompensa verificável faz o RL funcionar em matemática e código. Aqui é arquitetura: verificador disponível faz o loop valer a pena. É a mesma ideia em duas escalas.

E o erro de critério mais comum, que eu vejo em proposta de projeto e em post de blog: usar "a tarefa é complexa" como razão para usar agente. Complexidade não pede agente. **Incerteza intermediária com verificação possível** pede agente. Muita tarefa complexa é um pipeline longo, e pipeline longo é um bom lugar para estar.

> Ideia central: "Complexidade não pede agente. Incerteza intermediária com verificação possível pede agente. Se não tem verificador, o loop não explora — ele propaga erro com autoridade."

## Slide 11 · Custo e latência do loop · 01:28–01:34

Vou fazer uma conta rápida, porque ela muda como vocês desenham o sistema.

Uma resposta de chat é uma chamada de API. Um agente de seis passos são sete chamadas: seis voltas mais a síntese. Só que — e isso é o que a demo mostrou na tela — cada chamada reenvia a trajetória acumulada. Se cada volta acrescenta em média `d` tokens, o total enviado ao longo da trajetória não é `n · d`, é a soma de `k · d` para k de 1 a n, que dá aproximadamente `d · n² / 2`. Cresce com o **quadrado** do número de passos.

Latência acumula do mesmo jeito, e ela é sequencial por construção: o passo 4 não começa antes de o 3 voltar. Não tem paralelismo para tirar aqui, porque a decisão do passo seguinte depende do resultado do anterior. Se cada volta leva três segundos, seis voltas são dezoito segundos de espera na cara do usuário — e ninguém aceita dezoito segundos numa caixa de busca.

Por isso eu insisto: `max_passos` não é defensividade, é **decisão de produto**. Ele fixa o teto de custo por pergunta e o teto de espera do usuário, e essas duas coisas são requisitos, não detalhes. No Lab 6 vocês já escreveram esse teto. No Lab 7 ele volta como item de nota.

> Ideia central: "O custo do loop não é linear nos passos, é quadrático — porque cada volta reenvia a trajetória inteira. E a latência é sequencial: não tem paralelismo para salvar."

## Slide 12 · Paradas mal projetadas · 01:34–01:40

Dois defeitos, e eles são os dois lados da mesma peça faltando.

**Lado um, o loop que não termina.** O modelo pede ferramenta indefinidamente: porque a ferramenta falha sempre, porque a observação não responde à pergunta, ou porque o prompt não deixou claro como encerrar. Os sintomas são reconhecíveis: a mesma ação com o mesmo argumento repetida; ou duas ações alternando em ciclo, A, B, A, B. As mitigações são três e são baratas: orçamento de passos, detector de repetição — mesma ação e mesmo argumento duas vezes seguidas, aborta — e uma resposta de fallback declarada, do tipo "não consegui responder, e é isto que eu tentei", que é infinitamente melhor que uma resposta inventada.

**Lado dois, a parada precoce.** O agente responde antes de ter fundamento. Ou porque o formato de parada é fácil de emitir por acidente, ou porque a primeira observação pareceu suficiente. O sintoma é `Final Answer` no primeiro passo, sem nenhuma ação. A mitigação é exigir que a resposta final cite a observação que a sustenta — se não citou, não terminou.

E agora o contraste que eu quero cravar. Todo mundo se preocupa com o loop infinito, porque ele dói na fatura e aparece no gráfico de custo. A parada precoce é mais frequente e mais silenciosa: ela produz uma resposta plausível, sem evidência, e ninguém percebe **sem olhar a trajetória**. Guardem essa frase, porque ela é a tese da Aula 26.

> Ideia central: "O loop infinito dói na fatura, então todo mundo conserta. A parada precoce entrega resposta plausível sem evidência — e essa só aparece se alguém olhar a trajetória."

## Slide 13 · Estudo de caso: um coding agent numa issue real · 01:40–01:44

Deixa eu fechar o conteúdo com o caso em que as cinco peças aparecem sem esforço nenhum de interpretação: um agente de programação recebendo uma issue de um repositório.

**Objetivo:** o texto da issue. **Ferramentas:** buscar no repositório, ler arquivo, editar arquivo, rodar a suíte de testes, rodar o linter, abrir o diff. **Loop:** localizar o código responsável, formar uma hipótese, editar, rodar o teste, ler a falha, editar de novo. **Memória de curto prazo:** os arquivos lidos e as saídas de teste daquela sessão. **Critério de parada:** a suíte passa.

E aqui está a lição, que é o resumo executivo da aula inteira. O coding agent funciona bem **não** porque o modelo é especialmente bom em código. Ele funciona porque existe um verificador barato, automático e não negociável: o teste. Cada volta do loop recebe um sinal externo honesto — passou ou não passou. Onde o verificador é caro ou não existe — mudança de experiência de usuário, decisão de arquitetura, redação de política interna — o mesmo modelo, com o mesmo loop, com as mesmas ferramentas, rende muito menos.

O que transfere de domínio para domínio é a arquitetura. O que não transfere é o verificador. E é por isso que o benchmark que mais pegou nesta área é o SWE-bench, com issues reais de repositórios reais — a gente volta nele na Aula 26.

> Ideia central: "O coding agent não é bom porque o modelo é bom em código. Ele é bom porque o teste é um verificador barato que não mente. A arquitetura transfere; o verificador não."

## Slide 14 · [Exercício] Agente ou pipeline? · 01:44–01:50

Seis minutos em dupla, e é o exercício que mais volta na Entrega 2.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> Ideia central: "Cinco cenários. Para cada um: agente ou pipeline, qual é o verificador — e se não tiver, a palavra 'nenhum' escrita, porque escrever 'nenhum' é o achado."

## Slide 15 · Fechamento: a definição, terceira vez · 01:50–02:00

Terceira e última vez, e agora não como definição nem como código: como checklist de projeto.

Modelo, ferramentas, loop, objetivo, critério de parada. Para o projeto de vocês, eu quero que cada uma dessas cinco linhas tenha uma resposta escrita. E depois os dois testes: o caminho é conhecido? existe verificador para o passo intermediário? Se a resposta ao segundo teste for "nenhum verificador", isso não é um problema para esconder da Entrega 2 — é um achado para levar à Entrega 2, porque significa que ou vocês constroem um verificador, ou vocês põem um humano no laço, ou vocês reconhecem que aquilo é um pipeline com um LLM dentro e escrevem um pipeline. Qualquer uma das três é uma resposta defensável. Fingir que existe verificador não é.

Uma frase de honestidade sobre hoje: tudo o que a gente viu foi **um** agente. Um loop, um conjunto de ferramentas, um objetivo. Na próxima aula a gente coloca mais de um na mesa — orquestrador e trabalhadores, pipeline de estágios, debate, painel de especialistas — e eu vou passar boa parte da aula argumentando que a maior parte disso é desnecessária. Sistemas multiagente e orquestração, Aula 24. Eu prometo ser cético, e o ceticismo vai ser conteúdo, não opinião.

E para a semana, duas coisas: rodar a demo nos quatro modos e escrever qual peça está faltando em cada modo com defeito; e a leitura do ReAct, arXiv 2210.03629, com a pergunta dirigida do slide — qual modo de falha só aparece no raciocínio isolado, e por que a observação de uma ferramenta o elimina. Quem responder isso já entrou no Lab 7.

> Ideia central: "Modelo, ferramentas, loop, objetivo, critério de parada. Se uma dessas cinco linhas do projeto de vocês estiver em branco na Aula 26, o problema não é o modelo — é o projeto."

---

## Parte 2 — Demonstração guiada

Treze minutos, terminal e editor, sem rede e sem dependência nenhuma. O script é `codigo/demo-loop-agente.py`: o modelo é um simulador roteirado determinístico com semente fixa e as ferramentas são locais, então a saída é sempre a mesma e eu posso ensaiar em casa com a certeza de que a sala vê o mesmo. O objetivo é anticlímax deliberado: eu quero que a turma saia com a sensação de que agente é pequeno.

**1.** **[Abro `demo-loop-agente.py` num editor com fonte grande e rolo o arquivo de cima a baixo em quinze segundos]** Deixa eu começar pelo tamanho. Isso aqui é o arquivo inteiro. O loop do agente é essa parte, menos de uma tela e meia. Todo o resto é ferramenta e é o simulador de modelo, que existe para a gente rodar sem rede.

**2.** **[Aponto com o cursor, na ordem, os cinco trechos: a função que chama o modelo, o dicionário `FERRAMENTAS`, o `while`, a constante do objetivo dentro do prompt de sistema, e a condição de `Final Answer` junto ao `max_passos`]** Cinco peças, cinco trechos. Modelo: essa função. Ferramentas: esse dicionário — nome para função, o mesmo `REGISTRO` do Lab 6. Loop: esse `while`. Objetivo: essa string, dentro do prompt de sistema. Critério de parada: essas duas linhas, a que reconhece a resposta final e o teto de passos. Não tem uma sexta.

**3.** **[Rodo `python demo-loop-agente.py --normal` com a pergunta que exige duas ferramentas]** Agora rodando. A pergunta é do tipo que precisa de duas ferramentas: primeiro achar o prazo no regulamento, depois fazer uma conta com esse prazo. Olha a saída: cada volta vem rotulada. `OBSERVAR`, `PLANEJAR`, `AGIR`, `REFLETIR`. É o ciclo do slide 3 impresso no terminal.

**4.** **[Aponto a coluna de tokens acumulados que o script imprime ao lado de cada passo]** Essa coluna aqui é o que eu queria mostrar. É o tamanho acumulado do prompt em tokens aproximados, passo a passo. Repararam que ela não sobe em degraus iguais? Ela acelera. Isso é a conta quadrática de que eu vou falar no slide 11, e é mais convincente vista assim do que como fórmula.

**5.** **[Rodo `--sem-parada`]** Agora eu tiro uma peça. Nesse modo eu removi a condição de `Final Answer` e deixei só o orçamento de passos. Olha o que acontece: o agente repete a mesma ação com o mesmo argumento até bater o teto, e para por esgotamento. Nome do sintoma: mesma ação, mesmo argumento, duas vezes seguidas. É o sinal de que ou o critério de parada está mal escrito, ou a ferramenta não está entregando o que o modelo pediu.

**6.** **[Rodo `--sem-orcamento`]** Nesse eu tirei o teto e deixei um detector de repetição. Ele aborta na terceira repetição e imprime por quê. Sem esse detector, isso seria um laço infinito com fatura — e eu quero que vocês vejam que a proteção que salvou aqui não foi inteligência do modelo, foi uma linha de código minha.

**7.** **[Rodo `--parada-precoce`]** Último modo, e é o que me interessa mais. Aqui o prompt de sistema permite responder direto, sem obrigar a citar observação. Olha: `Final Answer` no passo um. Zero ações. E a resposta é **plausível** — se vocês não estivessem vendo a trajetória, vocês aceitariam. Compara com o modo anterior: aquele era feio e caro, esse é bonito e errado. O feio e caro aparece no gráfico de custo; esse só aparece se alguém abrir a trajetória.

**8.** **[Volto ao editor e deixo lado a lado a linha do `max_passos` e a linha da condição de parada]** Fecho aqui. Duas linhas. Uma protege a fatura, a outra protege a resposta. E as duas são a mesma peça da definição — critério de parada. Voltando para o slide.

---

## Parte 3 — Hands-on

Seis minutos, em dupla, com os cinco cenários projetados. O objetivo não é acertar a classificação — é forçar a pergunta do verificador, que é a que a turma não faz sozinha.

**1.** **[Projeto os cinco cenários e formo as duplas]** Seis minutos em dupla. Cinco cenários no slide. Para cada um eu quero três coisas, e a terceira é a que vale: a letra A de agente ou P de pipeline; qual é o verificador do passo intermediário — e se não existir, a palavra "nenhum" escrita, porque escrever "nenhum" é o achado; e uma frase de justificativa.

Os cinco cenários:

1. Converter quatro mil notas fiscais em PDF numa tabela com sete campos fixos, todos os PDFs com o mesmo layout.
2. Responder perguntas de alunos sobre o regulamento citando o dispositivo, sobre o acervo que vocês indexaram no Lab 5.
3. Corrigir um bug de teste vermelho num repositório com suíte de testes rápida.
4. Escrever a política de privacidade da empresa a partir de seis documentos internos.
5. Reconciliar duas planilhas de pagamento e listar as divergências, com a regra de reconciliação já definida no manual.

*Como recolher:* quatro minutos de dupla, dois de correção. Não corrijo os cinco: peço voluntário para o 1, corrijo o 3 em dez segundos, e gasto o resto no 4. Encerro com a frase que amarra no fechamento: "escrever 'nenhum verificador' não é falhar no exercício — é o achado que vocês levam para a Entrega 2".

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a conta em aula.
Esta aula tem **um** item de apêndice, então a contingência é curta — e a versão de trinta segundos
dela eu já faço no slide 11, porque a soma é curta o suficiente para caber no quadro sem virar aula
de matemática.

**Item 1 — "de onde vem esse `n²`?" (A.1, Etapas 1 a 3, ~4 min).**
A pergunta mais provável do Bloco 2, e a que **vale** fazer no quadro, porque são três linhas. Eu
escrevo os tamanhos das chamadas — `p₀`, `p₀+d`, `p₀+2d`, … — e somo: dá `d` vezes a soma dos
primeiros `n` inteiros, que é `d·n(n+1)/2`. E fecho com a razão que interessa: a estimativa ingênua
"custo de uma chamada vezes número de passos" subestima por um fator `(n+1)/2`, que com seis passos
é **três vezes e meia**. Se a turma quiser número absoluto, eu uso o `d` que a demo imprimiu na
coluna de tokens acumulados, não um número inventado.

**Item 2 — "então quanto eu ponho no `max_passos`?" (A.1, Etapa 5, ~3 min).**
A melhor pergunta que esta aula pode gerar, porque ela transforma a conta em decisão. Eu inverto a
desigualdade no quadro: se o teto de orçamento é `B` tokens por pergunta, então
`n_max = ⌊√(2B/d)⌋`. E leio o efeito da raiz em voz alta: **dobrar o orçamento não dobra os passos**,
aumenta-os em quarenta por cento — comprar o dobro de exploração custa quatro vezes mais. Dois
números fecham: cem mil tokens com mil por volta dá quatorze passos; vinte mil dá seis. Se não
houver tempo, a frase é: "`max_passos` sai de uma desigualdade, e a desigualdade está em A.1".

**Item 3 — "por que truncar resolve e referenciar não?" (A.1, Etapa 6, ~4 min).**
Costuma vir no slide 6, e é a discussão mais útil das três. Truncar e resumir mudam a **ordem** de
crescimento — de quadrática para linear —, porque limitam o tamanho de cada chamada a uma constante.
Referenciar **não** muda a ordem: continua `n²`, e ataca a constante `d`. Nas trajetórias curtas
desta disciplina, quatro a oito passos, a constante é onde o dinheiro está, e por isso referenciar é
a tática de melhor retorno aqui — pela Etapa 5, cortar `d` por dez multiplica `n_max` por três. Se o
tempo apertar, eu digo só a conclusão: "as três táticas atacam coisas diferentes da mesma fórmula, e
a tabela está em A.1".

**Item 4 — "e com janela de um milhão de tokens?" (A.1, casos-limite, ~1 min).**
Esta vem sempre, e a resposta formal é curta o suficiente para eu dar na hora: a fórmula não muda,
porque o custo depende do que eu **mando**, não do que caberia. Janela grande adia o erro de limite e
não toca em `T(n)`. A segunda metade da resposta — a degradação de achar informação no meio de muito
texto — é a Aula 10 e não é assunto deste apêndice.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 15 da Parte 1 — a definição operacional pela terceira vez, agora como checklist aplicável ao projeto, os dois testes de decisão, a ponte para a Aula 24 (Sistemas multiagente e orquestração) com o aviso de ceticismo, e as duas tarefas da semana.

> Ideia central: "Hoje foi um agente: um loop, um objetivo, uma parada. Semana que vem eu coloco vários na mesa — e passo metade da aula argumentando que vocês provavelmente não precisam deles."

---

*Roteiro do Instrutor · Aula 23 de 30 · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
