---
aula: 27
titulo: "Avaliação de LLMs e de sistemas com LLMs"
modulo: "6 — Avaliação de LLMs"
tipo: teorica
semana: 14
duracao_min: 120
versao: v2
---

# Aula 27 — Avaliação de LLMs e de sistemas com LLMs

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** Cada bloco do argumento abre por um **sintoma de equipe** — quatro
> semanas ajustando o prompt de um sistema cujo recuperador nunca entregou o documento certo;
> um número que subiu de 0,71 para 0,78 em vinte casos; um juiz que muda de vencedor quando se
> troca a ordem; um modelo que lidera o ranking e é o pior no caso de uso. A matemática entra
> depois, **enunciada e lida, nunca derivada no quadro**, e a derivação completa fica no
> apêndice do deck (A.1 a A.4). Objetivos de aprendizagem, carga horária e numeração
> permanecem os da V1. O que muda é a ordem de apresentação, o lugar da derivação e o verbo
> cobrado: de "calcular kappa" para "diagnosticar por que aquele acordo bruto não significa
> nada".

## 1. Objetivo da aula

Substituir a pergunta "esse LLM é bom?" — que não tem resposta — pela pergunta que tem: **qual é a menor camada do sistema que explica esta falha, e com que número eu a meço?** E, junto com ela, instalar a segunda pergunta, que a V2 promove a par da primeira: **esse número se moveu, ou só pareceu se mover?** É a aula em que a disciplina paga a dívida anunciada na Aula 1: o modelo foi unificado sob o próximo-token, as métricas não foram.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Decompor** um sistema com LLM dentro em camadas avaliáveis (modelo, prompt, retriever, ferramenta, resposta final, trajetória, produto) e **atribuir** uma falha observada à menor camada que a explica.
2. **Escrever** uma rubrica de anotação humana com níveis discriminantes e **calcular** o kappa de Cohen entre dois anotadores, **justificando** por que o acordo bruto superestima a concordância.
3. **Explicar** por que BLEU e ROUGE deixam de medir qualidade em geração aberta e **identificar** os casos em que ainda são a métrica correta.
4. **Distinguir** LLM-as-judge pairwise de LLM-as-judge por rubrica e **nomear** os três vieses do juiz (posição, verbosidade, autopreferência) com o protocolo que mitiga cada um.
5. **Medir** a inconsistência posicional de um juiz rodando o mesmo par nas duas ordens e **interpretar** a taxa de inversão como limite superior de confiança naquele número.
6. **Avaliar** factualidade por decomposição em afirmações atômicas verificadas contra a fonte, em vez de por impressão global de qualidade.
7. **Argumentar** por que posição em leaderboard não substitui avaliação de produto, citando contaminação de dados e desalinhamento de distribuição.

*(Idênticos aos da V1. O que mudou foi o verbo dominante em torno deles: de "calcular" e
"descrever" para "diagnosticar" e "justificar" — a matemática permanece cobrada, como
ferramenta de justificativa. Cada resultado tem, no apêndice do deck, o item que o fundamenta:
2 → A.1, 3 → A.3, 5 → A.2, 6 → A.4.)*

## 3. Teoria aplicada

Cada conceito abaixo é apresentado pelo **comportamento observável** que o motiva — na maior parte dos casos, um prejuízo real de equipe —, com o fundamento matemático nomeado e a derivação remetida ao apêndice.

### Bloco 1 (00:10–00:55) — De que camada é essa falha, e o número se moveu mesmo?

**Conceito 1 — O sintoma de abertura: quatro semanas na camada errada.**
*Comportamento observável:* uma equipe de RAG recebe "a resposta está errada", itera no prompt por quatro semanas — instrução reescrita três vezes, few-shot, formato padronizado, modelo maior — e a qualidade percebida não muda. Ao ligar o log do ranking recuperado, descobre que o documento certo não estava entre os cinco recuperados em quase metade dos casos.
*Por que a intuição sozinha não basta:* nenhuma quantidade de prompt conserta um contexto que não tem a informação. O modelo estava respondendo bem sobre o texto errado.
*Erro conceitual comum:* achar que a camada errada é a que se manifesta. O usuário reclama da resposta final; a falha quase sempre está numa camada abaixo.

**Conceito 2 — "Esse modelo é bom?" é uma pergunta mal formada.**
*Comportamento observável:* a nota global sobe e desce entre iterações e não indica onde mexer — é o termômetro sem escala que permitiu as quatro semanas do Conceito 1.
Não existe "o LLM" para avaliar num sistema real. Há um modelo base, um prompt de sistema, um retriever, um conjunto de ferramentas, um loop de agente, uma resposta final renderizada e um produto que o usuário aprova ou abandona. Uma nota única sobre esse conjunto é a média de sete coisas diferentes — e média de camadas não localiza defeito.
*Analogia do instrutor:* é a diferença entre "o carro está ruim" e "o carro puxa para a direita a partir de 80 km/h". A segunda frase tem oficina; a primeira tem só opinião.

