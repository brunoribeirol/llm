---
aula: 12
titulo: "Pré-treinamento: dados, leis de escala e sistemas"
tipo: teorica
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 12 de 30

> **Rebalanceamento V2.** A aula é conduzida por três defeitos de fábrica e fecha cada um pela causa. As contas aparecem enunciadas com o número que produzem; as seis derivações estão no apêndice. **`C ≈ 6ND` é a derivação que a Aula 10 prometeu para cá** — se a turma puxar, atender: está na Parte 4, item 1, com cinco minutos de quadro preparados.

## Como usar este roteiro

A prosa é fala em primeira pessoa: é o que eu digo, na ordem em que digo. As linhas com `🗣️` são as frases-âncora, faladas quase literalmente.

As notas `Bastidor:` **não** são faladas. As direções entre `**[…]**` são a ação física.

A **Parte 4** é contingência: as derivações que a turma pode pedir ao vivo, com custo em minutos, versão de trinta segundos e ordem de sacrifício. Nesta aula ela é especialmente importante, porque a Aula 10 mandou a turma para cá com uma pergunta na mão.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · Abertura: três defeitos, nenhum deles no código · 00:00–00:05

**[Projeto os três defeitos juntos e leio os três em voz alta antes de dizer qualquer outra coisa]**

Aula passada vocês puxaram quatro alavancas e mediram o efeito de cada uma em três eixos. Hoje a gente entra na fábrica que produziu o arquivo de pesos que estava do outro lado daquelas alavancas.

E a primeira coisa que a fábrica tem não é uma GPU. É um **orçamento**.

Três defeitos. Primeiro: "tenho um orçamento fechado, faço um modelo maior ou treino com mais tokens?" — e a indústria inteira respondeu isso errado até 2022, com dinheiro de verdade. Segundo: o treino estoura a memória da GPU **antes** de estourar a aritmética; dá `OOM` com a placa a trinta por cento de ocupação. Terceiro: o modelo devolve, palavra por palavra, um parágrafo do corpus — e acerta um benchmark que estava na web.

**[Aponto a coluna "onde fecha"]**

Nenhum dos três é bug de implementação. Os três são consequência correta de uma decisão de orçamento tomada antes da primeira linha de código. E cada um fecha num slide específico desta aula.

> 🗣️ "Vocês passaram duas aulas puxando alavancas. Hoje a gente entra na fábrica — e a primeira coisa que a fábrica tem é um orçamento."

> **Nota:** Bastidor: ler os três e **não resolver nenhum agora**. O defeito 2 é o mais concreto para quem sofreu `OOM` no Lab 2 — usar como isca, perguntando quem levou `OOM` lá. Recap do Lab 3 em uma frase só: as alavancas medidas em três eixos, com campo de proveniência.

---

### Slide 2 · O número que vocês trouxeram · 00:05–00:10

Lição de casa da aula passada. Quem tem aí o `N` e o `D` do modelo que rodou no Ollama?

**[Preencho os dois campos na tela com o que a turma disser]**

Agora as duas contas da aula, e eu vou só enunciar as duas.

Treinar custa aproximadamente **seis vezes** `N` vezes `D` — parâmetros vezes tokens. Gerar um token custa aproximadamente **duas vezes** `N`. Nada de derivação agora; olhem o que as duas dizem.

A primeira diz que treinar custa proporcional a **capacidade vezes experiência**. A segunda diz que gerar custa proporcional só à **capacidade ativa** — o `D` não aparece, porque o modelo já foi treinado.

E é aí que está a economia inteira desta área: treinar é caríssimo e acontece **uma vez**. Inferir é barato por token e acontece um trilhão de vezes.

> 🗣️ "Uma conta de guardanapo separa o que se paga uma vez do que se paga para sempre."

**[Escrevo `D/N` no quadro com o valor da turma e circulo]**

Agora dividam `D` por `N`. Esse número fica no quadro a aula inteira, porque no meio dela uma teoria vai dizer que o valor certo é **vinte**. E o de vocês não é vinte.

> **Nota:** Bastidor: fazer a multiplicação de `6ND` devagar na tela, com as potências de dez alinhadas verticalmente — turma sem prática de ordem de grandeza erra o expoente e o número perde sentido. **Dizer em voz alta que esta é a derivação que a Aula 10 prometeu para hoje**, porque parte da turma perguntou lá. Não derivar aqui: A.1 tem a conta inteira, e a Parte 4 tem a versão de quadro em 5 min. E **não** resolver o paradoxo do `D/N` — ele é o fechamento da aula.

