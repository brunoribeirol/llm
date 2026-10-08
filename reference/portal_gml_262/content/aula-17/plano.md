---
aula: 17
titulo: "Prova (conteúdo das Aulas 1 a 16)"
modulo: "4 — Alinhamento e Raciocínio"
tipo: avaliacao
semana: 9
duracao_min: 120
versao: v2
---

# Aula 17 — Prova (AV1)

> **Postura deste material.** A prova é artefato: circula em papel, é corrigida com critério
> escrito e produz estatística por questão que realimenta as aulas seguintes.

> **Rebalanceamento V2.** A distribuição de pontos foi invertida em relação à V1: a prova
> deixa de cobrar predominantemente derivação e passa a cobrar **diagnóstico, interpretação
> e justificativa de escolha**. A matemática continua presente e cobrada — como ferramenta
> de justificativa, não como fim. A cobertura de tópicos (Aulas 1 a 16), a duração, o peso
> na AV1 e a política de nota parcial permanecem os da V1.

## 1. Objetivo da aula

Verificar individualmente, sem consulta e sem IA, se o estudante consegue **usar** os
fundamentos dos Módulos 1 a 4 para explicar um comportamento de modelo, diagnosticar uma
falha e defender uma decisão de arquitetura — e se sabe recorrer à matemática certa para
sustentar a explicação.

## 2. Resultados de aprendizagem verificados

1. **Diagnosticar** uma falha de treino ou de inferência a partir do sintoma, nomeando a
   causa e a evidência que a confirmaria.
2. **Interpretar** um resultado experimental (tabela de métricas, curva, saída de modelo) e
   dizer o que ele permite e o que **não** permite concluir.
3. **Justificar** uma escolha de arquitetura, técnica ou hiperparâmetro para um cenário com
   restrições dadas.
4. **Enunciar e aplicar** corretamente os fundamentos centrais do curso.
5. **Derivar** um resultado formal, quando a derivação for o instrumento da justificativa.

## 3. Estrutura da sessão

Grade própria de avaliação.

| Início | Dur. | Bloco |
|---|---|---|
| 00:00 | 10 min | Abertura: regras, distribuição de pontos, o que é permitido, marcos de tempo |
| 00:10 | 100 min | Execução, com avisos em 00:40, 01:10, 01:35 e 01:45 |
| 01:50 | 10 min | Recolhimento folha por folha; ponte para a Aula 18 |

Individual, escrita, **sem consulta e sem uso de ferramentas de IA**. Estudantes com laudo
têm 1h adicional, operacionalizada pelo Apoio Psicopedagógico.

## 4. A prova

### Q1 — Tokenização e custo (12 pontos · 10 min) · *interpretação*

Uma equipe mede o mesmo corpus com dois tokenizadores e obtém:

| Tokenizador | tokens (PT) | tokens (EN) | perplexidade reportada |
|---|---|---|---|
| A (BPE, treinado em EN) | 1.480 | 1.020 | 18,4 |
| B (SentencePiece multilíngue) | 1.115 | 1.070 | 24,1 |

**(a)** *(7 pts)* A equipe conclui que "o tokenizador A produz um modelo melhor, porque a
perplexidade é menor". A conclusão **não** se sustenta. Explique por quê, e diga qual
informação seria necessária para tornar a comparação legítima.

**(b)** *(5 pts)* A equipe atende usuários majoritariamente em português e paga por token.
Com base apenas na tabela, qual tokenizador você recomenda e qual é o ganho relativo
esperado? Justifique com o número.

---

### Q2 — Diagnóstico de treino (15 pontos · 12 min) · *diagnóstico*

Um time treina dois modelos idênticos exceto pela dimensão: `d_model = 256` e
`d_model = 1024`. Mesmos dados, mesmo número de passos, mesma taxa de aprendizado. O modelo
maior termina com **loss de treino e de validação piores** que o menor. Não houve `NaN`,
não houve divergência, e nenhum aviso apareceu no log.

**(a)** *(9 pts)* Aponte a causa mais provável e explique o mecanismo pelo qual ela produz
exatamente esse sintoma.

**(b)** *(6 pts)* Descreva **uma medição** que confirmaria sua hipótese — o que exatamente
seria medido, e que resultado confirmaria contra que resultado a refutaria.

---

### Q3 — Leitura de arquitetura sob restrição (18 pontos · 15 min) · *justificativa*

