---
aula: 15
titulo: "Alinhamento: RLHF, PPO e DPO"
modulo: "4 — Alinhamento e Raciocínio"
tipo: teorica
semana: 8
duracao_min: 120
versao: v2
---

# Aula 15 — Alinhamento: RLHF, PPO e DPO

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos versionáveis
> (medição, tabela de diagnóstico, anotação de decisão), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** O fluxo da aula é conduzido por três defeitos observáveis de um modelo
> alinhado — acerta a forma e erra o pedido, bajula, e piora no que já sabia. A matemática entra
> como fundamento nomeado, com a derivação completa no apêndice do deck (itens A.1 a A.6). Os
> objetivos de aprendizagem, a carga horária e a numeração permanecem os da V1; o que muda é a
> ordem de apresentação e onde a derivação é feita.

## 1. Objetivo da aula

Fechar a lacuna que o SFT deixa aberto e, sobretudo, tornar o aluno capaz de **diagnosticar** o
que dá errado quando ela é fechada mal: reconhecer bajulação como sobre-otimização de proxy,
reconhecer capacidade perdida como deriva de distribuição que o KL existe para conter, e escolher
entre PPO e DPO pela origem da recompensa e pela natureza dos dados. As contas — Bradley-Terry, o
objetivo clipado, a vantagem, a política ótima sob KL e a reformulação do DPO — ficam disponíveis
no apêndice, para consulta e estudo.

## 2. Resultados de aprendizagem

Ao final da aula, o aluno será capaz de:

1. **Explicar** por que maximizar a verossimilhança de bons exemplos (SFT) não ensina o modelo a
   evitar respostas ruins, e citar duas classes de falha que só o sinal de preferência corrige.
2. **Enunciar** a perda do modelo de recompensa de Bradley-Terry, **ler** cada termo, e
   **justificar** por que apenas as *diferenças* de recompensa são identificáveis (derivação em
   A.1).
3. **Mapear** a geração de texto para o vocabulário de RL — política, estado, ação, recompensa
   terminal — e **localizar** nesse mapa o papel do clipping, da vantagem e da regularização KL
   (A.2 e A.3).
4. **Diagnosticar** um caso de reward hacking a partir de sintomas observáveis (bajulação,
   inflação de comprimento, recusa excessiva), **propor a medição que o confirma** e indicar uma
   mitigação.
5. **Calcular** o custo de Best-of-N em tokens e latência, **ler** o desvio de KL que ele induz
   como orçamento equivalente (A.5), e decidir se ele cabe num orçamento de inferência dado.
6. **Escolher** entre DPO e PPO para um cenário concreto, justificando pela natureza dos dados,
   pela infraestrutura disponível e pela origem da recompensa.

*(Idênticos aos da V1. O que mudou foi o verbo dominante nos itens 2 e 4: de "escrever a perda" e
"reconhecer o sintoma" para "ler o resultado, justificar e propor a evidência" — a derivação
permanece disponível e é cobrada como fundamento da justificativa.)*

## 3. Teoria aplicada

Cada conceito abaixo é apresentado pelo comportamento que o motiva, com o fundamento matemático
nomeado e a derivação remetida ao apêndice.

### Bloco 1 (00:10–00:55) — Do defeito observável ao escalar

**Conceito 1 — Os três sintomas de abertura.**
*Comportamento observável:* (a) o modelo responde no template certo, com tom certo, e responde
outra coisa que não o que foi pedido; (b) o usuário afirma uma premissa falsa e o modelo concorda
e elabora em cima dela; (c) depois do alinhamento, o modelo erra uma tarefa que acertava antes.
Os três sobrevivem a mais dados de SFT — e é isso que os torna diagnósticos.
*Erro conceitual comum:* atribuir os três a treino insuficiente. Nenhum deles é falta de forma.
*Nota de condução:* os três cartões voltam nominalmente nos slides 5, 11 e 10, cada um amarrado
ao fundamento que o explica. O arco fecha no exercício.

