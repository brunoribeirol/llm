# Aula 29 — Síntese e fronteiras: o que permanece, o que muda

Conecte as camadas do curso a tokens visuais, difusão, dados sintéticos, roteamento e memória. Contas geométricas e modelos pequenos são explícitos; não são benchmarks.

Roteiro da demonstração interativa. Os controles mantêm os valores entre etapas; use Restaurar controles para voltar ao cenário inicial.

## Preparação

Abra a demonstração e mantenha este roteiro em outra janela ou impresso. No projetor, use Modo projeção para ocultar as notas docentes.

- **Resolução da página (DPI)**: valor inicial `96`.
- **Lado do patch (pixels)**: valor inicial `16`.
- **Redução de sequência no encoder**: valor inicial `16`.
- **Rodadas de geração / reamostragem**: valor inicial `4`.
- **Fração de dados reais (%)**: valor inicial `20`.
- **Fração enviada ao modelo maior (%)**: valor inicial `25`.

## 01. Um mapa com dois endereços

### Fala sugerida

Um repositório cheio de arquivos não garante integração. Quero apontar onde cada peça entrou no sistema. Depois quero ligar essa peça à ideia que permite depurá-la.

### Na demonstração

Escolha uma camada da tabela e explique qual evidência mostraria que ela funciona.

### No quadro branco

camada → artefato → fundamento

### Pergunta à turma

O que é uma camada órfã no mapa do projeto?

### Resposta e transição

Uma parte do sistema sem artefato verificável ou sem fundamento que a equipe consiga explicar.

Avance para **Próximo token e sistema completo** e relacione o resultado observado ao próximo mecanismo.

## 02. Próximo token e sistema completo

### Fala sugerida

A equação do próximo token continua válida para um modelo autorregressivo. Ela não descreve sozinha o produto. O sistema escolhe contexto, verifica resultados e controla ações.

### Na demonstração

Siga os dados da entrada até a resposta e localize onde entram as evidências externas.

### No quadro branco

p(token seguinte dado contexto) dentro de um sistema

### Pergunta à turma

Melhorar a perplexidade resolve automaticamente acesso a dados atuais?

### Resposta e transição

Não. Acesso, atualização, recuperação e verificação dependem também da arquitetura do sistema.

Avance para **Uma imagem também vira sequência** e relacione o resultado observado ao próximo mecanismo.

## 03. Uma imagem também vira sequência

### Fala sugerida

Uma página em branco e uma página cheia ocupam a mesma grade nesta simplificação. O número depende da resolução. Portanto, cortar em patches não é por si só comprimir conteúdo.

### Na demonstração

Mude DPI e lado do patch e observe linhas, colunas e quantidade total.

### No quadro branco

patches = floor(largura/P) × floor(altura/P)

### Pergunta à turma

Dobrar o DPI aproximadamente faz o número de patches crescer quanto?

### Resposta e transição

Cerca de quatro vezes, porque largura e altura aproximadamente dobram.

Avance para **Texto e pixels não têm custo idêntico** e relacione o resultado observado ao próximo mecanismo.

## 04. Texto e pixels não têm custo idêntico

### Fala sugerida

Não tratem um patch como se custasse exatamente um token de texto em qualquer API. Estamos comparando comprimentos de sequência num modelo simplificado. A implementação real define projeção, pooling e contabilização.

### Na demonstração

Compare os 375 tokens com a grade em diferentes resoluções.

### No quadro branco

unidades visuais brutas / unidades textuais

### Pergunta à turma

Uma sequência visual maior prova custo monetário maior em qualquer produto?

### Resposta e transição

Não. Preço e processamento dependem da arquitetura e da política de cobrança do produto.

Avance para **O encoder comprime a representação** e relacione o resultado observado ao próximo mecanismo.

## 05. O encoder comprime a representação

### Fala sugerida

O ganho surge depois da transformação do encoder. A grade sozinha não fez esse trabalho. A compressão real precisa preservar informação suficiente para a tarefa.

### Na demonstração

Aumente a redução e localize quando tokens visuais ficam abaixo de 375.

### No quadro branco

tokens visuais = ceil(patches/r)

### Pergunta à turma

Um fator maior permite afirmar melhor sistema?

### Resposta e transição

Não. Precisamos medir o que foi perdido e como essa perda afeta a tarefa.

Avance para **Compressão e fidelidade** e relacione o resultado observado ao próximo mecanismo.

## 06. Compressão e fidelidade

### Fala sugerida

Não vamos desenhar uma curva inventada e chamá-la de benchmark. Aqui a perda vem de uma regra explícita de retenção. Em OCR real, mediríamos reconstrução e desempenho nos casos de uso.

### Na demonstração

