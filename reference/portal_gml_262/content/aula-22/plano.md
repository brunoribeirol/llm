---
aula: 22
titulo: "Laboratório 6: Tool calling e MCP — Entrega 1 do projeto"
modulo: "5 — RAG, Ferramentas e Agentes de IA"
tipo: laboratorio
semana: 11
duracao_min: 120
versao: v2
---

# Aula 22 — Laboratório 6: Tool calling e MCP — Entrega 1 do projeto

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2 — §6-bis (laboratórios).** O roteiro prático **não foi reordenado**: os
> quatro checkpoints e a janela da Entrega 1 estão na ordem que funciona no teclado, e a janela do
> projeto continua fixa em 01:40. O que mudou é que cada checkpoint abre pelo **que a tela imprime
> quando está certo** — a linha `Checkpoint N OK` com o que o teste conferiu — antes de dizer o que
> implementar. O apêndice é **enxuto e organizado por checkpoint**: dois itens, os dois do
> Checkpoint 2. A **Aula 21 não tem apêndice próprio**, por decisão registrada — ela é aula de
> arquitetura e protocolo. Logo **este é o primeiro lugar do bloco de agentes em que o formalismo
> aparece**, e ele aparece aqui porque é aqui que o `max_passos` deixa de ser defensividade de
> programador e passa a ser a solução de uma desigualdade. Carga horária, numeração e objetivos
> inalterados. A **Entrega 1 do projeto** está preservada integralmente. O notebook em `codigo/`
> **não muda**.

## 1. Objetivo da aula

Escrever o **host** do ciclo da Aula 21: primeiro o loop de tool calling inteiro na mão, sem framework — schema, detecção, parsing, validação, despacho, retorno como mensagem `tool`, síntese — e só depois o mesmo poder pelo protocolo, conectando um cliente MCP a um servidor existente e publicando um servidor MCP próprio. Esta aula também recolhe e devolve, com feedback em sala, a **Entrega 1 do projeto final**.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Escrever** o schema de uma ferramenta com nome, descrição e parâmetros redigidos para o modelo ler, e **validar** argumentos contra esse schema antes de executar qualquer coisa.
2. **Implementar** o loop de tool calling sem framework, nomeando no código os cinco passos da Aula 21, com **orçamento de passos** e tratamento de erro de ferramenta como resultado.
3. **Inspecionar** uma trajetória — a lista de mensagens `system`/`user`/`assistant`/`tool` — e **apontar** nela a correlação entre a chamada e o resultado.
4. **Conectar** um cliente MCP a um servidor existente por `stdio` e **descobrir** suas capacidades com `initialize`, `tools/list` e `tools/call`.
5. **Publicar** um servidor MCP próprio que expõe a base do Lab 5 como **ferramenta** e o índice do acervo como **recurso**, e **justificar** a diferença pelo critério de quem decide usar.
6. **Defender** a proposta do projeto final contra cinco critérios: problema verificável, duas técnicas do curso, plano de avaliação por camada, divisão de trabalho e viabilidade em free tier.

*(Idênticos aos da V1.)*

## 3. Teoria aplicada

Este é um lab: a teoria é da Aula 21, dada no dia anterior. O que segue são os conceitos que o código materializa e o erro de implementação que cada um produz. A grade abaixo é a de laboratório da §3 do contrato, com uma adaptação declarada: o bloco de 35 min do segundo tempo é dividido em **25 min de checkpoints + 10 min de devolutiva da Entrega 1**, porque esta aula carrega o marco do projeto. O recolhimento dos artefatos da entrega acontece nos primeiros 5 min, junto com o setup.

### Os quatro checkpoints, pelo que cada um imprime

| CP | Relógio | O que faz | **O que a tela imprime quando está certo** | Apêndice |
|---|---|---|---|---|
| 1 | 00:35–00:48 | três schemas + `validar` | `Checkpoint 1 OK — 3 schemas válidos, 8 casos de validação, calculadora barrando código` | — |
| 2 | 00:48–01:05 | o loop na mão | `Checkpoint 2 OK — conta, busca, erro tratado e orçamento de passos` | **A.1 · A.2** |
| 3 | 01:15–01:27 | cliente MCP | o `initialize` com nome e versão do servidor, o `tools/list` com obrigatórios, e uma chamada com `isError = False` | — |
| 4 | 01:27–01:40 | servidor MCP próprio | o mesmo cliente, apontado para o servidor do aluno, imprimindo a ferramenta, o recurso e o resultado da busca | — |

