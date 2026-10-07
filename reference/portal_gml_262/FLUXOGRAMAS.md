# Mapa dos fluxogramas

31 mapas de percurso, 27 mapas de mecanismos e 2 mapas de orientação (curso e sessão de estudo).

Há mapas de mecanismos junto a **191 etapas de texto** e **196 etapas visuais**. As demais etapas visuais têm o percurso da aula. Os mapas são reutilizados quando o mesmo mecanismo reaparece; essas contagens indicam inserções, não diagramas distintos.

As setas do percurso representam ordem de estudo. Os mapas de mecanismos descrevem fluxo de dados, alternativas, paralelismo ou ciclos, conforme indicado. Os mapas não usam falas privadas do professor nem gabaritos. A aula 06 preserva seu player e distingue bloco original com pós-normalização de variante com pré-normalização.

| Aula | Assunto | Texto com mecanismo / total | Demonstração com mecanismo / total |
| --- | --- | --- | --- |
| 00 | Aula 0 — Recepção: o mapa do curso, os materiais e o ambiente | 3/17 | 2/10 |
| 01 | Apresentação da disciplina; panorama de LLMs; tarefas e métricas de NLP | 4/20 | 4/12 |
| 02 | Tokenização | 2/18 | 3/12 |
| 03 | Embeddings e representações vetoriais | 7/19 | 7/12 |
| 04 | Laboratório 1: Tokenizadores e embeddings | 7/15 | 4/12 |
| 05 | Modelos sequenciais e o nascimento da atenção | 11/27 | 6/12 |
| 06 | Transformer I: self-attention e a arquitetura | 8/25 | 18/20 |
| 07 | Transformer II: posição, normalização e o bloco moderno | 8/22 | 6/12 |
| 08 | Famílias de modelos e atenção eficiente | 4/19 | 5/12 |
| 09 | Laboratório 2: Mini-GPT do zero em PyTorch | 8/14 | 10/12 |
| 10 | Do Transformer ao LLM: escala, MoE, decodificação e prompting | 3/20 | 8/14 |
| 11 | Laboratório 3: Decodificação e prompting na prática | 8/14 | 5/12 |
| 12 | Pré-treinamento: dados, leis de escala e sistemas | 4/20 | 1/13 |
| 13 | SFT e fine-tuning eficiente: LoRA e QLoRA | 4/20 | 5/12 |
| 14 | Laboratório 4: Fine-tuning com LoRA/QLoRA | 7/14 | 4/12 |
| 15 | Alinhamento: RLHF, PPO e DPO | 6/20 | 5/12 |
| 16 | Modelos de raciocínio: GRPO e DeepSeek-R1 | 7/19 | 12/13 |
| 17 | Prova (conteúdo das Aulas 1 a 16) | 0/5 | 5/9 |
| 18 | RAG I: geração aumentada por recuperação | 4/19 | 6/12 |
| 19 | RAG II: retrieval híbrido, reranking e métricas | 7/19 | 7/13 |
| 20 | Laboratório 5: Pipeline RAG completo | 10/16 | 6/13 |
| 21 | Tool calling e Model Context Protocol (MCP) | 8/18 | 7/12 |
| 22 | Laboratório 6: Tool calling e MCP — Entrega 1 do projeto | 9/15 | 7/12 |
| 23 | Agentes de IA: loops, planejamento e memória | 10/19 | 9/12 |
| 24 | Sistemas multiagente e orquestração | 3/20 | 4/12 |
| 25 | Laboratório 7: Construindo um agente autônomo | 9/15 | 9/12 |
| 26 | Segurança e avaliação de agentes | 11/19 | 8/12 |
| 27 | Avaliação de LLMs e de sistemas com LLMs | 7/20 | 5/14 |
| 28 | Laboratório 8: Harness de avaliação do projeto | 8/15 | 5/12 |
| 29 | Recapitulação e fronteiras da área | 3/19 | 4/12 |
| 30 | Apresentações finais — Entrega final do projeto | 1/10 | 9/10 |

## Manutenção

Edite `flowcharts.py` e `demos/flowcharts.css`. Ao alterar títulos de etapas, confira suas associações e execute `python scripts/build_flowchart_map.py` para atualizar este relatório. O guia de uso tem uma fonte única em [COMO-USAR.md](COMO-USAR.md).

## Aula 00

Mapas disponíveis: percurso da aula; Laboratório: da hipótese à evidência.

