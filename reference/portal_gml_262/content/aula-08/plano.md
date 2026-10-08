---
aula: 8
titulo: "Famílias de modelos e atenção eficiente"
modulo: "1 — Fundamentos: do texto ao Transformer"
tipo: teorica
semana: 4
duracao_min: 120
versao: v2
---

# Aula 8 — Famílias de modelos e atenção eficiente

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (folha de conta do KV cache, mapa das famílias, tabela de decisão), não conversas
> descartáveis com um chatbot. O roteiro de fala vive em `roteiro.md`; a especificação dos slides em
> `instructions-slides.md`.

> **Rebalanceamento V2.** A aula abre por **três chamados de plantão**, nenhum deles com exceção no log:
> um serviço que atende dez conversas simultâneas e morre em quarenta; uma escolha entre BERT e GPT
> tomada pelo nome e pela data do modelo, que sai errada por um fator de custo; e uma janela de 128 k
> anunciada cujo contexto útil ninguém sabe dimensionar. Os três se resolvem com duas contas — quem pode
> ler quem, e quanto o rascunho custa — e as duas ficam **enunciadas** no fluxo, com a aritmética completa
> no apêndice do deck (itens A.1 a A.4). O índice do apêndice está ao fim deste plano. Carga horária,
> numeração e objetivos de aprendizagem permanecem os da V1.

> **Divisão de escopo com a Aula 10.** Esta aula **estabelece** a fórmula do KV cache termo a termo e
> **deriva** o fator de redução de MQA e GQA (**A.2**). A Aula 10 **usa** a fórmula no regime de serviço:
> o ponto em que o cache empata com os pesos, paginação e cache quantizado (**A.6 de lá**). Cada uma
> referencia a outra, e nenhuma repete a outra.

## 1. Objetivo da aula

Mostrar que as três grandes famílias de modelos — encoder-only, encoder-decoder e decoder-only — são o
**mesmo bloco** da Aula 7 montado com máscaras e objetivos de treino diferentes, e que a partir dessa
escolha se derivam tanto os usos de cada família quanto o gargalo real de servir um modelo: o KV cache, que
é o que MQA, GQA e atenção esparsa existem para cortar. O aluno sai capaz de **diagnosticar** um sintoma de
serviço (o serviço que morre ao subir a concorrência, a fatura que multiplica ao trocar de família, a janela
que não caberia) e dizer **que conta o confirmaria**.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Distinguir** encoder-only, encoder-decoder e decoder-only pela máscara de atenção e pelo objetivo de
   pré-treino — não pelo tamanho, pelo nome ou pela data do modelo.
2. **Explicar** o objetivo MLM e o papel do token `[CLS]`, e **descrever** como um fine-tuning troca a
   cabeça de tarefa sobre o mesmo corpo pré-treinado.
3. **Justificar** por que a previsão do próximo token dominou, e **apontar** dois cenários concretos em que
   um encoder-only continua sendo a escolha certa.
4. **Calcular** o tamanho do KV cache a partir de `n_layers`, `n_kv_heads`, `d_head`, `n_tokens` e bytes
   por valor, e **derivar** o fator de redução de MQA e GQA.
5. **Comparar** o custo de atenção plena, de janela deslizante e de janela com atenção global em função de
   `n` e `w`, e **explicar** como a informação de longa distância sobrevive à janela.
6. **Explicar** o que a destilação transfere do professor para o aluno que um rótulo duro não transfere.

*(Idênticos aos da V1, palavra por palavra. O item 4 mantém os verbos "calcular" e "derivar" de propósito:
a conta do cache é a resposta de engenharia desta aula e a única derivação que a prova cobra desta aula —
retirá-la seria cortar conteúdo, não realocá-lo. O que a V2 muda é **onde** a conta é feita: no fluxo ela
aparece com o número que produz; a multiplicação fator a fator está em A.2, com a justificativa de cada
fator. Rastreabilidade: 1 → A.1, 2 → A.1, 3 → A.1, 4 → A.2, 5 → A.3, 6 → A.4.)*

## 3. Teoria aplicada

Cada conceito abaixo é apresentado pelo comportamento que o motiva, com o fundamento matemático nomeado e
a derivação remetida ao apêndice.

### Bloco 1 (00:10–00:55) — Três famílias, uma decisão: quem pode ler quem

**Conceito 1 — Os três chamados, e por que nenhum é bug.**
*Comportamento observável:* **(1)** o serviço atende dez conversas simultâneas com folga e a GPU estoura em
quarenta, sem que nada tenha mudado no modelo, nos pesos ou na máquina; **(2)** um time trocou um
classificador pequeno por um LLM "porque o LLM é de 2024", a qualidade subiu um pouco e a fatura de
inferência multiplicou; **(3)** o produto anunciou 128 k de janela e ninguém sabe dizer qual é o contexto
útil em produção.
*Tese:* os três se resolvem com duas contas — quem pode ler quem (Bloco 1) e quanto o rascunho custa
(Bloco 2).
*Nota de condução:* deixar os três cartões na tela ao anunciar o plano, e dizer em voz alta qual bloco
fecha qual. O chamado (1) fecha com um número, no slide 8.

