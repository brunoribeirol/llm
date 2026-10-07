---
aula: 21
titulo: "Tool calling e Model Context Protocol (MCP)"
tipo: teorica
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 21 de 30 (V2)

## Como usar este roteiro

A prosa deste documento é **fala em primeira pessoa**: é o que eu digo em sala, na ordem em que digo. Não é resumo do conteúdo — é o texto falado. Posso ler quase literalmente ou usar como trilho e improvisar em cima.

As linhas marcadas com 🗣️ são as **frases-âncora**: as que eu cravo, quase palavra por palavra, porque mudam o ritmo ou fecham um ponto. Cada slide tem uma.

As notas marcadas com **Bastidor** são operacionais e **não são faladas em voz alta** — são lembretes do que abrir na tela, onde a turma costuma travar, o que responder se alguém perguntar algo específico. Nesta aula há duas notas que valem mais que as outras: a de levar a saída da demo salva da véspera, e a de não deixar a discussão de segurança comer o Bloco 2 — ela tem uma aula inteira reservada.

> **O que muda nesta versão.** Nada na fala, e de propósito: esta aula já abria pela aplicação e não
> tem matemática no fluxo. A V2 acrescenta apenas a **Parte 4**, que aqui tem uma função diferente
> da das aulas teóricas com derivação: como esta aula **não tem apêndice próprio**, a Parte 4
> registra onde estão os fundamentos formais que ela mobiliza — o ruído de uma medição com seis
> perguntas, o custo quadrático do loop, e a multiplicação de orçamentos — todos em apêndices de
> outras aulas.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · Abertura: o modelo passa a pedir · 00:00–00:04

Boa noite, pessoal. Ontem vocês entregaram — ou estão terminando de entregar — um sistema de recuperação medido. Chunking com metadados, índice, BM25, fusão por posição, reranking, e duas tabelas com `recall@k`. Deixa eu dar uma devolutiva de uma linha antes de começar: o que eu vi de melhor foram as tabelas quebradas por tipo de consulta, e o que eu vi de pior foram relatórios sem dizer quantas consultas tinham. Declarar o `|Q|` é de graça e é o que separa medição de impressão.

Agora, uma pergunta sobre o que vocês construíram: quem decidiu buscar? Foi vocês. Vocês escreveram a linha que chama a busca. O sistema de ontem é um cano — entra pergunta, ele busca, ele responde, sempre, mesmo quando a pergunta é "bom dia".

Hoje a gente entrega essa decisão para o modelo. E a coisa mais importante desta aula é entender exatamente o que isso significa e o que isso não significa.

> 🗣️ "Hoje o modelo ganha mãos. E eu vou passar a primeira metade da aula provando para vocês que ele continua sem poder executar nada."

> **Nota:** Bastidor: chegar com a saída da demo já rodada na véspera em modo `api`, salva em arquivo, com a data e o identificador do modelo anotados. Conferir na véspera se o modelo do provedor ainda existe — a lista muda. Ter a devolutiva do Lab 5 lida de verdade: uma frase concreta sobre o que a turma fez, não elogio genérico.

### Slide 2 · O que muda quando o modelo pode agir · 00:04–00:10

Deixa eu situar isso no arco do curso, porque hoje é uma fronteira.

Até a Aula 16 a gente mexeu no modelo: arquitetura, escala, ajuste fino, alinhamento, raciocínio. Nas Aulas 18 a 20 a gente parou de mexer no modelo e passou a mexer no que entra nele — recuperação é isso, é dar contexto. O modelo continuava fazendo uma coisa só: ler texto e escrever texto.

A partir de hoje ele começa a **afetar o mundo**. Não porque ele executa algo, mas porque o texto que ele escreve passa a ser lido por um programa que executa. E essa diferença é fina e é tudo.

E as três aulas seguintes são consequências disso. Na Aula 23 a gente põe esse pedido dentro de um loop com objetivo e critério de parada, e o nome disso é agente. Na 24, vários deles. Na 26, o que dá errado quando um texto não confiável entra num sistema que age.

> 🗣️ "A partir de hoje o texto que o modelo escreve deixa de ser resposta e passa a ser pedido. Um programa lê esse pedido e obedece — e é aí que a área fica séria."

> **Nota:** Bastidor: este slide é o mapa e vale trinta segundos de silêncio na tela. Se a turma estiver muito ansiosa com a Entrega 1 de amanhã, dizer aqui que os cinco itens da proposta vão aparecer no fechamento e cortar o assunto — no meio do conteúdo isso destrói o Bloco 1.

### Slide 3 · O ciclo de cinco passos — e quem executa o quê · 00:10–00:18

