# Sistemas multiagente e orquestração

## Slide 1 · Abertura: um agente virou vários · 00:00–00:05

Boa noite, pessoal. Aula passada eu deixei cinco palavras na cabeça de vocês: modelo, ferramentas, loop, objetivo, critério de parada. E dois testes: o caminho é conhecido? existe verificador para o passo intermediário?

Também deixei um caso que eu quero recuperar em uma frase, porque ele é a régua de hoje. O agente de programação funciona bem porque a suíte de testes é um verificador barato que não mente. A arquitetura transfere para outros domínios; o verificador não transfere.

Hoje a gente coloca mais de um agente na mesa. Orquestrador com trabalhadores, pipeline de estágios, debate, painel de especialistas. E eu vou avisar de saída: uma parte considerável desta aula é sobre por que vocês provavelmente não precisam de nenhum deles. Isso não é pessimismo meu — é a mesma régua da aula passada aplicada a uma peça a mais.

> Ideia central: "Semana passada foi um agente. Hoje são vários — e eu vou passar boa parte da aula argumentando contra vários."

## Slide 2 · A tese: multiagente é resposta a limite, não degrau de sofisticação · 00:05–00:10

Deixa eu cravar a tese antes de mostrar padrão nenhum, porque senão a aula vira catálogo e catálogo é a pior forma de aprender arquitetura.

Sistema multiagente é uma resposta a **limites concretos** de um agente único. Limite de especialização, limite de paralelismo, limite de contexto. Quando um desses limites está doendo, dividir é a resposta certa e eu vou mostrar como. Quando nenhum está doendo, dividir acrescenta coordenação, custo e modos de falha, e não acrescenta capacidade.

E eu quero ser direto sobre uma coisa, porque ela é conteúdo desta aula e não opinião minha: muita coisa que hoje é vendida como sistema multiagente resolve melhor com **um** agente e boas ferramentas. Uma ferramenta bem descrita é mais barata, mais testável e mais previsível que um agente inteiro. Vocês já sabem por quê — no Lab 6 vocês descobriram que descrição de ferramenta é prompt. Então escrever uma ferramenta boa é escrever um prompt bom, com a vantagem de que ferramenta não tem loop, não tem trajetória e não tem fatura própria.

A analogia é monólito e microserviços, e ela é exata. Quebra-se um monólito por limite de time, de deploy ou de escala — não porque microserviço é mais moderno. Quem quebra sem motivo herda toda a coordenação e nenhum benefício. É a mesma decisão, com as mesmas consequências.

> Ideia central: "Multiagente é resposta a limite, não degrau de sofisticação. Se nenhum limite está doendo, dividir só acrescenta coordenação e fatura."

## Slide 3 · As três razões que se sustentam · 00:10–00:20

Três razões, e eu quero que vocês consigam nomear qual delas se aplica ao caso de vocês. Se não conseguirem nomear nenhuma, a resposta do exercício está pronta.

**Razão um, especialização.** Cada agente tem prompt de sistema próprio, catálogo de ferramentas próprio e critério de sucesso próprio. Isso reduz a ambiguidade da decisão em cada ponto: um agente que só extrai campos de documento decide entre menos opções do que um agente que faz tudo. Menos opções, menos erro de seleção.

**Razão dois, paralelismo.** Subtarefas independentes rodam ao mesmo tempo. E aqui eu preciso ser preciso: o ganho é em latência de parede, **não** em custo. Três buscas em paralelo custam exatamente o que três buscas em série custam. Se o problema de vocês é fatura, paralelismo não ajuda; se é usuário esperando, ajuda muito.

**Razão três, contexto limitado por agente.** Cada agente carrega só a trajetória do seu pedaço. Lembram do problema da aula passada: trajetória longa custa mais e piora a precisão do modelo em achar o que importa. Dividir o trabalho divide a trajetória, e isso é um ganho real e mensurável.

Fora dessas três, o que sobra costuma ser estética de arquitetura. E deixa eu marcar um caso que a turma sempre traz: "o prompt ficou grande, então eu preciso dividir". Não. Prompt grande pede edição de prompt. O que pede divisão é **trajetória** grande, que é outra coisa completamente diferente — prompt é o que eu escrevi, trajetória é o que o sistema acumulou.

> Ideia central: "Especialização, paralelismo, contexto por agente. Se vocês não conseguem nomear qual das três, vocês não têm razão para dividir — têm gosto."