**Conceito 2 — A máscara é a arquitetura, e a escolha por data ignora isso.**
*Comportamento observável:* o chamado (2). A comparação foi feita por **data de lançamento**, e o que
decide é uma propriedade de projeto que não aparece no nome do modelo.
O bloco fechado na Aula 7 — atenção multi-cabeça, residual, norm, feed-forward — é literalmente o mesmo nas
três famílias. O que muda é **a máscara** (que posições cada posição pode consultar) e o **objetivo de
treino** que decorre dela. Bidirecional: toda posição lê todas. Causal: cada posição lê só o passado.
Híbrido: uma pilha lê tudo, outra lê o próprio passado mais a saída da primeira, por cross-attention.
*Analogia do instrutor:* é o mesmo motor em três chassis. Trocar a máscara é trocar o chassi, não o motor —
e é o chassi que define se o veículo carrega carga ou corre.
*Erro conceitual comum:* achar que BERT e GPT têm blocos internamente diferentes. Não têm. Quem aprendeu o
bloco da Aula 7 já sabe o bloco das três famílias; o que falta é a máscara e a função de perda.
*Fundamento:* **máscara e objetivo são um pacote** — com máscara bidirecional, o alvo do próximo token está
no conjunto condicionante, a solução ótima é a identidade e a perda vai a zero sem aprendizado nenhum.
→ **A.1**

**Conceito 3 — BERT e o MLM: prever a lacuna com os dois lados.**
*Comportamento observável, medido na demo:* as mesmas duas frases da Aula 3 — `o banco do rio estava
[MASK]` e `o banco do centro estava [MASK]` — produzem **distribuições de predição diferentes**. É a
resposta ao sintoma que a Aula 3 deixou aberto de propósito.
```
MLM:  L = − Σ_(i ∈ M) log P(x_i | x_\M)
```
`M` é o conjunto mascarado (~15% das posições) e `x_\M` a sequência com essas posições apagadas. Detalhe de
engenharia: das posições escolhidas, 80% viram `[MASK]`, 10% um token aleatório e 10% ficam como estão —
para reduzir a discrepância entre treino e uso.
*Analogia:* é uma prova de preenchimento de lacunas, não de redação. Quem estuda para lacuna aprende a ler
o entorno; quem estuda para redação aprende a continuar.
*Erro conceitual comum:* pegar um BERT e esperar que ele complete texto. E a razão não é "não foi treinado
para isso": é que o MLM **não define uma distribuição conjunta sobre sequências** — ele otimiza uma
pseudo-verossimilhança, e não existe fatoração dela que a geração autorregressiva possa usar.
*Fundamento:* a perda causal **é** a log-verossimilhança exata, pela regra da cadeia; a do MLM não é. Mais
as três razões independentes pelas quais o MLM não gera e a aritmética do 80/10/10. → **A.1**
*Alternativa que vale nomear em uma frase:* o 80/10/10 **ameniza** a discrepância do `[MASK]`; o **ELECTRA** a **remove**, trocando a tarefa por "cada token é original ou foi substituído?" — o modelo nunca vê `[MASK]` no treino e a cobrança passa a valer para todas as `n` posições em vez de `0,15n`. É a evidência de que a densidade de sinal que o slide 7 credita aos decoders era do **objetivo**, não da máscara causal. → **A.1**

**Conceito 4 — `[CLS]`, fine-tuning e cabeças de tarefa: o chamado (2) explicado.**
O `[CLS]` é um token acrescentado na posição zero cujo vetor de saída é usado como resumo da sequência. Não
há mágica: ele funciona como resumo porque durante o pré-treino foi obrigado a resolver uma tarefa de nível
de sentença, então o gradiente empurrou aquela posição a agregar. Sobre o corpo pré-treinado, o fine-tuning
troca apenas a **cabeça**: linear sobre `[CLS]` para classificação, linear por posição para rotulagem, e
cabeça sobre par de sentenças para similaridade e reranking (Aula 19).
*Comportamento observável e aritmético:* um encoder faz **uma passada** e devolve rótulo ou vetor; um
decoder-only precisa **gerar tokens** para dizer o mesmo, e cada token é uma passada pela pilha. `1 passada`
contra `k tokens = k passadas` — em dez milhões de documentos por dia, é a diferença entre uma máquina e um
cluster. É o chamado (2) com a conta.
*Analogia:* o corpo pré-treinado é um profissional que sabe ler; a cabeça é o formulário que se pede para
ele preencher. Trocar de formulário é barato; formar o profissional é caro.
*Erro conceitual comum:* tratar o `[CLS]` como "vetor semântico universal" da frase. Ele é bom no que o
pré-treino e o fine-tuning pediram dele; modelos de embedding de produção usam agregações treinadas
explicitamente para similaridade.

**Conceito 5 — Onde encoder-only ainda ganha, e por quê.**
A família não é peça de museu: é a escolha certa quando o volume é grande e a tarefa é fixa — classificação
em escala, geração de embeddings para busca semântica, e cross-encoder de reranking, que reaparece com nome
e métrica próprios na Aula 19. O argumento é o do Conceito 4, e é aritmético.
*Analogia:* para saber se um e-mail é spam, ninguém escreve uma redação explicando; marca uma caixinha. O
encoder marca a caixinha.
*Erro conceitual comum:* concluir que "LLM resolve tudo, então encoder morreu". É literalmente o chamado
(2), e a conta desmente.

