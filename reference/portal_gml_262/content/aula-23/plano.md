---
aula: 23
titulo: "Agentes de IA: loops, planejamento e memória"
modulo: "5 — RAG, Ferramentas e Agentes de IA"
tipo: teorica
semana: 12
duracao_min: 120
versao: v2
---

# Aula 23 — Agentes de IA: loops, planejamento e memória

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** Esta aula já era conduzida pela aplicação na V1 e por isso muda pouco: a
> definição operacional é um checklist de diagnóstico, a demo mostra as cinco peças no código e os
> quatro modos com defeito, e o exercício já é de decisão de arquitetura. Existe **uma** conta no
> fluxo — o custo acumulado do laço —, e ela virou o item **A.1** do apêndice do deck, com a
> derivação completa, a inversão `n_max = ⌊√(2B/d)⌋` e a análise formal das três táticas de controle
> de trajetória. Carga horária, numeração e objetivos de aprendizagem inalterados.

## 1. Objetivo da aula

Fixar uma definição operacional de agente que o aluno consiga usar como checklist — **agente = modelo + ferramentas + loop + objetivo + critério de parada** — e, a partir dela, decidir com critério quando um problema pede agente e quando pede pipeline determinístico, sabendo o preço do loop em passos, tokens e latência.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Enunciar** as cinco peças da definição operacional de agente e **apontá-las** no código de um loop de 40 linhas, nomeando o que falta quando uma delas está ausente.
2. **Descrever** o ciclo observar → planejar → agir → refletir e **localizar** cada fase numa trajetória real registrada.
3. **Explicar** o que o ReAct (Yao et al., arXiv 2210.03629) intercala e **justificar** por que o raciocínio explícito antes da ação melhora a escolha de ferramenta.
4. **Distinguir** memória de curto prazo (a trajetória dentro da janela de contexto) de memória de longo prazo (o que persiste entre sessões) e **decidir** o que promover de uma para a outra.
5. **Decidir** entre agente e workflow determinístico aplicando dois testes: o caminho é conhecido? existe verificador para o passo intermediário?
6. **Calcular** o custo de um loop em chamadas e tokens em função do número de passos e **diagnosticar** as duas paradas mal projetadas: o loop que não termina e o que termina cedo.

## 3. Teoria aplicada

### Bloco 1 (00:10–00:55) — Do ciclo à memória: o que faz um agente ser agente

**Conceito 1 — A definição operacional, e por que ela é uma âncora e não um slogan.**
Agente é modelo + ferramentas + loop + objetivo + critério de parada. As cinco peças são um checklist de diagnóstico: retire o loop e sobra o tool calling da Aula 21; retire as ferramentas e sobra um modelo raciocinando sozinho; retire o objetivo e sobra um chat; retire o critério de parada e sobra uma conta de API crescendo. A aula volta a essa lista três vezes — na abertura como definição, no meio como leitura de código, no fim como fechamento.
*Analogia do instrutor:* é a diferença entre um motor, um carro e uma viagem. O modelo é o motor; ferramentas são as rodas; o loop é o acelerador; o objetivo é o destino; o critério de parada é saber que chegou. Sem o último, o carro anda até o tanque acabar.
*Erro conceitual comum:* achar que agente é uma técnica de prompt. Nenhuma das cinco peças é o prompt — o prompt é como o objetivo e o formato da ação entram no modelo, e é a menor parte do sistema.

**Conceito 2 — O ciclo observar → planejar → agir → refletir.**
Cada volta do loop tem quatro momentos, e eles são distinguíveis na trajetória. **Observar** é ler o estado: a pergunta, o que voltou da última ferramenta. **Planejar** é decidir o próximo passo — em texto, é o "Thought". **Agir** é emitir a ação: nome da ferramenta e argumentos. **Refletir** é julgar o resultado obtido antes de decidir a volta seguinte. Um agente que não reflete apenas encadeia chamadas; um que reflete é capaz de dizer "essa busca não trouxe o que eu preciso, vou reformular".
*Analogia:* é o laço de um depurador humano — leio o erro, formo uma hipótese, executo um teste, leio o resultado e decido se a hipótese sobreviveu.
*Erro conceitual comum:* tratar "refletir" como uma etapa mística. Reflexão, em implementação, é uma pergunta a mais no prompt sobre o resultado que acabou de chegar. Não é um módulo novo, é um turno a mais — e por isso custa tokens.

