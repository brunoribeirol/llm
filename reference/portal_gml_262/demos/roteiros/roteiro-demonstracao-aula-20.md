# Aula 20 — Laboratório RAG: pipeline completo e avaliação

Execute corpus, busca, fusão, reordenação e resposta extrativa em um acervo local pequeno.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Consulta de teste**: valor inicial `prazo`.
- **Palavras por chunk**: valor inicial `10`.
- **Sobreposição**: valor inicial `2`.
- **Candidatos recuperados**: valor inicial `4`.
- **Fontes no contexto**: valor inicial `2`.
- **Constante RRF**: valor inicial `20`.

## 01. Definir o contrato de ponta a ponta

### Fala sugerida

O modo local é explícito. Nenhum número aqui vem de um serviço de geração. Vamos produzir evidência inspecionável em cada estágio.

### Na demonstração

Confira a configuração registrada e escolha uma consulta.

### No quadro branco

Ingestão → índice → busca → contexto → saída → avaliação

### Pergunta à turma

Qual é o entregável central do laboratório real?

### Resposta e transição

Um pipeline reproduzível acompanhado de métricas e interpretação de seus limites.

Avance para **CP1: fragmentar com metadados** e relacione o resultado observado ao próximo mecanismo.

## 02. CP1: fragmentar com metadados

### Fala sugerida

O texto de origem permanece acessível. Uma fronteira artificial pode separar uma condição. No projeto, regras estruturais por seção podem ser melhores que esta segmentação simples.

### Na demonstração

Mude tamanho e sobreposição e examine os fragmentos.

### No quadro branco

chunk = texto + fonte + intervalo

### Pergunta à turma

Por que manter intervalo de origem?

### Resposta e transição

Para auditar cortes, reconstruir contexto e relacionar o fragmento ao documento.

Avance para **CP1: verificar integridade** e relacione o resultado observado ao próximo mecanismo.

## 03. CP1: verificar integridade

### Fala sugerida

Este é um contrato que pode virar teste automatizado. Não basta o programa terminar sem exceção. Precisamos saber se preservou o significado e os metadados.

### Na demonstração

Aproxime overlap do tamanho e confira a regra de limitação.

### No quadro branco

0 ≤ overlap < tamanho; início seguinte > início atual

### Pergunta à turma

O que acontece se overlap igualar tamanho sem proteção?

### Resposta e transição

O segmentador pode deixar de avançar e entrar em repetição infinita.

Avance para **CP2: normalizar e comparar** e relacione o resultado observado ao próximo mecanismo.

## 04. CP2: normalizar e comparar

### Fala sugerida

Esta separação é uma limitação intencional do simulador. No notebook real cada chunk recebe seu embedding. Aqui conseguimos conferir cada conta sem carregar um modelo.

### Na demonstração

Troque a consulta e compare vetores e normas.

### No quadro branco

‖v̂‖=1 ⇒ v̂q·v̂d = cosseno

### Pergunta à turma

Os vetores mostrados foram produzidos pelos chunks?

### Resposta e transição

Não; são vetores manuais de documentos, explicitamente usados para a demonstração geométrica.

Avance para **CP2: inspecionar o ranking denso** e relacione o resultado observado ao próximo mecanismo.

## 05. CP2: inspecionar o ranking denso

### Fala sugerida

Um resultado geometricamente próximo pode não conter o identificador. Este é o motivo de trazer uma segunda família de busca. Vamos guardar a posição antes de mudar o pipeline.

### Na demonstração

Selecione código e compare ranking com o documento correto.

### No quadro branco

Ranking não substitui inspeção da evidência

### Pergunta à turma

Por que manter uma consulta de controle?

### Resposta e transição

Para detectar regressões conhecidas e verificar o funcionamento mínimo do índice.

Avance para **CP3: acrescentar a busca lexical** e relacione o resultado observado ao próximo mecanismo.

## 06. CP3: acrescentar a busca lexical

### Fala sugerida

Os escores lexicais são calculados com os textos visíveis. Os vetores densos são manuais. Estamos comparando mecanismos, não anunciando um benchmark de modelos.

### Na demonstração

Troque a consulta e compare as duas listas.

### No quadro branco

Lexical: ocorrência; denso: proximidade

### Pergunta à turma

Um ranking lexical pode superar o denso?

### Resposta e transição

Sim, especialmente em identificadores e correspondências exatas.

Avance para **CP3: fundir pelas posições** e relacione o resultado observado ao próximo mecanismo.