**Conceito 6 — Encoder-decoder: quando entrada e saída são objetos diferentes.**
Há tarefas em que a entrada está inteira e disponível de uma vez e a saída é uma sequência nova: tradução,
sumarização. Aí faz sentido ter duas pilhas — encoder bidirecional e decoder causal consultando o encoder
por **cross-attention**, que é exatamente o mecanismo de Bahdanau da Aula 5, com Q do decoder e K,V do
encoder. Foi aqui que ele sobreviveu intacto.
*Analogia:* um tradutor que lê o parágrafo inteiro antes de escrever a primeira palavra, e que volta a olhar
o original a cada palavra que escreve.
*Erro conceitual comum:* supor que tradução exige encoder-decoder. Não exige: um decoder-only traduz
colocando original e tradução na mesma sequência. O custo do encoder-decoder é duas pilhas, dois conjuntos
de hiperparâmetros e um objetivo que não é reaproveitável para qualquer texto cru.

**Conceito 7 — Decoder-only: por que a previsão do próximo token venceu.**
```
LM causal: L = − Σ_(t=1..n) log P(x_t | x_(<t))
```
Cinco argumentos, na ordem de força: **(a) rótulo grátis** — todo texto cru do mundo é dado de treino, e o
rótulo do token `t` é o próprio token `t`; **(b) sinal denso** — o MLM treina em ~15% das posições, o LM
causal em 100%, e a razão é `1/0,15 ≈ 6,7` predições supervisionadas por token de corpus; **(c)
simplicidade operacional** — uma pilha, um objetivo, uma máscara; **(d) prompting unifica as tarefas** — a
tese da Aula 1; **(e) geração é nativa**, não um enxerto.
*Analogia:* o LM causal é o objetivo mais burro possível, aplicado à maior quantidade de dados possível. Foi
a burrice barata que ganhou da esperteza caríssima.
*Erro conceitual comum:* traduzir "venceu" como "é melhor em tudo". Venceu como **plataforma geral**. Por
rótulo entregue e por milissegundo de latência, um encoder pequeno destilado continua ganhando — o que
aparece nos cenários 1 e 2 do exercício.
*Fundamento:* a fatoração exata pela regra da cadeia, o contraste com a pseudo-verossimilhança do MLM, e a
contagem `1/0,15 ≈ 6,7` com as duas leituras dela (por época e por alvo). → **A.1**

### Bloco 2 (01:05–01:50) — O que a janela custa e o que se corta

**Conceito 8 — O KV cache: o chamado (1) com número.**
*Comportamento observável:* dez conversas simultâneas de 8 k tokens funcionam; quarenta derrubam a GPU. Peso
é **constante**; cache é linear no contexto **e** no número de conversas.
```
cache por token = 2 · camadas · cabeças_kv · d_head · bytes
decoder hipotético (L=32, H=32, d_head=128, fp16):  0,5 MiB por token
8 192 tokens → 4 GiB por conversa   ·   10 conversas → 40 GiB   ·   40 conversas → 160 GiB
```
Na geração autorregressiva da Aula 6, para produzir o token `n+1` o modelo recalcularia keys e values de
todas as `n` posições anteriores — que não mudaram, porque a máscara é causal. Guardá-los troca computação
por memória, e essa memória é o cache.
*Analogia:* o cache é o rascunho da conversa. Cada usuário simultâneo carrega o seu, e o rascunho cresce a
cada palavra dita.
*Erro conceitual comum:* dimensionar o serviço pelos pesos do modelo. Dimensionar pelos pesos é dimensionar
o caso de zero usuários.
*Fundamento:* a contagem fator a fator com a justificativa de cada um (o `2` é K e V; `L` porque cada camada
tem suas projeções; `d_h` e não `d_model`; `n` porque é um par por token), a instanciação até `0,5 MiB`, e a
leitura de **banda de memória** que explica por que a geração é limitada por leitura de cache e não por
aritmética. → **A.2** · *o regime de serviço, com o ponto em que o cache empata com os pesos, paginação e
cache quantizado:* → **A.6 da Aula 10**

**Conceito 9 — Longformer: janela deslizante mais atenção global, e a conta honesta do alcance.**
*Comportamento observável:* atenção plena com `n = 32 768` são cerca de **1,07 bilhão** de pares de posições
por cabeça e por camada; janela de `w = 512` são cerca de **16,8 milhões** — razão `n/w = 64`.
```
atenção plena:        custo O(n²)
janela deslizante w:  custo O(n · w)   (+ atenção global em k tokens escolhidos)
alcance por profundidade ≈ L · w/2 para cada lado
```
A informação de longa distância sobrevive por dois caminhos: **profundidade** (a informação caminha `w/2`
posições por camada em cada direção — com `L = 12` e `w = 512`, cerca de 3 072 posições para cada lado) e
**atenção global** em um punhado de `k` tokens escolhidos, que leem tudo e são lidos por todos.
*A honestidade que a V1 não trazia:* 3 072 de 32 768 é **9% da sequência**. Para a profundidade sozinha
cobrir a sequência seriam necessárias `L ≥ 2n/w = 128` camadas. A profundidade recupera alcance **médio**;
o alcance de ponta a ponta quem recupera são os tokens globais, e eles custam 3% a mais.
*Analogia:* cada leitor lê só o próprio parágrafo, mas existem alguns relatores que leem o documento
inteiro e todos podem consultar.
*Erro conceitual comum:* imaginar que janela deslizante é aproximação inofensiva. A escolha de **onde** vai
a atenção global é decisão de projeto por tarefa — errar isso é perder exatamente a dependência que
importava, sem mensagem de erro.
*Fundamento:* as duas contagens de pares, a conta das 128 camadas, o custo `2kn` da atenção global, e o
argumento de que os tokens globais reduzem o **diâmetro** do grafo de comunicação para 2 camadas.
→ **A.3**

