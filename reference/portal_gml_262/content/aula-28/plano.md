---
aula: 28
titulo: "Laboratório 8: Harness de avaliação do projeto"
modulo: "6 — Avaliação de LLMs"
tipo: laboratorio
semana: 14
duracao_min: 120
versao: v2
---

# Aula 28 — Laboratório 8: Harness de avaliação do projeto

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2 — aula de laboratório (§6-bis do contrato).** Num lab a matemática **é**
> a prática: a equipe implementa `recall_em_k`, `rr` e `kappa_cohen` com as próprias mãos.
> Inverter "aplicação antes de teoria" aqui seria redundante. Por isso o **roteiro prático não
> foi reordenado** — passo zero com stub, demo e os cinco checkpoints permanecem na ordem que
> funciona em bancada. Três mudanças: (i) cada checkpoint **abre pelo comportamento esperado**,
> a linha que o terminal imprime quando está certo, antes de nomear o que implementar; (ii) o
> deck ganhou um **apêndice matemático** com a fórmula, a leitura e os casos-limite de cada
> métrica que o harness calcula (A.1 a A.5), incluindo a estatística que a Aula 27 deixou em
> aberto; (iii) cada checkpoint cita o item correspondente, em uma linha, sem interromper a
> prática. Carga horária, numeração, checkpoints, entregável, pesos da nota e objetivos de
> aprendizagem permanecem os da V1.

## 1. Objetivo da aula

Transformar a Aula 27 em código que roda: cada equipe constrói o **harness de avaliação do próprio projeto** — conjunto de teste, métricas por camada, juiz com rubrica calibrado contra anotação humana, análise de falhas e priorização — e sai da aula com um relatório em que cada camada do sistema tem um número **com o seu denominador ao lado**. Este harness **não é exercício de aula**: ele integra a entrega final do projeto (Aula 30) e é o que sustenta os 30% de rigor quantitativo da rubrica.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Montar** um conjunto de teste de 20 ou mais casos para o próprio sistema, **justificando** a composição por poder discriminativo — pares de paráfrase, casos fora do escopo, casos adversariais e falhas já observadas — e não por facilidade de escrita.
2. **Implementar** as métricas de cada camada existente no próprio projeto: `recall@k`, `precision@k` e MRR na recuperação; acerto por termos exigidos, validade de citação e taxa de recusa correta na resposta; taxa de sucesso e distribuição de passos na trajetória.
3. **Escrever** uma rubrica de três critérios com níveis descritos por comportamento observável e **implementá-la** como juiz nas duas rotas — heurística determinística offline e LLM-as-judge por API.
4. **Calibrar** o juiz contra uma amostra anotada pela própria equipe, **calcular** o kappa de Cohen, **inspecionar** os desacordos um por um e **decidir** se o conserto é na rubrica, no juiz ou no sistema.
5. **Classificar** cada falha na menor camada que a explica e **priorizar** os consertos por impacto sobre custo declarado.
6. **Gerar** um relatório de avaliação em que toda camada declarada tem métrica, denominador e limitação escritos — e **reconhecer** por que "o sistema respondeu bem" não é resultado.

*(Idênticos aos da V1. Cada um tem, no apêndice do deck, o item que o fundamenta: 1 → A.5,
2 → A.1/A.2/A.3, 4 → A.4, 5 → A.5, 6 → todos.)*

## 3. Teoria aplicada

Este é um lab, e é o lab mais atípico do curso: **cada equipe avalia um sistema diferente**. Por isso o material não é um script fechado, é um **template parametrizável** — seis módulos em que a única peça que muda de projeto para projeto é o adaptador. A teoria está toda na Aula 27; o que segue são os conceitos que o código materializa, o **comportamento observável** que denuncia cada um quando é mal entendido, e **onde está a fórmula** que o sustenta.

**Convenção da V2 neste plano:** cada conceito abre pelo que aparece na tela e fecha com o ponteiro para o item do apêndice. A ordem dos blocos e dos checkpoints é a da V1, intocada.

### Bloco 1 (00:35–01:05) — O instrumento de medida: casos e métricas

**Conceito 1 — O harness fala com o sistema por uma função só.**
*Comportamento observável:* `Adaptador OK — contrato respeitado.` impresso antes de o sistema real entrar.
`adaptador.py` expõe `executar(entrada, k)` devolvendo sempre o mesmo dicionário: `resposta`, `fontes_citadas`, `ranking`, `trajetoria`, `parou_por`, `recusou`. Métricas, juiz, calibração e relatório não sabem nada sobre o projeto da equipe — só sobre esse contrato. Duas regras não negociáveis: **uma chamada por caso** (todas as camadas saem da mesma execução, senão os números medem execuções diferentes) e camada inexistente devolve **lista vazia**, o que remove a camada do denominador em vez de contar zero.
*Analogia do instrutor:* é o driver de dispositivo. O sistema operacional não é reescrito para cada impressora; escreve-se o driver.
*Fundamento da Regra 2:* zero e "não se aplica" produzem **denominadores diferentes**, e denominador errado gera número errado com aparência de número certo. Com 20 casos e 3 fora do escopo, contar os três como zero derruba um recall real de 0,80 para 0,68 — doze pontos percentuais fabricados. → **A.1**
*Erro conceitual comum:* chamar o sistema de novo para calcular outra métrica. Com gerador estocástico, o `recall@k` passa a se referir a uma execução e a nota do juiz a outra — e a tabela deixa de ser sobre um sistema.

