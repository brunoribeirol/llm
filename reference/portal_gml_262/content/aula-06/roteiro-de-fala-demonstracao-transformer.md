# Roteiro de fala — Demonstração interativa da arquitetura Transformer

**Aula 06 · Graduação em Ciência da Computação · 20 etapas.**

Material de apoio ao professor para conduzir `transformer-arquitetura-interativa.html`. A numeração acompanha as vinte etapas do HTML, e não as páginas dos slides antigos. O estilo de fala segue o material `roteiro-de-fala-aula06.pdf`: explicações em primeira pessoa, exemplos concretos, conceitos introduzidos progressivamente e transições entre os assuntos.

## Como usar este roteiro

**O que ler em voz alta.** Os parágrafos iniciados por **Fala** são sugestões prontas para conduzir a explicação. As instruções **Ação na tela**, **Observe**, **Pergunta**, **Resposta esperada** e **Transição** orientam a demonstração. Adapte o ritmo e a linguagem à turma; não é necessário ler os rótulos.

**Preparação.** Abra o HTML em um navegador e mantenha este roteiro impresso ou em uma segunda tela. Use “Modo projeção” para ocultar as falas e o menu lateral do artefato. Nesse modo, avance com “Avançar →” ou com a seta direita do teclado. Se precisar saltar para uma etapa pelo menu, use “Mostrar falas do professor” para sair do modo projeção. Ao operar um seletor ou um controle deslizante, as setas do teclado ajustam o próprio controle; use o botão “Avançar →” para prosseguir sem ambiguidade.

**Ponto de partida das experiências.** Ao entrar em cada etapa, clique em “Restaurar experiência”. Esse botão restaura somente a etapa atual. “Começar do início” volta à etapa 1, mas não apaga os ajustes feitos nas outras telas. Por isso, o roteiro sempre indica o estado que deve aparecer antes da fala. As etapas mantêm ajustes ao serem revisitadas.

**Dois tipos de exemplo.** A tradução “Eu gosto de gatos” → “I like cats” organiza a explicação da arquitetura. As contas pequenas de atenção, normalização e FFN são laboratórios independentes com parâmetros escolhidos à mão. Os valores de uma tela não são transmitidos para a próxima como em uma execução completa de um modelo treinado. Diga isso na abertura e retome quando a demonstração passar a usar os tokens abstratos t₁, t₂ e t₃.

**Precisão da exposição.** O percurso principal apresenta o Transformer encoder–decoder com pós-normalização. A etapa 19 compara outras famílias e a pré-normalização, identificando a mudança de ordem. Lote, dropout e alguns vieses são omitidos nas contas didáticas. Os números na tela são arredondados; quando comparar resultados, use as três casas exibidas, sem exigir igualdade exata de somas arredondadas.

**Tempo sugerido.** As vinte etapas somam aproximadamente 102 minutos, incluindo os cliques e as perguntas curtas indicadas. Reserve 10 minutos de intervalo após a etapa 8 e 8 minutos para perguntas ou retomadas: total de 120 minutos. Os tempos são uma referência de condução; não interrompa uma dúvida conceitual apenas para cumprir o relógio. Para uma demonstração breve, reduza as contas secundárias e preserve a sequência das peças.

**Se a interação falhar.** O arquivo `transformer-arquitetura-interativa.pdf` mostra o estado inicial de cada etapa. Este roteiro também registra resultados dos principais ajustes. Use essas duas fontes para conduzir a comparação verbalmente; não descreva uma mudança visual como se ela tivesse ocorrido se estiver exibindo apenas uma página estática.

## Etapa 01 — Duas pilhas, um caminho completo

**Menu:** A arquitetura inteira. **Tempo sugerido:** 4 minutos. **Estado inicial:** mapa de duas colunas, encoder à esquerda e decoder à direita. Não há controles numéricos nesta etapa.

### Passo 1 — Apresentar o objetivo

**Ação na tela.** Clique em “Começar do início”. Aponte a frase da fonte e, em seguida, as duas colunas. Se for projetar, ative “Modo projeção”.

**Fala.** Boa noite, pessoal. Hoje vamos percorrer o Transformer inteiro, desde a entrada do texto até a escolha de um token de saída. Vou usar a tradução de “Eu gosto de gatos” para “I like cats” como exemplo. A frase em português já está disponível. A tradução ainda precisa ser construída. A coluna da esquerda representa a entrada; a da direita usa essa representação enquanto produz a outra sequência. Quero que vocês consigam explicar o trabalho de cada caixa, sem depender de decorar sua posição no desenho.

### Passo 2 — Separar as responsabilidades

**Ação na tela.** Aponte “H_enc: uma linha por token” e depois “Cross-attention ← H_enc”. Não clique nas caixas ainda: elas levam a outras etapas.

**Fala.** O encoder não entrega as palavras em inglês. Ele entrega vetores que representam as posições da frase de entrada levando o contexto em consideração. Essa saída se chama H_enc no desenho. O decoder tem acesso a esses vetores e também ao que já foi escrito na tradução. A cross-attention é a ligação entre as duas sequências: ela permite ao decoder consultar a fonte codificada. O decoder não está aplicando uma função inversa para recuperar a frase original; ele está construindo outra sequência, que pode até ter outro comprimento.

### Passo 3 — Explicar o que será aberto

**Ação na tela.** Percorra com o cursor embedding, atenção, soma residual, normalização, feed-forward e projeção de saída.

**Fala.** Dentro de cada pilha temos operações com funções diferentes. O embedding transforma IDs em vetores. A posição acrescenta informação sobre a ordem. A atenção mistura informação entre posições. A feed-forward transforma cada representação. Residual e normalização organizam esse fluxo numa rede profunda. No final do decoder, uma projeção e um softmax produzem probabilidades para os tokens candidatos. As experiências numéricas vão usar matrizes pequenas para entendermos essas operações; elas não constituem um tradutor treinado, e seus números não serão transferidos de uma tela para a seguinte.

**Pergunta.** “Qual coluna recebe a frase que já conhecemos? Qual constrói a sequência que ainda não temos?”

**Resposta esperada.** O encoder recebe a fonte; o decoder participa da construção do alvo, com a cabeça de saída escolhendo tokens a partir de seus estados.

**Transição.** Vamos começar pela primeira mudança de representação: o computador precisa sair dos caracteres e chegar a uma sequência de vetores. Clique em “Avançar →”.

## Etapa 02 — 1 token → 1 ID → 1 vetor

**Menu:** Tokens e embeddings. **Tempo sugerido:** 5 minutos. **Estado inicial após restaurar:** seletor “Posição” em “2 · gosto”; destaque na segunda linha; E[42] = [0; 1; 0; 0].

### Passo 1 — Ler o caminho da entrada

**Ação na tela.** Aponte “gosto → ID 42 → linha de E” e a linha destacada da tabela à direita.

**Fala.** O primeiro passo é transformar o texto em tokens e associar cada token a um identificador. Para facilitar o desenho, cada palavra desta frase vale um token. Em um tokenizador real, uma palavra pode ser dividida em partes, e a segmentação também envolve espaços e pontuação. O ID 42 não significa que gosto seja maior ou mais importante que Eu, cujo ID aqui é 17. Esses números são índices: eles informam qual linha consultar na tabela de embeddings.

### Passo 2 — Mostrar a consulta à tabela

**Ação na tela.** Em “Posição”, escolha “1 · Eu”. Depois escolha “4 · gatos”.

**Observe.** Eu destaca o ID 17 e o vetor [1; 0; 0; 0]. Gatos destaca o ID 9 e o vetor [0; 0; 0; 1]. A forma da matriz continua 4 × 4.

**Fala.** Ao trocar o token selecionado, estou apenas mostrando outra linha consultada. Cada vetor tem quatro componentes. Esses componentes foram escolhidos manualmente para nossa demonstração; não são coordenadas aprendidas de significados reais. Em um modelo treinado, a tabela é ajustada para ajudar o objetivo de aprendizagem, mas suas dimensões não vêm obrigatoriamente com rótulos humanos como pessoa, animal ou ação. Consultar a tabela ainda não faz o token conversar com os vizinhos.

### Passo 3 — Explicar as dimensões e os parâmetros

**Ação na tela.** Aponte “E: N_vocab × d → E[IDs]: n × d”. Retorne a “2 · gosto”.

