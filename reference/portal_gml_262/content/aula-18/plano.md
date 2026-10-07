---
aula: 18
titulo: "RAG I: geração aumentada por recuperação"
modulo: "5 — RAG, Ferramentas e Agentes de IA"
tipo: teorica
semana: 9
duracao_min: 120
versao: v2
---

# Aula 18 — RAG I: geração aumentada por recuperação

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** Esta aula já era conduzida pela aplicação na V1 e por isso muda pouco:
> ela abre por um problema real, a matemática aparece como ferramenta pontual e os exercícios já
> eram de construção. O transporte para a V2 preserva blocos, tempos e objetivos, e acrescenta
> o apêndice com o fundamento formal que estava disperso — **A.1** (cosseno, normalização L2 e a
> perda contrastiva) e **A.2** (custo da busca exata e o que a ANN aproxima) — mais os ponteiros
> no fluxo. Carga horária, numeração e objetivos de aprendizagem inalterados.

## 1. Objetivo da aula

Trocar a pergunta "como faço o modelo saber isso?" pela pergunta "como faço o modelo achar isso na hora certa?" — desmontando o pipeline de RAG em nove etapas independentes e mostrando que a etapa que mais decide o resultado final (chunking) é a que menos recebe atenção. A aula também **lança o projeto final**, que vale 40% da disciplina.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Justificar** a escolha de recuperação sobre re-treino e sobre contexto longo, usando três eixos concretos: custo, atualidade e auditabilidade.
2. **Enumerar** as nove etapas do pipeline de RAG na ordem correta e **separar** as que rodam offline (ingestão) das que rodam por consulta (online).
3. **Comparar** chunking de tamanho fixo, por fronteira semântica e contextual, e **prever** o modo de falha que cada um produz na recuperação.
4. **Explicar** por que um encoder pré-treinado cru não serve para busca e o que o treino contrastivo do Sentence-BERT muda na geometria do espaço.
5. **Distinguir** busca exata de busca aproximada (ANN) e **nomear** o parâmetro que troca recall por latência num índice HNSW.
6. **Formular** uma proposta de projeto final que satisfaça os quatro requisitos da ementa: duas técnicas do curso, avaliação quantitativa, repositório reproduzível e custo próximo de zero.

## 3. Teoria aplicada

### Bloco 1 (00:10–00:55) — Por que recuperar, e o pipeline que faz isso

**Conceito 1 — Os pesos são uma fotografia do corpus, com data de corte.**
Um modelo de linguagem é uma função com parâmetros congelados no fim do treino. Tudo o que ele "sabe" foi comprimido em pesos numa data específica, e nada que aconteceu depois — ou que nunca esteve na web pública — existe para ele. Pior: o modelo não tem um mecanismo interno para dizer "isso eu não sei"; a distribuição do próximo token continua definida e continua produzindo texto plausível.
*Analogia do instrutor:* é um livro impresso. Excelente e imutável. Quando o mundo muda, você não reimprime o livro — você anexa um caderno de erratas e ensina o leitor a consultar o caderno antes de responder.
*Erro conceitual comum:* achar que o problema é só de atualidade ("é só usar um modelo mais novo"). O problema maior é de **escopo**: o regulamento interno da sua universidade, o histórico de tickets da sua empresa e a base de contratos do seu cliente nunca vão estar nos pesos de modelo nenhum, por mais recente que ele seja.

**Conceito 2 — Três saídas para o buraco, e duas delas não escalam.**
(i) **Re-treinar ou fazer fine-tuning.** Custa GPU, custa dado curado, e é a ferramenta errada para o problema: ajuste fino ensina **forma** (estilo, formato, comportamento), não **fato** consultável. Um fato novo por semana não vira uma rodada de treino por semana. Esse é o mesmo quadro de decisão da Aula 13 — prompting × RAG × fine-tuning — agora visto do outro lado.
(ii) **Colocar tudo no contexto.** Tecnicamente possível hoje, e ruim por três motivos somados: o custo por consulta cresce com o tamanho do contexto e é pago em toda requisição; a atenção é O(n²) na Aula 6 e a latência acompanha; e — o argumento decisivo — **contexto longo não é memória confiável**. A Aula 10 já mostrou "needle in a haystack" e a sensibilidade posicional: informação enterrada no meio de um contexto muito longo é recuperada pior que informação no começo ou no fim. Encher o contexto de material irrelevante não é neutro, é ativamente nocivo.
(iii) **Recuperar sob demanda.** Buscar os poucos trechos relevantes e colocar só eles no prompt. É o único dos três que fica barato quando a base cresce, porque o custo de consulta depende de `k`, não do tamanho do acervo.
*Erro conceitual comum:* tratar "janela de 1 milhão de tokens" como o fim do RAG. Janela grande muda o `k` viável, não a necessidade de escolher o que entra. Recuperar continua sendo o passo que decide.

