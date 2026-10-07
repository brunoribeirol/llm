---
aula: 16
titulo: "Modelos de raciocínio: GRPO e DeepSeek-R1"
tipo: teorica
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 16 de 30 (V2)

## Como usar este roteiro

A prosa deste documento é **fala em primeira pessoa**: é o que eu digo em sala, na ordem em que
digo. Não é resumo do conteúdo — é o texto falado.

As linhas marcadas com 🗣️ são as **frases-âncora**: as que eu cravo, quase palavra por palavra.
As notas marcadas com **Bastidor** são operacionais e **não são faladas em voz alta**. Nesta aula
elas têm peso extra: é a última antes da prova, e a ansiedade da turma vai tentar entrar no
conteúdo. O bastidor do slide 1 e o do slide 15 são o meu jeito de conter isso num lugar só.

> **O que muda nesta versão.** A aula é conduzida por quatro comportamentos observáveis: o modelo
> que acerta com dez tentativas e erra com uma, a conta que triplica sem ganho, a cadeia bonita que
> leva à resposta errada, e a cadeia que cresce sem acertar mais. As fórmulas são **enunciadas e
> lidas**; as derivações estão no apêndice do deck (A.1 a A.5), e lá estão mais completas do que a
> V1 tinha — o estimador de `pass@k` ganhou a derivação combinatória e a prova de variância, e a
> vantagem do GRPO ganhou a demonstração de que dispensa a rede de valor. Eu **não** derivo no
> quadro. Se a turma pedir, a **Parte 4** tem a condução pronta.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · O sintoma: acerta com dez tentativas, erra com uma · 00:00–00:10

Boa noite, pessoal. Eu vou começar hoje por um número que força uma decisão de produto.

Imaginem um modelo que resolve um problema quando vocês dão a ele dez tentativas, e erra quando
vocês dão uma. Não é hipótese: é o resultado padrão de qualquer avaliação de raciocínio que vocês
forem ler esta semana. E aí está a questão desconfortável: o usuário de vocês recebe **uma**. A
capacidade existe no modelo e não chega ao produto.

E tem um segundo comportamento que anda junto com esse, e que eu quero deixar na mesa desde já. Um
time liga o modo de raciocínio no produto inteiro, achando que é melhoria geral. A conta de API
triplica. E a métrica da tarefa fácil não se move — em algumas, ela piora.

Aula passada a gente fechou o alinhamento por preferência humana, e eu terminei com uma conta que
não fecha: todo aquele maquinário depende de gente sentada anotando pares, e gente concorda em
setenta por cento dos casos. Caro, lento, ruidoso.

Hoje eu venho pelo outro lado. Existe uma família de tarefas em que ninguém precisa dizer qual
resposta é melhor, porque dá para **conferir por programa** se ela está certa. Se a resposta é um
número, eu comparo com o gabarito. Se é código, eu rodo o teste. E no momento em que o sinal sai de
um programa, o custo marginal de pontuar uma tentativa cai a zero — e isso muda a economia inteira
do pós-treino.

Antes de começar, um recado de logística: a prova é na próxima aula. Eu reservei os últimos cinco
minutos de hoje inteirinhos para ela — formato, escopo e roteiro de estudo. Dúvida de prova eu vou
empurrar para lá, para o conteúdo de hoje não virar sessão de ansiedade coletiva.

> 🗣️ "Ter a resposta certa entre dez não é o mesmo que entregá-la. A distância entre essas duas coisas tem nome, tem fórmula e tem preço."

> **Nota:** Bastidor: dizer o recado da prova logo no primeiro slide é deliberado — sem isso, a
> primeira mão levantada é sobre a prova e o Bloco 1 nunca começa. Se alguém insistir, apontar o
> relógio e dizer "01:55". **Não** nomear `pass@k` aqui: o nome chega no slide 6, depois de a turma
> sentir a falta dele. Ter o quadro dos quatro modelos do PPO da Aula 15 pronto para redesenhar no
> slide 11.

### Slide 2 · Por que "amostra mais" não é uma resposta · 00:10–00:15

A reação natural ao que eu acabei de mostrar é: então amostra mais. Deixa eu quebrar essa intuição
em duas partes, porque as duas voltam a aula inteira.

Primeira parte. Sem um jeito de **conferir** qual das dez está certa, o ganho é inutilizável. "Uma
dessas dez respostas resolve o seu problema" não é uma coisa que eu entregue a um usuário. Eu sei
que a certa está lá dentro e não sei qual é — e não saber qual é anula o valor de ela estar lá.

Segunda parte, e essa é mais sutil. Sem verificador, a única regra de seleção que sobra é o voto
majoritário: eu fico com a resposta que apareceu mais vezes. E isso falha exatamente quando o
modelo erra de forma **consistente**. Se ele erra sempre do mesmo jeito, a moda é errada e é firme,
e mais amostras só dão mais votos ao candidato errado. Mais votos para o candidato errado não
elegem o certo.

Então amostrar mais aumenta o que o modelo *pode* fazer. Não aumenta necessariamente o que ele
*entrega*. E essas duas coisas precisam de dois nomes diferentes, que é o que eu vou dar daqui a
pouco.

> 🗣️ "Mais amostras compram potencial. Transformar potencial em produto exige alguém capaz de apontar a resposta certa — e é isso que um verificador é."

> **Nota:** Bastidor: não dar os nomes das métricas ainda. O objetivo aqui é a turma sentir que
> falta uma palavra. Se alguém já soltar "pass@k", confirmar em uma frase e seguir — o slide 6 é
> daqui a vinte minutos.

### Slide 3 · O que a gente vai chamar de raciocínio · 00:15–00:21

Deixa eu cravar a definição antes de qualquer outra coisa, porque essa palavra carrega bagagem
demais e a discussão desanda se eu não amarrar.

Nesta disciplina, raciocínio é uma coisa operacional: resolução em várias etapas, em que o modelo
produz ou usa passos intermediários antes de fixar a resposta. O contraste é direto. Modelo
vanilla: entra o prompt, sai a resposta. Modelo de raciocínio: entra o prompt, sai uma cadeia
intermediária, e depois sai a resposta. É uma definição de engenharia — mensurável, e útil para eu
decidir arquitetura.

