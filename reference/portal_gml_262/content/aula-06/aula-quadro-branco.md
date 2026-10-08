# Aula 06 — A arquitetura dos Transformers no quadro branco

**Roteiro do professor · Graduação em Ciência da Computação · 120 minutos, incluindo intervalo de 10 minutos.**

Uma aula para construir a arquitetura junto com a turma: do vetor de um token à distribuição do próximo token. As falas abaixo são sugestões prontas para uso; os blocos monoespaçados são o conteúdo a copiar no quadro. Os desenhos são esquemas autorais, deliberadamente simples de reproduzir à mão. Não é necessário projetor, computador ou execução de código em sala.

## Preparação e uso do quadro

**Conhecimentos de entrada.** Vetores, produto escalar, multiplicação de matrizes e noção de função. Retome embeddings e RNNs das aulas anteriores. Não pressuponha que os alunos conheçam softmax, normalização, perda ou gradiente: as definições entram no roteiro.

**Ao final, a turma deverá conseguir:** acompanhar as dimensões de uma cabeça; calcular uma linha da atenção; explicar a máscara causal; montar um bloco com atenção, residual, normalização e FFN; distinguir encoder, decoder e decoder-only; e explicar por que treino e geração têm paralelismos diferentes.

**Materiais.** Canetas preta, azul, verde e vermelha, apagador e este roteiro impresso. Se houver uma única cor, use os rótulos Q/K/V e tracejado para conexões bloqueadas. Reserve calculadora apenas para conferir exponenciais; os valores necessários já estão fornecidos.

**Divida o quadro em três áreas.** Na esquerda, mantenha a legenda e o mapa geral; no centro, desenvolva a conta ou desenho atual; à direita, guarde a conclusão e a pergunta. Não copie parágrafos das falas. Escreva os rótulos e fórmulas progressivamente, enquanto explica cada passo.

```text
┌────────────────┬────────────────────────────────┬──────────────────┐
│ ÂNCORA — 20%   │ DESENVOLVIMENTO — 60%          │ SÍNTESE — 20%    │
│ n = tokens     │ Desenho ou cálculo da etapa    │ Uma ideia        │
│ d = largura    │                                │ Uma pergunta     │
│ h = cabeças    │ Apagar entre etapas indicadas  │                  │
│ L = blocos     │                                │                  │
└────────────────┴────────────────────────────────┴──────────────────┘
```

**Convenções que evitam confusões.** Cada token ocupa uma **linha**. O lote fica omitido. `d = d_model`; `d_k` é a largura de Q e K de uma cabeça; `d_v` é a largura de V. `V` em maiúsculo é a matriz de valores; `N_vocab` é o tamanho do vocabulário. Usaremos índices de tokens a partir de 1. As matrizes W são parâmetros aprendidos; X, Q, K, V e os pesos de atenção são calculados para cada entrada. Ignoramos dropout nas contas e desenhos; ele reaparece nas notas de preparação.

**Escolha didática.** O primeiro bloco completo será o encoder com pós-normalização do Transformer original. Depois mostraremos, com rótulo explícito, um decoder-only com pré-normalização. Assim, o aluno não mistura duas ordens distintas. A posição entra já no início para que a arquitetura esteja completa. RoPE, RMSNorm e análise aprofundada da normalização continuam como aprofundamento da aula 07.

## Percurso e tempo

| Etapa | Relógio | Minutos | Resultado no quadro |
|---|---|---|---|
| 1. Problema e mapa | 00–07 | 7 | Da sequência à previsão |
| 2. Tokens e embeddings | 07–15 | 8 | X tem n linhas e d colunas |
| 3. Informação de posição | 15–22 | 7 | Conteúdo + posição |
| 4. Q, K e V | 22–32 | 10 | Três projeções, duas funções |
| 5. Atenção calculada | 32–42 | 10 | Escores → pesos → mistura |
| 6. Máscara causal | 42–52 | 10 | Futuro bloqueado antes do softmax |
| 7. Escala | 52–55 | 3 | Por que dividir por √d_k |
| Intervalo | 55–65 | 10 | Preserve a fórmula e a máscara |
| 8. Múltiplas cabeças | 65–73 | 8 | Concatenar e projetar |
| 9. Bloco completo | 73–84 | 11 | Atenção + residual + norma + FFN |
| 10. Encoder–decoder | 84–93 | 9 | Onde entra a cross-attention |
| 11. Decoder-only, treino e geração | 93–101 | 8 | Estados → logits → próximo token |
| 12. Custo e cache | 101–107 | 6 | Contexto maior custa mais |
| 13. Exercício com correção | 107–115 | 8 | Reconstrução e diagnóstico |
| 14. Fechamento | 115–120 | 5 | Arquitetura reconstruída pela turma |

O tempo de cada etapa inclui escrita, fala e interação. Não leia todo o material de apoio durante a aula. Para dividir a exposição em dois encontros de 60 minutos, faça as etapas 1–7 e reserve os 5 minutos finais do primeiro encontro para dúvidas; no segundo, retome a fórmula por 5 minutos e siga as etapas 8–14. Essa divisão substitui o intervalo do encontro único. Para aprofundar todas as contas, use o percurso de 180 minutos do apêndice D.

## Etapa 1 — Qual problema o Transformer resolve? · 00–07

**Objetivo.** Dar uma finalidade à arquitetura antes de apresentar suas peças.

**Escreva no quadro, nesta ordem.**

```text
1. “O banco aprovou o empréstimo.”
2. “Sentou no banco da praça.”

embedding inicial de “banco” → depende do ID do token
representação contextual    → depende também dos outros tokens

texto → tokens → vetores + posição → [blocos] → previsão
```

**Fala sugerida.** “As duas frases contêm banco. Se o token for o mesmo, a consulta à tabela de embeddings devolve o mesmo vetor. Mas o papel desse token nas duas frases é diferente. Queremos uma função que produza um vetor considerando o contexto. O modelo não recebe uma etiqueta dizendo qual sentido usar: ele aprende transformações que ajudam a resolver sua tarefa.”

“Uma RNN também incorpora contexto. Sua atualização carrega informação de um passo para o seguinte. A novidade que vamos estudar é uma forma de uma posição consultar diretamente outras posições permitidas. O Transformer organiza essa consulta em camadas, junto com outras transformações. Atenção é uma peça fundamental; ainda faltam peças para formar a arquitetura.”

