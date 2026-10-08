# Recapitulação e fronteiras da área

## Slide 1 · Abertura: a última aula de slide deste curso · 00:00–00:10

**[Projeto a grade da Aula 30 antes de qualquer outra coisa]**

Antes de começar a aula, a logística da semana que vem, porque senão vocês vão me perguntar isso nos próximos quarenta minutos e a aula morre.

Aula 30: slots de quinze minutos por equipe. Doze minutos de apresentação mais perguntas. Sete a oito equipes, ordem sorteada e publicada até a data que está no slide. Demo ao vivo é **obrigatória**, com o sistema real ligado, acompanhada dos números do Lab 8.

**[Aponto os quatro artefatos à esquerda]**

E vocês já têm tudo isso em mãos, desde a semana passada: o conjunto rotulado, a tabela por camada com o `n` declarado, o kappa do juiz e a fila de consertos priorizada.

Agora a aula. Ela tem duas metades que fazem coisas opostas.

> Ideia central: "Na primeira metade eu mostro o que vocês construíram. Na segunda, o que a área está fazendo para derrubar parte disso."

---

## Slide 2 · O mapa do percurso: onde cada peça foi construída, e onde está o fundamento dela · 00:10–00:18

**[Subo a pilha do rodapé para o topo, camada por camada]**

Token, Aula 2, e vocês treinaram BPE à mão no Lab 1. Representação vetorial, Aula 3, mesmo lab — e foi ali que vocês viram cosseno funcionar em paráfrase e falhar em identificador. Atenção e o bloco, Aulas 5 a 8, e no Lab 2 vocês escreveram `softmax(QKᵀ/√d_k)V` com as próprias mãos. Escala e decodificação, Aula 10, Lab 3. Pré-treino, Aula 12. SFT e PEFT, Aula 13, Lab 4. Preferências e raciocínio, 15 e 16. RAG, 18 e 19, Lab 5. Ferramentas e agentes, 21 a 26, Labs 6 e 7. Avaliação, 27, e o Lab 8 foi o harness do sistema de vocês.

Isso é o `git log` da disciplina. Cada aula é um commit, e vocês conseguem apontar o diff.

**[Acendo a segunda coluna e fico em silêncio por uns vinte segundos]**

Agora olhem a coluna da direita. É a primeira vez no curso que ela aparece inteira.

Cada camada tem um segundo endereço: onde está o **fundamento formal** dela. A derivação da atenção em quatro etapas, com a variância do produto escalar e a equivariância por permutação. O fator seis do `C ≈ 6ND`. O `ΔW = BA` com a contagem de parâmetros. Bradley-Terry. O estimador não-viesado de `pass@k`. BM25 e as quatro métricas. O kappa de Cohen e o intervalo de Wilson.

Ao longo do semestre esses apêndices chegaram um por aula, e é fácil ler cada um como um anexo solto. Vistos juntos, eles são outra coisa: são o índice do formalismo deste curso. É o material que não expira quando a fronteira mudar, e é dele que saem os quarenta pontos de justificativa da prova.

> Ideia central: "A coluna da esquerda é o que vocês construíram. A da direita é por que aquilo funciona — e ela continua consultável depois que o semestre acabar."

**[Projeto a tabela de três colunas do exercício e formo as duplas]**

E agora vocês fazem o mesmo com o sistema de vocês. Seis minutos, a condução está na Parte 3.

> Ideia central: "Toda equipe tem uma camada que não foi construída em nenhum lab. Essa é a camada que eu vou perguntar na semana que vem."

---

## Slide 3 · A tese do próximo-token, agora verificável · 00:26–00:33

Na Aula 1 eu afirmei uma coisa a crédito: as tarefas clássicas de NLP foram unificadas sob "prever o próximo token". Vocês não tinham como verificar. Agora têm, em três níveis.

Mecanismo: o decoder com máscara causal produz, por construção, uma distribuição sobre o próximo token. A tarefa não foi escolhida — ela é a arquitetura. Isso é a Aula 6.

