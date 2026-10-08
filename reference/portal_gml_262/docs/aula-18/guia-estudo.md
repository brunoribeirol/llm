# RAG I: geração aumentada por recuperação

## Slide 1 · Abertura: a prova ficou para trás · 00:00–00:05

Boa noite, pessoal. Primeira coisa: a prova acabou. Eu ainda não vou devolver nota hoje — devolvo no fim da aula, para vocês não passarem os próximos cem minutos olhando para o papel em vez de olhar para a tela.

Deixa eu dizer o que aquela prova era. Ela cobriu dezesseis aulas: token, atenção, arquitetura, escala, ajuste fino, preferências, raciocínio. Aquilo tudo era a metade de **entender**. A partir de hoje começa a metade de **construir**. Das doze aulas que faltam antes das apresentações, cinco são laboratório e todas as teóricas alimentam diretamente um sistema que vocês vão montar.

E tem uma coisa que muda hoje de forma concreta: no fim desta aula eu abro o projeto final. Quarenta por cento da nota de vocês. Equipes formadas hoje, aqui, nesta sala.

> Ideia central: "A primeira metade foi sobre entender o modelo. A segunda é sobre construir sistemas em volta dele — e o primeiro deles começa a ser desenhado no fim da aula de hoje."

## Slide 2 · A tese: o modelo não precisa saber, precisa achar · 00:05–00:10

Deixa eu abrir com uma pergunta que qualquer um de vocês já tentou fazer para um chatbot. Qual é o prazo para trancar uma disciplina aqui na universidade?

Um modelo de fronteira responde isso. Responde com confiança, com um número, e com uma redação que parece de regulamento. E está inventado, porque o regulamento desta instituição não estava no corpus de treino de modelo nenhum, e provavelmente nunca vai estar.

Agora, olha o que é interessante: o modelo não tem um mecanismo interno para dizer "isso eu não sei". A distribuição do próximo token continua definida. Ele continua produzindo o texto mais plausível — e "mais plausível" e "verdadeiro" são coisas diferentes quando a informação não está nos pesos.

Então a tese de hoje é uma inversão da pergunta. A pergunta errada é "como eu faço o modelo saber o regulamento?". A pergunta certa é "como eu faço o regulamento chegar na frente do modelo, no momento em que ele precisa?".

> Ideia central: "O modelo não precisa saber o regulamento. Ele precisa achar o parágrafo certo três milissegundos antes de responder."

## Slide 3 · Os pesos são uma fotografia com data de corte · 00:10–00:16

Vamos ser precisos sobre qual é o buraco, porque tem duas coisas diferentes aí dentro e a turma costuma confundir.

A primeira é **atualidade**. Um modelo de linguagem é uma função com parâmetros congelados no fim do treino. Tudo o que ele sabe foi comprimido em pesos numa data específica. O que aconteceu depois não existe para ele. Esse é o problema fácil, e é o problema que as pessoas citam.

A segunda é **escopo**, e é bem maior. O regulamento interno desta universidade, o histórico de tickets da empresa onde vocês estagiam, a base de contratos de um cliente, a documentação interna de um time — nada disso está na web pública, e portanto nada disso vai estar nos pesos de modelo nenhum, por mais novo que ele seja. Não é uma questão de esperar a próxima versão.

A analogia que eu uso é o livro impresso. Um livro excelente e imutável. Quando o mundo muda, você não reimprime o livro: você anexa um caderno de erratas e ensina o leitor a consultar o caderno antes de responder. A disciplina de hoje é sobre construir o caderno e ensinar a consulta.

> Ideia central: "Atualidade é o problema fácil e é o que todo mundo cita. Escopo é o problema grande: o que é seu nunca esteve no corpus de ninguém."

## Slide 4 · Três saídas, e por que duas não escalam · 00:16–00:25

Tem exatamente três saídas para esse buraco, e vale a pena passar pelas três, porque duas delas são erro caro e são as duas que a intuição sugere primeiro.

Saída um: **re-treinar ou fazer fine-tuning** com os seus documentos. Custa GPU, custa dado curado, e é a ferramenta errada para o problema. Lembram do quadro de decisão da Aula 13? Ajuste fino ensina **forma** — estilo, formato, comportamento, tom. Ele não ensina **fato consultável**. E mesmo que ensinasse: um fato novo por semana não vira uma rodada de treino por semana. É insustentável operacionalmente antes de ser insustentável tecnicamente.

