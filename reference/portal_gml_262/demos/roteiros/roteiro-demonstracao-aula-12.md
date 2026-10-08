# Aula 12 — Pré-treinamento: dados, escala e sistemas

Distribua orçamento, inspecione memória e acompanhe a fábrica de um completador.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Parâmetros (bilhões)**: valor inicial `7`.
- **Tokens de treino (bilhões)**: valor inicial `140`.
- **Lote de sequências**: valor inicial `4`.
- **Contexto (tokens)**: valor inicial `2048`.
- **Número de GPUs**: valor inicial `2`.
- **Duplicatas (%)**: valor inicial `20`.

## 01. Começar pelos recursos finitos

### Fala sugerida

N representa parâmetros e D tokens processados. Duas duplicações podem quadruplicar trabalho. Esta aproximação não é medição de hardware.

### Na demonstração

Dobre N e depois D, comparando o custo.

### No quadro branco

C ≈ 6ND FLOPs

### Pergunta à turma

Se N e D dobram, quanto cresce C?

### Resposta e transição

Cresce aproximadamente quatro vezes.

Avance para **O corpus fornece os rótulos** e relacione o resultado observado ao próximo mecanismo.

## 02. O corpus fornece os rótulos

### Fala sugerida

É o mesmo objetivo de próximo token já estudado. O rótulo existe e vem do texto. Por isso falamos em aprendizado auto-supervisionado.

### Na demonstração

Compare entrada e alvo deslocados.

### No quadro branco

entrada: a rede aprende; alvo: rede aprende EOS

### Pergunta à turma

Quem escolhe o alvo?

### Resposta e transição

O deslocamento da própria sequência de tokens.

Avance para **Mistura de dados é modelagem** e relacione o resultado observado ao próximo mecanismo.

## 03. Mistura de dados é modelagem

### Fala sugerida

Uma cópia adicional custa computação. Ela não acrescenta a mesma variedade. O volume único mostrado é uma contabilidade simples, não previsão de qualidade.

### Na demonstração

Aumente duplicatas e compare volume bruto e único.

### No quadro branco

D bruto = D único + repetições

### Pergunta à turma

Dobro de tokens significa dobro de informação?

### Resposta e transição

Não; diversidade, duplicação e qualidade importam.

Avance para **Duplicação e contaminação** e relacione o resultado observado ao próximo mecanismo.

## 04. Duplicação e contaminação

### Fala sugerida

Exemplos frequentes podem ser memorizados. Um benchmark presente no treino deixa de medir apenas generalização. Deduplicação interna e auditoria externa são complementares.

### Na demonstração

Inspecione grupos repetidos ao variar duplicatas.

### No quadro branco

Treino ∩ avaliação deve ser investigado

### Pergunta à turma

Deduplicação prova ausência de contaminação?

### Resposta e transição

Não; é preciso comparar treino com avaliação.

Avance para **De onde vem o seis** e relacione o resultado observado ao próximo mecanismo.

## 05. De onde vem o seis

### Fala sugerida

Multiplicação e adição contam separadamente. O backward propaga gradientes e calcula gradientes dos pesos. Atenção e detalhes do otimizador ficam fora desta aproximação.

### Na demonstração

Compare parcelas ao variar o modelo.

### No quadro branco

C ≈ (2N + 4N)D

### Pergunta à turma

Por que inferência custa menos por token?

### Resposta e transição

Ela não calcula backward; a aproximação é 2N por token.

Avance para **Um orçamento, vários candidatos** e relacione o resultado observado ao próximo mecanismo.

## 06. Um orçamento, vários candidatos

### Fala sugerida

Nenhum candidato recebe dinheiro extra. O mínimo depende da função assumida. Os coeficientes são didáticos, não um ajuste de modelos reais.

### Na demonstração

Mude N e D e compare candidatos de mesmo custo.

### No quadro branco

D = C/(6N); L = 1,5 + 4/√N + 17,89/√D

### Pergunta à turma

Modelo maior sempre vence com C fixo?

### Resposta e transição

Não; ele pode receber poucos tokens para seu tamanho.

Avance para **Ler o ótimo com suas premissas** e relacione o resultado observado ao próximo mecanismo.

## 07. Ler o ótimo com suas premissas

