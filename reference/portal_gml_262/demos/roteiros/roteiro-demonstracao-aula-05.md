# Aula 05 — Da recorrência à atenção: três sintomas, três mecanismos

Estados, gradientes, gates e alinhamento calculados passo a passo

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Comprimento T**: valor inicial `20`.
- **Ganho por passo**: valor inicial `0.9`.
- **Porta de esquecimento f**: valor inicial `0.95`.
- **Estado-consulta do decoder**: valor inicial `0.8`.
- **Escala dos scores de atenção**: valor inicial `1`.
- **Ordem da sequência**: valor inicial `forward`.

## 01. Separe três sintomas diferentes

### Fala sugerida

Erro em sequências longas, gradiente fraco e baixa paralelização têm causas relacionadas, mas distintas. A miniatura oferece uma medição para cada uma sem inventar uma curva de qualidade de um modelo treinado. Aumente T e observe caminho, produto de ganhos e quantidade de etapas sequenciais. Pergunto à turma: “Uma solução que melhora memória necessariamente libera paralelismo?” Não; LSTMs melhoram o transporte de informação, mas continuam calculando um estado após o anterior.

### Na demonstração

Aumente T e observe caminho, produto de ganhos e quantidade de etapas sequenciais.

### No quadro branco

Comprimento; gradiente; dependência de execução

### Pergunta à turma

Uma solução que melhora memória necessariamente libera paralelismo?

### Resposta e transição

Não; LSTMs melhoram o transporte de informação, mas continuam calculando um estado após o anterior.

Avance para **Desenrole a recorrência** e relacione o resultado observado ao próximo mecanismo.

## 02. Desenrole a recorrência

### Fala sugerida

A mesma transformação é aplicada em cada posição com parâmetros compartilhados. O estado atual depende do estado anterior e da nova entrada. Troque a ordem da sequência e siga os estados numéricos calculados por tanh. Pergunto à turma: “A rede guarda todos os tokens dentro do estado?” Ela carrega um vetor atualizado; não existe uma cópia literal garantida de cada entrada passada.

### Na demonstração

Troque a ordem da sequência e siga os estados numéricos calculados por tanh.

### No quadro branco

hₜ = tanh(0,8hₜ₋₁ + xₜ)

### Pergunta à turma

A rede guarda todos os tokens dentro do estado?

### Resposta e transição

Ela carrega um vetor atualizado; não existe uma cópia literal garantida de cada entrada passada.

Avance para **A ordem aparece na composição** e relacione o resultado observado ao próximo mecanismo.

## 03. A ordem aparece na composição

### Fala sugerida

Aplicar as mesmas funções em outra ordem pode produzir um estado final diferente. O exemplo usa a sequência 1, −1, 0,5 e coeficientes fixos para permitir conferência. Alterne Original e Invertida, comparando o primeiro e o último estado. Pergunto à turma: “Por que somar as entradas não reproduz necessariamente uma RNN?” Porque a recorrência intercala transformações dependentes do estado e não linearidades.

### Na demonstração

Alterne Original e Invertida, comparando o primeiro e o último estado.

### No quadro branco

f₃(f₂(f₁(h₀))) pode diferir de f₁(f₂(f₃(h₀)))

### Pergunta à turma

Por que somar as entradas não reproduz necessariamente uma RNN?

### Resposta e transição

Porque a recorrência intercala transformações dependentes do estado e não linearidades.

Avance para **Meça o produto que transporta o gradiente** e relacione o resultado observado ao próximo mecanismo.

## 04. Meça o produto que transporta o gradiente

### Fala sugerida

O produto de ganhos isola o efeito multiplicativo de atravessar muitos passos. Não é o gradiente completo de uma RNN, pois fixa o mesmo ganho em todas as transições. Compare ganho 0,9 e 1,1 para T=50; leia a escala logarítmica da magnitude. Pergunto à turma: “Aumentar apenas a dimensão elimina esse expoente?” Não; mantendo o regime de ganhos, o efeito exponencial no comprimento continua presente.

### Na demonstração

Compare ganho 0,9 e 1,1 para T=50; leia a escala logarítmica da magnitude.