E agora a parte em que eu preciso ser honesto: isso **não** é uma afirmação sobre cognição. Não
existe consenso científico sobre se o que esses modelos fazem "é" raciocínio no sentido que a
palavra tem em filosofia da mente. Eu adoto essa definição porque ela me deixa medir e decidir, não
porque ela resolve a pergunta grande.

E aqui vem o terceiro comportamento observável da aula, e ele é o mais traiçoeiro dos quatro: a
cadeia bonita que leva à resposta errada. Vocês vão ver isso. Uma cadeia impecável, bem formatada,
com passos que parecem certos, terminando num número errado. E vão ver o inverso também — cadeia
confusa terminando na resposta certa.

O erro que eu quero desarmar de véspera é tratar a cadeia como registro fiel do processo interno.
Não é. Aquela cadeia é texto gerado sob a mesma distribuição de todo o resto. Pode ser construída
depois da conclusão, pode ser inconsistente com a resposta final, pode ser bonita e irrelevante.
Medir o quanto ela de fato representa a computação que levou à resposta é problema aberto, e volta
na Aula 27.

> 🗣️ "A cadeia que aparece na tela é texto gerado como qualquer outro. Ela pode ser explicação e pode ser álibi — e distinguir as duas coisas é problema em aberto."

> **Nota:** Bastidor: este é o slide que atrai o debate filosófico. Reconhecer a legitimidade da
> pergunta, marcar que a definição do curso é operacional e explicitamente não-cognitiva, e cortar
> em três minutos apontando para a Aula 27. Se a turma quiser insistir, prometer cinco minutos no
> fim — e não cumprir, porque o fim é da prova.

### Slide 4 · A fatura em três eixos · 00:21–00:27

Voltando ao segundo comportamento da abertura: a conta que triplicou sem ganho. Deixa eu abrir essa
fatura, porque essa parte quase nunca aparece nas manchetes.

São três custos que chegam juntos. O primeiro é **latência**: a resposta só começa a sair depois
que a cadeia terminou. Se o modelo gastou dois mil tokens pensando, o usuário está olhando para uma
tela parada durante aqueles dois mil tokens. O segundo é **preço**: token de raciocínio é cobrado
como qualquer outro, e em tarefa difícil ele costuma ser a maior parte da conta — paga-se mais pelo
que o modelo pensou do que pelo que ele respondeu. E o terceiro é **contexto**: a cadeia ocupa
janela. Cada token de raciocínio é um token que não é documento recuperado, e essa colisão é
literal: ela aparece na Aula 18, quando a gente montar RAG e tiver que decidir o que cabe.

A analogia que eu uso é hora extra. Hora extra resolve o problema difícil na sexta à noite. Hora
extra como rotina destrói a margem da empresa.

E daí sai o corolário de projeto: raciocínio é uma **alavanca** que se puxa em tarefa difícil e
verificável. Não é uma configuração global do produto. O erro comum é a conclusão preguiçosa de que
"modelo de raciocínio é melhor". Em tarefa fácil ele é mais caro, mais lento e às vezes pior —
porque uma cadeia longa é uma cadeia com mais oportunidades de errar do que a resposta direta tinha.

> 🗣️ "Raciocínio é hora extra. Resolve o problema difícil e destrói a margem se virar rotina."

> **Nota:** Bastidor: se alguém pedir números concretos de preço por milhão de tokens, não estimar
> de cabeça — as tabelas mudam e ficam como `[definir na oferta]`. O ponto do slide é a estrutura
> dos três custos, não a cotação da semana.

### Slide 5 · Onde há gabarito automático · 00:27–00:32

Agora uma observação sobre a literatura que parece trivial e não é.

Se vocês olharem os papers de raciocínio, os benchmarks são quase sempre os mesmos: matemática —
GSM8K, MATH, AIME — e código — HumanEval, MBPP, SWE-bench. E a pergunta natural é por que esses
dois domínios, se raciocínio deveria importar em direito, em medicina, em análise de negócio.

A resposta é estrutural e é o eixo da aula: **nesses dois domínios a resposta é conferível por
máquina**. Comparar um número com o gabarito é trivial. Rodar uma suíte de testes é barato e é
automático. O SWE-bench, do Jimenez e coautores, arXiv 2310.06770, é o caso mais duro da lista: ele
pega uma issue real de um repositório real e usa a suíte de testes do próprio projeto como
verificador. Nenhum humano na alça de correção.

E aqui está o erro de leitura que eu quero desarmar: confundir o domínio dos benchmarks com o
domínio da capacidade. Matemática e código dominam a literatura porque são **fáceis de corrigir**,
não porque sejam onde o raciocínio importa mais. A área otimiza o que ela consegue medir barato — e
essa frase vale para muito além desta aula.

> 🗣️ "Matemática e código dominam a literatura de raciocínio porque são fáceis de corrigir, não porque sejam onde raciocinar importa mais."

> **Nota:** Bastidor: este slide costuma provocar "então não dá para treinar raciocínio jurídico?".
> A resposta honesta é: dá, com preferência humana ou juiz calibrado, e sai muito mais caro — e é
> exatamente o fechamento. Anotar a pergunta no quadro e devolver ao slide 15.

### Slide 6 · O fundamento nomeado: `pass@k` · 00:32–00:39

Se a resposta é conferível, eu posso fazer uma coisa que em geração aberta eu não posso: gerar
várias tentativas e perguntar se **alguma** delas está certa. E a métrica que mede isso é `pass@k`.

*[Projeto a fórmula e leio em voz alta, apontando cada termo.]*

`pass@k` é a probabilidade de pelo menos uma resposta correta num orçamento de `k` tentativas. Eu
gerei `n` amostras, `c` delas acertaram, e a fórmula é um menos combinação de `n` menos `c`,
escolhe `k`, sobre combinação de `n` escolhe `k`.

A leitura em português, termo a termo, porque a fórmula intimida e a ideia é simples. O numerador
conta de quantos jeitos eu escolho `k` amostras **só entre as erradas**. Dividido pelo total de
jeitos de escolher `k` amostras quaisquer, isso é a probabilidade de eu tirar `k` amostras e todas
serem erradas. E um menos isso é a probabilidade de pelo menos uma estar certa.

