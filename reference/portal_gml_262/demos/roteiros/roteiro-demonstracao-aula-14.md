# Aula 14 — Laboratório de adaptação: do dado ao adaptador

Execute um treino minúsculo de verdade e interprete o protocolo de um fine-tuning.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Posto**: valor inicial `2`.
- **Taxa de aprendizado**: valor inicial `0.15`.
- **Passos de atualização**: valor inicial `20`.
- **Exemplos por passo**: valor inicial `4`.
- **Contexto estimado**: valor inicial `512`.
- **Template consistente**: valor inicial `True`.

## 01. Dois tamanhos, um protocolo

### Fala sugerida

O navegador consegue mostrar toda a conta porque o modelo é minúsculo. Isso não mede a qualidade de um LLM. O que transferimos é o protocolo de configuração, medição e comparação.

### Na demonstração

Compare as dimensões do experimento com o perfil de GPU ilustrativo.

### No quadro branco

Objeto treinado aqui: y=(W₀+BA)x

### Pergunta à turma

O simulador substitui o notebook de GPU?

### Resposta e transição

Não; prepara a compreensão e executa apenas o problema linear declarado.

Avance para **Verificar memória antes de carregar** e relacione o resultado observado ao próximo mecanismo.

## 02. Verificar memória antes de carregar

### Fala sugerida

Estas parcelas são aproximações de planejamento. O pico real deve ser medido no ambiente do notebook. Deixar uma margem evita tratar toda memória física como disponível.

### Na demonstração

Aumente lote e contexto e compare parcelas estimadas.

### No quadro branco

Memória = base + adaptador/estados + ativações

### Pergunta à turma

Por que uma base que cabe pode falhar no primeiro passo?

### Resposta e transição

Porque backward e ativações acrescentam memória além dos pesos.

Avance para **Salvar uma linha de base** e relacione o resultado observado ao próximo mecanismo.

## 03. Salvar uma linha de base

### Fala sugerida

Sem baseline não sabemos o que mudou. Vamos guardar previsões, não apenas uma impressão geral. Nos próximos passos compararemos exatamente essas entradas.

### Na demonstração

Selecione zero passos e leia previsões e erros.

### No quadro branco

Baseline: mesmas entradas, nenhuma atualização

### Pergunta à turma

Comparar perguntas diferentes antes e depois é válido?

### Resposta e transição

Não para atribuir a diferença ao ajuste; precisamos controlar as entradas.

Avance para **Inspecionar a representação do dado** e relacione o resultado observado ao próximo mecanismo.

## 04. Inspecionar a representação do dado

### Fala sugerida

No problema numérico o alvo está visível. No LLM a resposta é uma sequência de alvos. Em ambos os casos um erro de preparação muda a tarefa efetivamente aprendida.

### Na demonstração

Alterne template e identifique a mudança de interface.

### No quadro branco

Dado de treino = entrada + alvo + contrato

### Pergunta à turma

Dados válidos em JSON garantem tarefa correta?

### Resposta e transição

Não; estrutura sintática e significado supervisionado são verificações diferentes.

Avance para **Separar treino, validação e controle** e relacione o resultado observado ao próximo mecanismo.

## 05. Separar treino, validação e controle

### Fala sugerida

O controle aqui preserva um comportamento original da base. Ele não participa da otimização. Uma melhoria no alvo pode ter um custo visível nesse conjunto.

### Na demonstração

Compare quais entradas pertencem a cada partição.

### No quadro branco

Treino ≠ validação ≠ controle

### Pergunta à turma

Por que não escolher a configuração pelo teste final?

### Resposta e transição

Porque isso torna o teste parte da otimização e contamina a estimativa final.

Avance para **Construir o adaptador treinável** e relacione o resultado observado ao próximo mecanismo.

## 06. Construir o adaptador treinável

### Fala sugerida

A base continua participando da previsão. Apenas A e B recebem atualizações. Em uma matriz tão pequena, o adaptador não precisa economizar parâmetros para ilustrar o mecanismo.

### Na demonstração

Mude o posto e conte as entradas das matrizes.

