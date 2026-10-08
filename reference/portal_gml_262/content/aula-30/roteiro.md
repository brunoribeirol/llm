---
aula: 30
titulo: "Apresentações finais — Entrega final do projeto"
tipo: apresentacao
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 30 de 30

> **Rebalanceamento V2.** Nada a rebalancear: esta sessão não expõe conteúdo. O roteiro foi transportado integralmente — as cinco regras, o protocolo de condução, o banco de perguntas e a ficha ao vivo. **Sem apêndice matemático**, com a razão declarada na Parte 2 da especificação de slides. O único ajuste é no slide 4: a turma passa a ouvir que a pergunta da defesa é do mesmo tipo das questões de justificativa da prova.

## Como usar este roteiro

Este roteiro é diferente dos vinte e nove anteriores. Na maior parte dos cento e vinte minutos **eu não falo** — quem fala são as equipes. O que este documento traz é a fala dos momentos em que eu falo (abertura, transições, encerramento) e, mais importante, o **protocolo de condução**: como manter o relógio, que perguntas fazer, como preencher a ficha ao vivo.

As linhas com `🗣️` são as frases-âncora. As notas `Bastidor:` não são faladas.

A **Parte 2** aqui não é uma demonstração do instrutor — é o protocolo de sessão. A **Parte 3** é o que as equipes executam. A **Parte 4** existe, mas é curta e tem função diferente: nesta aula, o que a turma pode puxar não é derivação, e sim pergunta sobre a própria nota.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · Abertura: hoje quem fala são vocês · 00:00–00:05

**[Projeto as quatro regras e não avanço enquanto não terminar de ler]**

Bom dia. Última aula, e hoje eu falo cinco minutos no começo e cinco no fim. O resto é de vocês.

Quatro regras, e cada uma tem uma razão que eu vou dizer junto.

Doze minutos de apresentação. Em dez, eu levanto dois dedos, sem interromper — é o sinal de que faltam dois. Em doze, encerra onde estiver. A razão: sem corte firme, a primeira equipe consome vinte minutos e a última apresenta em seis, e aí a nota passa a medir a ordem do sorteio em vez de medir o trabalho.

Demo ao vivo, com pelo menos um caso difícil do conjunto de teste de vocês. Paráfrase, multi-fonte, fora do escopo, adversarial — vocês escolhem, mas tem que ser um que discrimine. A razão: demo no caminho felizeado é indistinguível de demo falsa.

Números na tela, não na narração. A tabela do Lab 8 projetada, com o `n` de cada linha visível. Número que vocês falam de cabeça eu não consigo verificar, e ele não pontua.

E perguntas: duas ou três por equipe, sobre o que vocês construíram. Não é prova, não é pegadinha de fronteira, e eu não vou perguntar sobre o que vocês não fizeram.

**[Faço uma pausa antes da próxima frase e falo devagar]**

E agora a coisa mais importante desta abertura. Se o caso difícil **falhar** ao vivo, isso não penaliza vocês.

> 🗣️ "Falha ao vivo com a camada nomeada vale mais que sucesso não explicado. Se quebrar, me digam em que camada quebrou e sigam."

Isso está escrito no descritor de nível pleno da ficha. Eu digo isso agora porque quero que vocês escolham um caso difícil de verdade, e não o mais seguro.

Última coisa: a entrega é o que está no repositório. A apresentação é a defesa dela.

> **Nota:** Bastidor: a regra do corte em 12:00 **tem** de ser dita agora — corte anunciado na hora parece arbitrário e gera conflito na frente da turma. A garantia sobre falha ao vivo, dita devagar, é o que muda a escolha do caso de demo; em turmas onde eu não disse, sete de sete equipes escolheram o caminho seguro.

---

### Slide 2 · A ordem e o relógio · projetado nas trocas

**[Projeto a grade e deixo o marcador na equipe 1]**

Esta é a grade. A ordem foi sorteada e publicada antes da aula. Slot de quinze minutos: doze de apresentação, três de perguntas e troca de máquina.

> 🗣️ "Slot é slot. Quem começa atrasado apresenta em menos tempo — não empurra o próximo."

