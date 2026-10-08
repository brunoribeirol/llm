---
aula: 24
titulo: "Sistemas multiagente e orquestração"
modulo: "5 — RAG, Ferramentas e Agentes de IA"
tipo: teorica
semana: 12
duracao_min: 120
versao: v2
---

# Aula 24 — Sistemas multiagente e orquestração

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** Esta aula já era conduzida pela aplicação na V1 e por isso muda pouco: o
> ceticismo dela já era conteúdo medido (a demo compara duas arquiteturas com três números) e o
> exercício já era de redesenho de arquitetura. As **duas** contas do fluxo viraram itens do apêndice
> do deck — **A.1** (`p^N`, com as inversões `p ≥ s^(1/N)` e `N ≤ ln s / ln p`, e o efeito da
> verificação por estágio) e **A.2** (o produto dos tetos, a soma geométrica da delegação e a latência
> por topologia). Carga horária, numeração e objetivos de aprendizagem inalterados.

## 1. Objetivo da aula

Dar ao aluno os quatro padrões de composição multiagente com seus custos declarados — e a capacidade de argumentar, com número, quando **um** agente com boas ferramentas resolve melhor. O ceticismo desta aula é conteúdo: multiagente é resposta a limites concretos, não um degrau de sofisticação.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Nomear** as três razões que justificam dividir um sistema em vários agentes — especialização, paralelismo e contexto limitado por agente — e **identificar** qual delas se aplica a um caso dado.
2. **Desenhar** os quatro padrões (orquestrador-trabalhadores, pipeline de estágios, debate/crítico, painel de especialistas) indicando quem decide, quem executa e por onde a informação passa.
3. **Estimar** o custo de uma arquitetura multiagente em chamadas e tokens e **compará-lo** com o de um agente único na mesma tarefa.
4. **Calcular** a taxa de sucesso composta de um pipeline de N estágios e **explicar** por que acrescentar estágio confiável piora o resultado final.
5. **Aplicar** o teste de três perguntas que separa multiagente necessário de multiagente decorativo, e **reescrever** uma arquitetura inflada numa mais simples.
6. **Situar** LangGraph, CrewAI e SDKs de agentes pelo que cada um resolve (estado, papéis, transporte) e **justificar** por que o curso implementa o loop na mão antes de adotar framework.

## 3. Teoria aplicada

### Bloco 1 (00:10–00:55) — Por que dividir, e os quatro padrões

**Conceito 1 — As três razões que se sustentam, e as que não.**
Dividir em vários agentes se justifica por três motivos verificáveis. **Especialização:** cada agente tem um prompt de sistema, um catálogo de ferramentas e um critério de sucesso próprios — o que reduz a ambiguidade da decisão em cada ponto. **Paralelismo:** subtarefas independentes rodam ao mesmo tempo, e aqui o ganho é em latência de parede, não em custo. **Contexto limitado por agente:** cada agente carrega só a trajetória do seu pedaço, o que evita a degradação de precisão da Aula 23 quando a trajetória fica longa. Fora dessas três, o resto costuma ser estética de arquitetura.
*Fundamento (razão 2):* o ganho do paralelismo é `L = max_i ℓ_i` em latência de parede, com `custo = Σ_i custo_i` inalterado. → **A.2**, Derivação 4
*Analogia do instrutor:* é a mesma decisão de quebrar um monólito em serviços. Quebra-se por limite de time, de deploy ou de escala — não porque "microserviço é mais moderno". E quem quebra sem motivo herda a coordenação sem herdar o benefício.
*Erro conceitual comum:* tratar "o prompt ficou grande" como razão para dividir. Prompt grande pede edição de prompt; o que pede divisão é trajetória grande, que é outra coisa.