Vamos ao mecanismo. Cinco passos, e eu quero que a turma saia daqui sabendo de cor quem faz cada um.

Passo um: o **host** — que é o programa de vocês, o notebook, o aplicativo — monta o prompt e serializa **dentro dele** o catálogo de ferramentas disponíveis. Isso é texto. Está no prompt.

Passo dois: o **modelo** devolve, em vez de prosa, um objeto que descreve uma chamada — nome da ferramenta e argumentos, em JSON. Só isso. É a única coisa que o modelo faz neste ciclo.

Passo três: o **host** recebe esse JSON, valida os argumentos, decide se tem permissão para executar, e executa. Repararam? Validar, decidir e executar são três verbos, e nenhum deles é do modelo.

Passo quatro: o resultado volta para a conversa como uma mensagem de papel `tool`, amarrada à chamada por um identificador.

Passo cinco: o modelo lê o resultado e escreve a resposta final — agora sim, em prosa.

A analogia que eu uso é receita médica. O médico escreve o pedido. Ele não manipula o remédio, não abre a farmácia e não decide se o convênio cobre. O sistema em volta obedece — ou recusa.

E é por isso que a pergunta "e se o modelo apagar meu banco de dados?" está mal formulada. O modelo nunca apagou nada na vida. Se o banco foi apagado, foi porque alguém escreveu uma ferramenta chamada `apagar` e ligou ela no despacho, sem confirmação. A responsabilidade tem um autor, e não é o modelo.

> 🗣️ "Cinco passos, e o modelo é dono de um. Todo poder que a ferramenta tem foi dado por quem escreveu o host."

> **Nota:** Bastidor: desenhar os cinco passos no quadro, numerados, e escrever ao lado de cada um "modelo" ou "host". Deixar o quadro assim o resto da aula — eu volto a apontar para ele no Bloco 2 quando falar de MCP, porque a mesma separação reaparece entre processos.

### Slide 4 · Anatomia da chamada: o JSON na tela · 00:18–00:25

Deixa eu mostrar a coisa concreta, porque "chamada estruturada" é abstrato e o objeto é simples.

A chamada tem três campos que importam. O `name`, que é o nome da ferramenta. O `arguments`, que é uma string com um JSON dentro — e sim, é string, é JSON dentro de JSON, e todo mundo estranha isso na primeira vez. E o `id`.

O `id` é o campo que a turma sempre pergunta para que serve. Ele existe porque um único turno do modelo pode pedir **várias** chamadas de uma vez — três buscas em paralelo, por exemplo. Quando os três resultados voltarem, o modelo precisa saber qual resultado responde a qual pedido. Sem correlação explícita, não dá.

E a volta: o resultado entra na conversa como uma mensagem com papel `tool`, com o mesmo `tool_call_id`. Não é mensagem de usuário. E aqui tem uma coisa que parece burocracia e não é: se eu devolver o resultado como se fosse o usuário falando "o resultado foi sessenta", às vezes funciona. Funciona por acidente. O modelo foi treinado com aquele papel específico naquela posição, e trocar o papel é sair da distribuição de treino — o comportamento fica pior de um jeito que ninguém consegue depurar.

> 🗣️ "O resultado da ferramenta não é o usuário falando. Existe um papel próprio para isso, e usar o papel errado é sair da distribuição de treino do modelo."

> **Nota:** Bastidor: projetar o JSON da chamada de verdade, copiado da saída da demo da véspera — não um exemplo estilizado. Ver `"arguments": "{\"expressao\": \"0.125 * 480\"}"` com as barras de escape na tela é o que fixa que aquilo é string dentro de string.

### Slide 5 · O schema é parte do prompt · 00:25–00:33

Agora a parte desta aula que costuma surpreender a turma, e eu vou ser bem explícito porque é a coisa mais aplicável do dia.

Como o catálogo de ferramentas é serializado dentro do prompt, **cada palavra dele é engenharia de prompt**. O nome da função. A descrição. O nome de cada parâmetro. O `enum` de valores aceitos. O exemplo que você escreve dentro da descrição do parâmetro. Tudo isso é lido pelo modelo no momento em que ele decide o que chamar e o que passar.

Então: renomear um parâmetro de `expressao` para `q` não é refatoração. Cortar a descrição de três frases para uma palavra não é limpeza de código. As duas coisas são **reescrever o prompt do modelo**, e o efeito aparece na taxa de acerto.

A minha analogia é caixa de ferramentas. Uma caixa etiquetada e uma gaveta com tudo jogado dentro têm o mesmo conteúdo. O que muda é o tempo até achar a chave certa — e, no caso do modelo, se ele acha.

