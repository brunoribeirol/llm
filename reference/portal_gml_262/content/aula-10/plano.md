---
aula: 10
titulo: "Do Transformer ao LLM: escala, MoE, decodificação e prompting"
modulo: "2 — Do Transformer ao LLM: escala e inferência"
tipo: teorica
semana: 5
duracao_min: 120
versao: v2
---

# Aula 10 — Do Transformer ao LLM: escala, MoE, decodificação e prompting

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** Esta é a aula mais densa do curso e a que cobre mais assuntos. A V2 a
> organiza em torno de **quatro chamados de suporte** — quatro defeitos reais, nenhum deles nos
> pesos do modelo — e cada bloco da aula fecha um deles pela causa. O fundamento matemático
> aparece enunciado e lido no fluxo, com a derivação completa no apêndice do deck (Parte 2 de
> `instructions-slides.md`, itens A.1 a A.6). O índice do apêndice está ao fim deste plano.
> Carga horária, numeração e objetivos de aprendizagem inalterados.

## 1. Objetivo da aula

Fechar a distância entre "eu sei como um Transformer funciona" e "eu sei por que este LLM em produção está se comportando assim". A aula mostra que um modelo em serviço é **pesos mais decisões** — de arquitetura de capacidade, de decodificação, de contexto e de serving — e que a maior parte dos defeitos que chegam ao suporte vive nas decisões, não nos pesos.

## 2. Resultados de aprendizagem

Ao final desta aula o estudante deve ser capaz de:

1. Distinguir parâmetros **totais** de parâmetros **ativos por token** num modelo Mixture of Experts, e explicar por que os dois números divergem.
2. Reconhecer o **colapso de roteamento** pelo sintoma observável e nomear o mecanismo que o previne.
3. Prever, dada uma distribuição de próximo token, quais candidatos sobrevivem a `top-k` e a `top-p`, e o que a temperatura faz com essa distribuição.
4. Justificar por que o beam search encontra a sequência de maior probabilidade conjunta e ainda assim produz respostas curtas e genéricas.
5. Diagnosticar, a partir de um comportamento relatado, **qual parâmetro de decodificação** foi mal escolhido — e dizer que medição confirmaria o diagnóstico.
6. Explicar por que uma janela de contexto grande não é memória confiável, e nomear os três gargalos de serving (memória do cache, banda, ocupação) com a resposta técnica de cada um.

*(Idênticos aos da V1 — a reorganização não muda o que o estudante deve saber fazer.)*

## 3. Teoria aplicada

A aula abre pelos **quatro chamados**, projetados juntos no slide 1, e volta a cada um no momento em que o conteúdo o resolve. Nenhum dos quatro é bug de implementação; todos são consequência correta de uma decisão.

| # | O chamado, como chega | Onde fecha | Causa nomeada |
|---|---|---|---|
| 1 | "A mesma configuração que funciona num prompt vira lixo em outro" | Slide 10 | `top-p` e temperatura não são controles independentes |
| 2 | "O modelo repete a mesma frase para sempre" | Slide 8 | decodificação determinística sobre uma distribuição concentrada |
| 3 | "Esse modelo tem 47B de parâmetros mas custa como um de 13B" | Slides 2 e 5 | ativação esparsa: totais ≠ ativos por token |
| 4 | "O documento cabe na janela e o modelo ignora o meio" | Slide 14 | contexto longo não é memória; há sensibilidade posicional |

### Bloco 1 (00:10–00:55) — Capacidade: o que torna um LLM "grande"

**O orçamento em uma linha.** Parâmetros, tokens de treino e FLOPs como três eixos de um mesmo orçamento, com `C ≈ 6ND` **enunciada e lida** — o que ela afirma, e por que ela é a restrição que decide arquitetura. A derivação do fator 6 é da Aula 12, de propósito: aqui ela é a ferramenta que motiva o MoE, lá é o objeto.

**MoE como a peça trocada.** Roteamento top-k sobre `E` especialistas; capacidade esparsa; a diferença entre parâmetros totais e ativos por token, que é exatamente o chamado 3. O erro conceitual característico da turma é ler MoE como "modelo menor": ele tem *mais* parâmetros e ativa *menos* por token — a memória cobra o total, a aritmética cobra o ativo.

