---
aula: 21
titulo: "Tool calling e Model Context Protocol (MCP)"
modulo: "5 — RAG, Ferramentas e Agentes de IA"
tipo: teorica
semana: 11
duracao_min: 120
versao: v2
---

# Aula 21 — Tool calling e Model Context Protocol (MCP)

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** Esta aula já era conduzida pela aplicação na V1 e por isso muda pouco:
> abre por uma pergunta sobre o sistema que a turma acabou de construir, o conceito central vira
> número medido na demo, e o exercício já é de reescrita de schema. **Não há apêndice matemático**:
> a aula é de arquitetura e protocolo, não existe fórmula no fluxo para recolher, e a Parte 2 do
> deck diz isso explicitamente e aponta os apêndices de outras aulas (A.2 da Aula 19, A.5 da Aula
> 28, A.5 da Aula 9, A.1 da Aula 23 e A.2 da Aula 24). Carga horária, numeração e objetivos de
> aprendizagem inalterados.

## 1. Objetivo da aula

Dar mãos ao modelo sem perder de vista quem manda: o modelo emite uma **chamada estruturada** e o **host executa** — o modelo não roda nada. E estabelecer as duas consequências práticas disso: o schema da ferramenta é parte do prompt (mudar um nome muda a taxa de acerto) e padronizar essa exposição em vez de integrar de um em um é o problema que o MCP resolve.

## 2. Resultados de aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Descrever** os cinco passos do ciclo de tool calling e **apontar**, em cada um, quem executa: o modelo, o host ou a ferramenta.
2. **Ler** e **escrever** uma chamada de ferramenta em JSON — nome, argumentos, identificador de correlação — e **explicar** por que o resultado volta como mensagem de papel `tool`.
3. **Justificar** por que nome, descrição e nomes de parâmetro de uma ferramenta são **parte do prompt**, e **prever** o efeito de degradá-los sobre a taxa de acerto.
4. **Distinguir** as três formas pelas quais um modelo passa a usar ferramentas — exemplos no prompt, SFT de formato e auto-supervisão à la Toolformer.
5. **Avaliar** um schema de ferramenta contra seis propriedades (estreita, bem nomeada, validável, permissionada, observável, com efeito colateral determinístico) e **reescrever** um schema ruim.
6. **Explicar** a arquitetura host/cliente/servidor do MCP, **distinguir** recurso de ferramenta pelo que decide o uso, e **argumentar** por que padronizar vence N integrações um-a-um.

## 3. Teoria aplicada

### Bloco 1 (00:10–00:55) — Do texto à ação

**Conceito 1 — O modelo não executa nada. Ele pede.**
O ciclo tem cinco passos e só um deles é do modelo: (i) o host manda o prompt **com o catálogo de ferramentas serializado dentro**; (ii) o modelo devolve, em vez de prosa, um texto que descreve a chamada — nome da ferramenta e argumentos, em JSON; (iii) o **host** valida os argumentos, decide se pode executar e executa; (iv) o resultado volta para o modelo como uma mensagem de papel `tool`, amarrada à chamada por um identificador; (v) o modelo lê o resultado e sintetiza a resposta final. Nenhum byte de código roda dentro do modelo.
*Analogia do instrutor:* o modelo é um médico que escreve receita. Ele não manipula o remédio, não abre a farmácia e não decide se você tem convênio — ele escreve um pedido, e o sistema em volta obedece ou recusa.
*Erro conceitual comum:* achar que o modelo "tem acesso" a uma calculadora, a um banco ou à internet. Ele não tem. Quem tem é o programa que hospeda a conversa, e todo poder que a ferramenta dá foi dado por esse programa. Isso não é sutileza acadêmica: é onde mora a decisão de segurança da Aula 26.

**Conceito 2 — Anatomia da chamada, e por que existe um identificador.**
A chamada é um objeto com três campos que importam: `id`, `name` e `arguments` (uma string JSON). A resposta correspondente é uma mensagem com `role: "tool"` e o mesmo `tool_call_id`. O identificador existe porque um único turno pode pedir **várias** chamadas de uma vez — três buscas em paralelo, por exemplo — e sem correlação explícita não há como dizer qual resultado é de qual pedido.
*Erro conceitual comum:* devolver o resultado como se fosse uma mensagem de usuário ("o resultado foi 60"). Funciona às vezes e por acidente: o modelo foi treinado a esperar aquele papel específico ali, e trocar o papel é sair da distribuição de treino.

