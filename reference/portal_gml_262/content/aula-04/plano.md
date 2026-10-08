---
aula: 4
titulo: "Laboratório 1: Tokenizadores e embeddings"
modulo: "1 — Fundamentos: do texto ao Transformer"
tipo: laboratorio
semana: 2
duracao_min: 120
versao: v2
---

# Aula 4 — Laboratório 1: Tokenizadores e embeddings

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook executado, medição, tabela), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2 — aula de laboratório (§6-bis do contrato).** Num lab a matemática **é** a
> prática. Inverter "aplicação antes de teoria" aqui seria redundante: o lab já é aplicação integral.
> Por isso o **roteiro prático não foi reordenado** — setup, live coding e os quatro checkpoints
> permanecem nos minutos em que estavam. Três mudanças: (i) cada checkpoint **abre pelo que a tela
> imprime** quando está certo, antes de dizer o que fazer; (ii) o deck ganhou um **apêndice
> matemático** com um item por checkpoint (A.1 a A.5, com o CP4 recebendo dois porque tem dois
> fundamentos independentes); (iii) cada checkpoint cita o item correspondente, em uma linha, sem
> interromper a prática. Carga horária, numeração, checkpoints, entregável, rubrica interna e
> objetivos de aprendizagem permanecem os da V1. **O notebook em `codigo/` não muda.**

## 1. Objetivo da aula

Tornar concreto e medido o caminho texto → tokens → vetores: o aluno executa quatro tokenizadores reais
sobre o mesmo texto, mede a razão de tokens entre português e inglês num corpus paralelo, treina o
próprio Word2Vec em português e verifica na geometria dos vetores o que a Aula 3 afirmou — inclusive
onde a afirmação falha. E, ao lado disso, sai com o **fundamento formal do que executou disponível para
consulta**, de modo que "por que este número é este?" tenha resposta escrita quando a pergunta aparecer,
uma semana depois, na hora de responder às seis questões-guia.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Carregar** tokenizadores de famílias diferentes (BPE byte-level, WordPiece, Unigram/SentencePiece)
   via Hugging Face e **comparar** contagem de tokens e fertilidade sobre um mesmo texto.
2. **Medir** a razão de tokens PT/EN num corpus paralelo e **projetar** a consequência dessa razão em
   custo relativo e em ocupação de janela de contexto.
3. **Treinar** um modelo Word2Vec skip-gram com `gensim` sobre corpus em português, reportando
   vocabulário resultante e tempo de treino.
4. **Visualizar** embeddings em 2D com PCA e t-SNE e **interpretar** o agrupamento por grupo semântico.
5. **Testar** analogias vetoriais e **explicar**, com evidência do próprio notebook, por que a maioria
   falha num corpus pequeno.
6. **Justificar** qual intervenção — trocar de tokenizador ou treinar embeddings próprios — tem mais
   impacto num sistema em português, citando um número que ele mesmo mediu.

*(Idênticos aos da V1, palavra por palavra. O que a V2 acrescenta é a rastreabilidade: cada um dos seis
tem, no apêndice do deck, o item que o fundamenta — 1 → A.1, 2 → A.2, 3 → A.3, 4 → A.4, 5 → A.5,
6 → A.1 e A.3 juntos, porque a justificativa exige comparar o ganho de fertilidade com o ganho de
vocabulário próprio.)*

## 3. Teoria aplicada

Este é o primeiro laboratório da disciplina, e a teoria dele já foi dada: a Aula 2 estabeleceu o token
como decisão de engenharia e a Aula 3 estabeleceu o vetor como subproduto de uma tarefa-proxy. O papel
desta aula é converter as duas afirmações em medição. Os "conceitos" abaixo são, portanto, os pontos
que o instrutor reancora enquanto o código roda — não conteúdo novo.

**Convenção da V2 neste plano:** cada conceito abre pelo **comportamento observável** — o que aparece
na tela quando o aluno erra ou acerta — e fecha com o ponteiro para o item do apêndice. A ordem dos
blocos e dos checkpoints é a da V1, intocada.

### Bloco 1 (00:00–01:05) — Do texto às peças: tokenizadores medidos

**Conceito 1 — Reancoragem: o token é escolha, o vetor é subproduto.**
*Comportamento observável:* a primeira célula imprime o tamanho do vocabulário de quatro tokenizadores —
quatro números diferentes para o mesmo idioma de entrada. Não existe "o" token.
*Analogia do instrutor:* a Aula 2 entregou a régua, a Aula 3 entregou o mapa; hoje a turma mede a sala
com a régua e desenha o mapa.
*Erro conceitual comum:* achar que o lab é "a parte fácil da semana". O lab é onde a afirmação da aula
teórica encontra o número — e onde ela às vezes não sobrevive ao número.