Saída dois: **colocar tudo no contexto**. Hoje isso é tecnicamente possível, as janelas cresceram muito. E é ruim por três motivos que se somam. Primeiro, custo: o contexto é pago em **toda** requisição, não uma vez. Segundo, latência: a atenção é O(n²), isso é a Aula 6, e o tempo até o primeiro token acompanha. E o terceiro é o que mata, e vocês já viram esse dado na Aula 10 — contexto longo **não é** memória confiável. Needle in a haystack: informação enterrada no meio de um contexto muito longo é recuperada pior que informação no começo ou no fim. Encher o contexto de material irrelevante não é neutro. É ativamente nocivo, porque o material irrelevante compete pela atenção com a instrução.

Saída três: **recuperar sob demanda**. Buscar os poucos trechos relevantes e colocar só eles no prompt. E olha por que essa é a única que escala: o custo por consulta depende de `k`, o número de trechos que eu trago, e não do tamanho do acervo. Meu acervo pode ir de mil para um milhão de documentos que o prompt continua do mesmo tamanho.

Ah, e antes que alguém pergunte: janela de um milhão de tokens não acabou com RAG. Ela mudou o `k` viável. Continua existindo alguém escolhendo o que entra — e esse alguém é o recuperador.

> Ideia central: "Contexto longo não é memória. Enfiar o acervo inteiro no prompt é pagar mais caro para o modelo prestar menos atenção."

## Slide 5 · RAG: anexar memória não-paramétrica · 00:25–00:32

O nome disso tem paper, e vale citar o paper porque a formulação dele é mais limpa que a versão de blog. Lewis e colegas, dois mil e vinte, arXiv 2005.11401: *Retrieval-Augmented Generation*.

A ideia é separar duas memórias dentro do mesmo sistema. A **memória paramétrica** é o que está nos pesos: língua, raciocínio, formato, senso comum. Isso o modelo faz bem e é caro de mudar. A **memória não-paramétrica** é um índice externo, e a propriedade que interessa é esta: adicionar um documento é uma operação de **escrita**, não uma rodada de gradiente.

A analogia é o advogado e a biblioteca. O modelo é o advogado: ele sabe argumentar, sabe estruturar, sabe escrever. A biblioteca é o índice. Trocar um livro da estante não exige reeducar o advogado. E vocês percebem o que isso muda em operação: o conhecimento passa a ter ciclo de vida próprio — ingestão, versionamento, expurgo — desacoplado do modelo.

E tem um efeito colateral que não é colateral coisa nenhuma, é requisito: se a resposta veio de trechos, a resposta pode **citar** de onde veio. Documento, seção, artigo. Em domínio jurídico, regulado ou acadêmico, resposta sem fonte é resposta não utilizável, mesmo quando está certa. É a diferença entre o colega que responde de cabeça e o que responde apontando o parágrafo — os dois podem acertar, e só um dos dois você usa numa petição.

Agora, um alerta que eu preciso deixar plantado: o modelo citar uma fonte não significa que a fonte sustenta a afirmação. Ele pode trazer o chunk certo e afirmar algo que não está nele. Verificar essa ligação tem nome e tem aula — é decomposição em afirmações atômicas, Aula 27.

> Ideia central: "O modelo é o advogado, o índice é a biblioteca. Trocar um livro da estante não exige reeducar o advogado."

## Slide 6 · O pipeline em nove etapas · 00:32–00:40

Agora eu vou abrir a caixa. RAG não é uma técnica, é uma linha de produção com nove etapas, e eu quero que vocês saiam daqui sabendo desenhar as nove de cabeça, porque cada uma delas é um lugar onde o sistema quebra de um jeito diferente.

Quatro etapas rodam **offline**, uma vez por versão do acervo. Um: **limpeza** — extrair texto de PDF, de HTML, tirar cabeçalho, rodapé, numeração de página. Etapa suja, subestimada, e é onde entra lixo que contamina tudo depois. Dois: **chunking** — quebrar o texto em unidades recuperáveis. Três: **embeddings** — vetorizar cada chunk. Quatro: **índice** — gravar os vetores e os metadados numa estrutura de busca.

