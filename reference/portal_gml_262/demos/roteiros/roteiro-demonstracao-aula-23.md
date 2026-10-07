# Aula 23 — Agentes: observar, agir e saber parar

Inspecione um agente roteirizado que busca um prazo e calcula uma data relativa. Explore memória, verificação, custo e critérios de parada.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Orçamento de passos**: valor inicial `5`.
- **Tokens novos por volta**: valor inicial `250`.
- **Comportamento**: valor inicial `normal`.
- **Anexar observações ao histórico**: valor inicial `True`.
- **Exigir evidência antes de concluir**: valor inicial `True`.

## 01. As cinco peças

### Fala sugerida

Dar um nome ao agente não explica sua arquitetura. Quero localizar cada peça em uma responsabilidade concreta. Se não existe condição de parada, o desenho ainda está incompleto.

### Na demonstração

Selecione o fluxo normal e identifique as cinco peças no desenho.

### No quadro branco

agente = modelo + ferramentas + loop + objetivo + parada

### Pergunta à turma

Uma chamada isolada de modelo já constitui o loop desta aula?

### Resposta e transição

Não. O que estudamos é um sistema que decide ações sucessivas usando observações e um critério explícito de término.

Avance para **O objetivo exige duas fontes de trabalho** e relacione o resultado observado ao próximo mecanismo.

## 02. O objetivo exige duas fontes de trabalho

### Fala sugerida

Uma ferramenta não resolve o objetivo inteiro. A busca devolve um fato e a calculadora aplica uma transformação. A resposta precisa preservar a origem do fato utilizado.

### Na demonstração

Observe os dois subproblemas e diga qual ferramenta fornece cada evidência.

### No quadro branco

buscar prazo → somar dias → citar artigo

### Pergunta à turma

Uma calculadora pode confirmar que o prazo recuperado é o correto?

### Resposta e transição

Não. Ela verifica a transformação numérica, mas depende da informação fornecida pela busca.

Avance para **Observar, planejar, agir, refletir** e relacione o resultado observado ao próximo mecanismo.

## 03. Observar, planejar, agir, refletir

### Fala sugerida

O ciclo só aprende algo quando a observação retorna. Aqui o erro de argumento vira informação para corrigir a chamada. Sem esse retorno, repetição não é adaptação.

### Na demonstração

Mude para correção de argumento e localize onde a observação de erro altera o plano.

### No quadro branco

estado → decisão → ação → observação → novo estado

### Pergunta à turma

Qual evento diferencia o segundo plano do primeiro?

### Resposta e transição

A nova observação que descreve o erro ou o resultado da ferramenta anterior.

Avance para **O plano antes e depois da ação** e relacione o resultado observado ao próximo mecanismo.

## 04. O plano antes e depois da ação

### Fala sugerida

Podemos antecipar a sequência geral. Isso não significa prever todas as falhas. Um plano útil mantém a ordem das dependências e permite revisar a ação quando chega um erro.

### Na demonstração

Compare os cenários normal e correção de argumento e observe o passo adicional.

### No quadro branco

dependência: prazo conhecido antes de somar

### Pergunta à turma

Por que paralelizar busca e cálculo seria incorreto neste caso?

### Resposta e transição

Porque o cálculo depende do prazo que a busca ainda precisa fornecer.

Avance para **Ação não é observação** e relacione o resultado observado ao próximo mecanismo.

## 05. Ação não é observação

### Fala sugerida

Olhem quem escreveu cada linha. Uma frase dizendo calculei não demonstra execução. O host precisa anexar a observação obtida de fato da função.

### Na demonstração

Selecione parada precoce e compare a ausência de ferramenta com o caminho normal.

### No quadro branco

proposta do modelo ≠ resultado da ferramenta

### Pergunta à turma

Quem está autorizado a preencher a observação?

### Resposta e transição

O host com o retorno da ferramenta, não o texto proposto pelo modelo.

Avance para **Memória de curto prazo** e relacione o resultado observado ao próximo mecanismo.

## 06. Memória de curto prazo

### Fala sugerida

A ferramenta pode ter funcionado perfeitamente e ainda assim o sistema falhar. Se o retorno não entra no próximo contexto, o modelo não o vê. Esse defeito está na gestão de estado do host.

### Na demonstração

Desmarque anexar observações e acompanhe a repetição.

### No quadro branco

memória curta = histórico visível nesta execução

