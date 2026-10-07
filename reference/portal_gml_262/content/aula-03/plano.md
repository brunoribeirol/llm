---
aula: 3
titulo: "Embeddings e representações vetoriais"
modulo: "1 — Fundamentos: do texto ao Transformer"
tipo: teorica
semana: 2
duracao_min: 120
versao: v2
---

# Aula 3 — Embeddings e representações vetoriais

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (folha de diagnóstico, saída da demo, hipótese escrita), não conversas
> descartáveis com um chatbot. O roteiro de fala vive em `roteiro.md`; a especificação dos
> slides em `instructions-slides.md`.

> **Rebalanceamento V2.** A aula abre por **três sintomas**: uma busca que não devolve o documento
> que está na base, `banco` com um vetor só, e a analogia que funciona no modelo baixado e falha no
> modelo do Lab 1. Dois se resolvem hoje; o terceiro fica **explicitamente em aberto** e é a dívida
> que a Aula 6 paga. A matemática entra como fundamento nomeado, com a derivação completa no
> apêndice do deck (itens A.1 a A.5). O índice do apêndice está ao fim deste plano. Carga horária,
> numeração e objetivos de aprendizagem permanecem os da V1.

## 1. Objetivo da aula

Fechar a lacuna que a Aula 2 abriu: o tokenizador entrega ao modelo uma lista de inteiros, e um
inteiro não carrega semelhança nenhuma. Esta aula mostra como a semelhança entra na representação —
pela geometria de um espaço vetorial denso, aprendido como subproduto de uma tarefa que ninguém quer
resolver por si mesma. O aluno sai capaz de **diagnosticar** uma falha de representação (busca que
não recupera, vetor que não separa sentidos, analogia que não sobrevive ao corpus pequeno) e dizer
**que evidência a confirmaria**.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Explicar** por que a representação one-hot impede generalização, partindo da ortogonalidade dos
   vetores e do cosseno nulo entre quaisquer duas palavras distintas.
2. **Enunciar** a hipótese distribucional e **derivar** dela o critério operacional de proximidade
   entre vetores de palavras.
3. **Calcular** a similaridade de cosseno entre dois vetores e **justificar** por que se usa cosseno
   em vez de distância euclidiana em espaços de palavras.
4. **Distinguir** CBOW de skip-gram pela tarefa-proxy que cada um resolve e pelo regime de dados em
   que cada um é preferível.
5. **Explicar** a amostragem negativa como reescrita do objetivo de treino em classificação binária,
   e **estimar** a economia de custo por exemplo.
6. **Identificar** o limite do embedding estático em palavras ambíguas e **justificar** a necessidade
   de representações contextuais.

*(Idênticos aos da V1, palavra por palavra. O que a V2 acrescenta é a rastreabilidade: cada um dos
seis tem, no apêndice do deck, o item que o fundamenta — 1 → A.1, 2 → A.3, 3 → A.2, 4 → A.4,
5 → A.4, 6 → A.3 e o gancho do slide 12. O item 3 mantém o verbo "calcular" de propósito: a conta do
cosseno é curta e **é** a resposta de engenharia; retirá-la seria cortar conteúdo, não realocá-lo.)*

## 3. Teoria aplicada

Cada conceito abaixo é apresentado pelo comportamento que o motiva, com o fundamento matemático
nomeado e a derivação remetida ao apêndice.

### Bloco 1 (00:10–00:55) — Do sintoma ao espaço: o que a geometria compra

**Conceito 1 — O sintoma: a busca que não acha o documento que está lá.**
*Comportamento observável:* um time indexou dez mil documentos internos; a consulta `médico` devolve
zero resultados, e existe na base um documento inteiro sobre atendimento clínico — que escreve
`clínico`, `doutor`, `ambulatório`. O sistema calculou semelhança **zero**, e estava certo dada a
representação que recebeu.
*Causa:* a representação era um índice de palavras, e num índice duas palavras distintas são objetos
sem relação.
*Erro conceitual comum:* atribuir a falha ao ranqueamento ou à falta de sinônimos cadastrados. O
problema é anterior: a função de semelhança não tem sobre o que operar.