Equipe um, a máquina é sua.

> **Nota:** Bastidor: este slide fica projetado durante todas as trocas de máquina — é o que evita a pergunta "quando eu apresento?" sete vezes. Mover o marcador é um gesto pequeno que orienta a sala. Ordem e nomes: `[definir na oferta]`.

---

### Slide 3 · Os critérios, projetados · projetado na pausa técnica

**[Projeto durante a pausa, sem falar sobre]**

> **Nota:** Bastidor: este slide não tem fala própria — ele é referência. Fica na tela durante a pausa técnica, e a razão é oportunista: é a última chance de uma equipe do Bloco B perceber que precisa projetar a tabela do Lab 8, e vale que ela perceba. Se alguém perguntar na pausa, responder a pergunta e não fazer discurso.

---

### Slide 4 · O que eu vou perguntar · dito na abertura, projetado antes da primeira pergunta

**[Projeto a pergunta canônica antes de fazer a primeira pergunta do dia]**

Antes de eu perguntar qualquer coisa, aqui está a forma da pergunta. Uma só.

> 🗣️ "Por que essa camada existe no sistema, e que número prova que ela funciona?"

De onde ela vem: da camada órfã que vocês mesmos nomearam no inventário da semana passada — a que não foi construída em nenhum lab.

E uma coisa que vale dizer, porque tira o mistério: **isso é exatamente a forma das questões de justificativa da prova**, as que valiam quarenta dos cem pontos. Não é uma pergunta nova, é a mesma competência aplicada ao sistema de vocês em vez de a um cenário hipotético.

> 🗣️ "Quem treinou para a prova treinou para isto. Não são duas preparações."

> **Nota:** Bastidor: **novo na V2**, e faz diferença real no clima da sala. Dizer a equivalência com a prova converte a defesa de uma ameaça vaga em algo que a turma já exercitou duas vezes. Reduz o pânico, melhora a qualidade da resposta, e é honesto — os dois instrumentos cobram a mesma coisa, e esconder isso não beneficia ninguém.

---

### Slide 5 · [Transição] Pausa técnica e o Bloco B · 01:05–01:10

**[Projeto o cronômetro de 5 minutos]**

Cinco minutos. Troca de máquina, respiro, e é a única janela de hoje para logística individual — se alguém precisa falar comigo sobre alguma coisa, é agora.

Bloco B: equipes cinco, seis e sete. A máquina de contingência está ligada, com Colab aberto, para quem precisar.

> **Nota:** Bastidor: esta pausa é a **folga do sistema**. Com atraso acumulado, ela encolhe para 2 min sem cerimônia. Se o atraso passar de 8 min, comprimir as perguntas para uma por equipe — e proteger o encerramento, que não tem substituto. Conferir aqui se as sete fichas do Bloco A estão preenchidas; se alguma ficou pela metade, completar agora, não no fim.

---

### Slide 6 · Encerramento da disciplina · 01:55–02:00

**[Projeto o mapa do percurso da Aula 29, com as duas colunas acesas]**

Cinco minutos, e eles são meus.

Três observações da sessão de hoje. **[digo as três, tiradas das fichas preenchidas ao vivo]**

A devolução individual vem com a minha ficha e com as fichas de pares que vocês preencheram, no prazo que está no slide.

**[Aponto o mapa]**

E o fechamento. Na primeira aula deste semestre eu disse uma coisa que vocês não tinham como verificar: que os LLMs unificaram as tarefas de NLP sob "prever o próximo token", e que o custo dessa unificação tinha sido transferido para a avaliação. Que a gente tinha ganhado um modelo geral e perdido o instrumento de medida.

Vocês pagaram essa conta. Cada equipe que apresentou hoje tem uma tabela com uma linha por camada, um `n` declarado e um juiz com kappa. Isso é a fatura quitada.

> 🗣️ "Vocês entraram sabendo usar um LLM. Saem sabendo provar que o sistema de vocês funciona — e essa é a parte que quase ninguém sabe fazer."

