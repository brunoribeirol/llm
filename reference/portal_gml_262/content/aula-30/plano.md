---
aula: 30
titulo: "Apresentações finais — Entrega final do projeto"
modulo: "7 — Fronteiras e Encerramento"
tipo: apresentacao
semana: 15
duracao_min: 120
versao: v2
---

# Aula 30 — Apresentações finais — Entrega final do projeto

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** Esta aula não tinha o que rebalancear: ela é a sessão de apresentações,
> não expõe conteúdo, e não contém uma única fórmula. O transporte para a V2 preservou tudo —
> grade própria, o limite de 7 equipes derivado aritmeticamente, as cinco regras de sessão, a
> ficha de avaliação e as contingências. **Sem apêndice matemático**, e a razão está registrada na
> seção correspondente. O único ajuste de substância é a amarração explícita entre a **defesa oral
> desta sessão e a composição da prova** (§9): perguntar "por que essa camada existe e que número
> prova que ela funciona" é uma questão de justificativa aplicada ao sistema da própria equipe, e
> o aluno merece saber que os dois instrumentos cobram a mesma coisa.

## 1. Objetivo da aula

Encerrar a disciplina com a **entrega final do projeto**: cada equipe apresenta o sistema que construiu, roda a demo ao vivo e mostra os números da própria avaliação, respondendo por cada camada do que entregou. O objetivo do instrutor é duplo — avaliar com a rubrica da ementa preenchida ao vivo, e fechar o arco aberto na Aula 1.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Apresentar** um sistema com LLM em 12 minutos, cobrindo problema, arquitetura, demo ao vivo, números por camada e limitações, sem exceder o tempo.
2. **Demonstrar** o sistema ao vivo em pelo menos um caso difícil do próprio conjunto de teste — não apenas no caminho felizeado.
3. **Sustentar** cada número apresentado com a métrica, o denominador e a procedência do juiz que o produziu.
4. **Defender** oralmente qualquer camada do sistema, explicando por que ela existe e qual número prova que ela funciona.
5. **Reconhecer** as limitações da própria avaliação em termos específicos (cobertura do conjunto, viés da anotação, ausência de variância), não genéricos.
6. **Avaliar** criticamente o trabalho de outra equipe pelos mesmos critérios com que o próprio será avaliado.

*(Idênticos aos da V1.)*

## 3. Teoria aplicada

Esta aula não expõe conteúdo novo. O que segue são as **regras de operação da sessão** — e elas são conteúdo, porque decidem se a avaliação discrimina ou não.

### A grade própria desta aula, e o limite de equipes

A grade padrão da §3 do contrato não se aplica: não há dois blocos conceituais. A grade é derivada aritmeticamente do slot por equipe.

**A conta, explicitada porque ela define o limite duro da sessão.** Um slot de 15 minutos por equipe (12 min de apresentação + 3 min de perguntas e troca de máquina) sobre 120 minutos totais:

```
120 min  −  5 min de abertura  −  5 min de pausa técnica  −  5 min de encerramento
=  105 min disponíveis  ÷  15 min por equipe  =  7 equipes
```

> **Limite registrado: 7 equipes.** Acima disso a sessão não fecha sem cortar o slot, e cortar o slot abaixo de 13 minutos elimina as perguntas — que são o instrumento da política de defesa da ementa. As alternativas para 8 ou mais equipes estão na §6 e são as que a própria ementa autoriza.

Configuração alternativa, quando há **6 equipes ou menos**: mantém-se o slot de 15 min, o intervalo formal volta a 10 min e o encerramento sobe para 10 min — mais confortável para todos e preferível quando o número de equipes permite.

### Regras de sessão, e por que cada uma existe

**Regra 1 — 12 minutos, com sinal de 2 minutos restantes.**
O relógio é do instrutor e é visível. Em 10:00 vem o sinal combinado (dois dedos levantados, sem interromper a fala). Em 12:00 a apresentação encerra onde estiver. A regra existe porque, sem ela, a primeira equipe consome 20 minutos e a última apresenta em 6 — e a nota passa a medir a ordem do sorteio.
*Erro comum das equipes:* gastar 6 dos 12 minutos em contextualização do domínio. A ordem que funciona é problema em 1 min, arquitetura em 2, demo em 4, números em 3, limitações em 2.