- Slide 10 · [Transição] Agora o ambiente · 00:35–00:37 → **Laboratório: da hipótese à evidência**
- Slide 11 · Como estudar nesta disciplina · 00:37–00:40 → **Laboratório: da hipótese à evidência**
- Parte 3 — Setup de ambiente → **Laboratório: da hipótese à evidência**

## Aula 01

Mapas disponíveis: percurso da aula; Classificação: das previsões à métrica.

- Slide 7 · O detector de fraude com 99% de acurácia que nunca achou uma fraude · 01:05–01:12 → **Classificação: das previsões à métrica**
- Slide 8 · [Exercício 1] A matriz na mão: três detectores, seis números · 01:12–01:19 → **Classificação: das previsões à métrica**
- Slide 9 · F₁ é média harmônica — e o peso é decisão de produto · 01:19–01:24 → **Classificação: das previsões à métrica**
- Sub-bloco 1 — Exercício 1 · A matriz na mão (slide 8, 01:12–01:19) → **Classificação: das previsões à métrica**

## Aula 02

Mapas disponíveis: percurso da aula; BPE: aprender e depois aplicar.

- Slide 6 · O que o BPE produz: uma lista ordenada de merges · 00:29–00:38 → **BPE: aprender e depois aplicar**
- Slide 8 · Byte-level BPE: o fim do UNK e o preço do acento · 00:46–00:55 → **BPE: aprender e depois aplicar**

## Aula 03

Mapas disponíveis: percurso da aula; Embeddings: aprender relações e buscar vizinhos.

- Slide 4 · A hipótese distribucional · 00:17–00:24 → **Embeddings: aprender relações e buscar vizinhos**
- Slide 5 · Vetores densos: semântica como geometria · 00:24–00:30 → **Embeddings: aprender relações e buscar vizinhos**
- Slide 6 · A régua: cosseno, e o que ela permite decidir · 00:30–00:37 → **Embeddings: aprender relações e buscar vizinhos**
- Slide 7 · Analogias: a relação virou direção — e o terceiro sintoma · 00:37–00:43 → **Embeddings: aprender relações e buscar vizinhos**
- Slide 9 · Word2Vec: CBOW × skip-gram · 01:05–01:14 → **Embeddings: aprender relações e buscar vizinhos**
- Slide 10 · O softmax de cem mil classes e a amostragem negativa · 01:14–01:23 → **Embeddings: aprender relações e buscar vizinhos**
- Slide 14 · Fechamento: de vetor estático a vetor contextual · 01:50–02:00 → **Embeddings: aprender relações e buscar vizinhos**

## Aula 04

Mapas disponíveis: percurso da aula; Embeddings: aprender relações e buscar vizinhos; BPE: aprender e depois aplicar; Laboratório: da hipótese à evidência.

- Slide 1 · Abertura: Lab 1 — do texto ao vetor · 00:00–00:04 → **Embeddings: aprender relações e buscar vizinhos**
- Slide 3 · O entregável e o critério · 00:08–00:12 → **Laboratório: da hipótese à evidência**
- Slide 4 · Setup do ambiente · 00:12–00:15 → **Laboratório: da hipótese à evidência**
- Slide 6 · [Checkpoint 1] Quatro tokenizadores, três textos · 00:35–00:50 → **Laboratório: da hipótese à evidência**
- Slide 7 · [Checkpoint 2] A razão PT/EN e a conta do custo · 00:50–01:05 → **Laboratório: da hipótese à evidência**
- Slide 8 · [Checkpoint 3] Word2Vec em português com gensim · 01:15–01:32 → **Embeddings: aprender relações e buscar vizinhos**
- Slide 9 · [Checkpoint 4] PCA, t-SNE, vizinhos e analogias · 01:32–01:50 → **Embeddings: aprender relações e buscar vizinhos**

## Aula 05

Mapas disponíveis: percurso da aula; Recorrência e acesso por atenção; Self-attention: da entrada ao contexto.