Interface: classificação, rotulagem e geração passam a ser instâncias do mesmo objeto, porque a saída é texto e a especificação da tarefa entra no prompt. Aula 10 e Lab 3.

Utilidade: o que transformou o completador em assistente foi SFT e alinhamento. Não arquitetura. Aulas 13 e 15.

> Ideia central: "A unificação moveu a dificuldade. Ela não a eliminou — e o próximo slide cobra a conta."

---

## Slide 4 · A dívida da Aula 1, e a fatura paga · 00:33–00:45

A Aula 1 fechou com uma promessa incômoda, e eu vou repetir ela na mesma palavras: **unificamos o modelo, não unificamos as métricas.**

BLEU e ROUGE pressupõem referência aproximadamente única. Perplexidade só compara entre tokenizadores iguais. Acurácia mente em dados desbalanceados. Quando a interface virou geração aberta, a área herdou um instrumento que não mede o que passou a existir.

**[Aponto a coluna do pagamento]**

Essa dívida foi paga em dois movimentos.

Aula 27, conceitual: a pergunta "esse modelo é bom?" foi substituída por "qual a menor camada que explica esta falha, e com que número eu a meço?". Rubrica com níveis observáveis. Kappa no lugar do acordo bruto. Os três vieses do juiz nomeados, com o protocolo de cada um. Factualidade por afirmações atômicas. E o limite do leaderboard.

Aula 28, operacional: cada equipe construiu o harness do próprio sistema. Métrica por camada, `n` declarado, juiz calibrado contra anotação humana, falhas priorizadas por impacto sobre custo.

> Ideia central: "A Aula 1 prometeu que o custo da unificação tinha sido transferido para a avaliação. As Aulas 27 e 28 são a fatura paga — e o comprovante é a tabela que cada equipe leva para a semana que vem."

---

## Slide 5 · O que este curso deliberadamente não cobriu · 00:45–00:55

Última coisa do Bloco 1, e é a mais desconfortável. Honestidade de escopo.

Pré-treino de verdade em escala: o Lab 2 é um mini-GPT em corpus de brinquedo. RLHF completo com modelo de recompensa treinado: as Aulas 15 e 16 param na formulação e no DPO. Serving em produção com batching contínuo e autoescala: não fizemos. Multimodalidade de fato: é fronteira desta aula, não conteúdo praticado. Segurança adversarial ofensiva além do que a Aula 26 introduziu. E avaliação com significância estatística — o curso exigiu `n` declarado, e o intervalo de confiança ficou no apêndice do Lab 8, não na prática de vocês.

> Ideia central: "Confundir 'vimos' com 'sei fazer em produção' é a distância exata desta lista."

---

*Intervalo · 00:55–01:05*

---

## Slide 6 · O token não é sobre texto: ViT e o patch de 16×16 · 01:05–01:11

Segunda metade. A partir daqui, cada slide traz num canto **o pressuposto do curso que aquela fronteira ameaça** — e essa é a regra de admissão do bloco. Fronteira que não desestabiliza nada do que vocês aprenderam é notícia, não fronteira.

Primeira: o Vision Transformer faz uma coisa só. Corta a imagem em patches de dezesseis por dezesseis pixels, projeta cada patch linearmente num vetor de dimensão `d`, soma um embedding de posição, e joga a sequência num Transformer encoder comum.

**[Aponto a pilha com os dois drivers de entrada embaixo]**

Nada na arquitetura sabe que é imagem. E o que isso revela é maior que multimodalidade: o objeto central deste curso nunca foi *texto*. Foi **sequência de vetores com posição**. O tokenizer da Aula 2 é um caso de discretização; o patch é outro; frames de espectrograma são outro.

> Ideia central: "O Transformer é um processador de sequências que não pergunta de onde a sequência veio."

---

## Slide 7 · [Demo] A conta: 375 tokens de texto contra 3.430 patches · 01:11–01:21

**[Passo para a Parte 2]**

O que muda quando a entrada é imagem é o **custo** dela, e agora eu vou medir. Os passos estão na Parte 2 deste roteiro.

> Ideia central: "A compressão é do codec, não do corte. Ninguém comprime vídeo cortando quadros em quadradinhos."