**Conceito 2 — Três sintomas, uma causa.**
Os três comportamentos que a aula persegue: **(a)** a busca do Conceito 1; **(b)** `banco` de
dinheiro e `banco` de praça recebendo um vetor só; **(c)** a analogia
`rei − homem + mulher ≈ rainha` funcionando no modelo baixado e falhando no modelo que a turma vai
treinar no Lab 1.
*Tese:* os três vêm da mesma falta — a representação atual não carrega noção de semelhança.
*Nota de condução:* deixar os três cartões na tela ao anunciar o plano, com o (b) marcado como
**fica em aberto**. Anunciar desde o começo que um dos três não se resolve hoje é o que dá sentido às
Aulas 5 a 7.

**Conceito 3 — Por que a intuição não basta: one-hot e a ortogonalidade mútua.**
*Comportamento observável:* o cosseno entre quaisquer duas palavras distintas é exatamente 0 —
medido na Medição 1 da demo, numa matriz 4×4 com 1,00 na diagonal e 0,00 nos doze pares restantes.
`gato`/`gatinho` tão longe quanto `gato`/`parafuso`.
*Erro conceitual comum:* achar que o problema do one-hot é o tamanho. Compressão e hashing resolvem
memória e **não** resolvem semelhança — hashing troca "nenhuma semelhança" por "semelhança
arbitrária", porque a colisão é sorteada pela função de hash e não pelo sentido.
*Fundamento:* `e_i · e_j = δ_ij`, logo a matriz de Gram é a identidade; e um modelo linear sobre
entrada one-hot tem, por palavra, parâmetros que nenhuma outra palavra atualiza. → **A.1**
*Analogia do instrutor:* one-hot é uma lista de endereços, não um mapa. Saber que `gato` mora no
4021 e `gatinho` no 4022 não diz que eles são vizinhos.

**Conceito 4 — A hipótese distribucional.**
"Uma palavra é conhecida pelas companhias que ela mantém" (Firth, 1957; formulação distribucional em
Harris, 1954). O que faz dessa frase engenharia é que ela é operacionalizável: mesmos contextos →
vetores próximos, e isso é um critério programável.
*Analogia:* o teste do *glorp* — a palavra inventada dentro de cinco frases, e a sala acerta o campo
semântico sem nunca ter visto a definição. Foi só o contexto.
*Fundamento:* a hipótese é uma afirmação sobre **distribuições condicionais de contexto**: se
`p(c|w₁) ≈ p(c|w₂)` para todo `c`, os vetores devem ficar próximos. Daí sai o critério e daí sai o
colapso dos antônimos. → **A.3**
*Erro conceitual comum:* ler a hipótese como "palavras sinônimas ficam próximas". `quente` e `frio`
ocorrem nos mesmos contextos e ficam próximos — é **predição correta** da hipótese, e é limitação
real do método.

**Conceito 5 — Vetores densos: semântica como geometria.**
`d` dimensões reais (tipicamente 50 a 1024) em vez de `|V|` binárias. Nenhuma dimensão isolada é
interpretável — não existe "a dimensão da realeza"; as direções semânticas são combinações. Como a
turma não tem Aprendizagem de Máquina pressuposta, "treinar" recebe definição operacional na hora:
ajustar números por gradiente até um erro medido parar de cair; o mecanismo formal é da Aula 12.
*Analogia:* one-hot é o índice da biblioteca; embedding é a planta do prédio, em que livros de
assunto parecido ficam na mesma ala.
*Erro conceitual comum:* procurar significado em uma dimensão específica do vetor.