- Slide 3 · O conceito em uso: ler em ordem e carregar um resumo · 00:10–00:16 → **Recorrência e acesso por atenção**
- Slide 4 · Sintoma 2: o modelo que esquece o sujeito · 00:16–00:23 → **Recorrência e acesso por atenção**
- Slide 6 · O que o gating do LSTM compra · 00:28–00:34 → **Recorrência e acesso por atenção**
- Slide 8 · Onde memória e acesso se concentram · 00:38–00:43 → **Recorrência e acesso por atenção**
- Slide 10 · Acesso em vez de compressão · 01:05–01:17 → **Recorrência e acesso por atenção**
- Slide 12 · Q, K, V: três papéis antes de três matrizes · 01:28–01:39 → **Self-attention: da entrada ao contexto**
- Slide 14 · Fechamento: se a atenção dá acesso, para que serve a recorrência? · 01:50–02:00 → **Recorrência e acesso por atenção**
- Medição 1 — o produto que decide o gradiente (3 min) → **Recorrência e acesso por atenção**
- Medição 2 — a compressão em quatro números (5 min) → **Recorrência e acesso por atenção**
- "Escreve o LSTM inteiro?" → **A.3** · 7 min no quadro → **Recorrência e acesso por atenção**
- "Qual é a ponte de Bahdanau até `softmax(QKᵀ/√d_k)V`?" → **A.6** · 6 min no quadro → **Self-attention: da entrada ao contexto**

## Aula 06

Mapas disponíveis: percurso da aula; Bloco encoder com pós-normalização; Encoder–decoder: dois caminhos se encontram; KV cache: reutilizar o passado; Self-attention: da entrada ao contexto; Bloco Transformer com pré-normalização; Geração autorregressiva.

- Slide 3 · Como a self-attention combina informações · 00:10–00:16 → **Self-attention: da entrada ao contexto**
- Slide 4 · Q, K, V: três papéis, uma entrada · 00:16–00:23 → **Self-attention: da entrada ao contexto**
- Slide 5 · Lendo a fórmula de atenção · 00:23–00:33 → **Self-attention: da entrada ao contexto**
- Slide 7 · [Demo] Observando os pesos de atenção · 00:43–00:55 → **Self-attention: da entrada ao contexto**
- Slide 8 · Máscara causal: usando apenas o contexto disponível · 01:05–01:14 → **Self-attention: da entrada ao contexto**
- Slide 11 · Encoder, decoder e cross-attention · 01:29–01:35 → **Encoder–decoder: dois caminhos se encontram**
- Slide 12 · Geração token a token e KV cache · 01:35–01:39 → **KV cache: reutilizar o passado**
- 3. “Por que não zerar os pesos depois?” → A.3 · 5 min → **Bloco Transformer com pré-normalização**

## Aula 07

Mapas disponíveis: percurso da aula; RoPE: posição dentro do score; Bloco Transformer com pré-normalização.

- Slide 5 · A terceira resposta: a posição entra dentro do score · 00:24–00:35 → **RoPE: posição dentro do score**
- Slide 6 · Por que RoPE venceu, e o que ele não resolve · 00:35–00:43 → **RoPE: posição dentro do score**
- Slide 9 · Qual norma: LayerNorm × RMSNorm · 01:12–01:19 → **Bloco Transformer com pré-normalização**
- Slide 10 · Onde a norma entra muda o treino · 01:19–01:27 → **Bloco Transformer com pré-normalização**
- Slide 11 · Onde estão dois terços dos pesos · 01:27–01:34 → **Bloco Transformer com pré-normalização**
- Slide 12 · O bloco moderno, consolidado · 01:34–01:39 → **Bloco Transformer com pré-normalização**
- Slide 14 · Fechamento: o bloco está pronto; falta decidir como conectá-lo · 01:50–02:00 → **Bloco Transformer com pré-normalização**
- Medição 4 — RoPE: o mesmo score dentro e fora do treino (6 min) → **RoPE: posição dentro do score**

## Aula 08

Mapas disponíveis: percurso da aula; Encoder–decoder: dois caminhos se encontram; KV cache: reutilizar o passado; Geração autorregressiva.

- Slide 6 · Encoder-decoder: quando entrada e saída são objetos diferentes · 00:44–00:49 → **Encoder–decoder: dois caminhos se encontram**
- Slide 7 · Decoder-only: por que prever o próximo token venceu · 00:49–00:55 → **Geração autorregressiva**
- Slide 8 · O preço da janela: o KV cache em números · 01:05–01:14 → **KV cache: reutilizar o passado**
- Slide 10 · MQA e GQA: cortar o KV cache pela raiz · 01:22–01:31 → **KV cache: reutilizar o passado**

## Aula 09

Mapas disponíveis: percurso da aula; Self-attention: da entrada ao contexto; Bloco Transformer com pré-normalização; Geração autorregressiva; Treinamento por próximo token; Laboratório: da hipótese à evidência.

