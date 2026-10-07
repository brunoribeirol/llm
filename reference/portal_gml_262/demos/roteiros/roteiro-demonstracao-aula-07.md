# Aula 07 — O bloco moderno: posição, normalização e caminhos residuais

Do código de posição ao RoPE, com vetores e contas inspecionáveis

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Posição da query m**: valor inicial `3`.
- **Distância n − m**: valor inicial `2`.
- **Frequência angular θ**: valor inicial `0.25`.
- **Profundidade da cadeia**: valor inicial `20`.
- **Ganho da transformação por camada**: valor inicial `0.8`.
- **Deslocamento comum do vetor**: valor inicial `0`.
- **Dimensão d do modelo**: valor inicial `32`.
- **Normalização**: valor inicial `layer`.

## 01. Sem posição, o conjunto troca de ordem

### Fala sugerida

Self-attention sem informação posicional é equivariante a permutações: reordenar entradas reordena as saídas. A máscara causal restringe acesso, mas não é um código explícito de distância ou posição. Mova Posição e observe que os vetores de conteúdo sem posição permanecem idênticos. Pergunto à turma: “A máscara triangular equivale a adicionar um vetor posicional?” Não; ela define acessibilidade, enquanto uma codificação posicional fornece informação adicional sobre posição ou distância.

### Na demonstração

Mova Posição e observe que os vetores de conteúdo sem posição permanecem idênticos.

### No quadro branco

Sem posição: Attention(PX) = P Attention(X), com máscara também compatível

### Pergunta à turma

A máscara triangular equivale a adicionar um vetor posicional?

### Resposta e transição

Não; ela define acessibilidade, enquanto uma codificação posicional fornece informação adicional sobre posição ou distância.

Avance para **Some um código senoidal** e relacione o resultado observado ao próximo mecanismo.

## 02. Some um código senoidal

### Fala sugerida

Canais alternam seno e cosseno com frequências diferentes. A demonstração calcula quatro canais para comparar posições sem depender de uma tabela aprendida. Mova Posição e observe o código de quatro números e o vetor de entrada após a soma. Pergunto à turma: “O código é aprendido por gradiente?” Na versão senoidal original, ele é calculado por fórmula; os demais parâmetros aprendem a usá-lo.

### Na demonstração

Mova Posição e observe o código de quatro números e o vetor de entrada após a soma.

### No quadro branco

PE(pos,2i)=sin(pos/10000^(2i/d)); PE(pos,2i+1)=cos(...)

### Pergunta à turma

O código é aprendido por gradiente?

### Resposta e transição

Na versão senoidal original, ele é calculado por fórmula; os demais parâmetros aprendem a usá-lo.

Avance para **Uma tabela aprendida tem um domínio** e relacione o resultado observado ao próximo mecanismo.

## 03. Uma tabela aprendida tem um domínio

### Fala sugerida

Posições aprendidas são entradas de uma tabela ajustada no treino. A miniatura fixa oito posições para tornar visível o caso de índice além da tabela, sem fingir que esses números foram treinados. Mova Posição de 7 para 8 e identifique a ausência de uma entrada definida. Pergunto à turma: “Qual diferença prática aparece fora do comprimento da tabela?” A consulta direta deixa de estar definida; ampliar ou adaptar o método requer uma decisão adicional.

### Na demonstração

Mova Posição de 7 para 8 e identifique a ausência de uma entrada definida.

### No quadro branco

Tabela P ∈ R^(L×d); acessar posição ≥ L requer uma estratégia

### Pergunta à turma

Qual diferença prática aparece fora do comprimento da tabela?

### Resposta e transição

A consulta direta deixa de estar definida; ampliar ou adaptar o método requer uma decisão adicional.

Avance para **Gire query e key em pares** e relacione o resultado observado ao próximo mecanismo.

## 04. Gire query e key em pares

### Fala sugerida

RoPE aplica rotações a pares de coordenadas de queries e keys. Cada par pode usar uma frequência diferente; esta miniatura isola um único par 2D. Mova Posição e Frequência e observe os vetores rotacionados. Pergunto à turma: “RoPE gira os IDs dos tokens?” Não; atua nas representações projetadas de query e key usadas para calcular scores.