E o último desafio do curso, o único sem prazo: consertar o primeiro item da fila de vocês, rodar o harness de novo, e comparar as duas tabelas. A medição já existia antes do conserto, então o ganho é demonstrável — e isso é a coisa mais parecida com trabalho real que vocês vão fazer com esse projeto. Depois, deixem o repositório público e legível. É portfólio, e a parte que mais chama atenção de quem contrata é a existência da avaliação, não o sistema.

Obrigado pelo semestre.

> **Nota:** Bastidor: cinco minutos reservados e **não negociáveis**. É a única parte da sessão sem substituto: se atrasar, cortam-se as perguntas da última equipe, não o encerramento. As três observações transversais saem das fichas — é mais um motivo para a Regra 5. Não improvisar as três: escolher enquanto o Bloco B corre e anotar.

---

## Parte 2 — Protocolo de sessão

Não há demonstração do instrutor nesta aula. O que eu conduzo é o protocolo, e ele tem quatro peças que rodam sete vezes.

**1.** **[Inicio o relógio visível no primeiro slide de cada equipe]** O relógio é meu e é visível para a equipe. Em 10:00 eu levanto dois dedos sem interromper a fala. Em 12:00 eu digo "tempo" uma vez, e a equipe encerra onde estiver.

**2.** **[Escolho as perguntas enquanto a equipe apresenta]** Duas ou três, e a fonte preferencial é a camada órfã que a equipe nomeou na Aula 29 — eu tenho a lista anotada. Banco reutilizável, para quando a camada órfã não render:

- "Essa camada aqui — por que ela existe no sistema, e que número prova que ela funciona?"
- "Vocês escolheram [técnica]. Qual era a alternativa, e o que fez vocês descartarem ela?"
- "Esse número tem `n` de quanto? E o que ele **não** permite vocês concluírem?"
- "O juiz de vocês foi calibrado contra o quê? Qual foi o kappa, e vocês olharam os desacordos?"
- "Se vocês tivessem duas semanas a mais, qual item da fila vocês consertariam primeiro, e por que esse?"

**3.** **[Preencho a ficha durante a apresentação, não depois]** `codigo/ficha-avaliacao.md`, uma por equipe. Nível marcado por item, e uma linha de evidência escrita **na hora** — "o caso difícil foi paráfrase multi-fonte, rodou, recall@3 na tela com n=24". Ficha de memória no fim da sessão converge para "todos medianos", e aí a nota deixa de discriminar exatamente na entrega de maior peso do semestre.

**4.** **[Devolvo duas linhas ainda dentro do slot]** Uma coisa que funcionou, uma coisa a consertar. Ditas para a equipe na frente da turma, porque a plateia aprende com a devolução alheia mais do que com a própria.

> **Nota de contingência:** Bastidor: a máquina de contingência — notebook com Python, Colab aberto, conexão testada — é preparada **na véspera**, não na hora. Se a demo de uma equipe não sobe nos primeiros 2 minutos do bloco de demo, oferecer a máquina; se nem isso resolver, a equipe apresenta a saída salva **declarando que é gravada**, e a ficha distingue "demo ao vivo" de "saída salva com contingência combinada". Rate limit com a sala inteira conectada é risco real a partir da terceira equipe: a orientação de chegar com o modo offline funcionando foi dada na Aula 29, e rota local declarada não é penalizada.

---

## Parte 3 — Hands-on

O hands-on desta aula é a aula. Cada equipe executa quatro checkpoints no próprio slot, e o que eu faço é registrar.

**1.** **[Lanço o Checkpoint 1 — Apresentação em 12 minutos]** Estrutura que funciona, e eu digo isso na abertura para quem quiser usar: problema e usuário em 1 min, arquitetura com as técnicas do curso identificadas em 2, demo em 4, números em 3, limitações em 2.

*Bastidor — erros comuns:* gastar 6 dos 12 minutos contextualizando o domínio, e chegar em 12:00 sem ter mostrado os números. É o erro mais comum e o mais caro, porque os números são o item de 30%. O sinal de 10:00 existe para isso.
*Como recolher:* observável — a equipe cobre demo **e** números antes de 12:00.

