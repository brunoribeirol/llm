---
aula: 8
titulo: "Famílias de modelos e atenção eficiente"
tipo: teorica
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 8 de 30 (V2)

## Como usar este roteiro

A prosa deste documento é **fala em primeira pessoa**: é o que eu digo em sala, na ordem em que digo. Não
é resumo do conteúdo — é o texto falado. Posso ler quase literalmente ou usar como trilho e improvisar em
cima.

As linhas marcadas com 🗣️ são as **frases-âncora**: as que eu cravo, quase palavra por palavra, porque
mudam o ritmo ou fecham um ponto. Cada slide tem uma.

As notas marcadas com **Bastidor** são operacionais e **não são faladas em voz alta** — são lembretes do
que abrir na tela, onde a turma costuma travar, o que responder se alguém perguntar algo específico. Nesta
aula em particular, elas guardam os números do KV cache com todos os fatores, porque a instanciação
acontece ao vivo na demo e não pode sair errada na frente da turma.

> **O que muda nesta versão.** Eu abro por três chamados de plantão, nenhum deles com erro no log: o
> serviço que atende dez conversas e morre em quarenta, o time que trocou um encoder por um LLM porque o
> LLM é mais novo, e a janela de 128 k anunciada cujo contexto útil ninguém sabe dizer. Os três se
> resolvem com duas contas, e eu digo isso desde o começo. **A multiplicação fator a fator do KV cache
> saiu do quadro**: o slide traz o resultado com a unidade, a instanciação com números reais acontece na
> demo — lendo um `config.json` — e a contagem completa, com a justificativa de cada fator e a leitura de
> banda de memória, está em A.2. Se a turma pedir a conta, a **Parte 4** tem a condução pronta com o custo
> em minutos e o que sacrificar em troca.
>
> **Uma nota de escopo que vale saber e não vale falar:** esta aula **estabelece** a fórmula do cache e o
> fator de MQA/GQA; a Aula 10 **usa** a fórmula no regime de serviço, com o ponto em que o cache empata com
> os pesos. Se alguém puxar concorrência e paginação hoje, o lugar é a Aula 10.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · Abertura: três chamados, nenhum bug · 00:00–00:10

Boa noite, pessoal. Na aula passada a gente fechou o bloco Transformer moderno, e vale recapitular em uma
linha o que exatamente ficou fechado: posição entrando por RoPE, girando query e key para que a distância
relativa apareça dentro do score; normalização por RMSNorm em pré-norm, com a residual passando limpa de
ponta a ponta; e feed-forward com SwiGLU. Esse bloco é o que os modelos abertos de hoje empilham, e vocês
sabem desenhar ele.

Hoje eu não vou construir bloco nenhum. Hoje eu vou trazer três chamados que chegaram na mesma semana, e
eu quero que vocês repararem numa coisa que os três têm em comum: **nenhum deles tem exceção no log**.

Chamado um. O serviço de conversa atende dez usuários simultâneos com folga. Em quarenta, a GPU estoura.
Mesmo modelo, mesmos pesos, mesma máquina, e ninguém fez deploy de nada entre uma coisa e a outra.

Chamado dois. Um time tinha um classificador pequeno rodando desde 2019 e trocou por um LLM, com o
argumento de que o LLM é de 2024. A qualidade subiu um pouco. A fatura de inferência multiplicou, e a
latência saiu do orçamento do produto.

Chamado três. O produto anunciou janela de cento e vinte e oito mil tokens. Em produção, com usuários de
verdade, o contexto útil que sobra é uma fração disso — e ninguém na equipe consegue dizer qual fração.

Nenhum dos três é bug. Os três se resolvem com duas contas que eu vou dar hoje: **quem pode ler quem**, e
**quanto o rascunho custa**. A primeira metade da aula responde o chamado dois. A segunda metade responde
o um e o três — e o chamado um fecha com um número.

> 🗣️ "Nenhum dos três tem erro no log. E os três se resolvem com duas contas: quem pode ler quem, e quanto o rascunho custa."

> **Nota:** Bastidor: deixar o diagrama do bloco da Aula 7 projetado por trinta segundos antes de trocar de
> slide — a continuidade visual faz o argumento sozinha. Se a turma vier de uma Aula 7 corrida, gastar um
> minuto extra confirmando que pré-norm e residual estão claros; sem isso o slide 2 não funciona. Anunciar
> em voz alta qual bloco fecha qual chamado: a turma que sabe onde a resposta vem aguenta melhor os
> quarenta e cinco minutos de família.

### Slide 2 · Por que a escolha por nome sai errada: a máscara é a arquitetura · 00:10–00:16

Deixa eu começar pelo chamado dois, porque o erro dele é de raciocínio, não de engenharia.

O time comparou **datas**. E data não é uma propriedade que decide arquitetura. Deixa eu mostrar o que
decide.

Eu vou pegar exatamente o bloco da aula passada e trocar **uma** coisa: quem pode ler quem. Três opções.

Primeira: máscara nenhuma. Toda posição consulta todas as outras, passado e futuro. Isso é bidirecional, e
é o que a gente chama de encoder. Segunda: máscara causal, aquela matriz triangular que a gente montou na
Aula 6 — cada posição só consulta o próprio passado. Isso é o decoder. Terceira: as duas juntas, em duas
pilhas. Uma pilha lê a entrada inteira sem máscara, outra pilha gera com máscara causal e consulta a
primeira por cross-attention.

Agora o ponto que eu quero que vocês levem deste slide, porque ele é o eixo da aula. A máscara não é um
detalhe de implementação: ela **determina o objetivo de treino possível**. Se toda posição vê o futuro,
não dá para treinar prevendo o próximo token — a resposta está na entrada. O modelo aprende a copiar, a
perda vai a zero, e nada de linguagem foi aprendido. Então o objetivo tem que mudar junto. Máscara e
função de perda são um pacote, não duas escolhas independentes.

E é por isso que o chamado dois errou. A pergunta certa não era "qual é mais novo". Era: essa tarefa
precisa gerar texto, ou precisa devolver um rótulo? A resposta dessa pergunta escolhe a máscara, e a
máscara escolhe a família.

> 🗣️ "Trocar a máscara troca o que o modelo pode aprender — e aí o objetivo de treino não tem escolha."

> **Nota:** Bastidor: desenhar as três matrizes de máscara no quadro, lado a lado, cinco por cinco,
> marcando as células permitidas. Leva noventa segundos e é a imagem que a turma vai lembrar na prova — é
> o único momento da aula em que ir ao quadro compra algo. Se alguém perguntar por prefix-LM ou máscaras
> híbridas, responder que existem, que são variações da mesma ideia e que **geram**, porque têm fatoração,
> sem abrir o fio: está em A.1 nos casos-limite.

