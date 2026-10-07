---
aula: 29
titulo: "Recapitulação e fronteiras da área"
modulo: "7 — Fronteiras e Encerramento"
tipo: teorica
semana: 15
duracao_min: 120
versao: v2
---

# Aula 29 — Recapitulação e fronteiras da área

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** Esta aula já era conduzida pela aplicação: abre pelo percurso da própria
> turma e seleciona cada fronteira pelo pressuposto do curso que ela ameaça. O transporte preservou
> o fluxo e os 15 slides. Duas coisas entraram. O **slide 2 ganhou uma segunda coluna** — o mapa de
> onde está o fundamento formal de cada camada — porque esta é a última aula de conteúdo e é aqui
> que o aluno vê que os apêndices formam um corpo, não uma coleção de anexos. E entrou um
> **apêndice de três itens** com o formalismo que **nasce** nesta aula: a difusão mascarada, a
> recursão do colapso de modelo, e a intensidade aritmética que explica o gargalo de memória.
> Carga horária, numeração e objetivos inalterados. Índice do apêndice ao fim deste plano.

## 1. Objetivo da aula

Fechar o arco: mostrar o stack completo — token, atenção, pré-treino, SFT, preferências, raciocínio, RAG, ferramentas, agentes, avaliação — como **um percurso que a turma construiu**, com a aula em que cada peça foi feita **e o item de apêndice que a sustenta**, e cobrar explicitamente a promessa da Aula 1 (a dívida de avaliação foi paga nas Aulas 27 e 28). Na segunda metade, abrir as fronteiras que atacam os pressupostos do próprio curso: o token como abstração independente de modalidade, geração não-autorregressiva, contexto comprimido em pixels, dados sintéticos que corroem a distribuição, e a fronteira do custo.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Reconstruir** o stack de um LLM em sete camadas e **localizar** em qual aula e em qual lab cada camada foi construída, apontando o artefato produzido.
2. **Enunciar** a dívida de avaliação anunciada na Aula 1 — o modelo foi unificado sob o próximo-token, as métricas não foram — e **demonstrar** com que instrumentos das Aulas 27 e 28 ela foi paga.
3. **Explicar** por que um patch de imagem 16×16 é tratável como token e **generalizar** a abstração "sequência de vetores discretizados" para além do texto.
4. **Distinguir** geração autorregressiva de geração por difusão mascarada (LLaDA) e **identificar** três decisões do curso — KV cache, decodificação, prompting — que deixam de valer quando o modelo não gera da esquerda para a direita.
5. **Calcular** a razão entre tokens de texto e tokens visuais de uma mesma página e **argumentar** por onde entra a compressão em DeepSeek-OCR — pelo encoder que reduz, não pela fatia em patches.
6. **Descrever** o mecanismo do colapso de modelo (perda das caudas da distribuição por realimentação recursiva) e **propor** duas práticas de curadoria que o mitigam.
7. **Justificar** a eficiência como métrica de primeira classe, usando o argumento de que a atenção na decodificação é limitada por banda de memória e não por FLOPs.
8. **Diferenciar** os caminhos de pesquisa e de engenharia de IA em termos de artefato produzido e de critério de sucesso.

*(Idênticos aos da V1 — a reorganização não muda o que o aluno deve saber fazer.)*

## 3. Teoria aplicada

### Bloco 1 (00:10–00:55) — O percurso: onde cada peça foi construída, e onde está o fundamento dela

Este bloco é a recapitulação, e ela tem uma regra: **nada de resumo abstrato**. Cada peça é nomeada com a aula em que foi construída e o artefato que ficou no repositório do aluno. O objetivo é que o aluno reconheça o próprio percurso — não que ele reveja conteúdo.

**Conceito 1 — O mapa do percurso, agora com dois endereços.**
O stack, de baixo para cima, com a aula e o lab de cada peça: **token** (Aula 2, Lab 1 na Aula 4); **representação vetorial** (Aula 3, Lab 1); **atenção e o bloco Transformer** (Aulas 5 a 8, Lab 2 na Aula 9); **escala, MoE e decodificação** (Aula 10, Lab 3 na Aula 11); **pré-treino e leis de escala** (Aula 12); **SFT e PEFT** (Aula 13, Lab 4 na Aula 14); **preferências e raciocínio** (Aulas 15 e 16); **RAG** (Aulas 18 e 19, Lab 5 na Aula 20); **ferramentas e MCP** (Aula 21, Lab 6 na Aula 22); **agentes e multiagente** (Aulas 23 a 25, Lab 7); **segurança** (Aula 26); **avaliação** (Aula 27, Lab 8 na Aula 28).