---

## Slide 8 · Comprimir contexto em pixels: DeepSeek-OCR · 01:21–01:27

O DeepSeek-OCR inverte o uso habitual da visão. Em vez de descrever imagens, usa a imagem como **formato de compressão de texto longo**: renderiza o documento como página, um encoder visual produz poucos tokens visuais, e o decoder reconstrói o texto.

O artigo reporta reconstrução em torno de noventa e sete por cento de precisão de decodificação na faixa de dez tokens de texto por token visual, e isso degrada para a faixa de sessenta por cento perto de vinte vezes.

**[Aponto os dois patamares na curva]**

E aqui está o que eu quero que vocês levem: o número relevante nunca é a compressão sozinha. É o **par**.

> Ideia central: "Fidelidade de reconstrução é recall de conteúdo com outro nome — e o instrumento que mede é o do Lab 8."

Isto é uma alternativa de engenharia ao RAG das Aulas 18 a 20, para documentos longos e estáveis. E ela tem exatamente o mesmo tipo de trade-off que vocês já sabem medir.

---

## Slide 9 · Difusão para linguagem: o pressuposto que atravessou 28 aulas · 01:27–01:35

Este é o slide que eu mais gosto de dar em todo o curso.

Vinte e oito aulas pressupuseram uma coisa que ninguém nomeou: geração **da esquerda para a direita**. A máscara causal da Aula 6. O KV cache da Aula 8. A amostragem token a token do Lab 3. Até a forma como o prompt é montado.

O LLaDA treina um modelo de difusão mascarada. O processo direto mascara tokens progressivamente, e o modelo aprende a **prever os mascarados**. A geração é iterativa: desmascara posições em qualquer ordem, refinando a sequência inteira a cada passo. Não há máscara causal, e não há "próximo" token.

**[Aponto as duas linhas do tempo de geração]**

O que isso ataca, item por item. O KV cache perde o sentido, porque não existe prefixo fixo cujo estado se reaproveita. A decodificação deixa de ser escolha de amostragem por posição e passa a ser política de quantas e quais posições desmascarar por passo. A latência deixa de ser linear no número de tokens e passa a ser função do número de passos de refinamento — o que abre um paralelismo que o autorregressivo não tem. E a maldição da reversão, aquele modelo que sabe "A é B" e falha em "B é A", é atacada na raiz, porque o treino não privilegia direção nenhuma.

> Ideia central: "Um pressuposto que atravessa 28 aulas sem ser nomeado é um pressuposto, não uma lei."

---

## Slide 10 · Dados sintéticos e colapso de modelo · 01:35–01:41

Dado sintético é insumo padrão hoje. Instruções geradas para SFT, pares de preferência gerados, casos de teste gerados. Vocês mesmos usaram no Lab 8.

O custo aparece quando isso é **recursivo**: treinar a geração `n+1` predominantemente na saída da geração `n` corrói a distribuição. Três fontes de erro somadas — amostragem finita, que perde os eventos raros; expressividade, que não representa a cauda; e otimização. E o efeito é cumulativo.

**[Aponto as quatro distribuições em sequência]**

Primeiro desaparecem as **caudas**: a variância encolhe, o raro vira improvável, e o centro continua parecido — que é justamente o que torna o problema difícil de detectar. Depois a distribuição converge para algo estreito e distante da original.

É fotocópia de fotocópia. Cada geração é legível; a décima não tem mais as letras finas.

> Ideia central: "O resultado não é 'sintético é ruim'. É sobre realimentação recursiva sem âncora humana."

E respondendo a pergunta concreta que sempre vem: caso de teste gerado por LLM e **revisado por vocês** é legítimo. O rótulo é humano, e isso é exatamente o que o Lab 8 exigiu. Sintético verificado por oráculo — código que passa em teste, matemática conferida — não é a mesma operação que sintético plausível.

---

## Slide 11 · A fronteira do custo: pequeno, roteado, medido · 01:41–01:45

A pressão da área deslocou-se de "o maior possível" para "o suficiente pelo menor custo". Três movimentos.

