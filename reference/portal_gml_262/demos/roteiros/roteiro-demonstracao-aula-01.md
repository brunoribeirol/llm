# Aula 01 — Uma interface, muitas tarefas: o que a métrica realmente mede

Classificação, geração e avaliação com números que você pode conferir

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Tarefa**: valor inicial `sentiment`.
- **Fraudes detectadas (TP)**: valor inicial `80`.
- **Alarmes falsos (FP)**: valor inicial `100`.
- **Custo relativo de perder uma fraude**: valor inicial `20`.
- **Texto candidato**: valor inicial `o gato dorme no sofá`.
- **Texto de referência**: valor inicial `o gato está no sofá`.
- **Probabilidade atribuída a cada token correto**: valor inicial `0.25`.
- **Peso de revocação β**: valor inicial `1`.

## 01. Cinco mudanças de mecanismo

### Fala sugerida

Regras explícitas, contagens, vetores, atenção e ajuste por instruções resolvem problemas diferentes. O percurso é conceitual: usar uma interface de chat não revela sozinho qual mecanismo produziu uma saída. Troque a tarefa e identifique qual propriedade da interface permanece comum. Pergunto à turma: “Uma interface conversacional determina a arquitetura?” Não; a interface organiza a interação, enquanto a arquitetura e o treinamento determinam como o modelo calcula.

### Na demonstração

Troque a tarefa e identifique qual propriedade da interface permanece comum.

### No quadro branco

Regras → contagens → vetores → atenção → instruções

### Pergunta à turma

Uma interface conversacional determina a arquitetura?

### Resposta e transição

Não; a interface organiza a interação, enquanto a arquitetura e o treinamento determinam como o modelo calcula.

Avance para **Classifique pela forma da saída** e relacione o resultado observado ao próximo mecanismo.

## 02. Classifique pela forma da saída

### Fala sugerida

Classificação devolve um rótulo, rotulagem associa categorias às posições e geração produz uma sequência. As saídas desta tela são exemplos escritos para a aula, sem chamada a modelo. Percorra as quatro tarefas e compare entrada, formato esperado e exemplo ilustrativo. Pergunto à turma: “Extração em JSON deixa de ser uma tarefa de extração?” Não; mudou o formato de execução, mas o objetivo continua identificar entidades com critérios verificáveis.

### Na demonstração

Percorra as quatro tarefas e compare entrada, formato esperado e exemplo ilustrativo.

### No quadro branco

texto → rótulo | texto → rótulos por token | texto → texto

### Pergunta à turma

Extração em JSON deixa de ser uma tarefa de extração?

### Resposta e transição

Não; mudou o formato de execução, mas o objetivo continua identificar entidades com critérios verificáveis.

Avance para **O próximo token unifica a interface** e relacione o resultado observado ao próximo mecanismo.

## 03. O próximo token unifica a interface

### Fala sugerida

Um gerador representa tarefas como sequências condicionadas à entrada. Isso simplifica a interface, mas não fornece uma métrica universal de sucesso. Altere Probabilidade do token e veja a distribuição ilustrativa entre quatro alternativas. Pergunto à turma: “Uma sequência provável é necessariamente correta?” Não; a probabilidade mede compatibilidade com o modelo, e a correção depende da tarefa e da evidência.

### Na demonstração

Altere Probabilidade do token e veja a distribuição ilustrativa entre quatro alternativas.

### No quadro branco

P(y|x) = produto das probabilidades condicionais dos tokens

### Pergunta à turma

Uma sequência provável é necessariamente correta?

### Resposta e transição

Não; a probabilidade mede compatibilidade com o modelo, e a correção depende da tarefa e da evidência.

Avance para **Construa a matriz de confusão** e relacione o resultado observado ao próximo mecanismo.

## 04. Construa a matriz de confusão

### Fala sugerida

O conjunto didático tem 10.000 transações e exatamente 100 fraudes. TP e FP são controláveis; FN e TN são calculados para preservar esses totais. Fixe TP=80 e FP=100; calcule FN e TN antes de ler a matriz. Pergunto à turma: “Qual célula representa uma fraude liberada?” É FN, o falso negativo: a transação era fraudulenta, mas o sistema não a sinalizou.

