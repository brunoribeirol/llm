# Aula 17 — Oficina de revisão: diagnosticar antes de escolher

Atividades inéditas de revisão conceitual; não contém prova nem gabarito oficial.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Comprimento da sequência**: valor inicial `4`.
- **Temperatura**: valor inicial `1`.
- **Parâmetros (bilhões)**: valor inicial `3`.
- **Posto LoRA**: valor inicial `4`.
- **Itens da avaliação**: valor inicial `20`.

## 01. Um mapa de dependências

### Fala sugerida

Hoje vamos justificar, não procurar enunciados de uma avaliação. Cada atividade foi criada para esta demonstração. Antes de calcular, digam qual variável explica o sintoma.

### Na demonstração

Siga as setas e identifique a entrada e a saída de cada fase.

### No quadro branco

Texto → tokens → estados → logits → distribuição

### Pergunta à turma

Por que diagnosticar antes de escolher técnica?

### Resposta e transição

Porque intervenções diferentes alteram partes diferentes do sistema.

Avance para **Tokens não são palavras universais** e relacione o resultado observado ao próximo mecanismo.

## 02. Tokens não são palavras universais

### Fala sugerida

Usamos rótulos abstratos para focar nas posições. Um token pode ser parte de palavra ou pontuação. O custo depende da sequência efetiva que entra no modelo.

### Na demonstração

Aumente comprimento e conte posições e pares.

### No quadro branco

T posições; T² pares de atenção

### Pergunta à turma

É seguro estimar contexto contando apenas palavras?

### Resposta e transição

Não; a correspondência varia conforme idioma, texto e tokenizer.

Avance para **A máscara define quem pode ver quem** e relacione o resultado observado ao próximo mecanismo.

## 03. A máscara define quem pode ver quem

### Fala sugerida

Localizem a linha correspondente à posição atual. As células à direita representam futuro. A máscara muda a informação disponível, não a forma externa da matriz.

### Na demonstração

Aumente contexto e compare células permitidas e bloqueadas.

### No quadro branco

Permitido(i,j) ⇔ j ≤ i

### Pergunta à turma

Por que bloquear o futuro durante treino autoregressivo?

### Resposta e transição

Para evitar usar o alvo futuro como entrada e alinhar treino com geração.

Avance para **Logits, temperatura e escolha** e relacione o resultado observado ao próximo mecanismo.

## 04. Logits, temperatura e escolha

### Fala sugerida

Primeiro identifiquem o máximo. Depois observem a massa dos candidatos restantes. Não confundam uma distribuição mais espalhada com uma garantia de criatividade útil.

### Na demonstração

Compare temperaturas 0,3 e 1,8.

### No quadro branco

p = softmax(z/T)

### Pergunta à turma

Temperatura maior troca necessariamente o token mais provável?

### Resposta e transição

Não; preserva o ranking dos logits.

Avance para **Orçamento de treino e memória** e relacione o resultado observado ao próximo mecanismo.

## 05. Orçamento de treino e memória

### Fala sugerida

As duas colunas respondem a perguntas distintas. A primeira armazena pesos. A segunda inclui uma receita de atualização e ainda deixa ativações de fora.

### Na demonstração

Aumente parâmetros e compare pesos BF16 e estados de treino.

### No quadro branco

Pesos ≈ 2N bytes; treino típico ≈ 16N bytes + ativações

### Pergunta à turma

GPU ociosa elimina risco de falta de memória?

### Resposta e transição

Não; utilização aritmética e capacidade de memória são recursos diferentes.

Avance para **Adaptador exige conta de dimensões** e relacione o resultado observado ao próximo mecanismo.

## 06. Adaptador exige conta de dimensões

### Fala sugerida

Escrevam as formas antes da multiplicação. Isso evita inverter A e B. A base congelada continua computando o caminho principal.

### Na demonstração

Varie posto e calcule os adaptadores de um módulo 512×512.

### No quadro branco

Nₐ = r(512+512)

### Pergunta à turma

Dobrar r dobra quantos parâmetros treináveis neste módulo?

### Resposta e transição

Dobra de 1024r para 2048r, mantendo dimensões fixas.

Avance para **O objetivo determina o sinal** e relacione o resultado observado ao próximo mecanismo.

## 07. O objetivo determina o sinal

### Fala sugerida

Não deem ao método uma capacidade que o dado não mede. Um verificador de formato não verifica fatos. Uma preferência de estilo não prova correção matemática.

### Na demonstração

Compare as três linhas e escolha o sinal de cada situação.

### No quadro branco

Texto → imitação; pares → preferência; programa → verificação

### Pergunta à turma

Qual sinal verifica diretamente se uma soma está correta?

### Resposta e transição

Uma regra executável de correção para a soma, dentro de sua especificação.

Avance para **Um número precisa de denominador** e relacione o resultado observado ao próximo mecanismo.

## 08. Um número precisa de denominador

### Fala sugerida

Em dez exemplos, um item vale dez pontos. A precisão de exibição não muda esse fato. Também precisamos conhecer a distribuição dos casos.

### Na demonstração

Varie itens e observe quanto vale um único acerto.

### No quadro branco

Δ mínimo observado = 100/n pontos

### Pergunta à turma

Mostrar 0,9000 aumenta a confiança em nove acertos de dez?

### Resposta e transição

Não; apenas muda a apresentação do mesmo dado.

Avance para **Da hipótese ao teste que pode refutá-la** e relacione o resultado observado ao próximo mecanismo.

## 09. Da hipótese ao teste que pode refutá-la

### Fala sugerida

Evitem responder apenas com um nome de técnica. Digam qual resultado esperam se a hipótese estiver correta. Depois definam o que os faria mudar de ideia.

### Na demonstração

Leia os cenários e associe uma medição concreta.

### No quadro branco

Sintoma → hipótese → intervenção → teste → limite

### Pergunta à turma

Como investigar uma saída fora do formato?

### Resposta e transição

Controlar template e instrução, medir taxa de inválidos em entradas fixas e separar esse erro da correção do conteúdo.