E tem um corolário desconfortável: a descrição da ferramenta não é documentação para a sua equipe. O leitor dela é o modelo. Documentação para gente vai no código; para o modelo, vai no schema. Quando as duas coisas competem, o modelo ganha, porque é ele que está decidindo.

Deixa eu provar isso com número, em vez de afirmar.

> 🗣️ "Trocar `expressao` por `q` e apagar a descrição não é refatoração. É reescrever o prompt — e a taxa de acerto sente."

> **Nota:** Bastidor: não adiantar o resultado da demo aqui. A pergunta "quanto vocês acham que cai?" funciona melhor se eu deixar a sala chutar antes de mostrar a tabela — e quase sempre a sala subestima a queda.

### Slide 6 · [Demo] Três catálogos, uma função · 00:33–00:45

Doze minutos comigo na tela. Duas partes: uma chamada passo a passo, e depois a mesma função com três catálogos diferentes.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> 🗣️ "A função executada é idêntica nos três. Muda só o que o modelo lê — e é isso que a tabela vai medir."

> **Nota:** Bastidor: passos na Parte 2. Se a rede cair, projetar a saída salva da véspera. A Parte 1 da demo roda em modo offline com um simulador roteirado, e isso serve para a mecânica; a tabela da Parte 2 **não** pode ser apresentada como medição no modo offline — o script inclusive avisa isso na saída, em letra grande. Dizer em voz alta a data e o modelo da execução real.

### Slide 7 · Como o modelo aprendeu a fazer isso · 00:45–00:55

Antes do intervalo, a pergunta que fecha o Bloco 1: de onde vem essa habilidade? Ninguém programou "quando a pergunta tiver conta, chame a calculadora".

Três caminhos, em ordem de custo.

O mais barato é **exemplo no prompt**: mostrar duas ou três chamadas bem feitas e deixar o aprendizado em contexto da Aula 10 fazer o resto. Funciona. Gasta contexto em toda requisição, e é frágil no formato.

O segundo é **ajuste supervisionado de formato**: pegar dezenas de milhares de exemplos de chamada bem formada e ajustar o modelo neles. É por isso que os modelos de hoje já vêm "com tool calling" — alguém pagou esse SFT antes de vocês. É o Módulo 3 da disciplina aplicado a um formato de saída.

E o terceiro é o mais bonito conceitualmente, e é a leitura de hoje: **Toolformer**, do Schick e colegas, 2023. A ideia é auto-supervisão. O modelo insere candidatos de chamada de API no meio de textos comuns, o sistema executa esses candidatos, e aí vem o critério: mantém-se apenas as chamadas que **reduzem a perda de previsão dos tokens seguintes**. Ou seja, a chamada é considerada boa se ela ajudou o modelo a prever melhor o que vinha depois. Não tem rótulo humano nenhum nesse laço.

Repararam no que isso resolve? O problema de "quem diz se essa chamada foi útil" some. A utilidade passa a ser medida na própria função de perda. Guardem esse truque, porque ele reaparece em raciocínio e em agentes: sempre que alguém consegue transformar "foi útil?" numa quantidade mensurável, a área anda.

> 🗣️ "Toolformer decide se uma chamada presta perguntando se ela ajudou o modelo a prever o resto do texto. Utilidade virou perda — e é por isso que escala sem humano no laço."

> **Nota:** Bastidor: este é o slide de sacrifício se o tempo estourou no Bloco 1 — ele é o único bloco do dia que não é pré-requisito do Lab 6 de amanhã. Se cortar, mandar para a leitura dirigida e dizer isso à turma em voz alta. Depois deste slide vai o intervalo de 10 min.

### Slide 8 · Seis propriedades de uma boa ferramenta · 01:05–01:15

Voltando. A segunda metade da aula é design, e ela é o que vocês vão levar para o projeto.

Seis propriedades. Uma boa ferramenta é: **estreita** — faz uma coisa, e o nome diz qual; **bem nomeada** — porque o nome e a descrição são lidos na hora da escolha, e isso é o slide cinco de novo; **validável por schema** — tipo, obrigatoriedade, `enum`, e o host rejeitando antes de executar em vez de confiar no modelo; **permissionada** — rodando com o mínimo de privilégio, e com ação sensível exigindo confirmação humana; **observável** — cada chamada deixando registro de argumento, resultado, latência e erro; e **com efeito colateral determinístico** — mesma entrada, mesmo efeito, e de preferência idempotente.

Deixa eu insistir nas duas últimas, que são as mais negligenciadas.

Observabilidade: sem registro de trajetória, depurar um agente é impossível. Vocês vão sentir isso no Lab 7. Quando o agente erra na quarta chamada, a resposta final é só o sintoma — o que interessa é o que ele pediu, com que argumento, e o que a ferramenta devolveu. Isso a Aula 26 formaliza.