**Conceito 2 — O conjunto de teste é o artefato que sobrevive ao sistema.**
Modelo, framework e prompt vão trocar; o conjunto rotulado é o que diz se a troca melhorou. Cada caso carrega `entrada` (escrita como o usuário escreve, com erro de digitação e pergunta dupla), `categoria`, `referencia` (o conteúdo obrigatório, não a resposta ideal redigida), `termos_exigidos`, `fontes_relevantes`, `deve_recusar` e `nota` — a frase que explica por que aquele caso existe.
*Erro conceitual comum:* escrever o caso **depois** de olhar a saída do sistema. O caso passa a ser escrito para passar, e a medição vira autoelogio. A regra do lab é escrever primeiro, rodar depois.

**Conceito 3 — Casos que discriminam, não casos fáceis.**
*Comportamento observável:* `python casos.py` imprime a distribuição por categoria e `Checkpoint 1 OK`.
Este é o ponto que decide a qualidade do lab. Um caso que todas as versões do sistema acertam não carrega informação: ele ocupa denominador e não separa nada. O critério é **poder discriminativo** — o conjunto serve se ele consegue distinguir duas versões do sistema. Quatro construções que discriminam de fato:
(i) **par de paráfrase** — a mesma pergunta escrita com o vocabulário da fonte e com o vocabulário do usuário. Se a primeira passa e a segunda falha, a falha é do retrieval, e o par prova isso sem mais nenhum instrumento;
(ii) **fora do escopo com palavra armadilha** — pergunta plausível que a base não cobre, usando um termo que aparece na base em outro sentido. Mede recusa, que é metade da qualidade de um sistema com citação;
(iii) **multi-fonte** — resposta correta exige combinar dois dispositivos; separa "recuperou" de "sintetizou";
(iv) **regressão** — toda falha já vista virou caso. Bug que não entra no conjunto de teste volta.
O validador do Checkpoint 1 exige o mínimo estrutural: 20 casos, 3 categorias, 3 casos fora do escopo, nenhum `TODO` restante, nenhuma fonte inexistente no corpus.
*Fundamento do número 20:* com `n` casos, a menor diferença que o conjunto consegue exibir é `1/n` — cinco pontos percentuais com 20. Um conjunto de 20 **não distingue 0,71 de 0,78**; essa é a resolução do instrumento, e é a razão de "20 é o mínimo, não a meta". Resolver 5 pontos percentuais com confiança de 95% exigiria da ordem de **323 casos**. → **A.5**
*Erro conceitual comum:* confundir caso difícil com caso ambíguo. Caso difícil tem resposta certa e o sistema erra; caso ambíguo não tem resposta certa e envenena a anotação — dois anotadores da equipe vão discordar, e o kappa vai cair por defeito do caso, não do juiz.

**Conceito 4 — Métrica por camada, com denominador visível.**
*Comportamento observável:* `python metricas.py` imprime `Checkpoint 2 OK`; os testes comparam com casos pequenos calculados à mão, inclusive o de `relevantes` vazio.
`recall@k`, `precision@k` e MRR só são calculados sobre os casos que declaram fonte relevante — os casos fora do escopo **não entram nesse denominador** (com `R = ∅`, o recall é `0/0`, indefinido, não zero), e por isso o relatório imprime `n` ao lado de cada número. Na camada de resposta, três métricas determinísticas antes de qualquer juiz: os termos exigidos aparecem, a citação existe entre as fontes entregues ao gerador, e a recusa aconteceu quando devia. Na trajetória, o sucesso é conjunção de três condições — passos dentro do orçamento, nenhum passo com `ok=False`, e parada por resposta ou recusa, nunca por limite.
*Leitura que organiza as três de retrieval:* elas têm **o mesmo numerador** e denominadores diferentes, e é a divisão que define a pergunta. `recall@k` divide pelo que existia (*o que escapou?*); `precision@k` divide por `k` (*quanto do que trouxe presta?*); o `rr` não divide — ele lê a **posição**, informação que as outras duas descartam.
*Analogia:* é a bissecção de bug da Aula 27 virando função. `recall@k` é barato, determinístico e não precisa de juiz — é onde se começa.
*Fundamento:* denominadores, tetos e casos-limite de `recall@k` e `precision@k` (inclusive por que `precision@3 = 0,31` é **93% do máximo atingível**, e não uma nota baixa) → **A.1**; o `rr`, o decaimento hiperbólico, o que ele vê que o recall não vê e a generalização por nDCG → **A.2**; as três métricas determinísticas de resposta, a conjunção da trajetória e o caso em que cada uma mente → **A.3**.
*Erro conceitual comum:* reportar uma fração sem o `n`. Com 20 casos, cada caso vale cinco pontos percentuais: uma diferença de 0,05 entre duas versões é **um caso**, e sem o `n` ninguém sabe disso.

### Bloco 2 (01:15–01:50) — O juiz, a calibração e o que se conserta primeiro

**Conceito 5 — A rubrica é o instrumento; o juiz é o executor.**
*De onde partir, em vez de partir do zero:* escrever três critérios do nada é a parte mais cara deste checkpoint e a que mais varia entre equipes. O **Agent GPA** (`arXiv 2510.08847`) oferece cinco dimensões já validadas para sistema com agente — **Cumprimento de Objetivo, Qualidade do Plano, Aderência ao Plano, Consistência Lógica e Eficiência de Execução** —, com juízes-modelo concordando entre **80% e mais de 95%** com anotação humana e **86%** de concordância na *localização* do erro. A equipe **não** copia as cinco: escolhe as que se aplicam ao próprio sistema e redige os níveis observáveis de cada uma. Um RAG sem planejamento explícito não tem o que medir em Aderência ao Plano — e perceber isso **é** parte do checkpoint. As cinco e a razão de serem ortogonais à taxonomia por etapa estão no slide 10 da **Aula 26**.

