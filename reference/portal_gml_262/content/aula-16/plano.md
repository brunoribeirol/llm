---
aula: 16
titulo: "Modelos de raciocínio: GRPO e DeepSeek-R1"
modulo: "4 — Alinhamento e Raciocínio"
tipo: teorica
semana: 8
duracao_min: 120
versao: v2
---

# Aula 16 — Modelos de raciocínio: GRPO e DeepSeek-R1

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos versionáveis
> (medição, tabela de verificadores, roteiro de estudo anotado), não conversas descartáveis com um
> chatbot. O roteiro de fala vive em `roteiro.md`; a especificação dos slides em
> `instructions-slides.md`.

> **Rebalanceamento V2.** O fluxo da aula é conduzido por quatro comportamentos observáveis — o
> modelo que acerta com dez tentativas e erra com uma, a conta de API que triplica sem ganho, a
> cadeia bonita que leva à resposta errada, e a cadeia que cresce sem acertar mais. A matemática
> entra como fundamento nomeado, com a derivação completa no apêndice do deck (itens A.1 a A.5), e
> lá está mais completa do que na V1: o estimador de `pass@k` ganhou a derivação combinatória e a
> prova de variância; a vantagem do GRPO ganhou a demonstração de que dispensa a rede de valor. Os
> objetivos de aprendizagem, a carga horária e a numeração permanecem os da V1.

## 1. Objetivo da aula

Mostrar que "raciocínio" em LLM é, operacionalmente, **gastar computação em passos intermediários
antes de responder**; que essa capacidade se treina sem anotador humano sempre que a tarefa tem
verificador automático; e — o que a V2 acrescenta como eixo — tornar o aluno capaz de **ler os
números que decidem produto**: a distância entre `pass@k` e `consensus@k`, a saturação de uma
temperatura baixa, e a curva de comprimento que sobe sem a de acerto acompanhar.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Enunciar** a definição operacional de raciocínio usada no curso e **apontar** por que ela não é
   uma definição científica assentada.
2. **Quantificar** o custo de um modelo de raciocínio em três eixos — latência, preço por resposta e
   contexto consumido — e **decidir** quando ele não se justifica.
3. **Interpretar** `pass@k` a partir do estimador enunciado, **distinguir** o que ele mede do que
   `consensus@k` mede, e **usar** a distância entre os dois como argumento de decisão (derivação em
   A.1 e A.2).
4. **Explicar** o que torna uma recompensa verificável, **classificar** tarefas entre as que admitem
   verificador automático e as que não admitem, e **nomear o que o verificador não confere**.
5. **Descrever** o GRPO como vantagem relativa ao grupo de completações e **justificar** por que ele
   dispensa a função de valor aprendida do PPO (demonstração em A.3).
6. **Reconstituir** as quatro etapas do pipeline DeepSeek-R1 e **explicar** que problema cada etapa
   resolve da anterior.
7. **Diagnosticar** o crescimento de comprimento como efeito colateral do objetivo de RL, **dizer
   por onde ele entra** (o gradiente, não a recompensa) e **citar** as duas mitigações vistas
   (normalização de comprimento, budget forcing) — incluindo o viés que a primeira introduz (A.5).

*(Idênticos aos da V1. O que mudou foi o verbo dominante nos itens 3, 4 e 7: de "calcular",
"classificar" e "identificar" para "interpretar, usar como argumento, nomear o que fica de fora e
diagnosticar" — a conta permanece disponível no apêndice e é cobrada como fundamento da
justificativa.)*

## 3. Teoria aplicada

Cada conceito abaixo é apresentado pelo comportamento que o motiva, com o fundamento matemático
nomeado e a derivação remetida ao apêndice.

### Bloco 1 (00:10–00:55) — Do sintoma à medição