**Conceito 3 — ReAct: intercalar raciocínio e ação.**
O ReAct (Yao et al., arXiv 2210.03629) é a observação de que raciocinar **e** agir alternadamente vence cada uma das duas isoladamente. Só raciocinar (cadeia de pensamento) produz um plano bonito sobre fatos que o modelo não tem. Só agir produz chamadas sem critério, porque nada obrigou o modelo a articular por que aquela ferramenta. Intercalando, o pensamento condiciona a ação seguinte e a observação corrige o pensamento seguinte. O formato canônico é textual e repetitivo: `Thought → Action → Action Input → Observation`, e a última volta troca a ação pela `Final Answer`.
*Analogia:* é a diferença entre um aluno que resolve o problema todo na cabeça e chuta o valor, e um que escreve cada passo e confere o intermediário na calculadora.
*Erro conceitual comum:* confundir ReAct com a API de tool calling da Aula 21. São camadas diferentes: ReAct é o **padrão de interação** (raciocínio explícito intercalado com ação); tool calling é o **mecanismo de transporte** da ação. Dá para fazer ReAct em texto puro com um modelo sem suporte a ferramentas — e é exatamente isso que o Lab 7 faz, de propósito.

**Conceito 4 — Planejamento e decomposição: plano antecipado × plano emergente.**
Duas famílias. No **plano antecipado**, o agente escreve a lista de subtarefas antes de agir e depois executa — bom quando a tarefa tem estrutura previsível e ruim quando o primeiro resultado invalida o plano. No **plano emergente**, cada passo é decidido com o que já se sabe — robusto a surpresa, sujeito a perder o fio em tarefas longas. Sistemas maduros misturam: um plano grosso no início, revisado quando uma observação o contradiz. Decompor bem significa produzir subtarefas **verificáveis** — "achar o artigo que fixa o prazo" é verificável; "entender o regulamento" não é.
*Erro conceitual comum:* medir a qualidade do plano pela sua beleza. Plano com sete etapas elegantes que não podem ser verificadas individualmente é pior que três etapas grosseiras com critério de sucesso cada.

**Conceito 5 — Memória de curto prazo é a trajetória, e ela tem preço.**
A memória de curto prazo do agente é literalmente a lista de mensagens que volta ao modelo a cada passo: pergunta, pensamentos, ações, observações. Ela é o que dá continuidade ao raciocínio, e ela cresce a cada volta — o que significa que o custo por passo **não** é constante: o passo 6 reenvia tudo o que aconteceu nos passos 1 a 5. Daí as três táticas de controle: truncar (descartar observações antigas), resumir (comprimir o passado em algumas linhas) e referenciar (guardar o resultado grande num arquivo e manter no contexto só o caminho).
*Fundamento:* `c_k = p₀ + (k−1)·d`; truncar e resumir tornam `c_k` constante e derrubam o total para linear, referenciar reduz `d` e ataca a constante. → **A.1**
*Analogia:* é a mesa de trabalho. Cabe muito, mas cada papel a mais deixa a mesa mais lenta de ler — e alguns papéis viram um resumo colado na borda.
*Erro conceitual comum:* achar que a janela de contexto grande resolve. Ela adia o problema e piora dois outros: custo cresce linearmente e a capacidade de o modelo achar a informação relevante no meio de muito texto degrada. Contexto é recurso, não depósito.

**Conceito 6 — Memória de longo prazo é o que sobrevive ao fim da sessão.**
Curto prazo morre quando a trajetória termina. Longo prazo é o que se escreveu em algum lugar: um arquivo de fatos aprendidos, uma tabela de preferências do usuário, um índice vetorial de episódios anteriores — que é o RAG do Módulo 5 aplicado ao próprio histórico do agente. A decisão de engenharia não é "ter memória de longo prazo", é **o que promover** para ela e **como recuperar** só o pedaço relevante depois. Sem critério de promoção, a memória de longo prazo vira lixo acumulado que polui todo prompt futuro.
*Erro conceitual comum:* gravar a trajetória inteira como memória de longo prazo. Trajetória serve para auditoria (Aula 26); memória de longo prazo é o **destilado** dela — fato, preferência, procedimento que funcionou.