**Conceito 6 — A régua: cosseno, e o que ela permite decidir.**
*Comportamento observável:* dois pares de vetores em que **cosseno e distância euclidiana ordenam ao
contrário** — o par de mesma direção e tamanhos diferentes tem cosseno 1,000 e distância 6,000; o par
de mesmo tamanho a 60° tem cosseno 0,500 e distância 5,000.
*Justificativa de engenharia:* num espaço de palavras treinado, a norma correlaciona com a
**frequência** da palavra no corpus, e frequência não é o que se compara quando a pergunta é sobre
sentido. A euclidiana mistura as duas coisas; o cosseno separa.
*Fundamento:* `cos(u,v) = (u·v)/(‖u‖‖v‖)`, com `‖u−v‖² = ‖u‖² + ‖v‖² − 2u·v` — e as duas medidas só
são equivalentes na esfera unitária. → **A.2**
*Erros conceituais comuns, dois irmãos:* ler cosseno como probabilidade (0,7 não é "70% parecido") e
comparar cossenos entre espaços vetoriais diferentes (a escala é interna a cada espaço; compara-se
ordenação, não valor).

**Conceito 7 — Analogias vetoriais, e o terceiro sintoma.**
*Comportamento observável, medido na Medição 3:* a analogia de gênero devolve a palavra esperada no
top-3; a de país→moeda **não**. A saída do script imprime `a palavra esperada apareceu no top-3: NÃO`
para a segunda.
*Leitura correta:* uma **relação** virou uma **direção** no espaço, e a mesma direção vale partindo de
vários pontos. Ninguém programou regra de gênero em lugar nenhum.
*Fundamento:* o teste é `argmax_x cos(x, b − a + c)` **excluindo `{a,b,c}`**, e com vetores
normalizados o objetivo se reduz a `cos(x,b) − cos(x,a) + cos(x,c)` — uma soma de três similaridades.
→ **A.5**
*Erro conceitual comum:* tratar a analogia como evidência de que o modelo raciocina. É regularidade
linear induzida por coocorrência, não inferência. O modelo não sabe o que é um rei.

### Bloco 2 (01:05–01:50) — Como esse vetor é aprendido, e o que ele ainda não faz

**Conceito 8 — Word2Vec: CBOW × skip-gram.**
Mikolov et al., *Efficient Estimation of Word Representations in Vector Space* (arXiv 1301.3781),
com duas arquiteturas rasas. CBOW prevê a palavra central a partir da média do contexto: mais rápido,
melhor em palavras frequentes. Skip-gram inverte — prevê cada palavra do contexto a partir da central:
mais lento por gerar mais pares, melhor em palavras raras e corpus pequeno. A janela é o outro botão:
pequena captura substituibilidade, grande captura tópico.
*Analogia:* CBOW é a prova de lacuna; skip-gram é o inverso — "dada esta palavra, que companhias ela
costuma ter?".
*Fundamento:* os dois objetivos sobre a mesma janela, e o papel de `window`, `min_count` e `negative`.
→ **A.4**
*Erro conceitual comum:* achar que CBOW e skip-gram produzem o mesmo embedding, um mais rápido que o
outro. São tarefas-proxy diferentes e os espaços têm propriedades diferentes.

**Conceito 9 — O softmax de cem mil classes e a amostragem negativa.**
*Comportamento observável:* o objetivo ingênuo normaliza sobre `|V|` classes a cada exemplo. Com
`|V| = 10⁵`, `d = 100` e `10⁹` pares, só as exponenciais do denominador dão `10¹⁴` operações por
época — não é constante ruim, é ordem de grandeza errada.
*A reescrita:* dado um par (palavra, contexto), ele é real ou sorteado? Classificação binária, com
`k` negativos por positivo de uma unigrama distorcida (frequência elevada a 3/4).
*O número:* custo por exemplo cai de `|V|` para `k+1` — com `|V| = 100 000` e `k = 5`, de 100 000
para 6, cerca de **17 mil vezes menos**.
*Fundamento:* `log σ(v_c·v_w) + Σ_i log σ(−v_{n_i}·v_w)`, cujo ponto ótimo satisfaz
`v_c·v_w = PMI(w,c) − log k` — ele **fatora implicitamente** a matriz de PMI. → **A.4**
*Erro conceitual comum:* achar que amostragem negativa é uma aproximação preguiçosa do softmax. Ela
**muda o objetivo** — quem aproxima o softmax é a NCE, que a amostragem negativa simplifica
descartando o termo de normalização. O objetivo trocado produz embeddings melhores para este fim.