**Conceito 2 — Por que mais dados de imitação não resolvem.**
*Comportamento observável:* respostas ruins que importam são fluentes, confiantes e erradas —
vivem numa região que o gradiente da entropia cruzada nunca visita nem penaliza.
*Argumento de custo:* escrever a demonstração de ouro exige um anotador tão bom quanto o modelo
desejado; comparar dois candidatos exige um anotador razoável, e ele acerta.
*Erro conceitual comum:* "alinhamento é SFT com mais dados". O que muda é o objetivo, não o volume.

**Conceito 3 — O que o alinhamento acrescenta.**
Pré-treino → capacidade. SFT → forma. Alinhamento → julgamento. O escalar otimizado deixa de ser
verossimilhança de texto humano e passa a ser preferência humana sobre saídas do modelo.
*Erro conceitual comum:* achar que o RLHF ensina conhecimento novo. Ele redistribui massa de
probabilidade sobre o que o modelo já sabe produzir.

**Conceito 4 — O dado que muda o objetivo.**
A tripla `(x, y_w, y_l)`, amostrada do próprio SFT; `K` amostras por prompt geram `K(K−1)/2`
pares. Comparação pareada vence nota absoluta porque nota absoluta não é estável. A diretriz de
anotação é o artefato mais subestimado do pipeline: precedência escrita, tratamento de empate,
tratamento de "as duas são ruins".
*Número que limita tudo:* concordância entre anotadores na casa de 70% em tarefas abertas
(InstructGPT) — um teto, não um detalhe.
*Erro conceitual comum:* pensar que o anotador escreve a resposta. Ele ordena.

**Conceito 5 — O fundamento nomeado: Bradley-Terry.**
`P(y_w ≻ y_l | x) = σ( r(x,y_w) − r(x,y_l) )` e a perda por máxima verossimilhança, **enunciadas
e lidas**, nunca manipuladas em aula. Duas leituras: só a diferença entra; e a saturação da
sigmoide faz par fácil parar de contribuir gradiente.
*Fundamento:* a verossimilhança, a perda, o peso `1 − σ(Δ)` de cada par e a identificabilidade a
menos de constante aditiva por prompt. → **A.1**
*Erro conceitual comum:* ler `r = 3,7` como qualidade absoluta. Não existe escala; existe ordem.
*Nota de condução:* ler as duas fórmulas em voz alta uma vez, apontando os termos. **Não derivar
no quadro** — a Parte 4 do roteiro tem a contingência.

**Conceito 6 — O reward model como proxy congelado.**
O RM é o SFT com cabeça escalar; uma época; menor que a política; métrica de sanidade é acurácia
em pares held-out.
*Número medido na demo:* com 25% de rótulos discordantes, a acurácia satura em torno de **0,75** —
o teto é `1 − ruído`, e é do rótulo, não do modelo.
*Fundamento:* o teto sob ruído de rótulo sai da forma da perda de Bradley-Terry. → **A.1**
*Erro conceitual comum:* confundir modelo de recompensa (prediz preferência, congelado) com modelo
de valor do PPO (prediz retorno esperado, treina junto com a política).

### Bloco 2 (01:05–01:50) — Como se gasta o escalar, e o que dá errado

**Conceito 7 — O LLM como política, e o crédito que não chega.**
Estado, ação, política, episódio e recompensa terminal. O crédito de uma decisão no token 12 é
inferido do resultado no token 400 — atribuição de crédito. Quem distribui o escalar único ao
longo dos tokens é a vantagem, e medir "o que se esperava" exige uma linha de base.
*Fundamento:* `A(s,a) = Q(s,a) − V(s)`; qualquer linha de base que dependa só do estado deixa o
gradiente sem viés e reduz variância; GAE como interpolação viés/variância. → **A.2**
*Erro conceitual comum:* imaginar que o RM dá uma nota por token.
*Gancho:* o resultado de A.2 é exatamente o que a Aula 16 usa para eliminar o modelo de valor.

**Conceito 8 — PPO: por que o passo é cortado.**
*Comportamento observável:* o treino colapsa em texto degenerado e a recompensa média sobe
enquanto isso acontece.
*Fundamento:* `ρ_t = π_θ/π_old` e o objetivo clipado com `ε ≈ 0,2`, **enunciados e lidos**; o
custo prático são quatro modelos na memória. → **A.3**
*Erro conceitual comum:* achar que o clipping limita o quanto os pesos mudam. Ele limita a
contribuição daquela ação ao gradiente — região de confiança em espaço de política.