**Regra 2 — Demo ao vivo, com um caso difícil.**
A demo não é o caminho felizeado. Cada equipe escolhe, do próprio conjunto de teste, ao menos um caso que discrimina — paráfrase, multi-fonte, fora do escopo ou adversarial. A regra existe porque demo felizeada é indistinguível de demo falsa.
*Se o caso falhar ao vivo:* isso **não** penaliza a equipe. O que se avalia é se ela nomeia a camada da falha e segue. Falha explicada vale mais que sucesso não explicado, e a ficha registra isso no descritor de nível pleno do Item 1.

**Regra 3 — Os números na tela, não na narração.**
A tabela por camada do Lab 8 vai projetada, com o `n` de cada linha visível. Número narrado de cabeça não é verificável durante a apresentação e não pontua no Item 2.
*Erro comum:* apresentar uma nota global ("acurácia de 80%") no lugar da tabela. O padrão das Aulas 27 e 28 é uma linha por camada.

**Regra 4 — Perguntas testam compreensão, não conhecimento geral.**
Duas ou três perguntas por equipe, escolhidas com um critério: elas verificam se a equipe entende o que construiu. Não são perguntas de prova, não são pegadinhas de fronteira, e não perguntam sobre o que a equipe não fez. A fonte preferencial da pergunta é a **camada órfã** que a própria equipe nomeou no exercício de inventário da Aula 29.
*Base normativa:* a política de uso de IA da ementa — o aluno é responsável por entender e defender todo o código entregue, e qualquer entrega pode virar defesa oral.
*Nota V2:* a forma canônica da pergunta — *"por que essa camada existe, e que número prova que ela funciona?"* — é a mesma das questões de **justificativa de escolha** da prova, que valem 40 dos 100 pontos. Não é coincidência de redação: é o mesmo instrumento aplicado a um objeto diferente. Vale dizer isso à turma na abertura, porque converte a defesa de uma ameaça vaga em algo que eles já treinaram.

**Regra 5 — A ficha é preenchida ao vivo.**
`codigo/ficha-avaliacao.md`, uma por equipe, com o nível marcado enquanto a equipe apresenta. Ficha preenchida de memória no fim da sessão converge para "todos medianos" — que é exatamente o defeito que o Lab 8 ensinou a evitar. Cada item tem três descritores de nível com faixa de pontos e comportamento observável, e a evidência é anotada em uma linha durante a demo.

### Grade temporal

| Início | Dur. | Bloco | Conteúdo |
|---|---|---|---|
| 00:00 | 5 min | Abertura da sessão | Regras em quatro linhas (12 min + sinal de 2, demo com caso difícil, números na tela, perguntas de compreensão); ordem sorteada projetada; critérios projetados com os quatro pesos; confirmação de que a entrega no repositório é o que vale, e a apresentação é a defesa dela |
| 00:05 | 60 min | Bloco A — Equipes 1 a 4 | Quatro slots de 15 min: 12 min de apresentação + 2 a 3 min de perguntas e troca de máquina. Ficha preenchida ao vivo por equipe |
| 01:05 | 5 min | Pausa técnica | Troca de máquinas, respiro, e a única janela para logística individual |
| 01:10 | 45 min | Bloco B — Equipes 5 a 7 | Três slots de 15 min, mesma regra. O instrutor mantém o ritmo: o Bloco B é onde o atraso acumulado aparece |
| 01:55 | 5 min | Encerramento da disciplina | Devolução coletiva em três observações transversais; anúncio de prazo e forma da devolução individual; e a última fala do curso, que fecha o arco aberto na Aula 1 |

**Total: 120 min.** Ajuste com 6 equipes: abertura 6 min, Bloco A 45 min (3 equipes), intervalo 10 min, Bloco B 45 min (3 equipes), encerramento 14 min.

## 4. Demonstração guiada

Não há demonstração do instrutor nesta aula — quem demonstra são as equipes. O que o instrutor conduz, no lugar, é o **protocolo de sessão**, detalhado passo a passo na Parte 2 do `roteiro.md`:

1. Relógio visível iniciado no primeiro slide de cada equipe, e o sinal de 2 minutos restantes em 10:00.
2. Perguntas escolhidas do banco reutilizável (cinco exemplos na Parte 2 do roteiro), com preferência pela camada órfã anotada na Aula 29.
3. Ficha preenchida durante a apresentação, com a linha de evidência escrita na hora.
4. Devolução de duas linhas por equipe, ainda no slot: uma coisa que funcionou, uma coisa a consertar.

**Número que a sessão produz.** Não há demo do instrutor, mas há um número que ele produz e que importa: **as sete fichas preenchidas ao vivo, com evidência anotada por item.** É o único artefato de avaliação do curso que não pode ser reconstruído depois — e é por isso que a Regra 5 existe. Ficha de memória converge para "todos medianos", e aí a nota deixa de discriminar exatamente na entrega de maior peso do semestre.

O único artefato técnico que o instrutor prepara é a máquina de contingência: um notebook com Python, Colab aberto e conexão testada, para a equipe cuja máquina falhar. Preparado na véspera, não na hora.

## 5. Hands-on

O hands-on desta aula **é a aula**: são as apresentações. Cada equipe executa, no próprio slot:

**Checkpoint 1 · Apresentação em 12 minutos.**
Estrutura recomendada: problema e usuário (1 min), arquitetura com as técnicas do curso identificadas (2 min), demo ao vivo (4 min), números por camada (3 min), limitações e o que consertariam a seguir (2 min).
*Critério de conclusão observável:* a equipe cobre demo **e** números antes dos 12 minutos. Quem não chega aos números perde o item de maior peso da apresentação, e é o erro mais comum.

**Checkpoint 2 · Demo ao vivo com caso difícil.**
Ao menos um caso do próprio conjunto de teste que discrimine.
*Critério de conclusão observável:* o caso executa na frente da turma e a equipe declara de qual categoria ele é. Se falhar, a equipe nomeia a camada.

**Checkpoint 3 · Números na tela.**
A tabela por camada projetada, com `n`, o juiz declarado e o kappa.
*Critério de conclusão observável:* existe na tela pelo menos uma linha por camada declarada do sistema, e o `n` é legível da última fileira.

**Checkpoint 4 · Defesa.**
Duas ou três perguntas respondidas.
*Critério de conclusão observável:* a equipe responde por que a camada questionada existe e qual número prova que ela funciona. Transferir a resposta para um integrante ausente conta como resposta parcial.

**Atividade da plateia — avaliação por pares (sem nota).**
Cada aluno que não está apresentando registra, para duas equipes sorteadas, uma linha: o número mais convincente que a equipe mostrou, e a pergunta que ele faria. As fichas de pares são recolhidas no fim e devolvidas às equipes junto do feedback do instrutor. Isso mantém a plateia ativa nos 105 minutos e faz a turma exercitar a rubrica do lado de quem avalia — que é a forma mais rápida de entendê-la.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Mais de 7 equipes na oferta** | Contagem fechada acima de 7 na Aula 26 | As duas contingências que a ementa autoriza: (a) **vídeo assíncrono de 5 min** por equipe, entregue antes da aula e avaliado fora da sessão, com **demo ao vivo apenas das melhores propostas**; (b) **estender as apresentações para a Aula 29**, movendo o conteúdo de fronteiras para leitura dirigida com as duas perguntas do desafio pós-aula. A escolha é anunciada na Aula 26, nunca na Aula 30 |
| **Equipe estoura o tempo** | 10:00 no relógio e a demo ainda não começou | Sinal de 2 min em 10:00, corte firme em 12:00 — a equipe encerra onde estiver. O corte é anunciado na abertura para não parecer arbitrário. O Item 4 registra o estouro; os Itens 1 e 2 avaliam o que foi mostrado |
| **Máquina da equipe falha** ou a rede cai na demo | Demo não sobe nos primeiros 2 min do bloco de demo | Máquina de contingência do instrutor com Colab aberto, preparada na véspera. Se nem isso resolver, a equipe apresenta a saída salva **declarando que é gravada** e o Item 1 é avaliado pelo resto — a ficha distingue "demo ao vivo" de "saída salva com contingência combinada" |
| **Free tier / rate limit** estoura com a sala conectada | 429 na demo da terceira equipe em diante | Orientação dada na Aula 29: chegar com o modo offline funcionando. Sistemas com rota local (Ollama, modelo pequeno, resposta extrativa) demonstram sem rede. A ficha não penaliza rota offline declarada |
| **Atraso acumulado** no Bloco B | 01:20 e a equipe 5 ainda apresentando | A pausa técnica de 5 min é a folga do sistema e pode ser reduzida a 2. Se o atraso passar de 8 min, comprimir as perguntas para uma por equipe e proteger o encerramento — a última fala do curso não é cortada |
| **Equipe chega sem números** | Slides sem tabela por camada | A apresentação segue e o Item 2 é pontuado como parcial ou insuficiente conforme os descritores. Não há reapresentação. O relatório do Lab 8 entregue com stub comprova o instrumento, não o resultado — e isso está na ficha |
| **Integrante ausente** justamente da camada questionada | "Quem fez essa parte não veio" | Registrado como resposta parcial e acionada a **defesa oral individual** fora da sessão, conforme a política da ementa. Não penaliza a equipe inteira pelo ausente; penaliza a resposta não dada |
| **Plateia dispersa** depois da terceira equipe | Celulares, conversa paralela, sala esvaziando | A ficha de pares é o mecanismo: cada aluno tem duas equipes sorteadas. Anunciar na abertura que as fichas são recolhidas e devolvidas |
| **Sessão vira comparação entre equipes** em voz alta | Comentário de plateia depreciando outra equipe | Regra anunciada na abertura: comentário de plateia é sobre o trabalho, na ficha, e a devolução em voz alta é do instrutor. Cortar na primeira ocorrência |
| **Encerramento atropelado** | 01:58 e a última equipe respondendo pergunta | Os 5 min finais são reservados e não negociáveis. Se necessário, encerrar as perguntas da última equipe e passar direto — é a única parte da sessão que não tem substituto |