**Conceito 10 — Tarefa-proxy: o objetivo de treino não é o produto.**
Este é o conceito mais transferível da aula. Ninguém quer um modelo que prevê palavras de contexto —
esse modelo é descartado. O produto é a **matriz de embedding**, que numa visão ingênua seria só um
parâmetro interno do treino. E o treino é auto-supervisionado: o rótulo vem do próprio texto, o que é
a razão de dar para treinar em corpus arbitrariamente grande.
*Analogia:* é o halterofilismo do modelo. Ninguém levanta peso porque quer que a barra suba; quer-se
o que o corpo se torna ao levantá-la.
*Erro conceitual comum:* procurar utilidade na tarefa-proxy em si. A ponte a cravar: "prever o próximo
token" é exatamente a mesma jogada, escalada — o assunto da Aula 12.

**Conceito 11 — O sintoma que hoje não se resolve: o limite do vetor estático.**
*Comportamento observável, medido na Medição 4:* os vizinhos de `bank` no modelo pré-treinado trazem
vocabulário de finanças e de margem de rio **na mesma lista**. Um vetor, dois sentidos.
*Causa:* a operação é consulta a uma tabela por ID — entra um número, sai uma linha. **A frase não
participa da conta.**
*Erro conceitual comum:* propor "treinar mais" ou "aumentar `d`". Nenhuma quantidade de dados resolve,
porque a limitação é da interface, não da capacidade — e A.3 mostra isso como equação: o que se
estima é a **mistura** das duas distribuições de contexto.
*Gancho explícito:* a saída é fazer a representação depender do contexto, e o mecanismo que faz isso
é a atenção. **Este sintoma fica aberto de propósito e fecha na Aula 6**, com
`softmax(QKᵀ/√d_k)V`. Dizer isso em voz alta é parte do conceito.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura pelo sintoma | **A busca que devolve zero com o documento na base**; recap da Aula 2 em uma linha (o texto virou `[4021, 8977, 312]`, e o ID é endereço, não quantidade); os três sintomas do dia, com o `banco` marcado como o que **não** se resolve hoje |
| 00:10 | 45 min | Bloco 1 — do sintoma ao espaço | Por que a intuição não basta: one-hot, ortogonalidade e por que hashing não resolve (A.1); hipótese distribucional e o teste do *glorp* (A.3); vetores densos e o que é "treinar"; cosseno como régua, lido e não manipulado, com o par que inverte a ordenação (A.2); analogias e o terceiro sintoma (A.5); **demo com quatro medições (12 min)** |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — como o vetor é aprendido | CBOW × skip-gram e o papel da janela (A.4); o softmax de `\|V\|` classes, a amostragem negativa e o número 100 000 → 6 (A.4); tarefa-proxy e treino auto-supervisionado; o `banco` devolvido com a evidência da Medição 4 e o gancho explícito para a Aula 6; **exercício de decisão e diagnóstico (8 min + 3 de correção)** |
| 01:50 | 10 min | Fechamento | O placar dos três sintomas — resolvido, explicado, aberto; **índice do apêndice projetado (20 s)**; ponte para a Aula 4 (Lab 1) e leitura de Mikolov com a pergunta dirigida, agora com A.5 ao lado |

*Comparação com a V1: os ~9 min de quadro em torno do cosseno e do objetivo da amostragem negativa
caíram para 0 min de manipulação algébrica conduzida — as duas fórmulas são enunciadas e lidas, e a
álgebra está em A.2 e A.4. Os minutos liberados foram para a abertura pelo sintoma, para a demo (de
10 para 12 min) e para o exercício (de 9 para 11 min). A derivação permanece integralmente disponível
em A.1–A.5, em versão mais detalhada.*

## 4. Demonstração guiada

**Demo "agora medido, não afirmado" — 12 min (00:43–00:55), `codigo/demo-embeddings.py`.**

A parte 1 não depende de rede; as partes 2 a 4 usam um modelo pré-treinado pequeno baixado por
`gensim.downloader` (cache em `~/gensim-data`, download **na véspera** — são da ordem de 100 MB e não
se faz isso na frente da turma). O script tem `--offline`, que treina um Word2Vec minúsculo sobre um
mini-corpus embutido no próprio arquivo; ele existe como contingência de rede e como demonstração de
mecânica — os vizinhos que ele produz são ruins, e isso é dito à turma.