Modelos pequenos: um modelo de um a oito bilhões com bom SFT resolve a maior parte das tarefas de um produto. Foi o que vocês usaram nos labs, por escolha didática — que também é a escolha de engenharia. Roteamento: um classificador barato decide, por requisição, se ela vai para o modelo local, para a API ou para uma cascata com verificação, e a métrica é acerto por real gasto. Esparsidade: MoE ativa uma fração dos parâmetros por token.

**[Aponto as duas colunas novas na tabela do Lab 8]**

E a consequência metodológica, que é o que importa aqui: eficiência entra na tabela do Lab 8 como qualquer outra métrica. Custo por caso, latência p95, tokens por resposta, ao lado do `recall@k` e da nota do juiz.

> Ideia central: "Sistema que acerta mais e custa dez vezes mais é decisão de produto. Sem as duas colunas na tabela, ela não é tomada — é sofrida."

---

## Slide 12 · Hardware: a atenção é limitada por memória · 01:45–01:50

Última fronteira, e ela explica três coisas que vocês já usaram sem que eu tivesse derivado.

Na decodificação, cada token novo precisa ler o KV cache **inteiro** para produzir uma posição. A razão entre operações aritméticas e bytes lidos é baixíssima — da ordem de uma operação por byte. E um acelerador moderno consegue fazer centenas de operações por byte de banda.

**[Aponto as duas barras e a distância entre elas]**

O acelerador passa quase todo o tempo esperando memória. Daí três coisas. FlashAttention ganha por reduzir tráfego entre HBM e SRAM, não por reduzir contas. GQA e MQA ganham por encolher o objeto que é lido. E batching ganha por amortizar a leitura dos pesos entre requisições — é o único dos três que muda a razão de fato.

O pano de fundo é o *memory wall*: capacidade de cálculo e banda de memória cresceram em ritmos muito diferentes na última década, e a segunda virou o gargalo.

> Ideia central: "Para inferência autorregressiva, banda de memória prediz desempenho melhor do que TFLOPs de pico."

E amarrando com o slide 9: difusão mascarada processa todas as posições por passo, então tem um perfil de acesso a memória diferente. É por isso que ela é interessante do ponto de vista de sistemas, não só de modelagem.

---

## Slide 13 · Pesquisa, engenharia de IA, e o meio · 01:50–01:54

Três caminhos, distinguidos por **artefato** e **critério de sucesso** — não por prestígio.

Pesquisa produz conhecimento novo verificável. O artefato é o paper com código, o critério é revisão por pares e reprodutibilidade. Preparação: reimplementar do zero, ler com caneta, iniciação científica, procurar orientador cujo trabalho você consegue explicar.

Engenharia de IA produz sistemas que funcionam em produção. O artefato é o serviço com SLO, o critério é usuário atendido a custo sustentável. É exatamente o que esta disciplina treinou.

Research engineering é o meio: infraestrutura de treino, avaliação em escala, otimização de kernels. Costuma ser o de maior alavancagem para quem gosta de sistemas e de pesquisa em doses iguais.

> Ideia central: "O diferencial no mercado não é saber chamar API. É saber provar com número que o sistema funciona — que é a única coisa que o Lab 8 fez."

---

## Slide 14 · O que estudar em seguida, na ordem · 01:54–01:57

Fundamentos primeiro. Jurafsky e Martin, capítulos de Transformers e LLMs, e o Raschka, para o lado do modelo. Huyen para o lado do sistema. Depois **um** paper por semana, lido a fundo, com reimplementação de um componente.

**[Aponto o degrau zero da trilha]**

E o degrau zero vocês já têm: os apêndices dos trinta decks. Fundamento de atenção e de otimização não tem meia-vida curta — agentes e fronteiras revisam-se a cada oferta, aquilo não.

> Ideia central: "O exercício que mais separa 'acompanhei o curso' de 'sei construir' é reimplementar um componente do Lab 2 sem olhar o notebook."

---

## Slide 15 · O arco fechado, e a ponte para a Aula 30 · 01:57–02:00

**[Volto à pilha do slide 2, com a coluna de fundamento acesa]**