### Na demonstração

Mova Posição e Frequência e observe os vetores rotacionados.

### No quadro branco

q′=R(mθ)q; k′=R(nθ)k

### Pergunta à turma

RoPE gira os IDs dos tokens?

### Resposta e transição

Não; atua nas representações projetadas de query e key usadas para calcular scores.

Avance para **Meça a dependência da distância relativa** e relacione o resultado observado ao próximo mecanismo.

## 05. Meça a dependência da distância relativa

### Fala sugerida

O produto interno entre os vetores rotacionados depende da diferença entre os ângulos. Mantendo os vetores de conteúdo e a distância, deslocar ambas as posições preserva o score nesta miniatura. Mantenha Distância=2 e altere Posição de 3 a 20; confira o score constante. Pergunto à turma: “O score deve mudar ao deslocar as duas posições igualmente?” Não neste par com o mesmo conteúdo e frequência; a rotação comum preserva o produto interno.

### Na demonstração

Mantenha Distância=2 e altere Posição de 3 a 20; confira o score constante.

### No quadro branco

R(mθ)q · R(nθ)k = q · R((n−m)θ)k

### Pergunta à turma

O score deve mudar ao deslocar as duas posições igualmente?

### Resposta e transição

Não neste par com o mesmo conteúdo e frequência; a rotação comum preserva o produto interno.

Avance para **Não confunda fórmula com extrapolação garantida** e relacione o resultado observado ao próximo mecanismo.

## 06. Não confunda fórmula com extrapolação garantida

### Fala sugerida

Uma fórmula definida para posições longas não garante qualidade fora do treino. Frequências, distribuição de distâncias e comportamento aprendido continuam relevantes. Aumente Distância e observe a oscilação do score; compare distâncias diferentes com scores parecidos. Pergunto à turma: “RoPE elimina a necessidade de avaliar contextos longos?” Não; a generalização depende do modelo e dos dados, e precisa ser medida.

### Na demonstração

Aumente Distância e observe a oscilação do score; compare distâncias diferentes com scores parecidos.

### No quadro branco

Definido numericamente ≠ validado empiricamente

### Pergunta à turma

RoPE elimina a necessidade de avaliar contextos longos?

### Resposta e transição

Não; a generalização depende do modelo e dos dados, e precisa ser medida.

Avance para **Abra o caminho residual** e relacione o resultado observado ao próximo mecanismo.

## 07. Abra o caminho residual

### Fala sugerida

O residual soma a entrada à transformação do bloco. A conta escalar compara uma cadeia de ganhos com uma cadeia que inclui um caminho identidade, sem prometer estabilidade de uma rede inteira. Varie Profundidade e Ganho; compare g^L e (1+g)^L em escala logarítmica. Pergunto à turma: “Ter residual significa que gradientes nunca explodem?” Não; ele cria um caminho direto, mas o produto total ainda pode crescer ou sofrer cancelamentos.

### Na demonstração

Varie Profundidade e Ganho; compare g^L e (1+g)^L em escala logarítmica.

### No quadro branco

x′=x+F(x); Jacobiano = I+J_F

### Pergunta à turma

Ter residual significa que gradientes nunca explodem?

### Resposta e transição

Não; ele cria um caminho direto, mas o produto total ainda pode crescer ou sofrer cancelamentos.

Avance para **LayerNorm centraliza e escala** e relacione o resultado observado ao próximo mecanismo.

## 08. LayerNorm centraliza e escala

### Fala sugerida

LayerNorm subtrai a média e divide pelo desvio padrão de cada vetor. A miniatura omite parâmetros afins aprendidos para destacar o mecanismo. Aumente Deslocamento comum e observe que os valores normalizados permanecem praticamente iguais. Pergunto à turma: “Adicionar a mesma constante a todos os canais muda esta LayerNorm sem affine?” Não, salvo arredondamentos e epsilon; a centralização remove esse deslocamento.

### Na demonstração

Aumente Deslocamento comum e observe que os valores normalizados permanecem praticamente iguais.

### No quadro branco

LN(x)=(x−média)/sqrt(variância+ε)

