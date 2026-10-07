---
aula: 0
titulo: "Aula 0 — Recepção: o mapa do curso, os materiais e o ambiente"
modulo: "0 — Recepção (extra-classe)"
tipo: recepcao
semana: 0
duracao_min: 60
versao: v2
---

# Aula 0 — Recepção: o mapa do curso, os materiais e o ambiente

> **Postura deste material.** Artifact-first: o que esta sessão produz são artefatos
> versionáveis (ambiente configurado, repositório criado, documento do contrato), não
> conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **O que esta sessão é, e o que ela não é.** Recepção de **60 minutos**, **extra-classe**, na
> semana zero — antes do início oficial das aulas. Ela **não consome carga horária**: as 60h
> continuam distribuídas nas 30 aulas de 2h, e a numeração das aulas é inalterada. É o **único
> lugar onde o contrato da disciplina é apresentado por inteiro**, e é onde o ambiente sobe.
> **Sem apêndice matemático** — a sessão não expõe conteúdo técnico, por regra própria.

## 1. Objetivo da sessão

Que ninguém comece o semestre no escuro, em dois sentidos. Primeiro, o **contrato**: ao sair desta sessão, o estudante sabe como será avaliado, o que a prova cobra e em que proporção, o que a política de uso de IA permite e veda, que materiais existem e como se usam. Segundo, o **ambiente**: sai com Colab, Hugging Face, chave de API e repositório funcionando — porque download e permissão são o que mais atrasa laboratório, e o Lab 1 é em duas semanas.

A sessão **não ensina conteúdo técnico**. Isso é regra, não omissão: se um slide desta sessão ensina algo sobre LLM, ele está no lugar errado — o conteúdo começa na Aula 1.

## 2. Resultados esperados

Ao final desta sessão, o estudante deve ser capaz de:

1. **Descrever** o artefato final da disciplina — um sistema com LLM, defendido em 12 minutos com demo ao vivo e uma tabela de métricas por camada — e dizer o que a pergunta de defesa vai cobrar.
2. **Localizar** qualquer uma das sete camadas do curso na pilha, nomeando a aula e o laboratório em que ela é construída.
3. **Enunciar** a composição da própria avaliação: a fórmula AV1/AV2, os pesos, os três marcos do projeto com data, e a distribuição da prova em 42/40/8/10.
4. **Distinguir** o fluxo do apêndice num material da disciplina, e dizer o que estudar em cada um antes de uma aula e antes da prova.
5. **Aplicar** a política de uso de IA: o que a declaração de uso precisa conter, e qual é a régua (defender o que se entrega).
6. **Ter** o ambiente funcionando: Colab com GPU habilitada, token do Hugging Face, chave de API testada, repositório criado com `.gitignore` que exclui chaves.

*Não há resultado de aprendizagem técnico — por desenho.*

## 3. Conteúdo

Não há teoria. O que segue são os **quatro blocos da sessão** e a razão de cada um estar aqui.

### Bloco 1 (00:00–00:12) — Para onde este curso vai

Abre pelo **fim**: a Aula 30, com cada equipe defendendo um sistema em 12 minutos, com demo ao vivo num caso difícil e a tabela de métricas por camada projetada. Depois o **diagnóstico da turma** por mão levantada — quatro perguntas cujos números calibram decisões reais do semestre. E o **mapa das sete camadas** com o endereço de cada uma.

*Por que abrir pelo fim:* primeira aula que abre pela ementa não retém nada. Abrir pelo artefato final dá à sala uma imagem concreta do que se espera dela, e todo o resto da sessão passa a ser lido como "o caminho até lá".

*A propriedade que se quer fixar:* **é pilha, não lista.** Cada camada só faz sentido porque a de baixo existe, e o Lab 8 mede exatamente as camadas que os Labs 1 a 7 construíram.

### Bloco 2 (00:12–00:24) — O contrato

**O que o curso não faz** (honestidade de escopo, e a relação com a Eletiva 1 — as duas não se sobrepõem e podem ser cursadas em qualquer ordem). **Como se é avaliado**: a fórmula institucional, os pesos 40/60 em cada módulo, e os três marcos do projeto com data. **A prova em números**: a distribuição 42/40/8/10, com a consequência dita explicitamente — decorar derivação rende 10 pontos; entender o que ela autoriza a afirmar rende os outros 40.

