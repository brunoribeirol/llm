# Aula 08 — Famílias de Transformers e a conta da atenção

Máscaras, tarefas, cache KV, atenção local e destilação

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Família**: valor inicial `encoder`.
- **Comprimento do contexto**: valor inicial `16`.
- **Cabeças de query**: valor inicial `8`.
- **Cabeças KV**: valor inicial `8`.
- **Camadas**: valor inicial `12`.
- **Raio da janela local**: valor inicial `2`.
- **Temperatura da distribuição docente**: valor inicial `2`.

## 01. A primeira escolha é quem pode ler quem

### Fala sugerida

Uma máscara determina quais pares de posições podem interagir em um bloco. O padrão de acesso deve combinar com a informação disponível na tarefa. Alterne Encoder e Decoder e leia a primeira linha da máscara. Pergunto à turma: “Permitir acesso ao token futuro é válido ao prever o próximo token?” Não durante a previsão causal; isso introduziria informação indisponível no momento de gerar.

### Na demonstração

Alterne Encoder e Decoder e leia a primeira linha da máscara.

### No quadro branco

Bidirecional: j livre; causal: j ≤ i

### Pergunta à turma

Permitir acesso ao token futuro é válido ao prever o próximo token?

### Resposta e transição

Não durante a previsão causal; isso introduziria informação indisponível no momento de gerar.

Avance para **Encoder: represente uma entrada completa** e relacione o resultado observado ao próximo mecanismo.

## 02. Encoder: represente uma entrada completa

### Fala sugerida

Um encoder bidirecional transforma cada posição usando contexto dos dois lados. Isso é adequado quando a entrada inteira está disponível antes de produzir uma classificação ou representação. Escolha Encoder e observe as conexões que chegam à posição central. Pergunto à turma: “O encoder é um gerador autorregressivo pronto por definição?” Não; ele produz representações, e a tarefa de saída requer uma cabeça e um objetivo compatíveis.

### Na demonstração

Escolha Encoder e observe as conexões que chegam à posição central.

### No quadro branco

Entrada completa → estados contextualizados

### Pergunta à turma

O encoder é um gerador autorregressivo pronto por definição?

### Resposta e transição

Não; ele produz representações, e a tarefa de saída requer uma cabeça e um objetivo compatíveis.

Avance para **MLM: recupere uma lacuna** e relacione o resultado observado ao próximo mecanismo.

## 03. MLM: recupere uma lacuna

### Fala sugerida

Na previsão de tokens mascarados, parte da entrada é escondida e o modelo usa o contexto disponível para reconstruí-la. Os candidatos desta tela são ilustrativos e não vêm de um modelo BERT em execução. Compare a lacuna com o contexto à esquerda e à direita no diagrama. Pergunto à turma: “Ver o lado direito nesse objetivo é vazamento?” Não; faz parte da entrada permitida para reconstruir a lacuna, diferentemente da geração causal.

### Na demonstração

Compare a lacuna com o contexto à esquerda e à direita no diagrama.

### No quadro branco

texto corrompido → prever posições selecionadas

### Pergunta à turma

Ver o lado direito nesse objetivo é vazamento?

### Resposta e transição

Não; faz parte da entrada permitida para reconstruir a lacuna, diferentemente da geração causal.

Avance para **Cabeça de classificação: uma saída supervisionada** e relacione o resultado observado ao próximo mecanismo.

## 04. Cabeça de classificação: uma saída supervisionada

### Fala sugerida

Uma representação agregada pode alimentar uma camada que prevê rótulos. O custo de uma decisão não exige gerar uma frase inteira quando a saída desejada é um enum. Compare a linha de classificação com a linha de geração de vários tokens. Pergunto à turma: “O token CLS sabe classificar sem treinamento adequado?” Não; sua utilidade depende do pré-treinamento, da cabeça e do ajuste ou protocolo usados.

### Na demonstração

Compare a linha de classificação com a linha de geração de vários tokens.

### No quadro branco

h agregado → W h + b → softmax de classes

