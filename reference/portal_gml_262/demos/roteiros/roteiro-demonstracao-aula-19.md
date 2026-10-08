# Aula 19 — Recuperação híbrida, reranking e métricas

Compare busca lexical e vetorial, funda posições e localize onde a evidência se perdeu.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Consulta**: valor inicial `prazo`.
- **Resultados entregues**: valor inicial `3`.
- **Candidatos para reranking**: valor inicial `4`.
- **Constante do RRF**: valor inicial `20`.
- **Saturação BM25 k1**: valor inicial `1.2`.
- **Normalização de tamanho b**: valor inicial `0.7`.

## 01. O erro começa com a consulta

### Fala sugerida

Não existe documento relevante em abstrato. Os rótulos foram definidos manualmente neste acervo didático. Eles não são escores produzidos pela busca.

### Na demonstração

Troque a consulta e leia os rótulos de relevância.

### No quadro branco

Relevância depende da consulta

### Pergunta à turma

Uma busca sem resultados exatos é sempre ruim?

### Resposta e transição

Não; uma paráfrase relevante pode não repetir as palavras da consulta.

Avance para **O índice invertido encontra termos** e relacione o resultado observado ao próximo mecanismo.

## 02. O índice invertido encontra termos

### Fala sugerida

Aqui a correspondência literal é uma vantagem. Uma representação densa pode diluir um identificador raro. A lista de ocorrências explica por que o documento entrou como candidato.

### Na demonstração

Escolha a consulta de código e localize o termo nos documentos.

### No quadro branco

termo → lista de documentos

### Pergunta à turma

Por que um código favorece busca lexical?

### Resposta e transição

Porque a identidade exata do token pode ser o critério de relevância.

Avance para **BM25 satura frequência** e relacione o resultado observado ao próximo mecanismo.

## 03. BM25 satura frequência

### Fala sugerida

As frequências vêm dos textos visíveis. O cálculo é feito localmente com uma variante positiva de IDF. Os parâmetros mudam a sensibilidade, não os rótulos de relevância.

### Na demonstração

Varie k1 e b e acompanhe os escores calculados.

### No quadro branco

IDF × tf(k1+1)/(tf+k1(1−b+b|d|/média))

### Pergunta à turma

Repetir uma palavra cem vezes multiplica linearmente o score?

### Resposta e transição

Não; a saturação limita o ganho de frequência.

Avance para **Busca densa encontra outra vizinhança** e relacione o resultado observado ao próximo mecanismo.

## 04. Busca densa encontra outra vizinhança

### Fala sugerida

Os vetores foram escolhidos para tornar os erros compreensíveis. Não são resultados de um modelo de embedding. Compare agora o que o lexical perdeu e o denso recuperou.

### Na demonstração

Troque a consulta e compare os cossenos.

### No quadro branco

score denso = cosseno(q,d)

### Pergunta à turma

Um bom resultado neste espaço prova qualidade de um encoder?

### Resposta e transição

Não; é uma simulação geométrica explícita.

Avance para **Os erros podem se complementar** e relacione o resultado observado ao próximo mecanismo.

## 05. Os erros podem se complementar

### Fala sugerida

Um escore BM25 não tem a mesma unidade de um cosseno. Somá-los diretamente cria uma ponderação implícita arbitrária. Posições oferecem uma forma simples de fusão.

### Na demonstração

Troque entre código e auxílio e compare posições.

### No quadro branco

Lexical e denso: sinais diferentes

### Pergunta à turma

Por que não somar os scores sem tratamento?

### Resposta e transição

Porque suas escalas e distribuições não são comparáveis.

Avance para **RRF soma evidência de posição** e relacione o resultado observado ao próximo mecanismo.

## 06. RRF soma evidência de posição

### Fala sugerida

As posições começam em um. Uma constante maior suaviza diferenças entre primeiras posições. A fusão não usa o rótulo de relevância.

### Na demonstração

Mude a constante e calcule a contribuição de cada ranking.

### No quadro branco

RRF(d)=Σ listas 1/(c+rank(d))

### Pergunta à turma

RRF precisa de scores calibrados?

### Resposta e transição

Não; usa posições, embora ainda exija escolher rankings e parâmetros.

Avance para **Bi-encoder calcula separado** e relacione o resultado observado ao próximo mecanismo.

## 07. Bi-encoder calcula separado

### Fala sugerida

O benefício do bi-encoder está na reutilização do documento. O segundo estágio paga processamento conjunto para poucos candidatos. A figura não executa redes neurais reais.