Os extremos confirmam. Se `c` é zero, todas as escolhas são de erradas, a razão dá um, e `pass@k` é
zero para qualquer `k`. Se `c` é igual a `n`, não existe nenhuma escolha só de erradas, a razão dá
zero, e `pass@k` é um. E se `k` é um, a conta desmonta em `c` sobre `n`, que é a acurácia empírica.
Faz sentido.

Duas coisas que eu quero cravar sobre esse estimador, e as duas estão demonstradas em A.1. A
primeira: ele é **não-viesado** — a esperança dele é exatamente um menos, um menos `p`, elevado a
`k`. A segunda, que é a que quase nunca se conta: ele tem variância **menor** que a do estimador
ingênuo, que seria rodar `k` amostras e ver se acertou. E o motivo é bonito: o ingênuo olha só `k`
das `n` amostras e reduz tudo a um bit; o combinatório usa as `n` e calcula a média sobre todos os
subconjuntos possíveis, de forma fechada. Menos sorteio, menos variância.

E agora a condição que separa isso de um número decorativo: **`pass@k` só é acionável se existir
verificador**. É o slide 2, agora com nome.

> 🗣️ "`pass@k` mede o que o modelo **pode** fazer. `pass@1` mede o que ele **entrega**. Comparar o `pass@10` de um com o `pass@1` de outro é comparar potencial com produto."

> **Nota:** Bastidor: **não derivar em aula.** Se a fórmula travar a sala, ir ao quadro pelos
> extremos primeiro — `c = 0`, `c = n` — e só depois o caso `n = 10, c = 1, k = 5`, que dá
> exatamente 0,5. O combinatório fica intuitivo pelos extremos e não pela álgebra. A derivação
> combinatória inteira, a prova de que é não-viesado e o argumento de Rao-Blackwell para a variância
> estão em A.1 — mais completos do que a V1 tinha. Se insistirem: Parte 4, item 1.

### Slide 7 · `consensus@k`: o que o verificador compra · 00:39–00:45

E se não existir verificador? Aí sobra a coisa muito mais modesta do slide 2: gerar `k` amostras e
ficar com a resposta que apareceu mais vezes. Voto majoritário. A taxa de acerto desse voto é o que
a gente chama de `consensus@k`.

E vale reparar na assimetria, que é a desigualdade projetada aí: `consensus@k` é sistematicamente
**menor ou igual** a `pass@k`, e nunca maior. O motivo é direto — a resposta certa pode estar entre
as `k` sem ser a maioria delas. O `pass@k` conta que ela apareceu; o `consensus@k` só conta se ela
ganhou a eleição. Em A.2 isso está demonstrado numa linha, por inclusão de eventos: se o voto
majoritário acertou, então a resposta certa apareceu ao menos uma vez. Vale para todo `k`, toda
distribuição e toda regra de desempate.

E aí está a leitura mais importante do Bloco 1: **a distância entre essas duas curvas é,
literalmente, o valor de ter um verificador.** É o quanto eu ganho por ser capaz de olhar as dez
respostas e apontar a certa, em vez de ter que apostar na mais popular. Daqui a pouco eu mostro esse
número medido, na tela, e ele é grande.

E o erro do slide 2, agora quantificável: achar que amostrar mais sempre melhora o consenso. Não
melhora. Com `k` crescendo, o voto majoritário converge para a **moda** da distribuição de respostas
— então ele converge para um se a moda for a resposta certa, e converge para zero se a moda for
errada. Enquanto isso, `pass@k` converge para um sempre que a resposta certa tiver probabilidade
positiva. São duas perguntas diferentes: uma é "a resposta certa está no suporte", a outra é "a
resposta certa é a mais provável". A segunda é muito mais exigente.

> 🗣️ "A distância entre a curva de `pass@k` e a de `consensus@k` é o preço que vale a pena pagar por um verificador."

> **Nota:** Bastidor: escrever `pass@k ≥ consensus@k` num canto do quadro e deixar até o fim do
> Bloco 1 — na demo eu aponto para a desigualdade em vez de reexplicar. Se alguém perguntar sobre
> self-consistency do paper do Wang, é isto: `consensus@k` é a métrica dela. A análise assintótica
> que eu acabei de resumir está escrita em A.2, com o caso do problema `servidor` lido pela fórmula.

### Slide 8 · [Demo] Os números medidos · 00:45–00:55

Agora eu paro de afirmar e vou medir. Dez minutos, script rodando na tela.

*[A demonstração completa está na Parte 2 deste roteiro.]*

O que vai aparecer são cinco problemas de aritmética de várias etapas, dez amostras de cada, em três
temperaturas, com as duas tabelas lado a lado. E o resultado é um trade-off limpo: a temperatura que
ganha em `pass@1` **perde** em `pass@10`, e vice-versa.

> 🗣️ "A temperatura que vence depende inteiramente de quantas tentativas eu tenho. Não existe uma temperatura boa — existe uma temperatura boa para um orçamento."

> **Nota:** Bastidor: passos detalhados na Parte 2. Rodar a rota `--offline`, que é determinística e
> não depende de rede nem de chave. Se o Python da sala não subir, a saída da véspera está salva em
> texto e o PNG do gráfico já existe — a demo vira leitura de tabela, e é ali que está o valor
> pedagógico de qualquer jeito. Depois deste slide vai o intervalo de 10 min.

### Slide 9 · Recompensa verificável: o professor automático · 01:05–01:12

Voltando. O Bloco 1 foi sobre medir. O Bloco 2 é sobre treinar.

Deixa eu retomar o problema da Aula 15. Naquele pipeline, o sinal de treino vinha de preferência
humana: um anotador olhava duas respostas e dizia qual era melhor. Caro por hora de anotador, lento,
e ruidoso — anotadores discordam entre si em trinta por cento das comparações abertas, e o modelo de
recompensa aprende a média de opiniões que não concordam.

Agora, quando a tarefa tem verificador, o sinal sai de um programa. A resposta bate com o gabarito?
Recompensa um. Não bate? Zero. Acabou. Sem anotador, sem modelo de recompensa aprendido, sem o viés
de quem anotou, e — o mais importante para escala — sem custo marginal por amostra. Eu posso pontuar
um milhão de tentativas hoje à noite.

