---
aula: 1
titulo: "Apresentação da disciplina; panorama de LLMs; tarefas e métricas de NLP"
modulo: "1 — Fundamentos: do texto ao Transformer"
tipo: teorica
semana: 1
duracao_min: 120
versao: v2
---

# Aula 1 — Apresentação da disciplina; panorama de LLMs; tarefas e métricas de NLP

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (anotação de métrica, contagem medida no quadro), não conversas descartáveis
> com um chatbot. O roteiro de fala vive em `roteiro.md`; a especificação dos slides em
> `instructions-slides.md`.

> **Rebalanceamento V2.** Duas mudanças, e a segunda é posterior à primeira rodada.
> **(i) O bloco de métricas foi reenquadrado** — de "o que cada métrica mede" para "o detector
> de fraude com 99% de acurácia que nunca achou uma fraude". As fórmulas continuam enunciadas
> no fluxo; a álgebra inteira está no apêndice do deck, em seis itens (A.1 a A.6), mais
> detalhada do que estava na V1. O **A.6** é acréscimo desta rodada: METEOR, que é a
> resposta à pergunta que o slide 12 provoca — "então por que ninguém consertou isso?".
>
> **(ii) O contrato didático saiu desta aula.** Ele migrou integralmente para a **Aula 0** — a
> sessão de recepção de 60 min, extra-classe, na semana zero — junto com o diagnóstico da
> turma, o escopo do curso, o arco dos oito labs, o projeto e a política de uso de IA. Os
> slides 2 a 8 da versão anterior desta aula estão lá agora. Esta aula **aponta** para o
> documento de uma página do contrato em 30 segundos, no slide de abertura, sem recapitulá-lo.
>
> **Os ~15 minutos liberados foram para métricas de NLP**, que era o bloco mais apertado da
> aula: a matriz de confusão virou exercício em dupla em vez de resultado pronto, a perplexidade
> ganhou slide próprio no fluxo, e BLEU e ROUGE ganharam o exemplo numérico feito no quadro.
> Carga horária, numeração e objetivos de aprendizagem permanecem os da V1.

## 1. Objetivo da aula

Reorganizar o que o aluno já sabe (ou acha que sabe) sobre LLM em torno de uma tese verificável:
as tarefas clássicas de NLP foram unificadas sob a interface "prever o próximo token", e as
métricas que a área herdou dessas tarefas não sobrevivem intactas a essa unificação. O aluno sai
capaz de **ler um número de avaliação com desconfiança calibrada**: saber que denominador aquele
número tem e que falha ele não pega.

O contrato da disciplina **não** é objeto desta aula — ele foi apresentado na Aula 0 e está no
documento de uma página distribuído à turma. Esta aula gasta 30 segundos apontando para ele e usa
o tempo restante em conteúdo.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Situar** os cinco saltos técnicos que vão de ELIZA ao ChatGPT, identificando o que cada
   um resolveu que o anterior não resolvia.
2. **Classificar** uma tarefa de NLP arbitrária em uma das três famílias — classificação de
   sequência, rotulagem de tokens, geração — a partir da forma da saída.
3. **Diagnosticar** por que um número de acurácia alto pode não significar nada, comparando-o
   com o piso trivial `1 − π`, e **calcular** precisão, revocação e `F₁` a partir de uma matriz
   de confusão dada (derivação em A.1 e A.2).
4. **Decidir**, para um caso de uso concreto, qual das duas métricas — precisão ou revocação —
   importa mais, justificando pelo **custo do erro** naquele caso, e **dizer** o que o `F₁`
   esconde ao tratar as duas como igualmente importantes.
5. **Explicar** o que BLEU, ROUGE e perplexidade medem, e **justificar** por que métricas
   baseadas em referência falham em geração aberta (derivação em A.3 e A.4).
6. **Enunciar** a tese do curso: o próximo-token como interface única, e o custo que essa
   unificação transferiu da modelagem para a avaliação — e **explicar** por que perplexidade
   não atravessa tokenizadores (derivação em A.5).

