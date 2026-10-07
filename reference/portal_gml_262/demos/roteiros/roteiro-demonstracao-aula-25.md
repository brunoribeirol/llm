# Aula 25 — Lab 7: o agente com a própria base

Monte um loop ReAct observável, conecte busca ao regulamento e depure parsing, memória, parada e custo. A política do modelo é uma simulação declarada.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Pergunta de teste**: valor inicial `deadline`.
- **Limite de passos**: valor inicial `4`.
- **Tokens de observação**: valor inicial `300`.
- **Defeito inserido**: valor inicial `none`.
- **Guardar observações**: valor inicial `True`.

## 01. O contrato de três partes

### Fala sugerida

O contrato informa o que resolver, com que recursos e como conversar com o host. Se uma dessas partes falta, o parser e o modelo podem discordar. Hoje vamos tornar essa discordância visível.

### Na demonstração

Selecione prazo com fonte e leia as três partes antes de executar o percurso.

### No quadro branco

objetivo + catálogo + formato

### Pergunta à turma

Um prompt detalhado substitui validação do host?

### Resposta e transição

Não. O host precisa conferir o que recebeu, mesmo quando as instruções foram claras.

Avance para **Thought e Action são propostas** e relacione o resultado observado ao próximo mecanismo.

## 02. Thought e Action são propostas

### Fala sugerida

Não estamos exibindo pensamentos internos de um modelo real. São campos de um protocolo didático roteirizado. A regra essencial é identificar quem tem autoridade para afirmar que uma execução ocorreu.

### Na demonstração

Ative modelo escreve Observation e veja a linha rejeitada.

### No quadro branco

modelo propõe Action; host produz Observation

### Pergunta à turma

Por que rejeitar Observation escrita pelo modelo?

### Resposta e transição

Para impedir que texto proposto seja confundido com evidência de uma ferramenta executada.

Avance para **Parsing estrito** e relacione o resultado observado ao próximo mecanismo.

## 03. Parsing estrito

### Fala sugerida

Um parser permissivo pode esconder o primeiro defeito da trajetória. Prefiro um erro localizável a uma chamada arbitrária. O teste precisa mostrar exatamente qual formato foi recusado.

### Na demonstração

Ative ação malformada e compare a entrada bruta com o resultado do parser.

### No quadro branco

ação inválida → erro observável, nunca execução implícita

### Pergunta à turma

Escolher a primeira ferramenta quando parsing falha é seguro?

### Resposta e transição

Não. Isso transforma uma falha de interpretação numa ação sem fundamento.

Avance para **A base anterior vira ferramenta** e relacione o resultado observado ao próximo mecanismo.

## 04. A base anterior vira ferramenta

### Fala sugerida

A interface do agente não precisa conhecer como a busca é implementada. Mas o resultado precisa preservar os identificadores. Sem fonte, a resposta perde a ligação com a evidência recuperada.

### Na demonstração

Alterne pergunta com prazo e assunto fora do acervo e compare os scores.

### No quadro branco

buscar(consulta) → trechos + ids + scores

### Pergunta à turma

Retornar só o texto do melhor trecho é suficiente para auditoria?

### Resposta e transição

É insuficiente quando elimina fonte, score e demais informações necessárias para investigar a recuperação.

Avance para **A ferramenta calcula, o modelo usa** e relacione o resultado observado ao próximo mecanismo.

## 05. A ferramenta calcula, o modelo usa

### Fala sugerida

Declaro a simplificação antes de fazer a conta. Não estamos decidindo dias úteis nem exceções de calendário. Estamos verificando se uma observação alimenta corretamente a próxima ação.

### Na demonstração

Selecione prazo e cálculo e confira a soma de dia inicial e duração.

### No quadro branco

dia final relativo = dia inicial + prazo

### Pergunta à turma

Acertar a soma basta para responder qualquer prazo real?

### Resposta e transição

Não. É preciso modelar a regra de contagem, calendário e exceções do domínio.

Avance para **A lista de mensagens é o estado** e relacione o resultado observado ao próximo mecanismo.

## 06. A lista de mensagens é o estado

### Fala sugerida

Aqui o defeito está no host, não na busca. A ferramenta retornou o artigo. O próximo passo falha porque esse retorno não foi preservado no estado.

### Na demonstração

Desmarque guardar observações e localize a primeira repetição.

### No quadro branco

histórico(t+1) = histórico(t) + ação + observação

### Pergunta à turma

