---
aula: 6
titulo: "Transformer I: self-attention e a arquitetura"
modulo: "1 — Fundamentos: do texto ao Transformer"
tipo: teorica
semana: 3
duracao_min: 120
versao: v2
---

# Aula 6 — Transformer I: self-attention e a arquitetura

> **Sobre o material.** A aula combina explicações, uma demonstração em NumPy e um
> exercício em dupla. Os alunos registram suas observações para retomar no laboratório.
> A fala sugerida está em `roteiro.md`; a especificação dos slides, em `instructions-slides.md`.

> **Organização.** Os exemplos vêm antes da notação. A fórmula é apresentada e explicada
> em aula; as derivações completas ficam nos itens A.1 a A.6 do apêndice dos slides.
> Os temas, os objetivos de aprendizagem e a duração de 120 minutos são mantidos.

## 1. Objetivo da aula

Compreender como a self-attention usa o contexto para produzir a representação de cada
token e como ela se encaixa no Transformer. Usar a fórmula de atenção para investigar
problemas de escala, máscara causal e consumo de memória.

## 2. Resultados de aprendizagem

Ao final da aula, o aluno deverá ser capaz de:

1. **Explicar** os papéis de Q, K e V e por que as três projeções vêm da mesma entrada
   na self-attention.
2. **Enunciar** `Attention(Q,K,V) = softmax(QKᵀ/√d_k)V` e **descrever** a função de cada termo.
3. **Investigar** a saturação do softmax como possível causa de dificuldade no treinamento
   e **justificar** o fator de escala com o argumento desenvolvido em A.2.
4. **Reconhecer** sinais de possível vazamento de futuro e **verificar** a ordem entre
   máscara e softmax, com apoio da análise em A.3.
5. **Descrever** o que as várias cabeças de atenção acrescentam e **explicar** por que
   um mapa de pesos, sozinho, não determina a função de uma cabeça no modelo.
6. **Estimar** a memória ocupada pela matriz de atenção e **relacionar** essa estimativa
   ao comprimento de contexto que cabe no hardware disponível.
7. **Localizar** encoder, decoder, self-attention causal e cross-attention no diagrama
   e **explicar** a geração de texto token a token.

## 3. Teoria aplicada

**Conhecimentos retomados:** vetores, produto escalar, multiplicação de matrizes,
embeddings e estado oculto de uma RNN. Não pressupor uma disciplina anterior de
aprendizagem de máquina. Explicar perda, gradiente e saturação quando aparecerem.

### Abertura (00:00–00:10) — Como incluir o contexto

**1. A mesma palavra em dois contextos.** Retomar as frases do exemplo de embeddings:
“o banco do rio estava cheio” e “o banco do centro estava fechado”. Esclarecer que, na
primeira, banco se refere a uma formação de areia no rio. Na tabela de embeddings
estáticos, a palavra recebe o mesmo vetor nas duas frases. Um classificador que recebe
apenas esse vetor não tem como distinguir os usos pelo contexto.

**2. O que a RNN já permite fazer.** Retomar a Aula 5, “Modelos sequenciais e o nascimento
da atenção”. A RNN incorpora contexto ao atualizar seu estado oculto. O desafio está no
caminho entre posições distantes e na dependência sequencial: da posição 1 à 50, são
49 atualizações. A atenção permite consultar diretamente outras posições.

**Cuidado na explicação:** a RNN consegue produzir representações contextuais. Apresentar
suas limitações sem sugerir que contexto só se tornou possível com o Transformer.

### Bloco 1 (00:10–00:55) — Entendendo a self-attention

**3. Combinação de informações.** Cada posição recebe uma média ponderada de conteúdos
da própria sequência. Explicar “peso” com um exemplo de contribuições de 60%, 30% e 10%.
Inicialmente, considerar atenção sem máscara: todas as posições podem participar.
O mesmo embedding inicial pode produzir saídas diferentes conforme o contexto.

