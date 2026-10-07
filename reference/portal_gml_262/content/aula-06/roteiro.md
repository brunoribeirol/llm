---
aula: 6
titulo: "Transformer I: self-attention e a arquitetura"
tipo: teorica
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 6 de 30 (V2)

## Como usar este roteiro

Este roteiro sugere uma fala para a aula. As explicações podem ser adaptadas ao ritmo da
turma; as pausas servem para ouvir respostas e retomar o que ainda não ficou claro.
As frases com 🗣️ destacam a ideia principal de cada slide. As notas com **Bastidor:** são
orientações para o professor e não fazem parte da fala.

A aula começa com exemplos, apresenta a fórmula de atenção e usa essa fórmula para
entender alguns problemas de implementação. As contas completas estão nos itens A.1 a A.6
do apêndice dos slides. A Parte 4 prepara respostas para perguntas sobre essas contas.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · A mesma palavra em dois contextos · 00:00–00:05

Boa noite, pessoal. Vou retomar o exemplo de “banco” que apareceu quando estudamos
embeddings. Em “o banco do rio estava cheio”, estamos usando banco no sentido de uma
formação de areia no rio. Em “o banco do centro estava fechado”, estamos falando de uma
instituição financeira. As palavras ao redor ajudam a entender de qual banco estamos falando.

O embedding estático é um vetor associado à palavra. Quando buscamos “banco” na mesma
tabela de embeddings, recebemos os mesmos números nas duas frases. As outras palavras
ainda não participaram desse cálculo.

Se eu entregar só esse vetor a um classificador, ele não terá informação para distinguir
os dois usos. Um classificador é um modelo que escolhe uma categoria; neste exemplo,
queremos que ele identifique o sentido da palavra. Precisamos, portanto, de uma
representação que também leve em conta o restante da frase.

> 🗣️ “O vetor inicial de banco é o mesmo; o contexto precisa entrar no cálculo da nova representação.”

> **Nota:** Bastidor: retomar a saída do Lab 1, se disponível. Perguntar quais palavras
> ajudam a distinguir os sentidos e reservar alguns segundos para as respostas.

### Slide 2 · Como a RNN leva o contexto adiante · 00:05–00:10

Na Aula 5, “Modelos sequenciais e o nascimento da atenção”, vimos uma forma de incluir
contexto: a RNN. Ela mantém um estado oculto, um vetor que é atualizado a cada token e
carrega informação dos passos anteriores.

Isso permite representar a mesma palavra de maneiras diferentes conforme a sequência.
Mas existe uma dificuldade: para uma informação da posição 1 chegar à posição 50, ela
passa por 49 atualizações. A rede precisa aprender a preservá-la ao longo desse caminho.
As LSTMs ajudam nisso, embora o processamento continue sendo sequencial.

Além disso, dentro de uma mesma sequência, cada passo espera o anterior. Isso limita
quanto do trabalho pode ser feito ao mesmo tempo na GPU. A atenção permite outra forma
de relacionar as posições: uma posição pode consultar diretamente outra, mesmo distante.

> 🗣️ “A RNN inclui contexto passo a passo; a atenção permite uma ligação direta entre posições.”

### Slide 3 · Como a self-attention combina informações · 00:10–00:16

Vou começar pela ideia, antes da fórmula. Na self-attention, cada token recebe uma nova
representação que combina informações dos tokens da própria sequência. Por enquanto,
vou considerar que todas as posições podem participar. Depois veremos como restringir isso.

Essa combinação usa pesos. Por exemplo, um peso de 0,6 faz uma informação contribuir mais
que um peso de 0,1. Os pesos são calculados a partir dos vetores da entrada, então podem
mudar de uma frase para outra.

No exemplo de “banco”, a presença de “rio” pode mudar tanto os pesos quanto o conteúdo
disponível para combinar. Com “centro”, o conjunto de informações é outro. É assim que
o mesmo vetor inicial pode dar origem a representações diferentes.

Estamos usando palavras inteiras para facilitar a leitura. Em um modelo de linguagem,
um token também pode ser uma parte de palavra ou um sinal de pontuação.

> 🗣️ “A self-attention calcula quanto cada token contribui para a representação dos outros.”

> **Nota:** Bastidor: pedir uma explicação da ideia com as próprias palavras. Se houver
> dificuldade com “peso”, retomar o exemplo de média ponderada antes de seguir.