**Conceito 3 — Auditabilidade é requisito, não enfeite.**
Uma resposta gerada a partir de trechos recuperados pode citar a origem: documento, seção, página. Isso muda a natureza do sistema — de oráculo para instrumento de consulta. Em domínio regulado, jurídico ou acadêmico, resposta sem fonte é resposta não utilizável, independentemente de estar correta.
*Analogia:* a diferença entre um colega que responde de cabeça e um que responde apontando o parágrafo. Os dois podem acertar; só um dos dois você usa numa petição.
*Erro conceitual comum:* confundir "o modelo citou uma fonte" com "a fonte sustenta a afirmação". O modelo pode citar o chunk certo e ainda assim afirmar algo que não está nele — verificar essa ligação é assunto da Aula 27 (decomposição em afirmações atômicas).

**Conceito 4 — RAG: memória paramétrica mais memória não-paramétrica.**
A formulação de Lewis et al. (arXiv 2005.11401) separa duas memórias no mesmo sistema. A **paramétrica** é o que está nos pesos: língua, raciocínio, formato, senso comum. A **não-paramétrica** é um índice externo, editável sem treino: adicionar um documento é uma operação de escrita, não uma rodada de gradiente. O gerador consome a segunda para produzir a resposta.
*Analogia:* o modelo é o advogado; o índice é a biblioteca. Trocar um livro da estante não exige reeducar o advogado.
*Erro conceitual comum:* pensar em RAG como "um prompt com um `if` de busca". A separação das duas memórias é arquitetural: ela é o que permite atualizar conhecimento sem tocar em pesos e é a razão pela qual o índice tem ciclo de vida próprio (ingestão, versionamento, expurgo).

**Conceito 5 — O pipeline completo, em nove etapas.**
Offline, uma vez por versão do acervo: (1) **limpeza** — extrair texto de PDF/HTML, remover cabeçalho, rodapé, numeração de página; (2) **chunking** — quebrar em unidades recuperáveis; (3) **embeddings** — vetorizar cada chunk; (4) **índice** — gravar vetores e metadados numa estrutura de busca. Online, a cada consulta: (5) **embedding da consulta** — pelo mesmo modelo, obrigatoriamente; (6) **recuperação** — top-`k` por similaridade; (7) **reranking** — reordenar os `k` candidatos com um modelo mais caro e mais preciso (Aula 19); (8) **aumento do prompt** — montar a mensagem com os trechos e a instrução de citar fonte; (9) **geração**.
*Analogia:* é uma linha de produção. Toda etapa herda os defeitos da anterior e nenhuma etapa posterior conserta um chunk que foi cortado errado.
*Erro conceitual comum:* embutir a consulta com um modelo diferente do que embutiu os documentos. Os dois vetores passam a viver em espaços distintos e a similaridade vira ruído — e o sistema não quebra, ele só responde mal.