Tem uma segunda recompensa que anda junto e que é mais esperta do que parece: a **recompensa de
formato**. O modelo ganha ponto por emitir a cadeia dentro de uma marcação, tipo `<think>` e
`</think>`, e a resposta fora dela. Parece cosmético e não é: é o que torna a saída parseável, e
portanto verificável de forma estável. Sem formato fixo, o meu verificador vira uma expressão
regular frágil que quebra na primeira resposta criativa.

A analogia é a diferença entre corrigir redação e corrigir prova de múltipla escolha. A segunda
escala sem limite — e é exatamente por isso que o RL de raciocínio começou aí, e não em outro lugar.

E o erro conceitual que eu preciso desarmar: verificável **não** quer dizer fácil. O verificador
define, com precisão cirúrgica, o que vai ser otimizado. Verificador fraco produz reward hacking,
que é o mesmo risco da Aula 15 vestindo roupa nova. Um teste unitário incompleto ensina o modelo a
**passar no teste** — não a resolver o problema. Se o teste só confere o caso feliz, o modelo
aprende o caso feliz e ignora o resto, e faz isso porque foi exatamente isso que eu paguei para ele
fazer.

> 🗣️ "O verificador não mede a qualidade da resposta. Ele define o que vai ser otimizado — e o modelo vai otimizar exatamente aquilo, inclusive o que eu esqueci de conferir."

> **Nota:** Bastidor: se a turma colou reward hacking na Aula 15, retomar em uma frase e seguir; se
> não colou, dar o exemplo do teste que só cobre o caso feliz. Este conceito volta no exercício, no
> caso 6 — não gastar mais que dois minutos aqui.

### Slide 10 · GRPO: a linha de base sai do próprio grupo · 01:12–01:21

Agora o algoritmo, e ele é bonito de simples.

Deixa eu lembrar o PPO da Aula 15. Ele carrega quatro modelos na memória durante o treino: a
política, a referência congelada para o KL, o modelo de recompensa, e o modelo de **valor**. Esse
último existe para uma coisa só: estimar a linha de base contra a qual eu meço se uma ação foi boa
ou ruim. É uma rede inteira, treinada em paralelo, cujo único trabalho é responder "quanto eu
esperava ganhar aqui?".

*[Projeto o bloco e leio.]*

O GRPO — do Shao e coautores, arXiv 2402.03300 — elimina esse modelo com uma observação que, depois
de ouvida, parece óbvia: se eu vou amostrar várias completações **para o mesmo prompt** de qualquer
jeito, a média do próprio grupo já é a linha de base. Amostro `G` completações, pontuo todas com o
verificador, e a vantagem de cada uma é a nota dela menos a média do grupo, dividida pelo desvio.
Quem ficou acima é reforçado, quem ficou abaixo é penalizado.

E eu quero ser preciso sobre por que isso é **legítimo**, porque parece mágica e não é. Existe um
resultado que diz que qualquer linha de base que dependa só do prompt — e não da completação
amostrada — deixa o gradiente de política **sem viés**. Ela não muda para onde o gradiente aponta;
muda só a variância. O PPO usa essa liberdade para aprender uma rede. O GRPO usa a mesma liberdade
para calcular uma média amostral. É a mesma quantidade estimada por dois caminhos, e a demonstração
está em A.3, em cinco linhas.

Sobre a divisão pelo desvio, que é a pergunta que sempre vem: ela não é cosmética. Com recompensa
binária, a conta fecha e dá para ler direto. Num problema difícil, em que só uma das dez
completações acertou, a correta recebe vantagem grande e as erradas recebem correção pequena — o
gradiente vai quase todo reforçar o caminho que funcionou. Num problema fácil, em que só uma errou,
é o contrário: a falha rara leva o empurrão grande. A padronização faz o passo se concentrar sozinho
no evento informativo do grupo. A forma fechada está em A.4, com a tabela.

E repara como isso encaixa em recompensa verificável: pontuar `G` completações é rodar o verificador
`G` vezes, e o verificador é um programa. O custo é desprezível. É a combinação certa de algoritmo e
domínio.

O erro comum é achar que o GRPO substitui o PPO em tudo. Não substitui. Ele resolve o caso "muitas
amostras do mesmo prompt, com pontuação barata" — que é o caso do raciocínio verificável, e não o
caso geral. Onde pontuar é caro, a média do grupo custa caro também.

> 🗣️ "O PPO precisava de uma rede inteira só para dizer 'quanto eu esperava ganhar aqui'. O GRPO responde isso com a média da própria turma."

> **Nota:** Bastidor: escrever a fórmula da vantagem relativa no quadro e deixar até o slide 12. Se
> perguntarem por que dividir pelo desvio, a resposta curta é escala, e a tabela de A.4 é a resposta
> longa — vale projetar o apêndice por 20 s se a pergunta vier com força. **Não** abrir a derivação
> do clipping: é Aula 15, A.3, e consome dez minutos. Se pedirem a prova da linha de base: Parte 4,
> item 2.

### Slide 11 · GRPO × PPO, lado a lado · 01:21–01:27

Deixa eu botar os dois lado a lado, porque essa distinção é ponto de prova e eu quero que ela fique
gravada com o desenho, não com o texto.

À esquerda, o PPO da Aula 15: quatro caixas — política, referência, recompensa, valor. À direita, o
GRPO: as mesmas caixas com a de **valor riscada**, e no lugar dela um grupo de `G` completações do
mesmo prompt com a média marcada.

A troca, em uma linha: o PPO **aprende** uma linha de base; o GRPO **calcula** a linha de base por
amostragem. Uma custa uma rede a mais e generaliza para qualquer prompt. A outra custa `G` amostras
por prompt e não precisa aprender nada.

E tem uma consequência prática que eu quero explicitar: o GRPO troca **memória de treino** por
**computação de inferência**. Sumiu uma rede da GPU, apareceram `G` gerações por passo. Numa tarefa
em que gerar é barato e pontuar é um programa, esse é um câmbio excelente. Numa tarefa em que cada
geração custa uma chamada de API paga e cada pontuação custa um anotador, é péssimo. É o tipo de
decisão que vocês vão tomar no projeto final.

Uma pegadinha que vale saber, e está em A.3: com `G` igual a um, a média do grupo é a própria nota,
a vantagem dá zero e o gradiente some. O GRPO precisa de pelo menos dois. E tem o caso irmão desse:
se todas as `G` completações acertaram, ou todas erraram, o grupo inteiro tem vantagem zero e aquele
prompt não produz gradiente nenhum. É computação gasta sem sinal — e é por isso que existem
estratégias que descartam prompt saturado.