E cinco etapas rodam **online**, a cada consulta. Cinco: **embedding da consulta**, pelo mesmo modelo que embutiu os documentos — obrigatoriamente o mesmo, e eu já volto nisso. Seis: **recuperação** dos top-`k` por similaridade. Sete: **reranking**, que é reordenar esses `k` candidatos com um modelo mais caro e mais preciso, e é a aula que vem. Oito: **aumento do prompt** — montar a mensagem com os trechos, a pergunta e a instrução de citar a fonte. Nove: **geração**.

Duas observações que valem a aula inteira. A primeira: isso é uma linha de produção, então toda etapa herda os defeitos da anterior, e **nenhuma etapa posterior conserta um chunk que foi cortado errado**. Se o texto foi partido no meio da regra, não existe reranking, prompt ou modelo que reconstitua o pedaço que ficou de fora.

A segunda é o erro operacional mais comum que eu vejo: embutir a consulta com um modelo diferente do que embutiu os documentos. Os dois vetores passam a viver em espaços distintos e a similaridade vira ruído. E olha o veneno: o sistema não quebra. Ele não levanta exceção. Ele só responde mal, e você vai passar duas semanas ajustando prompt.

> Ideia central: "Nenhuma etapa posterior conserta um chunk que foi cortado errado. O reranking não remonta o parágrafo."

## Slide 7 · Chunking: onde a maioria dos RAGs morre · 00:40–00:45

Etapa dois. Se eu tivesse que apostar em qual etapa está o problema de um RAG que alguém me trouxer para depurar, eu aposto no chunking, e eu ganho essa aposta com frequência desconfortável.

Três famílias. **Tamanho fixo**: corta a cada N caracteres ou N tokens, geralmente com uma sobreposição. É trivial de implementar, é o que todo tutorial faz, e é completamente insensível ao conteúdo — corta frase no meio, corta tabela no meio, corta a regra separando a condição da consequência. A sobreposição existe justamente para diluir esse dano, e ela é um curativo, não uma cura.

**Fronteira semântica**: quebrar por parágrafo, por seção, por artigo, por cabeçalho de markdown. O chunk passa a coincidir com uma unidade de sentido. O custo é que o tamanho fica irregular, e aí você tem chunk de trinta caracteres e chunk de quatro mil, e precisa de uma política para os dois extremos.

**Contextual**: cada chunk carrega um pequeno prefixo que o situa. Em vez de guardar só "o prazo é de trinta dias contados da divulgação", eu guardo "Regulamento Acadêmico, Capítulo Três, Artigo quarenta e dois, Trancamento de disciplina: o prazo é de trinta dias...". Por que isso importa? Porque a consulta vai falar de trancamento, e o texto do trecho não repete a palavra trancamento — ela está no título da seção, que o corte jogou fora.

E junto com o chunking vem uma coisa que quase todo mundo esquece: **metadados**. Todo chunk carrega fonte, título, seção, posição, versão, e um identificador canônico quando existir — número do artigo, código do edital. Metadado serve para três coisas: filtrar antes da busca, citar depois da geração, e depurar quando a recuperação erra. Quem guarda só o vetor e o texto não consegue citar fonte e não consegue responder "isso é de qual versão do regulamento?".

Ah, e a pergunta que vem: qual o tamanho ótimo de chunk? Não existe constante universal. Depende do formato do documento e do tipo de consulta. É uma variável que se **mede** com recall arroba k — próxima aula — e não que se escolhe copiando de um blog post.

> Ideia central: "Não existe tamanho ótimo de chunk. Existe o tamanho que você mediu no seu corpus, com as suas consultas."

## Slide 8 · [Demo] O corte no lugar errado, medido no cosseno · 00:45–00:55

Chega de afirmar. Vou medir isso na frente de vocês, em dez minutos, com um script que roda em CPU e não precisa de chave de API nenhuma.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> Ideia central: "A mesma pergunta, o mesmo modelo, o mesmo corpus — e três respostas diferentes, porque eu cortei o texto de três jeitos diferentes."

## Slide 9 · Embeddings para busca: por que o BERT cru não serve · 01:05–01:14

Voltando. A etapa três do pipeline é a que transforma texto em vetor, e ela merece cuidado, porque tem uma armadilha aí que parece detalhe e não é.