**Entregável:** notebook executado + `servidor_regulamento.py` + trajetória comentada. Mais a **Entrega 1 do projeto**, recolhida às 00:05 e devolvida com comentário na janela das 01:40.

### Bloco 1 (00:35–01:05) — O host escrito na mão

**Conceito 1 — O schema é a única coisa que o modelo lê; o `REGISTRO` é a única coisa que executa.**
São dois objetos com papéis opostos e é comum confundi-los. `SCHEMAS` é texto que vai para o prompt: nome, descrição, parâmetros. `REGISTRO` é o dicionário que amarra nome de ferramenta a função Python — a única ponte entre o texto que o modelo escreveu e o código que roda. Ferramenta que está no schema e não está no registro produz erro em tempo de execução; ferramenta que está no registro e não no schema é código morto que o modelo nunca vai pedir.
*Observável que motiva:* o teste do CP1 falha nominalmente quando um nome de `SCHEMAS` não existe no `REGISTRO` — o defeito aparece antes de qualquer chamada de modelo.
*Analogia do instrutor:* o schema é o menu, o registro é a cozinha. O cliente pede pelo menu; quem cozinha é a cozinha. Menu com prato que a cozinha não faz é reclamação garantida.
*Erro conceitual comum:* declarar o schema e esquecer de registrar a função — e como o modelo *chama*, o sintoma aparece como "o modelo errou", quando o defeito é do host.

**Conceito 2 — Validar antes de despachar, e validar duas vezes.**
`validar(nome, argumentos)` confere contra o schema: ferramenta existe, obrigatórios presentes, nenhum parâmetro inventado, tipos casando, `minimum`/`maximum` respeitados. Depois disso, cada implementação valida de novo o que é dela (a calculadora rejeita o que não é aritmética; o CEP rejeita o que não tem oito dígitos). Não é redundância: o host não confia no modelo, e a ferramenta não confia em quem a chamou.
*Erro conceitual comum:* confiar na decodificação restrita. Ela garante JSON **bem formado**, não **correto** — o modelo pode entregar `{"expressao": "quanto é 15% de 320"}` com sintaxe impecável.

**Conceito 3 — `arguments` é uma string com JSON dentro, e ela pode vir truncada.**
O parsing é um passo separado do despacho justamente porque pode falhar. Truncamento por limite de tokens acontece, e um `json.loads` sem proteção derruba o loop inteiro no meio de uma trajetória. O tratamento certo é devolver o erro **como resultado de ferramenta**, e deixar o modelo decidir o que fazer com ele.
*Analogia:* erro de ferramenta é informação, não exceção. Quem transforma erro em exceção interrompe a conversa que deveria continuar.
*Erro conceitual comum:* levantar exceção no despacho. O agente morre; e, pior, morre sem registrar o que aconteceu.

**Conceito 4 — O orçamento de passos existe porque o modelo insiste — e o número dele sai de uma conta.**
O loop chama o modelo, executa, devolve o resultado e chama o modelo de novo. Se o modelo pedir ferramenta para sempre — porque não entendeu o resultado, porque a ferramenta erra sempre, porque o prompt está ambíguo — o laço não termina. `max_passos` é a proteção mínima, e o notebook usa `MAX_PASSOS = 4`. Esse 4 não é superstição: com o prompt fixo e a observação típica deste lab, quatro voltas é o que cabe num orçamento de cinco mil tokens enviados por pergunta.
*Observável que motiva:* o teste do CP2 usa um **modelo teimoso**, que nunca para de pedir ferramenta, e exige que o loop pare exatamente em `max_passos = 3` chamadas, devolvendo a mensagem de orçamento esgotado.
*Erro conceitual comum:* achar que `while True` com uma condição de parada baseada no conteúdo da resposta é suficiente. É a condição de parada mal projetada que a ementa lista na Aula 23 — e ela custa dinheiro em produção.

- **Fundamento:** cada volta reenvia a trajetória inteira, porque o modelo não guarda estado entre chamadas. Logo o custo de uma volta cresce com o número de voltas já dadas, e o total enviado numa trajetória de `n` passos é `T(n) = n·p₀ + d·n(n−1)/2` — quadrático em `n`, não linear. Invertendo a desigualdade `T(n) ≤ B` para um teto de orçamento `B` sai o `max_passos`.
  → a conta por volta, o total da trajetória e o `MAX_PASSOS = 4` como solução da desigualdade: **Apêndice A.1** (slide 11)