**Novo na V2:** cada camada carrega um **segundo endereço** — o item de apêndice que a sustenta. A derivação da atenção em quatro etapas com a variância do produto escalar e a equivariância por permutação; o fator 6 do `C ≈ 6ND`; `ΔW = BA` com a contagem de parâmetros; Bradley-Terry; o estimador não-viesado de `pass@k`; BM25 e as quatro métricas; kappa de Cohen e o intervalo de Wilson.

Esta segunda coluna tem função própria e é a razão de ela existir só aqui: **é a única vez no curso em que os apêndices aparecem juntos.** Ao longo do semestre eles chegaram um por aula, e é fácil ler cada um como anexo solto. Vistos em conjunto, formam o índice do formalismo da disciplina — o material que não expira quando a fronteira mudar, e de onde saem os 40 pontos de justificativa da prova.

*Analogia do instrutor:* a coluna da esquerda é o `git log` da disciplina; cada aula é um commit e o aluno aponta o diff. A da direita é a documentação de projeto que explica por que cada commit é daquele jeito.
*Erro conceitual comum:* achar que o curso foi uma lista de tópicos. Foi uma pilha: cada camada só faz sentido porque a de baixo existe, e o Lab 8 mede exatamente as camadas que os Labs 1 a 7 construíram.

**Conceito 2 — A tese do próximo-token, revisitada com o que a turma sabe agora.**
Na Aula 1 a tese era afirmação a crédito. Agora é verificável em três níveis, cada um com sua aula. **Mecanismo:** o Transformer decoder com máscara causal (Aula 6) produz, por construção, uma distribuição sobre o próximo token — a tarefa não é escolhida, é a arquitetura. **Interface:** classificação, rotulagem e geração passam a ser instâncias do mesmo objeto porque a saída é texto e a especificação entra no prompt (Aula 10, Lab 3). **Utilidade:** o que transformou o completador em assistente foi SFT e alinhamento (Aulas 13 e 15), não arquitetura.
*Erro conceitual comum:* concluir que "tudo é geração, então tudo é fácil". A unificação moveu a dificuldade — ela não a eliminou. É o que o Conceito 3 cobra.

**Conceito 3 — A dívida de avaliação, e a cobrança.**
A Aula 1 fechou com uma promessa incômoda: **unificamos o modelo, não as métricas.** BLEU e ROUGE pressupõem referência aproximadamente única; perplexidade só compara entre tokenizadores iguais; acurácia mente em dados desbalanceados. Quando a interface virou geração aberta, a área herdou um instrumento que não mede o que passou a existir.
A dívida foi paga em dois movimentos. **Aula 27**, conceitual: "esse modelo é bom?" foi substituída por "qual a menor camada que explica esta falha, e com que número eu a meço?"; rubrica com níveis observáveis; kappa de Cohen no lugar do acordo bruto; LLM-as-judge com os três vieses nomeados; factualidade por afirmações atômicas; contaminação e o limite do leaderboard. **Aula 28**, operacional: cada equipe construiu o harness do próprio sistema, com métrica por camada, `n` declarado, juiz calibrado e falhas priorizadas.
*Frase de fechamento do bloco:* a Aula 1 prometeu que o custo da unificação tinha sido transferido para a avaliação. As Aulas 27 e 28 são a fatura paga — e o comprovante é a tabela que cada equipe leva para a Aula 30.
*Erro conceitual comum:* achar que a dívida foi paga porque agora existe uma métrica melhor. Não existe métrica melhor; existem **decomposição em camadas** e **procedência declarada do número**. É o método que quita, não uma fórmula.

**Conceito 4 — O que o curso deliberadamente não cobriu.**
Honestidade de escopo, porque ela orienta o estudo seguinte: pré-treino de verdade em escala (o Lab 2 é um mini-GPT em corpus de brinquedo); RLHF completo com modelo de recompensa treinado (as Aulas 15 e 16 param na formulação e no DPO); serving em produção com batching contínuo e autoescala; multimodalidade de fato (é fronteira desta aula, não conteúdo praticado); segurança adversarial ofensiva além do que a Aula 26 introduziu; e avaliação com significância estatística — o curso exigiu `n` declarado, e o intervalo de confiança ficou no apêndice do Lab 8, não na prática.
*Erro conceitual comum:* confundir "vimos" com "sei fazer em produção". A distância entre as duas coisas é justamente a lista acima.