**Conceito 6 — Chunking: onde a maioria dos RAGs morre.**
Três famílias. **Tamanho fixo** (N caracteres ou tokens, com sobreposição): trivial de implementar, insensível ao conteúdo, e corta frases e tabelas ao meio. A sobreposição existe justamente para diluir esse dano. **Fronteira semântica**: quebrar por parágrafo, seção, artigo, cabeçalho de markdown; o chunk passa a coincidir com uma unidade de sentido, e o custo é que o tamanho fica irregular. **Contextual**: cada chunk carrega um pequeno prefixo que o situa no documento ("Regulamento X, Capítulo III, Art. 42 — Trancamento:") antes do texto próprio, para que ele seja recuperável mesmo quando o texto do trecho não repete os termos da seção.
*Analogia:* cortar um livro em pedaços de mesmo peso versus cortar por capítulo. O primeiro é mais fácil de automatizar e produz pedaços que não querem dizer nada sozinhos.
*Erro conceitual comum:* buscar "o tamanho ótimo de chunk" como se fosse constante universal. O tamanho ótimo depende do formato do documento e do tipo de consulta — e é uma variável que se **mede** com recall@k (Aula 19), não que se escolhe por analogia com um blog post.

**Conceito 7 — Metadados são o que torna o chunk útil e a resposta auditável.**
Todo chunk carrega, além do texto: fonte (arquivo, URL), título e seção, posição no documento, versão/data de ingestão e, quando existir, um identificador canônico (número do artigo, código do edital). Metadado serve para três coisas: filtrar antes da busca (só documentos vigentes), citar depois da geração, e depurar quando a recuperação erra.
*Erro conceitual comum:* guardar só o vetor e o texto. Sem metadado o sistema não consegue citar fonte nem responder "isso é da versão de qual ano?", e a depuração vira leitura de texto solto.

### Bloco 2 (01:05–01:50) — Como o vetor encontra o texto, e o lançamento do projeto

**Conceito 8 — Um encoder pré-treinado cru não serve para busca.**
O BERT da Aula 8 produz vetores por token; a média deles, ou o `[CLS]`, não foi otimizada para que a similaridade de cosseno signifique "responde a esta pergunta". Reimers & Gurevych (*Sentence-BERT*, arXiv 1908.10084) resolvem isso com uma arquitetura **bi-encoder** — duas passagens independentes pelo mesmo encoder, uma pooling no fim, e um treino contrastivo que **aproxima** pares relacionados e **afasta** pares negativos. O ganho de engenharia é decisivo: como as duas passagens são independentes, o vetor de cada documento é calculado **uma vez**, offline, e a consulta vira um produto escalar.
*Analogia:* é a mesma ideia do Word2Vec da Aula 3 — semântica como geometria — só que a unidade deixou de ser a palavra e passou a ser a sentença ou o parágrafo, e o objetivo de treino passou a ser explicitamente "similaridade útil para busca".
*Fundamento:* `cos(q,d) = (q·d)/(‖q‖‖d‖)`, e a perda contrastiva que molda a geometria do espaço. → **A.1**
*Erro conceitual comum:* achar que "embedding" é uma coisa só. Modelo de embedding tem objetivo de treino, e um treinado para similaridade semântica geral não é o mesmo que um treinado para casamento pergunta-documento (assimétrico). Muitos modelos pedem prefixos distintos para consulta e para passagem, e ignorar isso derruba o recall sem erro nenhum na tela.

**Conceito 9 — Escolher um modelo de embedding: quatro eixos e um benchmark.**
(a) **Idioma** — modelo monolíngue em inglês aplicado a português é o erro mais comum e mais silencioso do lab; (b) **janela de entrada** — se o chunk excede a janela, o excedente é truncado sem aviso; (c) **dimensão** — mais dimensões custam memória e latência de índice, com ganho decrescente; (d) **normalização** — com vetores normalizados em norma L2, cosseno e produto interno coincidem, o que simplifica o índice. Como referência pública existe o MTEB (leaderboard de tarefas de embedding), com a ressalva da Aula 1: leaderboard não é avaliação de produto; o número que decide é o recall@k medido no **seu** conjunto rotulado.
*Fundamento:* com norma L2 unitária, `cos(a,b) = a·b` e o ranking por cosseno, por produto interno e por distância L2 coincide — é o que o eixo (d) compra. → **A.1**
*Erro conceitual comum:* escolher pelo topo do leaderboard e nunca medir no próprio corpus. É o mesmo erro de método que a disciplina persegue desde a Aula 1.