**Fala.** A tabela completa tem uma linha por item do vocabulário. A matriz da sequência contém apenas as linhas consultadas, na ordem dos tokens. Aqui n é quatro, porque temos quatro posições, e d também é quatro, porque escolhemos quatro componentes por vetor. São duas dimensões com papéis distintos, apesar de terem o mesmo valor neste exemplo. Se a frase passar a ter dez tokens, ganharemos linhas na matriz da sequência, não componentes adicionais em cada vetor. A tabela E continua com o mesmo tamanho.

**Pergunta.** “Se o mesmo ID aparecer duas vezes na frase, a consulta inicial a E devolve o mesmo vetor?”

**Resposta esperada.** Sim. A posição e o processamento contextual podem diferenciar essas ocorrências nas etapas seguintes.

**Transição.** Já temos o conteúdo de cada token representado por um vetor. Agora falta dizer em que posição ele está. Avance.

## Etapa 03 — O vetor precisa carregar conteúdo e posição

**Menu:** Informação de posição. **Tempo sugerido:** 5 minutos. **Estado inicial:** “Somar posição senoidal” marcado; “Inverter a ordem dos tokens” desmarcado. A primeira linha de X, relativa a Eu, é [2; 1; 0; 1].

### Passo 1 — Identificar as duas parcelas

**Ação na tela.** Aponte P à esquerda e X à direita. Leia a fórmula X = √d · E[IDs] + P.

**Fala.** Agora temos um vetor de conteúdo e um vetor de posição. O Transformer original multiplica o embedding pela raiz de d e soma a codificação posicional. Aqui d vale quatro, então a escala é dois. Para a primeira posição, o embedding escalado de Eu é [2; 0; 0; 0], e a posição fornece [0; 1; 0; 1]. A soma resulta em [2; 1; 0; 1]. Continuamos com quatro componentes. Somar não é colocar um vetor depois do outro: isso seria concatenar e mudaria a largura.

### Passo 2 — Retirar a posição antes de trocar a ordem

**Ação na tela.** Desmarque “Somar posição senoidal”. Depois marque “Inverter a ordem dos tokens”.

**Observe.** Eu passa da primeira para a última linha, mas mantém o vetor [2; 0; 0; 0]. As linhas de X apenas trocam de ordem. A tabela P continua mostrando as posições, embora sua contribuição esteja desligada.

**Fala.** Sem somar a posição, o vetor continua ligado apenas ao ID consultado. Eu mudou de lugar, mas levou o mesmo vetor consigo. A atenção sem posição e sem máscara tem uma propriedade correspondente: permutar as linhas da entrada apenas permuta as linhas da saída. Ela não ganha uma marca explícita de primeiro, segundo ou último só porque a matriz foi apresentada numa determinada ordem. Chamamos isso de equivariância a permutação, não de saída invariável.

### Passo 3 — Recolocar a informação de ordem

**Ação na tela.** Mantendo a ordem invertida, marque novamente “Somar posição senoidal”.

**Observe.** Eu, agora na quarta linha, recebe aproximadamente [2,141; −0,990; 0,030; 1,000], diferente de sua representação inicial na primeira posição.

**Fala.** Agora Eu recebe o vetor da posição em que está. O conteúdo e o lugar na sequência participam da representação. Não precisamos deduzir todas as senoides para acompanhar a arquitetura; o essencial é entender onde essa informação entra. Há alternativas, como posições aprendidas e rotações de Q e K. Também precisamos tomar cuidado com a máscara causal: ela introduz uma assimetria de ordem, então a afirmação de permutação que acabei de fazer não se aplica diretamente se mantivermos essa máscara fixa.

**Pergunta.** “A soma de posição mudou o número de linhas ou de componentes?”

**Resposta esperada.** Não. Mudou os valores de X; sua forma continuou n × d.

**Transição.** Com conteúdo e posição representados, vamos criar as três projeções usadas pela atenção. Restaure a experiência e avance.

## Etapa 04 — Q e K comparam; V fornece o conteúdo

**Menu:** Consultas, chaves e valores. **Tempo sugerido:** 6 minutos. **Estado inicial:** “Token abstrato” em t₂; q₂ = [0; 1], k₂ = [1,414; 0] e v₂ = [0; 2].

### Passo 1 — Declarar a mudança para a miniatura numérica

**Ação na tela.** Aponte o aviso de três tokens abstratos e a linha “X: 3 tokens × 4 componentes”.

**Fala.** Agora vamos sair temporariamente da tradução e usar três posições abstratas, t₁, t₂ e t₃. Isso permite fazer a conta inteira. Não estamos dizendo que esses números representam Eu, gosto ou gatos. As matrizes foram construídas à mão. A entrada X tem três linhas e quatro componentes por linha. Vamos multiplicá-la por três matrizes diferentes, cada uma com forma quatro por dois. O resultado são três projeções com três linhas e dois componentes.

### Passo 2 — Explicar consulta, chave e valor

**Ação na tela.** Aponte, nesta ordem, Q, K e V. Mantenha t₂ selecionado.

**Fala.** A consulta, Q, será usada para procurar compatibilidade. A chave, K, fornece aquilo com que a consulta será comparada. O valor, V, fornece o conteúdo que vamos transportar depois de decidir os pesos. Podemos pensar em procurar registros: um critério de consulta é comparado com informações de identificação, e os conteúdos dos registros encontrados são recuperados. Aqui, porém, não há uma busca exata: teremos vetores, produtos escalares e uma mistura suave de várias posições.

### Passo 3 — Mostrar que a mesma entrada pode gerar três vetores diferentes

**Ação na tela.** Troque “Token abstrato” para t₃. Leia q₃ = [1; 1], k₃ = [0; 1,414] e v₃ = [2; 2]. Depois volte a t₂.

**Fala.** As três projeções vêm da mesma linha de X, mas usam matrizes diferentes. Por isso, Q, K e V não precisam ser iguais. Essas matrizes são parâmetros aprendidos; as projeções são resultados calculados para uma entrada. Na self-attention, consulta, chave e valor vêm da mesma sequência. Mais adiante, na cross-attention, veremos uma consulta vindo do decoder e chaves e valores vindo do encoder. Essa diferença de origem é mais importante que decorar as letras.

### Passo 4 — Preparar a conta seguinte

**Ação na tela.** Aponte q₂ e depois percorra as três linhas de K, não apenas k₂.

**Fala.** Selecionar t₂ não significa compará-lo só com ele mesmo. Vamos pegar sua consulta e compará-la com todas as chaves permitidas. Cada comparação dará um número, e esses números formarão uma linha da matriz de escores. V aguardará a próxima parte: os valores só serão combinados depois de produzirmos os pesos.

**Pergunta.** “Quem calcula a compatibilidade e quem fornece o conteúdo misturado?”

**Resposta esperada.** Q e K calculam compatibilidade; V fornece o conteúdo.

**Transição.** Vamos acompanhar uma consulta comparando as três chaves. Avance.

## Etapa 05 — Cada consulta compara todas as chaves

**Menu:** Escores e escala. **Tempo sugerido:** 5 minutos. **Estado inicial:** “Quem consulta?” em t₂ e “Dividir por √d_k” marcado. A linha selecionada é [0; 0; 1].

### Passo 1 — Calcular uma célula antes de ler a matriz

**Ação na tela.** Aponte q₂ = [0; 1] e a comparação com k₃ = [0; 1,414].

**Fala.** A consulta da segunda posição tem componentes zero e um. A terceira chave tem zero e raiz de dois. O produto escalar multiplica componentes correspondentes e soma: zero vezes zero, mais um vezes raiz de dois. O resultado é raiz de dois. Como a largura da chave é dois, dividimos também por raiz de dois e obtemos um. Essa é a célula da linha dois, coluna três. Linha identifica quem consulta; coluna identifica quem é consultado.

### Passo 2 — Relacionar a operação à forma da matriz

**Ação na tela.** Troque “Quem consulta?” para t₁. Compare s₁₂ = 1 com s₂₁ = 0. Depois retorne a t₂.

**Fala.** Q tem forma três por dois, e K transposto tem forma dois por três. O produto produz três por três: uma comparação para cada par de posições. Não precisamos repetir essa operação numa estrutura manual de laços para explicar o conceito; a multiplicação de matrizes já expressa todas as comparações. Observem também que a matriz não é simétrica. Consultar a posição dois a partir da um não é necessariamente a mesma coisa que fazer a consulta no sentido contrário, porque Q e K usam projeções diferentes.

### Passo 3 — Demonstrar o fator de escala

**Ação na tela.** Desmarque “Dividir por √d_k”. Observe o terceiro escore de t₂ mudar de 1,000 para 1,414. Marque novamente.

