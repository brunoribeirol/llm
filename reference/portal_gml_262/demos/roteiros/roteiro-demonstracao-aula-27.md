# Aula 27 — Avaliação: do acerto aparente à evidência

Calcule métricas, acordo, kappa e viés de posição em pequenos conjuntos explícitos. O juiz é uma função sintética inspecionável, não uma chamada de LLM.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Redação da resposta lexical**: valor inicial `paraphrase`.
- **Humano aprova / juiz aprova**: valor inicial `82`.
- **Humano reprova / juiz reprova**: valor inicial `2`.
- **Humano reprova / juiz aprova**: valor inicial `8`.
- **Humano aprova / juiz reprova**: valor inicial `8`.
- **Bônus para a primeira resposta**: valor inicial `0.2`.
- **Bônus por comprimento**: valor inicial `0.15`.

## 01. Avaliar modelo ou sistema?

### Fala sugerida

Uma resposta errada não diz qual peça deve mudar. Antes de trocar o modelo, olhamos a fonte e a recuperação. A avaliação precisa acompanhar as fronteiras do sistema.

### Na demonstração

Examine as falhas ilustradas e atribua cada uma à menor camada que a explica.

### No quadro branco

qual falha? qual camada? qual evidência?

### Pergunta à turma

Uma classificação geral de modelos mede a qualidade do seu retriever?

### Resposta e transição

Não. É necessário avaliar o componente e o sistema nas entradas do domínio.

Avance para **O denominador acompanha a taxa** e relacione o resultado observado ao próximo mecanismo.

## 02. O denominador acompanha a taxa

### Fala sugerida

Oitenta por cento em cinco casos tem significado diferente de oitenta por cento em quinhentos. Também precisamos saber quais casos foram escolhidos. Contagem, distribuição e protocolo vêm junto da taxa.

### Na demonstração

Altere as contagens e acompanhe n e a proporção de aprovações humanas.

### No quadro branco

n = TP + TN + FP + FN

### Pergunta à turma

Se todas as contagens forem zero, qual é a acurácia?

### Resposta e transição

Não é definida. Não há observações que permitam calcular a proporção.

Avance para **A matriz de confusão** e relacione o resultado observado ao próximo mecanismo.

## 03. A matriz de confusão

### Fala sugerida

Leiam os eixos antes de interpretar o número. Trocar o significado das linhas altera o diagnóstico. A matriz permite separar um juiz permissivo de um juiz excessivamente severo.

### Na demonstração

Aumente falsos positivos e localize exatamente a célula que muda.

### No quadro branco

FP: juiz aprova, humano reprova

### Pergunta à turma

Por que acordo sozinho pode esconder o tipo de erro?

### Resposta e transição

Porque soma coincidências sem separar aprovações indevidas e reprovações indevidas.

Avance para **Acordo observado e esperado** e relacione o resultado observado ao próximo mecanismo.

## 04. Acordo observado e esperado

### Fala sugerida

Se quase todo mundo recebe aprovado, dois avaliadores podem concordar bastante só por usar esse rótulo com frequência. As marginais quantificam esse efeito. É essa referência que o kappa desconta.

### Na demonstração

Concentre as contagens na célula de aprovação conjunta e compare p observado e p esperado.

### No quadro branco

pₒ=(TP+TN)/n; pₑ=pH+·pJ+ + pH−·pJ−

### Pergunta à turma

Acordo alto implica um instrumento discriminativo?

### Resposta e transição

Não. Em dados muito desbalanceados, boa parte pode ser explicada pela prevalência dos rótulos.

Avance para **Kappa e seu caso indefinido** e relacione o resultado observado ao próximo mecanismo.

## 05. Kappa e seu caso indefinido

### Fala sugerida

Com a configuração inicial temos oitenta e quatro por cento de acordo. O desconto pelo acaso deixa kappa perto de zero vírgula onze. Isso não contradiz o acordo; responde a outra pergunta.

### Na demonstração

Use 82, 2, 8 e 8 e depois uma matriz com somente aprovações conjuntas.

### No quadro branco

κ = (pₒ−pₑ)/(1−pₑ)

### Pergunta à turma

Por que uma matriz com apenas um rótulo pode impedir o cálculo?

### Resposta e transição

Porque as marginais podem produzir p esperado igual a um, zerando o denominador.

Avance para **Uma rubrica precisa distinguir critérios** e relacione o resultado observado ao próximo mecanismo.

## 06. Uma rubrica precisa distinguir critérios

### Fala sugerida

Uma nota só é útil se sabemos o que ela mede. Se o critério diz apenas possui citação, uma resposta vazia pode passar. Precisamos testar a redação da rubrica em casos de desacordo.

### Na demonstração

Compare as duas respostas ilustradas e indique qual critério diferencia as notas.

### No quadro branco

correto + fundamentado + responde à pergunta

### Pergunta à turma

Por que revisar a rubrica antes de trocar o juiz?

### Resposta e transição

Porque o avaliador pode estar aplicando corretamente um critério que mede a coisa errada.

Avance para **Pointwise e pairwise** e relacione o resultado observado ao próximo mecanismo.

## 07. Pointwise e pairwise

### Fala sugerida

Comparar pode ser mais fácil que pontuar. Mas as perguntas não são equivalentes. Um sistema pode ganhar todas as disputas contra um adversário ruim e ainda reprovar no critério mínimo.

### Na demonstração

Observe notas absolutas e vencedores para os mesmos pares sintéticos.

