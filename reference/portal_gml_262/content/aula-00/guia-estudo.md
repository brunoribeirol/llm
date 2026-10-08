# Aula 0 — Recepção: o mapa do curso, os materiais e o ambiente

## Slide 1 · Abertura: o que vocês vão ter construído em dezembro · 00:00–00:04

**[Projeto a cena da última aula do semestre antes de dizer bom dia]**

Bom dia. Eu vou começar pelo fim.

Primeiro de dezembro. Cada equipe desta sala vai ter doze minutos para apresentar um sistema que construiu. Com demo ao vivo — não vídeo gravado, não captura de tela: o sistema rodando, na frente de todos, num caso difícil que a própria equipe escolheu do conjunto de teste dela.

**[Aponto a tabela à direita]**

E ao lado da demo, isto: uma tabela com uma linha por camada do sistema, cada linha com o número que mede aquela camada e com o `n` daquela medição. Não uma nota global. Uma linha por camada.

E aí eu vou fazer uma pergunta, para uma camada que eu escolho:

> Ideia central: "Por que essa camada existe no sistema, e que número prova que ela funciona?"

Quem não conseguir responder isso perde ponto. E eu já sei qual camada costuma travar: é aquela em que a equipe copiou código de algum lugar e nunca entendeu.

Esta sessão de hoje é sobre como vocês chegam lá. O conteúdo em si começa na terça.

---

## Slide 2 · Quem está nesta sala · 00:04–00:08

Antes de eu falar do curso, eu preciso saber quem está aqui. Quatro perguntas, mão levantada, e eu vou anotar.

**[Faço as quatro na ordem, anotando a contagem]**

Quem já cursou Aprendizagem de Máquina ou Aprendizagem Profunda? … Quem já chamou um LLM por API, escrevendo código? … Quem já treinou ou ajustou um modelo, de qualquer tamanho? … E quem já colocou alguma coisa em produção, com usuário de verdade do outro lado?

**[Olho os números que anotei]**

Isso muda decisões reais. Se a maioria não fez Aprendizagem de Máquina, os conceitos de perda e de gradiente ganham dois minutos extras quando aparecerem. Se muitos já chamaram API, o Lab 3 sobe o nível. Se ninguém pôs nada em produção, os slides de custo e de latência ganham peso, porque é onde a intuição falta.

> Ideia central: "Este curso não pressupõe Aprendizagem de Máquina. Onde ela for necessária, eu explico em duas frases no ponto em que aparece — não numa aula de revisão."

---

## Slide 3 · O mapa: sete camadas, e onde cada uma é construída · 00:08–00:12

**[Subo a pilha com o dedo, do rodapé ao topo, enquanto falo]**

Sete camadas. Token e representação, Aulas 2 e 3, e vocês constroem no Lab 1. Atenção e o Transformer, Aulas 5 a 8, Lab 2 — e é no Lab 2 que vocês escrevem a atenção causal à mão. Escala e decodificação, Aulas 10 a 12, Lab 3. Adaptação e alinhamento, 13 a 16, Lab 4. Recuperação, 18 e 19, Lab 5. Ferramentas e agentes, 21 a 26, Labs 6 e 7. Avaliação, Aula 27, Lab 8.

Agora a propriedade que eu quero que vocês levem daqui:

> Ideia central: "Isto não é uma lista de tópicos da moda. É uma pilha — cada camada só faz sentido porque a de baixo existe."

E tem uma consequência prática nisso. O Lab 8, o último, mede exatamente as camadas que os Labs 1 a 7 construíram. Não é um laboratório a mais no fim: é onde tudo o que veio antes ganha número.

---

## Slide 4 · O que este curso não faz · 00:12–00:15

Agora a parte que quase nenhuma primeira aula tem, e que eu acho a mais importante para vocês confiarem no resto: o que este curso **não** faz.