*(Escopo técnico idêntico ao da V1. O item que descrevia as formas de avaliação da disciplina
saiu — ele é resultado da Aula 0 agora. Em troca, o item 4 é novo e usa parte do tempo liberado:
ele cobra **decisão** sobre qual métrica importa, com o custo do erro como critério, que é o
formato das questões de justificativa da prova.)*

## 3. Teoria aplicada

Cada conceito abaixo é apresentado pelo comportamento que o motiva, com o fundamento
matemático nomeado e a derivação remetida ao apêndice.

### Bloco 1 (00:10–00:55) — Panorama: por que este é *o* tema, e o que ele unificou

**O ponteiro do contrato — 30 segundos, no slide 1.**
O contrato desta disciplina — avaliação, composição da prova, política de uso de IA, arco dos
oito labs, projeto — foi apresentado na **Aula 0**, a sessão de recepção da semana zero, e está
no **documento de uma página** distribuído no canal da turma. Esta aula não o recapitula: ela
aponta para o documento em meia dúzia de frases e segue.

*Por que apontar em vez de recapitular:* recap de três minutos devolveria um quinto do tempo que
a migração liberou. O apontamento resolve o caso de quem faltou à sessão — que é extra-classe e
não obrigatória — sem custar o conteúdo. **Se o documento não tiver sido distribuído, o
apontamento não funciona**, e aí a mitigação correta é distribuí-lo antes desta aula, não
recapitular aqui.

*Erro a evitar:* transformar o apontamento em conversa. A pergunta "como vai ser a prova?" tem
resposta no documento; a resposta em sala é "está na página 1, e eu prefiro gastar o tempo de
hoje em métricas". Perguntas de contrato ficam para o fim da aula.

**Conceito 1 — De ELIZA ao ChatGPT em cinco saltos.**
(i) **Regras** — ELIZA (Weizenbaum, 1966): casamento de padrões e reescrita; a ilusão de
compreensão sem modelo de língua. (ii) **Estatística** — modelos de n-gramas e tradução
estatística: a língua como distribuição de probabilidade estimada por contagem; o teto é a
esparsidade. (iii) **Representações densas** — Word2Vec (2013): palavras como vetores,
semântica como geometria. (iv) **Atenção e Transformer** — atenção em NMT (2014) e o
Transformer (2017): paralelismo e dependências longas no mesmo mecanismo. (v) **Escala e
instrução** — GPT-3 (2020) mostra aprendizado em contexto; o ajuste por instrução e por
preferências transforma um completador de texto em assistente utilizável.
*Analogia:* cada salto trocou trabalho humano por dados e computação — de escrever regras,
para contar frequências, para aprender representações, para aprender a própria função de
comparação.
*Erro conceitual comum:* achar que ChatGPT foi um salto de arquitetura. Foi um salto de
*interface e alinhamento* sobre uma arquitetura de 2017.

**Conceito 2 — Por que LLM virou infraestrutura.**
Três propriedades combinadas: (a) uma interface única de texto substitui N modelos
especializados; (b) o custo marginal de tentar uma tarefa nova caiu de "montar um dataset
rotulado" para "escrever um prompt"; (c) a mesma pilha serve produto, ferramenta interna e
automação. Isso desloca o gargalo da modelagem para a **avaliação** e para a **engenharia de
sistema** — que é a razão de existir dos Módulos 5 a 7.
*Nota de honestidade:* números de mercado e faixas salariais locais são `[definir na oferta]` —
o instrutor traz dados atualizados da praça, não estimativa.

### Bloco 2 (01:05–01:50) — Tarefas de NLP e as métricas que as julgam

**Conceito 3 — A taxonomia pela forma da saída.**
Toda tarefa clássica de NLP cai em uma de três famílias, e a família é determinada pelo *tipo*
da saída, não pelo domínio: **classificação de sequência** (texto → 1 rótulo), **rotulagem de
tokens** (texto → 1 rótulo por token) e **geração** (texto → texto).
*Analogia:* é a diferença entre uma função que retorna um enum, uma que retorna uma lista do
mesmo tamanho da entrada, e uma que retorna uma string de tamanho livre.
*Erro conceitual comum:* classificar pelo domínio ("é jurídico, então é classificação"). O
critério é a assinatura da função.