---

### Slide 3 · Transferência de aprendizado: um treino caro, muitas tarefas baratas · 00:10–00:15

Antes: uma tarefa, um dataset rotulado à mão, um modelo, um deploy. O teto era o custo de anotação — você conseguia resolver tantas tarefas quantas conseguisse pagar para rotular.

Depois: um objetivo genérico, um pré-treino caríssimo, e adaptação com pouco ou nenhum dado novo. O teto virou o custo de compute.

**[Aponto a régua logarítmica embaixo]**

E para quem não fez Aprendizagem de Máquina antes: treinar é ajustar pesos por descida de gradiente para reduzir uma perda. A perda do pré-treino é **a mesma** entropia cruzada do próximo token que vocês minimizaram no Lab 2, no mini-GPT de dois vírgula sete milhões de parâmetros.

> 🗣️ "A perda do pré-treino é a mesma que vocês minimizaram no Lab 2. A diferença para o GPT-3 não é de ideia — é de orçamento."

> **Nota:** Bastidor: é aqui que a metade da turma sem ML se perde ou se salva. Se as mãos hesitarem, gastar 60 s extras na definição de perda e gradiente. **Não** abrir teoria de otimização — não cabe e não é o ponto.

---

### Slide 4 · O rótulo que não existe: o supervisor é o corpus · 00:15–00:20

Em aprendizado supervisionado clássico, alguém rotula. E o limite do que você consegue fazer é o quanto consegue pagar para rotular.

No pré-treino ninguém rotulou nada. O rótulo de cada posição é **o token seguinte**, que já está no corpus.

**[Aponto a conta na tela]**

E olhem a densidade disso. No Lab 2, um lote de sessenta e quatro por cento e vinte e oito produzia oito mil cento e noventa e duas previsões supervisionadas de uma vez. De texto cru, sem ninguém anotar nada.

Uma correção de vocabulário, porque ela tem consequência. Isso não é "não supervisionado". É **auto-supervisionado** — o rótulo existe, ele é só derivado do dado em vez de anotado por gente.

E a consequência prática é a frase mais importante deste bloco:

> 🗣️ "O supervisor deste treino é o corpus. Então a qualidade do corpus é decisão de modelagem, não de infraestrutura."

E é por isso que a próxima meia hora é sobre corpus.

> **Nota:** Bastidor: se perguntarem por que se chama auto-supervisionado, é convenção para marcar que o rótulo é derivado sem anotação humana — não brigar com o termo. Este slide é a ponte para o defeito 3: se o supervisor é o corpus, um corpus com duplicata supervisiona a mesma coisa duas vezes.

---

### Slide 5 · De onde vem o texto: a mistura do corpus · 00:20–00:26

Quatro fontes, e cada uma ensina uma coisa que as outras não ensinam.

Web, dos derivados do CommonCrawl: trilhões de tokens, qualidade média baixa. O que ela dá é **quantidade** — e quantidade é insubstituível.

Livros: volume médio, qualidade alta. O que só eles dão é **coerência longa** — dependência entre coisas separadas por milhares de tokens. Não existe outra fonte com texto tão longo e tão coerente.

Código: volume médio, e uma propriedade única — a qualidade é **verificável**. O que ele ensina é formato e estrutura estrita. E aquele JSON que vocês pediram no Lab 3 e receberam perfeitamente formatado veio daqui.

Curado, enciclopédico: volume pequeno, qualidade alta, **densidade de fato**.

**[Aponto a faixa inferior]**

E a mistura — quantas épocas de cada fonte — é uma decisão de treino. É exatamente o ponto em que os cartões de modelo ficam vagos.

Agora, "curadoria importa" é a frase mais vazia que se pode dizer sobre isso, então eu vou dar a linhagem, porque ela é pública e é comparável. Começa em dois mil e dezenove com o CCNet, que filtra a web pela semelhança com a Wikipédia, e o C4, que filtra por regras. Passa pelo Gopher em vinte e um. E aí vêm os modernos: DCLM e FineWeb em vinte e quatro, Nemotron-CC no mesmo ano, OLMo 2 em vinte e cinco.