### Pergunta à turma

Por que aumentar o limite não corrige a memória ausente?

### Resposta e transição

Porque as novas voltas continuam sem receber a informação necessária; apenas repetem o mesmo defeito.

Avance para **Memória que sobrevive à sessão** e relacione o resultado observado ao próximo mecanismo.

## 07. Memória que sobrevive à sessão

### Fala sugerida

Salvar texto em um banco não o transforma em verdade. O registro precisa dizer de onde veio e quando deixa de valer. Uma nova sessão deve recuperar e conferir essa informação.

### Na demonstração

Compare o histórico de sessão com o registro persistente ilustrado.

### No quadro branco

memória longa = dado + fonte + versão + validade

### Pergunta à turma

Persistir toda a conversa é suficiente para uma boa memória?

### Resposta e transição

Não. É preciso selecionar, recuperar, atualizar e controlar acesso aos registros relevantes.

Avance para **Verificação e autocorreção** e relacione o resultado observado ao próximo mecanismo.

## 08. Verificação e autocorreção

### Fala sugerida

Refletir é útil quando há algo externo a conferir. O erro de tipo é um sinal objetivo. Pedir ao modelo que pense de novo sem evidência não garante melhora.

### Na demonstração

Selecione correção de argumento e acompanhe rejeição, ajuste e execução.

### No quadro branco

erro detectável → nova ação → nova verificação

### Pergunta à turma

Qual verificador é barato nesta tarefa?

### Resposta e transição

Validar os argumentos, conferir a soma e exigir a referência ao artigo recuperado.

Avance para **Quando um pipeline basta** e relacione o resultado observado ao próximo mecanismo.

## 09. Quando um pipeline basta

### Fala sugerida

Não vamos premiar complexidade por si só. Se a ordem sempre é buscar e somar, um pipeline pode resolver. O loop faz sentido quando precisamos escolher e revisar ações conforme o ambiente responde.

### Na demonstração

Compare os caminhos normal e correção; identifique quais decisões poderiam ser código fixo.

### No quadro branco

caminho fixo? verificador disponível?

### Pergunta à turma

Uma tarefa com três ferramentas exige três agentes?

### Resposta e transição

Não. Quantidade de ferramentas não determina quantidade de agentes nem necessidade de autonomia.

Avance para **O custo acumulado da trajetória** e relacione o resultado observado ao próximo mecanismo.

## 10. O custo acumulado da trajetória

### Fala sugerida

Contem quantas vezes a primeira observação reaparece. Ela custa em todas as chamadas seguintes. O gráfico separa comprimento do próximo prompt e total enviado até ali.

### Na demonstração

Aumente passos e tokens por volta; compare custo marginal e acumulado.

### No quadro branco

T(n) = n·600 + d·n(n−1)/2

### Pergunta à turma

Por que número de chamadas não basta para estimar tokens?

### Resposta e transição

Porque chamadas posteriores podem carregar contextos maiores que as primeiras.

Avance para **Dois defeitos de parada** e relacione o resultado observado ao próximo mecanismo.

## 11. Dois defeitos de parada

### Fala sugerida

Um loop que terminou não necessariamente resolveu a tarefa. O motivo da parada faz parte do resultado. Exigir evidência reduz um tipo de erro, enquanto o teto evita execução interminável.

### Na demonstração

Alterne parada precoce e repetição; marque e desmarque exigir evidência.

### No quadro branco

terminar ≠ concluir com sucesso

### Pergunta à turma

O teto de passos prova que a resposta está correta?

### Resposta e transição

Não. Ele limita recursos; a correção depende de evidência e verificadores apropriados.

Avance para **Trajetória de um coding agent** e relacione o resultado observado ao próximo mecanismo.

## 12. Trajetória de um coding agent

### Fala sugerida

Um teste que falhou pode ser mais informativo que outra reflexão livre. Ele localiza uma hipótese que precisa mudar. Mesmo testes passando, ainda precisamos conferir se cobrem o comportamento solicitado.

### Na demonstração

Compare o ciclo de busca com localizar, editar e testar no diagrama.

### No quadro branco

hipótese → alteração → teste → leitura da falha

### Pergunta à turma

Passar uma suíte garante que toda mudança está correta?

### Resposta e transição

Não. A suíte fornece evidência dentro de sua cobertura, junto com revisão do diff e dos requisitos.