Aumente a redução e compare quantos símbolos do exemplo permanecem disponíveis.

### No quadro branco

compressão precisa vir acompanhada de qualidade

### Pergunta à turma

Reconstruir a maior parte da página garante responder uma exceção pequena?

### Resposta e transição

Não. Uma omissão rara pode conter justamente a condição decisiva para a pergunta.

Avance para **Autorregressão: ordem causal** e relacione o resultado observado ao próximo mecanismo.

## 07. Autorregressão: ordem causal

### Fala sugerida

O desenho torna a dependência visível. As posições futuras não estão prontas para serem usadas. Isso explica parte do custo sequencial de geração, embora implementações possam usar otimizações.

### Na demonstração

Aumente as rodadas e observe o prefixo que cresce da esquerda para a direita.

### No quadro branco

p(x)=∏ p(xₜ dado x₍<t₎)

### Pergunta à turma

Calcular várias posições de treino em paralelo contradiz a geração causal?

### Resposta e transição

Não. Treino com tokens conhecidos e geração de tokens ainda desconhecidos são situações diferentes.

Avance para **Difusão discreta: revelar posições** e relacione o resultado observado ao próximo mecanismo.

## 08. Difusão discreta: revelar posições

### Fala sugerida

A visualização não promete menos computação. Cada refinamento pode examinar muitas posições. O ponto é que a fatoração e o processo de geração podem mudar sem abandonar representações de tokens.

### Na demonstração

Compare as mesmas rodadas com a linha autorregressiva e veja quais posições aparecem.

### No quadro branco

sequência mascarada → refinamentos → sequência

### Pergunta à turma

Mostrar várias posições por rodada prova menor latência?

### Resposta e transição

Não. Precisamos contabilizar custo de cada rodada, quantidade de refinamentos e execução no hardware.

Avance para **Dados sintéticos e perda da cauda** e relacione o resultado observado ao próximo mecanismo.

## 09. Dados sintéticos e perda da cauda

### Fala sugerida

A cauda desaparece aqui por uma regra que podemos inspecionar. Isso ilustra um mecanismo, não prova que todo uso de dados sintéticos colapsa. Qualidade, filtragem e mistura com dados reais mudam o processo.

### Na demonstração

Reduza a fração real a zero e aumente as rodadas; acompanhe a categoria rara.

### No quadro branco

reamostragem finita pode apagar eventos raros

### Pergunta à turma

Por que mais dados sintéticos não garantem recuperar uma categoria já perdida?

### Resposta e transição

Porque amostrar de uma distribuição que atribui probabilidade zero à categoria não a recria.

Avance para **Roteamento entre modelos** e relacione o resultado observado ao próximo mecanismo.

## 10. Roteamento entre modelos

### Fala sugerida

A economia depende de quantos casos seguem cada rota. Mas o roteador também pode errar ao avaliar dificuldade. Precisamos medir qualidade por categoria junto com a fatura.

### Na demonstração

Altere a fração enviada ao maior e confira o custo médio ponderado.

### No quadro branco

E[custo] = (1−r)·1 + r·8

### Pergunta à turma

Reduzir a fração do modelo maior preserva necessariamente a qualidade?

### Resposta e transição

Não. Essa conta só descreve custo; qualidade requer avaliação das decisões de roteamento.

Avance para **FlashAttention e tráfego de memória** e relacione o resultado observado ao próximo mecanismo.

## 11. FlashAttention e tráfego de memória

### Fala sugerida

A multiplicação ainda considera relações entre posições. O ganho vem de organizar onde os dados ficam e quando são lidos. Confundir isso com atenção esparsa leva a uma explicação errada.

### Na demonstração

Compare a matriz de scores conceitual com o processamento em blocos.

### No quadro branco

menos tráfego de memória ≠ menos pares QK

### Pergunta à turma

FlashAttention precisa descartar pares de atenção para economizar memória?

### Resposta e transição

Não. Sua estratégia central é o cálculo em blocos com redução de tráfego e sem materializar toda a matriz de scores.

Avance para **A última avaliação continua sendo sua** e relacione o resultado observado ao próximo mecanismo.

## 12. A última avaliação continua sendo sua

### Fala sugerida

Uma novidade técnica muda o que precisamos medir. Ela não nos dispensa de medir. Usem o mapa para explicar qual pressuposto mudou e qual fundamento permanece útil.

### Na demonstração

Escolha uma fronteira e diga qual caso do harness precisaria mudar para avaliá-la.

### No quadro branco

nova hipótese → novo teste → mesma disciplina de evidência

### Pergunta à turma

Qual habilidade permanece útil quando as ferramentas mudam?

### Resposta e transição

Decompor o sistema, formular hipóteses verificáveis e construir experimentos que localizem falhas e limites.