> 🗣️ "O PPO aprende a linha de base. O GRPO calcula a linha de base amostrando. É trocar uma rede de treino por mais gerações — e é um câmbio excelente quando pontuar é de graça."

> **Nota:** Bastidor: este é o slide que resolve a confusão GRPO/PPO mais rápido que qualquer
> explicação. Desenhar as quatro caixas do PPO no quadro e riscar a de valor **na frente deles**,
> com o giz, em vez de projetar o desenho pronto. O gesto de riscar é o que fica.

### Slide 12 · O pipeline DeepSeek-R1 em quatro etapas · 01:27–01:34

Agora o caso concreto, e ele tem um valor didático raro, porque o artigo — DeepSeek-AI, arXiv
2501.12948 — descreve o caminho **e os problemas de cada etapa**. Isso é raro na literatura, onde em
geral só se conta o que deu certo.

A primeira, **R1-Zero**: RL puro sobre o modelo base, sem SFT nenhum antes, só com recompensa
verificável e de formato. E o resultado é o que fez esse artigo virar assunto: comportamentos de
raciocínio **emergem** sozinhos. O modelo passa a revisar a própria conta, a voltar atrás quando
percebe que errou, a gastar mais tokens em problema difícil. Ninguém ensinou isso com exemplo —
apareceu porque acertar era recompensado e revisar aumentava a chance de acertar. Só que o R1-Zero
tem dois problemas concretos: mistura idiomas dentro da mesma cadeia, e a legibilidade é ruim.

A segunda, **cold-start SFT**: um conjunto pequeno de cadeias bem escritas, usado como ajuste
supervisionado antes do RL principal. Conserta formato e consistência de idioma. É pouco dado, com
propósito cirúrgico.

A terceira, **RL em larga escala**, agora com dados de raciocínio **e de não-raciocínio**
misturados. Por quê? Porque um modelo que só otimiza problema de olimpíada vira um resolvedor de
olimpíada e deixa de ser um assistente utilizável. Essa mistura é o que mantém o modelo generalista.

A quarta, **destilação**: as saídas do modelo grande viram dados de SFT para modelos densos menores,
que herdam boa parte do comportamento a uma fração do custo de servir.

E a leitura errada que eu quero desarmar: ler a primeira como o método final. A lição do artigo é a
oposta. O RL puro **prova que emerge** — e entrega um modelo desagradável de usar. As três seguintes
existem para consertar o que ele quebrou.

> 🗣️ "A primeira etapa prova que o raciocínio emerge sozinho. As três seguintes existem para consertar o modelo que ela produziu."

> **Nota:** Bastidor: se o tempo estiver apertado, comprimir as duas últimas para uma frase cada e
> proteger as duas primeiras — o par "emerge / mas fica ilegível" é o que a prova pode cobrar e é a
> pergunta dirigida da leitura da semana. Não abrir o fio de destilação: merece aula própria e não
> tem uma nesta ementa.

### Slide 13 · A cadeia que cresce sem acertar mais · 01:34–01:38

Quarto e último comportamento observável da aula, e é uma armadilha bonita.

Ao longo do RL, o comprimento médio da cadeia sobe. E aqui está o sintoma: **a taxa de acerto não
acompanha**. A curva de comprimento sobe e a curva de acerto achata. Parte do crescimento é ganho
real — problema difícil merece mais passos, e o modelo aprendeu isso. Mas parte é artefato do
objetivo, e a razão é precisa e vale saber.

O comprimento **não** entra na recompensa. Uma resposta certa em quarenta tokens e uma resposta
certa em quatro mil recebem exatamente a mesma nota: um. Só que o comprimento entra no
**gradiente**, porque a contribuição de uma completação é uma soma sobre os tokens dela. Uma
completação certa e longa tem mais parcelas, e empurra mais, com a mesma recompensa. O otimizador
não está sendo verboso de propósito; ele está explorando uma dimensão em que ninguém colocou preço,
e que aparece no gradiente sem aparecer no objetivo.

Duas mitigações. A primeira é **normalização de comprimento** na vantagem, dividindo pela
quantidade de tokens da completação. Ela resolve o efeito que eu acabei de descrever — e, sendo
honesto, cria outro: dividir cada completação pelo próprio comprimento faz errar longo custar
**menos por token** do que errar curto, e o comprimento volta a subir pelo lado dos erros. Em A.5
está a conta e está a correção usual, que é normalizar por uma constante em vez do comprimento da
amostra. A segunda mitigação é **budget forcing**, na inferência: limitar ou forçar o orçamento de
raciocínio. Essa não mexe no gradiente — mexe na fatura do slide 4.

O erro comum, e ele está em muita manchete: interpretar cadeia mais longa como raciocínio melhor.
Sem controle, comprimento é a variável mais fácil de o otimizador inflar.

> 🗣️ "Se ninguém põe preço no token, alongar é grátis. Cadeia mais longa não é raciocínio melhor — às vezes é só reward hacking barato."

> **Nota:** Bastidor: este é o slide que eu corto se o relógio estourou — vira leitura dirigida. O
> que **não** se corta é o slide 11 nem o aviso da prova no 15. A conta do efeito no gradiente e o
> viés que a normalização introduz estão em A.5, e o paralelo com o DPO da Aula 15 está lá também.

### Slide 14 · [Exercício] Quem tem verificador, e o que ele não confere · 01:38–01:50

Doze minutos: sete de dupla e cinco de correção. Seis tarefas, e desta vez eu quero uma coluna a
mais do que parece óbvio.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> 🗣️ "A pergunta não é só 'dá para conferir'. É 'o que fica de fora quando eu confiro' — porque é exatamente ali que o modelo vai morar."

> **Nota:** Bastidor: enunciado e correção na Parte 3. Cronometrar de verdade. A coluna "o que ele
> não confere" é a novidade da V2 e é ela que produz o artefato da aula. O caso que interessa é o 6
> — tradução Python para Rust — e é nele que eu gasto a maior parte da correção.

### Slide 15 · Fechamento: o critério do módulo — e a prova é na próxima aula · 01:50–02:00

Deixa eu fechar o Módulo 4 inteiro com um critério, e depois falar da prova.