Na Aula 1 eu disse que a gente ia unificar o modelo e que a conta viria na avaliação. A conta veio, e vocês pagaram: cada equipe tem um harness com número por camada.

E a coluna da direita é a outra metade do que vocês levam. Os apêndices dos trinta decks são o índice do formalismo deste curso — é ele que sustenta os quarenta pontos de justificativa da prova, e é ele que sustenta a defesa oral da semana que vem.

**[Projeto a grade da Aula 30 e o checklist]**

Semana que vem: sistema ligado, tabela do Lab 8 na mão, slide de arquitetura com o inventário que vocês fizeram hoje.

> Ideia central: "Na semana que vem quem fala são vocês — e a pergunta que eu faço sai da camada que a equipe não conseguiu endereçar a nenhuma aula."

---

## Parte 2 — Demonstração guiada

Oito minutos, `codigo/demo-patches-como-tokens.py`, no terminal, cem por cento offline e determinística. O script não baixa nada e não precisa de rede.

Ele tem duas rotas para contar tokens de texto: se `transformers` estiver instalado, usa um tokenizer real e imprime o nome dele; se não, usa um contador determinístico por regex documentado no arquivo. Nos dois casos ele **declara na saída qual rota usou** — a mesma exigência de procedência do Lab 8.

**1.** **[Rodo o script e paro no primeiro bloco]** Esta é a página de texto embutida no script, um trecho de regulamento com mil quatrocentos e sessenta e seis caracteres. E aqui está a contagem: trezentos e setenta e cinco tokens pela rota offline — e olhem que ele imprimiu qual rota usou.

**2.** **[Mostro o bloco da geometria]** Agora a mesma página renderizada como imagem. A4 a noventa e seis DPI dá setecentos e noventa e três por mil cento e vinte e dois pixels. Com patch de dezesseis por dezesseis: quarenta e nove por setenta, **três mil quatrocentos e trinta patches**. **[deixo o silêncio]** A versão em imagem tem nove vezes **mais** unidades de sequência que a versão em texto.

**3.** **[Vario o DPI e o tamanho do patch]** E olhem uma propriedade que texto não tem: o número de patches é função da resolução e do patch, **não do conteúdo**. A página em branco e a página cheia têm exatamente o mesmo custo em patches. Isso já deveria acender uma luz sobre o que a imagem está comprimindo.

**4.** **[Introduzo o fator de redução do encoder]** Agora o passo que desfaz a confusão. Com um encoder que comprime a grade em dezesseis vezes, três mil quatrocentos e trinta viram duzentos e catorze tokens visuais. A razão texto sobre visual sai de zero vírgula onze para um vírgula setenta e cinco, e a compressão finalmente aparece. A compressão é do **codec**, não do corte.

**5.** **[Mostro a tabela final de compressão × fidelidade]** E o fecho: os patamares que o artigo reporta. Na faixa de dez vezes, precisão de decodificação em torno de noventa e sete por cento; perto de vinte vezes, na faixa de sessenta. O número relevante é o par, nunca a compressão sozinha.

**6.** **[Fecho ligando ao Lab 8]** E fidelidade de reconstrução é `recall` de conteúdo com outro nome. O instrumento que mede isso é o que vocês construíram na semana passada.

---

## Parte 3 — Hands-on

Seis minutos de dupla mais dois de correção, dentro do slide 2. É o único hands-on da aula: a prática desta unidade aconteceu no Lab 8, e o resto do tempo é expositivo por decisão de desenho.

**1.** **[Projeto a tabela de três colunas e formo as duplas, de preferência da mesma equipe de projeto]** Seis minutos. Vocês vão escrever o sistema do próprio projeto decomposto em camadas e, ao lado de cada camada, **a aula e o lab em que aquela peça foi construída** e o artefato que sobrou no repositório de vocês. Quatro a seis linhas basta.

Exemplo, para arrancar: tokenização e contagem de custo, Aula 2 e Lab 1, e o artefato é o notebook com tokens por língua. Recuperação, Aulas 18 e 19 e Lab 5, e o artefato é a tabela de `recall@k`.

