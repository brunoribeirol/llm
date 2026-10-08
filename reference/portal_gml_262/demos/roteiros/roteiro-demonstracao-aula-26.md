# Aula 26 — Segurança de agentes: a trajetória que muda de rumo

Compare duas execuções de uma injeção inócua em documentos fictícios. A mitigação é um comportamento roteirizado, nunca uma garantia de proteção de um LLM.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Incluir documento com instrução injetada**: valor inicial `True`.
- **Separar conteúdo recuperado como dado**: valor inicial `False`.
- **Permitir apenas leitura**: valor inicial `True`.
- **Origem do conteúdo**: valor inicial `document`.
- **Casos do lote sintético**: valor inicial `12`.
- **Casos com falha de interpretação**: valor inicial `2`.

## 01. A tarefa legítima e a entrada externa

### Fala sugerida

Começamos pelo comportamento esperado. Sem referência, não saberíamos reconhecer o desvio. O que vamos alterar é uma fonte recuperada, mantendo a mesma pergunta legítima.

### Na demonstração

Desative o documento injetado e observe a execução de referência.

### No quadro branco

objetivo autorizado: responder com fonte

### Pergunta à turma

Qual é a tarefa que deve permanecer estável?

### Resposta e transição

Responder o prazo com a fonte correspondente, sem trocar o objetivo por instruções do documento.

Avance para **Três canais, a mesma fronteira** e relacione o resultado observado ao próximo mecanismo.

## 02. Três canais, a mesma fronteira

### Fala sugerida

Não é preciso falar diretamente com o agente para influenciar seu contexto. Um texto recuperado já entra na execução. Isso torna a proveniência dos dados parte do desenho do sistema.

### Na demonstração

Alterne a origem do conteúdo e localize o ponto em que ele entra no contexto.

### No quadro branco

canal externo → conteúdo não confiável → contexto

### Pergunta à turma

Um retorno de ferramenta é automaticamente uma instrução autorizada?

### Resposta e transição

Não. A ferramenta pode transportar texto de terceiros; sucesso da chamada não legitima comandos contidos nele.

Avance para **O documento de demonstração** e relacione o resultado observado ao próximo mecanismo.

## 03. O documento de demonstração

### Fala sugerida

O formato do documento é parecido com os demais. O que muda é a intenção de uma linha dentro dele. A linha pede uma mudança de tarefa, e essa é a fronteira que queremos tornar visível.

### Na demonstração

Ative o documento injetado e compare seu corpo com o artigo legítimo.

### No quadro branco

dado citado ≠ comando para o host

### Pergunta à turma

Por que metadados plausíveis não bastam para confiar no conteúdo?

### Resposta e transição

Porque o corpo pode conter instruções incompatíveis com o objetivo, independentemente da aparência do documento.

Avance para **Recuperar não é obedecer** e relacione o resultado observado ao próximo mecanismo.

## 04. Recuperar não é obedecer

### Fala sugerida

Esta comparação é importante para localizar a mitigação. Ela não consertou o ranking. Ela mudou o tratamento do que chegou depois da busca.

### Na demonstração

Marque e desmarque separar conteúdo e confira que os documentos recuperados continuam iguais.

### No quadro branco

mesma recuperação; interpretação diferente

### Pergunta à turma

A mitigação desta demo remove o documento do acervo?

### Resposta e transição

Não. O documento continua recuperável; a mudança ilustrada ocorre na interpretação do contexto.

Avance para **O primeiro passo de divergência** e relacione o resultado observado ao próximo mecanismo.

## 05. O primeiro passo de divergência

### Fala sugerida

A resposta final mostra o sintoma. A trajetória mostra onde o sintoma nasceu. É essa localização que permite corrigir a camada adequada.

### Na demonstração

Compare as duas trajetórias e aponte a primeira linha diferente.

### No quadro branco

busca igual → interpretação oposta → resposta diferente

### Pergunta à turma

Qual evidência mostra que a falha não está no parsing da chamada?

### Resposta e transição

A mesma busca foi chamada corretamente em ambos os cenários; a divergência aparece após o retorno.

Avance para **Delimitação é uma mitigação** e relacione o resultado observado ao próximo mecanismo.

## 06. Delimitação é uma mitigação

### Fala sugerida

O botão sempre funciona aqui porque escrevemos o roteiro assim. Essa propriedade pertence ao simulador. Num modelo real, a eficácia precisa ser medida com casos adversariais e contexto de uso.

### Na demonstração

Alterne separar conteúdo e leia a observação sobre o alcance do experimento.