**Fala.** A escala alterou a magnitude, não a ordem das comparações desta linha. Em dimensões maiores, o produto escalar soma mais parcelas. Sob a hipótese simplificada de componentes independentes, com média zero e variância um, a variância da soma cresce como d_k, e seu desvio-padrão cresce como a raiz de d_k. A divisão compensa esse crescimento. Nossa dimensão dois produz uma diferença modesta; a motivação fica mais evidente quando os escores se tornam muito dispersos e o softmax se concentra perto de zero e um. Não estamos normalizando o comprimento dos vetores nem calculando cosseno.

**Pergunta.** “Se d_k fosse 64, por qual número dividiríamos?”

**Resposta esperada.** Oito. d_k é a largura da chave por cabeça, não o comprimento da sequência.

**Transição.** Já temos comparações. Precisamos convertê-las em pesos e usar esses pesos sobre V. Deixe a escala marcada e avance.

## Etapa 06 — Escores → pesos → um novo vetor

**Menu:** Softmax e mistura de V. **Tempo sugerido:** 7 minutos. **Estado inicial:** “Consulta” em t₂; escores [0; 0; 1]; pesos [0,212; 0,212; 0,576]; saída [1,576; 1,576].

### Passo 1 — Ler o softmax como uma conta de pesos

**Ação na tela.** Aponte os três escores e depois as três barras. Antes de mostrar a soma, pergunte qual barra deve ser maior.

**Fala.** A terceira comparação tem escore maior e receberá mais peso. O softmax aplica a exponencial e divide cada resultado pela soma da linha. Os dois zeros viram um; o escore um vira aproximadamente 2,718. O denominador é aproximadamente 4,718. Assim chegamos a 0,212, 0,212 e 0,576. Os pesos são positivos e somam um. A normalização acontece separadamente para cada consulta, não sobre a matriz inteira.

### Passo 2 — Fazer a primeira componente da saída

**Ação na tela.** Aponte a tabela V e leia as três parcelas exibidas abaixo dela. Faça no quadro a conta da primeira componente.

**Fala.** Agora cada peso multiplica uma linha inteira de V. Para o primeiro componente, temos 0,212 vezes dois, mais 0,212 vezes zero, mais 0,576 vezes dois. O resultado, calculando antes de arredondar, é aproximadamente 1,576. Para o segundo componente, fazemos a mesma combinação com a segunda coluna: zero, dois e dois. Neste exemplo, o resultado coincide. A atenção produziu um vetor com dois componentes porque V tem largura dois; ela não escolheu uma palavra.

### Passo 3 — Mostrar outra consulta com o mesmo conjunto de valores

**Ação na tela.** Selecione t₁ em “Consulta”. Compare os pesos [0,212; 0,576; 0,212] e a saída [0,848; 1,576].

**Fala.** As linhas de V continuam iguais, mas a consulta mudou os pesos. Agora a segunda posição contribui mais. Isso mostra como posições diferentes podem extrair combinações diferentes do mesmo contexto. A palavra atenção dá nome a essa operação, mas não significa uma decisão humana de importância. Um mapa de pesos também não explica sozinho toda a resposta do modelo: precisamos considerar os valores, a projeção de saída, as outras cabeças e as camadas seguintes.

### Passo 4 — Fixar o que entra e o que sai

**Ação na tela.** Volte a t₂ e aponte o resultado z₂.

**Fala.** Nesta cabeça, antes de dropout e da projeção de saída, fazemos uma combinação convexa: pesos não negativos que somam um, aplicados aos valores. Mas o Transformer completo não fica limitado a tirar médias. Há transformações aprendidas antes e depois dessa mistura, residuais e não linearidades. A conta que acabamos de fechar é apenas uma suboperação. Vamos agora restringir quais posições podem participar dela.

**Pergunta.** “Um peso de 0,576 é a probabilidade de gerar o terceiro token?”

**Resposta esperada.** Não. É o peso de uma posição na mistura de valores desta cabeça. Probabilidades de geração aparecerão no softmax sobre o vocabulário.

**Transição.** Na previsão do próximo token, certas posições revelariam a resposta. Vamos bloqueá-las antes da normalização. Avance.

## Etapa 07 — O futuro não pode entrar no denominador

**Menu:** Máscara causal. **Tempo sugerido:** 7 minutos. **Estado inicial:** “Máscara causal ligada” marcado; “Escore futuro s₂₃” em 1,0; saída da posição 2 igual a [1,000; 1,000].

### Passo 1 — Ler o triângulo bloqueado

**Ação na tela.** Aponte a linha 2 nas duas matrizes e a posição da coluna 3 marcada como bloqueada.

**Fala.** Estamos olhando para a segunda posição de uma sequência causal. Ela pode consultar a primeira e a própria segunda posição. A terceira está no futuro e precisa ser excluída. Na matriz de escores, colocamos menos infinito nessa célula; depois do softmax, seu peso vira zero. Sobram dois escores iguais, então os pesos são meio e meio. A saída é metade de [2; 0] mais metade de [0; 2], ou seja, [1; 1].

### Passo 2 — Pedir uma previsão antes de mexer no escore futuro

**Ação na tela.** Pergunte o que acontecerá se o escore futuro ficar muito grande. Mova “Escore futuro s₂₃” para 9,0, mantendo a máscara marcada.

**Observe.** A saída continua [1,000; 1,000], e a linha de pesos continua [0,500; 0,500; 0,000].

**Fala.** O resultado não mudou. Não importa quanto aumentamos o escore de uma posição proibida: ela continua excluída da normalização. Estamos alterando diretamente uma célula de S para isolar o efeito da máscara, não treinando um modelo nem trocando uma frase real. Essa experiência mostra a propriedade que desejamos: uma informação futura não pode afetar uma previsão anterior no caminho causal.

### Passo 3 — Retirar a restrição e observar o vazamento

**Ação na tela.** Com o escore ainda em 9,0, desmarque “Máscara causal ligada”.

**Observe.** A terceira posição domina a linha 2. Com três casas decimais, seus pesos aparecem como [0,000; 0,000; 1,000], e a saída aparece [2,000; 2,000]. São arredondamentos de valores próximos desses extremos.

**Fala.** Sem a máscara, a posição futura passa a dominar a mistura. A comparação entre os dois estados é a parte importante: a restrição mudou quais informações podem participar. Se apenas substituíssemos o escore proibido por zero, sua exponencial ainda seria um. Se aplicássemos softmax e só depois apagássemos o peso futuro, o denominador já teria usado aquele escore, e a soma dos pesos restantes deixaria de ser um. A ordem correta é restringir os escores antes do softmax.

### Passo 4 — Ligar a diagonal ao alvo deslocado

**Ação na tela.** Marque novamente a máscara e aponte a diagonal. Termine com “Restaurar experiência”.

**Fala.** A diagonal é permitida porque o token atual já pertence ao prefixo conhecido. É a saída dessa posição que prevê o token seguinte. Vamos mostrar esse deslocamento explicitamente na etapa 13. Em uma implementação, outro teste é alterar um token futuro e conferir se as saídas anteriores permanecem iguais, com dropout desativado. Uma loss pequena sozinha não demonstra que esse comportamento está correto.

**Pergunta.** “O futuro foi excluído antes ou depois da normalização?”

**Resposta esperada.** Antes, para que não contribua nem com peso nem com o denominador.

**Transição.** Uma cabeça já está completa. Vamos combinar várias consultas aprendidas em paralelo. Avance.

## Etapa 08 — Consultas diferentes, uma saída concatenada

**Menu:** Múltiplas cabeças. **Tempo sugerido:** 5 minutos. **Estado inicial:** “Inspecionar” em “Cabeça 1”. A linha 2 dessa cabeça produz [1,576; 1,576].

### Passo 1 — Explicar a multiplicidade

**Ação na tela.** Aponte “Toda X alimenta as duas cabeças”, depois o mapa à esquerda.

**Fala.** Uma cabeça produz um padrão de mistura por consulta. Agora queremos permitir diferentes padrões ao mesmo tempo. Para isso, cada cabeça tem projeções próprias e recebe toda a entrada X. Não estamos entregando o começo da frase a uma cabeça e o fim a outra. Elas consultam a mesma sequência em espaços de representação diferentes, definidos por suas matrizes aprendidas.

### Passo 2 — Comparar saídas que serão concatenadas

**Ação na tela.** Troque “Inspecionar” para “Cabeça 2”. Aponte a linha 2 dos pesos e seu vetor de saída.