**Conceito 3 — As sete camadas e a regra de ouro.**
A regra é: **avaliar a menor camada que explica a falha**. Menor no sentido de mais barata de medir, mais determinística e mais próxima da causa. No Conceito 1, o número que faltava era `recall@5` — custa um log e nenhuma anotação humana, contra quatro semanas de iteração. Medir a camada de cima quando a de baixo explica a falha é comprar ruído: a métrica de cima flutua com o modelo, com a temperatura e com o juiz, e não aponta o conserto.
*Analogia:* é bissecção de bug. Ninguém depura um sistema distribuído lendo só a mensagem de erro do front-end.
*Erro conceitual comum:* o inverso — descer *demais*. Se o retriever traz o dispositivo certo em 95% dos casos e a resposta continua errada, insistir em recall é fuga. A regra é a *menor camada que explica*, não a menor camada existente.

**Conceito 4 — Exercício de atribuição de camada.**
Quatro falhas descritas como o usuário as reportaria; a turma decide, em dupla, que camada medir, com que número, e **que dado precisa estar logado** para esse número existir depois do fato. O objetivo é treinar o reflexo de tradução: da queixa em linguagem natural para uma métrica com denominador.
*Erro conceitual comum:* responder "avaliação humana" para tudo. Anotação humana é caríssima em tempo de aluno; ela é o instrumento de *calibração* e de casos genuinamente subjetivos, não o instrumento de primeira linha.

**Conceito 5 — O número que subiu e não quer dizer nada.** *(novo na V2)*
*Comportamento observável:* uma equipe troca o retriever, a taxa de acerto vai de **0,71 para 0,78** e a mudança é declarada uma melhora. O conjunto tem **20 casos**.
*O que a aritmética diz:* com `n = 20`, cada caso vale 5 pontos percentuais. Sete pontos é **um caso e meio** mudando de lado. E a incerteza de uma proporção medida em 20 casos é larga o bastante para que os dois números sejam indistinguíveis.
*Por que este sintoma é o mais caro dos quatro:* ele não produz paralisia, produz **decisão errada com aparência de evidência** — um componente novo entra no sistema, com custo de latência e manutenção, por causa de ruído.
*Amarração com o curso:* é a mesma estrutura de erro do Checkpoint 5 do Lab 2 (Aula 9), onde 500 passos com uma semente não distinguiam duas configurações. Lá o ruído era da semente; aqui é da amostra. A conta — intervalo de confiança de proporção e o teste pareado apropriado — é conteúdo do **Lab 8 (Aula 28)** e está no apêndice de lá.
*Regra de higiene que fica:* **o `n` vai do lado de todo número.** Sem denominador, uma taxa é uma opinião com vírgula.

**Conceito 6 — Avaliação humana: a rubrica é o instrumento, não a opinião.**
*Comportamento observável:* dois anotadores da mesma equipe, com a mesma rubrica, produzem rótulos diferentes para o mesmo caso — e o problema não são eles.
Três decisões constituem uma anotação utilizável: (i) a **unidade** anotada (a resposta inteira? cada afirmação? o par ordenado?); (ii) a **escala** com níveis descritos por comportamento observável, não por adjetivo — "cita o dispositivo correto e não adiciona informação ausente da fonte" discrimina; "boa" não discrimina; (iii) **múltiplos anotadores** sobre um subconjunto sobreposto, porque um anotador sozinho não tem contra quem errar.
*Analogia:* a rubrica é o teste unitário do julgamento humano — se dois anotadores rodam o mesmo caso e obtêm resultados diferentes, o teste é que está mal escrito.
*Erro conceitual comum:* escala de 1 a 10. Ninguém distingue 6 de 7 de forma reprodutível. Três a quatro níveis com âncoras textuais produzem acordo muito maior.