*Comportamento observável:* `python judge.py` imprime `Checkpoint 3 OK` com a nota **e o motivo** de cada caso, e `ADVERTENCIA_JUIZ` sem `TODO`.
Três critérios, três níveis (0, 1, 2), níveis descritos por **comportamento observável**. "Cita o dispositivo correto" discrimina; "boa" não discrimina. Três níveis é o teto do que duas pessoas distinguem de forma reprodutível — escala de 1 a 10 é ilusão de precisão. O limiar de aprovação é decisão declarada no relatório, não default silencioso.
*Fundamento da frase "a rubrica decide o kappa":* a rubrica define **quais rótulos existem e com que frequência cada um é usado**, isto é, a distribuição — e é a distribuição que determina quanto do acordo é explicado por acaso. Rubrica com um nível quase nunca usado produz distribuição desbalanceada, e aí acordo alto convive com kappa baixo **por construção**. → **A.4**
*Erro conceitual comum:* escrever a rubrica pensando no juiz automático. A rubrica precisa ser aplicável **por um humano** primeiro — é ela que vai guiar a anotação do Checkpoint 4. Rubrica que só um LLM consegue aplicar não é calibrável.

**Conceito 6 — Duas rotas de juiz, e a rota padrão é offline.**
`juiz_heuristico` aplica a rubrica por regra: determinístico, sem rede, sem chave, roda na sala inteira ao mesmo tempo sem quota. `juiz_llm` faz a mesma coisa por HTTP, com a chave lida de variável de ambiente ou `getpass`, temperatura 0 e queda para a rota heurística caso por caso quando a chamada falha. O harness fecha nas duas — e o relatório **declara qual juiz produziu os números**, com modelo, família e temperatura quando for LLM.
*Erro conceitual comum:* tratar a rota heurística como "o lab pela metade". Ela é um juiz honesto de baixa sofisticação, e tem uma propriedade que o relatório precisa dizer: como a nota do pairwise deriva da nota absoluta, `J(x,y) = J(y,x)` por construção e a taxa de inversão posicional sai em 0% **identicamente**. Esse zero é **propriedade do instrumento**, não virtude do sistema. Com LLM-as-judge esse número é diferente de zero, como a demo da Aula 27 mostrou.
*Fundamento:* a formalização de `τ` e a demonstração de que um juiz pairwise derivado de nota absoluta tem `τ = 0` estão em **A.2 da Aula 27**.

**Conceito 7 — Calibrar é medir concordância com humano antes de escalar.**
*Comportamento observável:* `python calibracao.py` imprime acordo bruto, kappa e a lista de desacordos — e existe **uma linha escrita por desacordo**.
O procedimento é o da Aula 27, agora sobre o conjunto da própria equipe: anotar à mão uma amostra (o exemplo de referência usa 12 de 20 casos, 60%, incluindo os de fronteira), rodar o juiz nos mesmos casos, montar a matriz de confusão, calcular acordo bruto **e** kappa de Cohen, e inspecionar cada desacordo. Na maioria das vezes o conserto é na redação da rubrica.

```
κ = (p_o − p_e) / (1 − p_e)        p_e = Σ_c P_humano(c) · P_juiz(c)
```

*Leitura:* o numerador é o acordo que **sobrou** depois do acaso, o denominador é o acordo que **estava disponível**. `κ` é a fração do acordo conquistável que foi conquistada. No exemplo de referência: `p_o = 0,83`, `p_e = 0,50`, `κ = 0,67`.
*Padrão de leitura dos desacordos (novo na V2):* **desacordos que se agrupam por mecanismo apontam para a rubrica; desacordos espalhados sem padrão apontam para o juiz.** Dois desacordos com a mesma causa não são dois erros — são um erro de redação, cometido duas vezes.
*O teto:* o **kappa humano-humano** na mesma tarefa é o máximo que qualquer juiz pode atingir. Um juiz com `κ = 0,55` contra teto de `0,60` está em 92% do teto e é excelente; o mesmo `0,55` contra teto de `0,90` é ruim. Mesmo número, conclusões opostas.
*Fundamento:* derivação de `p_e` sobre a matriz de confusão do exemplo (`p_o = 0,83 → κ = 0,67`, passo a passo), o **kappa ponderado** para os três níveis ordenados da rubrica, o teto humano-humano e os casos-limite específicos do lab. → **A.4** (derivação geral em **A.1 da Aula 27**)
*Erro conceitual comum:* anotar só os casos fáceis. A amostra de calibração precisa dos casos de fronteira, porque é neles que o juiz decide o resultado do relatório. O segundo: anotar depois de ver a nota do juiz — não há como detectar isso no número, e por isso a defesa é a ordem. O terceiro, novo na V2: usar kappa **simples** numa rubrica de três níveis ordenados sem declarar que foi o simples.

**Conceito 8 — Classificar a falha na menor camada que a explica.**
A ordem de teste importa e é a mesma da Aula 27, de baixo para cima: primeiro escopo (respondeu o que devia recusar, ou recusou o que a base cobre), depois retrieval (a fonte certa não entrou no top-k), depois geração (a fonte certa entrou e o fato não saiu), depois citação, e por fim trajetória. A primeira condição que dispara é a camada da falha. Uma resposta errada porque o documento não foi recuperado é falha de retrieval — contá-la como falha de geração produz o conserto errado.
*Erro conceitual comum:* classificar pela camada em que a falha se **manifesta** (a resposta final, sempre). A queixa é sobre a resposta; a métrica é sobre a camada abaixo.

