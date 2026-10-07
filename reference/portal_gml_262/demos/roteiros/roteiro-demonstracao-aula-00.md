# Aula 00 — Recepção: construa seu mapa do curso

Do diagnóstico inicial ao primeiro artefato reproduzível

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Domínio de Python (autoavaliação)**: valor inicial `2`.
- **Álgebra linear (autoavaliação)**: valor inicial `2`.
- **Horas semanais de estudo**: valor inicial `4`.
- **Média dos sete melhores laboratórios**: valor inicial `7`.
- **Nota da prova**: valor inicial `7`.
- **Nota do projeto**: valor inicial `8`.
- **Laboratórios concluídos**: valor inicial `0`.

## 01. O produto que construiremos

### Fala sugerida

O semestre conecta representação de texto, modelos, recuperação, ferramentas e avaliação. Cada camada produz um artefato que pode ser inspecionado e reproduzido. Mova Laboratórios concluídos de 0 a 8 e acompanhe a passagem entre os produtos. Pergunto à turma: “Um chat funcionando prova que um sistema está pronto?” Não: ainda faltam evidências de qualidade, limites de custo e comportamento diante de falhas.

### Na demonstração

Mova Laboratórios concluídos de 0 a 8 e acompanhe a passagem entre os produtos.

### No quadro branco

Texto → modelo → RAG → ferramentas → agente → avaliação

### Pergunta à turma

Um chat funcionando prova que um sistema está pronto?

### Resposta e transição

Não: ainda faltam evidências de qualidade, limites de custo e comportamento diante de falhas.

Avance para **Diagnostique os pré-requisitos** e relacione o resultado observado ao próximo mecanismo.

## 02. Diagnostique os pré-requisitos

### Fala sugerida

A autoavaliação organiza o estudo inicial e não atribui nota. Python sustenta os laboratórios e álgebra linear sustenta a leitura das representações e da atenção. Compare Python 1/Álgebra 4 com Python 4/Álgebra 1; leia as recomendações específicas. Pergunto à turma: “Um pré-requisito fraco impede começar?” Ele indica uma lacuna para trabalhar cedo; a demonstração propõe tarefas concretas de revisão.

### Na demonstração

Compare Python 1/Álgebra 4 com Python 4/Álgebra 1; leia as recomendações específicas.

### No quadro branco

Python: listas, funções, matrizes; matemática: produto interno e probabilidade

### Pergunta à turma

Um pré-requisito fraco impede começar?

### Resposta e transição

Ele indica uma lacuna para trabalhar cedo; a demonstração propõe tarefas concretas de revisão.

Avance para **Percorra as sete camadas** e relacione o resultado observado ao próximo mecanismo.

## 03. Percorra as sete camadas

### Fala sugerida

O curso parte do texto e chega a sistemas avaliáveis. Um erro na camada de recuperação pede uma intervenção diferente de um erro de geração. Avance o número de laboratórios e identifique o último artefato disponível. Pergunto à turma: “Onde investigar uma resposta sem documento de apoio?” Primeiro na recuperação e na evidência entregue ao modelo; trocar a arquitetura sem diagnóstico não localiza a falha.

### Na demonstração

Avance o número de laboratórios e identifique o último artefato disponível.

### No quadro branco

Representação → arquitetura → treino → adaptação → RAG → agentes → avaliação

### Pergunta à turma

Onde investigar uma resposta sem documento de apoio?

### Resposta e transição

Primeiro na recuperação e na evidência entregue ao modelo; trocar a arquitetura sem diagnóstico não localiza a falha.

Avance para **Planeje o tempo que existe** e relacione o resultado observado ao próximo mecanismo.

## 04. Planeje o tempo que existe

### Fala sugerida

Uma agenda precisa reservar execução, leitura e análise dos resultados. A divisão exibida é uma sugestão ajustável de organização pessoal, não uma carga oficial adicional. Altere Horas semanais de 2 para 8 e compare o tempo sugerido para testar e escrever conclusões. Pergunto à turma: “Por que reservar tempo para análise além do código?” O entregável exige interpretar o que foi medido; terminar a execução sem explicar o resultado deixa a aprendizagem incompleta.

### Na demonstração

Altere Horas semanais de 2 para 8 e compare o tempo sugerido para testar e escrever conclusões.

### No quadro branco

Tempo disponível = leitura + implementação + análise

### Pergunta à turma

Por que reservar tempo para análise além do código?

### Resposta e transição

O entregável exige interpretar o que foi medido; terminar a execução sem explicar o resultado deixa a aprendizagem incompleta.

Avance para **Calcule a composição da avaliação** e relacione o resultado observado ao próximo mecanismo.

## 05. Calcule a composição da avaliação

### Fala sugerida

O plano do curso prevê laboratórios com peso 30%, prova com 30% e projeto com 40%. O campo de laboratórios representa a média após o descarte da menor entre oito notas. Altere apenas Projeto em um ponto e observe a variação de 0,4 na nota ponderada. Pergunto à turma: “Aumentar a prova em um ponto produz o mesmo efeito do projeto?” Não: produz 0,3 contra 0,4; os pesos multiplicam a variação individual.

### Na demonstração

Altere apenas Projeto em um ponto e observe a variação de 0,4 na nota ponderada.

### No quadro branco

Nota = 0,30 L + 0,30 P + 0,40 J