**Conceito 2 — Orquestrador-trabalhadores.**
Um agente central recebe o objetivo, decompõe, decide qual trabalhador chama, recebe os resultados e sintetiza. Os trabalhadores não conversam entre si e podem ser burros de propósito — muitos são função determinística, não agente. É o padrão mais usado e o mais fácil de depurar, porque existe um único ponto onde a decisão acontece. Custo: pelo menos uma chamada do orquestrador por rodada, mais as chamadas dos trabalhadores.
*Analogia:* editor-chefe e pauteiros. O chefe não escreve as matérias, mas é o único que decide o que entra na edição.
*Fundamento:* trabalhador determinístico tem `b_w = 0` e `p = 1` — sai do produto dos tetos (**A.2**) e sai da conta de `p^N` (**A.1**). E repassar a trajetória inteira faz a entrada da rodada `k` valer `p₀ + k·d`, com soma quadrática sobre as rodadas. → **A.2**, composição
*Erro conceitual comum:* fazer o orquestrador repassar a trajetória inteira a cada trabalhador. Isso destrói a razão 3 (contexto limitado) e multiplica o custo — o trabalhador deve receber a menor entrada suficiente, e devolver a menor saída suficiente.

**Conceito 3 — Pipeline de estágios.**
A saída de um agente é a entrada do seguinte, com a ordem fixada de antemão: extrair → normalizar → classificar → redigir. Não há decisão de roteamento, e por isso é o padrão mais previsível, mais barato de testar e o único em que dá para avaliar cada estágio separadamente. Note o que ele é: é o **workflow determinístico** da Aula 23 com LLMs nos estágios. Se o problema encaixa aqui, quase sempre é aqui que ele deve ficar.
*Erro conceitual comum:* chamar isso de sistema multiagente para parecer mais avançado. É um pipeline, e ser um pipeline é uma virtude — código previsível, testável, com falha localizável.

**Conceito 4 — Debate e crítico.**
Duas variantes do mesmo mecanismo: gerar e depois julgar. No **crítico**, um agente produz e outro avalia contra critérios explícitos, devolvendo para revisão — é uma volta, no máximo duas. No **debate**, dois ou mais agentes defendem posições e um juiz decide. O ganho real aparece quando o crítico tem acesso a algo que o gerador não tem: um verificador, uma fonte, um teste. Quando os dois têm exatamente a mesma informação e o mesmo modelo, o que se compra por duas vezes o custo é sobretudo variância, não qualidade.
*Analogia:* revisão por pares só funciona quando o revisor pode conferir os dados. Revisor que só leu o resumo faz revisão de estilo.
*Erro conceitual comum:* acreditar que "dois agentes discutindo" corrige erro factual. Sem fonte externa, o desacordo pode convergir para o erro mais fluente. É o Conceito 7 da Aula 23 em escala de sistema.

**Conceito 5 — Painel de especialistas.**
Vários agentes com prompts de domínio distintos respondem em paralelo à mesma pergunta e um agregador combina — por voto, por síntese ou por seleção do melhor. Faz sentido quando as perspectivas são **genuinamente** diferentes (um analisa risco jurídico, outro custo, outro prazo) e o agregador tem regra explícita de combinação. Quando os especialistas diferem apenas por adjetivo no prompt, o painel produz três respostas parecidas e uma fatura triplicada.
*Erro conceitual comum:* confundir painel com auto-consistência. Auto-consistência é o mesmo prompt amostrado várias vezes com temperatura, e ela tem uso legítimo em tarefa com resposta verificável (Aula 13). Painel é prompt diferente para papel diferente; o mecanismo e o motivo são outros.

### Bloco 2 (01:05–01:50) — O que cada arquitetura custa e o teste do overkill

**Conceito 6 — A conta, feita na mesma tarefa.**
A demonstração roda a mesma tarefa em duas arquiteturas e imprime três números para cada uma: chamadas ao modelo, tokens enviados no total e passos até a resposta. O script é roteirado para que a sala veja sempre os mesmos valores, e a ordem de grandeza é esta: o orquestrador-trabalhadores gasta cerca de 1,4× os tokens do agente único e quase o dobro na variante que repassa a trajetória inteira, com 5 chamadas de modelo contra 3 — e entrega **a mesma resposta**. Os números exatos são os que aparecem na tela; nenhum deles é resultado universal. É um contraexemplo suficiente para desmontar a ideia de que mais agentes é melhor por definição, e uma escala honesta: numa tarefa de três passos a diferença é de dezenas de por cento, e ela cresce com o número de trabalhadores e com o tamanho do contexto repassado.
*Erro conceitual comum:* comparar arquiteturas por qualidade percebida da resposta, sem instrumentar chamadas e tokens. Sem os três números, a comparação é preferência estética.