Vocês viram BERT na Aula 8. O BERT produz um vetor por token e tem o token `[CLS]`. Intuição natural: pego a média dos vetores, ou pego o `[CLS]`, e uso o cosseno para medir similaridade. Isso funciona mal. E funciona mal por um motivo simples: **ninguém treinou aquele espaço para que o cosseno significasse "isto responde àquilo"**. O objetivo de treino do BERT era prever token mascarado. A geometria que sai daí é ótima para o que ela foi otimizada e mediana para busca.

Reimers e Gurevych resolveram isso em dois mil e dezenove, no *Sentence-BERT*, arXiv 1908.10084. Duas peças. A primeira é a arquitetura **bi-encoder**: duas passagens independentes pelo mesmo encoder, uma para a consulta e outra para o documento, com um pooling no fim de cada. A segunda é o treino **contrastivo**: aproximar pares que se correspondem e afastar pares que não se correspondem. Depois desse treino, cosseno alto passa a significar o que a gente quer que signifique.

E olha o ganho de engenharia, porque ele é o ponto que faz a coisa toda ser viável. Como as duas passagens são independentes, o vetor de cada documento é calculado **uma vez**, offline. Na hora da consulta, comparar é produto escalar. Sem isso, responder uma pergunta exigiria passar a pergunta junto com cada documento pelo modelo, e um acervo de cem mil documentos seria cem mil inferências por consulta. Guardem essa frase, porque na próxima aula eu vou fazer exatamente isso — e vou explicar por que vale a pena fazer isso com vinte documentos.

No fundo, é a mesma ideia do Word2Vec da Aula 3: semântica como geometria. Só que a unidade deixou de ser a palavra e virou a sentença, e o objetivo de treino passou a ser explicitamente busca.

> Ideia central: "O cosseno só quer dizer o que você quer que ele queira dizer se alguém treinou o espaço para isso. Espaço não treinado para busca não serve para busca."

## Slide 10 · Escolher um modelo de embedding · 01:14–01:21

Prática. Vocês vão ter que escolher um modelo no Lab 5 e no projeto. Quatro eixos e um alerta.

Primeiro eixo, **idioma**. Esse é o erro mais comum e o mais silencioso: pegar um modelo treinado em inglês e aplicar em corpus em português. Não dá erro. Só dá recall ruim. Modelo multilíngue, ou modelo treinado em português, e ponto.

Segundo, **janela de entrada**. Se o chunk é maior que a janela do modelo, o excedente é truncado — de novo, sem aviso. Se o modelo aceita duzentos e cinquenta e seis tokens e vocês fizeram chunks de mil, metade do seu acervo está sendo indexada pela primeira frase.

Terceiro, **dimensão**. Mais dimensões custam memória e latência de índice, com ganho decrescente. Não é uma corrida.

Quarto, **normalização**. Se os vetores estão normalizados em norma L2, cosseno e produto interno dão a mesma ordenação, e o índice fica mais simples. Vale conferir se a biblioteca já normaliza ou se vocês precisam normalizar.

E o alerta. Existe um leaderboard público de modelos de embedding, o MTEB, e ele é útil como ponto de partida. Mas vocês lembram da Aula 1: leaderboard não é avaliação de produto. O número que decide qual modelo vocês usam é o recall arroba k medido **no corpus de vocês**, com **as consultas de vocês**. Escolher pelo topo do leaderboard e nunca medir no próprio corpus é o mesmo erro de método que essa disciplina persegue desde a primeira aula.

> Ideia central: "Escolher modelo de embedding pelo leaderboard e nunca medir no seu corpus é a versão RAG de acreditar em noventa e nove por cento de acurácia."

## Slide 11 · Bancos vetoriais e busca aproximada · 01:21–01:30

Etapa quatro: onde os vetores moram.

Começa simples. Busca exata é força bruta: comparar a consulta com todos os `N` vetores. Custo `O(N·d)`. Com `N` na casa dos milhares, isso é instantâneo — e é literalmente o que o Lab 5 de vocês vai fazer, porque o corpus é pequeno e força bruta é exata. Não tem vergonha nenhuma nisso; tem honestidade.