**Conceito 7 — Reflexão e autocorreção, e o limite honesto delas.**
Pedir ao modelo que critique o próprio resultado antes de seguir melhora resultados quando existe um sinal externo para reagir: a ferramenta devolveu erro, o teste falhou, a busca voltou vazia. Quando não existe sinal externo, a autocrítica tende a ser confirmatória — o modelo defende o que acabou de escrever, ou muda de opinião sem informação nova. É o mesmo fio da Aula 16: verificação automática é o que transforma tentativa em aprendizado.
*Erro conceitual comum:* montar uma etapa de "auto-avaliação" sem verificador e acreditar no resultado dela. O agente diz "revisei e está correto" com a mesma fluência com que diria o contrário.

### Bloco 2 (01:05–01:50) — Quando usar, quanto custa e como quebra

**Conceito 8 — O loop em código: as cinco peças visíveis em 40 linhas.**
A demonstração existe para desmistificar. Um loop de agente é um `while` com orçamento de passos, uma chamada ao modelo, um `parse` do texto devolvido, um despacho para um dicionário de funções e um `append` da observação na trajetória. As cinco peças da definição aparecem como cinco trechos apontáveis na tela. Não há framework, não há mágica, e o volume de código que separa "chat" de "agente" é da ordem de trinta linhas.
*Erro conceitual comum:* atribuir a um framework a inteligência que é do modelo. O framework organiza chamadas; ele não decide nada.

**Conceito 9 — Agente × workflow determinístico: dois testes, nesta ordem.**
Primeiro teste: **o caminho é conhecido?** Se a sequência de passos é a mesma sempre — extrair, validar, transformar, gravar — isso é um pipeline, e escrever um agente para executá-lo troca código previsível por sorteio caro. Segundo teste, o que decide os casos difíceis: **existe verificador para o passo intermediário?** Se dá para checar automaticamente se o passo deu certo (o teste passou, o JSON validou, a busca trouxe o dispositivo pedido), o loop pode explorar com segurança, porque o erro é detectado e corrigido dentro da própria trajetória. Sem verificador, o loop propaga erro com autoridade. É o critério da Aula 16 — recompensa verificável — reaparecendo como decisão de arquitetura.
*Analogia:* GPS com trânsito × trilho de trem. Se o trajeto muda e existe sinal para saber que a rota deu errado, GPS. Se o trajeto é o mesmo e o sinal não existe, trilho.
*Erro conceitual comum:* usar "a tarefa é complexa" como critério. Complexidade não pede agente; **incerteza intermediária verificável** pede agente. Muita tarefa complexa é um pipeline longo.

**Conceito 10 — Custo e latência de loops: a conta que ninguém faz antes.**
Uma resposta de chat é uma chamada. Um agente de seis passos são sete chamadas (seis voltas mais a síntese), cada uma reenviando a trajetória acumulada. Se cada volta acrescenta em média `d` tokens, o total enviado cresce de forma quadrática em passos, não linear: `Σ(k·d) ≈ d·n²/2`. Latência acumula do mesmo jeito, e ela é sequencial por construção — o passo 4 não começa antes de o 3 voltar. É por isso que o orçamento de passos (`max_passos`) é decisão de produto e não de defensividade: ele fixa o teto de custo e o teto de espera do usuário.
*Fundamento:* `T(n) = d·n(n+1)/2 ≈ d·n²/2`; a estimativa ingênua erra por `(n+1)/2`; e `max_passos = ⌊√(2B/d)⌋` para um orçamento `B` de tokens por pergunta. → **A.1**
*Erro conceitual comum:* estimar o custo do agente multiplicando o custo de uma chamada pelo número de passos. Subestima, porque ignora o reenvio da trajetória — e o fator do erro é `(n+1)/2`, que com seis passos é 3,5×.

