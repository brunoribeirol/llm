# Aula 21 — Ferramentas e MCP: do texto à execução

Siga uma chamada de calculadora, valide o contrato e conecte aplicações a servidores de contexto. A seleção do modelo é roteirizada; a aritmética é calculada no navegador.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Valor da compra**: valor inicial `400`.
- **Desconto (%)**: valor inicial `15`.
- **Argumento emitido**: valor inicial `valid`.
- **Descrição no catálogo**: valor inicial `clear`.
- **Aplicações (N)**: valor inicial `3`.
- **Serviços (M)**: valor inicial `4`.

## 01. Quem faz a conta?

### Fala sugerida

Peço quinze por cento de quatrocentos. O modelo não ganhou uma calculadora dentro dos pesos. A aplicação recebeu um pedido e decidiu executar uma função.

### Na demonstração

Altere o valor e o desconto; calcule mentalmente o resultado antes de avançar.

### No quadro branco

pedido → chamada em texto → execução no host

### Pergunta à turma

Onde a multiplicação é executada?

### Resposta e transição

No host, depois que a chamada foi validada; o modelo apenas descreve a operação.

Avance para **O catálogo que o modelo lê** e relacione o resultado observado ao próximo mecanismo.

## 02. O catálogo que o modelo lê

### Fala sugerida

Leiam o catálogo como se nunca tivessem visto o código. A função é a mesma nas duas versões. Só o contrato comunica quando e como usá-la.

### Na demonstração

Troque a descrição entre clara e vaga e compare os campos publicados.

### No quadro branco

schema = nome + descrição + tipos

### Pergunta à turma

Trocar a descrição prova aumento da acurácia?

### Resposta e transição

Não. Aqui observamos a ambiguidade do contrato; medir acurácia exigiria chamadas reais e um conjunto de testes.

Avance para **Tipos e campos obrigatórios** e relacione o resultado observado ao próximo mecanismo.

## 03. Tipos e campos obrigatórios

### Fala sugerida

Agora separemos duas perguntas. O objeto obedece ao contrato? O objeto representa o pedido do usuário? O schema ajuda na primeira; a segunda exige avaliação da tarefa.

### Na demonstração

Selecione texto ou parâmetro desconhecido e veja qual regra deixa de ser satisfeita.

### No quadro branco

válido sintaticamente ≠ semanticamente correto

### Pergunta à turma

Um JSON válido pode pedir a conta errada?

### Resposta e transição

Sim. Inverter base e porcentagem ou escolher a ferramenta inadequada pode produzir um objeto perfeitamente válido.

Avance para **A mensagem de chamada** e relacione o resultado observado ao próximo mecanismo.

## 04. A mensagem de chamada

### Fala sugerida

Aponto o identificador antes de apontar os números. Se houver duas chamadas simultâneas, a posição da mensagem não basta. O identificador mantém cada resultado ligado à solicitação correta.

### Na demonstração

Mude o desconto e localize a mudança na string arguments.

### No quadro branco

call_id ↔ tool_call_id

### Pergunta à turma

Por que guardar o identificador?

### Resposta e transição

Para correlacionar chamada e retorno sem depender da ordem de conclusão.

Avance para **Validação antes do despacho** e relacione o resultado observado ao próximo mecanismo.

## 05. Validação antes do despacho

### Fala sugerida

Não executamos um texto porque ele parece convincente. Primeiro transformamos a proposta num objeto validado. Depois conferimos se aquela operação está autorizada para este usuário.

### Na demonstração

Selecione os três tipos de argumento e observe a fronteira entre aceitar e rejeitar.

### No quadro branco

parse → validar → autorizar → despachar

### Pergunta à turma

Validação substitui autorização?

### Resposta e transição

Não. Uma chamada pode ter argumentos corretos e ainda pedir uma ação que o usuário não pode realizar.

Avance para **O registro executável** e relacione o resultado observado ao próximo mecanismo.

## 06. O registro executável

### Fala sugerida

O nome aponta para uma implementação que nós controlamos. Aqui só há multiplicação de números. Não há avaliação de expressão livre nem código vindo do modelo.

### Na demonstração

Volte a números válidos e varie a porcentagem de zero a cinquenta.

### No quadro branco

desconto = valor × percentual / 100