O problema aparece com milhões de vetores, e aí entra **busca aproximada**, ANN. A troca é explícita: aceito errar um pouco na recuperação para responder em tempo sublinear. Duas famílias que vocês vão encontrar em Chroma, FAISS e afins.

**HNSW** é um grafo navegável em camadas — camadas de cima com poucos nós e saltos longos, camadas de baixo densas. A busca desce pelo grafo. Os dois parâmetros que importam são `M`, que é quantas conexões cada nó tem, e `efSearch`, que é quantos candidatos a busca mantém vivos enquanto navega. E é aqui que mora a alavanca: **aumentar `efSearch` compra recall pagando latência**. É um botão, e é um botão que vocês têm que saber que existe.

**IVF** é a outra: particionar o espaço em células, e na consulta visitar só `nprobe` células. Mesmo trade-off, botão diferente.

E o que é um banco vetorial, afinal? É esse índice mais tudo o que falta em volta para ele ser software de verdade: persistência em disco, filtro por metadado, atualização incremental, coleções separadas. Chroma é o mais simples de subir e é o do lab; FAISS é biblioteca, mais crua e mais rápida.

Última coisa, e é a que salva vocês numa depuração. Se o recall arroba k do sistema está baixo, a primeira pergunta é: a perda veio do **recuperador** ou do **índice**? Rodar a mesma consulta contra força bruta no mesmo corpus separa as duas causas em cinco minutos. Índice aproximado que ninguém sabe que é aproximado já custou muita semana de gente boa.

> Ideia central: "`efSearch` é o botão que compra recall pagando latência. Se você não sabe onde ele está, seu índice está tomando essa decisão por você."

## Slide 12 · [Projeto] Quarenta por cento da nota começa agora · 01:30–01:37

Bom, pessoal. Fecha o notebook por um minuto. Isso aqui é a parte da aula que decide a nota de vocês.

O projeto final vale **quarenta por cento** da disciplina, e ele começa hoje. Equipes de três ou quatro pessoas. Tema livre — o domínio é escolha de vocês, e eu falo sério quando digo livre: pode ser acadêmico, pode ser do trabalho de vocês, pode ser aquela coisa da universidade que irrita vocês desde o segundo período.

O que eu quero é isto: no dia da apresentação, na Aula 30, vocês sobem aqui, rodam uma demo ao vivo, e mostram uma tabela de números que sustenta a demo. Não é um slide dizendo que funciona. É um número, medido num conjunto de teste que vocês construíram, com uma análise das falhas que vocês encontraram.

E deixa eu antecipar a pergunta sobre escopo, porque ela vem sempre. Não é para vocês construírem um produto. É para vocês construírem um **sistema medido**. Um assistente de regulamentos que responde vinte perguntas com setenta por cento de acerto e uma análise honesta dos trinta por cento que erraram vale mais, nesta disciplina, do que uma interface bonita com zero medição. Muito mais.

Olha o arco que vocês já têm nas mãos. Daqui a duas aulas, no Lab 5, vocês constroem um RAG medido. No Lab 6, ferramentas e MCP. No Lab 7, um agente que usa a base do Lab 5. No Lab 8, o harness de avaliação **do projeto de vocês** — o Lab 8 não é um exercício, é uma aula de trabalho no projeto. Os laboratórios da segunda metade foram desenhados para serem peças do projeto de vocês.

> Ideia central: "Na Aula 30 vocês sobem aqui com uma demo e uma tabela de números. Sem a tabela, é só uma demo — e demo qualquer um faz."

## Slide 13 · [Projeto] Requisitos, entregas e regras do jogo · 01:37–01:44

Agora o contrato, e ele é curto. Quatro requisitos obrigatórios, três entregas.

Requisito um: o sistema combina **pelo menos duas técnicas centrais do curso**. RAG mais agente com ferramentas. Ajuste fino com LoRA mais avaliação sistemática. Agente multiestágio mais RAG. Tool calling com MCP mais um juiz calibrado. Duas, no mínimo — porque uma técnica só não é um sistema, é um exercício.

Requisito dois, e é o que separa as notas: **avaliação quantitativa é obrigatória**. Conjunto de teste próprio, métricas **por camada**, análise de falhas. Por camada quer dizer: se vocês têm RAG, mede o recall do retrieval separado da qualidade da resposta. Se tem agente, mede a taxa de sucesso da trajetória separado da resposta final. Falha em camada errada é diagnóstico errado, e diagnóstico errado é a semana de vocês jogada fora. Na rubrica, esse item sozinho vale trinta por cento da nota do projeto.