**Conceito 4 — O detector de fraude com 99% de acurácia.**
*Comportamento observável:* `return False` numa base com 1% de fraude entrega **99% de
acurácia** e **revocação zero**. Nenhum ajuste conserta, porque não há o que ajustar — o modelo
não aprendeu nada.
*Causa, e é o resultado que a aula usa:* num problema de prevalência `π`, o classificador
trivial atinge acurácia `1 − π` **de graça**. A régua não é 50%: é `1 − π`. Ler uma acurácia
sem saber a prevalência é ler um número sem denominador.
*Números concretos (em A.1, tabela completa):* com `N = 10.000` e `π = 1%`, o modelo agressivo
tem acurácia **pior** que o trivial (0,909 contra 0,990) e é o único dos três que serve para
triagem. A acurácia ordena os modelos ao contrário do que o problema exige.
*Fundamento:* as quatro métricas saem das quatro células da matriz de confusão; o piso trivial
é `1 − π`; em multiclasse, macro e micro divergem exatamente na classe rara. → **A.1**
*Erros conceituais comuns:* tratar acurácia como nota de 0 a 100 (o piso é `1 − π`); e usar
micro-F₁ num roteador com fila crítica de 2%, que esconde justamente a fila que importa.

**Conceito 5 — `F₁` é média harmônica, e o peso é decisão de produto.**
*Comportamento observável:* um detector com precisão 1,00 e revocação 0,01 tem média
aritmética 0,505 e `F₁` de 0,0198. A média harmônica é dominada pelo menor dos dois — e é
isso que se quer.
*Fundamento:* `F₁ = 2PR/(P+R)` é a média harmônica de `P` e `R`; `F_β` é a média harmônica
**ponderada**, com `β²` sendo a razão de importância entre revocação e precisão. Vale
`H ≤ G ≤ A`, com igualdade só quando `P = R`. → **A.2**
*Números:* com `P = 0,30` e `R = 0,90`, o mesmo sistema vale `F₀,₅ = 0,346`, `F₁ = 0,450` ou
`F₂ = 0,643`. Os três estão certos; respondem perguntas diferentes.
*Erro conceitual comum:* tratar `F₁` como "a métrica certa" universal. `β² ≈ c_FN / c_FP`, e
esses custos **não estão no conjunto de dados** — a escolha é de produto.

**Conceito 6 — Métricas de geração: três perguntas, um numerador, dois denominadores.**
*Comportamento observável, medido na demo:* a mesma contagem de n-gramas dividida pelo
candidato e dividida pela referência dá dois números diferentes. É literalmente a diferença
entre BLEU e ROUGE.
BLEU é **precisão** de n-gramas com contagem truncada e penalidade de brevidade:
`BLEU = BP · exp(Σ wₙ log pₙ)`. ROUGE é **revocação** de n-gramas (ROUGE-N) ou usa a maior
subsequência comum (ROUGE-L). Perplexidade não compara com referência humana:
`PPL = exp(−(1/N) Σ log P(tᵢ | t₍<ᵢ₎))`.
*Fundamento:* BLEU combina as ordens por **média geométrica**, e um `pₙ = 0` zera o resultado
inteiro — no exemplo de A.3, uma tradução correta recebe BLEU-4 exatamente **zero**. → **A.3**
*Fundamento:* ROUGE-N troca o denominador; ROUGE-L usa a recorrência da subsequência comum, e
é sensível à ordem sem exigir adjacência. → **A.4**
*Fundamento:* `PPL = exp(H)` é a média geométrica do inverso das probabilidades — o número
efetivo de opções entre as quais o modelo hesita. Como `H` é média por token, trocar o
tokenizador muda a unidade: `PPL_B = PPL_A^r`. → **A.5**
*Erro conceitual comum:* comparar perplexidade entre modelos com tokenizadores diferentes, e
tentar consertar reescalando pela razão de fertilidade. Não basta: além do denominador, muda o
espaço de eventos. Esse fio se amarra na Aula 2 e produz número próprio no Lab 2.