**Conceito 2 — Fertilidade é a métrica que torna a Aula 2 verificável.**
*Comportamento observável:* uma tabela com **doze linhas** (quatro tokenizadores × três textos) e a
coluna `fertilidade` preenchida em todas. Sem essa coluna, a tabela é uma lista de contagens que não
compara nada, porque os textos têm tamanhos diferentes.
*Analogia:* fertilidade é consumo por quilômetro, não litros no tanque.
*Erro conceitual comum:* tratar fertilidade como propriedade do tokenizador. É propriedade do **par**
tokenizador × texto: o mesmo tokenizador tem fertilidade baixa em inglês jornalístico e alta em
português médico. É por isso que a tabela tem doze linhas e não quatro.
*Fundamento:* `f = n_tok / n_pal`, com o denominador definido como sequências de não-espaço; o viés de
`[CLS]`/`[SEP]` (que é **assimétrico** e atinge só três dos quatro tokenizadores); e a conta do acento
em UTF-8, que explica por que o byte-level fragmenta português. → **A.1** (formalização da métrica em
**A.4 da Aula 2**)

**Conceito 3 — A razão PT/EN é dinheiro e é janela — e são duas contas diferentes.**
*Comportamento observável:* o notebook imprime **duas médias**, em células diferentes: a coluna
`razão média` é a média das razões par a par; a coluna `sobrepreço` sai da razão dos totais. Os dois
números **não** são iguais.
*Erro conceitual comum, e é o erro nº 1 do checkpoint:* reportar a média das razões como "quanto o
português custa mais". A fatura é proporcional ao **total** de tokens, logo o número da fatura é a razão
dos totais. O outro número serve para caracterizar o tokenizador, com desvio e com `n`.
*Segundo erro conceitual:* generalizar a razão medida para "português custa X% mais". A razão depende do
tokenizador, do domínio e da tradução; o número do notebook vale para aquele corpus e aquele
tokenizador, e a terceira linha da interpretação tem de dizer isso.
*Fundamento:* `R = Σt_pt / Σt_en` é a média das razões **ponderada pelo comprimento**; em custo a
relação é linear (`R−1`) e em janela é inversa (`(R−1)/R`) — razão 1,33 é 33% mais caro e **25%** menos
conteúdo na janela. → **A.2** (conta da janela em **A.4 da Aula 2**)

### Bloco 2 (01:15–02:00) — Do símbolo ao vetor: geometria treinada em sala

**Conceito 4 — Treinar Word2Vec é assistir a tarefa-proxy funcionando.**
*Comportamento observável:* quatro linhas na tela — qual fonte de corpus respondeu, quantas sentenças,
o tempo de treino em segundos, e o tamanho do vocabulário após `min_count`. Em segundos, uma matriz de
vetores existe.
*Analogia:* é o carvão que sobra do fogo — o fogo era para outra coisa, o carvão é o produto.
*Erro conceitual comum:* interpretar `min_count=5` como detalhe de desempenho. É decisão semântica:
ela decide quais palavras existem no mapa, e a cauda que ela corta é exatamente onde as analogias
interessantes moram.
*Segundo erro conceitual, específico da implementação:* achar que `seed=42` garante reprodutibilidade.
Com `workers=4` o treino é assíncrono e **não determinístico**; duas execuções idênticas dão vetores
diferentes.
*Fundamento:* cada um dos sete argumentos localizado no objetivo do skip-gram — `negative=10` desloca
todos os alvos em `−log 10 = −2,303`, `window=5` é dinâmico (meia-janela esperada 3, peso `(6−j)/5`),
`min_count` age antes de os pares existirem. → **A.3** (objetivo derivado em **A.4 da Aula 3**)

**Conceito 5 — PCA e t-SNE mostram coisas diferentes, e nenhuma das duas é "o espaço".**
*Comportamento observável:* dois gráficos com os mesmos pontos em disposições diferentes. No t-SNE os
grupos aparecem mais compactos e mais separados — e essa separação é, em parte, artefato.
*Erro conceitual comum, e é o erro de leitura mais frequente do lab:* medir distância num gráfico de
t-SNE. A distância entre dois grupos num t-SNE não significa nada; só a pertinência ao grupo significa.
*Fundamento:* a PCA é projeção ortogonal, logo **contração** (`‖y_i−y_j‖ ≤ ‖x_i−x_j‖`) — longe no
gráfico é longe de verdade, perto pode não ser. O t-SNE minimiza uma KL **assimétrica** que pune
quebrar vizinhança e quase não pune inventá-la — vizinhança é confiável, escala global não é.
→ **A.4**