- **Fundamento:** o número de **chamadas** cresce linearmente com os passos e o número de **tokens enviados** cresce com o quadrado. Por isso toda estimativa da forma "custo de uma chamada × número de passos" subestima a fatura, e o fator do erro cresce com o tamanho da trajetória.
  → por que o crescimento é superlinear, o custo marginal do `k`-ésimo passo e o que muda a ordem de crescimento: **Apêndice A.2** (slide 12)

**Conceito 5 — A trajetória é o artefato, não a resposta final.**
A saída do `loop_agente` é um par: a resposta e a lista de mensagens. A lista é o que permite depurar: qual ferramenta foi pedida, com que argumento, o que voltou, e em que passo a coisa desandou. Sem isso, "o agente errou" é tudo o que se pode dizer.
*Erro conceitual comum:* retornar só a string final. É o mesmo erro do Lab 5 quando o aluno reportava a resposta e não a tabela — e é a razão de a Aula 26 exigir registro de trajetória, não de resposta.

### Bloco 2 (01:15–01:40) — O mesmo poder, agora pelo protocolo

**Conceito 6 — No MCP o catálogo deixa de ser seu.**
No Checkpoint 2 o aluno escreveu o schema. No Checkpoint 3 ele **descobre** o schema com `tools/list` — e a descrição que vai influenciar a escolha do modelo foi escrita por quem publicou o servidor. Isso muda a natureza do risco: a qualidade da decisão passa a depender de texto de terceiro, que entra no prompt.
*Erro conceitual comum:* tratar o servidor de terceiro como biblioteca confiável. Descrição de ferramenta é prompt; servidor desconhecido é prompt desconhecido — o fio que a Aula 26 puxa.

**Conceito 7 — Servidor MCP é um processo que lê JSON de uma linha e escreve JSON de uma linha.**
O transporte `stdio` significa literalmente isso: o cliente sobe o servidor como subprocesso e conversa por entrada e saída padrão, uma mensagem JSON-RPC por linha. Três verbos bastam: `initialize`, `tools/list`, `tools/call`. É por isso que existe `mcp_minimo.py` na pasta do lab — 80 linhas, biblioteca padrão, o mesmo protocolo sem SDK. Ler aquele arquivo é o antídoto contra achar que MCP é mágica, e é também o caminho offline do lab.
*Erro conceitual comum:* usar `print()` num servidor `stdio`. Qualquer byte fora do protocolo corrompe a conversa. Diagnóstico vai para `stderr`, sempre.

**Conceito 8 — A docstring da ferramenta é prompt.**
Com o SDK, a docstring da função decorada com `@servidor.tool()` **vira a `description`** publicada em `tools/list`. Ou seja: o texto que o aluno escreveria para a equipe é exatamente o texto que o modelo vai ler ao decidir. É o Conceito 4 da Aula 21 aparecendo como consequência de uma escolha de biblioteca.
*Erro conceitual comum:* docstring de uma linha ("busca no regulamento") num servidor que será usado por hosts que o autor nunca vai ver.

**Conceito 9 — Ferramenta e recurso, no mesmo servidor, para a diferença ficar concreta.**
O servidor do Checkpoint 4 expõe `buscar_regulamento` como **ferramenta** (ação; quem decide chamar é o modelo) e `regulamento://dispositivos` como **recurso** (dado; quem decide anexar é a aplicação). Duas linhas de código diferentes para dois donos de decisão diferentes.
*Erro conceitual comum:* expor o índice como ferramenta `ler_arquivo(caminho)`, o que põe caminho de arquivo no alcance do modelo — o exemplo canônico do Conceito 10 da Aula 21.

