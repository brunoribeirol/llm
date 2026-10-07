# Aula 10 — Do Transformer ao LLM: capacidade, escolha e contexto

Orçamento de treino, especialistas, decodificação e diagnóstico do serving

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Parâmetros compartilhados (bilhões)**: valor inicial `4`.
- **Tokens de treino (bilhões)**: valor inicial `100`.
- **Quantidade de especialistas**: valor inicial `4`.
- **Especialistas ativos por token**: valor inicial `2`.
- **Temperatura**: valor inicial `1`.
- **Top-k**: valor inicial `3`.
- **Top-p**: valor inicial `0.9`.
- **Sorteio determinístico u**: valor inicial `0.42`.
- **Estrutura do prompt**: valor inicial `instruction`.

## 01. Quatro chamados, quatro perguntas

### Fala sugerida

Custo inesperado, repetição, saídas diferentes e informação ignorada podem surgir sem defeito de implementação. Localizar o mecanismo evita trocar pesos para resolver uma decisão de inferência. Altere Temperatura e Especialistas ativos; identifique qual chamado cada controle pode afetar. Pergunto à turma: “Todo comportamento indesejado pede fine-tuning?” Não; orçamento, algoritmo de seleção, formato da entrada ou serving podem explicar o sintoma.

### Na demonstração

Altere Temperatura e Especialistas ativos; identifique qual chamado cada controle pode afetar.

### No quadro branco

Capacidade; decodificação; contexto; execução

### Pergunta à turma

Todo comportamento indesejado pede fine-tuning?

### Resposta e transição

Não; orçamento, algoritmo de seleção, formato da entrada ou serving podem explicar o sintoma.

Avance para **Calcule um orçamento de treino** e relacione o resultado observado ao próximo mecanismo.

## 02. Calcule um orçamento de treino

### Fala sugerida

Uma aproximação comum para treino de Transformers densos é C≈6ND, onde N é parâmetros e D é tokens. A conta é uma estimativa de operações, não uma previsão de tempo nem uma lei de qualidade. Dobre Parâmetros mantendo Tokens e observe os FLOPs aproximados. Pergunto à turma: “Dobrar o orçamento garante a mesma melhora em toda tarefa?” Não; o resultado depende de dados, regime de treino, arquitetura e avaliação.

### Na demonstração

Dobre Parâmetros mantendo Tokens e observe os FLOPs aproximados.

### No quadro branco

C ≈ 6 × N × D

### Pergunta à turma

Dobrar o orçamento garante a mesma melhora em toda tarefa?

### Resposta e transição

Não; o resultado depende de dados, regime de treino, arquitetura e avaliação.

Avance para **Separe parâmetros totais de ativos** e relacione o resultado observado ao próximo mecanismo.

## 03. Separe parâmetros totais de ativos

### Fala sugerida

Uma camada MoE possui vários especialistas, mas encaminha cada token a apenas alguns. A miniatura atribui um bilhão de parâmetros a cada especialista e separa a parte compartilhada. Compare Especialistas=8, Ativos=2 com Ativos=4; veja memória de pesos e trabalho ativo. Pergunto à turma: “O modelo precisa armazenar apenas os especialistas ativados por um token?” Não em geral; o conjunto de pesos precisa estar disponível no sistema, embora cada token use uma parte.

### Na demonstração

Compare Especialistas=8, Ativos=2 com Ativos=4; veja memória de pesos e trabalho ativo.

### No quadro branco

N_total=N_comp+E·N_exp; N_ativo=N_comp+k·N_exp

### Pergunta à turma

O modelo precisa armazenar apenas os especialistas ativados por um token?

### Resposta e transição

Não em geral; o conjunto de pesos precisa estar disponível no sistema, embora cada token use uma parte.

Avance para **Acompanhe o roteamento top-k** e relacione o resultado observado ao próximo mecanismo.

## 04. Acompanhe o roteamento top-k

### Fala sugerida

O roteador produz scores para os especialistas e escolhe k deles por token. A matriz calculada usa scores determinísticos didáticos e expõe quais especialistas recebem cada token. Aumente Ativos e compare a matriz de despacho e a contagem por especialista. Pergunto à turma: “Escolher especialistas equivale a escolher palavras do vocabulário?” Não; roteamento seleciona computação interna, enquanto decodificação seleciona a saída.

### Na demonstração

Aumente Ativos e compare a matriz de despacho e a contagem por especialista.

### No quadro branco

token → scores do roteador → top-k → especialistas → combinação

### Pergunta à turma

Escolher especialistas equivale a escolher palavras do vocabulário?

### Resposta e transição

Não; roteamento seleciona computação interna, enquanto decodificação seleciona a saída.

Avance para **Procure desequilíbrio de carga** e relacione o resultado observado ao próximo mecanismo.

## 05. Procure desequilíbrio de carga

### Fala sugerida