Determinismo e idempotência: o loop vai repetir a chamada. Não é hipótese, é comportamento. O modelo não entendeu a resposta, ele tenta de novo. Se a sua ferramenta incrementa um contador ou avança um cursor a cada chamada, o retry corrompe o estado e a trajetória fica irreproduzível.

A analogia é: é o mesmo checklist de uma boa API interna, só que o cliente é novo e estranho. É um cliente que lê a documentação rápido, não pede esclarecimento, e às vezes chuta.

> 🗣️ "Projetem ferramenta como quem projeta API para um cliente que lê rápido, nunca pergunta e às vezes chuta. Porque é exatamente esse o cliente."

> **Nota:** Bastidor: as seis propriedades ficam no slide o Bloco 2 inteiro, porque o exercício do slide 13 cobra elas nominalmente. Se alguém perguntar "e o custo em tokens do catálogo?", a resposta é boa e é curta: catálogo grande é prompt grande, e a Aula 24 volta nisso quando dividir ferramentas entre agentes.

### Slide 9 · O catálogo das más ferramentas · 01:15–01:23

O espelho, que é mais divertido e mais útil.

**Vaga.** `dados(query)`, descrição "pega dados". O modelo não tem como decidir quando usar isso, e a taxa de acerto cai — vocês acabaram de ver na tabela da demo.

**Ampla demais.** `executar_sql(comando)`. `rodar_shell(cmd)`. O schema aqui é decorativo: a linguagem inteira cabe no parâmetro, então não existe validação possível. Isso não é um argumento contra ferramentas poderosas; é um argumento a favor de estreitá-las até o que a tarefa exige.

**Silenciosamente com estado.** `proximo_registro()`. Cada chamada depende de um cursor invisível. O modelo repete a chamada, o cursor anda, e ninguém reproduz aquela execução nunca mais.

**Irreversível sem confirmação.** `enviar_email`. `apagar_registro`. `pagar`. E eu quero ser preciso aqui, porque isso vai voltar no exercício: o problema não é ser irreversível. Sistema real precisa fazer coisa irreversível. O problema é ser irreversível **sem um passo de confirmação** — porque aí o custo de um erro deixa de ser um retry e passa a ser um incidente.

E o antipadrão que eu mais vejo, inclusive em código de gente experiente: a pessoa tem vinte ferramentas, acha que é demais, e cria uma ferramenta genérica com um parâmetro `acao`. Isso não reduziu complexidade nenhuma. Isso escondeu a complexidade **do schema** — e o schema era justamente o único lugar onde ela era verificável.

> 🗣️ "Juntar vinte ferramentas numa só com um parâmetro `acao` não simplifica nada. Só tira do schema a única coisa que o schema sabia checar."

> **Nota:** Bastidor: se a turma engatar em segurança aqui — e engata, sempre — reconhecer e devolver para a Aula 26 em uma frase. Hoje o assunto é design; lá é ataque e mitigação. Não gastar mais de um minuto nisso ou o MCP não cabe.

### Slide 10 · O problema N×M · 01:23–01:29

Agora eu mudo de assunto, e a ponte é uma pergunta prática.

Vocês vão sair daqui com uma base RAG do Lab 5, que é uma ferramenta útil. Suponham que vocês queiram usar essa base em quatro lugares: no notebook do projeto, no editor de código de vocês, num assistente de terminal, e num chat interno. Quatro hosts.

E suponham cinco sistemas para integrar: a base RAG, o repositório, o banco, o gerenciador de tickets, o calendário.

Quatro vezes cinco, vinte adaptadores. Cada um com sua autenticação, seu formato de erro, seu ciclo de vida. E cada host novo multiplica.

Com um protocolo comum, cada host implementa **um** cliente e cada sistema expõe **um** servidor. Quatro mais cinco, nove peças. É exatamente a economia que o Protocolo de Servidor de Linguagem trouxe para editores: antes disso, cada editor implementava autocompletar para cada linguagem; depois, cada linguagem expõe um servidor e cada editor fala o protocolo. O MCP é declaradamente inspirado nisso.

E eu quero marcar uma coisa, porque é onde a turma se confunde: dar ferramenta ao modelo **não precisa** de protocolo. Vocês vão fazer isso amanhã na mão, sem protocolo nenhum, e vai funcionar. O que o protocolo resolve é reuso e distribuição.

> 🗣️ "N vezes M adaptadores contra N mais M peças. Protocolo não é sobre dar ferramenta ao modelo — é sobre não reescrever a ferramenta em cada host."