**Conceito 7 — Acordo de 84% que vale kappa de 0,11.**
*Comportamento observável:* dois anotadores concordam em 84% de 50 casos e o relatório reporta "boa concordância". O conjunto é desbalanceado — ~90% das respostas estão corretas —, e dois anotadores que marcassem "correta" no automático já concordariam em ~81%.
*Fundamento nomeado e lido:*
```
κ = (p_o − p_e) / (1 − p_e)          p_e = Σ_c P₁(c) · P₂(c)
```
`p_o` é o acordo observado; `p_e` é o acordo esperado por acaso, calculado a partir de quanto **cada anotador usa cada rótulo**. Leitura que fica: o numerador é o acordo que sobrou, o denominador é o acordo que estava disponível — `κ` é a **fração do acordo conquistável que foi conquistada**. No caso: `p_o = 0,84`, `p_e = 0,82`, `κ ≈ 0,11`.
Leitura prática em três casos: `κ ≈ 0` é o mesmo que sortear; `κ` alto com `p_o` alto é acordo real; `p_o` alto com `κ` baixo é o sinal de que a tarefa é desbalanceada e a anotação não está medindo nada. Para mais de dois anotadores, o análogo é o kappa de Fleiss.
*Fundamento e derivação:* tabela 2×2 completa que produz o 0,11, derivação de `p_e` a partir das marginais, o caso balanceado com o mesmo `p_o` dando `κ = 0,68`, os quatro casos-limite e o kappa **ponderado** para escalas ordinais (que é o que o Lab 8 usa, com três níveis). → **A.1**
*Erro conceitual comum:* reportar só `p_o` — é o erro que a rubrica do projeto penaliza no item de rigor. O segundo: interpretar faixas de kappa como lei da natureza. As faixas são convenção editorial; a referência é o kappa entre **dois humanos** na mesma tarefa, que é o teto.

**Conceito 8 — A dívida da Aula 1: BLEU e ROUGE em geração aberta.**
*Comportamento observável, com números:* referência `"o prazo de trancamento é de trinta dias"`. Um candidato **correto** — `"o aluno tem um mês para solicitar o trancamento"` — recebe BLEU perto de 0. Um candidato **errado** — `"o prazo de trancamento é de treze dias"` — recebe BLEU ≈ 0,87. A métrica erra nas duas direções.
*A premissa que ninguém enuncia:* existe uma referência e ela é **aproximadamente única**. Em geração aberta essa premissa cai: há muitas respostas boas mutuamente diferentes, e sobreposição de n-gramas passa a medir estilo.
*Fundamento nomeado e lido:* `BLEU = BP · exp(Σ wₙ log pₙ)` — precisão de n-gramas com corte de contagem, média geométrica (um `pₙ` zerado zera tudo), e penalidade de brevidade (sem ela, "o" seria tradução perfeita). `ROUGE-N` troca o denominador para a referência, virando revocação; `ROUGE-L` usa a maior subsequência comum.
*Onde eles continuam certos:* tarefa com saída canônica e curta — tradução com referência profissional, sumarização extrativa com resumo de ouro, conversão de formato, extração estruturada. Aí a referência é quase única e a métrica é barata, determinística e não precisa de juiz.
*Fundamento e derivação:* clipping com o exemplo que ele resolve, média geométrica contra aritmética, penalidade de brevidade verificada nos extremos, os dois exemplos numéricos completos e a medida F do ROUGE-L. → **A.3**
*Erro conceitual comum:* a conclusão preguiçosa "então métrica automática não serve". Serve — e a regra é a mesma do Conceito 3: métrica determinística na camada em que a saída é canônica, juiz e humano na camada em que ela não é.

### Bloco 2 (01:05–01:50) — LLM-as-judge, factualidade e o que leaderboard não mede

**Conceito 9 — LLM-as-judge: pairwise × rubrica.**
Duas formas, com propriedades diferentes. **Pairwise:** mostrar duas saídas para o mesmo insumo e pedir a melhor. É mais fácil para o juiz, produz sinal para ordenar sistemas, e **não** produz nota absoluta — não serve para responder "está bom o suficiente?". Custo em chamadas cresce com o número de sistemas comparados. **Rubrica (pointwise):** dar os critérios e pedir nota por critério. Produz nota absoluta, comparável entre execuções e rastreável ao critério que caiu, mas é muito mais sensível à redação da rubrica e tende a comprimir tudo no topo da escala.
*Analogia:* pairwise é um campeonato; rubrica é uma prova com gabarito. Campeonato ordena, prova aprova.
*Erro conceitual comum:* usar pairwise para decidir se o sistema está pronto para produção. Pairwise diz "melhor que aquele", não "bom o bastante".
*Gancho para o Lab 8:* o uso legítimo de pairwise no projeto é comparar duas versões do próprio sistema — e como as duas rodam nos **mesmos** casos, a comparação é pareada, o que reaparece no Lab 8 como o teste apropriado.

