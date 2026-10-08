# Aula 04 — Lab 1: um experimento reproduzível do texto ao vetor

Meça tokenização e execute uma miniatura de treinamento de embeddings

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Texto em português**: valor inicial `o gato dorme na casa`.
- **Texto equivalente em inglês**: valor inicial `the cat sleeps at home`.
- **Merges do mini-BPE**: valor inicial `5`.
- **Requisições hipotéticas**: valor inicial `1000`.
- **Janela em tokens**: valor inicial `64`.
- **Passos de treino do vetor central**: valor inicial `10`.
- **Taxa de aprendizado**: valor inicial `0.1`.
- **Rotação da projeção (graus)**: valor inicial `0`.

## 01. Formule uma comparação verificável

### Fala sugerida

O laboratório transforma intuições sobre tokenização e embeddings em medições. Esta versão de navegador usa algoritmos pequenos locais, enquanto os notebooks do curso permitem repetir o estudo com bibliotecas e modelos reais. Mantenha os dois textos equivalentes e escolha uma quantidade fixa de merges. Pergunto à turma: “Comparar frases com conteúdos diferentes isola o efeito do idioma?” Não; comprimento e assunto também variam, por isso um par aproximadamente equivalente torna a comparação mais interpretável.

### Na demonstração

Mantenha os dois textos equivalentes e escolha uma quantidade fixa de merges.

### No quadro branco

Hipótese + dados + configuração + métrica + evidência

### Pergunta à turma

Comparar frases com conteúdos diferentes isola o efeito do idioma?

### Resposta e transição

Não; comprimento e assunto também variam, por isso um par aproximadamente equivalente torna a comparação mais interpretável.

Avance para **Fixe os dados e a configuração** e relacione o resultado observado ao próximo mecanismo.

## 02. Fixe os dados e a configuração

### Fala sugerida

Uma comparação reproduzível registra corpus, normalização e parâmetros antes de medir. O mini-BPE é treinado no mesmo corpus fixo usado na demonstração de tokenização. Altere Merges e observe a ficha de configuração que deve acompanhar os resultados. Pergunto à turma: “Por que guardar o texto bruto além da contagem?” A contagem sozinha não permite verificar se pontuação, acentos ou espaços foram tratados do mesmo modo.

### Na demonstração

Altere Merges e observe a ficha de configuração que deve acompanhar os resultados.

### No quadro branco

Registro: textos, regras, contagens, versão do experimento

### Pergunta à turma

Por que guardar o texto bruto além da contagem?

### Resposta e transição

A contagem sozinha não permite verificar se pontuação, acentos ou espaços foram tratados do mesmo modo.

Avance para **Compare quatro divisões didáticas** e relacione o resultado observado ao próximo mecanismo.

## 03. Compare quatro divisões didáticas

### Fala sugerida

A tabela compara palavras, caracteres, bytes UTF-8 e o mini-BPE local. Elas não representam medições dos tokenizadores comerciais discutidos no notebook. Edite um acento ou emoji e veja quais divisões aumentam mais. Pergunto à turma: “Byte e caractere são unidades equivalentes?” Não; UTF-8 pode codificar um caractere em vários bytes, alterando a contagem.

### Na demonstração

Edite um acento ou emoji e veja quais divisões aumentam mais.

### No quadro branco

Mesmo texto → quatro unidades → quatro contagens

### Pergunta à turma

Byte e caractere são unidades equivalentes?

### Resposta e transição

Não; UTF-8 pode codificar um caractere em vários bytes, alterando a contagem.

Avance para **Inspecione as peças antes de confiar no total** e relacione o resultado observado ao próximo mecanismo.

## 04. Inspecione as peças antes de confiar no total

### Fala sugerida

Duas segmentações podem ter contagens iguais e fronteiras diferentes. A inspeção das peças explica resultados que um número agregado esconderia. Acrescente casas casaco e compare a segmentação antes e depois de aumentar Merges. Pergunto à turma: “O que verificar se a contagem parece estranha?” Primeiro o texto normalizado, os espaços e as peças; depois a implementação e suas regras.

### Na demonstração

Acrescente casas casaco e compare a segmentação antes e depois de aumentar Merges.