- Slide 2 · Setup e os números deste lab · 00:05–00:11 → **Laboratório: da hipótese à evidência**
- Slide 3 · O mapa: cinco checkpoints e o entregável · 00:11–00:15 → **Laboratório: da hipótese à evidência**
- Slide 4 · [Demo] Live coding: scaled dot-product attention do zero · 00:15–00:35 → **Self-attention: da entrada ao contexto**
- Slide 5 · [Checkpoint 1] Atenção causal · 00:35–00:50 → **Self-attention: da entrada ao contexto**
- Slide 6 · [Checkpoint 2] Multi-head · 00:50–01:05 → **Laboratório: da hipótese à evidência**
- Slide 7 · [Checkpoint 3] O bloco completo · 01:15–01:27 → **Bloco Transformer com pré-normalização**
- Slide 8 · [Checkpoint 4] Treinar, gerar, medir perplexidade · 01:27–01:42 → **Geração autorregressiva**
- Slide 9 · [Checkpoint 5] Variar hiperparâmetros e comparar · 01:42–01:50 → **Laboratório: da hipótese à evidência**

## Aula 10

Mapas disponíveis: percurso da aula; MoE: rotear e combinar especialistas; KV cache: reutilizar o passado; Geração autorregressiva.

- Slide 5 · MoE: a peça trocada que fecha o ticket 3 · 00:31–00:42 → **MoE: rotear e combinar especialistas**
- Slide 6 · O defeito característico do MoE: ninguém supervisiona o roteador · 00:42–00:55 → **MoE: rotear e combinar especialistas**
- Slide 9 · Beam search: acerta o alvo errado · 01:12–01:17 → **Geração autorregressiva**

## Aula 11

Mapas disponíveis: percurso da aula; Geração autorregressiva; Laboratório: da hipótese à evidência.

- Slide 3 · O mapa: cinco checkpoints e o mini-relatório · 00:10–00:15 → **Laboratório: da hipótese à evidência**
- Slide 4 · [Demo] Uma pergunta, seis decodificações · 00:15–00:35 → **Geração autorregressiva**
- Slide 5 · [Checkpoint 1] Decodificação implementada e medida · 00:35–00:50 → **Geração autorregressiva**
- Slide 6 · [Checkpoint 2] Few-shot e o colapso de formato · 00:50–01:05 → **Laboratório: da hipótese à evidência**
- Slide 7 · [Checkpoint 3] Chain-of-thought e o preço do raciocínio · 01:15–01:27 → **Laboratório: da hipótese à evidência**
- Slide 8 · [Checkpoint 4] A tabela dos três eixos · 01:27–01:40 → **Laboratório: da hipótese à evidência**
- Slide 9 · [Checkpoint 5] Modelo local pequeno × modelo de API · 01:40–01:50 → **Laboratório: da hipótese à evidência**
- Slide 10 · Recolhimento: o mini-relatório e a ponte para a Aula 12 · 01:50–02:00 → **Laboratório: da hipótese à evidência**

## Aula 12

Mapas disponíveis: percurso da aula; Treinamento por próximo token.

- Slide 3 · Transferência de aprendizado: um treino caro, muitas tarefas baratas · 00:10–00:15 → **Treinamento por próximo token**
- Slide 4 · O rótulo que não existe: o supervisor é o corpus · 00:15–00:20 → **Treinamento por próximo token**
- Slide 5 · De onde vem o texto: a mistura do corpus · 00:20–00:26 → **Treinamento por próximo token**
- Slide 7 · Leis de escala: a perda cai como lei de potência · 00:33–00:40 → **Treinamento por próximo token**

## Aula 13

Mapas disponíveis: percurso da aula; LoRA: dois caminhos, uma saída.

- Slide 10 · LoRA: um delta de baixo posto sobre pesos congelados · 01:11–01:19 → **LoRA: dois caminhos, uma saída**
- Slide 11 · A conta dos parâmetros treináveis: 0,60% · 01:19–01:25 → **LoRA: dois caminhos, uma saída**
- Slide 12 · Quantização: duas finalidades que se confundem · 01:25–01:31 → **LoRA: dois caminhos, uma saída**
- Slide 13 · QLoRA: base congelada em 4 bits + adaptador em precisão alta · 01:31–01:38 → **LoRA: dois caminhos, uma saída**

## Aula 14

Mapas disponíveis: percurso da aula; LoRA: dois caminhos, uma saída; Laboratório: da hipótese à evidência.