**Conceito 10 — A mesma ferramenta, escrita duas vezes, e o que sobra.**
Ao fim do lab o aluno escreveu `buscar_regulamento` duas vezes: como função no loop na mão e como ferramenta MCP. O que mudou: quem entrega o schema, quem valida, e onde o processo roda. O que não mudou: a função de busca, a assinatura, e o corpo do `loop_agente`. Essa invariância é o argumento inteiro do protocolo — e é o gancho do Lab 7, que troca o `REGISTRO` local por `session.call_tool` sem reescrever o agente.
*Nota de custo, e ela é do apêndice:* trocar a ferramenta local por uma ferramenta remota **não** muda a estrutura de custo da trajetória, porque o que a domina é o tamanho da observação devolvida, não onde ela foi produzida. Uma ferramenta MCP que devolve quarenta linhas de JSON encarece a trajetória inteira, e o efeito está quantificado em **A.2**.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 15 min | Setup + contexto + **recolhimento da Entrega 1** | Recolher a proposta (2 páginas, PDF ou link, uma por equipe) e anotar quem entregou; recap de uma linha da Aula 21 (cinco passos, quem executa); abrir o notebook e conferir o modo (chave por `getpass` ou simulador roteirado); o mapa dos quatro checkpoints **pelo que cada um imprime** e o entregável |
| 00:15 | 20 min | Demonstração guiada (live coding) | O loop **desenrolado à mão**, sem função nenhuma: montar a lista de mensagens, chamar o modelo, imprimir o JSON cru, executar a ferramenta na mão, anexar a mensagem `tool` com o `tool_call_id`, chamar de novo, ler a resposta final; depois, de propósito, um argumento inválido para ver o erro voltar como resultado. Termina sem escrever o laço — o laço é o Checkpoint 2 |
| 00:35 | 30 min | Checkpoints 1–2 (aluno executando) | CP1: os três schemas (`calcular_expressao` pronta como molde, `buscar_regulamento` e `consultar_cep` como TODO) e `validar`; CP2: `detectar_chamadas`, `parsear_argumentos`, `despachar` e `loop_agente` com orçamento de passos |
| 01:05 | 10 min | Intervalo | — |
| 01:15 | 25 min | Checkpoints 3–4 | CP3: `cliente_mcp.py` contra um servidor de referência por `stdio`, com `initialize`/`tools/list`/`tools/call` — ou `mcp_minimo.py` no caminho offline; CP4: `servidor_regulamento.py` próprio, com uma ferramenta e um recurso, chamado pelo cliente do CP3 |
| 01:40 | 10 min | **Entrega 1: devolutiva dirigida** | Projetar os cinco critérios; devolutiva em voz alta de 3 a 4 propostas voluntárias, uma por critério; os dois erros mais comuns (problema não verificável e plano de avaliação sem métrica por camada) |
| 01:50 | 10 min | Recolhimento | O que entregar do lab (notebook executado, servidor próprio, trajetória comentada, questões-guia, declaração de uso de IA), prazo de uma semana, critério; ponte para a Aula 23 |

## 4. Demonstração guiada

**Live coding "o loop desenrolado à mão" — 20 min, `codigo/lab-06-tools-mcp/lab-06-tools-mcp.ipynb` (células novas ao fim, apagadas depois).**

O objetivo não é adiantar o Checkpoint 2: é fazer a turma ver **uma volta** do ciclo com a lista de mensagens crescendo na tela, sem nenhuma função escondendo o mecanismo. O laço vem depois, e é deles.

Passos em alto nível:

1. Criar a lista `mensagens` com `system` e `user` na mão, e imprimir. Duas mensagens, nada mais.
2. Chamar o modelo uma vez com `SCHEMAS` e imprimir a mensagem devolvida crua: `tool_calls`, `id`, `name`, `arguments` com as barras de escape à mostra.
3. Anexar essa mensagem à lista e imprimir a lista: três mensagens agora.
4. Executar a ferramenta **na mão**, digitando `ferramenta_buscar_regulamento(termo="...")` numa célula — para separar visualmente "o modelo pediu" de "eu executei".
5. Anexar o resultado como `{"role": "tool", "tool_call_id": ..., "content": json.dumps(...)}` e imprimir a lista: quatro mensagens, e o `tool_call_id` casando com o `id` da segunda etapa.
6. Chamar o modelo de novo com a lista completa e ler a resposta final. Uma volta completa, cinco passos, zero framework.
7. Repetir a execução manual de propósito com um argumento inválido (`termo=""` ou um CEP de três dígitos), anexar o dicionário de erro como resultado, e chamar o modelo: mostrar que ele lê o erro e se recupera. Cravar: erro de ferramenta é informação, não exceção.
8. Parar antes de escrever o laço, e dizer isso em voz alta: o `while` com orçamento de passos é o Checkpoint 2.