E o que separa uma receita da outra são **dois** mecanismos, só dois. O primeiro é **deduplicação**, na prática por MinHash — porque a web repete, e repetição não vira generalização, vira memorização. Isso é literalmente o defeito três desta aula, o parágrafo que o modelo devolve literalmente. O segundo é **filtro de qualidade por classificador**: em vez de escrever regra a regra, treina-se um classificador barato para separar texto tipo-Wikipédia de texto tipo-web-bruta, e joga-se fora a cauda.

> 🗣️ "Curadoria não é adjetivo. São duas decisões — deduplicar e filtrar por classificador — e a diferença entre uma receita de dado e outra está quase toda aí."

> 🗣️ "Nenhuma das quatro fontes sozinha dá o modelo."

> **Nota:** Bastidor: direito autoral de corpus é pergunta legítima e vai aparecer aqui. É Aula 29 — não abrir agora, consome 15 min e desmonta o bloco. Resposta de dez segundos: "é questão aberta e séria, e a gente trata na Aula 29".

---

### Slide 6 · [Defeito 3 fechado] O parágrafo que o modelo devolve literalmente · 00:26–00:33

Defeito três, e agora com a causa.

Um documento que aparece em mil espelhos da web é visto mil vezes pelo modelo. E um exemplo visto mil vezes não é aprendido — é **memorizado**.

Três efeitos, e nenhum deles é sobre estética de dados. Primeiro: orçamento gasto em repetição. Cada passada por uma duplicata é compute que não comprou generalização nenhuma. Segundo: memorização literal, que é o sintoma do slide 1 e é também um risco de vazamento. Terceiro, e é o pior de todos: **contaminação de benchmark**. Se o conjunto de teste estava na web, o modelo não acertou a prova — ele já tinha visto o gabarito.

> 🗣️ "Deduplicar não é limpeza. É orçamento — e é a diferença entre um número de benchmark que significa algo e um que não significa nada."

> **Nota:** Bastidor: o terceiro efeito é o que amarra com a Aula 27 (contaminação e o limite do leaderboard) — sinalizar sem abrir. Se alguém perguntar como se detecta contaminação, a resposta curta é n-grama do conjunto de teste contra o corpus, e o problema é que quase ninguém publica o corpus.

---

### Slide 7 · Leis de escala: a perda cai como lei de potência · 00:33–00:40

Agora a parte que transformou isto de artesanato em engenharia.

A perda de teste cai como **lei de potência** no compute. Em escala log-log, isso é uma reta. E o que uma reta permite é a coisa mais valiosa que existe quando se vai gastar milhões: **prever antes de gastar**.

**[Aponto a reta no gráfico]**

Kaplan e coautores estabeleceram as potências: quanto a perda cai por década de compute, de parâmetros, de dados. Não é lei da natureza — é ajuste empírico dentro de um regime. Mas dentro daquele regime ele extrapola, e foi isso que autorizou os saltos de escala que vieram depois.

> 🗣️ "Uma reta em log-log é a diferença entre apostar milhões e estimar milhões."

> **Nota:** Bastidor: a pergunta boa aqui é "e fora do regime ajustado?". Resposta honesta: não se sabe, e é onde a área erra. A.3 tem o significado do expoente e a discussão de extrapolação. Não gastar mais de 40 s nisso — o slide 8 é onde está o valor.

---

### Slide 8 · [Defeito 1 fechado] A pergunta não era "quão grande" — era "como dividir o cheque" · 00:40–00:47

Defeito um. E aqui está a mudança de pergunta que vale a aula inteira.

Durante anos a pergunta foi "quão grande dá para fazer o modelo?". A pergunta certa era outra: **dado um cheque fechado, como dividir entre capacidade e experiência?**

**[Desenho o U no quadro enquanto falo]**

Fixem o compute. Agora variem `N`, e com `C` fixo o `D` varia junto na direção oposta — porque `C` é seis vezes `N` vezes `D`. Modelo grandinho treinado pouco: perda alta, porque falta experiência. Modelo pequeno treinado muito: perda alta, porque falta capacidade.

No meio tem um **mínimo**. E é um mínimo interior, não um extremo.

Chinchilla mediu isso, e a razão que sai do fundo do U é aproximadamente **vinte tokens por parâmetro**.