**Conceito 1 — Os sintomas de abertura, e a decisão de produto que forçam.**
*Comportamento observável:* (a) o modelo resolve com dez tentativas e erra com uma — e o usuário
recebe uma; (b) um time liga o modo de raciocínio no produto inteiro, a conta de API **triplica** e
a métrica da tarefa fácil não se move.
*Ponte com a Aula 15:* lá o sinal de treino vinha de gente, com 70% de concordância; aqui ele vem de
um programa, e o custo marginal de pontuar uma tentativa cai a zero.
*Nota de condução:* não nomear `pass@k` neste ponto. O nome chega no Conceito 5, depois de a turma
sentir a falta dele.

**Conceito 2 — Por que "amostra mais" não é resposta.**
*Comportamento observável:* sem um jeito de conferir, "uma dessas dez resolve o seu problema" não é
entregável; e o voto majoritário falha exatamente quando o erro é consistente, porque mais amostras
dão mais votos ao candidato errado.
*Erro conceitual comum:* tratar amostragem como melhoria de qualidade. Ela melhora o que o modelo
**pode** fazer; não necessariamente o que ele **entrega**.

**Conceito 3 — A definição operacional, e sua honestidade.**
`vanilla: prompt → resposta` contra `raciocínio: prompt → cadeia intermediária → resposta`. É
definição de engenharia — mensurável, útil para decidir arquitetura — e **não** afirmação sobre
cognição.
*Terceiro sintoma da aula:* a cadeia bonita que leva à resposta errada (e o inverso). A cadeia
exibida é texto gerado sob a mesma distribuição de tudo o mais; pode ser post-hoc, pode contradizer
a resposta final.
*Erro conceitual comum:* tratar a cadeia como registro fiel do processo interno. Medir a fidelidade
dela é problema aberto e reaparece na Aula 27.

**Conceito 4 — A fatura em três eixos.**
*Comportamento observável, decomposto:* **latência** (a resposta só começa depois da cadeia),
**preço** (token de raciocínio custa como qualquer outro e costuma ser a maior parte da conta) e
**contexto** (a cadeia ocupa janela que poderia ser documento recuperado — colide com RAG na Aula
18).
*Corolário de projeto:* raciocínio é alavanca para tarefa difícil e verificável, não configuração
global do produto.
*Erro conceitual comum:* concluir que "modelo de raciocínio é melhor". Em tarefa fácil é mais caro,
mais lento e às vezes pior.

**Conceito 5 — O fundamento nomeado: `pass@k`.**
`pass@k = 1 − C(n − c, k) / C(n, k)`, **enunciada e lida** termo a termo, nunca manipulada em aula.
Os extremos confirmam a leitura: `c = 0 → 0`; `c = n → 1`; `k = 1 → c/n`.
*Condição de uso:* `pass@k` só é acionável com verificador — sem ele, sabe-se que uma das `k` está
certa e não qual.
*Fundamento:* o estimador é não-viesado (esperança `1 − (1−p)^k`) e tem variância **menor** que a do
estimador ingênuo de rodar `k` amostras, por Rao-Blackwell. → **A.1**
*Erro conceitual comum:* comparar `pass@10` de um sistema com `pass@1` de outro. `pass@k` mede o que
o modelo pode fazer; `pass@1` mede o que ele entrega.

**Conceito 6 — `consensus@k` e o valor do verificador.**
Sem verificador resta o voto majoritário; `consensus@k` é a taxa de acerto desse voto, e é sempre
`≤ pass@k` porque a resposta certa pode estar entre as `k` sem ser a maioria. A distância entre as
curvas é literalmente o valor de ter um verificador.
*Fundamento:* a desigualdade sai por inclusão de eventos em uma linha; e o limite `k → ∞` mostra que
`consensus@k` converge para "a moda está certa" enquanto `pass@k` converge para "a resposta certa
está no suporte". → **A.2**
*Erro conceitual comum:* achar que mais amostras sempre melhoram o consenso. Se a moda errada é
firme, amostrar mais reforça o erro — e é isso que o problema `servidor` da demo mostra medido.

### Bloco 2 (01:05–01:50) — Treinar contra um programa