### Slide 3 · BERT: atenção bidirecional e a lacuna a preencher · 00:16–00:25

Vou começar pela família bidirecional, que é onde a história moderna começa de verdade em 2018, com o
BERT.

O problema é o que eu acabei de dizer: com atenção bidirecional, prever o próximo token é trapaça. A
solução do BERT é o **masked language modeling**: mascarar cerca de quinze por cento dos tokens da
sequência e treinar o modelo para prever cada um deles usando o contexto dos dois lados. A perda está no
slide, e eu vou ler em vez de derivar: menos a soma, sobre as posições mascaradas, do log da probabilidade
do token correto dado o resto da sequência.

E aqui a gente fecha um laço que está aberto desde a Aula 3. Vocês lembram do problema do "banco"?
Embedding estático dava um vetor só para a palavra, e eu deixei aquele sintoma **aberto de propósito**,
dizendo que fechava na Aula 6. Na Aula 6 a gente viu o mecanismo — a atenção mistura o vetor de "banco"
com os vetores dos vizinhos, e a saída depende do contexto. O que o BERT fez foi montar o **objetivo de
treino** que força esse mecanismo a aprender exatamente isso, dos dois lados, em bilhões de frases. E na
demo, daqui a quinze minutos, vocês vão ver as duas frases do banco produzindo distribuições diferentes,
na tela.

Tem um detalhe honesto que vale contar, porque parece gambiarra e é engenharia. Existe uma discrepância
entre treino e uso: no treino o modelo vê o token `[MASK]`, e em uso ninguém manda `[MASK]` para ele. O
BERT original ameniza isso substituindo só oitenta por cento das posições escolhidas pelo `[MASK]`, dez
por cento por um token aleatório e dez por cento por nada — deixando a palavra original no lugar e ainda
pedindo a predição. Esses últimos dez por cento são o mais engenhoso dos três, e a razão está em A.1.

Só que reparem no verbo que eu usei: **ameniza**. E dá para remover. Em dois mil e vinte, o ELECTRA trocou a tarefa: em vez de "adivinhe a palavra que está debaixo da máscara", ele pergunta, para cada palavra da frase, "esta aqui é a original ou foi trocada?". Um modelo pequeno preenche as lacunas com palavras plausíveis, e o modelo que interessa recebe a frase já preenchida — **sem nenhum `[MASK]`**. A discrepância some, porque ela não existe mais. E tem um segundo ganho, que eu vou cobrar de volta no slide sete: a pergunta é feita para **todas** as posições, não para quinze por cento delas.

Guardem isso, porque no slide sete eu vou dizer que o decoder aprende com mais densidade de sinal que o encoder, e o ELECTRA é a prova de que essa densidade não vinha da máscara causal — vinha do objetivo. Dá para ter as duas coisas. Está em A.1, inclusive a parte contraintuitiva: o gerador do ELECTRA é pequeno **de propósito**, porque um gerador bom demais deixa a tarefa impossível.

E o que essa família **não** faz: gerar. Aqui eu quero ser mais preciso do que o normal, porque a resposta
fácil está errada. A resposta fácil é "ele não foi treinado para isso". A resposta certa é mais forte: o
MLM **não define uma distribuição conjunta sobre sequências**. A perda causal, que eu vou escrever no
slide sete, é exatamente a log-verossimilhança da sequência inteira, pela regra da cadeia — e gerar é
ler essa fatoração da esquerda para a direita. O MLM não tem fatoração nenhuma: ele aprende um conjunto de
condicionais que não se multiplicam para dar a probabilidade do texto. Não é dificuldade de engenharia; é
ausência do objeto de que a geração precisaria. As três razões independentes estão em A.1.

> 🗣️ "Se toda posição vê todas, prever o próximo token é copiar a resposta. O objetivo tem que ser outro: a lacuna."

> **Nota:** Bastidor: escrever a perda do MLM no quadro ao lado da perda do LM causal, mesmo que a causal só
> apareça formalmente no slide 7 — a comparação visual entre "soma sobre M" e "soma sobre todas as posições"
> antecipa o argumento do sinal denso e economiza tempo depois. **Não derivar a degeneração** do
> bidirecional-com-próximo-token: são três linhas tentadoras e estão em A.1, junto com o argumento de
> pseudo-verossimilhança, que é a parte que a V1 não tinha. Se a turma perguntar sobre RoBERTa ou sobre o
> que veio depois do BERT, responder curto: as receitas mudaram, o objetivo MLM continua o mesmo.

### Slide 4 · `[CLS]`, fine-tuning e cabeças de tarefa · 00:25–00:32

Uma pergunta prática: o BERT devolve um vetor por token. Se eu quero **um** rótulo para a frase inteira, de
onde eu tiro?

A resposta do BERT é o token `[CLS]`, acrescentado na posição zero da sequência. O vetor de saída daquela
posição é usado como resumo. E eu quero desmontar a mágica disso na frente de vocês, porque a turma sempre
acha que tem algo especial no `[CLS]`. Não tem. Ele funciona como resumo porque no pré-treino ele foi
obrigado a resolver uma tarefa de nível de sentença, e o gradiente empurrou aquela posição a agregar
informação da sequência inteira. É uma posição treinada para isso, não uma posição privilegiada por
natureza.

E daí vem a parte que interessa para produção: o **fine-tuning**. O corpo pré-treinado é caro e é um só.
Sobre ele, eu troco só a cabeça. Cabeça linear sobre o `[CLS]`: classificação de sequência. Cabeça linear
por posição: rotulagem de tokens, reconhecimento de entidade. Cabeça sobre um par de sentenças:
similaridade, e aí a gente chega no reranking, que volta com nome e métrica próprios na Aula 19.

Agora eu volto no chamado dois, porque é aqui que ele fecha. Por que alguém ainda usaria BERT em 2026? Por
custo, e é aritmética. Um encoder pequeno faz **uma** passada pela sequência e devolve um rótulo ou um
vetor. Um decoder-only tem que **gerar tokens** para dizer a mesma coisa, e cada token gerado é uma passada
pela pilha inteira. Uma passada contra k passadas. Em dez milhões de documentos por dia, isso é a diferença
entre uma máquina e um cluster.

O time do chamado dois não comparou uma passada com k passadas. Comparou 2019 com 2024.

> 🗣️ "O corpo pré-treinado é caro e é um só. A cabeça é barata e troca por tarefa."