Pré-treino de verdade em escala: não. O Lab 2 é um mini-GPT num corpus de brinquedo. Vocês vão fazer a conta de um treino de fronteira na Aula 12, e vão entender o orçamento — mas ninguém aqui vai treinar um modelo grande.

RLHF completo, com modelo de recompensa treinado: não. As Aulas 15 e 16 param na formulação e no DPO.

Serving em produção, com batching contínuo e autoescala: não.

Multimodalidade com as mãos: não. É fronteira na Aula 29.

Segurança adversarial ofensiva, além do que a Aula 26 introduz: não.

> Ideia central: "Confundir 'vimos em aula' com 'sei fazer em produção' é a distância exata desta lista."

**[Aponto o cartão da Eletiva 1]**

E sobre a outra eletiva: quem cursou ou vai cursar Inteligência Artificial, Aprendizagem Profunda e IA Generativa encontra lá CNNs, GANs e visão computacional, que aqui não aparecem. As duas não se sobrepõem. Podem ser cursadas em qualquer ordem.

---

## Slide 5 · Como vocês são avaliados · 00:15–00:19

**[Projeto as duas colunas]**

Média final é a média simples de duas avaliações. Cada uma tem quarenta por cento de prática e sessenta por cento de avaliação individual.

AV1, que cobre as Aulas 1 a 17: quarenta por cento são os Labs 1 a 4 mais participação, e sessenta por cento é a prova individual escrita — sem consulta e sem IA.

AV2, Aulas 18 a 30: quarenta por cento são os Labs 5 a 8 mais as duas entregas parciais do projeto, e sessenta por cento é o projeto final — sistema, relatório e defesa oral.

**[Aponto a linha do tempo do projeto]**

Três datas para anotarem agora. Proposta do projeto: vinte e sete de outubro. Checkpoint: dez de novembro. Entrega final e apresentação: primeiro de dezembro.

> Ideia central: "O projeto vale mais que a prova, e ele começa na semana nove — não na última."

E duas regras institucionais que valem desde hoje. Trabalho entregue fora do prazo tem nota inicial oito. E falta acima de vinte e cinco por cento da carga reprova, independentemente das notas.

---

## Slide 6 · A prova, em números · 00:19–00:24

Este é o slide mais importante do que eu vou dizer hoje.

**[Projeto as quatro barras]**

A prova da Aula 17 tem cem pontos, e eles estão distribuídos assim. Quarenta e dois pontos de diagnóstico e interpretação: eu dou um sintoma, ou uma tabela de resultados, e vocês identificam a causa — ou dizem o que aqueles dados **não** permitem concluir. Quarenta pontos de justificativa de escolha: eu dou um cenário com restrição real de memória, de orçamento ou de latência, e vocês defendem uma decisão técnica com argumento. Oito pontos de conceito aplicado. E dez pontos de derivação.

**[Aponto a soma]**

Oitenta e dois dos cem pontos são de ler comportamento e defender decisão.

E agora a consequência, que muda como vocês estudam:

> Ideia central: "Decorar derivações rende dez pontos. Entender o que cada derivação autoriza a afirmar rende os outros quarenta."

Por quê? Porque uma defesa de escolha de arquitetura que não invoca o fundamento correto **não é uma justificativa suficiente**. Se eu peço para vocês escolherem entre dois paralelismos e vocês respondem "usaria o de dados" sem a conta que mostra que os estados não cabem numa GPU, isso não fecha a questão.

Última coisa: as questões de diagnóstico e de justificativa **aceitam hipóteses diferentes da minha**, desde que fundamentadas. O gabarito declara onde isso vale. Um sintoma real quase sempre tem mais de uma causa plausível, e eu não vou penalizar quem raciocinou certo e chegou a outra hipótese defensável.

**[Fico em silêncio por um minuto inteiro, com o slide na tela]**

---

## Slide 7 · Os materiais, e a divisão que organiza o semestre · 00:24–00:28

**[Abro um deck de verdade — o da Aula 6 — no projetor]**

Cada aula entrega um material com duas partes, e entender essa divisão muda como vocês estudam.