**Conceito 7 — Recompensa verificável: o professor automático.**
`1` se a resposta bate com o gabarito, `0` se não. Sem anotador, sem modelo de recompensa aprendido,
sem viés de anotação e — o que importa para escala — **sem custo marginal por amostra**. Some-se a
**recompensa de formato** (`<think>…</think>`), que torna a saída parseável e portanto verificável de
forma estável.
*Erro conceitual comum:* supor que verificável significa fácil. O verificador define exatamente o
que será otimizado; verificador fraco produz reward hacking — é o risco da Aula 15 em roupa nova. Um
teste unitário incompleto ensina o modelo a passar no teste, não a resolver o problema.

**Conceito 8 — GRPO: a linha de base sai do próprio grupo.**
Amostrar `G` completações do **mesmo** prompt, pontuar todas, e usar a média do grupo como linha de
base: `Aᵢ = (rᵢ − média(r)) / desvio(r)`. Mantém o clipping do PPO e a penalidade KL contra a
referência; tira um modelo inteiro da pilha de treino (Shao et al., arXiv 2402.03300).
*Fundamento 1:* trocar a rede de valor por uma média amostral é legítimo porque **qualquer** linha
de base que dependa só do prompt deixa o gradiente de política sem viés — ela só muda a variância.
→ **A.3**
*Fundamento 2:* com recompensa binária e `p̂` de acertos no grupo, a vantagem tem forma fechada
(`+√((1−p̂)/p̂)` para a correta, `−√(p̂/(1−p̂))` para a errada) — e é dela que sai a leitura de por
que a divisão pelo desvio concentra o gradiente no evento informativo. → **A.4**
*Erro conceitual comum:* achar que GRPO substitui o PPO em tudo. Ele resolve o caso "muitas amostras
do mesmo prompt, com pontuação barata".

**Conceito 9 — GRPO × PPO, e o que isso custa.**
O PPO **aprende** a linha de base; o GRPO a **calcula** por amostragem. Troca-se memória de treino
por computação de inferência — excelente quando gerar é barato e pontuar é um programa; péssimo
quando cada geração é uma chamada paga.
*Fundamento:* com `G = 1` a vantagem é identicamente zero, e um grupo homogêneo (todas certas ou
todas erradas) não produz gradiente nenhum — computação gasta sem sinal. → **A.3**

**Conceito 10 — O pipeline DeepSeek-R1, etapa a etapa.**
O artigo (arXiv 2501.12948) descreve o caminho **e os problemas de cada etapa**.
1. **R1-Zero** — RL puro sobre o base, sem SFT, com recompensa verificável e de formato. Raciocínio
   **emerge**: o modelo revisa a própria conta, volta atrás, gasta mais tokens em problema difícil.
   *Problemas: mistura de idiomas, legibilidade ruim.*
2. **Cold-start SFT** — conjunto pequeno de cadeias bem escritas. *Conserta formato e idioma.*
3. **RL em larga escala** — dados de raciocínio e de não-raciocínio misturados. *Impede que vire só
   um resolvedor de olimpíada.*
4. **Destilação** — saídas do modelo grande viram SFT de modelos densos menores. *Herda o
   comportamento a uma fração do custo de servir.*
*Erro conceitual comum:* ler a primeira etapa como o método final. Ela prova que emerge e entrega um
modelo desagradável de usar; as três seguintes existem para consertar o que ela quebrou.

**Conceito 11 — A cadeia que cresce sem acertar mais.**
*Comportamento observável:* ao longo do RL o comprimento médio sobe **e a taxa de acerto achata**.
*Onde o comprimento entra:* não na recompensa — uma resposta certa em 40 tokens e uma em 4.000
recebem a mesma nota —, mas no **gradiente**, porque a contribuição de uma completação é uma soma
sobre os tokens dela.
*Fundamento:* o efeito do fator `|o|` sobre a magnitude do gradiente, e o viés que a normalização
por `1/|o|` introduz (errar longo custa menos por token). → **A.5**
*Mitigações:* normalização de comprimento na vantagem — preferencialmente por uma constante, não
pelo comprimento da amostra — e budget forcing na inferência, que atua sobre a fatura do Conceito 4
e não sobre o treino.
*Erro conceitual comum:* interpretar cadeia mais longa como raciocínio melhor.

