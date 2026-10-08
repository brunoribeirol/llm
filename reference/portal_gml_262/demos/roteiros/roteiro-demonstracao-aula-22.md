# Aula 22 — Lab 6: construindo o host de ferramentas

Monte schema, parsing, despacho, histórico e cliente MCP em uma execução explicada. Nenhum servidor externo é iniciado por esta simulação.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Cenário da chamada**: valor inicial `normal`.
- **Teto de passos**: valor inicial `4`.
- **Tokens por observação**: valor inicial `400`.
- **Orçamento de tokens**: valor inicial `5000`.
- **Transporte ilustrado**: valor inicial `stdio`.

## 01. Os quatro checkpoints

### Fala sugerida

Antes de escrever o while, definimos o que será verificável. Não basta receber uma resposta bonita. Precisamos saber qual mensagem e qual invariável cada checkpoint produz.

### Na demonstração

Selecione o cenário normal e percorra a lista de saídas esperadas.

### No quadro branco

schema → loop → cliente → servidor

### Pergunta à turma

Qual artefato permite reproduzir um defeito?

### Resposta e transição

A trajetória completa com entrada, chamada, argumentos, observação e motivo da parada.

Avance para **Schema e registro se encontram** e relacione o resultado observado ao próximo mecanismo.

## 02. Schema e registro se encontram

### Fala sugerida

O menu e a cozinha precisam concordar. A descrição não cria automaticamente uma função. Este teste simples captura um erro que muitas vezes seria atribuído ao modelo.

### Na demonstração

Selecione ferramenta inexistente e procure o nome sem implementação.

### No quadro branco

nomes(schema) = nomes(registro autorizado)

### Pergunta à turma

Uma ferramenta no registro mas fora do catálogo será escolhida normalmente?

### Resposta e transição

Não. O modelo não conhece esse nome pelo catálogo; código executável e interface precisam ser mantidos juntos.

Avance para **Parsear sem derrubar o processo** e relacione o resultado observado ao próximo mecanismo.

## 03. Parsear sem derrubar o processo

### Fala sugerida

Esta etapa ainda não calcula nada. Ela só pergunta se o texto representa um objeto. Se falhar, registramos o erro e não seguimos como se a chamada tivesse sido executada.

### Na demonstração

Escolha JSON truncado e depois conta correta; compare texto bruto e objeto.

### No quadro branco

texto → JSON.parse → objeto ou erro

### Pergunta à turma

Por que parsing e validação são etapas separadas?

### Resposta e transição

Porque um texto pode nem representar JSON; um objeto JSON válido pode violar o schema.

Avance para **Duas fronteiras de validação** e relacione o resultado observado ao próximo mecanismo.

## 04. Duas fronteiras de validação

### Fala sugerida

A implementação não deve pressupor que todo chamador é cuidadoso. Isso permite reutilizar a ferramenta em outro host. Cada fronteira protege uma responsabilidade diferente.

### Na demonstração

Compare o fluxo normal com a ferramenta inexistente e identifique onde a chamada é barrada.

### No quadro branco

host: contrato; ferramenta: domínio

### Pergunta à turma

Validar somente na interface gráfica é suficiente?

### Resposta e transição

Não. O despacho e a função precisam conferir as condições, pois outros clientes podem contornar a interface.

Avance para **Uma volta desenrolada** e relacione o resultado observado ao próximo mecanismo.

## 05. Uma volta desenrolada

### Fala sugerida

Primeiro faço uma volta sem laço. Assim ninguém precisa adivinhar onde a observação entrou. Depois colocamos exatamente esse mecanismo dentro da repetição.

### Na demonstração

No cenário normal, siga a mudança da lista de mensagens da primeira à última linha.

### No quadro branco

system, user, assistant(call), tool(result)

### Pergunta à turma

Qual mensagem informa ao modelo que a ferramenta terminou?

### Resposta e transição

A mensagem de resultado associada ao identificador da chamada.

Avance para **O loop com erro e insistência** e relacione o resultado observado ao próximo mecanismo.

## 06. O loop com erro e insistência

### Fala sugerida

Este modelo teimoso é um teste de infraestrutura. Ele não tenta imitar inteligência. Ele verifica se nosso código termina quando o comportamento externo nunca coopera.

### Na demonstração

Selecione modelo insiste e reduza o teto para três passos.

### No quadro branco

for passo < teto: chamar → validar → executar → registrar