Um roteador pode concentrar tokens em poucos especialistas, deixando capacidade ociosa e filas desiguais. A tela mede a distribuição do despacho da miniatura e não simula treinamento do roteador. Mude Quantidade de especialistas e observe máximo, média e cargas por especialista. Pergunto à turma: “Especialistas iguais em tamanho garantem carga igual?” Não; a distribuição das escolhas do roteador pode ser desigual, exigindo mecanismos e métricas de balanceamento.

### Na demonstração

Mude Quantidade de especialistas e observe máximo, média e cargas por especialista.

### No quadro branco

Carga por especialista; razão máximo/média

### Pergunta à turma

Especialistas iguais em tamanho garantem carga igual?

### Resposta e transição

Não; a distribuição das escolhas do roteador pode ser desigual, exigindo mecanismos e métricas de balanceamento.

Avance para **O treino terminou: logits não escolhem sozinhos** e relacione o resultado observado ao próximo mecanismo.

## 06. O treino terminou: logits não escolhem sozinhos

### Fala sugerida

O modelo fornece scores para próximos tokens e o algoritmo de decodificação decide como usá-los. Os seis logits desta demonstração são fixos e públicos. Observe os logits e ajuste Temperatura sem mudar nenhum peso. Pergunto à turma: “Mudar temperatura altera os pesos do modelo?” Não; altera como os mesmos scores são convertidos em probabilidades.

### Na demonstração

Observe os logits e ajuste Temperatura sem mudar nenhum peso.

### No quadro branco

logits → transformação → distribuição → seleção

### Pergunta à turma

Mudar temperatura altera os pesos do modelo?

### Resposta e transição

Não; altera como os mesmos scores são convertidos em probabilidades.

Avance para **Greedy e beam otimizam objetivos específicos** e relacione o resultado observado ao próximo mecanismo.

## 07. Greedy e beam otimizam objetivos específicos

### Fala sugerida

Greedy escolhe o maior score em cada passo e pode perder a sequência de maior probabilidade global. O pequeno grafo com dois passos mostra um caso em que ampliar a busca muda o resultado. Compare o caminho que começa com 0,55 com aquele que começa com 0,45 e calcule os produtos. Pergunto à turma: “A sequência mais provável é necessariamente a melhor resposta?” Não; probabilidade do modelo e qualidade da aplicação são objetivos diferentes.

### Na demonstração

Compare o caminho que começa com 0,55 com aquele que começa com 0,45 e calcule os produtos.

### No quadro branco

P(sequência)=produto das probabilidades condicionais

### Pergunta à turma

A sequência mais provável é necessariamente a melhor resposta?

### Resposta e transição

Não; probabilidade do modelo e qualidade da aplicação são objetivos diferentes.

Avance para **Temperatura controla concentração** e relacione o resultado observado ao próximo mecanismo.

## 08. Temperatura controla concentração

### Fala sugerida

Dividir logits por uma temperatura positiva altera o contraste antes do softmax. Temperaturas menores concentram massa, e temperaturas maiores a distribuem. Compare T=0,2 e T=2 e leia a entropia calculada. Pergunto à turma: “Temperatura zero é usada diretamente nesta fórmula?” Não; o limite se relaciona ao máximo, mas dividir por zero é indefinido, por isso o controle usa T positivo.

### Na demonstração

Compare T=0,2 e T=2 e leia a entropia calculada.

### No quadro branco

pᵢ=softmax(logitᵢ/T); H=−soma pᵢ ln pᵢ

### Pergunta à turma

Temperatura zero é usada diretamente nesta fórmula?

### Resposta e transição

Não; o limite se relaciona ao máximo, mas dividir por zero é indefinido, por isso o controle usa T positivo.

Avance para **Top-k fixa quantidade, top-p fixa massa** e relacione o resultado observado ao próximo mecanismo.

## 09. Top-k fixa quantidade, top-p fixa massa

### Fala sugerida

Top-k conserva k candidatos e top-p conserva o menor prefixo ordenado cuja massa atinge p. Ambos renormalizam a distribuição após remover candidatos. Ajuste Top-k e Top-p e compare quais palavras permanecem em cada método. Pergunto à turma: “Top-p=0,9 mantém sempre 90% das palavras?” Não; mantém candidatos suficientes para cobrir pelo menos 90% da massa de probabilidade.

### Na demonstração

Ajuste Top-k e Top-p e compare quais palavras permanecem em cada método.

### No quadro branco

Top-k: k itens; top-p: massa acumulada ≥ p

### Pergunta à turma

Top-p=0,9 mantém sempre 90% das palavras?

### Resposta e transição

Não; mantém candidatos suficientes para cobrir pelo menos 90% da massa de probabilidade.

Avance para **Amostre de forma verificável** e relacione o resultado observado ao próximo mecanismo.

## 10. Amostre de forma verificável

### Fala sugerida