**Conceito 12 — O critério que fecha o módulo.**
**Existe verificador para a sua tarefa?** Se existe (código com teste, extração com schema, cálculo
com gabarito), há caminho barato de melhoria — Best-of-N com verificador, e RL se houver orçamento.
Se não existe, o caminho é preferência humana (Aula 15) ou juiz calibrado (Aula 27), ambos mais
caros e mais ruidosos. A pergunta vale para o projeto final, lançado na Aula 18.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas |
|---|---|---|---|
| 00:00 | 10 min | Abertura pelos sintomas | Acerta com dez e erra com uma; a conta que triplica sem ganho; a virada da Aula 15 para o sinal que sai de um programa; **anúncio do espaço reservado à prova** |
| 00:10 | 45 min | Bloco 1 — do sintoma à medição | Por que "amostra mais" não é resposta (5) · definição operacional e a cadeia que engana (6) · a fatura em três eixos (6) · onde há gabarito automático (5) · `pass@k` enunciado e lido (7) · `consensus@k` e o valor do verificador (6) · **demo com os números medidos (10 min)** |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — treinar contra um programa | Recompensa verificável e recompensa de formato (7) · GRPO e a linha de base do grupo (9) · GRPO × PPO lado a lado (6) · o pipeline R1 em quatro etapas (7) · a cadeia que cresce sem acertar mais (4) · **exercício "quem tem verificador, e o que ele não confere" (12 min)** |
| 01:50 | 10 min | Fechamento | O critério "existe verificador?" como fecho do Módulo 4 (5) · **aviso da Prova da Aula 17, com o novo perfil de pontuação e a orientação de estudo (5)** |

*Comparação com a V1: os minutos que a V1 gastava enunciando fórmula sem consequência foram para a
demo (de 8 para 10 min) e para o exercício (de 9 para 12 min), que ganhou uma coluna nova e uma
pergunta de decisão de produto. A abertura deixou de ser recap da Aula 15 e passou a ser sintoma
medido. A matemática que saiu do fluxo está em A.1–A.5, com duas demonstrações que a V1 não tinha —
o não-viés e a variância do estimador de `pass@k`, e a invariância da linha de base.*

## 4. Demonstração guiada

**Demo "pass@k contra temperatura" — 10 min (00:45–00:55), `codigo/demo-pass-at-k.py`.**

O script tem duas rotas. A rota `--offline` (padrão) usa um amostrador sintético determinístico com
semente fixa: não depende de rede, não usa chave de API e produz exatamente a mesma tabela toda vez
— é a rota da aula. A rota `--api` chama um modelo real num provedor com free tier compatível com a
OpenAI, com a chave vinda de variável de ambiente ou de `getpass`, nunca de arquivo.

São cinco problemas de aritmética de várias etapas, escritos para esta aula no estilo do GSM8K (não
são itens do GSM8K), cada um com a resposta correta e três distratores plausíveis. O amostrador
sintético **não resolve** os problemas: ele simula a distribuição de saídas de um modelo pequeno. Em
três dos cinco o argmax do modelo simulado está correto; nos outros dois está errado, e a resposta
certa só aparece quando a amostragem se afasta do argmax. É essa assimetria que produz o trade-off.

Na V2 a demo deixa de ilustrar a fórmula e passa a ser **a evidência que o fluxo usa**: os números
abaixo aparecem no slide 8, voltam no exercício como pergunta de decisão de produto, e voltam no
fechamento.

1. Rodar `python demo-pass-at-k.py --offline` e mostrar a listagem por problema em cada temperatura:
   quantas das 10 amostras acertaram, qual foi a moda, qual era o gabarito.
2. Ler a linha do problema `servidor` em T = 0,2: **0 acertos em 10**, moda 750, gabarito 1050. O
   modelo erra de forma consistente — a moda errada é firme. É o Conceito 2 medido.
3. Ler o mesmo problema em T = 1,2: **4 acertos em 10**, e a moda passou a ser 1050. A diversidade
   encontrou o que a temperatura baixa nunca alcançava, e a resposta certa virou argmax — que é a
   condição de A.2 para o consenso também acertar.