**Conceito 7 — Por que a métrica de referência falha em geração aberta.**
*Comportamento observável:* tradução ótima com sinônimos → BLEU baixo; resposta errada que
copia palavras da referência → BLEU alto. A métrica é sensível à forma e cega ao conteúdo.
*Por que trocar de métrica de sobreposição não resolve:* ROUGE cai junto com BLEU no caso do
sinônimo, porque as duas contam a mesma coisa. → **A.4**
Daí o arco do curso: a Aula 27 volta a este ponto com avaliação humana, LLM-as-judge calibrado
e decomposição em afirmações atômicas.
*Erro conceitual comum:* concluir "então métrica não serve". Serve — desde que se avalie a
menor camada que explica a falha, o que é literalmente a tese da Aula 27.
*Erro conceitual comum de quem já ouviu falar do assunto:* supor que ninguém tentou consertar
isso. Tentaram, em 2005, e a métrica chama-se **METEOR**: ela casa palavras por forma exata, por
radical **e por sinônimo**, pesa revocação acima de precisão (`α = 0,9`) e cobra a ordem por fora,
como penalidade sobre o número de blocos contíguos. Na frase do sinônimo desta aula, **BLEU-4 =
0,000 e METEOR ≈ 0,998**. O que METEOR **não** conserta é o caso 3 — resposta falsa com o
vocabulário certo continua tirando nota alta —, e é exatamente isso que torna a Aula 27
necessária: afrouxar o casamento resolve forma, não resolve verdade. Ressalva local que vale
dizer: o casamento por sinônimo depende de um léxico por idioma, e a cobertura em português é
sensivelmente pior que em inglês. → **A.6**

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura | Sem recap (primeira aula de conteúdo): **o ponteiro de 30 s para o documento do contrato** (slide 1); as duas frases verdadeiras e as duas erradas sobre LLM, que abrem a tese da aula (slide 2) |
| 00:10 | 45 min | Bloco 1 — Panorama | De ELIZA ao ChatGPT em cinco saltos, cada um resolvendo o que o anterior não resolvia (13 min); por que LLM virou infraestrutura (10 min); **demo "um modelo, quatro tarefas"** com a instrumentação na tela (12 min); taxonomia pela forma da saída (10 min) |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — Métricas de NLP | **O detector de fraude com 99% de acurácia** e o piso trivial `1 − π` (7 min); **Exercício 1 — a matriz na mão: três detectores, seis números** (7 min, em dupla); `F₁` como média harmônica e o peso como decisão de produto (5 min); **BLEU e ROUGE com o exemplo numérico no quadro** — um numerador, dois denominadores (9 min); **perplexidade, slide próprio** — a métrica que dispensa gabarito (5 min); onde a métrica de referência quebra, com o caso do sinônimo (5 min); **Exercício 2 — da tarefa à métrica** (7 min) |
| 01:50 | 10 min | Fechamento | Síntese da tese do próximo-token; **índice do apêndice projetado (20 s)**; checklist de setup para o Lab 1; ponte para a Aula 2 (Tokenização); leitura indicada |

*Comparação com a V1 e com a primeira rodada da V2.* A grade de 120 min é a mesma. A mudança está
na distribuição: **o Bloco 1 perdeu os ~15 min de contrato didático** — avaliação, arco dos labs,
projeto, política de IA, que agora são da Aula 0 — e o **Bloco 2 os absorveu inteiros**, virando o
bloco mais longo em conteúdo efetivo da aula.

O que os 15 minutos compraram, item por item: a matriz de confusão deixou de ser resultado
projetado e virou **Exercício 1**, com a turma calculando seis números em dupla (7 min); a
**perplexidade ganhou slide próprio** no fluxo, em vez de menção de passagem, porque ela volta na
Aula 2 (fertilidade) e no Lab 2 (`PPL = exp(loss)`); **BLEU e ROUGE ganharam o exemplo numérico
feito no quadro** sobre o mesmo par de frases, mostrando que uma pune o que a outra premia; e o
slide de quebra da métrica de referência ganhou o **segundo caso**, o do sinônimo, que é o mais
convincente porque a resposta está correta e o BLEU a penaliza.

## 4. Demonstração guiada

**Demo "um modelo, quatro tarefas" — 9 min, 100% navegador, sem código.**
Por ser a primeira aula e haver alunos ainda decidindo a matrícula, a demonstração não pede
ambiente montado: roda em um chat de LLM com free tier (Google AI Studio ou equivalente) e no
quadro. Por isso **esta aula não tem pasta `codigo/`**.