**Número que a demo produz.** O contador de mensagens, e ele é o número que o apêndice usa. A lista sai de **2** mensagens, vai a **3** quando a resposta do assistente é guardada, vai a **4** quando o resultado da ferramenta é anexado, e a segunda chamada ao modelo envia **as quatro** — não só a última. Esse é o observável central da aula: a mesma pergunta é reenviada em toda volta, junto com tudo o que aconteceu antes. Se o provedor imprimir o campo `usage`, vale anotar na lousa os tokens de entrada das duas chamadas lado a lado: a segunda é visivelmente maior que a primeira, e a razão entre elas é a semente da conta de **A.1**. Onde não houver `usage`, o contador de mensagens já basta — 2, 3, 4, e a próxima volta seria 6.

Insumos preparados na véspera: o notebook rodado de ponta a ponta em modo API e em modo offline, com os tempos anotados; a saída do `cliente_mcp.py` contra o servidor de referência salva em texto; as rodas (`pip download`) de `mcp` e do servidor de referência num pendrive, para a sala sem rede.

## 5. Hands-on

Quatro checkpoints, cada um abrindo pelo observável, mais a janela da Entrega 1.

**Checkpoint 1 · 00:35–00:48 — Os três schemas e a validação.**
Escrever os schemas de `buscar_regulamento` e `consultar_cep` seguindo o molde de `calcular_expressao`, e implementar `validar(nome, argumentos)`. As três implementações já existem; o que é do aluno é o texto que o modelo lê e a barreira que o host aplica.
*Critério de conclusão observável:* a tela imprime `Checkpoint 1 OK — 3 schemas válidos, 8 casos de validação, calculadora barrando código`. O teste conferiu: três schemas com `description` de pelo menos 60 caracteres, todo parâmetro com `type` e `description`, todo nome presente no `REGISTRO`, os oito casos de validação passando (inclui parâmetro inventado, tipo errado, valor fora do `maximum` e ferramenta fora do catálogo) e a calculadora recusando uma expressão que não é aritmética.

**Checkpoint 2 · 00:48–01:05 — O loop na mão.**
Implementar `detectar_chamadas`, `parsear_argumentos`, `despachar` e `loop_agente`. Sem biblioteca de agente, sem framework: os cinco passos da Aula 21 nomeados no código.
*Critério de conclusão observável:* a tela imprime `Checkpoint 2 OK — conta, busca, erro tratado e orçamento de passos`. O teste conferiu cinco coisas: a pergunta de conta chega ao resultado numérico correto; a pergunta de regulamento cita o dispositivo certo; a trajetória tem a ordem `system, user, assistant, tool, assistant` com o `tool_call_id` casando com o `id` da chamada; argumento inválido devolve dicionário de erro em vez de exceção; e o **modelo teimoso**, que nunca para de pedir ferramenta, é chamado exatamente `max_passos = 3` vezes e a resposta contém a palavra `orçamento`.

**Checkpoint 3 · 01:15–01:27 — Cliente MCP contra um servidor existente.**
Completar `cliente_mcp.py`: parâmetros de `stdio`, `initialize`, `tools/list`, `resources/list` protegido por `try`, e `tools/call`. Rodar contra um servidor de referência instalado por `pip`.
*Critério de conclusão observável:* na saída do notebook aparecem o nome e a versão do servidor negociados no `initialize`, a lista de ferramentas com nome, obrigatórios e **descrição** de cada uma, e o resultado de uma chamada com `isError = False`. No caminho offline, a mesma evidência produzida por `python mcp_minimo.py`.

**Checkpoint 4 · 01:27–01:40 — Seu próprio servidor MCP.**
Escrever `servidor_regulamento.py`: `buscar_regulamento` decorada como ferramenta, com docstring escrita para o modelo, validação de `termo` e limite de `k`; e o índice do acervo exposto como **recurso** em `regulamento://dispositivos`.
*Critério de conclusão observável:* o `cliente_mcp.py` do CP3, apontado para o servidor do aluno, imprime a ferramenta em `tools/list`, o recurso em `resources/list`, e o resultado de `buscar_regulamento` com os dispositivos certos. Nenhum `print()` no servidor: diagnóstico só em `stderr` — e o sintoma de violação é o cliente falhando ao decodificar JSON.

**Entrega 1 do projeto — recolhida às 00:05, devolutiva às 01:40.**
Uma proposta por equipe, duas páginas, PDF ou link. Os cinco itens que o instrutor olha, na ordem em que olha:

1. **Problema claro e verificável.** Existe uma pergunta ou tarefa concreta, com usuário nomeado, e é possível dizer se o sistema acertou. "Assistente inteligente para a universidade" não é problema; "responder perguntas sobre o regulamento citando o artigo, para alunos de graduação" é.
2. **Duas técnicas do curso, nomeadas.** RAG + agente, tool calling/MCP + juiz calibrado, LoRA + avaliação sistemática. Nomeadas, não insinuadas.
3. **Plano de avaliação com métrica por camada.** Conjunto de teste próprio, com tamanho declarado, e uma métrica por camada do sistema — `recall@k` para a recuperação, taxa de acerto de ferramenta para a camada de ação, e uma métrica de resposta. Uma métrica só, no fim do pipeline, não atende.
4. **Divisão de trabalho.** Três ou quatro pessoas, com quem faz o quê. Não precisa ser definitivo; precisa existir.
5. **Viabilidade em free tier.** Qual modelo, qual provedor, qual quota, qual tamanho de corpus. Se o plano exige GPU paga ou 50 mil chamadas de API, ele é replanejado hoje e não na Aula 26.

*Acréscimo da V2 ao item 5, e ele é consequência do apêndice:* "viável em free tier" para um sistema com laço tem uma conta associada, e ela é a de **A.1**. Uma proposta que prevê agente com dez a quinze passos por consulta e observações grandes gasta, por pergunta, algo da ordem de dezenas de milhares de tokens enviados — e a quota do free tier é por minuto e por dia. A pergunta que a devolutiva faz, quando a proposta tem laço, é uma só: **qual é o `max_passos` de vocês, e de onde saiu esse número?** Quem responder "não pensei" leva o A.1 como leitura dirigida para a Entrega 2.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **`pip install mcp` falha** ou a sala não tem rede | Erro na célula de instalação do CP3 | `mcp_minimo.py`, na pasta do lab: cliente e servidor JSON-RPC sobre `stdio` escritos à mão, biblioteca padrão, sem instalar nada. Vale como CP3 e é pedagogicamente superior — a turma vê o protocolo cru. O instrutor também leva as rodas (`pip download`) num pendrive |
| **Aluno sem chave de API** | `getpass` vazio | O simulador roteirado embutido fecha os CP1 e CP2 de forma determinística. O notebook avisa em letra grande que a escolha da ferramenta é roteirada e que aquilo não mede modelo nenhum |
| **Chave de API vazando** no arquivo entregue | Chave visível numa célula | `getpass` em todos os caminhos; a nota do recolhimento avisa que chave hardcoded é tratada como problema de segurança e o instrutor confere na correção |
| **Servidor de referência do CP3 mudou de nome ou de ferramenta** | `tools/list` vazio ou erro de módulo | O `cliente_mcp.py` é genérico: recebe o comando do servidor, o nome da ferramenta e os argumentos por linha de comando. Trocar o servidor é trocar uma string. Conferir na véspera é parte do preparo |
| **`print()` no servidor `stdio`** corrompe a conversa | Cliente falha ao decodificar JSON | Está escrito no notebook, no Conceito 7 e no comentário do arquivo: diagnóstico só em `stderr`. É o erro mais comum do CP4 e o instrutor pergunta isso antes de olhar o código |
| **Aluno tenta usar framework de agente** | Célula com import de biblioteca de agente | Política dita na abertura: hoje é na mão, de propósito, e o teste do CP2 exige as funções nomeadas. Comparação com framework é a Aula 24 e o Lab 7 |
| **Quota estourando no CP2** com a sala inteira no mesmo provedor | 429 a partir da terceira volta do loop de alguém | Baixar `MAX_PASSOS` para 2 na célula de configuração e dizer em voz alta por que isso funciona: o custo enviado cai com o **quadrado** do orçamento de passos, então cortar o orçamento pela metade corta o gasto por pergunta por quatro (**A.2**). É contingência e é aula ao mesmo tempo |
| **Equipe sem a Entrega 1** | Não entrega às 00:05 | Registrar quem não entregou e dar prazo de 24 h com desconto declarado; a devolutiva das 01:40 é a mesma para todos, então quem não entregou ainda ouve os cinco critérios |
| **A devolutiva da Entrega 1 come o tempo dos checkpoints** | 01:20 e a sala discutindo projeto | A devolutiva tem janela fixa (01:40–01:50) e não começa antes. Perguntas sobre projeto durante os checkpoints são anotadas e respondidas na janela |
| **Tempo estourar no Bloco 2** | 01:35 e ninguém no CP4 | O CP4 vai para casa, e o instrutor anuncia isso: os CP1 a CP3 são o núcleo. O servidor próprio é o item mais fácil de terminar sozinho, porque é um arquivo com dois decoradores |
| **Colab e `asyncio`** brigando no cliente MCP | Erro de event loop dentro de célula | Os CP3 e CP4 rodam por `!python arquivo.py`, em subprocesso — nunca com `await` dentro de célula. Isso está no notebook e é deliberado |