### Pergunta à turma

Por que testar com um modelo que nunca para?

### Resposta e transição

Para comprovar que o limite é aplicado pelo host e não depende da boa vontade do modelo.

Avance para **O prompt cresce a cada volta** e relacione o resultado observado ao próximo mecanismo.

## 07. O prompt cresce a cada volta

### Fala sugerida

A observação parece barata quando aparece uma vez. Mas ela volta no próximo prompt e nos seguintes. Por isso respostas de ferramenta extensas afetam o restante da trajetória.

### Na demonstração

Aumente tokens por observação e compare as alturas das barras por passo.

### No quadro branco

P(k) = p₀ + (k−1)d

### Pergunta à turma

Dobrar a observação dobra todo o custo?

### Resposta e transição

Não necessariamente. O prefixo fixo permanece; a parte acumulada associada às observações cresce.

Avance para **Derivar o teto de passos** e relacione o resultado observado ao próximo mecanismo.

## 08. Derivar o teto de passos

### Fala sugerida

Agora o limite de passos deixa de ser um palpite. Escrevemos a restrição e testamos inteiros. A estimativa só é honesta se declararmos o que não foi contabilizado.

### Na demonstração

Reduza o orçamento e compare o teto escolhido com o teto permitido pela conta.

### No quadro branco

T(n) ≤ B → maior n inteiro admissível

### Pergunta à turma

Um teto que cabe em tokens garante que cabe em tempo?

### Resposta e transição

Não. Ferramentas lentas e latência do modelo exigem limites de tempo separados.

Avance para **MCP: abrir a conversa** e relacione o resultado observado ao próximo mecanismo.

## 09. MCP: abrir a conversa

### Fala sugerida

O transporte muda o caminho dos bytes. Não muda a necessidade de negociar a conversa. No desenho local, o cliente cria um subprocesso; no remoto, conecta-se a um endpoint.

### Na demonstração

Alterne stdio e HTTP e observe o que muda no transporte e o que permanece no protocolo.

### No quadro branco

initialize → resposta → notifications/initialized

### Pergunta à turma

MCP precisa sempre abrir um subprocesso?

### Resposta e transição

Não. Isso caracteriza o transporte stdio; servidores remotos podem usar Streamable HTTP.

Avance para **Descoberta e chamada** e relacione o resultado observado ao próximo mecanismo.

## 10. Descoberta e chamada

### Fala sugerida

O nome da função não está mais duplicado à mão em todos os hosts. Mas alguém escreveu aquela descrição. Reaproveitamento de interface não elimina a necessidade de revisar capacidades e permissões.

### Na demonstração

Localize inputSchema e compare com o contrato local do começo da aula.

### No quadro branco

tools/list → catálogo; tools/call → resultado

### Pergunta à turma

A descoberta autoriza automaticamente todas as ferramentas?

### Resposta e transição

Não. Descobrir uma capacidade e conceder permissão para usá-la são decisões diferentes.

Avance para **Publicar busca e recurso** e relacione o resultado observado ao próximo mecanismo.

## 11. Publicar busca e recurso

### Fala sugerida

O recurso é um endereço para um dado. A ferramenta recebe argumentos e realiza uma busca. Um print de depuração no canal errado pode impedir que o cliente entenda ambos.

### Na demonstração

Alterne o transporte e leia a separação entre canal do protocolo e diagnóstico.

### No quadro branco

stdout: protocolo; stderr: diagnóstico em stdio

### Pergunta à turma

Por que um print inocente pode quebrar o servidor stdio?

### Resposta e transição

Porque o cliente espera mensagens do protocolo na saída padrão; texto avulso rompe esse contrato.

Avance para **Entrega reproduzível** e relacione o resultado observado ao próximo mecanismo.

## 12. Entrega reproduzível

### Fala sugerida

Não entreguem apenas a captura da resposta certa. Entreguem uma execução que outra pessoa consiga examinar. A falha controlada costuma demonstrar melhor a robustez do host que o caminho feliz.

### Na demonstração

Escolha um cenário com falha e descreva qual checkpoint e qual evidência o detectam.

### No quadro branco

entrada → execução → observação → diagnóstico

### Pergunta à turma

O que distingue demo funcionando de artefato reproduzível?

### Resposta e transição

Entradas, configuração, histórico, resultados e verificações explícitas permitem repetir e localizar diferenças.