**Conceito 10 — MQA e GQA: cortar o cache pela raiz.**
*Comportamento observável:* trocar `n_kv_heads` de 32 para 8 derruba 4 GiB para 1 GiB por conversa de 8 k, e
derruba o piso de latência por token gerado na mesma razão.
```
fator de redução do cache = n_heads / n_kv_heads
MHA: n_kv_heads = n_heads   ·   MQA: n_kv_heads = 1   ·   GQA: 1 < n_kv_heads < n_heads
```
O que **não** muda: as queries continuam `H`, logo o número de padrões de relação por camada é o mesmo; a
fórmula `softmax(QKᵀ/√d_k)V` é a da Aula 6; camadas e dimensão são as mesmas.
*Analogia:* trinta e dois leitores fazendo perguntas diferentes, mas consultando um índice compartilhado em
vez de cada um manter a sua cópia.
*Erro conceitual comum:* achar que MQA e GQA reduzem o tamanho do modelo ou a computação da atenção.
Reduzem a **memória do cache** e o **tráfego de memória** para lê-lo. O trade-off é qualidade: MQA corta
mais e pode custar qualidade; GQA recupera quase tudo com uma fração do cache, e é o padrão dos modelos
abertos recentes.
*Segundo erro conceitual, e é o que a V2 corrige:* dizer que "nada além do cache muda". As projeções de K e
V **encolhem** — de `3·d_model²` para `d_model² + 2·d_model·(H_kv·d_h)` —, o que é uma redução real de
parâmetros que as implementações costumam compensar alargando a FFN.
*Fundamento:* a razão derivada, com o cancelamento de todos os outros fatores; a conta de banda de memória
por token gerado (2,0 ms em MHA contra 0,5 ms em GQA, com 2 TB/s); e a nota honesta sobre os parâmetros.
→ **A.2**

**Conceito 11 — Destilação: aprender a distribuição, não o rótulo.**
Um modelo grande já treinado não devolve só o rótulo certo: devolve uma distribuição sobre todas as
alternativas. Treinar o aluno para reproduzir essa distribuição — com temperatura `T` para achatá-la e
revelar a cauda — entrega muito mais informação por exemplo do que um rótulo one-hot.
```
destilação: L = α · CE(y_aluno, rótulo) + (1 − α) · T² · KL(P_professor^T ‖ P_aluno^T)
```
*Comportamento observável, com número:* com logits `(5, 3, 1, −2)`, a classe menos provável tem
probabilidade `0,0008` a `T = 1` e `0,081` a `T = 4` — a cauda ficou **cem vezes mais visível** sem que o
professor mudasse.
*Analogia:* o rótulo diz "a resposta é B". O professor diz "é B, mas C era defensável e D é absurdo". A
segunda frase ensina mais.
*Onde isso aterrissa:* os encoders pequenos que sustentam classificação e reranking em produção são em boa
medida destilados — a família encoder-only continua viva **porque** dá para comprimir, o que fecha o laço
com o Conceito 5 e com o chamado (2). O tema volta no Módulo 7.
*Erro conceitual comum:* confundir destilação com ajuste em textos gerados pelo professor. As duas práticas
existem e as duas são chamadas de destilação, mas a clássica precisa da **distribuição completa**, o que
exige acesso aos logits — e é justamente o que uma API fechada não dá.
*Fundamento:* a KL na ordem `professor ‖ aluno` é **cobre-modos**, e é a assimetria que força o aluno a
cobrir a cauda; o gradiente `(1/T)(q − p)` justifica o fator `T²`; e em temperatura alta destilar é
equivalente a **igualar logits**. → **A.4**

### Mapa das famílias

| Família | Máscara | Objetivo de pré-treino | Faz bem | Exemplo canônico | Onde volta no curso |
|---|---|---|---|---|---|
| Encoder-only | nenhuma — bidirecional | MLM (~15% mascarados) | rótulo, vetor de embedding, escore de par | BERT | Aula 19 (embeddings e reranking) |
| Encoder-decoder | bidirecional no encoder, causal no decoder, cross-attention entre eles | reconstrução / corrupção de trechos | transformar uma entrada completa em outra sequência | T5, BART | Aula 5 (cross-attention é o Bahdanau) |
| Decoder-only | causal | LM causal (100% das posições) | gerar, seguir instrução, servir de interface única | GPT | Aula 9 (na unha), Aula 10 (escala e inferência) |

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura pelos sintomas | Recap da Aula 7 em uma linha (RoPE em Q/K, pré-norm com RMSNorm, SwiGLU, residual limpa — **o bloco está pronto**); **os três chamados de plantão**, nenhum com exceção no log; tese: os três se resolvem com duas contas, e cada bloco fecha um par deles |
| 00:10 | 45 min | Bloco 1 — três famílias | A máscara decide quem lê quem, e por que a escolha por data sai errada (A.1); BERT e o MLM, com as duas frases do `banco` fechando o gancho da Aula 3 (A.1); `[CLS]`, fine-tuning e a conta `1 passada × k tokens` que fecha o chamado (2); **demonstração no Hugging Face Hub (12 min)**, terminando na leitura dos dois campos do `config.json`; encoder-decoder e a sobrevivência da cross-attention; decoder-only e os cinco argumentos, com o sinal denso quantificado em `6,7×` |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — o que a janela custa | **O KV cache enunciado com o número que produz** (`0,5 MiB/token`, `4 GiB` por conversa) e o chamado (1) fechado por aritmética de concorrência (A.2); Longformer, com a conta honesta do alcance — 3 072 de 32 768, e as 128 camadas que faltariam (A.3); MQA e GQA e o fator `n_heads/n_kv_heads`, com a conta de banda de memória (A.2); destilação com o número da cauda a `T=4` (A.4); mapa das famílias consolidado; **exercício de decisão com conta exigida (8 min + 3 de correção)** |
| 01:50 | 10 min | Fechamento | Os três chamados fechados com a causa nomeada e onde ela mora; síntese (máscara + objetivo + o que o cache cobra); **índice do apêndice projetado (20 s)**; ponte para a Aula 9 (Lab 2 — Mini-GPT do zero em PyTorch) e as leituras |