Na V2 a demo deixa de ser só ilustração da tese "uma interface, N tarefas" e passa a produzir
**dois números medidos** que o Bloco 2 usa como evidência.

Passos em alto nível:

1. Abrir o chat com um modelo pequeno de free tier; deixar o painel de parâmetros visível mas
   sem tocar nele.
2. Colar um comentário real de app em português e pedir o **sentimento** em uma palavra →
   família *classificação de sequência*.
3. Sobre o mesmo texto, pedir **extração de entidades em JSON** (pessoa, organização, local) →
   família *rotulagem de tokens*, agora resolvida por geração.
4. Pedir **tradução** do comentário para o inglês → família *geração*.
5. Pedir **resumo em uma frase** de um parágrafo longo → família *geração*.
6. No quadro: escrever a tradução de referência (feita pelo instrutor antes da aula) e a saída
   do modelo; contar à mão os unigramas e bigramas em comum.
7. **Fazer as duas divisões.** Primeiro dividindo pelos n-gramas do **candidato** — é a
   precisão, é o numerador do BLEU. Depois dividindo pelos n-gramas da **referência** — é a
   revocação, é o ROUGE. Mesmo numerador, dois denominadores, dois números.
8. Deixar os dois números circulados no quadro.

**Números que a demo produz e que a aula usa como evidência (§7 do contrato):** a precisão de
unigramas e de bigramas de uma tradução que a sala julgou boa, e a revocação dos mesmos
acertos. Os dois reaparecem no slide 14 (as três perguntas) e no slide 15 (a dívida de
avaliação). Sem eles, o slide 15 volta a ser afirmação.

Insumos preparados antes da aula: um comentário de app em PT (3–4 linhas), sua tradução de
referência escrita pelo instrutor, e um parágrafo longo para sumarizar. Todos ficam num arquivo
de texto local para copiar e colar sem depender de rede.

## 5. Hands-on

São **dois** exercícios, e o primeiro é novo — ele existe porque a migração do contrato para a Aula 0 liberou tempo, e a matriz de confusão deixou de ser resultado projetado para virar cálculo da turma.

### Exercício 1 — A matriz na mão: três detectores, seis números (7 min, slide 8, 01:12–01:19)

Três matrizes de confusão projetadas, de três detectores de fraude sobre o **mesmo** conjunto de 10.000 transações com 1% de fraude real. Cada dupla calcula, para cada detector, **precisão e revocação** — seis números — e responde uma pergunta: *qual dos três você poria em produção, e o que você precisaria saber sobre o negócio para ter certeza?*

Os três detectores são construídos para ensinar coisas diferentes: um que **nunca acusa** (acurácia 99%, revocação 0); um que **acusa muito** (revocação alta, precisão baixíssima); e um intermediário. A pergunta não tem resposta única — ela depende do custo relativo entre fraude não detectada e transação legítima bloqueada, e é isso que a dupla precisa descobrir que precisa saber.

*Critério de conclusão observável:* os seis números calculados, e a dupla nomeia em voz alta **a informação de negócio que falta** para decidir. Escolher um detector sem nomear o que falta não fecha o exercício.

*Por que ele vale o tempo:* é o formato exato das questões de justificativa da prova — cenário com restrição, decisão a defender, e a conta como ferramenta de sustentação. E o detector que nunca acusa é o gancho do slide 7, agora medido pela própria turma em vez de contado por mim.

### Exercício 2 — Da tarefa à métrica (7 min, slide 13, 01:43–01:50)

**Componente prático da unidade — exercício em dupla (5 min de dupla + 2 de correção).**

Cinco cenários projetados no slide. Cada dupla escreve, para cada um: (a) a família da tarefa,
(b) a métrica primária, (c) **uma falha que essa métrica não pegaria**. A terceira coluna é a
mudança da V2 e é a que vale — ela é o mesmo verbo dos 42 pontos de diagnóstico da prova.