Requisito três: repositório com README reproduzível, mais um relatório técnico curto — quatro a seis páginas, em estilo de artigo: problema, arquitetura, experimentos, resultados, limitações. Limitações não é seção de modéstia, é seção de competência.

Requisito quatro: **custo zero ou próximo de zero**. Free tier, modelo local, Colab. Ninguém aqui vai gastar dólar para passar na minha disciplina, e um projeto que só roda com cartão de crédito não é reprodutível pelo colega que vai corrigir.

Três entregas. Proposta na **Aula 22** — que é o Lab 6, daqui a duas semanas: equipe, problema, usuários, técnicas, plano de avaliação e divisão de trabalho. Vale cinco por cento. Checkpoint na **Aula 26**: o pipeline central funcionando de ponta a ponta, mesmo que simples e feio. Vale cinco. E a entrega final na **Aula 30**: sistema, harness de avaliação, relatório e apresentação com demo — vinte por cento de sistema e relatório, dez de apresentação.

E os temas, se vocês quiserem chão firme: assistente de regulamentos da universidade com citações; agente de triagem de issues de um repositório; tutor socrático de uma disciplina com verificação de factualidade; agente de análise de dados com ferramentas Python; busca semântica com reranking para um acervo local; ajuste fino de modelo pequeno para um domínio de linguagem com avaliação comparativa. Nenhum desses é obrigatório e nenhum desses é proibido para mais de uma equipe.

> Ideia central: "Avaliação quantitativa não é o capítulo final do projeto. É o que vocês desenham na proposta, daqui a duas semanas, antes de escrever a primeira linha de código."

## Slide 14 · [Exercício] O rascunho de trinta segundos · 01:44–01:50

Seis minutos, e ninguém sai daqui hoje sem equipe.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> Ideia central: "Três linhas: o problema, as duas técnicas, e como vocês vão medir. A terceira linha é a que eu vou ler com atenção."

## Slide 15 · Fechamento: um sistema de recuperação com um gerador no fim · 01:50–02:00

Deixa eu juntar as peças.

A gente começou com um buraco: os pesos são uma fotografia com data de corte, e o que é seu nunca esteve no corpus de ninguém. Passou por três saídas e descartou duas: re-treinar ensina forma, não fato; contexto longo é caro e não é memória confiável. Sobrou recuperar.

E aí a gente abriu a caixa e descobriu que RAG não é uma técnica. São nove etapas, quatro offline e cinco online, e o resultado final é refém da pior delas. O chunking, que é a etapa que ninguém quer discutir, decide mais coisa que a escolha do modelo. A demo mostrou isso com número.

Então a frase que eu quero na cabeça de vocês é esta: RAG é um sistema de **recuperação** com um gerador no fim. A palavra que importa nessa frase é a primeira. Se a recuperação não trouxe o trecho certo, o gerador não tem o que fazer — e nenhum prompt conserta isso.

Na próxima aula a gente ataca exatamente essa parte. Retrieval denso é o que vimos hoje, e ele tem um ponto cego enorme: ele é ruim em identificador, em código de edital, em nome próprio raro, em qualquer coisa que precise casar o termo exato. A gente vai ver BM25, vai ver híbrido, vai ver reranking com cross-encoder — e, mais importante, vai ver **como medir** tudo isso: recall arroba k, precision arroba k, MRR, nDCG. E por que recall arroba k é a primeira coisa que você depura num RAG doente. Aula 19.

Para a semana, três coisas. Cada equipe escolhe o corpus do projeto, converte para texto e **olha com os próprios olhos** o resultado da conversão — a etapa um do pipeline é onde entra o lixo. Conta quantos documentos e qual o tamanho médio de uma seção; esse número decide o chunking de vocês no Lab 5. E a leitura: Lewis e colegas, 2005.11401, com a pergunta dirigida — no artigo o recuperador é treinado junto com o gerador, e hoje quase ninguém faz isso; o que se perde e o que se ganha com essa simplificação? Quem quiser puxar mais, o Sentence-BERT, 1908.10084, seção três: o que o bi-encoder sacrifica em relação ao cross-encoder. Essa segunda resposta é o Bloco 1 da próxima aula.