O módulo passou por três formas de sinal de pós-treino. **Imitação**, na Aula 13: eu mostro exemplos
de boa resposta e o modelo copia. **Preferência humana**, na Aula 15: eu não sei escrever a resposta
certa, mas sei dizer qual de duas é melhor. E **verificação automática**, hoje: eu nem preciso
julgar, porque um programa confere.

E o critério prático que eu quero que vocês levem para o projeto final é uma pergunta só: **existe
verificador para a sua tarefa?** Se existe — código com teste, extração com schema, cálculo com
gabarito — vocês têm um caminho barato de melhoria: best-of-N com verificador já resolve muito, e RL
se houver orçamento. Se não existe, o caminho é preferência humana ou juiz calibrado, que é a Aula
27, e os dois são mais caros e mais ruidosos. Essa pergunta vale a pena ser feita na primeira
reunião do grupo de vocês, e o projeto é lançado na Aula 18.

Agora a prova. **Próxima aula, Aula 17, é a prova.** Individual, escrita, sem consulta e sem IA,
cobrindo da Aula 1 até esta aqui de hoje. Vale trinta por cento da média.

E eu quero ser explícito sobre uma coisa, porque muda o jeito de estudar: **o perfil da prova
mudou**. O peso está em interpretar, diagnosticar e justificar. Derivar vale **um** item, e ele vem
marcado como tal. A distribuição está no slide: quarenta e cinco pontos de diagnóstico, trinta de
justificativa de escolha, quinze de conceito aplicado, dez de derivação.

O roteiro de estudo, seis itens. Um: dado um sintoma de treino — treino que estagna quando a
dimensão cresce, perda boa demais com geração incoerente, memória que estoura ao dobrar o contexto
— nomear a causa e dizer que evidência a confirma. Dois: o mesmo, para comportamento de modelo
alinhado — bajulação, capacidade perdida, recompensa que sobe enquanto a avaliação humana cai. Três:
justificar a escolha entre prompting, RAG e fine-tuning para um cenário dado, citando o dado
disponível e a restrição. Quatro: justificar a escolha do sinal de pós-treino — imitação,
preferência ou verificação — dizendo de onde vem a recompensa e se os dados são fixos ou
amostráveis. Cinco: ler um número corretamente, e aí entram perplexidade entre tokenizadores,
`pass@k` contra `pass@1`, e por que `consensus@k` é menor ou igual a `pass@k`. E seis: um item de
fundamento formal, marcado como tal — uma das derivações dos apêndices —, e mesmo ele pede o que a
conta **prevê**, não só a conta.

Sobre como estudar isso: os cinco primeiros itens se estudam **refazendo os exercícios de
diagnóstico** de cada aula, não relendo fórmula. O item seis se estuda pelos apêndices dos decks,
que existem exatamente para isso e estão mais completos do que qualquer coisa que eu tenha escrito
no quadro.

Se eu tivesse que apontar onde a turma historicamente perde ponto, é nos itens de justificativa —
porque a resposta boa cita o **dado** e a **restrição**, e a resposta fraca cita só a preferência
pessoal. Quem consegue defender uma escolha em voz alta, com os dois eixos na frase, está pronto.

E a leitura da semana é secundária, com o R1: a introdução e a seção do R1-Zero, com a pergunta
dirigida — o RL puro produziu raciocínio emergente e dois problemas concretos; quais foram, e qual
etapa seguinte resolveu cada um? Quem já sabe responder isso, respondeu meia questão da prova.

> 🗣️ "A pergunta que fecha este módulo é uma só: existe verificador para a sua tarefa? A resposta decide se melhorar vai custar um programa ou vai custar gente."

> **Nota:** Bastidor: projetar o roteiro de estudo e ficar 30 s em silêncio para a turma fotografar.
> Dizer a distribuição de pontos em voz alta — é a informação que mais muda o comportamento de
> estudo da turma, e ela não estava na V1. Responder as dúvidas de formato aqui e só aqui —
> material permitido, duração, se tem consulta — porque foi o que eu prometi no slide 1. Não
> estourar o horário: chegar atrasado no dia da prova é o pior sinal possível de gestão de tempo.

---

## Parte 2 — Demonstração guiada

Dez minutos, script em `codigo/demo-pass-at-k.py`, rodado na rota `--offline`. Essa rota usa um
amostrador sintético determinístico com semente fixa: não depende de rede, não usa chave de API, e
produz exatamente a mesma tabela toda vez — então os números que eu digo aqui são os números que vão
aparecer na tela. Existe uma rota `--api` que chama modelo de verdade num provedor com free tier, e
ela fica como extensão pós-aula.

Preparação na véspera: rodar o script e salvar a saída em texto; conferir que o PNG
`pass-at-k-vs-temperatura.png` está gerado; confirmar que o Python da sala sobe.

**1.** **[Abro o terminal na pasta `codigo/` e rodo `python demo-pass-at-k.py --offline`]** São
cinco problemas de aritmética de várias etapas, escritos para esta aula no estilo do GSM8K — não são
itens do GSM8K. Cada um tem uma resposta correta e três distratores plausíveis, que são tipicamente
o resultado de esquecer uma das etapas. E eu preciso ser explícito sobre uma coisa antes de vocês
olharem os números: este amostrador **não resolve** os problemas. Ele simula a distribuição de saída
de um modelo pequeno. Em três dos cinco o argmax dele está certo; nos outros dois está errado, e a
resposta certa só aparece quando a amostragem se afasta do argmax. É essa assimetria que produz tudo
o que vem a seguir.

**2.** **[Mostro a listagem por problema em cada temperatura: acertos em 10, moda, gabarito]** Para
cada temperatura, o script lista os cinco problemas com quantas das dez amostras acertaram, qual foi
a moda das respostas e qual era o gabarito. Vou ler dois deles com vocês.

**3.** **[Aponto a linha do problema `servidor` em T = 0,2]** Esta linha aqui. Problema do servidor:
duzentas e cinquenta requisições por minuto, quarenta por cento mais depois da otimização, quantas
em três minutos. Gabarito mil e cinquenta. Em temperatura zero vírgula dois: **zero acertos em
dez**. Zero. E a moda foi setecentos e cinquenta — que é o que dá se a pessoa esquece de aplicar o
aumento de quarenta por cento e multiplica duzentos e cinquenta por três. O modelo não está confuso:
ele está **consistentemente errado**, e a moda errada é firme. É o slide 2 acontecendo numa linha de
tabela.