Na V2 a demo deixa de ser ilustração e passa a ser **a evidência dos três sintomas**:

1. **Medição 1 — o zero, medido.** Vetores one-hot de quatro palavras e a matriz de cossenos entre
   todos os pares, calculada com a fórmula do slide e não com biblioteca. **É a evidência dos slides
   1 e 3 e a que não se corta.**
2. **Medição 2 — vizinhos semânticos.** `king`, `python`, `hospital` num espaço denso pré-treinado.
   A lista é o argumento: ninguém escreveu essas relações à mão. Em `python` aparecem linguagem de
   programação **e** cobra — a ambiguidade já se anuncia aqui.
3. **Medição 3 — duas analogias.** Uma de categoria forte (gênero) e uma notoriamente fraca
   (país→moeda). O script imprime os três primeiros candidatos e a linha
   `a palavra esperada apareceu no top-3: sim | NÃO`. **A analogia que falha é a parte pedagógica** —
   ela sustenta o Conceito 7 e o sintoma (c).
4. **Medição 4 — a palavra ambígua.** Vizinhos de `bank`: finanças e margem de rio na mesma lista.
   Roda **quarenta minutos antes** de o Conceito 11 ser enunciado, e a lista fica na tela para ser
   retomada lá.

**Número que a demo produz.** O número central é o **`0,00` da Medição 1**: numa matriz 4×4, `1,00`
na diagonal e `0,00` em **todos os doze pares distintos** — o cosseno do one-hot medido, não
afirmado. Ele é citado de volta no slide 1 (é literalmente o `cos = 0,00` da busca que falhou) e no
slide 3 (é a ortogonalidade, derivada em A.1). O segundo número é a linha
`a palavra esperada apareceu no top-3: NÃO` da Medição 3, citada de volta no slide 7 e no slide 14
como o sintoma (c) medido. O terceiro é qualitativo e vale como número de ordem: **quantos dos dez
vizinhos de `bank` são de finanças e quantos são de margem de rio** — o instrutor conta em voz alta e
anota no quadro, e essa contagem é citada de volta no slide 12.

Insumos preparados na véspera: modelo em cache; script rodado uma vez com a saída salva em texto,
para o caso de o ambiente não subir; e o modo `--offline` testado.

## 5. Hands-on

**Componente prático da unidade — exercício de decisão e diagnóstico (8 min de dupla + 3 de
correção, 01:39–01:50).**

Mantém os dois primeiros itens da V1 — que já eram de decisão — e **substitui o terceiro**: onde a V1
pedia "proponha um jeito de separar os dois sentidos com o ferramental de hoje" (item cuja resposta
honesta é "não dá"), a V2 pede um diagnóstico com evidência, que é o que o Lab 1 vai cobrar.

1. **Ordenar por cosseno esperado.** Cinco pares: (`médico`, `enfermeiro`), (`gato`, `parafuso`),
   (`quente`, `frio`), (`Recife`, `Fortaleza`), (`comer`, `comida`). Ordenar do cosseno mais alto ao
   mais baixo, com uma frase de justificativa por par. O par de antônimos é a armadilha: pela hipótese
   distribucional ele fica **alto**, não baixo.
2. **Escolher a janela.** Duas tarefas: (a) sugerir termos substituíveis num campo de busca;
   (b) agrupar documentos por assunto. Para cada uma, janela pequena ou grande, justificada em uma
   frase.
3. **Diagnosticar.** Um time treinou embeddings próprios num corpus de poucos megabytes e as analogias
   falham quase todas; o mesmo teste funciona no modelo baixado da internet. Nomear **duas causas
   prováveis** e, para cada uma, **que evidência do próprio notebook a confirmaria**.

