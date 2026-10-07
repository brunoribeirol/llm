---
aula: 13
titulo: "SFT e fine-tuning eficiente: LoRA e QLoRA"
tipo: teorica
duracao_min: 120
versao: v2
---

# Roteiro do Instrutor — Aula 13 de 30 (V2)

## Como usar este roteiro

A prosa deste documento é **fala em primeira pessoa**: é o que eu digo em sala, na ordem em que digo. Não é resumo do conteúdo — é o texto falado. Posso ler quase literalmente ou usar como trilho e improvisar em cima.

As linhas marcadas com 🗣️ são as **frases-âncora**: as que eu cravo, quase palavra por palavra, porque mudam o ritmo ou fecham um ponto. Cada slide tem uma.

As notas marcadas com **Bastidor** são operacionais e **não são faladas em voz alta** — são lembretes do que abrir na tela, onde a turma costuma travar, o que responder se alguém perguntar algo específico. Nesta aula elas guardam duas coisas em especial: a aritmética do LoRA, que eu não posso errar no quadro, e o momento em que alguém vai propor consertar alucinação com fine-tuning — que é o ponto pedagógico mais valioso do dia.

> **O que muda nesta versão.** A aula é conduzida por **três sintomas** que eu projeto juntos no primeiro slide e vou fechando um por um: o modelo que continua a lista, o treino que não cabe na placa, e o modelo que esqueceu o que sabia. As fórmulas aparecem enunciadas e lidas; eu **não** derivo no quadro e **não** somo os sete módulos ao vivo — a soma está no slide e a derivação está no apêndice do deck (A.1 a A.5). Se a turma pedir, a **Parte 4** deste roteiro tem as quatro conduções prontas, com o custo em minutos de cada uma e a versão de trinta segundos.

---

## Parte 1 — Roteiro de fala, slide a slide

### Slide 1 · Abertura: três sintomas, e nenhum deles é bug · 00:00–00:05

Bom dia, pessoal. Ontem a gente entrou na fábrica, e eu fechei a aula com uma frase incômoda: tudo aquilo — o cheque de nove dígitos, os trilhões de tokens, os cento e quatro gibibytes de estado — entrega uma máquina que **continua texto**.

Hoje eu quero começar por três coisas que acontecem de verdade. Estão os três no slide.

A primeira: eu pergunto "qual a capital da França?" e o modelo responde "…e a capital da Itália? Qual a capital da Alemanha?". Ele continua a lista.

A segunda: eu tento fazer fine-tuning de um modelo de sete bilhões numa placa de vinte e quatro gigabytes, e estoura a memória. E os pesos desse modelo ocupam catorze gigabytes. Ou seja: cabe o modelo, não cabe o treino.

A terceira, e é a mais desconfortável: eu ajusto um modelo, ele passa a acertar o formato em cem por cento dos casos, e passa a errar uma conta de somar que antes ele acertava. E a curva de perda do treino continua descendo bonito, do começo ao fim.

Nenhum dos três levanta exceção. Nenhum dos três é bug. Os três são a consequência correta de uma decisão que alguém tomou — e o que eu quero é que, ao sair daqui, vocês saibam qual decisão, nos três casos.

> 🗣️ "Nenhum dos três é bug. Os três são a consequência correta de decisões que alguém tomou, e sabendo qual decisão você conserta os três."

> **Nota:** Bastidor: começar sem computador, de pé. O Ollama já tem que estar com o modelo carregado em outra janela, e a página do cartão do modelo no Hugging Face já aberta em aba — nada de procurar na frente da turma. As três etiquetas de diagnóstico ficam **cobertas** no slide e vão sendo reveladas nos slides 5, 13 e 7. Se a Aula 12 terminou atropelada, gastar 90 s recuperando os dezesseis bytes por parâmetro, porque o sintoma 2 depende dessa conta. Mencionar em uma frase que o deck tem apêndice e que o A.5 é a conta que fecha o sintoma 2 — trinta segundos, não mais.

### Slide 2 · [Sintoma 1] O pré-treinado não está errado · 00:05–00:10

Vamos ao primeiro. E eu quero ser preciso sobre o que está faltando, porque a palavra que quase todo mundo usa aqui é errada.

Não está faltando **conhecimento**. O modelo pré-treinado sabe a capital da França. Ele viu isso dez mil vezes. Se eu medir a probabilidade que ele atribui ao token "Paris" logo depois de "a capital da França é", ela é altíssima. O conhecimento está lá, e é verificável.

O que está faltando é uma **convenção**: a convenção de que, quando aparece uma pergunta, o papel dele é responder — e não continuar o documento em que a pergunta apareceu. Porque no corpus, "Qual a capital da França?" quase nunca aparece dentro de um diálogo. Ela aparece dentro de uma lista de exercícios de geografia. Então a continuação de maior probabilidade é "Qual a capital da Alemanha? Qual a capital da Itália?".

E eu quero cravar isso: o modelo não está errado. Ele está fazendo exatamente o que ele foi treinado para fazer, com competência. O erro é meu, que pedi uma coisa e treinei outra.

A analogia que eu uso é de teatro: é um ator que decorou a peça inteira, todas as falas de todos os personagens, e nunca foi informado de qual papel ele interpreta. Ele sabe o texto. Ele não sabe a vez dele.

> 🗣️ "Não falta conhecimento. Falta o modelo saber que a vez dele chegou. É um ator que decorou a peça inteira e não sabe qual personagem ele é."

> **Nota:** Bastidor: essa distinção entre conhecimento e comportamento é o eixo da aula inteira e é ela que sustenta o framework de decisão do slide 14. Cravar aqui, devagar. Se alguém perguntar "então o modelo-base é inútil?", a resposta é não e está no próprio slide — para continuação de código, para pontuar log-verossimilhança e para servir de base de fine-tuning, a base é o objeto certo.

### Slide 3 · [Demo] Os mesmos pesos, dois comportamentos · 00:10–00:20

Dez minutos agora eu mostrando, e a demo tem duas metades: uma no navegador, que reproduz o sintoma 1 ao vivo e fecha ele na mesma tela; e uma no quadro, que produz o número da segunda metade da aula.

*[A demonstração completa está na Parte 2 deste roteiro.]*

> 🗣️ "Eu não vou trocar de modelo. Mesmo arquivo de pesos, mesma máquina, mesma pergunta — e comportamento completamente diferente, só porque eu liguei e desliguei quatro tokens especiais."

> **Nota:** Bastidor: roteiro na Parte 2. Ollama já carregado, cartão do modelo já em aba aberta, capturas de tela da véspera prontas. Se o modelo instruct responder bem até sem template — acontece com modelos muito bem ajustados —, usar isso como conteúdo em vez de insistir: significa que o SFT foi forte o bastante para sobreviver ao protocolo errado, e o efeito puro aparece na variante base. Não gastar mais de 60 s nisso.

### Slide 4 · SFT: a mesma perda, com outro dado · 00:20–00:28

Agora o mecanismo. E ele é decepcionantemente simples, o que é bom.

Supervised fine-tuning — SFT — continua minimizando exatamente a mesma coisa que vocês minimizaram no Lab 2: a entropia cruzada do próximo token. Nada de nova função de perda, nada de arquitetura nova, nada de truque. A mesma conta.

O que muda é o **dado**. Em vez de texto da web, pares de instrução e resposta: uma pergunta e a resposta que a gente considera boa; um pedido e o resultado que a gente considera correto. Escritos por humanos, ou curados por humanos a partir de saída de modelo. A ordem de grandeza é de dezenas de milhares a alguns milhões de exemplos.

