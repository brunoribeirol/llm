# Laboratório 4: Fine-tuning com LoRA/QLoRA

## Slide 1 · Abertura: ontem a conta, hoje o adaptador · 00:00–00:05

Bom dia, pessoal. Ontem eu escrevi um número no quadro e hoje esse número vai aparecer na tela de vocês.

Deixa eu recuperar. Ontem eu contei que uma projeção de mil quinhentos e trinta e seis por mil quinhentos e trinta e seis tem dois milhões e trezentos mil pesos, e que o adaptador dela com posto oito tem vinte e quatro mil quinhentos e setenta e seis. Somei os sete módulos de uma camada, multipliquei pelas vinte e oito camadas, e cheguei em nove milhões duzentos e trinta e dois mil trezentos e oitenta e quatro. Zero vírgula sessenta por cento de um modelo de um vírgula cinco bilhão.

Hoje vocês vão chamar uma função da biblioteca que imprime exatamente essa porcentagem. E eu quero que vocês confiram — não que vocês aceitem. Porque um `print` que a pessoa não sabe reproduzir não é conhecimento, é fé.

E tem uma segunda coisa que eu quero de vocês hoje, que fecha um laço de duas semanas. No Lab 3, vocês mediram uma tarefa de classificação em duas colunas: acerto de categoria e taxa de resposta **fora do espaço de rótulos**. E vocês descobriram que o few-shot mexeu muito mais na segunda coluna do que na primeira, e reportaram isso honestamente. Hoje vocês vão atacar aquela segunda coluna com fine-tuning, com cem exemplos, e ver o que acontece com ela.

E o que vai acontecer com a **primeira** coluna é a parte mais interessante do lab. Eu não vou estragar a surpresa.

> Ideia central: "Ontem o número estava no quadro. Hoje ele vai estar na tela de vocês — e eu quero que vocês confiram a conta, não que aceitem o `print`."

## Slide 2 · Os dois perfis e os números esperados · 00:05–00:11

Antes de qualquer coisa, o setup — e este notebook tem duas configurações, não uma.

Perfil `gpu`: quem tem GPU no Colab. Modelo de um vírgula cinco bilhão de parâmetros, aberto, licença permissiva, sem necessidade de token. Base quantizada em quatro bits NF4. Noventa passos de treino, comprimento máximo de trezentos e vinte tokens, lote físico um com acumulação de quatro.

Perfil `cpu`: quem não tem GPU. Modelo da **mesma família**, muito menor — e eu escolhi a mesma família de propósito, porque o template de chat é o mesmo e nada do que vocês vão aprender muda. Menos passos, sequência mais curta, sem quantização.

E agora a parte que eu preciso que seja ouvida com clareza: o perfil de CPU **fecha os cinco checkpoints** e produz um resultado **ilustrativo**. Ele é honesto e ele é pequeno. O notebook imprime um aviso quando entra nesse modo, e o campo de proveniência registra qual perfil produziu cada número. Vocês já sabem por que eu insisto nisso — foi a lição de método do Lab 3.

**[Rodo a célula de diagnóstico e aponto o bloco de números esperados]**

Este bloco aqui é o **contrato do lab**. Memória dos pesos na ordem de um gibibyte. Pico de treino entre dois e cinco. Tempo de treino de quatro a dez minutos. Adaptador de vinte a quarenta megabytes. Eu rodei tudo ontem na GPU desta oferta para ter esses valores. Se o número de vocês estiver muito longe, tem alguma coisa errada e é melhor me chamar do que insistir.

E uma nota sobre memória que é conteúdo, não setup. Quando vocês imprimirem a memória dos pesos, o número vai ser **maior** do que um vírgula cinco bilhão vezes meio byte, que dá zero vírgula sete gibibyte. Isso não é bug. A quantização não comprime a tabela de embeddings, e esse modelo tem vocabulário de cento e cinquenta e dois mil tokens — o embedding sozinho tem duzentos e trinta e três milhões de parâmetros, e eles custam dois bytes cada em vez de meio. São trezentos e cinquenta megabytes de diferença, e eles têm nome: é a Aula 2 voltando com fatura de VRAM. O tamanho do vocabulário é decisão de tokenizador, e ela se paga em memória de GPU.

> Ideia central: "O perfil de CPU fecha os cinco checkpoints e produz um resultado ilustrativo. As duas coisas são verdade, e as duas vão no campo de proveniência."

## Slide 3 · O mapa: cinco checkpoints e o entregável · 00:11–00:15

Quatro minutos de mapa e eu solto vocês. E eu vou apresentar cada checkpoint **pelo que a tela imprime quando está certo**, porque é assim que vocês vão saber que terminaram.