> 🗣️ "O mínimo do U não é opinião de arquitetura. É onde as duas potências se cruzam."

E é por isso que a indústria errou: todo mundo estava andando na parede esquerda do U, fazendo modelos cada vez maiores treinados com muito menos dados do que deveriam.

> **Nota:** Bastidor: desenhar o U no quadro **antes** de a demo mostrar as curvas — a demo confirma o desenho, e a ordem importa. Se alguém apontar que o `D/N` do modelo dele é muito maior que vinte, dizer "guarda essa pergunta, ela é o fechamento da aula" e seguir. Não antecipar.

---

### Slide 9 · [Demo] A curva isoFLOP e o ponto ótimo · 00:47–00:55

**[Passo para a Parte 2]**

Os passos estão na Parte 2. O que eu digo antes de trocar de tela é o aviso de proveniência, porque ele é conteúdo:

As constantes da superfície de perda deste script são calibradas para fins didáticos. Elas reproduzem a razão de vinte para um, mas **não** são os coeficientes publicados do ajuste. Eu digo isso porque é exatamente a exigência que o Lab 8 vai fazer com vocês: número na tela vem com procedência declarada.

> 🗣️ "O mínimo do U não é opinião. É onde as duas potências se cruzam — e a razão que sai dali é vinte tokens por parâmetro."

> **Nota:** Bastidor: terminal com fonte grande. Se o `matplotlib` não abrir janela, PNGs da véspera; sem Python, o U no quadro em 90 s. **Os números desta demo voltam nos slides 10, 15 e 16** — a coluna `D/N = 20`, o contrafactual `51 B / 1,02 T` e o par `6,0e20 → 2,2 B`. Intervalo de 10 min imediatamente depois.

---

*Intervalo · 00:55–01:05*

---

### Slide 10 · `C ≈ 6ND` com hora de GPU real · 01:05–01:11

Segunda metade. A primeira foi sobre o orçamento; esta é sobre a máquina que tem de executá-lo.

E a primeira coisa é converter FLOPs em algo que se compra. Pico da placa em TFLOP por segundo, vezes o número de placas, vezes segundos, vezes a **MFU** — a fração do pico que se aproveita de verdade, que na prática fica entre trinta e cinquenta por cento.

**[Aponto a conta na tela]**

Isso dá o `C` que vocês têm. E com o `C`, a alocação do slide 8 diz o `N` e o `D`.

> 🗣️ "Daqui para frente, orçamento não é abstração: é número de placas vezes dias vezes a fração que você realmente aproveita."

> **Nota:** Bastidor: a MFU é o número que surpreende — se alguém perguntar por que não é cem por cento, a resposta curta é comunicação, carregamento de dados e kernels que não saturam. O slide 13 e o A.5 tratam da parte de comunicação.

---

### Slide 11 · [Defeito 2 fechado] O `OOM` que acontece com a GPU ociosa · 01:11–01:21

Defeito dois, e é o mais concreto da aula para quem já sofreu.

Por que dá `OOM` com a placa a trinta por cento de ocupação? Porque memória e aritmética são **dois recursos diferentes**, e o treino consome os dois em proporções que não têm nada a ver.

**[Aponto os quatro blocos]**

Quatro consumidores, não um. Os pesos. Os gradientes, que têm o mesmo tamanho dos pesos. Os dois momentos do Adam, que juntos têm o dobro do tamanho dos pesos. E as **ativações**.

Os três primeiros dão a conta famosa: **dezesseis bytes por parâmetro**. Um modelo de um bilhão de parâmetros precisa de dezesseis gigabytes só para existir em treino, antes de processar um único token.

E as ativações são a parte traiçoeira, porque elas não escalam com o modelo — escalam com **lote vezes contexto**. É o que estoura sem aviso quando alguém aumenta o batch para "aproveitar melhor a GPU".

> 🗣️ "Dezesseis bytes por parâmetro é o que o modelo precisa para existir. As ativações são o que ele precisa para pensar — e são elas que estouram."

> **Nota:** Bastidor: perguntar quem levou `OOM` no Lab 2 e o que fez para resolver. Quase sempre a resposta é "diminuí o batch" — e aí está a confirmação experimental do argumento, dada pela própria turma. **Não fazer a multiplicação fator a fator no quadro**: está em A.4, e o slide já traz o resultado com a unidade.