### Slide 4 · Q, K, V: três papéis, uma entrada · 00:16–00:23

Para fazer essa combinação, transformamos o vetor de cada token em três vetores.
Vou usar os nomes em inglês porque são os que aparecem no artigo e no código.

A **query**, ou consulta, é o vetor que será comparado com os demais. A **key**, ou chave,
é o vetor usado nessa comparação do outro lado. O **value**, ou valor, contém a informação
que será combinada na saída.

Uma busca em uma biblioteca ajuda a imaginar esses papéis: tenho uma consulta, comparo
essa consulta com informações do catálogo e uso o conteúdo dos materiais encontrados.
Aqui, porém, tudo é representado por números, e a saída pode combinar vários conteúdos.

Chamamos essas transformações de projeções lineares: multiplicamos a entrada por três
matrizes, cujos valores são aprendidos durante o treinamento. Ao reunir os vetores de
todos os tokens, obtemos as matrizes Q, K e V. Na self-attention, as três vêm da mesma
entrada X.

> 🗣️ “Q e K calculam os pesos; V fornece o conteúdo que será combinado.”

> **Nota:** Bastidor: apontar as três setas que saem de X. Uma dúvida sobre dimensões pode
> ser respondida com o exemplo de seis tokens: X tem seis linhas. O detalhamento está em A.1.

### Slide 5 · Lendo a fórmula de atenção · 00:23–00:33

Agora vou mostrar a fórmula que reúne essas operações.

**[Projeto a fórmula e acompanho os termos com o cursor.]**

`Attention(Q, K, V) = softmax(QKᵀ / √d_k) V`

Eu leio assim: atenção de Q, K e V é o softmax de Q vezes K transposto, dividido pela raiz
de d_k, e o resultado é multiplicado por V.

O produto `QKᵀ` calcula um escore para cada par de posições. Escore é apenas um número que
expressa o resultado da comparação entre uma query e uma key. A transposição, indicada
pelo T, organiza K para que essa multiplicação compare cada consulta com cada chave.

O `d_k` é o número de componentes de cada query e key. A divisão por sua raiz ajusta a
escala dos escores. Vou explicar o motivo no próximo slide.

O **softmax** transforma os escores de cada linha em pesos não negativos que somam 1.
Por fim, multiplicar por V combina os vetores de conteúdo usando esses pesos. Se os pesos
forem 0,6, 0,3 e 0,1, usamos 60% do primeiro vetor, 30% do segundo e 10% do terceiro.

Essa média ponderada também recebe o nome de **combinação convexa**. O termo parece novo,
mas descreve justamente essas duas condições: pesos não negativos e soma igual a 1.

Outra observação: a comparação de uma posição com outra não precisa dar o mesmo resultado
no sentido inverso. Q e K usam transformações diferentes. Por isso, a matriz de escores
não precisa ser simétrica.

> 🗣️ “A fórmula compara os tokens, calcula os pesos e combina os conteúdos.”

> **Nota:** Bastidor: verificar se a turma identifica onde entram os pesos e onde entra o
> conteúdo. A derivação e as dimensões estão em A.1; não é preciso desenvolvê-las neste slide.

### Slide 6 · Por que dividir por `√d_k` · 00:33–00:43

Vou voltar à divisão por raiz de d_k. Quando aumentamos a dimensão de Q e K, o produto
escalar passa a somar mais termos. Sob as hipóteses do exemplo que veremos, isso aumenta
a dispersão dos escores.

O softmax usa exponenciais. Assim, diferenças grandes entre escores podem gerar pesos
muito concentrados: um fica perto de 1 e os outros, perto de 0. Chamamos esse comportamento
de **saturação**. Nessa situação, pequenas mudanças nos escores quase não alteram os pesos.

Isso pode dificultar o treinamento. O gradiente indica como uma pequena mudança nos
parâmetros afeta a perda, que mede o erro do modelo. Quando o gradiente que passa pelo
softmax fica muito pequeno, os ajustes em Q e K por esse caminho também podem ficar pequenos.

Para vetores com componentes independentes, média zero e variância um, o desvio-padrão
dos escores é raiz de d_k. Com 64 componentes, dá 8; com 512, aproximadamente 22,6. Esses
números descrevem a dispersão, não os limites mínimo e máximo dos escores.