### No quadro branco

Nₐ = r(3+1)

### Pergunta à turma

Por que usar este caso pequeno mesmo sem economia?

### Resposta e transição

Porque permite auditar a atualização; economia de memória exige dimensões maiores.

Avance para **Ver o primeiro gradiente** e relacione o resultado observado ao próximo mecanismo.

## 07. Ver o primeiro gradiente

### Fala sugerida

Agora vemos a assimetria de inicialização em ação. Primeiro B começa a se mover. Em passos posteriores A também pode receber gradiente.

### Na demonstração

Compare zero e um passo.

### No quadro branco

L = média(ŷ−y)²; θ ← θ−η∇L

### Pergunta à turma

A inicialização com B zero bloqueia o treino?

### Resposta e transição

Não; A não nula permite gradiente em B.

Avance para **Treinar e ler o histórico** e relacione o resultado observado ao próximo mecanismo.

## 08. Treinar e ler o histórico

### Fala sugerida

O eixo horizontal representa atualizações reais deste problema pequeno. Taxa alta pode provocar oscilação ou divergência. Quando houver valores não finitos, precisamos reconhecer falha numérica.

### Na demonstração

Aumente passos e compare taxas 0,05 e 0,7.

### No quadro branco

Não selecionar modelo só pela perda de treino

### Pergunta à turma

Uma curva decrescente garante bom comportamento externo?

### Resposta e transição

Não; ela mede o objetivo de treino, não todas as capacidades desejadas.

Avance para **Lote muda o estimador do gradiente** e relacione o resultado observado ao próximo mecanismo.

## 09. Lote muda o estimador do gradiente

### Fala sugerida

Aqui controlamos até a ordem dos exemplos. Assim fica claro qual diferença veio do tamanho do lote. Em treino real também registraríamos semente e embaralhamento.

### Na demonstração

Compare lote 1 e lote 4 com a mesma taxa.

### No quadro branco

∇L_lote = média dos gradientes do lote

### Pergunta à turma

Menos exemplos por passo implica mesmo número de exemplos vistos?

### Resposta e transição

Não; comparar por passos e comparar por épocas completas são protocolos diferentes.

Avance para **Antes e depois na mesma tabela** e relacione o resultado observado ao próximo mecanismo.

## 10. Antes e depois na mesma tabela

### Fala sugerida

Olhem as linhas, não só a média. Um item pode melhorar e outro piorar. É essa tabela pareada que precisamos guardar no notebook real.

### Na demonstração

Mude passos e compare o erro em cada partição.

### No quadro branco

Δ erro = erro depois − erro antes

### Pergunta à turma

Uma média menor exclui regressões individuais?

### Resposta e transição

Não; ganhos em alguns casos podem esconder perdas em outros.

Avance para **Poucos exemplos limitam a afirmação** e relacione o resultado observado ao próximo mecanismo.

## 11. Poucos exemplos limitam a afirmação

### Fala sugerida

Não vamos vender certeza a partir de uma demonstração. O caso pequeno é ótimo para encontrar bugs. Para comparar modelos precisamos de conjunto maior e representativo.

### Na demonstração

Leia a resolução de uma avaliação de oito itens.

### No quadro branco

Um item em 8 = 12,5 pontos percentuais

### Pergunta à turma

Oito sucessos provam perfeição?

### Resposta e transição

Não; há incerteza e possível falta de cobertura.

Avance para **Empacotar o que permite reproduzir** e relacione o resultado observado ao próximo mecanismo.

## 12. Empacotar o que permite reproduzir

### Fala sugerida

Salvar apenas as matrizes não conta toda a história. Outra pessoa precisa reconstruir o mesmo caminho de inferência. O manifesto exibido é um exemplo do que documentar, não um arquivo de pesos de LLM.

### Na demonstração

Confira o manifesto calculado com seus controles.

### No quadro branco

base + A/B + config + template + avaliação

### Pergunta à turma

Qual informação torna um adaptador isolado insuficiente?

### Resposta e transição

A identidade e versão da base, além de arquitetura, módulos, escala, tokenizer e template compatíveis.