**Conceito 10 — Banco vetorial e busca aproximada (ANN).**
Busca exata é força bruta: comparar a consulta com todos os `N` vetores, `O(N·d)`. Com `N` na casa dos milhares isso é instantâneo e é o que o Lab 5 faz de verdade. Com `N` na casa dos milhões, entra **ANN**: estruturas que aceitam errar um pouco para responder em tempo sublinear. As duas famílias que aparecem em Chroma, FAISS e afins são **HNSW** (grafo navegável em camadas; parâmetros `M` e `efSearch` — aumentar `efSearch` compra recall pagando latência) e **IVF** (particionar o espaço em células e visitar `nprobe` delas). Um banco vetorial é esse índice mais o que falta em volta: persistência, filtro por metadado, atualização incremental e coleções.
*Fundamento:* busca exata em `O(N·d)`, com os dois números que decidem o regime (5 mil × 384 → 1,9 M multiplicações; 10 M × 384 → 3,8 G); e o erro da ANN definido como `recall_índice@t = |Â_t ∩ E_t| / t`, que **não** é o `recall@k` da Aula 19. → **A.2**
*Analogia:* é a diferença entre ler a estante inteira e usar o fichário. O fichário às vezes deixa passar um livro — e o `efSearch` é literalmente quantas gavetas você aceita abrir antes de desistir.
*Erro conceitual comum:* medir a qualidade do sistema sem saber que o índice é aproximado. Se o recall@k está baixo, a primeira pergunta é se a perda veio do **recuperador** ou do **índice**: comparar contra força bruta no mesmo corpus separa as duas causas em cinco minutos.

**Lançamento do projeto final (01:30–01:50).**
Bloco de 20 min, com conteúdo normativo vindo da seção 9 da ementa e nada inventado aqui: equipes de 3–4; tema livre no domínio da equipe; quatro requisitos obrigatórios — (1) combinar pelo menos duas técnicas centrais do curso, (2) **avaliação quantitativa obrigatória** com conjunto de teste próprio, métricas por camada e análise de falhas, (3) repositório com README reproduzível mais relatório técnico de 4–6 páginas em estilo de artigo, (4) custo zero ou próximo de zero; três entregas — proposta na Aula 22, checkpoint na Aula 26, entrega final na Aula 30; pesos — proposta 5%, checkpoint 5%, sistema e relatório 20%, apresentação 10%, dentro dos 40% da ementa. Exemplos de tema, todos da ementa: assistente de regulamentos da universidade com citações; agente de triagem de issues de um repositório; tutor socrático com avaliação de factualidade; agente de análise de dados com ferramentas Python; busca semântica com reranking para um acervo local; fine-tuning de modelo pequeno para um domínio com avaliação comparativa. Datas de calendário: `[definir na oferta]`.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura | Comentário breve sobre a prova da Aula 17 e o que ela mediu; anúncio de que a segunda metade do curso é a de construir sistemas; tese da aula (o modelo não precisa saber, precisa achar) |
| 00:10 | 45 min | Bloco 1 — Por que recuperar, e o pipeline | Pesos como fotografia com data de corte; as três saídas (re-treinar, contexto longo, recuperar) e por que duas não escalam; needle in a haystack como argumento contra contexto longo (recap da Aula 10); auditabilidade; RAG como memória paramétrica + não-paramétrica (Lewis et al.); o pipeline em nove etapas, offline × online; chunking fixo × semântico × contextual; metadados; demonstração do corte no lugar errado (10 min) |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — Embeddings, índices e o projeto | Por que o encoder cru não serve para busca; Sentence-BERT, bi-encoder e treino contrastivo (recap da Aula 3); escolher modelo de embedding — idioma, janela, dimensão, normalização, MTEB; busca exata × ANN, HNSW e IVF, recall × latência; bancos vetoriais (Chroma/FAISS); **lançamento do projeto final** (20 min), com exercício de rascunho em trio (6 min) |
| 01:50 | 10 min | Fechamento | Síntese: RAG é um sistema de recuperação com um gerador no fim; ponte para a Aula 19 (retrieval híbrido, reranking e métricas); leituras (2005.11401 e 1908.10084) com pergunta dirigida |

## 4. Demonstração guiada

**Demo "o corte no lugar errado, medido no cosseno" — 10 min, `codigo/demo-chunking-embeddings.py`.**