---

### Slide 12 · Precisão mista: bf16 para calcular, fp32 para acumular · 01:21–01:26

Metade da memória e o dobro da velocidade, com uma ressalva que é o ponto do slide.

Calcula-se em bf16 — dezesseis bits — porque é rápido e é metade da memória. Mas **acumula-se** em fp32.

A razão é aritmética: somar milhares de números pequenos em meia precisão perde os pequenos. Quando o gradiente de um passo é muito menor que o valor acumulado, ele simplesmente desaparece na soma. Em fp32 não desaparece.

> 🗣️ "bf16 para calcular, fp32 para acumular. A precisão baixa é para velocidade; a alta é para não perder o gradiente pequeno."

> **Nota:** Bastidor: slide para comprimir a 2 min se o tempo apertar. O que não se corta é a razão da acumulação em fp32 — é a única coisa aqui que responde uma pergunta de prova.

---

### Slide 13 · Paralelismo de dados, de tensor e de pipeline · 01:26–01:36

Se não cabe numa placa, distribui. E há três formas de distribuir, que particionam coisas diferentes e **comunicam** coisas diferentes.

**[Aponto os três diagramas em sequência]**

Paralelismo de **dados**: cada placa tem o modelo inteiro e um pedaço do lote. Comunica **gradientes**, ao fim de cada passo. É o mais simples e o primeiro a se tentar. Com estados do otimizador particionados, ele também resolve boa parte do problema de memória.

Paralelismo de **tensor**: a mesma camada é fatiada entre placas. Comunica **ativações**, no meio da camada, muitas vezes por passo. É rápido dentro de um nó com interconexão boa e ruim atravessando nós.

Paralelismo de **pipeline**: camadas diferentes em placas diferentes. Comunica ativações **entre estágios**, e o problema dele é a bolha — placas ociosas esperando o estágio anterior.

> 🗣️ "A pergunta não é 'qual paralelismo é melhor'. É 'o que eu passo a comunicar, e quantas vezes por passo'."

> **Nota:** Bastidor: a resposta que a turma dá por default é "tensor", porque soa mais sofisticado. Corrigir com o critério: comece por dados, e só vá para tensor quando uma camada isolada não couber. O volume exato de comunicação de cada um está em A.5, e é o que responde o item 3 do exercício.

---

### Slide 14 · FlashAttention: atenção exata, consciente da memória · 01:36–01:44

Última peça, e é a que mais confunde.

FlashAttention é atenção **exata**. Não é aproximação, não é esparsidade, não é janela. O resultado é bit a bit o mesmo da atenção padrão.

E ainda assim ela é várias vezes mais rápida. Como?

**[Aponto o diagrama de HBM e SRAM]**

Porque a atenção padrão materializa a matriz `n × n` de escores na memória principal da placa, escreve, lê de volta, aplica o softmax, escreve, lê de novo. FlashAttention processa em blocos que caibam na memória rápida e **nunca materializa** a matriz inteira.

A complexidade assintótica é a mesma. O número de contas é praticamente o mesmo. O que muda é o número de **idas e voltas à memória lenta** — e nesse regime é a memória que manda, não a aritmética.

> 🗣️ "Mesma complexidade, mesmas contas, menos tráfego. E é o tráfego que estava custando o tempo."

> **Nota:** Bastidor: a frase "não muda a complexidade e ainda assim acelera" é contraintuitiva e é ponto de prova. A contagem de acessos a HBM nos dois esquemas está em A.6, e ela liga com o A.3 da Aula 29, que estabelece a intensidade aritmética do regime de decodificação. Se sobrar tempo, essa é a melhor conexão de curso para fazer aqui.

---

### Slide 15 · [Exercício] Decidir, não calcular · 01:44–01:50

**[Projeto o cenário e formo as duplas]**

Quatro minutos, em dupla. E o cenário já está resolvido na tela — a demo imprimiu os números. O que eu quero é a **decisão**.

Oito placas equivalentes a A100 por sete dias, pico de trezentos e doze TFLOP por segundo em bf16, MFU de quarenta por cento. A demo disse: seis vezes dez à vigésima FLOPs, dois vírgula dois bilhões de parâmetros, quarenta e cinco bilhões de tokens.