> **Nota:** Bastidor: aqui costuma vir "então o vetor do `[CLS]` é o embedding da frase?". A resposta honesta
> é não — modelos de embedding de produção treinam a agregação explicitamente para similaridade, e é por
> isso que existe uma família de modelos só para isso, que aparece na demo daqui a pouco. Não abrir o fio de
> pooling: só sinalizar Aula 19. Amarrar explicitamente ao chamado dois em voz alta — é o fechamento do
> primeiro dos três, e a turma precisa sentir que a aula está pagando o que prometeu.

### Slide 5 · [Demo] BERT hoje, e os dois campos que abrem a segunda metade · 00:32–00:44

Chega de slide. Deixa eu mostrar três coisas funcionando, no navegador, e terminar com dois números lidos
de um arquivo de configuração — que são os números que abrem a segunda metade da aula.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> 🗣️ "Mesma palavra, dois contextos, duas distribuições. Isso é a resposta ao 'banco' que a Aula 3 deixou aberto."

> **Nota:** Bastidor: quatro abas do Hugging Face Hub abertas antes da aula começar e as duas frases do
> "banco" num arquivo de texto local para colar sem digitar. Testar o par de frases na véspera e ajustar se
> a separação de sentidos não aparecer. **O ato 4 é insubstituível** — é ele que produz o número que o
> resto da aula usa como evidência — e ele não depende de rede se os quatro campos do `config.json`
> estiverem anotados da véspera. Passos detalhados na Parte 2; capturas de tela da véspera como plano B.

### Slide 6 · Encoder-decoder: quando entrada e saída são objetos diferentes · 00:44–00:49

Segunda família, e vou ser rápido. Tem um tipo de tarefa em que a entrada está inteira e disponível de uma
vez, e a saída é uma sequência **nova**, de tamanho diferente, em outro idioma ou em outro nível de
detalhe. Tradução e sumarização são os dois casos canônicos.

Para esse tipo de tarefa, a montagem natural é duas pilhas. Um encoder que lê a entrada bidirecionalmente,
sem máscara, porque a entrada está toda lá. E um decoder que gera com máscara causal, porque a saída ainda
não existe — e que consulta o encoder por **cross-attention**.

E agora deixa eu cravar uma coisa que eu prometi na Aula 5. A cross-attention é o mecanismo de Bahdanau,
sem uma linha de diferença. As queries vêm do decoder — "o que eu preciso agora, nesta palavra que estou
escrevendo" — e as keys e values vêm do encoder — "o que a frase de origem oferece". Aquele mecanismo de
2014 que a gente estudou como solução para o gargalo do vetor de contexto fixo não foi substituído: ele foi
absorvido e virou um dos três tipos de atenção do Transformer. Foi aqui que ele sobreviveu.

O custo dessa família é honesto: duas pilhas, dois conjuntos de hiperparâmetros, e um objetivo de
pré-treino que não é qualquer texto cru — precisa de uma tarefa de reconstrução ou de corrupção de trechos
montada de propósito. E o argumento que enfraqueceu a família é que tradução também dá para fazer com uma
pilha só: coloca o original e a tradução na mesma sequência e prevê a continuação. Se dá para fazer com uma
pilha, a segunda pilha tem que se justificar.

> 🗣️ "A cross-attention é o Bahdanau da Aula 5, vivo e sem mudar uma linha. Foi aqui que ele sobreviveu."

> **Nota:** Bastidor: se o tempo estiver curto, este é o slide para comprimir — três minutos, mantendo só a
> frase-âncora e o custo das duas pilhas. O que não pode cair é a conexão com Bahdanau, porque é o pagamento
> da promessa feita na Aula 5. T5 e BART como exemplos canônicos, sem detalhar os objetivos de cada um.

### Slide 7 · Decoder-only: por que prever o próximo token venceu · 00:49–00:55

Terceira família, e a que ocupa as outras vinte e duas aulas desta disciplina. Máscara causal, uma pilha,
um objetivo: prever o próximo token, em toda posição.

Eu quero dar cinco argumentos, e eu quero que vocês vejam que nenhum deles é "essa arquitetura é mais
inteligente".

Primeiro, **rótulo grátis**. O rótulo do token `t` é o próprio token `t`. Todo texto cru do mundo, sem
anotação humana, sem par alinhado, vira dado de treino supervisionado. Isso contrasta com tradução, que
precisa de pares alinhados por gente.

Segundo, e esse é o mais bonito: **sinal denso**. O MLM treina em quinze por cento das posições de cada
sequência. O LM causal treina em cem por cento delas. E eu quero dar o número, porque "mais denso" é
adjetivo: a razão é um sobre zero vírgula quinze, ou seja, cerca de **seis vezes e sete décimos** mais
predições supervisionadas por token de corpus lido. Multiplicado por trilhões de tokens, isso deixa de ser
detalhe.

Terceiro, **simplicidade operacional**: uma pilha, um objetivo, uma máscara. Menos peças para escalar, e
escalar é o assunto do Módulo 2. Quarto, **prompting unifica as tarefas** — é literalmente a tese que eu
abri na Aula 1: classificar é gerar a palavra do rótulo, extrair é gerar JSON, sem trocar de cabeça e sem
trocar de modelo. Quinto, **geração é nativa**, não é um enxerto em cima de um modelo que não foi feito
para isso.

E tem uma sexta coisa, que não é argumento de vitória e é a razão formal da diferença: essa perda que está
no slide **é** a log-verossimilhança exata da sequência, pela regra da cadeia da probabilidade. O MLM não
tem essa propriedade. É por isso que um gera e o outro não — e não porque um é mais moderno.

O alerta, que é a parte que separa quem entendeu de quem decorou: "venceu" quer dizer venceu **como
plataforma geral**. Não quer dizer melhor em tudo. Por rótulo entregue e por milissegundo de latência, um
encoder pequeno destilado continua ganhando, e é o chamado dois de novo.

> 🗣️ "O MLM treina em quinze por cento das posições. O LM causal treina em cem por cento. Isso, multiplicado por trilhões de tokens, é a diferença."

> **Nota:** Bastidor: este é o slide de maior valor por minuto da aula — os cinco argumentos são resposta
> direta de prova. Numerar em voz alta e deixar o slide na tela até o intervalo. A contagem `6,7×` com as
> duas leituras (por época e por alvo), e o argumento de que o sinal do MLM é **mais rico por alvo** ainda
> que menos denso, estão em A.1 — e essa nuance é o que separa uma resposta boa de uma resposta decorada.
> Depois deste slide vai o intervalo de 10 min; avisar o horário de volta em voz alta.

### Slide 8 · O preço da janela: o KV cache em números · 01:05–01:14

Voltando. A primeira metade foi sobre escolher a família, e ela fechou o chamado dois. A segunda metade
fecha o chamado um, e ela começa com uma conta que ninguém faz até a primeira vez que serve um modelo em
produção e a GPU estoura.