Checkpoint 1, até dez para as onze: carregar o modelo em quatro bits e capturar a linha de base. A tela imprime três linhas de memória — corpo, embedding, total —, a conta ingênua marcada como não explicando o total, e depois `Checkpoint 1 OK`. Cinco prompts da tarefa e três de controle guardados.

E deixa eu explicar os três de controle, porque eles não são enfeite. Eles são uma multiplicação, uma tradução curta e uma pergunta factual — coisas que não têm nada a ver com a tarefa que vocês vão treinar. Eles estão lá porque ontem eu falei de esquecimento catastrófico e eu disse que ele é invisível para quem mede só na tarefa-alvo. Hoje vocês vão ter o instrumento para ver.

Checkpoint 2: a tela imprime a string formatada em `repr`, com os tokens de papel visíveis, mais a linha de comprimentos em tokens, mais `Checkpoint 2 OK`. Cem exemplos embutidos, formatados, divididos em oitenta e oito e doze.

Checkpoint 3: a tela imprime `treináveis: nove milhões duzentos e trinta e dois mil trezentos e oitenta e quatro`, a minha conta ao lado da conta da biblioteca, e a diferença em porcentagem. É o checkpoint mais curto e o mais importante.

Checkpoint 4: a tela mostra um gráfico com **duas** curvas, mais pico de memória e tempo.

Checkpoint 5: a tela mostra duas tabelas e o tamanho do adaptador em megabytes, mais `idênticas: True` no recarregamento.

O entregável é o notebook executado mais o **adaptador salvo**. Este é o primeiro lab do curso em que vocês entregam um modelo — pequeno, de dezenas de megabytes, mas um modelo.

**[Aponto a coluna cinza com os `A.n`]**

Essa coluninha do lado é ponteiro de estudo, não tarefa de hoje. Cada número que hoje aparece na tela tem um item de apêndice com a conta por trás dele. Ninguém precisa disso agora — e a questão-guia cinco, que é a que mais separa nota, é literalmente o A.3.

> Ideia central: "Cinco checkpoints, e este é o primeiro lab em que vocês entregam um modelo. Dezenas de megabytes que mudam o comportamento de um arquivo de gigabytes."

## Slide 4 · [Demo] O caminho completo em miniatura · 00:15–00:35

Vinte minutos agora comigo escrevendo e vocês olhando. Depois eu solto.

Eu vou percorrer o caminho inteiro em miniatura: carregar, medir, gerar uma vez, formatar um exemplo, configurar o LoRA, e dar **um** passo de treino. No fim desses vinte minutos vocês vão ter visto cada peça funcionando isolada — e, o mais importante, vão ter visto a porcentagem de treináveis aparecer na tela ao lado da conta de ontem no quadro.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> Ideia central: "Eu vou percorrer o caminho inteiro em miniatura e parar antes do laço de treino. O laço é de vocês."

## Slide 5 · [Checkpoint 1] Carregar em 4 bits e capturar a linha de base · 00:35–00:50

Quinze minutos, e é de vocês.

**[Projeto o critério de conclusão antes de qualquer coisa]**

Quando estiver certo, a tela imprime três linhas de memória e depois `Checkpoint 1 OK`. E para imprimir isso, o teste vai ter conferido quatro coisas — eu vou ler as quatro, porque cada uma aponta para um erro que o Python aceita sem reclamar.

Um: existe parâmetro de quatro bits no modelo. Se não existir, a `BitsAndBytesConfig` não foi aplicada.

Dois: a memória dos pesos está entre zero vírgula seis e dois gibibytes.

Três: a função `responder` é **determinística** — duas chamadas seguidas devolvem a mesma string — e ela não devolve o prompt de volta.

Quatro: o dicionário `ANTES` tem oito respostas não vazias.

**[Aponto os dois TODOs]**

O primeiro é a `BitsAndBytesConfig`: quatro bits, tipo NF4, dupla quantização, e o `compute_dtype`. O nome desse último parâmetro diz tudo: o peso está **armazenado** em quatro bits e o **cálculo** acontece em dezesseis, o que é literalmente a distinção que eu fiz ontem no slide de quantização.

E aqui tem uma pegadinha de hardware que é conteúdo, não detalhe. Ontem eu disse que bf16 virou o padrão porque tem a mesma faixa do fp32 e dispensa loss scaling. Verdade — e bf16 só existe a partir da arquitetura Ampere. A T4 que o Colab gratuito entrega é Turing, e não tem bf16. Então o notebook não fixa nada: ele pergunta à placa, com `is_bf16_supported`, e define uma constante. Quem fixar `bfloat16` no código porque foi o que eu recomendei em aula vai descobrir, do jeito difícil, que "o padrão da área" e "o que a sua máquina tem" são duas coisas diferentes.