A divisão por raiz de d_k compensa esse crescimento no exemplo. Ela ajusta os escores;
não transforma Q e K em vetores de comprimento um. Na atenção que estamos estudando,
esse fator é calculado a partir da dimensão.

Se um modelo maior estiver aprendendo pior, vale verificar essa parte da implementação.
Mas esse resultado, sozinho, não identifica a causa: precisamos olhar os escores, os
pesos e também outras condições do treinamento.

> 🗣️ “A divisão por raiz de d_k ajuda a evitar que os pesos fiquem concentrados demais por causa da escala.”

> **Nota:** Bastidor: usar A.2 para uma pergunta sobre a variância. Antes da demo, perguntar
> o que a turma espera observar nos pesos quando a divisão for retirada.

### Slide 7 · [Demo] Observando os pesos de atenção · 00:43–00:55

Vou abrir um exemplo pequeno em NumPy para vermos esses cálculos. Primeiro comparo as
duas frases com “banco”. Depois observo o efeito da divisão, a máscara e a troca de ordem
dos tokens. Os passos estão na Parte 2 deste roteiro.

> 🗣️ “Vou comparar as saídas para relacionar cada parte da fórmula com os números do exemplo.”

> **Nota:** Bastidor: reservar mais tempo para as medições 1 e 2. Usar os minutos finais
> para dúvidas curtas. Intervalo de 00:55 a 01:05.

### Slide 8 · Máscara causal: usando apenas o contexto disponível · 01:05–01:14

Voltando ao modelo que gera texto: ele precisa prever um token usando o que veio antes.
Se a entrada termina em “o banco estava”, o próximo token ainda não está disponível.

No treinamento, temos a sequência completa e podemos calcular previsões para várias
posições ao mesmo tempo. A saída da posição i é usada para prever o token i+1. Por isso,
precisamos impedir que essa posição consulte o token que deveria prever.

A **máscara causal** permite consultar a própria posição e as anteriores, bloqueando as
seguintes. Causal, aqui, quer dizer que a previsão usa apenas o contexto já disponível.
Sem esse bloqueio, o modelo pode usar a resposta durante o treino. Chamamos isso de
**vazamento de futuro**. A perda pode ficar muito baixa, mas a geração não se beneficiar
do mesmo modo, porque ali o próximo token ainda não existe.

A máscara entra antes do softmax: colocamos menos infinito nos escores proibidos.
O softmax atribui peso zero a eles e distribui os pesos entre as posições permitidas.

Se eu calcular o softmax sobre todas as posições e apenas zerar os pesos do futuro depois,
a linha deixa de somar 1. Além disso, os escores futuros já participaram do denominador
e influenciaram os pesos que restaram.

Vou conferir duas coisas na implementação: se as linhas somam aproximadamente 1 e se
mudar o último token preserva as saídas anteriores. Nesse segundo teste, qualquer sorteio
do modelo precisa estar desativado para a comparação fazer sentido.

> 🗣️ “A máscara causal bloqueia as posições futuras antes de calcular os pesos.”

> **Nota:** Bastidor: percorrer uma linha da matriz triangular. A soma das linhas, sozinha,
> não prova que a máscara está correta; uma atenção sem máscara também soma 1. Ver A.3.

### Slide 9 · Multi-head: várias combinações em paralelo · 01:14–01:22

Até aqui, usamos um conjunto de Q, K e V. Isso é uma cabeça de atenção. Na **multi-head
attention**, usamos vários conjuntos de projeções e calculamos suas saídas em paralelo.
Depois juntamos essas saídas e fazemos mais uma transformação linear.

Cada cabeça pode dar pesos diferentes às posições. Isso permite combinar informações
de várias maneiras na mesma camada. Não significa que cada cabeça receba uma tarefa
definida, como “encontrar o sujeito”. Essa divisão não vem pronta.

Como exemplo, podemos usar dimensão total 512 e oito cabeças com dimensão 64 cada.
Mantendo a dimensão total, o custo das principais multiplicações fica semelhante ao de
uma cabeça larga. Ainda existem custos de memória e de implementação a considerar.

Os mapas de atenção mostram os pesos calculados. Se uma cabeça costuma ligar um verbo
a um substantivo, isso pode sugerir um padrão. Para concluir qual papel ela tem na resposta
do modelo, precisamos de outros testes. Vamos retomar essa discussão na Aula 27.