> **Nota:** Bastidor: desenhar a malha de vinte flechas no quadro e depois a estrela com nove. O desenho vende o argumento em dez segundos e nenhum slide faz isso tão bem.

### Slide 11 · MCP: host, cliente, servidor · 01:29–01:38

Agora a arquitetura, e ela tem três papéis. Eu vou usar o quadro do slide três de novo, porque a separação é a mesma.

O **host** é a aplicação onde a conversa acontece e onde o modelo é chamado. É ele que decide o que expor ao modelo e é ele que executa as decisões — igualzinho ao passo três de hoje.

O **cliente** é o componente dentro do host que mantém a conexão com um servidor. Um cliente por servidor, e é o cliente que fala o protocolo.

O **servidor** é um processo separado que expõe capacidades. E aqui está a parte que a turma sempre erra na primeira vez: **o servidor nunca vê o modelo**. Ele não conversa com o modelo, não sabe qual modelo é, não sabe se existe um modelo. Ele responde a um cliente. Quem monta o prompt e chama o modelo é o host.

O transporte é `stdio` — servidor local rodando como subprocesso, conversando por entrada e saída padrão, que é o que vocês vão fazer amanhã — ou HTTP, para servidor remoto. Em cima disso vai JSON-RPC, e o diálogo mínimo tem três verbos: `initialize`, que negocia capacidades; `tools/list`, que descobre o que existe; `tools/call`, que executa.

A analogia que fecha: o servidor é um driver de dispositivo. Ele não sabe qual aplicação vai usá-lo, e é exatamente por isso que ele serve para todas.

E amanhã vocês fazem os dois lados: escrevem um cliente que se conecta a um servidor que já existe, e escrevem um servidor próprio, expondo a base do Lab 5.

> 🗣️ "O servidor MCP nunca vê o modelo. Ele responde a um cliente — a mesma separação do passo três, agora entre processos."

> **Nota:** Bastidor: se perguntarem qual servidor a gente vai usar amanhã, responder concretamente: um servidor de referência instalável por `pip`, rodando por `stdio`, e depois o próprio. Não abrir a lista do ecossistema aqui — o estado do ecossistema é `[definir na oferta]` e eu confiro na semana da aula, não cito de memória.

### Slide 12 · Recurso, ferramenta e prompt: quem decide · 01:38–01:43

Última peça conceitual, e ela é curta e vale prova.

Um servidor MCP expõe três tipos de coisa, e o que distingue as três não é o formato — é **quem escolhe usar**.

**Ferramenta** é ação, e quem escolhe é o **modelo**. É o `tools/call`.

**Recurso** é dado endereçável por identificador — um arquivo, uma linha de banco, um documento do acervo. E quem escolhe anexar aquilo ao contexto é a **aplicação**, ou o usuário clicando. Não o modelo.

**Prompt** é um template parametrizado que o **usuário** invoca explicitamente.

Modelo, aplicação, usuário. Três donos de decisão diferentes, e o erro clássico é confundir os dois primeiros: expor o acervo inteiro como uma ferramenta `ler_arquivo(caminho)` quando o que se queria era um recurso. A diferença prática é enorme — na primeira versão, o caminho está no alcance do modelo; na segunda, não está.

E do lado do cliente existem capacidades simétricas, que eu menciono para vocês reconhecerem quando virem: o servidor pode pedir uma geração ao modelo do host, pode receber quais raízes do sistema de arquivos ele tem direito de ver, e pode pedir ao usuário um dado que falta.

Agora, três coisas que o MCP **não** resolve, e eu prefiro dizer isso do que deixar vocês descobrirem no projeto. Schema ruim continua ruim depois de padronizado — protocolo não conserta nome vago. Permissão continua sendo decisão do host. E servidor de terceiro amplia a superfície de injeção indireta: o texto que volta de uma ferramenta entra no mesmo campo da instrução do sistema, exatamente como o documento recuperado da Aula 19.

> 🗣️ "Ferramenta o modelo escolhe, recurso a aplicação escolhe, prompt o usuário escolhe. Quem confunde os dois primeiros entrega o caminho de arquivo para o modelo sem querer."

> **Nota:** Bastidor: não entrar em detalhe de esquema de URI de recurso nem em versão de especificação — não cabe e não é o que a ementa pede. Se alguém perguntar sobre revisões da especificação, responder que o protocolo é versionado por data e que a versão vigente é `[definir na oferta]`, conferida na semana da aula.

### Slide 13 · [Exercício] Reescrever o schema ruim · 01:43–01:50