*Comparação com a V1: os ~5 min de quadro multiplicando os seis fatores do KV cache caíram para 0 min de
conta conduzida — o slide 8 passou a trazer o resultado com a unidade, e a multiplicação fator a fator
está em A.2, com a justificativa de cada fator e a leitura de banda de memória que a V1 não tinha. Os
minutos liberados foram para a abertura pelos sintomas (10 min de chamados em vez de 10 de recap seco),
para a demo (de 9 para 12 min, com o ato 4 promovido a evidência) e para o exercício (de 8 para 11 min). A
aritmética permanece integralmente disponível em A.1–A.4.*

## 4. Demonstração guiada

**Demo "BERT hoje, e os dois campos que abrem a segunda metade" — 12 min, 100% navegador, terminando no
quadro.**
Roda inteira no Hugging Face Hub, com a instanciação da fórmula do cache feita ao vivo com números lidos da
tela. Por isso **esta aula não tem pasta `codigo/`** — nada aqui exige ambiente montado, e o que é
essencial (a aritmética do cache com números reais) não depende de rede se os valores estiverem anotados da
véspera.

Passos em alto nível:

1. Abrir a página de um BERT em português no Hub (`neuralmind/bert-base-portuguese-cased`) ou de um BERT
   multilíngue, com o widget de fill-mask visível.
2. Submeter `O banco do rio estava [MASK].` e ler as predições que aparecem na tela.
3. Submeter `O banco do centro estava [MASK].` — mesma palavra "banco", contexto diferente, distribuição
   diferente. **É a resposta visível ao sintoma que a Aula 3 deixou aberto de propósito**: a representação
   de "banco" mudou porque a atenção leu os dois lados.
4. Abrir a página de um modelo de embedding (`sentence-transformers/all-MiniLM-L6-v2`) e mostrar que a
   saída não é texto — é um vetor de dimensão fixa.
5. Abrir a página de um cross-encoder de reranking (`cross-encoder/ms-marco-MiniLM-L-6-v2`) e mostrar que a
   saída é **um número** para um par (consulta, documento). Uma passada, um escore.
6. Abrir o `config.json` de um decoder-only aberto e recente (`[definir na oferta]` qual) e ler na tela os
   quatro campos que importam: `num_hidden_layers`, `num_attention_heads`, `num_key_value_heads` e
   `hidden_size`. Se os dois do meio diferem, é GQA.
7. No quadro: aplicar a fórmula do KV cache com os valores lidos na tela e refazer a mesma conta trocando
   `num_key_value_heads` por `num_attention_heads`, que é o que seria sem GQA. A razão entre as duas contas
   é exatamente a razão entre os dois números que estão na tela.

**Número que a demo produz.** Três, e os três voltam ao fluxo. Primeiro, **os dois números lidos do
`config.json`** — `num_attention_heads` e `num_key_value_heads` — que não estão escritos em slide nenhum e
são anotados no quadro. Segundo, **o cache por token daquele modelo real**, calculado no passo 7 a partir dos
quatro campos; ele é citado de volta no slide 8 como confirmação de que o `0,5 MiB` do modelo hipotético é
uma ordem de grandeza honesta, e no cenário 5 do exercício. Terceiro, **a razão entre as duas contas do
passo 7**, que sai igual a `num_attention_heads / num_key_value_heads` — é o fator de redução do slide 10
saindo da aritmética em vez de sair do slide. E o quarto produto, qualitativo mas verificável, é o **par de
distribuições diferentes** dos passos 2 e 3, citado de volta como o fechamento do gancho da Aula 3.

Insumos preparados antes da aula: as quatro URLs do Hub abertas em abas separadas, as duas frases do "banco"
num arquivo de texto local para colar sem digitar, os quatro campos do `config.json` **anotados na véspera**
(para o passo 7 rodar sem rede), e capturas de tela de todos os passos. **As predições do widget não são
anotadas neste plano de propósito** — o instrutor testa as frases na véspera, confirma que o par funciona e
ajusta as frases se necessário.

## 5. Hands-on