### No quadro branco

G = ganhoᵀ; log₁₀|G| = T log₁₀|ganho|

### Pergunta à turma

Aumentar apenas a dimensão elimina esse expoente?

### Resposta e transição

Não; mantendo o regime de ganhos, o efeito exponencial no comprimento continua presente.

Avance para **Distingua desaparecer de explodir** e relacione o resultado observado ao próximo mecanismo.

## 05. Distingua desaparecer de explodir

### Fala sugerida

Ganhos menores que um fazem o sinal decair; maiores que um fazem crescer neste modelo escalar. A proximidade de um muda fortemente o alcance útil. Passe por 0,99, 1 e 1,01 com T alto; compare as ordens de grandeza. Pergunto à turma: “Perda descendo garante que dependências longas estão sendo aprendidas?” Não; o modelo pode melhorar relações locais enquanto o sinal relevante para posições distantes continua fraco.

### Na demonstração

Passe por 0,99, 1 e 1,01 com T alto; compare as ordens de grandeza.

### No quadro branco

ganho < 1: decai; = 1: preserva; > 1: cresce

### Pergunta à turma

Perda descendo garante que dependências longas estão sendo aprendidas?

### Resposta e transição

Não; o modelo pode melhorar relações locais enquanto o sinal relevante para posições distantes continua fraco.

Avance para **Conte a dependência sequencial** e relacione o resultado observado ao próximo mecanismo.

## 06. Conte a dependência sequencial

### Fala sugerida

Para calcular hₜ é necessário terminar hₜ₋₁. Operações dentro de um passo podem ser paralelas, mas a cadeia temporal impõe T dependências. Dobre T e compare a profundidade sequencial com a leitura em paralelo usada como referência conceitual. Pergunto à turma: “A limitação desaparece no treino porque a frase inteira é conhecida?” Não na recorrência: conhecer as entradas não torna os estados anteriores disponíveis antes de calculá-los.

### Na demonstração

Dobre T e compare a profundidade sequencial com a leitura em paralelo usada como referência conceitual.

### No quadro branco

h₁ → h₂ → ... → h_T

### Pergunta à turma

A limitação desaparece no treino porque a frase inteira é conhecida?

### Resposta e transição

Não na recorrência: conhecer as entradas não torna os estados anteriores disponíveis antes de calculá-los.

Avance para **Abra o caminho aditivo do LSTM** e relacione o resultado observado ao próximo mecanismo.

## 07. Abra o caminho aditivo do LSTM

### Fala sugerida

A célula combina memória anterior e nova informação por uma soma controlada por gates. O cálculo exibido isola a retenção da memória com entrada nova igual a zero. Compare f=0,9 e f=0,99 para o mesmo T; veja a fração de memória preservada. Pergunto à turma: “O LSTM elimina automaticamente o desaparecimento?” Não; permite aprender gates que preservam informação nos canais necessários, mas sua retenção ainda depende desses valores.

### Na demonstração

Compare f=0,9 e f=0,99 para o mesmo T; veja a fração de memória preservada.

### No quadro branco

cₜ = fₜcₜ₋₁ + iₜgₜ; caminho isolado: c_T = fᵀc₀

### Pergunta à turma

O LSTM elimina automaticamente o desaparecimento?

### Resposta e transição

Não; permite aprender gates que preservam informação nos canais necessários, mas sua retenção ainda depende desses valores.

Avance para **Localize o gargalo do contexto fixo** e relacione o resultado observado ao próximo mecanismo.

## 08. Localize o gargalo do contexto fixo

### Fala sugerida

No seq2seq básico, o decoder recebe um resumo fixo do encoder. Aumentar o estado amplia capacidade, mas não oferece acesso separado a cada posição de origem. Aumente T e compare o caminho da primeira posição até o decoder. Pergunto à turma: “Por que capacidade e acesso são problemas diferentes?” Um resumo maior pode conter mais informação, mas recuperar uma posição específica continua dependendo de como ela foi comprimida.

### Na demonstração

Aumente T e compare o caminho da primeira posição até o decoder.

### No quadro branco

c = h_T; caminho da posição j ao passo t = (T−j)+t

