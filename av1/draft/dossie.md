# Dossiê de diagnóstico conceitual — Avaliação 01

**Nome completo:**
**Turma:**
**Disciplina:** Grandes Modelos de Linguagem

<!-- Estrutura pedida no enunciado para cada caso: problema central, mecanismo,
     consequência ou decisão, fundamento consultado. 100–180 palavras por caso. -->

## Caso 1

A acurácia alta engana porque o classificador de fato acerta nas solicitações comuns, mas, quando uma solicitação é urgente, ele a trata como comum, o que é muito prejudicial. O modelo é ruim porque erra justamente as solicitações mais importantes: existe uma hierarquia entre elas.

O erro que merece atenção prioritária é a urgente classificada como comum (falso negativo). A métrica pertinente é a revocação (recall), porque as urgentes precisam ser encontradas o máximo possível.

Se muitas solicitações comuns forem classificadas como urgentes, deixa de existir uma categorização: muitas coisas que não são urgentes serão tratadas como urgentes, e as realmente urgentes serão atendidas depois, porque os falsos positivos atrapalham a decisão.

**Fundamento:** Aula 1 — slide 7 (matriz de confusão, precisão e revocação; detector de fraude com 99% de acurácia) e slide 8 (comparação dos três detectores).

## Caso 2

O texto em português produziu mais tokens porque o tokenizador provavelmente foi treinado principalmente em inglês. Nesse caso, uma palavra em português é quebrada em mais pedaços, justamente pelas características da língua, como os acentos e o ç.

Com isso, a janela de contexto estoura mais rápido em português e, como se gastam mais tokens, um serviço cobrado por token fica mais caro.

Não é possível concluir que português sempre exige mais tokens: depende. Se o tokenizador foi treinado em uma língua diferente do português, sim; se foi treinado em português, ele tende a gastar menos tokens. Como o teste usou apenas um par de textos, eu aumentaria a amostra de dados para que a comparação fosse mais confiável. Também traria os mesmos conteúdos em línguas diferentes e usaria tokenizadores diferentes.

**Fundamento:** Aula 2 — slide 8 (byte-level e o preço do acento) e slide 12 (fertilidade, janela de contexto e custo por token).

## Caso 3

**Fundamento:**

## Caso 4

**Fundamento:**

## Caso 5

**Fundamento:**

## Caso 6

**Fundamento:**

## Caso 7

**Fundamento:**

## Caso 8

**Fundamento:**

<!-- Uma variação de um caso entre 1–4 e outra de um caso entre 5–8. 150–250 palavras cada. -->

## Variação 1

| Campo | |
|---|---|
| Caso de origem | |
| Nova condição | |
| O que muda | |
| O que permanece | |
| Como verificar | |

## Variação 2

| Campo | |
|---|---|
| Caso de origem | |
| Nova condição | |
| O que muda | |
| O que permanece | |
| Como verificar | |

## Referências

## Declaração de uso de IA

Utilizei [ferramenta] para [finalidade]. Conferi ou alterei [partes] com base em [materiais].