- Slide 1 · Abertura: ontem a conta, hoje o adaptador · 00:00–00:05 → **LoRA: dois caminhos, uma saída**
- Slide 3 · O mapa: cinco checkpoints e o entregável · 00:11–00:15 → **Laboratório: da hipótese à evidência**
- Slide 5 · [Checkpoint 1] Carregar em 4 bits e capturar a linha de base · 00:35–00:50 → **Laboratório: da hipótese à evidência**
- Slide 6 · [Checkpoint 2] Dataset e template de chat · 00:50–01:05 → **Laboratório: da hipótese à evidência**
- Slide 7 · [Checkpoint 3] LoRA e a conta dos treináveis · 01:15–01:25 → **LoRA: dois caminhos, uma saída**
- Slide 8 · [Checkpoint 4] Treinar e registrar · 01:25–01:38 → **Laboratório: da hipótese à evidência**
- Slide 9 · [Checkpoint 5] Antes × depois, controle e o adaptador · 01:38–01:50 → **LoRA: dois caminhos, uma saída**

## Aula 15

Mapas disponíveis: percurso da aula; Preferências: duas rotas de ajuste.

- Slide 4 · O dado que muda o objetivo · 00:21–00:28 → **Preferências: duas rotas de ajuste**
- Slide 6 · O reward model é um proxy congelado · 00:36–00:43 → **Preferências: duas rotas de ajuste**
- Slide 8 · O LLM como política, e o crédito que não chega · 01:05–01:10 → **Preferências: duas rotas de ajuste**
- Slide 9 · PPO: por que o passo precisa ser cortado · 01:10–01:16 → **Preferências: duas rotas de ajuste**
- Slide 13 · DPO: a conta que apaga o modelo de recompensa · 01:34–01:41 → **Preferências: duas rotas de ajuste**
- Slide 15 · DPO × PPO: o critério de escolha · 01:50–01:55 → **Preferências: duas rotas de ajuste**

## Aula 16

Mapas disponíveis: percurso da aula; Tentativas, seleção e recompensa verificável.

- Slide 1 · O sintoma: acerta com dez tentativas, erra com uma · 00:00–00:10 → **Tentativas, seleção e recompensa verificável**
- Slide 6 · O fundamento nomeado: `pass@k` · 00:32–00:39 → **Tentativas, seleção e recompensa verificável**
- Slide 7 · `consensus@k`: o que o verificador compra · 00:39–00:45 → **Tentativas, seleção e recompensa verificável**
- Slide 9 · Recompensa verificável: o professor automático · 01:05–01:12 → **Tentativas, seleção e recompensa verificável**
- Slide 10 · GRPO: a linha de base sai do próprio grupo · 01:12–01:21 → **Tentativas, seleção e recompensa verificável**
- Slide 11 · GRPO × PPO, lado a lado · 01:21–01:27 → **Tentativas, seleção e recompensa verificável**
- Slide 14 · [Exercício] Quem tem verificador, e o que ele não confere · 01:38–01:50 → **Tentativas, seleção e recompensa verificável**

## Aula 17

Mapas disponíveis: percurso da aula; Self-attention: da entrada ao contexto; Geração autorregressiva; Treinamento por próximo token; LoRA: dois caminhos, uma saída; Preferências: duas rotas de ajuste.

O percurso permanece disponível na área Fluxogramas. Não foi inserido um mecanismo em títulos sem correspondência clara.

## Aula 18

Mapas disponíveis: percurso da aula; Projeto: do problema à defesa; RAG: do acervo à resposta com fontes.

- Slide 5 · RAG: anexar memória não-paramétrica · 00:25–00:32 → **RAG: do acervo à resposta com fontes**
- Slide 7 · Chunking: onde a maioria dos RAGs morre · 00:40–00:45 → **RAG: do acervo à resposta com fontes**
- Slide 12 · [Projeto] Quarenta por cento da nota começa agora · 01:30–01:37 → **Projeto: do problema à defesa**
- Slide 13 · [Projeto] Requisitos, entregas e regras do jogo · 01:37–01:44 → **Projeto: do problema à defesa**

## Aula 19

Mapas disponíveis: percurso da aula; Entrada externa até uma ação autorizada; Busca híbrida: ramificar, fundir, reordenar.