### Bloco 2 (01:05–01:50) — Fronteiras: o que ataca os pressupostos deste curso

O critério de seleção deste bloco não é novidade: é **qual pressuposto do curso cada fronteira ameaça**. Uma fronteira que não desestabiliza nada do que a turma aprendeu é notícia, não fronteira. A convenção do deck é que cada slide do Bloco 2 traz num canto o pressuposto que ele ataca.

**Conceito 5 — O token como abstração independente de modalidade (ViT).**
O Vision Transformer (Dosovitskiy et al., arXiv 2010.11929) faz uma coisa só: corta a imagem em patches de 16×16, projeta cada patch linearmente num vetor de dimensão `d`, soma um embedding de posição e joga a sequência num Transformer encoder comum. Nada da arquitetura sabe que é imagem. O que isso revela é que o objeto central do curso nunca foi *texto*: foi **sequência de vetores com posição**.
*Erro conceitual comum:* achar que "multimodal" é uma arquitetura nova. Na maioria dos sistemas atuais é um **encoder por modalidade projetando no mesmo espaço de embedding**, com o decoder inalterado.
*Consequência para o curso:* tudo o que a turma sabe sobre atenção, posição e KV cache continua valendo. O que muda é o custo da entrada — e é o que o Conceito 6 mede.

**Conceito 6 — Comprimir contexto em pixels: DeepSeek-OCR.**
A ideia (arXiv 2510.18234) inverte o uso habitual da visão: usar a imagem como **formato de compressão de texto longo**. O artigo reporta reconstrução em torno de 97% de precisão de decodificação na faixa de ~10 tokens de texto por token visual, degradando para a faixa de 60% perto de 20×.
Aqui entra a conta da demonstração, porque ela desfaz uma confusão inevitável: **fatiar em patches não comprime nada**. Uma página A4 a 96 DPI tem 793×1122 pixels; em patches de 16×16 são 49×70 = 3.430 patches — nove vezes mais que os 375 tokens de texto da mesma página. A compressão vem do **encoder que reduz**, não do patch.
*Erro conceitual comum:* ler "10 tokens de texto por token visual" como se a imagem fosse intrinsecamente mais densa. A densidade é do encoder treinado, e ela é **lossy** — por isso o número que importa é o **par** (compressão, fidelidade), nunca a compressão sozinha.
*Consequência prática:* é alternativa de engenharia ao RAG das Aulas 18 a 20 para documentos longos e estáveis, com o mesmo tipo de trade-off que a turma já sabe medir. Fidelidade de reconstrução é `recall` de conteúdo com outro nome.

**Conceito 7 — Difusão para linguagem: LLaDA e a queda do pressuposto autorregressivo.**
Todo o curso pressupôs geração **da esquerda para a direita**: máscara causal (Aula 6), KV cache (Aula 8), amostragem token a token (Lab 3). LLaDA (arXiv 2502.09992) treina um modelo de difusão mascarada: o processo direto mascara tokens progressivamente e o modelo aprende a **prever os mascarados**; a geração desmascara posições em qualquer ordem, refinando a sequência inteira a cada passo.
O que isso ataca: **KV cache** perde o sentido, porque não existe prefixo fixo cujo estado se reaproveita; **decodificação** deixa de ser amostragem por posição e passa a ser política de quantas e quais posições desmascarar; **latência** deixa de ser linear no número de tokens; e a **maldição da reversão** é atacada na raiz.

- **Fundamento:** o processo direto de mascaramento e o objetivo de desruído — e por que a ausência de máscara causal é consequência do objetivo, não escolha de implementação.
  → derivação completa: **Apêndice A.1** (slide 16)

*Erro conceitual comum:* concluir "então o autorregressivo está superado". O artigo mostra **viabilidade competitiva em escala de 8B**, não substituição — e o ecossistema de inferência eficiente foi construído para o outro paradigma. A lição metodológica é mais durável que o resultado: um pressuposto que atravessa 28 aulas sem ser nomeado é um pressuposto, não uma lei.