**Conceito 9 — A trava de KL e o sintoma que ela contém.**
*Comportamento observável:* o modelo perdeu uma capacidade que tinha. Nenhum peso foi apagado: a
massa de probabilidade se mudou de bairro.
*Fundamento:* `r_total = r_φ − β·KL(π_θ ‖ π_ref)`. Com `β → ∞` a política ótima é `π_ref`; com
`β → 0` ela colapsa no argmax do RM. → **A.4**
*Erro conceitual comum:* tratar o KL como regularizador cosmético. Sem ele o problema não é
bem-posto.
*Métrica de acompanhamento:* o par (recompensa, KL acumulado), nunca a recompensa sozinha.

**Conceito 10 — Reward hacking: quando a métrica sobe e o produto piora.**
*Comportamento observável:* bajulação, inflação de comprimento, recusa excessiva, enfeite de
formatação. As curvas de sobre-otimização traçadas **contra o KL**: proxy sempre subindo,
preferência humana com pico e queda.
*Fundamento:* o eixo da sobre-otimização é o mesmo KL do Conceito 9 — distância percorrida, não
passos de treino; por isso escolher `β` e escolher onde parar são a mesma decisão. → **A.4**
*Mitigações:* orçamento de KL explícito; avaliação humana fora do RM; recompensa normalizada por
comprimento; ensemble de RMs; RLHF iterado.
*Erro conceitual comum:* concluir que "o RM está errado". Ele está fazendo o que foi treinado
para fazer.

**Conceito 11 — Best-of-N.**
Alinhamento sem tocar em peso: `N` amostras, o RM pontua, devolve-se a maior. Custo: `N ×` tokens
de saída; `N ×` latência se serial.
*Fundamento:* o desvio de KL induzido é `log N − (N−1)/N` — cresce com o logaritmo e põe `N` e o
orçamento de KL na mesma moeda (`N = 8` ≈ 1,2 nat). → **A.5**
*Quando não usar:* latência sensível; volume alto; sem pontuador confiável; `N` amostras com o
mesmo erro sistemático.
*Erro conceitual comum:* apresentar Best-of-N como alternativa a treinar. É computação de
inferência recorrente trocada por computação de treino única.

**Conceito 12 — DPO: a conta que apaga o modelo de recompensa.**
Contado em três frases no fluxo — forma fechada, inversão, cancelamento — e com a perda final
**enunciada**. Dois forward e um backward; das quatro caixas sobram duas, uma congelada.
*Fundamento:* `π*(y|x) ∝ π_ref(y|x)·exp(r(x,y)/β)`; invertê-la e substituí-la no Bradley-Terry
cancela `Z(x)` porque os dois lados compartilham o prompt. → **A.6**
*Erro conceitual comum:* "DPO é PPO mais simples e igual". DPO é off-policy por construção.
*Modo de falha característico:* a margem cresce porque `log π_θ(y_l|x)` desaba, não porque `y_w`
melhora — e o gradiente em A.6 mostra que nada no objetivo exige o contrário. *Diagnóstico:*
registrar as duas log-probabilidades separadas, não só a margem.

**Conceito 13 — O critério de escolha.**