## 07. CP3: fundir pelas posições

### Fala sugerida

Não digitamos uma terceira lista manualmente. O ranking combinado sai da fórmula. Confiram a soma antes de confiar no resultado.

### Na demonstração

Mude a constante e confira o total de um documento.

### No quadro branco

score = 1/(c+r_lex) + 1/(c+r_denso)

### Pergunta à turma

A fusão consulta os rótulos de relevância?

### Resposta e transição

Não; os rótulos só entram na avaliação.

Avance para **CP4: reordenar um conjunto fechado** e relacione o resultado observado ao próximo mecanismo.

## 08. CP4: reordenar um conjunto fechado

### Fala sugerida

A regra é simples para poder ser auditada. Um cross-encoder real substituiria essa função no notebook. A limitação de cobertura continuaria igual.

### Na demonstração

Reduza candidatos e compare posições antes e depois.

### No quadro branco

Conjunto antes = conjunto depois; ordem pode mudar

### Pergunta à turma

Qual propriedade deve continuar verdadeira após reordenar?

### Resposta e transição

Os identificadores dos candidatos permanecem os mesmos, sem criação ou perda de itens.

Avance para **CP4: contabilizar o trabalho** e relacione o resultado observado ao próximo mecanismo.

## 09. CP4: contabilizar o trabalho

### Fala sugerida

A latência exibida usa uma hipótese didática por par. Não é medição de rede ou GPU. Mesmo assim a conta ajuda a escolher o orçamento de reranking.

### Na demonstração

Aumente candidatos mantendo o número final de fontes.

### No quadro branco

Pares avaliados = K_candidatos

### Pergunta à turma

Reduzir fontes finais reduz automaticamente custo do reranker?

### Resposta e transição

Não; se o conjunto candidato permanece igual, a quantidade de pares avaliados também.

Avance para **CP5: responder e citar a evidência** e relacione o resultado observado ao próximo mecanismo.

## 10. CP5: responder e citar a evidência

### Fala sugerida

Não há texto produzido por um LLM nesta etapa. A extração torna o vínculo com a fonte verificável. Um gerador real exigiria medir também fidelidade e abstenção.

### Na demonstração

Troque consulta e k e leia as fontes usadas.

### No quadro branco

Resposta = trechos selecionados + IDs de origem

### Pergunta à turma

Uma citação existente basta para uma resposta correta?

### Resposta e transição

Não; deve apoiar o conteúdo e responder à pergunta.

Avance para **CP6: comparar sobre consultas fixas** e relacione o resultado observado ao próximo mecanismo.

## 11. CP6: comparar sobre consultas fixas

### Fala sugerida

O denominador aqui é três, bem menor que o laboratório completo. Não escondemos essa limitação. A tabela é calculada a partir de rankings e rótulos explícitos.

### Na demonstração

Varie k e candidatos e compare médias e resultados por consulta.

### No quadro branco

Métrica média = soma por consulta / número de consultas

### Pergunta à turma

Podemos usar três consultas para declarar uma técnica superior?

### Resposta e transição

Não de modo geral; faltam volume, diversidade e análise de incerteza.

Avance para **Distinguir invariância de ganho observado** e relacione o resultado observado ao próximo mecanismo.

## 12. Distinguir invariância de ganho observado

### Fala sugerida

Este é o principal fechamento do laboratório. Uma propriedade estrutural não precisa de sorte para valer. Uma melhoria de qualidade exige dados e pode deixar de ocorrer.

### Na demonstração

Compare recall dos candidatos antes/depois e recall no corte final.

### No quadro branco

Garantido: mesma cobertura candidata; empírico: melhor topo

### Pergunta à turma

Qual afirmação pode ser garantida sem benchmark?

### Resposta e transição

Que permutar o mesmo conjunto não muda a quantidade de documentos relevantes presentes nele.

Avance para **Registrar limites para a próxima etapa** e relacione o resultado observado ao próximo mecanismo.

## 13. Registrar limites para a próxima etapa

### Fala sugerida

Uma captura de tela bonita não é o experimento inteiro. Guardem as listas recuperadas e as métricas. Isso permite investigar depois se a falha veio da busca ou da resposta.

### Na demonstração

Confira o manifesto e formule uma melhoria testável.

### No quadro branco

Resultado + proveniência + falhas + próximo teste

### Pergunta à turma

O que permitirá reproduzir esta demonstração?

### Resposta e transição

Acervo e rótulos fixos, configuração dos controles, funções de ranking e registro do modo didático local.