Vamos lembrar da geração autorregressiva da Aula 6. Para produzir o token `n+1`, o modelo precisa das keys
e values de todas as `n` posições anteriores. E essas keys e values **não mudaram** — a máscara é causal, o
passado não vê o futuro, então o que foi calculado continua valendo. Recalcular tudo a cada token é
desperdício puro. Guardar é o que se chama de KV cache, e é troca de computação por memória.

A fórmula está no slide, e eu vou lê-la: o cache por token é dois — porque são K e V — vezes o número de
camadas, vezes o número de cabeças de key/value, vezes a dimensão de cada cabeça, vezes os bytes por valor.

E aqui está o número, num decoder hipotético — e eu quero ser explícito de que é hipotético: trinta e duas
camadas, trinta e duas cabeças, dimensão cento e vinte e oito por cabeça, meia precisão. **Meio mebibyte
por token.** Uma conversa de oito mil tokens custa quatro gibibytes de cache. E aqui está a parte que dói:
quatro gibibytes **por conversa**.

Agora o chamado um, com aritmética. Dez conversas simultâneas: quarenta gibibytes. Quarenta conversas:
cento e sessenta. Os pesos de um modelo de sete bilhões em meia precisão são catorze gibibytes, e são
**constantes**. Numa GPU de oitenta gibibytes, descontando os pesos e a folga de ativações, sobram da ordem
de sessenta para cache. Quarenta cabe com folga. Cento e sessenta não cabe, por um fator de quase três.

Entre dez e quarenta **não mudou nada no modelo**. Mudou o que ele tem que guardar, e o crescimento é
linear na concorrência. É por isso que esse sintoma aparece de repente: o cache não degrada devagar, ele
estoura.

Peso é constante. Cache é linear no contexto **e** no número de conversas simultâneas. O que estoura a GPU
em serviço não é o peso do modelo — é o rascunho.

> 🗣️ "Meio mebibyte por token. Oito mil tokens dão quatro gibibytes — por conversa. Dez conversas caberiam; quarenta não."

> **Nota:** Bastidor: **não fazer a multiplicação dos seis fatores no quadro.** Na V1 isso consumia cinco
> minutos e travava a sala com aritmética de cabeça. Aqui eu leio a fórmula e dou o resultado com a unidade;
> a contagem fator a fator, com a razão de existir de cada fator e a leitura de banda de memória, está em
> A.2, mais detalhada do que eu fazia no quadro. A instanciação com números **reais** já aconteceu na demo,
> lendo o `config.json` — e ela é mais convincente que a do modelo hipotético. Deixar `0,5 MiB por token`
> circulado no quadro: os slides 10 e 13 dependem dessa âncora. Se alguém apontar que MiB não é MB, dar o
> ponto e seguir; o arredondamento é deliberado. Se alguém puxar paginação ou o ponto em que o cache empata
> com os pesos, a resposta é: Aula 10.

### Slide 9 · Longformer: janela deslizante mais atenção global · 01:14–01:22

Antes de cortar o cache, deixa eu atacar o outro lado da conta, que é o custo da própria atenção.

Atenção plena é quadrática no comprimento, e isso a gente já sabe desde a Aula 6. Com trinta e dois mil
tokens de contexto, são mais de um bilhão de pares de posições, por cabeça e por camada. A ideia do
Longformer é simples e é a que mais parece trapaça sem ser: cada posição não precisa consultar todas — só
uma janela de largura `w` em torno de si. O custo cai de `n` ao quadrado para `n` vezes `w`. Com trinta e
dois mil tokens e janela de quinhentos e doze, são dezesseis milhões e oitocentos mil pares em vez de um
bilhão. A razão é `n` sobre `w`: sessenta e quatro vezes menos.

E a pergunta óbvia é: e a dependência longa, que foi o motivo de a atenção existir? Dois caminhos.

O primeiro é **profundidade**: a informação caminha metade da janela para cada lado a cada camada, então
com doze camadas e janela de quinhentos e doze o alcance é da ordem de três mil posições para cada lado.

E aqui eu vou ser mais honesto do que a versão anterior desta aula era, porque esse número merece ser
comparado. Três mil de trinta e dois mil é **nove por cento da sequência**. Para a profundidade sozinha
ligar a primeira posição à última, seriam necessárias **cento e vinte e oito camadas** — a conta é duas
vezes `n` sobre `w`, e ela está em A.3. Ou seja: a profundidade recupera alcance *médio*. Ela não recupera
alcance de ponta a ponta.

Então o segundo caminho não é complemento opcional, é essencial: **atenção global** em um punhado de tokens
escolhidos. Alguns tokens leem tudo e são lidos por todos — o token de classificação, os tokens da
pergunta, os títulos de seção. Com oito tokens globais, o custo sobe três por cento. E o que esses três por
cento compram é o seguinte: qualquer par de posições passa a ter um caminho de **duas** camadas, indo até um
token global e voltando. O diâmetro da comunicação vira dois, independentemente do comprimento.

E aqui está o preço honesto dessa família: escolher **onde** vai a atenção global é decisão de projeto, por
tarefa. Se eu escolher errado, eu perco exatamente a dependência que importava, e o modelo não me avisa.

> 🗣️ "A profundidade compra três mil posições de trinta e duas mil. O alcance de ponta a ponta quem compra são os poucos tokens globais — se eu escolher certo."

> **Nota:** Bastidor: desenhar a matriz de atenção `n × n` no quadro e hachurar só a faixa diagonal, depois
> pintar uma linha e uma coluna inteiras para os tokens globais. Essa figura é o Longformer inteiro em vinte
> segundos. **A conta das 128 camadas é a melhor pergunta que pode aparecer no Bloco 2** — se ela vier, dar
> o ponto e remeter a A.3, que tem a conta e o argumento do diâmetro. Não entrar em implementação de kernel
> esparso nem em janela dilatada; a dilatada está nos casos-limite de A.3.

### Slide 10 · MQA e GQA: cortar o KV cache pela raiz · 01:22–01:31

Agora o corte no cache, e ele é elegante porque sai direto da fórmula.

Olha a fórmula do slide 8 de novo. O cache é proporcional ao número de cabeças de **key e value**. E aqui
vem a pergunta que alguém em 2019 fez: as cabeças de query precisam ser muitas, porque cada uma faz uma
pergunta diferente. Mas as chaves e os valores precisam ser um conjunto por cabeça?

A resposta do MQA é: não. Mantém as trinta e duas cabeças de query e compartilha **uma única** cabeça de
key/value entre todas. O cache é dividido por trinta e dois. Na conta do slide 8, quatro gibibytes viram
cento e vinte e oito mebibytes.