Ah, e as provas. Podem vir pegar aqui na frente.

> Ideia central: "RAG é um sistema de recuperação com um gerador no fim. Se o trecho certo não chegou, nenhum prompt do mundo conserta."

---

## Parte 2 — Demonstração guiada

Dez minutos, um script, CPU, sem chave de API. O objetivo é único: mostrar com número na tela que a estratégia de chunking altera o resultado da recuperação **antes** de qualquer decisão sobre modelo ou sobre prompt. Eu rodo `python demo-chunking-embeddings.py` com o terminal em fonte grande e vou comentando a saída.

**1.** **[Abro o script e mostro o corpus embutido, sem rolar o código todo]** O corpus está dentro do arquivo, são três artigos de um regulamento acadêmico fictício — eu inventei o texto, e está escrito lá que é fictício, porque eu não vou colar regulamento real numa demo. Cada artigo tem cabeçalho de seção e um identificador canônico. Guardem esse identificador: ele volta na próxima aula como o caso que a busca vetorial erra.

**2.** **[Rodo o script e paro na primeira saída, a das três estratégias de corte]** Olha o que o script fez com o mesmo texto. Corte fixo de duzentos e vinte caracteres sem sobreposição: deu esse número de chunks. Corte fixo com sessenta de sobreposição: mais chunks, porque tem repetição. Corte por fronteira de artigo: três chunks, um por artigo. Mesmo texto, três realidades diferentes daqui para frente.

**3.** **[Aponto para o primeiro chunk do corte fixo sem sobreposição]** Lê comigo onde esse chunk termina. Ele termina no meio de uma frase. Não no meio de um parágrafo: no meio de uma **frase**, entre a condição e a consequência da regra. Esse pedaço vai ser vetorizado, indexado e potencialmente recuperado como se fosse uma unidade de sentido, e ele não é.

**4.** **[Deixo o carregamento do modelo de embedding rodar e narro enquanto baixa]** O script está carregando um modelo de embedding multilíngue pequeno. Se ele não conseguir baixar, ele cai sozinho num vetorizador léxico e avisa na tela — e se isso acontecer hoje, eu vou aproveitar, porque a falha do modo degradado é bonita.

**5.** **[Rodo a consulta em paráfrase e mostro o top-3 de cada estratégia]** A consulta é uma paráfrase: eu não usei nenhuma das palavras-chave do regulamento de propósito. Olha os três rankings lado a lado, com o cosseno de cada chunk.

**6.** **[Leio em voz alta o chunk vencedor do corte fixo sem sobreposição]** Agora a parte que eu quero que vocês vejam. Esse chunk aqui ganhou. O cosseno dele é alto. E ele está **cortado ao meio** — a regra está lá, e a exceção da regra ficou no chunk seguinte, que não foi recuperado. Repararam no que aconteceu? A recuperação "acertou". A métrica de similaridade está satisfeita. E o gerador vai receber meia regra e responder com confiança total. Esse é o modo de falha mais desagradável de RAG, porque ele não parece falha.

**7.** **[Mostro o top-1 da estratégia por artigo]** Mesma consulta, corte por artigo. O chunk vencedor tem a regra inteira, a exceção, e o identificador canônico do artigo — que é exatamente o que a citação de fonte vai usar na resposta. Nada mudou no modelo. Nada mudou no prompt. Mudou uma função de vinte linhas que decide onde cortar.

**8.** **[Fecho apontando para o número]** E aqui está o ponto da demo em uma frase: essa diferença apareceu **antes** de existir gerador. Não teve LLM nenhum envolvido nessa tela. É recuperação pura, e ela já decidiu se a resposta vai poder estar certa.

---

## Parte 3 — Hands-on

Seis minutos, em trio ou quarteto. O objetivo declarado é escrever três linhas; o objetivo real é que ninguém saia da sala sem equipe e sem tema provisório.

**1.** **[Projeto o enunciado das três linhas e mando formar os grupos de pé]** Seis minutos. Formem grupos de três ou quatro, e formem de pé — vira mais rápido. Em cada grupo, uma folha, os nomes de todo mundo no topo, e três linhas:

Linha um: o problema, em uma frase, dizendo quem sofre com ele. "Aluno não acha a regra de trancamento" é melhor que "sistema de perguntas e respostas".