E eu quero que vocês sintam essa proporção, porque ela é o argumento inteiro. O pré-treino desses modelos usa trilhões de tokens. O SFT usa, digamos, centenas de milhões. Isso é **partes por milhão** do total. É como se, depois de quatro anos de graduação, uma semana de integração definisse como a pessoa se comporta no escritório. E define mesmo.

Agora a consequência que eu quero cravar e que volta em dez slides: se o SFT é partes por milhão, ele **não** pode estar ensinando conhecimento novo. Não tem tokens para isso. O que ele move é comportamento — formato, papel, disposição a responder, aderência a instrução. Guardem isso, porque é a chave do framework de decisão do fim da aula.

> 🗣️ "SFT é a mesma perda do Lab 2 com outro dado, e em quantidade que é partes por milhão do pré-treino. Com esse orçamento não se ensina fato — se ensina comportamento."

> **Nota:** Bastidor: se vier a pergunta "quantos exemplos eu preciso?", a resposta honesta em duas frases: para mudar formato e estilo, algumas centenas a alguns milhares já mexem visivelmente — e no Lab 4 de amanhã eles vão ver isso com cem exemplos; para um assistente de propósito geral, ordens de grandeza acima disso. Não dar número único, porque não existe.

### Slide 5 · Template de chat: o formato é a interface · 00:28–00:36

Agora o detalhe que a demo já mostrou e que eu quero formalizar, porque ele é a causa de uma quantidade absurda de bug em produção — e porque é ele que fecha o primeiro sintoma.

Um diálogo não é texto solto. É uma sequência de turnos, e cada turno tem um papel: sistema, usuário, assistente. Mas o modelo só vê tokens. Então alguém precisa codificar papel e fronteira de turno **em tokens** — e é isso que o template de chat faz, com tokens especiais reservados para essa função.

A forma está no slide. Um token que abre o turno, o nome do papel, o conteúdo, um token que fecha o turno. Repete. E no fim, o mais importante de todos: o token que abre o turno do **assistente** e não fecha. É depois dele que o modelo aprendeu a produzir a resposta. Aquele token é literalmente o sinal de "sua vez".

Então o template não é enfeite de formatação. Ele é o **protocolo**. E chamar o modelo fora do protocolo dele não produz um modelo mais permissivo — produz o sintoma 1 de volta. Aquela lista de capitais que a gente viu no slide 2 é o que acontece quando o modelo não recebe o sinal de que é a vez dele.

Eu já vi mais de uma equipe concluir que um modelo aberto era ruim porque estava concatenando "Usuário: … Assistente:" à mão, com dois-pontos, em texto puro. O modelo era ótimo. Estava sendo chamado errado. É por isso que toda biblioteca séria expõe uma função `apply_chat_template` em vez de deixar vocês montarem a string — e é por isso que o Checkpoint 2 do lab de amanhã obriga vocês a imprimir a string formatada e olhar os tokens especiais com o olho.

E um alerta prático: cada família de modelo tem o **seu** template. Usar o template de uma família noutra degrada silenciosamente. Sem exceção, sem aviso, sem erro.

*[Descubro a primeira etiqueta do slide de abertura: sintoma 1, fechado.]*

> 🗣️ "O template de chat não é formatação. É protocolo. HTTP sem os dois quebra-linhas não é HTTP mais tolerante — é lixo."

> **Nota:** Bastidor: projetar o template real do modelo escolhido, copiado do `tokenizer_config.json` na véspera, e apontar com o cursor cada delimitador. Se a turma tiver gente que já usou API de chat, perguntar retoricamente onde é que o template aconteceu na vida deles — resposta: no servidor, invisível, e é por isso que ninguém percebe que existe até rodar modelo local. Descobrir a etiqueta do sintoma 1 na tela: o gesto vale mais que a frase.

### Slide 6 · Comportamento de segurança começa aqui · 00:36–00:42

Um parênteses de seis minutos, porque ele explica uma coisa que costuma ser mal entendida.

De onde vem o comportamento de recusa? Quando um assistente diz "não posso ajudar com isso", ou "eu não tenho essa informação", ou "você quis dizer X ou Y?" — de onde isso vem?

Não vem do pré-treino. Nada disso é o próximo token mais provável em corpus da web: na web, uma pergunta perigosa é seguida de uma resposta, não de uma recusa fundamentada. E dizer "eu não sei" é raríssimo em texto publicado, porque texto publicado é escrito por gente que está afirmando coisas.

Então isso entra como **dado de SFT**. Exemplos em que a resposta correta é uma recusa com justificativa. Exemplos em que a resposta correta é admitir incerteza. Exemplos em que a resposta correta é pedir esclarecimento em vez de adivinhar. É comportamento treinado, e ele tem um piso estabelecido aqui, no SFT.

E eu paro exatamente aqui, porque a semana que vem tem uma aula inteira sobre por que o SFT não basta para isso. O argumento, em uma frase: imitar bons exemplos ensina o que fazer e **não** ensina o que evitar quando o caso não estava na lista. Isso é Aula 15, alinhamento, RLHF e DPO.

O que eu quero desmontar agora é uma ideia comum: que segurança é um filtro na saída. Filtro existe, é útil, é complementar. Mas o comportamento que vocês veem num assistente moderno é em boa parte comportamento **treinado** — e por isso ele é frágil do mesmo jeito que qualquer generalização é frágil.

> 🗣️ "Recusar e dizer 'não sei' não são o próximo token mais provável em lugar nenhum da web. Isso é comportamento treinado — entrou como dado, e por isso quebra como dado."

> **Nota:** Bastidor: este slide é o que mais atrai pergunta de jailbreak. Segurar: responder que a fragilidade do comportamento treinado é exatamente o assunto da Aula 15 e que a discussão de ataque e defesa em sistema é a Aula 29. Não abrir nenhuma das duas aqui — cada uma custa dez minutos.

### Slide 7 · [Sintoma 3] Esquecimento catastrófico: o teste que não vê · 00:42–00:48

Agora o terceiro sintoma da abertura, e ele tem nome dramático porque merece.

O que eu descrevi no começo foi isto: o modelo passa a acertar o formato em cem por cento dos casos, e passa a errar uma soma que antes acertava. E a curva de treino continua descendo. Esse é o esquecimento catastrófico.

O mecanismo: quando eu atualizo **todos** os pesos com um dado muito mais estreito que o dado de origem, o modelo melhora na distribuição nova e piora fora dela. E o "piora fora dela" é invisível para quem está medindo, porque quem está medindo está medindo na tarefa que treinou.

A analogia: é regravar em cima de uma fita. A faixa nova entra bem. O que estava embaixo não volta.

E aqui está o erro de método que eu quero prevenir, porque ele é o mais comum de todos: medir o fine-tuning **só** na tarefa que você treinou. Se o seu conjunto de teste é do mesmo domínio do seu treino, o esquecimento é literalmente invisível. Precisa de um conjunto de controle **fora** do domínio treinado — algumas perguntas de outra natureza, guardadas de propósito — e comparar antes e depois nas duas coisas.

Agora a parte boa, que é o gancho do Bloco 2. LoRA mitiga esse risco **estruturalmente**, e não por sorte: com a base congelada, o que se aprende vive num delta pequeno e separado. Desligar o adaptador restaura o modelo original **bit a bit**.

E eu quero ser preciso sobre esse "bit a bit", porque não é figura de linguagem. Uma das duas matrizes do adaptador começa em zeros, então o delta é a matriz nula no passo zero, e desligar o adaptador devolve exatamente a matriz original. Não aproximadamente. A conta que mostra isso — e que mostra por que o treino ainda assim funciona — está no A.2 do apêndice, e eu não vou fazer ela agora.

*[Descubro a etiqueta do sintoma 3 no slide de abertura.]*