**Conceito 3 — A saída estruturada não vem de um canal mágico.**
O catálogo de ferramentas é **texto injetado no prompt** pelo provedor, num formato que o modelo viu no pós-treino. E o JSON sai bem formado por duas razões que se somam: treino de formato (SFT com milhares de exemplos de chamada) e, do lado do serving, **decodificação restrita** — a cada passo o decodificador zera a probabilidade dos tokens que quebrariam a gramática do schema. É a mesma alavanca de decodificação da Aula 10, agora com uma gramática por cima.
*Erro conceitual comum:* concluir que, com decodificação restrita, o JSON está sempre *correto*. Ele está sempre **bem formado** — o que é outra coisa. Nada impede o modelo de preencher `expressao` com a pergunta inteira, ou de escolher a ferramenta errada com sintaxe impecável.

**Conceito 4 — O schema é parte do prompt, e isso costuma surpreender a turma.**
Como o catálogo entra no prompt, **cada palavra dele é engenharia de prompt**: o nome da ferramenta, a descrição, o nome de cada parâmetro, o `enum` de valores aceitos, o exemplo dentro da descrição do parâmetro. Renomear `expressao` para `q` e cortar a descrição de três frases para uma palavra não é refatoração — é reescrever o prompt. E o efeito é mensurável: a demonstração desta aula roda a **mesma função** com três catálogos e imprime a taxa de acerto de cada um.
*Analogia:* é a diferença entre uma caixa de ferramentas etiquetada e uma gaveta com tudo dentro. O conteúdo é o mesmo; o tempo até achar a chave certa, não.
*Erro conceitual comum:* tratar a descrição da ferramenta como documentação para humano. O leitor daquele texto é o modelo, na hora de decidir. Documentação para a equipe vai no código; para o modelo, vai no schema.

**Conceito 5 — Como modelos aprendem a usar ferramentas.**
Três caminhos, em ordem histórica e de custo. **Exemplos no prompt:** mostrar duas ou três chamadas bem feitas e deixar o aprendizado em contexto fazer o resto — funciona, gasta contexto em toda requisição e é frágil quanto ao formato. **SFT de formato:** ajustar o modelo com dezenas de milhares de exemplos de chamada, o que o torna confiável no formato e é a razão de os modelos de hoje já virem "com tool calling". **Auto-supervisão** — Toolformer (Schick et al., arXiv 2302.04761): o modelo insere candidatos de chamada de API no meio de textos comuns, executa esses candidatos e **mantém apenas as chamadas que reduzem a perda de previsão dos tokens seguintes**. O critério de qualidade não é rótulo humano: é utilidade medida na própria função de perda.
*Fundamento mobilizado:* o critério do Toolformer é a redução da perda de previsão nos tokens seguintes — utilidade convertida em quantidade mensurável. A aula **não** deriva a perda; a entropia cruzada do próximo token está no **Apêndice A.4 da Aula 9**.
*Erro conceitual comum:* achar que Toolformer ensina *quais* ferramentas existem. Ele ensina *quando chamar* e *o que passar*, usando o próprio corpus como supervisão — e é essa ideia, não o conjunto de APIs do artigo, que sobreviveu.

### Bloco 2 (01:05–01:50) — Design de ferramenta e o protocolo

**Conceito 6 — Seis propriedades de uma boa ferramenta — e duas que só aparecem quando o catálogo cresce.**
*As duas acrescentadas nesta oferta* (Anthropic, *Writing effective tools for agents*, set/2025): **(7) espaço de nome** — com dezenas de ferramentas de servidores diferentes, prefixar por domínio (`asana_buscar`, `jira_buscar`) é o que impede o modelo de escolher a busca do sistema errado; o N×M do Conceito 8 cria o problema e o prefixo é a defesa mais barata. **(8) resposta econômica em tokens** — o que a ferramenta **devolve** também é prompt, e é o item mais esquecido: devolver o JSON inteiro da API gasta contexto que o laço reenvia a cada volta. Devolver o campo útil, paginado e com identificador para buscar o resto **é** design de ferramenta.
*Como saber se a descrição está boa, em vez de achar:* as oito são critério de projeto, não medição. A versão medida é um **laço** — conjunto pequeno de tarefas que exercitam as ferramentas, mede-se quantas o agente completa, reescreve-se a descrição, mede-se de novo. É a quarta alavanca da **Aula 13 (A.7)** aplicada ao schema em vez de ao prompt de sistema, e é o que faz "descrição de ferramenta é prompt" deixar de ser figura de linguagem: se é prompt, é otimizável contra métrica.

