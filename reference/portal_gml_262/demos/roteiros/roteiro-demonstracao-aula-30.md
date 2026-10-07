# Aula 30 — Apresentação final: demonstrar e defender com evidência

Ensaie uma apresentação de 12 minutos, escolha um caso difícil e monte uma defesa verificável. Esta oficina não calcula nota oficial nem revela avaliações da turma.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Minutos reservados à demonstração**: valor inicial `4`.
- **Minutos reservados aos números**: valor inicial `3`.
- **Casos no conjunto apresentado**: valor inicial `20`.
- **Percentual de casos aprovados**: valor inicial `75`.
- **Caso demonstrado**: valor inicial `paraphrase`.

## 01. Doze minutos, uma tese

### Fala sugerida

A restrição de tempo obriga a escolher evidências. Não precisamos contar tudo que foi feito. Precisamos sustentar uma afirmação clara sobre o que o sistema faz e onde falha.

### Na demonstração

Ajuste tempo de demo e números e observe se o total cabe em doze minutos.

### No quadro branco

1 problema + 2 arquitetura + demo + números + 2 limites

### Pergunta à turma

Por que uma demo longa pode enfraquecer a apresentação?

### Resposta e transição

Porque pode consumir o tempo de explicar avaliação e limitações, deixando o resultado sem sustentação.

Avance para **O problema e seu usuário** e relacione o resultado observado ao próximo mecanismo.

## 02. O problema e seu usuário

### Fala sugerida

Evitem começar pela biblioteca escolhida. Comecem pela decisão que o usuário precisa tomar. Assim a turma sabe o que procurar na demonstração.

### Na demonstração

Escolha o caso demonstrado e formule o resultado esperado antes de mostrá-lo.

### No quadro branco

usuário + tarefa + condição verificável de sucesso

### Pergunta à turma

Por que gerar texto útil é um critério insuficiente?

### Resposta e transição

Porque não especifica correção, fontes, cobertura ou condição observável que permita decidir se houve sucesso.

Avance para **Arquitetura ligada às técnicas do curso** e relacione o resultado observado ao próximo mecanismo.

## 03. Arquitetura ligada às técnicas do curso

### Fala sugerida

Um diagrama não deve ter componentes decorativos. A defesa pode pedir a saída de qualquer caixa. Se a caixa não produz algo observável, precisamos esclarecer sua função.

### Na demonstração

Siga a entrada até a saída e identifique onde entram duas técnicas estudadas.

### No quadro branco

entrada → representação → recuperação → geração → avaliação

### Pergunta à turma

Como demonstrar que RAG participa de fato do sistema?

### Resposta e transição

Mostrar a consulta, os trechos recuperados e como eles entram na resposta, com identificadores verificáveis.

Avance para **Escolher um caso que discrimine** e relacione o resultado observado ao próximo mecanismo.

## 04. Escolher um caso que discrimine

### Fala sugerida

Não precisamos torcer para tudo dar certo. Precisamos saber o que o caso testa. Se ele falhar, o registro ainda pode sustentar uma análise técnica competente.

### Na demonstração

Alterne os tipos de caso e compare o que cada um testa.

### No quadro branco

caso difícil = hipótese específica posta à prova

### Pergunta à turma

Uma falha durante a demo torna toda evidência inútil?

### Resposta e transição

Não. Ela pode revelar comportamento relevante quando a equipe identifica a camada e explica o que o teste demonstra.

Avance para **Mostrar a execução e sua fonte** e relacione o resultado observado ao próximo mecanismo.

## 05. Mostrar a execução e sua fonte

### Fala sugerida

O público deve conseguir localizar de onde veio a afirmação principal. Mostro a observação antes de celebrar o resultado. Isso evita transformar uma frase convincente em prova de funcionamento.

### Na demonstração

Compare fato simples, fora de escopo e falha com diagnóstico na linha de execução.

### No quadro branco

resposta + trajetória + fonte

### Pergunta à turma

Que evidência falta numa captura contendo só a resposta?

### Resposta e transição

Falta o caminho que a produziu: dados, chamadas, fontes e decisões.

Avance para **Os números com n** e relacione o resultado observado ao próximo mecanismo.

## 06. Os números com n

### Fala sugerida

Não podemos ter meio caso aprovado. Por isso uma amostra pequena permite poucos valores de taxa. Reportem a contagem junto com a proporção e a composição do conjunto.

### Na demonstração

Mude o tamanho do conjunto e compare percentual desejado e contagem realmente possível.

### No quadro branco

taxa observada = aprovados inteiros / n

### Pergunta à turma

Em cinco casos, setenta e cinco por cento é uma taxa exata possível?

### Resposta e transição

Não. As taxas variam de vinte em vinte pontos percentuais; arredondar casos muda o percentual observado.

Avance para **Declarar juiz e calibração** e relacione o resultado observado ao próximo mecanismo.

## 07. Declarar juiz e calibração

### Fala sugerida

O número do juiz não vem sozinho. Quero saber como ele chegou à decisão. Se não houve calibração, a equipe deve declarar a ausência e limitar a conclusão.

### Na demonstração

Confira o cartão do que apresentar e identifique qual campo falta no seu relatório.

### No quadro branco

juiz + rubrica + amostra humana + acordo + limites

### Pergunta à turma

É melhor omitir que o juiz não foi calibrado?

### Resposta e transição

Não. Declarar a limitação permite interpretar corretamente a força da evidência.

Avance para **Uma limitação que muda uma decisão** e relacione o resultado observado ao próximo mecanismo.

## 08. Uma limitação que muda uma decisão

### Fala sugerida

Escolham um limite sustentado pelo conjunto ou pela arquitetura. Expliquem o que o usuário deve esperar nessa condição. Depois proponham uma verificação capaz de mostrar melhora.

### Na demonstração

Use o caso selecionado para formular uma limitação e um teste de correção.

### No quadro branco

condição → falha → consequência → próximo teste

### Pergunta à turma

Qual limitação é mais útil que pode alucinar?

### Resposta e transição

Por exemplo: paráfrases sem termos compartilhados recuperam fonte errada; medir recall por categoria após alterar a recuperação.

Avance para **Defender por composição** e relacione o resultado observado ao próximo mecanismo.

## 09. Defender por composição

### Fala sugerida

Se a explicação terminar no nome da biblioteca, ainda falta o mecanismo. Podemos começar pela entrada de uma caixa e derivar sua saída. Depois ligamos isso à falha ou ao ganho observado.

### Na demonstração

Escolha uma pergunta do cartão e responda usando a trajetória exibida.

### No quadro branco

mecanismo → consequência → evidência

### Pergunta à turma

Como responder o que mudaria se aumentássemos k?

### Resposta e transição

Explicar efeitos possíveis em recall, precisão, tamanho do contexto, custo e resposta, e indicar os casos usados para medir.

Avance para **Fechar com algo reproduzível** e relacione o resultado observado ao próximo mecanismo.

## 10. Fechar com algo reproduzível

### Fala sugerida

Uma pessoa que não estava na sala deve conseguir conferir a conclusão. A apresentação aponta o caminho para esses artefatos. Encerramos com o que foi medido e o que ainda precisa de teste.

### Na demonstração

Volte ao cronograma, ajuste os tempos e associe cada bloco a um arquivo ou resultado do projeto.

### No quadro branco

afirmação → evidência → artefato reexecutável

### Pergunta à turma

Qual é a diferença entre uma promessa e a conclusão técnica da apresentação?

### Resposta e transição

A conclusão identifica evidência, condições e limites verificáveis; a promessa apenas antecipa um resultado.