4. Abrir a tabela de `pass@k` e ler as duas pontas: em `pass@1` a melhor temperatura é **0,2**
   (**0,540** contra **0,440**); em `pass@10` a melhor é **1,2** (**1,000** contra **0,600**). A
   temperatura que vence depende inteiramente do orçamento de tentativas.
5. Apontar que T = 0,2 **satura** em **0,600** e não passa disso por mais amostras que se dê: dois
   dos cinco problemas são inalcançáveis naquela temperatura. É o limite de A.2 — `pass@k` só
   converge para 1 se a resposta certa tiver probabilidade positiva.
6. Abrir a tabela de `consensus@k` e comparar na mesma temperatura 1,2: `pass@10` = **1,000** contra
   `consensus@10` = **0,800**. **Vinte pontos** é o que o verificador compra naquele conjunto — e é
   o número que volta como pergunta de decisão no hands-on.
7. Fechar no gráfico salvo (`pass-at-k-vs-temperatura.png`), com os dois painéis lado a lado, e na
   frase que o próprio script imprime: `pass@k` mede o que o modelo **pode** fazer; `consensus@k`
   mede o que ele **entrega** sem verificador.

Insumos preparados: o script rodado na véspera com a saída salva em texto e o PNG já gerado, para o
caso de o Python da sala não subir. Os passos 6 e 7 **não se cortam** — são os dois números que o
exercício e o fechamento usam.

## 5. Hands-on

**Componente prático da unidade — "quem tem verificador, e o que ele não confere" (7 min de dupla +
5 de correção, 01:38–01:50).**

Seis tarefas projetadas. Para cada uma, a dupla escreve: (a) existe verificador automático? (b) se
existe, qual é ele em uma frase, nomeando a coisa que roda; (c) **o que ele não confere** — a
superfície de reward hacking que ele deixa aberta; (d) se não existe, qual seria o sinal de treino
alternativo — preferência humana (Aula 15) ou juiz calibrado (Aula 27). A coluna (c) é a novidade da
V2 e é a que produz o artefato.

1. Resolver equação do segundo grau e devolver as raízes.
2. Corrigir um bug num repositório de forma que a suíte de testes passe.
3. Escrever um e-mail de desculpas a um cliente insatisfeito.
4. Extrair de uma nota fiscal um JSON com CNPJ, valor e data, obedecendo a um schema.
5. Resumir um artigo científico em um parágrafo.
6. Traduzir uma função de Python para Rust preservando o comportamento.

**Pergunta de decisão, ao fim das seis:** com `pass@10 = 1,000` e `consensus@10 = 0,800` medidos na
demo de hoje, o que a dupla entrega ao usuário — e o que muda nessa resposta se não houver
verificador em produção?

*Resultado esperado:* 1, 2, 4 e 6 têm verificador (comparação simbólica; suíte de testes; validação
de schema mais conferência dos campos; testes de equivalência nas duas linguagens). 3 e 5 não têm —
dependem de preferência ou juiz. Na coluna (c): o caso 1 não confere raízes complexas nem ordem se a
comparação for textual; o caso 2 não confere regressão fora da suíte; o caso 4 não confere se o CNPJ
bem formatado é o CNPJ **certo**; e o caso 6 é o mais rico da lista — o verificador **existe** e é
**parcial**: testes cobrem o comportamento observado, não a equivalência semântica completa, e
otimizar contra ele é o convite direto ao reward hacking do Conceito 7. Na pergunta de decisão: com
verificador, entrega-se a correta e a taxa é 1,000; sem verificador, entrega-se a mais votada e a
taxa cai para 0,800.

*Critério de conclusão observável:* a dupla classifica as seis, nomeia o verificador nos casos em
que há, **escreve pelo menos uma coisa que cada verificador não confere**, e defende em voz alta por
que o caso 6 é mais frágil do que parece. Classificar sem preencher a coluna (c) não fecha o
exercício.