Linha dois: as duas técnicas do curso que vocês vão combinar. Podem escrever provisório, ninguém vai cobrar fidelidade nisso hoje.

Linha três, e é a que vale: como vocês vão medir se funciona. Que número, sobre que conjunto.

*Como recolher:* aos 01:48 eu paro a sala e peço a **linha três** de três grupos, em voz alta, escolhidos por mim — de preferência um que escreveu bem e dois que escreveram vago, nessa ordem, para o contraste fazer o trabalho. Comento cada uma em quinze segundos, transformando o vago em concreto ali mesmo: "vinte perguntas que a gente escreve, e a gente conta em quantas o trecho certo apareceu no top-5" é o formato que eu quero ouvir. Recolho todas as folhas — elas viram o registro das equipes e o rascunho zero da Entrega 1. Devolvo com comentário escrito até a Aula 19, para a equipe chegar no Lab 5 já sabendo o que vai medir.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir o fundamento
formal em aula. A regra geral desta aula é remeter ao apêndice e seguir, porque o Bloco 2 termina
com o lançamento do projeto e ele não pode ser comprimido.

**Item 1 — "por que cosseno, e não distância euclidiana?" (A.1, ~4 min).**
A pergunta mais provável do Bloco 2, e a mais fácil de responder bem. Eu escrevo as duas linhas no
quadro: `cos(q,d) = q̂ · d̂` e `‖q̂ − d̂‖² = 2 − 2·cos(q,d)`. E leio a segunda em voz alta: com
vetores normalizados, as duas medidas dão o **mesmo ranking**, então a escolha é de conveniência
de implementação, não de qualidade. O que muda de verdade é o cosseno ignorar comprimento, e isso
é desejável — parágrafo longo não deve ganhar por ser longo. Se não houver tempo nem para isso, a
resposta curta é "dá o mesmo ranking com vetores normalizados, e a conta de duas linhas está em
A.1".

**Item 2 — "o que exatamente a busca aproximada erra?" (A.2, ~5 min).**
Vale fazer se sobrar tempo no slide 11, porque desfaz uma confusão que custa caro no Lab 5. Eu
escrevo a definição de `recall_índice@t` no quadro, com o denominador `t` bem visível, e ao lado
escrevo `recall@k` da próxima aula com o denominador "número de relevantes". Duas frações
diferentes, dois erros diferentes, duas etapas diferentes do pipeline. O ponto que mais convence:
um índice com recall perfeito pode ter `recall@k` zero, e nesse caso trocar de índice não muda
nada.

**Item 3 — "quantas multiplicações são, na prática?" (A.2, ~2 min).**
Se alguém duvidar que força bruta basta no Lab 5, eu faço a conta na tela: cinco mil chunks vezes
trezentos e oitenta e quatro dimensões é um milhão e novecentas mil multiplicações — menos que o
tempo de rede para a consulta chegar. E a comparação com dez milhões de chunks, que é o outro
regime. Dois números, trinta segundos, e a decisão do lab fica justificada em vez de assumida.

**Item 4 — "de onde vem o treino contrastivo?" (A.1, segunda metade, ~4 min).**
Raramente perguntam neste ponto do curso, mas quando perguntam vale: eu escrevo a perda com o
numerador `exp(cos(q,d⁺)/τ)` e o denominador somando os negativos, e mostro que minimizar aquilo
é literalmente empurrar o par positivo para cima e os negativos para baixo. Isso fecha o argumento
do slide 9 de forma definitiva — a geometria é consequência da perda, e o BERT cru não tem essa
perda. Se não houver tempo, a versão em uma frase é: "aproxima o que combina e afasta o que não
combina, e a fórmula está em A.1".

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 15 da Parte 1 — a síntese das nove etapas, a frase de que RAG é um sistema de recuperação com um gerador no fim, a ponte para a Aula 19 pelo ponto cego do retrieval denso, as três tarefas da semana e a devolução das provas no fim.

> Ideia central: "Hoje a gente aprendeu a achar por significado. Semana que vem a gente descobre o que o significado não acha — e é aí que entra o que a busca de vinte anos atrás já fazia bem."

---

*Roteiro do Instrutor · Aula 18 de 30 · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