**Observe.** A segunda cabeça produz aproximadamente [1,576; 0,848] para a linha 2, enquanto a primeira produzia [1,576; 1,576].

**Fala.** A segunda cabeça tem outro padrão de pesos e também usa sua própria projeção de valores. Por isso, sua saída pode ser diferente. Não defini uma cabeça de sujeito e outra de verbo. Os números são didáticos, e num modelo real os papéis que atribuímos às cabeças são hipóteses que precisam de evidência. O mecanismo apenas oferece mais de uma forma aprendida de comparar e combinar representações.

### Passo 3 — Ler concatenação e projeção de saída

**Ação na tela.** Aponte a linha concatenada à direita: [1,576; 1,576; 1,576; 0,848]. Depois aponte W_O.

**Fala.** Cada cabeça entregou dois componentes por posição. Concatenar significa colocar esses componentes lado a lado, obtendo quatro. A próxima transformação é W_O, que mistura essa concatenação e retorna à largura do modelo. A tela mostra o resultado numérico até a concatenação; não apresenta um valor numérico calculado depois de W_O. No exemplo de dimensões, a saída final continua três por quatro. Num modelo com d igual a 512 e oito cabeças, uma divisão usual dá 64 componentes a cada cabeça, que juntos voltam a 512.

**Pergunta.** “Concatenar as cabeças é somar os seus vetores?”

**Resposta esperada.** Não. A concatenação coloca componentes lado a lado; a projeção W_O faz a transformação aprendida seguinte.

**Transição.** Já temos o mecanismo de atenção. Depois do intervalo, vamos encaixá-lo num bloco completo. Restaure a etapa; se seguir o percurso de 120 minutos, faça agora o intervalo de 10 minutos.

## Etapa 09 — A entrada ganha uma atualização

**Menu:** Conexão residual. **Tempo sugerido:** 4 minutos. **Estado inicial:** intensidade em 1,0; “Somar a entrada X” marcado. X = [2; −1; 1; 3], F(X) = [0,5; −0,5; 1; −1] e saída [2,5; −1,5; 2; 2].

### Passo 1 — Retomar a atenção e introduzir a soma

**Ação na tela.** Aponte os cartões Entrada, Atualização e Soma. Leia a primeira componente: 2 + 0,5 = 2,5.

**Fala.** A atenção produz uma transformação da representação, mas não precisamos obrigar essa transformação a reconstruir sozinha toda a informação útil da entrada. A conexão residual soma a entrada com uma atualização. A seta lateral leva X diretamente até a soma, enquanto o outro caminho calcula F(X). Aqui F representa uma subcamada; a experiência usa apenas um vetor de atualização simples para enxergarmos a operação. As duas parcelas têm a mesma forma.

### Passo 2 — Reduzir a atualização a zero

**Ação na tela.** Leve “Intensidade da atualização” para 0,0, mantendo “Somar a entrada X” marcado.

**Observe.** A atualização fica [0; 0; 0; 0], mas a saída da soma permanece [2; −1; 1; 3].

**Fala.** Com atualização zero, a soma preserva X. Essa é uma razão para a interpretação de aprender uma correção sobre o estado existente. Em termos de treinamento, a derivada de X mais F(X) contém um caminho de identidade, além do caminho da transformação. Isso facilita o fluxo de informação e do gradiente numa pilha profunda. Não significa que uma rede residual nunca tenha problemas de otimização.

### Passo 3 — Comparar com o caminho sem residual

**Ação na tela.** Com intensidade zero, desmarque “Somar a entrada X”. Depois marque novamente e restaure a intensidade.

**Observe.** Sem residual e com atualização zero, a saída vira [0; 0; 0; 0].

**Fala.** Ao retirar a soma, dependemos apenas da transformação, que neste caso não está produzindo nada. A comparação torna visível o papel do atalho. Também precisamos localizar exatamente qual ponto estamos observando: esta tela termina antes da LayerNorm. No bloco pós-norm, ainda aplicaremos normalização depois da soma. Portanto, atualização zero preserva X na soma, mas a saída completa da subcamada será LN(X), que pode ser diferente de X.

**Pergunta.** “É possível somar uma entrada n × 4 com uma saída n × 2 diretamente?”

**Resposta esperada.** Não na soma residual desenhada; as formas devem coincidir. A projeção de saída da atenção ajuda a devolver a largura d.

**Transição.** Vamos abrir a operação que aparece depois dessa soma no Transformer original: LayerNorm. Avance.

## Etapa 10 — Normalizar os componentes de cada token

**Menu:** LayerNorm. **Tempo sugerido:** 5 minutos. **Estado inicial:** deslocamento 0,0, escala 1,0. x = [1; 3; 2; 6], média 3,000, variância 3,500 e saída aproximada [−1,069; 0,000; −0,535; 1,604].

### Passo 1 — Definir o eixo da normalização

**Ação na tela.** Aponte “Uma linha, quatro componentes”. Calcule a média oralmente e depois a variância no quadro.

**Fala.** A normalização está olhando para os quatro componentes de um token. A média de um, três, dois e seis é três. As diferenças para a média são menos dois, zero, menos um e três. Seus quadrados são quatro, zero, um e nove; a média desses quadrados é 3,5. Subtraímos a média de cada componente e dividimos pela raiz da variância mais um pequeno epsilon. Não estamos calculando uma média entre palavras da frase nem entre exemplos diferentes do lote.

### Passo 2 — Somar a mesma constante aos componentes

**Ação na tela.** Mova “Deslocamento de x” para 5,0, mantendo a escala em 1,0.

**Observe.** x vira [6; 8; 7; 11], a média vira 8,000, a variância permanece 3,500 e a saída normalizada mantém os valores exibidos.

**Fala.** Somamos cinco a todos os componentes. A média também aumentou cinco. Quando subtraímos a nova média, as diferenças relativas são as mesmas. Por isso a saída permanece igual. A operação remove esse deslocamento comum, permitindo trabalhar com uma representação cujo centro e escala foram controlados. Isso ajuda a organizar as ativações, mas não substitui o aprendizado do restante da rede.

### Passo 3 — Alterar a escala e explicar γ e β

**Ação na tela.** Volte o deslocamento a 0,0 e leve “Escala positiva de x” a 2,0.

**Observe.** x = [2; 6; 4; 12], média 6,000, variância 14,000. A saída exibida continua aproximadamente a mesma.

**Fala.** Ao multiplicar a entrada por dois, dobramos as diferenças e quadruplicamos a variância. A divisão pelo desvio-padrão compensa essa escala positiva. O epsilon impede que essa invariância de escala seja matematicamente exata em todos os casos. Depois dessa parte, LayerNorm aplica um ganho γ e um deslocamento β aprendidos por componente. Aqui deixamos γ em um e β em zero para enxergar a normalização central. Esses parâmetros não são o mesmo que os controles que acabamos de mover: os controles alteram a entrada x.

**Pergunta.** “Normalizar os componentes de x é o mesmo que fazer os pesos de atenção somarem um?”

**Resposta esperada.** Não. LayerNorm atua nos componentes de cada token; softmax de atenção normaliza escores entre posições para produzir pesos de mistura.

**Transição.** Já temos atenção, soma residual e norma. Falta uma rede que transforme cada representação dentro do bloco. Restaure e avance.

## Etapa 11 — Transformar cada posição com uma rede não linear

**Menu:** Rede feed-forward. **Tempo sugerido:** 5 minutos. **Estado inicial:** segundo componente de x em −2,0; “Aplicar ReLU” marcado. x = [1; −2], xW₁ = [1; −2; −1; −3], ativação [1; 0; 0; 0] e saída [1; 0].

### Passo 1 — Seguir a expansão e o retorno à largura original

**Ação na tela.** Aponte os três cartões da esquerda para a direita: dois componentes, quatro componentes e dois componentes.

**Fala.** Esta experiência tem uma entrada de dois componentes. A primeira matriz expande a largura para quatro. Entre as duas multiplicações, aplicamos uma função não linear. Depois, a segunda matriz retorna a dois componentes, mantendo uma forma que pode ser somada ao caminho residual. No Transformer original, essa rede usa ReLU; outras variantes usam outras ativações ou mecanismos de portas. Aqui todos os vieses foram definidos como zero para simplificar a conta.

### Passo 2 — Identificar exatamente o que a ReLU faz

**Ação na tela.** Leia xW₁ e o vetor depois da ReLU. Depois desmarque “Aplicar ReLU”.

