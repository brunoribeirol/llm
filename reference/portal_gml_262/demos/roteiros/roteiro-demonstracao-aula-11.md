# Aula 11 — Decodificação e prompting: laboratório guiado

Da distribuição de tokens à decisão experimental; cálculos locais, sem chamadas a modelos.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Temperatura**: valor inicial `1`.
- **Top-k**: valor inicial `4`.
- **Top-p**: valor inicial `0.9`.
- **Semente da amostragem**: valor inicial `7`.
- **Exemplos no prompt**: valor inicial `2`.
- **Itens avaliados**: valor inicial `20`.

## 01. O contrato do experimento

### Fala sugerida

Vamos começar pelo registro, antes de escolher uma resposta bonita. Estes logits são pequenos para auditar cada conta. Os resultados de classificação são um cenário sintético, não uma avaliação de um LLM.

### Na demonstração

Mude a semente e observe o registro da configuração.

### No quadro branco

Entrada → configuração → saída → métrica → proveniência

### Pergunta à turma

Por que registrar o modo offline?

### Resposta e transição

Porque uma simulação testa o método e a aritmética, mas não mede a qualidade de um modelo real.

Avance para **Seis candidatos antes da escolha** e relacione o resultado observado ao próximo mecanismo.

## 02. Seis candidatos antes da escolha

### Fala sugerida

Apontem o token favorito sem chamá-lo de probabilidade. Agora comparem o escore com a coluna normalizada. A ordem coincide, mas a escala e o significado mudaram.

### Na demonstração

Compare o maior logit com a maior probabilidade.

### No quadro branco

pᵢ = exp(zᵢ/T) / Σⱼ exp(zⱼ/T)

### Pergunta à turma

Um logit negativo proíbe o token?

### Resposta e transição

Não; a exponencial é positiva e esse token mantém probabilidade não nula.

Avance para **Temperatura modifica concentração** e relacione o resultado observado ao próximo mecanismo.

## 03. Temperatura modifica concentração

### Fala sugerida

Mantenham a semente parada enquanto mudamos a temperatura. O token favorito continua favorito. O que muda é quanto espaço sobra para os demais.

### Na demonstração

Leve a temperatura de 0,3 a 1,8 e acompanhe a entropia.

### No quadro branco

H(p) = −Σ pᵢ log₂ pᵢ

### Pergunta à turma

Por que dividir probabilidades por T e renormalizar não funciona?

### Resposta e transição

O fator comum cancela; a temperatura deve agir nos logits.

Avance para **Top-k limita candidatos** e relacione o resultado observado ao próximo mecanismo.

## 04. Top-k limita candidatos

### Fala sugerida

Agora cortamos candidatos, em vez de mudar suas proporções. Um sobrevivente torna a distribuição determinística. Todos os sobreviventes recuperam a distribuição anterior.

### Na demonstração

Ajuste top-k para 1 e depois 6.

### No quadro branco

p'ᵢ = pᵢ / Σⱼ∈S pⱼ

### Pergunta à turma

Top-k 1 depende da semente?

### Resposta e transição

Não neste exemplo sem empate; a probabilidade restante é 1.

Avance para **Top-p limita massa** e relacione o resultado observado ao próximo mecanismo.

## 05. Top-p limita massa

### Fala sugerida

Sigam a soma acumulada linha a linha. A linha que ultrapassa o limite faz parte do conjunto. Excluí-la impediria atingir a massa solicitada.

### Na demonstração

Mude top-p de 0,5 a 0,95 e conte sobreviventes.

### No quadro branco

Menor m tal que Σᵢ₌₁ᵐ pᵢ ≥ p

### Pergunta à turma

O tamanho do nucleus é fixo?

### Resposta e transição

Não; depende do limiar e da concentração.

Avance para **A ordem dos filtros faz parte do contrato** e relacione o resultado observado ao próximo mecanismo.

## 06. A ordem dos filtros faz parte do contrato

### Fala sugerida

Esta escolha costuma ficar escondida na implementação. O segundo limiar se refere à massa que sobrou do primeiro corte. Bibliotecas só são comparáveis quando conhecemos essa ordem.