**Conceito 8 — Dados sintéticos e colapso de modelo.**
Shumailov et al. (arXiv 2305.17493) mostram o custo da realimentação **recursiva**: treinar a geração `n+1` predominantemente na saída da geração `n` corrói a distribuição. Três fontes de erro somadas — aproximação estatística, expressividade, otimização — e o efeito é cumulativo: primeiro desaparecem as **caudas**, depois a distribuição converge para algo estreito.

- **Fundamento:** a recursão que produz o colapso, e por que a fonte de erro por amostragem finita **não** desaparece nem com modelo perfeitamente expressivo — com o caso gaussiano resolvido.
  → derivação completa: **Apêndice A.2** (slide 17)

*Erro conceitual comum:* ler o artigo como "dado sintético é ruim". O resultado é sobre **realimentação recursiva sem âncora humana**. Sintético com verificação por oráculo — código que passa em teste, matemática conferida — não é a mesma operação, porque o filtro reintroduz sinal externo.
*Consequência para curadoria:* preservar amostras humanas como âncora entre gerações; datar e proceder o corpus; preferir sintético **verificado** a sintético **plausível**; medir cobertura da cauda, não só qualidade média. É a mesma lição do Lab 8 em outro tamanho.

**Conceito 9 — A fronteira do custo: pequeno, roteado e medido.**
Três movimentos: **modelos pequenos** (1–8B com bom SFT resolvem a maior parte das tarefas de produto); **roteamento** (classificador barato decide por requisição, e a métrica é acerto por real gasto); **esparsidade** (MoE ativa uma fração dos parâmetros por token — Kimi K2, arXiv 2507.20534).
A consequência metodológica: **eficiência é métrica de primeira classe** e entra na tabela do Lab 8 como qualquer outra — custo por caso, latência p95, tokens por resposta.
*Erro conceitual comum:* tratar custo como restrição externa que o engenheiro herda. Custo é dimensão de projeto: muda a arquitetura, não só a fatura.

**Conceito 10 — Hardware: a atenção é limitada por memória.**
Na decodificação, cada token novo precisa ler o KV cache inteiro para produzir **uma** posição. A razão entre operações aritméticas e bytes lidos é baixíssima. É a explicação de fundo de três coisas que o curso já usou: **FlashAttention** (arXiv 2205.14135) ganha por reduzir tráfego entre HBM e SRAM, não FLOPs; **GQA e MQA** ganham por encolher o objeto lido; **batching** ganha por amortizar a leitura dos pesos.

- **Fundamento:** a razão aritmética-por-byte da decodificação nos dois regimes, e por que ela fica na ordem de 1 em ambos — o que torna o regime limitado por banda, não por cálculo.
  → derivação completa: **Apêndice A.3** (slide 18)

*Erro conceitual comum:* comparar aceleradores por TFLOPs de pico. Para inferência autorregressiva, banda e tamanho de memória rápida predizem melhor o desempenho. Números de banda e custo por token: `[definir na oferta]`.

**Conceito 11 — Onde estudar e trabalhar.**
Três caminhos, distinguidos pelo **artefato** e pelo **critério de sucesso**, não por prestígio. **Pesquisa** produz conhecimento novo verificável (artefato: paper com código; critério: revisão por pares e reprodutibilidade). **Engenharia de IA** produz sistemas em produção (artefato: serviço com SLO; critério: usuário atendido a custo sustentável) — é o que esta disciplina treinou. **Research engineering** é o meio: infraestrutura de treino, avaliação em escala, otimização de kernels.
*O que estudar em seguida, na ordem:* Jurafsky & Martin e Raschka para o lado do modelo; Huyen para o lado do sistema; depois **um** paper por semana lido a fundo, com reimplementação de um componente. E o degrau zero, que a turma já tem: os apêndices dos 30 decks.
*Erro conceitual comum:* escolher o caminho pela remuneração inicial. Os três divergem em **rotina diária**, e é essa variável que decide se a pessoa fica.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura | **Logística da Aula 30 nos três primeiros minutos** (ordem, 12 min + perguntas, demo obrigatória); recap do Lab 8 (o que cada equipe tem em mãos); a aula em duas metades |
| 00:10 | 45 min | Bloco 1 — O percurso e a dívida paga | O mapa do stack com os **dois** endereços · **exercício em dupla "inventário do próprio sistema" (6 min + 2 de correção)** · a tese do próximo-token em três níveis · a dívida da Aula 1 e a cobrança nas Aulas 27–28 · o que o curso não cobriu |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — Fronteiras | ViT e o token independente de modalidade · **demo `demo-patches-como-tokens.py` (8 min)** · DeepSeek-OCR e o par compressão/fidelidade · LLaDA e o pressuposto autorregressivo · colapso de modelo · a fronteira do custo · hardware e o memory wall |
| 01:50 | 10 min | Fechamento | Pesquisa × engenharia × research engineering · o que estudar na ordem · o arco da Aula 1 fechado com a coluna do fundamento acesa · logística da Aula 30 repetida · 20 s de índice do apêndice |