Sete minutos, em dupla, com um schema de verdade na tela — e é um schema ruim de verdade, do tipo que eu já vi em produção.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> 🗣️ "Uma ferramenta chamada `dados` que faz três coisas. Sete minutos para transformar isso em duas ou três ferramentas que um modelo consegue escolher."

> **Nota:** Bastidor: enunciado e correção na Parte 3. Cronometrar de verdade: 5 min de dupla, 2 min de correção. A ferramenta de e-mail é a que interessa na correção.

### Slide 14 · Fechamento: amanhã vocês fazem na mão · 01:50–02:00

Deixa eu juntar as quatro frases da aula e mandar vocês para casa.

Primeira: o modelo pede, o host executa. Cinco passos, e o modelo é dono de um.

Segunda: o schema é parte do prompt. Nome, descrição, nome de parâmetro — e vocês viram a taxa de acerto mudar sem uma linha de código mudar.

Terceira: boa ferramenta é estreita, bem nomeada, validável, permissionada, observável e determinística. Má ferramenta é vaga, ampla, com estado escondido, ou irreversível sem confirmação.

Quarta: protocolo não é sobre dar ferramenta ao modelo. É sobre `N` mais `M` em vez de `N` vezes `M`.

Amanhã é o Lab 6, e ele tem três partes. Primeiro vocês implementam o loop **na mão**, sem framework nenhum: definir o schema, detectar a chamada na resposta, fazer o parsing, despachar, executar, devolver como mensagem `tool`, sintetizar. Com três ferramentas — calculadora, busca na base do Lab 5, e uma consulta a uma API pública sem chave. Depois vocês conectam um cliente a um servidor MCP que já existe. E por último escrevem um servidor MCP próprio com uma ferramenta.

E a ordem é de propósito, então deixa eu justificar: fazer na mão antes do framework existe para vocês verem o protocolo antes da abstração. Depois de escrever o parsing e o despacho com as próprias mãos, nenhuma biblioteca de agente vai parecer mágica para vocês — vai parecer o que ela é, um laço com um parser.

Ah, e duas coisas operacionais. Amanhã eu recolho a **Entrega 1 do projeto**: a proposta. Cinco itens, e eu vou dizer agora para ninguém ser pego de surpresa — problema claro e verificável, duas técnicas do curso, plano de avaliação com métrica por camada, divisão de trabalho, e viabilidade em free tier. Vale cinco por cento da nota final e eu dou devolutiva na hora. E a leitura de hoje é o Toolformer, com a pergunta dirigida do slide.

> 🗣️ "Amanhã vocês escrevem o parsing e o despacho na mão. Depois disso, nenhum framework de agente vai parecer mágica — vai parecer um laço com um parser."

> **Nota:** Bastidor: projetar os cinco itens da proposta e ficar trinta segundos em silêncio para a turma fotografar. Dizer o formato do que recolher amanhã: duas páginas, PDF ou link, um por equipe. Não estourar o horário — amanhã é lab e lab que começa atrasado termina sem o último checkpoint.

---

## Parte 2 — Demonstração guiada

Doze minutos, `codigo/demo-tool-calling.py`, só biblioteca padrão. A demo tem duas metades com objetivos diferentes: a primeira torna visível *quem executa o quê*; a segunda transforma "o schema é parte do prompt" em número na tela.

Insumos da véspera: o script rodado em modo `api` com `--salvar-saida`, o arquivo de saída no pendrive, e a data e o identificador do modelo anotados. Confirmar na véspera que o modelo do provedor ainda está na lista dele.

**1.** **[Abro o script e mostro o catálogo de uma ferramenta só]** Este é o catálogo. Uma ferramenta, `calcular_expressao`, com descrição de três frases e um parâmetro chamado `expressao`, com exemplo dentro da descrição. E eu quero que a turma repare numa coisa antes de qualquer execução: isso aqui vai ser **serializado dentro do prompt**. Não existe canal separado, não existe registro mágico. É texto que o modelo vai ler.

**2.** **[Rodo `--parte 1` e mostro o JSON cru que o modelo devolveu]** A pergunta é "quanto é doze e meio por cento de quatrocentos e oitenta?". Olha o que voltou: nenhuma prosa. Um objeto com `tool_calls` dentro, e dentro dele `id`, `name` e `arguments`. E olha o `arguments` com atenção — ele é uma **string** com um JSON dentro, com as barras de escape à mostra. JSON dentro de JSON. Todo mundo estranha isso na primeira vez, e é assim que a interface é.

**3.** **[Aponto a validação no código antes do despacho]** Antes de executar, olha o que o host faz. Tem um regex aqui que só aceita dígitos e os operadores aritméticos. Se o modelo tivesse mandado `import os` dentro da expressão, esta linha recusaria. Essa linha é a propriedade "validável" e a propriedade "permissionada" no mesmo lugar — e ela existe porque eu não confio no argumento que veio, mesmo quando ele veio bem formado.