**4. Q, K e V.** Apresentar query (consulta), key (chave) e value (valor). Q e K são usados
na comparação; V fornece o conteúdo combinado. Explicar projeção linear como uma
multiplicação por uma matriz aprendida. As três projeções partem da mesma X. → **A.1**

**5. Leitura da fórmula.** Apresentar `Attention(Q,K,V) = softmax(QKᵀ/√d_k)V` e acompanhar
seus termos: comparação, ajuste de escala, cálculo dos pesos e combinação dos valores.
Definir `d_k` e softmax. Introduzir “combinação convexa” como uma média com pesos não
negativos que somam 1. A matriz de escores não precisa ser simétrica. → **A.1**

**6. O fator de escala.** Escores muito dispersos podem produzir pesos próximos de 0 e 1.
Nessa região, o softmax responde pouco a pequenas mudanças nos escores, o que pode
dificultar os ajustes de Q e K durante o treinamento. Para componentes independentes
de média zero e variância um, o desvio-padrão do produto escalar é `√d_k`: 8 para dimensão
64 e aproximadamente 22,6 para dimensão 512. São valores de dispersão, não limites dos
escores. A divisão compensa esse crescimento sob as hipóteses do exemplo. → **A.2**

**Cuidado na explicação:** um modelo maior ter perda pior é motivo para investigar, não
prova de saturação. Conferir a dimensão por cabeça, os escores, os pesos e o código da
escala. A demonstração usa vetores aleatórios; não mede o treinamento de um modelo.

### Bloco 2 (01:05–01:50) — Máscara, arquitetura e custo

**7. Máscara causal.** Ao treinar a previsão do próximo token, a saída da posição i não
pode consultar o token i+1. A máscara permite passado e presente e bloqueia o futuro
antes do softmax. Apenas zerar os pesos futuros depois da normalização deixa a soma
menor que 1 e mantém a influência dos escores futuros no denominador. Conferir os pesos,
a soma das linhas e a preservação das saídas anteriores ao alterar um token futuro. → **A.3**

**8. Multi-head attention.** Cada cabeça tem suas projeções e calcula seus pesos. As saídas
são concatenadas e projetadas novamente. Com dimensão total 512 e oito cabeças, cada uma
pode usar dimensão 64. As principais multiplicações têm custo semelhante ao de uma
cabeça larga; isso não garante o mesmo uso de memória nem o mesmo tempo de execução.
Mapas de atenção mostram pesos; atribuir uma função a uma cabeça exige outros testes. → **A.4**

**9. Comprimento e memória.** Uma matriz de atenção tem `n²` entradas por cabeça e por
sequência. Para 2.000 tokens, são 4 milhões; para 4.000, 16 milhões. Com dois bytes por
entrada, são cerca de 8 MB e 32 MB, respectivamente, só para essa matriz. Separar esse
termo do consumo total do treinamento. O cálculo da atenção tem custo `O(n²·d)`;
a memória da matriz materializada cresce como `O(n²)`, por cabeça e sequência. → **A.5**

**10. Arquitetura e geração.** Localizar encoder bidirecional, self-attention causal do
decoder e cross-attention. Nesta última, Q vem do decoder e K/V vêm do encoder.
Relacionar essa consulta à ideia vista com Bahdanau, sem confundir as fórmulas de
compatibilidade. Explicar geração autorregressiva e KV cache, que reutiliza chaves e
valores anteriores na inferência causal. Apresentar também a organização decoder-only.

### Fechamento (01:50–02:00) — Representando a posição

**11. Ordem dos tokens.** Na atenção sem informação posicional e sem máscara, permutar
os tokens apenas permuta as linhas da saída. Comparar as duas frases com cachorro e
homem e definir equivariância a permutação. A demonstração não se aplica diretamente
à atenção com máscara causal fixa. → **A.6**

