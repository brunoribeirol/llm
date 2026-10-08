# Aula 09 — Lab 2: mini-GPT, dos shapes à geração

Atenção causal calculada e uma pequena cabeça treinada no navegador

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Comprimento T da sequência**: valor inicial `4`.
- **Dimensão de embedding**: valor inicial `16`.
- **Número de cabeças**: valor inicial `4`.
- **Dividir scores por √d_head**: valor inicial `True`.
- **Aplicar máscara causal antes do softmax**: valor inicial `True`.
- **Passos de treino da cabeça didática**: valor inicial `10`.
- **Taxa de aprendizado da cabeça**: valor inicial `0.2`.
- **Temperatura da geração ilustrativa**: valor inicial `1`.

## 01. Construa entrada e alvo deslocados

### Fala sugerida

Uma sequência fornece várias previsões de próximo token: cada entrada aponta para o token seguinte. O exemplo usa caracteres de uma frase fixa e separa o último alvo da entrada. Aumente T e confira os pares x e y em cada posição. Pergunto à turma: “Usar o mesmo token como entrada e alvo ensina a prever o próximo?” Não; cria uma tarefa de reconstrução trivial diferente do deslocamento causal desejado.

### Na demonstração

Aumente T e confira os pares x e y em cada posição.

### No quadro branco

x = texto[0:T]; y = texto[1:T+1]

### Pergunta à turma

Usar o mesmo token como entrada e alvo ensina a prever o próximo?

### Resposta e transição

Não; cria uma tarefa de reconstrução trivial diferente do deslocamento causal desejado.

Avance para **Anote os shapes antes das multiplicações** e relacione o resultado observado ao próximo mecanismo.

## 02. Anote os shapes antes das multiplicações

### Fala sugerida

Cada eixo tem um papel: lote, sequência, cabeças e canais. Dimensão do modelo deve ser divisível pelo número de cabeças. Altere Dimensão e Cabeças e calcule d_head antes de ver a tabela. Pergunto à turma: “Dividir em cabeças reduz o total de canais concatenados?” Não; H × d_head continua igual à dimensão do modelo.

### Na demonstração

Altere Dimensão e Cabeças e calcule d_head antes de ver a tabela.

### No quadro branco

X:[B,T,d]; Q,K,V:[B,H,T,d/H]

### Pergunta à turma

Dividir em cabeças reduz o total de canais concatenados?

### Resposta e transição

Não; H × d_head continua igual à dimensão do modelo.

Avance para **Inspecione Q, K e V calculados** e relacione o resultado observado ao próximo mecanismo.

## 03. Inspecione Q, K e V calculados

### Fala sugerida

A miniatura usa entradas e projeções determinísticas para exibir valores reproduzíveis. Ela calcula a primeira cabeça explicitamente, enquanto as outras são representadas pelos shapes. Mude d e confira quantas coordenadas entram em cada produto da cabeça. Pergunto à turma: “Por que Q e K precisam ter a mesma largura na atenção por produto?” Porque o produto interno compara coordenadas correspondentes e soma sobre essa dimensão.

### Na demonstração

Mude d e confira quantas coordenadas entram em cada produto da cabeça.

### No quadro branco

Q=XW_Q; K=XW_K; V=XW_V

### Pergunta à turma

Por que Q e K precisam ter a mesma largura na atenção por produto?

### Resposta e transição

Porque o produto interno compara coordenadas correspondentes e soma sobre essa dimensão.

Avance para **Calcule scores e observe a escala** e relacione o resultado observado ao próximo mecanismo.

## 04. Calcule scores e observe a escala

### Fala sugerida

O produto QKᵀ gera um score para cada par de posições. Dividir por √d_head controla a escala típica quando coordenadas têm variância comparável. Desative a divisão, aumente Dimensão e compare amplitude e distribuição posterior. Pergunto à turma: “A divisão garante ausência de saturação em qualquer Q e K?” Não; é uma normalização de escala motivada estatisticamente, e os valores reais ainda dependem das representações.

### Na demonstração

Desative a divisão, aumente Dimensão e compare amplitude e distribuição posterior.

### No quadro branco