**Componente prático da unidade — exercício de decisão com conta exigida (8 min de dupla + 3 de correção,
01:39–01:50).**

Mantém os cinco cenários da V1, que já eram de decisão, e **endurece o critério**: onde a V1 pedia "uma
frase justificando", a V2 pede **que conta ou medição confirmaria a escolha**. É a mesma mudança que a Aula
6 fez no exercício dela, e ela existe porque justificativa sem conta é preferência com vocabulário técnico.

Cinco cenários projetados. Cada dupla escreve, para cada um: **(a)** a família (encoder-only,
encoder-decoder ou decoder-only); **(b)** o que usaria de atenção eficiente — ou explicitamente nada;
**(c)** **que conta ou medição confirmaria** a escolha.

1. Classificar 10 milhões de comentários por dia em três rótulos, com latência de milissegundos.
2. Busca semântica sobre 500 mil documentos internos, com reranking dos 50 primeiros resultados.
3. Assistente que conversa, chama ferramenta e escreve código.
4. Responder perguntas sobre um contrato de 80 páginas lido inteiro de uma vez.
5. Servir um modelo de 8 B para mil usuários simultâneos, com contexto de 32 mil tokens.

*Respostas esperadas, com a conta de cada uma:* (1) encoder-only, nada de atenção eficiente — a conta é
`custo por rótulo entregue`: uma passada contra `k` tokens gerados, multiplicado por 10⁷ documentos/dia;
(2) encoder-only **duas vezes** — um modelo de embedding para recuperar e um cross-encoder para reranquear
—, e a conta é o número de pares (consulta, documento) que o reranker precisa pontuar: 50 por consulta, o
que só fecha porque são 50 e não 500 mil; (3) decoder-only, é o cenário de controle e não tem discussão;
(4) decoder-only com janela + atenção global nos tokens da pergunta, e a conta é a do slide 9 —
`n·w` contra `n²`, mais a verificação de que o alcance por profundidade não cobre 80 páginas; (5)
decoder-only com GQA, e a conta é a do KV cache: `8 B × 2 bytes = 16 GiB` de peso constante contra o cache
de 32 k tokens **multiplicado por mil usuários** — e o ponto do exercício é que **GQA sozinho não fecha a
conta**, o que é a porta da Aula 10.

*Critério de conclusão observável:* a dupla entrega cinco linhas com as três colunas preenchidas e defende
ao menos uma escolha em voz alta **citando a conta**, não a preferência. "Porque é melhor" não conta;
"porque é mais novo" desconta — e é literalmente o chamado (2) do slide 1.

*Extensão para quem terminar antes (opcional):* refazer a conta do cache do cenário 5 nas três
configurações (MHA, GQA com 8 cabeças de K/V, MQA) e dizer, para cada uma, quantos usuários simultâneos
caberiam numa GPU de 80 GiB. É a conta que A.2 tem resolvida, e é o item de derivação que a prova cobra
desta aula.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Hub fora do ar** ou widget de inferência sem carregar | Spinner infinito no fill-mask | Capturas de tela dos passos feitas na véspera; **os passos 6 e 7 são os pedagogicamente essenciais e o 7 não depende de rede** — com os quatro campos anotados da véspera, a conta se faz no quadro do mesmo jeito |
| **Predições do fill-mask decepcionam** — o par de frases não separa os sentidos | As duas distribuições saem parecidas | Ter um segundo par de frases testado na véspera; se ainda falhar, dizer isso à turma e usar o resultado como observação honesta sobre modelo pequeno, sem forçar a narrativa |
| **A turma pedir a conta do cache fator a fator** | "Faz a multiplicação aí" no slide 8 | Parte 4 do roteiro, item 2, com 5 min de custo. A regra é remeter a A.2 e seguir; a instanciação com números reais já acontece na demo, e ela é mais convincente que a do modelo hipotético |
| **Confusão entre reduzir cache e reduzir computação** | Pergunta "então GQA deixa o modelo mais rápido de treinar?" | Voltar à fórmula: `n_kv_heads` aparece no cache e no tráfego de memória, não no número de queries. A resposta honesta é que **acelera a geração** (que é limitada por banda) e quase não muda o treino (que é limitado por aritmética). O número está em A.2 |
| **Turma pede comparação de modelos comerciais** ("qual usa GQA?") | Perguntas de nome de produto no Bloco 2 | Ler `config.json` no Hub ao vivo em vez de responder de cabeça; o que não estiver na tela é `[definir na oferta]` |
| **Turma sentir que "faltou rigor"** por a conta não ir ao quadro | Comentário de que a aula ficou descritiva | Projetar o apêndice por 30 s: são quatro itens, com a justificativa de cada fator da fórmula, a conta de banda de memória, a conta das 128 camadas do Longformer e a derivação do `T²` da destilação — nada disso estava na V1. O rigor mudou de lugar e ficou consultável |
| **Alguém questionar o alcance do Longformer** | "Mas a profundidade não resolve o alcance longo?" | Dar o ponto — é exatamente o que a V2 diz. `3 072` de `32 768`, e seriam necessárias 128 camadas. A conta está em A.3 e é a melhor pergunta que pode aparecer no Bloco 2 |
| **Tempo estourar no Bloco 1** (BERT gera muita pergunta) | 00:46 e ainda no `[CLS]` | Comprimir o slide 6 (encoder-decoder) a três minutos — o essencial é que a cross-attention é o Bahdanau — e **proteger o Bloco 2 inteiro**, que é o pré-requisito da Aula 10 |
| **Tempo estourar no Bloco 2** | 01:40 e ainda na destilação | Cortar o slide 12 (mapa consolidado) da exposição e deixá-lo projetado durante o exercício, que é o uso natural dele. **Não cortar** o slide 8 nem o 10: os dois são a resposta do chamado (1) e o pré-requisito da Aula 10 |