### Na demonstração

Use top-k 2 e top-p 0,9; compare com top-p sozinho.

### No quadro branco

T → top-k → renormalizar → top-p → renormalizar

### Pergunta à turma

O segundo corte retém 90% da massa original?

### Resposta e transição

Não necessariamente; retém pelo menos 90% da distribuição condicionada ao top-k.

Avance para **A semente explica uma realização** e relacione o resultado observado ao próximo mecanismo.

## 07. A semente explica uma realização

### Fala sugerida

Vemos uma realização, não a distribuição inteira. Uma semente explica divergências entre execuções. Um sorteio não prova que o vencedor era o token mais provável.

### Na demonstração

Troque a semente e localize u no intervalo escolhido.

### No quadro branco

F(i−1) ≤ u < F(i)

### Pergunta à turma

Amostragem é greedy?

### Resposta e transição

Não; greedy usa o máximo, enquanto amostragem pode escolher qualquer candidato de massa positiva.

Avance para **Few-shot comunica o formato** e relacione o resultado observado ao próximo mecanismo.

## 08. Few-shot comunica o formato

### Fala sugerida

Estes exemplos são contexto de inferência. Não estamos alterando pesos. Precisamos medir se ajudam no conteúdo ou somente no formato.

### Na demonstração

Aumente exemplos e leia a estimativa de tokens.

### No quadro branco

Instrução + exemplos + consulta → resposta

### Pergunta à turma

Few-shot atualiza parâmetros?

### Resposta e transição

Não; condiciona a inferência pelo contexto.

Avance para **Separar dois tipos de falha** e relacione o resultado observado ao próximo mecanismo.

## 09. Separar dois tipos de falha

### Fala sugerida

Não vamos esconder prosa livre dentro da classe errada. Corrigir formato pode tornar a interface utilizável. A soma deve permanecer igual ao tamanho do conjunto.

### Na demonstração

Mude exemplos e confira a soma das categorias.

### No quadro branco

n = acertos + erros + inválidos

### Pergunta à turma

Por que medir inválidos separadamente?

### Resposta e transição

Para identificar falhas de interface que pedem restrição de formato e validação.

Avance para **Raciocínio tem custo de saída** e relacione o resultado observado ao próximo mecanismo.

## 10. Raciocínio tem custo de saída

### Fala sugerida

Os preços exibidos são didáticos. Comparem entrada e saída separadamente. Sem ganho de acurácia, a razão não expressa eficiência positiva.

### Na demonstração

Compare as duas estratégias hipotéticas ao alterar exemplos.

### No quadro branco

Eficiência = Δ tokens / Δ pontos, se Δ pontos > 0

### Pergunta à turma

O que reportar se o ganho for zero?

### Resposta e transição

Razão não definida e custo adicional sem ganho observado.

Avance para **O conjunto limita a resolução** e relacione o resultado observado ao próximo mecanismo.

## 11. O conjunto limita a resolução

### Fala sugerida

Com vinte itens, um exemplo muda cinco pontos. Temperatura baixa não elimina a incerteza do conjunto. A aproximação não substitui uma análise pareada.

### Na demonstração

Compare n igual a 20 e 200.

### No quadro branco

Resolução = 100/n; EP ≈ √(p(1−p)/n)

### Pergunta à turma

Cinco pontos em vinte itens provam melhoria?

### Resposta e transição

Não; representam um único item e exigem examinar incerteza e casos.

Avance para **Decidir com três eixos** e relacione o resultado observado ao próximo mecanismo.

## 12. Decidir com três eixos

### Fala sugerida

Não existe vencedor universal. Uma aplicação aceita espera e outra exige resposta imediata. O relatório precisa declarar limites e proveniência.

### Na demonstração

Compare os perfis e seus tempos repetidos.

### No quadro branco

Decisão = qualidade mínima + custo + latência

### Pergunta à turma

O que levar para o projeto?

### Resposta e transição

Um protocolo com configuração, origem dos dados, repetições, métricas separadas e decisão sustentada.