“Ao final, vocês deverão conseguir explicar o caminho entre uma sequência de IDs e uma distribuição de probabilidades. Nosso trabalho será abrir a caixa chamada blocos, sem perder a visão do sistema inteiro.”

**Desenhe.** Abaixo das frases, faça cinco círculos em linha para uma RNN, unidos da esquerda para a direita. Em uma segunda linha, faça cinco círculos e ligue uma posição diretamente a duas outras. Rotule “caminho sequencial” e “consulta direta”. Não desenhe todas as ligações: duas bastam para comunicar a ideia.

**Pergunte e aguarde 20 segundos.** “Qual palavra em cada frase ajuda a escolher o sentido de banco?” Resposta esperada: empréstimo/aprovou; sentou/praça. Retome: “Essas palavras precisam ter uma rota até a representação de banco.”

**Gestão do quadro.** Preserve o mapa geral na esquerda. Apague as frases depois da discussão; serão substituídas pela pequena sequência numérica.

## Etapa 2 — Do texto à matriz de entrada · 07–15

**Objetivo.** Separar tokenização, consulta de embeddings e processamento contextual.

**Escreva.** Os IDs são inventados; uma palavra por token é uma simplificação deste exemplo.

```text
“Eu estudo IA” → [Eu, estudo, IA] → [17, 42, 9]

E: tabela aprendida, tamanho N_vocab × d
e_1 = E[17]    e_2 = E[42]    e_3 = E[9]

               componentes
              1   2   3   4
Eu           [·   ·   ·   ·]
estudo       [·   ·   ·   ·]   E[IDs]: 3 × 4
IA           [·   ·   ·   ·]

n = 3 tokens; d = 4 componentes por token
```

**Fala sugerida.** “O tokenizador converte texto em IDs. Um ID é um índice, não uma medida: 42 não é semanticamente maior que 17. Dependendo do tokenizador, uma palavra pode virar mais de um token, e espaços ou pontuação podem participar da segmentação. Aqui escolhi três tokens para conseguirmos desenhar tudo.”

“A tabela E guarda um vetor por item do vocabulário. A consulta pega três linhas. Agora temos uma matriz: cada linha é uma posição da sequência e cada coluna é um componente do vetor. O número de linhas acompanha o comprimento do texto. A largura d é uma escolha da arquitetura.”

“Os componentes não vêm com rótulos humanos obrigatórios, como dinheiro, pessoa ou verbo. São coordenadas aprendidas para ajudar a tarefa. E a consulta ao embedding ainda não trocou informação entre tokens. Essa troca acontecerá na atenção.”

**Desenhe.** Uma tabela alta E à esquerda e três setas saindo das linhas 17, 42 e 9 para as três linhas da matriz à direita. Use a mesma cor para cada linha de origem e destino.

**Checagem.** “Se o texto tiver 20 tokens e d continuar 4, qual será o tamanho da matriz?” Resposta: `20 × 4`; a tabela E mantém seu tamanho.

**Gestão do quadro.** Mantenha a matriz 3 × 4 no centro. Escreva `n × d` na legenda fixa.

## Etapa 3 — Como a ordem entra no cálculo? · 15–22

**Objetivo.** Mostrar por que a arquitetura precisa de informação de posição.

**Escreva e desenhe.**

```text
“Ana viu Bia”     ≠     “Bia viu Ana”

vetor do token           vetor da posição
e_i = [· · · ·]    +     p_i = [· · · ·]
                   ↓
                 x_i

X = E[IDs] + P             X: n × d

sem posição e sem máscara:
Attention(ΠX) = Π Attention(X)
Π apenas reordena as linhas
```

**Fala sugerida.** “As duas frases têm os mesmos tokens, mas a ordem muda quem viu quem. Se a atenção só compara conteúdo, sem posição e sem máscara, reordenar a entrada reordena a saída correspondente. Ela não ganha, por mágica, uma marca indicando quem veio primeiro. Isso se chama equivariância a permutação: a saída acompanha a troca das linhas.”

“Uma solução é somar, a cada embedding, um vetor que identifica sua posição. As duas parcelas têm a mesma largura. Na posição 1 somamos p_1; na 2, p_2. Não estamos concatenando: o resultado continua com d componentes. A atenção poderá usar informação de conteúdo e de posição nas suas projeções.”

“Para o nosso caminho principal, vamos usar a soma como modelo didático. O Transformer original usou um desenho senoidal e escalou o embedding antes da soma. Também é possível aprender os vetores de posição. Há outras estratégias: em RoPE, a posição modifica Q e K por rotações. A aula seguinte aprofunda essas alternativas.”

**Nota para dizer se perguntarem sobre a máscara.** “A máscara causal já introduz uma assimetria de ordem: cada posição tem um conjunto diferente de acessos permitidos. Por isso a equação de permutação acima não se aplica diretamente quando mantemos essa máscara fixa. Mesmo assim, adotaremos informação posicional explícita; máscara e posição têm funções diferentes.”

**Checagem.** “Se eu somar dois vetores de tamanho 4, obtenho tamanho 4 ou 8?” Resposta: 4. “O que torna diferentes duas ocorrências do mesmo token em posições diferentes?” A parcela posicional já pode fazê-lo antes da atenção.

**Gestão do quadro.** Acrescente `+ posição` ao mapa da esquerda. Apague a fórmula de permutação após explicá-la; preserve `X: n × d`.

## Etapa 4 — Q, K e V: comparar e transportar conteúdo · 22–32

**Objetivo.** Construir as três projeções e distinguir os parâmetros das ativações.

**Escreva aos poucos.**

```text
                     W_Q → Q: consultas    n × d_k
X: n × d  ────────── W_K → K: chaves       n × d_k
                     W_V → V: valores     n × d_v

Q = XW_Q       W_Q: d × d_k
K = XW_K       W_K: d × d_k
V = XW_V       W_V: d × d_v

consulta i compara com chave j:  q_i · k_j
conteúdo recebido de j:          v_j
```

**Fala sugerida.** “Cada linha de X vai produzir três vetores. Consulta e chave serão usados para calcular compatibilidade. Valor é o conteúdo que será combinado depois. Uma comparação pode dizer de onde buscar informação, mas ainda precisamos decidir qual informação transportar.”

“Imaginem uma consulta a registros: a consulta expressa um critério, a chave oferece algo comparável e o valor fornece o conteúdo recuperado. Aqui não há uma busca exata de banco de dados. São vetores e produtos escalares, com recuperação suave: várias posições podem contribuir ao mesmo tempo.”