**Conceito 6 — A analogia que falha é o resultado, não o defeito.**
*Comportamento observável:* a coluna `ok?` da tabela com quatro valores possíveis — `SIM`, `top3`, `não`
e `(fora do vocab: …)`. A quarta é a que mais aparece, e ela significa que **o teste não rodou**, não
que o modelo errou.
*Erro conceitual comum:* refazer o treino até a analogia funcionar e entregar só o caso bonito. O
entregável pede o resultado real, e a análise da falha é o que é avaliado.
*Segundo erro conceitual:* relatar "falhou" quando o que aconteceu foi indisponibilidade da palavra.
*Fundamento:* o que `most_similar(positive, negative)` calcula de fato (média com sinais, normalização,
e **exclusão obrigatória das entradas**, que está dentro da função); e a razão sinal/ruído — o sinal `s`
da relação não cresce com o corpus, o ruído `η` de estimação cresce quando as contagens caem, e no Lab 1
o corpus é **três ordens de grandeza** menor que o do artigo. → **A.5** (objetivo em **A.5 da Aula 3**)

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 15 min | Setup do ambiente + contexto | Abertura do Lab 1 com o selo de **CPU**; recap operacional das Aulas 2 e 3 (token é escolha → CP1 e CP2; vetor é subproduto → CP3 e CP4); o entregável e a rubrica interna, com as duas questões-guia que mais separam nota nomeadas (2 e 3, respondidas em A.2 e A.5); primeira célula rodando (instalação + download dos quatro tokenizadores) enquanto o instrutor fala; **aviso do `triu` e do reinício de runtime**; menção de 30 s ao apêndice |
| 00:15 | 20 min | Demonstração guiada (live coding) | Espinho dorsal do caminho completo pelo instrutor: um tokenizador, uma frase em PT, as peças, **as duas fertilidades anotadas no quadro**, um Word2Vec treinado em poucos milhares de sentenças **com o tempo cronometrado em voz alta**, três vizinhos semânticos — sendo o terceiro escolhido para falhar |
| 00:35 | 30 min | Checkpoints 1–2 (aluno executando) | CP1: quatro tokenizadores × três textos, aberto pela **tabela de doze linhas com fertilidade** e pela decomposição das palavras longas → A.1; CP2: corpus paralelo, aberto pelos **três blocos que a tela imprime** e pelo parágrafo de três linhas, com a armadilha das duas médias → A.2 |
| 01:05 | 10 min | Intervalo | — |
| 01:15 | 35 min | Checkpoints 3–4 + extensões | CP3: Word2Vec skip-gram, aberto pelas **quatro linhas de terminal** (fonte do corpus, sentenças, tempo, vocabulário) → A.3; CP4: PCA e t-SNE mais a tabela de analogias, aberto pelas **duas coisas que precisam existir no notebook** → A.4 e A.5; extensões (BPE próprio com `tokenizers`, CBOW × skip-gram, comparação com vetores pré-treinados) |
| 01:50 | 10 min | Recolhimento | O que entregar (notebook executado, 6 questões-guia, declaração de uso de IA), prazo de uma semana, critério; **índice do apêndice projetado por 20 s** com A.2 e A.5 indicados como as respostas das questões-guia 2 e 3; ponte para a Aula 5 (Modelos sequenciais e o nascimento da atenção) |

*Comparação com a V1: a grade é a mesma, minuto a minuto. O que mudou é a forma de lançar cada
checkpoint — comportamento esperado primeiro — e cerca de 90 segundos distribuídos em ponteiros para o
apêndice, tirados das explicações conceituais que a V1 fazia em voz alta e que agora estão escritas com
mais rigor no deck.*

## 4. Demonstração guiada

**Live coding "o caminho completo em 20 minutos" — 00:15–00:35, no Colab projetado.**

O instrutor executa o espinho dorsal do lab inteiro num notebook em branco, digitando na frente da
turma. O objetivo não é adiantar os checkpoints: é mostrar que o caminho todo cabe em vinte linhas, para
que ninguém trave em sintaxe durante os checkpoints. Na V2 a demo ganha uma função extra: **os números
que ela produz são os critérios de conclusão que os checkpoints depois exigem.**

Passos em alto nível:

1. Confirmar em voz alta que o ambiente é CPU — nenhum acelerador selecionado — e que o Lab 2 (Aula 9)
   é o primeiro que pede GPU.
2. `AutoTokenizer.from_pretrained("gpt2")` e tokenizar uma frase curta em português; mostrar os IDs e
   depois `convert_ids_to_tokens` para exibir as peças. Nomear o caractere estranho que representa o
   espaço no byte-level.
3. Repetir a mesma frase com `neuralmind/bert-base-portuguese-cased` e pôr as duas listas de peças uma
   embaixo da outra na saída.
4. Calcular fertilidade das duas na frente da turma: tokens dividido por palavras separadas por espaço.
   **Anotar os dois números no quadro** — eles ficam lá até o fim do CP1.
5. Carregar poucos milhares de sentenças em português pela função `carregar_corpus_pt` do notebook,
   mostrando qual fonte da cascata respondeu.
6. Tokenizar por espaço, treinar `Word2Vec(sg=1)` com parâmetros pequenos e **cronometrar**; comentar o
   tempo em voz alta e anotá-lo ao lado das fertilidades.
7. `most_similar` de três palavras — uma frequente, uma de domínio e uma rara — e comentar por que a
   terceira é ruim ou nem existe no vocabulário. **É `min_count` acontecendo em uma linha.**
8. Fechar apontando que os checkpoints são esse mesmo caminho, com rigor: quatro tokenizadores em vez de
   dois, corpus paralelo em vez de uma frase, e gráfico em vez de impressão.

**Número que a demo produz.** Três números, e os três voltam como critério. Primeiro, **as duas
fertilidades da mesma frase em português** — a do `gpt2` e a do `bert-pt` —, lidas em voz alta e
anotadas no quadro; elas são a primeira evidência de que fertilidade é propriedade do par, e são citadas
de volta no slide 6 (CP1) como a forma da tabela que o aluno tem de produzir. Segundo, o **tempo de
treino do Word2Vec em segundos**, que materializa a frase "embedding é subproduto barato" e é citado de
volta no slide 8 (CP3) como uma das quatro linhas que a tela precisa imprimir. Terceiro, e este é
qualitativo mas conta como observável, **a terceira palavra do `most_similar` saindo ruim ou fora do
vocabulário**: é `min_count` em ação, citado de volta no slide 8 e na questão-guia 5.

Insumos preparados na véspera: o notebook do aluno já aberto num navegador limpo, um parágrafo técnico
em PT e seu equivalente em EN num arquivo de texto local, o cache dos quatro tokenizadores quente, e
capturas de tela das saídas de cada passo caso a rede caia.

## 5. Hands-on

**O componente prático da unidade é o próprio laboratório** (§6-bis e §7 do contrato). O trabalho da V2
foi explicitar os números que ele produz e amarrá-los aos critérios de conclusão — de modo que
"terminei" seja uma observação, e não uma sensação.

Quatro checkpoints, cada um com o critério de conclusão **enunciado primeiro**. O aluno trabalha no
notebook `codigo/lab-01-tokenizadores-embeddings.ipynb`; a solução de referência fica em
`codigo/solucao/`.

**Checkpoint 1 — Tokenizadores lado a lado (00:35–00:50).**
*Ao final, a tela imprime duas coisas:* uma tabela **tokenizador × texto com doze linhas** e a coluna
`fertilidade` preenchida em todas, e a decomposição de três palavras longas em português — as peças de
cada uma, nos quatro vocabulários, com a contagem ao lado.
*O que fazer:* carregar `gpt2` (BPE byte-level), `bert-base-uncased` (WordPiece EN),
`neuralmind/bert-base-portuguese-cased` (WordPiece PT) e `xlm-roberta-base` (Unigram/SentencePiece), e
tokenizar três textos: parágrafo técnico em PT, o equivalente em EN, e um trecho de código com
indentação. Escrever onde o WordPiece do BERT-PT ganha do BPE do GPT-2 e por quê (TODO 1), e uma
hipótese sobre o número de tokens do código (TODO 2).
*Fundamento e derivação:* → **Apêndice A.1** (slide 11) — por que a razão e não a contagem, o que
exatamente o denominador `\S+` conta, o viés **assimétrico** de `[CLS]`/`[SEP]` (17% de erro numa frase
curta, e só nos três tokenizadores que os usam), e a conta do acento em UTF-8 que separa "diferença de
algoritmo" de "diferença de corpus dos merges".

