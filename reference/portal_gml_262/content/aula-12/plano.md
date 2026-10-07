---
aula: 12
titulo: "Pré-treinamento: dados, leis de escala e sistemas"
modulo: "3 — Treinamento: pré-treino, SFT e PEFT"
tipo: teorica
semana: 6
duracao_min: 120
versao: v2
---

# Aula 12 — Pré-treinamento: dados, leis de escala e sistemas

> **Postura deste material.** Artifact-first: o que esta aula produz são artefatos
> versionáveis (notebook, medição, anotação), não conversas descartáveis com um chatbot.
> O roteiro de fala vive em `roteiro.md`; a especificação dos slides em `instructions-slides.md`.

> **Rebalanceamento V2.** A aula é conduzida por **três defeitos de fábrica** — um orçamento
> dividido errado pela indústria inteira até 2022, um `OOM` que acontece com a GPU ociosa, e um
> parágrafo que o modelo devolve literalmente — e cada bloco fecha um deles pela causa. As contas
> aparecem enunciadas com o número que produzem; as derivações estão no apêndice, em sete itens.
> **`C ≈ 6ND` é a derivação que a Aula 10 remete explicitamente para cá** (Parte 4, item 1 do
> roteiro dela), e ela está completa em A.1. Carga horária, numeração e objetivos inalterados.

## 1. Objetivo da aula

Entrar na fábrica que produziu o arquivo de pesos. O aluno sai capaz de decidir, com um orçamento de compute na mão, quanto gastar em capacidade e quanto em experiência — e de diagnosticar por que um treino estoura a memória antes de estourar a aritmética. A aula fecha constatando que toda essa engenharia entrega um **completador de texto**, que é exatamente o problema da Aula 13.

## 2. Resultados de aprendizagem

Ao final desta aula o estudante deve ser capaz de:

1. Estimar o custo de treino em FLOPs por `C ≈ 6ND` e o custo de inferência por `C ≈ 2N`, explicando a assimetria entre o que se paga uma vez e o que se paga para sempre.
2. Calcular a alocação compute-optimal de Chinchilla para um orçamento dado e **justificar por que 20 tokens por parâmetro não é constante universal**.
3. Decompor a memória de treino nos quatro consumidores — pesos, gradientes, estados do otimizador, ativações — e diagnosticar qual deles estourou.
4. Distinguir paralelismo de dados, de tensor e de pipeline pelo que cada um particiona e pelo que cada um passa a comunicar.
5. Explicar por que a curadoria de corpus é decisão de modelagem e não de infraestrutura, nomeando os efeitos da duplicata sobre memorização e contaminação.
6. Justificar por que FlashAttention acelera sem reduzir a complexidade assintótica.

*(Idênticos aos da V1.)*

## 3. Teoria aplicada

A aula abre pelos **três defeitos**, projetados juntos no slide 1, e volta a cada um no momento em que o conteúdo o resolve. Nenhum é bug de implementação: todos são consequência correta de uma decisão de orçamento tomada antes da primeira linha de código.

| # | O defeito, como aparece | Onde fecha | Causa nomeada |
|---|---|---|---|
| 1 | "Tenho orçamento fechado. Modelo maior ou mais tokens?" — e a indústria respondeu errado até 2022 | Slide 8 | a curva isoFLOP tem mínimo interior |
| 2 | `OOM` com a GPU a 30% de ocupação: estoura a memória **antes** da aritmética | Slide 11 | 16 bytes por parâmetro, mais ativações |
| 3 | O modelo devolve **literalmente** um parágrafo do corpus, e acerta um benchmark que estava na web | Slide 6 | duplicata memoriza e contamina |

### Bloco 1 (00:10–00:55) — O orçamento: o que o próximo token supervisiona de graça

**O número que a turma trouxe.** A aula abre cobrando a lição de casa da Aula 11: `N` e `D` do modelo que cada um rodou no Ollama, e a razão `D/N`. As duas contas são **enunciadas e lidas**, não manipuladas: treinar custa proporcional a capacidade × experiência; gerar um token custa proporcional só à capacidade ativa. E a razão `D/N` da turma fica no quadro, porque no meio da aula uma teoria vai dizer que o valor certo é 20 — e o deles não é 20. O incômodo é deliberado e só se resolve no slide 16.