“As três matrizes W são diferentes e aprendidas. Na self-attention, elas recebem a mesma X. Isso não torna Q, K e V iguais. É como executar três funções diferentes sobre o mesmo registro. Em outra camada, X já será uma representação contextual produzida pela camada anterior.”

“Essas projeções são aplicadas da mesma maneira a todas as posições: não criamos uma W específica para o primeiro token. Os parâmetros são compartilhados entre posições dentro dessa camada e dessa cabeça. Em geral, camadas diferentes têm parâmetros diferentes.”

**Desenhe.** Três setas partindo do mesmo retângulo X. Use azul para Q, verde para K e preto para V. Abaixo, faça uma seta pontilhada entre q_i e k_j com o rótulo “escore”; uma seta sólida saindo de v_j terá o rótulo “conteúdo”.

**Pequena conta no quadro.** `X: 3 × 4`, `W_Q: 4 × 2`, portanto `Q: 3 × 2`. Peça que a turma explique por que a dimensão 4 desaparece na multiplicação e a dimensão 3 permanece.

**Checagem.** “W_Q muda quando eu troco a frase durante uma inferência comum?” Não. “Q muda?” Sim, porque X mudou. Os pesos de atenção também mudam com a entrada; não são uma tabela fixa de parâmetros.

**Gestão do quadro.** Preserve o desenho de três ramos. Reserve abaixo dele espaço para a conta da etapa 5.

## Etapa 5 — Uma cabeça de atenção, calculada à mão · 32–42

**Objetivo.** Entender a fórmula como uma sequência de operações verificáveis.

**Escreva a fórmula em quatro partes.**

```text
S = QKᵀ / √d_k        escores: n × n
A = softmax_linha(S)  pesos:   n × n
Z = AV                saída:  n × d_v

a_ij = exp(s_ij) / Σ_r exp(s_ir)
z_i = Σ_j a_ij v_j

LINHA i = quem consulta; COLUNA j = quem é consultado
```

**Fala sugerida.** “Uma consulta será comparada com todas as chaves permitidas. Em S, a célula da linha i e coluna j mede a compatibilidade entre a consulta i e a chave j. O softmax atua separadamente em cada linha. Ele transforma escores em pesos positivos que somam um. Não somamos a matriz inteira.”

“O produto AV faz uma soma ponderada de vetores. Cada componente da saída usa os mesmos pesos daquela linha. Para uma cabeça antes de dropout e da projeção de saída, essa operação é uma combinação convexa dos valores. Isso não significa que o bloco inteiro seja apenas uma média: ainda haverá projeções, residual e transformações não lineares.”

**Exemplo único para esta aula.** Os números são construídos para facilitar a conta, sem pretensão de representar significados linguísticos ou um modelo treinado. São projeções já prontas; o apêndice A mostra uma X e matrizes W capazes de produzi-las.

```text
tokens: t1 = Eu, t2 = estudo, t3 = IA
d_k = d_v = 2

Q = [1 0]       K = [0   0]       V = [2 0]
    [0 1]           [√2  0]           [0 2]
    [1 1]           [0  √2]           [2 2]

                    colunas: t1 t2 t3
S = QKᵀ / √2 =     t1 [ 0  1  0 ]
                    t2 [ 0  0  1 ]
                    t3 [ 0  1  1 ]
```

**Faça uma multiplicação antes de mostrar S inteira.** `q_2 · k_3 = (0,1) · (0,√2) = √2`; depois da divisão por `√2`, `s_23 = 1`.

**Continue pela linha 2.**

```text
s_2 = [0, 0, 1]          exp(s_2) = [1, 1, e]
e ≈ 2,718                soma ≈ 4,718
a_2 ≈ [0,212, 0,212, 0,576]

z_2 ≈ 0,212[2,0] + 0,212[0,2] + 0,576[2,2]
    ≈ [1,576; 1,576]
```

**Fala durante a conta.** “A posição estudo consulta três posições. Neste exemplo artificial, o maior peso foi para IA. Não estamos declarando que toda cabeça real deva fazer isso. Estamos verificando como um padrão de escores vira uma mistura. Observem que o resultado é um vetor de dois componentes, não uma palavra e não uma probabilidade sobre o vocabulário.”

**Visualização para copiar.** Faça uma grade 3 × 3. Preencha a linha 2 com `0,212 | 0,212 | 0,576`; hachure a última célula mais forte. Ao lado, desenhe três setas saindo das linhas de V e convergindo para z_2, com espessura proporcional aos pesos. O mapa A descreve pesos, mas a saída também depende de V.

**Checagem.** “A matriz de escores precisa ser simétrica?” Não: Q e K usam projeções diferentes; neste exemplo, `s_12 = 1` e `s_21 = 0`. “Por que a saída tem dois componentes?” Porque `d_v = 2`.

**Gestão do quadro.** Preserve S, V e a linha a_2. A próxima etapa usa exatamente os mesmos números.

## Etapa 6 — A máscara causal bloqueia o futuro · 42–52

**Objetivo.** Ligar a máscara à tarefa de prever o próximo token e evitar vazamento.

**Comece pelo alinhamento.**

```text
posição           1          2          3
entrada          Eu        estudo       IA
alvo            estudo       IA        <fim>

saída da posição i prevê o token i+1
pode consultar j ≤ i; não pode consultar j > i
```

**Fala sugerida.** “Durante o treinamento, a frase inteira está disponível no computador. Mas a previsão feita na posição 2 não pode consultar IA na posição 3: IA é justamente o alvo que queremos prever. Permitir essa consulta ensina a usar uma informação que não estará disponível quando o modelo precisar gerar a continuação.”

“A diagonal é permitida. A posição 2 pode usar estudo, porque estudo já foi fornecido. O deslocamento dos alvos é essencial: estar na diagonal da entrada não significa estar lendo o próximo token.”

**Escreva a máscara e aplique-a antes do softmax.**

```text
M = [0  -∞  -∞]      S + M = [0  -∞  -∞]
    [0   0  -∞]              [0   0  -∞]
    [0   0   0]              [0   1   1]

A_causal = softmax_linha(S + M)

A_causal ≈ [1,000  0,000  0,000]
           [0,500  0,500  0,000]
           [0,155  0,422  0,422]

z_2 causal = 0,5[2,0] + 0,5[0,2] = [1,1]
```