### No quadro branco

Não guardar só N: guardar também a sequência de peças

### Pergunta à turma

O que verificar se a contagem parece estranha?

### Resposta e transição

Primeiro o texto normalizado, os espaços e as peças; depois a implementação e suas regras.

Avance para **Calcule fertilidade em cada texto** e relacione o resultado observado ao próximo mecanismo.

## 05. Calcule fertilidade em cada texto

### Fala sugerida

A fertilidade divide tokens por palavras em cada entrada. O denominador é explícito e entradas vazias recebem uma indicação sem divisão por zero. Encurte um dos textos e compare tokens por palavra com o total bruto. Pergunto à turma: “Um texto com mais tokens necessariamente tem maior fertilidade?” Não; ele pode simplesmente ter mais palavras, por isso o denominador precisa ser observado.

### Na demonstração

Encurte um dos textos e compare tokens por palavra com o total bruto.

### No quadro branco

F_PT = N_PT/W_PT; F_EN = N_EN/W_EN

### Pergunta à turma

Um texto com mais tokens necessariamente tem maior fertilidade?

### Resposta e transição

Não; ele pode simplesmente ter mais palavras, por isso o denominador precisa ser observado.

Avance para **Separe razão de custo de capacidade** e relacione o resultado observado ao próximo mecanismo.

## 06. Separe razão de custo de capacidade

### Fala sugerida

Para o mesmo número de requisições e preço unitário, o custo é proporcional aos tokens por requisição. Para uma janela fixa, a quantidade aproximada de palavras é inversamente proporcional à fertilidade. Dobre Requisições e mantenha Janela fixa; depois dobre só a Janela. Pergunto à turma: “Por que as duas contas não são a mesma porcentagem?” Uma multiplica volume pelo número de tokens e a outra divide capacidade pela fertilidade.

### Na demonstração

Dobre Requisições e mantenha Janela fixa; depois dobre só a Janela.

### No quadro branco

Razão de custo = N_PT/N_EN; palavras que cabem ≈ janela/F

### Pergunta à turma

Por que as duas contas não são a mesma porcentagem?

### Resposta e transição

Uma multiplica volume pelo número de tokens e a outra divide capacidade pela fertilidade.

Avance para **Extraia pares positivos e negativos** e relacione o resultado observado ao próximo mecanismo.

## 07. Extraia pares positivos e negativos

### Fala sugerida

A miniatura de embeddings parte de um centro, um contexto positivo e contextos negativos fixos. Isso torna explícitos os exemplos que fornecem sinal de aprendizado. Observe os vetores iniciais e os rótulos positivo/negativo antes de mover Passos de treino. Pergunto à turma: “O vetor recebe diretamente um rótulo semântico como animal?” Não; o sinal vem da tarefa de discriminar contextos observados e amostrados.

### Na demonstração

Observe os vetores iniciais e os rótulos positivo/negativo antes de mover Passos de treino.

### No quadro branco

centro-contexto observado: 1; contraste amostrado: 0

### Pergunta à turma

O vetor recebe diretamente um rótulo semântico como animal?

### Resposta e transição

Não; o sinal vem da tarefa de discriminar contextos observados e amostrados.

Avance para **Acompanhe uma perda que de fato é calculada** e relacione o resultado observado ao próximo mecanismo.

## 08. Acompanhe uma perda que de fato é calculada

### Fala sugerida

Cada passo calcula perda logística e gradiente do vetor central e aplica SGD. Apenas esse vetor é ajustado; esta miniatura não é um treinamento Word2Vec completo. Mova Passos de 0 a 20 e compare perda inicial, atual e trajetória. Pergunto à turma: “A curva exibida foi inventada para parecer treinamento?” Não; os valores resultam das atualizações locais mostradas, embora a tarefa e o número de parâmetros sejam deliberadamente pequenos.

### Na demonstração

Mova Passos de 0 a 20 e compare perda inicial, atual e trajetória.

### No quadro branco

L = −log σ(v·u⁺) − soma log σ(−v·u⁻)

### Pergunta à turma

A curva exibida foi inventada para parecer treinamento?

### Resposta e transição

Não; os valores resultam das atualizações locais mostradas, embora a tarefa e o número de parâmetros sejam deliberadamente pequenos.

