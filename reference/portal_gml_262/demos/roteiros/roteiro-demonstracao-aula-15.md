# Aula 15 — Alinhamento: preferências, RLHF e DPO

Acompanhe um par de respostas até recompensa, política, regularização e diagnóstico.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Recompensa de A**: valor inicial `1`.
- **Recompensa de B**: valor inicial `0`.
- **Probabilidade atual de A**: valor inicial `0.6`.
- **Probabilidade de A na referência**: valor inicial `0.5`.
- **Peso de regularização / beta**: valor inicial `0.5`.
- **Amostras best-of-N**: valor inicial `4`.

## 01. Formato correto ainda pode ser inadequado

### Fala sugerida

Os dois textos são exemplos didáticos. O problema não é somente cumprir um formato. Precisamos tornar explícito qual comportamento queremos favorecer.

### Na demonstração

Compare as respostas A e B e escolha um critério de qualidade.

### No quadro branco

Imitar resposta ≠ preferir melhor resposta

### Pergunta à turma

Uma resposta polida é necessariamente correta?

### Resposta e transição

Não; estilo, factualidade e utilidade são dimensões distintas.

Avance para **O dado passa a ser um par** e relacione o resultado observado ao próximo mecanismo.

## 02. O dado passa a ser um par

### Fala sugerida

Não tratem a rejeitada como impossível. O par diz que uma opção foi preferida à outra naquele contexto. Discordância entre pessoas também faz parte da qualidade do dado.

### Na demonstração

Mude as recompensas e veja qual alternativa é favorecida.

### No quadro branco

(x, y escolhida, y rejeitada)

### Pergunta à turma

O rótulo de preferência é uma verdade universal?

### Resposta e transição

Não; depende de critérios, contexto e população de avaliadores.

Avance para **Bradley-Terry transforma diferença em chance** e relacione o resultado observado ao próximo mecanismo.

## 03. Bradley-Terry transforma diferença em chance

### Fala sugerida

Somente a diferença determina a comparação. Recompensas iguais produzem cinquenta por cento. A escala absoluta não tem interpretação direta de qualidade humana.

### Na demonstração

Iguale as recompensas e depois aumente apenas A.

### No quadro branco

P(A ≻ B) = σ(rA−rB)

### Pergunta à turma

Se rA e rB aumentam ambos em 1, o que muda?

### Resposta e transição

Nada na probabilidade Bradley-Terry.

Avance para **Treinar um proxy de preferência** e relacione o resultado observado ao próximo mecanismo.

## 04. Treinar um proxy de preferência

### Fala sugerida

A perda cresce quando o modelo contradiz o rótulo. Isso só mede consistência com os pares fornecidos. Um proxy pode aprender comprimento ou estilo em vez do critério desejado.

### Na demonstração

Faça A preferida mas com recompensa menor e observe a perda.

### No quadro branco

L_RM = −log σ(rA−rB)

### Pergunta à turma

Perda baixa no treino do RM garante bom julgamento?

### Resposta e transição

Não; depende da representatividade e da validade das preferências.

Avance para **A política distribui probabilidade** e relacione o resultado observado ao próximo mecanismo.

## 05. A política distribui probabilidade

### Fala sugerida

Reduzimos o espaço de linguagem a duas alternativas. A conta é exata neste espaço reduzido. Em texto real a ação é uma sequência de tokens.

### Na demonstração

Mude a probabilidade atual de A e acompanhe a média.

### No quadro branco

E[r] = p(A)rA + (1−p(A))rB

### Pergunta à turma

A política precisa escolher sempre o maior reward?

### Resposta e transição

Não; regularização e diversidade podem manter massa em outras respostas.

Avance para **Uma referência ancora o comportamento** e relacione o resultado observado ao próximo mecanismo.

## 06. Uma referência ancora o comportamento

### Fala sugerida

Quando as distribuições coincidem, KL é zero. Aumentar beta torna a mudança mais cara. Isso não prova preservação de toda capacidade, mas limita o afastamento neste objetivo.

### Na demonstração

Iguale política e referência; depois afaste as duas.

### No quadro branco

J = E[r] − β KL(π || π_ref)