S = QKᵀ/√d_head

### Pergunta à turma

A divisão garante ausência de saturação em qualquer Q e K?

### Resposta e transição

Não; é uma normalização de escala motivada estatisticamente, e os valores reais ainda dependem das representações.

Avance para **Aplique a máscara antes da normalização** e relacione o resultado observado ao próximo mecanismo.

## 05. Aplique a máscara antes da normalização

### Fala sugerida

Scores de posições futuras recebem −∞ antes do softmax. Desligar a máscara ilustra vazamento e não representa uma configuração válida de treino causal. Desmarque e marque Máscara causal; leia as células acima da diagonal. Pergunto à turma: “Zerar pesos futuros depois do softmax conserva a soma igual a um?” Não sem renormalizar; por isso a receita padrão mascara os scores antes da normalização.

### Na demonstração

Desmarque e marque Máscara causal; leia as células acima da diagonal.

### No quadro branco

j>i ⇒ score=-∞ ⇒ exp(score)=0

### Pergunta à turma

Zerar pesos futuros depois do softmax conserva a soma igual a um?

### Resposta e transição

Não sem renormalizar; por isso a receita padrão mascara os scores antes da normalização.

Avance para **Confira a soma de cada linha** e relacione o resultado observado ao próximo mecanismo.

## 06. Confira a soma de cada linha

### Fala sugerida

Softmax é aplicado sobre as chaves de cada query, e cada linha soma um. A primeira posição causal só pode atender a si mesma. Observe a primeira linha com T=4 e causal ligado; depois compare sem máscara. Pergunto à turma: “A máscara obriga todos os pesos passados a serem iguais?” Não; ela remove futuros, enquanto os scores determinam a divisão entre posições permitidas.

### Na demonstração

Observe a primeira linha com T=4 e causal ligado; depois compare sem máscara.

### No quadro branco

Aᵢⱼ = softmax(Sᵢ,: )ⱼ; somaⱼ Aᵢⱼ=1

### Pergunta à turma

A máscara obriga todos os pesos passados a serem iguais?

### Resposta e transição

Não; ela remove futuros, enquanto os scores determinam a divisão entre posições permitidas.

Avance para **Misture os valores e una as cabeças** e relacione o resultado observado ao próximo mecanismo.

## 07. Misture os valores e una as cabeças

### Fala sugerida

Multiplicar A por V produz uma combinação ponderada de valores para cada query. Multi-head concatena resultados das cabeças e aplica uma projeção de saída. Compare uma linha de pesos com os valores e o resultado AV da primeira cabeça. Pergunto à turma: “Multi-head exige um laço Python por cabeça?” Não; os eixos de lote e cabeça permitem calcular as multiplicações de forma vetorizada.

### Na demonstração

Compare uma linha de pesos com os valores e o resultado AV da primeira cabeça.

### No quadro branco

Z=AV; MultiHead=Concat(Z₁,…,Z_H)W_O

### Pergunta à turma

Multi-head exige um laço Python por cabeça?

### Resposta e transição

Não; os eixos de lote e cabeça permitem calcular as multiplicações de forma vetorizada.

Avance para **Monte o bloco com dois residuais** e relacione o resultado observado ao próximo mecanismo.

## 08. Monte o bloco com dois residuais

### Fala sugerida

O bloco reúne atenção e FFN com caminhos residuais e normalização. O diagrama destaca pré-norm, enquanto os valores de atenção continuam os da miniatura. Siga a entrada pelos dois caminhos de soma e confirme que a largura permanece d. Pergunto à turma: “Por que residual exige shapes compatíveis?” A soma é elemento a elemento; as duas parcelas precisam representar as mesmas posições e canais.

### Na demonstração

Siga a entrada pelos dois caminhos de soma e confirme que a largura permanece d.

### No quadro branco

x′=x+Attn(Norm(x)); y=x′+FFN(Norm(x′))

### Pergunta à turma

Por que residual exige shapes compatíveis?

### Resposta e transição

A soma é elemento a elemento; as duas parcelas precisam representar as mesmas posições e canais.

Avance para **Calcule a entropia cruzada do alvo** e relacione o resultado observado ao próximo mecanismo.

