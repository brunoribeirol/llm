# Aula 24 — Sistemas multiagentes: dividir tem um preço

Compare arquiteturas com contas explícitas de tokens, dependências, latência e probabilidade. Os números são parâmetros didáticos, não benchmarks de frameworks.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Trabalhadores / estágios**: valor inicial `3`.
- **Passos por trabalhador**: valor inicial `2`.
- **Acerto de cada estágio (%)**: valor inicial `90`.
- **Contexto por trabalhador (tokens)**: valor inicial `500`.
- **Subtarefas independentes em paralelo**: valor inicial `True`.
- **Copiar histórico inteiro para cada trabalhador**: valor inicial `False`.

## 01. A mesma tarefa, duas arquiteturas

### Fala sugerida

Se mudarmos a tarefa junto com a arquitetura, perdemos a comparação. Primeiro fixamos o que precisa ser entregue. Depois medimos que coordenação foi adicionada.

### Na demonstração

Defina três trabalhadores e compare a tarefa nos dois desenhos.

### No quadro branco

mesmo objetivo + mesmo conjunto de teste

### Pergunta à turma

Mais agentes é evidência de maior qualidade?

### Resposta e transição

Não. É uma mudança de arquitetura que deve ser avaliada na mesma tarefa.

Avance para **As três razões para dividir** e relacione o resultado observado ao próximo mecanismo.

## 02. As três razões para dividir

### Fala sugerida

Um pesquisador e um revisor só são diferentes se têm decisões ou evidências distintas. Rótulos sozinhos não reduzem incerteza. Quero saber o que cada participante vê e pode fazer.

### Na demonstração

Aumente trabalhadores e compare competências e dados necessários.

### No quadro branco

especialização; independência; contexto necessário

### Pergunta à turma

Quando trocar só o prompt pode ser suficiente?

### Resposta e transição

Quando não há novas ferramentas, dados ou decisões independentes que justifiquem coordenação persistente.

Avance para **Orquestrador e trabalhadores** e relacione o resultado observado ao próximo mecanismo.

## 03. Orquestrador e trabalhadores

### Fala sugerida

A unidade de delegação precisa caber numa instrução clara. O trabalhador deve saber o que entregar e como verificar. Repassar tudo transfere também ambiguidades e custo.

### Na demonstração

Marque copiar histórico inteiro e compare os pacotes enviados.

### No quadro branco

tarefa local + evidências necessárias → resultado verificável

### Pergunta à turma

O que um bom resultado de trabalhador contém?

### Resposta e transição

Resposta ao subproblema, evidências, incertezas e um formato que o orquestrador consiga verificar.

Avance para **Pipeline com dependências** e relacione o resultado observado ao próximo mecanismo.

## 04. Pipeline com dependências

### Fala sugerida

O botão de paralelismo não remove uma dependência de dados. Extrair precisa terminar antes de validar o que foi extraído. A arquitetura deve refletir a tarefa, não a quantidade de processos.

### Na demonstração

Compare o diagrama serial com a opção de paralelismo da pesquisa independente.

### No quadro branco

A → B → C: dependência impõe ordem

### Pergunta à turma

Por que uma busca independente pode ser paralela e uma transformação encadeada não?

### Resposta e transição

Na busca, os ramos já possuem as entradas; na transformação, cada entrada só existe após o estágio anterior.

Avance para **Debate e crítico** e relacione o resultado observado ao próximo mecanismo.

## 05. Debate e crítico

### Fala sugerida

Peço ao crítico uma condição verificável, não uma opinião mais confiante. Sem fonte, ele pode repetir o erro com outras palavras. A utilidade do debate depende do que ele consegue detectar.

### Na demonstração

Altere a taxa de acerto e observe o contraste entre revisão com verificador e mera concordância.

### No quadro branco

concordância ≠ verificação independente

### Pergunta à turma

Votar entre cópias do mesmo raciocínio elimina erro correlacionado?

### Resposta e transição

Não. A correlação limita o ganho; a hipótese de independência deve ser justificada.

Avance para **Painel de especialistas** e relacione o resultado observado ao próximo mecanismo.

## 06. Painel de especialistas

### Fala sugerida

O painel desloca parte do problema para a síntese. Alguém precisa comparar evidências incompatíveis. Esse trabalho tem custo e deve aparecer no orçamento.

### Na demonstração

Aumente trabalhadores e conte resultados que precisam ser integrados.

### No quadro branco

N saídas → agregação + resolução de conflitos

### Pergunta à turma

Quem decide quando dois especialistas divergem?