**O defeito característico: ninguém supervisiona o roteador.** O roteador é treinado por gradiente da tarefa, e nada na perda principal exige que ele distribua carga. Daí o colapso, e daí a perda auxiliar de balanceamento. Este é o coração do Bloco 1 e não se corta em nenhuma hipótese.

- **Fundamento:** o roteamento top-k e `L_aux = α·E·Σ f_i·P_i`, que vale 1 no equilíbrio e `E` no colapso.
  → derivação completa: **Apêndice A.4** (slide 20)

### Bloco 2 (01:05–01:50) — Decisões: quem escolhe o token

**O modelo não escolhe o token; o algoritmo de decodificação escolhe.** Greedy e a repetição infinita (chamado 2). Beam search fazendo corretamente o trabalho errado — encontra a sequência de maior probabilidade conjunta, que é a curta e genérica, porque probabilidade conjunta penaliza comprimento. Amostragem, e o par reprodutibilidade/diversidade como uma escolha vista de dois lados.

- **Fundamento:** o escore de sequência como produto de condicionais, o viés por comprimento e a normalização que o corrige.
  → derivação completa: **Apêndice A.3** (slide 19)

**Temperatura, top-k e top-p.** Temperatura dentro do softmax: muda o quanto o mais provável é mais provável, **não** a ordem dos candidatos. Truncamento por contagem (`k`) e por massa (`p`), ambos seguidos de renormalização — truncar não é só cortar, é redistribuir. E o ponto que fecha o chamado 1: numa distribuição achatada é preciso somar **mais** tokens para acumular a mesma massa, então o nucleus **cresce** quando a temperatura sobe. Os dois parâmetros interagem.

- **Fundamento:** a temperatura dentro do softmax, com os limites `T → 0` e `T → ∞`.
  → derivação completa: **Apêndice A.1** (slide 17)
- **Fundamento:** top-k e top-p como truncamento e renormalização, com o conjunto crescendo em `T` alto.
  → derivação completa: **Apêndice A.2** (slide 18)

**Prompting e aprendizado em contexto.** Zero-shot, few-shot; chain-of-thought em visão inicial (a Aula 16 aprofunda). O comportamento muda sem que nenhum peso mude — que é a tese da segunda metade da aula.

**Contexto e serving.** Janela longa não é memória confiável: needle-in-a-haystack e sensibilidade posicional (chamado 4). Os três gargalos de serving e a resposta de cada um: memória do KV cache → GQA e paged attention; banda → decodificação especulativa; ocupação → batching contínuo.

- **Fundamento:** `2 · L · H_kv · d_h · b` por token, e o ponto em que o cache empata com os pesos.
  → derivação completa: **Apêndice A.6** (slide 22)
- **Fundamento:** a verificação da especulativa como amostragem por rejeição que preserva a distribuição.
  → derivação completa: **Apêndice A.5** (slide 21)

### Grade temporal

| Início | Dur. | Bloco | Subtemas |
|---|---|---|---|
| 00:00 | 10 min | Abertura | Recap da Aula 9 (mini-GPT) + os quatro chamados projetados juntos |
| 00:10 | 45 min | Bloco 1 — Capacidade | O orçamento (`C ≈ 6ND`) · a restrição que virou arquitetura · MoE e o chamado 3 · colapso de roteamento e a perda auxiliar |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — Decisões | Greedy e o chamado 2 · beam search e o alvo errado · temperatura, `top-k`, `top-p` e o chamado 1 · exercício em dupla · demo · prompting · contexto longo e o chamado 4 · serving |
| 01:50 | 10 min | Fechamento | Os quatro chamados fechados pela causa · um item de apêndice apontado por nome · mapa do Lab 3 · leituras |

**Corte previsto.** Esta aula tem menos folga que qualquer outra do curso. Se atrasar, o slide 15 (serving) migra para os primeiros 30 minutos do Lab 3 — a ementa autoriza explicitamente. Depois dele, o slide 13 (prompting), que o Lab 3 refaz na prática. **Não se cortam** o slide 6 (colapso do roteador) nem o exercício do slide 11: o primeiro é o núcleo do Bloco 1, o segundo é o único momento em que a turma decide em vez de assistir.