*O slide da prova é o mais importante da sessão* e merece um minuto de silêncio depois de falado. É a informação que, dada tarde, produz a reclamação legítima de que as regras mudaram no meio do semestre.

### Bloco 3 (00:24–00:35) — Os materiais e a política de IA

**A divisão fluxo/apêndice**, que é o conceito organizador do semestre inteiro, demonstrada com um deck real aberto na tela — o da Aula 6, com 14 slides de fluxo e 6 itens de apêndice. Abrir o item A.2 e projetar por 20 segundos é insubstituível: a palavra "apêndice" faz pensar em anexo simbólico, e a turma precisa ver que é uma página de derivação escrita. Os 30 decks somam **111 itens**.

Depois os **outros materiais** — apostila de ~300 páginas com instrução de uso, notebooks com solução liberada após o prazo, papers com pergunta dirigida, e os seis formulários quinzenais. E a **política de uso de IA**: permitida e incentivada, com declaração de uso obrigatória e a régua de que o estudante precisa conseguir defender o que entrega.

### Bloco 4 (00:35–01:00) — Ambiente, e como estudar

Três minutos sobre **como usar o material** nos quatro momentos (antes da aula, depois, antes do lab, antes da prova), e **vinte e cinco minutos de setup ao vivo**: Colab com GPU, Hugging Face com token de leitura, chave de API testada, repositório criado.

*A regra dita antes de começar:* quem terminar um item ajuda o vizinho. Setup é a única parte do curso em que copiar a solução do colega é exatamente o comportamento certo.

### Grade temporal — própria desta sessão

A grade padrão do contrato (10/45/10/45/10, para 120 min) **não se aplica**: são 60 minutos e não há dois blocos conceituais. A grade é derivada da proporção que a sessão precisa ter — metade contrato, metade mão na massa — e **não há intervalo**.

| Início | Dur. | Bloco | Conteúdo |
|---|---|---|---|
| 00:00 | 12 min | Para onde o curso vai | A Aula 30 descrita primeiro (4) · diagnóstico da turma por mão levantada (4) · o mapa das sete camadas com endereço (4) |
| 00:12 | 12 min | O contrato | O que o curso não faz e a relação com a Eletiva 1 (3) · avaliação, pesos e os três marcos com data (4) · **a prova em números, 42/40/8/10, com um minuto de silêncio** (5) |
| 00:24 | 11 min | Materiais e IA | **Fluxo × apêndice, com um deck real aberto na tela** (4) · apostila, notebooks, papers, formulários (3) · política de uso de IA e a declaração (4) |
| 00:35 | 25 min | Ambiente | Transição e a razão de fazer hoje (2) · como estudar, os quatro momentos (3) · **setup ao vivo: Colab, HF, API, repositório** (20) |
| 01:00 | — | Encerramento | Checklist conferido item por item em voz alta · o documento de uma página · o gancho da Aula 1 |

**Total: 60 min.** O encerramento acontece dentro dos últimos três minutos do bloco de ambiente, com o checklist projetado.

**Se a sessão atrasar:** o corte é o slide 11 (como estudar) — está escrito neste plano e o estudante lê. **Não se corta o setup**, que é a razão de a sessão existir, nem o slide 6 (a prova).

## 4. Demonstração guiada

Não há demonstração técnica — a sessão não expõe conteúdo. O que o instrutor demonstra é o **material**, e há uma demonstração que não pode faltar.

**Abrir um deck real na tela (slide 7).** O deck da Aula 6 é o melhor exemplo do curso: 14 slides de fluxo e 6 itens de apêndice. O instrutor mostra a Parte 1 — poucos elementos, um conceito por slide, a fórmula enunciada com o ponteiro — e então rola até a Parte 2 e **abre o item A.2**, deixando na tela por 20 segundos.