**Conceito 9 — Priorizar é impacto sobre custo, com o custo declarado.**
*Comportamento observável:* `relatorio-avaliacao.md` existe com as seis seções e `teste_checkpoint_5` passa.
`prioridade = impacto / custo`, onde impacto é a fração de casos que a camada explica e custo é a estimativa da equipe em três níveis (1 barato, 2 médio, 3 caro). O número não é objetivo — o custo é palpite informado. O valor do exercício é **forçar a equipe a escrever o palpite**, porque a alternativa real é consertar o que é divertido em vez do que dói.
*Ressalva nova na V2, que vai para a seção de limitações:* o impacto de cada camada é uma **proporção medida em 20 casos**. Uma camada com 4 casos e outra com 3 estão empatadas dentro da resolução do conjunto, e a tabela as ordena como se houvesse hierarquia. A ordem só é confiável quando as diferenças são maiores que `1/n`. → **A.5**
*Erro conceitual comum:* priorizar pela camada mais interessante tecnicamente. No exemplo de referência a camada com maior prioridade é o **escopo** — um limiar de recusa mal ajustado, o conserto mais barato do relatório inteiro, e o de maior impacto.

**Conceito 10 — "O sistema respondeu bem" não é resultado — e número sem `n` também não.**
Vale dizer isto por escrito, porque é o desvio mais frequente. Um relatório com "o sistema acertou 8 de 10 perguntas" e nenhum número por camada **não cumpre o entregável** deste lab nem o item de rigor quantitativo do projeto final — independentemente de o sistema funcionar. O produto desta aula é a tabela com uma linha por camada, o kappa do juiz e a lista de falhas priorizada.
*O desvio simétrico, promovido na V2:* "o reranker melhorou o sistema em sete pontos" sem dizer que `n = 20` também não é resultado. Com 20 casos, sete pontos é um caso e meio.
*Fundamento:* o erro-padrão de uma proporção com `n = 20` e `p̂ = 0,71` é **0,10** — a diferença declarada é menor que um erro-padrão da própria medição; o intervalo de Wilson é `[0,49 ; 0,86]`. E quando os dois sistemas rodam **nos mesmos casos**, o teste correto é o de **McNemar**, que descarta os casos em que os dois concordam e pergunta se o saldo entre os discordantes é distinguível de uma moeda: com dois casos de saldo, `p = 0,50`. → **A.5**

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 15 min | Setup do ambiente + contexto | Recap da Aula 27 (a menor camada que explica a falha; rubrica com níveis observáveis; kappa; os três vieses do juiz); abrir `codigo/lab-08-harness-avaliacao/`; rodar `python rodar.py --testes` com o stub para ver o harness de pé antes do sistema entrar — **com a conta dos dois denominadores possíveis do stub (3/20 contra 3/3)**; o mapa dos cinco checkpoints **apresentado pelo que cada um imprime na tela**, com a coluna do item de apêndice; o entregável — e o aviso de que ele integra a entrega final da Aula 30 |
| 00:15 | 20 min | Demonstração guiada (live coding) | O sistema de referência (mini-RAG do Lab 5, com defeitos plantados) rodando o harness inteiro: `python harness-solucao.py` etapa por etapa; a tabela por camada com `n` visível **e a leitura de por que 17 e não 20**; `precision@3 = 0,31` lido **contra o teto de 1/3**; a matriz de confusão e o kappa de 0,67, com `p_e = 0,50` contrastado ao `p_e = 0,82` da Aula 27; os dois desacordos lidos em voz alta e agrupados por mecanismo; a tabela de prioridade com escopo em primeiro lugar **e a ressalva da resolução**; abrir `relatorio-avaliacao.md` gerado e mostrar que o relatório é saída do código, não redação posterior |
| 00:35 | 30 min | Checkpoints 1–2 (aluno executando) | CP1: os 20+ casos do próprio projeto em `casos.py`, com pares de paráfrase, três fora do escopo e os casos de regressão; `validar_conjunto` passando (abre pela distribuição impressa + `Checkpoint 1 OK` → A.5). CP2: implementar `recall_em_k`, `precisao_em_k`, `rr`, `acerto_por_termos`, `recusa_correta` e `trajetoria_bem_formada` em `metricas.py` até `teste_checkpoint_2` passar (abre pelo `OK` → A.1, A.2, A.3) |
| 01:05 | 10 min | Intervalo | — |
| 01:15 | 35 min | Checkpoints 3–5 + extensões | CP3: rubrica de três critérios em `judge.py` e os dois critérios de `juiz_heuristico` (abre pelo `OK` com nota e motivo → A.4); CP4: a anotação humana da própria equipe em `calibracao.py`, `kappa_cohen` implementado, desacordos inspecionados (abre por `p_o`, `κ` e a lista de desacordos → A.4); CP5: `classificar_falha`, custos declarados, `python rodar.py` gerando o relatório (abre pelo arquivo gerado + `teste_checkpoint_5` → A.5). Extensões: `--juiz llm` com chave por `getpass`, `taxa_inversao` do pairwise, **kappa humano-humano como teto** |
| 01:50 | 10 min | Recolhimento | O que entregar (harness executável, relatório gerado, anotação humana, análise de falhas priorizada, respostas às questões-guia, declaração de uso de IA), prazo de uma semana, critério; a frase de que número por camada é o entregável **e número sem denominador não é número**; **índice do apêndice projetado por 20 s**, com A.5 indicado como leitura para a seção de limitações; ponte para a Aula 29 (Recapitulação e fronteiras da área) |

*Comparação com a V1: a grade é a mesma, minuto a minuto. O que mudou é a forma de lançar cada
checkpoint (linha do terminal primeiro) e ~2 min distribuídos em leituras que a V1 não fazia — o
teto da precisão, o contraste entre `p_e = 0,50` e `p_e = 0,82`, e a ressalva de resolução da
tabela de prioridade. Esses minutos saíram de explicações que a V1 improvisava e que agora estão
escritas com rigor no apêndice.*

## 4. Demonstração guiada

**Live coding — 20 min, `codigo/solucao/harness-solucao.py`, offline, sem dependência externa.**