> 🗣️ “Várias cabeças permitem calcular combinações diferentes de informação na mesma camada.”

> **Nota:** Bastidor: mostrar a divisão 512/8 = 64 sem abrir os detalhes dos tensores.
> As dimensões e o custo estão em A.4.

### Slide 10 · Como o tamanho do contexto afeta a memória · 01:22–01:29

Vou olhar agora para o tamanho da matriz de atenção. Se a sequência tem n tokens, temos
n linhas e n colunas: uma entrada para cada par de posições.

Com 2.000 tokens, são 4 milhões de entradas por cabeça. Com 4.000 tokens, são 16 milhões.
Ao dobrar o contexto, esse número aumenta quatro vezes. Se cada entrada ocupa dois bytes,
a matriz passa de cerca de 8 MB para 32 MB, considerando apenas uma cabeça e uma sequência.

Na implementação que guarda essa matriz inteira, esse crescimento pesa na memória.
Ainda temos outras cabeças, exemplos do lote, camadas e dados do treinamento. Então essa
conta estima uma parte do uso de memória, não o total da GPU.

O custo de cálculo da atenção também cresce de forma quadrática com o comprimento,
mantendo a dimensão fixa. Isso não significa que o tempo medido do programa sempre
quadruplicará, porque ele depende do hardware e das outras operações.

A atenção permite processar posições em paralelo no treino, enquanto a RNN tem uma
dependência sequencial entre elas. Esse paralelismo é uma vantagem, mas não torna gratuito
o uso de sequências longas. Veremos formas mais eficientes de calcular a atenção adiante.

> 🗣️ “Dobrar o contexto quadruplica o número de entradas da matriz de atenção.”

> **Nota:** Bastidor: deixar explícito que a conta se refere à matriz materializada.
> A.5 separa custo de cálculo, memória e passos sequenciais.

### Slide 11 · Encoder, decoder e cross-attention · 01:29–01:35

Vou reunir as peças no Transformer com encoder e decoder, a arquitetura apresentada
no artigo que vamos ler. Um exemplo de uso é traduzir uma frase de uma língua para outra.

O **encoder** processa a frase de entrada. Sua self-attention é bidirecional: cada token
pode consultar os tokens dos dois lados, sem a restrição causal.

O **decoder** produz a sequência de saída e tem duas atenções por bloco. Na self-attention
causal, ele usa o trecho de saída já disponível. Na **cross-attention**, consulta as
representações produzidas pelo encoder: Q vem do decoder, e K e V vêm do encoder.

É a mesma ideia de consultar a entrada durante a geração que vimos com Bahdanau.
O cálculo de compatibilidade é diferente: aqui usamos o produto escalar com escala.

**[Aponto o caminho da entrada pelo encoder e a ligação até a cross-attention.]**

As caixas de rede feed-forward, normalização e conexões residuais também fazem parte do
bloco. Hoje vou apenas localizá-las; vamos estudar sua função na próxima aula.

> 🗣️ “Na cross-attention, o decoder faz a consulta e o encoder fornece as chaves e os valores.”

### Slide 12 · Geração token a token e KV cache · 01:35–01:39

Como o modelo continua um texto? Ele calcula probabilidades para o próximo token,
escolhe um token, acrescenta esse token à sequência e repete o processo. Chamamos isso
de **geração autorregressiva**, porque cada nova previsão usa os tokens anteriores.

Uma implementação simples executa o modelo de novo sobre toda a sequência a cada passo.
Com isso, recalcula chaves e valores das posições anteriores. Na atenção causal, em modo
de inferência, acrescentar um token ao final não altera essas posições.

O **KV cache** guarda as chaves e os valores já calculados em cada camada para reutilizá-los.
Isso reduz o trabalho repetido, mas ocupa memória. Vamos detalhar essa troca adiante.

Também existe a arquitetura **decoder-only**, como a família GPT. Ela usa uma sequência
com o prompt e sua continuação, sob máscara causal, sem a pilha separada de encoder
e sem a cross-attention que acabamos de ver no modelo de tradução.

> 🗣️ “O KV cache guarda chaves e valores anteriores para reutilizá-los durante a geração.”