(i) **Estreita** — faz uma coisa, e o nome diz qual. (ii) **Bem nomeada** — o nome e a descrição são lidos pelo modelo no momento da escolha. (iii) **Validável por schema** — tipos, `required`, `enum`; e o host **rejeita** antes de executar, sem confiar no modelo. (iv) **Permissionada** — a ferramenta roda com o mínimo de privilégio necessário, e ação sensível exige confirmação humana. (v) **Observável** — cada chamada deixa registro de argumentos, resultado, latência e erro; sem isso não existe depuração de agente. (vi) **Com efeito colateral determinístico** — mesma entrada, mesmo efeito; e idealmente idempotente, porque o loop vai repetir a chamada quando não entender a resposta.
*Fundamento mobilizado (propriedade vi):* o loop repete a chamada, e o custo desse reenvio cresce com o quadrado dos passos. → **Apêndice A.1 da Aula 23**
*Analogia:* é o mesmo checklist de uma boa API interna, com um usuário novo e estranho: um cliente que lê a documentação rápido, não pede esclarecimento e às vezes chuta.

**Conceito 7 — O catálogo das más ferramentas.**
**Vaga** — `dados(query)`, "pega dados": o modelo não tem como decidir quando usar, e a taxa de acerto cai. **Ampla demais** — `executar_sql(comando)` ou `rodar_shell(cmd)`: a validação por schema perde sentido, porque a linguagem inteira caiba no parâmetro. **Silenciosamente com estado** — `proximo_registro()` depende de um cursor invisível; o modelo repete a chamada, o cursor anda, e a trajetória fica irreproduzível. **Irreversível sem confirmação** — `enviar_email`, `apagar_registro`, `pagar` sem passo de confirmação: o custo do erro deixa de ser um retry e passa a ser um incidente.
*Erro conceitual comum:* resolver o problema de "muitas ferramentas" criando uma ferramenta genérica com um parâmetro `acao`. Isso não reduz a complexidade, só a esconde do schema — e o schema era exatamente o lugar onde ela era verificável.

**Conceito 8 — O problema N×M, que é o motivo de existir um protocolo.**
Com `N` hosts (editor, assistente de terminal, chat interno, agente próprio) e `M` sistemas para integrar (repositório, banco, base RAG do Lab 5, ticket, calendário), integrar de um em um custa `N × M` adaptadores, cada um com sua autenticação, seu formato de erro e seu ciclo de vida. Com um protocolo comum, cada host implementa **um** cliente e cada sistema expõe **um** servidor: `N + M`. É a mesma economia que a Linguagem de Consulta Estruturada trouxe para bancos e que o Protocolo de Servidor de Linguagem (LSP) trouxe para editores — e o MCP é declaradamente inspirado no segundo.
*Fundamento mobilizado:* crescimento multiplicativo contra aditivo; a mesma multiplicação reaparece sobre orçamentos de passos na Aula 24. → **Apêndice A.2 da Aula 24**
*Erro conceitual comum:* ver o MCP como "uma forma de dar ferramentas ao modelo". Dar ferramenta ao modelo já é possível sem protocolo nenhum — é o Lab 6, parte (a). O que o protocolo resolve é **reuso e distribuição**: a mesma ferramenta servindo hosts diferentes sem reescrita.

**Conceito 9 — MCP: host, cliente, servidor.**
Três papéis. O **host** é a aplicação onde a conversa acontece e onde o modelo é chamado; é ele que decide o que expor ao modelo e que executa as decisões. O **cliente** é o componente dentro do host que mantém uma conexão com um servidor — um cliente por servidor. O **servidor** é um processo separado que expõe capacidades: ele não fala com o modelo, ele fala com o cliente. O transporte é `stdio` (servidor local como subprocesso, o caso do Lab 6) ou HTTP (servidor remoto). A troca é JSON-RPC: `initialize` negocia capacidades, `tools/list` descobre o que existe, `tools/call` executa.
*Analogia:* o servidor é um driver de dispositivo. Ele não sabe que aplicação vai usá-lo, e é justamente por isso que serve para todas.
*Erro conceitual comum:* imaginar que o servidor MCP conversa com o modelo. Ele nunca vê o modelo. Ele responde a um cliente; quem monta o prompt e chama o modelo é o host — a mesma separação do Conceito 1, agora entre processos.