> 🗣️ "Se o conjunto de teste é do mesmo domínio do treino, o esquecimento catastrófico é invisível. É por isso que ele se chama catastrófico e não 'ruim'."

> **Nota:** Bastidor: a menção ao conjunto de controle fora do domínio é diretamente cobrada no Lab 4 e no Lab 8 — usar as mesmas palavras nos três lugares. Se sobrar tempo, a pergunta boa para lançar: e se eu misturar dado genérico no meu conjunto de SFT? Resposta curta: é uma das mitigações padrão e se chama *replay*; custa tokens e dilui o efeito desejado. Se alguém puxar o "bit a bit": Parte 4, item 2.

### Slide 8 · Overfitting em 100 exemplos · 00:48–00:55

O segundo risco do SFT, e este vocês vão encontrar amanhã com as mãos de vocês, então eu quero ele explícito.

Com poucas centenas de exemplos e algumas centenas de passos, o modelo pode simplesmente **decorar** o conjunto. A perda de treino desce bonito, a de validação para de descer ou começa a subir, e o modelo passa a devolver respostas do conjunto de treino levemente disfarçadas.

Os controles são os de sempre em aprendizagem de máquina, e amanhã vocês vão usá-los: separar validação, parar antes, taxa de aprendizado modesta, poucas épocas. E tem um controle específico deste gênero de problema que eu quero cravar: **ler as gerações**. Olhar a saída com o olho. Porque a perda de validação não captura repetição literal — um modelo que devolve, palavra por palavra, uma resposta que estava no treino pode ter perda de validação perfeitamente aceitável.

E o erro que eu quero prevenir é este: concluir que o fine-tuning funcionou porque a curva de perda de treino caiu bonito. A perda de treino cair é o que ela faz. É a função dela. O sinal útil é a perda de validação junto com a leitura das amostras, e é literalmente isso que o Checkpoint 5 do lab de amanhã pede: os mesmos cinco prompts, antes e depois, lado a lado, lidos com o olho.

> 🗣️ "A perda de treino cair não é evidência de nada — é o que ela faz. O sinal é a validação junto com as amostras lidas com o olho."

> **Nota:** Bastidor: depois deste slide vai o intervalo de 10 min. Avisar antes de soltar: o Bloco 2 é onde está o número que eles vão conferir no lab amanhã, então é bom voltar no horário. Se o Bloco 1 atrasou, este slide é o mais compressível — o overfitting reaparece no lab, e o deck do Lab 4 tem um item de apêndice inteiro sobre o que a curva de treino não permite concluir.

### Slide 9 · [Sintoma 2] O treino que não cabe numa placa onde o modelo cabe · 01:05–01:11

Voltando. Bloco 2, e ele começa pelo sintoma que eu deixei em aberto: a memória.

Ontem eu contei dezesseis bytes por parâmetro para treinar em precisão mista com AdamW: peso, gradiente, cópia mestre, e os dois momentos. Eu não vou refazer essa conta — ela é de ontem e está no A.4 da Aula 12. Eu vou **aplicar** ela em dois modelos.

Modelo de um vírgula cinco quatro bilhão, o que vocês vão usar amanhã. Os pesos em bf16: três vírgula um gigabytes. Os estados de treino: vinte e quatro vírgula seis. A T4 do Colab tem dezesseis.

Modelo de sete bilhões, o do sintoma da abertura. Os pesos: catorze gigabytes. Os estados de treino: **cento e doze**. A placa tinha vinte e quatro.

Olhem a estrutura das duas linhas, porque ela é idêntica: nos dois casos os pesos cabem e o treino não cabe. Então o problema nunca foi o tamanho do modelo. O problema é o aparato de treino em volta dele — os outros catorze bytes por parâmetro, que existem só porque eu quero atualizar todo mundo.

E daí a pergunta que abre o PEFT, que é uma pergunta boa: e se eu não atualizasse todo mundo?

> 🗣️ "Os pesos do modelo de sete bilhões cabem em catorze gigabytes. O aparato para atualizá-los ocupa cento e doze. O problema nunca foi o modelo — foi querer mexer em todo ele."

> **Nota:** Bastidor: escrever no quadro só as duas razões — `14 → 112` e `3,1 → 24,6` — porque a desproporção é o argumento e a decomposição dos 16 bytes é conteúdo de ontem. A conta comparativa das três configurações, com as ativações contadas separadamente, está em A.5 e é ela que fecha este sintoma no slide 13. Se alguém perguntar por SGD sem momento para economizar estado: resposta honesta, cai de 16 para 8 bytes, **ainda não cabe**, e a qualidade de convergência em transformer piora o suficiente para ninguém fazer — o número está em A.5, casos-limite.

### Slide 10 · LoRA: um delta de baixo posto sobre pesos congelados · 01:11–01:19

E aqui está a ideia, que cabe numa linha. Eu vou ler ela e não vou derivar nada.

*[Projeto a linha e leio apontando cada peça.]*

`h` é igual a `W₀` vezes `x`, mais alfa sobre `r`, vezes `B`, vezes `A`, vezes `x`.

Em português: eu congelo a matriz `W` e adiciono um caminho paralelo com duas matrizes finas, `A` e `B`. Só `A` e `B` recebem gradiente. E três leituras dessa linha, uma por peça.

Primeira: `B` vezes `A` vezes `x` é a **correção**, e ela tem posto no máximo `r`. Por quê? Porque `A` vezes `x` é um vetor de dimensão `r` — a informação passa por um gargalo. Tudo que a correção consegue carregar atravessou um gargalo de dimensão oito, num modelo de dimensão mil quinhentos e trinta e seis. A demonstração de que isso limita o posto está em A.1.

Segunda: `A` é inicializada aleatória e `B` é inicializada com **zeros**. Consequência: no passo zero o produto é a matriz nula, e o modelo adaptado é exatamente o modelo base. É o "bit a bit" do slide 7. E a pergunta natural — se o caminho contribui zero, como é que ele aprende? — tem resposta, e ela é bonita: o gradiente de `B` **não** é zero no passo zero, porque `A` é aleatória. Então `B` se move primeiro, e `A` começa a se mover no segundo passo. A assimetria é o mecanismo, e ela está escrita em A.2.

Terceira: aquele fator alfa sobre `r`. Ele desacopla a intensidade do efeito do valor de `r`, o que na prática significa que vocês podem trocar `r` de oito para trinta e dois sem reajustar a taxa de aprendizado. Por quê exatamente: porque o delta acaba sendo alfa vezes a **média** de `r` termos, não a soma. Média não cresce com o número de termos. Está em A.3.

E o que fez LoRA vencer as alternativas: na hora de servir, `W` mais alfa sobre `r` vezes `B` `A` pode ser **fundido** numa única matriz. Depois da fusão, o modelo adaptado tem exatamente a mesma forma e a mesma latência do modelo original. Zero overhead. Compare com adaptadores em série, que a literatura tentou antes: aqueles inserem camadas novas no caminho, e camada nova é latência nova em toda requisição, para sempre.

E a pergunta que sempre vem: por que posto baixo basta? A hipótese, que o artigo sustenta empiricamente, é que a **atualização** necessária para adaptar um modelo já competente tem posto intrínseco baixo. Repararam na palavra? A atualização, não o modelo. O modelo precisa de posto alto porque precisa representar a língua inteira. A correção que o transforma em assistente de um domínio, não — ela reorienta capacidades que já estão lá.

A analogia que eu uso: o modelo base é um piano afinado com oitenta e oito teclas. LoRA não constrói outro piano. É uma partitura fina dizendo quais teclas enfatizar.

> 🗣️ "`B` começa em zero, então o modelo adaptado começa idêntico ao base — e o que se treina é a correção, não o modelo. É a correção que tem posto baixo, não o modelo."