O GQA é o meio-termo, e é o que os modelos abertos recentes usam. Em vez de uma cabeça de K/V, `G` grupos:
as trinta e duas queries se dividem em, digamos, oito grupos, cada grupo com sua própria cabeça de
key/value. O fator de redução é a razão `n_heads` sobre `n_kv_heads` — trinta e dois sobre oito, quatro. Os
quatro gibibytes viram um gibibyte.

E esse fator é **exato**, não aproximado, porque todos os outros fatores da fórmula se cancelam quando eu
comparo duas configurações que só diferem no número de cabeças de K/V. A derivação de duas linhas está em
A.2.

Agora deixa eu ser explícito sobre o que **não** muda, porque é aqui que a turma escorrega. As queries
continuam trinta e duas — o número de padrões de relação por camada é o mesmo. A fórmula da atenção
continua sendo softmax de Q K transposto sobre raiz de d_k, vezes V, exatamente a mesma da Aula 6. O número
de camadas e a dimensão do modelo continuam iguais.

E uma coisa que muda e que eu não dizia antes, porque vale a precisão: as **projeções** de K e V encolhem.
Em atenção multi-cabeça cheia as três projeções custam três vezes a dimensão ao quadrado; com GQA de oito
cabeças de K/V, as de K e V ficam quatro vezes menores. É uma redução real de parâmetros, da ordem de
cinquenta por cento nos parâmetros de projeção da atenção — e as implementações costumam compensar isso
alargando a rede feed-forward. Está em A.2, com os números.

O que se ganha, então: memória de cache **e** tráfego de memória para lê-lo. E esse segundo ganho é o que
faz a geração ficar mais rápida, porque gerar um token exige **ler o cache inteiro**: com quatro gibibytes
e banda de dois terabytes por segundo, são dois milissegundos por token só de leitura. Com GQA de oito,
meio milissegundo. O que se paga é qualidade: MQA corta mais e pode custar mais; GQA recupera quase tudo
com uma fração do cache, e é por isso que virou o padrão.

> 🗣️ "As perguntas continuam trinta e duas. O índice consultado passa a ser um só, ou oito. O fator de redução é exatamente a razão entre eles."

> **Nota:** Bastidor: a pergunta que sempre vem é "então GQA deixa o treino mais rápido?". A resposta
> completa é: acelera a **geração**, porque a geração é limitada por banda de memória e o cache encolheu;
> o treino quase não muda, porque o treino é limitado por aritmética. O número da banda está em A.2 e vale
> dizer em voz alta — dois milissegundos contra meio milissegundo encerra a discussão. Se alguém perguntar
> como se converte um modelo MHA já treinado para GQA, dizer que é exatamente o que o paper do GQA trata —
> média dos pares K/V de cada grupo mais um treino curto de recuperação — e mandar para a leitura.

### Slide 11 · Destilação: o aluno aprende a distribuição do professor · 01:31–01:37

Última técnica de hoje, e ela fecha o laço com a primeira metade da aula.

A pergunta é: como se fabrica um modelo pequeno que é bom? Uma resposta é treinar do zero em dados
rotulados, e aí o pequeno é pequeno mesmo. A outra é destilação: usar um modelo grande, já treinado, como
professor.

E o pulo do gato é o que se copia do professor. Não é o rótulo — é a **distribuição**. Quando eu passo um
exemplo pelo professor, ele não devolve só "a resposta é B": devolve uma distribuição sobre todas as
alternativas, e nessa distribuição está a informação de que C era defensável e D é absurdo.

A perda está no slide e é uma combinação: uma parte de entropia cruzada contra o rótulo verdadeiro, outra
parte de divergência entre a distribuição do aluno e a do professor, com um peso alfa entre as duas — e um
fator de temperatura ao quadrado multiplicando a segunda parte.

Deixa eu dar o número que mostra o que a temperatura faz, porque "achatar a distribuição" é vago. Numa
distribuição cujos logits são cinco, três, um e menos dois: com temperatura um, a última classe tem
probabilidade zero vírgula zero zero zero oito. Com temperatura quatro, ela tem zero vírgula zero oito. A
cauda ficou **cem vezes mais visível**, e o professor não mudou. Foi só a temperatura.

E duas coisas de A.4 que eu quero enunciar sem derivar. A primeira: a divergência está escrita na ordem
professor, aluno, e essa ordem importa — nessa ordem, a divergência pune muito o aluno por **não cobrir** a
cauda do professor. Se estivesse invertida, o aluno poderia concentrar tudo na classe vencedora e ignorar o
resto, que é exatamente o que o rótulo duro já faz. A assimetria é o mecanismo. A segunda: aquele fator de
temperatura ao quadrado existe para que os dois termos continuem com pesos comparáveis quando a temperatura
muda — e no limite de temperatura alta a destilação vira, literalmente, igualar os logits do aluno aos do
professor. A conta está em A.4.

E onde isso aterrissa nesta aula: os encoders pequenos que sustentam classificação e reranking em produção,
que eu defendi no slide 4, são em boa medida destilados. A família encoder-only continua viva **porque** dá
para comprimir — e isso fecha o chamado dois de vez. O tema volta com mais profundidade no Módulo 7.

> 🗣️ "O rótulo diz que a resposta é B. O professor diz que é B, que C era defensável e que D é absurdo — e é a segunda frase que ensina."

> **Nota:** Bastidor: se alguém disser "mas eu vi gente chamar de destilação treinar em textos gerados pelo
> GPT", dar o ponto: o uso corrente do termo cobre as duas coisas. A distinção que importa é técnica — a
> destilação clássica precisa dos **logits** do professor, e API fechada não dá logits; treinar em texto
> gerado é supervisão sintética e **não** transfere a cauda, transfere amostras dela. Essa é uma boa
> resposta de prova, está escrita em A.4, e vale dizer em voz alta.

### Slide 12 · O mapa das famílias, consolidado · 01:37–01:39

Deixa eu juntar as três famílias numa tabela só, porque é essa tabela que vocês vão querer na mão na Aula
17 e no projeto.

Três colunas que decidem tudo: a máscara, o objetivo de pré-treino, e o que a família faz bem.
Encoder-only: sem máscara, MLM, entrega rótulo, vetor ou escore de par. Encoder-decoder: bidirecional de um
lado, causal do outro, cross-attention no meio, objetivo de reconstrução, entrega uma sequência
transformada a partir de uma entrada completa. Decoder-only: máscara causal, LM causal em cem por cento das
posições, entrega geração e serve de interface única.