**Conceito 10 — O juiz que muda de opinião quando se troca a ordem.**
*Comportamento observável:* o mesmo par, o mesmo prompt, a mesma rubrica, temperatura 0 — e o vencedor muda porque a resposta B foi apresentada antes da A. Não é ruído de amostragem: com temperatura 0 não há amostragem. É o instrumento.
Três vieses, cada um com protocolo: (i) **posição** — julgar nas duas ordens e tratar quem inverteu como empate; a **taxa de inversão** `τ` é o número que qualifica a confiança no resultado; (ii) **verbosidade** — resposta mais longa é lida como mais completa; protocolos são concisão como critério explícito, controle de comprimento, e reportar a correlação entre vencer e ser mais longo; (iii) **autopreferência** — o juiz favorece texto da própria família; protocolo é juiz de família diferente, e nunca o mesmo modelo como gerador e juiz sem declarar.
*Fundamento nomeado:* se o juiz fosse função só da qualidade, `τ = 0` exatamente. E vale a relação `π ≈ 0,5 + τ/2`, onde `π` é a fração de vitórias de quem aparece primeiro — **medir uma estima a outra**, e a demo confere isso na tela.
*Fundamento e derivação:* definição formal de `τ`, o modelo de escore latente com bônus de posição que produz os três regimes, a derivação de `π = 0,5 + τ/2`, a demonstração de que `|α_AB − α_BA| ≤ τ` (por que `τ` é limite superior de confiança), o preço exato do protocolo de dupla ordem (cobertura `1 − τ`, chamadas `2n`), e por que os pares descartados são justamente os informativos. → **A.2**
*Erro conceitual comum:* achar que temperatura 0 resolve. Temperatura 0 dá reprodutibilidade, não ausência de viés — o juiz determinístico erra sempre igual, e é isso que a demo mostra.

**Conceito 11 — Calibrar antes de escalar.**
*Comportamento observável:* um relatório com um número de juiz e nenhuma medida de concordância — uma opinião com aparência de número.
O procedimento é sempre o mesmo: anotar à mão uma amostra do próprio conjunto de teste (40 a 60 casos já dizem muito), rodar o juiz nos mesmos casos, medir concordância com kappa, **inspecionar os desacordos** e corrigir — na maioria das vezes o conserto é na rubrica, não no modelo. Só depois disso o juiz é liberado para rodar nos 500 casos que ninguém tem tempo de anotar.
*Analogia:* o juiz é um estagiário. Ele não começa assinando laudo; começa fazendo cinquenta laudos que alguém confere.
*O teto, promovido a ponto central na V2:* o kappa entre **dois humanos** na mesma tarefa é o máximo que qualquer juiz pode atingir. Se dois integrantes concordam com `κ = 0,6`, exigir `0,9` do juiz é exigir mais do que a definição da tarefa entrega. Medir esse teto custa uma segunda anotação. → **A.1**
*Erro conceitual comum:* calibrar em casos fáceis. A amostra de calibração precisa incluir os casos de fronteira, porque é exatamente ali que o juiz decide o resultado do relatório.

**Conceito 12 — Factualidade: decompor em afirmações atômicas.**
*Comportamento observável:* uma resposta com seis afirmações e uma errada não tem nota binária, e uma nota de 1 a 5 põe "cinco certas e uma inventada" no mesmo lugar que "tudo inventado".
O procedimento: (i) quebrar a resposta em **afirmações atômicas** verificáveis isoladamente; (ii) buscar suporte na fonte; (iii) rotular *suportada*, *contradita* ou *não verificável pela fonte*; (iv) reportar a proporção suportada, e **separadamente** a taxa de contraditas.
*Por que duas métricas e não uma:* elas **não** são complementares, porque o terceiro rótulo existe. Três suportadas e três não verificáveis dá precisão 0,50 com zero contraditas — resposta **incompleta**. Três suportadas e três contraditas dá a mesma precisão 0,50 — resposta **falsa**. A primeira é defeito de escopo; a segunda é alucinação, e os consertos são diferentes.
*Analogia:* é diff por linha em vez de "o arquivo está diferente".
*Fundamento e derivação:* `P = |S|/m` e `C = |C|/m` com `P + C + N = 1`; as duas agregações sobre o conjunto de teste (micro, por afirmação; macro, por resposta) com o exemplo numérico em que elas dão 0,571 e 0,750 nos mesmos dados; os três casos-limite (recusa com `m = 0`, decomposição inflacionada, afirmação parcialmente suportada). → **A.4**
*Erro conceitual comum:* confundir *não suportada pela fonte* com *falsa*. A afirmação pode ser verdadeira no mundo e ausente do documento — em sistema com citação, isso ainda é defeito, mas é defeito de escopo e não alucinação. O segundo erro, que só aparece no relatório: não declarar se a agregação foi micro ou macro.

**Conceito 13 — O modelo que lidera o leaderboard e é o pior no caso de uso.**
*Comportamento observável:* a equipe escolhe o primeiro colocado do ranking e ele é o pior dos candidatos na papelada da secretaria acadêmica.
Três razões independentes. **Distribuição:** o benchmark tem a distribuição do benchmark, e o produto tem a dos usuários. **Camada:** leaderboard mede o modelo; o produto é o sistema, e trocar o retriever costuma mover mais o resultado final que trocar o modelo — é literalmente o Conceito 1. **Restrição:** latência, custo por requisição, limite de contexto, política de privacidade e disponibilidade regional não aparecem em nenhuma coluna do ranking, e são frequentemente o que decide a escolha.
*Analogia:* é escolher pneu pela velocidade máxima quando o carro nunca passa de 60 e o problema é chuva.
*Ressalva que fecha o círculo com o Conceito 5:* o conjunto de teste próprio é melhor que o leaderboard porque tem a distribuição certa — e, com 20 casos, também não distingue dois candidatos a sete pontos de distância.
*Erro conceitual comum:* o inverso, que também aparece: descartar benchmark como inútil. Benchmark é bom para triagem inicial de candidatos e para detectar regressão grosseira. Ele não é o critério de aceitação.