O segundo TODO é a função `responder`, com três exigências que valem nota: aplicar o template de chat — não montar string à mão; gerar de forma determinística; e decodificar **só os tokens novos**.

O determinismo não é preciosismo. Se vocês amostrarem, a comparação antes × depois vai misturar efeito de treino com efeito de sorteio, e vocês não vão conseguir separar os dois. Vocês já viveram isso no Lab 3, quando greedy repetido três vezes deu a mesma saída e amostragem não.

E aí vocês rodam os oito prompts no modelo **base** e guardam tudo. Depois do treino, o modelo antigo não existe mais nesta sessão. O que vocês não capturarem agora, vocês perderam.

*[A condução completa está na Parte 3 deste roteiro.]*

> Ideia central: "Depois do treino, o modelo de antes não existe mais nesta sessão. O que vocês não capturarem agora, vocês perderam."

## Slide 6 · [Checkpoint 2] Dataset e template de chat · 00:50–01:05

Quinze minutos no Checkpoint 2.

**[Projeto o critério]**

Quando estiver certo, a tela imprime a string formatada em `repr` — com as barras `n` aparecendo, porque eu quero que vocês vejam a estrutura — mais a linha de comprimentos em tokens, mín, mediana e máx, e depois `Checkpoint 2 OK`. O teste confere cinco coisas: cem textos não vazios; a divisão somando cem; os delimitadores de turno presentes; os três papéis presentes; e — esta é a que interessa — **nenhum** exemplo atingindo o comprimento máximo.

Essa última é importante e eu quero explicar por quê. Se um exemplo é truncado, a resposta é cortada no meio, e o modelo aprende a parar no lugar errado. E o comprimento máximo de trezentos e vinte tokens foi escolhido olhando o histograma deste conjunto, não a placa. A placa aguentaria muito mais — está em A.1, e é uma coisa que surpreende.

Cem exemplos de instrução em português, embutidos no notebook. Comentário de aplicativo na entrada; na saída, duas linhas: `Categoria:` com uma das quatro palavras, e `Resposta:` com uma ou duas frases de atendimento. As quatro categorias são as mesmas do Lab 3 — bug, dúvida, elogio e recurso — e isso é de propósito.

Por que embutido e não baixado? Duas razões. Uma prática: rede de sala não é confiável, e vocês já sabem disso. E uma pedagógica, que é a que importa: eu quero que vocês **leiam** o dado. São cem exemplos, cabem numa tela de rolagem. Nenhum de vocês vai passar a carreira treinando em dataset que outra pessoa curou, e a primeira coisa que se faz com dado de treino é ler ele.

E o `print` do exemplo formatado é o coração do checkpoint. Eu quero que vocês vejam, com o olho, os tokens de papel e o token de fim de turno na string. Porque o erro que eu mais vi em fine-tuning de aluno é montar a string à mão com "Usuário dois-pontos, Assistente dois-pontos", treinar bonito, e depois avaliar chamando pelo template oficial. Aí o adaptador aprendeu a responder a um prompt que nunca vai chegar, e a comparação sai **pior** que o modelo base. Sem erro, sem aviso, sem exceção.

*[A condução completa está na Parte 3 deste roteiro.]*

> Ideia central: "Cem exemplos cabem numa tela. Eu quero que vocês leiam o dado — e que vejam os tokens de papel com o olho antes de treinar em cima deles."

*Intervalo · 01:05–01:15*

## Slide 7 · [Checkpoint 3] LoRA e a conta dos treináveis · 01:15–01:25

Voltando do intervalo. Dez minutos, e este é o checkpoint que vale a aula.

**[Projeto o critério, que aqui são quatro linhas de número]**

Quando estiver certo, a tela imprime: `módulos LoRA criados: cento e noventa e seis`, esperado sete vezes vinte e oito; depois a linha `por camada`, a linha `x camadas` marcada como **minha conta**, a linha `biblioteca` marcada como o que o PEFT reporta, e a `diferença` em porcentagem. E aí `Checkpoint 3 OK`.

Eu quero aquela linha de diferença em zero por cento na tela de todo mundo. Ela é o checkpoint.

**[Aponto os campos da configuração]**

Vocês preenchem a `LoraConfig`: posto oito, alfa dezesseis, dropout pequeno, os sete módulos-alvo pelos nomes, e o tipo de tarefa. Depois `prepare_model_for_kbit_training`, **antes** de `get_peft_model`. Depois `print_trainable_parameters`.