> **Nota:** Bastidor: desenhar no quadro o retângulo grande `W` e, ao lado, o retângulo alto e fino `B` colado no retângulo largo e baixo `A`. A geometria do desenho é o argumento — a turma vê que `A` e `B` juntas são uma fração da área de `W`. **Não derivar nenhuma das três leituras**: cada uma tem o item de apêndice nomeado em voz alta, e nomear já dá a sensação de rigor sem custar minuto. Se alguém perguntar qual `r` usar, adiar para o slide 11 e para a extensão do exercício, cujo gabarito está na tabela de variações de A.1.

### Slide 11 · A conta dos parâmetros treináveis: 0,60% · 01:19–01:25

Agora o número da aula. E eu vou fazer **um** módulo no quadro, não os sete, porque a soma dos sete está no slide e na tabela de A.1 e ela me custava quatro minutos na versão anterior desta aula.

Por módulo adaptado, LoRA acrescenta `r` vezes a soma das duas dimensões. Vamos no modelo de referência de amanhã: dimensão do modelo mil quinhentos e trinta e seis, vinte e oito camadas, adaptador nas sete projeções de cada camada — as quatro da atenção e as três do MLP — com `r` igual a oito.

Uma projeção de mil quinhentos e trinta e seis por mil quinhentos e trinta e seis tem dois milhões trezentos e cinquenta e nove mil pesos. O adaptador dela, com `r` oito, tem oito vezes três mil e setenta e dois: vinte e quatro mil quinhentos e setenta e seis. Cerca de um por cento daquele módulo.

*[Aponto os dois totais no slide.]*

Somando os sete módulos de uma camada, dá trezentos e vinte e nove mil setecentos e vinte e oito. Vezes vinte e oito camadas: nove milhões duzentos e trinta e dois mil trezentos e oitenta e quatro. Nove vírgula dois milhões.

E agora a única divisão que eu faço no quadro hoje: nove vírgula dois milhões sobre um vírgula cinco quatro bilhão. **Zero vírgula sessenta por cento.**

Menos de um por cento. É esse o número. E amanhã, no Checkpoint 3, vocês vão chamar uma função do PEFT que imprime exatamente essa porcentagem — e eu quero que vocês confiram contra a conta que vocês fizeram. Porque um `print` que você não sabe conferir não é conhecimento, é fé.

E tem um corolário em bytes de disco que é bonito: o adaptador salvo tem dezoito megabytes em bf16, contra três gigabytes do modelo base. Uma razão de um para cento e sessenta e sete. Isso muda arquitetura de produto: um servidor mantém **uma** base em memória e troca N adaptadores em tempo de execução, um por cliente, um por tarefa. Fine-tuning deixou de ser um artefato de gigabytes e passou a ser um arquivo que cabe em anexo de e-mail.

Um erro que eu quero prevenir antes de alguém cometer: zero vírgula seis por cento dos parâmetros treináveis **não** é zero vírgula seis por cento do custo de treino. O forward e o backward atravessam o modelo inteiro do mesmo jeito. O que a gente economizou é memória. A conta em FLOPs está em A.5 e o número honesto é dois terços do custo completo, não zero vírgula seis por cento — e amanhã vocês vão sentir isso no relógio.

> 🗣️ "Nove vírgula dois milhões de parâmetros treináveis num modelo de um vírgula cinco bilhão. Zero vírgula seis por cento — e amanhã vocês vão conferir esse número contra o que a biblioteca imprime."

> **Nota:** Bastidor: números para o quadro, na ordem: `24.576` por projeção quadrada, `329.728` por camada, `9.232.384` no total, `0,60%`. **A soma dos sete módulos não vai ao quadro** — está no slide e a tabela completa, com a conferência de que os módulos adaptados somam 1,31 B dos 1,54 B, está em A.1. Se travar na aritmética ao vivo, ir direto ao total e à razão. As dimensões `256` das projeções de chave e valor vêm de atenção com poucas cabeças de chave-valor (GQA, Aula 8) — se perguntarem, é uma frase e segue.

### Slide 12 · Quantização: duas finalidades que se confundem · 01:25–01:31

Antes do QLoRA, eu preciso separar duas coisas que a turma mistura sempre, e a confusão é entendível.

Quantizar é representar peso com menos bits. Mas existem **duas** finalidades completamente diferentes, e a diferença é o que o peso quantizado vai fazer da vida.

Primeira finalidade: quantizar **para inferência**. Aqui eu comprimo os pesos de uma vez, permanentemente, para o modelo caber e rodar mais rápido. Oito bits, quatro bits, os formatos que vocês já usaram sem saber quando baixaram modelo no Ollama. E é uma troca honesta: eu perco um pouco de qualidade e ganho memória e vazão. A perda é real, é medível, e ela cresce quando se desce abaixo de quatro bits.

Segunda finalidade: quantizar **para treino**. E aqui a lógica é diferente, porque o peso que eu quantizei é o peso que está **congelado**. Ele nunca é atualizado. Ele é descomprimido por bloco na hora de calcular, participa do forward e do backward, e o gradiente **atravessa** ele para chegar ao adaptador — que vive em precisão alta.

No primeiro caso eu comprimo o que vou usar. No segundo eu comprimo o que vou **congelar**, e o que eu vou treinar continua em precisão alta.

Agora, uma objeção que aparece sempre e que é uma boa objeção: a função de quantização é uma escada, tem derivada zero em quase todo ponto — como é que o gradiente passa por ela? A resposta é que ele não passa por ela. Ninguém pede derivada em relação ao peso quantizado, porque o peso está congelado. O peso descomprimido entra na conta como **constante multiplicativa**, e constante não precisa de derivada. É exatamente isso que separa o QLoRA do treino consciente de quantização, que precisa de um estimador aproximado porque lá o objetivo é atualizar o peso quantizado. O argumento completo está em A.4.

E o erro que segue disso, que eu já vi mais de uma vez: supor que treinar sobre base quantizada quantiza o que se aprendeu. Não. O adaptador sai em precisão alta. A base é que está comprimida.

E o corolário honesto, que vale para o relatório de vocês: um adaptador treinado contra uma base de quatro bits foi otimizado **contra aquela base**. Fundir ele numa base em bf16 funciona e não é matematicamente equivalente. Então a comparação honesta declara em qual base o número foi medido — é a mesma lição de proveniência do Lab 3, agora com quantização em vez de backend.

> 🗣️ "Quantizar para inferência comprime o que você vai usar. Quantizar para treino comprime o que você vai congelar. Não é a mesma decisão e não tem o mesmo custo."

> **Nota:** Bastidor: se a turma perguntar sobre GPTQ, AWQ e as variantes GGUF por nome, listar em uma frase que são esquemas de quantização pós-treino para inferência com estratégias diferentes de calibração, e que o Módulo 7 (serving, Aula 24) volta nisso. Não abrir aqui. A lista fechada do que fica em precisão alta — adaptador, estados do otimizador, o cálculo, as ativações, as normalizações — está em A.4, Parte 3, e é a forma mais rápida de responder qualquer variante dessa pergunta. E há uma pergunta melhor que costuma vir junto, "mas o que é quantizar, **exatamente**?" — ela é sinal de que a turma estava usando "quatro bits" como rótulo. A resposta de uma frase é a régua: em vez de guardar o número, guardo em qual das duzentas e cinquenta e seis marcas de uma régua ele caiu, mais a régua. Os dois jeitos de posicionar a régua, o erro que sobra e a taxonomia PTQ × QAT estão em A.6, e eu **não** abro em sala — são cinco minutos que sairiam do framework de decisão, que é o clímax da aula.

### Slide 13 · QLoRA: base congelada em 4 bits + adaptador em precisão alta · 01:31–01:38

