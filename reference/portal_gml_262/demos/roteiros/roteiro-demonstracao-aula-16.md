# Aula 16 — Raciocínio, verificadores e GRPO

Da diferença entre tentar e acertar ao sinal de atualização relativo ao grupo.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Amostras disponíveis n**: valor inicial `10`.
- **Acertos observados c (limitado a n)**: valor inicial `3`.
- **Tentativas escolhidas k (limitado a n)**: valor inicial `5`.
- **Tamanho do grupo**: valor inicial `4`.
- **Sucessos no grupo (limitado ao grupo)**: valor inicial `2`.
- **Tokens por tentativa**: valor inicial `100`.

## 01. A solução pode existir sem ser entregue

### Fala sugerida

Cada cartão representa uma tentativa sintética rotulada. Saber qual cartão está correto é informação de avaliação. Um usuário comum pode não dispor desse oráculo.

### Na demonstração

Mude o número de acertos e inspecione o conjunto de tentativas.

### No quadro branco

Existência da resposta correta ≠ seleção da correta

### Pergunta à turma

Pass@k alto garante resposta entregue correta?

### Resposta e transição

Não; mede a existência de ao menos uma correta entre as tentativas.

Avance para **Definir o que será verificado** e relacione o resultado observado ao próximo mecanismo.

## 02. Definir o que será verificado

### Fala sugerida

Um teste pode verificar saída e ainda ignorar custo ou segurança. Um validador de JSON verifica forma, não verdade. Devemos dizer exatamente o que a recompensa confere.

### Na demonstração

Compare verificadores de aritmética, código e formato.

### No quadro branco

Verificador = especificação executável parcial

### Pergunta à turma

JSON válido implica resposta factual correta?

### Resposta e transição

Não; o verificador só avaliou a estrutura.

Avance para **Uma tentativa tem uma taxa própria** e relacione o resultado observado ao próximo mecanismo.

## 03. Uma tentativa tem uma taxa própria

### Fala sugerida

Mais tentativas não significam automaticamente maior taxa por tentativa. Se o número de acertos não cresce, a fração cai. Não confundam quantidade total com probabilidade.

### Na demonstração

Aumente n mantendo c e acompanhe a fração.

### No quadro branco

pass@1 estimado = c/n

### Pergunta à turma

Se c fica fixo e n cresce, pass@1 aumenta?

### Resposta e transição

Não; a taxa observada diminui.

Avance para **Pass@k conta conjuntos sem acerto** e relacione o resultado observado ao próximo mecanismo.

## 04. Pass@k conta conjuntos sem acerto

### Fala sugerida

É mais fácil contar o fracasso: escolher apenas tentativas erradas. Depois subtraímos de um. O cálculo limita k e c ao número disponível, visível na tela.

### Na demonstração

Varie k e confira os extremos c=0 e c=n.

### No quadro branco

pass@k = 1 − C(n−c,k)/C(n,k)

### Pergunta à turma

Se k>n−c, qual o resultado?

### Resposta e transição

É 1, pois não há tentativas erradas suficientes para formar esse subconjunto.

Avance para **Independência é outra hipótese** e relacione o resultado observado ao próximo mecanismo.

## 05. Independência é outra hipótese

### Fala sugerida

As duas fórmulas respondem a experimentos diferentes. Um conjunto pequeno torna a diferença visível. Registrar o protocolo evita trocar uma estimativa pela outra.

### Na demonstração

Compare as duas curvas para n pequeno.

### No quadro branco

Independente: 1−(1−p)^k; amostra fixa: combinatória

### Pergunta à turma

Podemos substituir sempre uma fórmula pela outra?

### Resposta e transição

Não; elas assumem processos amostrais diferentes.

Avance para **Consenso é um seletor, não um oráculo** e relacione o resultado observado ao próximo mecanismo.

## 06. Consenso é um seletor, não um oráculo

### Fala sugerida

Aqui todas as respostas erradas concordam entre si por construção. Há uma solução correta no conjunto, mas a maioria pode ignorá-la. Diversidade de trajetórias não garante diversidade de respostas.

### Na demonstração

Ajuste acertos para uma minoria e compare existência e maioria.

### No quadro branco

Maioria pode amplificar erro correlacionado

### Pergunta à turma

Por que consenso pode ficar abaixo de pass@k?

### Resposta e transição

Porque o seletor pode não reconhecer o acerto que existe no conjunto.

Avance para **A fatura cresce com as tentativas** e relacione o resultado observado ao próximo mecanismo.

## 07. A fatura cresce com as tentativas