*Extensão para quem terminar antes (opcional):* propor um verificador **parcial** para o caso 3 ou
5 (por exemplo, checagem de que o e-mail cita o número do pedido; checagem de que o resumo menciona
o método e o resultado) e dizer o que ele otimizaria e o que ele deixaria escapar.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Python indisponível na máquina da sala** | O script não roda | Saída da véspera em texto e PNG do gráfico já existem; a demo vira leitura de tabela, que é onde está o valor pedagógico. Os passos 6 e 7 são os que **não** se cortam |
| **Turma achar que a demo mede um modelo real** | Pergunta "que modelo é esse?" | Ser explícito: a rota `--offline` é um **amostrador sintético** que simula a distribuição de um modelo pequeno; ele não resolve os problemas. A rota `--api` chama modelo real e fica como extensão pós-aula. Não deixar a ambiguidade passar — a demo perde autoridade |
| **A turma pedir as derivações em aula** | "De onde vem essa fórmula do `pass@k`?" | A Parte 4 do roteiro tem cinco conduções prontas com o custo em minutos. O item 5 (a desigualdade `consensus@k ≤ pass@k`) custa 2 min e vale sempre fazer; os demais só se sobrar tempo. O apêndice é autossuficiente |
| **Confusão entre GRPO e PPO** | Perguntas sobre o modelo de valor no Conceito 8 | Voltar ao quadro da Aula 15 com os quatro modelos do PPO e **riscar o de valor com o giz, na frente da turma**, escrevendo ao lado a vantagem relativa ao grupo. O contraste visual resolve mais rápido que a explicação |
| **Fórmula do `pass@k` travar a turma** | Silêncio no Conceito 5 | Fazer os extremos no quadro antes de qualquer álgebra: `c = 0` dá 0 para qualquer `k`; `c = n` dá 1; depois `n = 10, c = 1, k = 5`, que dá exatamente 0,5. O combinatório fica intuitivo pelos extremos |
| **Debate sobre "isso é raciocínio de verdade?"** | Discussão filosófica consumindo o Bloco 1 | Reconhecer a legitimidade da pergunta, marcar que a definição do curso é operacional e explicitamente não-cognitiva, e devolver ao arco: medir o que a cadeia representa é problema aberto e reaparece na Aula 27. Cortar em 3 min |
| **Ansiedade com a prova da aula seguinte** | Perguntas sobre a prova durante o conteúdo | Reservar os últimos 5 min do fechamento e **anunciar isso no slide 1** — evita que a dúvida vaze para dentro do Bloco 2. Esses 5 min não são negociáveis |
| **Tempo estourar no Bloco 2** | 01:35 e ainda no pipeline R1 | Cortar o Conceito 11 (crescimento de comprimento) para leitura dirigida e proteger o Conceito 12 e o aviso da prova. O que **não** se corta é a distinção GRPO × PPO, que é ponto de prova, nem o exercício |

## 7. Artefatos produzidos

- **Tabela de verificadores** do exercício: seis linhas × *tem verificador? · qual é · o que ele não
  confere · sinal alternativo*. É o artefato central da aula na V2, e a terceira coluna é o que o
  distingue de uma classificação decorada.
- Saída de `demo-pass-at-k.py` executado, com as duas tabelas e o gráfico, salva no repositório
  pessoal — com os números `0,540 / 0,600 / 0,440 / 1,000 / 0,800` anotados e o que cada um decide.
- Folha de síntese do Módulo 4: as três formas de sinal de pós-treino vistas em quatro aulas —
  imitação (SFT, Aula 13), preferência humana (RLHF/DPO, Aula 15) e verificação automática (GRPO,
  hoje) — com o critério de escolha entre elas.
- **Roteiro de estudo para a Prova da Aula 17**, anotado no fechamento, com a distribuição de pontos
  do novo perfil.

## 8. Desafio pós-aula

Não avaliado, e desta vez com um cuidado: **a Prova é na próxima aula**. A prioridade da semana é a
revisão, não a extensão. Na ordem:

1. **Estudo para a prova (prioritário).** Cobre as Aulas 1 a 16. O perfil mudou: o peso está em
   **diagnóstico e interpretação (42) e justificativa de escolha (40)**; conceito aplicado vale 8 e
   derivação vale 10, em um item marcado como tal. O modo de estudar que corresponde a isso:
   - **Refazer os exercícios de diagnóstico** de cada aula, escrevendo causa, evidência que confirma
     e decisão. Relembrar fórmula sem refazer diagnóstico prepara para 10 dos 100 pontos.
   - **Treinar a justificativa em voz alta**, com a regra de citar sempre dois eixos: o dado
     disponível e a restrição (ou, no pós-treino, a origem da recompensa e se os dados são fixos ou
     amostráveis).
   - **Usar os apêndices dos decks** para o item de fundamento formal. Eles existem para isso e
     estão mais completos do que qualquer coisa escrita no quadro.
2. **Leitura, se sobrar tempo.** DeepSeek-AI, *DeepSeek-R1* (arXiv 2501.12948) — introdução e a
   seção do R1-Zero. **Pergunta dirigida:** o artigo relata que o RL puro produziu raciocínio
   emergente **e** dois problemas concretos. Quais foram, e qual etapa seguinte do pipeline resolveu
   cada um?
3. **Extensão opcional de código.** Rodar `demo-pass-at-k.py --api --n 8` com um modelo real de free
   tier e comparar a forma das curvas com as do amostrador sintético. A pergunta honesta: o
   trade-off aparece igual, ou o modelo real se comporta de outro jeito? E a distância entre
   `pass@k` e `consensus@k` cresce ou encolhe?

Leituras da aula: Shao et al., *DeepSeekMath / GRPO* (arXiv 2402.03300) — a leitura fica muito mais
fácil com **A.3** e **A.4** ao lado; DeepSeek-AI, *DeepSeek-R1* (arXiv 2501.12948). Contexto de
avaliação de código: Jimenez et al., *SWE-bench* (arXiv 2310.06770).

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado** — valem os pesos da ementa: laboratórios 30%, prova 30%
(Aula 17), projeto final 40% (marcos nas Aulas 22, 26 e 30).

É, porém, a última aula antes da prova, e a V2 muda **como** o conteúdo é cobrado nela. A prova
passa a distribuir os 100 pontos assim: **diagnóstico e interpretação 42 · justificativa de escolha
40 · conceito aplicado 8 · derivação 10** (um item, e mesmo ele ancorado num porquê). O conteúdo
desta aula entra em três formas:

- **Diagnóstico.** Dado um comportamento — a curva de comprimento subindo com a de acerto achatada;
  um `pass@10` alto com `pass@1` baixo; um treino de GRPO em que muitos grupos não produzem
  gradiente —, nomear a causa e dizer **que evidência a confirmaria**.
- **Justificativa de escolha.** Classificar uma tarefa quanto à existência de verificador, escolher
  o sinal de pós-treino adequado (imitação, preferência, verificação) e defender a escolha citando a
  origem da recompensa e se os dados são fixos ou amostráveis. "É mais moderno" não é justificativa.
- **Leitura de número e conceito aplicado.** Distinguir `pass@k` de `pass@1` e de `consensus@k`,
  dizer o que cada um mede, e explicar por que `consensus@k ≤ pass@k`. Distinguir GRPO de PPO pela
  eliminação do modelo de valor e pela vantagem relativa ao grupo.
- **Derivação (o único item, marcado como tal).** Pode cair uma das do apêndice — o estimador de
  `pass@k`, a invariância da linha de base, a variância de `q·k` ou a perda de Bradley-Terry — e a
  pergunta sempre inclui **o que a conta prevê**, não apenas a conta.

*Observável em sala, sem nota:* na correção do exercício, o aluno identifica o caso 6 (tradução
Python → Rust) como verificador **parcial**, conecta isso ao risco de reward hacking do Conceito 7,
e consegue nomear pelo menos uma coisa que o verificador **não confere** em cada uma das quatro
tarefas verificáveis. Nomear o que fica de fora é o que distingue quem entendeu o fundamento de quem
decorou a classificação.