A Parte 1 é o **fluxo da aula**. Ela abre por um problema real e por um comportamento que se observa. Exemplos do que vocês vão ver: um modelo que treina bem e gera texto sem sentido nenhum. Um texto que custa trinta e três por cento mais em português do que em inglês. Um modelo maior que fica pior. Quando o fundamento matemático é necessário para entender aquele comportamento, ele aparece com a fórmula na tela, lida em português, e com a justificativa de por que ela importa — mais um ponteiro para onde ela é derivada.

**[Rolo o deck até a Parte 2 e abro o item A.2]**

E esta é a Parte 2, o **apêndice**. Olhem o que é: uma página de derivação escrita. Notação declarada, premissas explícitas, nenhuma etapa pulada, casos-limite trabalhados. Isto **não** é projetado em aula — é distribuído com o deck, e existe para ser estudado e consultado.

Os trinta decks do curso somam cento e onze itens desses.

> Ideia central: "A matemática não foi tirada deste curso. Ela foi escrita num lugar onde caberia escrevê-la inteira — o que um quadro de sala de aula não permite."

---

## Slide 8 · Os outros materiais · 00:28–00:31

Quatro coisas mais, e o que fazer com cada uma.

A **apostila**, cerca de trezentas páginas. É a versão escrita e mais lenta do curso, com exemplos resolvidos até o fim e exercícios com gabarito comentado — o gabarito explica o raciocínio, não só o resultado. Cada capítulo abre pela aplicação e reúne o desenvolvimento formal numa seção ao final, na mesma lógica dos decks.

Os **notebooks** dos oito laboratórios, com solução de referência liberada depois do prazo de cada checkpoint.

Os **papers**, um por aula, e cada um vem com uma **pergunta dirigida**. A pergunta é o que transforma a leitura num trabalho de quarenta minutos em vez de quatro horas.

E os **formulários quinzenais**: seis no semestre, anônimos, e não valem nota — nem para mais, nem para menos. Servem para ajustar o curso enquanto ele está acontecendo. Na aula seguinte a cada um, eu digo o que vai mudar por causa das respostas. E digo também o que **não** vai mudar, e por quê.

> Ideia central: "Sobre os formulários: 'não abri o apêndice' é uma resposta legítima, e é a que eu mais preciso saber."

---

## Slide 9 · Política de uso de IA · 00:31–00:35

Sem eufemismo, porque vocês vão perguntar de qualquer jeito.

Uso de IA nos labs e no projeto é **permitido e incentivado**. É o objeto desta disciplina; seria estranho proibir.

A condição é uma: cada entrega inclui uma **declaração de uso**. Qual ferramenta, o que vocês pediram, o que vocês entenderam da resposta, a avaliação crítica que fizeram do resultado, e as limitações que vocês viram.

E a responsabilidade é de vocês por **todo** artefato que incorporarem, independentemente da origem. Qualquer entrega pode virar defesa oral, e o domínio que vocês demonstrarem sobre o que entregaram integra a nota.

Vedado: usar IA na prova; fabricar dados ou resultados; treinar com dados institucionais sem aprovação. **A prova é individual e sem IA.**

> Ideia central: "A régua é uma só: você tem de conseguir defender o que entrega. Como você chegou lá é problema seu. Entender o que entregou é obrigação sua."

E tem uma coisa que sai disso: o bloco de uso de IA dos formulários alimenta um **diário de IA** da disciplina — um registro coletivo e anônimo de usos, acertos e falhas ao longo do semestre. Os melhores casos de "a IA errou e eu percebi" voltam como exemplo de aula.

---

## Slide 10 · [Transição] Agora o ambiente · 00:35–00:37

**[Projeto o checklist de quatro itens]**

Metade da sessão acabou. Os próximos trinta minutos são de mão na massa, e ninguém sai desta sala sem quatro coisas funcionando.

