---
aula: 22
titulo: "Laboratório 6: Tool calling e MCP — Entrega 1 do projeto"
tipo: laboratorio
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 22 de 30

> **Rebalanceamento V2 — §6-bis.** O roteiro prático **não foi reordenado**, e a janela da Entrega 1 continua fixa em 01:40. Cada checkpoint abre pelo que a tela imprime quando está certo, e só depois vem o que implementar. O apêndice é enxuto: **dois itens, os dois do Checkpoint 2** — a conta de custo do laço e a razão pela qual ela é superlinear. Como a Aula 21 não tem apêndice próprio, este é o primeiro lugar do bloco de agentes em que a matemática aparece, e vale dizer isso em voz alta uma vez. A Parte 4 traz as respostas de trinta segundos.

## Como usar este roteiro

A prosa deste documento é **fala em primeira pessoa**: é o que eu digo em sala, na ordem em que digo. Não é resumo do conteúdo — é o texto falado. Posso ler quase literalmente ou usar como trilho e improvisar em cima.

As linhas marcadas com 🗣️ são as **frases-âncora**: as que eu cravo, quase palavra por palavra, porque mudam o ritmo ou fecham um ponto. Cada slide tem uma.

As notas marcadas com **Bastidor** são operacionais e **não são faladas em voz alta**. Nesta aula elas cuidam de três coisas que podem estragar o dia: o recolhimento da Entrega 1 nos cinco primeiros minutos, a instalação do SDK do MCP (que é o único ponto do lab que depende de rede), e a disciplina de não deixar a conversa de projeto invadir os checkpoints — ela tem janela própria às 01:40.

A **Parte 4** é curta e nova: são as duas perguntas que o `max_passos` provoca, com resposta de trinta segundos e o custo em minutos da versão longa. Em lab eu não conduzo derivação no quadro — mas esta é a primeira aula do bloco de agentes com apêndice, e a conta do custo do laço é a única do curso que eu faria em quatro minutos se a turma pedisse, porque ela vale para o projeto de todos.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · Abertura: hoje vocês escrevem o host · 00:00–00:05

Boa noite, pessoal. Ontem eu passei uma aula inteira insistindo numa frase: o modelo pede, o host executa. Hoje vocês escrevem o host.

E eu quero ser preciso sobre o que isso significa em duas horas. Vocês vão escrever o schema de três ferramentas, a validação dos argumentos, a detecção da chamada na resposta do modelo, o parsing do JSON, o despacho, o retorno como mensagem de papel `tool`, e o laço com orçamento de passos. Sem framework. Sem biblioteca de agente. Na unha.

E depois, com isso na mão, vocês fazem a mesma coisa pelo protocolo: um cliente MCP contra um servidor que já existe, e um servidor MCP de vocês.

A ordem é deliberada e eu já disse ontem por quê: na mão antes do framework. Quem escreveu o parsing e o despacho com as próprias mãos nunca mais vai olhar uma biblioteca de agente e ver mágica.

> 🗣️ "Ontem o modelo ganhou mãos. Hoje vocês escrevem o programa que obedece — e escrevem na unha, para nunca mais achar que tem mágica ali dentro."

> **Nota:** Bastidor: chegar com o notebook rodado de ponta a ponta nos dois modos (API e offline) e com a saída do cliente MCP salva em texto. Levar as rodas do `mcp` e do servidor de referência num pendrive (`pip download mcp mcp-server-time -d rodas/`) — a instalação é o único ponto do lab que depende de rede. Não abrir a pasta `solucao/` em tela nenhuma. Mencionar em vinte segundos que este deck tem apêndice, dois itens, e que eles são os primeiros do bloco de agentes — a Aula 21 não tinha.

---

### Slide 2 · Entrega 1: como eu recolho agora · 00:05–00:10

Antes de qualquer código, o marco do projeto. Hoje é a Entrega 1: a proposta.

O que eu recolho agora, nestes cinco minutos: uma proposta por equipe, duas páginas, PDF ou link — no canal da turma. Eu vou anotar quem entregou enquanto vocês sobem o arquivo.

E eu **não** vou discutir proposta agora. A devolutiva tem hora marcada: às cento e quarenta, dez minutos antes do fim, eu projeto os cinco critérios e comento três ou quatro propostas em voz alta. Se alguém tiver dúvida sobre o projeto no meio do lab, eu anoto e respondo naquela janela. Isso não é burocracia: é a única forma de os checkpoints caberem no relógio.

Adianto só uma coisa, que é a que mais dói na correção: o item que reprova mais proposta é o plano de avaliação. Uma métrica só, no fim do pipeline, não atende. O requisito é **métrica por camada** — e vocês já sabem fazer isso, porque foi exatamente o que o Lab 5 cobrou.

> 🗣️ "Proposta agora, discussão às cento e quarenta. E o item que mais derruba proposta é o plano de avaliação com uma métrica só no fim do cano."

> **Nota:** Bastidor: abrir o canal da turma projetado e ir marcando os nomes das equipes ao vivo — a lista visível acelera quem esqueceu. Anotar quem não entregou, sem constranger ninguém; prazo de 24 h com desconto declarado, dito individualmente depois da aula. Não abrir discussão de tema aqui em nenhuma hipótese. Guardar para a janela das 01:40 a pergunta nova da V2: quem propôs agente, qual é o `max_passos` e de onde saiu o número.

