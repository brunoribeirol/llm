# Aula 18 — RAG: da fonte ao contexto recuperado

Construa uma memória externa com chunks, vetores, ranking e citações auditáveis.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Tamanho de chunk (palavras)**: valor inicial `10`.
- **Sobreposição (limitada ao chunk−1)**: valor inicial `2`.
- **Documentos recuperados**: valor inicial `3`.
- **Consulta: eixo prazo**: valor inicial `0.9`.
- **Consulta: eixo matrícula**: valor inicial `0.3`.
- **Orçamento de contexto (palavras)**: valor inicial `40`.

## 01. Conhecimento nos pesos tem data

### Fala sugerida

O exemplo é uma regra acadêmica inventada para ensino. A atualização acontece no acervo. O gerador ainda pode errar ao usar a informação recuperada.

### Na demonstração

Compare a fonte fictícia antiga e a atual.

### No quadro branco

Pesos fixos + fonte atual → contexto atualizado

### Pergunta à turma

RAG atualiza os pesos do modelo?

### Resposta e transição

Não; fornece contexto externo durante a inferência.

Avance para **Escolher entre contexto, treino e recuperação** e relacione o resultado observado ao próximo mecanismo.

## 02. Escolher entre contexto, treino e recuperação

### Fala sugerida

A memória externa também precisa de manutenção. Um acervo desatualizado produz evidência desatualizada. RAG desloca parte do problema para engenharia de dados e busca.

### Na demonstração

Mude o orçamento e compare acervo e contexto disponível.

### No quadro branco

Fonte extensa → seleção → contexto limitado

### Pergunta à turma

Recuperar dispensa verificar a qualidade da fonte?

### Resposta e transição

Não; o sistema depende da integridade e atualidade do acervo.

Avance para **Ingestão preserva a identidade** e relacione o resultado observado ao próximo mecanismo.

## 03. Ingestão preserva a identidade

### Fala sugerida

Uma frase sem origem é difícil de auditar. Vamos carregar identificadores desde o começo. Adicionar uma citação no final não recupera metadados que foram perdidos.

### Na demonstração

Inspecione os registros das cinco fontes fictícias.

### No quadro branco

Registro = texto + ID + seção + versão

### Pergunta à turma

Por que guardar versão da fonte?

### Resposta e transição

Para saber qual regra foi usada e invalidar conteúdos desatualizados.

Avance para **Chunking decide a unidade de evidência** e relacione o resultado observado ao próximo mecanismo.

## 04. Chunking decide a unidade de evidência

### Fala sugerida

Leiam os pedaços, não apenas suas contagens. Um corte pode remover a exceção que mudava a resposta. A melhor unidade depende do tipo de documento.

### Na demonstração

Varie tamanho e observe onde a frase foi cortada.

### No quadro branco

Granularidade = coerência local × orçamento

### Pergunta à turma

Existe tamanho de chunk universalmente ótimo?

### Resposta e transição

Não; estrutura, tarefa, modelo de embedding e orçamento influenciam a escolha.

Avance para **Sobreposição compra continuidade** e relacione o resultado observado ao próximo mecanismo.

## 05. Sobreposição compra continuidade

### Fala sugerida

O simulador limita a sobreposição para manter avanço. Com passo pequeno, produzimos muitos fragmentos parecidos. Continuidade tem custo e precisa ser medida.

### Na demonstração

Aumente overlap e compare número de chunks e palavras processadas.

### No quadro branco

Passo = tamanho − sobreposição

### Pergunta à turma

Sobreposição elimina todos os problemas de corte?

### Resposta e transição

Não; ajuda nas bordas, mas não garante preservar toda relação relevante.

Avance para **Embedding representa uma tarefa de busca** e relacione o resultado observado ao próximo mecanismo.

## 06. Embedding representa uma tarefa de busca

### Fala sugerida

Não estamos executando um modelo de embeddings. Os eixos nomeados tornam a geometria explicável. Em um embedding real, coordenadas individuais geralmente não têm esse significado simples.

### Na demonstração

Mude os eixos da consulta e veja sua direção.

### No quadro branco