## Slide 4 · Padrão 1: orquestrador-trabalhadores · 00:20–00:30

Primeiro padrão, e é o mais usado por um bom motivo: ele é o mais fácil de depurar.

Um agente central recebe o objetivo, decompõe, decide qual trabalhador chamar, recebe os resultados e sintetiza. Os trabalhadores não conversam entre si — falam só com o orquestrador. E olha uma coisa que economiza muito dinheiro: os trabalhadores podem ser burros de propósito. Muitos deles não são agente nenhum, são função determinística. Um "trabalhador de busca" que é literalmente a função `buscar` do Lab 5 é melhor que um agente de busca, porque não tem loop, não tem trajetória e não tem como se perder.

O que faz esse padrão depurável é que existe **um único ponto onde a decisão acontece**. Quando dá errado, eu leio a trajetória do orquestrador e sei o que ele escolheu e por quê. Comparem com um sistema em que quatro agentes conversam entre si: aí não existe um lugar para ler.

E o erro de implementação clássico, que eu vejo em todo projeto: o orquestrador repassa a trajetória inteira para cada trabalhador. Isso destrói a razão três — contexto limitado por agente — e multiplica o custo, porque cada trabalhador agora paga pelo histórico do sistema. A regra é: o trabalhador recebe a **menor entrada suficiente** e devolve a **menor saída suficiente**. Se o trabalhador precisa do histórico todo para funcionar, ele não é um trabalhador, ele é uma cópia do orquestrador.

A analogia é editor-chefe e pauteiros. O chefe não escreve as matérias, mas é o único que decide o que entra na edição. E ele não manda a pauta inteira do jornal para cada repórter.

> Ideia central: "Trabalhador recebe a menor entrada suficiente e devolve a menor saída suficiente. Se ele precisa do histórico todo, ele não é trabalhador — é uma cópia caríssima do orquestrador."

## Slide 5 · Padrão 2: pipeline de estágios · 00:30–00:38

Segundo padrão, e é o que eu mais recomendo, o que é uma frase estranha de dizer numa aula sobre multiagente.

A saída de um agente é a entrada do seguinte, com a ordem fixada de antemão: extrair, normalizar, classificar, redigir. Não existe decisão de roteamento, porque a ordem já está no código. E por causa disso ele tem três virtudes que nenhum outro padrão tem: é o mais previsível, é o mais barato de testar, e é o único em que dá para avaliar cada estágio separadamente — o que vai ser exigido de vocês no Lab 8.

Agora, olha o que esse padrão é de verdade. Ele é o **workflow determinístico da aula passada** com LLMs nos estágios. É o lado "trilho de trem" do slide da Aula 23. Se o problema de vocês encaixa aqui, quase sempre é aqui que ele deve ficar.

E deixa eu tirar uma pressão social de cima de vocês: chamar isso de sistema multiagente para parecer mais avançado não ajuda ninguém. É um pipeline. Ser um pipeline é uma **virtude** — código previsível, testável, com falha localizável. Eu prefiro corrigir um pipeline de quatro estágios do que depurar dois agentes conversando, e essa preferência é técnica.

> Ideia central: "Pipeline de estágios é o workflow determinístico da aula passada com LLM dentro. E ser um pipeline é uma virtude, não uma confissão."

## Slide 6 · Padrão 3: debate e crítico · 00:38–00:47

Terceiro padrão, e é aqui que eu preciso ser mais cético, porque é o que tem mais literatura entusiasmada e menos ganho garantido.

Duas variantes do mesmo mecanismo, gerar e depois julgar. No **crítico**, um agente produz e outro avalia contra critérios explícitos, devolvendo para revisão — e o número de voltas é uma, no máximo duas. No **debate**, dois ou mais agentes defendem posições e um juiz decide.

E agora a condição em que isso funciona, que é uma condição só: o crítico ganha quando ele tem acesso a **algo que o gerador não tem**. Um verificador. Uma fonte. Um teste. Um cálculo. Se o crítico tem exatamente a mesma informação e o mesmo modelo do gerador, o que vocês compraram por duas vezes o custo foi sobretudo variância — o crítico vai discordar às vezes, vai concordar às vezes, e a diferença entre esses dois casos não é qualidade.

Pior: sem fonte externa, o desacordo entre dois agentes pode convergir para o erro mais **fluente**, não para a resposta correta. Isso é o Conceito 7 da aula passada em escala de sistema — autocrítica sem verificador é o modelo defendendo o que acabou de escrever, agora com dois modelos fazendo isso e um terceiro pagando a conta.