## 7. Artefatos produzidos

- **Folha de conta do KV cache:** a fórmula com `L`, `n_kv_heads`, `d_head`, `n` e `b`, instanciada com os
  valores do modelo hipotético do slide 8 **e refeita com os quatro campos lidos no `config.json` da demo**,
  mais a razão entre as duas contas. É o artefato central da aula e o insumo direto da Aula 10.
- **Tabela de decisão do exercício:** cinco cenários × família × atenção eficiente × **conta que confirma**,
  fotografada ou digitada no repositório pessoal. É o artefato novo da V2, no lugar da tabela com "uma frase
  de justificativa".
- **Mapa das famílias** preenchido à mão (família × máscara × objetivo × uso), que é a folha de revisão
  desta aula para a prova da Aula 17.
- Anotação dos dois números do `config.json` (`num_attention_heads` e `num_key_value_heads`) do modelo real
  usado na demo, com a data da leitura — o valor muda a cada modelo e a anotação registra qual foi.
- Nenhum arquivo de código nesta aula — a demonstração é de navegador e quadro.

## 8. Desafio pós-aula

Não avaliado. Três itens, na ordem:

1. **Duas leituras de arquitetura.** Devlin et al., *BERT: Pre-training of Deep Bidirectional Transformers
   for Language Understanding* (arXiv 1810.04805): a seção do objetivo de pré-treino. E Ainslie et al.,
   *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints* (arXiv 2305.13245),
   com Shazeer, *Fast Transformer Decoding* / MQA (arXiv 1911.02150) como antecedente. **Pergunta
   dirigida:** no GQA, o que exatamente é compartilhado entre as cabeças, o que continua sendo por cabeça, e
   qual é o fator de redução do cache em função de `n_heads` e `n_kv_heads`? A derivação do fator está em
   **A.2**, e a resposta completa também nomeia o que **não** é reduzido (os padrões de relação) e o que é
   reduzido **além** do cache (os parâmetros das projeções de K e V).
2. **Leitura de configuração.** Abrir o `config.json` de dois modelos decoder-only abertos diferentes no
   Hugging Face Hub, anotar `num_attention_heads`, `num_key_value_heads`, `num_hidden_layers` e
   `hidden_size`, e calcular o cache por token de cada um com a fórmula da aula. Cinco linhas comparando os
   dois — e, para cada um, **quantos usuários simultâneos de 8 k tokens caberiam em 60 GiB de cache**. A
   conta está resolvida em **A.2**.
3. **Uma decisão sua.** Escolher uma tarefa de NLP que o aluno faria hoje, dizer qual família usaria e
   escrever três linhas sobre o que mudaria na decisão se o volume fosse mil vezes maior — citando qual das
   duas contas da aula muda primeiro.

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. Ela é pré-requisito direto do Lab 2 (Aula 9) e ponto certo de
prova na Aula 17. Os pesos são os da ementa e não são reinventados aqui:

- **Laboratórios — 30%.** Oito labs com entregável individual, entrega até uma semana após o lab,
  **descartando a menor nota**. O Lab 2, na próxima aula, implementa a família decoder-only desta aula — a
  máscara causal do slide 2 vira código.
- **Prova — 30%.** Individual, escrita, Aula 17, sobre as Aulas 1 a 16, com a distribuição
  **42 diagnóstico · 40 justificativa · 8 conceito aplicado · 10 derivação**. Desta aula, o conteúdo aparece
  principalmente como **diagnóstico e justificativa**: dado um serviço que degrada ao subir a concorrência,
  nomear a causa e a conta que confirma; justificar o uso de um encoder-only contra um decoder-only por
  argumento de custo por rótulo entregue; identificar a família a partir da máscara e do objetivo, e dizer
  por que a data do modelo não decide. **E é desta aula que sai o candidato natural ao item de derivação:**
  a conta do cache com o fator de redução de GQA é curta, verificável e ancorada num porquê — ela é o tipo
  de derivação que a V2 mantém cobrada.
- **Projeto final — 40%.** Equipes de 3–4, com entregas nas Aulas 22, 26 e 30. Vários projetos vão usar um
  encoder-only como componente de recuperação ou de reranking — a decisão de família tomada aqui volta como
  escolha de arquitetura no projeto, e a conta do cache volta como dimensionamento de quem for servir modelo
  local.

**O que a V2 muda no *como* se cobra o conteúdo desta aula**, sem mexer nos pesos:

- **A resposta sobre o cache vale pela leitura do fator, não pelo número.** "O cache é grande" é retórica.
  A resposta que separa nota diz **qual fator** da fórmula o sintoma move — contexto move `n`, concorrência
  multiplica o total, GQA move `H_kv` — e diz que peso é constante e cache não é. O material está em
  **A.2**.