Uma armadilha que eu quero anunciar antes de vocês caírem nela, porque ela é silenciosa e cara: se vocês escreverem um nome errado em `target_modules`, **nada acontece**. Nenhum erro. A biblioteca simplesmente não encontra o módulo e não cria adaptador ali. Vocês treinam meia hora e treinam menos do que pensam, ou nada. O teste confere que o número de adaptadores criados é sete vezes o número de camadas, exatamente para pegar isso.

E aí vem a segunda célula, que é a razão de existir deste checkpoint. Vocês vão **recalcular** o número à mão, no código, lendo as dimensões do `model.config` — não copiando do quadro. Dimensão do modelo, dimensão das projeções de chave e valor, dimensão intermediária, número de camadas. Aplicar posto vezes a soma de entrada mais saída em cada módulo, somar, multiplicar pelas camadas.

E comparar com o que a biblioteca imprimiu. Se bater, vocês entenderam LoRA. Se não bater, vocês descobriram alguma coisa — e as duas possibilidades são boas, porque as duas terminam com vocês sabendo de onde vem o número.

*[A condução completa está na Parte 3 deste roteiro.]*

> Ideia central: "Nome errado em `target_modules` não dá erro. Ele silenciosamente não cria adaptador — e vocês treinam meia hora treinando nada."

## Slide 8 · [Checkpoint 4] Treinar e registrar · 01:25–01:38

Treze minutos. Agora treina.

**[Projeto o critério, que aqui é um gráfico e quatro linhas]**

Quando estiver certo, vocês vão ter um gráfico com **duas** curvas no mesmo eixo — treino e validação —, as duas listas de perda impressas abaixo dele, e quatro linhas: passos, tempo total, pico de memória e perda final. E `Checkpoint 4 OK`.

O teste confere quatro coisas: que o histórico tem pelo menos dois pontos; que a perda final é **menor** que a inicial; que existe perda de validação registrada; e que o pico foi medido com `max_memory_allocated` e não com `memory_allocated`, porque um é o pico e o outro é um instante.

**[Aponto os três interruptores no bloco de configuração]**

E tem três interruptores nessa configuração que eu expliquei em aula e que agora vocês vão ligar de verdade.

`gradient_accumulation_steps` igual a quatro: lote físico de um, lote efetivo de quatro. É como ter lote maior sem ter memória para lote maior — e o detalhe bonito é que a acumulação **não** multiplica a memória de ativações, porque cada micro-lote é liberado antes do próximo.

`gradient_checkpointing` ligado: recomputação de ativações. É exatamente aquilo da Aula 12 — em vez de guardar as ativações intermediárias para o backward, guarda pouco e recalcula. Custa uns trinta por cento de tempo e devolve memória.

E `use_cache` desligado no `config` do modelo. O KV cache serve para geração, não para treino. Se vocês esquecerem, a biblioteca avisa — e o aviso é para ler, não para rolar para baixo.

E agora eu quero cravar uma coisa sobre a curva, porque ontem eu falei disso e hoje vocês vão ver.

A perda de **treino** cair não é evidência de nada. É o que ela faz. É a função dela. O teste exige que ela caia, e o que essa exigência estabelece é só uma coisa: que o gradiente está chegando ao adaptador. É um diagnóstico de encanamento.

E tem uma razão específica, deste notebook, para a curva ser ainda menos informativa do que vocês esperariam — e ela está no A.2, com conta. A perda é calculada sobre a sequência **inteira**, e a sequência inclui o prompt de sistema, que é **idêntico** nos cem exemplos. Aprender a prever uma constante que se viu trezentas e sessenta vezes é a coisa mais fácil que existe, e move a perda muito. O A.2 mostra que uma queda de quase metade da perda é compatível com **zero** melhoria na parte que interessa.

Então o sinal está na perda de **validação** — e mesmo ela não captura tudo, porque um modelo que devolve resposta decorada palavra por palavra pode ter validação aceitável. É por isso que o próximo checkpoint pede leitura com o olho.

> Ideia central: "A perda de treino cair é o que ela faz. O que ela prova é que o gradiente chegou no adaptador — e não muito mais que isso."

## Slide 9 · [Checkpoint 5] Antes × depois, controle e o adaptador · 01:38–01:50

Doze minutos, e é agora que o lab paga.

**[Projeto o critério, que aqui são duas tabelas e duas linhas]**

Quando estiver certo, a tela mostra: a tabela antes × depois com **duas** colunas e quatro números; a tabela de controle com os três prompts fora do domínio, antes e depois; o `TOTAL do adaptador` em megabytes; e `idênticas: True` na comparação entre o modelo em memória e o recarregado. E `Checkpoint 5 OK`.