**Número que a demonstração produz.** Um: **111 itens de apêndice** nos 30 decks. Ele volta no slide 8 (quando se fala da apostila, que segue a mesma divisão) e no encerramento. E ele existe para responder antecipadamente a pergunta que a divisão fluxo/apêndice provoca — *"então a matemática saiu do curso?"* — com um número em vez de uma garantia verbal.

O único artefato técnico que o instrutor prepara é o **plano B de rede**: se a conexão da sala não sustentar a turma toda no setup, a ordem dos quatro itens se inverte (repositório primeiro, Colab por último, em duplas). Preparado na véspera.

## 5. Hands-on

O hands-on é metade da sessão: **25 minutos de setup**, com critério de conclusão observável em cada item.

**Item 1 · Colab com GPU (~8 min).**
Criar notebook, `Ambiente de execução → Alterar o tipo → T4 GPU`, e rodar `!nvidia-smi`.
*Critério observável:* a placa aparece na saída da célula.
*Erro nº 1:* conta institucional com restrição de acesso ao Colab — **não tem solução em sala**; quem cair nisso usa conta pessoal, e vale avisar antes que alguém perca dez minutos. *Erro nº 2:* habilitar a GPU e esquecer de reconectar o ambiente.

**Item 2 · Hugging Face com token (~7 min).**
Criar conta, gerar token de **leitura** (não de escrita), testar com `login()`.
*Critério observável:* `login()` retorna sem erro.
*O hábito a corrigir agora:* colar o token no notebook. Mostrar `getpass` ou o painel de segredos, e cravar a regra — chave em variável de ambiente ou `getpass`, nunca no código. Corrigir isso no primeiro dia é mais barato que corrigir no Lab 4.

**Item 3 · Chave de API (~8 min).**
Provedor com camada gratuita, chave criada, **uma** chamada de teste.
*Critério observável:* a chamada retorna texto.
*Riscos:* a sala inteira criando conta no mesmo provedor pode esbarrar em limite por IP — ter um segundo provedor anotado. E a confusão entre camada gratuita e período de teste pago: dizer qual é qual, porque ninguém no curso precisa gastar dinheiro.

**Item 4 · Repositório (~5 min).**
Estrutura mínima — uma pasta por lab, `README.md`, e um `.gitignore` que exclua arquivos de chave. Link entregue no canal.
*Critério observável:* o link no canal da turma. **É o único item verificável depois da sessão**, e é o que o instrutor confere antes da Aula 1.
*Por que o `.gitignore` importa:* é a prevenção do acidente mais comum do semestre, que é comitar uma chave de API.

**A regra dita antes de começar:** quem terminar um item ajuda o vizinho.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Presença baixa** — a sessão é extra-classe e não obrigatória | Menos de metade da turma | O contrato **precisa** existir por escrito: o documento de uma página vai no canal da turma no mesmo dia, e a Aula 1 aponta para ele em 30 s. Sem esse documento, a decisão de absorver o contrato aqui deixaria os ausentes sem saber como serão avaliados |
| **Rede da sala não sustenta a turma** no setup | Colab não conecta para vários ao mesmo tempo | Inverter a ordem: repositório primeiro (mais leve), Colab por último, em duplas compartilhando conexão. Se nada funcionar, o checklist vai por escrito com prazo até segunda de manhã, e a sessão termina no slide 11 |
| **Conta institucional bloqueia o Colab** | Erro de permissão no primeiro acesso | Não tem solução em sala — usar conta pessoal. **Avisar isso antes** de o setup começar, senão alguém gasta dez minutos tentando |
| Limite de cadastro por IP no provedor de API | 429 ou recusa de cadastro a partir do terceiro aluno | Ter um **segundo provedor** anotado na véspera, com o passo a passo pronto |
| **A turma trata o slide da prova como detalhe** | Ninguém pergunta nada depois dele | O minuto de silêncio é o mecanismo. Se ainda passar batido, fazer uma pergunta à sala: *"o que muda no jeito de vocês estudarem, sabendo que derivação vale 10 e justificativa vale 40?"* |
| A divisão fluxo/apêndice é entendida como "a matemática saiu" | Pergunta do tipo "então não tem teoria?" | O deck real aberto na tela responde melhor que qualquer explicação, e o número — 111 itens — responde melhor que uma garantia verbal. Abrir o A.2 e deixar 20 s |
| **Setup "quase" funcionando** | Aluno diz que está ok sem ter rodado o teste | Conferir o checklist **item por item, em voz alta**. Perguntar "está tudo ok?" não descobre nada. Ambiente que quase funcionou na recepção é ambiente quebrado no Lab 1 |
| Sessão vira sessão de dúvidas individuais | Fila formando no meio do setup | Os dez minutos **depois** do fim são para isso, e são anunciados. Durante o setup, quem terminou ajuda o vizinho |