**4.** **[Aponto o mesmo problema em T = 1,2]** Mesmo problema, temperatura um vírgula dois:
**quatro acertos em dez**, e a moda agora é mil e cinquenta. A diversidade encontrou uma resposta
que a temperatura baixa nunca alcançava — e não só encontrou, como ela virou maioria. Em termos de
A.2: a probabilidade da resposta certa subiu o suficiente para ela virar o argmax da distribuição, e
por isso o consenso também passou a acertar aquele problema.

**5.** **[Abro a tabela de `pass@k` e leio as duas pontas]** Agora a tabela consolidada, com as três
temperaturas nas linhas e `k` igual a um, dois, cinco e dez nas colunas. Em `pass@1`, a melhor
temperatura é **zero vírgula dois**: zero vírgula cinco quatro zero, contra zero vírgula quatro
quatro zero da temperatura um vírgula dois. Ou seja: com **uma** tentativa, a temperatura baixa
ganha. Agora a coluna do `pass@10`: temperatura um vírgula dois dá **um ponto zero zero zero** —
resolveu os cinco problemas — e a temperatura zero vírgula dois dá zero vírgula seiscentos. A ordem
se inverteu completamente.

**6.** **[Circulo o valor de `pass@10` em T = 0,2 e comparo com `pass@5` na mesma linha]** E agora a
parte que eu acho a mais importante desta tabela. A temperatura zero vírgula dois **satura** em zero
vírgula seiscentos. Não é que ela cresce devagar: ela para. Por mais amostras que eu dê, ela não
passa disso, porque dois dos cinco problemas são simplesmente inalcançáveis naquela temperatura — a
resposta certa não está no suporte prático da distribuição. Mais orçamento não compra nada. Isso é
uma coisa que a intuição de "amostrar mais sempre ajuda" não prevê, e é exatamente o limite que A.2
descreve: `pass@k` só converge para um se a resposta certa tiver probabilidade positiva.

**7.** **[Abro a tabela de `consensus@k` e comparo com a de `pass@k` na temperatura 1,2]** Última
comparação, e é a que fecha o Bloco 1. Mesma temperatura um vírgula dois, mesmas dez amostras.
`pass@10` dá **um ponto zero zero zero**. `consensus@10` dá **zero vírgula oitocentos**. Essa
diferença — vinte pontos — é exatamente o que o verificador compra. Nos dois casos a resposta certa
estava lá dentro das dez. Com verificador eu colho as duas. Sem verificador, num deles a maioria
votou errado e eu entrego a resposta errada com toda a confiança do mundo.

**8.** **[Abro o gráfico `pass-at-k-vs-temperatura.png` com os dois painéis lado a lado]** E o
gráfico fecha visualmente: à esquerda as curvas de `pass@k` abrindo com o `k`, à direita as de
`consensus@k` subindo bem menos. A área entre elas é o que eu chamei de valor do verificador no
slide 7. O próprio script imprime a frase que eu quero que vocês levem, na última linha da saída:
`pass@k` mede o que o modelo **pode** fazer; `consensus@k` mede o que ele **entrega** sem
verificador.

> **Nota de contingência:** Bastidor: se o Python da sala não subir, abrir a saída salva da véspera
> em texto — a demo inteira é leitura de tabela e não perde nada de essencial. Se o `matplotlib` não
> estiver instalado, o script avisa e segue sem o gráfico; o PNG da véspera cobre. Se o tempo
> apertar, os passos 1 e 2 viram uma frase cada; os passos **6 e 7 não se cortam**, porque são os
> dois números que o exercício e o fechamento usam. Se alguém perguntar "que modelo é esse?",
> responder na hora e sem rodeio: é um amostrador sintético que simula a distribuição de um modelo
> pequeno, com semente fixa, e não resolve nada — a rota `--api` chama modelo real e é a extensão
> pós-aula. Não deixar essa ambiguidade passar: a demo perde autoridade se a turma achar que eu
> passei número simulado por medição real.

---

## Parte 3 — Hands-on

Doze minutos: sete de dupla e cinco de correção conduzida por mim. Seis tarefas projetadas. O
objetivo não é acertar a classificação — é forçar a dupla a **nomear** o verificador e, sobretudo, a
escrever **o que ele não confere**, porque é ao tentar escrever essa segunda frase que a fragilidade
aparece.

**1.** **[Projeto as seis tarefas e formo as duplas]** Sete minutos em dupla. No slide estão seis
tarefas. Para cada uma eu quero quatro coisas. Primeiro: existe verificador automático, sim ou não.
Segundo: se existe, qual é ele — em uma frase, com o nome da coisa que roda. Terceiro, e é a coluna
que vale: **o que ele não confere**. Quarto: se não existe verificador, qual seria o sinal de treino
alternativo — preferência humana, que é a Aula 15, ou juiz calibrado, que é a Aula 27.

| # | Tarefa |
|---|---|
| **1** | Resolver uma equação do segundo grau e devolver as raízes |
| **2** | Corrigir um bug num repositório de forma que a suíte de testes passe |
| **3** | Escrever um e-mail de desculpas a um cliente insatisfeito |
| **4** | Extrair de uma nota fiscal um JSON com CNPJ, valor e data, obedecendo a um schema |
| **5** | Resumir um artigo científico em um parágrafo |
| **6** | Traduzir uma função de Python para Rust preservando o comportamento |

E quando terminarem as seis, mais uma, que é de decisão de produto: com `pass@10` igual a um ponto
zero e `consensus@10` igual a zero vírgula oito, medidos na demo de hoje, o que vocês entregam ao
usuário? E o que muda nessa resposta se não houver verificador em produção?