**Conceito 14 — O que o MMLU mede bem, e por que isso é pouco.**
MMLU (Hendrycks et al., *Measuring Massive Multitask Language Understanding*, arXiv 2009.03300) é múltipla escolha de quatro alternativas em 57 áreas, com linha de base aleatória de 25%. O formato é o que o torna barato e comparável: gabarito único, correção automática, nenhuma ambiguidade de referência — o **oposto exato** do problema do Conceito 8. É exatamente por isso que ele mede pouco do que um sistema em produção faz: não há geração aberta, ferramenta, trajetória nem usuário.
**Contaminação de dados** é a ameaça estrutural: o benchmark é público, o pré-treino raspa a web, e não há garantia de que as questões não estejam no corpus. Sintomas: salto num benchmark antigo sem salto correspondente em benchmark novo de dificuldade equivalente; desempenho que cai sob paráfrase ou reordenação de alternativas.
*Erro conceitual comum:* tratar contaminação como fraude deliberada. Na maioria dos casos é consequência de raspar a web em escala — o que não a torna menos fatal para a conclusão.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura pelo sintoma | **Quatro semanas ajustando o prompt errado** — a equipe que iterou um mês na única camada que não estava quebrada, e o `recall@5` que faltava; recap da Aula 26 generalizado (hoje é qualquer coisa que tenha um LLM dentro); a dívida da Aula 1 cobrada por um prejuízo, não por uma promessa; por que a nota global é um termômetro sem escala. Status da Entrega 2 nos dois primeiros minutos |
| 00:10 | 45 min | Bloco 1 — camadas, ruído e o limite da referência | As sete camadas e a regra da menor camada, amarrada à história da abertura; **exercício em dupla de atribuição de camada (8 min)**; **o número que subiu de 0,71 para 0,78 em 20 casos (6 min, novo)**; avaliação humana e rubrica com níveis observáveis; **acordo de 84% e κ ≈ 0,11 — fórmula lida, não derivada (→ A.1)**; a dívida da Aula 1 — BLEU/ROUGE com os dois candidatos numéricos e onde ainda são a métrica certa (→ A.3) |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — juiz, factualidade e benchmarks | LLM-as-judge pairwise × rubrica; **o juiz que muda de opinião quando se troca a ordem** — os três vieses e a relação `π ≈ 0,5 + τ/2` enunciada (→ A.2); **demo `demo-judge-bias.py` (10 min)** com a taxa de inversão na tela **e a verificação numérica da relação**; calibração contra rótulo humano e o teto humano-humano (→ A.1); factualidade por afirmações atômicas, com as duas métricas não complementares (→ A.4); **o modelo que lidera o ranking e é o pior no caso de uso**; MMLU (2009.03300) e contaminação |
| 01:50 | 10 min | Fechamento | Os quatro prejuízos e as quatro respostas; a dívida da Aula 1 quitada com uma **regra**, não com uma métrica; o `n` ao lado de todo número; **índice do apêndice projetado por 20 s**, com a indicação de que A.1 é o Checkpoint 4 do Lab 8; o que cada equipe traz para a Aula 28; leitura indicada |

*Comparação com a V1: a derivação do kappa saiu do quadro (eram ~7 min de conta conduzida) e
virou fórmula lida em 2 min, com A.1 mais completo do que a conta que se fazia. Os minutos
liberados foram para o **slide novo do 0,71 → 0,78** (6 min), que é o sintoma que mais muda
comportamento de equipe. O total de 120 min é preservado, assim como a duração do exercício
(8 min) e da demo (10 min).*

## 4. Demonstração guiada

**Demo `codigo/demo-judge-bias.py` — 10 min, no terminal, sem rede obrigatória.**

A demo mede a **inconsistência posicional** de um LLM-as-judge: doze pares de respostas sobre o regulamento acadêmico fictício do Lab 5, cada par julgado duas vezes — na ordem (A, B) e na ordem (B, A). Se o juiz fosse função da qualidade, o vencedor seria o mesmo. A taxa de inversão é o número que a demo existe para imprimir.

