# Aula 02 — Tokenização: acompanhe o texto até os IDs

BPE treinado ao vivo, contagem, bytes e orçamento de contexto

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Texto para tokenizar**: valor inicial `casa casas casaco ação`.
- **Quantidade de merges aprendidos**: valor inicial `5`.
- **Janela disponível em tokens**: valor inicial `64`.
- **Quantidade de requisições**: valor inicial `1000`.
- **Preço hipotético por milhão de tokens**: valor inicial `1`.
- **Normalização**: valor inicial `none`.

## 01. Um texto não chega ao modelo como letras

### Fala sugerida

O modelo recebe IDs de um vocabulário finito, e não o significado diretamente. A escolha da divisão define a unidade de custo, contexto e previsão. Edite o texto e observe caracteres, palavras e bytes antes de escolher uma divisão. Pergunto à turma: “Um token é sempre uma palavra?” Não; pode ser uma palavra, uma parte dela, um caractere ou uma unidade associada a bytes.

### Na demonstração

Edite o texto e observe caracteres, palavras e bytes antes de escolher uma divisão.

### No quadro branco

texto → normalização → peças → IDs

### Pergunta à turma

Um token é sempre uma palavra?

### Resposta e transição

Não; pode ser uma palavra, uma parte dela, um caractere ou uma unidade associada a bytes.

Avance para **Normalização muda os símbolos** e relacione o resultado observado ao próximo mecanismo.

## 02. Normalização muda os símbolos

### Fala sugerida

Representações Unicode visualmente semelhantes podem usar sequências diferentes de códigos. NFC trata equivalências canônicas, enquanto transformar em minúsculas também perde informação de caixa. Digite AÇÃO e compare Preservar Unicode com NFC + minúsculas; inspecione os pontos de código. Pergunto à turma: “Por que registrar a normalização no experimento?” Porque ela altera as entradas do tokenizador e pode mudar contagens, vocabulário e reversibilidade.

### Na demonstração

Digite AÇÃO e compare Preservar Unicode com NFC + minúsculas; inspecione os pontos de código.

### No quadro branco

Aparência visual ≠ sequência de códigos Unicode

### Pergunta à turma

Por que registrar a normalização no experimento?

### Resposta e transição

Porque ela altera as entradas do tokenizador e pode mudar contagens, vocabulário e reversibilidade.

Avance para **Palavras e caracteres marcam os extremos** e relacione o resultado observado ao próximo mecanismo.

## 03. Palavras e caracteres marcam os extremos

### Fala sugerida

Separar por espaços produz sequências curtas, mas amplia o vocabulário necessário para palavras raras. Separar por caracteres limita as peças básicas e alonga as sequências. Acrescente uma palavra longa inventada e compare as duas contagens. Pergunto à turma: “Qual extremo lida melhor com uma palavra inédita sem acrescentar uma entrada inteira?” Caracteres podem compô-la com unidades já conhecidas, pagando o preço de usar mais posições.

### Na demonstração

Acrescente uma palavra longa inventada e compare as duas contagens.

### No quadro branco

Vocabulário grande ↔ sequência curta; vocabulário pequeno ↔ sequência longa

### Pergunta à turma

Qual extremo lida melhor com uma palavra inédita sem acrescentar uma entrada inteira?

### Resposta e transição

Caracteres podem compô-la com unidades já conhecidas, pagando o preço de usar mais posições.

Avance para **Prepare o corpus didático de BPE** e relacione o resultado observado ao próximo mecanismo.

## 04. Prepare o corpus didático de BPE

### Fala sugerida

O corpus fixo contém casa, casas, casaco e caso com frequências explícitas. Cada palavra começa dividida em caracteres e a marca de fronteira encerra a palavra. Coloque Merges=0 e leia o peso de cada palavra e sua sequência inicial. Pergunto à turma: “Uma palavra repetida dez vezes tem o mesmo peso de outra vista uma vez?” Não; as frequências ponderam a contagem dos pares que orientam a próxima fusão.

### Na demonstração

Coloque Merges=0 e leia o peso de cada palavra e sua sequência inicial.

### No quadro branco

Corpus com frequências → símbolos básicos + fronteira

### Pergunta à turma