Apresentar os temas da Aula 7, “Transformer II: posição, normalização e o bloco moderno”:
informação posicional, conexões residuais, normalização e rede feed-forward.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas |
|---|---|---|---|
| 00:00 | 10 min | Abertura | Embeddings estáticos, contexto e retomada da RNN; slides 1–2 |
| 00:10 | 45 min | Bloco 1 | Média ponderada, Q/K/V, fórmula e escala; slides 3–6. Demo de 12 min, das 00:43 às 00:55; slide 7 |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 | Máscara, multi-head, memória, arquitetura e geração; slides 8–12. Exercício de 8 min e correção de 3 min, das 01:39 às 01:50; slide 13 |
| 01:50 | 10 min | Fechamento | Ordem dos tokens, próxima aula e leitura; slide 14 |

## 4. Demonstração guiada

**Duração:** 12 minutos, das 00:43 às 00:55.

O script disponível é
[`../../../aulas/aula-06/codigo/demo-attention.py`](../../../aulas/aula-06/codigo/demo-attention.py).
O caminho é relativo a esta pasta; a V2 não contém uma cópia do script. Na raiz do projeto,
executar `python -X utf8 aulas/aula-06/codigo/demo-attention.py`. Requer apenas NumPy.
O argumento `--shuffle` executa somente o exemplo de permutação.

1. **Apresentar os vetores — 2 min.** Os quatro componentes e as matrizes foram definidos
   à mão para facilitar a leitura. Não são resultados de treinamento nem um exemplo
   de que dimensões de embeddings aprendidos tenham significados individuais claros.
2. **Comparar os contextos — 3 min.** Observar que “banco” recebe a mesma entrada nas
   duas frases e saídas diferentes depois da atenção.
3. **Comparar a escala — 4 min.** Para dimensões 4, 64 e 512, ler o desvio-padrão dos
   escores e a média do maior peso de cada linha, com e sem a divisão por `√d_k`.
4. **Observar a máscara — 1 min.** Localizar os zeros acima da diagonal e conferir a
   soma aproximada de 1 por linha. A explicação será retomada depois do intervalo.
5. **Permutar os tokens — 2 min.** Na atenção sem máscara e sem posição, acompanhar o
   mesmo token antes e depois da troca. Seus vetores de saída coincidem dentro da
   precisão numérica.

**Preparação:** executar o script antes da aula e salvar a saída. A leitura dos resultados
salvos substitui a execução ao vivo caso haja problema no ambiente.

## 5. Hands-on

**Exercício em dupla:** oito minutos de discussão e três de correção, das 01:39 às 01:50.
Para cada situação, registrar uma hipótese, uma verificação e o resultado esperado.

1. Um modelo com `d_model = 1024` tem perda de validação maior que uma versão com
   `d_model = 256`, usando os mesmos dados e o mesmo número de passos. Não aparecem
   valores numéricos inválidos.
2. Um modelo de linguagem tem perda quase zero no treino e gera texto incoerente.
   O programa termina sem apresentar erro.
3. Uma equipe aumenta o contexto de 2.000 para 4.000 tokens. O modelo e o tamanho do lote
   permanecem iguais, mas o treinamento passa a exceder a memória da GPU.

**Orientação para a correção:** no caso 1, investigar saturação e conferir se `d_k` mudou,
além da escala e das curvas de treino e validação. No caso 2, investigar vazamento de
futuro alterando o último token, com o sorteio do dropout desativado, e comparando as
saídas anteriores. No caso 3, conferir o crescimento de 4× no número de elementos da
matriz armazenada, distinguindo essa parcela da memória total.

As situações admitem outras causas. A resposta deve conectar a hipótese a uma verificação;
não basta associar automaticamente cada sintoma a um defeito. O gabarito comentado está
na Parte 3 do roteiro.

**Extensão opcional:** calcular a atenção com três tokens, seguindo A.1.

## 6. Riscos e contingências