**Conceito 7 — Coordenação: contexto não se compartilha de graça.**
Dois agentes só cooperam pelo que trocam, e o que trocam é texto. Isso cria três problemas ausentes no agente único: **perda na tradução** (o trabalhador recebe uma versão resumida do objetivo e resolve outro problema, ligeiramente diferente), **duplicação de trabalho** (dois trabalhadores buscam a mesma coisa porque nenhum sabe do outro) e **estado inconsistente** (dois agentes com versões diferentes do mesmo fato). Mitigar exige protocolo explícito: quem escreve onde, com que formato, e qual é a fonte de verdade.
*Analogia:* é o problema clássico de sistema distribuído. Passar de um processo para dois não dobra a complexidade — introduz uma classe nova de falha.
*Erro conceitual comum:* achar que "os agentes se coordenam sozinhos" porque o texto que eles trocam é em linguagem natural. Linguagem natural é o transporte mais ambíguo disponível; ela facilita a escrita do sistema e dificulta o diagnóstico dele.

**Conceito 8 — Orçamento compartilhado e custo multiplicado.**
No agente único, `max_passos` é um número. Com N agentes, cada um com o seu teto, o pior caso é o **produto** dos tetos, não a soma: um orquestrador de 5 passos que chama trabalhadores de 5 passos cada admite 25 chamadas de modelo antes de qualquer proteção global. Por isso o orçamento tem de ser compartilhado: um contador único, decrementado por qualquer agente, com o sistema abortando quando ele zera. Latência segue a topologia — soma no pipeline, máximo no paralelo, soma dos máximos no orquestrador.
*Fundamento:* `total ≤ b₀·(1 + b_w)` com `D = 1`, e `b₀·(b_w^{D+1} − 1)/(b_w − 1)` para profundidade `D` — os 25 do slide são o termo `b₀·b_w`, e `D = 3` dá 780. Orçamento por agente **descreve** o pior caso; contador global **escolhe** o pior caso. → **A.2**
*Erro conceitual comum:* definir orçamento por agente e supor que o total está controlado. É o erro que aparece na fatura no primeiro dia de produção.

**Conceito 9 — Propagação de erro: a conta que condena pipelines longos.**
Se cada estágio acerta com probabilidade `p` e o erro de um estágio compromete o resultado final, a taxa de sucesso é `p^N`. Com `p = 0,95` — que é bom para uma etapa com LLM — cinco estágios dão `0,77`; dez dão `0,60`. Cada estágio a mais é uma multiplicação, não uma adição. E há um agravante: erro em estágio inicial chega ao estágio final **com a mesma fluência** de um dado correto, porque o estágio seguinte não tem como saber que a entrada está errada. Daí a única mitigação que funciona: verificação **por estágio**, com a etapa parando em vez de repassar — o que é exatamente o gancho do Lab 8 (Aula 28), onde a métrica é por camada.
*Fundamento:* `P_sist = Π p_i = p^N`; invertendo, `p ≥ s^(1/N)` (meta de 90% com 5 estágios exige 97,9% por estágio) e `N ≤ ln s / ln p` (com `p = 0,95` e meta 90%, cabem **dois** estágios). Com verificação e uma segunda tentativa, `p′ = 1 − (1−p)²` e a taxa de 5 estágios vai de `0,774` a `0,988` — é a forma quantitativa de "verificação por estágio é a única mitigação que funciona". → **A.1**
*Analogia:* linha de montagem sem inspeção intermediária. O defeito só aparece no fim, e aí o produto inteiro é perda.
*Erro conceitual comum:* acreditar que "o próximo agente vai corrigir". Ele não vai: ele não sabe que há o que corrigir.