### Pergunta à turma

O token CLS sabe classificar sem treinamento adequado?

### Resposta e transição

Não; sua utilidade depende do pré-treinamento, da cabeça e do ajuste ou protocolo usados.

Avance para **Encoder–decoder: entrada e saída separadas** e relacione o resultado observado ao próximo mecanismo.

## 05. Encoder–decoder: entrada e saída separadas

### Fala sugerida

O encoder lê a origem inteira e o decoder gera o destino causalmente. Cross-attention permite ao decoder consultar estados da origem em cada passo. Escolha Encoder–decoder e acompanhe separadamente autoatenção de origem, destino e atenção cruzada. Pergunto à turma: “A máscara causal do destino proíbe ler o fim da origem?” Não; restringe o futuro do destino, enquanto toda a origem já está disponível.

### Na demonstração

Escolha Encoder–decoder e acompanhe separadamente autoatenção de origem, destino e atenção cruzada.

### No quadro branco

Origem → encoder; prefixo → decoder; decoder consulta encoder

### Pergunta à turma

A máscara causal do destino proíbe ler o fim da origem?

### Resposta e transição

Não; restringe o futuro do destino, enquanto toda a origem já está disponível.

Avance para **Decoder: prever uma continuação** e relacione o resultado observado ao próximo mecanismo.

## 06. Decoder: prever uma continuação

### Fala sugerida

Um decoder causal prevê a continuação a partir de um prefixo. Durante o treino, várias posições podem ser processadas em paralelo com máscara, mas gerar novos tokens continua sequencial. Escolha Decoder e avance o comprimento; compare treino com laço de geração. Pergunto à turma: “Máscara causal impede paralelismo de treino?” Não; todas as entradas do lote já são conhecidas, e a máscara impede acesso indevido sem exigir uma RNN.

### Na demonstração

Escolha Decoder e avance o comprimento; compare treino com laço de geração.

### No quadro branco

P(x₁…x_T)=produto P(xₜ|x_<ₜ)

### Pergunta à turma

Máscara causal impede paralelismo de treino?

### Resposta e transição

Não; todas as entradas do lote já são conhecidas, e a máscara impede acesso indevido sem exigir uma RNN.

Avance para **Identifique o trabalho repetido na geração** e relacione o resultado observado ao próximo mecanismo.

## 07. Identifique o trabalho repetido na geração

### Fala sugerida

As keys e values de posições anteriores não precisam ser recalculadas a cada novo token em um decoder causal usual. O cache reutiliza esses tensores, mas cresce com contexto, camadas e lote. Dobre Comprimento e observe a quantidade de posições armazenadas. Pergunto à turma: “KV cache guarda as probabilidades finais de todos os tokens?” Não; armazena keys e values intermediários por camada para evitar recomputação.

### Na demonstração

Dobre Comprimento e observe a quantidade de posições armazenadas.

### No quadro branco

Novo token: calcular Q,K,V novos; reutilizar K,V anteriores

### Pergunta à turma

KV cache guarda as probabilidades finais de todos os tokens?

### Resposta e transição

Não; armazena keys e values intermediários por camada para evitar recomputação.

Avance para **Calcule a memória do KV cache** e relacione o resultado observado ao próximo mecanismo.

## 08. Calcule a memória do KV cache

### Fala sugerida

A conta usa lote 1, dimensão de cabeça 64 e dois bytes por elemento. O número de cabeças KV efetivo é ajustado para um divisor válido das cabeças de query escolhidas. Dobre Camadas e depois Contexto; veja a memória dobrar em cada alteração. Pergunto à turma: “O fator inicial 2 representa duas cabeças?” Não; representa os dois tensores, keys e values.

### Na demonstração

Dobre Camadas e depois Contexto; veja a memória dobrar em cada alteração.

### No quadro branco

Bytes = 2 × B × L × T × H_KV × d_head × bytes/elemento

### Pergunta à turma

O fator inicial 2 representa duas cabeças?

### Resposta e transição

Não; representa os dois tensores, keys e values.