**Conceito 10 — Recurso, ferramenta e prompt: o que decide o uso.**
As três primitivas que um servidor expõe se distinguem por **quem escolhe usá-las**. **Ferramenta** é ação, e quem escolhe é o **modelo** — é o `tools/call` do Conceito 9. **Recurso** é dado endereçável por URI (um arquivo, uma linha de banco, um documento do acervo), e quem escolhe anexar ao contexto é a **aplicação** ou o usuário — não o modelo. **Prompt** é um template parametrizado que o **usuário** invoca explicitamente. Do lado do cliente existem capacidades simétricas — pedir uma geração ao modelo do host (*sampling*), declarar as raízes do sistema de arquivos que o servidor pode ver (*roots*), pedir um dado que falta ao usuário (*elicitation*).
*Erro conceitual comum:* expor o acervo inteiro como ferramenta de leitura arbitrária ("`ler_arquivo(caminho)`") quando o que se queria era um recurso: dado que a aplicação escolhe anexar, com o caminho fora do alcance do modelo.
*O que o MCP não resolve, e vale dizer em voz alta:* schema ruim continua ruim depois de padronizado; permissão continua sendo decisão do host; e servidor de terceiro amplia a superfície de **injeção indireta** — o texto que volta de uma ferramenta entra no mesmo campo da instrução do sistema, exatamente como o documento recuperado da Aula 19. A Aula 26 é inteira sobre isso.

### Tabela de tempos

| Início | Dur. | Bloco | Subtemas reais |
|---|---|---|---|
| 00:00 | 10 min | Abertura | Recap da Aula 20 (o pipeline medido, as duas tabelas, o pulso de quem chegou ao CP6) e devolutiva de uma linha sobre o lab; a tese de hoje: o modelo passa a **pedir** ações e o host executa; aviso operacional de que a Entrega 1 do projeto é recolhida na próxima aula |
| 00:10 | 45 min | Bloco 1 — Do texto à ação | O ciclo de cinco passos e quem executa cada um; anatomia da chamada em JSON e o papel `tool` com identificador de correlação; por que o JSON sai bem formado (schema no prompt + decodificação restrita) e por que bem formado ≠ correto; o schema é parte do prompt; demonstração "três catálogos, uma função" (12 min); como modelos aprendem a usar ferramentas — few-shot, SFT de formato, Toolformer |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — Design de ferramenta e MCP | As seis propriedades da boa ferramenta; o catálogo das más (vaga, ampla, com estado, irreversível); o problema N×M e a analogia com o LSP; MCP host/cliente/servidor, transportes e o handshake JSON-RPC; recurso × ferramenta × prompt pelo critério de quem decide; ecossistema atual e o que o MCP **não** resolve; exercício em dupla (7 min) |
| 01:50 | 10 min | Fechamento | Síntese: o modelo pede, o host executa, o schema é prompt, o protocolo é reuso; ponte para o Lab 6 (Aula 22) com as três partes; lembrete da Entrega 1; leitura do Toolformer com pergunta dirigida |

## 4. Demonstração guiada

**Demo "três catálogos, uma função" — 12 min, `codigo/demo-tool-calling.py`.**

O objetivo é duplo: tornar visível *quem executa o quê* (Parte 1) e transformar "o schema é parte do prompt" de afirmação em número (Parte 2). O script só usa a biblioteca padrão; a chave da API vem de variável de ambiente e nunca aparece no arquivo. Há modo offline com um simulador **roteirado**, que mostra a mecânica do loop e é rotulado em toda saída como não sendo medição de modelo.

Passos em alto nível:

1. Mostrar o catálogo de uma ferramenta só — `calcular_expressao` — e dizer em voz alta que aquele JSON vai ser **serializado dentro do prompt**.
2. Fazer a pergunta ("quanto é 12,5% de 480?") e imprimir o JSON cru que o modelo devolveu: `tool_calls` com `id`, `name` e `arguments`. Não há resposta em prosa nesse turno.
3. Mostrar o host validando (o regex de caracteres permitidos rejeita qualquer coisa que não seja aritmética) e executando; imprimir o retorno.
4. Mostrar o resultado voltando como mensagem de papel `tool` com o `tool_call_id`, e o modelo sintetizando a resposta final. Fechar o ponto: o modelo emitiu texto, o programa obedeceu.
5. Trocar de assunto para a Parte 2: seis perguntas com gabarito aritmético, três catálogos, **a mesma função executada nos três**.
6. Rodar e imprimir a tabela: catálogo bom (nome descritivo, descrição de três frases, parâmetro `expressao` com exemplo), catálogo magro (`calc`, descrição de uma palavra, parâmetro `q`) e catálogo vago (`ferramenta`, "uso geral", parâmetro `entrada`).
7. Ler a coluna "chamou" ao lado da coluna "acertou": o modelo quase sempre **chama** — o formato está garantido pela decodificação restrita — e erra o **argumento**. Bem formado não é correto.
8. Fechar com o que a demo não mostrou: permissão, observabilidade e padronização. As ferramentas estão cravadas no arquivo; trocar de host obriga a reescrever tudo — e esse é o Bloco 2.