*Respostas esperadas no item 3:* (i) cauda esparsa e `min_count` cortando o vocabulário — a evidência
é imprimir o tamanho do vocabulário após o treino e verificar se a palavra esperada tem vetor; se não
tem, o teste não mediu nada; (ii) o protocolo de exclusão — a evidência é rodar a mesma analogia
**sem** excluir `{a,b,c}` e observar que o vencedor passa a ser uma das entradas, o que mostra que a
margem sobre os termos triviais é pequena naquele espaço. Uma terceira resposta aceitável é o número
de épocas, desde que venha com a evidência (rodar com mais épocas e verificar que a falha persiste,
o que aponta para dado e não para otimização).

*Critério de conclusão observável:* a dupla entrega a ordenação com as cinco justificativas, as duas
escolhas de janela justificadas, e no item 3 **duas causas com a evidência de cada uma**. Nomear
causa sem propor evidência não fecha o exercício.

*Extensão para quem terminar antes (opcional):* calcular à mão o cosseno de dois pares de vetores de
três dimensões e verificar que a ordenação por cosseno e por distância euclidiana **discorda** —
é o contraexemplo de A.2, com gabarito lá.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Dependência quebrada** (gensim × scipy × numpy) | `ImportError` em `scipy.linalg.triu` ou erro de ABI do NumPy ao importar gensim | Versões pinadas no cabeçalho do script (`gensim==4.3.3`, `scipy<1.14`, `numpy<2`) e runtime reiniciado após instalar; a **Medição 1 usa só NumPy** e roda de qualquer forma — e ela é a que sustenta a abertura |
| **Download do modelo pré-treinado** lento ou indisponível | Barra de progresso travada nos primeiros segundos | Baixar na véspera (cache em `~/gensim-data`); em último caso rodar com `--offline` e dizer à turma que os vizinhos ruins são o esperado com corpus de brinquedo — é literalmente a pergunta dirigida da leitura |
| **A turma pedir a derivação em aula** | "De onde vem essa fórmula do cosseno?" ou "por que 3/4?" | Parte 4 do roteiro, cinco itens com o custo de cada um. Ordem de sacrifício declarada lá; a regra geral é remeter ao apêndice e seguir |
| **Turma sentir que "faltou rigor"** | Comentário de que a aula ficou descritiva | Projetar o apêndice por 30 s: são cinco itens, com a fatoração implícita de PMI e o contraexemplo numérico do cosseno, que a V1 não tinha em lugar nenhum. O rigor mudou de lugar e ficou consultável |
| **Turma sem Aprendizagem de Máquina** trava em "treinar" e "gradiente" | Perguntas sobre o que está sendo ajustado no Conceito 5 | Definição operacional em 2–3 frases na hora: ajustar números até um erro medido parar de cair; o mecanismo formal é da Aula 12, e isso é dito explicitamente |
| **Confusão cosseno × probabilidade** | Alguém interpreta 0,7 como "70% parecido" | Voltar ao slide, mostrar a faixa −1 a 1 e comparar **dois pares no mesmo espaço** em vez de interpretar um número isolado. A leitura errada está nomeada em A.2 |
| **Analogia que deveria funcionar falha ao vivo** | A palavra esperada não aparece no top-3 nem na categoria forte | Não consertar: é o Conceito 7. O script já imprime os candidatos, e a falha vira o argumento contra tratar analogia como raciocínio. A.5 tem a razão estatística |
| **Tempo estourar no Bloco 1** | 00:43 e ainda no Conceito 6 | Cortar a Medição 2 da execução ao vivo (fica como leitura da saída). O que **não** se corta: Medição 1, Medição 4 e o Conceito 3 |
| **A turma querer resolver o `banco` hoje** | Propostas de `banco_1`/`banco_2` ou "treina mais" | Elogiar a proposta de dois tokens e devolver a réplica: alguém tem de decidir qual é qual em cada frase, e esse alguém é o problema. Manter o sintoma aberto — fechá-lo antecipadamente esvazia a Aula 6 |

## 7. Artefatos produzidos

- **Folha de diagnóstico do exercício:** a ordenação dos cinco pares com justificativa, as duas
  escolhas de janela, e no item 3 as **duas causas com a evidência de cada uma** — fotografada ou
  digitada no repositório pessoal. É o artefato central da aula na V2, no lugar da tentativa de
  separar os sentidos de `banco`.