E aí chega o QLoRA, que é a junção do slide 10 com o slide 12 mais três engenharias.

A ideia: a base fica congelada em **quatro bits**, e os adaptadores LoRA ficam em precisão alta. É isso. O resto são as três engenharias que fazem funcionar sem perder qualidade.

Primeira: **NF4**, um tipo de dado de quatro bits cujos dezesseis níveis não são igualmente espaçados — eles são posicionados nos quantis de uma distribuição normal, por bloco de sessenta e quatro pesos. A justificativa é que os pesos de um transformer pré-treinado são aproximadamente normais, então quantis normais gastam os dezesseis níveis onde há peso de verdade, em vez de gastar metade deles em faixas vazias. E tem um detalhe de projeto que eu gosto: a grade é construída para conter o **zero exato**, porque peso zero aparece em máscara e em padding, e um zero que descomprime para zero vírgula zero três deixa de ser zero.

Segunda: **dupla quantização**. Quantização por bloco precisa guardar uma constante de escala por bloco, e essas constantes custam meio bit por parâmetro. Então quantiza-se também as constantes, e o custo cai de quatro vírgula cinco bits por peso para quatro vírgula cento e vinte e sete. É uma economia de zero vírgula trinta e sete bit por peso — parece exagero, e no modelo de amanhã são setenta e dois megabytes. Num treino que está a algumas centenas de megabytes do limite da placa, é exatamente esse tipo de exagero que faz caber.

Terceira: **otimizadores paginados**. Nos picos de memória, os estados do otimizador são movidos para a memória do host em vez de estourar. É paginação, aplicada a estado de treino.

E agora o fecho do sintoma dois, com número. Olhem a tabela.

*[Aponto as três linhas.]*

Fine-tuning completo do modelo de sete bilhões: cento e doze gigabytes. Não cabe em lugar nenhum que vocês tenham acesso. LoRA sobre base em bf16: catorze vírgula três — cabe na placa de vinte e quatro. QLoRA com base em NF4: **três vírgula nove gigabytes**. Cabe na T4 do Colab gratuito, com folga.

Cento e doze para três vírgula nove. Vinte e nove vezes. E a economia vem de duas coisas independentes que se multiplicam: congelar tira catorze dos dezesseis bytes de quase todo parâmetro, e quantizar comprime os dois que sobraram. Congelar vale mais que quantizar; quantizar é o que faz o resto caber.

*[Descubro a etiqueta do sintoma 2 no slide de abertura.]*

Um alerta antes de fechar: QLoRA **não** é uma técnica de qualidade. É uma técnica de viabilidade. Ela faz caber. E ela cobra em tempo: descomprimir por bloco a cada passagem é trabalho extra, então um passo de QLoRA é mais lento que um passo de LoRA sobre base não quantizada. A qualidade fica próxima, e quem compara sem declarar a base está repetindo a falha de proveniência que eu cobrei no relatório de vocês semana passada.

> 🗣️ "QLoRA não melhora nada. Ele faz caber — e 'caber' é a diferença entre esta disciplina ter um laboratório de fine-tuning e não ter."

> **Nota:** Bastidor: se o tempo estiver curto, cortar dupla quantização e otimizador paginado sem culpa — são detalhe de implementação, estão escritos em A.4 e não são cobráveis. O que **não** pode ser cortado é o par "base congelada em 4 bits, adaptador em precisão alta", a linha do QLoRA na tabela e o gesto de descobrir a etiqueta do sintoma 2, porque os três aparecem no Checkpoint 1 do lab. A conta completa das três linhas, com as ativações separadas e a regra de diagnóstico do `OOM`, está em A.5.

### Slide 14 · O framework de decisão: prompting × RAG × fine-tuning · 01:38–01:45

Agora o slide mais importante da aula, e provavelmente um dos três mais importantes do curso. Ele volta na Aula 18, ele volta no projeto final e ele volta na prova.

A pergunta é: eu quero mudar o comportamento de um sistema com LLM. Tenho três alavancas. Qual eu puxo?

**Prompting.** Resolve formato leve, tom, tarefa nova sem dado nenhum, instrução pontual. Não resolve conhecimento que o modelo não tem, não resolve consistência em escala, e cobra token em **toda** requisição, para sempre. Custo de treino zero. Latência de mudança: minutos.

**RAG.** Resolve conhecimento privado, conhecimento que muda, e — isso é o que mais importa — fato com **citação de fonte auditável**. Não resolve comportamento, não resolve estilo, não resolve aderência a esquema rígido, e a qualidade dele é limitada pelo recuperador, o que vocês vão medir no Lab 5. Custo: infraestrutura de índice. Latência de mudança: horas, o tempo de reindexar.

**Fine-tuning.** Resolve comportamento, formato rígido, estilo, jargão de domínio — e resolve encurtar o prompt, que é uma economia real e subestimada: aquilo que você não precisa mais explicar em cada requisição virou peso. Não resolve fato que muda, não garante factualidade, e não dá auditoria de origem. Custo: GPU, dados curados e avaliação. Latência de mudança: dias.

E agora a linha que ninguém escreve nas tabelas de internet: o que **nenhuma das três** resolve. Nenhuma das três garante que a resposta esteja correta. Nenhuma. Isso exige medição — Aula 27 — e, quando o fato é verificável, uma ferramenta que verifique, que é Aula 21.

Agora o erro clássico, e eu vou nomear ele em voz alta porque ele é a proposta de projeto final que mais aparece nesta disciplina: tentar injetar por fine-tuning um fato que **muda**. Preço. Política vigente. Catálogo. Tabela de horários. Alguém sempre propõe treinar o modelo nos documentos da empresa para ele "saber" o conteúdo.

Por que não funciona? Quatro razões, e eu quero as quatro. O fato entra fraco, porque cem exemplos não competem com trilhões de tokens. O fato se mistura com o que o modelo já tinha, e você não controla qual dos dois vai sair. Não existe fonte citável, então você não tem como auditar nem como corrigir. E na semana seguinte o preço muda e você tem que retreinar. Fine-tuning **não é banco de dados**.

Fato que muda entra por recuperação ou por ferramenta. Fine-tuning entra quando o problema é **como** o modelo responde, não **o que** ele sabe.

E tem um terceiro erro, que é de leitura da tabela e é o mais caro dos três. Olhando essas linhas, a cabeça monta uma escada: prompting é o degrau fraco, RAG é o do meio, fine-tuning é o forte. Está errado. Existe uma quarta alavanca, e ela mora no vão entre escrever prompt e treinar peso: **otimizar o prompt contra uma métrica**.

Em dois mil e vinte e seis saiu um trabalho chamado GEPA que faz exatamente isso. Ele roda o sistema, guarda a trajetória inteira — o raciocínio, as chamadas de ferramenta, o que voltou —, e aí um modelo **lê** essa trajetória e escreve em português o que deu errado e de quem é a culpa. Com esse diagnóstico ele reescreve a instrução e testa. E o resultado é o que me fez colocar essa linha na tabela: ele supera o **GRPO** — que é o algoritmo da Aula 16, o que treina peso — em seis por cento na média, até vinte, usando **trinta e cinco vezes menos execuções**. Sem tocar num peso.

Então guardem a distinção, porque ela não é retórica: escrever prompt na mão é fraco. Otimizar prompt contra métrica não é. E o preço dessa alavanca é o que restringe ela: você precisa de conjunto rotulado e de métrica automática. Sem os dois, não tem o que otimizar — e é por isso que essa linha só faz sentido depois do Lab 8. O mecanismo inteiro está em A ponto sete.

> 🗣️ "A tabela não é uma escada de poder. Otimizar o texto do prompt bateu treinar o peso, com trinta e cinco vezes menos execução — e o que separa quem pode usar isso de quem não pode é ter conjunto rotulado e métrica."