Avance para **Corte pares com uma janela local** e relacione o resultado observado ao próximo mecanismo.

## 09. Corte pares com uma janela local

### Fala sugerida

Atenção local lê posições próximas e reduz a quantidade de conexões por camada. O gráfico usa uma janela bidirecional didática; posições globais precisam ser planejadas separadamente. Aumente Raio e compare a matriz esparsa com o total de pares densos. Pergunto à turma: “Uma janela de raio r conecta qualquer posição em uma camada?” Não; o alcance cresce ao empilhar camadas, e nós globais podem criar atalhos adicionais.

### Na demonstração

Aumente Raio e compare a matriz esparsa com o total de pares densos.

### No quadro branco

Pares densos ≈ T²; locais ≈ T(2r+1), com bordas

### Pergunta à turma

Uma janela de raio r conecta qualquer posição em uma camada?

### Resposta e transição

Não; o alcance cresce ao empilhar camadas, e nós globais podem criar atalhos adicionais.

Avance para **Compartilhe K e V entre queries** e relacione o resultado observado ao próximo mecanismo.

## 10. Compartilhe K e V entre queries

### Fala sugerida

MQA usa um único conjunto KV e GQA compartilha conjuntos entre grupos de queries. A redução de cache depende das cabeças KV, não de reduzir automaticamente o número de cabeças de query. Mantenha Heads=8 e compare KV=8, 2 e 1. Pergunto à turma: “A memória de KV cai quatro vezes de 8 para 2 cabeças KV?” Sim com lote, camadas, contexto, dimensão e precisão fixos nesta conta.

### Na demonstração

Mantenha Heads=8 e compare KV=8, 2 e 1.

### No quadro branco

MHA: H_KV=H_Q; GQA: 1<H_KV<H_Q; MQA: H_KV=1

### Pergunta à turma

A memória de KV cai quatro vezes de 8 para 2 cabeças KV?

### Resposta e transição

Sim com lote, camadas, contexto, dimensão e precisão fixos nesta conta.

Avance para **Destile uma distribuição, não só um rótulo** e relacione o resultado observado ao próximo mecanismo.

## 11. Destile uma distribuição, não só um rótulo

### Fala sugerida

A distribuição do professor mostra relações entre classes além da primeira colocada. Temperatura maior torna essa distribuição mais suave; esta miniatura calcula softmax de logits fixos. Aumente Temperatura e observe a massa nas classes não vencedoras. Pergunto à turma: “Aumentar a temperatura cria novos conhecimentos?” Não; torna diferenças relativas de scores mais visíveis ao objetivo, sem acrescentar evidência externa.

### Na demonstração

Aumente Temperatura e observe a massa nas classes não vencedoras.

### No quadro branco

p_T = softmax(logits/T); aluno aproxima a distribuição docente

### Pergunta à turma

Aumentar a temperatura cria novos conhecimentos?

### Resposta e transição

Não; torna diferenças relativas de scores mais visíveis ao objetivo, sem acrescentar evidência externa.

Avance para **Escolha pela tarefa e pelo gargalo** e relacione o resultado observado ao próximo mecanismo.

## 12. Escolha pela tarefa e pelo gargalo

### Fala sugerida

Família, máscara, cache e padrão de atenção são decisões conectadas ao caso de uso. A comparação final explicita representações, geração e memória, sem eleger uma arquitetura universal. Configure uma classificação curta e depois uma geração longa; diga qual gargalo mudou. Pergunto à turma: “Um modelo mais recente é automaticamente a melhor escolha?” Não; adequação da tarefa, qualidade medida, latência, memória e custo precisam orientar a decisão.

### Na demonstração

Configure uma classificação curta e depois uma geração longa; diga qual gargalo mudou.

### No quadro branco

Objetivo → acesso permitido → saída → orçamento

### Pergunta à turma

Um modelo mais recente é automaticamente a melhor escolha?

### Resposta e transição

Não; adequação da tarefa, qualidade medida, latência, memória e custo precisam orientar a decisão.