A analogia é revisão por pares. Ela funciona quando o revisor pode conferir os dados. Revisor que só leu o resumo faz revisão de estilo, e revisão de estilo é útil — só não é revisão de correção.

> Ideia central: "Crítico só ganha se ele vê algo que o gerador não vê. Se os dois têm a mesma informação e o mesmo modelo, vocês pagaram o dobro por variância."

## Slide 7 · Padrão 4: painel de especialistas · 00:47–00:55

Quarto e último padrão, e eu prometo que este é rápido, porque ele é o mais fácil de usar errado.

Vários agentes com prompts de domínio diferentes respondem em paralelo à mesma pergunta, e um agregador combina — por voto, por síntese, ou escolhendo o melhor. Isso faz sentido quando as perspectivas são **genuinamente** diferentes: um analisa risco jurídico, outro analisa custo, outro analisa prazo. Três lentes reais sobre o mesmo objeto, e um agregador com regra explícita de combinação.

Quando é que isso desanda? Quando os especialistas diferem apenas por um adjetivo no prompt. "Você é um analista sênior", "você é um analista detalhista", "você é um analista crítico". Isso não é painel, isso são três amostras do mesmo modelo com prompt levemente diferente, e o resultado são três respostas parecidas e uma fatura triplicada.

E uma distinção que vale a prova: painel **não** é auto-consistência. Auto-consistência é o mesmo prompt amostrado várias vezes com temperatura e depois votado, e ela tem uso legítimo em tarefa com resposta verificável — a gente viu isso na Aula 13. Painel é prompt diferente para papel diferente. O mecanismo é outro e o motivo é outro.

> Ideia central: "Se os seus especialistas diferem por um adjetivo no prompt, vocês não têm um painel. Vocês têm três amostras e uma fatura triplicada."

## Slide 8 · [Demo] A mesma tarefa, duas arquiteturas · 01:05–01:13

Voltando. Eu passei o primeiro bloco descrevendo padrões, e descrição é fácil. Agora eu quero número.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> Ideia central: "Mesma tarefa, mesma resposta final, duas arquiteturas. A diferença está em três números — chamadas, tokens e passos — e é para eles que eu quero que vocês olhem."

## Slide 9 · Coordenação: contexto não se compartilha de graça · 01:13–01:18

Agora os custos que não aparecem na fatura, e eles são três falhas que simplesmente não existem em agente único.

Dois agentes só cooperam pelo que trocam, e o que trocam é texto. Daí: **perda na tradução** — o trabalhador recebe uma versão resumida do objetivo e resolve um problema ligeiramente diferente, com competência total, e ninguém percebe porque a resposta é bem escrita. **Duplicação de trabalho** — dois trabalhadores buscam a mesma coisa porque nenhum dos dois sabe do outro. E **estado inconsistente** — dois agentes com versões diferentes do mesmo fato, os dois convictos.

Mitigar isso exige protocolo explícito: quem escreve onde, com que formato, e qual é a fonte de verdade quando há divergência. Sim, é isso mesmo: é o mesmo tipo de problema de sistema distribuído que vocês vão ver em outra disciplina, com a diferença cruel de que aqui o transporte é linguagem natural, que é o formato mais ambíguo disponível.

E é isso que eu quero cravar: passar de um processo para dois não dobra a complexidade. Introduz uma **classe nova** de falha. Linguagem natural facilita escrever o sistema e dificulta diagnosticá-lo — e essa troca é péssima num sistema que vocês vão ter que avaliar.

> Ideia central: "Os agentes não se coordenam sozinhos por falarem em linguagem natural. Linguagem natural é o transporte mais ambíguo que existe — ela facilita escrever e dificulta depurar."

## Slide 10 · Orçamento compartilhado e custo multiplicado · 01:18–01:24

Uma conta de trinta segundos que já salvou fatura de gente.

No agente único, `max_passos` é um número e pronto. Com N agentes, cada um com o seu teto, o pior caso não é a soma dos tetos — é o **produto**. Um orquestrador com cinco passos que pode chamar trabalhadores de cinco passos cada admite vinte e cinco chamadas de modelo antes de qualquer proteção global. E se um trabalhador puder chamar outro, vocês fazem a conta.