- Slide 4 · BM25: o índice remissivo que ainda ganha · 00:18–00:27 → **Busca híbrida: ramificar, fundir, reordenar**
- Slide 6 · Fusão: por que somar score é errado e RRF funciona · 00:35–00:42 → **Busca híbrida: ramificar, fundir, reordenar**
- Slide 7 · [Demo] Três estratégias, três rankings · 00:42–00:55 → **Busca híbrida: ramificar, fundir, reordenar**
- Slide 8 · Bi-encoder × cross-encoder: quando a consulta encontra o documento · 01:05–01:14 → **Entrada externa até uma ação autorizada**
- Slide 9 · Dois estágios: recuperar 50, reordenar, entregar 5 · 01:14–01:21 → **Busca híbrida: ramificar, fundir, reordenar**
- Slide 11 · Por que recall@k é a primeira coisa a depurar · 01:29–01:35 → **Busca híbrida: ramificar, fundir, reordenar**
- Slide 13 · Modos de falha — e o documento que dá ordens · 01:39–01:42 → **Entrada externa até uma ação autorizada**

## Aula 20

Mapas disponíveis: percurso da aula; RAG: do acervo à resposta com fontes; Busca híbrida: ramificar, fundir, reordenar; Laboratório: da hipótese à evidência.

- Slide 1 · Abertura: hoje o RAG sai do slide e vira número · 00:00–00:05 → **RAG: do acervo à resposta com fontes**
- Slide 2 · Setup, corpus embutido e modo degradado · 00:05–00:11 → **RAG: do acervo à resposta com fontes**
- Slide 3 · O mapa: seis checkpoints e o que eu recolho · 00:11–00:15 → **Laboratório: da hipótese à evidência**
- Slide 4 · [Demo] O RAG mínimo em nove linhas · 00:15–00:35 → **RAG: do acervo à resposta com fontes**
- Slide 5 · Checkpoint 1 — Chunking com metadados · 00:35–00:48 → **RAG: do acervo à resposta com fontes**
- Slide 6 · Checkpoint 2 — Indexar e buscar por vetor · 00:48–01:05 → **Laboratório: da hipótese à evidência**
- Slide 7 · Checkpoint 3 — BM25 e fusão por posição · 01:15–01:24 → **Busca híbrida: ramificar, fundir, reordenar**
- Slide 8 · Checkpoint 4 — Reranking e a conta de inferências · 01:24–01:32 → **Busca híbrida: ramificar, fundir, reordenar**
- Slide 9 · Checkpoint 5 — Responder citando as fontes · 01:32–01:40 → **RAG: do acervo à resposta com fontes**
- Slide 10 · Checkpoint 6 — As dezoito consultas e a tabela · 01:40–01:50 → **Laboratório: da hipótese à evidência**

## Aula 21

Mapas disponíveis: percurso da aula; MCP: conectar, descobrir e chamar; Tool calling: proposta, execução e retorno.

- Slide 4 · Anatomia da chamada: o JSON na tela · 00:18–00:25 → **Tool calling: proposta, execução e retorno**
- Slide 5 · O schema é parte do prompt · 00:25–00:33 → **Tool calling: proposta, execução e retorno**
- Slide 8 · Seis propriedades de uma boa ferramenta · 01:05–01:15 → **Tool calling: proposta, execução e retorno**
- Slide 9 · O catálogo das más ferramentas · 01:15–01:23 → **Tool calling: proposta, execução e retorno**
- Slide 10 · O problema N×M · 01:23–01:29 → **MCP: conectar, descobrir e chamar**
- Slide 11 · MCP: host, cliente, servidor · 01:29–01:38 → **MCP: conectar, descobrir e chamar**
- Slide 12 · Recurso, ferramenta e prompt: quem decide · 01:38–01:43 → **Tool calling: proposta, execução e retorno**
- Slide 13 · [Exercício] Reescrever o schema ruim · 01:43–01:50 → **Tool calling: proposta, execução e retorno**

## Aula 22

Mapas disponíveis: percurso da aula; MCP: conectar, descobrir e chamar; Projeto: do problema à defesa; Tool calling: proposta, execução e retorno; Laboratório: da hipótese à evidência.