| Escolha | Quando ela é a certa |
|---|---|
| **DPO** | Conjunto de preferências fixo e razoavelmente on-distribution; orçamento de GPU e de complexidade apertado; reprodutibilidade importa; tarefa de turno único; sem infraestrutura de amostragem online. |
| **PPO** | É possível amostrar da política em treino e pontuar continuamente; o RM será reaproveitado por várias iterações; a recompensa **não** vem de pares nem é diferenciável (classificador de segurança, verificador programático, soma ponderada de objetivos); quer-se empurrar além do que o dataset fixo permite. |
| **DPO iterado** | Amostrar da política atual, anotar, treinar DPO, repetir. Recupera boa parte do ganho on-policy sem crítico nem loop de RL — é o DPO com a premissa de A.6 restaurada a cada rodada. |

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas |
|---|---|---|---|
| 00:00 | 10 min | Abertura pelos sintomas | Os três defeitos observáveis; por que nenhum deles é falta de dados de SFT; o Lab 4 como origem do primeiro |
| 00:10 | 45 min | Bloco 1 — do defeito ao escalar | Por que imitação não basta (6) · três estágios (5) · dados de preferência e diretriz (7) · Bradley-Terry enunciado e lido (8) · o RM como proxy congelado (7) · **demo de medição (12 min)** |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — como se gasta o escalar | O LLM como política e a vantagem (5) · PPO e o corte do passo (6) · a trava de KL e a capacidade perdida (6) · reward hacking lido contra o KL (7) · Best-of-N e o `log N` (5) · DPO em três frases (7) · **exercício de diagnóstico e decisão (9 min)** |
| 01:50 | 10 min | Fechamento | O critério DPO × PPO com as respostas reveladas (5) · o pipeline completo, os três defeitos respondidos e a ponte para a Aula 16 (5) |

*Comparação com a V1: o quadro algébrico passou de ~16 min de derivação conduzida (Bradley-Terry,
o objetivo do PPO e a inversão do DPO) para 0 min. Esses minutos foram para a demo (de 10 para 12
min), para o exercício (de 7 para 9 min) e para os dois slides de diagnóstico — KL e reward
hacking —, que ganharam 2 min cada. A derivação permanece integralmente disponível em A.1–A.6, e
lá está mais completa do que estava no quadro.*

## 4. Demonstração guiada

**Demo "o que o RM realmente aprende" — 12 min (00:43–00:55), `codigo/demo-bradley-terry.py`.**

Roda em CPU, em segundos, sem rede, sem chave de API e sem download de modelo. Na V2 ela deixa de
ser ilustração da fórmula e passa a ser a **evidência** de duas afirmações do fluxo.

1. **O gerador sintético.** Cada "resposta" é um vetor de oito atributos e a qualidade verdadeira
   é uma projeção linear num vetor de pesos **oculto**. Quem anota nunca vê a função — é a
   situação exata do anotador humano.
2. **A perda de uma linha.** `-F.logsigmoid(r_w - r_l).mean()` é literalmente a fórmula do
   Conceito 5, sem adaptação; o RM é um `nn.Linear(8,1)`, a cabeça escalar do Conceito 6.
3. **Separação, não qualidade.** Histogramas de score antes e depois: sobrepostos no início,
   separados no fim, com o eixo x rotulado "unidade arbitrária". É a identificabilidade de A.1
   aparecendo desenhada.
4. **O teto que é do rótulo — a medição que não se corta.** Três treinos, com 0%, 10% e 25% de
   rótulos invertidos. As curvas encostam nas linhas tracejadas de `1 − ruído` e param: com 25%,
   a acurácia medida **satura em torno de 0,75**. Esta é a evidência do Conceito 6 e o número dos
   70% do Conceito 4 virando platô.
5. **A coluna que separa "modelo ruim" de "rótulo ruim".** Contra a ordem verdadeira — observável
   só porque a demo é sintética — a recuperação continua alta. O teto é do rótulo; a razão
   algébrica está em A.1.
6. **O que a demo não mostra**, dito explicitamente: não há política, não há KL, não há hacking.
   É a fábrica do escalar, e ela precisa estar sólida antes do intervalo.

Insumos preparados: script rodado na véspera com a saída em texto salva e o PNG
`separacao-bradley-terry.png` gerado, para o caso de o Python da sala não subir. O script degrada
sozinho sem matplotlib, imprimindo a tabela-resumo em texto puro.

## 5. Hands-on

**Componente prático da unidade — exercício de diagnóstico e decisão (6 min de dupla + 3 de
correção, 01:41–01:50).**

Substitui o exercício de escolha DPO/PPO da V1, que virou a terceira ficha. Para cada ficha a
dupla escreve **causa provável**, **evidência que a confirmaria** e **decisão que ela força**.

1. **O bajulador.** Depois do RLHF, o assistente passou a concordar com premissas falsas do
   usuário. A recompensa média do RM no treino subiu de forma consistente. Nenhum erro no log.