**Conceito 11 — Paradas mal projetadas: os dois lados do mesmo defeito.**
**Loop que não termina:** o modelo pede ferramenta indefinidamente porque a ferramenta falha sempre, porque a observação não responde à pergunta, ou porque o prompt não deixou claro como encerrar. Sintomas: a mesma ação repetida com o mesmo argumento; duas ações alternando em ciclo. Mitigações: orçamento de passos, detecção de repetição (mesma ação e mesmo argumento duas vezes seguidas) e uma resposta de fallback declarada — "não consegui, e é isto que eu tentei".
**Parada precoce:** o agente responde antes de ter fundamento, seja porque o formato de parada é fácil de emitir por acidente, seja porque a primeira observação parecia suficiente. Sintoma: `Final Answer` no primeiro passo, sem nenhuma ação. Mitigação: exigir que a resposta final cite a observação que a sustenta.
*Erro conceitual comum:* tratar só o loop infinito, porque ele dói na fatura. A parada precoce é mais frequente e mais silenciosa: produz resposta plausível, sem evidência, e ninguém percebe sem olhar a trajetória — que é a tese da Aula 26.

**Conceito 12 — Estudo de caso: como um coding agent resolve uma issue real.**
O caso fecha a aula porque nele as cinco peças aparecem sem esforço de interpretação. **Objetivo:** o texto da issue. **Ferramentas:** buscar no repositório, ler arquivo, editar arquivo, rodar testes, rodar linter, abrir diff. **Loop:** localizar o código responsável, formar hipótese, editar, rodar o teste, ler a falha, editar de novo. **Memória de curto prazo:** os arquivos lidos e as saídas de teste da própria sessão. **Critério de parada:** a suíte de testes passa — e é aqui que está a lição. O coding agent funciona bem não porque o modelo é melhor em código, mas porque **existe verificador barato e automático**: o teste. Onde o verificador é caro ou não existe — mudança de UX, decisão de arquitetura, redação de política — o mesmo modelo com o mesmo loop rende muito menos. Esse contraste é o resumo executivo da aula e a razão de o SWE-bench (arXiv 2310.06770), que a Aula 26 revisita, ser o benchmark que mais se popularizou.
*Erro conceitual comum:* generalizar o sucesso do coding agent para qualquer domínio. O que transfere é a arquitetura; o que não transfere é o verificador.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura | Recap da Aula 22 (Lab 6: o loop de tool calling na mão, o servidor MCP próprio, Entrega 1 recolhida); o gancho — no Lab 6 a gente deu mãos ao modelo, hoje a gente dá um loop e um objetivo; a definição operacional apresentada como âncora da aula |
| 00:10 | 45 min | Bloco 1 — Do ciclo à memória | Ciclo observar → planejar → agir → refletir; ReAct (2210.03629) e a diferença entre padrão de interação e mecanismo de transporte; planejamento antecipado × emergente e decomposição verificável; memória de curto prazo como trajetória e seu custo crescente; memória de longo prazo e o critério de promoção; reflexão e autocorreção com e sem verificador |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — Quando usar, quanto custa, como quebra | Demonstração do loop de 40 linhas com as cinco peças apontadas na tela (13 min); agente × workflow determinístico pelos dois testes (caminho conhecido, verificador possível); custo e latência do loop e por que a conta é quadrática; orçamento de passos; paradas mal projetadas (loop infinito e parada precoce); estudo de caso do coding agent; exercício em dupla (6 min) |
| 01:50 | 10 min | Fechamento | A definição operacional pela terceira vez, agora como checklist de projeto; ponte para a Aula 24 (Sistemas multiagente e orquestração); leitura do ReAct com pergunta dirigida |

## 4. Demonstração guiada

**Demo "o loop em 40 linhas" — 13 min, `codigo/demo-loop-agente.py`, offline, sem dependências.**

O script roda em qualquer Python 3.9+ sem rede: o modelo é um simulador roteirado determinístico com semente fixa, e as ferramentas são locais. O objetivo não é mostrar um agente impressionante — é mostrar que o agente é pequeno, e que as cinco peças da definição são cinco trechos que o instrutor aponta com o cursor.

Passos em alto nível:

1. Abrir o arquivo e mostrar o tamanho: menos de uma tela e meia para o loop, o resto é ferramenta e simulador.
2. Apontar as cinco peças na ordem da definição: a função que chama o modelo, o dicionário `FERRAMENTAS`, o `while`, a constante `OBJETIVO` dentro do prompt de sistema, e a condição de `Final Answer` mais o `max_passos`.
3. Rodar `python demo-loop-agente.py --normal` com uma pergunta que exige duas ferramentas (buscar o prazo no regulamento e depois calcular uma data). A saída imprime cada volta rotulada: `[OBSERVAR]`, `[PLANEJAR]`, `[AGIR]`, `[REFLETIR]`.
4. Mostrar a trajetória crescendo: ao lado de cada passo, o script imprime o tamanho acumulado do prompt em tokens aproximados. O número sobe, e é aí que a conta quadrática do Conceito 10 fica visível sem fórmula.
5. Rodar `--sem-parada`, que remove a condição de `Final Answer` e mantém só o orçamento: o agente repete a mesma ação até o teto e para por esgotamento. Nomear o sintoma: mesma ação, mesmo argumento, duas vezes.
6. Rodar `--sem-orcamento`, que remove o teto e mantém um detector de repetição: mostrar que sem o detector aquilo seria um laço infinito com fatura.
7. Rodar `--parada-precoce`, em que o prompt de sistema permite responder direto: o agente emite `Final Answer` no passo 1, sem ação nenhuma, e a resposta é plausível e sem fundamento. Cravar o contraste com o caso anterior: o erro que dói na fatura é fácil de achar; este é o perigoso.
8. Fechar apontando a linha do orçamento e a linha da condição de parada, lado a lado, e voltando à definição operacional no slide.

**Número que a demo produz, e que a aula usa como evidência:** a **coluna de tokens acumulados por
passo** que o script imprime ao lado de cada volta do modo `--normal`. É esse número que o Conceito
10 usa como evidência — a coluna não sobe em degraus iguais, ela **acelera**, e é a conta quadrática
de **A.1** aparecendo antes da fórmula. Os outros três modos produzem um segundo resultado
observável, que é qualitativo e igualmente citado no fluxo: a **peça ausente** e o **sintoma** de
cada um (`--sem-parada` → mesma ação com mesmo argumento até o teto; `--sem-orcamento` → repetição
abortada por detector; `--parada-precoce` → `Final Answer` no passo 1, sem nenhuma ação). O slide 12
é apresentado a partir dessas saídas, e o slide 11 usa o `d` real que a demo imprimiu em vez de um
número inventado.

Insumos preparados na véspera: o script rodado nos quatro modos com as saídas salvas em texto, para o caso de o terminal falhar na projeção; o arquivo aberto num editor com fonte grande e os quatro trechos já marcados.

## 5. Hands-on

**Exercício em dupla — "agente ou pipeline?" (6 min, 01:44–01:50).**

Cinco cenários projetados. Para cada um, a dupla escreve duas letras e uma frase: **A** (agente) ou **P** (pipeline determinístico), o verificador que existe — ou a palavra "nenhum" — e uma frase de justificativa.

1. Converter 4.000 notas fiscais em PDF numa tabela com sete campos fixos, todos os PDFs com o mesmo layout.
2. Responder perguntas de alunos sobre o regulamento citando o dispositivo, sobre o acervo do Lab 5.
3. Corrigir um bug de teste vermelho num repositório com suíte de testes rápida.
4. Escrever a política de privacidade da empresa a partir de seis documentos internos.
5. Reconciliar duas planilhas de pagamento e listar as divergências, com regra de reconciliação já definida no manual.