**Fala durante o desenho.** “O zero da máscara significa não alterar o escore. O menos infinito significa proibir. Não é uma matriz multiplicativa. Depois da exponencial, a posição bloqueada contribui zero. Na linha 2 sobram dois escores iguais, então cada um recebe metade do peso. A linha 3 ainda pode consultar todas as três posições.”

“Se eu apenas trocar um escore proibido por zero, ele continua produzindo exp(0) = 1 e continua participando da soma. Se eu aplicar o softmax e só depois apagar os pesos futuros, a linha deixa de somar um e o denominador já usou o futuro. A operação que acabamos de escrever evita esses dois problemas.”

**Visualização.** Risque de vermelho o triângulo acima da diagonal da grade. Rotule os dois eixos: “consulta” na vertical e “chave” na horizontal. No navegador, a visualização interativa permite alternar essa máscara usando as mesmas matrizes da etapa 5.

**Checagem prática.** “Se eu mudar só o terceiro token, as saídas das posições 1 e 2 de uma pilha causal devem mudar?” Não, mantendo parâmetros, posições e demais entradas fixos, com dropout desativado. A propriedade deve valer em todas as camadas. Esse é um teste de vazamento; uma perda baixa, sozinha, não prova o defeito.

**Gestão do quadro.** Enquadre a fórmula `softmax(QKᵀ/√d_k + M)V`. Preserve-a e preserve a máscara durante o intervalo.

## Etapa 7 — Por que dividir por √d_k? · 52–55

**Objetivo.** Explicar a escala sem interromper a construção da arquitetura.

**Escreva.**

```text
softmax([1,0])  ≈ [0,731; 0,269]
softmax([10,0]) ≈ [0,99995; 0,00005]

hipótese didática: componentes independentes, média 0, variância 1
Var(q·k) = d_k       desvio-padrão = √d_k
Var((q·k)/√d_k) = 1
```

**Fala sugerida.** “O produto escalar soma muitas parcelas. Sob estas hipóteses simplificadas, sua dispersão cresce com a raiz da dimensão. Escores muito separados podem concentrar o softmax perto de zero e um. Nessa região, pequenos ajustes nos escores podem mudar muito pouco os pesos, dificultando a passagem do sinal de aprendizado por esse caminho.”

“Dividir pela raiz da largura da chave compensa esse crescimento no exemplo estatístico. Isso não normaliza o comprimento de q e k e não transforma o produto em similaridade cosseno. A largura usada é a de cada cabeça, d_k, não o número de tokens.”

**Checagem rápida.** “Com d_k = 64, dividimos por quanto?” Oito. Encerre com: “Já sabemos produzir uma mistura contextual. Depois do intervalo, vamos encaixá-la no bloco e construir o modelo inteiro.”

**Gestão do quadro.** Ao fim do intervalo, apague os números das contas, conservando a fórmula geral, as dimensões e a máscara.

## Etapa 8 — Várias cabeças, várias consultas aprendidas · 65–73

**Objetivo.** Entender concatenação, projeção de saída e preservação da largura.

**Retomada de 30 segundos.** Aponte cada parte da fórmula e peça que três alunos digam: “comparar”, “normalizar”, “combinar valores”.

**Escreva e desenhe.**

```text
                    cabeça 1 → Z_1: n × 2
X: n × 4 ─────────<
                    cabeça 2 → Z_2: n × 2
                                  ↓
                  concatenar [Z_1 | Z_2]: n × 4
                                  ↓ W_O: 4 × 4
                         MHA(X): n × 4

Z_r = softmax((XW_Qr)(XW_Kr)ᵀ/√d_k + M)(XW_Vr)
MHA(X) = Concat(Z_1,...,Z_h) W_O
```

**Fala sugerida.** “Uma cabeça produz um conjunto de pesos por consulta. Duas cabeças podem produzir padrões diferentes, porque usam projeções diferentes. As duas recebem toda a largura de X. Não entregamos a primeira metade da frase para uma e a segunda metade para outra.”

“Ao concatenar, colocamos os componentes lado a lado. Não somamos as duas saídas. A projeção W_O mistura os componentes concatenados e devolve a largura d_model. Essa largura permitirá somar a saída com a entrada numa conexão residual.”

“É possível que cabeças aprendam padrões relacionados a sintaxe, posição ou outras regularidades. Mas não programamos uma cabeça de sujeito e outra de verbo, nem garantimos esses papéis. Um mapa de pesos sozinho não mostra toda a contribuição causal de uma cabeça.”

**Amplie para uma configuração usual.** `d_model = 512`, `h = 8`, `d_k = d_v = 64`. Cada cabeça tem `n × 64`; a concatenação tem `n × 512`; W_O tem `512 × 512`. Explique que essa divisão é uma escolha comum da atenção multi-head padrão, não a definição de toda variante possível.

**Checagem.** “Dobrar h mantendo d fixo exige dobrar a largura final?” Não; na divisão usual, a largura por cabeça diminui. “As cabeças precisam ter os mesmos pesos de atenção?” Não.

**Gestão do quadro.** Substitua os ramos pela caixa “Multi-head attention”. Ela será a primeira peça do bloco seguinte.

## Etapa 9 — Atenção dentro de um bloco completo · 73–84

**Objetivo.** Dar uma função concreta a residual, LayerNorm e feed-forward.

**Desenho principal: encoder com pós-normalização.** Leia de cima para baixo. Desenhe primeiro o caminho vertical e só depois as duas setas laterais de soma.

```text
X: n × d ───────────────┐
       ↓               │
self-attention         │
       ↓               │
       + ←─────────────┘
       ↓
   LayerNorm
       ↓
U: n × d ───────────────┐
       ↓               │
      FFN              │
       ↓               │
       + ←─────────────┘
       ↓
   LayerNorm
       ↓
Y: n × d

U = LN(X + MHA(X))
Y = LN(U + FFN(U))
```

**Fala sobre residual — cerca de 2 minutos.** “Na seta lateral, a entrada chega à soma sem passar pela transformação central. A rede pode aprender uma atualização sobre uma representação que já existe. Se a transformação produzir algo próximo de zero, a soma fica próxima da entrada, antes da normalização. Isso também cria uma rota direta para o gradiente, que é o sinal usado para ajustar os parâmetros. Não é uma garantia de treino perfeito, mas ajuda a construir redes profundas.”

**Escreva ao lado da soma.** `entrada + atualização`; as duas parcelas precisam ter a mesma forma `n × d`.