*Bastidor — erros comuns:* a dupla escreve "sim" no caso 3 pensando em métrica automática de texto
tipo BLEU — e aí vale lembrar a Aula 1: sobreposição de n-gramas mede estilo, não qualidade, e não é
verificador de nada. No caso 4, muita gente para em "valida o schema" e esquece que schema válido
não é conteúdo correto — o CNPJ pode estar bem formatado e ser o CNPJ errado; o verificador completo
é schema **mais** conferência de campo contra o documento, e a coluna "o que ele não confere" é
exatamente onde isso aparece. No caso 5 vem a tentação de dizer "ROUGE", que é o mesmo erro do caso
3 com outro nome. E no caso 1, alguém sempre diz "compara a string" — e aí eu pergunto o que
acontece com `2` e `2.0`, e com raízes na ordem trocada; o verificador certo é comparação simbólica,
não textual, e é a mesma normalização de resposta que o `consensus@k` de A.2 exige para funcionar.

*Como recolher:* sete minutos de dupla, cinco de correção. Eu não corrijo os seis. Confirmo rápido
que 1, 2, 4 e 6 têm verificador — comparação simbólica; suíte de testes; validação de schema mais
conferência dos campos; testes de equivalência rodando nas duas linguagens — e que 3 e 5 não têm.
E aí eu gasto o resto no caso 6, porque ele é o mais rico da lista: o verificador **existe**, e ele
é **parcial**. Testes cobrem o comportamento observado nos casos que alguém escreveu; eles não
provam equivalência semântica das duas funções. Otimizar contra ele é exatamente o convite ao reward
hacking do slide 9 — o modelo aprende a passar naqueles testes, e a tradução pode estar errada em
tudo que os testes não olham. A frase que eu quero ouvir de alguém da sala é "o verificador existe
mas é incompleto, e o modelo vai encontrar o buraco". Se ninguém disser, eu digo e escrevo no quadro.

E a pergunta de decisão eu recolho no fim, em trinta segundos, de uma dupla só: com verificador em
produção, eu entrego a certa e a taxa é um ponto zero; sem verificador, eu entrego a mais votada e a
taxa cai para zero vírgula oito. Vinte pontos de produto separam ter e não ter um programa que
confere — e essa é a frase que emenda no fechamento.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a derivação em
aula. A regra geral é remeter ao apêndice e seguir; conduzir uma derivação só se sobrar tempo, e
anunciando que é conteúdo de consulta.

> **Nota:** Bastidor: o custo de cada item abaixo sai do Bloco 1 ou do Bloco 2, e nesta aula o
> relógio é mais apertado que o normal porque os últimos 5 min são da prova e **não** são
> negociáveis. A ordem de preferência para sacrificar, se for preciso: primeiro o slide 13
> (comprimento, que vira leitura dirigida), depois as duas últimas etapas do pipeline R1, depois os
> passos 1 e 2 da demo. O que **não** se sacrifica: o slide 11 e o aviso da prova no 15.

**Item 1 — "De onde vem essa fórmula do `pass@k`?" (A.1, ~5 min).**
A pergunta mais provável do Bloco 1. Eu faço só a contagem: total de subconjuntos de tamanho `k` é
`C(n,k)`; subconjuntos só de erradas é `C(n−c,k)`; a razão é a probabilidade de errar todas; um
menos isso é o resultado. Três linhas, e é combinatória de primeiro período. **Não** faço a prova de
não-viés nem o argumento de Rao-Blackwell no quadro — menciono que existem, que o estimador ingênuo
tem variância maior porque joga fora informação, e que a demonstração está em A.1.

**Item 2 — "Por que a média do grupo pode substituir a rede de valor?" (A.3, ~6 min).**
A pergunta mais provável do Bloco 2, e a mais legítima, porque parece mágica. Eu faço a conta da
linha de base no quadro: a esperança de `b(x)` vezes o gradiente do log da política é `b(x)` vezes a
soma dos gradientes das probabilidades, que é `b(x)` vezes o gradiente de um, que é zero. Cinco
linhas, e ela fecha a questão inteira. E eu fecho dizendo o que isso autoriza: **qualquer** linha de
base que dependa só do prompt serve, então trocar rede por média não é aproximação, é outra
estimativa da mesma coisa.

**Item 3 — "Por que dividir pelo desvio?" (A.4, ~4 min).**
Vale fazer, porque a resposta é curta e é a que fixa o GRPO. Com recompensa binária e `p̂` de
acertos no grupo, a média é `p̂` e o desvio é a raiz de `p̂` vezes um menos `p̂`. Eu escrevo os dois
valores que a vantagem assume — mais raiz de `(1−p̂)/p̂` para a correta, menos raiz de `p̂/(1−p̂)`
para a errada — e leio a tabela: problema difícil dá vantagem grande ao acerto raro, problema fácil
dá vantagem grande em módulo à falha rara. A tabela completa está em A.4 e dá para projetar em vez
de escrever.

**Item 4 — "Como o comprimento entra se ele não está na recompensa?" (A.5, ~4 min).**
Se a pergunta vier no slide 13, ela merece resposta na hora porque é o cerne do sintoma. Eu escrevo
a contribuição de uma completação como a vantagem vezes a soma dos gradientes de token, e aponto que
o número de parcelas é o comprimento. Uma linha resolve. Se sobrar meio minuto, digo o viés que a
normalização por `|o|` cria — errar longo custa menos por token — e remeto a A.5 para a correção.

**Item 5 — "Prova que `consensus@k` é sempre menor?" (A.2, ~2 min).**
A mais barata de todas e vale sempre fazer se perguntarem: se o voto majoritário acertou, então a
resposta certa apareceu ao menos uma vez; logo o evento do consenso está contido no evento do
`pass`; logo a probabilidade é menor ou igual. Uma linha. O que **não** cabe no quadro é a análise
assintótica, e é ela que está em A.2.

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 15 da Parte 1 — a síntese das três formas de sinal
de pós-treino do Módulo 4 (imitação na Aula 13, preferência humana na Aula 15, verificação
automática hoje), o critério "existe verificador para a sua tarefa?" como pergunta a levar para o
projeto final, o **aviso e o roteiro de estudo da Prova da Aula 17 com o novo perfil de pontuação**,
e a leitura de DeepSeek-AI, *DeepSeek-R1* (arXiv 2501.12948) com a pergunta dirigida.

> 🗣️ "Semana que vem não tem aula nova: tem prova, das Aulas 1 a 16. E o perfil mudou — quarenta e cinco pontos de diagnóstico, trinta de justificativa, e derivação vale um item. Quem estudou refazendo os diagnósticos está em vantagem sobre quem estudou decorando fórmula."

---

*Roteiro do Instrutor · Aula 16 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