Então a regra é: orçamento **compartilhado**. Um contador único, decrementado por qualquer agente do sistema, e o sistema inteiro aborta quando ele zera. Não é elegante, é necessário.

Latência segue a topologia, e vale decorar as três formas: no pipeline, ela é a **soma** dos estágios; no paralelo, é o **máximo** dos ramos; no orquestrador com rodadas, é a soma dos máximos de cada rodada. Isso é o que vocês precisam para prometer um tempo de resposta a um usuário.

> Ideia central: "Com vários agentes, o pior caso é o produto dos tetos, não a soma. Orçamento por agente é a forma mais educada de descobrir isso na fatura."

## Slide 11 · Propagação de erro · 01:24–01:29

Esta é a conta que condena pipeline longo, e ela é uma multiplicação.

Se cada estágio acerta com probabilidade `p`, e o erro de um estágio compromete o resultado final, a taxa de sucesso do sistema é `p` elevado a `N`. Com `p` igual a noventa e cinco por cento — que é bom para uma etapa com LLM — cinco estágios dão setenta e sete por cento. Dez estágios dão sessenta por cento. Cada estágio a mais é uma multiplicação, não uma adição, e é assim que um sistema em que cada peça funciona bem entrega mal.

E tem um agravante que é o pior de todos. Erro em estágio inicial chega ao estágio final **com a mesma fluência** de um dado correto. O estágio três não tem como saber que a saída do estágio dois está errada — ele recebe texto bem escrito e trabalha em cima.

Daí a única mitigação que funciona de verdade: verificação **por estágio**, com o estágio parando em vez de repassar. É melhor um sistema que falha alto no estágio dois do que um que entrega resposta bonita e errada no estágio dez. E isso é exatamente o gancho do Lab 8, na Aula 28, quando vocês vão medir métrica por camada — não uma métrica no fim do pipeline.

A analogia é linha de montagem sem inspeção intermediária. O defeito só aparece no fim, e aí o produto inteiro é perda.

> Ideia central: "Noventa e cinco por cento por estágio, cinco estágios: setenta e sete por cento no fim. Cada estágio a mais é uma multiplicação — e o próximo agente não vai corrigir, porque ele não sabe que há o que corrigir."

## Slide 12 · Quando multiagente é overkill: o teste de três perguntas · 01:29–01:35

Agora o instrumento que eu quero que vocês levem para a Entrega 2. Três perguntas, com resposta **escrita**, antes de dividir qualquer coisa.

**Pergunta A: qual das três razões se aplica, nominalmente?** Especialização, paralelismo ou contexto por agente. Se a resposta não é uma dessas três, não divide.

**Pergunta B: o que o segundo agente vê que o primeiro não veria?** Essa é a pergunta que mata mais arquiteturas. Se a resposta é "nada, só um prompt diferente", então é um prompt diferente e não um agente. Trocar de prompt custa uma chamada; acrescentar um agente custa uma arquitetura.

**Pergunta C: como esta arquitetura falha, e onde eu leio a falha?** Se não existe um lugar único onde eu leio a trajetória do sistema inteiro, o sistema não é depurável. E isso não é um problema teórico: é o problema da primeira semana.

E aqui está a postura do curso, dita com todas as letras: **muito do que é vendido como multiagente resolve melhor com um agente e boas ferramentas.** Isso não é conservadorismo — é o mesmo critério da aula passada. Acrescentar peça sem verificador acrescenta modo de falha. Um agente com cinco ferramentas bem descritas é mais barato, mais testável e mais previsível que cinco agentes conversando, e vocês já sabem escrever ferramenta boa, porque isso foi o Lab 6.

> Ideia central: "A pergunta que mata mais arquiteturas é a segunda: o que o segundo agente vê que o primeiro não veria? Se a resposta é 'nada, só um prompt diferente', vocês têm um prompt, não um agente."

## Slide 13 · Panorama crítico de frameworks · 01:35–01:41

Vocês vão me perguntar sobre framework, então eu vou responder de forma organizada e curta. Três categorias, pelo que cada uma resolve.

**Grafos de estado** — LangGraph e semelhantes. O sistema é um grafo: nós, estado explícito, arestas condicionais, pontos de interrupção. É bom quando o fluxo tem ciclos e checkpoints, e a curva de aprendizado que vocês pagam é a do modelo de estado dele, não a do LLM. **Papéis e equipes** — CrewAI e semelhantes. Agentes declarados por papel e objetivo, com delegação embutida. Prototipa rápido, e o preço é que a abstração de "papel" esconde exatamente aquilo que precisa ser inspecionado. **SDKs de agentes dos provedores.** O loop de ferramentas mantido pelo fornecedor, colado na API. Menor atrito, maior acoplamento, e o loop deixa de ser seu.

