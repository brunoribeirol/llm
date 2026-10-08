# Aula 28 — Lab 8: construir um harness de avaliação

Execute um corpus fictício, inspecione ranking, avalie por camada e produza prioridades. Métricas são calculadas de casos explícitos; a rubrica é determinística.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Documentos recuperados (k)**: valor inicial `1`.
- **Recuperação**: valor inicial `lexical`.
- **Nota mínima de aprovação**: valor inicial `2`.
- **Casos extras aprovados pelo juiz**: valor inicial `1`.
- **Esforço estimado de corrigir paráfrases**: valor inicial `2`.

## 01. Um adaptador para o sistema inteiro

### Fala sugerida

A avaliação não precisa conhecer todos os detalhes internos. Ela precisa de um contrato estável. Se a implementação mudar, os casos ainda devem conseguir fazer a mesma pergunta.

### Na demonstração

Compare entrada e saída do adaptador para o primeiro caso.

### No quadro branco

executar(pergunta) → resposta, fontes, latência, trajetória

### Pergunta à turma

Por que uma string de resposta apenas limita o harness?

### Resposta e transição

Porque esconde fontes, ações e medidas necessárias à avaliação por camada.

Avance para **O corpus de referência** e relacione o resultado observado ao próximo mecanismo.

## 02. O corpus de referência

### Fala sugerida

Um corpus minúsculo permite conferir a conta à mão. A escala pequena é deliberada. Depois o mesmo contrato pode avaliar um sistema maior, desde que as referências continuem confiáveis.

### Na demonstração

Leia os artigos e localize a informação que responde ao caso de prazo.

### No quadro branco

fonte identificável + conteúdo verificável

### Pergunta à turma

Por que usar um domínio fictício nesta simulação?

### Resposta e transição

Para deixar todas as regras visíveis e evitar confundir o exemplo com orientação real.

Avance para **Casos que discriminam** e relacione o resultado observado ao próximo mecanismo.

## 03. Casos que discriminam

### Fala sugerida

O caso de paráfrase usa palavras diferentes da fonte. Ele testa algo que o caminho feliz não testa. O caso fora do escopo testa se o sistema reconhece ausência de evidência.

### Na demonstração

Troque o retriever e identifique quais perguntas mudam de comportamento.

### No quadro branco

id + categoria + pergunta + fontes relevantes

### Pergunta à turma

Por que registrar a categoria de cada caso?

### Resposta e transição

Para verificar se uma média global está escondendo concentração de falhas numa habilidade.

Avance para **Ranking com scores visíveis** e relacione o resultado observado ao próximo mecanismo.

## 04. Ranking com scores visíveis

### Fala sugerida

Aqui podemos explicar cada ponto do score. Quando adicionamos equivalências, sabemos exatamente quais palavras foram tratadas como próximas. Isso permite avaliar o ganho sem fingir uma busca neural.

### Na demonstração

Alterne as duas recuperações e inspecione a pontuação da pergunta com paráfrase.

### No quadro branco

score(q,d) = tamanho da interseção lexical

### Pergunta à turma

Por que a variante não demonstra compreensão semântica geral?

### Resposta e transição

Porque usa uma lista curta de equivalências programadas e só funciona nos casos cobertos por ela.

Avance para **Recall e precisão com k** e relacione o resultado observado ao próximo mecanismo.

## 05. Recall e precisão com k

### Fala sugerida

Uma fonte relevante em três resultados impõe precisão máxima de um terço. Isso é aritmética, não necessariamente um defeito grave. O recall responde outra pergunta: encontramos o que era necessário?

### Na demonstração

Aumente k e observe recall, precisão e os denominadores dos casos elegíveis.

### No quadro branco

recall = recuperados relevantes / relevantes; precisão = relevantes no top-k / k

### Pergunta à turma

Por que aumentar k pode elevar recall e reduzir precisão?

### Resposta e transição

Porque pode incluir a fonte necessária junto com mais documentos não relevantes.

Avance para **O teto imposto pelo conjunto** e relacione o resultado observado ao próximo mecanismo.

## 06. O teto imposto pelo conjunto

### Fala sugerida

Não comparem este valor com um número universal de precisão boa. Olhem primeiro a construção do conjunto. O teto ajuda a interpretar a distância entre resultado observado e resultado possível.

### Na demonstração

Defina k igual a três e compare a precisão com seu teto atingível.

### No quadro branco

precisão máxima = min(relevantes,k)/k

### Pergunta à turma