### Pergunta à turma

Aumentar a prova em um ponto produz o mesmo efeito do projeto?

### Resposta e transição

Não: produz 0,3 contra 0,4; os pesos multiplicam a variação individual.

Avance para **Entenda o percurso dos laboratórios** e relacione o resultado observado ao próximo mecanismo.

## 06. Entenda o percurso dos laboratórios

### Fala sugerida

Os oito laboratórios deixam produtos progressivos: tokenização, mini-GPT, decodificação, adaptação, RAG, ferramentas, agente e avaliação. Concluir um laboratório significa conseguir mostrar o artefato e defender uma medição. Selecione 3 e depois 6 laboratórios concluídos; identifique o próximo produto. Pergunto à turma: “O que distingue um notebook executado de um entregável?” Um entregável inclui entradas, configuração, resultados e interpretação suficientes para outra pessoa repetir o experimento.

### Na demonstração

Selecione 3 e depois 6 laboratórios concluídos; identifique o próximo produto.

### No quadro branco

Executar → medir → interpretar → versionar

### Pergunta à turma

O que distingue um notebook executado de um entregável?

### Resposta e transição

Um entregável inclui entradas, configuração, resultados e interpretação suficientes para outra pessoa repetir o experimento.

Avance para **Escolha o material pela pergunta** e relacione o resultado observado ao próximo mecanismo.

## 07. Escolha o material pela pergunta

### Fala sugerida

O plano informa objetivos, o guia ajuda no estudo e o notebook contém a execução. A demonstração interativa torna as relações visíveis, enquanto os roteiros de fala orientam o professor. Compare os cartões e associe a dúvida sobre uma fórmula ao material de estudo adequado. Pergunto à turma: “Todos os materiais precisam ser lidos na mesma ordem?” Não: a pergunta guia a consulta, mas objetivo, evidência e reflexão precisam estar conectados ao final.

### Na demonstração

Compare os cartões e associe a dúvida sobre uma fórmula ao material de estudo adequado.

### No quadro branco

Objetivo: plano; intuição: demonstração; execução: notebook; revisão: guia

### Pergunta à turma

Todos os materiais precisam ser lidos na mesma ordem?

### Resposta e transição

Não: a pergunta guia a consulta, mas objetivo, evidência e reflexão precisam estar conectados ao final.

Avance para **Use IA com responsabilidade acadêmica** e relacione o resultado observado ao próximo mecanismo.

## 08. Use IA com responsabilidade acadêmica

### Fala sugerida

Uma resposta produzida com ajuda de IA precisa continuar verificável e explicável pelo aluno. Registrar como a ferramenta foi usada permite distinguir assistência de evidência. Aumente Laboratórios concluídos e leia qual registro deve acompanhar o artefato atual. Pergunto à turma: “Uma resposta eloquente substitui uma medição?” Não: previsões devem ser confrontadas com execução ou fontes adequadas; registre o que foi conferido e o que continua incerto.

### Na demonstração

Aumente Laboratórios concluídos e leia qual registro deve acompanhar o artefato atual.

### No quadro branco

Ajuda recebida + verificação própria + limites encontrados

### Pergunta à turma

Uma resposta eloquente substitui uma medição?

### Resposta e transição

Não: previsões devem ser confrontadas com execução ou fontes adequadas; registre o que foi conferido e o que continua incerto.

Avance para **Prepare um ambiente reproduzível** e relacione o resultado observado ao próximo mecanismo.

## 09. Prepare um ambiente reproduzível

### Fala sugerida

O ambiente precisa importar dependências e executar um exemplo mínimo antes do trabalho principal. Esta tela é um checklist didático e não executa comandos no computador do aluno. Observe a sequência de verificação e relacione a recomendação à sua autoavaliação de Python. Pergunto à turma: “Por que registrar versões se hoje tudo funciona?” Uma atualização pode alterar resultados ou APIs; o registro ajuda a distinguir mudança do código de mudança do ambiente.

### Na demonstração

Observe a sequência de verificação e relacione a recomendação à sua autoavaliação de Python.

### No quadro branco

Ambiente isolado → dependências → execução mínima → versões

### Pergunta à turma

Por que registrar versões se hoje tudo funciona?

### Resposta e transição

Uma atualização pode alterar resultados ou APIs; o registro ajuda a distinguir mudança do código de mudança do ambiente.

Avance para **Feche com um plano observável** e relacione o resultado observado ao próximo mecanismo.

## 10. Feche com um plano observável

### Fala sugerida

O objetivo da recepção é sair com um próximo passo concreto, tempo reservado e entendimento da avaliação. Os números exibidos são uma simulação de planejamento, não o boletim real do curso. Configure sua disponibilidade e uma meta de laboratório; leia o próximo passo calculado. Pergunto à turma: “Que evidência mostra que a recepção cumpriu seu objetivo?” O aluno consegue abrir o material correto, executar o exemplo inicial e explicar o produto que construirá em seguida.

### Na demonstração

Configure sua disponibilidade e uma meta de laboratório; leia o próximo passo calculado.

### No quadro branco

Próximo passo + prazo pessoal + evidência de conclusão

### Pergunta à turma

Que evidência mostra que a recepção cumpriu seu objetivo?

### Resposta e transição

O aluno consegue abrir o material correto, executar o exemplo inicial e explicar o produto que construirá em seguida.