1. Roteador de tickets de suporte em 12 filas, com uma fila crítica que representa 2% do volume.
2. Extração de número de processo e nome das partes em petições jurídicas.
3. Tradução PT→EN de descrições de produto de e-commerce.
4. Detector de discurso de ódio em comentários, com revisão humana a jusante.
5. Assistente que responde perguntas sobre o regulamento da universidade, com citação da fonte.

*Respostas esperadas na terceira coluna:* (1) micro-F₁ alto esconde a fila crítica de 2% —
a falha invisível é a fila que importa, e a correção é macro (A.1); (2) um dígito trocado no
número de processo casa quase todos os caracteres e passa; (3) sinônimo correto derruba BLEU
sem derrubar a qualidade (A.3), e ROUGE não salva (A.4); (4) com humano a jusante o peso é
assimétrico — `β > 1` (A.2) — e `F₁` esconde isso; (5) nenhuma métrica de referência verifica
se a citação sustenta a afirmação.

*Critério de conclusão observável:* a dupla entrega cinco linhas com as **três** colunas
preenchidas e defende ao menos uma escolha em voz alta. Preencher família e métrica sem a
terceira coluna não fecha o exercício.

*Extensão para quem terminar antes (opcional):* calcular `F₁` e `F₂` para um sistema com
`P = 0,30` e `R = 0,90`, seguindo A.2, e dizer qual dos dois números o cenário 4 deveria
reportar. É a conta que na V1 seria obrigatória e aqui vira aprofundamento.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| Turma heterogênea: parte sem Aprendizagem de Máquina | Diagnóstico inicial mostra menos de metade com ML | Cada conceito de ML pressuposto é explicado em 2–3 frases na hora; "modelo", "treinar" e "supervisionado" ganham definição operacional no Bloco 2. E o slide 5 é repetido em uma frase: a derivação está escrita, não escondida |
| **A turma ler "apêndice" como "matéria cortada"** | Comentário de que a disciplina "não tem matemática" | Projetar o índice do apêndice deste próprio deck: seis itens, com derivação completa de tudo que foi enunciado. O rigor não saiu, mudou de lugar — e agora é consultável |
| **A turma pedir a derivação em aula** | "De onde vem esse F1?" no slide 13 | Parte 4 do roteiro, itens 1 a 5, com o tempo de cada um. A regra é remeter e seguir; o que **não** se sacrifica é o slide 15 nem a contagem no quadro da demo |
| Free tier do chat indisponível ou com rate limit na hora da demo | Erro de quota na primeira requisição | Capturas de tela das quatro tarefas preparadas na véspera; **as duas contagens de n-gramas no quadro não dependem de rede e são a parte insubstituível** |
| Projetor/rede falham | — | O Bloco 2 inteiro é executável no quadro: as três famílias, a matriz de confusão com o caso de 1% e as duas contagens de n-gramas |
| Expectativa errada ("curso de prompt engineering") | Perguntas sobre prompt nos primeiros 10 min | Mostrar o arco dos 8 labs no slide 6 e situar prompting na Aula 10 / Lab 3; a resposta é o mapa, não a discussão |
| Alunos ainda decidindo matrícula | Sala com mais gente do que o esperado | Os slides 3 a 8 são autossuficientes como "o que é esta disciplina"; a demo do Bloco 2 é a amostra do produto |
| Tempo estourar no Bloco 1 (contrato gera muita pergunta) | 00:45 e ainda no projeto final | Cortar "mercado e carreiras" para o fim da aula e proteger o Bloco 2; o contrato completo está na ementa entregue. **Não cortar o slide 5** — sem ele o semestre inteiro estuda pela distribuição errada |
| **Debate sobre pesos da prova consumir o Bloco 1** | Discussão de avaliação passando de 5 min no slide 5 | Cravar em uma frase que a ementa tem os pesos por escrito e que o formulário quinzenal vai treinar o formato; seguir |

## 7. Artefatos produzidos

- **Anotação do exercício em dupla:** tabela **cenário → família → métrica → falha que a
  métrica não pega**, com cinco linhas, fotografada ou digitada no repositório pessoal do
  aluno. É o artefato central da aula na V2 — a quarta coluna é nova.
- **As duas contagens de n-grama do quadro**, anotadas: a precisão e a revocação dos mesmos
  acertos, sobre a tradução que a sala julgou boa. É o número que sustenta o argumento da
  dívida de avaliação.