**O que a V2 acrescenta:** a demo deixa de ser só ilustração do viés e passa a ser **a verificação da relação enunciada no fluxo**. O slide 10 enuncia `π ≈ 0,5 + τ/2` sem derivar; o passo 4 da demo confere na tela, em dez segundos, que os dois números impressos satisfazem a relação. É a evidência que substitui a derivação — e ela é o passo que **não** se corta.

O script tem duas rotas e **a rota padrão é offline**: um juiz sintético determinístico, com semente fixa e hash estável entre máquinas, cujo escore soma quatro parcelas explícitas — plausibilidade da resposta, bônus para quem aparece primeiro, bônus para quem escreve mais, e ruído pequeno. Ele não mede modelo nenhum: reproduz o mecanismo, com número reprodutível na frente da turma. A rota `--modo api` roda o mesmo experimento com um juiz de verdade, com a chave lida de `API_KEY` ou por `getpass`, e cai para o juiz sintético par por par se a chamada falhar.

Passos em alto nível:

1. Abrir o arquivo e mostrar o dicionário de um par: a pergunta, as duas respostas, o rótulo humano `melhor` e a plausibilidade de cada resposta. Cravar a distinção: `melhor` é correção verificada contra a fonte; `plaus_*` é o quanto a resposta *soa* certa para quem não tem a fonte. O juiz só vê a segunda coisa.
2. Mostrar as três armadilhas plantadas: pares em que a errada é a mais longa; pares em que as duas respostas são equivalentes; pares em que a certa é a mais seca.
3. Rodar `python demo-judge-bias.py` e ler a tabela linha por linha, parando no primeiro `>>> INVERTEU`: mesmo par, mesmo prompt, vencedor diferente.
4. **[Passo insubstituível]** Ler o bloco de métricas na ordem em que ele imprime — taxa de inversão, preferência pela primeira posição, preferência pela mais longa — e **fazer a conta em voz alta**: meio mais metade da taxa de inversão, e conferir que bate com a preferência pela primeira posição. Sem viés, seriam 0% e 50%. A derivação está em A.2; aqui a turma vê a relação valer.
5. Comparar as duas linhas de acordo com o humano — só ordem (A, B) contra só ordem (B, A). São dois números diferentes para o mesmo juiz e o mesmo conjunto, e a distância entre eles é limitada pela taxa de inversão (demonstrado em A.2). Qualquer relatório que rode uma ordem só escolheu um deles sem saber.
6. Rodar `python demo-judge-bias.py --protocolo` e mostrar o conserto: manter só os pares que não inverteram, tratar o resto como empate. Nomear o preço — cobertura `1 − τ`, o dobro de chamadas, e o fato de que os pares descartados são exatamente os próximos em qualidade, isto é, os informativos.
7. Fechar no ponto que a demo faz questão de mostrar: entre os pares consistentes o juiz **ainda** não concorda com o humano em dois casos, e são os dois em que a resposta falsa é a mais plausível. Consistência não é acerto; isso é factualidade, e o conserto é decompor e verificar contra a fonte.
8. Se houver rede e chave, repetir o passo 3 com `--modo api` e comparar as duas taxas de inversão — a sintética e a real.

**Números que a demo produz e que a aula usa como evidência (§7 do contrato):** a taxa de inversão `τ`; a preferência pela primeira posição `π`, conferida contra `0,5 + τ/2`; a preferência pela resposta mais longa; e as **duas** taxas de acordo com o humano, uma por ordem. Os quatro reaparecem no Checkpoint 4 do Lab 8, agora sobre o juiz da própria equipe.

Insumos preparados na véspera: a saída do modo offline salva em arquivo de texto (é determinística, então serve de plano B integral) e, se houver chave, a saída do `--modo api` também salva, com o nome do modelo e a data da execução anotados.

## 5. Hands-on

**Componente prático da unidade — exercício em dupla "de que camada é essa falha?" (8 min, 00:18–00:26).**

Quatro falhas projetadas, redigidas como o usuário as reportaria. Cada dupla escreve, para cada uma: (a) a menor camada que explica a falha, (b) a métrica com denominador que a mede, (c) o dado que precisaria estar registrado para essa métrica ser calculável depois do fato.

1. "Perguntei o prazo de trancamento fora do período e ele respondeu sobre trancamento total." (retrieval → `recall@k` sobre o dispositivo correto; exige log do ranking recuperado por consulta)
2. "A resposta cita o Art. 42, mas o Art. 42 não diz isso." (factualidade/atribuição → proporção de afirmações suportadas pelo trecho citado; exige log do chunk citado junto da resposta)
3. "O agente ficou dando voltas e parou sem responder." (trajetória → taxa de sucesso e distribuição de passos até a parada; exige log da trajetória completa, e não só da resposta final)
4. "Está tudo certo, mas ninguém da secretaria usou depois da primeira semana." (produto → taxa de retorno e de abandono por sessão; nenhuma métrica de resposta detecta isso, e nenhum log do sistema tem o dado)