O teste confere que `DEPOIS` tem oito respostas, que a aderência ao formato **subiu**, que o diretório do adaptador existe e tem menos de duzentos megabytes com arquivo `adapter_`, e que a saída recarregada bate com a de memória.

Três coisas para fazer.

Primeira: os mesmos cinco prompts, no modelo adaptado, e a tabela lado a lado com duas colunas. Acerto de categoria e aderência ao formato. Duas colunas, não uma — mesma disciplina do Lab 3.

E eu tenho uma aposta sobre o resultado de vocês, e eu quero que vocês confirmem ou desmintam com o dado de vocês. Aposta: a coluna de **formato** vai melhorar muito, provavelmente para cinco de cinco. E a coluna de **acerto de categoria** vai melhorar pouco, ou nada.

Se isso acontecer, não é falha. É o resultado, e é o resultado mais importante do lab. Porque ele diz, com número de vocês, aquilo que eu afirmei ontem: cem exemplos e zero vírgula seis por cento dos parâmetros movem **forma**, não movem **capacidade**.

E agora eu preciso adiantar uma coisa que vai no relatório de vocês, porque é o erro de método que eu mais vejo neste lab. Se o acerto de vocês foi de três em cinco para quatro em cinco, isso são vinte pontos percentuais — e vinte pontos com cinco prompts é **um prompt mudando de lado**. Com cinco itens, a menor diferença que existe é vinte pontos, e o A.3 mostra uma coisa desconfortável: mesmo que **todos os cinco** prompts mudassem de errado para certo, o resultado ainda não seria distinguível do acaso.

Então: a mudança de formato vocês podem afirmar, porque ela é categórica e verificável por leitura — a saída passou de prosa a esquema, em todos os casos. A melhoria de acurácia vocês **não** podem afirmar. As duas frases são diferentes, e escrever as duas certo é o que separa nota na questão-guia cinco.

Segunda coisa: os três prompts de controle. A multiplicação, a tradução, a pergunta factual. Rodar no modelo adaptado e comparar com o que vocês guardaram. Se alguma coisa piorou, vocês acabaram de medir esquecimento — e com LoRA isso é menos provável, porque a base está congelada, mas menos provável não é impossível. E o notebook imprime, junto, que a verificação por substring é grosseira **de propósito**: é para vocês lerem as três respostas, não para confiarem no `ok`.

Terceira: salvar o adaptador. `save_pretrained` no modelo **PEFT**, não no base — quem errar isso vai gravar gigabytes e descobrir na hora do upload. Imprimir o tamanho em megabytes. E depois recarregar: base pública mais o diretório pequeno, num objeto novo, e conferir que a saída se reproduz.

Esse último passo é a prova de que o artefato é real e portátil. O modelo base é público e está no Hugging Face. O que é **de vocês** são as dezenas de megabytes que vocês acabaram de treinar.

> Ideia central: "Minha aposta: a coluna de formato vai a cinco de cinco e a coluna de acerto quase não mexe. Se isso acontecer, escrevam isso — é o achado, não a falha."

## Slide 10 · Recolhimento: o que entregar, a Aula 15 e a prova · 01:50–02:00

Deixa eu fechar.

O que vocês têm agora: um modelo aberto de um vírgula cinco bilhão de parâmetros rodando quantizado no Colab gratuito; uma linha de base capturada antes de qualquer treino; cem exemplos que vocês leram, formatados no template oficial; uma configuração LoRA com nove milhões de parâmetros treináveis que vocês conferiram à mão; uma curva de treino e validação; uma comparação antes e depois em duas colunas; um teste de esquecimento; e um adaptador de dezenas de megabytes que vocês salvaram e recarregaram.

A entrega, em uma semana: notebook executado com as saídas visíveis, o adaptador salvo, as duas tabelas do Checkpoint 5, o campo de proveniência preenchido, as respostas das cinco questões-guia e a declaração de uso de IA. Proveniência incompleta zera aquele item — vocês já conhecem essa regra.

**[Projeto o índice do apêndice por 20 s]**

Três itens, um por número que hoje apareceu na tela. E eu nomeio um: o **A.3**. Ele responde a questão-guia cinco, que é a que pergunta o que os números de vocês **não** provam. E ele é o terceiro de quatro itens deste curso que fazem a mesma pergunta: no Lab 2 o ruído vinha da semente; no Lab 3, de quais vinte comentários caíram no notebook; hoje, de quais cinco prompts eu escolhi; e no Lab 8 vocês vão ver o tratamento completo, com intervalo de Wilson e teste de McNemar, sobre o conjunto de teste do projeto de vocês. Quem seguir os quatro na ordem vê a mesma ideia crescendo de uma semente até uma decisão de produto.