Colab com GPU habilitada — sem isso os Labs 2 e 4 não rodam. Conta no Hugging Face com token de leitura — Labs 1, 4 e 5. Uma chave de API de provedor com camada gratuita — Labs 3, 6 e 7. E o repositório da disciplina criado, que é onde tudo é entregue.

E a razão de fazer isso hoje, e não na Aula 4:

> Ideia central: "Download e permissão são o que mais atrasa laboratório. Trinta minutos hoje valem quatro laboratórios."

Quem chega ao Lab 1 sem ambiente perde os primeiros quinze minutos. Quem chega ao Lab 2 sem GPU habilitada perde a aula inteira.

---

## Slide 11 · Como estudar nesta disciplina · 00:37–00:40

Antes de vocês abrirem o Colab, três minutos sobre como usar o material. É a única dica de estudo que eu vou dar no semestre.

Quatro momentos.

**Antes da aula**, vinte minutos: os objetivos e as caixas de conceito da seção da apostila. Vocês entram na aula com o vocabulário pronto e usam o tempo de sala para perguntar — que é justamente o que não dá para fazer sozinho.

**Depois da aula**: a seção inteira, o exemplo resolvido refeito no papel, e os exercícios do capítulo que já estiverem cobertos. O gabarito é para conferir, não para ler antes.

**Antes do laboratório**: o roteiro de prática. Quem chega sabendo o que cada checkpoint pede gasta o tempo de sala programando, não lendo enunciado.

**Antes da prova**: os objetivos de todas as seções, as caixas de erro comum, os exercícios refeitos sem o gabarito ao lado — e as seções de fundamento. Não para reproduzir derivação de memória, e sim para saber qual resultado sustenta cada decisão que a prova pedir para vocês defenderem.

> Ideia central: "Vinte minutos antes da aula rendem mais que duas horas depois. Se eu pudesse dar uma dica só, era essa."

---

## Slide 12 · [Referência] O calendário completo · projetado durante o setup

**[Projeto durante o trabalho prático, sem falar sobre]**

---

## Slide 13 · [Referência] Os oito laboratórios e o que sai de cada um · projetado durante o setup

**[Alterno com o slide 12 durante o trabalho prático]**

---

## Slide 14 · [Referência] Fechamento e o que levar · 00:57–01:00

A fala deste slide está no **Encerramento**, ao final deste roteiro — ele é o checklist conferido item por item em voz alta, mais o recado sobre o documento de uma página e o gancho da Aula 1.

---

## Parte 3 — Setup de ambiente

Trinta minutos, e é a metade mais importante da sessão. Os slides 12 a 14 ficam projetados alternadamente; a turma consulta enquanto trabalha.

**A regra que eu digo antes de começar:** quem terminar um item ajuda o vizinho. Setup é a única parte deste curso em que copiar a solução do colega é exatamente o comportamento certo.

**1.** **[Lanço o item 1 — Colab com GPU, ~8 min]** Abrir o Colab, criar um notebook novo, e o passo que todo mundo esquece: `Ambiente de execução → Alterar o tipo de ambiente de execução → T4 GPU`. Depois, rodar uma célula só, com `!nvidia-smi`, e confirmar que a placa aparece.

**2.** **[Lanço o item 2 — Hugging Face com token, ~7 min]** Criar conta, ir em `Settings → Access Tokens`, gerar um token de **leitura** — não de escrita — e guardar. Depois, testar no Colab com `from huggingface_hub import login`.

**3.** **[Lanço o item 3 — chave de API, ~8 min]** Escolher um provedor com camada gratuita, criar a chave, e fazer **uma** chamada de teste — a mais simples possível, pedindo uma frase.

**4.** **[Lanço o item 4 — repositório, ~5 min]** Criar o repositório da disciplina, com a estrutura mínima: uma pasta por laboratório, um `README.md` e um `.gitignore` que **exclua arquivos de chave**. Entregar o link no canal da turma.

---

## Parte 4 — Se perguntarem