**Fala sobre LayerNorm — cerca de 3 minutos.** “A normalização atua nos componentes de cada token separadamente. Para uma linha, calculamos média e variância dos seus d componentes; centralizamos, ajustamos a escala e aplicamos ganho e deslocamento aprendidos. Não estamos calculando estatísticas entre frases do lote e não estamos fazendo a média entre tokens.”

```text
para uma linha x = [x_1,...,x_d]:
μ = média dos componentes      σ² = média de (x_r − μ)²
LN(x)_r = γ_r (x_r − μ)/√(σ² + ε) + β_r

x = [1,3] → μ = 2, σ² = 1 → aproximadamente [-1,1]
exemplo: γ = [1,1], β = [0,0], ε pequeno
```

**Fala sobre FFN — cerca de 3 minutos.** “A atenção combina informação entre posições. A rede feed-forward transforma os componentes de cada posição. Ela aplica a mesma função a cada linha, sem buscar diretamente outra linha nessa subcamada. Como a atenção já incorporou contexto, esse processamento local atua sobre uma representação contextual.”

```text
FFN(u) = ReLU(uW_1 + b_1) W_2 + b_2
ReLU(a) = max(0,a), componente a componente

uma linha:       d → d_ff → d
exemplo:       512 → 2048 → 512
W_1: d × d_ff          W_2: d_ff × d
```

“A expansão permite trabalhar em um espaço intermediário maior. A não linearidade é indispensável para que duas transformações lineares não se reduzam a uma única transformação afim. ReLU é a escolha do Transformer original; outras arquiteturas usam outras ativações ou portas.”

**Amarre o bloco — cerca de 3 minutos, incluindo escrita.** “Esse conjunto é repetido L vezes. A forma n × d permanece, mas o conteúdo muda. Repetir o desenho do bloco não significa reutilizar os mesmos parâmetros: em geral, cada bloco aprende suas próprias matrizes. A atenção mistura posições, a FFN transforma cada posição, e residual e normalização organizam o fluxo de representações e o treinamento.”

**Checagem.** “A FFN da linha 2 usa diretamente a linha 3?” Não. Pode usar informação que já chegou da linha 3 na atenção, se essa consulta era permitida. “LayerNorm substitui o softmax?” Não; normalizam objetos e eixos distintos.

**Gestão do quadro.** Envolva o desenho com uma moldura rotulada “bloco encoder — pós-norm”. Preserve-a para a etapa 10.

## Etapa 10 — Transformer original: encoder e decoder · 84–93

**Objetivo.** Localizar os três usos de atenção numa tarefa de transformação de sequência.

**Escreva uma tradução ilustrativa.** `fonte: “Eu estudo IA” → alvo: “I study AI”`. A segmentação por palavras continua sendo didática.

**Desenhe duas colunas.** Em cada subcamada abaixo, “Add & Norm” significa somar a entrada da subcamada à sua saída e depois aplicar LayerNorm. Mostre uma seta residual em detalhe e use o rótulo nas demais para caber no quadro.

```text
ENCODER                               DECODER
tokens da fonte                       tokens do alvo deslocados
Eu | estudo | IA                      <início> | I | study
       ↓                                      ↓
embedding + posição                   embedding + posição
       ↓                                      ↓
┌─ repetir L_e vezes ─────┐            ┌─ repetir L_d vezes ──────┐
│ self-attention         │            │ self-attention causal    │
│ Add & Norm             │            │ Add & Norm               │
│                        │            │       ↓ D                │
│ FFN                    │            │ cross-attention          │
│ Add & Norm             │            │ Add & Norm               │
└────────────────────────┘            │ FFN                      │
       ↓ H_enc                        │ Add & Norm               │
       └───────── K,V ───────────────→ └──────────────────────────┘
                                              ↓
                                      linear → softmax_vocab
                                      I | study | AI

cross-attention:
Q = D W_Q      K = H_enc W_K      V = H_enc W_V
```

**Fala sugerida.** “O encoder recebe toda a sequência fonte disponível. Sua self-attention permite consultar as posições válidas dessa sequência nos dois sentidos. O resultado é uma matriz de representações, uma por posição da fonte. Não precisamos comprimir tudo em um único vetor.”

“O decoder primeiro consulta o prefixo do alvo com máscara causal. Depois usa uma segunda atenção para consultar a fonte codificada. Essa é a cross-attention: Q vem do estado corrente do decoder; K e V vêm da saída final do encoder. Cada subcamada de cross-attention tem suas projeções aprendidas.”

“Consultar toda a fonte não é vazar o futuro do alvo. Numa tradução com a fonte inteira disponível, a frase de entrada já é conhecida. O que não pode estar disponível é a próxima palavra da tradução que estamos tentando prever. Também mascaramos posições de padding para que preenchimento não vire conteúdo.”

**Escreva as dimensões da cross-attention.** Se a fonte tiver `n` tokens e o alvo deslocado tiver `m`, então `Q: m × d_k`, `K: n × d_k`, `V: n × d_v`; o mapa tem `m × n` e a saída `m × d_v`.

**Checagem.** “Qual mecanismo usa duas sequências diferentes?” Cross-attention. “A máscara causal triangular m × m deve bloquear a fonte?” Não. Na fonte, o caso usual desta aula usa máscara de padding; restrições adicionais dependeriam da tarefa.

**Gestão do quadro.** Faça uma foto mental com a turma: três caixas de atenção, três papéis. Preserve os rótulos encoder e decoder; simplifique o restante para abrir espaço ao decoder-only.

## Etapa 11 — Decoder-only: do prefixo ao próximo token · 93–101

**Objetivo.** Fechar o caminho entrada–saída e separar treinamento de geração.

**Desenhe a variante com pré-normalização, identificada explicitamente.**

```text
tokens → embedding + posição → X
                               ↓
                   ┌─ repetir L vezes ─────────────┐
                   │ U = X + MHA_causal(LN(X))     │
                   │ Y = U + FFN(LN(U))            │
                   │ próxima camada recebe Y      │
                   └───────────────────────────────┘
                               ↓
                         LayerNorm final
                               ↓ H: n × d
                         logits = H W_vocab + b
                               ↓ n × N_vocab
                         softmax no vocabulário

W_vocab: d × N_vocab
```

**Fala sugerida.** “Aqui temos um modelo de linguagem que usa apenas a pilha causal. Não existe encoder separado nem a cross-attention que consultaria esse encoder. O prompt entra na mesma sequência em que a continuação será produzida.”