### Na demonstração

Fixe TP=80 e FP=100; calcule FN e TN antes de ler a matriz.

### No quadro branco

FN = 100 − TP; TN = 9900 − FP

### Pergunta à turma

Qual célula representa uma fraude liberada?

### Resposta e transição

É FN, o falso negativo: a transação era fraudulenta, mas o sistema não a sinalizou.

Avance para **Desmonte os 99% de acurácia** e relacione o resultado observado ao próximo mecanismo.

## 05. Desmonte os 99% de acurácia

### Fala sugerida

Um detector que nunca alerta acerta todas as 9.900 transações legítimas. Ele alcança 99% de acurácia e detecta zero das 100 fraudes. Coloque TP=0 e FP=0; compare acurácia e revocação. Pergunto à turma: “Por que o número alto não demonstra utilidade?” Porque resulta da frequência da classe majoritária; o sistema não realizou a função de encontrar fraudes.

### Na demonstração

Coloque TP=0 e FP=0; compare acurácia e revocação.

### No quadro branco

Acurácia trivial = 1 − prevalência = 0,99

### Pergunta à turma

Por que o número alto não demonstra utilidade?

### Resposta e transição

Porque resulta da frequência da classe majoritária; o sistema não realizou a função de encontrar fraudes.

Avance para **Precisão e revocação têm denominadores distintos** e relacione o resultado observado ao próximo mecanismo.

## 06. Precisão e revocação têm denominadores distintos

### Fala sugerida

Precisão responde quantos alertas eram verdadeiros, e revocação responde quantas fraudes foram encontradas. Quando não há alertas, a precisão é indicada como indefinida em vez de inventar um acerto. Mantenha TP fixo e aumente FP; observe qual das duas métricas muda. Pergunto à turma: “Dobrar os alarmes falsos altera a revocação?” Não se TP e o total de fraudes permanecerem iguais; altera a precisão e a carga de investigação.

### Na demonstração

Mantenha TP fixo e aumente FP; observe qual das duas métricas muda.

### No quadro branco

Precisão = TP/(TP+FP); revocação = TP/(TP+FN)

### Pergunta à turma

Dobrar os alarmes falsos altera a revocação?

### Resposta e transição

Não se TP e o total de fraudes permanecerem iguais; altera a precisão e a carga de investigação.

Avance para **A média harmônica cobra desequilíbrio** e relacione o resultado observado ao próximo mecanismo.

## 07. A média harmônica cobra desequilíbrio

### Fala sugerida

F1 combina precisão e revocação pela média harmônica. Fβ explicita uma preferência relativa por revocação, mas não substitui a descrição dos custos do problema. Experimente TP=90, FP=900 e compare β=0,5 com β=2. Pergunto à turma: “Por que F1 fica baixo quando apenas uma das métricas é alta?” A média harmônica é dominada pelo menor termo; uma dimensão quase nula impede uma pontuação alta.

### Na demonstração

Experimente TP=90, FP=900 e compare β=0,5 com β=2.

### No quadro branco

Fβ = (1+β²)PR/(β²P+R)

### Pergunta à turma

Por que F1 fica baixo quando apenas uma das métricas é alta?

### Resposta e transição

A média harmônica é dominada pelo menor termo; uma dimensão quase nula impede uma pontuação alta.

Avance para **Tome a decisão pelo custo** e relacione o resultado observado ao próximo mecanismo.

## 08. Tome a decisão pelo custo

### Fala sugerida

Um falso negativo e um falso positivo podem ter impactos diferentes. A conta exibida atribui custo unitário ao falso positivo e multiplica falsos negativos pelo custo escolhido. Compare o detector atual com nunca alertar e alertar tudo, alterando Custo relativo. Pergunto à turma: “O melhor detector é o que tem maior acurácia?” Somente se essa métrica representar os custos relevantes; a decisão pode mudar quando perder uma fraude custa muito mais.

### Na demonstração

Compare o detector atual com nunca alertar e alertar tudo, alterando Custo relativo.

### No quadro branco

Custo = FP + c × FN

### Pergunta à turma

O melhor detector é o que tem maior acurácia?

### Resposta e transição