### Pergunta à turma

É necessário usar eval para criar calculadora?

### Resposta e transição

Não. Uma função restrita com parâmetros numéricos resolve esta tarefa e reduz a superfície de execução.

Avance para **O resultado volta à conversa** e relacione o resultado observado ao próximo mecanismo.

## 07. O resultado volta à conversa

### Fala sugerida

O retorno não fica escondido num print. Ele entra na trajetória que será enviada ao modelo. Sem isso, a próxima resposta não tem acesso ao cálculo executado.

### Na demonstração

Compare o resultado numérico com a mensagem de papel tool.

### No quadro branco

assistant(call) → tool(result) → assistant(text)

### Pergunta à turma

O que acontece se o resultado não entrar no histórico?

### Resposta e transição

O modelo não recebe a evidência da execução e pode repetir a chamada ou inventar uma resposta.

Avance para **Trajetória e responsabilidade** e relacione o resultado observado ao próximo mecanismo.

## 08. Trajetória e responsabilidade

### Fala sugerida

Quero um diagnóstico mais preciso que o agente errou. Mostrem a mensagem que iniciou o desvio. Se a validação rejeitou corretamente, ela protegeu o sistema em vez de causar o erro.

### Na demonstração

Ative um argumento inválido e identifique a primeira linha que muda.

### No quadro branco

falha = camada + evidência + passo

### Pergunta à turma

Uma resposta final fluente demonstra que o ciclo funcionou?

### Resposta e transição

Não. Precisamos conferir a chamada, a validação e a observação que sustenta essa resposta.

Avance para **A conta das integrações** e relacione o resultado observado ao próximo mecanismo.

## 09. A conta das integrações

### Fala sugerida

Esta é uma conta de conectores, não uma promessa de custo total. Ainda existem autenticação, manutenção e diferenças semânticas. O protocolo reaproveita a forma da conversa entre participantes.

### Na demonstração

Aumente aplicações e serviços e compare os dois totais.

### No quadro branco

ponto a ponto: N·M; comum: N+M

### Pergunta à turma

N+M é sempre menor que N×M?

### Resposta e transição

Não. Para catálogos pequenos pode empatar ou ser maior; o benefício de padronização cresce com o ecossistema.

Avance para **Host, cliente e servidor** e relacione o resultado observado ao próximo mecanismo.

## 10. Host, cliente e servidor

### Fala sugerida

MCP não é um agente novo. É uma fronteira de integração entre programas. O host continua responsável por decidir o contexto e controlar ações.

### Na demonstração

Varie a quantidade de serviços e conte as conexões cliente-servidor.

### No quadro branco

host contém clientes; cliente ↔ servidor

### Pergunta à turma

O servidor precisa ver todas as mensagens do usuário?

### Resposta e transição

Não. Ele deve receber os dados necessários à operação, mantendo as fronteiras de contexto.

Avance para **Inicializar, descobrir, chamar** e relacione o resultado observado ao próximo mecanismo.

## 11. Inicializar, descobrir, chamar

### Fala sugerida

Leiam a sequência como um protocolo entre processos. Primeiro combinamos o que ambos entendem. Só depois pedimos uma operação anunciada pelo servidor.

### Na demonstração

Inspecione as mensagens em ordem e localize qual delas é uma notificação sem id.

### No quadro branco

initialize → initialized → tools/list → tools/call

### Pergunta à turma

Por que não começar imediatamente com tools/call?

### Resposta e transição

Porque versão, capacidades e estado da conexão precisam ser estabelecidos antes do uso normal.

Avance para **Ferramenta, recurso e prompt** e relacione o resultado observado ao próximo mecanismo.

## 12. Ferramenta, recurso e prompt

### Fala sugerida

Buscar um prazo pode ser uma ferramenta. O texto do regulamento pode ser um recurso anexado pela aplicação. Um roteiro de revisão pode ser um prompt escolhido pelo usuário.

### Na demonstração

Compare os três exemplos e diga quem inicia o uso em cada desenho.

### No quadro branco

tool: operação; resource: dado; prompt: modelo

### Pergunta à turma

Publicar um servidor MCP resolve permissões do produto?

### Resposta e transição

Não. O host ainda precisa controlar acesso, consentimento e tratamento dos dados e resultados.