- **Fundamento:** o fator 6 é `2 + 4` — dois FLOPs por parâmetro por token no forward, quatro no backward — e a atualização do otimizador fica fora porque paga por passo, não por token. Verificação: `6 × 1,75e11 × 3,0e11 = 3,15e23`, o valor reportado para o GPT-3.
  → derivação completa: **Apêndice A.1** (slide 17). **É a derivação que a Aula 10 prometeu para cá.**

**Transferência de aprendizado, e o supervisor que não existe.** Um treino caro, muitas tarefas baratas. E a correção de vocabulário que importa: não é "não supervisionado", é **auto-supervisionado** — o rótulo de cada posição é o token seguinte, que já está no corpus. A consequência prática fecha o bloco: se o supervisor é o corpus, **a qualidade do corpus é decisão de modelagem**, não de infraestrutura. Para a metade da turma sem ML prévio, este é o ponto de perder ou salvar a aula: a perda do pré-treino é a mesma entropia cruzada do próximo token que eles minimizaram no Lab 2, e a diferença para o GPT-3 é de orçamento, não de ideia.

**De onde vem o texto.** Quatro fontes — web, livros, código, curado — cada uma com o que **só** ela ensina: quantidade, coerência longa, formato estrito, densidade de fato. Nenhuma sozinha dá o modelo, e a mistura é decisão de treino que os cartões de modelo não declaram.
*A linhagem, para que "curadoria importa" pare de ser adjetivo:* `CCNet` (2019, filtra a web por semelhança com a Wikipédia) → `C4` (2019, por regras) → `Gopher` (2021) → `DCLM` e `FineWeb` (2024) → `Nemotron-CC` (2024) → `OLMo 2` (2025). Dois mecanismos separam uma receita da outra, e são só dois: **deduplicação** — na prática por `MinHash`, porque a web repete e repetição vira memorização, que é o Defeito 3 desta aula — e **filtro de qualidade por classificador**, em que se treina um classificador barato para distinguir texto tipo-Wikipédia de texto tipo-web-bruta e se descarta a cauda, em vez de escrever regra a regra.

**Defeito 3 fechado: deduplicar não é limpeza, é orçamento.** Um documento em mil espelhos é visto mil vezes, e um exemplo visto mil vezes é memorizado, não aprendido. Três efeitos: gasto de orçamento em repetição, memorização literal, e contaminação de benchmark.

**Leis de escala, e a divisão do cheque.** A perda cai como lei de potência no compute — e o que isso permite é **prever** antes de gastar. Kaplan estabeleceu as potências; Chinchilla mostrou que, com orçamento fixo, existe um mínimo interior: a curva isoFLOP tem um U, e o fundo dele é a alocação ótima. **Defeito 1 fechado.** A razão de ~20 tokens por parâmetro é o resultado desse regime, apresentada como resultado e não como lei.

- **Fundamento:** a otimização com restrição que produz `N ≈ √(C/120)` e `D ≈ 20·N`, com as premissas declaradas.
  → derivação completa: **Apêndice A.2** (slide 18)
- **Fundamento:** a lei de potência de Kaplan e o que significa o expoente.
  → derivação completa: **Apêndice A.3** (slide 19)

### Bloco 2 (01:05–01:50) — A máquina que executa o orçamento

O eixo troca: sai da teoria do orçamento e entra na máquina que precisa executá-lo.

**`C ≈ 6ND` com hora de GPU real.** A conversão que torna o orçamento concreto: pico em TFLOP/s, MFU, dias de GPU — e o `C` que sai disso.

**Defeito 2 fechado: o `OOM` com a GPU ociosa.** Quatro consumidores de memória, não um: pesos, gradientes, os dois momentos do Adam, ativações. A conta de **16 bytes por parâmetro** só cobre os três primeiros; as ativações escalam com lote × contexto e são o que estoura sem aviso. É por isso que a GPU pode estar a 30% de ocupação aritmética e ainda assim faltar memória.

- **Fundamento:** a decomposição de 16 bytes por parâmetro nos quatro consumidores, com as ativações contabilizadas.
  → derivação completa: **Apêndice A.4** (slide 20)

**Precisão mista, e os três paralelismos.** bf16 para calcular, fp32 para acumular — e a razão de a acumulação não poder ser em meia precisão. Dados, tensor e pipeline: o que cada um particiona, e **o que cada um passa a comunicar**, que é o custo escondido.

- **Fundamento:** o volume de comunicação de cada paralelismo, por passo.
  → derivação completa: **Apêndice A.5** (slide 21)