**Checkpoint 2 — A razão PT/EN e a conta do custo (00:50–01:05).**
*Ao final, a tela imprime três blocos:* razão média **com desvio e com o número de pares** por
tokenizador; a projeção de custo com o preço hipotético; e quantos pares cabem em `8 192` tokens em cada
idioma, com a perda em porcentagem. **E existe no notebook um parágrafo de três linhas, cuja terceira é
obrigatória:** o que estes números **não** permitem concluir.
*O que rodar:* o corpus paralelo embutido (20 pares), contando tokens dos dois lados com o **mesmo**
tokenizador. O preço é `PRECO_HIPOTETICO_POR_1K_TOKENS = 0.50  # [definir na oferta]` — **hipótese
declarada do exercício**, não preço de provedor nenhum.
*Fundamento e derivação:* → **Apêndice A.2** (slide 12) — as duas médias com contraexemplo numérico
(1,500 contra 1,143), por que a razão dos totais é a de dinheiro, a assimetria custo/janela (33% mais
caro, 25% menos conteúdo), o `pstdev` do notebook e por que o `int()` da contagem de páginas erra
quando os números são pequenos.

**Checkpoint 3 — Word2Vec em português com gensim (01:15–01:32).**
*Ao final, a tela imprime quatro linhas:* qual das três fontes de corpus respondeu (e o tamanho em MB),
quantas sentenças e quantos tokens de palavra, o **tempo de treino em segundos**, e o **tamanho do
vocabulário com `min_count=5`**. Mais o `most_similar` de três palavras escolhidas pelo aluno, cada uma
com um comentário de uma linha julgando a vizinhança.
*O que rodar:* `Word2Vec(vector_size=100, window=5, min_count=5, negative=10, epochs=5, sg=1,
workers=4, seed=42)`.
*Fundamento e derivação:* → **Apêndice A.3** (slide 13) — cada um dos sete argumentos localizado no
objetivo do skip-gram: `negative=10` deslocando todos os alvos em `−2,303`, a **janela dinâmica** do
gensim (esperada 3, não 5), `min_count` cortando muitos tipos e poucas ocorrências pela lei de Zipf, e
o fato de `workers=4` **quebrar o determinismo** do `seed`.

**Checkpoint 4 — PCA, t-SNE, vizinhos e analogias (01:32–01:50).**
*Ao final, existem duas coisas no notebook:* **dois gráficos** lado a lado, com eixo rotulado e legenda
por grupo, e a **tabela de 4 a 6 analogias com o resultado real de cada uma** — incluindo as que
falharam e as que não rodaram por palavra fora do vocabulário, com a linha final
`X/Y analogias com acerto no top-1`.
*O que rodar:* projeção de ~60 a 200 palavras escolhidas em grupos semânticos com `PCA` e `TSNE` do
`sklearn`, e `most_similar(positive=[...], negative=[...])` nas analogias.
*Fundamento e derivação:* → **Apêndice A.4** (slide 14) — as duas otimizações escritas, a prova de que
a PCA é contração (`‖y_i−y_j‖ ≤ ‖x_i−x_j‖`), a assimetria da KL que faz o t-SNE preservar vizinhança e
destruir escala, o que `perplexity` é de fato, e a **tabela de leitura** com o que cada gráfico
autoriza afirmar · → **Apêndice A.5** (slide 15) — o que `most_similar` calcula, os quatro valores da
coluna `ok?` (com `fora do vocab` significando que **o teste não rodou**), a razão sinal/ruído, e as
quatro razões estruturais da falha **com a evidência que confirma cada uma**.

**Extensões, para quem terminar antes:**
(a) treinar um BPE próprio em português com a biblioteca `tokenizers` (`ByteLevelBPETokenizer`,
vocabulário 8k) e comparar a fertilidade com a do GPT-2 no mesmo texto — é o experimento que **isola**
o efeito do corpus dos merges do efeito do algoritmo, e A.1 explica por quê;
(b) treinar CBOW no mesmo corpus e comparar os vizinhos com os do skip-gram — o contraste que A.3
prevê;
(c) comparar os vizinhos do modelo treinado com um modelo de vetores pré-treinados de português, se
houver rede e tempo.

*Extensão de dois minutos, barata e formativa:* rodar a célula de treino **duas vezes sem mudar nada** e
comparar o `most_similar` das mesmas três palavras. Com `workers=4` os resultados podem diferir, e ver
isso é a primeira aparição no curso da pergunta que o Lab 2 e o Lab 8 formalizam: *quanto esse número
se moveria sozinho?* A razão está em **A.3**.

**Questões-guia do entregável** (numeradas no notebook, respondidas em célula markdown):