E o que nenhum deles faz: decidir. Quem decide é o modelo. Framework organiza chamadas, guarda estado, padroniza retentativa. Isso é útil — e é bom que fique claro que é isso.

Então o critério honesto de escolha, e é um só: **eu consigo ler a trajetória inteira que esse framework produziu?** Se eu não consigo, ele não serve para um sistema que eu vou avaliar. E avaliar é obrigatório nesta disciplina, então esse critério não é negociável aqui.

Por isso a ordem do curso é essa: loop na mão primeiro, framework depois. Quem monta o loop primeiro avalia framework por conveniência, com base de comparação. Quem começa pelo framework não tem base nenhuma — e é literalmente o Checkpoint 5 do Lab 7, semana que vem.

> Ideia central: "Framework não decide nada: quem decide é o modelo. O critério de escolha é um só — eu consigo ler a trajetória inteira que ele produziu?"

## Slide 14 · Estudos de caso · 01:41–01:45

Três casos, quatro minutos, e em cada um eu quero dizer qual é a arquitetura **mínima**.

**Deep research.** Um orquestrador planeja subperguntas, trabalhadores buscam em paralelo, um sintetizador redige com citação. Aqui multiagente se justifica pelas três razões ao mesmo tempo — especialização, paralelismo e contexto por agente. E olha o ponto crítico: a citação. É ela que dá verificador ao resultado. Sem citação, é um painel produzindo texto confiante.

**Automação de suporte.** O desenho quase sempre certo é pipeline de estágios: classificar intenção, recuperar histórico e política, redigir, e um portão de aprovação humana para ação irreversível. "Um agente por tipo de ticket" é o caso mais comum de multiagente decorativo que eu vejo — tipo de ticket é um parâmetro de roteamento, não uma especialização de decisão.

**Agentes de dados.** Um agente com ferramentas boas — executar SQL, ler schema, rodar script — e um verificador barato: a consulta executa? o total fecha com o controle? Dividir em "agente de SQL" e "agente de análise" costuma render dois agentes discutindo sobre um schema que nenhum dos dois leu inteiro.

E o erro que amarra os três: copiar a arquitetura do deep research para o caso de suporte. As três razões não se aplicam, e a fatura triplica sem ganho.

> Ideia central: "Deep research justifica as três razões de uma vez. Suporte é pipeline. Agente de dados é um agente com um verificador. Copiar o primeiro nos outros dois é o erro mais caro desta aula."

## Slide 15 · [Exercício] Enxugar a arquitetura · 01:45–01:50

Cinco minutos, em dupla, e é o exercício mais útil da aula.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> Ideia central: "Três arquiteturas infladas. Para cada uma: a versão mínima equivalente, e qual das três razões sobrevive. Se nenhuma sobrevive, escrevam 'nenhuma' — é resposta."

## Slide 16 · Fechamento: princípios antes de ferramentas · 01:50–02:00

Deixa eu juntar as peças da aula em três frases e fazer a ponte.

Primeira: multiagente é resposta a limite — especialização, paralelismo, contexto por agente — e se nenhum limite está doendo, dividir acrescenta coordenação, custo e classe nova de falha. Segunda: os custos são calculáveis antes de escrever código. Produto dos tetos para o pior caso, `p` elevado a `N` para a taxa de sucesso, e a topologia dita a latência. Terceira: framework nenhum decide nada, e o critério de escolha é se dá para ler a trajetória inteira.

E é por isso que o curso é organizado nessa ordem. Semana que vem é o Lab 7, e ele é, na minha opinião, o lab mais importante do módulo. Vocês vão implementar o loop ReAct **na mão** — prompt de sistema, parsing de ação, execução de ferramenta, memória da trajetória, critério de parada, limite de passos. As ferramentas vão ser busca, calculadora, e a base RAG que vocês construíram no Lab 5, que volta como ferramenta do agente de vocês. Depois vocês vão registrar a trajetória completa e analisá-la por escrito. E só no fim, com o loop de vocês funcionando na tela, vocês vão reimplementar a mesma coisa com um framework — e aí a comparação controle versus conveniência vai ser uma medida, não uma opinião de blog.