### Na demonstração

Compare os caminhos e conte pares candidatos.

### No quadro branco

Bi: f(q),g(d); cross: h(q,d)

### Pergunta à turma

Por que não aplicar cross-encoder ao acervo inteiro sempre?

### Resposta e transição

Porque o custo de avaliar todos os pares pode ser alto.

Avance para **Reranking só reordena candidatos** e relacione o resultado observado ao próximo mecanismo.

## 08. Reranking só reordena candidatos

### Fala sugerida

Esta regra não é um cross-encoder treinado. Ela permite observar a limitação estrutural do segundo estágio. Um documento perdido na recuperação não pode reaparecer por reordenação.

### Na demonstração

Reduza candidatos e observe se o documento relevante desaparece.

### No quadro branco

Saída do reranker ⊆ candidatos

### Pergunta à turma

Reranking pode recuperar um documento fora dos candidatos?

### Resposta e transição

Não, a menos que o sistema faça uma nova busca.

Avance para **Precisão e recall respondem perguntas distintas** e relacione o resultado observado ao próximo mecanismo.

## 09. Precisão e recall respondem perguntas distintas

### Fala sugerida

Mudar k altera o compromisso entre cobertura e ruído. Um ranking pode ter boa precisão e perder evidências necessárias. Para uma consulta mostramos RR; MRR exige média sobre consultas.

### Na demonstração

Varie k e calcule os três valores.

### No quadro branco

P@k=acertos/k; R@k=acertos/total relevantes; RR=1/primeiro relevante

### Pergunta à turma

Precisão alta garante recall alto?

### Resposta e transição

Não; recuperar um relevante entre muitos possíveis pode ter precisão perfeita e recall baixo.

Avance para **nDCG observa a ordem inteira** e relacione o resultado observado ao próximo mecanismo.

## 10. nDCG observa a ordem inteira

### Fala sugerida

Neste exemplo os rótulos são binários. Relevância graduada permitiria pesos diferentes. A referência ideal depende de quantos documentos relevantes existem.

### Na demonstração

Compare ranking atual com o ideal para o mesmo k.

### No quadro branco

DCG=Σ relᵢ/log₂(i+1); nDCG=DCG/IDCG

### Pergunta à turma

nDCG igual a um significa o quê?

### Resposta e transição

Que a ordenação alcançou o ganho ideal para os rótulos e corte considerados.

Avance para **O teto vem da recuperação inicial** e relacione o resultado observado ao próximo mecanismo.

## 11. O teto vem da recuperação inicial

### Fala sugerida

Esta invariância é matemática. A melhoria no top-k menor é uma questão empírica. São dois tipos de afirmação que não devemos misturar.

### Na demonstração

Compare recall dos candidatos antes e depois da reordenação.

### No quadro branco

Recall@K_candidatos é invariante à permutação

### Pergunta à turma

O reranking é obrigado a melhorar recall@3?

### Resposta e transição

Não; ele só tem a possibilidade de melhorar as posições dentro do conjunto.

Avance para **Documentos são dados, não instruções** e relacione o resultado observado ao próximo mecanismo.

## 12. Documentos são dados, não instruções

### Fala sugerida

A instrução maliciosa aqui é apenas um exemplo visível. Não precisamos executá-la para entender o risco. O sistema deve separar conteúdo documental de instruções autorizadas.

### Na demonstração

Inspecione o cartão de conteúdo não confiável.

### No quadro branco

Fonte recuperada fornece evidência, não política do sistema

### Pergunta à turma

Uma fonte relevante pode conter uma instrução indevida?

### Resposta e transição

Sim; relevância de busca não confere autoridade operacional.

Avance para **Depurar da entrada para a resposta** e relacione o resultado observado ao próximo mecanismo.

## 13. Depurar da entrada para a resposta

### Fala sugerida

Antes de trocar o modelo gerador, verifiquem se ele recebeu a evidência. Antes de trocar o reranker, verifiquem se o candidato existia. Essa ordem evita mudanças caras sem relação com a causa.

### Na demonstração

Escolha uma consulta e explique o primeiro estágio em que o alvo se perde.

### No quadro branco

Consulta → cobertura → ordem → contexto → resposta

### Pergunta à turma

Qual ajuste investigar quando o alvo não aparece entre candidatos?

### Resposta e transição

Consulta, chunking, representação e estratégia de recuperação inicial.