Agora a ponte, e ela é uma virada de objetivo.

Nestas duas aulas a gente ensinou o modelo a **imitar bons exemplos**. Foi isso e só isso: cem pares de instrução e resposta, e o modelo aprendeu a se parecer com eles. Funciona muito bem para forma.

Mas olhem o que essa abordagem não consegue fazer, por construção. Imitar bons exemplos ensina o que **fazer**. Ela não ensina o que **evitar** — porque o que se deve evitar não está nos exemplos bons, e não caberia: o espaço de respostas ruins é infinito. E ela também não sabe dizer que, entre duas respostas aceitáveis, uma é melhor que a outra. O rótulo é binário: este exemplo é bom, e ponto.

Semana que vem a gente resolve isso trocando o tipo de sinal. Em vez de "esta é a resposta boa", o sinal passa a ser "esta resposta é **melhor** que aquela" — comparação, preferência humana. E aí aparece um aparato inteiro: modelo de recompensa, RLHF, PPO, e uma alternativa mais simples que virou padrão prático, que é o DPO. Aula 15: alinhamento.

E o último aviso, que eu quero dado agora e não depois. A **prova é na Aula 17**, individual, escrita, sem uso de IA, e ela cobre da Aula 1 à Aula 16. Isso inclui tudo o que a gente fez neste módulo: a conta `C ≈ 6ND`, a alocação compute-optimal, os dezesseis bytes por parâmetro, os três paralelismos, por que FlashAttention é exata, a conta do LoRA que vocês acabaram de conferir, e o framework prompting × RAG × fine-tuning. São duas aulas até lá: a 15 e a 16. Depois, prova.

> Ideia central: "Vocês ensinaram o modelo a imitar bons exemplos. Isso ensina o que fazer e não ensina o que evitar — e é por isso que existe a Aula 15."

---

## Parte 2 — Demonstração guiada

Vinte minutos de live coding no meu Colab, com GPU e o modelo já em cache. O objetivo não é adiantar os checkpoints — é fazer a turma ver cada peça funcionando isolada antes de encadeá-las, e ver a porcentagem de treináveis aparecer na tela ao lado da conta de ontem no quadro.

Insumos da véspera: o notebook rodado de ponta a ponta na GPU da oferta, com **memória de pico e tempo real anotados**; o notebook rodado também no perfil de CPU, para eu saber quanto tempo o fallback leva de verdade; um adaptador já treinado e salvo no meu Drive, para o caso de alguém não conseguir treinar e precisar seguir para o Checkpoint 5.

**1.** **[Rodo a célula de diagnóstico e projeto a saída]** Primeira célula: ela me diz se tem GPU, qual é, e quanta memória. Olha o que ela imprimiu — o perfil escolhido, o `compute_dtype`, e o bloco de números esperados. Nada aqui é decorativo: esses números são o contrato do lab.

**2.** **[Carrego o modelo com `BitsAndBytesConfig` de 4 bits e imprimo a memória alocada]** Agora eu carrego. Quatro bits, tipo NF4, dupla quantização, cálculo em dezesseis — os quatro parâmetros que eu expliquei ontem, agora como código. Rodo, e olha a memória alocada.

**3.** **[Decomponho a memória na tela: corpo em 4 bits, embedding em 16 bits, total]** E eu quero explicar esse número, porque ele não é o que a conta ingênua dá. Um vírgula cinco bilhão de parâmetros a meio byte daria zero vírgula sete gibibyte, e o que apareceu é mais de um. A diferença é o embedding: a quantização não comprime a tabela de embeddings, e esse modelo tem vocabulário de cento e cinquenta e dois mil tokens. Duzentos e trinta e três milhões de parâmetros a dois bytes cada, quase meio gibibyte, que não encolhe. Trezentos e vinte e seis mebibytes de diferença atribuídos a uma decisão de tokenizador — é a Aula 2 chegando com fatura de VRAM.

**4.** **[Escrevo a função `responder` na frente da turma]** Agora eu escrevo a função de geração, na mão, porque cada linha dela é conceito. Monta as mensagens com papel. Aplica o template — não concatena string. Gera com `do_sample` falso, ou seja, determinístico. E decodifica **só** os tokens novos, cortando o prompt. Se eu amostrasse aqui, a comparação antes × depois ia misturar efeito de treino com efeito de sorteio, e eu não conseguiria separar os dois. Vocês viveram isso no Lab 3.