A demonstração roda o harness completo sobre um **sistema de referência**: um recorte reduzido do pipeline RAG do Lab 5 (Aula 20) sobre o regulamento acadêmico fictício, com gerador extrativo determinístico e **defeitos plantados de propósito** — limiar de recusa mal ajustado e retrieval léxico que erra em paráfrase. Os números não saem em 100%, e é por isso que o exemplo ensina algo.

**O que a V2 acrescenta:** três dos quatro números que a demo imprime só se lê corretamente sabendo de onde vêm, e a V1 deixava essa leitura implícita. Agora ela é dita na hora, em vinte segundos cada, com o ponteiro para o item do apêndice.

Passos em alto nível:

1. Abrir o arquivo e mostrar a arquitetura no cabeçalho: o mapa dos cinco checkpoints e a linha que importa — o adaptador é a única peça que muda de projeto para projeto. Deixar claro que este arquivo não é o entregável de ninguém; o que se copia dele é a estrutura.
2. Rodar `python harness-solucao.py --etapa 1`: o conjunto de 20 casos e o validador passando. Ler três casos em voz alta — um par de paráfrase e um fora do escopo com palavra armadilha — e nomear por que cada um está ali.
3. Rodar `--etapa 2`: a tabela por camada. Parar em duas linhas. `recall@1 = 0,74` com `n = 17` — dezessete e não vinte porque os três fora do escopo não declaram fonte relevante, e o recall deles seria `0/0`, indefinido. E `precision@3 = 0,31`, lido **contra o teto**: com uma fonte relevante e três posições, o máximo possível é `1/3 = 0,333`, e 0,31 é 93% do máximo atingível. Precisão baixa aqui não é defeito, é aritmética. (→ A.1)
4. Rodar `--etapa 3`: a rubrica, o veredito por caso e os sete reprovados. Mostrar a taxa de inversão em 0% e explicar imediatamente que esse zero é propriedade do juiz determinístico — que deriva o pairwise de uma nota absoluta e por isso não pode se contradizer —, não qualidade do sistema. (→ A.2 da Aula 27)
5. Rodar `--etapa 4`: a matriz de confusão, o acordo bruto de 0,83 e o kappa de 0,67. Contrastar em voz alta: aqui `p_e = 0,50`, enquanto no exemplo desbalanceado da Aula 27 era `0,82` — a diferença é a **distribuição dos rótulos**, e é ela que a rubrica controla. Ler os dois desacordos (`c08` e `c20`) com a resposta na tela e conduzir a decisão em voz alta: os dois têm a **mesma causa** (a resposta cita o dispositivo certo e não responde a pergunta feita), logo não são dois erros, são um erro de redação cometido duas vezes — e o conserto é na rubrica. (→ A.4)
6. Rodar `--etapa 5`: falhas por camada, falhas por categoria e a tabela de prioridade. O ponto pedagógico está na tabela por categoria — `fato_simples` em 0% de falha e `parafrase` em 100%. Uma nota global de 65% de aprovação esconde exatamente isso. E a ressalva: quatro casos contra três casos é diferença de um caso em vinte; a tabela é ponto de partida, não veredito. (→ A.5)
7. Abrir `relatorio-avaliacao.md` no editor e rolar as seis seções. O relatório é **saída do código**: ninguém o redige à mão, e é isso que o torna reexecutável quando o sistema mudar.
8. Fechar mostrando `lab-08-harness-avaliacao/adaptador.py` lado a lado: as três funções que a equipe implementa, e o stub que já faz o harness rodar hoje.

**Números que a demo produz e que a aula usa como evidência (§7 do contrato):** `recall@1 = 0,74 (n=17)`; `precision@3 = 0,31` contra o teto de `0,333`; taxa de inversão `0%` com a ressalva de instrumento; `p_o = 0,83` e `κ = 0,67` com `p_e = 0,50`; e a tabela por categoria com 0% e 100% nas linhas extremas contra 65% global. Todos reaparecem como critério de leitura dos números da própria equipe.

Insumos preparados na véspera: a saída completa do `harness-solucao.py` salva em arquivo de texto (é determinística, então serve de plano B integral) e o `relatorio-avaliacao.md` gerado, aberto numa aba.

## 5. Hands-on

**O componente prático da unidade é o próprio laboratório** (§6-bis e §7 do contrato) — e, neste caso, ele é também entregável de projeto. O trabalho da V2 foi tornar cada critério de conclusão uma **linha de terminal**, de modo que "terminei" seja uma observação e não uma sensação.

Cinco checkpoints, cada um com o critério de conclusão **enunciado primeiro**. O trabalho é **em equipe de projeto**, não individual: o harness é da equipe.

**Checkpoint 0 · adaptador (dentro do setup, 00:10–00:15).**
*Ao final, a tela imprime `Adaptador OK — contrato respeitado.`*, seguido do aviso do stub e da lista de pendências do CP1.
*O que fazer:* rodar `python rodar.py --testes` com o `executar_stub`. O harness roda de ponta a ponta com um sistema que recusa tudo, e o relatório sai quase todo em zero. Quem já tem o sistema do projeto rodando troca `executar = executar_stub` por `executar = executar_meu_sistema` aqui.
*Leitura obrigatória do resultado:* o stub recusa tudo, logo acerta 100% dos casos `fora_do_escopo`. Com denominador "todos os casos" ele tira `3/20 = 0,15`; com denominador "só os fora do escopo", `3/3 = 1,00`. **Um sistema inútil com uma métrica perfeita** — a lição não é que a métrica é ruim, é que uma métrica isolada com denominador escolhido a dedo sempre pode parecer boa. → **Apêndice A.3** (slide 14)