E eu botei uma quarta coluna de propósito: onde cada família volta nesta disciplina. Encoder-only volta na
Aula 19, como modelo de embedding e como cross-encoder de reranking. A cross-attention do encoder-decoder
já apareceu na Aula 5 e é o Bahdanau. E o decoder-only volta na próxima aula, na unha, e depois na Aula 10
com escala e inferência.

E repararam no que **não** tem nessa tabela? Data. Nenhuma coluna aqui é o ano do modelo.

> 🗣️ "Máscara, objetivo, e o que a família faz bem. Essas três colunas respondem a maioria das perguntas de arquitetura que vocês vão fazer — e nenhuma delas é a data do modelo."

> **Nota:** Bastidor: este slide fica na tela durante o exercício que vem a seguir — a turma vai consultar.
> Não avançar o deck no slide 13; deixar este projetado e ler os cenários em voz alta. Se faltar tempo,
> este slide é o resumo suficiente da aula inteira, e cortar a exposição dele custa pouco porque ele se
> sustenta lido.

### Slide 13 · [Exercício] Qual família, qual atenção, e que conta confirma · 01:39–01:50

Oito minutos com vocês trabalhando, em dupla, e três de correção comigo.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> 🗣️ "Cinco cenários. Família, atenção eficiente, e a conta que sustenta a escolha — e 'porque é mais novo' desconta."

> **Nota:** Bastidor: passos e correção na Parte 3. Cronometrar de verdade — 8 min de dupla, 3 de correção.
> O cenário 5 é o que amarra a aula e é onde os três minutos finais vão. A exigência da terceira coluna
> (a conta) é a mudança da V2 e é o que faz o exercício deixar de ser preferência com vocabulário técnico.

### Slide 14 · Fechamento: três chamados, duas contas · 01:50–02:00

Deixa eu fechar pelos três chamados com que eu abri.

Chamado um, o serviço que atende dez e morre em quarenta: **cache linear no contexto e na concorrência**. O
peso é constante, o cache não é, e a conta está no slide 8 e em A.2. Ninguém mexeu no modelo — mexeu na
carga.

Chamado dois, o time que trocou o encoder por um LLM porque o LLM é mais novo: **uma passada contra k
tokens gerados**. A escolha por data ignorou uma aritmética de custo, e o que decide a família é a máscara e
o objetivo de pré-treino.

Chamado três, os cento e vinte e oito mil tokens anunciados: **o cache disputa a mesma memória dos pesos**.
Quanto de janela é utilizável não é uma propriedade do modelo, é uma consequência de quantas conversas
simultâneas o serviço precisa atender — e a conta de dimensionamento é a Aula 10.

E as duas metades da aula, em duas linhas. Primeira: a arquitetura não é o bloco, é a máscara. E o
decoder-only venceu não por ser mais inteligente, mas por ter o objetivo mais barato — rótulo grátis, sinal
em cem por cento das posições, seis vírgula sete vezes mais predições por token lido — e por permitir que
prompting unifique as tarefas. Segunda: essa vitória tem uma fatura, e ela vem em memória. Contra isso, duas
alavancas: cortar pares de atenção com janela mais atenção global, e cortar o cache com MQA ou GQA, com
fator igual à razão entre o número de cabeças e o número de cabeças de key/value.

E na próxima aula essa família sai do slide. Aula 9, Laboratório 2: vocês vão implementar atenção causal na
mão, com a máscara triangular que eu desenhei no slide 2; multi-head, como a gente derivou na Aula 6; o
bloco completo, com residual, norm e feed-forward da Aula 7. Depois vão treinar um modelo de linguagem de
verdade num corpus pequeno, gerar texto e medir perplexidade — aquela mesma perplexidade que eu prometi na
Aula 1 que vocês mediriam com as próprias mãos.

As leituras da semana: o paper do BERT, na seção do objetivo de pré-treino; o do GQA, com o do MQA como
antecedente; e o do Longformer. A pergunta dirigida é: no GQA, o que exatamente é compartilhado entre as
cabeças, o que continua sendo por cabeça, e qual é o fator de redução do cache em função de `n_heads` e
`n_kv_heads`? E um item de dez minutos: abrir o `config.json` de dois modelos abertos no Hub e calcular o
cache por token de cada um com a fórmula de hoje.

> 🗣️ "Na próxima aula a família decoder-only sai do slide. Vocês vão escrever a máscara causal, o multi-head e o bloco — e treinar."

> **Nota:** Bastidor: projetar o checklist do Lab 2 no final — Colab com GPU habilitada e o notebook do lab
> aberto — e ficar em silêncio meia dúzia de segundos para a turma fotografar. Quem chega na Aula 9 sem GPU
> habilitada perde os primeiros quinze minutos do lab. Antes de encerrar, projetar o índice do apêndice por
> vinte segundos: são quatro itens, e o que mais volta é **A.2** — a Aula 10 parte dele, e ele é o candidato
> natural ao item de derivação da prova.

---

## Parte 2 — Demonstração guiada

Esta demo roda em doze minutos, no navegador, e termina no quadro. O objetivo é triplo: mostrar que a
representação do BERT é contextual de verdade — fechando o sintoma que a Aula 3 deixou aberto —, mostrar que
a família encoder-only entrega coisas que não são texto, e **ler numa configuração real os dois números de
que a segunda metade da aula depende**.

Na V2 o ato 4 deixa de ser complemento e passa a ser a **evidência** do slide 8 e do slide 10: os números
saem de um arquivo que o modelo publica, não de um slide meu.

Insumos preparados antes da aula: quatro abas do Hugging Face Hub já abertas, as duas frases do "banco" num
arquivo de texto local para colar sem digitar, **os quatro campos do `config.json` anotados na véspera** (para
o passo 7 rodar mesmo sem rede), e capturas de tela dos passos.

**1.** **[Abro a página de um BERT em português no Hub, com o widget de fill-mask visível]** Vou usar um
BERT treinado em português aqui. Isso é um modelo de 2020, encoder-only, e ele está no Hub com um widget que
roda inferência direto na página — não preciso de código nenhum para o que eu quero mostrar.

**2.** **[Colo `O banco do rio estava [MASK].` e submeto]** Primeira frase: "o banco do rio estava" e uma
lacuna. Olha as predições que ele devolveu. O modelo está preenchendo a lacuna com o que faz sentido depois
de um banco de rio.

**3.** **[Colo `O banco do centro estava [MASK].` e submeto, deixando a primeira resposta visível para
comparar]** Segunda frase, e eu troquei uma palavra só: "centro" em vez de "rio". Olha a diferença nas
predições. A palavra mascarada está na mesma posição, a estrutura é a mesma, e a distribuição mudou. Isso só
é possível porque o vetor de "banco" que chegou naquela camada final é **diferente** nas duas frases — a
atenção leu "rio" de um lado e "centro" do outro. E é a resposta ao sintoma que eu deixei aberto na Aula 3
de propósito, e que a Aula 6 explicou mecanicamente: embedding estático não separa os dois sentidos;
representação contextual separa.