## 7. Artefatos produzidos

**Pelas equipes (entrega final avaliada):**
- Repositório com README reproduzível, o sistema, o **harness de avaliação executável** do Lab 8 e o `relatorio-avaliacao.md` gerado pelo código.
- Relatório técnico de 4 a 6 páginas: problema, arquitetura, experimentos, resultados, limitações.
- Deck da apresentação, com a tabela por camada projetada.
- Declaração de uso de IA.

**Pelo instrutor:**
- Uma `ficha-avaliacao.md` preenchida por equipe, com nível marcado por item, evidência anotada ao vivo, perguntas registradas e as duas linhas de devolução.
- Registro das notas dos quatro itens, somando 100, para lançamento.

**Pela turma:**
- Fichas de avaliação por pares (duas por aluno), recolhidas e devolvidas às equipes.

## 8. Desafio pós-aula

Não avaliado. É o fecho da disciplina, e existe porque a maior perda depois de um projeto de curso é o projeto morrer no dia da apresentação.

1. **Consertar o primeiro item da fila.** A tabela de priorização do Lab 8 já diz qual é. Consertar, rodar o harness de novo e comparar as duas tabelas. É o exercício que mais se parece com trabalho real: a medição existia antes do conserto, então o ganho é demonstrável.
2. **Deixar o repositório público e legível.** README que um estranho executa, uma imagem da tabela por camada no topo, e a declaração honesta do que o sistema não faz. Esse repositório é portfólio, e a parte que mais chama atenção de quem contrata é a existência da avaliação — não o sistema.
3. **Escrever cinco linhas para si mesmo:** qual camada do sistema você entenderia melhor se refizesse, e qual das leituras da ordem indicada na Aula 29 você começa na semana que vem.

## 9. Critérios de avaliação

Esta aula é a **entrega final do projeto**, que vale **40%** da média final segundo a ementa, distribuídos em proposta 5% (Aula 22), checkpoint 5% (Aula 26) e **sistema/relatório 20% + apresentação 10%** — os 30 pontos percentuais decididos aqui. Nenhum peso novo é criado.

A rubrica da ementa é operacionalizada em `codigo/ficha-avaliacao.md`, com faixa de pontos e descritores de nível observável por item:

| Item | Peso | O que é nível pleno | O que é nível insuficiente |
|---|---|---|---|
| **Funcionamento e adequação técnica** | 40% | Demo ao vivo, com caso difícil, técnicas do curso integradas, arquitetura justificada com a alternativa descartada, e falha ao vivo com a camada nomeada | Demo não roda ao vivo sem contingência combinada, ou só uma técnica do curso, ou o sistema demonstrado não é o do relatório |
| **Rigor da avaliação quantitativa** | 30% | 20+ casos que discriminam, uma linha por camada com `n`, juiz declarado e calibrado com **kappa**, desacordos inspecionados, falhas atribuídas à menor camada, priorização com custo | "O sistema respondeu bem em N de M" e nada mais — **inclusive quando o sistema funciona perfeitamente na demo** |
| **Relatório técnico** | 20% | Cinco seções, decisões com alternativa e critério, resultados ligados ao harness, limitações específicas, README que reproduz | Fora do formato, número no texto que não existe em nenhuma medição, sem limitações, **sem declaração de uso de IA** (item zerado e defesa obrigatória) |
| **Apresentação e demo** | 10% | Fecha em 12 min, números na tela, mais de um integrante fala, responde sobre **qualquer** camada | Demo ou números ficam de fora do tempo; nenhum integrante explica uma camada central |

A soma dá a nota do projeto de 0 a 100, proporcional aos 30 pontos percentuais decididos nesta sessão.

**O que a ficha registra e vale nota, dito por escrito:**

- **Número por camada é o padrão de aceitação.** É a cobrança direta da dívida anunciada na Aula 1 e paga nas Aulas 27 e 28. Um sistema impecável na demo com avaliação por impressão perde 30% da nota do projeto.
- **Falha ao vivo com a camada nomeada não penaliza.** É desempenho de nível pleno no Item 1. Sucesso no caminho felizeado sem explicação é nível parcial.
- **Defesa é individual dentro da equipe.** Resposta transferida para integrante ausente é resposta parcial e aciona defesa oral fora da sessão, conforme a política da ementa.
- **Declaração de uso de IA** ausente zera o item de relatório e torna a defesa oral obrigatória.

### A defesa oral e a composição da prova são o mesmo instrumento

Vale registrar por escrito, porque muda como o aluno se prepara. A prova da Aula 17 pesa **42 pontos em diagnóstico e interpretação de comportamento** e **40 em justificativa de escolha técnica**. A pergunta canônica desta sessão — *"por que essa camada existe, e que número prova que ela funciona?"* — é exatamente uma questão de justificativa, aplicada ao sistema que a própria equipe construiu em vez de a um cenário hipotético.

A consequência prática é dupla. Para o aluno: quem treinou para a prova treinou para a defesa, e vice-versa — não são duas preparações. Para o instrutor: a distribuição da prova e os descritores desta ficha precisam continuar coerentes entre ofertas; se uma mudar, a outra muda junto, senão o curso passa a cobrar duas coisas diferentes com o mesmo discurso.

Devolução: coletiva nos 5 min finais, em três observações transversais; individual por equipe, com a ficha e as fichas de pares, em prazo `[definir na oferta]`.

Observável em sala: cada equipe consegue apontar, na própria tabela projetada, a camada que consertaria primeiro e o número que justifica a escolha. Quem chegar até aqui e responder "vamos melhorar as respostas" apresentou um sistema, não um projeto de engenharia — e a ficha registra a diferença.

## Apêndice matemático

**Sem apêndice.** Esta é a sessão de apresentações: ela não expõe conteúdo e não contém uma única fórmula. A única conta do material é a derivação aritmética da grade — 105 minutos divididos por slots de 15 dão 7 equipes — e o lugar dela é a §3, onde ela decide a operação da sessão.

O formalismo que a sessão **cobra** é o dos apêndices anteriores, sobretudo o da Aula 27 (kappa de Cohen, os três vieses do juiz) e o do Lab 8 na Aula 28 (intervalo de Wilson, McNemar, o `n` necessário) — é o que sustenta o Item 2 da ficha, que vale 30% da nota do projeto. Uma equipe que projeta uma tabela sem `n` declarado ou um juiz sem kappa está falhando num item cujo fundamento está escrito naqueles dois apêndices.

Criar apêndice próprio aqui produziria um item artificial, e o contrato é explícito: item de apêndice inventado ensina o aluno a ignorar a Parte 2.