Para a semana: rodar a demo nos quatro modos e anotar as razões de tokens; e aplicar o teste de três perguntas ao projeto de vocês, com as três respostas escritas. Se a resposta da pergunta B for "nada, só um prompt diferente", tragam as duas versões da arquitetura para a Entrega 2 e a justificativa da escolha. Isso conta a favor, não contra.

> Ideia central: "Princípios antes de ferramentas. Semana que vem vocês escrevem o loop na mão — e só depois de ele funcionar é que framework passa a ser uma escolha informada."

---

## Parte 2 — Demonstração guiada

Oito minutos, terminal, sem rede e sem dependência. O script é `codigo/demo-orquestrador-vs-agente.py`: resolve a **mesma** pergunta em duas arquiteturas e imprime três números para cada uma — chamadas ao modelo, tokens enviados no total, e passos até a resposta. O modelo é um simulador roteirado determinístico com semente fixa, e as duas arquiteturas chegam à mesma resposta final, de propósito.

**1.** **[Enuncio a tarefa antes de rodar qualquer coisa]** Antes de rodar, a tarefa. É uma pergunta que precisa de três coisas: consultar o regulamento, fazer uma conta com o que voltou, e redigir a resposta citando o dispositivo. Guardem que as duas arquiteturas vão chegar na mesma resposta — o que muda é o preço.

**2.** **[Rodo `python demo-orquestrador-vs-agente.py --unico`]** Primeira arquitetura: um agente, três ferramentas, o loop da aula passada. Olha a trajetória: três passos, e no fim a resposta com a citação.

**3.** **[Rodo `--multi`]** Segunda arquitetura: um orquestrador e três trabalhadores. Olha a diferença na estrutura da saída — uma chamada de planejamento, uma delegação por trabalhador, a chamada de cada trabalhador, e uma síntese no fim. Mesma resposta. Muito mais linha.

**4.** **[Rodo `--comparar` e fico em silêncio enquanto a turma lê a tabela]** Agora as duas juntas, com os três números lado a lado. Eu vou ficar quieto uns dez segundos aqui. … Alguém me diz em voz alta a razão de tokens entre as duas?

**5.** **[Aponto no código as duas linhas onde o custo extra nasce]** Deixa eu mostrar onde esse custo nasce, porque não é abstrato. Aqui: a linha em que o orquestrador monta o contexto que vai para o trabalhador. E aqui: a síntese final, que é uma chamada de modelo que a arquitetura de um agente não tem. Duas linhas, e a maior parte da diferença está nelas.

**6.** **[Rodo `--multi-vazado`]** E agora o erro do Conceito 2, para vocês verem o tamanho dele. Nessa variante o orquestrador repassa a **trajetória inteira** para cada trabalhador, que é o que acontece quando ninguém pensou no que passar. A razão de tokens piora de novo. E a resposta continua exatamente a mesma.

**7.** **[Volto ao slide]** Uma honestidade sobre o que essa demo **não** mostra: ela não mostra um caso em que multiagente ganha. Esse caso existe — é o deep research que eu vou citar no slide 14 — e ele não cabe em oito minutos sem rede. O que essa demo prova é mais modesto e mais útil: a arquitetura não é gratuita, e o preço dela é mensurável antes de escrever o sistema.

---

## Parte 3 — Hands-on

Cinco minutos, em dupla, com as três propostas projetadas. Elas são infladas de propósito e são parecidas com o que aparece em proposta de projeto de verdade — inclusive nas desta turma.

**1.** **[Projeto as três propostas e formo as duplas]** Cinco minutos, em dupla. Três arquiteturas no slide, todas infladas. Para cada uma eu quero duas coisas: a arquitetura mínima equivalente, escrita em uma linha, e qual das três razões sobrevive na versão reduzida. Se nenhuma sobrevive, escrevam "nenhuma" — isso é uma resposta e é a resposta mais comum.

As três propostas:

1. "Assistente de regulamentos com um agente de busca, um agente de leitura, um agente de redação e um agente revisor."
2. "Sistema de triagem de issues com um agente por linguagem de programação do repositório."
3. "Analista de dados com um agente que escreve SQL, um agente que executa, um agente que interpreta e um agente que faz o gráfico."