---

### Slide 3 · Setup, chaves e o modo offline · 00:10–00:15

Três coisas operacionais e a gente parte para o código.

Primeira: a chave da API. Ela é **opcional** e ela entra por `getpass`, na célula do setup. Quem não tiver chave dá Enter e o notebook usa um simulador roteirado embutido — um modelo de mentira, escrito à mão, que escolhe a ferramenta por palavra-chave. Ele existe por dois motivos: os testes dos checkpoints precisam ser determinísticos, e o lab tem que fechar numa sala sem rede. O que ele **não** faz é medir competência de modelo, e o notebook avisa isso em letra grande na saída.

E o aviso que eu repito todo lab: chave dentro do arquivo entregue eu trato como problema de segurança, não como bug. `getpass` sempre.

Segunda: os Checkpoints 1 e 2 não têm dependência nenhuma. Biblioteca padrão do Python, mais nada.

Terceira: os Checkpoints 3 e 4 usam o SDK do MCP, e essa é a única coisa do dia que precisa de rede. Se o `pip install` falhar, tem um plano B na pasta do lab que é melhor que o plano A do ponto de vista pedagógico: o `mcp_minimo.py`. São oitenta linhas, biblioteca padrão, cliente e servidor JSON-RPC sobre entrada e saída padrão, escritos à mão. Mesmo protocolo, mesmos três verbos. Quem cair nesse caminho não perde nada — ao contrário, vê o protocolo cru.

> 🗣️ "Os dois primeiros checkpoints não têm dependência nenhuma. E se o SDK não instalar, o plano B é ler oitenta linhas que mostram que MCP é JSON numa linha só."

> **Nota:** Bastidor: rodar a célula de setup junto com a turma e ler a saída em voz alta. Se mais de um terço não conseguir instalar o `mcp`, distribuir as rodas do pendrive agora — não no meio do CP3. Perguntar quantos estão em modo offline e anotar: isso calibra quanto tempo gastar no CP2. Se a sala inteira estiver no mesmo provedor e o 429 começar a aparecer, a contingência é baixar `MAX_PASSOS` para 2 — e dizer por que isso funciona tão bem: o gasto por pergunta cai com o quadrado do orçamento.

---

### Slide 4 · [Demo] O loop desenrolado à mão · 00:15–00:35

Vinte minutos comigo na tela, e eu vou fazer uma coisa de propósito estranha: eu vou rodar **uma volta** do ciclo sem escrever função nenhuma. Nem laço.

E eu já adianto o número que eu quero que vocês olhem, porque ele é o ponto de virada da aula: a **contagem de mensagens**. A lista começa com duas. Vira três. Vira quatro. E a segunda chamada ao modelo envia **as quatro**, não só a última.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> 🗣️ "Uma volta do ciclo, na mão, com a lista de mensagens crescendo na tela. O laço é de vocês — é o Checkpoint 2."

> **Nota:** Bastidor: passos na Parte 2. Escrever em células novas ao fim do notebook e apagar antes de soltar a turma. Se a API falhar, a demo roda igual com o simulador roteirado: a mecânica é a mesma e é ela que está sendo mostrada. A execução com argumento inválido é a parte mais importante e não pode ser cortada. Se o provedor devolver `usage`, anotar no canto do quadro os tokens de entrada das duas chamadas — a razão entre eles é a semente do A.1, e a turma vai reencontrar isso no slide 6.

---

### Slide 5 · Checkpoint 1 — Os três schemas e a validação · 00:35–00:48

Treze minutos. Duas coisas para escrever.

**[Projeto o critério de conclusão antes de qualquer coisa]**

Quando estiver certo, a tela imprime uma linha: `Checkpoint 1 OK`, três schemas válidos, oito casos de validação, calculadora barrando código. E o teste vai ter conferido cinco coisas para poder imprimir isso.

Três schemas com descrição de pelo menos sessenta caracteres. Todo parâmetro com `type` e com `description`. Todo nome de ferramenta presente no `REGISTRO`. Os oito casos de validação passando — e entre eles estão parâmetro inventado, tipo errado, valor acima do máximo e ferramenta que não existe no catálogo. E a calculadora recusando uma expressão que não é aritmética.

**[Aponto os dois objetos lado a lado, `SCHEMAS` e `REGISTRO`]**

A primeira coisa a escrever são os schemas. Três ferramentas: `calcular_expressao`, que já está pronta e serve de molde; `buscar_regulamento`, que é a base do Lab 5 virando ferramenta; e `consultar_cep`, que bate numa API pública sem chave. As implementações das três já existem no notebook. **O que é de vocês é o schema** — porque o schema é o prompt, e foi isso que a tabela de ontem mediu.

E eu vou ser chato num detalhe: a descrição tem que dizer **quando usar** a ferramenta, não só o que ela faz. O modelo não escolhe pela assinatura, ele escolhe pela descrição. O teste exige sessenta caracteres, e isso não é para castigar ninguém — é o mínimo para caber "faz X" mais "use quando Y".

A segunda é o `validar`. Ele confere contra o schema: a ferramenta existe, os obrigatórios estão lá, nenhum parâmetro inventado, os tipos casam, o `k` está dentro do máximo. E isso roda **antes** do despacho, sempre. A decodificação restrita garante que o JSON está bem formado; ela não garante que o argumento presta.