### Pergunta à turma

Adicionar a mesma constante a todos os canais muda esta LayerNorm sem affine?

### Resposta e transição

Não, salvo arredondamentos e epsilon; a centralização remove esse deslocamento.

Avance para **RMSNorm remove a centralização** e relacione o resultado observado ao próximo mecanismo.

## 09. RMSNorm remove a centralização

### Fala sugerida

RMSNorm divide pela raiz da média dos quadrados e não subtrai a média. Por isso deslocar todos os canais muda a direção normalizada de forma diferente de LayerNorm. Alterne Normalização e aumente Deslocamento comum; compare média e RMS da saída. Pergunto à turma: “RMSNorm obriga a média da saída a ser zero?” Não; controla escala pela RMS, preservando componentes de média que LayerNorm retiraria.

### Na demonstração

Alterne Normalização e aumente Deslocamento comum; compare média e RMS da saída.

### No quadro branco

RMSNorm(x)=x/sqrt(média(x²)+ε)

### Pergunta à turma

RMSNorm obriga a média da saída a ser zero?

### Resposta e transição

Não; controla escala pela RMS, preservando componentes de média que LayerNorm retiraria.

Avance para **Posicione a norma no bloco** e relacione o resultado observado ao próximo mecanismo.

## 10. Posicione a norma no bloco

### Fala sugerida

No pré-norm, a normalização fica dentro da transformação residual; no pós-norm, normaliza-se o resultado da soma. Isso altera o caminho de propagação e o comportamento de otimização. Compare os dois diagramas e a mesma transformação escalar sob os dois arranjos. Pergunto à turma: “Trocar a posição da norma é apenas reorganizar a escrita?” Não; normalização é uma operação não linear e a ordem de composição muda a função calculada.

### Na demonstração

Compare os dois diagramas e a mesma transformação escalar sob os dois arranjos.

### No quadro branco

Pré: x+F(Norm(x)); pós: Norm(x+F(x))

### Pergunta à turma

Trocar a posição da norma é apenas reorganizar a escrita?

### Resposta e transição

Não; normalização é uma operação não linear e a ordem de composição muda a função calculada.

Avance para **Conte os pesos da FFN** e relacione o resultado observado ao próximo mecanismo.

## 11. Conte os pesos da FFN

### Fala sugerida

Uma FFN com expansão 4d possui aproximadamente 8d² pesos nas duas projeções, sem biases. Uma FFN com gate possui três projeções e pode usar dimensão intermediária próxima de 8d/3 para orçamento semelhante. Dobre Dimensão e compare a contagem quadrática dos pesos. Pergunto à turma: “Dobrar d dobra a quantidade de pesos da FFN?” Com a expansão proporcional a d, a quantidade cresce quatro vezes.

### Na demonstração

Dobre Dimensão e compare a contagem quadrática dos pesos.

### No quadro branco

FFN: 2dm; gated FFN: 3dm; m≈8d/3 para 8d²

### Pergunta à turma

Dobrar d dobra a quantidade de pesos da FFN?

### Resposta e transição

Com a expansão proporcional a d, a quantidade cresce quatro vezes.

Avance para **Reconstrua um bloco moderno** e relacione o resultado observado ao próximo mecanismo.

## 12. Reconstrua um bloco moderno

### Fala sugerida

Posição, normalização, atenção, residual e FFN respondem a funções distintas. O diagrama reúne escolhas comuns sem afirmar que todo modelo moderno usa a mesma combinação. Escolha a norma, ajuste dimensão e siga os dois caminhos residuais até a saída. Pergunto à turma: “Qual componente troca informação entre posições e qual transforma canais em cada posição?” A atenção mistura posições; a FFN aplica a mesma transformação de canais separadamente em cada posição.

### Na demonstração

Escolha a norma, ajuste dimensão e siga os dois caminhos residuais até a saída.

### No quadro branco

x → norma → atenção → soma → norma → FFN → soma

### Pergunta à turma

Qual componente troca informação entre posições e qual transforma canais em cada posição?

### Resposta e transição

A atenção mistura posições; a FFN aplica a mesma transformação de canais separadamente em cada posição.