**4.** **[Abro a página de um modelo de embedding, sentence-transformers, e mostro a saída]** Segundo ato.
Este é outro encoder, e olha o que ele devolve: não é texto, é um vetor de dimensão fixa. Este modelo existe
para transformar frase em ponto num espaço, e é sobre esse espaço que a busca semântica da Aula 18 vai
funcionar.

**5.** **[Abro a página de um cross-encoder de reranking e mostro a saída para um par consulta-documento]**
Terceiro. Este recebe um **par** — uma consulta e um documento — e devolve um número: quão relevante. Uma
passada, um escore. Nenhum token gerado. Este é o argumento de custo do slide 4 na tela: para dizer
"relevante, nota tal", um decoder-only teria que escrever uma frase.

**6.** **[Abro o `config.json` de um decoder-only aberto e recente no Hub e leio os quatro campos]** Agora eu
mudo de família e vou atrás de quatro números. Neste arquivo tem `num_hidden_layers`, tem
`num_attention_heads`, tem `num_key_value_heads` e tem `hidden_size`. Olha os quatro valores — e olha os dois
do meio em particular. Quando esses dois são diferentes, isso é GQA. E a razão entre eles é o fator pelo qual
o cache foi reduzido em relação a atenção multi-cabeça cheia. Vou anotar os quatro no quadro.

**7.** **[Vou para o quadro e aplico a fórmula do KV cache com os valores lidos na tela]** E aqui eu fecho no
quadro, com números que não são meus: dois, vezes camadas, vezes cabeças de key/value, vezes a dimensão por
cabeça — que é `hidden_size` dividido por `num_attention_heads` —, vezes dois bytes. Isso dá o cache por
token deste modelo. Depois eu refaço a mesma conta trocando `num_key_value_heads` por `num_attention_heads`,
que é o que seria sem GQA. A razão entre as duas contas é exatamente a razão entre os dois números que estão
na tela. Não é um número que eu trouxe no slide: é aritmética em cima do que o modelo declara sobre si.

> **Nota de contingência:** Bastidor: se o Hub estiver fora do ar ou o widget de inferência não carregar,
> usar as capturas de tela da véspera — os cinco primeiros passos já estão fotografados. **Os passos 6 e 7
> são os pedagogicamente essenciais e o 7 não depende de rede:** com os quatro campos anotados na véspera, a
> conta se faz no quadro do mesmo jeito. Se as predições do fill-mask nos passos 2 e 3 saírem parecidas, não
> forçar a narrativa: dizer à turma que o par não separou, comentar que é um modelo pequeno, e usar o segundo
> par de frases testado na véspera. Não anotar aqui quais palavras o modelo prevê — isso se lê na tela, e o
> instrutor confirma na véspera. Se o tempo apertar, o ato 4 (embeddings) é o único que vira menção falada.

---

## Parte 3 — Hands-on

Oito minutos em dupla, três de correção, com os cinco cenários projetados e o mapa das famílias do slide 12
ainda na tela. O objetivo não é acertar a família — é obrigar a justificativa a virar **conta**, que é o
vocabulário que a aula construiu. Na V1 eu pedia "uma frase citando custo, latência ou memória"; na V2 eu
peço a conta, porque frase citando custo ainda é frase.

**1.** **[Projeto os cinco cenários e formo as duplas]** Oito minutos, em dupla. Cinco cenários. Para cada um
eu quero três coisas: a família — encoder-only, encoder-decoder ou decoder-only; o que vocês usariam de
atenção eficiente, ou explicitamente nada; e **que conta ou medição confirmaria** a escolha. E eu vou ser
chato com a terceira: "porque é melhor" não conta, e "porque é mais novo" desconta — esse é literalmente o
chamado dois com que eu abri a aula.

Os cinco cenários:

1. Classificar dez milhões de comentários por dia em três rótulos, com latência de milissegundos.
2. Busca semântica sobre quinhentos mil documentos internos, com reranking dos cinquenta primeiros.
3. Assistente que conversa, chama ferramenta e escreve código.
4. Responder perguntas sobre um contrato de oitenta páginas lido inteiro de uma vez.
5. Servir um modelo de oito bilhões de parâmetros para mil usuários simultâneos, com contexto de trinta e
   dois mil tokens.

*Bastidor — erros comuns:* o erro dominante é responder "LLM" para os cinco. Os cenários 1 e 2 são
encoder-only por custo, e o 2 é encoder-only **duas vezes** — um modelo de embedding para recuperar e um
cross-encoder para reranquear, que é exatamente a arquitetura da Aula 19; a conta que confirma é o número de
pares que o reranker pontua, cinquenta por consulta e não quinhentos mil. No cenário 3 a resposta é
decoder-only e não tem discussão; é o cenário de controle. No 4, a dupla frequentemente responde só "contexto
longo" e esquece que janela longa custa cache — a alavanca aqui é janela deslizante com atenção global nos
tokens da pergunta, e a conta é `n·w` contra `n²` **mais** a verificação de que o alcance por profundidade não
cobre oitenta páginas. E no 5 o erro é confundir peso do modelo com KV cache: oito bilhões de parâmetros em
dois bytes são dezesseis gibibytes de peso, constantes; o cache com trinta e dois mil tokens de contexto,
por usuário, é o que multiplica por mil. Um segundo erro no 5, mais sutil: dar a conta e parar nela, sem
notar que a conta **não fecha**.

*Como recolher:* oito minutos de dupla, três de correção conduzida por mim. Não corrijo os cinco: peço
voluntário para o 1 e forço a terceira coluna — "como você confirmaria isso?" —, corrijo o 2 rápido apontando
que são dois encoders e sinalizando a Aula 19, e gasto os minutos finais no cenário 5. No 5 eu faço a conta
na frente deles com a fórmula do slide 8, primeiro com atenção multi-cabeça cheia e depois com GQA de oito
cabeças de key/value. E eu fecho com a parte honesta: **mesmo com GQA a conta para mil usuários simultâneos
não fecha.** GQA é a primeira alavanca, não a solução — o resto é gerenciamento de memória de cache e
agendamento de requisições, que é o que a Aula 10 trata como inferência eficiente. Encerro dizendo isso: "a
conta ainda não fecha, e é por isso que existe uma aula sobre inferência".

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a aritmética em aula. A
regra geral é remeter ao apêndice e seguir; conduzir uma conta só se sobrar tempo, e anunciando que é
conteúdo de consulta.