Avance para **Investigue a taxa de aprendizado** e relacione o resultado observado ao próximo mecanismo.

## 09. Investigue a taxa de aprendizado

### Fala sugerida

A taxa controla o tamanho de cada atualização, e sua escolha muda a trajetória. Compare configurações mantendo dados, vetor inicial e quantidade de passos constantes. Compare taxas 0,05 e 1 com 10 passos; registre perda e coordenadas finais. Pergunto à turma: “Uma taxa que reduz a perda aqui funciona em qualquer modelo?” Não; a estabilidade depende da geometria da perda, da escala dos gradientes e do otimizador.

### Na demonstração

Compare taxas 0,05 e 1 com 10 passos; registre perda e coordenadas finais.

### No quadro branco

Comparação justa: mudar uma variável por vez

### Pergunta à turma

Uma taxa que reduz a perda aqui funciona em qualquer modelo?

### Resposta e transição

Não; a estabilidade depende da geometria da perda, da escala dos gradientes e do otimizador.

Avance para **Projete sem confundir a figura com o espaço** e relacione o resultado observado ao próximo mecanismo.

## 10. Projete sem confundir a figura com o espaço

### Fala sugerida

O gráfico usa uma projeção explícita de pontos 3D para 2D e permite girar os eixos de leitura. A projeção é uma demonstração de perda de informação, não uma execução de PCA ou t-SNE. Gire a projeção e compare quais pontos parecem próximos em 2D com as distâncias 3D da tabela. Pergunto à turma: “Um agrupamento bonito em duas dimensões prova que os vizinhos originais são bons?” Não; a projeção pode comprimir ou esconder diferenças, então as relações devem ser conferidas no espaço original.

### Na demonstração

Gire a projeção e compare quais pontos parecem próximos em 2D com as distâncias 3D da tabela.

### No quadro branco

Distância no espaço original ≠ distância na projeção

### Pergunta à turma

Um agrupamento bonito em duas dimensões prova que os vizinhos originais são bons?

### Resposta e transição

Não; a projeção pode comprimir ou esconder diferenças, então as relações devem ser conferidas no espaço original.

Avance para **Teste vizinhos e registre falhas de analogia** e relacione o resultado observado ao próximo mecanismo.

## 11. Teste vizinhos e registre falhas de analogia

### Fala sugerida

O ranking é calculado no espaço disponível e precisa ser confrontado com o objetivo do experimento. Uma analogia que falha é um resultado a interpretar, não um ponto a remover do relatório. Compare os vizinhos antes e depois do treino e a perda associada a cada configuração. Pergunto à turma: “É correto selecionar só analogias que funcionaram?” Não; isso esconde as limitações e impede avaliar a representação no conjunto de casos proposto.

### Na demonstração

Compare os vizinhos antes e depois do treino e a perda associada a cada configuração.

### No quadro branco

Resultado observado + hipótese de causa + próximo teste

### Pergunta à turma

É correto selecionar só analogias que funcionaram?

### Resposta e transição

Não; isso esconde as limitações e impede avaliar a representação no conjunto de casos proposto.

Avance para **Monte o relatório com evidência suficiente** e relacione o resultado observado ao próximo mecanismo.

## 12. Monte o relatório com evidência suficiente

### Fala sugerida

O relatório reúne segmentações, fertilidade, projeção de custo, configuração e interpretação dos vetores. Os resultados deste navegador podem ser usados como ensaio antes da execução completa do notebook. Revise a tabela final e explique uma diferença medida usando os controles atuais. Pergunto à turma: “Qual conclusão é defensável com esta miniatura?” Uma conclusão sobre estes textos e este pequeno objetivo; generalizações para idiomas ou modelos inteiros exigem amostras e experimentos adicionais.

### Na demonstração

Revise a tabela final e explique uma diferença medida usando os controles atuais.

### No quadro branco

Dados → configuração → números → interpretação → limites

### Pergunta à turma

Qual conclusão é defensável com esta miniatura?

### Resposta e transição

Uma conclusão sobre estes textos e este pequeno objetivo; generalizações para idiomas ou modelos inteiros exigem amostras e experimentos adicionais.