“Também mudei uma escolha do bloco, indicada nas equações: a normalização agora ocorre antes de cada transformação, e há uma normalização final. Isso é pré-normalização. O diagrama anterior tinha pós-normalização. Não são duas maneiras de desenhar uma ordem idêntica; são variantes. A versão aqui usa LayerNorm e posição somada para manter as peças que já estudamos. Nem todo LLM usa exatamente essas escolhas.”

“O estado de cada posição tem d componentes. A projeção final produz um escore, chamado logit, para cada item do vocabulário. Agora o softmax normaliza sobre N_vocab possibilidades. Este é outro eixo e outra finalidade em relação ao softmax da atenção, que distribuiu peso entre posições de contexto.”

**Escreva treino e geração lado a lado.**

```text
TREINO, sequência conhecida         GERAÇÃO, continuação desconhecida
entrada: Eu | estudo | IA           Eu → prever → estudo
alvos: estudo | IA | <fim>          Eu estudo → prever → IA
                                   Eu estudo IA → prever → <fim>

loss = média_i [−log p(alvo_i | prefixo até i)]
```

**Fala de fechamento.** “No treinamento, calculamos previsões para várias posições em paralelo, mantendo a máscara que impede cada posição de consultar seus alvos futuros. A perda compara a distribuição prevista com o token correto, e a retropropagação ajusta os parâmetros. Se a probabilidade do alvo aumenta, menos log dessa probabilidade diminui.”

“Na geração, usamos a distribuição da última posição do prefixo para escolher um token, por máximo ou por amostragem. Acrescentamos esse token à sequência e repetimos. Dentro de um passo há muito cálculo paralelo; os passos de geração desta sequência têm uma dependência temporal. Normalmente, os parâmetros ficam fixos durante esse processo.”

**Checagem.** “Treinar em paralelo significa gerar toda uma continuação em uma única passagem autorregressiva comum?” Não. “Qual softmax gera probabilidades de palavras ou subpalavras?” O da saída sobre o vocabulário.

## Etapa 12 — Custo da atenção e KV cache · 101–107

**Objetivo.** Relacionar a arquitetura à memória e à execução.

**Escreva.**

```text
por cabeça, por sequência: A tem n × n entradas
n = 2.000 →  4.000.000 entradas →  8 MB a 2 bytes/entrada
n = 4.000 → 16.000.000 entradas → 32 MB a 2 bytes/entrada
dobrar n → quadruplicar esta matriz

atenção densa, somando cabeças usuais: O(n² d)
projeções: O(n d²)       FFN: O(n d d_ff)
```

**Fala sugerida.** “Esses megabytes são decimais e descrevem uma única matriz, com um tipo numérico de dois bytes. Não são a memória total do modelo. O lote, as cabeças, as camadas, outras ativações, os parâmetros e o otimizador acrescentam custos. O custo quadrático também não significa que a atenção será sempre a maior parcela do tempo: largura, contexto e implementação importam.”

“Algoritmos como FlashAttention calculam atenção exata em blocos sem armazenar a matriz n × n completa na memória principal da GPU. Assim, a conta que fizemos descreve a implementação que materializa a matriz, não uma obrigação de toda implementação. A atenção densa continua envolvendo interações entre pares de posições.”

**Desenhe o cache.**

```text
passo anterior, em cada camada: [K_1 ... K_t] e [V_1 ... V_t]
novo token: calcular q_novo, k_novo, v_novo
                  ↓
guardar k_novo e v_novo no cache
q_novo consulta chaves/valores acumulados
                  ↓
estado do novo token → distribuição do próximo
```

**Fala sugerida.** “Na pilha causal, acrescentar um token não altera os estados dos tokens antigos: eles não podem olhar para o futuro. Podemos reutilizar suas chaves e valores em cada camada. O cache evita recomputá-los a cada passo, mas ocupa memória e não elimina a consulta ao contexto acumulado. A primeira passagem sobre o prompt é chamada de prefill; os passos seguintes acrescentam tokens.”

**Checagem.** “Dobrar o contexto sempre quadruplica toda a memória da GPU?” Não; quadruplica a matriz de atenção materializada, mantendo os demais fatores fixos. “O cache guarda as matrizes aprendidas W_K e W_V?” Não; guarda K e V calculados para aquele prefixo em cada camada.

## Etapa 13 — Exercício em dupla e correção · 107–115

**Organização.** Cinco minutos para resolver e três para corrigir. Escreva apenas os enunciados; o gabarito fica no roteiro. Os alunos devem justificar as respostas com uma dimensão, uma conta ou uma ligação do diagrama.

**Escreva no quadro.**

```text
1. X: 5 × 12; h = 3; d_k = d_v = 4.
   Formas de W_Q por cabeça, Q, QKᵀ, AV e concatenação?

2. Na posição 2, os escores são [0, 0, 9].
   Com máscara causal, quais são os pesos?

3. Complete o bloco pré-norm:
   U = X + __________
   Y = U + __________
   Qual subcamada mistura posições?

4. Na tradução, Q vem do decoder; K e V vêm do encoder.
   Nome da operação? Por que consultar a fonte não vaza o alvo?
```

**Fala de orientação.** “Não basta escrever que uma dimensão parece correta. Marquem qual eixo representa tokens e qual representa componentes. Na segunda questão, resolvam a máscara antes da exponencial. Na terceira, confiram onde a normalização aparece.”

**Gabarito comentado.**

1. Por cabeça, `W_Q: 12 × 4`; `Q: 5 × 4`; `QKᵀ: 5 × 5`; `AV: 5 × 4`; concatenação das três cabeças: `5 × 12`. W_O pode ser `12 × 12`, produzindo `5 × 12` para somar a X.
2. A posição 3 é futura. Os escores permitidos são `[0,0]`, portanto a linha completa é `[0,5; 0,5; 0]`. O valor 9 bloqueado não pode afetar a resposta.
3. `U = X + MHA_causal(LN(X))`; `Y = U + FFN(LN(U))`. A atenção mistura posições permitidas. A FFN atua linha a linha e mistura componentes.
4. Cross-attention. A fonte completa faz parte da entrada disponível nessa tarefa; os tokens futuros do alvo continuam bloqueados na self-attention do decoder.

**Se houver erro recorrente.** Para `QKᵀ`, escreva `(5 × 4)(4 × 5)`. Para a máscara, volte a `exp(−∞) = 0`. Para pré-norm, siga a seta da entrada e a seta lateral da soma, em vez de decorar a posição das caixas.