Um número u entre zero e um seleciona o intervalo correspondente na distribuição acumulada. O controle permite repetir exatamente o sorteio e separar distribuição de aleatoriedade. Mova Sorteio determinístico u e compare escolhas sob distribuição completa, top-k e top-p. Pergunto à turma: “Duas execuções com os mesmos logits podem produzir tokens diferentes?” Sim se usarem sorteios diferentes; a política de amostragem e a semente precisam ser registradas.

### Na demonstração

Mova Sorteio determinístico u e compare escolhas sob distribuição completa, top-k e top-p.

### No quadro branco

Escolher menor j com somaᵢ≤ⱼ pᵢ ≥ u

### Pergunta à turma

Duas execuções com os mesmos logits podem produzir tokens diferentes?

### Resposta e transição

Sim se usarem sorteios diferentes; a política de amostragem e a semente precisam ser registradas.

Avance para **O prompt fornece uma tarefa em contexto** e relacione o resultado observado ao próximo mecanismo.

## 11. O prompt fornece uma tarefa em contexto

### Fala sugerida

Instrução, formato, exemplos e evidência alteram a entrada usada para prever a continuação. Os cartões mostram modelos de prompt, sem chamar um LLM nem prometer respostas específicas. Alterne as quatro estruturas e identifique qual informação foi acrescentada. Pergunto à turma: “Few-shot atualiza pesos durante a chamada?” No uso usual de aprendizado em contexto, não; exemplos entram no prefixo que condiciona a previsão.

### Na demonstração

Alterne as quatro estruturas e identifique qual informação foi acrescentada.

### No quadro branco

Pedido + restrições + exemplos + evidência + formato

### Pergunta à turma

Few-shot atualiza pesos durante a chamada?

### Resposta e transição

No uso usual de aprendizado em contexto, não; exemplos entram no prefixo que condiciona a previsão.

Avance para **Caber na janela não garante uso da evidência** e relacione o resultado observado ao próximo mecanismo.

## 12. Caber na janela não garante uso da evidência

### Fala sugerida

A janela limita a entrada, mas não mede se o modelo recuperou a informação relevante. A inspeção deve testar posição da evidência, instrução e necessidade de recuperação. Selecione Prompt com documento e examine onde ficam tarefa, evidência e resposta esperada. Pergunto à turma: “Como investigar um fato presente no documento que foi ignorado?” Teste perguntas verificáveis, posição da evidência e formatos de contexto, mantendo os demais fatores controlados.

### Na demonstração

Selecione Prompt com documento e examine onde ficam tarefa, evidência e resposta esperada.

### No quadro branco

Cabe na janela ≠ informação usada corretamente

### Pergunta à turma

Como investigar um fato presente no documento que foi ignorado?

### Resposta e transição

Teste perguntas verificáveis, posição da evidência e formatos de contexto, mantendo os demais fatores controlados.

Avance para **Diferencie os gargalos do serving** e relacione o resultado observado ao próximo mecanismo.

## 13. Diferencie os gargalos do serving

### Fala sugerida

Prefill processa o prefixo e decode produz tokens sucessivos; ambos usam recursos de forma diferente. MoE, cache e batching afetam a execução, mas o navegador exibe apenas contas de capacidade e fluxo. Altere Parâmetros e Ativos; compare pesos totais, ativos e fases do atendimento. Pergunto à turma: “Reduzir parâmetros ativos garante menor latência ponta a ponta?” Não; comunicação, leitura de memória, tamanho do lote e implementação também entram no tempo total.

### Na demonstração

Altere Parâmetros e Ativos; compare pesos totais, ativos e fases do atendimento.

### No quadro branco

Prefill → primeiro token → decode; latência ≠ throughput

### Pergunta à turma

Reduzir parâmetros ativos garante menor latência ponta a ponta?

### Resposta e transição

Não; comunicação, leitura de memória, tamanho do lote e implementação também entram no tempo total.

Avance para **Feche cada chamado com uma evidência** e relacione o resultado observado ao próximo mecanismo.

## 14. Feche cada chamado com uma evidência

### Fala sugerida

Uma intervenção útil vem acompanhada de uma previsão mensurável. A síntese liga orçamento, roteamento, decodificação e contexto aos números produzidos ao longo da demonstração. Escolha um dos quatro chamados e defenda uma mudança usando uma medida da tela. Pergunto à turma: “O que torna o diagnóstico melhor que apenas tentar configurações?” Uma hipótese prevê qual medida deve mudar e permite rejeitar a explicação quando o resultado não acompanha essa previsão.

### Na demonstração

Escolha um dos quatro chamados e defenda uma mudança usando uma medida da tela.

### No quadro branco

Sintoma → hipótese → controle alterado → medida → conclusão

### Pergunta à turma

O que torna o diagnóstico melhor que apenas tentar configurações?

### Resposta e transição

Uma hipótese prevê qual medida deve mudar e permite rejeitar a explicação quando o resultado não acompanha essa previsão.