**5.** **[Rodo um dos cinco prompts de teste no modelo base e leio a resposta em voz alta]** Vou rodar um dos prompts de teste no modelo **base**, sem treino nenhum. Olha a resposta. Ele entendeu perfeitamente o pedido — e respondeu em prosa, do jeito dele, fora do formato que eu quero. Isso não é o modelo sendo ruim. É o modelo respondendo como ele aprendeu no SFT dele, que não é o meu SFT. E é exatamente a coluna dois do Lab 3 aparecendo de novo.

**6.** **[Pego um exemplo do conjunto embutido e imprimo `apply_chat_template(..., tokenize=False)`]** Agora um exemplo do conjunto de treino, formatado. Olha a string. Aqui está o token que abre o turno do sistema. Aqui o do usuário. Aqui o do assistente — o "sua vez". E aqui o de fim de turno. Isso é o que o modelo vai ver noventa vezes durante o treino, e é o que ele precisa ver na hora da avaliação, senão vocês treinaram para um prompt que não vai chegar. E olhem o tamanho do bloco de sistema em relação ao resto: guardem essa proporção, porque ela volta no Checkpoint 4.

**7.** **[Monto a `LoraConfig`, chamo `get_peft_model` e `print_trainable_parameters()`]** Agora o momento da aula. Posto oito, alfa dezesseis, sete módulos-alvo. Chamo, e imprimo. Olha o número. Nove milhões duzentos e trinta e dois mil trezentos e oitenta e quatro. Zero vírgula sessenta por cento.

**8.** **[Vou ao quadro e escrevo a conta de ontem ao lado do número da tela]** E aqui, no quadro, eu escrevo a conta de ontem: trezentos e vinte e nove mil setecentos e vinte e oito por camada, vezes vinte e oito. Nove milhões duzentos e trinta e dois mil trezentos e oitenta e quatro. As duas coisas na mesma sala, ao mesmo tempo. A biblioteca não fez mágica — ela fez a conta que a gente fez.

**9.** **[Rodo um único passo de treino e mostro a perda]** Último passo da demo: um lote, um passo, e a perda. Esse número absoluto não diz nada — não tem com o que comparar. O que vai dizer alguma coisa é a curva dos noventa passos, e essa curva é o Checkpoint 4 e é de vocês.

**10.** **[Apago as células da demo]** E eu apago tudo o que eu escrevi, porque os TODOs continuam sendo de vocês.

---

## Parte 3 — Hands-on

Cinco checkpoints. Eu circulo olhando tela, não esperando pergunta — neste lab o erro típico não estoura exceção. Nome errado em `target_modules` não dá erro; decodificar a sequência inteira em vez dos tokens novos não dá erro; montar o prompt à mão em vez do template não dá erro. Os três produzem resultado plausível e errado, e quem está com eles não levanta a mão porque não sabe.

**1.** **[Lanço o Checkpoint 1 — carregar em 4 bits e capturar a linha de base, até 00:50]** Quinze minutos. O critério é as três linhas de memória decomposta na tela e depois `Checkpoint 1 OK`. Dois TODOs — a configuração de quantização e a função `responder` — e depois os oito prompts no modelo base, guardados em `ANTES`.

**2.** **[Lanço o Checkpoint 2 — dataset e template de chat, até 01:05]** Quinze minutos. O critério é a string formatada em `repr` na tela, com os tokens de papel visíveis, mais a linha de comprimentos, mais `Checkpoint 2 OK`. Antes de codificar, eu peço dois minutos de leitura do dado: rolar os cem exemplos e ver o que eles ensinam.

**3.** **[Lanço o Checkpoint 3 — LoRA e a conta, até 01:25]** Dez minutos, e é o checkpoint mais importante. O critério é a linha `diferença: 0.00%` na tela, com `196` módulos LoRA criados e a fração abaixo de um por cento.

**4.** **[Lanço o Checkpoint 4 — treinar e registrar, até 01:38]** Treze minutos. O critério é um gráfico com **duas** curvas, as duas listas de perda impressas, e as quatro linhas de número. Enquanto treina, a sala fica em silêncio e eu circulo.

**5.** **[Lanço o Checkpoint 5 — antes × depois, controle e adaptador, até 01:50]** Doze minutos. O critério são as duas tabelas na tela, o tamanho do adaptador em megabytes, o `idênticas: True`, e `Checkpoint 5 OK`.

---

## Parte 4 — Apêndice: se perguntarem

Em laboratório eu **não conduzo derivação no quadro** — o tempo é do teclado. O que esta parte traz são as respostas de trinta segundos, mais o que fazer se a pergunta for boa demais para despachar.