E o segundo erro, mais sutil: tratar as três como exclusivas. Sistema real combina. Fine-tuning para o formato e o jargão, RAG para o fato, prompting para o ajuste do turno. O framework existe para escolher **por onde começar** — não para escolher uma só.

> 🗣️ "Fine-tuning não é banco de dados. Ele muda **como** o modelo responde, não **o que** ele sabe — e confundir os dois é a proposta de projeto que mais fracassa nesta disciplina."

> **Nota:** Bastidor: este slide tem que ficar projetado pelo maior tempo possível e a turma tem que fotografar. Perguntar explicitamente se alguém já pensou em "treinar o modelo nos documentos da empresa" — quase sempre alguém levanta a mão, e usar essa pessoa como aliada, não como exemplo negativo: a intuição é boa, o instrumento é errado, e a Aula 18 dá o instrumento certo. A quarta linha é nova nesta oferta e vale sessenta segundos, não mais — o que tem de ficar é que ela ocupa o vão entre "escrevi um prompt" e "treinei o modelo", e que o pré-requisito dela é o mesmo do Lab 8. Se alguém perguntar como o otimizador sabe o que reescrever, a resposta de uma frase é "ele lê a trajetória que falhou e escreve o diagnóstico em português, em vez de receber só um número". Não abrir A.7 em sala: são cinco minutos que saem do exercício de decisão.

### Slide 15 · [Exercício] Decidir, não calcular · 01:45–01:50

Cinco minutos com vocês trabalhando, em dupla.

*[O enunciado e a condução completa estão na Parte 3 deste roteiro.]*

> 🗣️ "Quatro casos, três colunas: qual alavanca, o que ela resolve, e o que ela **não** resolve. A terceira coluna é a que vale — e nenhum dos quatro se resolve calculando."

> **Nota:** Bastidor: enunciado e correção na Parte 3. O caso 4 é o do preço que muda e é o único cuja resposta não é nenhuma das três — deixar a dupla errar nele. Cronometrar de verdade: 3 min de dupla, 2 min na correção do caso 4 apenas, e o resto vai no encerramento. Quem terminar antes tem a extensão de contagem no slide, com gabarito em A.1 — isso mantém as duplas rápidas ocupadas sem consumir tempo de condução.

### Slide 16 · Fechamento: o mapa do Lab 4 · 01:50–02:00

Deixa eu fechar voltando aos três sintomas, que agora estão todos com etiqueta.

O primeiro — o modelo que continua a lista — era falta de comportamento, não de conhecimento, e entra por dado de instrução formatado num template que é o protocolo do modelo.

O segundo — o treino que não cabe — era dezesseis bytes por parâmetro para atualizar tudo. E a resposta é base congelada, delta de posto baixo, `B` começando em zero, quatro bits na base. Cento e doze gigabytes viraram três vírgula nove.

O terceiro — o modelo que esqueceu — era medir só na tarefa treinada, e a resposta são duas: conjunto de controle fora do domínio, e a base congelada, que torna o esquecimento estruturalmente menos provável e o adaptador removível.

E um framework que diz quando essa é a ferramenta certa — e, mais importante, quando não é.

Amanhã, Laboratório 4, e é o lab que eu mais gosto de dar, porque o número aparece na tela e o número é chocante. Vocês vão carregar um modelo aberto de um vírgula cinco bilhão de parâmetros quantizado em quatro bits no Colab gratuito. Vão rodar cinco prompts de teste **antes** de treinar qualquer coisa e guardar as respostas. Vão pegar cem exemplos de instrução em português que estão embutidos no notebook — e eu escolhi de propósito a mesma tarefa de classificação do Lab 3, para vocês fecharem o laço. Vão configurar LoRA e imprimir a porcentagem de treináveis, que vocês vão conferir contra a conta do slide 11. Vão treinar. E vão rodar os **mesmos** cinco prompts depois, lado a lado.

E o que vocês vão ver é isto: no Lab 3 vocês mediram que o modelo acertava o rótulo e respondia em prosa livre, e vocês reportaram isso numa coluna separada. Amanhã essa coluna vai a zero, com cem exemplos e menos de um por cento dos parâmetros. Few-shot é crachá; fine-tuning é uniforme.

No fim, vocês salvam o adaptador, olham o tamanho do arquivo, e recarregam ele em cima da base. Dezoito megabytes que mudam o comportamento de um modelo de gigabytes.

*[Projeto o índice do apêndice por 15 s.]*

Cinco itens. E eu nomeio um: o **A.5**, que é a conta de memória das três configurações lado a lado. É ela que fechou o sintoma dois hoje, e é ela que o apêndice do lab de amanhã vai aplicar ao caso concreto da T4 para explicar por que o `r` que eu escolhi cabe. Quem quiser entender por que o notebook está configurado como está, é por ali.

Uma coisa prática, e é a única coisa que eu peço para hoje: eu preciso que quem ainda não confirmou GPU no Colab confirme antes de amanhã. O notebook tem um caminho de fallback sem GPU, com um modelo menor ainda, e ele funciona — mas ele é ilustrativo, e eu prefiro que a medição de vocês seja real.

As duas leituras estão no slide com os arXiv IDs: o Hu do LoRA e o Dettmers do QLoRA. E a pergunta dirigida do LoRA é a que eu mais gosto: o artigo inicializa `B` com zeros e `A` aleatoriamente. O que aconteceria se as duas fossem aleatórias, e por que essa escolha importa muito mais no primeiro passo do que no centésimo? Respondam antes de ler, e depois confiram contra o A.2 — a resposta está escrita lá, com a conta da perturbação composta ao longo das vinte e oito camadas.

> 🗣️ "Amanhã vocês vão mudar o comportamento de um modelo de um vírgula cinco bilhão de parâmetros com cem exemplos e um arquivo de dezoito megabytes. E o número que vai aparecer na tela é menos de um por cento."

> **Nota:** Bastidor: projetar o mapa dos cinco checkpoints do Lab 4 e ficar 20 segundos em silêncio para fotografar. Recolher o pulso por mão levantada: quantos já confirmaram GPU no Colab. Se for menos da metade, mandar confirmar hoje em voz alta, porque o modo de fallback funciona e mede menos. Não estourar as duas horas — amanhã é lab e lab que começa atrasado perde o Checkpoint 5.

---

## Parte 2 — Demonstração guiada

Dez minutos, em duas metades: cinco no navegador e cinco no quadro. O objetivo da primeira metade é reproduzir o sintoma 1 ao vivo e fechar ele na mesma tela, usando o mesmo modelo que eles já baixaram no Lab 3. O da segunda é produzir o número da aula — os zero vírgula sessenta por cento —, porque é ele que o Checkpoint 3 de amanhã vai imprimir.

Insumos da véspera: o modelo do Ollama já carregado na minha máquina; o cartão do modelo aberto numa aba, com a variante base e a variante instruct visíveis; o template do tokenizador copiado num arquivo de texto local; capturas de tela das duas chamadas, para o caso de a máquina falhar; e a conta do LoRA já conferida no papel.

**1.** **[Abro o cartão do modelo no Hugging Face e mostro que a mesma família publica duas variantes]** Olha aqui uma coisa que passa batida quando a gente baixa modelo: a mesma família publica duas variantes do mesmo tamanho. Uma base e uma *instruct*. E olha o que o cartão da base diz — vou ler em voz alta: que ela não foi ajustada para seguir instruções e não deve ser usada como assistente. Esse aviso existe porque muita gente baixa a errada e conclui que o modelo é ruim.