> 🗣️ "A descrição precisa dizer quando usar, não só o que faz. O modelo não escolhe pela assinatura — ele escolhe pelo texto que vocês escreveram."

> **Nota:** Bastidor: condução na Parte 3. O erro mais comum é descrição de humano ("Endpoint de consulta ao acervo"). Quando eu vejo isso, eu pergunto: se você fosse o modelo, você saberia quando chamar isso? Aos 00:46, mão levantada para o `Checkpoint 1 OK`; aos 00:48 eu libero a solução deste checkpoint, porque o CP2 depende dela. Este checkpoint não tem item de apêndice, e vale saber disso para não prometer conta que não existe.

---

### Slide 6 · Checkpoint 2 — O loop na mão · 00:48–01:05

Dezessete minutos, e é o coração do lab.

**[Projeto o critério]**

A tela vai imprimir `Checkpoint 2 OK`, conta, busca, erro tratado e orçamento de passos. E o teste vai ter conferido cinco coisas: a pergunta de conta chegando ao número certo; a pergunta de regulamento citando o dispositivo certo; a trajetória na ordem `system`, `user`, `assistant`, `tool`, `assistant`, com o `tool_call_id` casando com o `id` da chamada; argumento inválido devolvendo dicionário de erro em vez de exceção; e o **modelo teimoso** — um modelo escrito de propósito para nunca parar de pedir ferramenta — sendo chamado exatamente três vezes e a resposta trazendo a palavra "orçamento".

**[Aponto as quatro assinaturas]**

Quatro funções. `detectar_chamadas`, que olha a mensagem do modelo e devolve as chamadas ou uma lista vazia. `parsear_argumentos`, que transforma aquela string em dicionário — e que **não pode levantar exceção** quando o JSON vem truncado, porque isso acontece. `despachar`, que valida, procura no registro e executa. E o `loop_agente`, que amarra tudo.

Duas coisas que o teste cobra e que a maioria esquece na primeira tentativa.

A primeira é o orçamento de passos. O loop chama o modelo, executa, devolve, chama de novo. Se o modelo insistir em pedir ferramenta, o laço não termina sozinho. O notebook usa `MAX_PASSOS` igual a quatro.

**[Aponto o contador no meio do diagrama do laço]**

E aqui eu quero gastar trinta segundos, porque este é o único ponto matemático do lab e ele vale para o projeto de todos vocês. Aquele quatro não é chute. O modelo não guarda estado: em cada volta, o programa de vocês reenvia a trajetória **inteira**. Então a segunda chamada é maior que a primeira, a terceira é maior que a segunda, e o total de tokens que vocês mandam numa trajetória de `n` passos cresce com o **quadrado** de `n`, não com `n`. Quatro é o maior número de voltas que cabe em cinco mil tokens enviados por pergunta, com a observação típica deste notebook. Está tudo escrito no apêndice, itens A.1 e A.2, e eu não vou fazer a conta agora — mas eu quero que vocês saibam que ela existe, porque na hora de propor um agente no projeto essa é a conta que decide se o plano cabe no free tier.

A segunda coisa que o teste cobra é o tratamento de erro. Quando a ferramenta falha, o erro volta para o modelo **como resultado**, num dicionário, na mensagem `tool`. Erro de ferramenta é informação, não exceção. Quem levanta exceção no despacho mata a conversa — e mata sem registrar o que aconteceu.

E a saída do `loop_agente` são duas coisas: a resposta e a **trajetória**. A lista de mensagens inteira. Ela é o artefato que interessa, e é ela que vai comentada na entrega — porque quando um agente erra, a resposta final é só o sintoma.

> 🗣️ "Erro de ferramenta é informação, não exceção. E a saída do loop não é a resposta: é a trajetória. A resposta é o sintoma."

> **Nota:** Bastidor: condução na Parte 3. Circular olhando a estrutura do laço, não esperando pergunta. Se alguém importar biblioteca de agente, cortar na hora e com bom humor: hoje é na mão, e o teste exige as quatro funções pelo nome. Aos 01:03 mão levantada; aos 01:05 solução liberada e intervalo. Os trinta segundos sobre o quadrado são o único momento de matemática do lab: dizer e seguir, sem quadro. Se a pergunta vier, Parte 4, item 1.

---

*Intervalo · 01:05–01:15*

---

### Slide 7 · Checkpoint 3 — Cliente MCP contra um servidor que já existe · 01:15–01:27

Voltando. Doze minutos, e agora o protocolo.

**[Projeto o critério, que aqui são três evidências e não uma linha de OK]**

Este checkpoint não imprime `Checkpoint 3 OK`. O critério dele são três coisas na saída: o `initialize` com o nome e a versão do servidor negociados, o `tools/list` com o nome, os obrigatórios e a **descrição** de cada ferramenta, e uma chamada de ferramenta com `isError` igual a falso. Quem está no caminho offline produz a mesma evidência com o `mcp_minimo.py`.

**[Aponto a etiqueta sobre a seta `stdio`]**

O que muda em relação ao que vocês acabaram de escrever é uma coisa só, e é grande: **o catálogo deixa de ser de vocês**. No Checkpoint 2 vocês escreveram o schema. Aqui vocês **descobrem** o schema, com `tools/list`, e a descrição que vai influenciar a escolha do modelo foi escrita por quem publicou o servidor.