*Como recolher:* dois minutos, e eu peço uma coisa só de cada dupla — **nomear em voz alta uma camada do próprio sistema que ela não construiu em nenhum lab**. Anoto todas. Essa é a camada que a equipe vai ter mais dificuldade de defender na Aula 30, e é de onde sai a minha pergunta. Quase sempre é a camada em que o sistema copiou código sem entender, e a defesa oral testa exatamente isso.

*Extensão opcional, para depois da aula:* para cada camada do inventário, responder em voz alta em uma frase por que ela existe no sistema e **que número do harness prova que ela funciona**. A camada que não tiver as duas respostas é a que recebe a pergunta.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência. Mas nesta aula ela tem um peso diferente: é a **última** oportunidade do semestre de o formalismo ser puxado em sala, e se houver tempo vale atender com generosidade em vez de remeter.

**Item 1 — "De onde sai esse objetivo da difusão? Ele é o MLM com outro nome?" (A.1, ~6 min).**
A melhor pergunta possível nesta aula, e a resposta é quase sim. Eu escrevo o processo direto no quadro — cada posição mascarada com probabilidade `t`, independentemente — e depois o objetivo. E aí faço a comparação que responde de verdade: o MLM da Aula 8 é este objetivo com `t` **fixo** em zero vírgula quinze; aqui `t` é sorteado uniformemente em zero e um. É a variação de `t` que faz a diferença, porque o MLM em taxa fixa nunca vê a sequência quase toda mascarada, e por isso não aprende a construir texto do zero. **Versão de 30 segundos:** "é o MLM com taxa de mascaramento variável em vez de fixa em 15% — e é essa variação que permite gerar, porque o regime de máscara quase total é geração a partir de nada. Está em A.1, com o fator `1/t` explicado."

**Item 2 — "Isso de colapso é real ou é alarmismo?" (A.2, ~4 min).**
Pergunta cética, e ela merece o melhor argumento que eu tenho. Eu tomo o caso gaussiano: família correta, otimização exata, dado limpo, e o **único** mecanismo em ação é a amostragem finita. O estimador de variância por máxima verossimilhança tem esperança `σ²·(n−1)/n`. Iterando `k` gerações, a variância vai a `σ₀²·((n−1)/n)^k`. Escrevo isso, instancio com mil amostras — zero vírgula um por cento por geração, e em mil gerações resta trinta e sete por cento. **Versão de 30 segundos:** "no caso mais favorável possível, com família correta e otimização exata, a variância decai geometricamente só por amostragem finita. A conta está em A.2, com o motivo de essa fonte de erro não desaparecer nem com modelo perfeito."

**Item 3 — "Por que FlashAttention acelera se não faz menos contas?" (A.3, ~5 min).**
A pergunta que fecha o arco técnico do curso, e eu adoro quando ela vem nesta aula. Escrevo a intensidade aritmética: operações por byte lido. Instancio nos dois regimes — contexto curto, dominado pelos pesos, e contexto longo, dominado pelo cache — e mostro que nos **dois** ela dá da ordem de um. Um acelerador faz centenas de operações por byte de banda. Então a decodificação usa uma fração de um por cento da capacidade aritmética, e reduzir bytes lidos é reduzir tempo. **Versão de 30 segundos:** "porque a decodificação faz cerca de uma operação por byte lido, e o acelerador conseguiria fazer centenas — o gargalo é a memória, não a conta. É a mesma razão de GQA acelerar a geração. Está em A.3, com os dois regimes instanciados e o caso do batching."

---

## Encerramento · 01:57–02:00

O encerramento está redigido como fala no Slide 15 da Parte 1 — a dívida da Aula 1 devolvida e quitada, a coluna do fundamento acesa como a segunda metade do que a turma leva, a logística da Aula 30 repetida, o checklist projetado, e os vinte segundos finais de índice do apêndice.

> Ideia central: "A coluna da esquerda é o que vocês construíram. A da direita é por que aquilo funciona. As duas continuam suas depois de quinta-feira."

---

*Roteiro do Instrutor · Aula 29 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