**Conceito 10 — Quando multiagente é overkill: o teste de três perguntas.**
Antes de dividir, três perguntas com resposta escrita. **(a) Qual das três razões do Conceito 1 se aplica, nominalmente?** Se a resposta não é uma das três, não divida. **(b) O que o segundo agente vê que o primeiro não veria?** Se a resposta é "nada, só um prompt diferente", isso é um prompt diferente, não um agente — e trocar de prompt custa uma chamada, não uma arquitetura. **(c) Como esta arquitetura falha, e onde eu leio a falha?** Se não existe lugar único para ler a trajetória do sistema inteiro, o sistema não é depurável, e o custo disso aparece na primeira semana.
Esta é a postura do curso, e ela é técnica, não estilística: **muito do que é vendido como multiagente resolve melhor com um agente e boas ferramentas.** Uma ferramenta bem descrita é mais barata, mais testável e mais previsível que um agente inteiro — e o Lab 6 já mostrou que descrição de ferramenta é prompt.
*Erro conceitual comum:* tratar esse ceticismo como conservadorismo. Ele é o mesmo critério do Conceito 9 da Aula 23: acrescentar peça sem verificador acrescenta modo de falha.

**Conceito 11 — Panorama crítico de frameworks: princípios antes de ferramentas.**
Três categorias, pelo que cada uma resolve. **Grafos de estado (LangGraph e semelhantes):** o sistema é um grafo de nós com estado explícito, arestas condicionais e pontos de interrupção — bom quando o fluxo tem ciclos e checkpoints, e a curva de aprendizado é do modelo de estado, não do LLM. **Papéis e equipes (CrewAI e semelhantes):** agentes declarados por papel e objetivo, com delegação embutida — rápido para prototipar, e a abstração de "papel" esconde justamente o que precisa ser inspecionado. **SDKs de agentes dos provedores:** o loop de ferramentas mantido pelo fornecedor, colado na API — menor atrito, maior acoplamento, e o loop deixa de ser seu.
Nenhum deles decide nada: quem decide é o modelo. Framework organiza chamadas, guarda estado e padroniza retentativas. O critério de escolha honesto é: eu consigo ler a trajetória inteira que esse framework produziu? Se não consigo, ele não serve para um sistema que eu vou avaliar — e avaliar é obrigatório neste curso.
*Erro conceitual comum:* escolher framework antes de ter o loop funcionando na mão. Quem monta o loop primeiro avalia framework por conveniência; quem começa pelo framework não tem base de comparação — é literalmente o Checkpoint 5 do Lab 7.

**Conceito 12 — Três estudos de caso, com a arquitetura mínima de cada.**
**Deep research:** um orquestrador planeja subperguntas, trabalhadores buscam em paralelo e um sintetizador redige com citação. Aqui multiagente se justifica pelas três razões ao mesmo tempo — e o ponto crítico é a citação, porque é ela que dá verificador ao resultado.
**Automação de suporte:** o desenho quase sempre certo é um pipeline de estágios — classificar intenção, recuperar histórico e política, redigir, e um portão de aprovação humana para ação irreversível. Um agente por tipo de ticket é o caso mais comum de multiagente decorativo.
**Agentes de dados:** um agente com ferramentas boas (executar SQL, ler schema, rodar script) e um verificador barato — a consulta executa? o total fecha com o controle? Dividir em "agente de SQL" e "agente de análise" costuma render dois agentes discutindo sobre um schema que nenhum dos dois leu inteiro.
*Erro conceitual comum:* copiar a arquitetura do caso de deep research para o caso de suporte. As três razões não se aplicam, e a fatura triplica sem ganho.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura | Recap da Aula 23 (as cinco peças; os dois testes de decisão; o coding agent e o verificador); a tese de hoje — multiagente é resposta a limites concretos, não um degrau de sofisticação |
| 00:10 | 45 min | Bloco 1 — Por que dividir e os quatro padrões | As três razões que se sustentam (especialização, paralelismo, contexto limitado) e as que não; orquestrador-trabalhadores; pipeline de estágios; debate e crítico; painel de especialistas — cada padrão com quem decide, quem executa e o custo declarado |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — Custos, riscos e o teste do overkill | Demonstração comparando agente único × orquestrador-trabalhadores na mesma tarefa, com chamadas, tokens e passos (8 min); coordenação e as três falhas novas; orçamento compartilhado e o produto dos tetos; propagação de erro e `p^N`; o teste de três perguntas; panorama crítico de frameworks; três estudos de caso; exercício em dupla (5 min) |
| 01:50 | 10 min | Fechamento | Síntese "princípios antes de ferramentas"; ponte para a Aula 25 (Lab 7: construindo um agente autônomo), em que o loop é escrito na mão e depois comparado com framework; leitura indicada |