**4.** **[Executo e mostro o retorno e a mensagem de papel `tool`]** O host executou. Resultado sessenta. E agora o resultado volta para a conversa como uma mensagem de papel `tool`, com o mesmo identificador da chamada. Olha a lista de mensagens crescendo na tela: sistema, usuário, assistente com a chamada, `tool` com o resultado. Essa é a conversa que o modelo vê no próximo turno.

**5.** **[Mostro a resposta final sintetizada]** E aí o modelo lê o resultado e escreve a resposta em prosa. Fim do ciclo. Cinco passos, e eu quero cravar o que aconteceu: o modelo emitiu **texto**. Este script obedeceu. Em nenhum momento houve código rodando dentro do modelo.

**6.** **[Mudo para `--parte 2` e explico o desenho do experimento]** Segunda metade. Seis perguntas com gabarito aritmético, porque eu quero um critério de acerto que não dependa de julgamento — ou o número saiu certo, ou não saiu. E três catálogos: o bom, que vocês já viram; um magro, com a função renomeada para `calc`, descrição de uma palavra e parâmetro `q`; e um vago, chamado `ferramenta`, descrição "uso geral", parâmetro `entrada`. E a coisa mais importante do experimento: **a função executada é a mesma nas três**. O código não muda. Muda o que o modelo lê.

**7.** **[Rodo e leio a tabela, com atenção às duas colunas]** Olha a tabela. E eu quero que a leitura seja feita nas duas colunas juntas, não só na última. A coluna "chamou" mostra que o modelo quase sempre **chama** a ferramenta, nos três catálogos — o formato está garantido pela decodificação restrita do serving. A coluna "acertou" é a que despenca. Ou seja: bem formado não é correto. O JSON é impecável e o argumento é lixo. Guardem essa distinção, porque ela é a diferença entre um lab que funciona e um sistema que funciona.

**8.** **[Fecho na seção "o que esta demo não mostrou"]** E o script termina listando o que ficou de fora, que é o Bloco 2 de hoje. Nada aqui pediu confirmação para agir. O único registro de trajetória é este `print`, que não serve para nada em produção. E as ferramentas estão **cravadas** neste arquivo: se eu quiser usar esta calculadora em outro programa, eu reescrevo tudo. Esse terceiro item é o problema que o MCP resolve.

> **Nota de contingência:** Bastidor: se a chamada de API falhar, o script cai no simulador roteirado e avisa em letra grande na saída. Nesse caso, os passos 1 a 5 continuam válidos e valiosos — a mecânica do loop é real. O passo 7 **não** pode ser apresentado como medição: nesse caso eu projeto a tabela da saída salva da véspera e digo em voz alta a data e o modelo. Se nem o arquivo salvo estiver à mão, refazer o argumento no quadro e ser honesto: "eu medi ontem, o número está no arquivo que eu não tenho aqui" é infinitamente melhor que inventar um número. Não editar o script ao vivo — a única variação prevista é o `--parte`.

---

## Parte 3 — Hands-on

Sete minutos, em dupla, com o schema ruim projetado. O objetivo não é a sintaxe do JSON — é forçar a turma a escrever uma descrição **para o modelo ler**, que é uma habilidade nova e desconfortável.

**1.** **[Projeto o schema `dados` e formo as duplas]** Sete minutos, em dupla. Este schema está na tela e ele é real — do tipo que eu já vi em produção mais de uma vez:

```json
{
  "name": "dados",
  "description": "pega dados do sistema",
  "parameters": {
    "type": "object",
    "properties": {
      "acao": {"type": "string"},
      "params": {"type": "object"}
    }
  }
}
```

E o contexto: esse `dados` hoje faz três coisas. Ele consulta o regulamento por texto, ele lê a matrícula de um aluno por código, e ele envia um e-mail de confirmação.

Três coisas na folha. Primeira: duas ou três ferramentas estreitas no lugar do `dados`, com nome, descrição de uma ou duas frases escrita para o modelo, e parâmetros com tipo e nome explícito — com `enum` onde couber. Segunda: qual delas exige confirmação humana antes de executar, e por quê em uma frase. Terceira: qual das seis propriedades do slide oito o schema original violava mais, com uma frase de justificativa.