Você precisa servir um modelo de 7 bilhões de parâmetros com contexto de 8k tokens, em GPU
com 24 GB, atendendo requisições concorrentes. Medições preliminares mostram que a memória
estoura com 4 requisições simultâneas, embora o modelo sozinho caiba folgadamente.

**(a)** *(8 pts)* Explique de onde vem o consumo que escala com o número de requisições
concorrentes, e por que ele não aparece quando se mede o modelo isolado.

**(b)** *(6 pts)* Entre reduzir o contexto para 4k e trocar MHA por GQA, qual medida ataca
melhor esse gargalo específico? Justifique dizendo o que cada uma reduz.

**(c)** *(4 pts)* Um colega sugere "usar um modelo menor". Diga em que condição essa
sugestão resolveria o problema e em que condição não resolveria.

---

### Q4 — O pipeline como sequência de decisões (18 pontos · 15 min) · *justificativa*

Para cada situação, indique **em que estágio do pipeline** (pré-treino, SFT, modelagem de
recompensa, otimização por preferência, RL com recompensa verificável) você intervém, e
**por quê aquele estágio e não o anterior**:

**(a)** *(4 pts)* O modelo responde no formato errado — devolve parágrafos quando se pede
JSON.
**(b)** *(4 pts)* O modelo responde no formato certo, mas escolhe consistentemente a
alternativa que agrada o usuário em vez da correta.
**(c)** *(5 pts)* O modelo erra sistematicamente problemas de aritmética de várias etapas,
embora acerte quando a conta é dada pronta.
**(d)** *(5 pts)* O modelo desconhece um domínio técnico inteiro — vocabulário, convenções e
fatos básicos.

---

### Q5 — Escolha de técnica com restrição (12 pontos · 10 min) · *justificativa*

Três cenários. Para cada um, escolha entre **prompting**, **RAG** e **fine-tuning**, e
justifique em uma frase dizendo o que a alternativa escolhida resolve **e o que ela não
resolve**:

**(a)** *(4 pts)* Assistente que deve responder sobre um regulamento que muda a cada semestre.
**(b)** *(4 pts)* Modelo que deve adotar um formato de saída muito específico da empresa, com
milhares de exemplos disponíveis.
**(c)** *(4 pts)* Sistema que precisa citar a fonte de cada afirmação para auditoria.

---

### Q6 — Interpretação de resultado experimental (15 pontos · 13 min) · *interpretação*

Uma equipe mede `pass@k` do mesmo modelo em três temperaturas, sobre cinco problemas com
verificador automático:

| Temperatura | pass@1 | pass@10 | consensus@10 |
|---|---|---|---|
| 0,2 | 0,540 | 0,600 | 0,600 |
| 0,7 | 0,440 | 0,600 | 0,600 |
| 1,2 | 0,440 | 1,000 | 0,800 |

**(a)** *(6 pts)* A temperatura 0,2 satura em `pass@10 = 0,600` e não passa disso por mais
amostras que se gere. Explique o que isso revela sobre a distribuição de saídas do modelo
nessa temperatura.

**(b)** *(5 pts)* Em T = 1,2, `pass@10 = 1,000` e `consensus@10 = 0,800`. Explique a origem
dessa diferença e o que ela custa, em termos de sistema, para ser convertida em ganho real.

**(c)** *(4 pts)* A equipe vai colocar isso em produção, respondendo **uma vez** por
requisição, sem verificador. Que temperatura você recomenda, e por quê a tabela quase induz
à escolha errada?

---

### Q7 — Fundamento formal (10 pontos · 10 min) · *derivação*

O fator `1/√d_k` na atenção não é arbitrário nem ajustável.

**(a)** *(6 pts)* Assumindo que as componentes de `q` e `k` são independentes, com média 0 e
variância 1, mostre que `Var(q·k) = d_k`. Explicite onde a hipótese de independência é usada.

**(b)** *(4 pts)* A partir desse resultado, explique por que a divisão por `√d_k` — e não por
`d_k`, nem por uma constante ajustável — é a correção certa.

---

**Total: 100 pontos · 85 minutos sugeridos**, em janela de 100 — 15 min de folga deliberada
para revisão.

### Distribuição por registro cobrado

| Registro | V1 | **V2** | Questões |
|---|---|---|---|
| Interpretação e diagnóstico | 12 | **42** | Q1 (12), Q2 (15), Q6 (15) |
| Justificativa de escolha | 16 | **40** | Q3b+c (10), Q4 (18), Q5 (12) |
| Conceito aplicado | 52 | **8** | Q3a (8) |
| Derivação | 20 | **10** | Q7 (10) |