Guardem isso, porque é um risco novo: descrição de ferramenta é prompt, então servidor desconhecido é prompt desconhecido. Esse fio é da Aula 26.

O que vocês implementam é o cliente: montar os parâmetros do transporte, fazer o `initialize`, listar as ferramentas e imprimir nome, obrigatórios e descrição de cada uma, tentar listar os recursos dentro de um `try` — porque muitos servidores não expõem recurso nenhum — e chamar uma ferramenta.

E uma decisão de engenharia que está tomada no notebook e que eu quero explicar: o cliente roda por `!python cliente_mcp.py`, num subprocesso, e não com `await` dentro de célula. Isso é de propósito. Cliente MCP é código assíncrono, e código assíncrono dentro de notebook é uma fonte de sofrimento que não ensina nada sobre o protocolo.

> 🗣️ "No MCP o catálogo deixa de ser seu. A descrição que decide a escolha do modelo foi escrita por outra pessoa — e ela entra no prompt de vocês."

> **Nota:** Bastidor: condução na Parte 3. Conferir na véspera que o servidor de referência ainda instala e que a ferramenta dele tem o nome que está no notebook — o cliente é genérico, então trocar servidor é trocar uma string. Quem falhou no `pip install` vai para o `mcp_minimo.py` e o checkpoint vale igual.

---

### Slide 8 · Checkpoint 4 — Seu próprio servidor MCP · 01:27–01:40

Treze minutos, e o outro lado do protocolo.

**[Projeto o critério]**

O critério é o cliente do checkpoint anterior, apontado para o servidor de vocês, imprimindo três coisas: a ferramenta em `tools/list`, o recurso em `resources/list`, e o resultado da busca com os dispositivos certos. E uma coisa que não aparece na saída e que eu confiro: nenhum `print` no servidor.

**[Aponto as duas funções decoradas, com as etiquetas de dono da decisão]**

O arquivo é curto: importa o corpus, cria o servidor, e expõe **duas coisas de naturezas diferentes**. Uma ferramenta, `buscar_regulamento` — ação, e quem decide chamar é o modelo. E um recurso, `regulamento://dispositivos`, com o índice do acervo — dado, e quem decide anexar é a aplicação. Duas linhas de código diferentes para dois donos de decisão diferentes, e é o Conceito da aula de ontem virando arquivo.

E tem um detalhe que eu adoro nesse checkpoint: com o SDK, a **docstring da função vira a descrição da ferramenta**. Aquela docstring que vocês escreveriam para a equipe é literalmente o texto que o modelo vai ler para decidir. Isso é o "schema é prompt" de ontem, agora como consequência de uma escolha de biblioteca.

E o erro que eu vou ver em pelo menos três máquinas: `print` dentro do servidor. Em transporte de entrada e saída padrão, o `print` escreve **no canal do protocolo**. Qualquer byte fora do formato corrompe a conversa e o cliente morre com erro de decodificação. Diagnóstico vai para `stderr`, sempre.

Uma última coisa, e ela liga este checkpoint ao apêndice: o `k` da ferramenta de vocês tem limite. Isso não é só validação defensiva. Cada resultado que a ferramenta devolve entra na trajetória e é reenviado em **todas** as voltas seguintes — então uma ferramenta generosa que devolve dez trechos encarece a trajetória inteira, não só aquela volta. Ferramenta enxuta é decisão de custo.

> 🗣️ "A docstring da sua ferramenta vira a descrição que o modelo lê. Vocês estão escrevendo prompt achando que estão escrevendo documentação."

> **Nota:** Bastidor: condução na Parte 3. Quando alguém disser "meu cliente quebrou", primeira pergunta antes de olhar código: tem `print` no servidor? Resolve metade dos casos. Se o tempo estourou, este checkpoint vai para casa e eu anuncio — é o mais fácil de terminar sozinho, porque são dois decoradores. A frase sobre o `k` é a ponte natural para o A.2 e vale dez segundos.

---

### Slide 9 · Entrega 1: os cinco itens que eu olho numa proposta · 01:40–01:50

Parando o código. Dez minutos de projeto.

Cinco itens, na ordem em que eu leio.

Um: **problema claro e verificável**. Existe uma pergunta ou tarefa concreta, com usuário nomeado, e eu consigo dizer se o sistema acertou. "Assistente inteligente para a universidade" não é problema. "Responder perguntas sobre o regulamento citando o artigo, para aluno de graduação" é.

Dois: **duas técnicas do curso, nomeadas**. Recuperação mais agente. Ferramentas mais juiz calibrado. Ajuste fino mais avaliação sistemática. Nomeadas — não insinuadas em prosa.

Três: **plano de avaliação com métrica por camada**, e este é o que mais derruba. Conjunto de teste próprio, com tamanho declarado, e uma métrica por camada do sistema: `recall@k` para a recuperação, taxa de acerto de ferramenta para a camada de ação, e uma métrica para a resposta final. Uma métrica só, no fim, não atende — e vocês já sabem fazer o certo, porque foi isso que o Lab 5 cobrou.

Quatro: **divisão de trabalho**. Três ou quatro pessoas, com quem faz o quê. Não precisa ser definitivo. Precisa existir.

Cinco: **viabilidade em free tier**. Qual modelo, qual provedor, qual quota, qual tamanho de corpus. Se o plano precisa de GPU paga ou de cinquenta mil chamadas de API, é melhor descobrir hoje do que na Aula 26.