## 4. Demonstração guiada

Sete minutos, `codigo/demo-decodificacao.py` — Python puro, sem rede, sem GPU, sem quota de API. A escolha é deliberada: a aula é longa demais para gastar três minutos em rate limit, e a matemática de decodificação não precisa de um modelo de verdade para ser vista — precisa de uma distribuição e de um terminal.

Sete passos: a distribuição de dez candidatos com histograma ASCII; quatro temperaturas lado a lado; `top-k = 3` com a renormalização explícita; **`top-p = 0,9` nas duas distribuições** (o passo insubstituível); busca gulosa × feixe sobre a árvore do slide 8; cinco amostragens contra cinco decodificações gulosas; e as quatro constantes no topo do arquivo, que são as quatro alavancas do Lab 3.

**Número que a demo produz.** Dois, e os dois voltam ao fluxo. O terceiro colocado sai de `0,15` para `0,21` após a renormalização do `top-k = 3` — **41% mais provável sem que nada mude no modelo**, citado de volta no slide 11 e derivado em A.2. E o tamanho do nucleus a `p = 0,9`: **6 tokens em `T = 1`, 8 em `T = 2`, 3 em `T = 0,5`** — que é a resposta medida do terceiro chamado do exercício e a evidência de que os dois parâmetros interagem.

**Contingência:** se o terminal do projetor falhar, projetar a saída salva na véspera (prevista como `.txt` ao lado do script). Sem ela, os passos 2 e 4 são reproduzíveis no quadro com quatro números à mão e são os dois insubstituíveis.

## 5. Hands-on

Cinco minutos em dupla, três de correção, dentro do slide 11.

O exercício da V1 era **calcular o nucleus à mão**; na V2 ele virou extensão opcional e o obrigatório passou a ser **decisão**: três chamados novos e, para cada um, qual parâmetro se mexe e **que medição confirmaria** o diagnóstico. A segunda parte é a que vale.

| # | O chamado | Configuração atual |
|---|---|---|
| 1 | Resumidor devolve texto correto e chatíssimo, sempre a mesma estrutura de frase | `T = 0,3`, `top_p = 1,0` |
| 2 | Gerador de descrições acerta 9 de 10 e na décima inventa um atributo inexistente | `T = 1,3`, `top_p = 1,0` |
| 3 | Time subiu `T` de 1,0 para 2,0 e o `top_p = 0,9` "parou de cortar" | ninguém mexeu no `top_p` |

**Como recolher:** começar pelo terceiro, não pelo primeiro. Chamar uma dupla que respondeu "cresce" e uma que respondeu "encolhe", trinta segundos cada, e só então dar o número da demo. O erro comum — responder "encolhe" — vem de associar temperatura alta a mais aleatoriedade e portanto a mais corte; é o raciocínio invertido, e é onde a dupla aprende.

**Extensão opcional:** refazer a conta do nucleus à mão seguindo A.2, em `T = 1` e `T = 2`. Gabarito completo no apêndice.

## 6. Riscos e contingências

| Risco | Plano B |
|---|---|
| **Tempo** — é a aula mais densa do curso e a mais provável de estourar | Ordem de corte definida: slide 15 (serving) → Lab 3; depois slide 13 (prompting). Nunca o slide 6 nem o exercício. |
| Python indisponível na máquina da sala / terminal do projetor falha | Saída salva em `.txt` ao lado do script; em último caso, passos 2 e 4 no quadro com quatro números |
| A turma confunde MoE com "modelo menor" | Cravar a distinção em números: *mais* parâmetros totais, *menos* ativos por token; a memória cobra um, a aritmética cobra o outro |
| A turma responde "o nucleus encolhe" e não se convence pelo argumento verbal | Não discutir: dar o número da demo (6 → 8 → 3). É o único jeito de desfazer o raciocínio invertido |
| Pergunta sobre a derivação do fator 6 do `C ≈ 6ND` | Resposta curta preparada (Parte 4, item 1, ~4 min); a derivação é da Aula 12 de propósito |
| Quatro assuntos numa aula viram lista sem fio condutor | Os quatro chamados são o fio: cada bloco fecha um, e o slide 16 fecha os quatro pela causa |