**2.** **[Chamo o modelo pelo caminho de chat, com o template aplicado, e projeto a resposta]** Agora eu vou perguntar "qual a capital da França?" pelo caminho normal de chat, o que aplica o template por baixo. Resposta bem-comportada, direta, uma frase. É o que todo mundo espera de um assistente.

**3.** **[Chamo o mesmo modelo pelo caminho de completion cru, com o template desligado, e projeto a resposta ao lado]** Mesmo modelo. Mesmo arquivo de pesos. Mesma máquina. Mesma pergunta, palavra por palavra. Só que agora eu desliguei o template — estou mandando o texto cru, sem nenhum token de papel. Olha o que voltou. Ele continuou. Mais perguntas, ou uma lista, ou um parágrafo qualquer. **É o sintoma um da abertura, acontecendo aqui.** Nada mudou no modelo; o que mudou foram quatro tokens especiais que eu deixei de mandar.

**4.** **[Abro o arquivo de configuração do tokenizador e projeto a string do template]** E aqui está o que eu desliguei. Este é o template do tokenizador desse modelo, copiado ontem. Olha os delimitadores de turno. Olha o nome do papel. E olha este último aqui, o que **abre** o turno do assistente e não fecha — esse é o "sua vez". É depois dele que o modelo aprendeu, no SFT, que ele é quem fala. Sintoma um, diagnosticado e fechado em quatro minutos.

**5.** **[Vou para o quadro e escrevo a conta do LoRA para um módulo]** Segunda metade, e agora no quadro. Uma projeção de mil quinhentos e trinta e seis por mil quinhentos e trinta e seis: dois milhões trezentos e cinquenta e nove mil duzentos e noventa e seis pesos. Agora o adaptador dela com `r` igual a oito: oito vezes mil quinhentos e trinta e seis mais mil quinhentos e trinta e seis. Oito vezes três mil e setenta e dois. Vinte e quatro mil quinhentos e setenta e seis. Divide um pelo outro: cerca de um por cento daquele módulo.

**6.** **[Escrevo os dois totais e faço a única divisão da aula]** Agora eu não vou somar os sete módulos aqui — a soma está no slide e a tabela completa está no A.1, com a conferência de que os módulos adaptados somam um vírgula três um bilhão dos um vírgula cinco quatro. Eu escrevo os dois totais: trezentos e vinte e nove mil setecentos e vinte e oito por camada, nove milhões duzentos e trinta e dois mil trezentos e oitenta e quatro no modelo. E ao lado o total do modelo, um vírgula cinco quatro bilhão. Divisão: **zero vírgula sessenta por cento**. Esse é o número da aula, e ele vai aparecer na tela de vocês amanhã.

**7.** **[Volto ao navegador e abro a página de um repositório de adaptador LoRA]** E eu fecho com a mesma razão em bytes de disco. Olha o tamanho do arquivo do adaptador nesta página: dezenas de megabytes. E olha o tamanho do modelo base ao lado: gigabytes. Um para cento e sessenta e sete. É a mesma razão do quadro, agora em disco — e é por isso que fine-tuning deixou de ser um artefato que se hospeda e passou a ser um arquivo que se anexa.

> **Nota de contingência:** Bastidor: se o Ollama não responder em 30 segundos, ir direto para as capturas de tela da véspera e não tentar consertar ao vivo. Se o modelo instruct responder bem até no caminho cru, dizer isso em voz alta como conteúdo — o SFT foi forte o bastante para sobreviver ao protocolo errado — e ir direto ao passo 4, que é o essencial da primeira metade. A segunda metade (passos 5 e 6, o quadro) **não depende de máquina nenhuma** e é a parte que não pode ser cortada: se tudo falhar, a demo é ela. Se o tempo apertar, cortar o passo 7 — a razão em disco é bonita e é redundante com a do quadro.

---

## Parte 3 — Hands-on

Cinco minutos, em dupla, com os quatro casos projetados. O objetivo não é acertar a alavanca — é preencher a terceira coluna, o "não resolve", que é onde a compreensão aparece e onde o projeto final costuma tropeçar. Na V1 o exercício da aula era refazer a contagem de parâmetros com outro `r`; isso virou extensão opcional com gabarito no apêndice, e o obrigatório passou a ser decisão.

**1.** **[Projeto os quatro casos e formo as duplas]** Cinco minutos, em dupla. Quatro casos no slide, e para cada um eu quero três coisas: qual a alavanca primária — prompting, RAG ou fine-tuning; uma frase dizendo o que ela resolve nesse caso; e uma frase dizendo o que ela **não** resolve e de onde vem a solução dessa parte. É a terceira que vale.

Os quatro casos:

1. Um assistente precisa responder sobre o regulamento da universidade, citando o artigo exato.
2. O modelo acerta a classificação mas responde em prosa livre; a integração exige rótulo puro, sempre.
3. O sistema precisa escrever laudos em português técnico de um domínio, com o jargão e a estrutura do setor.
4. O preço dos produtos muda toda semana e o assistente precisa informá-lo corretamente.

E para quem terminar antes: a extensão está no slide — refazer a contagem com `r` igual a dezesseis, e depois com adaptadores só nas quatro projeções de atenção, e dizer qual das duas mudanças move mais o número. O gabarito é a tabela de variações do A.1, e a resposta é contraintuitiva.

*Bastidor — erros comuns:* no caso 1, escrever "fine-tuning nos documentos do regulamento" — é o erro clássico, e ele aparece porque a intuição de "o modelo precisa conhecer isso" leva direto ao lugar errado; a exigência de **citar o artigo** é o sinal que decide, porque citação exige fonte recuperada. No caso 2, escrever "prompting com few-shot" e parar — funciona parcialmente e é exatamente o que eles mediram no Lab 3, onde a coluna de fora-do-espaço não foi a zero; o "sempre, sem exceção" é o que empurra para fine-tuning ou para saída restrita por esquema. No caso 3, confundir jargão com fato: o jargão é forma e vai para fine-tuning; o conteúdo do laudo é fato e vem de outro lugar. E no caso 4, quase todo mundo escolhe uma das três, quando a resposta certa é nenhuma delas isoladamente — preço que muda toda semana é consulta a fonte viva, ferramenta, e isso é Aula 21.

*Como recolher:* três minutos de dupla, dois de correção. Não corrijo os quatro: pergunto o caso 1 por voluntário e checo se alguém escreveu fine-tuning — se sim, agradeço em voz alta, porque é o erro mais útil do dia; e gasto os dois minutos no caso 4. No caso 4 eu quero ouvir da sala a frase "nenhuma das três". Se ninguém disser, eu espero cinco segundos e digo. Fecho conectando: o caso 1 é a Aula 18, o caso 4 é a Aula 21, e os dois vão aparecer em metade das propostas de projeto final. Se alguma dupla fez a extensão, peço o número em voz alta e uso ele: restringir aos módulos de atenção corta por quatro vírgula dois, dobrar o `r` só dobra — quais módulos importa mais que quanto.

---

## Parte 4 — Apêndice: se perguntarem

Esta parte **não é fala planejada**. É contingência: o que eu faço se a turma pedir a conta em aula. A regra geral é remeter ao item por nome e seguir; conduzir uma derivação só se o Bloco 2 estiver adiantado, e anunciando que é conteúdo de consulta.

> **Nota:** Bastidor: o custo de cada item abaixo sai do Bloco 2, e o Bloco 2 é o mais apertado dos dois. Se eu fizer o item 2, perco o exercício de decisão — e o exercício vale mais para o objetivo da aula, porque ele é o formato dos quarenta pontos de justificativa da prova. **Ordem de sacrifício se a aula atrasar:** corto primeiro o passo 7 da demo (a razão em disco, que é redundante); depois a dupla quantização e o otimizador paginado do slide 13, que são detalhe de implementação; depois o slide 6 (segurança), que o slide sustenta sozinho e que a Aula 15 retoma inteiro. **Não corto** o slide 14 — o framework volta na Aula 18, no projeto final e na prova — nem o par "base congelada em 4 bits, adaptador em precisão alta" do slide 13, sem o qual o Checkpoint 1 do lab de amanhã não faz sentido. E não corto o exercício.