Critério de conclusão observável: as cinco linhas preenchidas, e a dupla defende em voz alta um caso em que a resposta mudou depois de aplicar o segundo teste. Correção conduzida em 3 min, com foco em 1 (pipeline puro — layout fixo e caminho conhecido), 3 (agente com o melhor verificador possível) e 4 (parece complexo, não tem verificador, e é o caso em que agente entrega texto plausível sem apoio; se for agente, é com humano no loop, o que é Aula 26).

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Projeção do terminal ilegível** na demo | Turma pedindo para aumentar a fonte | Saídas dos quatro modos salvas em texto e projetadas num editor com fonte grande; a demo é sobre a estrutura da saída, não sobre executar ao vivo |
| **Python indisponível** na máquina da sala | Erro ao rodar o script | O script está impresso no anexo do roteiro e as saídas dos quatro modos estão salvas; a demo vira leitura de código com as cinco peças apontadas |
| **Turma confunde ReAct com tool calling** da Aula 21 | Pergunta "então isso é a mesma coisa da aula passada?" | Slide dedicado com a separação em duas camadas — padrão de interação × mecanismo de transporte — e o argumento decisivo: o Lab 7 faz ReAct em texto puro, sem a API de ferramentas |
| **Discussão sobre framework** dominando o Bloco 2 | Perguntas sobre LangGraph ou CrewAI antes do slide 13 | Resposta curta e agenda explícita: panorama de frameworks é a Aula 24 inteira, e a comparação com o loop na mão é o Checkpoint 5 do Lab 7 |
| **Debate "isso é AGI?"** consumindo tempo | Discussão sobre autonomia e consciência | Devolver à definição operacional: as cinco peças são engenharia verificável; a aula responde perguntas que têm critério de resposta |
| **Tempo estourar no Bloco 1** (memória gera muita pergunta) | 00:50 e ainda no Conceito 5 | Comprimir Conceito 7 (reflexão) para duas frases e levá-lo junto ao Conceito 11; a demo do Bloco 2 não pode ser cortada, porque é o que torna a definição concreta |
| **Exercício sem tempo** | 01:46 e o estudo de caso não terminou | O exercício vira a primeira pergunta da Aula 24, projetada na abertura; os cenários ficam no material |

## 7. Artefatos produzidos

- Anotação do exercício em dupla: tabela **cenário → agente/pipeline → verificador → justificativa** com cinco linhas, no repositório pessoal do aluno.
- O **checklist das cinco peças** copiado e aplicado ao projeto final da própria equipe, com uma linha por peça — é insumo direto da Entrega 2 (Aula 26).
- `codigo/demo-loop-agente.py`, que o aluno roda em casa nos quatro modos e usa como esqueleto mental do Lab 7.
- Nenhum entregável avaliado nesta aula.

## 8. Desafio pós-aula

Não avaliado. Três itens, na ordem:

1. **Rodar a demo nos quatro modos** e responder por escrito, em cinco linhas: qual das cinco peças da definição está ausente em cada modo com defeito, e qual sintoma isso produziu na saída.
2. **Aplicar o checklist ao próprio projeto.** Escrever as cinco peças do sistema da equipe — modelo, ferramentas, loop, objetivo, critério de parada — e responder aos dois testes do Conceito 9. Se a resposta ao segundo teste for "nenhum verificador", isso é um achado para levar à Entrega 2, não um problema para esconder.
3. **Leitura.** Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models* (arXiv 2210.03629). **Pergunta dirigida:** o artigo compara ReAct com raciocínio isolado e com ação isolada. Qual é o modo de falha que só aparece no raciocínio isolado, e por que a observação de uma ferramenta o elimina? A resposta é o argumento que o Lab 7 implementa.

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. Os pesos são os da ementa e não são reinventados: laboratórios 30% (o próximo é o Lab 7, na Aula 25), prova 30% (Aula 17, já realizada), projeto final 40% com os marcos das Aulas 22, 26 e 30.

O que esta aula alimenta, com peso já definido em outro lugar:

- **Lab 7 (Aula 25) — dentro dos 30% dos laboratórios.** A definição operacional é o que o lab implementa peça por peça; o critério de parada e o limite de passos são itens explícitos da nota do lab.
- **Entrega 2 do projeto (Aula 26) — 5% da nota final.** O checklist das cinco peças e a resposta aos dois testes do Conceito 9 entram na justificativa de arquitetura que o checkpoint cobra: por que este sistema é agente, ou por que ele deliberadamente não é.

Observável em sala, sem nota: ao ser questionado no fechamento, o aluno enuncia as cinco peças sem consultar o slide e aponta, para um cenário dado pelo instrutor, se existe verificador para o passo intermediário.