### No quadro branco

delimitar reduz ambiguidade; não prova imunidade

### Pergunta à turma

Por que cem por cento de sucesso nesta página não seria uma taxa de segurança?

### Resposta e transição

Porque o resultado foi programado; não é amostra de comportamento de um modelo sob ataque.

Avance para **Permissões limitam consequências** e relacione o resultado observado ao próximo mecanismo.

## 07. Permissões limitam consequências

### Fala sugerida

Mesmo que a interpretação falhe, o host não precisa oferecer todo poder disponível. A lista permitida restringe consequências. Esse controle deve ser aplicado por código, não só descrito no prompt.

### Na demonstração

Alterne permitir apenas leitura e observe quais operações o host aceitaria.

### No quadro branco

proposta de ação → autorização → execução

### Pergunta à turma

O prompt pode conceder uma permissão que o host negou?

### Resposta e transição

Não deveria. A autorização do host é a fronteira executável que decide quais ações podem ocorrer.

Avance para **Reversibilidade e revisão humana** e relacione o resultado observado ao próximo mecanismo.

## 08. Reversibilidade e revisão humana

### Fala sugerida

Uma pergunta vaga de autorização não ajuda quem decide. Precisamos mostrar o que será feito e sobre quais dados. O nível de controle depende da consequência concreta da ferramenta.

### Na demonstração

Compare as três operações e seu grau de reversibilidade no quadro.

### No quadro branco

ação + efeito + reversibilidade → política

### Pergunta à turma

Toda ferramenta precisa da mesma política de autorização?

### Resposta e transição

Não. Leitura, alteração reversível e ação externa irreversível exigem políticas proporcionais às consequências.

Avance para **Cinco lugares onde um agente falha** e relacione o resultado observado ao próximo mecanismo.

## 09. Cinco lugares onde um agente falha

### Fala sugerida

A taxonomia evita tentar resolver tudo com prompt. Um nome de ferramenta errado é diferente de ignorar uma exceção no artigo certo. Cada defeito precisa de evidência na trajetória.

### Na demonstração

Altere os casos com falha de interpretação e compare sua participação no lote.

### No quadro branco

percepção → ferramenta → argumentos → observação → parada

### Pergunta à turma

Responder certo sem consultar a fonte pode esconder uma falha?

### Resposta e transição

Sim. Pode ser uma parada sem evidência que acertou por coincidência e não atende ao contrato do sistema.

Avance para **Métricas com denominadores** e relacione o resultado observado ao próximo mecanismo.

## 10. Métricas com denominadores

### Fala sugerida

O denominador muda a interpretação do mesmo número de erros. Também precisamos saber de onde vieram os casos. Um lote artificial é útil para aprender a conta, não para prometer qualidade real.

### Na demonstração

Aumente o tamanho do lote sem mudar as falhas e observe a taxa.

### No quadro branco

taxa = falhas observadas / casos avaliados

### Pergunta à turma

Duas falhas em quatro casos equivalem a duas em vinte?

### Resposta e transição

Não. As taxas e a incerteza da amostra são diferentes.

Avance para **Auditar o que realmente aconteceu** e relacione o resultado observado ao próximo mecanismo.

## 11. Auditar o que realmente aconteceu

### Fala sugerida

O log deve responder quem forneceu o conteúdo e quem autorizou a ação. Não basta guardar a última frase. Ao mesmo tempo, registrar tudo sem seleção pode reter dados que não precisávamos guardar.

### Na demonstração

Escolha um canal e compare os campos de auditoria do cenário atual.

### No quadro branco

evento = origem + ação + decisão + observação

### Pergunta à turma

Qual campo falta quando só salvamos resposta e horário?

### Resposta e transição

Faltam as transições: origem, chamadas, argumentos, resultados, decisões e motivo da parada.

Avance para **Checkpoint do projeto** e relacione o resultado observado ao próximo mecanismo.

## 12. Checkpoint do projeto

### Fala sugerida

Uma interface pronta não compensa um caminho crítico invisível. Quero uma execução e o lugar onde ela pode falhar. Nomear o problema agora permite corrigir antes da apresentação final.

### Na demonstração

Monte um diagnóstico: canal de entrada, primeira divergência, barreira e evidência.

### No quadro branco

pipeline executado + risco localizado + teste planejado

### Pergunta à turma

O que este simulador permite concluir sobre o seu projeto?

### Resposta e transição

Ele oferece um método de inspeção; a segurança e a qualidade do projeto precisam ser testadas na sua implementação.