E uma pergunta que eu acrescentei a este item, para quem propôs sistema com laço: **qual é o `max_passos` de vocês, e de onde saiu esse número?** Isso não é pegadinha. A conta que eu mencionei no Checkpoint 2 está no apêndice, e ela transforma um teto de tokens por pergunta num número de passos. Quem propõe um agente com dez a quinze passos e observação grande está propondo dezenas de milhares de tokens por consulta — e o free tier é medido por minuto.

Agora eu quero três voluntários. Eu leio o problema de vocês em voz alta e digo em qual dos cinco itens eu apertaria.

> 🗣️ "Se eu não consigo dizer se o sistema acertou, vocês não têm um problema — vocês têm um tema. E tema não dá para avaliar."

> **Nota:** Bastidor: cronometrar. Dois minutos nos cinco critérios e oito minutos em três ou quatro propostas voluntárias, uma crítica por proposta, em voz alta e sem ironia. Se ninguém se voluntariar, usar uma proposta anônima de uma oferta anterior — nunca expor uma equipe sem consentimento. Registrar por escrito na proposta devolvida qual item ficou fraco. Se a proposta tiver laço e o `max_passos` não estiver justificado, escrever "ler A.1 do Lab 6" na devolutiva — é uma correção que se paga na Entrega 2.

---

### Slide 10 · Recolhimento e ponte para a Aula 23 · 01:50–02:00

Deixa eu fechar.

O inventário do que existe agora: três ferramentas com schema validável, um loop de tool calling escrito por vocês com orçamento de passos e tratamento de erro, uma trajetória registrada, um cliente MCP que serve para qualquer servidor, e um servidor MCP próprio expondo uma ferramenta e um recurso. Em duas horas.

A entrega: notebook executado com as saídas visíveis, o `servidor_regulamento.py`, a trajetória comentada em três a cinco linhas, as quatro questões-guia e a declaração de uso de IA. Uma semana. Checkpoints um a três são o núcleo; o quatro pode terminar em casa.

**[Projeto o índice do apêndice por 15 s]**

Dois itens, e eu nomeio o primeiro: o **A.1** é a conta que responde "de onde vem esse quatro do `max_passos`". Ela é curta, ela é a primeira conta do bloco de agentes — a aula de ontem não tinha nenhuma — e ela vai ser cobrada implicitamente na Entrega 2, quando eu perguntar o orçamento de passos do projeto de vocês. O **A.2** é o "por quê" do A.1: por que o custo cresce mais rápido que o número de passos.

E agora a ponte, que é a coisa que eu mais gosto de dizer no Módulo 5. Olhem o que o sistema de vocês faz hoje: ele recebe uma pergunta, o modelo pede uma ferramenta, o host executa, o modelo responde. Uma volta. Duas, se ele precisar.

Falta uma coisa só para isso virar um agente, e a palavra é **objetivo**. Hoje o loop de vocês para quando o modelo para de pedir ferramenta. Um agente para quando o **objetivo** foi atingido — e isso muda tudo: ele precisa planejar, precisa decidir o próximo passo olhando o que já sabe, precisa de memória entre os passos, e precisa de um critério de parada que não seja "o modelo cansou".

Na próxima aula a gente escreve a definição operacional e ela tem cinco peças: modelo, mais ferramentas, mais loop, mais objetivo, mais critério de parada. Vocês já têm três delas prontas, escritas hoje, com as próprias mãos. Aula 23, Agentes de IA.

> 🗣️ "Vocês deram mãos ao modelo. Semana que vem a gente dá um loop e um objetivo — e o nome disso é agente."

> **Nota:** Bastidor: projetar o checklist de entrega e ficar trinta segundos em silêncio para a turma fotografar. Recolher o pulso: perguntar quem fechou o CP4. Se menos de um terço fechou, a Aula 25 (Lab 7) começa recapitulando MCP em dez minutos. Devolver as propostas comentadas na saída, em mão, para quem entregou impresso. Nomear o A.1 em voz alta é o hábito que mantém a Parte 2 viva, e aqui é natural porque a Aula 23 vai retomar essa conta no apêndice dela.

---

## Parte 2 — Demonstração guiada

Vinte minutos, live coding, uma volta do ciclo sem função nenhuma. O objetivo não é adiantar o Checkpoint 2 — é o contrário: é fazer a turma ver a lista de mensagens crescendo passo a passo, para que o laço que eles vão escrever seja a formalização de algo que eles já viram acontecer.

Insumos da véspera: notebook rodado nos dois modos com os tempos anotados; a saída do `cliente_mcp.py` contra o servidor de referência salva em texto; as rodas do `mcp` num pendrive.

**1.** **[Crio a lista `mensagens` na mão, com `system` e `user`, e imprimo]** Duas mensagens. Só isso. Uma de sistema, dizendo que existem ferramentas e que é melhor usar, e uma do usuário com a pergunta. E eu quero apontar uma coisa que já está aqui e que ninguém vê: o catálogo de ferramentas não está nesta lista. Ele vai como um argumento separado, e o provedor serializa ele dentro do prompt. Está no prompt, mas não está na minha lista de mensagens.

