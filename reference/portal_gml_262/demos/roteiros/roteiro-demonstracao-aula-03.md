# Aula 03 — Embeddings: veja a geometria e o objetivo que a aprende

Vetores, cosseno, contexto, negativos e limites da representação estática

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Ângulo da consulta (graus)**: valor inicial `25`.
- **Norma da consulta**: valor inicial `1`.
- **Raio da janela de contexto**: valor inicial `1`.
- **Negativos por par positivo**: valor inicial `2`.
- **Taxa de um passo de SGD**: valor inicial `0.1`.
- **Contexto de banco**: valor inicial `money`.

## 01. A busca literal encontra apenas a forma

### Fala sugerida

Buscar uma palavra exata pode perder documentos que usam sinônimos. A pequena coleção desta aula separa correspondência lexical de proximidade geométrica em vetores desenhados manualmente. Mova o Ângulo da consulta e compare o ranking vetorial com a busca literal por carro. Pergunto à turma: “Falhar na busca literal significa que o documento é irrelevante?” Não; o vocabulário pode diferir mantendo o assunto, motivando uma representação compartilhada.

### Na demonstração

Mova o Ângulo da consulta e compare o ranking vetorial com a busca literal por carro.

### No quadro branco

Consulta carro; documento automóvel; correspondência literal = 0

### Pergunta à turma

Falhar na busca literal significa que o documento é irrelevante?

### Resposta e transição

Não; o vocabulário pode diferir mantendo o assunto, motivando uma representação compartilhada.

Avance para **One-hot distingue, mas não aproxima** e relacione o resultado observado ao próximo mecanismo.

## 02. One-hot distingue, mas não aproxima

### Fala sugerida

Cada palavra ocupa uma coordenada própria no one-hot. Palavras diferentes têm produto interno zero e distância igual, independentemente de semelhança de significado. Compare carro e automóvel na matriz identidade antes de olhar os vetores densos. Pergunto à turma: “Qual informação semântica o ID ou one-hot oferece sozinho?” Nenhuma relação de proximidade; a geometria útil precisa vir de uma representação aprendida ou construída.

### Na demonstração

Compare carro e automóvel na matriz identidade antes de olhar os vetores densos.

### No quadro branco

eᵢ · eⱼ = 0 para i ≠ j

### Pergunta à turma

Qual informação semântica o ID ou one-hot oferece sozinho?

### Resposta e transição

Nenhuma relação de proximidade; a geometria útil precisa vir de uma representação aprendida ou construída.

Avance para **Conte quem aparece perto de quem** e relacione o resultado observado ao próximo mecanismo.

## 03. Conte quem aparece perto de quem

### Fala sugerida

A hipótese distribucional usa contextos de ocorrência como sinal para aprender representações. A janela escolhida define quais pares positivos são extraídos da frase de treino. Aumente Raio da janela de 1 para 3 e conte os pares que passam a ligar palavras distantes. Pergunto à turma: “Uma janela maior produz apenas mais exemplos da mesma relação?” Não; além de quantidade, ela muda as relações capturadas, incluindo associações mais distantes.

### Na demonstração

Aumente Raio da janela de 1 para 3 e conte os pares que passam a ligar palavras distantes.

### No quadro branco

Centro + raio de contexto → pares positivos

### Pergunta à turma

Uma janela maior produz apenas mais exemplos da mesma relação?

### Resposta e transição

Não; além de quantidade, ela muda as relações capturadas, incluindo associações mais distantes.

Avance para **Desenhe um espaço denso** e relacione o resultado observado ao próximo mecanismo.

## 04. Desenhe um espaço denso

### Fala sugerida

Vetores densos usam poucas coordenadas compartilhadas. Neste plano de duas dimensões, os pontos foram escolhidos à mão para tornar a conta visível; não são embeddings de um modelo real. Altere o Ângulo da consulta e observe sua direção em relação a carro, automóvel, gato e banco. Pergunto à turma: “Cada eixo precisa representar um conceito nomeável?” Não; em embeddings aprendidos, o significado é distribuído e a base pode ser rotacionada sem mudar as relações relevantes.

### Na demonstração

Altere o Ângulo da consulta e observe sua direção em relação a carro, automóvel, gato e banco.