*Bastidor — erros comuns:* manter uma ferramenta só e melhorar o nome dela, sem separar as três ações — é a resistência mais comum, e a resposta é que o modelo escolhe pelo nome, então três ações num nome é uma escolha impossível; escrever descrição para humano ("Endpoint responsável por recuperar dados do subsistema acadêmico"), que é documentação e não ajuda a decisão; deixar o parâmetro do e-mail como `params: object`, o que joga fora a validação exatamente na ferramenta mais perigosa das três; esquecer o `enum` no que é obviamente enumerável; e listar "irreversível" como propriedade violada quando a propriedade violada é **permissionada** — irreversível não é defeito, irreversível sem confirmação é.

*Como recolher:* aos 01:48 eu paro a sala. Peço para duas duplas lerem em voz alta só a **descrição** que elas escreveram para a ferramenta de e-mail, e comparo as duas em voz alta: qual das duas eu escolheria se eu fosse o modelo, e por quê. Aí eu faço a pergunta que fecha o Bloco 2: onde mora a confirmação — no schema ou no host? A resposta que eu quero ouvir é "no host", e quando alguém diz isso, a aula fechou: o schema descreve, o host decide. Se sobrar trinta segundos, eu comento o antipadrão `acao`: a dupla que manteve um parâmetro de ação está reinventando o `dados` com nome melhor.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência. E nesta aula ela tem uma particularidade que
vale dizer em voz alta se a pergunta vier: **esta aula não tem apêndice matemático próprio**, porque
não há derivação nenhuma no fluxo dela. O que existe é ponteiro para o fundamento formal que a aula
mobiliza e que mora em outra aula. Os três casos abaixo são os que aparecem de verdade.

> **Nota:** Bastidor: o custo de qualquer item abaixo sai do Bloco 2, e o Bloco 2 tem dois trechos
> intocáveis — o MCP (slides 10 a 12, que é o que a ementa pede) e os 7 min do exercício. A ordem de
> preferência para sacrificar, se for preciso: primeiro o Conceito 5 (slide 7, como o modelo
> aprendeu, que já é o slide de sacrifício declarado), depois o catálogo das más ferramentas. Nunca
> o exercício e nunca a caixa "o que o MCP não resolve".

**Item 1 — "essa diferença de taxa entre os catálogos é significativa?" (~4 min).**
A melhor pergunta que a demo pode gerar, e eu quero que ela venha. A resposta honesta é: com seis
perguntas e três catálogos, **não sei** — e é por isso que o desafio pós-aula pede para rodar o
catálogo bom duas vezes. Se sobrar tempo, eu faço a conta grosseira no quadro: seis perguntas, uma
diferença de uma acerto é 17 pontos percentuais, e o intervalo de confiança de uma proporção com
`n = 6` é largo o suficiente para engolir isso. O tratamento formal — intervalo e teste pareado —
está no **Apêndice A.5 da Aula 28**, e a versão "uma semente não é resultado" está no **Apêndice A.5
da Aula 9**, que a turma já leu. Se não houver tempo, a frase é: "a tabela mostra a direção do
efeito, não o tamanho dele; medir o tamanho é a Aula 28".

**Item 2 — "quanto custa o loop repetir a chamada?" (~3 min).**
Costuma vir junto da propriedade 6 do slide 8, quando eu digo que o retry é comportamento e não
hipótese. Eu não abro a conta aqui, porque ela é o slide 11 da Aula 23 com fórmula e tudo. O que eu
digo é a forma do resultado: o custo não é o número de passos vezes o custo de um passo — cada volta
reenvia a trajetória acumulada, então o total cresce com o **quadrado** dos passos. A soma está no
**Apêndice A.1 da Aula 23**. Isso planta a aula seguinte em quinze segundos.

**Item 3 — "o `N × M` não é só uma conta?" (~2 min).**
É, e é de propósito. Se alguém apontar que o slide 10 é aritmética de escola, eu concordo e uso a
deixa: o valor do slide é o desenho, não a conta. Vinte flechas emaranhadas contra nove, no quadro,
em dez segundos. E aproveito para plantar que a **mesma** multiplicação reaparece na Aula 24 com
consequência bem menos inocente — orçamento de cinco passos vezes cinco trabalhadores dá vinte e
cinco chamadas antes de qualquer proteção global (**Apêndice A.2 da Aula 24**).

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 14 da Parte 1 — as quatro frases de síntese, o desenho das três partes do Lab 6 com a justificativa de fazer na mão antes do framework, o aviso dos cinco itens da Entrega 1 recolhida amanhã, e a leitura do Toolformer com a pergunta dirigida.

> 🗣️ "Hoje o modelo ganhou mãos e continuou sem poder executar nada. Amanhã vocês escrevem o programa que obedece — e na Aula 23 a gente põe isso num loop com um objetivo."

---

*Roteiro do Instrutor · Aula 21 de 30 · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