Texto → vetor; proximidade depende do espaço aprendido

### Pergunta à turma

Qualquer estado oculto serve como ótimo embedding de busca?

### Resposta e transição

Não; objetivo de treinamento, pooling e avaliação da tarefa importam.

Avance para **Normalizar separa direção de escala** e relacione o resultado observado ao próximo mecanismo.

## 07. Normalizar separa direção de escala

### Fala sugerida

A conta usa os mesmos dois eixos. Se o vetor consulta for zero, cosseno não está definido. O painel explicita esse caso em vez de inventar direção.

### Na demonstração

Mude a consulta e compare norma, vetor e vetor unitário.

### No quadro branco

û = u/‖u‖; cos(u,v)=û·v̂

### Pergunta à turma

Produto escalar sempre é cosseno?

### Resposta e transição

Não; a igualdade exige vetores normalizados.

Avance para **Comparar consulta com candidatos** e relacione o resultado observado ao próximo mecanismo.

## 08. Comparar consulta com candidatos

### Fala sugerida

Agora o índice vira uma lista ordenada. O resultado depende da representação que escolhemos. Um texto parecido pode omitir o detalhe necessário.

### Na demonstração

Mova a consulta e acompanhe as mudanças do ranking.

### No quadro branco

score(q,d) = q·d/(‖q‖‖d‖)

### Pergunta à turma

O maior cosseno garante evidência suficiente?

### Resposta e transição

Não; precisamos verificar conteúdo e relevância para a pergunta.

Avance para **O índice troca custo por cobertura** e relacione o resultado observado ao próximo mecanismo.

## 09. O índice troca custo por cobertura

### Fala sugerida

A figura de aproximação é conceitual, não uma implementação de HNSW. A economia precisa ser medida junto com recall. Perder o documento correto aqui limita as etapas seguintes.

### Na demonstração

Compare comparações exatas e a ilustração de candidatos aproximados.

### No quadro branco

Exata: todos; aproximada: subconjunto candidato

### Pergunta à turma

Uma busca aproximada é necessariamente errada?

### Resposta e transição

Não; pode recuperar os mesmos melhores itens com menos trabalho, mas não há garantia universal.

Avance para **Montar contexto é outra seleção** e relacione o resultado observado ao próximo mecanismo.

## 10. Montar contexto é outra seleção

### Fala sugerida

O ranking inicial não é a resposta final. Vamos ver quais fontes chegaram de fato ao contexto. Cortar texto sem cuidado pode descartar justamente a exceção relevante.

### Na demonstração

Aumente top-k e reduza orçamento.

### No quadro branco

Contexto final ⊆ candidatos recuperados

### Pergunta à turma

O gerador pode citar uma fonte que não recebeu?

### Resposta e transição

Ele pode inventar uma referência, mas isso não constitui citação fundamentada.

Avance para **Resposta com evidência e abstenção** e relacione o resultado observado ao próximo mecanismo.

## 11. Resposta com evidência e abstenção

### Fala sugerida

Estamos usando extração para tornar a origem visível. Um gerador real exigiria avaliação de fidelidade. Uma citação existente também pode não sustentar a afirmação.

### Na demonstração

Mude a consulta e orçamento e observe a resposta extrativa.

### No quadro branco

Afirmação → trecho de apoio → fonte

### Pergunta à turma

Basta uma referência no final para garantir fundamentação?

### Resposta e transição

Não; é necessário verificar se ela apoia a afirmação específica.

Avance para **Desenhar um projeto que possa ser medido** e relacione o resultado observado ao próximo mecanismo.

## 12. Desenhar um projeto que possa ser medido

### Fala sugerida

Uma demonstração feliz não mede o sistema. Escolham perguntas com sinônimos, identificadores e ausência de resposta. O resultado deve permitir localizar a etapa que falhou.

### Na demonstração

Compare critérios de sucesso em cada estágio.

### No quadro branco

Corpus → consultas rotuladas → recall → resposta fundamentada

### Pergunta à turma

Qual métrica ajuda a descobrir se a evidência sequer chegou?

### Resposta e transição

Recall sobre os documentos ou trechos relevantes no conjunto recuperado.