**Checkpoint 1 · o conjunto de teste (00:35–00:50).**
*Ao final, `python casos.py` imprime a distribuição por categoria e `Checkpoint 1 OK`*, com `corpus_ids` passado para que fonte inexistente seja pega.
*O que fazer:* escrever os 20+ casos do próprio projeto em `casos.py`, apagando os três exemplos do template. Composição exigida: pelo menos 3 categorias, pelo menos 3 casos `fora_do_escopo`, pelo menos um par de paráfrase (mesma referência, vocabulários diferentes) e todos os casos de regressão que a equipe já viu falhar. Cada caso tem a `nota` explicando por que existe.
*Fundamento:* com `n` casos a resolução do conjunto é `1/n` — 5 pontos percentuais com 20 casos. É por isso que 20 é o mínimo e não a meta, e é por isso que este conjunto **não** serve para declarar melhorias de sete pontos. → **Apêndice A.5** (slide 16)

**Checkpoint 2 · métricas por camada (00:50–01:05).**
*Ao final, `python metricas.py` imprime `Checkpoint 2 OK`* — os testes comparam com casos pequenos calculados à mão, inclusive o caso de `relevantes` vazio, que é o que separa "sem fonte relevante" de "recall zero".
*O que implementar:* `recall_em_k`, `precisao_em_k`, `rr` (retrieval), `acerto_por_termos`, `recusa_correta` (resposta) e `trajetoria_bem_formada`. `citacao_valida` já vem escrita como modelo. As comparações de texto normalizam acento pelos dois lados.
*Fundamento:* denominadores, tetos e casos-limite de `recall@k` e `precision@k` → **Apêndice A.1** (slide 12); o `rr`, o decaimento hiperbólico, o que ele vê que o recall não vê (e por que quem tem reranker **precisa** reportar MRR) e o nDCG como generalização → **Apêndice A.2** (slide 13); as três determinísticas de resposta e a conjunção da trajetória, com o caso em que cada uma mente → **Apêndice A.3** (slide 14).

**Checkpoint 3 · o juiz com rubrica (01:15–01:25).**
*Ao final, `python judge.py` imprime `Checkpoint 3 OK`* com a nota **e o motivo** de cada caso de teste, e `ADVERTENCIA_JUIZ` sem `TODO`.
*O que fazer:* escrever a `RUBRICA` do próprio domínio — três critérios, três níveis com âncora observável — e implementar os dois critérios pendentes de `juiz_heuristico` (o de escopo já está pronto como modelo). Declarar `LIMIAR_APROVACAO` e preencher `ADVERTENCIA_JUIZ` com quem julgou.
*Fundamento:* a rubrica define a **distribuição de rótulos**, e é a distribuição que determina quanto do acordo é explicado por acaso — daí "a rubrica decide o kappa dez minutos depois" ser mecanismo e não retórica. → **Apêndice A.4** (slide 15)

**Checkpoint 4 · calibração e kappa (01:25–01:37).**
*Ao final, `python calibracao.py` imprime acordo bruto, kappa e a lista de desacordos* — e existe **uma linha escrita por desacordo**, com a decisão: conserto na rubrica, no juiz ou no sistema. Kappa baixo **não** reprova o checkpoint; kappa sem inspeção de desacordo, sim.
*O que fazer:* anotar à mão em `calibracao.py` pelo menos 10 casos do próprio conjunto — de preferência 12, incluindo os de fronteira — **antes** de rodar o juiz. Implementar `kappa_cohen`. Rodar, ler a matriz de confusão e inspecionar cada desacordo.
*Fundamento:* derivação de `p_e` sobre a matriz do exemplo (`p_o = 0,83`, `p_e = 0,50`, `κ = 0,67`, passo a passo), o **kappa ponderado** para os três níveis ordenados, o **teto humano-humano** e os casos-limite específicos do lab. → **Apêndice A.4** (slide 15), que remete a **A.1 da Aula 27**
*Padrão de leitura a aplicar:* desacordos agrupados por mecanismo → conserto na rubrica; desacordos espalhados sem padrão → conserto no juiz.

**Checkpoint 5 · rodar, analisar, priorizar, relatar (01:37–01:47).**
*Ao final, o arquivo `relatorio-avaliacao.md` existe com as seis seções e `teste_checkpoint_5` passa* — ele falha de propósito se o sistema declara camada de retrieval e o relatório não tem `recall@`, ou se não há kappa no relatório.
*O que fazer:* implementar `classificar_falha` na ordem de baixo para cima, preencher `CUSTO_POR_CAMADA` com a estimativa da equipe e rodar `python rodar.py`.
*Fundamento:* o impacto de cada camada é uma proporção medida em 20 casos; a ordem da tabela de prioridade só é confiável quando as diferenças excedem a resolução `1/n`. E, para comparar a versão consertada com a de hoje, o teste correto é o de **McNemar** — pareado, porque os dois sistemas rodam nos mesmos casos. → **Apêndice A.5** (slide 16)

**Extensões (para quem terminar antes, 01:47–01:50).** `python rodar.py --juiz llm` com a chave por `getpass` e comparação do kappa das duas rotas; `taxa_inversao` do pairwise implementada e reportada; kappa **entre dois anotadores humanos** da equipe sobre a mesma amostra, para comparar com o kappa juiz-humano — o número que diz se o teto é o juiz ou a tarefa, e cuja leitura está em A.4.

**Questões-guia** (respondidas no relatório, avaliadas por precisão conceitual):