**Extensão para dupla que terminar cedo.** Na questão 2, se os valores forem `[2,0]`, `[0,2]`, `[100,100]`, qual será a saída? `[1,1]`: o valor futuro é irrelevante porque seu peso é zero.

## Etapa 14 — Reconstrução final da arquitetura · 115–120

**Apague o centro e peça que a turma dite o desenho.**

```text
IDs → embeddings + posição
                ↓
       [ atenção: consulta contexto ]
       [ residual + normalização    ]  × L
       [ FFN: transforma cada linha ]
       [ residual + normalização    ]
                ↓
     cabeça de saída adequada à tarefa

encoder:          contexto bidirecional
decoder original: contexto causal do alvo + consulta à fonte
decoder-only:     contexto causal → distribuição do próximo token
```

**Nota de condução.** O resumo agrupa funções e não fixa a ordem pré-norm/pós-norm. Escreva “esquema funcional” ao lado. Se a turma pedir a ordem de operações, reconstrua explicitamente um dos blocos das etapas 9 ou 11.

**Fala final sugerida.** “O Transformer recebe vetores organizados por posição. A atenção decide quanto cada posição consulta outras posições, combinando seus valores. Múltiplas cabeças produzem consultas diferentes. A rede feed-forward transforma cada representação; residual e normalização ajudam a organizar uma pilha profunda. A tarefa determina quais consultas são permitidas e como a saída será usada.”

“No modelo de linguagem causal, a saída de uma posição representa uma distribuição para o próximo token. No treino, muitas dessas previsões podem ser calculadas em paralelo. Na geração, cada token escolhido passa a fazer parte do prefixo para o passo seguinte.”

**Bilhete de saída — dois minutos.** Peça três respostas curtas no caderno: “O que Q/K fazem e o que V faz?”, “Por que a máscara entra antes do softmax?” e “Qual a diferença entre softmax da atenção e softmax da saída?”. Respostas esperadas: compatibilidade versus conteúdo; excluir futuro da normalização; distribuição entre posições versus distribuição sobre o vocabulário.

**Ponte para a aula 07.** “Agora temos a arquitetura inteira. Na próxima aula, vamos examinar com mais cuidado como representar posição e como as escolhas de normalização e feed-forward mudam o comportamento do bloco.”

## Apêndice A — Conta completa para consulta do professor

Não é necessário copiar este apêndice inteiro em sala. Ele permite conferir a etapa 5 sem depender de um exemplo que apenas pareça plausível.

Uma entrada e três projeções consistentes com o exemplo são:

```text
X = [1 0 0 0]
    [0 1 0 0]
    [0 0 1 0]

W_Q = [1 0]     W_K = [0  0 ]     W_V = [2 0]
      [0 1]           [√2 0 ]           [0 2]
      [1 1]           [0  √2]           [2 2]
      [0 0]           [0  0 ]           [0 0]
```

X representa a entrada já preparada da subcamada. Estes valores foram escolhidos manualmente; não são embeddings linguísticos aprendidos. Como a multiplicação seleciona as três primeiras linhas de cada W, as projeções produzem exatamente o Q, K e V mostrados na etapa 5.

```text
sem máscara:
A ≈ [0,211942  0,576117  0,211942]
    [0,211942  0,211942  0,576117]
    [0,155362  0,422319  0,422319]

Z = AV ≈ [0,847766  1,576117]
         [1,576117  1,576117]
         [1,155362  1,689275]

com máscara causal:
A ≈ [1,000000  0,000000  0,000000]
    [0,500000  0,500000  0,000000]
    [0,155362  0,422319  0,422319]

Z = AV ≈ [2,000000  0,000000]
         [1,000000  1,000000]
         [1,155362  1,689275]
```

Diferenças na última casa e somas como 0,999 ou 1,001 decorrem do arredondamento exibido. Calcule com precisão interna antes de arredondar.

**Softmax estável.** Para escores finitos de uma linha, subtrair o maior escore não muda os pesos: `softmax(s) = softmax(s − max(s))`. Isso evita exponenciais desnecessariamente grandes. Uma linha sem nenhuma chave permitida exige tratamento próprio; softmax de uma linha inteira em menos infinito não define uma distribuição válida. Na máscara causal deste exemplo, a diagonal garante ao menos uma posição permitida.

## Apêndice B — Respostas para dúvidas comuns

**Por que não usar X diretamente como Q, K e V?** É possível construir uma atenção restrita desse tipo. Projeções diferentes permitem aprender espaços distintos para compatibilidade e conteúdo; múltiplas cabeças ampliam as formas de consulta. Não confunda esse ganho de flexibilidade com uma garantia de desempenho para qualquer escolha de parâmetros.

**A atenção é uma explicação do raciocínio?** O mapa mostra pesos de mistura naquela cabeça e entrada. A influência na saída depende também dos valores, das projeções, de outras cabeças, dos residuais e das camadas seguintes. Não atribua uma causa completa apenas ao maior peso do mapa.

**Softmax é aplicado às colunas ou linhas?** Nesta convenção, cada linha é uma consulta; normalizamos sobre as colunas das chaves. Uma biblioteca pode organizar eixos de forma diferente: confira qual eixo representa as chaves. Para uma implementação padrão com lote, A costuma ter forma `[B,h,n,n]`, com softmax no último eixo.

**LayerNorm deixa toda a matriz com média zero e variância um?** A centralização e escala são feitas por linha, antes do ganho γ e deslocamento β aprendidos; o ε também altera ligeiramente a variância. Não é uma normalização global da sequência.

**Por que pré-norm e pós-norm aparecem em desenhos diferentes?** São variantes de arquitetura. Pós-norm: `LN(X + F(X))`. Pré-norm: `X + F(LN(X))`. A localização afeta o caminho do gradiente e as condições de otimização; pré-norm é uma escolha frequente em modelos profundos. Não conclua que a ausência de uma norma final, isoladamente, sempre causa divergência.

**Onde está dropout?** O Transformer original aplica dropout em pontos como a saída das subcamadas antes da soma residual e a soma de embedding e posição. Omitimos dropout para desenhar o fluxo e fazer contas determinísticas. Com dropout nos pesos de atenção durante o treino, a soma dos pesos realizados não precisa ser exatamente um; a descrição de combinação convexa da etapa 5 é anterior a esse dropout.

**Onde estão os vieses?** Foram omitidos nas projeções Q/K/V para simplificar a notação. A FFN e a cabeça de saída os mostram. Variantes podem incluir ou omitir vieses, sem mudar a lógica de comparar, normalizar e combinar.