1. Onde o WordPiece do BERT-PT ganha do BPE do GPT-2, e por quê?
2. O que a razão PT/EN medida significa em custo e em janela de contexto — e o que ela *não* permite
   concluir?
3. Por que a maioria das analogias falha no modelo treinado nesta aula? Cite pelo menos duas diferenças
   entre este setup e o do artigo do Word2Vec.
4. Por que o número de tokens do trecho de código muda tanto entre tokenizadores?
5. O que acontece com `min_count` maior, e por que isso é um trade-off e não um ajuste?
6. Trocar de tokenizador ou treinar embeddings próprios: qual teria mais impacto num sistema em
   português, e com que evidência **deste notebook**?

*(As seis são as da V1. As que mais separam nota são a **2** e a **3**, e as duas estão respondidas com
rigor em **A.2** e **A.5** — o que é dito em voz alta no slide 3.)*

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Incompatibilidade `gensim` × `scipy`** — o `gensim` chama `scipy.linalg.triu`, removido no `scipy` ≥ 1.13 | `ImportError` mencionando `triu` ao importar `gensim` | A primeira célula fixa `"gensim==4.3.3" "scipy<1.14"` e o notebook avisa, em caixa, para **reiniciar o runtime** depois de instalar; se persistir, há um caminho alternativo com `sklearn` (`TruncatedSVD` sobre matriz de coocorrência) só para o CP4 não travar |
| **Download do corpus falha ou é lento** | A célula de corpus fica pendurada ou estoura exceção de rede | `carregar_corpus_pt` tem cascata de três fontes com `print` dizendo qual respondeu; a terceira é um mini-corpus embutido, com aviso explícito de que os resultados ficam ruins **de propósito** — e quem cair nela precisa dizer isso na resposta da questão-guia 3 |
| **Download dos quatro tokenizadores lento no início** | Barra de progresso do Hugging Face arrastando durante a explicação | O instrutor pede que a primeira célula rode nos dois primeiros minutos, antes de qualquer explicação: o download acontece enquanto ele fala do entregável. O `xlm-roberta-base` é o mais pesado — começar a tabela com três e completar depois |
| **t-SNE lento ou erro de `perplexity`** | `ValueError` sobre `perplexity` maior que o número de amostras, ou célula demorando minutos | Limitar a ~200 palavras; o notebook calcula `perp = max(5, min(30, len(palavras)//3))` automaticamente, e quem editou a lista precisa reconferir. **PCA sozinho já satisfaz metade do critério** — e A.4 explica por que a PCA é a projeção com garantia |
| **Aluno sem conta Hugging Face ou sem Colab funcionando** | Falha de autenticação ou notebook que não sobe | O checklist foi entregue na Aula 1; plano B é trabalhar em dupla na aula e entregar o notebook individualmente depois, dentro do prazo normal |
| **Turma dispersa em velocidades diferentes** | Metade da sala no CP2 enquanto a outra ainda está no CP1 | Recolhimento é por checkpoint, não por aula: CP3 e CP4 têm célula de atalho que carrega um modelo já treinado se o treino falhar, e as extensões absorvem quem terminou antes |
| **Alunos esperando GPU e gastando cota** | Alguém seleciona acelerador e recebe aviso de limite | O instrutor afirma no primeiro slide que o lab é de CPU e que o Lab 2 (Aula 9) é o primeiro que pede GPU |
| **Tratar a constante de preço como preço real** | Alguém cita `0.50` como se fosse tabela de provedor | Corrigir na hora, **em voz alta e para a sala inteira** — esse é o tipo de número que vaza para relatório depois. A constante é hipótese do exercício e o valor da oferta é `[definir na oferta]` |
| **A turma pedir a derivação durante o lab** | "De onde vem essa média ponderada?" no meio do CP2 | Num lab **a bancada tem prioridade**: resposta de uma frase mais o ponteiro para o item do apêndice, e a conversa continua na mesa de quem perguntou, não para a sala. A Parte 4 do roteiro tem cinco derivações prontas com o tempo de cada uma; a única janela realmente barata são os minutos em que o treino do CP3 roda sozinho |
| **Aluno achar que o apêndice é matéria nova para hoje** | "Isso vai cair na entrega?" | Cravar: o apêndice é material de consulta; o que se entrega são os quatro checkpoints e as seis questões-guia. Duas das seis ficam melhores com A.2 e A.5 ao lado, e isso é dito abertamente |

## 7. Artefatos produzidos

- `lab-01-tokenizadores-embeddings.ipynb` executado, com as saídas visíveis nos quatro checkpoints,
  commitado no repositório pessoal do aluno.