**FlashAttention.** Atenção exata, consciente da hierarquia de memória. O ponto que a turma precisa levar: ela **não** muda a complexidade assintótica e ainda assim acelera, porque o regime é limitado por I/O entre HBM e SRAM.

- **Fundamento:** o argumento de I/O, com a contagem de acessos à memória nos dois esquemas.
  → derivação completa: **Apêndice A.6** (slide 22)

### Grade temporal

| Início | Dur. | Bloco | Subtemas |
|---|---|---|---|
| 00:00 | 10 min | Abertura | Recap do Lab 3 em uma frase · **os três defeitos projetados juntos** · o número que a turma trouxe (`N`, `D`, `D/N`) e as duas contas enunciadas |
| 00:10 | 45 min | Bloco 1 — O orçamento | Transferência de aprendizado · o supervisor é o corpus · as quatro fontes · **defeito 3 fechado** (dedup) · leis de potência · **defeito 1 fechado** (isoFLOP tem mínimo) · **demo da curva isoFLOP** |
| 00:55 | 10 min | Intervalo | — |
| 01:05 | 45 min | Bloco 2 — A máquina | `C ≈ 6ND` com hora de GPU real · **defeito 2 fechado** (os quatro consumidores) · precisão mista · os três paralelismos e o que cada um comunica · FlashAttention · **exercício em dupla (4 min)** |
| 01:50 | 10 min | Fechamento | Os três defeitos fechados · **a resolução do paradoxo do slide 2** (20:1 e milhares:1 são ótimos de funções diferentes) · a fábrica entrega um completador de texto · leituras · 20 s de índice do apêndice |

## 4. Demonstração guiada

**`codigo/demo-scaling-laws.py` — Python puro, sem GPU, sem rede, determinística.**

Quatro atos: a tabela de alocação ótima de `10¹⁹` a `10²⁵` FLOPs; perda × compute em log-log; as **curvas isoFLOP** com os mínimos marcados; e o contrafactual do GPT-3 com a conversão de horas de GPU em FLOPs.

**Aviso de proveniência, que vai na tela:** as constantes da superfície de perda são calibradas para fins didáticos — elas reproduzem a razão 20:1, mas **não** são os coeficientes publicados do ajuste. É a mesma exigência de procedência que o Lab 8 vai cobrar das equipes, aplicada ao material do professor.

**Número que a demo produz.** Três, e os três voltam ao fluxo. A coluna **`D/N = 20`** da tabela de alocação, que é o que fecha o defeito 1 no slide 8. O contrafactual do GPT-3 — **51 B de parâmetros com 1,02 T de tokens** seria a alocação ótima para o mesmo orçamento, contra os 175 B / 300 B reais — que é o argumento mais forte da aula, porque mostra a indústria inteira errando com dinheiro real. E o par **`6,0e20 FLOPs → 2,2 B parâmetros`**, que é o cenário do exercício do slide 15 e o que amarra o Bloco 1 ao Bloco 2.

**Contingência:** se o `matplotlib` não abrir janela, usar os PNGs gerados na véspera; se não houver Python na máquina, desenhar o U no quadro em 90 segundos — os mínimos são o que importa, não a suavidade da curva. O script tem guarda de encoding e detecção de backend, então não trava em terminal sem display.

## 5. Hands-on

**Exercício em dupla — 4 minutos, dentro do slide 15. "Decidir, não calcular."**

O cenário já está resolvido na tela: a demo imprimiu os números. O que se pede é a **decisão**.

> *Orçamento: 8 GPUs equivalentes a A100 por 7 dias, pico 312 TFLOP/s em bf16, MFU 40%.*
> *A demo imprimiu: `C ≈ 6,0e20 FLOPs`, `N ≈ 2,2e9`, `D ≈ 4,5e10`.*

1. Esse modelo **cabe** no treino que vocês dimensionaram? Que conta responde isso, e o que ela conta?
2. O que estoura primeiro — memória ou aritmética? Que **medição** confirma o diagnóstico?
3. Se não couber numa GPU, qual paralelismo primeiro — e o que ele passa a comunicar?
4. Vocês têm 45 B de tokens no orçamento e um corpus cru de 300 B com 40% de duplicata. Filtrar agressivamente ajuda ou atrapalha? Justifiquem com um dos três efeitos do slide 6.