- Saída da demo rodada na própria máquina: a matriz de cossenos do one-hot, as listas de vizinhos, os
  candidatos das duas analogias com a linha de `sim | NÃO`, e a lista de `bank`. É o insumo do
  Checkpoint 4 do Lab 1.
- **Hipótese escrita** para a pergunta dirigida: quais analogias devem falhar num corpus de poucos
  megabytes e por quê, **citando mecanismo** (cauda esparsa, `min_count`, protocolo de exclusão) em
  vez de adjetivo. A hipótese vai para o lab e é confrontada com a medição lá.
- Anotação da contagem de vizinhos de `bank` por campo semântico, feita em voz alta pelo instrutor.
- `codigo/demo-embeddings.py` executado, com o modelo pré-treinado já em cache local **antes** da
  Aula 4.

## 8. Desafio pós-aula

Não avaliado. Três itens, na ordem:

1. **Cache pronto.** Rodar `codigo/demo-embeddings.py` uma vez na própria máquina ou no Colab, para
   que o modelo pré-treinado fique baixado antes do lab. Quem chegar na Aula 4 sem isso gasta o
   Checkpoint 1 esperando download.
2. **Cinco vizinhos seus.** Escolher cinco palavras do próprio domínio (curso, trabalho, jogo, música)
   e olhar os vizinhos que o modelo dá. Anotar um vizinho que surpreendeu e escrever duas linhas sobre
   que coocorrência do corpus explicaria aquele resultado — a linguagem de **A.3** ajuda aqui: é uma
   afirmação sobre `p(c|w)`.
3. **Leitura.** Mikolov et al., *Efficient Estimation of Word Representations in Vector Space*
   (arXiv 1301.3781) — as seções de arquitetura (CBOW e skip-gram) e a de resultados em analogia.
   **Pergunta dirigida:** no artigo o corpus tem bilhões de palavras e o vocabulário centenas de
   milhares; no Lab 1 vocês vão treinar Word2Vec num corpus de poucos megabytes. Quais analogias vão
   falhar nesse corpus pequeno, e por quê? A hipótese escrita vai para o lab — e a resposta que vale
   nomeia mecanismo, com **A.5** ao lado.

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. O que ela produz é insumo direto do Lab 1 (Aula 4), que é
avaliado dentro dos 30% de laboratórios da ementa — os pesos não são reinventados aqui:

- **Laboratórios — 30%.** Oito labs com entregável individual, entrega até uma semana após o lab,
  descartando a menor nota. O Lab 1 cobra exatamente o que esta aula fundamenta: vizinhos semânticos,
  analogias e a leitura crítica do que falhou. Quem sai desta aula sabendo **por que** a analogia
  falha em corpus pequeno responde a questão-guia 3 do lab com mecanismo, não com adjetivo.
- **Prova — 30%.** Individual, escrita, Aula 17, sobre as Aulas 1 a 16, com a distribuição
  **42 diagnóstico · 40 justificativa · 8 conceito aplicado · 10 derivação**. Desta aula, o conteúdo
  aparece principalmente como **diagnóstico e justificativa**: dado um sintoma de recuperação (a busca
  que não devolve o documento), nomear a causa na representação e a medição que a confirma; justificar
  a escolha de cosseno contra distância euclidiana citando a correlação entre norma e frequência;
  justificar a escolha de janela para uma tarefa dada; explicar por que aumentar `d` não resolve
  ambiguidade. A conta do cosseno aparece, se aparecer, como o item de **conceito aplicado** — nunca
  como o item de derivação.
- **Projeto final — 40%.** Nada é cobrado desta aula diretamente, mas a noção de espaço vetorial e de
  similaridade é o alicerce da recuperação (Aulas 18 a 20), que aparece em boa parte dos projetos —
  e **A.2** é o item que volta lá, na forma "normalizar e usar produto interno é equivalente a usar
  cosseno".

**O que a V2 muda no *como* se cobra o conteúdo desta aula**, sem mexer nos pesos:

