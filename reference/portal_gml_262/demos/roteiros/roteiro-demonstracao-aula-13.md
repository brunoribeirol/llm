# Aula 13 — SFT, LoRA e QLoRA

Do comportamento de assistente ao produto de matrizes de um adaptador.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Posto do adaptador**: valor inicial `2`.
- **Escala alpha**: valor inicial `4`.
- **Magnitude do adaptador**: valor inicial `0.4`.
- **Base (bilhões de parâmetros)**: valor inicial `7`.
- **Bits da quantização uniforme didática**: valor inicial `4`.
- **Aplicar template de conversa**: valor inicial `True`.

## 01. Continuação não é diálogo

### Fala sugerida

As respostas exibidas são exemplos escritos, não saídas de um modelo em execução. Um completador pode continuar uma lista de perguntas. Isso pode ser coerente com seu objetivo de treino.

### Na demonstração

Ligue e desligue o template e compare as sequências ilustrativas.

### No quadro branco

Completar texto ≠ convenção de responder

### Pergunta à turma

Uma continuação de perguntas prova falta de conhecimento?

### Resposta e transição

Não; pode revelar incompatibilidade de tarefa e formato.

Avance para **O template marca a vez de falar** e relacione o resultado observado ao próximo mecanismo.

## 02. O template marca a vez de falar

### Fala sugerida

Um modelo recebe tokens, não balões de conversa. Os papéis precisam virar uma sequência. O prefixo final condiciona qual tipo de continuação esperamos.

### Na demonstração

Alterne template e acompanhe a posição do prefixo assistant.

### No quadro branco

system → user → assistant

### Pergunta à turma

Tags escritas por qualquer pessoa garantem compatibilidade?

### Resposta e transição

Não; cada modelo espera seu template e seus tokens específicos.

Avance para **SFT mantém a perda de próximo token** e relacione o resultado observado ao próximo mecanismo.

## 03. SFT mantém a perda de próximo token

### Fala sugerida

A fórmula não mudou de família. Mudaram os dados e quais posições supervisionamos. Mascarar o prompt evita cobrar a reprodução da pergunta nesta receita.

### Na demonstração

Veja a máscara e compare tokens de contexto e alvo.

### No quadro branco

L = −Σ mₜ log p(yₜ|x,y<t) / Σmₜ

### Pergunta à turma

A máscara impede o modelo de ler o prompt?

### Resposta e transição

Não; ele continua como contexto, apenas não contribui diretamente para a perda mostrada.

Avance para **Formato e capacidade devem ser avaliados** e relacione o resultado observado ao próximo mecanismo.

## 04. Formato e capacidade devem ser avaliados

### Fala sugerida

As curvas são cenários, não medições reais. A validação da tarefa detecta ajuste excessivo. O conjunto de controle observa habilidades que queríamos preservar.

### Na demonstração

Mude a magnitude e observe curvas sintéticas de treino, validação e controle.

### No quadro branco

Treino ↓ não implica validação ↓

### Pergunta à turma

Uma validação só de formato detecta perda em aritmética?

### Resposta e transição

Não; é necessário incluir tarefas de controle relevantes.

Avance para **Por que ajustar todos os pesos é caro** e relacione o resultado observado ao próximo mecanismo.

## 05. Por que ajustar todos os pesos é caro

### Fala sugerida

Guardar pesos para inferir não equivale a guardar tudo para treinar. Gradientes e momentos também precisam de espaço. Esta conta não inclui ativações nem infraestrutura.

### Na demonstração

Mude o tamanho da base e compare as três receitas.

### No quadro branco

Completo ≈ 16N; LoRA ≈ 2N + 16Nₐ bytes

### Pergunta à turma

LoRA elimina o custo do forward da base?

### Resposta e transição

Não; a base congelada ainda participa do cálculo.

Avance para **A atualização passa por um gargalo** e relacione o resultado observado ao próximo mecanismo.

## 06. A atualização passa por um gargalo

### Fala sugerida

Vamos multiplicar matrizes pequenas de verdade. O caminho alternativo atravessa r coordenadas. Essa restrição limita o posto da atualização, não o posto da matriz base.

### Na demonstração

Mude o posto e observe as formas de A e B.