### Slide 13 · [Exercício] Como investigar três problemas · 01:39–01:50

Agora vou propor três situações para discutirmos em dupla. Para cada uma, a resposta
precisa ter uma causa possível e uma forma de verificar se essa causa faz sentido.
Temos oito minutos para discutir e três para comparar as respostas.

**[Projeto o enunciado da Parte 3.]**

> 🗣️ “Para cada problema, vamos propor uma hipótese e dizer como testá-la.”

### Slide 14 · Por que ainda precisamos representar a posição · 01:50–02:00

Hoje vimos como a self-attention combina informações da sequência. Q e K calculam os
pesos, V fornece os conteúdos, a divisão ajusta a escala e a máscara restringe o contexto.
Também vimos por que sequências longas aumentam o custo dessa operação.

Falta retomar um resultado da demonstração. No exemplo sem informação de posição e
sem máscara causal, embaralhar os tokens apenas embaralha as linhas da saída. Quando
acompanho o mesmo token, encontro o mesmo vetor de antes.

Isso importa porque “o cachorro morde o homem” e “o homem morde o cachorro” têm as mesmas
palavras, mas sentidos diferentes. Precisamos representar a posição para que o mecanismo
use essa diferença. O nome matemático da propriedade que vimos é **equivariância a
permutação**: trocar a ordem da entrada troca a ordem da saída da mesma maneira.
A máscara causal restringe quais posições podem ser consultadas; a demonstração sem
máscara não pode ser aplicada diretamente a esse caso.

Na Aula 7, “Transformer II: posição, normalização e o bloco moderno”, vamos estudar
informação posicional, conexões residuais, normalização e a rede feed-forward.

Para a leitura, ficam as seções 3.1 a 3.3 de Vaswani e colaboradores. Minha sugestão é
começar pela figura da arquitetura e localizar a fórmula de hoje. O item A.2 do apêndice
ajuda a acompanhar a justificativa da raiz de d_k. A pergunta para o estudo é como a conta
da variância se relaciona com os números observados na demonstração.

> 🗣️ “Além do conteúdo de cada token, o modelo precisa de informação sobre sua posição.”

> **Nota:** Bastidor: mostrar onde estão A.1, A.2 e A.6 no material. Reservar tempo para uma
> dúvida final ou para cada aluno registrar uma pergunta a retomar no Lab 2.

---

## Parte 2 — Demonstração guiada

> **Nota:** Bastidor: o script existente está em
> [`../../../aulas/aula-06/codigo/demo-attention.py`](../../../aulas/aula-06/codigo/demo-attention.py),
> relativo a esta pasta. A pasta da aula em V2 não contém uma cópia. Na raiz do projeto,
> executar `python -X utf8 aulas/aula-06/codigo/demo-attention.py`; para repetir só a
> permutação, acrescentar `--shuffle`. Requer NumPy. Executar antes da aula e salvar a
> saída para consulta caso o ambiente da sala falhe.

**1. [Mostro o vocabulário e os vetores do exemplo — 2 min.]**
Aqui cada palavra tem quatro componentes, que escolhi chamar de água, dinheiro, lugar e
ação. Os números e as matrizes foram definidos à mão para facilitar a leitura. Não houve
treinamento. Em embeddings aprendidos, não devemos esperar que cada componente tenha
um significado tão simples.

**2. [Comparo as saídas das duas frases — 3 min.]**
O vetor de entrada de “banco” é igual nos dois casos. Depois da atenção, as saídas são
diferentes. Vou comparar os componentes ligados a água e dinheiro e os pesos usados
para produzir essas saídas.

Neste exemplo, os pesos de “banco” coincidem nas duas frases, mas os valores combinados
mudam. O componente água da saída passa de aproximadamente 0,509 para 0,126; o de dinheiro
faz o caminho inverso. A mudança de contexto pode alterar os valores, os pesos ou ambos.

**3. [Mostro a tabela de escala — 4 min.]**
Agora o script usa vetores aleatórios com dimensões 4, 64 e 512. A coluna “desvio bruto”
mostra a dispersão dos escores. As duas últimas colunas mostram a média do maior peso
de cada linha, sem e com a divisão por raiz de d_k. Vou comparar como esses valores mudam.
É um experimento sobre os escores e os pesos; ele não está treinando um modelo.

