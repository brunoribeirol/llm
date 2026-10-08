# Demonstrações completas do curso

31 demonstrações, 381 etapas visuais. Cada aula abre diretamente na demonstração interativa. O percurso de 20 etapas da aula 06 foi preservado.

Cada percurso contém visualizações próprias do tema, controles, explicação, orientação para observar os resultados e pergunta com resposta. O professor também recebe fala sugerida e orientação para o quadro. Os valores são calculados localmente ou identificados como simulações didáticas.

As 552 etapas de estudo originais continuam na aba **Passo a passo**. Os experimentos Python continuam como complementos abaixo de cada demonstração.

| Aula | Tema | Etapas visuais |
|---|---|---:|
| 00 | Aula 0 — Recepção: o mapa do curso, os materiais e o ambiente | 10 |
| 01 | Apresentação da disciplina; panorama de LLMs; tarefas e métricas de NLP | 12 |
| 02 | Tokenização | 12 |
| 03 | Embeddings e representações vetoriais | 12 |
| 04 | Laboratório 1: Tokenizadores e embeddings | 12 |
| 05 | Modelos sequenciais e o nascimento da atenção | 12 |
| 06 | Transformer I: self-attention e a arquitetura | 20 |
| 07 | Transformer II: posição, normalização e o bloco moderno | 12 |
| 08 | Famílias de modelos e atenção eficiente | 12 |
| 09 | Laboratório 2: Mini-GPT do zero em PyTorch | 12 |
| 10 | Do Transformer ao LLM: escala, MoE, decodificação e prompting | 14 |
| 11 | Laboratório 3: Decodificação e prompting na prática | 12 |
| 12 | Pré-treinamento: dados, leis de escala e sistemas | 13 |
| 13 | SFT e fine-tuning eficiente: LoRA e QLoRA | 12 |
| 14 | Laboratório 4: Fine-tuning com LoRA/QLoRA | 12 |
| 15 | Alinhamento: RLHF, PPO e DPO | 12 |
| 16 | Modelos de raciocínio: GRPO e DeepSeek-R1 | 13 |
| 17 | Prova (conteúdo das Aulas 1 a 16) | 9 |
| 18 | RAG I: geração aumentada por recuperação | 12 |
| 19 | RAG II: retrieval híbrido, reranking e métricas | 13 |
| 20 | Laboratório 5: Pipeline RAG completo | 13 |
| 21 | Tool calling e Model Context Protocol (MCP) | 12 |
| 22 | Laboratório 6: Tool calling e MCP — Entrega 1 do projeto | 12 |
| 23 | Agentes de IA: loops, planejamento e memória | 12 |
| 24 | Sistemas multiagente e orquestração | 12 |
| 25 | Laboratório 7: Construindo um agente autônomo | 12 |
| 26 | Segurança e avaliação de agentes | 12 |
| 27 | Avaliação de LLMs e de sistemas com LLMs | 14 |
| 28 | Laboratório 8: Harness de avaliação do projeto | 12 |
| 29 | Recapitulação e fronteiras da área | 12 |
| 30 | Apresentações finais — Entrega final do projeto | 10 |

## Como demonstrar

1. Abra uma aula: a demonstração completa é a tela inicial.
2. Navegue pela lista lateral ou pelos botões Voltar e Avançar.
3. Leia a previsão/pergunta, altere os controles e compare os valores.
4. Use Restaurar controles para repetir a experiência inicial.
5. Para projetar, ative Modo projeção na demonstração ou Modo apresentação no portal.
6. Em Materiais, baixe o HTML autônomo e, no perfil professor, o roteiro da demonstração.

Os roteiros separados estão em `demos/roteiros/roteiro-demonstracao-aula-NN.md`. A versão HTML do estudante é gerada sem os dados de fala e quadro do professor. A aula 17 é revisão inédita, sem a prova oficial ou seu gabarito; a aula 30 ensaia a apresentação, sem substituir os critérios oficiais.

## Autoria e manutenção

- Conteúdo: `demos/lessons/NN.json`.
- Cálculos e visualizações: `demos/simulators-foundations.js`, `simulators-training.js`, `simulators-systems.js`.
- Apresentação compartilhada: `demos/player.html`, `player.css`, `player.js`, `helpers.js`.
- Integração e separação de perfis: `demos.py`.
- Atualização deste mapa e dos roteiros: `python scripts/build_demo_scripts.py`, executado na pasta portal.

Após editar o conteúdo JSON, reinicie o Streamlit para renovar o cache do catálogo de demonstrações.