**Observe.** Com ReLU, os componentes negativos viram zero e a saída é [1; 0]. Sem ReLU, a saída passa a [3; −6].

**Fala.** ReLU toma o máximo entre zero e cada componente. Ela mantém o um positivo e zera os três números negativos. Ao desligá-la, os negativos passam para a segunda multiplicação e a saída muda. Isso não demonstra que a primeira saída é melhor; demonstra que a função calculada é diferente. Se só encadearmos transformações lineares, podemos reuni-las numa única matriz. A não linearidade impede essa redução geral e amplia o tipo de função que a rede pode representar.

### Passo 3 — Alterar a entrada para ver a ativação mudar

**Ação na tela.** Marque novamente ReLU. Mova “Segundo componente de x” para 2,0.

**Observe.** x = [1; 2], xW₁ = [1; 2; 3; 1], todos os componentes passam pela ReLU e a saída é [3; 6].

**Fala.** Os mesmos parâmetros produziram outra resposta porque a entrada mudou. É assim que a mesma rede pode atuar em todas as posições da sequência sem devolver o mesmo vetor para elas. A FFN não consulta diretamente uma outra linha da matriz. Ela mistura componentes da linha atual. Mas essa linha pode ter recebido informação de outros tokens na atenção anterior. Por isso dizemos que o processamento é por posição, não que sua entrada seja desprovida de contexto.

**Pergunta.** “Qual subcamada mistura posições e qual transforma os componentes de cada posição?”

**Resposta esperada.** A atenção mistura informação entre posições permitidas; a FFN transforma cada linha com parâmetros compartilhados entre posições daquela camada.

**Transição.** Já temos todas as peças de um bloco encoder. Vamos juntá-las na ordem correta. Restaure e avance.

## Etapa 12 — Um bloco completo; depois, vários blocos

**Menu:** Pilha encoder. **Tempo sugerido:** 5 minutos. **Estado inicial:** “Quantidade de blocos ilustrados” em 3. À esquerda, um bloco em detalhe; à direita, três blocos empilhados.

### Passo 1 — Montar a primeira metade do bloco

**Ação na tela.** Aponte X, multi-head self-attention e “Soma com X → LayerNorm → U”.

**Fala.** Agora a entrada X passa pela atenção multi-head. O resultado tem a mesma forma de X e pode ser somado a ela. Depois vem LayerNorm. Chamamos esse resultado intermediário de U. A equação resume o caminho: U é LN de X mais MHA de X. Esta é a pós-normalização do Transformer original: a norma está depois da soma. Não vamos mudar essa ordem silenciosamente quando desenharmos o próximo bloco.

### Passo 2 — Fechar a segunda metade

**Ação na tela.** Percorra FFN(U) e “Soma com U → LayerNorm → Y”.

**Fala.** Em seguida, U passa pela FFN. Essa transformação retorna à largura d e é somada ao próprio U, que segue pelo atalho residual desta segunda subcamada. Aplicamos outra LayerNorm e obtemos Y. Há duas somas e duas normalizações, não uma única normalização no fim de tudo. No modelo original também há dropout em pontos como a saída das subcamadas antes da soma. Omitimos esse sorteio nas contas para concentrar a explicação no fluxo determinístico.

### Passo 3 — Variar a profundidade do desenho

**Ação na tela.** Escolha 1 em “Quantidade de blocos ilustrados”. Depois escolha 6 e, ao final, retorne a 3.

**Observe.** A coluna direita muda o número de blocos. O controle desenha a pilha; não calcula representações de camadas treinadas.

**Fala.** A saída de um bloco alimenta o seguinte. A forma n por d permanece, mas o conteúdo dos vetores pode mudar a cada transformação. Repetir a estrutura não significa repetir os mesmos pesos. Em geral, o bloco dois tem parâmetros próprios, diferentes dos do bloco um. No modelo original, o encoder tinha seis blocos. O número é uma escolha de arquitetura, não uma exigência da definição de atenção. No final, H_enc contém uma representação contextual por posição da fonte.

**Pergunta.** “O encoder precisa comprimir a frase inteira em um único vetor para passá-la ao decoder?”

**Resposta esperada.** Não. Neste Transformer, a saída é uma sequência de vetores, que o decoder poderá consultar por cross-attention.

**Transição.** A fonte já pode ser representada. Agora vamos organizar a entrada do decoder para que ele aprenda a prever sem ler sua resposta. Avance.

## Etapa 13 — A posição atual prevê o token seguinte

**Menu:** Alvo deslocado. **Tempo sugerido:** 5 minutos. **Estado inicial:** “Posição que faz a previsão” em “3 · like”. Pode consultar `<início>`, I e like; deve prever cats.

### Passo 1 — Explicar as duas linhas da tabela

**Ação na tela.** Leia a linha “Entrada” e, abaixo, a linha “Alvo correto”. Aponte a coluna da terceira posição.

**Fala.** Durante o treino, temos a tradução correta: I like cats. Mas construímos as entradas de forma deslocada. A primeira posição recebe o marcador de início e prevê I. A segunda recebe I e prevê like. A terceira recebe like e prevê cats. A quarta recebe cats e prevê fim. Não estamos pedindo para a saída da terceira posição reproduzir o token da terceira entrada. Ela precisa prever o token seguinte, usando somente o prefixo disponível.

### Passo 2 — Voltar ao início da sequência

**Ação na tela.** Selecione “1 · <início>”. Observe que apenas o marcador inicial está permitido e que o alvo é I.

**Fala.** Na primeira previsão, ainda não escrevemos nenhuma palavra da tradução. O decoder pode usar o marcador inicial e a fonte codificada, que continua disponível. Os tokens I, like e cats são conhecidos no conjunto de treino, mas ficam bloqueados na entrada do alvo para essa posição. A máscara é justamente o que impede aproveitar essa disponibilidade física do texto para copiar o futuro durante a aprendizagem.

### Passo 3 — Avançar o prefixo sem confundir entrada e resposta

**Ação na tela.** Selecione “3 · like” novamente; depois, “4 · cats”.

**Observe.** Na terceira posição, cats está no futuro da entrada e deve ser previsto. Na quarta, cats já pertence ao prefixo e o alvo passa a ser `<fim>`.

**Fala.** O mesmo token pode ser resposta em um passo e entrada no passo seguinte. Isso não é uma contradição. O que importa é o que já estava disponível no momento de cada previsão. A diagonal da máscara é permitida porque contém o token atual da entrada, que já conhecemos. Quando cats passa a fazer parte do prefixo, o decoder pode usá-lo para prever se deve continuar ou encerrar a sequência.

**Pergunta.** “Na posição que recebe like, seria correto usar cats como entrada só porque ele está no arquivo de treinamento?”

**Resposta esperada.** Não. Isso revelaria o alvo daquela posição e quebraria a restrição causal que também precisamos respeitar na geração.

**Transição.** O prefixo do alvo está organizado. Falta entender como ele consulta a outra sequência: a fonte que o encoder representou. Restaure e avance.

## Etapa 14 — O decoder pergunta; o encoder fornece a fonte

**Menu:** Cross-attention. **Tempo sugerido:** 6 minutos. **Estado inicial:** “Consulta do decoder” em “Posição 2”. Mapa de atenção 3 × 4; saída selecionada aproximadamente [1,227; 0,891].

### Passo 1 — Identificar a origem das projeções

**Ação na tela.** Aponte “Estado do decoder D → Q” e “H_enc → K e V”.

**Fala.** Na self-attention, as três projeções vieram da mesma sequência. Aqui mudamos essa organização. A consulta vem do estado corrente do decoder. As chaves e os valores são projeções da saída final do encoder. A pergunta é feita por uma posição do alvo, e o conteúdo consultado está na fonte. Por isso o nome cross-attention: estamos relacionando duas sequências diferentes. Não é necessário que elas tenham o mesmo comprimento.

### Passo 2 — Ler o mapa retangular

**Ação na tela.** Conte as três linhas de consultas e as quatro colunas, rotuladas Eu, gosto, de e gatos.

**Fala.** Temos m igual a três consultas e n igual a quatro posições da fonte. Q tem forma três por dois, K tem forma quatro por dois e V também quatro por dois. QK transposto produz três por quatro, não três por três. Depois do softmax, cada linha distribui peso entre as quatro posições da fonte. O produto com V devolve três vetores de largura dois. Essa conta mostra por que o decoder pode produzir uma sequência de comprimento diferente da entrada.

### Passo 3 — Trocar a consulta mantendo a fonte