- Slide 1 · Abertura: hoje vocês escrevem o host · 00:00–00:05 → **Tool calling: proposta, execução e retorno**
- Slide 2 · Entrega 1: como eu recolho agora · 00:05–00:10 → **Projeto: do problema à defesa**
- Slide 3 · Setup, chaves e o modo offline · 00:10–00:15 → **Laboratório: da hipótese à evidência**
- Slide 4 · [Demo] O loop desenrolado à mão · 00:15–00:35 → **Tool calling: proposta, execução e retorno**
- Slide 5 · Checkpoint 1 — Os três schemas e a validação · 00:35–00:48 → **Tool calling: proposta, execução e retorno**
- Slide 6 · Checkpoint 2 — O loop na mão · 00:48–01:05 → **Tool calling: proposta, execução e retorno**
- Slide 7 · Checkpoint 3 — Cliente MCP contra um servidor que já existe · 01:15–01:27 → **MCP: conectar, descobrir e chamar**
- Slide 8 · Checkpoint 4 — Seu próprio servidor MCP · 01:27–01:40 → **MCP: conectar, descobrir e chamar**
- Slide 9 · Entrega 1: os cinco itens que eu olho numa proposta · 01:40–01:50 → **Projeto: do problema à defesa**

## Aula 23

Mapas disponíveis: percurso da aula; Agente: um ciclo com verificação e parada.

- Slide 3 · O ciclo: observar, planejar, agir, refletir · 00:10–00:18 → **Agente: um ciclo com verificação e parada**
- Slide 4 · ReAct: intercalar raciocínio e ação · 00:18–00:28 → **Agente: um ciclo com verificação e parada**
- Slide 5 · Planejamento e decomposição · 00:28–00:36 → **Agente: um ciclo com verificação e parada**
- Slide 6 · Memória de curto prazo é a trajetória · 00:36–00:44 → **Agente: um ciclo com verificação e parada**
- Slide 7 · Memória de longo prazo · 00:44–00:50 → **Agente: um ciclo com verificação e parada**
- Slide 8 · Reflexão e autocorreção — e o limite dela · 00:50–00:55 → **Agente: um ciclo com verificação e parada**
- Slide 9 · [Demo] O loop em 40 linhas · 01:05–01:18 → **Agente: um ciclo com verificação e parada**
- Slide 11 · Custo e latência do loop · 01:28–01:34 → **Agente: um ciclo com verificação e parada**
- Slide 12 · Paradas mal projetadas · 01:34–01:40 → **Agente: um ciclo com verificação e parada**
- Parte 2 — Demonstração guiada → **Agente: um ciclo com verificação e parada**

## Aula 24

Mapas disponíveis: percurso da aula; Orquestrador e trabalhadores.

- Slide 4 · Padrão 1: orquestrador-trabalhadores · 00:20–00:30 → **Orquestrador e trabalhadores**
- Slide 9 · Coordenação: contexto não se compartilha de graça · 01:13–01:18 → **Orquestrador e trabalhadores**
- Slide 10 · Orçamento compartilhado e custo multiplicado · 01:18–01:24 → **Orquestrador e trabalhadores**

## Aula 25

Mapas disponíveis: percurso da aula; Tool calling: proposta, execução e retorno; Agente: um ciclo com verificação e parada; Laboratório: da hipótese à evidência.

- Slide 2 · Setup, o modo offline e os números deste lab · 00:05–00:11 → **Laboratório: da hipótese à evidência**
- Slide 3 · O mapa: cinco checkpoints e o entregável · 00:11–00:15 → **Laboratório: da hipótese à evidência**
- Slide 4 · [Demo] Live coding: o contrato de formato e o parser · 00:15–00:35 → **Tool calling: proposta, execução e retorno**
- Slide 5 · [Checkpoint 1] Prompt de sistema, parsing e despacho · 00:35–00:48 → **Tool calling: proposta, execução e retorno**
- Slide 6 · [Checkpoint 2] O loop: memória, observação e parada · 00:48–01:05 → **Tool calling: proposta, execução e retorno**
- Slide 7 · [Checkpoint 3] A base do Lab 5 vira ferramenta · 01:15–01:24 → **Tool calling: proposta, execução e retorno**
- Slide 8 · [Checkpoint 4] Registrar e analisar a trajetória · 01:24–01:38 → **Agente: um ciclo com verificação e parada**
- Slide 9 · [Checkpoint 5] O mesmo agente num framework · 01:38–01:50 → **Laboratório: da hipótese à evidência**
- Parte 2 — Demonstração guiada → **Agente: um ciclo com verificação e parada**

## Aula 26

Mapas disponíveis: percurso da aula; Entrada externa até uma ação autorizada; Projeto: do problema à defesa; Agente: um ciclo com verificação e parada; Avaliação: do caso à decisão.