**Item 1 — "Por que a memória é maior que um vírgula cinco bilhão vezes meio byte?" (A.1, 30 s).**
A pergunta mais provável do lab, e ela vem do próprio `print`. **Resposta curta:** "porque a quantização não comprime a tabela de embeddings. Esse modelo tem vocabulário de cento e cinquenta e dois mil tokens, o que dá duzentos e trinta e três milhões de parâmetros, e eles custam dois bytes cada em vez de meio — trezentos e cinquenta megabytes de diferença. O tamanho do vocabulário é decisão de tokenizador, e ela se paga em VRAM." Se insistirem, o orçamento inteiro da placa, decomposto em cinco parcelas, está em A.1. **Não** conduzir no quadro.

**Item 2 — "Se cabe tanta folga na placa, por que o `r` é oito?" (A.1, 30 s).**
A melhor pergunta que esse lab pode receber, e ela é rara. **Resposta curta:** "porque `r` não é a restrição de memória. A tabela do A.1 mostra que a placa aguentaria `r` igual a duzentos e cinquenta e seis com folga. O oito foi escolhido pelo **dado**: com oitenta e oito exemplos de treino, mais capacidade no delta é mais chance de decorar o conjunto sem melhorar o comportamento." Se sobrar tempo, essa é a única do lab que vale trinta segundos extras, porque ela desfaz a suposição de que todo hiperparâmetro é escolhido por hardware.

**Item 3 — "Minha perda caiu pela metade, isso é bom?" (A.2, 30 s).**
Aparece no Checkpoint 4 e é uma pergunta honesta. **Resposta curta:** "cair é o que ela faz, e o que a queda prova é que o gradiente chegou no adaptador. E tem um detalhe deste notebook: a perda é calculada sobre a sequência inteira, e metade dela é o prompt de sistema, que é **idêntico** nos cem exemplos. O A.2 mostra com conta que uma queda de quase metade é compatível com zero melhoria na resposta. O que mede a resposta é o Checkpoint 5, não a curva."

**Item 4 — "Por que a validação está abaixo do treino?" (A.2, 20 s).**
**Resposta curta:** "porque o dropout está ligado no treino e desligado na avaliação, e porque doze exemplos de validação podem ser mais fáceis que a média. Não é paradoxo nem erro. Está nos casos-limite do A.2."

**Item 5 — "Meu acerto foi de três em cinco para quatro em cinco. Melhorou?" (A.3, 30 s — e vale fazer na frente da sala).**
A pergunta que eu **quero** que apareça, porque ela é a questão-guia cinco chegando sozinha. **Resposta curta, feita em voz alta para todos:** "com cinco prompts, a menor diferença que existe é vinte pontos percentuais — então isso é **um** prompt mudando de lado. E o A.3 mostra uma coisa mais forte: mesmo que os cinco mudassem de errado para certo, o `p`-valor seria zero vírgula zero seis, ainda acima de cinco por cento. Nenhum resultado possível deste conjunto é significativo em acurácia. O que vocês **podem** afirmar é a mudança de formato, porque ela é categórica e verificável por leitura. As duas frases são diferentes, e escrever as duas certo é a questão-guia cinco."

**Item 6 — "Então de quantos prompts eu precisaria?" (A.3, 20 s).**
**Resposta curta:** "para precisão de mais ou menos dez pontos, da ordem de oitenta itens; para cinco pontos, trezentos e vinte e três. A fórmula é a mesma do A.3 do Lab 3 e a conta está no A.3 de hoje. E o tratamento completo, com intervalo de Wilson e teste de McNemar, é o A.5 do Lab 8 — daqui a catorze aulas, sobre o conjunto de teste do projeto de vocês."

---

## Recolhimento · 01:50–02:00

O recolhimento está redigido como fala no Slide 10 da Parte 1 — o inventário do que a turma construiu, o checklist de entrega com prazo de uma semana e a exigência de proveniência, os vinte segundos de índice do apêndice nomeando o A.3 e situando ele como terceiro elo do fio Lab 2 → Lab 3 → Lab 4 → Lab 8, a ponte para a Aula 15 pela limitação estrutural da imitação de bons exemplos, e o aviso de que a prova é na Aula 17 e cobre as Aulas 1 a 16.

> Ideia central: "Vocês treinaram um modelo a imitar bons exemplos e conferiram a conta que faz isso caber. Semana que vem o sinal muda de 'esta é a resposta boa' para 'esta é melhor que aquela' — e é aí que nasce o alinhamento. E daqui a duas aulas tem prova, cobrindo tudo da Aula 1 à 16."

---

*Roteiro do Instrutor · Aula 14 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