**Cada camada aprende uma operação humana específica?** Não existe uma regra que obrigue a primeira camada a aprender palavras, a segunda gramática e a terceira raciocínio. São transformações aprendidas; qualquer interpretação funcional exige evidência.

**O encoder prevê o próximo token?** O bloco encoder produz representações contextuais. A cabeça e o objetivo de treinamento definem o que se prevê. BERT é um exemplo de encoder treinado com um objetivo que inclui prever tokens mascarados; isso difere do objetivo causal descrito aqui.

**Um decoder-only precisa codificar o prompt num encoder separado?** Não. Ele processa prompt e continuação na mesma pilha causal. O nome decoder-only descreve essa família de arquitetura; não implica a presença de um encoder oculto.

**KV cache é memória permanente ou aprendizado?** É estado de execução associado a um prefixo, por camada. Reutilizar esse estado não equivale a atualizar os parâmetros. O cache precisa corresponder ao prefixo, ao modelo e à configuração posicional usados no cálculo.

## Apêndice C — Aprofundamentos matemáticos para o quadro

**Escala, em quatro linhas.** Assuma que todos os componentes envolvidos são independentes, com média zero e variância um. Então cada produto `q_r k_r` tem média zero e variância um. A soma de `d_k` produtos independentes tem variância `d_k`. Dividir a soma por `√d_k` divide sua variância por `d_k`, resultando em um. Essas hipóteses motivam a escala; não descrevem exatamente toda representação aprendida nem toda entrada da diagonal de self-attention.

**Gradiente do softmax.** Para uma linha, `∂a_i/∂s_j = a_i(δ_ij − a_j)`. Se um peso está muito perto de um e os demais muito perto de zero, essas sensibilidades são pequenas. Isso explica a preocupação com escores excessivamente dispersos; não prova que toda atenção concentrada seja inadequada.

**Residual.** Para `y = x + F(x)`, o Jacobiano é `I + J_F(x)`. O termo identidade cria uma rota direta. Na pós-normalização ainda há o Jacobiano da norma após a soma; na pré-normalização a soma mantém esse caminho de identidade no bloco. Evite dizer que o gradiente nunca diminui ou nunca explode.

**Posição senoidal.** Para posição p e índice de par r, `PE(p,2r) = sin(p / 10000^(2r/d))` e `PE(p,2r+1) = cos(p / 10000^(2r/d))`. Cada par usa uma frequência. No original, a entrada é `√d · E[IDs] + PE`. Desenhe duas ondas de frequências diferentes e marque a mesma posição nas duas. Isso ajuda a visualizar a construção; não garante, por si só, bom desempenho além dos comprimentos de treino.

**Parâmetros do bloco simples.** Na divisão usual `h d_k = h d_v = d`, Q/K/V totalizam aproximadamente `3d²` parâmetros e W_O acrescenta `d²`, ignorando vieses. A FFN simples tem aproximadamente `2d d_ff`. Se `d_ff = 4d`, são `8d²` na FFN, contra `4d²` na atenção. Não inclua embeddings, cabeça de saída e normas nessa conta parcial. Mais cabeças com d fixo não multiplicam automaticamente esse total por h.

## Apêndice D — Ajuste de duração e consulta rápida

**Percurso de 180 minutos.** Mantenha a aula principal de 120 minutos e acrescente: 10 minutos para multiplicar X pelas três W do apêndice A; 10 para calcular as outras linhas de A e Z; 10 para derivar escala e softmax; 10 para uma FFN e LayerNorm numéricas; 10 para comparar os caminhos residuais pré-norm/pós-norm; e 10 para reconstruir encoder–decoder em duplas. Total: 180 minutos, incluindo o mesmo intervalo de 10 minutos. Os aprofundamentos entram logo após suas etapas correspondentes.

**Se atrasar.** Preserve o exemplo numérico, a máscara e a montagem do bloco. Transfira a derivação estatística, a fórmula completa da norma e a conta de memória para leitura posterior. Não elimine a distinção entre softmax de atenção e de vocabulário: ela fecha o caminho até a saída.

**Mapa de consulta das visualizações.**

| Visual | Usar na etapa | O que copiar |
|---|---|---|
| 01 — Caminho dos dados | 1–3 | IDs → matriz → posição → blocos → saída |
| 02 — Uma cabeça por dentro | 4–5 | Ramos Q/K/V, escores, pesos e AV |
| 03 — Máscara causal | 6 | Grade com futuro bloqueado |
| 04 — Múltiplas cabeças | 8 | Ramos, concatenação e W_O |
| 05 — Bloco pós-norm e pré-norm | 9 e 11 | Posição das normas e atalhos residuais |
| 06 — Encoder–decoder | 10 | Duas pilhas e origem de Q/K/V |
| 07 — Treino e geração | 11 | Alvos deslocados versus laço de geração |
| 08 — Crescimento do contexto | 12 | Área n² e memória da matriz |

## Referências e ligação com o curso

O roteiro retoma os objetivos de [plano.md](plano.md) e os exemplos de contexto do material existente. A organização para quadro e o exemplo numérico foram preparados especificamente para esta versão. O PDF local [Attention-is-all-you-need.pdf](Attention-is-all-you-need.pdf), especialmente seções 3.1–3.5 e Figura 1, é a referência de preparação para o desenho original.

- [Vaswani et al. — Attention Is All You Need](https://arxiv.org/abs/1706.03762): fonte da arquitetura original; consultar para atenção escalada, múltiplas cabeças, encoder–decoder e posição senoidal.
- [Ba, Kiros e Hinton — Layer Normalization](https://arxiv.org/abs/1607.06450): fundamenta a normalização por exemplo e os parâmetros de ganho e deslocamento usados na etapa 9.
- [Xiong et al. — On Layer Normalization in the Transformer Architecture](https://arxiv.org/abs/2002.04745): aprofunda a distinção entre pré-normalização e pós-normalização e seus efeitos na otimização.
- [Devlin et al. — BERT](https://arxiv.org/abs/1810.04805): exemplo de uso de encoder bidirecional com predição de tokens mascarados, mencionado no apêndice B.
- [Dao et al. — FlashAttention](https://arxiv.org/abs/2205.14135): fundamenta a ressalva da etapa 12 sobre atenção exata sem materializar a matriz completa na memória principal da GPU.

As referências apoiam a preparação docente. Não é preciso lê-las em voz alta nem exigir sua leitura prévia para acompanhar esta aula.