**Amarração nova na V2:** o caso 1 é exatamente a falha da história de abertura. A dupla que o resolve corretamente **reconstrói sozinha o número que a equipe do slide 1 não tinha** — e é assim que a correção começa, com o instrutor apontando isso em voz alta.

*Critério de conclusão observável:* a dupla entrega quatro linhas com a camada e a métrica nomeadas, e ao menos uma dupla defende em voz alta por que não escolheu a camada de cima. Correção conduzida pelo instrutor em 3 min, com foco no caso 2 (a queixa é sobre a resposta, a métrica é sobre a afirmação) e no caso 4 (a camada de produto não é medível com os logs que o sistema tem — é decisão de instrumentação, tomada antes).

*Extensão para quem terminar antes (opcional):* acrescentar uma quinta linha com uma falha do **próprio projeto** da equipe, seguindo o mesmo formato. Essa linha vale mais que as quatro do slide, porque ela vai direto para o Checkpoint 2 do Lab 8.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Sem rede ou sem chave de API** na hora da demo | Falha na primeira requisição | A rota padrão da demo já é offline e determinística: o juiz sintético imprime a mesma tabela sem rede. A saída salva na véspera cobre até falha total de máquina |
| **Rate limit** do free tier no `--modo api` | Erro 429 em alguns pares | O script cai para o juiz sintético par por par e avisa na tela; a demo continua e o instrutor declara quais linhas são sintéticas |
| **Turma pedir a conta do kappa** (era derivada no quadro na V1) | "De onde saiu esse 0,11?" | Ler a fórmula, cravar a leitura "fração do acordo conquistável", e remeter a A.1. Se sobrar tempo, a Parte 4 do roteiro tem a condução em 5 min — e o preço é o slide 15 (MMLU), que sustenta sozinho e é coberto pela leitura pós-aula |
| **Turma pedir a conta do intervalo de confiança** no slide 5 | "Como você sabe que 0,71 e 0,78 são o mesmo?" | Resposta de 30 s (erro-padrão da ordem de 10 p.p. com `n = 20`) e adiamento deliberado para o Lab 8, onde ela vira código. Parte 4, item 2 — 3 min se a turma insistir |
| **Turma sentir que "a aula ficou menos rigorosa"** | Comentário de que a V1 tinha mais conta | Projetar A.1 por 30 s: é mais matemática do que se fazia no quadro, com casos-limite e kappa ponderado que a V1 não tinha. O rigor não saiu, mudou de lugar — e agora é consultável antes do Lab 8 |
| **Ceticismo generalizado** ("então nada é confiável") | Turma desiste de medir | Voltar à regra da menor camada: `recall@k` é barato, determinístico e não precisa de juiz. A desconfiança é sobre a camada de cima, não sobre medir |
| **Confusão entre juiz e modelo avaliado** | Aluno pergunta se o juiz precisa ser melhor que o sistema | Separar explicitamente os dois papéis no slide das camadas e citar autopreferência: juiz de família diferente, declarado no relatório |
| **Aula estourar no Bloco 1** (as sete camadas geram discussão longa) | 00:40 e ainda em rubrica | Comprimir o Conceito 8 (BLEU/ROUGE) para 4 min — a turma já viu isso na Aula 1 e o slide serve de recap, e os dois candidatos numéricos sustentam o ponto sozinhos — e proteger o Bloco 2, que é o que o Lab 8 cobra. **Não comprimir o slide 5:** ele é o que muda comportamento |
| **Equipes com Entrega 2 atrasada** perguntam sobre nota em vez de conteúdo | Perguntas de logística nos primeiros minutos | Responder em bloco na abertura, em dois minutos, e remeter o resto para o fim da aula; o conteúdo de hoje é pré-requisito do Lab 8 e não pode ser cortado |

## 7. Artefatos produzidos

- Anotação do exercício em dupla: tabela **falha → camada → métrica → dado que precisa estar logado**, com quatro linhas (cinco, para quem fez a extensão com uma falha do próprio projeto), no repositório do aluno.
- Saída da demo salva pelo aluno (ou copiada da tela) com a **taxa de inversão**, a **preferência pela primeira posição** e as duas linhas de acordo com o humano — é o conjunto de números que o Checkpoint 4 do Lab 8 vai pedir para o juiz da própria equipe.
- **A verificação da relação `π ≈ 0,5 + τ/2`** anotada com os números da execução do dia. É o artefato novo da V2 e é o que prova que a fórmula do slide 10 não é decoração.
- **Esboço da rubrica do projeto**: dimensão avaliada, três a quatro níveis com âncoras observáveis, e a unidade anotada. Sai desta aula em rascunho e entra no Lab 8 como insumo.
- Decisão registrada, por equipe, de **quais camadas o projeto vai medir** — no mínimo uma métrica de recuperação ou de ferramenta, uma de resposta final e, se houver loop, uma de trajetória.