Uma palavra repetida dez vezes tem o mesmo peso de outra vista uma vez?

### Resposta e transição

Não; as frequências ponderam a contagem dos pares que orientam a próxima fusão.

Avance para **Conte pares adjacentes** e relacione o resultado observado ao próximo mecanismo.

## 05. Conte pares adjacentes

### Fala sugerida

BPE procura o par de símbolos adjacentes mais frequente no corpus atual. O desempate desta demonstração é lexicográfico para tornar a execução reproduzível. Compare os pares em Merges=0 e Merges=1; encontre o que deixa de existir depois da fusão. Pergunto à turma: “Por que recontar depois de cada merge?” A fusão cria novos vizinhos e remove antigos; escolher todos os pares apenas uma vez produz outro algoritmo.

### Na demonstração

Compare os pares em Merges=0 e Merges=1; encontre o que deixa de existir depois da fusão.

### No quadro branco

contagem(a,b) = soma das ocorrências ponderadas no corpus

### Pergunta à turma

Por que recontar depois de cada merge?

### Resposta e transição

A fusão cria novos vizinhos e remove antigos; escolher todos os pares apenas uma vez produz outro algoritmo.

Avance para **Execute uma fusão e examine o estado** e relacione o resultado observado ao próximo mecanismo.

## 06. Execute uma fusão e examine o estado

### Fala sugerida

A fusão substitui ocorrências não sobrepostas do par escolhido por um símbolo novo. A lista mantém a ordem das decisões aprendidas. Avance Merges um a um até 5 e leia a regra acrescentada em cada passo. Pergunto à turma: “O vocabulário aprende uma lista sem ordem?” Não; a ordem de aplicação das fusões é necessária para reproduzir a segmentação.

### Na demonstração

Avance Merges um a um até 5 e leia a regra acrescentada em cada passo.

### No quadro branco

(c,a) → ca; depois recontar no corpus transformado

### Pergunta à turma

O vocabulário aprende uma lista sem ordem?

### Resposta e transição

Não; a ordem de aplicação das fusões é necessária para reproduzir a segmentação.

Avance para **Separe treinamento de aplicação** e relacione o resultado observado ao próximo mecanismo.

## 07. Separe treinamento de aplicação

### Fala sugerida

Depois de aprender as regras no corpus fixo, a demonstração aplica as mesmas regras ao texto digitado. Editar o texto de aplicação não retreina automaticamente o tokenizador. Mantenha Merges fixo e troque casa por casaria; compare as peças novas com as regras existentes. Pergunto à turma: “Uma palavra inédita precisa aparecer inteira no vocabulário?” Não; ela pode permanecer decomposta nas unidades conhecidas que as regras conseguem combinar.

### Na demonstração

Mantenha Merges fixo e troque casa por casaria; compare as peças novas com as regras existentes.

### No quadro branco

Aprender regras no corpus; aplicar regras em outra entrada

### Pergunta à turma

Uma palavra inédita precisa aparecer inteira no vocabulário?

### Resposta e transição

Não; ela pode permanecer decomposta nas unidades conhecidas que as regras conseguem combinar.

Avance para **Construa IDs e reconstrua o texto** e relacione o resultado observado ao próximo mecanismo.

## 08. Construa IDs e reconstrua o texto

### Fala sugerida

Cada símbolo tem um ID no vocabulário didático, inclusive os espaços preservados. Símbolos Unicode fora do alfabeto básico são mostrados como desconhecidos neste mini-BPE, sem alegar cobertura universal. Adicione um emoji e procure a indicação de símbolo desconhecido; remova-o e leia os IDs. Pergunto à turma: “Podemos somar dois IDs para obter um significado intermediário?” Não; IDs são índices arbitrários, sem distância semântica útil por si só.

### Na demonstração

Adicione um emoji e procure a indicação de símbolo desconhecido; remova-o e leia os IDs.

### No quadro branco

Peça ↔ ID; decodificar requer vocabulário e regras de fronteira

### Pergunta à turma

Podemos somar dois IDs para obter um significado intermediário?

### Resposta e transição

Não; IDs são índices arbitrários, sem distância semântica útil por si só.

Avance para **Bytes oferecem uma base universal** e relacione o resultado observado ao próximo mecanismo.