## 4. Demonstração guiada

**`codigo/demo-patches-como-tokens.py` — 8 min, no terminal, 100% offline e determinística.**

A demo existe para tornar aritmética uma frase que a turma vai ouvir como slogan: "uma imagem vale por dez mil tokens de texto". Ela mostra que **fatiar em patches não comprime** e que a compressão de DeepSeek-OCR mora no encoder.

O script não baixa nada e não precisa de rede. Tem duas rotas para contar tokens: com `transformers` instalado usa um tokenizer real e imprime o nome dele; sem, usa um contador determinístico por regex documentado no arquivo. Nos dois casos **declara na saída qual rota usou** — a mesma exigência de procedência do Lab 8.

Seis passos: a página de texto embutida e a contagem; a geometria da mesma página renderizada; a variação de DPI e patch mostrando que o custo é função da resolução e não do conteúdo; o fator de redução do encoder; a tabela compressão × fidelidade; e o fecho ligando ao Lab 8.

**Número que a demo produz.** Três, e os três voltam ao fluxo. **375 tokens** de texto para a página embutida. **3.430 patches** para a mesma página em imagem — nove vezes mais unidades de sequência, e é o número que fecha o argumento do slide 7. E **214 tokens visuais** após um encoder que comprime a grade em 16×, que é onde a razão texto/visual finalmente inverte (de 0,11 para 1,75) e onde a compressão aparece. Os três são citados de volta no slide 8, e o par (compressão, fidelidade) da tabela final é o que amarra com o instrumento do Lab 8.

Insumos preparados na véspera: a saída do script salva em arquivo de texto — é determinística, então serve de plano B integral; e a conta do passo 2 escrita no quadro antes da aula, para o caso de projetor indisponível.

## 5. Hands-on

**Exercício em dupla — "inventário do próprio sistema" (6 min + 2 de correção, dentro do slide 2).**

Cada dupla (de preferência da mesma equipe de projeto) escreve o sistema do próprio projeto decomposto em camadas e, ao lado de cada camada, **a aula e o lab em que aquela peça foi construída** e o artefato que sobrou no repositório.

Formato pedido, quatro a seis linhas:

| Camada do meu sistema | Construída na Aula / Lab | Artefato no repositório |
|---|---|---|
| tokenização e contagem de custo | Aula 2 / Lab 1 (Aula 4) | notebook com tokens por língua |
| recuperação | Aulas 18–19 / Lab 5 (Aula 20) | tabela de `recall@k` |
| … | … | … |

**Critério de conclusão observável:** a dupla entrega a tabela preenchida e **nomeia em voz alta uma camada do próprio sistema que ela não construiu em nenhum lab** — porque essa é a camada que a equipe vai ter mais dificuldade de defender na Aula 30. Correção conduzida pelo instrutor em 2 min, com atenção às equipes que não conseguem apontar a aula de alguma camada: quase sempre é a camada em que o sistema copiou código sem entender, e é exatamente o que a defesa oral da Aula 30 vai testar.