1. Por que os casos `fora_do_escopo` não entram no denominador de `recall@k`, e o que aconteceria com o número se entrassem?
2. O acordo bruto da equipe ficou acima do kappa. Explique a diferença com a distribuição de rótulos do conjunto de vocês.
3. Qual desacordo juiz–humano vocês corrigiram mexendo na rubrica e qual vocês deixaram de pé? Justifique a decisão.
4. A tabela por categoria mostra alguma categoria com taxa de falha muito acima da média? O que a nota global esconde nesse caso?
5. Vocês priorizaram a camada de maior impacto ou a de melhor razão impacto/custo? Se as duas divergem, defenda a escolha. **E diga se a diferença entre as duas primeiras camadas da sua tabela é maior que a resolução do seu conjunto.**

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Equipe sem sistema rodando** (Entrega 2 atrasada ou pipeline quebrado) | O adaptador não tem o que chamar | O `executar_stub` já resolve: o harness fecha de ponta a ponta com um sistema que recusa tudo, e os cinco checkpoints são avaliáveis. A equipe entrega o harness pronto e liga o sistema na semana seguinte. Nenhum checkpoint deste lab depende do sistema estar bom |
| **Sem rede ou sem chave de API** | Falha na primeira chamada do `--juiz llm` | A rota padrão é o `juiz_heuristico`: determinístico, offline, sem quota, e o lab inteiro fecha nele. A rota LLM é extensão declarada, não requisito |
| **Rate limit** do free tier no `--juiz llm` com a sala inteira chamando | Erro 429 em parte dos casos | O `juiz_llm` cai para a rota heurística caso por caso e marca a queda; o relatório declara quais linhas são heurísticas. Alternativa: metade da sala roda a rota LLM e a outra metade fica no offline, e comparam o kappa |
| **Projetos muito diferentes entre si** (um sem retrieval, um sem loop) | Métricas de camada inexistente saindo em zero | O contrato do adaptador já cobre: lista vazia remove a camada do denominador. A equipe tira a camada de `SISTEMA["camadas"]` e o relatório não a menciona. O instrutor circula na primeira meia hora para conferir isso projeto por projeto |
| **Escrever 20 casos leva mais que os 15 min do CP1** | 00:50 e a maioria com 8 casos | Aceitar 12 casos válidos em sala e mandar os 8 restantes para casa junto do desafio; o objetivo do checkpoint em sala é a **forma** do caso e o validador passando, não o volume. O mínimo de 20 vale na entrega |
| **Kappa muito baixo** e equipe desanimada | Kappa perto de zero em várias equipes | É o resultado mais didático do lab, não uma falha: kappa baixo é diagnóstico da rubrica. Conduzir uma reescrita ao vivo com uma equipe, na frente da turma, mostrando os níveis ganhando âncora observável. E dizer o mecanismo — a rubrica define a distribuição, a distribuição define `p_e` (A.4) |
| **Kappa suspeito de alto** (acima de 0,9) na primeira tentativa | Zero desacordo em 12 casos | Quase sempre a anotação foi feita depois de ver a saída do juiz, ou a amostra é só de casos fáceis. Pedir três casos de fronteira e reanotar; o número honesto costuma cair muito |
| **Equipe confunde o harness com o sistema** | Pergunta "então o que a gente entrega, o notebook do projeto ou este?" | Cravar no recolhimento: são dois artefatos no mesmo repositório. O sistema responde; o harness mede o sistema. A Aula 30 pede os dois |
| **A turma pedir a derivação durante o lab** | "Como você sabe que 0,71 e 0,78 são o mesmo número?" no meio do CP1 | Num lab, **a bancada tem prioridade**: resposta de uma frase mais o ponteiro para o item do apêndice. A Parte 4 do roteiro tem cinco contas prontas com o tempo de cada uma; a única janela barata é os três minutos do Slide 10, que é expositivo. O item 4 (A.5) é o único que vale abrir espaço, porque é a pergunta que a Aula 27 plantou |
| **Equipe lê a tabela de prioridade como ranking** | "A camada X é a pior, vamos consertar ela" com 4 casos contra 3 | Cravar a ressalva da resolução: diferença de um caso em vinte não ordena nada. A tabela é ponto de partida; a decisão final olha também o custo e o que a equipe consegue consertar em duas semanas. Está em A.5 e vale na seção de limitações |

## 7. Artefatos produzidos

- **Harness executável** em `codigo/lab-08-harness-avaliacao/` com os cinco módulos preenchidos: `adaptador.py` ligado ao sistema da equipe (ou ao stub declarado), `casos.py` com 20+ casos, `metricas.py`, `judge.py` com a rubrica do domínio, `calibracao.py` com a anotação humana.
- **`relatorio-avaliacao.md` gerado pelo código**, com as seis seções: métricas por camada com `n`, calibração do juiz com kappa e matriz de confusão, falhas por camada, falhas por categoria, priorização dos consertos e limitações reconhecidas.
- **Anotação humana da equipe**: a amostra rotulada à mão, com o nome de quem anotou, e uma linha escrita por desacordo com a decisão tomada.
- **A resolução declarada do conjunto** — `1/n` em pontos percentuais, escrita na seção de limitações, com a frase sobre o que este conjunto consegue e não consegue distinguir. É o artefato novo da V2 e o que impede o relatório de declarar melhorias que não existem.
- **Lista de consertos priorizada** — a fila de trabalho da equipe até a Aula 30, que é o insumo direto do slide de resultados da apresentação final.
- **Respostas às cinco questões-guia** e a declaração de uso de IA.

Tudo isso vive no repositório do projeto e **integra a entrega final da Aula 30**. Este lab não produz um artefato descartável.

## 8. Desafio pós-aula

É o único lab do curso em que o desafio pós-aula é, também, trabalho de projeto — porque o harness é entregável nos dois lugares.