Aumentar a qualidade do retriever corrige esse defeito?

### Resposta e transição

Não. O resultado pode ser perfeito e continuar invisível ao modelo por falha de memória.

Avance para **O while com limite** e relacione o resultado observado ao próximo mecanismo.

## 07. O while com limite

### Fala sugerida

O limite é uma escolha do produto com efeitos observáveis. Um limite pequeno protege recursos e pode impedir uma tarefa legítima. Precisamos registrar esgotamento como estado diferente de resposta completa.

### Na demonstração

Selecione prazo e cálculo, reduza o limite para um e depois aumente para quatro.

### No quadro branco

continuar = precisa agir E tem orçamento

### Pergunta à turma

Qual é o erro de devolver sucesso ao atingir o teto?

### Resposta e transição

Ocultar que a tarefa foi interrompida e apresentar uma resposta possivelmente sem fundamento.

Avance para **Sem fonte, a parada honesta** e relacione o resultado observado ao próximo mecanismo.

## 08. Sem fonte, a parada honesta

### Fala sugerida

O sistema pode cumprir seu contrato dizendo que não encontrou base. Isso é mais útil que uma data arbitrária. O log deve permitir distinguir ausência na coleção de uma falha do retriever.

### Na demonstração

Selecione assunto fora do acervo e observe a resposta e o motivo de parada.

### No quadro branco

sem evidência → abstenção localizada

### Pergunta à turma

Uma abstenção sempre significa que o dado não existe?

### Resposta e transição

Não. Pode haver falha de recuperação; precisamos avaliar o acervo e o mecanismo de busca separadamente.

Avance para **A trajetória como artefato** e relacione o resultado observado ao próximo mecanismo.

## 09. A trajetória como artefato

### Fala sugerida

Quero que outra pessoa consiga reconstruir a execução sem me perguntar o que aconteceu. A resposta final é apenas uma linha desse artefato. O diagnóstico mora nas transições.

### Na demonstração

Alterne sem defeito e repetição da busca; compare as linhas da trajetória.

### No quadro branco

passo, ação, argumento, observação, custo, parada

### Pergunta à turma

Por que registrar somente erros não é suficiente?

### Resposta e transição

Porque precisamos comparar também as etapas corretas e a sequência que levou ao defeito.

Avance para **Custo por passo** e relacione o resultado observado ao próximo mecanismo.

## 10. Custo por passo

### Fala sugerida

A observação grande continua sendo paga nas voltas seguintes. É por isso que recortar o retorno de uma ferramenta pode reduzir muito o contexto. Precisamos fazer o recorte sem remover a evidência necessária.

### Na demonstração

Aumente tokens de observação e compare barras de cada chamada e total.

### No quadro branco

T(n) = n p₀ + d·n(n−1)/2

### Pergunta à turma

O modo offline mede o custo real de um provedor?

### Resposta e transição

Não. Ele verifica a fórmula e o controle do fluxo; tokenização, cache, preço e latência reais exigem medição própria.

Avance para **Comparação justa com framework** e relacione o resultado observado ao próximo mecanismo.

## 11. Comparação justa com framework

### Fala sugerida

Não vamos comparar uma versão manual simples com outra cheia de recursos extras. Primeiro igualamos o contrato. Depois medimos o que ficou mais fácil e o que ficou menos visível.

### Na demonstração

Observe o mapeamento de responsabilidades entre loop manual e abstração de framework.

### No quadro branco

mesma tarefa + mesmas ferramentas + mesmos limites

### Pergunta à turma

Migrar para framework resolve automaticamente parada e autorização?

### Resposta e transição

Não. Essas políticas precisam ser configuradas, verificadas e observadas em qualquer implementação.

Avance para **Cinco checkpoints verificáveis** e relacione o resultado observado ao próximo mecanismo.

## 12. Cinco checkpoints verificáveis

### Fala sugerida

A simulação é útil porque falha sempre do mesmo jeito. Ela permite depurar o nosso código. Depois precisamos avaliar a política real em um conjunto representativo, com o mesmo registro de trajetória.

### Na demonstração

Escolha dois defeitos e diga qual checkpoint deve detectá-los antes da entrega.

### No quadro branco

infraestrutura testada ≠ qualidade do agente avaliada

### Pergunta à turma

Quais resultados desta página podem ser tratados como benchmark de LLM?

### Resposta e transição

Nenhum. São verificações e simulações de mecanismos locais, não medições de capacidade de um modelo.