**2.** **[Chamo o modelo uma vez com `SCHEMAS` e imprimo a mensagem devolvida, crua]** Uma chamada. E olha o que voltou: `content` nulo, e `tool_calls` com um objeto dentro. `id`, `name`, `arguments`. E o `arguments` com as barras de escape à mostra, porque é uma string com JSON dentro. Isso é a mesma tela de ontem, agora no notebook de vocês. Se o provedor devolver `usage`, eu anoto aqui no canto os tokens de entrada desta chamada — guardem esse número.

**3.** **[Anexo essa mensagem à lista e imprimo a lista]** Três mensagens agora. Repararam que eu **guardei** a mensagem do assistente inteira, com os `tool_calls` dentro? Isso não é opcional. Se eu jogar essa mensagem fora e só mandar o resultado depois, o modelo não tem como saber a que pedido aquele resultado responde.

**4.** **[Executo a ferramenta na mão, digitando a chamada Python numa célula nova]** Agora a terceira etapa do ciclo de ontem, e eu vou fazer ela do jeito mais explícito que existe: eu digito a chamada. `ferramenta_buscar_regulamento` com o termo que o modelo pediu. Repararam no que aconteceu? **Eu** executei. Não o modelo. Eu li o pedido dele e digitei a chamada. É literalmente isso que o `despachar` de vocês vai fazer, com um dicionário no lugar dos meus dedos.

**5.** **[Anexo o resultado como mensagem de papel `tool` com o `tool_call_id` e imprimo a lista]** Quarta mensagem: papel `tool`, o resultado em JSON, e o `tool_call_id` copiado do `id` que veio antes. Olha os dois campos na tela, um do lado do outro. Essa correlação é o que o teste do Checkpoint 2 verifica. E olha o **tamanho** dessa quarta mensagem: ela é a maior das quatro, e ela é o que a ferramenta devolveu.

**6.** **[Chamo o modelo de novo com a lista completa e leio a resposta final]** Segunda chamada ao modelo, agora com quatro mensagens de histórico. E olha: agora ele devolve `content` e nenhum `tool_calls`. Fim do ciclo. Cinco passos, uma volta, zero framework, e a única coisa que eu escrevi foram duas chamadas de função. E olha o `usage` desta chamada comparado com o daquela primeira, que eu anotei no canto: a entrada cresceu. Não é a mesma pergunta ficando mais cara por magia — é que eu reenviei tudo.

**7.** **[Refaço a execução manual com um argumento inválido de propósito, anexo o erro e chamo o modelo]** Agora a parte que eu mais quero mostrar. Vou fingir que o modelo mandou um CEP com três dígitos. Olha o que a ferramenta devolve: um dicionário com a chave `erro`. E olha o que eu faço com ele — eu anexo **o erro** como resultado da ferramenta, na mensagem `tool`, e chamo o modelo de novo. Olha a resposta: ele leu o erro e se recuperou. Guardem essa cena, porque ela é o Checkpoint 2 inteiro: erro de ferramenta é informação, não exceção.

**8.** **[Fecho sem escrever o laço]** E eu paro aqui, de propósito. O que ficou de fora é o `while`, o orçamento de passos e as quatro funções que empacotam o que eu acabei de fazer com as mãos. Isso é de vocês, são dezessete minutos, e vocês já viram acontecer.

> **Nota de contingência:** Bastidor: se a API falhar, a demo roda idêntica com o simulador roteirado — a mecânica é o que está sendo mostrada, e o simulado é determinístico, o que na verdade ajuda. Sem `usage`, o argumento do crescimento se faz com a contagem de mensagens (2, 3, 4) em vez de tokens, e funciona igual. Se o notebook não abrir, os oito passos são executáveis no quadro com a lista de mensagens desenhada crescendo — a parte insubstituível é a execução manual, a mensagem `tool` com o `tool_call_id`, e o erro tratado. Apagar as células da demo antes de soltar a turma: em lab, o que fica na tela é copiado. Não conduzir conta nenhuma aqui.

---

## Parte 3 — Hands-on

Quatro checkpoints e uma janela de projeto. Eu circulo olhando a estrutura do código, não esperando pergunta — em tool calling o sintoma quase sempre aparece longe da causa.

**1.** **[Lanço o Checkpoint 1 — os três schemas e a validação, 00:35–00:48]** Treze minutos. O critério é a linha `Checkpoint 1 OK — 3 schemas válidos, 8 casos de validação, calculadora barrando código`. Os schemas de `buscar_regulamento` e `consultar_cep`, com o `calcular_expressao` como molde, e a função `validar`. As implementações já estão prontas: o que é de vocês é o texto que o modelo lê e a barreira que o host aplica.

*Bastidor — erros comuns:* descrição escrita para humano em vez de para o modelo, sem dizer *quando* usar — é o erro número um e o teste pega pelo tamanho mínimo; esquecer o `k` no schema do `buscar_regulamento` e depois estranhar que o modelo nunca pede mais de um trecho; declarar `k` como string; esquecer o `required`, que é o campo que o `validar` usa; criar um nome de ferramenta que não existe no `REGISTRO` — schema sem implementação é menu com prato que a cozinha não faz; e escrever um `validar` que só confere os obrigatórios e deixa passar parâmetro inventado, que é justamente o que o modelo faz quando o nome do parâmetro é ruim.