## 7. Artefatos produzidos

- `lab-06-tools-mcp.ipynb` executado, com as saídas visíveis: `Checkpoint 1 OK`, `Checkpoint 2 OK`, o `initialize`/`tools/list`/`tools/call` do CP3 e a mesma tríade contra o servidor próprio no CP4.
- `servidor_regulamento.py` — servidor MCP próprio, com uma **ferramenta** e um **recurso**.
- `cliente_mcp.py` — cliente genérico por `stdio`, que serve para qualquer servidor.
- **Trajetória comentada:** a lista de mensagens de uma execução do `loop_agente`, com 3 a 5 linhas apontando onde o modelo acertou e onde vacilou. É o embrião da análise de trajetória do Lab 7.
- Respostas às **quatro questões-guia** em células de markdown do notebook.
- **Declaração de uso de IA** — quais ferramentas, para quê, em duas linhas.
- **Entrega 1 do projeto** (por equipe): proposta de duas páginas, com os cinco itens, entregue às 00:05 e devolvida com comentário do instrutor.

## 8. Desafio pós-aula

**Este lab é o entregável avaliado da semana.** Prazo: uma semana. O conteúdo está no §7; os Checkpoints 1 a 3 são o núcleo obrigatório e o CP4 pode ser concluído em casa.

Extensão dirigida, e ela é literalmente a primeira célula do Lab 7: **ligar o servidor MCP ao loop do Checkpoint 2**. O caminho tem dois passos — converter cada ferramenta devolvida por `tools/list` para o formato de `SCHEMAS` (o `inputSchema` do MCP já é o `parameters` que o seu schema espera), e fazer o `despachar` chamar `session.call_tool` quando o nome vier do servidor, em vez de olhar o `REGISTRO` local. A pergunta dirigida é a que interessa: **o que muda no `loop_agente`?** Se a resposta for "nada", o protocolo cumpriu o que promete.

Segunda extensão, opcional: trocar a busca por termos do `corpus_regulamento.buscar` pelo pipeline híbrido do Lab 5 — copiando `chunks.json` do `lab05_saida/` para a pasta do lab, o módulo já usa a sua base. A assinatura não muda, e é esse o ponto.

Terceira extensão, com número: **medir o `d` do próprio loop.** Rodar `loop_agente` numa pergunta que exija duas ferramentas, somar os tokens de entrada de todas as chamadas (campo `usage`, quando o provedor devolver; contagem de caracteres dividida por 4 como estimativa, quando não devolver) e comparar com `n·p₀`. A razão entre os dois é o fator pelo qual a estimativa ingênua erra, e **A.2** diz qual valor esperar. Com o `d` medido em mão, resolver a desigualdade de **A.1** e responder: o `MAX_PASSOS = 4` do notebook está apertado ou frouxo para o seu caso?

Leitura: a especificação do Model Context Protocol, seção de arquitetura e a de ferramentas (`[definir na oferta]` — a versão vigente é conferida na semana da aula). **Pergunta dirigida:** o protocolo separa ferramenta, recurso e prompt por quem decide usar. Escolha uma capacidade do seu projeto e argumente em cinco linhas se ela deve ser ferramenta ou recurso — e o que muda no risco de segurança em cada caso.

## 9. Critérios de avaliação

Este lab **é avaliado** e compõe os **30%** dos laboratórios, com a política da ementa — oito labs, entrega até uma semana, **descartando a menor nota**. A **Entrega 1** vale **5%** da nota final, dentro dos 40% do projeto, exatamente como a ementa define. Nenhum peso novo é inventado aqui.

Distribuição da nota deste lab:

- **Checkpoints 1 e 2, com saída visível — 45%.** Os dois `Checkpoint N OK` impressos, e o loop rodando nas três perguntas. **O loop precisa ser o do aluno:** notebook que chama uma biblioteca de agente e não tem `detectar_chamadas`, `parsear_argumentos`, `despachar` e `loop_agente` não atende ao checkpoint, mesmo funcionando.
- **Checkpoint 3, cliente MCP — 15%.** `initialize`, `tools/list` e `tools/call` na saída, contra o servidor de referência ou contra o `mcp_minimo.py`.
- **Checkpoint 4, servidor próprio — 20%.** A ferramenta com docstring escrita para o modelo, o recurso exposto como recurso, validação de argumento no servidor, e nenhum `print()` no caminho do `stdio`.
- **Trajetória comentada e questões-guia — 15%.** Avaliadas por precisão conceitual. As duas que separam as notas: a que pede a linha em que o **host** executa, e a que pede o que mudou e o que não mudou entre a ferramenta escrita à mão e a ferramenta MCP.
- **Declaração de uso de IA presente — 5%.** Ausência zera este item e habilita defesa oral.