**2.** **[Lanço o Checkpoint 2 — Demo com caso difícil]** Um caso do próprio conjunto que discrimine, com a equipe declarando de qual categoria ele é.

*Bastidor — erros comuns:* escolher o caso mais seguro e chamar de difícil. Dá para perceber: se o sistema acerta na primeira tentativa sem hesitar e a equipe não explica por que aquele caso é difícil, é caminho felizeado. Perguntar "por que esse caso discrimina?" resolve.
*Como recolher:* o caso executa na frente da turma e a categoria é declarada. Se falhar, a equipe nomeia a camada — e isso é nível pleno.

**3.** **[Lanço o Checkpoint 3 — Números na tela]** A tabela por camada projetada, com `n`, juiz declarado e kappa.

*Bastidor — erros comuns:* projetar uma nota global ("acurácia de 80%") no lugar da tabela. O padrão das Aulas 27 e 28 é uma linha por camada, e a nota global esconde exatamente o que o curso ensinou a decompor.
*Como recolher:* existe na tela pelo menos uma linha por camada declarada, e o `n` é legível da última fileira.

**4.** **[Lanço o Checkpoint 4 — Defesa]** Duas ou três perguntas respondidas.

*Bastidor — erros comuns:* transferir a resposta para um integrante ausente. Registrar como resposta parcial e acionar a defesa oral individual fora da sessão — não penaliza a equipe inteira pelo ausente, penaliza a resposta não dada.
*Como recolher:* a equipe responde por que a camada questionada existe e qual número prova que ela funciona.

**Atividade da plateia — avaliação por pares, sem nota.** Cada aluno que não está apresentando registra, para duas equipes sorteadas, uma linha: o número mais convincente que a equipe mostrou, e a pergunta que ele faria. Recolhidas no fim e devolvidas às equipes junto do meu feedback.

*Bastidor:* isto é o mecanismo contra plateia dispersa, que aparece a partir da terceira equipe. Anunciar na abertura que as fichas são recolhidas **e devolvidas às equipes** — a segunda parte é o que faz o aluno escrever algo útil. E vale dizer o motivo pedagógico: exercitar a rubrica do lado de quem avalia é a forma mais rápida de entendê-la.

---

## Parte 4 — Se perguntarem

Esta aula não tem derivação para puxar. O que a turma puxa aqui é outra coisa, e vale ter resposta pronta.

> **Nota:** Bastidor: as três perguntas abaixo aparecem em quase toda sessão de encerramento. As duas primeiras são sobre nota e merecem resposta curta e firme, na frente da turma. A terceira merece generosidade, porque é a pergunta de quem vai continuar.

**"A nota sai hoje?"** Não. A devolução individual vem com a ficha preenchida e as fichas de pares, no prazo que está no slide 6 — `[definir na oferta]`. O que sai hoje são as três observações transversais do encerramento.

**"Se a demo falhou, perdemos quanto?"** Nada, se a camada foi nomeada. Está no descritor de nível pleno do Item 1, e eu disse isso na abertura justamente para não haver essa dúvida agora. O que perde ponto é sucesso no caminho felizeado sem explicação — que é o oposto do que aconteceu.

**"E agora, o que eu estudo?"** A ordem está no slide 14 da aula passada: Jurafsky e Martin e Raschka para o lado do modelo, Huyen para o lado do sistema, e depois um paper por semana com reimplementação de um componente. E o degrau zero vocês já têm na mão: os apêndices dos trinta decks. Fundamento de atenção e de otimização não tem meia-vida curta — o que envelhece rápido é agente e fronteira, não aquilo. Se der para fazer uma coisa só nas próximas semanas, é reimplementar um componente do Lab 2 sem olhar o notebook.

---

## Encerramento · 01:55–02:00

O encerramento está redigido como fala no Slide 6 da Parte 1 — as três observações transversais tiradas das fichas, o prazo da devolução individual, e o fechamento do arco aberto na Aula 1 com a dívida de avaliação quitada.

> 🗣️ "Vocês entraram sabendo usar um LLM. Saem sabendo provar que o sistema de vocês funciona."

---

*Roteiro do Instrutor · Aula 30 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