**Critério de conclusão observável:** a dupla responde o item 1 com uma conta e o item 3 com um paralelismo nomeado mais o que ele comunica. As quatro perguntas pedem saber o que a conta **prevê** — nenhuma pede derivação.

O rodapé do slide traz as fórmulas necessárias já escritas (`16 bytes/param`, `8 × 80 GB`): o exercício testa raciocínio, não memória de fórmula.

**Erros esperados, e são informativos.** No item 1, contar só os pesos (2 bytes) e concluir que cabe folgado — a resposta é `2,2e9 × 16 = 35,2e9 bytes ≈ 32,8 GiB` de estados contra `8 × 74,5 GiB` agregados: **cabe distribuído, não cabe numa GPU só**. No item 3, responder "tensor" por ser o que soa mais sofisticado, quando a resposta é **dados com estados particionados**. O item 4 é o que amarra os dois blocos e é o que se corrige se só houver tempo para um.

**Extensão opcional:** refazer à mão a aritmética que a demo fez — de pico e MFU até `C`, e de `C` até `(N, D)`. Gabarito completo em **A.2**.

## 6. Riscos e contingências

| Risco | Sinal | Plano B |
|---|---|---|
| **Metade da turma sem ML prévio** se perde na noção de perda e gradiente | Mãos hesitam no slide 3 | Gastar 60 s extras na definição operacional: treinar é ajustar pesos por descida de gradiente para reduzir uma perda, e a perda daqui é a mesma do Lab 2. **Não** abrir teoria de otimização |
| Turma **erra a ordem de grandeza** e o número perde sentido | Alguém multiplica e chega a `10¹⁵` | Fazer a multiplicação devagar na tela, com as potências de dez alinhadas verticalmente. É a habilidade que a aula inteira depende |
| `matplotlib` não abre janela / sem Python na máquina | Demo não sobe | PNGs da véspera; em último caso, o U desenhado no quadro em 90 s. O script já tem guarda de encoding e detecção de backend |
| Pergunta sobre **direito autoral de corpus** | Aparece no slide 5, sempre | Legítima, e é Aula 29. Não abrir aqui: consome 15 min e desmonta o Bloco 1 |
| Turma toma **20:1 como lei universal** | Ninguém se incomoda com o `D/N` do próprio modelo | O incômodo é o mecanismo: o `D/N` da turma fica no quadro desde o slide 2 e o paradoxo só se resolve no slide 16. Se ninguém se incomodar, provocar: "o de vocês deu quanto?" |
| **Não antecipar o paradoxo** | — | O slide 16 só funciona se a tensão foi mantida. Não resolver antes, mesmo se perguntarem — dizer "guarda essa pergunta, ela é o fechamento da aula" |
| Pergunta pela derivação do fator 6 | Provável, porque a Aula 10 prometeu | **Atender**: é a promessa que esta aula honra. Parte 4, item 1, 5 min de quadro |
| Bloco 2 fica sem tempo | 01:35 e ainda no slide 12 | Comprimir precisão mista (slide 12) para 2 min e FlashAttention (14) para 3, mantendo o argumento de I/O. **Não cortar** o slide 11 (defeito 2) nem o exercício |

## 7. Artefatos produzidos

- `codigo/demo-scaling-laws.py` e os PNGs das curvas isoFLOP — ficam no repositório do aluno como referência de dimensionamento.
- A tabela de alocação ótima impressa pela demo, com a coluna `D/N`.
- As respostas do exercício de decisão, recolhidas em aula (não avaliadas).
- O `N`, `D` e `D/N` do modelo que cada aluno rodou no Ollama, anotados desde a Aula 11 — insumo do slide 2 e do paradoxo do slide 16.

## 8. Desafio pós-aula

1. **A conta do próprio modelo.** Para o modelo que vocês rodaram no Lab 3: qual seria a alocação ótima de Chinchilla para o mesmo orçamento de treino? O modelo real está acima ou abaixo de 20:1, e **por que quem o treinou tomou essa decisão**? Responder com número.
2. **Leitura, com pergunta dirigida.** Hoffmann et al., *Chinchilla* (arXiv 2203.15556): o artigo apresenta três abordagens independentes para estimar a alocação ótima e as três convergem. Qual delas depende de menos suposições sobre a forma da superfície de perda, e por que isso importa para confiar no resultado?
3. **Setup para o Lab 4:** Colab com GPU habilitada e conta do Hugging Face com token criado. Quem não tem uma aula de prazo perde os primeiros 15 minutos do lab.