O objetivo é único: mostrar, com número na tela, que a estratégia de chunking altera o resultado da recuperação **antes** de qualquer decisão sobre modelo ou prompt. O script roda em CPU, em segundos, e não precisa de chave de API.

Passos em alto nível:

1. Exibir o mini-corpus embutido: três artigos de um regulamento acadêmico **fictício**, com cabeçalho de seção e um identificador canônico por artigo.
2. Aplicar três estratégias de chunking sobre o mesmo texto: fixo de 220 caracteres sem sobreposição, fixo de 220 com 60 de sobreposição, e por fronteira de artigo. Imprimir a contagem de chunks e o primeiro chunk de cada estratégia.
3. Carregar o modelo de embedding multilíngue; se o download falhar, o script cai automaticamente num vetorizador léxico e **avisa na tela** que está em modo degradado.
4. Fazer uma consulta em paráfrase — sem repetir os termos do regulamento — e imprimir o top-3 de cada estratégia com o cosseno de cada chunk.
5. Ler em voz alta o chunk vencedor do corte fixo sem sobreposição: a resposta está cortada ao meio, e o cosseno mesmo assim é alto. O sistema "acertou" a recuperação e ainda assim entregou uma resposta incompleta ao gerador.
6. Mostrar o mesmo top-1 na estratégia por artigo: o chunk contém a regra inteira e o identificador canônico, que é o que a citação da fonte vai usar.
7. Se o script estiver em modo degradado, aproveitar: o vetorizador léxico erra a consulta em paráfrase, e essa falha é exatamente o slide de abertura da Aula 19.