### No quadro branco

v ∈ Rᵈ; coordenadas compartilhadas

### Pergunta à turma

Cada eixo precisa representar um conceito nomeável?

### Resposta e transição

Não; em embeddings aprendidos, o significado é distribuído e a base pode ser rotacionada sem mudar as relações relevantes.

Avance para **Calcule cosseno e produto interno** e relacione o resultado observado ao próximo mecanismo.

## 05. Calcule cosseno e produto interno

### Fala sugerida

Cosseno divide o produto interno pelas normas e mede direção. Produto interno inclui também a magnitude dos vetores. Mantenha o ângulo e dobre a Norma da consulta; confira qual medida permanece estável. Pergunto à turma: “Aumentar a norma torna o cosseno maior?” Não quando a direção é mantida; o produto interno cresce, mas a normalização cancela essa escala.

### Na demonstração

Mantenha o ângulo e dobre a Norma da consulta; confira qual medida permanece estável.

### No quadro branco

cos(q,v) = q·v/(||q|| ||v||)

### Pergunta à turma

Aumentar a norma torna o cosseno maior?

### Resposta e transição

Não quando a direção é mantida; o produto interno cresce, mas a normalização cancela essa escala.

Avance para **Ordene vizinhos e escolha uma régua** e relacione o resultado observado ao próximo mecanismo.

## 06. Ordene vizinhos e escolha uma régua

### Fala sugerida

A busca vetorial calcula uma pontuação para cada documento e ordena os candidatos. O ranking exibido resulta dos vetores didáticos, não de avaliação de relevância em produção. Gire a consulta até trocar o primeiro colocado e compare a diferença entre os dois melhores. Pergunto à turma: “O maior cosseno prova que o documento responde à pergunta?” Não; similaridade oferece candidatos, e a resposta requer conferir conteúdo e critérios de relevância.

### Na demonstração

Gire a consulta até trocar o primeiro colocado e compare a diferença entre os dois melhores.

### No quadro branco

top-k = índices das maiores similaridades

### Pergunta à turma

O maior cosseno prova que o documento responde à pergunta?

### Resposta e transição

Não; similaridade oferece candidatos, e a resposta requer conferir conteúdo e critérios de relevância.

Avance para **CBOW e skip-gram invertem a tarefa** e relacione o resultado observado ao próximo mecanismo.

## 07. CBOW e skip-gram invertem a tarefa

### Fala sugerida

CBOW usa o contexto para prever o centro; skip-gram usa o centro para prever palavras vizinhas. Em ambos, aprender vetores é uma consequência da tarefa de previsão. Mude a janela e conte quantas previsões skip-gram e quantos contextos CBOW resultam. Pergunto à turma: “O objetivo de treino diz diretamente quais documentos buscar?” Não; é uma tarefa-proxy, cuja representação precisa ser avaliada na aplicação desejada.

### Na demonstração

Mude a janela e conte quantas previsões skip-gram e quantos contextos CBOW resultam.

### No quadro branco

CBOW: contexto → centro; skip-gram: centro → contexto

### Pergunta à turma

O objetivo de treino diz diretamente quais documentos buscar?

### Resposta e transição

Não; é uma tarefa-proxy, cuja representação precisa ser avaliada na aplicação desejada.

Avance para **O custo do vocabulário inteiro** e relacione o resultado observado ao próximo mecanismo.

## 08. O custo do vocabulário inteiro

### Fala sugerida

Um softmax completo normaliza sobre todo o vocabulário. A miniatura mostra como as probabilidades dependem simultaneamente dos scores dos candidatos. Mova a consulta para aumentar o score de carro e observe as probabilidades dos demais. Pergunto à turma: “Aumentar um score pode reduzir a probabilidade de outro sem mudar seu vetor?” Sim; o denominador é compartilhado, e todas as classes competem pela massa de probabilidade.

### Na demonstração

Mova a consulta para aumentar o score de carro e observe as probabilidades dos demais.

### No quadro branco

p(j|c) = exp(uⱼ·v꜀)/soma exp(uₖ·v꜀)

### Pergunta à turma

Aumentar um score pode reduzir a probabilidade de outro sem mudar seu vetor?