- **A resposta sobre encoder × decoder vale pela conta por rótulo entregue.** "Encoder é mais barato" é
  incompleta. A resposta completa é `1 passada` contra `k tokens = k passadas`, multiplicada pelo volume
  diário do cenário.
- **A resposta sobre a janela deslizante vale pelo alcance, não pela complexidade.** "Cai de `n²` para
  `n·w`" é metade. A resposta que separa nota diz **quanto alcance a profundidade compra** (`L·w/2`) e que
  isso não cobre a sequência — por isso a atenção global não é opcional. Está em **A.3**.
- **A resposta sobre destilação vale pelo que a cauda carrega.** "Transfere mais informação" é adjetivo. A
  resposta completa diz que a KL está na ordem `professor ‖ aluno` porque isso força o aluno a **cobrir** a
  cauda, e que a temperatura controla quanto da ordenação da cauda entra no gradiente — com o número.
  Está em **A.4**.

*Observável desta aula, sem nota:* ao ser questionado no fechamento, o aluno diz qual família resolve um
cenário novo e sustenta a resposta **com a aritmética do cache ou com o custo por rótulo entregue**, em vez
de com o nome ou a data do modelo. E, dado um sintoma de degradação por concorrência, aponta qual fator da
fórmula do cache o sintoma move. Nomear a família é a V1; nomear o fator é a V2.

## Apêndice matemático — índice

Quatro itens, nos slides 15 a 18 do deck. É o mapa que o professor consulta antes da aula, e o que a turma
leva para estudar para a Aula 17.

| Item | O que desenvolve | Apontado do |
|---|---|---|
| **A.1** | Os dois objetivos escritos (`L_MLM` e `L_LM`); a **degeneração** de "bidirecional + próximo token", em que o alvo está no condicionante e a solução ótima é a identidade; as **três razões independentes** pelas quais o MLM não gera — a principal sendo que ele otimiza uma **pseudo-verossimilhança** e não define fatoração de nenhuma conjunta, contra a perda causal que **é** a log-verossimilhança exata pela regra da cadeia; a aritmética do 80/10/10 e o papel dos 10% não marcados; a contagem `1/0,15 ≈ 6,7` com as duas leituras; os casos-limite `\|M\| = n` e `\|M\| = 1` que fixam o 15%; as variantes prefix-LM e corrupção de trechos, que **geram** porque têm fatoração; e o **ELECTRA**, que troca o objetivo por Detecção de Token Substituído e resolve os **dois** defeitos que o item estabelece — o discriminador nunca vê `[MASK]` no treino, e a cobrança vale para as `n` posições em vez de `0,15n`, recuperando a densidade de sinal que a contagem `6,7` atribuía aos decoders. Com o contrapeso honesto (RTD é binária, logo mais alvos de menor informação), a precisão de que **não é uma GAN** (não há gradiente de `D` para `G`, porque a amostragem de token é discreta) e o caso-limite que explica o projeto: gerador **bom demais** transforma os rótulos em ruído, e é por isso que `G` é deliberadamente pequeno. | slides 3 e 7 |
| **A.2** | O KV cache **fator por fator**, com a razão de existir de cada um (`2` = K e V; `L` porque cada camada tem projeções próprias; `d_h` e não `d_model`; `n` porque é um par por token); a instanciação até `0,5 MiB/token` e `4 GiB` por conversa de 8 k; o fechamento do chamado (1) por aritmética (40 GiB cabe, 160 GiB não, e 15 conversas é o teto); a **derivação exata** de `fator = n_heads/n_kv_heads` com o cancelamento de todos os outros fatores, instanciada nos três regimes; a lista honesta do que muda e do que não muda — **inclusive a redução de 50% nos parâmetros das projeções de K e V**, que a V1 não mencionava; a **conta de banda de memória** (2,0 ms contra 0,5 ms por token, a 2 TB/s) que explica por que GQA acelera a geração e não o treino; e como ler tudo isso de um `config.json`. | slides 8 e 10 |
| **A.3** | Atenção em janela: as duas contagens de pares (`1,07·10⁹` contra `1,68·10⁷`, razão 64) e por que o ganho `n/w` só compensa em contexto longo; o alcance por profundidade `L·w/2` e a **conta que a V1 devia** — `3 072` de `32 768`, e `L ≥ 2n/w = 128` camadas para a profundidade sozinha cobrir a sequência; o custo `2kn` da atenção global (3,1% a mais com `k=8`) e o argumento de que ela reduz o **diâmetro** do grafo para 2 camadas; a conta de memória (2,0 GiB contra 32 MiB por cabeça); e cinco casos-limite, incluindo a janela dilatada. | slide 9 |
| **A.4** | A perda de destilação com notação declarada; **por que a KL está na ordem `professor ‖ aluno`** — a assimetria cobre-modos que força o aluno a cobrir a cauda, contra a busca-modos da ordem invertida; o gradiente `(1/T)(q−p)` derivado, e de onde vem o fator `T²`; o **limite de temperatura alta**, em que destilar é equivalente a igualar logits (mínimos quadrados nos logits); o exemplo numérico completo (`0,00079 → 0,0809`, cauda cem vezes mais visível; razão `1 097 → 5,75`); seis casos-limite, incluindo `α = 0`, que é a razão de a destilação funcionar em **dados não rotulados**; e a distinção entre destilação de distribuição e ajuste em texto gerado — as duas chamadas de destilação, e o que só a primeira transfere. | slide 11 |