**Número que a demo produz, e que a aula usa como evidência:** a **taxa de acerto de cada um dos
três catálogos** sobre as mesmas 6 perguntas com gabarito aritmético, ao lado da taxa de **chamada**
de cada um — duas colunas, três linhas. É esse par de colunas que transforma "o schema é parte do
prompt" (Conceito 4) de afirmação em medição, e ele é citado de volta no fluxo em dois pontos: no
slide 9, quando a ferramenta vaga é apresentada ("vocês acabaram de ver na tabela da demo"), e na
segunda frase de síntese do fechamento ("a taxa de acerto mudou sem uma linha de código mudar"). A
coluna "chamou" é a que sustenta a distinção **bem formado ≠ correto**, e sem ela a tabela mediria
outra coisa. *Ressalva de método declarada em aula:* com 6 perguntas, a tabela mostra a direção do
efeito, não o tamanho dele — o tratamento formal está no **Apêndice A.5 da Aula 28**.

Insumos preparados na véspera: o script rodado em modo `api` com `--salvar-saida`, e o arquivo de saída levado para a aula. Se a rede da sala cair, projeta-se a saída salva — o número vem de uma execução real, com data e modelo anotados, nunca de estimativa.

## 5. Hands-on

**Exercício em dupla — "reescrever o schema ruim" (7 min, 01:43–01:50).**

Projetar uma ferramenta real e mal desenhada:

```json
{
  "name": "dados",
  "description": "pega dados do sistema",
  "parameters": {
    "type": "object",
    "properties": {
      "acao": {"type": "string"},
      "params": {"type": "object"}
    }
  }
}
```

O contexto dito em voz alta: esse `dados` hoje faz três coisas — consulta o regulamento por texto, lê a matrícula de um aluno por código e envia um e-mail de confirmação.

Cada dupla entrega três itens:

1. **Duas ou três ferramentas estreitas** no lugar de `dados`, com nome, descrição de uma ou duas frases redigida *para o modelo ler*, e os parâmetros com tipo e nome explícito. Onde couber, um `enum`.
2. **Qual delas exige confirmação humana antes de executar**, e por quê em uma frase.
3. **Qual das seis propriedades o schema original violava mais** — e a frase que justifica a escolha.

Critério de conclusão observável: a dupla entrega as três coisas por escrito, e ao menos duas duplas leem em voz alta a descrição que escreveram para a ferramenta de envio de e-mail. O ponto que o instrutor persegue na correção: `enviar_email` não é ruim por ser irreversível — é ruim por ser irreversível **sem confirmação**; e a diferença entre as duas coisas mora no host, não no schema.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Rede ou free tier indisponível** na hora da demo | Erro de quota ou timeout na primeira chamada | Projetar a saída salva da véspera (`--salvar-saida`); a Parte 1 também roda em modo offline com o simulador roteirado, que mostra a mecânica. A tabela da Parte 2 **não** é reexecutada com o simulador como se fosse medição — o número projetado é o da execução real |
| **Modelo do provedor aposentado** ou renomeado | Erro 400/404 na chamada | O identificador do modelo é variável de ambiente (`MODELO`); trocar por um da lista atual do provedor. Conferir isso na véspera é parte do preparo |
| **A turma trata tool calling como "o modelo executa código"** | Perguntas do tipo "e se ele apagar meu banco?" | Voltar ao Conceito 1 e ao passo 3 da demo: quem executa é o host, e todo poder foi concedido por ele. A pergunta é boa e é a Aula 26 — registrar e devolver |
| **Discussão de framework** (qual biblioteca de agente usar) consome o Bloco 2 | Debate sobre bibliotecas aos 01:15 | Cortar com a política da disciplina: no Lab 6 o loop é escrito **na mão**, sem framework, de propósito; comparação com framework é a Aula 24 e o Lab 7. Registrar a pergunta para o canal da turma |
| **MCP virar discussão de produto** ("vale a pena usar X?") | Perguntas sobre ferramentas comerciais | Ficar na arquitetura e nas primitivas, que é o que a ementa pede. O estado do ecossistema é `[definir na oferta]` — o instrutor confere na semana da aula em vez de citar de memória |
| **Tempo estourar no Bloco 1** (a demo gera muita pergunta) | 00:50 e ainda na tabela dos catálogos | Cortar o Conceito 5 (como modelos aprendem) para leitura dirigida — ele está escrito no plano e é o único bloco do dia que não é pré-requisito do Lab 6. Proteger design de ferramenta e MCP |
| **Alunos sem equipe ou sem proposta** a um dia da Entrega 1 | Perguntas sobre o projeto na abertura | Anunciar na abertura os cinco itens que a proposta precisa ter (estão no plano da Aula 22) e reservar os dois minutos finais do fechamento para isso. Não abrir a discussão no meio do conteúdo |