## 4. Demonstração guiada

**Demo "a mesma tarefa, duas arquiteturas" — 8 min, `codigo/demo-orquestrador-vs-agente.py`, offline, sem dependências.**

O script resolve a mesma pergunta duas vezes — uma com um agente único que tem três ferramentas, outra com um orquestrador que delega a três trabalhadores — e imprime, para cada arquitetura, chamadas ao modelo, tokens enviados no total e passos até a resposta. O modelo é um simulador roteirado determinístico com semente fixa; as duas arquiteturas chegam à **mesma** resposta final.

Passos em alto nível:

1. Enunciar a tarefa antes de rodar: uma pergunta que exige consultar o regulamento, fazer uma conta e redigir a resposta com citação.
2. Rodar `python demo-orquestrador-vs-agente.py --unico` e ler a trajetória: um agente, três ferramentas, três passos.
3. Rodar `--multi` e ler a trajetória do orquestrador: uma chamada de planejamento, uma delegação por trabalhador, uma chamada de cada trabalhador, uma síntese final.
4. Rodar `--comparar`, que executa as duas e imprime a tabela de três colunas lado a lado. Deixar a turma ler a razão de tokens em voz alta antes de comentar.
5. Apontar no código onde o custo extra nasce: a linha em que o orquestrador repassa contexto ao trabalhador, e a linha da síntese final.
6. Rodar `--multi-vazado`, uma variante em que o orquestrador repassa a trajetória inteira a cada trabalhador: a razão de tokens piora de novo, e a resposta continua a mesma. Nomear: é o erro do Conceito 2.
7. Fechar com honestidade sobre o que a demo **não** mostra: ela não mostra um caso em que multiagente ganha. Esse caso existe — é o deep research do Conceito 12 — e ele não cabe em oito minutos sem rede. O que a demo prova é que a arquitetura não é gratuita.

**Números que a demo produz, e que a aula usa como evidência:** as **três colunas** — chamadas ao
modelo, tokens enviados no total e passos até a resposta — para cada arquitetura, mais as duas
**razões** que a turma lê em voz alta no passo 4: `--multi` sobre `--unico`, e `--multi-vazado` sobre
`--multi`. As duas razões são o que sustenta a tese do slide 2 e o que dá conteúdo empírico ao slide
9: a resposta final é **a mesma** nas três execuções, e só o preço muda. A segunda razão é a evidência
direta do erro do Conceito 2, e ela é retomada no exercício (proposta 1) e no fechamento. *Ressalva
declarada em aula e repetida no slide:* são valores de um simulador roteirado — contraexemplo
suficiente para desmontar "mais agentes é melhor", e não benchmark.

Insumos preparados na véspera: o script rodado nos quatro modos com as saídas salvas em texto; a tabela do modo `--comparar` também transcrita no slide, para o caso de o terminal não projetar.

## 5. Hands-on

**Exercício em dupla — "enxugar a arquitetura" (5 min, 01:45–01:50).**

Três propostas de arquitetura projetadas, todas infladas de propósito e todas parecidas com o que aparece em proposta de projeto. Para cada uma, a dupla escreve a arquitetura mínima equivalente e uma frase dizendo qual das três razões do Conceito 1 sobrevive.

1. "Assistente de regulamentos com um agente de busca, um agente de leitura, um agente de redação e um agente revisor."
2. "Sistema de triagem de issues com um agente por linguagem de programação do repositório."
3. "Analista de dados com um agente que escreve SQL, um agente que executa, um agente que interpreta e um agente que faz o gráfico."