**Ação na tela.** Troque para “Posição 1” e depois “Posição 3”. Compare com a posição 2 inicial.

**Observe.** As saídas selecionadas são, respectivamente, [1,000; 0,665] e [1,170; 0,835]. O mapa completo já mostra as três consultas; o seletor destaca uma delas.

**Fala.** As chaves e os valores da fonte permanecem os mesmos, mas cada consulta produz seus próprios pesos. Esses números também são construções didáticas. Não devemos concluir que representam um alinhamento aprendido entre palavras da tradução. O que podemos concluir é como uma consulta escolhe uma combinação de conteúdos disponíveis. Mesmo que o maior peso recaia sobre gatos em uma linha, a saída ainda é uma combinação de vetores, não uma palavra em inglês.

### Passo 4 — Separar fonte conhecida de futuro do alvo

**Ação na tela.** Aponte a coluna gatos e retome o prefixo I like do exemplo de tradução.

**Fala.** Para prever cats, o decoder pode consultar gatos na fonte. A frase inteira em português já fazia parte da entrada. O que ele não pode fazer é consultar cats como token futuro da própria tradução. Nesta tarefa, não colocamos uma máscara triangular causal sobre a fonte só porque existe uma máscara causal no alvo. Normalmente bloqueamos as posições de padding da fonte; outras restrições dependeriam de uma tarefa diferente, como tradução com entrada chegando aos poucos.

**Pergunta.** “Qual eixo do mapa representa a fonte e qual representa o alvo?”

**Resposta esperada.** As colunas são chaves da fonte; as linhas são consultas originadas no decoder.

**Transição.** Vamos encaixar essa consulta à fonte entre as outras subcamadas do decoder. Restaure e avance.

## Etapa 15 — Três subcamadas dentro do decoder

**Menu:** Bloco decoder completo. **Tempo sugerido:** 5 minutos. **Estado inicial:** “Destacar subcamada” em “Cross-attention”. O bloco usa pós-normalização.

### Passo 1 — Seguir a atenção causal do alvo

**Ação na tela.** Em “Destacar subcamada”, escolha “Self-attention causal”. Aponte X, a subcamada destacada e a soma que produz A.

**Fala.** Começamos com a representação do alvo. A self-attention causal consulta apenas posições permitidas desse alvo. Em seguida, somamos o resultado à entrada X e aplicamos LayerNorm, obtendo A. Até aqui, este caminho organiza o contexto já escrito na tradução. Cada posição mantém sua restrição causal: a pilha inteira deve preservar a impossibilidade de consultar o futuro do alvo.

### Passo 2 — Acrescentar a consulta à fonte

**Ação na tela.** Escolha “Cross-attention”. Percorra a ligação com H_enc, a soma com A e a normalização que produz B.

**Fala.** Agora A fornece as consultas para a cross-attention. H_enc fornece o material para gerar chaves e valores. A saída dessa consulta é uma nova atualização, somada ao próprio A. Depois vem outra LayerNorm, e chamamos o resultado de B. Observem que o atalho desta subcamada leva A, não a entrada original X de todo o bloco. Cada subcamada tem seu próprio ponto de entrada e sua própria conexão residual.

### Passo 3 — Fechar o bloco com a FFN

**Ação na tela.** Escolha “Feed-forward”. Aponte a equação Y = LN(B + FFN(B)).

**Fala.** A FFN transforma cada posição de B. Somamos o resultado a B, normalizamos e obtemos Y. Temos três subcamadas, três somas e três normalizações. Empilhamos esse conjunto L_d vezes. A fonte codificada fica disponível para a cross-attention de cada bloco decoder; cada bloco aprende suas próprias projeções. Não precisamos rodar o encoder novamente para cada token se a fonte continua a mesma, mas as consultas do decoder mudam conforme o prefixo cresce.

**Pergunta.** “Quais são as três subcamadas, na ordem do decoder original?”

**Resposta esperada.** Self-attention causal, cross-attention e FFN, cada uma seguida de sua soma residual e LayerNorm no arranjo pós-norm.

**Transição.** A pilha produz estados com d componentes. Ainda precisamos convertê-los numa escolha entre os tokens do vocabulário. Avance.

## Etapa 16 — O segundo softmax responde outra pergunta

**Menu:** Logits e vocabulário. **Tempo sugerido:** 5 minutos. **Estado inicial:** temperatura T em 1,0. Logits ilustrativos [2; 1; 0; −1]; candidatos cats, dogs, birds e `<fim>`. Probabilidades aproximadas [0,644; 0,237; 0,087; 0,032].

### Passo 1 — Mudar do espaço de representação para o vocabulário

**Ação na tela.** Aponte h: 1 × d, depois W_vocab e a linha de logits.

**Fala.** O estado final tem d componentes, mas precisamos avaliar N_vocab candidatos. Uma projeção aprendida converte a largura da representação na largura do vocabulário. Cada escore resultante é um logit. Os quatro logits desta experiência foram definidos manualmente para mostrar a operação de saída; não foram produzidos pelas experiências anteriores. Em um modelo real, eles são calculados a partir do estado do decoder, e o vocabulário costuma ter muito mais itens.

### Passo 2 — Distinguir os dois softmax

**Ação na tela.** Percorra os rótulos das barras: cats, dogs, birds e fim. Compare verbalmente com t₁, t₂ e t₃ na atenção.

**Fala.** A fórmula do softmax é a mesma ideia de normalizar exponenciais, mas o eixo e o significado mudaram. Na atenção, distribuímos peso entre posições para combinar valores. Aqui distribuímos probabilidade entre tokens candidatos à próxima saída. Cats recebe aproximadamente 64,4% da probabilidade no vocabulário reduzido deste exemplo. Isso não é uma garantia de que a tradução esteja correta; é a distribuição definida por estes logits.

### Passo 3 — Explorar a temperatura sem confundi-la com a escolha

**Ação na tela.** Leve “Temperatura T” para 0,3. Depois para 2,0. Observe tanto as barras quanto “Escolha por argmax”.

**Observe.** A distribuição fica mais concentrada com 0,3 e mais distribuída com 2,0. Cats continua sendo o argmax nos dois casos.

**Fala.** Dividimos os logits por uma temperatura positiva antes do softmax. Uma temperatura menor amplia diferenças relativas na entrada do softmax e concentra as probabilidades; uma maior as suaviza. A ordem dos logits não muda, então escolher sempre o maior continua produzindo cats. Se usarmos amostragem, a mudança nas probabilidades altera a chance de selecionar outros candidatos. Esta tela exibe argmax; não está sorteando um token a cada ajuste.

**Pergunta.** “A barra de cats indica quanto a atenção consultou a palavra gatos na fonte?”

**Resposta esperada.** Não. Ela indica a probabilidade de cats no vocabulário de saída desta experiência. A consulta à fonte ocorreu em outra operação.

**Transição.** Vamos usar a escolha do próximo token para fechar o laço de geração. Restaure a temperatura e avance.

## Etapa 17 — O token escolhido entra no próximo prefixo

**Menu:** Geração passo a passo. **Tempo sugerido:** 5 minutos. **Estado inicial:** zero escolhas realizadas, prefixo `<início>` e tradução ainda vazia. Botões “Gerar próximo token” e “Reiniciar tradução”.

### Passo 1 — Separar o que é reutilizado do que vai mudar

**Ação na tela.** Aponte os quatro vetores do encoder à esquerda e o prefixo à direita.

**Fala.** A frase fonte já foi codificada e está disponível nesses quatro vetores. A tradução ainda está vazia. O decoder começa com o marcador de início, consulta a fonte, produz um estado e, pela cabeça de saída, uma distribuição. Nesta demonstração as escolhas estão roteirizadas para mostrar a sequência I, like, cats e fim. O botão não executa um tradutor treinado, mas representa corretamente a dependência entre as etapas de uma geração autorregressiva.

### Passo 2 — Gerar os dois primeiros tokens

**Ação na tela.** Clique uma vez em “Gerar próximo token”. Faça uma pausa. Clique uma segunda vez.

**Observe.** Após o primeiro clique, a tradução contém I e o prefixo para o próximo passo contém `<início> I`. Após o segundo, a tradução contém I like e o prefixo inclui essas duas palavras.

**Fala.** O primeiro token escolhido passou a ser uma entrada do passo seguinte. Depois da segunda escolha, temos um prefixo maior. A tela mostra o estado já atualizado para a próxima previsão; por isso o token que acabou de sair aparece imediatamente no prefixo. A fonte codificada permanece a mesma. O que muda é o contexto do alvo e, portanto, as consultas e os estados calculados pelo decoder.