### Resposta e transição

Sim; o denominador é compartilhado, e todas as classes competem pela massa de probabilidade.

Avance para **Amostragem negativa cria comparações locais** e relacione o resultado observado ao próximo mecanismo.

## 09. Amostragem negativa cria comparações locais

### Fala sugerida

O exemplo positivo recebe alvo 1 e os negativos recebem alvo 0 em perdas logísticas. Isso aproxima o centro do contexto observado e afasta exemplos amostrados segundo essa tarefa. Varie Negativos por par e compare termos da perda e esforço de cálculo. Pergunto à turma: “Os negativos são afirmações de que duas palavras nunca se relacionam?” Não; são contrastes amostrados para o objetivo de treino, sujeitos a ruído e à distribuição escolhida.

### Na demonstração

Varie Negativos por par e compare termos da perda e esforço de cálculo.

### No quadro branco

L = −log σ(v·u⁺) − soma log σ(−v·u⁻)

### Pergunta à turma

Os negativos são afirmações de que duas palavras nunca se relacionam?

### Resposta e transição

Não; são contrastes amostrados para o objetivo de treino, sujeitos a ruído e à distribuição escolhida.

Avance para **Faça um passo de atualização real** e relacione o resultado observado ao próximo mecanismo.

## 10. Faça um passo de atualização real

### Fala sugerida

A simulação calcula o gradiente da perda logística e atualiza somente o vetor central. Os vetores de contexto ficam fixos para isolar o mecanismo de um passo. Altere a taxa de SGD e compare vetor antes/depois e perda recalculada. Pergunto à turma: “Uma taxa maior sempre melhora a perda?” Não; um passo excessivo pode ultrapassar uma região útil, então é necessário conferir a perda após atualizar.

### Na demonstração

Altere a taxa de SGD e compare vetor antes/depois e perda recalculada.

### No quadro branco

v novo = v antigo − η∇ᵥL

### Pergunta à turma

Uma taxa maior sempre melhora a perda?

### Resposta e transição

Não; um passo excessivo pode ultrapassar uma região útil, então é necessário conferir a perda após atualizar.

Avance para **Analogia é uma hipótese geométrica** e relacione o resultado observado ao próximo mecanismo.

## 11. Analogia é uma hipótese geométrica

### Fala sugerida

Somar e subtrair vetores propõe uma direção relacional no espaço. Os vetores de rei, rainha, homem e mulher desta miniatura foram construídos para exibir a operação, sem provar raciocínio linguístico. Compare o vetor calculado com a resposta esperada e observe a origem manual dos pontos. Pergunto à turma: “Acertar uma analogia demonstra compreensão geral?” Não; é um resultado localizado e precisa ser testado em exemplos e relações que não foram escolhidos para funcionar.

### Na demonstração

Compare o vetor calculado com a resposta esperada e observe a origem manual dos pontos.

### No quadro branco

rei − homem + mulher ≈ rainha

### Pergunta à turma

Acertar uma analogia demonstra compreensão geral?

### Resposta e transição

Não; é um resultado localizado e precisa ser testado em exemplos e relações que não foram escolhidos para funcionar.

Avance para **Um vetor estático mistura sentidos** e relacione o resultado observado ao próximo mecanismo.

## 12. Um vetor estático mistura sentidos

### Fala sugerida

No embedding estático, banco tem o mesmo vetor na frase financeira e na frase sobre a praça. Uma representação contextual pode depender da frase, mas a mudança exibida aqui é apenas uma ilustração manual. Troque Contexto de banco e compare o ponto estático com a representação contextual ilustrativa. Pergunto à turma: “Atenção é o único mecanismo capaz de contextualizar?” Não; redes recorrentes também produzem representações dependentes do contexto, como veremos na próxima sequência de aulas.

### Na demonstração

Troque Contexto de banco e compare o ponto estático com a representação contextual ilustrativa.

### No quadro branco

v estático(banco) = constante; h(banco, contexto) pode variar

### Pergunta à turma

Atenção é o único mecanismo capaz de contextualizar?

### Resposta e transição

Não; redes recorrentes também produzem representações dependentes do contexto, como veremos na próxima sequência de aulas.