A matemática permanece cobrada em Q7 diretamente e, indiretamente, em toda a prova: nenhuma
resposta de Q2, Q3 ou Q6 se sustenta sem o fundamento correto. A diferença é que agora ela
aparece **a serviço de uma explicação**, não como exercício isolado.

## 5. Hands-on

Não se aplica — a sessão é a própria avaliação.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Turma estranhar o formato** (esperava derivação) | Perguntas na abertura sobre "vai cair conta?" | O formato foi anunciado desde a Aula 16 e praticado nos exercícios de diagnóstico de todas as aulas. Reafirmar na abertura: Q7 é a única de derivação pura, e vale 10 |
| **Q2 e Q6 parecerem "sem resposta única"** | Aluno paralisado procurando a resposta certa | O enunciado pede causa **e** evidência; o gabarito aceita variantes. Está impresso na folha que justificativa vale mais que a resposta |
| **Tempo mal dimensionado** | Muitos em branco na Q6 e Q7 | Os avisos de tempo em 00:40 / 01:10 / 01:35 / 01:45 existem para isso. A folga de 15 min absorve atraso moderado |
| **Estudante com laudo sem sala separada** | Ausência de comunicação prévia | Acionar o Apoio Psicopedagógico com antecedência, conforme orientação institucional; a 1h adicional é direito |
| **Questão com média muito baixa** | Estatística pós-correção | Hipótese padrão é falha de ensino ou de enunciado, não de turma. Retomada de 5 min na aula seguinte e reescrita da questão |

## 7. Artefatos produzidos

- As provas corrigidas, com pontuação por alínea.
- **Estatística por questão** — média, dispersão e taxa de branco. É o artefato que mais
  rende: diz o que retomar nas Aulas 18 a 30.
- **Comparação com a V1**, se houver oferta anterior: a mudança de perfil deve aparecer na
  distribuição de acertos por registro. Vale registrar.
- Nenhum arquivo de código: a Q7 é resolvida a lápis.

## 8. Desafio pós-aula

A prova encerrou o ciclo dos Módulos 1 a 4. As duas tarefas olham para frente:

1. **Leitura para a Aula 18.** Lewis et al., *RAG* (arXiv 2005.11401), seções 1 e 2.
   **Pergunta dirigida:** a prova cobrou o pipeline de treinamento inteiro, cada estágio
   custando computação. O RAG resolve um problema de conhecimento **sem tocar em nenhum
   peso**. Em um parágrafo: qual problema, exatamente, ele resolve que nenhum estágio de
   treinamento resolve bem?
2. **Formação de equipes.** O projeto final é lançado na Aula 18, em equipes de 3 a 4, e vale
   60% da AV2. Chegar com equipe formada e dois ou três domínios candidatos economiza a
   primeira semana.

## 9. Critérios de avaliação

Esta prova compõe **60% da AV1**, junto com Laboratórios 1–4 e participação (40%). A média
final da disciplina é `(AV1 + AV2) / 2`.

### Política de nota parcial

- **Justificativa é o que vale.** Resposta certa sem justificativa recebe no máximo metade
  dos pontos da alínea. Está impresso na folha.
- **Em Q2 e Q6**, hipótese plausível bem justificada com evidência coerente recebe pontuação
  integral mesmo que não seja a hipótese do gabarito. O que se avalia é o raciocínio
  diagnóstico, não a adivinhação.
- **Em Q7**, erro algébrico com o caminho correto e explícito perde 1 ponto, não a alínea.
  Caminho ausente com resultado correto recebe metade.
- **Erro que se propaga** entre alíneas é penalizado uma única vez.
- **Formulação alternativa correta** é aceita integralmente; o gabarito registra as variantes.
- **Questão em branco** vale zero e entra na estatística de branco, lida separadamente da de
  erro.

### Onde estão as respostas

Critérios detalhados, respostas esperadas e variantes aceitáveis estão em `gabarito.md`, na
mesma pasta, **instructor-only**. Não tem versão HTML, de propósito. Este plano circula sem ele.

### Calibração

Após a correção, levantar média e dispersão por questão. Média abaixo de 40% do valor da
questão dispara revisão do enunciado e retomada do tópico. Atenção especial a **Q2 e Q6**:
são o novo eixo da prova, e se a turma não responder bem a elas, o problema é de como as
aulas 1 a 16 foram conduzidas — não de dificuldade da prova.