Esta sessão não tem apêndice, então não há derivação para puxar. O que a turma puxa numa recepção é outra coisa — e as perguntas são previsíveis o suficiente para valer resposta preparada. As seis abaixo aparecem em quase toda primeira aula.

**"A prova é difícil?"**
A pergunta real por baixo é "dá para passar decorando?". **Resposta:** ela não é difícil de decorar — ela é impossível de decorar, porque oitenta e dois dos cem pontos partem de um caso que vocês não viram antes. Quem acompanha os labs e entende o que cada número mede vai bem. Quem decora derivação na véspera pega dez pontos.

**"Preciso saber Aprendizagem de Máquina?"**
**Resposta:** não. Onde a disciplina precisa de perda, gradiente ou sobreajuste, eu explico em duas ou três frases no ponto em que aparece. O que eu pressuponho é Python, Álgebra Linear e Probabilidade — e Álgebra Linear é a que mais aparece, porque atenção é multiplicação de matriz.

**"Dá para fazer o projeto sozinho?"**
**Resposta:** o projeto é em equipe de três a quatro, e a razão é o escopo — sistema com avaliação própria não sai em duas semanas de uma pessoa. Se houver um caso específico, falamos depois; mas a resposta padrão é não.

**"Preciso de GPU / preciso pagar alguma coisa?"**
**Resposta:** não, e isso é decisão de projeto do curso, não sorte. Todos os oito labs rodam no Colab gratuito e em provedores com camada gratuita. O Lab 4 treina um adaptador numa T4 grátis, e o número que faz isso caber está no apêndice daquela aula. Se algum dia você **quiser** pagar por um modelo maior, é escolha sua e não muda nota.

**"Quanto tempo por semana isso vai me custar?"**
**Resposta honesta:** quatro horas de aula, mais os vinte minutos antes de cada aula que eu recomendei, mais o lab que sobra da semana — em geral uma a duas horas. Na segunda metade, o projeto entra e sobe. As semanas dos marcos (27/10, 10/11, 01/12) são as pesadas, e elas estão no calendário desde hoje justamente para vocês planejarem.

**"Vale a pena, se eu não quero pesquisar nisso?"**
A melhor pergunta que aparece nesta sessão. **Resposta:** o que este curso treina é provar com número que um sistema funciona — e essa é a parte que quase ninguém sabe fazer, dentro ou fora de IA. O repositório que vocês entregam em dezembro, com a avaliação por camada no topo do README, é portfólio. A parte dele que chama atenção de quem contrata não é o sistema; é a existência da medição.

---

## Encerramento · 00:57–01:00

**[Projeto o checklist do slide 14 e vou item por item, em voz alta, com a turma respondendo]**

Quatro coisas para sair daqui com. Ambiente rodando: Colab com GPU, Hugging Face com token, chave de API testada. Repositório criado e link entregue. O documento de uma página do contrato, salvo. E a apostila baixada, com os objetivos da seção 1 lidos antes de terça — são vinte minutos.

**[Sobre o documento]**

Uma coisa sobre esse terceiro item, e ela é importante. Esta sessão de hoje é extra-classe e não é obrigatória. Quem não veio vai receber o mesmo documento no canal da turma, e é **nele** que o contrato está por escrito — a avaliação, a composição da prova, a política de IA. A Aula 1 não vai repetir isso, porque o tempo dela vai para conteúdo.

> Ideia central: "Esse documento é o único registro escrito do contrato. Salvem, e leiam antes de quinta."

Terça, Aula 1: panorama de LLMs e métricas de processamento de linguagem natural. E eu vou abrir com uma pergunta, para vocês pensarem até lá:

> Ideia central: "Um detector de fraude com noventa e nove por cento de acurácia, que nunca achou uma fraude na vida. Como isso é possível — e o que ele deveria estar medindo?"

Quem não conseguiu subir alguma coisa fica dez minutos comigo agora.

---

*Roteiro do Instrutor · Aula 0 (recepção, extra-classe) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