*Como recolher:* eu passo de mesa em mesa e leio a descrição em voz alta, perguntando "se você fosse o modelo, saberia quando chamar isso?". Aos 00:46, mão levantada para o `Checkpoint 1 OK`. Aos 00:48 eu libero a solução, porque o CP2 não existe sem ela.

**2.** **[Lanço o Checkpoint 2 — o loop na mão, 00:48–01:05]** Dezessete minutos, quatro funções, e é o coração do lab. O critério é `Checkpoint 2 OK — conta, busca, erro tratado e orçamento de passos`. `detectar_chamadas`, `parsear_argumentos`, `despachar`, `loop_agente`. Os cinco passos de ontem, nomeados no código de vocês.

*Bastidor — erros comuns:* `msg["tool_calls"]` direto, sem `.get`, e aí a resposta final estoura com `KeyError` — o campo simplesmente não existe quando o modelo responde em prosa; `json.loads` sem `try`, e um JSON truncado derruba a trajetória inteira; levantar exceção no `despachar` em vez de devolver dicionário de erro; esquecer de anexar a mensagem do **assistente** antes da mensagem `tool`, o que quebra a correlação e confunde o modelo; usar `while True` sem contador, que é o teste do modelo teimoso falhando; devolver só a resposta final e não a trajetória; e — o mais sutil — anexar o resultado com papel `user` em vez de `tool`, que às vezes até funciona e é sair da distribuição de treino.

*Como recolher:* o `Checkpoint 2 OK`, que verifica cinco coisas: a conta chega ao número certo, a busca cita o dispositivo certo, a ordem dos papéis na trajetória, o `tool_call_id` casando com o `id`, e o orçamento de passos parando o modelo teimoso em três chamadas. Aos 01:03 mão levantada; aos 01:05 solução liberada e intervalo. Quem terminou antes: mandar rodar o loop nas três perguntas e começar a comentar a trajetória, que é item de entrega. Se alguém perguntar de onde vem o quatro do `MAX_PASSOS`, resposta de trinta segundos da Parte 4 e o ponteiro para o A.1 — **não** conduzir no quadro durante o lab.

**3.** **[Lanço o Checkpoint 3 — cliente MCP, 01:15–01:27]** Doze minutos. O critério são as três evidências na tela: `initialize` com nome e versão, `tools/list` com obrigatórios e descrição, e uma chamada com `isError` falso. O `cliente_mcp.py` roda por `!python` num subprocesso — não com `await` dentro de célula, e isso é decisão de projeto, não preguiça. Cinco TODOs: parâmetros do transporte, `initialize`, `tools/list`, `resources/list` protegido, e `tools/call`.

*Bastidor — erros comuns:* esquecer o `initialize` e chamar `tools/list` direto, o que o servidor recusa; passar o comando do servidor como uma string única em vez de comando mais argumentos; não proteger o `resources/list` com `try` e ver o cliente morrer contra um servidor que só expõe ferramenta; imprimir o objeto de resultado em vez do `.text` de cada bloco de conteúdo; e quem falhou no `pip install` tentar depurar o SDK em vez de ir para o `mcp_minimo.py`, que era o plano B anunciado.

*Como recolher:* três evidências na tela — nome e versão do servidor no `initialize`, a lista de ferramentas com os obrigatórios, e uma chamada com `isError` falso. No caminho offline, a mesma evidência saindo do `mcp_minimo.py`. Aqui eu paro trinta segundos e faço uma pergunta para a sala: quem escreveu a descrição da ferramenta que vocês acabaram de listar? A resposta — "não fui eu" — é o ponto do checkpoint.

**4.** **[Lanço o Checkpoint 4 — servidor próprio, 01:27–01:40]** Treze minutos, um arquivo curto. O critério é o cliente do CP3 apontado para o servidor deles, mostrando a ferramenta, o recurso e o resultado. A ferramenta com docstring escrita para o modelo, a validação de `termo`, o limite de `k`, e o índice do acervo exposto como **recurso**.

*Bastidor — erros comuns:* `print()` no servidor, que corrompe o canal do protocolo e é a primeira coisa que eu pergunto quando alguém diz "quebrou"; docstring de uma linha, que joga fora exatamente a lição de ontem; expor o índice como ferramenta em vez de recurso, e aí o modelo passa a poder pedir o índice — que é o erro conceitual que o checkpoint existe para provocar; esquecer o decorador e ficar com uma função Python comum que o `tools/list` não vê; devolver objeto Python em vez de string do retorno da ferramenta; e tirar o limite do `k` "para ficar mais útil", o que engorda toda volta seguinte da trajetória.

*Como recolher:* o cliente do CP3, apontado para o servidor deles, mostrando a ferramenta, o recurso e o resultado. Se o tempo estourou, este vai para casa e eu digo isso em voz alta. Fecho com a pergunta que vira questão-guia: vocês escreveram `buscar_regulamento` duas vezes hoje — o que mudou entre as duas, e o que não mudou?

**5.** **[Abro a janela da Entrega 1, 01:40–01:50]** Dez minutos, código fechado. Dois minutos nos cinco critérios projetados, e oito minutos em três ou quatro propostas voluntárias.

*Bastidor — o que eu procuro em cada uma:* problema que eu não consiga avaliar ("melhorar a experiência do aluno"); duas técnicas que na verdade são uma ("RAG com prompt bem feito" é uma técnica); plano de avaliação com uma métrica só no fim do pipeline, que é o item que mais reprova; equipe de dois, ou de cinco; escopo que não cabe em free tier — corpus de dez mil PDFs, ajuste fino de modelo de sete bilhões de parâmetros, agente que faz cem chamadas de API por consulta; e, novo na V2, proposta com laço e sem orçamento de passos declarado.