Somente se essa métrica representar os custos relevantes; a decisão pode mudar quando perder uma fraude custa muito mais.

Avance para **Conte sobreposição sem confundir verdade** e relacione o resultado observado ao próximo mecanismo.

## 09. Conte sobreposição sem confundir verdade

### Fala sugerida

As duas frases são divididas por espaços e normalizadas em letras minúsculas. A contagem de acertos é truncada pela frequência de cada palavra na referência. Repita gato várias vezes no candidato; observe que repetições extras não criam acertos ilimitados. Pergunto à turma: “Por que truncar a contagem?” Para impedir que repetir uma palavra comum aumente artificialmente o número de correspondências.

### Na demonstração

Repita gato várias vezes no candidato; observe que repetições extras não criam acertos ilimitados.

### No quadro branco

Acertos = soma de min(contagem candidata, contagem referência)

### Pergunta à turma

Por que truncar a contagem?

### Resposta e transição

Para impedir que repetir uma palavra comum aumente artificialmente o número de correspondências.

Avance para **BLEU-1 e ROUGE-1 respondem perguntas diferentes** e relacione o resultado observado ao próximo mecanismo.

## 10. BLEU-1 e ROUGE-1 respondem perguntas diferentes

### Fala sugerida

A demonstração calcula BLEU de unigramas com penalidade de brevidade e ROUGE-1 por revocação. Ela não é uma implementação de BLEU-4, METEOR ou de avaliação semântica. Reduza o candidato a o gato; compare precisão, penalidade e revocação. Pergunto à turma: “Uma frase curtíssima pode ter precisão alta?” Sim; a penalidade de brevidade reduz BLEU-1 e a baixa cobertura reduz ROUGE-1.

### Na demonstração

Reduza o candidato a o gato; compare precisão, penalidade e revocação.

### No quadro branco

BLEU-1 = BP × precisão; ROUGE-1 = acertos/tokens de referência

### Pergunta à turma

Uma frase curtíssima pode ter precisão alta?

### Resposta e transição

Sim; a penalidade de brevidade reduz BLEU-1 e a baixa cobertura reduz ROUGE-1.

Avance para **Perplexidade mede surpresa por unidade** e relacione o resultado observado ao próximo mecanismo.

## 11. Perplexidade mede surpresa por unidade

### Fala sugerida

Quando todos os tokens corretos recebem a mesma probabilidade p, a perda média é −ln(p) e a perplexidade é 1/p. Comparações exigem a mesma unidade de tokenização e o mesmo conjunto de avaliação. Mova p de 0,25 para 0,5 e preveja a perplexidade antes de conferir. Pergunto à turma: “PPL menor prova melhor atendimento ao usuário?” Não; indica menor surpresa média nos tokens avaliados, sem garantir factualidade, segurança ou utilidade.

### Na demonstração

Mova p de 0,25 para 0,5 e preveja a perplexidade antes de conferir.

### No quadro branco

H = −ln p; PPL = exp(H) = 1/p

### Pergunta à turma

PPL menor prova melhor atendimento ao usuário?

### Resposta e transição

Não; indica menor surpresa média nos tokens avaliados, sem garantir factualidade, segurança ou utilidade.

Avance para **Audite a métrica antes de concluir** e relacione o resultado observado ao próximo mecanismo.

## 12. Audite a métrica antes de concluir

### Fala sugerida

Sobreposição pode punir um sinônimo correto e premiar uma frase falsa com as palavras esperadas. O resultado precisa ser conectado ao tipo de erro que a aplicação não pode tolerar. Escreva uma frase com negação no candidato e compare a pontuação com seu julgamento humano. Pergunto à turma: “Qual medição complementar expõe uma resposta falsa com alta sobreposição?” Uma verificação de afirmações contra evidências ou uma avaliação humana com critérios de correção definidos.

### Na demonstração

Escreva uma frase com negação no candidato e compare a pontuação com seu julgamento humano.

### No quadro branco

Tarefa → falha relevante → métrica → inspeção de exemplos

### Pergunta à turma

Qual medição complementar expõe uma resposta falsa com alta sobreposição?

### Resposta e transição

Uma verificação de afirmações contra evidências ou uma avaliação humana com critérios de correção definidos.