### No quadro branco

A: r×d_in; B: d_out×r; ΔW = (α/r)BA

### Pergunta à turma

Qual é o posto máximo de BA?

### Resposta e transição

No máximo r e também limitado pelas dimensões de entrada e saída.

Avance para **Contar treináveis antes de executar** e relacione o resultado observado ao próximo mecanismo.

## 07. Contar treináveis antes de executar

### Fala sugerida

Aqui a matriz minúscula torna a contagem verificável. Não extrapolem sua fração diretamente para bilhões de parâmetros. Em modelos reais somamos todos os módulos adaptados.

### Na demonstração

Varie r e compare adaptador e matriz densa 4×4.

### No quadro branco

Nₐ = r(d_in+d_out)

### Pergunta à turma

Quando o adaptador 4×4 deixa de economizar parâmetros?

### Resposta e transição

Com r=2 ele iguala 16 parâmetros; acima disso usa mais que a matriz densa.

Avance para **Inicializar sem perturbar a base** e relacione o resultado observado ao próximo mecanismo.

## 08. Inicializar sem perturbar a base

### Fala sugerida

A saída inicial deve coincidir com a base. Isso não significa que todo gradiente seja zero. Inicializar A e B simultaneamente em zero impediria a aprendizagem desse produto.

### Na demonstração

Leve magnitude a zero e veja a atualização desaparecer.

### No quadro branco

B₀ = 0 ⇒ ΔW₀ = 0

### Pergunta à turma

Por que não zerar as duas matrizes?

### Resposta e transição

Porque os gradientes de ambas passam pela outra matriz e ficam nulos.

Avance para **Escala e fusão da atualização** e relacione o resultado observado ao próximo mecanismo.

## 09. Escala e fusão da atualização

### Fala sugerida

As duas contas usam os mesmos números. A igualdade é algébrica, sujeita a arredondamento numérico. Uma base quantizada exige cuidado adicional ao fundir.

### Na demonstração

Mude alpha e confira as saídas pelos dois caminhos.

### No quadro branco

W'x = W₀x + (α/r)B(Ax)

### Pergunta à turma

Alpha zero significa adaptador fraco?

### Resposta e transição

Significa contribuição exatamente nula nesta parametrização.

Avance para **Quantizar cria uma grade** e relacione o resultado observado ao próximo mecanismo.

## 10. Quantizar cria uma grade

### Fala sugerida

Os valores reconstruídos não são idênticos aos originais. Menos bits engrossam a grade. NF4 usa níveis diferentes desta ilustração uniforme.

### Na demonstração

Mude bits e compare peso, código e reconstrução.

### No quadro branco

q = round(w/s); ŵ = s q; erro = w−ŵ

### Pergunta à turma

Quantizar e desquantizar recupera sempre o valor exato?

### Resposta e transição

Não; em geral existe erro de arredondamento.

Avance para **QLoRA separa armazenamento e treino** e relacione o resultado observado ao próximo mecanismo.

## 11. QLoRA separa armazenamento e treino

### Fala sugerida

O gradiente precisa atravessar a operação que usa a base. Ele não precisa atualizar o peso congelado. A economia não elimina ativações nem todos os custos computacionais.

### Na demonstração

Compare caminhos de forward e gradiente.

### No quadro branco

Base 4 bits congelada + adaptador treinável

### Pergunta à turma

O QLoRA treina diretamente os códigos de 4 bits?

### Resposta e transição

Não; a base quantizada permanece congelada e os adaptadores são treinados.

Avance para **Escolher a intervenção pelo problema** e relacione o resultado observado ao próximo mecanismo.

## 12. Escolher a intervenção pelo problema

### Fala sugerida

Não organizem as técnicas como uma escada de poder. Comecem pelo defeito observável. Uma atualização de documento não deveria exigir treinar novamente um comportamento já correto.

### Na demonstração

Compare os três casos e explique a intervenção mínima.

### No quadro branco

Formato → prompt/SFT; fatos atuais → recuperação; avaliação sempre

### Pergunta à turma

Qual intervenção é adequada para regulamento que muda semanalmente?

### Resposta e transição

Recuperação de fontes atualizadas, com avaliação de recuperação e fundamentação das respostas.