### Passo 3 — Concluir a tradução e emitir fim

**Ação na tela.** Clique uma terceira vez e leia I like cats. Clique uma quarta vez.

**Observe.** A quarta escolha é o marcador de fim. A tela indica “Geração encerrada”, o botão de geração fica desabilitado e a tradução visível permanece I like cats.

**Fala.** Depois de cats, ainda fazemos uma previsão para decidir se a sequência continua. A escolha de fim encerra o processo. Não acrescentamos a palavra fim à tradução. Também não precisamos produzir quatro palavras só porque a fonte tinha quatro tokens: o comprimento da saída é determinado pela geração e pelo critério de parada. Nesta inferência comum, os parâmetros ficam fixos; aumentar o prefixo não é treinar a rede de novo.

### Passo 4 — Relacionar causalidade e reaproveitamento

**Ação na tela.** Aponte o prefixo final e os vetores da fonte. Se quiser repetir a sequência, use “Reiniciar tradução”.

**Fala.** Como o decoder é causal, um token antigo não precisa incorporar um token que foi gerado depois dele. Isso permite reaproveitar chaves e valores calculados para o prefixo antigo, em cada camada. Vamos quantificar esse cache na última etapa. Mesmo com reaproveitamento, ainda há uma dependência entre escolhas: precisamos do token selecionado agora para montar o próximo prefixo.

**Pergunta.** “O paralelismo das multiplicações dentro de um passo elimina a dependência entre os tokens gerados?”

**Resposta esperada.** Não. A geração autorregressiva comum desta sequência depende das escolhas anteriores.

**Transição.** A geração depende de um prefixo desconhecido que vai sendo construído. No treino, a sequência correta já existe. Vamos comparar os dois casos. Avance.

## Etapa 18 — Prever em paralelo; aprender com o erro

**Menu:** Treinamento e perda. **Tempo sugerido:** 5 minutos. **Estado inicial:** “Observar” em “Treinamento”; probabilidade do alvo em 0,7; perda de uma posição aproximadamente 0,357.

### Passo 1 — Mostrar por que várias previsões podem ser calculadas juntas

**Ação na tela.** Leia entrada deslocada e alvos no cartão esquerdo.

**Fala.** No treinamento, temos uma sequência correta para usar como exemplo. Podemos montar todas as entradas deslocadas e calcular previsões para várias posições numa passagem pela pilha. Isso não autoriza consultar o futuro: cada posição continua usando a máscara causal. Não há uma recorrência que obrigue a posição dois da mesma camada a esperar o estado recém-calculado da posição um. As camadas ainda são percorridas em ordem, mas há paralelismo entre posições dentro de cada camada.

### Passo 2 — Interpretar a perda sem pressupor experiência em machine learning

**Ação na tela.** Aponte −log p(alvo). Mova a probabilidade do alvo para 0,1 e depois para 0,9.

**Observe.** Com 0,1, a perda fica aproximadamente 2,303. Com 0,9, fica aproximadamente 0,105. O controle altera uma probabilidade ilustrativa de uma posição.

**Fala.** A perda penaliza atribuir pouca probabilidade ao token correto. Se o modelo deu apenas 10% de probabilidade à resposta do exemplo, menos log dessa probabilidade é relativamente grande. Com 90%, essa perda é menor. Para a sequência, podemos tirar a média das perdas nas posições válidas. Depois, a retropropagação calcula como mudanças nos parâmetros afetam a perda, e o otimizador usa esse sinal para ajustar as matrizes. Mover este controle não executa uma atualização real; ele mostra como a função de perda responde à probabilidade do alvo.

### Passo 3 — Comparar com inferência

**Ação na tela.** Em “Observar”, selecione “Geração”. Leia os três prefixos e o cartão “Parâmetros fixos”.

**Fala.** Na geração, não recebemos a continuação correta. Escolhemos um token, acrescentamos ao prefixo e fazemos a próxima previsão. Não há atualização de W neste laço comum. Treinamento e inferência compartilham a arquitetura e a restrição causal, mas têm dados disponíveis e objetivos operacionais diferentes. Uma loss muito pequena também não prova que o código está certo: se houve vazamento do alvo, o modelo pode parecer excelente no treino por uma razão que desaparece na geração.

**Pergunta.** “A máscara causal deve ser desligada porque o treinamento conhece a frase inteira?”

**Resposta esperada.** Não. Ela impede usar tokens futuros como entrada de uma previsão que deveria depender apenas do prefixo.

**Transição.** Agora entendemos o sistema completo. Vamos comparar algumas variantes sem confundir as diferenças de arquitetura. Restaure e avance.

## Etapa 19 — Reconheça as variantes sem misturar as ordens

**Menu:** Famílias e pré-norm. **Tempo sugerido:** 4 minutos. **Estado inicial:** “Família” em “Encoder–decoder”; “Ordem do bloco” em “Pós-norm”.

### Passo 1 — Fixar qual arquitetura foi demonstrada

**Ação na tela.** Aponte o caminho fonte → encoder → H_enc e a fórmula Y = LN(X + F(X)).

**Fala.** Até aqui seguimos o encoder–decoder com pós-normalização. O modelo recebe uma sequência fonte e constrói uma sequência alvo, com a cross-attention fazendo a ligação. A norma vem depois da soma em cada subcamada. Vou mudar agora duas escolhas separadas: primeiro a família de arquitetura e depois a ordem da normalização. Separar essas mudanças evita interpretar diagramas diferentes como se fossem apenas estilos de desenho.

### Passo 2 — Comparar as famílias

**Ação na tela.** Em “Família”, selecione “Encoder-only” e depois “Decoder-only”. Mantenha “Pós-norm” durante essa comparação.

**Fala.** Um encoder-only produz representações bidirecionais da entrada e pode receber uma cabeça adequada à tarefa, como classificação. Já o decoder-only usa uma pilha causal para prever a continuação do próprio prefixo. Prompt e continuação pertencem à mesma sequência. Não há um encoder separado escondido nem a cross-attention à fonte do nosso exemplo. A ausência dessa consulta não elimina o contexto: o contexto conhecido está no próprio prefixo processado pela pilha causal.

### Passo 3 — Mudar a ordem da normalização

**Ação na tela.** Mantendo “Decoder-only”, troque “Ordem do bloco” para “Pré-norm”. Aponte a fórmula e a nova caixa de norma final.

**Fala.** Na pré-normalização, aplicamos a norma antes da transformação F e somamos o resultado ao caminho residual: X mais F de LN de X. Isso difere de aplicar LN depois de somar X com F de X. A variante ilustrada também tem uma norma final após a pilha. Essa escolha afeta o caminho das ativações e dos gradientes. Não podemos concluir, a partir deste desenho, que toda variante precisa de exatamente as mesmas normas ou que retirar uma norma sempre causa divergência. RoPE, RMSNorm e FFNs com portas são outras escolhas que aprofundaremos na aula seguinte.

**Pergunta.** “Mudar para decoder-only e mudar de pós-norm para pré-norm são a mesma alteração?”

**Resposta esperada.** Não. Uma escolha define a família e suas conexões; a outra define onde a normalização aparece nas subcamadas.

**Transição.** Para fechar, vamos relacionar os desenhos a duas consequências de execução: crescimento do contexto e reaproveitamento de K e V. Restaure e avance.

## Etapa 20 — O desenho da arquitetura explica o custo

**Menu:** Contexto, custo e cache. **Tempo sugerido:** 4 minutos. **Estado inicial:** “Contexto n” em “2.000 tokens”; “Usar KV cache na geração” marcado. Uma matriz materializada ocupa 8,0 MB; o cache hipotético ocupa 2,05 MB na exibição, calculados a partir de 2,048 MB.

### Passo 1 — Relacionar o custo ao número de pares

**Ação na tela.** Aponte “Uma matriz de atenção” e seus quatro milhões de entradas. Depois selecione “4.000 tokens”.

**Observe.** A matriz passa a dezesseis milhões de entradas e 32,0 MB. O cache hipotético passa a cerca de 4,10 MB, calculados a partir de 4,096 MB.

**Fala.** Cada posição faz consultas às chaves do contexto. Uma matriz n por n tem n ao quadrado entradas. Ao dobrar n, quadruplicamos essa matriz. Aqui cada entrada ocupa dois bytes, e MB usa a convenção decimal. Estamos contando uma matriz materializada por cabeça, sequência e camada, não toda a memória da GPU. Parâmetros, outras ativações, lote e estado do otimizador acrescentam parcelas diferentes. O crescimento do cache mostrado ao lado é linear neste exemplo; ele mede outra coisa.