- **Tabela tokenizador × texto** com doze linhas, tokens **e fertilidade** (CP1), mais a decomposição
  das três palavras longas em português nos quatro vocabulários.
- **Medição da razão PT/EN** com desvio e com o número de pares, mais a tabela de projeção de custo e de
  ocupação de janela (CP2), e o parágrafo de três linhas com a ressalva obrigatória.
- Modelo Word2Vec treinado em português, com **vocabulário e tempo de treino registrados** (CP3).
- Dois gráficos de projeção 2D (PCA e t-SNE) com eixos rotulados e legenda, e a **tabela de analogias
  com o resultado real** de cada uma, incluindo as que não rodaram por palavra fora do vocabulário (CP4).
- **O par de execuções da mesma configuração** (extensão de dois minutos do §5): o `most_similar` das
  mesmas três palavras em duas execuções idênticas. É o artefato novo da V2 e a primeira evidência, no
  curso, de que um número pode se mover sozinho.
- Respostas às seis questões-guia e a declaração de uso de IA, no próprio notebook.

## 8. Desafio pós-aula

**Este lab é o entregável avaliado da semana.** Prazo: uma semana após a aula. O que entra na entrega
está no §7 acima. O desafio abaixo é o gancho opcional, não avaliado:

1. **Fertilidade do próprio domínio.** Rodar o Checkpoint 1 sobre um texto do domínio do aluno (código
   do seu projeto, artigo da sua área, transcrição de reunião) e verificar se a **ordem** entre os
   tokenizadores se mantém. Se mudar, escrever três linhas sobre o que no texto causou a inversão — e
   **A.1** dá o vocabulário para isso (o que o denominador conta, e de onde vieram os merges).
2. **Leitura.** Mikolov et al., *Efficient Estimation of Word Representations in Vector Space*
   (arXiv 1301.3781) — releitura da seção de resultados de analogia com o resultado do próprio
   Checkpoint 4 ao lado. **Pergunta dirigida:** o artigo relata analogias funcionando em escala; quais
   das diferenças entre aquele setup e o desta aula explicam a distância entre os dois resultados? A
   tabela das quatro razões estruturais, com a evidência de cada uma, está em **A.5** — e a resposta que
   vale nomeia mecanismo e cita o número do próprio notebook.

## 9. Critérios de avaliação

Este lab compõe a nota de **Laboratórios — 30% do total**, com **descarte da menor nota** entre os oito
labs, conforme a ementa. Prazo: uma semana após a aula. Os pesos do curso não são reinventados aqui; a
rubrica abaixo é interna a este lab e é **idêntica à da V1**.

| Item | Peso interno | Observável |
|---|---|---|
| Checkpoint 1 — tokenizadores lado a lado | 20% | Tabela tokenizador × texto com tokens **e fertilidade** impressa (doze linhas), peças das palavras longas exibidas |
| Checkpoint 2 — razão PT/EN e projeção | 20% | Razão média **e desvio** impressos com o número de pares, tabela de projeção preenchida, três linhas de interpretação com a terceira presente |
| Checkpoint 3 — Word2Vec treinado | 20% | Modelo treinado, vocabulário e tempo impressos, três `most_similar` comentados |
| Checkpoint 4 — projeções e analogias | 20% | Dois gráficos com eixos rotulados e legenda, tabela de 4–6 analogias com resultado real |
| Respostas às 6 questões-guia | 20% | Respostas presentes, cada uma referenciando um número ou uma saída do próprio notebook |

Condições de forma, verificadas antes da correção do conteúdo: notebook **executado** (saídas visíveis,
não células vazias), declaração de uso de IA presente, e resultado real reportado — analogia que falhou
entra na tabela como falha. Notebook entregue sem saídas volta para reexecução.

**O que a V2 muda no *como* se corrige**, sem mexer nos pesos:

- **A resposta da questão 2 vale pela escolha da média, não pela advertência.** "Português custa mais"
  é retórica. A resposta que separa nota diz **qual das duas médias** o notebook usou para a coluna de
  custo (a razão dos totais), por que aquela é a correta para dinheiro, e que a perda de janela é
  `(R−1)/R` e não `R−1` — trinta e três por cento mais caro é vinte e cinco por cento menos conteúdo.
  O material está em **A.2** e é dito em sala.
- **A resposta da questão 3 vale pelo diagnóstico em ordem, não pela lista de razões.** "O corpus é
  pequeno" é causa sem evidência. A resposta completa verifica **disponibilidade** primeiro (as palavras
  da analogia têm vetor? a linha `fora do vocab` apareceu?), depois **contagem**, depois **otimização**,
  e só então conclui sobre o método — e distingue "falhou" de "não rodou". **A.5** tem a tabela de razão
  × evidência.