> **Nota:** Bastidor: na execução com a semente padrão, a média do maior peso, sem divisão,
> foi 0,275, 0,807 e 0,939; com divisão, 0,110, 0,119 e 0,118. São resultados desta amostra,
> não valores que todo modelo deve apresentar.

**4. [Mostro a matriz com máscara causal — 1 min.]**
Acima da diagonal, os pesos são zero. Cada linha soma aproximadamente 1, dentro da
precisão numérica. Vamos retomar o motivo dessa máscara no slide 8, depois do intervalo.

**5. [Mostro a permutação dos tokens — 2 min.]**
Este exemplo usa atenção sem máscara e sem informação posicional. Depois de embaralhar
os tokens, comparo cada token com sua posição original. Os vetores correspondentes
continuam iguais, dentro da precisão numérica. Vamos voltar a isso no fechamento.

> **Nota:** Bastidor: o título impresso pelo script usa “invariante”. Esclarecer que o nome
> adequado aqui é “equivariante”: as linhas da saída acompanham a troca de ordem.

> **Nota:** Bastidor: se faltar tempo, usar a saída salva nos passos 4 e 5. Preservar a
> comparação de contexto e de escala, ouvindo as previsões da turma antes de mostrar o resultado.

---

## Parte 3 — Hands-on

**[Projeto as situações e organizo as duplas.]**

Vou deixar estas três situações na tela. Para cada uma, a dupla registra uma hipótese,
uma verificação e o resultado esperado se a hipótese estiver correta. Pode haver mais
de uma explicação; vamos usar os conceitos de hoje para começar a investigação.

1. Um modelo com `d_model = 1024` tem perda de validação maior que uma versão com
   `d_model = 256`, usando os mesmos dados e o mesmo número de passos. A perda de validação
   mede o erro em dados separados do treinamento. Não aparecem valores numéricos inválidos.
2. Um modelo de linguagem tem perda quase zero no treino e gera texto incoerente.
   O programa termina sem apresentar erro.
3. Uma equipe aumenta o contexto de 2.000 para 4.000 tokens. O modelo e o tamanho do lote
   permanecem iguais, mas o treinamento passa a exceder a memória da GPU.

> **Nota:** Bastidor: dar oito minutos para discussão. Aos quatro minutos, se necessário,
> resolver um exemplo de verificação: observar os escores e os pesos do softmax para
> investigar a hipótese de escala.

**Respostas para orientar a correção — 3 min:**

| Situação | Hipótese a investigar | Verificação e resultado esperado |
|---|---|---|
| 1 | Escores muito dispersos e saturação do softmax, caso a dimensão por cabeça tenha aumentado | Conferir `d_k` e a divisão por `√d_k`; comparar a dispersão dos escores e a concentração dos pesos. Se a escala estiver incorreta, corrigi-la deve reduzir a concentração causada por esse erro. Comparar também as curvas de treino e validação. |
| 2 | Vazamento de futuro por máscara ausente ou incorreta | Desativar o dropout, que introduz sorteio no treino, e alterar o último token. As saídas anteriores devem permanecer iguais. Verificar também os pesos futuros e a soma das linhas. |
| 3 | Crescimento da matriz de atenção armazenada | Conferir o formato da matriz e a memória que ela ocupa. Ao dobrar n, seu número de elementos quadruplica. O consumo total da GPU inclui outras parcelas e pode crescer em outra proporção. |

> **Nota:** Bastidor: não tratar essas hipóteses como diagnósticos já confirmados. No caso 1,
> a informação sobre validação não permite descartar sobreajuste, quando o modelo se ajusta
> bem ao treino e generaliza mal. Aumentar `d_model` também não implica aumentar `d_k` se o
> número de cabeças mudar. No caso 2, a perda baixa também admite outras explicações. Valorizar
> quem propõe uma verificação que distingue as hipóteses.

**[Convido uma dupla a comentar cada situação.]**

Vou começar pela hipótese que vocês levantaram e depois pela verificação. Que resultado
nos faria manter essa hipótese? E que resultado indicaria que precisamos procurar outra causa?

**Extensão opcional:** cálculo de atenção com três tokens, seguindo o item A.1.

---

## Parte 4 — Apêndice: se perguntarem

Estas respostas dão apoio às perguntas que surgirem. Uma dúvida curta deve ser acolhida
no momento; uma derivação completa pode usar o tempo disponível ou ficar para o estudo
orientado pelo apêndice.