## 09. Bytes oferecem uma base universal

### Fala sugerida

UTF-8 representa todo texto Unicode válido como bytes, e um alfabeto de 256 bytes cobre essa base. O mini-BPE anterior usa caracteres e não se torna byte-level apenas por mostrar esta comparação. Digite ação e um emoji; compare a quantidade de caracteres com a quantidade de bytes. Pergunto à turma: “Um caractere ocupa sempre um byte?” Não; letras acentuadas e emojis podem ocupar vários bytes em UTF-8.

### Na demonstração

Digite ação e um emoji; compare a quantidade de caracteres com a quantidade de bytes.

### No quadro branco

Unicode → UTF-8 → bytes em 0..255

### Pergunta à turma

Um caractere ocupa sempre um byte?

### Resposta e transição

Não; letras acentuadas e emojis podem ocupar vários bytes em UTF-8.

Avance para **Compare famílias sem misturar critérios** e relacione o resultado observado ao próximo mecanismo.

## 10. Compare famílias sem misturar critérios

### Fala sugerida

BPE funde pares por frequência; WordPiece usa um critério associado ao vocabulário e à modelagem; Unigram remove candidatos preservando uma boa segmentação probabilística. Apenas o mini-BPE está sendo treinado nesta tela. Altere Merges e acompanhe somente a linha BPE; identifique quais linhas são explicações conceituais. Pergunto à turma: “Ver menos peças demonstra que o algoritmo é sempre melhor?” Não; cobertura, compressão, corpus, normalização e custo total precisam ser medidos em conjunto.

### Na demonstração

Altere Merges e acompanhe somente a linha BPE; identifique quais linhas são explicações conceituais.

### No quadro branco

BPE: fusões; WordPiece: vocabulário; Unigram: seleção probabilística

### Pergunta à turma

Ver menos peças demonstra que o algoritmo é sempre melhor?

### Resposta e transição

Não; cobertura, compressão, corpus, normalização e custo total precisam ser medidos em conjunto.

Avance para **Transforme fertilidade em custo e contexto** e relacione o resultado observado ao próximo mecanismo.

## 11. Transforme fertilidade em custo e contexto

### Fala sugerida

Fertilidade é a razão entre tokens e palavras no texto observado. A projeção de custo usa um preço hipotético por milhão e a capacidade em palavras usa essa mesma fertilidade. Dobre Requisições e depois Janela; veja quais números dobram em cada caso. Pergunto à turma: “Reduzir 20% dos tokens aumenta em 20% a capacidade em palavras?” A capacidade multiplica por 1/0,8 = 1,25, portanto cresce 25% sob fertilidade constante.

### Na demonstração

Dobre Requisições e depois Janela; veja quais números dobram em cada caso.

### No quadro branco

F = tokens/palavras; custo = tokens × requisições × preço/10⁶

### Pergunta à turma

Reduzir 20% dos tokens aumenta em 20% a capacidade em palavras?

### Resposta e transição

A capacidade multiplica por 1/0,8 = 1,25, portanto cresce 25% sob fertilidade constante.

Avance para **Leia números como sequências, não como algarismos soltos** e relacione o resultado observado ao próximo mecanismo.

## 12. Leia números como sequências, não como algarismos soltos

### Fala sugerida

A segmentação de números depende das peças disponíveis e pode variar entre entradas parecidas. O modelo precisa aprender relações sobre essa representação, e não recebe aritmética garantida pelos IDs. Digite 1234 1235 e compare as divisões; retorne ao orçamento e registre corpus, regras e contagem. Pergunto à turma: “É válido comparar perplexidade por token entre segmentações diferentes sem ressalva?” Não; a unidade e o espaço de eventos mudaram, então a comparação direta perde o significado.

### Na demonstração

Digite 1234 1235 e compare as divisões; retorne ao orçamento e registre corpus, regras e contagem.

### No quadro branco

Mesma escrita numérica → segmentação dependente do vocabulário

### Pergunta à turma

É válido comparar perplexidade por token entre segmentações diferentes sem ressalva?

### Resposta e transição

Não; a unidade e o espaço de eventos mudaram, então a comparação direta perde o significado.