- **A resposta sobre one-hot vale pelo mecanismo, não pela adjetivação.** "One-hot é esparso e não
  tem semântica" é a resposta da V1 e vale parcialmente. A resposta completa diz que os vetores são
  mutuamente ortogonais e que, por isso, os parâmetros de uma palavra **não são atualizados** por
  exemplos de outra — e explica por que hashing não resolve. O material está em **A.1**.
- **A resposta sobre cosseno vale pela contrapartida.** "Usa-se cosseno porque ignora a magnitude" é
  incompleta. A resposta que separa nota diz **por que** a magnitude é ruído neste espaço (norma
  correlaciona com frequência) e nomeia o caso em que as duas medidas coincidem (esfera unitária).
  **A.2** existe para tornar isso barato.
- **A resposta sobre a analogia vale pela razão, não pela ressalva.** "Analogia não prova raciocínio"
  é retórica. A resposta que separa nota diz que o objetivo é uma soma de três cossenos, que a
  exclusão de `{a,b,c}` é indispensável, e por que corpus pequeno inverte a razão sinal/ruído da
  direção da relação. Está em **A.5**.

*Observável em sala, sem nota:* ao ser questionado no fechamento, o aluno explica por que `quente` e
`frio` ficam próximos num espaço distribucional **citando a distribuição de contexto**, e diz por que
aumentar a dimensão do embedding não resolve o problema do `banco` **nomeando a interface** (entra um
ID, sai uma linha; a frase não é argumento da função). Dizer "não resolve" é a V1; nomear o que
exatamente não entra na conta é a V2.

## Apêndice matemático — índice

Cinco itens, nos slides 15 a 19 do deck. É o mapa que o professor consulta antes da aula para saber
o que tem preparado, e o que a turma leva para estudar.

| Item | O que desenvolve | Apontado do |
|---|---|---|
| **A.1** | One-hot: `e_i · e_j = δ_ij` derivado, a matriz de Gram como identidade, `‖e_i − e_j‖ = √2` para todo par distinto, a prova de que os parâmetros de uma palavra não são atualizados por outra, a contagem de memória (200 KB contra 400 bytes) e **por que hashing não resolve** — troca ausência de semelhança por semelhança arbitrária. | slides 1 e 3 |
| **A.2** | Cosseno derivado de `⟨u,v⟩ = ‖u‖‖v‖cos θ`, faixa por Cauchy–Schwarz, invariância de escala, a relação exata com a distância euclidiana, o **contraexemplo numérico que inverte a ordenação** (1,000/0,500 contra 6,000/5,000), a equivalência na esfera unitária — que é o fundamento operacional da Aula 18 — e as duas leituras erradas nomeadas. | slide 6 |
| **A.3** | A hipótese distribucional como afirmação sobre `p(c\|w)`; a matriz de coocorrência, por que a contagem crua falha e a PMI como correção, com exemplo numérico (`log 8 ≈ 2,08`); a ponte com a fatoração implícita do Word2Vec; e **o colapso dos antônimos como teorema da hipótese**, não como bug. Mais o caso da palavra ambígua escrito como mistura de distribuições — o `banco` em equação. | slide 4 |
| **A.4** | Skip-gram: o objetivo ingênuo com softmax sobre `\|V\|` e a conta do inviável (`10¹⁴` operações por época); a reescrita binária com `k` negativos; **o que a amostragem negativa aproxima** — não o softmax, e sim a fatoração de `PMI(w,c) − log k` (Levy & Goldberg, 2014); o expoente 3/4 quantificado (razão 100 → 31,6); a contagem de custo `\|V\|/(k+1) ≈ 16 667`; e a tabela de **o que cada hiperparâmetro controla no objetivo**, com `min_count` tratado como decisão semântica. | slides 9 e 10 |
| **A.5** | Analogias: o objetivo `argmax_x cos(x, b−a+c)` com a exclusão de `{a,b,c}`; a decomposição em `cos(x,b) − cos(x,a) + cos(x,c)`; **por que sem a exclusão o vencedor é `b` ou `c`** e o que isso significa para os números publicados; por que categorias arbitrárias (país→moeda) falham; a razão sinal/ruído da direção da relação em corpus pequeno; as **quatro coisas que a analogia não prova**; e o gabarito do item 3 do exercício. | slides 7 e 13 |