*Como recolher:* uma crítica por proposta, em voz alta, dita sem ironia e sempre com o conserto junto — "esse problema não é avaliável como está; se vocês fixarem o conjunto de perguntas e o que conta como acerto, ele fica". Se ninguém se voluntariar, usar uma proposta anônima de oferta anterior; nunca expor equipe sem consentimento. Registrar por escrito na proposta qual dos cinco itens ficou fraco, porque a devolutiva oral evapora e a escrita chega na Entrega 2 — e, quando o caso for orçamento de passos, escrever o ponteiro para o A.1 junto.

---

## Parte 4 — Apêndice: se perguntarem

Em laboratório eu **não conduzo derivação no quadro** — o tempo é do teclado. Mas esta aula tem uma particularidade que vale registrar: ela é a **primeira do bloco de agentes com apêndice**, porque a Aula 21 não tem. E a conta do A.1 é a única do curso que eu consideraria fazer ao vivo num lab, porque ela é curta e porque todo projeto com laço vai precisar dela na Entrega 2.

> **Nota:** Bastidor: se uma pergunta merecer mais que trinta segundos, a resposta é "isso está escrito no A.n, e vale ler antes de propor o `max_passos` do projeto" — e seguir. As duas primeiras perguntas abaixo aparecem no CP2, e a terceira aparece na janela da Entrega 1, quando alguém defende um agente com muitos passos.

**Item 1 — "De onde vem esse quatro do `MAX_PASSOS`?" (A.1, 30 s · 4 min no quadro).**
A pergunta mais provável do lab e a que eu mais quero. **Resposta curta:** "de uma desigualdade. O modelo não guarda estado, então cada volta reenvia a trajetória inteira: a primeira chamada manda o prompt fixo, a segunda manda o prompt fixo mais uma observação, a terceira manda mais duas. Somando, o total enviado numa trajetória de `n` passos é o prompt fixo vezes `n` mais a observação vezes `n` vezes `n` menos um sobre dois — ou seja, cresce com o **quadrado** de `n`. Com o prompt e a observação deste notebook, quatro voltas é o que cabe em cinco mil tokens enviados por pergunta. Trocando o teto, troca o quatro." Se a sala estiver adiantada e alguém insistir, esta é a única conta que vale quatro minutos no quadro: as três primeiras chamadas escritas uma embaixo da outra e a soma. O detalhe todo está em **A.1**.

**Item 2 — "Se eu dobrar o orçamento, eu dobro os passos?" (A.2, 30 s).**
A pergunta que separa quem entendeu de quem decorou. **Resposta curta:** "não. Como o custo cresce com o quadrado dos passos, o número de passos cresce com a **raiz** do orçamento: dobrar o teto de tokens compra só quarenta e um por cento mais passos. E o inverso é a boa notícia: **reduzir a observação** é muito mais eficiente que aumentar o orçamento. Cortar o tamanho médio da observação pela metade multiplica os passos permitidos por raiz de dois, e cortar para um quarto **dobra** os passos — sem gastar um token a mais." É por isso que o `k` da ferramenta de vocês tem limite. A conta está em **A.2**.

**Item 3 — "Mas o meu agente do projeto vai precisar de dez ou quinze passos." (A.1 e A.2, 40 s).**
Aparece na janela da Entrega 1, e é uma conversa de arquitetura e não de matemática. **Resposta curta:** "pode precisar, e então a conta muda de lado: com quinze passos e observação grande, vocês estão falando de dezenas de milhares de tokens **por pergunta**, e o free tier é medido por minuto. Duas saídas, e as duas estão no apêndice: encolher a observação, que ataca a constante, ou truncar e resumir a trajetória, que muda a ordem de crescimento de quadrática para linear. A segunda é o que a Aula 23 desenvolve." Registrar por escrito na devolutiva da proposta: **ler A.1 antes da Entrega 2**.

### Ordem de sacrifício

Se a aula atrasar: o **CP4 vai para casa** primeiro — são dois decoradores e é o item mais fácil de terminar sozinho. Depois, cortar a primeira e a terceira etapas da demo, que são as mais previsíveis. **Não corto** a execução manual da ferramenta, a mensagem `tool` com o `tool_call_id`, nem a etapa do argumento inválido: sem essas três a turma escreve o Checkpoint 2 sem ter visto o mecanismo. E **não corto a janela da Entrega 1 em nenhuma hipótese** — ela é marco de projeto, vale 5% da nota final, e a devolutiva em sala não tem substituto assíncrono. Se for preciso escolher entre o CP4 e a janela do projeto, o CP4 perde.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 10 da Parte 1 — o inventário do que a turma construiu, o checklist de entrega com prazo de uma semana, os quinze segundos de índice do apêndice nomeando o A.1, e a ponte para a Aula 23 pela peça que falta no loop de hoje: o objetivo.

> 🗣️ "O loop de vocês para quando o modelo para de pedir ferramenta. Um agente para quando o objetivo foi atingido — e essa diferença é a aula da semana que vem."

---

*Roteiro do Instrutor · Aula 22 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