Este é o único hands-on da aula. A prática desta unidade aconteceu no **Lab 8 (Aula 28)**; o restante do tempo é expositivo por decisão de desenho — é a aula de síntese e de fronteiras.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Turma em modo "véspera de entrega"**: perguntas de logística consumindo o Bloco 1 | Primeiras cinco perguntas são sobre a Aula 30 | Anunciar a logística completa nos primeiros 3 min (ordem, 12 min + perguntas, slots) e remeter o resto para o fim; a repetição no fechamento fecha o assunto |
| **Recapitulação virar aula repetida** e a turma desligar | Sala silenciosa e olhando o celular no Bloco 1 | A recapitulação é conduzida pelo **exercício de inventário**, não pela exposição. Se ainda assim cair, pular para o Conceito 3 (a dívida paga), que é o que a turma reconhece como conquista |
| **A segunda coluna do slide 2 passar batida** | Ninguém olha, ninguém pergunta | Os 20 s de silêncio são obrigatórios, não retórica. Se ainda passar, nomear um item concreto: "quem não entendeu por que existe `√d_k`, o A.2 da Aula 6 resolve em uma página" |
| **Bloco 2 virar desfile de novidades** sem consequência | Perguntas do tipo "qual é o melhor modelo hoje?" | Cada fronteira é apresentada pelo **pressuposto que ela ameaça**, e essa é a única ordem permitida. Novidade sem pressuposto ameaçado sai do deck |
| **Sem projetor ou sem máquina** para a demo | — | A demo é aritmética: os três números (375, 3.430, 214) cabem no quadro, e a saída determinística está salva. Nenhum passo depende de rede |
| **Turma conclui "autorregressivo está morto"** | Pergunta se ainda vale aprender KV cache | Nomear o que o artigo mostra (viabilidade em 8B) e o que não mostra (substituição). A lição é metodológica: pressuposto não nomeado continua sendo pressuposto |
| **Turma conclui "dado sintético é proibido"** | Equipe pergunta se pode gerar casos de teste com LLM | Separar realimentação recursiva sem âncora de sintético **verificado por oráculo**. Caso de teste gerado e **revisado pela equipe** é legítimo — o rótulo é humano, e é o que o Lab 8 exige |
| **Ansiedade de carreira** dominando o fechamento | Fila de perguntas individuais no fim | O slide distingue os três caminhos por artefato e rotina diária, não por salário; perguntas individuais ficam para depois da aula. Números de mercado são `[definir na oferta]` |
| **Fronteiras desatualizadas** na oferta seguinte | Papers do Bloco 2 com mais de um ano | O Módulo 7 é o de meia-vida mais curta do curso: revisar os cinco papers a cada oferta, mantendo a estrutura "pressuposto ameaçado → mecanismo → consequência". **Os três itens de apêndice envelhecem mais devagar** — difusão discreta, colapso e intensidade aritmética são resultados, não notícias |

## 7. Artefatos produzidos

- **Tabela de inventário do próprio sistema**: camada → aula/lab em que foi construída → artefato no repositório. Vai para o repositório do projeto e é insumo direto do slide de arquitetura da apresentação final.
- **Mapa do percurso com as duas colunas** exportado e guardado — é o índice de estudo de quem for revisar o curso depois, e a coluna da direita é o índice do fundamento.
- **Saída da demo** com os três números: tokens de texto, patches da página, tokens visuais após o encoder.
- **Lista pessoal de próximos passos**: qual caminho, qual leitura da ordem indicada, qual paper do Bloco 2 será lido a fundo primeiro.
- Nenhum entregável avaliado — esta aula não tem nota própria.

## 8. Desafio pós-aula

Não avaliado, e é o último da disciplina. Os dois primeiros itens ajudam diretamente a apresentação da Aula 30.

1. **Ensaiar a defesa pela tabela de inventário.** Para cada camada, responder em voz alta, em uma frase: por que essa camada existe no sistema, e que número do harness prova que ela funciona. A camada que não tiver as duas respostas é a que vai receber a pergunta do instrutor na Aula 30.
2. **Rodar a conta da demo no próprio corpus.** Quantos tokens de texto tem o corpus do projeto? Quantos patches, se ele fosse renderizado em páginas? E com um fator de redução de 16× no encoder, a compressão óptica seria vantajosa para o sistema de vocês, ou o RAG das Aulas 18 a 20 continua melhor? Responder com número, não com opinião.
3. **Leitura, escolhendo uma das duas:**
   - Nie et al., *Large Language Diffusion Models* (arXiv 2502.09992). **Pergunta dirigida:** liste três otimizações de inferência que este curso ensinou e que deixam de se aplicar quando a geração não é da esquerda para a direita, e diga, para cada uma, o que a substituiria.
   - Shumailov et al., *The Curse of Recursion* (arXiv 2305.17493). **Pergunta dirigida:** a perda das caudas é descrita como efeito de três fontes de erro somadas. Qual delas **não** desaparece nem com amostra infinita, e por quê? *(A resposta completa está em A.2 — vale tentar antes de abrir.)*