## 7. Artefatos produzidos

**Pelo estudante:**
- Colab com GPU habilitada e `nvidia-smi` respondendo.
- Conta Hugging Face com token de leitura, testado.
- Chave de API de provedor gratuito, com uma chamada de teste bem-sucedida.
- **Repositório da disciplina criado**, com estrutura mínima e `.gitignore` excluindo chaves, e o link entregue no canal.

**Pelo instrutor:**
- **O documento de uma página do contrato** — avaliação, composição da prova, política de IA, calendário dos marcos. Distribuído no canal da turma no mesmo dia, **independentemente de presença**. É o único registro escrito do contrato, e a Aula 1 aponta para ele.
- Os quatro números do diagnóstico da turma, anotados. Eles calibram decisões ao longo do semestre.
- A lista de quem saiu sem ambiente funcionando, para acompanhar antes da Aula 4.

## 8. Depois da sessão

Não avaliado, e tem prazo curto porque a Aula 1 é no dia seguinte ou no seguinte.

1. **Ler os objetivos e as caixas de conceito da seção 1 da apostila** — 20 minutos. É a recomendação do slide 11 aplicada imediatamente, e a Aula 1 rende mais para quem fizer.
2. **Salvar o documento de uma página** e ler o contrato inteiro, se não estava na sessão.
3. **Pensar na pergunta de abertura da Aula 1**, sem procurar a resposta: *um detector de fraude com 99% de acurácia que nunca achou uma fraude na vida — como isso é possível, e o que ele deveria estar medindo?*

## 9. Critérios de avaliação

**Esta sessão não é avaliada e não tem nota.** Ela é extra-classe, não consome carga horária e não cria peso novo: os pesos continuam sendo AV1 e AV2 conforme a §5 do plano de ensino.

O que ela **estabelece** para o resto do semestre:

- **O contrato de avaliação passa a ser conhecido**, e é o que torna legítimo cobrar 42 pontos de diagnóstico e 40 de justificativa na Aula 17. Um contrato anunciado no primeiro dia é diferente de um contrato descoberto na véspera da prova.
- **A régua da política de IA** — conseguir defender o que se entrega — vale desde o Lab 1, e foi dita aqui.
- **O ambiente é pré-requisito operacional** dos Labs 1 a 8. Não vale nota, mas quem chega sem ele perde tempo de laboratório que não volta.

**Observável ao final da sessão**, sem nota: cada estudante consegue dizer, em uma frase, o que vai apresentar em dezembro; e tem os quatro itens do checklist marcados.

## Apêndice matemático

**Sem apêndice.** Esta sessão não expõe conteúdo técnico — é regra própria do deck, não omissão: um slide que ensinasse algo sobre LLM estaria no lugar errado aqui, porque o conteúdo começa na Aula 1. Não há uma única fórmula no material, e portanto não há o que derivar.

O que a sessão faz em relação ao apêndice é **explicá-lo** (slide 7) e mostrar um item real aberto na tela, para que a turma veja que a Parte 2 dos decks é uma página de derivação escrita e não um anexo simbólico. O primeiro apêndice que o estudante vai efetivamente estudar é o da **Aula 1** — A.1 a A.5: matriz de confusão, F₁ como média harmônica, BLEU com penalidade de brevidade, ROUGE, e perplexidade com a razão de não atravessar tokenizadores.

Criar apêndice próprio aqui produziria um item artificial, e o contrato é explícito quanto a isso: item de apêndice inventado ensina o estudante a ignorar a Parte 2.