2. **A capacidade que sumiu.** Um modelo que convertia unidades corretamente antes do alinhamento
   passou a errar. A perda de treino caiu bem; o KL contra `π_ref` triplicou.
3. **A decisão.** Uma equipe de plataforma precisa reduzir uma taxa de violação de política de
   segurança medida por um **classificador já existente e auditado**; há infraestrutura de
   amostragem online e budget para iterar semanalmente. DPO ou PPO — e por quê?

*Respostas esperadas:* (1) reward hacking — o RM foi otimizado além da região onde foi validado;
confirma-se com avaliação **fora** do RM, lendo a preferência humana contra o KL e não contra
passos; decisão: orçamento de KL explícito e RLHF iterado. (2) deriva de distribuição por `β` baixo
demais — o KL triplicado é a assinatura; confirma-se rodando o eval de capacidade em checkpoints
**ordenados por KL** e localizando o joelho; decisão: subir `β` ou parar no joelho. (3) PPO —
porque não existem pares ali, existe um programa que pontua, e programa não vira dataset de
comparação sem alguém construir os pares.

*Critério de conclusão observável:* a dupla nomeia a causa **e** propõe uma medição que a
confirmaria. Nomear sem propor evidência não fecha a ficha — "esquecimento catastrófico" é nome,
não diagnóstico.

*Extensão para quem terminar antes (opcional):* refazer o cenário oposto da ficha 3 — 40 mil
pares já anotados sobre respostas do próprio SFT, três pessoas, duas GPUs de 24 GB — e dizer o que
muda na resposta. É o exercício que na V1 era obrigatório e aqui vira aprofundamento.

## 6. Riscos e contingências

| Risco | Sinal em sala | Plano B |
|---|---|---|
| **A turma pedir a derivação em aula** | "De onde sai essa perda?" já no Conceito 5 | A Parte 4 do roteiro tem cinco conduções prontas com o custo em minutos de cada uma. Fazê-las **só se sobrar tempo**, anunciando que é conteúdo de apêndice. Se não couber, remeter e seguir — o apêndice é autossuficiente |
| **Turma sentir que "faltou rigor"** | Comentário de que a aula ficou superficial | Projetar o apêndice por 30 s: seis itens, com premissas, casos-limite e o gradiente do DPO escrito — mais matemática do que a V1 tinha no fluxo inteiro. O rigor não saiu, mudou de lugar e virou consultável |
| **Turma sem ML prévio travando em política/vantagem/crítico** | Silêncio no Conceito 7 | Definir "episódio" e "política" em duas frases e seguir com a leitura da vantagem; a conta está em A.2. GAE é cortável sem prejuízo, e o DPO do Conceito 12 é autossuficiente com log-probabilidade |
| **Demo não roda** (torch, matplotlib) | Traceback na projeção | PNG e saída em texto da véspera. Os passos 4 e 5 são os que sustentam o Conceito 6 e **não** se cortam; os passos 1 e 2 viram uma frase cada |
| **Confusão persistente entre reward model e value model** | Perguntas trocando os dois nomes | Desenhar os quatro modelos e o contraste RM × valor no quadro e **não apagar** até o fim do Bloco 2. Responder apontando, em vez de reexplicar |
| **O sintoma da capacidade perdida não convencer** | "Isso acontece mesmo?" | Ler os dois casos-limite de A.4 em voz alta: `β → ∞` devolve a referência, `β → 0` colapsa no argmax do RM. O segundo limite **é** o sintoma, e ele é uma consequência, não uma anedota |
| **Bloco 1 estourar** | 00:50 e Bradley-Terry ainda não fechado | Cortar o Conceito 3 (três estágios), cuja informação volta no fechamento, e emendar direto em dados de preferência. O que **não** se corta é a demo |
| **Bloco 2 estourar** | 01:45 e o DPO ainda no meio | Contar apenas as três frases do Conceito 12 e mostrar a perda final; a derivação já está em A.6 e vira o desafio pós-aula. Proteger o exercício |

## 7. Artefatos produzidos

- **Tabela de diagnóstico** do exercício: três fichas × causa × evidência que confirma × decisão —
  fotografada ou digitada no repositório pessoal. É o artefato central da aula na V2.