Quatro perguntas. Esse modelo cabe? O que estoura primeiro, memória ou aritmética — e que **medição** confirma? Se não couber numa placa, qual paralelismo primeiro, e o que ele passa a comunicar? E a quarta: vocês têm quarenta e cinco bilhões de tokens de orçamento e um corpus cru de trezentos bilhões com quarenta por cento de duplicata. Filtrar agressivamente ajuda ou atrapalha?

> 🗣️ "Nenhuma das quatro pede derivação. As quatro pedem saber o que a conta prevê."

As fórmulas que vocês precisam estão no rodapé do slide. Isto não testa memória de fórmula.

> **Nota:** Bastidor: condução na Parte 3. Erro nº 1 no item 1 é contar só os pesos e concluir que cabe folgado; erro nº 2 no item 3 é responder "tensor". O **item 4 é o que amarra o Bloco 1 ao Bloco 2** e é o que eu corrijo se só houver tempo para um.

---

### Slide 16 · Fechamento: a fábrica entrega um completador de texto · 01:50–02:00

**[Volto aos três defeitos, riscados, com a causa ao lado]**

Defeito um, a divisão do cheque: a curva isoFLOP tem mínimo interior. Defeito dois, o `OOM` com a placa ociosa: dezesseis bytes por parâmetro mais as ativações. Defeito três, o parágrafo literal: duplicata memoriza e contamina.

**[Aponto o `D/N` que está no quadro desde o slide 2]**

E agora o paradoxo. Uma teoria séria, medida com cuidado, disse que o ótimo é vinte tokens por parâmetro. O modelo que vocês rodaram tem milhares. Quem está errado?

**Ninguém.** E a razão é que os dois otimizam funções diferentes.

Chinchilla otimiza o **custo de treinar**. Uma vez. Quem serve o modelo otimiza a **inferência** — e cada parâmetro extra custa memória e latência em *toda* requisição, para sempre.

Então: treinar um modelo pequeno muito além de vinte para um é caro no treino e barato para sempre. E é exatamente por isso que existe um modelo de um bilhão bom o suficiente para rodar na máquina de vocês.

> 🗣️ "Vinte para um e milhares para um estão os dois certos. São ótimos de funções diferentes — e a diferença é quem paga a conta."

**[Projeto o balão de prompt do fechamento]**

Última coisa, e é o gancho de amanhã. Toda essa fábrica — o orçamento, as placas, a curadoria, o paralelismo — entrega uma máquina que **continua texto**.

Prompt: "qual a capital da França?". Uma continuação perfeitamente coerente é: "qual a capital da Alemanha? qual a capital da Itália?".

Não é defeito. É o objetivo funcionando exatamente como especificado.

> 🗣️ "Toda essa fábrica entrega uma máquina que continua texto. Amanhã a gente descobre que virar assistente custa uma fração de um por cento disso."

**[Projeto as leituras e fico 20 s em silêncio]**

Kaplan, Chinchilla, FlashAttention — os três arXiv na tela.

**[Projeto o índice do apêndice por 20 s]**

Seis itens. E eu nomeio um: o **A.1** é a derivação do `C ≈ 6ND` que eu prometi na Aula 10 quando alguém perguntou de onde vinha o seis. Está lá inteira, e é conta que a prova cobra.

> **Nota:** Bastidor: o paradoxo **só funciona** se a turma ficou incomodada desde o slide 8 — não antecipar em nenhuma hipótese. Os 20 s de silêncio nas leituras são para fotografar. Nomear o A.1 em voz alta fecha a promessa da Aula 10 e é o hábito que mantém o apêndice vivo. Lembrar: quem não abriu o Colab com GPU tem uma aula de prazo antes do Lab 4.

---

## Parte 2 — Demonstração guiada

Oito minutos, `codigo/demo-scaling-laws.py`, Python puro, sem GPU e sem rede. Determinística.

**1.** **[Rodo o script e paro na tabela de alocação]** Aqui está a alocação ótima para orçamentos de dez à décima nona até dez à vigésima quinta potência de FLOPs. Três colunas: o compute, o `N` ótimo, o `D` ótimo. E a quarta coluna, que é a que interessa: `D` sobre `N`. **[aponto]** Vinte. Vinte. Vinte. Ao longo de seis ordens de grandeza de orçamento, a razão é estável — e é isso que faz dela uma regra útil.