- Matriz de confusão do caso de 1% preenchida à mão, com acurácia, precisão e revocação
  calculadas e o piso trivial `1 − π` anotado ao lado.
- Checklist de setup para o Lab 1 (Aula 4), entregue no fechamento: conta Google com Colab
  funcionando, conta Hugging Face criada, conta em um provedor de API com free tier.
- Cópia da ementa e do esquema de avaliação, com os três marcos do projeto e **os quatro pesos
  da prova** anotados.
- Nenhum arquivo de código nesta aula — a demonstração é de navegador e quadro.

## 8. Desafio pós-aula

Não avaliado. Três itens, na ordem:

1. **Setup.** Criar as três contas do checklist e abrir um notebook Colab em branco
   confirmando que o ambiente sobe. Isso remove o gargalo do Lab 1.
2. **Uma métrica que você já leu errado.** Escolher um número de avaliação que você já viu ou
   reportou (acurácia de um modelo, nota de um benchmark, perplexidade de um cartão de modelo)
   e escrever cinco linhas dizendo **qual denominador** aquele número tem e **que falha** ele
   não pegaria. Não é preciso recalcular nada.
3. **Leitura.** Jurafsky & Martin, *Speech and Language Processing* (3ª ed., rascunho aberto):
   capítulo de modelos de linguagem por n-gramas (seção de perplexidade) e capítulo de
   classificação de texto (seção de avaliação: precisão, revocação, F1). **Pergunta dirigida:**
   por que a perplexidade de dois modelos só é comparável se o tokenizador for o mesmo? Compare
   o que o livro afirma com a conta de **A.5** deste deck — que mostra que a diferença é uma
   **potência**, não um fator. A resposta completa, com fertilidade medida, é a Aula 2.

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. Ela estabelece os critérios que valem para as 29
aulas seguintes, com os pesos da ementa — que não são reinventados aqui:

- **Laboratórios — 30%.** Oito labs com entregável individual, entrega até uma semana após o
  lab, **descartando a menor nota**. Cada lab é avaliado por: checkpoints concluídos com saída
  visível no notebook, respostas às questões-guia, e declaração de uso de IA presente.
- **Prova — 30%.** Individual, escrita, Aula 17, sobre as Aulas 1 a 16. Sem uso de IA. A
  distribuição dos 100 pontos é **42 interpretação e diagnóstico · 40 justificativa de escolha ·
  8 conceito aplicado · 10 derivação**, e ela é dita em voz alta nesta aula (slide 5).
- **Projeto final — 40%.** Equipes de 3–4. Proposta 5% (Aula 22) + checkpoint 5% (Aula 26) +
  sistema e relatório 20% + apresentação 10% (Aula 30). Rubrica: funcionamento técnico 40%,
  rigor da avaliação quantitativa 30%, relatório 20%, apresentação 10%.
- **Declaração de uso de IA** obrigatória em toda entrega, e responsabilidade integral pelo
  código entregue: qualquer entrega pode virar defesa oral.

**O que a V2 muda no *como* se cobra o conteúdo desta aula específica:**

- **A parte de métricas é cobrada como diagnóstico.** Um item típico não pede "calcule F1":
  pede "um time reporta 99% de acurácia num detector de fraude; diga o que está errado nessa
  frase e que número você pediria no lugar". A resposta completa nomeia a prevalência e o piso
  `1 − π`.
- **A perplexidade é cobrada pela conta, não pela advertência.** "Não é comparável porque o
  tokenizador é diferente" vale parcialmente. A resposta completa diz **quanto** muda —
  `PPL_B = PPL_A^r` — e nomeia bits por caractere como a normalização honesta. O material está
  em A.5 e é dito em sala.
- **O apêndice é cobrável como fundamento de justificativa, nunca como derivação isolada** —
  com a exceção do único item de derivação da prova, que vale 10 pontos.

*Observável em sala, sem nota:* ao ser questionado no fechamento, o aluno classifica uma tarefa
nova nas três famílias e, para o cenário desbalanceado, **compara a acurácia com o piso trivial**
em vez de dizer só que "acurácia engana". Dizer que engana é a V1; nomear `1 − π` é a V2.