- Slide 2 · A tese: dado e instrução entram pelo mesmo canal · 00:05–00:10 → **Entrada externa até uma ação autorizada**
- Slide 3 · Injeção direta: o usuário é o atacante · 00:10–00:16 → **Entrada externa até uma ação autorizada**
- Slide 4 · Injeção indireta: o atacante nunca fala com o sistema · 00:16–00:24 → **Entrada externa até uma ação autorizada**
- Slide 5 · Exfiltração de dados: o canal de saída também é superfície · 00:24–00:30 → **Entrada externa até uma ação autorizada**
- Slide 6 · Ações irreversíveis: a diferença entre erro e dano · 00:30–00:36 → **Entrada externa até uma ação autorizada**
- Slide 7 · [Demo] O documento envenenado no acervo do Lab 7 · 00:36–00:48 → **Entrada externa até uma ação autorizada**
- Slide 8 · As cinco mitigações, e o que cada uma deixa aberto · 00:48–00:55 → **Entrada externa até uma ação autorizada**
- Slide 9 · Avaliar agente: a falha pode estar em cinco etapas · 01:05–01:12 → **Avaliação: do caso à decisão**
- Slide 12 · Registrar trajetórias, não só respostas · 01:24–01:29 → **Agente: um ciclo com verificação e parada**
- Slide 14 · [Entrega 2] O checkpoint do projeto · 01:35–01:50 → **Projeto: do problema à defesa**
- Parte 2 — Demonstração guiada → **Agente: um ciclo com verificação e parada**

## Aula 27

Mapas disponíveis: percurso da aula; Classificação: das previsões à métrica; Avaliação: do caso à decisão.

- Slide 3 · As sete camadas, e a regra de ouro · 00:10–00:18 → **Avaliação: do caso à decisão**
- Slide 4 · [Exercício] De que camada é essa falha? · 00:18–00:26 → **Avaliação: do caso à decisão**
- Slide 6 · Avaliação humana: a rubrica é o instrumento · 00:32–00:39 → **Avaliação: do caso à decisão**
- Slide 7 · Acordo de 84% e kappa de 0,11 · 00:39–00:48 → **Avaliação: do caso à decisão**
- Slide 9 · LLM-as-judge: pairwise × rubrica · 01:05–01:11 → **Avaliação: do caso à decisão**
- Slide 10 · O juiz que muda de opinião quando eu troco a ordem · 01:11–01:19 → **Avaliação: do caso à decisão**
- Slide 12 · Calibrar antes de escalar · 01:29–01:35 → **Avaliação: do caso à decisão**

## Aula 28

Mapas disponíveis: percurso da aula; Avaliação: do caso à decisão; Laboratório: da hipótese à evidência.

- Slide 1 · Abertura: hoje a avaliação do projeto de vocês vira número · 00:00–00:05 → **Avaliação: do caso à decisão**
- Slide 3 · O mapa: cinco checkpoints, e o harness roda antes de o sistema entrar · 00:10–00:15 → **Laboratório: da hipótese à evidência**
- Slide 5 · Checkpoint 1 — O conjunto que discrimina · 00:35–00:50 → **Laboratório: da hipótese à evidência**
- Slide 6 · Checkpoint 2 — Métricas por camada, com denominador visível · 00:50–01:05 → **Avaliação: do caso à decisão**
- Slide 7 · Checkpoint 3 — A rubrica é o instrumento · 01:15–01:25 → **Avaliação: do caso à decisão**
- Slide 8 · Checkpoint 4 — Calibrar o juiz e reportar a concordância · 01:25–01:37 → **Avaliação: do caso à decisão**
- Slide 9 · Checkpoint 5 — Falha na menor camada, e conserto por prioridade · 01:37–01:47 → **Avaliação: do caso à decisão**
- Slide 10 · O critério: número por camada, e o que não conta · 01:47–01:50 → **Avaliação: do caso à decisão**

## Aula 29

Mapas disponíveis: percurso da aula; Uma imagem como sequência de representações; Geração autorregressiva.

- Slide 6 · O token não é sobre texto: ViT e o patch de 16×16 · 01:05–01:11 → **Uma imagem como sequência de representações**
- Slide 7 · [Demo] A conta: 375 tokens de texto contra 3.430 patches · 01:11–01:21 → **Uma imagem como sequência de representações**
- Slide 8 · Comprimir contexto em pixels: DeepSeek-OCR · 01:21–01:27 → **Uma imagem como sequência de representações**

## Aula 30

Mapas disponíveis: percurso da aula; Projeto: do problema à defesa; Avaliação: do caso à decisão.

- Slide 3 · Os critérios, projetados · projetado na pausa técnica → **Projeto: do problema à defesa**