## 9. Critérios de avaliação

Esta aula não tem entregável avaliado. A prática desta unidade é recolhida no **Lab 4 (Aula 14)**, que compõe os 30% de laboratórios da ementa.

O conteúdo desta aula é cobrado na **prova da Aula 17**, cuja composição é: diagnóstico e interpretação de comportamento **42** · justificativa de escolha **40** · conceito aplicado **8** · derivação **10**.

Esta aula tem uma relação particular com essa distribuição, e vale explicitar. O exercício do slide 15 é deliberadamente do formato das questões de **justificativa** — cenário com restrições reais, decisão a defender, e a conta como ferramenta de sustentação. E a conta de memória (A.4) e a alocação de Chinchilla (A.2) são exatamente o tipo de fundamento cuja ausência faz uma resposta de justificativa perder pontos: dizer "usaria paralelismo de dados" sem a conta que mostra que os estados não cabem numa GPU não é justificativa suficiente. **O apêndice desta aula é cobrado sobretudo dentro dos 40 pontos, não dos 10.**

## Apêndice matemático — índice

Sete itens, slides 17 a 23 do deck. Material de estudo e consulta, autossuficiente.

| Item | O que estabelece | Apontado do |
|---|---|---|
| **A.1** | De onde sai `C ≈ 6ND`: os 2 FLOPs por parâmetro por token no forward, os 4 no backward, e a atualização do otimizador **contabilizada e descartada com número** (ela paga por passo, não por token). Mais `C ≈ 2N` por token na inferência, e a verificação contra o valor reportado do GPT-3. **É a derivação que a Aula 10 remete para cá.** | slides 2 e 10 |
| **A.2** | A otimização com restrição de Chinchilla: minimizar a perda sob `C = 6ND` fixo, produzindo `N ≈ √(C/120)` e `D ≈ 20·N`, com **premissas declaradas**. Inclui a inversão da função-objetivo de quem *serve* o modelo — `6ND + 2N·(tokens da vida do produto)` — que explica por que um modelo de 1 B com `D/N = 15.000` não está errado, e as três ressalvas sobre o 20:1. Gabarito da extensão opcional do exercício. | slides 8, 15 e 16 |
| **A.3** | A lei de potência de Kaplan, o significado do expoente, e o que ela permite prever antes de gastar. Por que a extrapolação é confiável dentro do regime ajustado e não fora dele. | slide 7 |
| **A.4** | A memória de treino decomposta nos quatro consumidores: pesos, gradientes, os dois momentos do Adam (que somam os 16 bytes por parâmetro), **mais as ativações**, que escalam com lote × contexto e são o que estoura sem aviso. É a conta que responde o item 1 do exercício. | slides 11 e 15 |
| **A.5** | O custo de comunicação de cada paralelismo, por passo: o que dados, tensor e pipeline particionam e o volume que cada um passa a trocar. É o que responde o item 3 do exercício e o que explica por que "tensor" é a resposta errada ali. | slides 13 e 15 |
| **A.6** | Por que FlashAttention não muda a complexidade assintótica e ainda assim acelera: a contagem de acessos a HBM nos dois esquemas, e o argumento de I/O. Liga com A.3 da Aula 29, que estabelece a intensidade aritmética do regime de decodificação. | slide 14 |
| **A.7** | **Como se escolhe a taxa de aprendizado de um modelo que ainda não existe.** O item que fecha a pergunta que A.2 monta e não responde: Chinchilla diz o tamanho certo, e nada diz qual taxa usar — sendo que varrer a taxa no modelo-alvo custa mais que o próprio modelo-alvo. A saída é **ajustar no pequeno e transferir**, e ela só é legítima sob a **parametrização maximal (muP)**, que reescala inicialização e taxa por camada em função da largura de modo que a taxa ótima fique **≈ invariante à escala** — com o `≈` sendo invariância empírica, não teorema. A receita completa do **MiniCPM** em quatro passos, com as constantes publicadas: muP, **razão de aspecto fixa** (para restar um só eixo de escala), ajuste do lote e da taxa por análise de escala em modelos de 9 M a 170 M, e extrapolação com vão de cerca de **5×** — que é a leitura honesta de quanto se pode extrapolar. Casos-limite: trocar de otimizador invalida a transferência (o **Muon** é o caso ativo), mudar a razão de aspecto também, extrapolação longa demais degrada, e lote grande demais deixa de comprar convergência. | slides 7 a 10 |