**2.** **[Mostro o gráfico de perda × compute em log-log]** A lei de potência, e em log-log ela é uma reta. Isso é o que autoriza prever: dá para estimar a perda de um treino que ainda não aconteceu.

**3.** **[Mostro as curvas isoFLOP com os mínimos marcados]** E aqui está o U que eu desenhei no quadro. Cada curva é um orçamento fixo, variando o `N`. Olhem os mínimos marcados: eles não estão nas pontas, estão no meio. É a existência desse mínimo interior que responde o defeito um.

**4.** **[Mostro o contrafactual do GPT-3]** Este é o slide mais desconfortável da demo. Para o mesmo orçamento de compute que treinou o GPT-3 de cento e setenta e cinco bilhões de parâmetros com trezentos bilhões de tokens, a alocação ótima teria sido **cinquenta e um bilhões de parâmetros com um trilhão de tokens**. Mesmo dinheiro, modelo três vezes menor, perda menor. **[pausa]** Não é crítica retrospectiva fácil: ninguém sabia. É o que uma medição bem feita compra.

**5.** **[Mostro a conversão de horas de GPU em FLOPs]** E o último ato liga a teoria à fatura: pico, MFU, dias de placa, e o `C` que sai. Este é o par que vocês vão usar no exercício: seis vezes dez à vigésima FLOPs, dois vírgula dois bilhões de parâmetros.

> **Nota de contingência:** Bastidor: se o `matplotlib` não abrir janela, os PNGs da véspera cobrem os passos 2 e 3 integralmente. Sem Python na máquina, desenhar o U no quadro em 90 s — os mínimos são o que importa, não a suavidade. O passo 4 (contrafactual) é **insubstituível** e sobrevive a qualquer falha: são quatro números que cabem no quadro. Se o tempo apertar, cortar o passo 2. O script já tem guarda de encoding e detecção de backend, então não trava em terminal sem display.

---

## Parte 3 — Hands-on

Quatro minutos de dupla mais dois de correção, dentro do slide 15.

**1.** **[Projeto as quatro perguntas e formo as duplas]** Quatro minutos. As fórmulas estão no rodapé — o que eu quero é a decisão, não a memória.

*Bastidor — respostas e erros comuns:*

**Item 1 (cabe?).** A conta é `2,2e9 × 16 = 35,2e9` bytes, cerca de **32,8 GiB** de estados, contra `8 × 74,5 GiB` de memória agregada. **Cabe distribuído; não cabe numa placa só.** O erro dominante é contar só os pesos a dois bytes — dá quatro gigabytes e a conclusão errada de que cabe folgado. Quem errar assim errou de um jeito útil: mostra que a conta de dezesseis bytes não foi absorvida.

**Item 2 (o que estoura primeiro).** Memória, e a medição que confirma é ocupação da GPU contra memória alocada: `OOM` com utilização aritmética baixa é diagnóstico de memória, não de compute.

**Item 3 (qual paralelismo).** **Dados, com estados do otimizador particionados** — não tensor. O critério é: comece por dados, vá para tensor só quando uma camada isolada não couber. Um modelo de dois vírgula dois bilhões tem camadas que cabem folgadas. O erro nº 2 é responder "tensor" por soar mais sofisticado.

**Item 4 (filtrar agressivamente).** É o mais interessante e o que amarra os dois blocos. Filtrar ajuda: o orçamento é de quarenta e cinco bilhões de tokens e o corpus cru tem trezentos, então há folga de sobra para descartar — e quarenta por cento de duplicata significa que boa parte daquele volume supervisiona a mesma coisa repetidamente. Pelo slide 6: orçamento gasto em repetição não compra generalização. A resposta errada interessante é "filtrar reduz o corpus e o corpus é o supervisor" — está certa na premissa e erra na aritmética, porque ignora que sobra corpus.

*Como recolher:* dois minutos, e eu começo pelo item 4, não pelo primeiro. Se só houver tempo para um, é esse — porque é o que mostra que a decisão de dados e a decisão de orçamento são a mesma decisão.

*Extensão para quem terminar antes (opcional):* refazer à mão a aritmética que a demo fez — de pico e MFU até `C`, e de `C` até o par `(N, D)`. Gabarito completo em **A.2**.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência. E nesta aula ela tem uma particularidade: a Aula 10 mandou a turma para cá com uma pergunta na mão, então o item 1 provavelmente vai ser puxado — e deve ser atendido.