**Número que a demo produz, e que a aula usa como evidência:** o **cosseno do chunk vencedor em
cada uma das três estratégias**, para a mesma consulta em paráfrase, ao lado da **contagem de
chunks** de cada estratégia. O par de números é o que sustenta a tese do slide 7 ("não existe
tamanho ótimo de chunk") e é retomado explicitamente no fechamento (slide 15): o corte fixo sem
sobreposição vence com cosseno alto **e** entrega meia regra, e o corte por artigo vence com o
chunk inteiro mais o identificador canônico. Sem esses dois números na tela, o slide 7 é opinião.

Insumos preparados antes da aula: o script rodado na véspera com a saída salva em texto, para o caso de a rede da sala não permitir o download do modelo.

## 5. Hands-on

**Exercício em trio — "o rascunho de trinta segundos" (6 min, 01:44–01:50).**

O exercício é o embrião da Entrega 1 e serve para que ninguém saia da aula sem equipe. Cada trio (ou quarteto) escreve **três linhas**, uma por item:

1. O problema e quem sofre com ele, em uma frase.
2. As duas técnicas do curso que o sistema vai combinar.
3. Como a equipe vai medir se funciona — que número, sobre que conjunto.

Critério de conclusão observável: cada trio entrega as três linhas com nome dos integrantes, e pelo menos três trios leem a linha 3 em voz alta. A linha 3 é a que o instrutor comenta, porque é a que a maioria escreve vaga ("vamos testar com uns exemplos") — e é o requisito que separa a nota média da nota alta na rubrica do projeto.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Turma desmobilizada** logo depois da prova | Sala quieta, pouca pergunta nos primeiros 15 min | A abertura devolve as notas da prova só depois da aula, não no início; o Bloco 1 é aberto pela pergunta concreta "o modelo responde sobre o regulamento da universidade?" em vez de definição de RAG |
| **Download do modelo de embedding falha** na demo | `sentence-transformers` demora ou levanta exceção de rede | O script cai sozinho no vetorizador léxico e imprime aviso; a falha vira conteúdo (é o gancho da Aula 19). Em último caso, projetar a saída salva da véspera |
| **Confusão RAG × fine-tuning** trava a turma | Perguntas do tipo "então fine-tuning não serve para nada?" | Reprojetar o quadro de decisão da Aula 13 (prompting × RAG × fine-tuning) e responder com a distinção forma × fato em duas frases; não abrir discussão longa aqui — o quadro completo já foi dado |
| **Discussão sobre contexto longo** consome o bloco | Debate sobre janelas de 1 M de tokens aos 00:25 | Cortar com o dado da Aula 10 (sensibilidade posicional) e a conta de custo por consulta; anunciar que a comparação quantitativa é possível no projeto de quem quiser |
| **O lançamento do projeto estoura o tempo** | 01:44 e ainda em perguntas de tema | Proteger os 6 min do exercício em trio: formar equipe em sala vale mais que responder perguntas de tema, que podem ir para o canal da turma. Os requisitos estão na ementa por escrito |
| **Equipes não se formam** (turma com número quebrado ou alunos isolados) | Alunos sozinhos ao fim do exercício | O instrutor forma as equipes restantes na hora, por proximidade de tema declarado; equipe de 3 é o piso e nenhum aluno fica sozinho. Registro provisório aceito até a aula seguinte |
| **Tema proposto exige dado sensível ou pago** | Proposta com base de dados privada de empresa | Regra explicitada no lançamento: custo próximo de zero e dado que a equipe pode versionar num repositório. Alternativa sempre disponível: acervo público ou regulamento da própria universidade |

## 7. Artefatos produzidos

- **Rascunho de proposta** em três linhas por equipe (problema, duas técnicas, plano de medição), com os nomes dos integrantes — recolhido em sala e devolvido com comentário até a Aula 19.
- Composição das equipes do projeto final registrada, com tema provisório declarado.
- Anotação pessoal do **pipeline de nove etapas**, com a marcação de quais rodam offline e quais rodam por consulta — é o mapa que o Lab 5 vai executar.
- `codigo/demo-chunking-embeddings.py` disponível no repositório da disciplina, com a saída da execução da aula.
- Nenhum entregável avaliado nesta aula.

## 8. Desafio pós-aula

Não avaliado, e desenhado para reduzir o atrito do Lab 5.

1. **Escolher o corpus.** Cada equipe escolhe o acervo que vai usar no projeto — ou, quem ainda não fechou tema, um acervo de treino qualquer (regulamento da universidade, documentação de uma biblioteca que a equipe usa, um conjunto de editais públicos). Baixar, converter para texto e olhar o resultado da conversão com os próprios olhos: essa é a etapa 1 do pipeline e é onde mora o lixo.
2. **Contar.** Quantos documentos, quantos caracteres, qual o tamanho médio de uma seção. Esse número decide o chunking do Lab 5.
3. **Leitura.** Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (arXiv 2005.11401) — introdução e a seção de modelos. **Pergunta dirigida:** no artigo, o recuperador é treinado junto com o gerador; no RAG que a indústria usa hoje, ele quase nunca é. O que se perde e o que se ganha com essa simplificação? Complementar: Reimers & Gurevych, *Sentence-BERT* (arXiv 1908.10084), seção 3 — por que a arquitetura bi-encoder torna a busca viável, e o que ela sacrifica em relação ao cross-encoder. A resposta a essa segunda pergunta é o Bloco 1 da Aula 19.

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**, mas é onde o instrumento de 40% da nota é aberto. Os pesos são os da ementa e não são reinventados aqui:

- **Projeto final — 40%**, dividido em proposta 5% (Entrega 1, Aula 22), checkpoint 5% (Entrega 2, Aula 26), sistema e relatório 20% e apresentação 10% (Aula 30).
- **Rubrica do projeto:** funcionamento e adequação técnica do sistema 40%; **rigor da avaliação quantitativa** — conjunto de teste, métricas por camada, análise de falhas — 30%; relatório técnico 20%; apresentação e demo 10%.
- **Requisitos de admissibilidade da proposta** (Aula 22): equipe de 3–4 identificada; problema e usuários declarados; pelo menos duas técnicas centrais do curso combinadas; plano de avaliação com métrica nomeada e conjunto de teste dimensionado; divisão de trabalho.
- **Declaração de uso de IA** obrigatória em toda entrega do projeto, com responsabilidade integral pelo código — qualquer entrega pode virar defesa oral.

Observável em sala, sem nota: ao fim do exercício em trio, a equipe consegue nomear a métrica que vai usar e sobre que conjunto ela será calculada, sem usar a palavra "testar" como sinônimo de "medir".