- Saída de `demo-bradley-terry.py` executado, com o PNG da curva de separação e a acurácia pareada
  nos três níveis de ruído, e o número do teto (`≈ 0,75` com 25% de ruído) anotado.
- A tabela de decisão DPO × PPO × DPO iterado do Conceito 13, copiada como cola de uma página.
- A lista de sintomas de reward hacking, para reuso na Aula 26 (segurança e avaliação de agentes)
  e no projeto final.
- *(Opcional, extensão)* folha de derivação seguindo A.1 ou A.6, para quem fez o aprofundamento.

## 8. Desafio pós-aula

Gancho opcional, não avaliado. Três itens, na ordem:

1. **Diagnóstico próprio.** Descrever um comportamento anômalo que você já viu (ou que imagina
   plausível) num assistente comercial, e dizer qual dos três fundamentos da aula — identificação
   por diferença (A.1), orçamento de KL (A.4) ou desvio induzido por seleção (A.5) — o explicaria,
   e que medição confirmaria. Cinco linhas.
2. **Leitura com o apêndice ao lado.** Rafailov et al., *DPO* (arXiv 2305.18290), seção 4.
   **Pergunta dirigida:** em que passo exato a partição `Z(x)` cancela, e por que esse
   cancelamento seria impossível se as duas respostas do par viessem de prompts diferentes?
   Compare a passagem do artigo com **A.6** — a verificação de sanidade no fim do item responde a
   segunda parte em uma linha.
3. **Leitura dirigida.** Ouyang et al., *InstructGPT* (arXiv 2203.02155). **Pergunta:** por que os
   autores colocam todos os `K(K−1)/2` pares de um mesmo prompt no mesmo lote de treino do RM, em
   vez de espalhá-los pelo dataset? (Dica: a identificabilidade de A.1 é metade da resposta; a
   outra metade é sobre correlação entre amostras do mesmo prompt.)
4. **Extensão de código.** Em `demo-bradley-terry.py`, trocar o RM linear por um MLP de duas
   camadas e verificar se a acurácia pareada com 25% de ruído melhora. Se não melhorar, escrever em
   duas linhas por que não — e A.1 já contém a resposta.

## 9. Critérios de avaliação

Aula teórica sem entregável avaliado. Os pesos são os da ementa e não se alteram: **Laboratórios
30%** (descartando a menor nota) · **Prova 30%** (Aula 17) · **Projeto final 40%**.

A V2 muda **como** este conteúdo é cobrado, não quanto:

- **Prova (Aula 17, 30%).** O conteúdo aparece principalmente como **diagnóstico e justificativa**:
  dado um sintoma (bajulação, capacidade perdida, recompensa que sobe enquanto a avaliação humana
  cai, treino que colapsa em texto degenerado), identificar a causa, dizer que evidência a
  confirmaria e propor a mitigação. A escolha DPO/PPO é cobrada como **justificativa** — citando a
  natureza dos dados e a origem da recompensa, nunca "DPO é mais simples". A derivação aparece em
  no máximo um item, ancorada num porquê: por exemplo, usar a identificabilidade de A.1 para
  explicar por que recompensas de prompts diferentes não podem ser comparadas num painel.
- **Projeto final (40%).** Equipes que treinarem qualquer coisa devem justificar no relatório
  técnico por que **não** fizeram alinhamento, se não fizeram. Ausência de justificativa conta como
  decisão não fundamentada na rubrica de "justificativa das decisões" (20% da nota do projeto).

*Observável em sala, sem nota:* na correção do exercício, o aluno nomeia a causa **e** propõe uma
medição que a confirmaria — e, na ficha 1, sabe dizer que a medição correta se lê contra o KL e
não contra passos de treino. Propor a medição é o que distingue quem entendeu o fundamento de quem
decorou o sintoma.

**Leituras da aula:** Ouyang et al., *InstructGPT* (arXiv 2203.02155); Rafailov et al., *DPO*
(arXiv 2305.18290). Complementar, para quem quiser o PPO na fonte: Schulman et al., *PPO*
(arXiv 1707.06347) — a leitura fica muito mais fácil com **A.3** ao lado.