**Entrega 1 do projeto — 5% da nota final** (proposta), avaliada pelos cinco itens do §5: problema verificável, duas técnicas nomeadas, plano de avaliação com métrica por camada, divisão de trabalho e viabilidade em free tier. Cada item vale um ponto do total desta entrega. A devolutiva é dada em sala, na janela das 01:40, e por escrito na proposta devolvida.

**Nota sobre a prova.** A prova da Aula 17 já foi aplicada; a composição dela é diagnóstico e interpretação **42** · justificativa de escolha **40** · conceito aplicado **8** · derivação **10**. Registra-se aqui porque o hábito que este lab treina é o da parte de 40 pontos: justificar uma escolha de engenharia com um número. "`max_passos` igual a quatro" sem justificativa é a resposta que perde ponto; "quatro, porque com a observação típica deste sistema é o que cabe em cinco mil tokens por pergunta" é a que ganha.

Observável em sala, sem nota: ao ser questionado no recolhimento, o aluno aponta no próprio código a linha em que o host executa a ferramenta, e diz por que o resultado precisa voltar com o papel `tool`.

## Apêndice matemático — índice

**Dois itens, e dois é o número certo.** Este lab tem exatamente um lugar com fundamento formal a recolher — o orçamento do laço do Checkpoint 2 — e ele rende duas coisas distintas: a conta e a razão pela qual a conta não é linear. Os Checkpoints 1, 3 e 4 são schema, protocolo e transporte: eles têm rigor de engenharia e não têm matemática, e **inventar um terceiro item para satisfazer forma ensinaria o aluno a ignorar a Parte 2**.

**Este é o primeiro item de apêndice do bloco de agentes.** A Aula 21 não tem apêndice próprio, por decisão registrada: ela é aula de arquitetura e protocolo. O formalismo do bloco começa aqui, no lab, porque é aqui que o `max_passos` sai do código e passa a ter uma justificativa.

| Item | O que estabelece | Checkpoint |
|---|---|---|
| **A.1** | A conta de custo acumulado do laço: o modelo não guarda estado, então a chamada `k` reenvia a trajetória inteira e custa `p₀ + (k−1)·d` tokens; o total de uma trajetória de `n` voltas é `T(n) = n·p₀ + d·n(n−1)/2`. Com o `p₀` e o `d` medidos neste lab, a conta é resolvida em números e invertida: dado um teto `B` de tokens enviados por pergunta, `max_passos` é o maior `n` que satisfaz `T(n) ≤ B` — e o `MAX_PASSOS = 4` do notebook é exatamente a solução dessa desigualdade para `B = 5 000`. | **CP2** |
| **A.2** | Por que o custo é **superlinear** no número de passos: chamadas crescem em `n`, tokens enviados crescem em `n²`, e a razão entre o total real e a estimativa ingênua cresce com o tamanho da trajetória. O custo marginal do `k`-ésimo passo, o efeito da raiz quadrada no orçamento (dobrar `B` compra apenas `√2` passos), o que domina `d` na prática (a observação, não o pensamento), e as três coisas que mudam a **ordem** de crescimento em vez da constante. | **CP2** |

**Continuidade.** A **Aula 23** retoma esta conta no apêndice dela, no item A.1, com duas extensões que não cabem num lab: a latência da trajetória e por que ela não admite paralelismo, e a justificativa formal das três táticas de controle de trajetória (truncar, resumir, referenciar) em termos de qual termo da soma cada uma ataca. O **Lab 7 (Aula 25)** fecha o fio medindo a trajetória de verdade: passos, tokens de entrada e saída acumulados, e custo por tarefa resolvida — e é lá que o `d` deste apêndice deixa de ser estimativa e passa a ser leitura de um arquivo de trajetória. Quem seguir os três na ordem vê a mesma desigualdade três vezes: escrita aqui, generalizada na Aula 23, e medida no Lab 7.