### Fala sugerida

Não atribuímos preço comercial aos tokens aqui. A conta já mostra o trade-off básico. Uma solução mais longa precisa justificar o orçamento adicional.

### Na demonstração

Mude k e comprimento mantendo a taxa de acerto.

### No quadro branco

Tokens ≈ kL; custo não é qualidade

### Pergunta à turma

Dobrar o comprimento garante maior acerto?

### Resposta e transição

Não; custo cresce por definição, qualidade precisa ser medida.

Avance para **Recompensa verificável dá sinal ao treino** e relacione o resultado observado ao próximo mecanismo.

## 08. Recompensa verificável dá sinal ao treino

### Fala sugerida

Este é um exemplo binário para expor o mecanismo. Critérios reais podem combinar correção e formato. Qualquer composição deve ser auditada para evitar atalhos.

### Na demonstração

Mude sucessos no grupo e leia os rewards.

### No quadro branco

rᵢ ∈ {0,1}

### Pergunta à turma

Toda tarefa tem recompensa verificável confiável?

### Resposta e transição

Não; preferências abertas e julgamentos ambíguos exigem outros sinais.

Avance para **GRPO compara respostas do mesmo grupo** e relacione o resultado observado ao próximo mecanismo.

## 09. GRPO compara respostas do mesmo grupo

### Fala sugerida

O grupo fornece sua própria linha de base. A soma das vantagens fica aproximadamente zero. O simulador calcula esse termo, não executa todo o treinamento de linguagem.

### Na demonstração

Varie sucessos mantendo tamanho do grupo.

### No quadro branco

Aᵢ = (rᵢ−média(r))/(desvio(r)+ε)

### Pergunta à turma

Uma resposta correta sempre tem vantagem positiva?

### Resposta e transição

Não; se todas forem corretas, a diferença para a média é zero.

Avance para **Um grupo uniforme não discrimina** e relacione o resultado observado ao próximo mecanismo.

## 10. Um grupo uniforme não discrimina

### Fala sugerida

A tarefa pode estar fácil demais ou difícil demais para este grupo. Nos dois casos falta contraste no sinal relativo. O termo estabilizador evita divisão por zero, mas não cria informação.

### Na demonstração

Teste zero sucessos e depois sucessos igual ao grupo.

### No quadro branco

r₁=…=rG ⇒ vantagens = 0

### Pergunta à turma

Adicionar epsilon cria aprendizagem num grupo sem contraste?

### Resposta e transição

Não; mantém estabilidade numérica, enquanto o numerador continua zero.

Avance para **Comparar GRPO com PPO sem confundir** e relacione o resultado observado ao próximo mecanismo.

## 11. Comparar GRPO com PPO sem confundir

### Fala sugerida

Risquem apenas o componente que deixou de ser necessário. Não apaguem a política nem o sinal de recompensa. A simplificação arquitetural não elimina custo de gerar grupos.

### Na demonstração

Compare os componentes dos dois desenhos.

### No quadro branco

PPO: crítico de valor; GRPO: baseline do grupo

### Pergunta à turma

GRPO elimina a necessidade de recompensa?

### Resposta e transição

Não; o grupo precisa de recompensas para definir vantagens.

Avance para **Uma receita completa tem fases** e relacione o resultado observado ao próximo mecanismo.

## 12. Uma receita completa tem fases

### Fala sugerida

Não chamem todo pós-treino de uma única técnica. Cada fase muda a origem do sinal. A demonstração ajuda a perguntar qual capacidade cada fase pretende melhorar.

### Na demonstração

Siga as fases e identifique onde entra cada tipo de sinal.

### No quadro branco

Exemplos iniciais → RL → seleção/SFT → refinamento

### Pergunta à turma

Imitação e verificação são o mesmo sinal?

### Resposta e transição

Não; uma copia demonstrações e a outra avalia resultados por regras.

Avance para **Comprimento não é evidência suficiente** e relacione o resultado observado ao próximo mecanismo.

## 13. Comprimento não é evidência suficiente

### Fala sugerida

Nesta experiência a taxa de acerto permanece controlada separadamente. Isso mostra por que não devemos deduzir qualidade do comprimento. O relatório precisa declarar o que o verificador não observa.

### Na demonstração

Aumente comprimento sem alterar acertos e compare a fatura.

### No quadro branco

Mais tokens ≠ mais acertos

### Pergunta à turma

Qual conclusão o simulador permite sobre raciocínio real?

### Resposta e transição

Somente compreender métricas e sinais; não inferir mecanismos cognitivos de modelos nem desempenho real.