> **Nota:** Bastidor: o custo de cada item abaixo sai do bloco em que a pergunta aparece. Se eu fizer o item
> 2 inteiro, perco o exercício — e o exercício vale mais para o objetivo da aula, porque é onde a conta vira
> decisão. A ordem de preferência para sacrificar está no fim desta parte.

**Item 1 — "Por que um BERT não gera texto?" (A.1, ~5 min).**
A pergunta mais interessante do Bloco 1, e a que eu mais gosto de responder porque a resposta fácil está
errada. Se eu tiver os cinco minutos, eu conduzo assim: escrevo a perda causal e digo que aquela soma **é** a
log-verossimilhança da sequência inteira, pela regra da cadeia — cada fator é uma condicional, e o produto
dos fatores é a probabilidade do texto. Gerar é ler essa fatoração da esquerda para a direita. Depois escrevo
a perda do MLM ao lado e mostro que não existe produto daqueles termos que dê a probabilidade do texto:
cada termo condiciona em posições que outros termos tratam como alvo. É pseudo-verossimilhança.
**Versão de 30 segundos:** "a perda causal é a verossimilhança exata pela regra da cadeia, e gerar é ler a
fatoração. O MLM não tem fatoração nenhuma — ele otimiza uma pseudo-verossimilhança. Não é que ele não foi
treinado para gerar: é que não existe o objeto de que a geração precisaria. Está em A.1, com três razões."

**Item 2 — "Faz a multiplicação do cache aí" (A.2, ~5 min).**
A pergunta mais provável do Bloco 2. Se eu decidir fazer, eu faço em **duas etapas** e não em seis fatores de
uma vez, porque foi assim que a V1 travava a sala. Etapa um: dois vezes trinta e dois vezes trinta e dois
vezes cento e vinte e oito dá duzentos e sessenta e dois mil valores por token, e a dois bytes é meio
mebibyte. Etapa dois: multiplica pelo contexto, e depois pelo número de conversas. E eu digo em voz alta a
razão de cada fator: o dois é K e V, o L é porque cada camada tem projeções próprias, o `d_head` é porque a
projeção já reduziu a dimensão.
**Versão de 30 segundos:** "meio mebibyte por token no modelo hipotético, quatro gibibytes por conversa de
oito mil. A conta fator a fator, com a razão de existir de cada fator e a leitura de banda de memória, está
em A.2 — e a instanciação com números reais é o que a demo já fez, lendo o `config.json`."

**Item 3 — "Como se prova que o fator do GQA é exatamente essa razão?" (A.2, ~3 min).**
Barata e satisfatória, e vale sempre que aparecer. Eu escrevo o cache das duas configurações uma em cima da
outra e divido: camadas, dimensão por cabeça, tokens e bytes são os mesmos nas duas, então cancelam. Sobra a
razão dos números de cabeças de key/value. Duas linhas, e o resultado é exato, não aproximado.
**Versão de 30 segundos:** "compare duas configurações que só diferem no número de cabeças de key/value: todos
os outros fatores cancelam e sobra a razão entre eles. É exato. Está em A.2."

**Item 4 — "A profundidade não resolve o alcance longo?" (A.3, ~4 min).**
A melhor pergunta que pode aparecer no Bloco 2, e se ela vier eu abro espaço. Eu escrevo o alcance por
profundidade — `L` vezes `w` sobre dois —, instancio com doze camadas e janela quinhentos e doze, dá três mil
setenta e dois. E aí comparo com trinta e dois mil, que é a sequência: nove por cento. E inverto a conta:
para cobrir a sequência, `L` maior ou igual a duas vezes `n` sobre `w`, que dá cento e vinte e oito camadas.
Fecho com a consequência: por isso a atenção global não é opcional, e por isso escolher onde ela vai é
decisão de projeto.
**Versão de 30 segundos:** "a profundidade compra `L` vezes `w` sobre dois: três mil de trinta e duas mil.
Para cobrir a sequência seriam cento e vinte e oito camadas. É a atenção global que faz o alcance de ponta a
ponta, e ela reduz o diâmetro para duas camadas. Está em A.3."

**Item 5 — "De onde vem esse T ao quadrado da destilação?" (A.4, ~5 min).**
Raramente perguntam, e quando perguntam vale, porque é a única derivação realmente elegante do Bloco 2. Eu
digo que o gradiente do termo suave em relação a um logit do aluno é a diferença entre as duas distribuições
suavizadas, dividida pela temperatura — e que, em temperatura alta, essa diferença **também** encolhe como um
sobre T. Dois fatores de um sobre T, então o gradiente iria a zero como um sobre T ao quadrado; multiplicar
por T ao quadrado devolve a magnitude e faz alfa significar a mesma coisa em qualquer temperatura. E fecho
com o resultado bonito: nesse limite, destilar é igualar logits.
**Versão de 30 segundos:** "o gradiente do termo suave escala como um sobre T ao quadrado em temperatura alta;
o T ao quadrado compensa isso para que o peso alfa signifique a mesma coisa em qualquer temperatura. E nesse
limite destilar é literalmente igualar os logits. A derivação está em A.4."

### Ordem de sacrifício

Se a aula atrasar: corto primeiro o **slide 12** da exposição, deixando-o projetado durante o exercício —
ele se sustenta lido e é assim que a turma o usa de qualquer forma. Depois comprimo o **slide 6**
(encoder-decoder) para três minutos, mantendo só a conexão com Bahdanau, que é o pagamento da promessa da
Aula 5. Depois encolho a **destilação** de seis para quatro minutos, ficando no número da cauda e no
fechamento com o chamado dois.
**Não corto** o slide 8 nem o slide 10: os dois juntos são a resposta do chamado um e o pré-requisito direto
da Aula 10, e uma Aula 10 que precisa reensinar a fórmula do cache perde os primeiros dez minutos dela.
**Não corto** os passos 6 e 7 da demo, que são os únicos números reais da aula. E **não corto** o cenário 5
do exercício, porque é ele que entrega a aula seguinte — a conta que não fecha é a porta da Aula 10.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 14 da Parte 1 — os três chamados fechados com a causa
nomeada e onde ela mora, a síntese das duas metades (a máscara é a arquitetura; o cache é a fatura), o índice
do apêndice projetado por vinte segundos, a ponte para a Aula 9 (Laboratório 2: Mini-GPT do zero em PyTorch) e
as três leituras da semana com a pergunta dirigida do GQA.

> 🗣️ "Hoje vocês escolheram a família por uma conta, não por uma data. Na próxima aula vocês escrevem a máscara causal em PyTorch e treinam a coisa até ela gerar texto."

---

*Roteiro do Instrutor · Aula 8 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