| Dificuldade | Como perceber | Como conduzir |
|---|---|---|
| Confusão entre Q, K e V | A turma mistura comparação e conteúdo | Voltar às três setas que saem de X e à analogia da consulta |
| Softmax ou gradiente ainda pouco claros | A explicação de saturação não é acompanhada | Retomar os pesos 0,6/0,3/0,1 e explicar o gradiente como sensibilidade da perda aos parâmetros |
| Pergunta sobre uma derivação | Dúvida sobre dimensões, variância ou máscara | Usar a resposta curta da Parte 4 e localizar o item do apêndice; fazer a conta completa se houver tempo |
| Falha ao executar a demo | Erro de Python ou dependência ausente | Usar a saída salva e manter as comparações de contexto e escala |
| Duplas sem conseguir começar | Nenhuma hipótese após quatro minutos | Resolver uma verificação do caso 1 e deixar os demais para discussão |
| Atraso no primeiro bloco | Pouco tempo restante para a demo | Usar as saídas salvas nas medições 3 e 4; preservar as medições 1 e 2 |
| Conclusões apressadas sobre cabeças | Uma cabeça recebe um rótulo humano só pelo mapa | Distinguir o peso observado da hipótese sobre sua função; retomar os testes na Aula 27 |

## 7. Artefatos produzidos

- Tabela do exercício com situação, hipótese, verificação e resultado esperado.
- Anotação da fórmula com a função de cada termo, escrita pelo aluno.
- Saída da demonstração, caso o aluno também a execute.
- Uma dúvida registrada para retomar no Lab 2.
- Folha de cálculo com três tokens, para quem fizer a extensão opcional.

## 8. Desafio pós-aula

Atividade opcional, sem nota:

1. **Revisitar uma hipótese.** Escolher uma das situações do exercício e descrever, em
   até cinco linhas, um resultado que faria descartar a causa inicialmente proposta.
2. **Ler com apoio do apêndice.** Vaswani et al., *Attention Is All You Need*,
   [arXiv 1706.03762](https://arxiv.org/abs/1706.03762), seções 3.1–3.3. Começar pela figura
   da arquitetura; depois comparar a justificativa de `√d_k` da seção 3.2.1 com A.2 e com
   a tabela da demonstração. Que hipóteses permitem relacionar esses resultados?
3. **Explorar o código.** Alterar os vetores do vocabulário para que, na frase com “rio”,
   “banco” atribua mais peso a “cheio” que a “rio”. Registrar o que foi alterado e comparar
   os pesos antes e depois.

## 9. Critérios de avaliação

Esta aula não tem entrega avaliada. Mantêm-se os pesos da ementa: AV1 (Laboratórios 1–4
e participação 40%, prova 60%) e AV2 (Laboratórios 5–8 e entregas do projeto 40%, projeto
final 60%).

Na discussão em sala, observar se o aluno consegue explicar as operações com suas
próprias palavras, relacionar uma hipótese ao conceito adequado e propor uma verificação
coerente. Os fundamentos do apêndice apoiam essas justificativas.

O conteúdo será retomado na prova e no Lab 2, Aula 9, na implementação da atenção em
PyTorch. A ordem da máscara, as dimensões das matrizes e a leitura dos pesos são pontos
de preparação para esse laboratório.

## Apêndice matemático — índice

| Item | Conteúdo | Referência no fluxo |
|---|---|---|
| A.1 · slide 15 | Projeções, dimensões, fórmula de atenção e média ponderada | Slides 4 e 5 |
| A.2 · slide 16 | Variância dos escores, fator de escala e saturação | Slide 6 |
| A.3 · slide 17 | Máscara causal e ordem das operações | Slide 8 |
| A.4 · slide 18 | Dimensões dos tensores e custo de multi-head | Slide 9 |
| A.5 · slide 19 | Custo de cálculo, memória e comparação com a RNN | Slides 2 e 10 |
| A.6 · slide 20 | Equivariância a permutação, sem máscara e sem posição | Slide 14 |