**Item 1 — "De onde vem esse `r · (d_in + d_out)`?" (A.1, ~4 min no quadro).**
A pergunta mais fácil de responder bem. Eu escrevo as duas matrizes com as dimensões: `A` é `r` por `d_in`, `B` é `d_out` por `r`. Conto as entradas de cada uma, somo, e ponho ao lado o produto `d_in` vezes `d_out` que é o tamanho da matriz original. E, se a pergunta foi boa, acrescento a de graça: o produto `B` `A` tem posto no máximo `r` porque `A` vezes `x` mora em dimensão `r`, e é o gargalo que limita tudo.
**Versão de 30 segundos:** "conta as entradas de cada matriz: `r` vezes `d_in` mais `d_out` vezes `r`. E o produto tem posto no máximo `r` porque a informação passa por um gargalo de dimensão `r`. A tabela dos sete módulos, com a conferência do total do modelo, está no A.1."

**Item 2 — "Se `B` começa em zero, como é que ele aprende?" (A.2, ~5 min no quadro).**
A melhor pergunta que essa aula pode receber, e eu faço ela com prazer se houver tempo. No quadro eu escrevo os dois gradientes: o de `B` tem `A` vezes `x` como fator, e o de `A` tem `B` transposta como fator. Avalio no passo zero: o de `B` é diferente de zero porque `A` é aleatória; o de `A` é zero porque `B` é zero. Então `B` anda primeiro, `A` anda a partir do segundo passo. E fecho com o contrafactual: se as duas fossem zero, os dois gradientes seriam zero e o adaptador nunca sairia da origem — é o único jeito de configurar LoRA que roda perfeitamente e não aprende nada.
**Versão de 30 segundos:** "o gradiente de `B` não é zero, porque ele depende de `A`, e `A` é aleatória. Então `B` sai do zero no primeiro passo e `A` começa a andar no segundo. Se as duas começassem em zero, aí sim ficaria travado para sempre. A conta está no A.2, com o contrafactual das duas aleatórias e a perturbação composta nas vinte e oito camadas."

**Item 3 — "Por que dividir por `r` e não por outra coisa?" (A.3, ~4 min no quadro).**
Vale fazer se sobrar tempo, porque é o hiperparâmetro que a turma vai mexer amanhã. Eu escrevo o produto `B` `A` como soma de `r` termos de posto um, e ponho o `um sobre r` na frente: o delta é alfa vezes a **média** dos `r` termos, não a soma. Média não cresce com o número de termos; soma cresce. Por isso trocar `r` não obriga a reajustar a taxa de aprendizado. E digo o que essa escala **não** compra: ela não regulariza nada, `r` grande continua tendo mais capacidade de decorar.
**Versão de 30 segundos:** "porque o delta acaba sendo alfa vezes a média de `r` termos, em vez da soma. Média não cresce com `r`, soma cresce — então a escala do efeito fica independente de `r` e a taxa de aprendizado não precisa ser reajustada. É argumento de escala, não teorema, e está no A.3."

**Item 4 — "Como é que o gradiente passa por um peso de quatro bits?" (A.4, ~3 min).**
Aparece sempre que a turma tem gente que já ouviu falar de treino consciente de quantização, e é uma pergunta de quem entendeu. A resposta é curta e não precisa de quadro: ele não passa pela função de quantização. O peso está congelado, ninguém pede derivada em relação a ele, e o peso descomprimido entra na conta como constante multiplicativa. Se der para gastar um minuto a mais, eu escrevo as duas expressões do backward e aponto o `W` aparecendo como fator nas duas, e nenhum termo pedindo derivada em relação a ele.
**Versão de 30 segundos:** "ele não passa pela quantização. O peso está congelado, então ninguém pede a derivada em relação a ele — ele entra na conta como constante que multiplica. É exatamente isso que separa o QLoRA do treino consciente de quantização, que precisa de um estimador aproximado porque lá o objetivo é atualizar o peso quantizado. Está no A.4."

**Item 5 — "Por que cento e doze gigabytes e não sessenta?" (A.5, ~3 min no quadro).**
Se alguém contestar o número do slide 9, o que é ótimo. Eu escrevo os cinco consumidores em coluna: peso dois, gradiente dois, cópia mestre quatro, primeiro momento quatro, segundo momento quatro. Soma dezesseis. Vezes sete bilhões. E aponto que essa decomposição é de ontem, A.4 da Aula 12, e que o que este apêndice acrescenta são as outras duas linhas da tabela.
**Versão de 30 segundos:** "dezesseis bytes por parâmetro, e a decomposição nos cinco consumidores é a de ontem, A.4 da Aula 12. Vezes sete bilhões dá cento e doze gigabytes. As três configurações lado a lado, com as ativações contadas separadamente e a conta em FLOPs, estão no A.5 desta aula."

**Item 6 — "Mas o que é quantizar, exatamente?" (A.6, ~5 min no quadro — e eu evito).**
É a melhor pergunta desta lista e a que eu tenho **menos** vontade de responder em sala, porque ela vem no slide 12 e cinco minutos ali saem do framework de decisão, que é o clímax. Então a resposta padrão é a régua, em quinze segundos: em vez de guardar o número, eu guardo em qual das duzentas e cinquenta e seis marcas de uma régua ele caiu, mais a régua. Se eu decidir gastar os cinco minutos — e o único lugar de onde eles saem sem estrago é o exercício do slide 15, encurtado de cinco para três —, o que eu escrevo no quadro não são as fórmulas, é **um exemplo**. Um bloco de pesos entre menos zero vírgula um e zero vírgula um, e um intruso em dois. Calculo a constante com o intruso e sem ele, e mostro o mesmo peso de zero vírgula zero cinco voltando com erro sete vezes maior por causa de um vizinho que ele nunca viu. Aí a pergunta seguinte se responde sozinha: é por isso que o QLoRA quantiza em blocos de sessenta e quatro e não o tensor inteiro. As duas fórmulas, a regra de escolha entre absmax e ponto-zero, e o lugar do QLoRA na taxonomia PTQ × QAT — que não é nenhum dos dois — estão em A.6.
**Versão de 15 segundos:** "trocar a régua: em vez do número, guardo em qual marca ele caiu, mais a régua. Tem dois jeitos de posicionar essa régua, e a escolha é pela forma da distribuição — está em A.6."

---

## Encerramento · 01:50–02:00

O encerramento está redigido como fala no Slide 16 da Parte 1 — os três sintomas fechados com as etiquetas descobertas, o mapa dos cinco checkpoints do Lab 4 com os números esperados, o A.5 nomeado em voz alta como a conta que fechou o sintoma 2 e que o apêndice do lab vai aplicar, o fechamento do laço com a segunda coluna do Lab 3, o aviso sobre GPU no Colab e as duas leituras com a pergunta dirigida do LoRA.

> 🗣️ "No Lab 3 vocês mediram uma coluna de respostas fora do formato e reportaram ela honestamente. Amanhã essa coluna vai a zero com cem exemplos e zero vírgula seis por cento dos parâmetros. Few-shot é crachá; fine-tuning é uniforme."

---

*Roteiro do Instrutor · Aula 13 de 30 (V2) · Grandes Modelos de Linguagem: do Transformer aos Agentes de IA · 60h · Eletiva de Graduação em Ciência da Computação · CESAR*