### No quadro branco

melhor que B ≠ atende ao requisito

### Pergunta à turma

Qual instrumento responde se a qualidade é suficiente?

### Resposta e transição

Uma rubrica com limiares e critérios ligados ao uso, além da comparação relativa.

Avance para **O viés da primeira posição** e relacione o resultado observado ao próximo mecanismo.

## 08. O viés da primeira posição

### Fala sugerida

Mantemos os textos fixos e só trocamos a ordem. Assim isolamos o mecanismo de posição. O resultado é da função sintética, não uma taxa medida em um produto real.

### Na demonstração

Aumente o bônus para a primeira resposta e conte inversões.

### No quadro branco

inversão = vencedor(A,B) ≠ vencedor(B,A)

### Pergunta à turma

Uma inversão significa que a qualidade real da resposta mudou?

### Resposta e transição

Não. Mudou a decisão do avaliador diante da ordem de apresentação.

Avance para **Verbosidade e plausibilidade** e relacione o resultado observado ao próximo mecanismo.

## 09. Verbosidade e plausibilidade

### Fala sugerida

O juiz pode premiar a aparência de completude. Uma fonte externa permite verificar o fato. Controlar comprimento ajuda a investigar o viés, mas não substitui a conferência factual.

### Na demonstração

Aumente o bônus de comprimento e compare o vencedor com o rótulo humano.

### No quadro branco

comprimento ≠ correção; plausibilidade ≠ evidência

### Pergunta à turma

Eliminar viés de posição garante acordo com o humano?

### Resposta e transição

Não. Pode permanecer viés de comprimento, preferência de estilo ou erro de verificação factual.

Avance para **Dupla ordem e cobertura** e relacione o resultado observado ao próximo mecanismo.

## 10. Dupla ordem e cobertura

### Fala sugerida

Existe um preço para o protocolo. Descartamos justamente alguns pares difíceis. Depois precisamos olhar também os erros que sobreviveram às duas ordens.

### Na demonstração

Aumente o bônus de posição e acompanhe cobertura e número de julgamentos.

### No quadro branco

cobertura = 1−taxa de inversão

### Pergunta à turma

Cobertura baixa pode acompanhar alto acordo nos pares restantes?

### Resposta e transição

Sim. Por isso acordo e cobertura precisam ser reportados juntos.

Avance para **Factualidade por afirmação** e relacione o resultado observado ao próximo mecanismo.

## 11. Factualidade por afirmação

### Fala sugerida

Uma citação no fim do parágrafo não comprova cada frase. Separamos unidades verificáveis e buscamos suporte para cada uma. A ausência de uma informação pedida exige ainda um critério de cobertura.

### Na demonstração

Leia as três afirmações e reconstrua a fração de sustentação.

### No quadro branco

precisão factual = afirmações apoiadas / verificadas

### Pergunta à turma

Boa precisão factual garante resposta completa?

### Resposta e transição

Não. Um texto pode afirmar pouco e ser inteiramente correto, mas omitir partes essenciais da pergunta.

Avance para **A incerteza acompanha o acordo** e relacione o resultado observado ao próximo mecanismo.

## 12. A incerteza acompanha o acordo

### Fala sugerida

O acordo continua parecido quando replicamos as proporções. O que muda é a precisão da estimativa sob as hipóteses declaradas. Copiar literalmente os mesmos casos não produz independência e não justifica estreitar o intervalo numa avaliação real.

### Na demonstração

Multiplique as quatro contagens aproximadamente pelo mesmo fator e compare o acordo com a largura do intervalo.

### No quadro branco

estimativa pontual + n + intervalo + hipóteses da amostra

### Pergunta à turma

Um intervalo estreito elimina o problema de um conjunto enviesado?

### Resposta e transição

Não. Ele descreve incerteza amostral sob um modelo; não garante representatividade, referências corretas ou ausência de contaminação.

Avance para **Sobreposição lexical não é factualidade** e relacione o resultado observado ao próximo mecanismo.

## 13. Sobreposição lexical não é factualidade

### Fala sugerida

Uma paráfrase pode trocar quase todas as palavras e preservar a resposta. Um número errado pode trocar uma palavra só e destruir o fato principal. É por isso que precisamos escolher a métrica de acordo com aquilo que a tarefa exige.

### Na demonstração

Alterne paráfrase correta, cópia literal e número errado e compare os scores com a correção factual.

### No quadro branco

precisão lexical = matches / candidato; recall lexical = matches / referência

### Pergunta à turma

Por que a resposta com número errado pode ter score lexical maior que a paráfrase correta?

### Resposta e transição

Porque a métrica conta sobreposição de unidades de texto, sem atribuir ao número a importância factual que ele tem na pergunta.

Avance para **Escolher com evidência e restrições** e relacione o resultado observado ao próximo mecanismo.

## 14. Escolher com evidência e restrições

### Fala sugerida

Quero uma decisão que outra equipe consiga revisar. Mostrem casos, denominadores e limites do instrumento. Se o resultado depende do juiz, mostrem também como ele foi calibrado.

### Na demonstração

Compare o cartão de avaliação com o cartão de restrições e formule uma decisão condicionada.

### No quadro branco

qualidade + n + protocolo + custo + latência

### Pergunta à turma

Qual dado precisa acompanhar uma nota produzida por juiz automático?

### Resposta e transição

Rubrica, modelo ou regra do juiz, protocolo, conjunto e tamanho da amostra, calibração e limitações.