### 1. “De onde vem a fórmula?” → A.1 · 8 min

Vou escrever as projeções e identificar as dimensões. Para seis tokens, a matriz de
escores tem seis linhas e seis colunas. Depois acompanho uma linha: comparações com as
chaves, ajuste de escala, pesos do softmax e média dos valores. O item A.1 detalha cada conta.

**Versão de 30 segundos:** “Q e K produzem as comparações entre posições. Ajustamos a
escala, transformamos os resultados em pesos que somam 1 e usamos esses pesos para
combinar V. A.1 mostra como as dimensões se encaixam.”

### 2. “Por que raiz de d_k, e não d_k?” → A.2 · 6 min

Vou explicitar as hipóteses: componentes independentes, média zero e variância um.
Cada produto tem variância um; somar d_k desses produtos dá variância d_k. O desvio-padrão
é a raiz da variância. Dividir por esse desvio faz a variância do escore escalado voltar a um.

**Versão de 30 segundos:** “Nessas hipóteses, a dispersão típica cresce com a raiz da
dimensão. Dividimos por essa raiz para compensar o crescimento. A conta está em A.2.”

### 3. “Por que não zerar os pesos depois?” → A.3 · 5 min

Vou comparar a soma de uma linha nos dois casos. Se eu normalizar usando também o futuro
e depois apenas zerá-lo, os pesos restantes somam menos que um. O denominador ainda
depende dos escores futuros. Com a máscara antes, só as posições permitidas participam
da normalização.

**Versão de 30 segundos:** “Ao zerar depois, os tokens futuros já influenciaram o cálculo
dos outros pesos. Aplicar a máscara antes evita essa influência e mantém a soma igual a um.”

### 4. “Várias cabeças não custam mais?” → A.4 · 4 min

Vou manter d_model fixo e dividir essa dimensão entre h cabeças. As projeções de cada
cabeça ficam menores; ao somá-las, o número de parâmetros dessas projeções se mantém.
O custo das multiplicações de atenção também fica na mesma ordem. Isso não garante
igualdade de tempo ou de memória na implementação.

**Versão de 30 segundos:** “Dividimos uma dimensão total fixa entre cabeças menores.
As principais multiplicações têm custo semelhante, mas guardar mais matrizes de pesos
pode consumir mais memória. A.4 separa essas contas.”

### 5. “De onde vem o n ao quadrado?” → A.5 · 3 min

Vou desenhar uma tabela com uma linha e uma coluna para cada token. Com quatro tokens,
são dezesseis pares; com oito, sessenta e quatro. Depois associo cada célula ao espaço
ocupado por um número na memória.

**Versão de 30 segundos:** “Cada uma das n posições é comparada com n posições. São n²
pares. Se dobrarmos os dois lados da matriz, o número de entradas aumenta quatro vezes.”

### 6. “Como sabemos que trocar a ordem só troca a saída de lugar?” → A.6 · 5 min

Vou considerar atenção sem informação posicional e sem máscara. Uso P para representar
a troca de linhas e acompanho essa troca nas projeções, nos escores e na saída. No fim,
a saída aparece multiplicada pela mesma P. A.6 traz as etapas e suas justificativas.

**Versão de 30 segundos:** “Nesse caso, os cálculos dependem dos vetores dos tokens, sem
usar seus índices na sequência. Ao mudar os tokens de lugar, suas saídas mudam junto.
A demonstração geral está em A.6; o exemplo do script mostra um caso.”

### Ajustes de tempo

> **Nota:** Bastidor: primeiro substituir a execução das medições 3 e 4 pela leitura das
> saídas salvas; depois reduzir a discussão dos mapas de cabeças e os exemplos adicionais
> de memória. Preservar a explicação de Q/K/V, a comparação de escala, a máscara causal e
> o exercício com correção. Uma derivação só entra se houver tempo recuperado suficiente.
> Caso contrário, responder brevemente, localizar o item do apêndice e registrar a dúvida.

---

## Encerramento · 01:50–02:00

A fala de encerramento está no slide 14: retomar as funções dos termos da fórmula,
discutir a posição dos tokens e indicar a leitura com o apoio de A.2.

*Roteiro do Instrutor · Aula 6 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