- **A resposta da questão 5 vale pela aritmética de Zipf.** "`min_count` maior deixa o vocabulário
  menor" é descrição. A resposta que separa nota diz que ele corta **muitos tipos e poucas ocorrências**,
  que o que se ganha é estimativa menos ruidosa e o que se perde são exatamente as palavras de domínio,
  e cita o próprio `len(w2v.wv)`. Está em **A.3**.
- **O apêndice é cobrável como fundamento de justificativa, nunca como derivação isolada.** Nenhuma
  questão-guia pede "derive". Elas pedem "por que" e "o que a medição não permite concluir" — e é a
  existência do apêndice que torna razoável exigir uma resposta com mecanismo em vez de uma resposta com
  adjetivo.

*Observável em sala, sem nota:* ao ser questionado no recolhimento, o aluno aponta na própria tela qual
das duas médias impressas é a que corresponde ao sobrepreço da fatura, e diz por que a outra existe.
Reportar a razão é a V1; saber qual das duas razões é a de dinheiro é a V2.

## Apêndice matemático — índice

Cinco itens, nos slides 11 a 15 do deck, **organizados por checkpoint** (§6-bis). É o mapa que o
professor consulta antes da aula, e o que o aluno leva para responder às questões-guia em casa.

| Item | Checkpoint | O que desenvolve | Apontado do |
|---|---|---|---|
| **A.1** | CP1 | Fertilidade: por que a razão e não a contagem; o que `\S+` conta como palavra e as três consequências disso; o viés **assimétrico** de `[CLS]`/`[SEP]` (2,9% num parágrafo, 17% numa frase curta, e só em três dos quatro tokenizadores); e a conta do acento em UTF-8 — `ção` entra como **5 símbolos base** contra 3 de `cao` — que separa "diferença de algoritmo" de "diferença de corpus dos merges", e explica o que a extensão (a) isola. | slides 5 e 6 |
| **A.2** | CP2 | A razão PT/EN: as duas agregações escritas, a prova de que a razão dos totais é a média das razões **ponderada pelo comprimento**, o contraexemplo numérico (1,500 contra 1,143 em dois pares), qual usar para dinheiro e qual para caracterizar; a conta da janela e a **assimetria** `R−1` contra `(R−1)/R` (33% mais caro, 25% menos conteúdo); o `pstdev` contra `stdev` (2,5% com `n=20`) como afirmação sobre o que se está medindo; o `int()` que trunca; e as quatro coisas que o experimento **não** permite concluir. | slide 7 |
| **A.3** | CP3 | Os sete argumentos da chamada dentro do objetivo do skip-gram: `sg` definindo `D` (`10N` pares contra `N`), a **janela dinâmica** do gensim (meia-janela esperada 3, peso `(6−j)/5`), `negative=10` como **limiar de PMI** (`−log 10 = −2,303`), `vector_size` como capacidade da fatoração, `min_count` com a aritmética de Zipf e os dois lados do trade-off, `epochs` que não melhora a estimativa de PMI, e `workers=4` **quebrando o determinismo do `seed`**. Com tabela-resumo. | slide 8 |
| **A.4** | CP4 | PCA × t-SNE: as duas otimizações escritas; a **prova de que a PCA é contração** (`‖y_i−y_j‖ ≤ ‖x_i−x_j‖`) e as duas regras de leitura que saem dela; a KL **assimétrica** do t-SNE, parcela por parcela, mostrando que quebrar vizinhança é caro e inventá-la é grátis — por isso **distância entre grupos não significa nada**; `perplexity` como número efetivo de vizinhos; por que a cauda pesada no plano; o não determinismo; e a **tabela de leitura** com cinco afirmações e o que cada gráfico autoriza. | slide 9 |
| **A.5** | CP4 | As analogias: o que `most_similar(positive, negative)` calcula de fato (média com sinais, normalização, **exclusão obrigatória** dentro da função) e por que isso é o mesmo `argmax` de A.5 da Aula 3; os quatro valores da coluna `ok?` e por que `fora do vocab` significa que **o teste não rodou**; a razão sinal/ruído `s` contra `η√2` e por que ela piora em corpus pequeno; a tabela dos dois experimentos lado a lado (`10⁹` contra `10⁶` palavras); as **quatro razões estruturais com a evidência de cada uma**; e a ordem de diagnóstico. | slide 9 |