### Resposta e transição

Uma regra de agregação ou um responsável com acesso às evidências, não a mera quantidade de textos.

Avance para **Custo é soma, latência pode ser máximo** e relacione o resultado observado ao próximo mecanismo.

## 07. Custo é soma, latência pode ser máximo

### Fala sugerida

Aqui a mesma quantidade de trabalho acontece em menos tempo de parede. Isso é útil, mas não é desconto automático na fatura. Limites de concorrência também podem reduzir o ganho.

### Na demonstração

Alterne paralelismo e compare tempo serial, paralelo e trabalho total.

### No quadro branco

latência ≈ max(tᵢ)+overhead; trabalho = Σtᵢ

### Pergunta à turma

Paralelismo reduz necessariamente os tokens pagos?

### Resposta e transição

Não. As mesmas chamadas continuam existindo e podem ganhar contexto de coordenação.

Avance para **O preço do contexto compartilhado** e relacione o resultado observado ao próximo mecanismo.

## 08. O preço do contexto compartilhado

### Fala sugerida

A mensagem enviada ao trabalhador é uma decisão de arquitetura. Um resumo verificável pode ser menor que o histórico bruto. O corte precisa preservar as evidências necessárias à subtarefa.

### Na demonstração

Aumente contexto e marque copiar histórico inteiro; compare os totais.

### No quadro branco

tokens de entrada = trabalhadores × passos × pacote

### Pergunta à turma

Resumir sempre melhora o sistema?

### Resposta e transição

Não. Pode economizar contexto e também remover detalhes que o trabalhador precisa para acertar.

Avance para **Orçamentos que se multiplicam** e relacione o resultado observado ao próximo mecanismo.

## 09. Orçamentos que se multiplicam

### Fala sugerida

O limite precisa existir onde os recursos são compartilhados. Dar a cada trabalhador o orçamento inteiro multiplica a exposição. O total da execução deve incluir planejamento e síntese.

### Na demonstração

Aumente trabalhadores e passos e observe as chamadas máximas.

### No quadro branco

B global ≥ coordenação + Σ bᵢ

### Pergunta à turma

Quem deve controlar o orçamento total?

### Resposta e transição

O coordenador ou runtime que vê todas as chamadas, além dos limites locais.

Avance para **Erro propagado pelo pipeline** e relacione o resultado observado ao próximo mecanismo.

## 10. Erro propagado pelo pipeline

### Fala sugerida

Noventa por cento por estágio parece confortável. Multipliquem ao encadear vários estágios obrigatórios. Se os erros forem correlacionados, precisaremos de outro modelo, não de repetir esta conta sem ressalva.

### Na demonstração

Aumente estágios mantendo noventa por cento de acerto e acompanhe a queda.

### No quadro branco

P(todos corretos) = ∏ pᵢ, sob independência

### Pergunta à turma

Um pipeline com cinco estágios a 90% acerta 90% no total?

### Resposta e transição

Sob as hipóteses indicadas, não: 0,9⁵ é aproximadamente 59%.

Avance para **Verificar e tentar novamente** e relacione o resultado observado ao próximo mecanismo.

## 11. Verificar e tentar novamente

### Fala sugerida

A melhoria vem de detectar a falha antes de propagá-la. Se o verificador aprovar uma resposta errada, esta fórmula deixa de representar o sistema. Medir a qualidade do verificador faz parte da avaliação.

### Na demonstração

Compare sem repetição e uma repetição para os mesmos estágios e acerto.

### No quadro branco

p′ = 1−(1−p)²; custo extra não é zero

### Pergunta à turma

Repetir duas vezes garante independência das tentativas?

### Resposta e transição

Não. O mesmo contexto e o mesmo modelo podem repetir o mesmo erro.

Avance para **Escolher a arquitetura mínima suficiente** e relacione o resultado observado ao próximo mecanismo.

## 12. Escolher a arquitetura mínima suficiente

### Fala sugerida

Peço uma arquitetura que possamos explicar e medir. Se um componente não muda evidências, decisões ou paralelismo, tentamos removê-lo. Depois verificamos se a versão menor preserva o resultado.

### Na demonstração

Escolha uma configuração e defenda se um pipeline ou agente único resolveria o mesmo objetivo.

### No quadro branco

por que dividir? quem vê o quê? onde depurar?

### Pergunta à turma

Qual comparação sustenta a adoção de multiagentes?

### Resposta e transição

Uma avaliação controlada contra uma arquitetura mais simples, mostrando ganho relevante e seu custo.