1. **Fechar o conjunto em 20+ casos** com a composição exigida e rodar o harness com o sistema real ligado no lugar do stub. Comparar a tabela por camada com a que saiu do stub: onde o sistema real ficou **abaixo** do sistema que recusa tudo? A resposta costuma estar em `recusa_correta`, e ela é uma lição sobre métrica isolada — a mesma da conta `3/20` contra `3/3` em A.3.
2. **Rodar a rota LLM-as-judge** com chave por `getpass`, recalcular o kappa contra a mesma anotação humana e reportar os dois kappas lado a lado. Se o juiz LLM concordar **menos** com o humano que o juiz heurístico, dizer por quê — e essa resposta vai para o relatório do projeto.
3. **Medir o teto da tarefa:** dois integrantes anotam a mesma amostra independentemente e calculam o kappa humano-humano. Se ele for 0,6, nenhum juiz vai passar de 0,6 nessa tarefa, e isso muda o que se pode cobrar do juiz. Reportar a **razão** entre o kappa juiz-humano e o teto, não só os dois números — a leitura está em A.4.
4. **Aplicar o McNemar.** *(novo na V2)* Depois de consertar a primeira camada da fila de prioridade, rodar o harness de novo e montar a tabela pareada: quantos casos só a versão antiga acerta, quantos só a nova acerta. Os casos em que as duas acertam ou as duas erram ficam de fora. Aplicar o teste exato e reportar o `p`-valor junto da diferença de taxa. Se o resultado não for distinguível de uma moeda — e com 20 casos ele provavelmente não será —, escrever isso no relatório e **listar os casos discordantes um a um**, que é onde está toda a informação do experimento. A conta está em **A.5**.
5. **Leitura.** Retomar Hendrycks et al., *Measuring Massive Multitask Language Understanding* (arXiv 2009.03300) com a pergunta invertida do desafio da Aula 27: agora que vocês têm um conjunto de teste próprio, quantos dos seus 20 casos poderiam ser reescritos como múltipla escolha de quatro alternativas sem perder o que eles medem? Os que não podem são exatamente a razão de o projeto precisar de harness próprio.

## 9. Critérios de avaliação

Este lab compõe os **30% de laboratórios** da ementa (média dos 8 labs, descartando a menor nota) **e** produz o insumo do item de **rigor da avaliação quantitativa — 30% da nota do projeto final** (rubrica: técnica 40%, avaliação 30%, relatório 20%, apresentação 10%). Nenhum peso novo é criado aqui.

Distribuição da nota deste lab (idêntica à V1):

- **Checkpoints 1 a 3 concluídos com saída visível — 35%.** Os três `Checkpoint N OK` impressos, o conjunto com a composição exigida, as métricas passando os testes de mesa e a rubrica com níveis observáveis. Módulo sem saída impressa não é avaliável.
- **Checkpoint 4, calibração — 25%.** A anotação humana da equipe, o kappa **calculado** (não só o acordo bruto), a matriz de confusão e uma linha escrita por desacordo com a decisão. **Kappa baixo não perde ponto; kappa sem inspeção de desacordo perde.**
- **Checkpoint 5, relatório gerado — 25%.** O `relatorio-avaliacao.md` com uma linha por camada declarada, o `n` de cada métrica, a tabela por categoria, a priorização com custo declarado e a seção de limitações. **É a parte que decide a nota:** um harness que roda e não gera relatório com número por camada fica, por construção, abaixo da média.
- **Respostas às cinco questões-guia — 10%.** Avaliadas por precisão conceitual. As duas que separam as notas: por que o caso fora do escopo não entra no denominador do `recall@k`, e por que o acordo bruto ficou acima do kappa naquele conjunto.
- **Declaração de uso de IA presente — 5%.** Ausência zera este item e habilita defesa oral.

O que **não** cumpre o entregável, dito por escrito porque é o desvio esperado:

> "O sistema respondeu bem em 8 de 10 perguntas" não é resultado. Sem número por camada, sem denominador declarado e sem concordância do juiz medida, o relatório perde o item de rigor — mesmo com o sistema funcionando perfeitamente na demo.

**O que a V2 muda no *como* se corrige**, sem mexer nos pesos:

- **Número sem `n` conta como número ausente.** Uma linha de tabela com "0,78" e sem denominador não pontua no item do Checkpoint 5. É a mesma exigência que a Aula 27 instalou e que este lab implementa em código — o gerador do relatório já imprime o `n`, então omiti-lo exige esforço.
- **A questão-guia 1 vale pela consequência, não pela regra.** "Porque eles não têm fonte relevante" é a resposta da V1 e vale parcialmente. A resposta completa diz **o que aconteceria com o número** se entrassem: com 3 fora do escopo em 20, um recall real de 0,80 seria reportado como 0,68. O material está em **A.1**.
- **A questão-guia 2 vale pela distribuição, não pelo nome do fenômeno.** "Porque o kappa desconta o acaso" não separa nota. A resposta que separa aponta as marginais do próprio conjunto e diz quanto de `p_e` elas produzem — e reconhece que uma rubrica com um nível quase nunca usado é a causa. **A.4** e a comparação `p_e = 0,50` contra `p_e = 0,82` existem para isso.
- **A seção de limitações passa a ter conteúdo exigível.** Declarar a resolução do conjunto (`1/n`) e reconhecer que a ordem da tabela de prioridade não é confiável dentro dessa resolução é o que distingue um relatório honesto de um relatório bonito. **A.5** é a leitura indicada, e o desafio pós-aula item 4 é o exercício.
- **O apêndice é cobrável como fundamento de justificativa, nunca como derivação isolada.** Nenhuma questão-guia pede "derive o intervalo de Wilson" ou "demonstre o McNemar". Várias pedem que o aluno **use** a resolução do conjunto para qualificar uma afirmação — e é a existência de A.5 que torna razoável exigir isso.

*Observável em sala, sem nota:* no recolhimento, cada equipe aponta na própria tabela a camada que vai consertar primeiro, diz o número que a justifica **e diz quantos casos aquele número representa**. Quem responder "vamos melhorar as respostas" ainda não leu a própria tabela. Quem disser o número sem o `n` está a meio caminho — e é o caminho que este lab existe para completar.