## 09. Calcule a entropia cruzada do alvo

### Fala sugerida

Uma cabeça de quatro logits aprende a aumentar a probabilidade de um alvo fixo. Essa tarefa isolada permite inspecionar loss e gradiente, mas não equivale ao treino do mini-GPT completo do notebook. Coloque Passos=0 e depois 1; compare logits, probabilidade do alvo e −ln(p_alvo). Pergunto à turma: “Diminuir a perda desse único exemplo prova generalização?” Não; comprova apenas ajuste local, que deve ser separado da avaliação em dados reservados.

### Na demonstração

Coloque Passos=0 e depois 1; compare logits, probabilidade do alvo e −ln(p_alvo).

### No quadro branco

L=−log p_alvo; ∂L/∂logitⱼ=pⱼ−1[j=alvo]

### Pergunta à turma

Diminuir a perda desse único exemplo prova generalização?

### Resposta e transição

Não; comprova apenas ajuste local, que deve ser separado da avaliação em dados reservados.

Avance para **Treine e transforme perda em perplexidade** e relacione o resultado observado ao próximo mecanismo.

## 10. Treine e transforme perda em perplexidade

### Fala sugerida

Os valores da curva são recalculados a cada passo de SGD da cabeça, sem resultados de treinamento inventados. Para a mesma unidade de previsão, PPL é a exponencial da perda. Altere Passos e Taxa; confira a relação entre perda atual e perplexidade. Pergunto à turma: “Podemos chamar essa perplexidade de resultado do corpus inteiro?” Não; ela pertence ao exemplo da miniatura e não substitui a média em um conjunto de validação.

### Na demonstração

Altere Passos e Taxa; confira a relação entre perda atual e perplexidade.

### No quadro branco

PPL = exp(loss); avaliar em conjunto separado

### Pergunta à turma

Podemos chamar essa perplexidade de resultado do corpus inteiro?

### Resposta e transição

Não; ela pertence ao exemplo da miniatura e não substitui a média em um conjunto de validação.

Avance para **Avalie sem vazamento e com variabilidade** e relacione o resultado observado ao próximo mecanismo.

## 11. Avalie sem vazamento e com variabilidade

### Fala sugerida

Uma avaliação adequada desativa efeitos de treino apropriados, usa dados reservados e agrega vários lotes. Os cartões são critérios de execução do notebook, sem inventar métricas de validação no navegador. Leia os três controles de validade e associe cada um a uma fonte de erro. Pergunto à turma: “Uma única semente permite afirmar que uma arquitetura é superior?” Não; variação do treino e da amostragem pode explicar a diferença, exigindo repetições e uma comparação controlada.

### Na demonstração

Leia os três controles de validade e associe cada um a uma fonte de erro.

### No quadro branco

eval + no_grad; split por dados; média de lotes; sementes registradas

### Pergunta à turma

Uma única semente permite afirmar que uma arquitetura é superior?

### Resposta e transição

Não; variação do treino e da amostragem pode explicar a diferença, exigindo repetições e uma comparação controlada.

Avance para **Feche o laço autorregressivo** e relacione o resultado observado ao próximo mecanismo.

## 12. Feche o laço autorregressivo

### Fala sugerida

Gerar consulta a distribuição da última posição, escolhe um token, acrescenta-o ao prefixo e repete. A tela mostra uma distribuição didática e o fluxo, sem apresentar texto como saída de um GPT treinado. Varie Temperatura e confira como a distribuição do próximo token muda após o treinamento da cabeça. Pergunto à turma: “Quais erros comuns quebram esse laço?” Usar logits de todas as posições como se fossem a última, esquecer o recorte da janela ou não distinguir argmax de amostragem.

### Na demonstração

Varie Temperatura e confira como a distribuição do próximo token muda após o treinamento da cabeça.

### No quadro branco

prefixo → logits finais → escolha → concatenar → recortar contexto

### Pergunta à turma

Quais erros comuns quebram esse laço?

### Resposta e transição

Usar logits de todas as posições como se fossem a última, esquecer o recorte da janela ou não distinguir argmax de amostragem.