*Como recolher:* três minutos de dupla, dois de correção. Corrijo a 1 com voluntário, a 2 em vinte segundos porque é a mais óbvia depois de dita, e uso o resto na 3, porque ela é a que mais aparece nos projetos desta turma. Encerro amarrando no fechamento: "em duas das três, a resposta certa foi trocar um agente por uma ferramenta ou por uma função — e vocês já sabem escrever as duas coisas".

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a conta em aula.
Nesta aula as duas contas do fluxo são curtas o suficiente para eu já fazer as versões mínimas delas
no quadro — `0,95⁵` no slide 11 e `5 × 5 = 25` no slide 10. O que está abaixo é o que fica **além**
disso, nos itens A.1 e A.2 do apêndice.

**Item 1 — "que taxa cada estágio precisa ter, então?" (A.1, Inversão 1, ~4 min).**
A melhor pergunta que o slide 11 pode gerar, porque ela inverte a conta e vira requisito. Eu escrevo
`p ≥ s^(1/N)` no quadro e faço um caso: meta de noventa por cento com cinco estágios exige **97,9%
por estágio**. A sala costuma achar que exigiria 98% e se surpreende de estar certa e de isso ser
inviável. Se sobrar tempo, faço a outra inversão, que é mais brutal: `N ≤ ln s / ln p`, e com estágios
de 95% e meta de 90% **cabem dois estágios**. Dois. Esse número fecha a aula sozinho.

**Item 2 — "e se eu verificar cada estágio?" (A.1, premissa 2, ~4 min).**
É a pergunta certa, e ela merece o número. Com verificador e uma segunda tentativa independente,
`p′ = 1 − (1−p)²`, que com `p = 0,95` dá `0,9975`. Elevando a cinco: **98,8%** contra os 77,4% de
antes. Eu escrevo as duas potências lado a lado no quadro, porque ver `0,774` virar `0,988` sem trocar
de modelo é o argumento mais forte que eu tenho para a exigência de métrica por camada do Lab 8. E
digo as duas condições escondidas: o verificador tem de ser **barato** (o custo esperado sobe) e
**honesto** (verificador que aprova errado piora a taxa).

**Item 3 — "o pior caso é vinte e cinco ou trinta?" (A.2, Derivação 1, ~2 min).**
Alguém confere a conta, e é ótimo quando confere. A resposta: vinte e cinco são as chamadas dos
**trabalhadores**, `b₀·b_w`; somando as do orquestrador, `b₀·(1+b_w)`, dá trinta. Eu digo isso na hora
e uso a deixa para o que interessa: a forma é um **produto**, e nenhum dos dois tetos, lido sozinho,
revela isso. Se a pergunta for sobre profundidade de delegação, a soma geométrica está em A.2 e o
número que convence é que `D = 3` dá 780 chamadas com os mesmos tetos locais.

**Item 4 — "por que paralelismo não reduz custo?" (A.2, Derivação 4, ~2 min).**
Costuma vir no slide 3 e a resposta é uma linha de cada lado. Latência de ramos paralelos é o
**máximo** dos ramos; custo em tokens é a **soma**, igual ao caso serial, porque as mesmas chamadas
acontecem. Escrevo `L = max ℓ_i` e `custo = Σ custo_i` lado a lado e paro. É a distinção que impede um
projeto de prometer economia onde só existe ganho de espera.

**Item 5 — "onde exatamente nasce o custo do `--multi-vazado`?" (A.2, composição, ~3 min).**
Se a turma quiser a conta do modo vazado da demo em vez do número, ela é o triângulo da Aula 23 pago
uma vez por delegação: se o orquestrador repassa a trajetória inteira, a entrada da rodada `k` é
`p₀ + k·d`, e somando sobre as rodadas dá `d·R(R+1)/2` **também** do lado do trabalhador. Duas linhas
no quadro e a ligação com a aula passada fica explícita: o erro de arquitetura do slide 4 é
quantitativamente o mesmo erro de não controlar trajetória do slide 6 da Aula 23.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 16 da Parte 1 — as três sínteses da aula (multiagente como resposta a limite; custos calculáveis antes do código; framework não decide), a ponte para a Aula 25 (Lab 7: construindo um agente autônomo) com o detalhe de que o Lab 5 volta como ferramenta, e as duas tarefas da semana.

> Ideia central: "Semana que vem o loop é de vocês, escrito na mão, com a base do Lab 5 como ferramenta. Depois disso, escolher framework deixa de ser fé e passa a ser medida."

---

*Roteiro do Instrutor · Aula 24 de 30 · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