## 7. Artefatos produzidos

- Folha do exercício em dupla: o schema `dados` reescrito em duas ou três ferramentas estreitas, com a marcação de qual exige confirmação e a propriedade violada.
- Anotação pessoal do **ciclo de cinco passos** com a coluna "quem executa" preenchida, e do diagrama host/cliente/servidor do MCP.
- `codigo/demo-tool-calling.py` no repositório da disciplina, com a saída da execução da véspera anotada com data e modelo.
- Nenhum entregável avaliado nesta aula. O que ela produz é o pré-requisito do Lab 6, no dia seguinte.

## 8. Desafio pós-aula

Não avaliado, e desenhado para o Lab 6 começar com a cabeça no lugar.

1. **Uma ferramenta do seu projeto, escrita como schema.** Cada aluno escolhe uma ação que o sistema do projeto vai precisar executar e escreve o schema completo: nome, descrição para o modelo, parâmetros com tipo e `enum` onde couber. Junto, duas linhas dizendo qual das seis propriedades essa ferramenta corre mais risco de violar.
2. **Rodar a demo com um catálogo seu.** Quem tiver chave: acrescentar um quarto catálogo ao `demo-tool-calling.py` com o nome e a descrição que *você* escreveria, e comparar a taxa de acerto com os três do script. A pergunta dirigida é honesta: com seis perguntas e três repetições, a diferença que você mediu é maior que o ruído entre duas execuções do mesmo catálogo? Rodar o catálogo bom duas vezes responde isso — é a mesma lição de método do Lab 2.
3. **Leitura.** Schick et al., *Toolformer: Language Models Can Teach Themselves to Use Tools* (arXiv 2302.04761), seções 1 e 2. **Pergunta dirigida:** o critério que decide se uma chamada de API é mantida no conjunto de treino é a redução da perda nos tokens seguintes. Por que esse critério é mais barato *e* mais alinhado ao objetivo do que pedir a um humano para julgar se a chamada foi útil — e em que tipo de ferramenta ele falharia?

## 9. Critérios de avaliação

Esta aula **não tem entregável avaliado**. Os pesos são os da ementa e não são reinventados aqui: labs 30% (descartando a menor nota), prova 30% (Aula 17), projeto final 40% (Aulas 22, 26 e 30).

O que esta aula fixa como critério para o que vem:

- **Lab 6 (Aula 22), avaliado dentro dos 30% dos laboratórios.** O loop de tool calling escrito na mão exige os cinco passos desta aula nomeados no código: detecção da chamada, parsing, validação, despacho e retorno como mensagem `tool`. Um lab que chama uma biblioteca e pula o parsing não atende ao checkpoint.
- **Projeto final — item "funcionamento e adequação técnica" (40% da rubrica do projeto).** Para quem usar ferramentas ou MCP, adequação inclui design de ferramenta: estreita, validável, e ação irreversível com confirmação. Ferramenta genérica com parâmetro `acao` é apontada como dívida técnica na correção.
- **Declaração de uso de IA** obrigatória em toda entrega, com responsabilidade integral pelo código — qualquer entrega pode virar defesa oral.

Observável em sala, sem nota: ao fim do exercício, a dupla consegue dizer quem executa a ferramenta num sistema com tool calling e por que o resultado precisa voltar com o papel `tool`, sem consultar a anotação.