## 7. Artefatos produzidos

- `codigo/demo-decodificacao.py` — script da demo, com as quatro constantes de configuração no topo. É o ponto de partida do Lab 3.
- A saída `.txt` da demo, gravada na véspera, como contingência de projeção.
- As respostas do exercício de diagnóstico, recolhidas em aula (não avaliadas).

## 8. Desafio pós-aula

Duas leituras com pergunta dirigida:

- **Brown et al., *Language Models are Few-Shot Learners* (arXiv 2005.14165).** Pergunta: o artigo mede desempenho em função do número de exemplos no prompt. Onde a curva satura, e o que a saturação sugere sobre o que o few-shot está de fato fazendo?
- **Fedus et al., *Switch Transformers* (arXiv 2101.03961).** Pergunta: o artigo relata instabilidade de treino e as medidas tomadas contra ela. Qual delas atua sobre o mesmo problema que a perda auxiliar de balanceamento, e qual atua sobre outro?

Checklist de setup para o Lab 3: chave de API do provedor com free tier configurada por variável de ambiente, Ollama instalado com um modelo pequeno baixado, e o `demo-decodificacao.py` rodando localmente.

## 9. Critérios de avaliação

Esta aula não tem entregável avaliado — a prática da unidade é recolhida no **Lab 3 (Aula 11)**, que compõe os 30% de laboratórios da ementa.

O conteúdo desta aula é cobrado na **prova da Aula 17**, cuja composição é: diagnóstico e interpretação de comportamento **42** · justificativa de escolha **40** · conceito aplicado **8** · derivação **10**. O exercício do slide 11 é deliberadamente do formato das questões de diagnóstico: sintoma relatado, parâmetro a identificar, medição que confirma. Os quatro chamados da abertura são material de questão de prova, e a turma sabe disso desde o slide 1.

## Apêndice matemático — índice

Seis itens, slides 17 a 22 do deck. Material de estudo e consulta, autossuficiente.

| Item | O que estabelece | Apontado do |
|---|---|---|
| **A.1** | A temperatura dentro do softmax: a família de distribuições `p_i(T)`, a monotonicidade da entropia em `T`, e os limites `T → 0` (argmax) e `T → ∞` (uniforme). Por que a ordem dos candidatos é invariante. | slide 10 |
| **A.2** | Top-k e top-p como truncamento seguido de renormalização. O exemplo numérico resolvido com dez candidatos, o ganho de 41% do terceiro colocado, e a demonstração de que o nucleus **cresce** com `T` — 6, 8 e 3 tokens em `T = 1`, `2` e `0,5`. | slides 10 e 11 |
| **A.3** | O escore de sequência como produto de condicionais; por que a sequência das escolhas mais prováveis não é a sequência mais provável (a árvore do slide 8, `0,30` contra `0,36`); o viés por comprimento (`0,7⁵` contra `0,9²⁰`) e a normalização que o corrige. | slide 9 |
| **A.4** | Roteamento top-k sobre `E` especialistas; a contagem de parâmetros totais contra ativos por token; `L_aux = α·E·Σ f_i·P_i` com os dois casos-limite trabalhados — **1 no equilíbrio, `E` no colapso**. | slides 5 e 6 |
| **A.5** | A aritmética da decodificação especulativa: a razão de aceitação esperada, e a prova de três linhas de que a verificação preserva a distribuição do modelo grande — `min(p,q) + max(0, p−q) = p`. | slide 15 |
| **A.6** | A conta do KV cache em regime de serviço: `2 · L · H_kv · d_h · b` por token, instanciada; o fator exato de redução de MQA e GQA; e o ponto em que o cache empata com os pesos. | slide 15 |

**Nota de fronteira.** A derivação do fator 6 de `C ≈ 6ND` **não** está neste apêndice: ela é da Aula 12, onde as leis de escala são o objeto e não a ferramenta. Aqui a fórmula é enunciada, lida e usada para motivar o MoE. A Parte 4 do roteiro traz a resposta de quatro minutos para quando a turma perguntar em aula.