## 8. Desafio pós-aula

Não avaliado, mas é preparação direta do Lab 8 — quem chega sem isso perde o primeiro checkpoint.

1. **Anotar dez casos do próprio projeto.** Rodar o sistema em dez entradas reais, salvar as saídas e rotular cada uma com uma rubrica de três níveis escrita pela própria equipe. Anotar duas vezes, por duas pessoas diferentes da equipe, e calcular o acordo bruto e o kappa. Se o kappa vier baixo, o problema é a rubrica: reescrever os níveis e anotar de novo. **Este kappa humano-humano é o teto do Checkpoint 4** — guardar o número.
2. **Rodar a demo com uma semente diferente** (`--semente turma-b`) e responder duas coisas: a taxa de inversão mudou? E a relação `π ≈ 0,5 + τ/2` continuou valendo? A segunda pergunta é a que interessa — se ela valer em duas sementes, a relação não é artefato de uma execução.
3. **Leitura.** Hendrycks et al., *Measuring Massive Multitask Language Understanding* (arXiv 2009.03300) — a seção que descreve a construção do conjunto de tarefas. **Pergunta dirigida:** o formato de múltipla escolha com gabarito único é o que faz o benchmark ser barato e comparável. Nomeie duas capacidades que o seu projeto precisa ter e que esse formato é estruturalmente incapaz de medir — e diga com que número você mediria cada uma.
4. **Leitura do apêndice, dirigida.** Ler **A.1** antes da Aula 28. É o item que o Checkpoint 4 do Lab 8 implementa, e quem chega com ele lido faz o checkpoint na metade do tempo. Pergunta para responder em três linhas: no exemplo da tabela 2×2, o que precisaria mudar no **conjunto** — e não nos anotadores — para o mesmo acordo bruto de 0,84 produzir um kappa alto?

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado próprio**. Ela é o suporte conceitual do **Lab 8 (Aula 28)**, que compõe os **30%** de laboratórios, e do item de **rigor da avaliação quantitativa — 30% da nota do projeto final** na rubrica da ementa (técnica 40%, avaliação 30%, relatório 20%, apresentação 10%). Nenhum peso novo é criado aqui.

O que esta aula estabelece como exigível nas entregas seguintes:

- **Métrica por camada, não nota global.** Um relatório de projeto com "o sistema respondeu bem em 8 de 10 perguntas" e nenhum número por camada perde o item de rigor, independentemente de o sistema funcionar.
- **Denominador ao lado do número.** *(reforçado na V2)* Toda taxa vem com o seu `n`. Uma diferença entre duas versões do sistema só é apresentada como melhora se a equipe disser quantos casos mudaram de lado — porque "sete pontos percentuais em vinte casos" é "um caso e meio".
- **Juiz declarado e calibrado.** Todo número produzido por LLM-as-judge vem acompanhado de: modelo e família do juiz, forma (pairwise ou rubrica), rubrica usada, e a concordância medida contra amostra anotada por humano — com kappa, não só acordo bruto. E, quando disponível, o **kappa humano-humano** como teto declarado.
- **Viés reportado, não eliminado.** Não se exige um juiz sem viés; exige-se que a taxa de inversão posicional esteja no relatório e que o protocolo usado esteja declarado — com a cobertura resultante, porque o protocolo de dupla ordem descarta casos.
- **Factualidade decomposta** onde o sistema afirma fatos: proporção de afirmações suportadas pela fonte citada, taxa de contraditas separada, e **a agregação declarada** (micro ou macro).

**O que a V2 muda no *como* se cobra**, sem mexer nos pesos:

- **A matemática é cobrada como justificativa, não como derivação.** A pergunta que separa nota não é "calcule o kappa" — é "o acordo bruto da sua equipe ficou acima do kappa; explique a diferença com a distribuição de rótulos do seu conjunto". A conta está em A.1 para quem quiser reconstruí-la; o que se avalia é a leitura.
- **O apêndice é cobrável como fundamento de justificativa, nunca como derivação isolada.** Nenhum item de avaliação pede a demonstração de `π = 0,5 + τ/2`. Vários pedem que o aluno use `τ` para qualificar a confiança num número — e é a existência de A.2 que torna razoável exigir isso.

*Observável em sala, sem nota:* no fechamento, cada equipe consegue nomear em voz alta as camadas que vai medir no projeto, a métrica de cada uma **e o `n` que ela vai ter**. Quem só souber dizer "vamos ver se as respostas estão boas" ainda não tem plano de avaliação, e o Lab 8 começa por aí. Quem disser a métrica sem o denominador está a meio caminho — e é o caminho que o slide 5 existe para completar.