### Pergunta à turma

KL zero significa o quê neste exemplo?

### Resposta e transição

Que as duas distribuições sobre A e B coincidem.

Avance para **PPO limita a razão de mudança** e relacione o resultado observado ao próximo mecanismo.

## 07. PPO limita a razão de mudança

### Fala sugerida

O corte depende do sinal da vantagem. Ele não é simplesmente prender probabilidades numa faixa. O algoritmo real inclui amostragem, várias atualizações e outros termos.

### Na demonstração

Mude a política e compare objetivo sem corte e com corte.

### No quadro branco

min(ρA, clip(ρ,1−ε,1+ε)A)

### Pergunta à turma

O clipping proíbe matematicamente qualquer mudança grande?

### Resposta e transição

Não; limita o incentivo no objetivo substituto, não impõe uma restrição dura à distribuição.

Avance para **O sinal final precisa atribuir crédito** e relacione o resultado observado ao próximo mecanismo.

## 08. O sinal final precisa atribuir crédito

### Fala sugerida

Uma boa nota final não identifica qual token ajudou. Um modelo de valor pode estimar retorno esperado. Nossa figura explica essa função sem executar PPO completo.

### Na demonstração

Compare a sequência de decisões com o escalar final.

### No quadro branco

Tokens → resposta → recompensa; onde atribuir crédito?

### Pergunta à turma

Por que um reward por resposta não explica cada decisão?

### Resposta e transição

Porque agrega o resultado de uma sequência inteira e não fornece causalidade token a token.

Avance para **Quando o proxy vira o alvo** e relacione o resultado observado ao próximo mecanismo.

## 09. Quando o proxy vira o alvo

### Fala sugerida

A conta está obedecendo ao objetivo que lhe demos. O defeito pode estar no sinal, não no otimizador. Avaliação externa precisa procurar essas divergências.

### Na demonstração

Aumente a recompensa da resposta estilizada e veja o objetivo favorecê-la.

### No quadro branco

Proxy ↑ pode coexistir com utilidade ↓

### Pergunta à turma

Aumentar a otimização conserta um proxy ruim?

### Resposta e transição

Não; pode intensificar a exploração de suas falhas.

Avance para **Best-of-N muda seleção sem treino** e relacione o resultado observado ao próximo mecanismo.

## 10. Best-of-N muda seleção sem treino

### Fala sugerida

Nenhum peso é alterado. Pagamos por várias gerações e avaliações. Selecionar pelo reward continua sujeito aos erros do proxy.

### Na demonstração

Mude N e compare chance de candidato com custo linear.

### No quadro branco

P(ao menos uma A) = 1−(1−pA)^N

### Pergunta à turma

Best-of-N garante verdade?

### Resposta e transição

Não; só favorece o candidato que o avaliador consegue reconhecer.

Avance para **DPO usa razões contra a referência** e relacione o resultado observado ao próximo mecanismo.

## 11. DPO usa razões contra a referência

### Fala sugerida

A referência continua presente na conta. Neste exemplo A é a escolhida do dataset. Aumentar sua vantagem relativa reduz a perda, sem significar que todo par esteja correto.

### Na demonstração

Mude política, referência e beta e acompanhe a margem.

### No quadro branco

L_DPO = −log σ(β[log π(A)/πref(A) − log π(B)/πref(B)])

### Pergunta à turma

DPO dispensa dados de preferência?

### Resposta e transição

Não; os pares são justamente o sinal do ajuste.

Avance para **Escolher o pipeline pelo sinal disponível** e relacione o resultado observado ao próximo mecanismo.

## 12. Escolher o pipeline pelo sinal disponível

### Fala sugerida

Não vamos transformar a comparação numa competição universal. O dado disponível condiciona o método. Qualquer opção precisa de avaliação independente do sinal de treino.

### Na demonstração

Compare os dois percursos e identifique o componente removido no DPO.

### No quadro branco

SFT → pares → RM + RL ou otimização direta de preferência

### Pergunta à turma

Qual é a principal economia estrutural ilustrada pelo DPO?

### Resposta e transição

O procedimento direto evita treinar e usar um reward model separado no loop de RL.