4. **Opcional, para quem vai seguir estudando:** escolher um componente do Lab 2 (mini-GPT) e reimplementá-lo sem olhar o notebook. É o exercício que mais separa "acompanhei o curso" de "sei construir".

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. Ela não cria peso novo: os pesos da ementa continuam sendo labs 30%, prova 30% e projeto final 40% (proposta 5% + checkpoint 5% + sistema e relatório 20% + apresentação 10%).

O que esta aula **prepara** para ser avaliado na Aula 30:

- **A tabela de inventário** é o ensaio da defesa oral. A política de defesa da ementa vale para toda entrega: o aluno é responsável por entender e defender o que entrega. A pergunta do instrutor sai da camada que a equipe não conseguiu endereçar a nenhuma aula.
- **A dívida de avaliação paga** é o padrão de aceitação do item de rigor quantitativo (30% da nota do projeto): número por camada com denominador, juiz declarado e calibrado, falhas priorizadas. Quem chegar à Aula 30 com "o sistema respondeu bem" chega sem o item.
- **Custo como dimensão de projeto** entra no slide de limitações: latência, custo por requisição e tamanho de modelo são decisões defensáveis, não desculpas.

**Nota sobre a defesa oral e a composição da prova.** As perguntas da Aula 30 são deliberadamente do mesmo formato das questões de maior peso da prova — **diagnóstico e interpretação (42 pontos) e justificativa de escolha (40)**. Perguntar "por que essa camada existe e que número prova que ela funciona" é uma questão de justificativa aplicada ao sistema da própria equipe. Quem estudou só as derivações e ignorou o comportamento responde mal nos dois lugares; quem ignorou o fundamento não consegue sustentar o "por quê" da defesa.

Observável em sala, sem nota: ao fim do Bloco 1, cada dupla consegue apontar a aula em que cada camada do próprio sistema foi construída, e nomear a camada órfã. Ao fim do Bloco 2, o aluno consegue dizer qual pressuposto do curso cada uma das cinco fronteiras ameaça — sem citar nome de modelo.

## Apêndice matemático — índice

Três itens, slides 16 a 18 do deck. **É um apêndice pequeno, e isso é o resultado correto:** esta é uma aula de síntese e de panorama, e o formalismo que ela mobiliza é o dos apêndices anteriores — reunidos na segunda coluna do slide 2. O que está aqui é o que **nasce** nesta aula.

| Item | O que estabelece | Apontado do |
|---|---|---|
| **A.1** | Difusão mascarada: o processo direto de mascaramento independente por posição, o objetivo de desruído com o fator `1/t` justificado, e a demonstração de que a **ausência de máscara causal é consequência do objetivo**. Mostra que o MLM da Aula 8 é o mesmo objetivo com `t` fixo em 0,15, e que é a variação de `t` que permite gerar. Casos-limite: uma posição por passo recupera o autorregressivo; todas num passo produz incoerência. Fecha explicando por que o KV cache não se aplica — a premissa de prefixo imutável desaparece. | slide 9 |
| **A.2** | Colapso de modelo: a recursão gerativa, as três fontes de erro, e a identificação de **qual delas é irredutível** (amostragem finita — não desaparece com modelo perfeitamente expressivo nem com otimização exata). Traz o caso gaussiano resolvido: a variância decai como `σ₀²·((n−1)/n)^k`, geometricamente, com família correta e ajuste exato. Casos-limite: sintético verificado por oráculo quebra o mecanismo; mistura com fração fixa de dado humano impede o decaimento. | slide 10 |
| **A.3** | Por que a decodificação é limitada por banda: a intensidade aritmética `I` derivada nos dois regimes (contexto curto, dominado pelos pesos; contexto longo, dominado pelo cache) — e o resultado de que **`I` fica na ordem de 1 em ambos**, contra centenas de operações por byte de capacidade do acelerador. Explica com um número só por que FlashAttention acelera sem fazer menos contas, por que GQA acelera a geração, e por que batching é a única das três que muda `I`. Casos-limite: o prefill é limitado por cálculo, não por banda — o mesmo modelo em dois regimes opostos. | slide 12 |

**Nota de fronteira.** A conta de patches da demo (375 contra 3.430) **não** está no apêndice: é aritmética de duas linhas que o aluno faz de cabeça, e o lugar dela é o fluxo, onde ela desfaz a confusão sobre compressão. Apêndice é para o que precisa de premissas declaradas e etapas — não para toda conta que aparece na aula.