Precisão de 0,33 com k=3 é necessariamente ruim?

### Resposta e transição

Não. Com uma única fonte relevante, pode representar recuperação perfeita dentro desse protocolo.

Avance para **Rubrica por critérios** e relacione o resultado observado ao próximo mecanismo.

## 07. Rubrica por critérios

### Fala sugerida

Um limiar baixo aceita mais casos, inclusive respostas incompletas. Um limiar alto pode rejeitar respostas úteis. Precisamos inspecionar o que cada ponto significa antes de escolher um corte.

### Na demonstração

Mude a nota mínima e compare quais casos deixam de passar.

### No quadro branco

nota por critério → soma → limiar declarado

### Pergunta à turma

Aumentar o limiar melhora necessariamente a resposta do sistema?

### Resposta e transição

Não. Muda a classificação da avaliação, não a resposta produzida pelo sistema.

Avance para **Juiz determinístico e calibração** e relacione o resultado observado ao próximo mecanismo.

## 08. Juiz determinístico e calibração

### Fala sugerida

Eu consigo provocar um desacordo sem mudar o sistema. Isso mostra que o instrumento também tem comportamento. Precisamos avaliar o juiz antes de confiar no volume de notas que ele produz.

### Na demonstração

Aumente casos extras aprovados e localize os desacordos que aparecem.

### No quadro branco

juiz sintético ≠ avaliação de LLM

### Pergunta à turma

Trocar o juiz altera automaticamente a qualidade do sistema avaliado?

### Resposta e transição

Não. Altera a medida; qualquer melhoria real precisa ser verificada nos casos e respostas.

Avance para **Matriz e kappa do harness** e relacione o resultado observado ao próximo mecanismo.

## 09. Matriz e kappa do harness

### Fala sugerida

O kappa não substitui a inspeção dos desacordos. Ele resume uma propriedade do conjunto de rótulos. Dois casos com o mesmo defeito de rubrica podem revelar uma correção mais útil que a estatística sozinha.

### Na demonstração

Mude o desvio do juiz e confira a célula de aprovação indevida.

### No quadro branco

κ = (pₒ−pₑ)/(1−pₑ)

### Pergunta à turma

O que fazer depois de encontrar desacordo?

### Resposta e transição

Ler a pergunta, a resposta e a fonte para decidir se o erro está no sistema, na referência ou na rubrica.

Avance para **A média esconde categorias** e relacione o resultado observado ao próximo mecanismo.

## 10. A média esconde categorias

### Fala sugerida

Uma média aceitável pode esconder uma categoria inteira reprovada. A divisão por tipo de pergunta localiza esse padrão. Com poucos casos, tratamos o padrão como hipótese para investigar.

### Na demonstração

Alterne o retriever e compare fatos simples, paráfrases e fora de escopo.

### No quadro branco

global = média ponderada; categoria = diagnóstico

### Pergunta à turma

Por que uma categoria com um único caso exige cuidado?

### Resposta e transição

Porque uma mudança em uma observação altera a taxa drasticamente e não estima bem a população.

Avance para **Priorizar consertos** e relacione o resultado observado ao próximo mecanismo.

## 11. Priorizar consertos

### Fala sugerida

A tabela torna nossa hipótese de custo explícita. Isso é melhor que escolher o componente favorito. Mas uma melhoria só se confirma depois da alteração e de uma nova execução no mesmo conjunto.

### Na demonstração

Aumente o esforço de corrigir paráfrases e observe a ordem das intervenções.

### No quadro branco

prioridade inicial = falhas afetadas / esforço estimado

### Pergunta à turma

A maior razão impacto/esforço garante a melhor intervenção?

### Resposta e transição

Não. O impacto é estimado, pode haver dependências e a amostra pode ser pequena.

Avance para **Relatório que pode ser reexecutado** e relacione o resultado observado ao próximo mecanismo.

## 12. Relatório que pode ser reexecutado

### Fala sugerida

O relatório é consequência da execução. Quando mudamos um componente, rodamos novamente e comparamos. Uma narrativa sem dados e configuração não permite saber se houve progresso.

### Na demonstração

Troque k e o retriever e compare os dois resumos produzidos pela mesma coleção.

### No quadro branco

casos + configuração + resultados + limites

### Pergunta à turma

Qual é o artefato mais duradouro deste laboratório?

### Resposta e transição

O conjunto de casos com referências e o contrato do harness, que continuam úteis mesmo quando o sistema muda.