### Pergunta à turma

Por que capacidade e acesso são problemas diferentes?

### Resposta e transição

Um resumo maior pode conter mais informação, mas recuperar uma posição específica continua dependendo de como ela foi comprimida.

Avance para **Calcule scores aditivos de alinhamento** e relacione o resultado observado ao próximo mecanismo.

## 09. Calcule scores aditivos de alinhamento

### Fala sugerida

A consulta do decoder é comparada às anotações do encoder por um score aditivo. A miniatura usa tanh(q+kⱼ) com pesos fixos para mostrar a dependência de q e k. Mova Estado-consulta e compare os scores das três posições de origem. Pergunto à turma: “Esse score já é uma probabilidade?” Não; é um número real que precisa ser normalizado sobre as posições disponíveis.

### Na demonstração

Mova Estado-consulta e compare os scores das três posições de origem.

### No quadro branco

eⱼ = escala × tanh(q + kⱼ)

### Pergunta à turma

Esse score já é uma probabilidade?

### Resposta e transição

Não; é um número real que precisa ser normalizado sobre as posições disponíveis.

Avance para **Normalize e leia uma mistura de valores** e relacione o resultado observado ao próximo mecanismo.

## 10. Normalize e leia uma mistura de valores

### Fala sugerida

Softmax converte os scores em pesos positivos que somam um. O contexto é a média ponderada dos valores, portanto muda quando a consulta ou a escala muda. Aumente Escala e compare pesos, soma da linha e contexto resultante. Pergunto à turma: “O contexto pode sair do intervalo entre valores escalares nesta mistura?” Não; com pesos não negativos somando um, ele é uma combinação convexa dos valores.

### Na demonstração

Aumente Escala e compare pesos, soma da linha e contexto resultante.

### No quadro branco

αⱼ = softmax(e)ⱼ; c = soma αⱼvⱼ

### Pergunta à turma

O contexto pode sair do intervalo entre valores escalares nesta mistura?

### Resposta e transição

Não; com pesos não negativos somando um, ele é uma combinação convexa dos valores.

Avance para **Veja um contexto por passo** e relacione o resultado observado ao próximo mecanismo.

## 11. Veja um contexto por passo

### Fala sugerida

Linhas diferentes representam consultas diferentes do decoder e colunas representam estados do encoder. A matriz é calculada com regras fixas didáticas, não aprendida de traduções reais. Mova Consulta e observe como as três linhas de alinhamento se deslocam. Pergunto à turma: “Um peso alto prova a causa linguística de uma decisão?” Não; revela uma contribuição no mecanismo, mas uma interpretação causal exige intervenções e evidências adicionais.

### Na demonstração

Mova Consulta e observe como as três linhas de alinhamento se deslocam.

### No quadro branco

Linhas: destino; colunas: origem; soma por linha = 1

### Pergunta à turma

Um peso alto prova a causa linguística de uma decisão?

### Resposta e transição

Não; revela uma contribuição no mecanismo, mas uma interpretação causal exige intervenções e evidências adicionais.

Avance para **Feche as dívidas antes do Transformer** e relacione o resultado observado ao próximo mecanismo.

## 12. Feche as dívidas antes do Transformer

### Fala sugerida

Atenção remove a obrigação de ler um único resumo ao dar acesso aos estados de origem. Na arquitetura recorrente de Bahdanau, produzir esses estados continua sequencial. Compare a tabela de mecanismos e associe cada sintoma à intervenção correspondente. Pergunto à turma: “Qual ganho pertence ao Transformer e não a qualquer atenção?” A possibilidade de processar posições de treino em paralelo sem a cadeia recorrente, respeitando as máscaras necessárias.

### Na demonstração

Compare a tabela de mecanismos e associe cada sintoma à intervenção correspondente.

### No quadro branco

LSTM: caminho de memória; atenção: acesso; Transformer: atenção sem recorrência

### Pergunta à turma

Qual ganho pertence ao Transformer e não a qualquer atenção?

### Resposta e transição

A possibilidade de processar posições de treino em paralelo sem a cadeia recorrente, respeitando as máscaras necessárias.