Critério de conclusão observável: três linhas escritas, cada uma com a arquitetura reduzida e a razão sobrevivente (ou a palavra "nenhuma"). Correção em 2 min: a 1 vira um agente com duas ferramentas mais, no máximo, um crítico com acesso ao acervo; a 2 vira um agente com uma ferramenta de busca no repositório — linguagem não é especialização de decisão, é parâmetro; a 3 vira um agente com ferramentas e um verificador (a consulta executa? o total fecha?), e o gráfico é uma função, não um agente.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Turma lê o ceticismo como "não use multiagente"** | Pergunta "então isso não serve para nada?" | O Conceito 12 existe para isso: deep research é o caso em que as três razões se aplicam simultaneamente. A postura é "justifique pelas três razões", não "não use" |
| **Terminal ilegível na projeção** | Turma pedindo fonte maior | A tabela do modo `--comparar` está transcrita no slide da demo; as saídas dos quatro modos estão salvas em texto |
| **Discussão de framework consumindo o Bloco 2** | 01:20 e a sala comparando bibliotecas | O slide de frameworks tem janela fixa (01:35–01:41) e um critério único de decisão: dá para ler a trajetória inteira? Perguntas de comparação de biblioteca são remetidas ao Checkpoint 5 do Lab 7 |
| **Aluno com projeto já desenhado como multiagente** se sente atacado | Reação defensiva na hora do teste de três perguntas | Enquadrar como revisão de arquitetura, não como erro: aplicar as três perguntas ao vivo no projeto de quem se ofereceu, e mostrar que a versão enxuta é entregável na Entrega 2 |
| **Números da demo tratados como resultado geral** | "Então multiagente custa 3× sempre" | Dito na demo e repetido no slide: é um contraexemplo roteirado, não um benchmark. Números de benchmark de agente são Aula 26 |
| **Tempo estourar no Bloco 1** (quatro padrões geram muita pergunta) | 00:50 e ainda no debate/crítico | Painel de especialistas comprime para duas frases e vira nota de rodapé do slide de debate; o Bloco 2 é o que não pode encolher, porque é onde estão os custos |
| **Exercício sem tempo** | 01:47 e os estudos de caso não terminaram | Reduzir para a proposta 1, feita coletivamente em 2 min; as outras duas ficam no material como desafio pós-aula |

## 7. Artefatos produzidos

- Anotação do exercício: três arquiteturas reduzidas, cada uma com a razão sobrevivente nomeada.
- **Ficha de decisão de arquitetura** do projeto da equipe: qual padrão (ou nenhum), qual das três razões justifica, qual é o orçamento compartilhado e onde a trajetória do sistema inteiro é lida. Entra na Entrega 2 (Aula 26).
- `codigo/demo-orquestrador-vs-agente.py`, rodado em casa nos quatro modos, com os três números anotados.
- Nenhum entregável avaliado nesta aula.

## 8. Desafio pós-aula

Não avaliado. Três itens:

1. **Rodar a demo** nos quatro modos e anotar a razão de tokens entre `--unico` e `--multi`, e entre `--multi` e `--multi-vazado`. Escrever duas linhas sobre onde exatamente o custo extra nasce.
2. **Aplicar o teste de três perguntas ao próprio projeto** e escrever as três respostas. Se a resposta a (b) for "nada, só um prompt diferente", reescrever a arquitetura como um agente com mais uma ferramenta — e levar as duas versões para a Entrega 2, com a justificativa da escolha.
3. **Leitura.** Nenhum paper novo é obrigatório nesta aula. O material de referência é a documentação vigente de um framework de orquestração à escolha do aluno (`[definir na oferta]` — a versão é conferida na semana da aula), lida com **uma** pergunta dirigida: onde, nesse framework, eu leio a trajetória completa de uma execução com dois agentes? Se a resposta não estiver na documentação, isso é um achado sobre o framework.

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. Os pesos são os da ementa: laboratórios 30%, prova 30% (Aula 17, já realizada), projeto final 40% com marcos nas Aulas 22, 26 e 30.

O que esta aula alimenta, com peso já definido em outro lugar:

- **Lab 7 (Aula 25) — dentro dos 30% dos laboratórios.** O Checkpoint 5 é a reimplementação com framework e a comparação controle × conveniência; o critério de comparação usado lá é o Conceito 11 desta aula.
- **Entrega 2 do projeto (Aula 26) — 5% da nota final.** A ficha de decisão de arquitetura é parte do que o checkpoint cobra: qual padrão, qual razão o justifica, qual o orçamento compartilhado, e onde se lê a trajetória. Arquitetura multiagente sem resposta a essas quatro é apontada como risco na devolutiva.

Observável em sala, sem nota: ao ser questionado no fechamento, o aluno reduz uma arquitetura de quatro agentes a uma de um agente com ferramentas, e nomeia o que se perde nessa redução.