### Fala sugerida

Vinte entra como hipótese do exercício. Dados e objetivo econômico podem mudar a escolha. Um produto servido muitas vezes pode preferir um modelo menor mais treinado.

### Na demonstração

Compare o ponto atual com a referência calculada.

### No quadro branco

N* ≈ √(C/120); D* ≈ 20N*

### Pergunta à turma

D/N muito maior que vinte está errado?

### Resposta e transição

Não; custo de inferência e regime de dados podem justificar outra alocação.

Avance para **Converter trabalho em tempo** e relacione o resultado observado ao próximo mecanismo.

## 08. Converter trabalho em tempo

### Fala sugerida

A divisão supõe nenhuma sobrecarga. Comunicação e alimentação de dados acrescentam tempo. Este número é uma hipótese, não promessa de prazo.

### Na demonstração

Aumente GPUs e observe o tempo ideal.

### No quadro branco

tempo = C/(GPUs × desempenho útil)

### Pergunta à turma

Dobrar GPUs sempre reduz tempo pela metade?

### Resposta e transição

Não; só no modelo ideal sem gargalos adicionais.

Avance para **Memória acaba antes da aritmética** e relacione o resultado observado ao próximo mecanismo.

## 09. Memória acaba antes da aritmética

### Fala sugerida

Dezesseis bytes representam uma receita típica de Adam em precisão mista. Outras receitas mudam a conta. As ativações aqui são uma aproximação declarada.

### Na demonstração

Aumente contexto e lote separadamente.

### No quadro branco

Estados ≈ 16N bytes + ativações

### Pergunta à turma

Reduzir lote reduz estados do Adam?

### Resposta e transição

Não; reduz principalmente ativações.

Avance para **Precisão mista separa funções** e relacione o resultado observado ao próximo mecanismo.

## 10. Precisão mista separa funções

### Fala sugerida

Não convertemos todos os objetos para um tipo único. Cálculo e atualização podem usar precisões diferentes. Dividir toda a memória por dois dá uma estimativa enganosa.

### Na demonstração

Compare pesos FP32 e BF16.

### No quadro branco

FP32: 4 bytes; BF16: 2 bytes por peso

### Pergunta à turma

BF16 corta toda memória pela metade?

### Resposta e transição

Não; nem todos os objetos mudam de precisão.

Avance para **Três formas de distribuir** e relacione o resultado observado ao próximo mecanismo.

## 11. Três formas de distribuir

### Fala sugerida

Primeiro identifiquem o que foi partido. Depois perguntem qual mensagem atravessa as placas. Memória agregada só ajuda se distribuir o objeto que não cabe.

### Na demonstração

Mude GPUs e compare o objeto dividido.

### No quadro branco

Dados: exemplos; tensor: operação; pipeline: camadas

### Pergunta à turma

Paralelismo de dados puro resolve modelo que não cabe?

### Resposta e transição

Não; o modelo continua replicado, sem particionamento adicional de estados.

Avance para **FlashAttention reorganiza tráfego** e relacione o resultado observado ao próximo mecanismo.

## 12. FlashAttention reorganiza tráfego

### Fala sugerida

Eficiência de implementação não altera a definição de atenção. A relação quadrática de pares permanece. O ganho vem do movimento de dados e dos intermediários armazenados.

### Na demonstração

Dobre contexto e acompanhe T².

### No quadro branco

Aritmética O(T²); menos tráfego intermediário

### Pergunta à turma

FlashAttention torna a aritmética linear?

### Resposta e transição

Não; melhora uso de memória mantendo atenção exata quadrática.

Avance para **A fábrica entrega um completador** e relacione o resultado observado ao próximo mecanismo.

## 13. A fábrica entrega um completador

### Fala sugerida

Produzimos uma distribuição de continuação de texto. A próxima aula muda os exemplos que a orientam. Justifiquem agora tamanho, corpus e sistema em conjunto.

### Na demonstração

Compare custo de treino e custo por token servido.

### No quadro branco

C vida ≈ 6ND + 2N × tokens servidos

### Pergunta à turma

Por que considerar inferência na escolha do modelo?

### Resposta e transição

Porque o custo repetido de servir pode dominar o ciclo de vida.