### Passo 2 — Explicar o que o cache guarda

**Ação na tela.** Aponte “Reutilizar K e V antigos”. Desmarque “Usar KV cache na geração”. Depois marque novamente.

**Observe.** Sem cache, o cartão indica “Recalcular K e V antigos”, e a parcela de armazenamento reutilizável é mostrada como zero. Isso não significa memória total zero.

**Fala.** O cache guarda chaves e valores calculados para tokens anteriores em cada camada. Quando chega um token novo, calculamos suas projeções e reutilizamos o que já foi calculado para o prefixo. Desligar o cache retira esse reaproveitamento persistente; não retira a necessidade de calcular atenção ou armazenar dados temporários. No exemplo da tela, contamos duas tabelas, K e V, para quatro camadas, largura 64, um exemplo e dois bytes por componente. Não estamos medindo o tempo de um modelo real nem afirmando que cache e matriz de atenção sejam as únicas parcelas de memória.

### Passo 3 — Encerrar reconstruindo a arquitetura

**Ação na tela.** Aponte as duas fórmulas no rodapé da experiência. Para fechar com o mapa, clique em “Começar do início”.

**Fala.** Implementações como FlashAttention evitam materializar a matriz completa na memória principal da GPU, embora a atenção densa ainda envolva interações entre pares de posições. O desenho nos ajuda a entender o cálculo, mas precisamos saber como ele foi implementado para estimar toda a execução. Agora podemos voltar ao mapa e contar a história inteira: tokens viram vetores, recebem posição, passam por atenção, FFN, somas e normas. O encoder representa a fonte; o decoder usa prefixo e fonte para construir estados. A cabeça de saída transforma esses estados em probabilidades, e a geração acrescenta um token por vez ao prefixo.

**Pergunta final.** “Onde se mistura informação entre posições? Onde se transforma cada linha? Onde aparece a distribuição do próximo token?”

**Resposta esperada.** Atenção mistura posições; FFN transforma cada linha; a projeção de saída e o softmax sobre o vocabulário produzem a distribuição do próximo token.

**Fechamento.** Se vocês conseguem seguir essas três perguntas no desenho, já conseguem ler a estrutura de um Transformer. Na próxima etapa do curso, vamos examinar escolhas internas e implementá-las, mantendo a ligação entre cada peça e o comportamento que ela deve produzir.

## Consulta rápida — Resultados e retomadas

**Atenção sem máscara, consulta t₂.** Escores [0; 0; 1]; pesos aproximados [0,212; 0,212; 0,576]; saída [1,576; 1,576]. Se os números não aparecerem, restaure a etapa 6 e confira o seletor “Consulta”.

**Máscara causal, linha 2.** Com a máscara ligada, os pesos são [0,500; 0,500; 0,000] e a saída é [1,000; 1,000]. Alterar apenas s₂₃ não muda a resposta. Desligar a máscara com s₂₃ = 9,0 faz a saída se aproximar de [2; 2]. O peso exibido como 1,000 é um arredondamento.

**Concatenação das cabeças, linha 2.** Cabeça 1: [1,576; 1,576]. Cabeça 2: [1,576; 0,848]. Concatenação: [1,576; 1,576; 1,576; 0,848]. W_O aparece como próxima transformação; não há resultado numérico depois dela nessa tela.

**Residual.** Intensidade zero com soma ligada devolve X antes da norma; intensidade zero sem soma devolve zero. No bloco pós-norm, ainda há LN depois da soma.

**LayerNorm.** Entrada [1; 3; 2; 6], média 3 e variância 3,5. Saída aproximada [−1,069; 0; −0,535; 1,604], com γ = 1, β = 0 e ε pequeno. Os controles alteram a entrada, não os parâmetros γ e β.

**FFN.** Com x = [1; −2], a saída é [1; 0] com ReLU e [3; −6] sem ReLU. Com x = [1; 2] e ReLU, a saída é [3; 6].

**Alvo deslocado.** Entrada `<início>, I, like, cats`; alvo `I, like, cats, <fim>`. A posição que recebe like prevê cats. A diagonal da entrada é permitida.

**Geração.** Quatro cliques: I, like, cats, fim. A tela mostra o prefixo já atualizado para o próximo passo. O botão fica desabilitado ao encerrar; “Reiniciar tradução” permite repetir.

**Perda.** −ln(0,7) ≈ 0,357; −ln(0,1) ≈ 2,303; −ln(0,9) ≈ 0,105. A probabilidade ajustada é de uma posição ilustrativa, não de uma sequência inteira.

**Memória.** Uma matriz de atenção a dois bytes por entrada: n = 2.000 → 8 MB; n = 4.000 → 32 MB. Cache hipotético: 2,048 MB e 4,096 MB, respectivamente, exibidos com duas casas. São parcelas distintas e não representam a memória total.

## Perguntas de fechamento e correção comentada

**“Qual é a diferença entre os pesos W e os pesos de atenção A?”** W são parâmetros ajustados pelo treinamento e mantidos fixos numa inferência comum. A é calculada a partir de Q e K para a entrada corrente. Trocar o texto pode mudar A mesmo que nenhuma matriz aprendida tenha sido atualizada.

**“Por que V não pode ser omitido?”** Os escores dizem quanto cada posição deve contribuir. V fornece o conteúdo efetivamente combinado. O mapa de pesos sozinho não especifica o vetor de saída. Seria possível projetar arquiteturas com restrições particulares sobre V, mas isso não torna seu papel dispensável na operação que estudamos.

**“O encoder entende e o decoder fala?”** Essa frase pode ajudar numa primeira aproximação, desde que seja refinada: o encoder calcula representações contextuais, e o decoder calcula estados condicionados às entradas permitidas. Uma cabeça de saída usa esses estados para prever tokens. Os verbos humanos não substituem a descrição das operações.

**“Se o decoder consulta toda a fonte, por que isso não é olhar o futuro?”** A restrição de futuro se refere ao alvo que está sendo gerado. A fonte completa já é uma entrada conhecida nessa tarefa. O cenário mudaria se a fonte ainda estivesse chegando em tempo real; esse não é o cenário do exemplo.

**“Atenção é tudo que existe no Transformer?”** Não. O modelo também usa embeddings, informação posicional, FFN, residuais, normalização e uma cabeça apropriada à tarefa. O nome do artigo não significa que essas outras operações tenham sido eliminadas.

**“O modelo altera seus parâmetros enquanto respondo a ele?”** No laço comum de inferência descrito aqui, não. O prefixo e o cache mudam, mas isso é estado de execução. Atualizar parâmetros requer um processo de aprendizagem, com um objetivo e um procedimento de ajuste.

## Referências e apoio à preparação

**Modelo de estilo.** `roteiro-de-fala-aula06.pdf`, já presente nesta pasta: referência para a linguagem docente, as falas em primeira pessoa e o detalhamento conceitual. Este novo roteiro corresponde às 20 etapas do artefato interativo, não aos 23 slides do material de referência.

**Fonte operacional.** `transformer-arquitetura-interativa.html`: nomes dos controles, estados iniciais, sequência de navegação e contas de cada experiência. Para consultar apenas os desenhos padrão, use `transformer-arquitetura-interativa.pdf`. Para a aula inteira no quadro, use `aula-quadro-branco.md` e seu PDF.

**Arquitetura original.** Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762), especialmente seções 3.1–3.5. Há uma cópia local em `Attention-is-all-you-need.pdf`. Fundamenta o caminho encoder–decoder, atenção escalada, múltiplas cabeças, FFN, posição e projeção de saída.

**Normalização.** Ba, Kiros e Hinton, [Layer Normalization](https://arxiv.org/abs/1607.06450), para a operação sobre os componentes de cada exemplo; Xiong et al., [On Layer Normalization in the Transformer Architecture](https://arxiv.org/abs/2002.04745), para a comparação pré-norm/pós-norm e suas implicações de otimização.

**Execução da atenção.** Dao et al., [FlashAttention](https://arxiv.org/abs/2205.14135), para a ressalva sobre atenção exata sem materializar a matriz completa na memória principal da GPU.

Os exemplos pequenos foram escolhidos para exposição e conferidos contra os resultados do artefato. Não são medições de um Transformer treinado. As referências são apoio ao professor e não precisam ser lidas em voz alta.