> **Nota:** Bastidor: esta aula tem folga no Bloco 1 e pouca no Bloco 2. Ordem de sacrifício: primeiro o slide 12 (precisão mista) comprimido a 2 min; depois o passo 2 da demo; depois o slide 14 reduzido ao argumento de I/O sem o diagrama. **Nunca** o slide 11 (defeito 2) nem o exercício — o 11 é o que fecha o defeito mais concreto da aula, e o exercício é o único momento em que eles decidem.

**Item 1 — "De onde vem esse seis?" (A.1, ~5 min).**
A pergunta que a Aula 10 gerou, e eu prometi responder hoje. Vale os cinco minutos. Escrevo no quadro: no forward, cada parâmetro participa de uma multiplicação e uma soma por token — **dois** FLOPs. No backward, preciso do gradiente em relação à entrada e em relação ao peso, o que dá o dobro — **quatro**. Dois mais quatro, seis. E aí vem a pergunta boa, que é sobre o otimizador: a atualização custa por **parâmetro e por passo**, não por token, então ela não escala com `D` e sai da conta. Escrevo essa razão e paro. **Versão de 30 segundos:** "dois no forward, quatro no backward, e a atualização do otimizador não entra porque paga por passo e não por token. A conta inteira, com a atualização contabilizada e descartada com número, está em A.1."

**Item 2 — "Como se chega em vinte tokens por parâmetro?" (A.2, ~6 min).**
A mais caro da lista. Eu monto a otimização: minimizar a perda sujeito a `C = 6ND` fixo. Substituo o `D` por `C/(6N)`, derivo em relação a `N`, igualo a zero. Sai `N ∝ √C`, e com as constantes do ajuste, `N ≈ √(C/120)` e `D ≈ 20N`. Escrevo as premissas junto, porque elas são o ponto: a forma da superfície de perda é ajustada empiricamente, e o vinte é consequência **daquelas** constantes, não de matemática pura. **Versão de 30 segundos:** "minimiza a perda com o compute fixo, substituindo `D` por `C/6N` — sai `N` proporcional à raiz de `C`, e a razão vinte cai das constantes do ajuste empírico. Está em A.2, com as três ressalvas sobre o 20:1."

**Item 3 — "De onde vêm os dezesseis bytes?" (A.4, ~3 min).**
Barata e produz um número que impressiona. Quatro bytes de peso em fp32, quatro de gradiente, e oito dos dois momentos do Adam — quatro cada. Quatro mais quatro mais oito, dezesseis. Instancio com um bilhão de parâmetros: dezesseis gigabytes antes de processar um token. E acrescento a parte que a conta famosa **não** cobre: as ativações, que escalam com lote vezes contexto. **Versão de 30 segundos:** "peso, gradiente e os dois momentos do Adam, quatro bytes cada, dão dezesseis por parâmetro — e as ativações são por cima disso. A decomposição está em A.4."

**Item 4 — "Se FlashAttention não muda a complexidade, como ela acelera?" (A.6, ~4 min).**
A melhor pergunta técnica que pode aparecer nesta aula. Escrevo os dois esquemas e conto **acessos à memória lenta**, não operações: a atenção padrão escreve e lê a matriz `n × n` várias vezes; a FlashAttention processa em blocos e nunca a materializa. Mesma complexidade em FLOPs, tráfego muito menor — e o regime é limitado por tráfego. **Versão de 30 segundos:** "porque o gargalo não é a conta, é o tráfego entre a memória lenta e a rápida — e ela nunca materializa a matriz de escores. A contagem de acessos está em A.6, e o A.3 da Aula 29 fecha o argumento com a intensidade aritmética."

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 16 da Parte 1 — os três defeitos riscados com a causa, a resolução do paradoxo do `D/N`, a constatação de que a fábrica entrega um completador de texto, as três leituras com 20 s de silêncio para fotografar, e os 20 s finais de índice do apêndice nomeando o A.1.

> 🗣️ "Toda essa fábrica entrega uma máquina que continua texto. Amanhã a gente descobre que virar assistente custa uma fração de um por cento disso."

---

*Roteiro do Instrutor · Aula 12 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
