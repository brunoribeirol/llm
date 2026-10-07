"""Authored teaching maps shared by the portal and its offline demonstrations.

Overview arrows denote a learning path. Mechanism maps describe data movement,
parallel branches and explicit return conditions instead. No external renderer.
"""
from html import escape
import json
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parent

# One explanation per phase of each existing demonstration (same focus indices).
PHASES = {
    0: ["Reconheça o que já sabe e o que precisa revisar.", "Localize fundamentos, treinamento e sistemas no curso.", "Confira avaliação, entregas e regras de uso de IA.", "Escolha guia, demonstração ou código pela dúvida.", "Prepare dependências e execute um exemplo pequeno.", "Registre uma hipótese e a evidência que vai procurar."],
    1: ["Defina entrada, saída e critério de sucesso da tarefa.", "Compare previsões com referências no mesmo conjunto.", "Conte verdadeiros e falsos positivos e negativos.", "Escolha a métrica considerando o custo de cada erro.", "Examine sobreposição e surpresa na geração de texto.", "Declare denominadores e limites antes de concluir."],
    2: ["Fixe texto e normalização antes de comparar.", "Escolha a unidade inicial: palavras, caracteres ou bytes.", "Conte pares adjacentes no corpus de treinamento.", "Aprenda fusões; na aplicação, reutilize a ordem aprendida.", "Mapeie peças para IDs e confira a reconstrução.", "Meça tokens por texto e impacto na janela e no custo."],
    3: ["Identifique o limite de índices e representações one-hot.", "Extraia coocorrências em janelas de contexto.", "Compare vetores por cosseno ou produto interno.", "Use uma tarefa-proxy para aprender representações.", "Ordene vizinhos com a régua escolhida.", "Teste polissemia, analogias e efeitos do corpus."],
    4: ["Formule uma comparação que possa ser refutada.", "Segmente os mesmos textos com configurações fixas.", "Calcule fertilidade e razão de custo entre textos.", "Aprenda embeddings com pares positivos e negativos.", "Inspecione vizinhos; projeções não preservam tudo.", "Entregue configuração, resultados e análise de falhas."],
    5: ["Leia tokens na ordem e compare sequências.", "Atualize o estado recorrente a cada entrada.", "Examine os produtos que podem sumir ou explodir.", "Observe o caminho aditivo e as portas do LSTM.", "Consulte estados do encoder por atenção a cada passo.", "Separe problemas de memória, acesso e paralelismo."],
    6: ["Converta tokens em vetores e represente suas posições.", "Projete a entrada em queries, keys e values.", "Calcule scores, aplique escala e a máscara adequada.", "Normalize scores e combine os values.", "Una cabeças e aplique os subblocos com residuais.", "Projete para logits e escolha o próximo token."],
    7: ["Teste o que acontece quando a ordem muda.", "Compare códigos posicionais somados à entrada.", "Aplique RoPE a Q e K para alterar os scores.", "Preserve um caminho de soma entre subblocos.", "Compare LayerNorm, RMSNorm e posição da norma.", "Transforme cada posição e reconstrua o bloco."],
    8: ["Defina quais posições podem consultar quais outras.", "Relacione máscara e objetivo de aprendizagem.", "Escolha encoder, decoder ou encoder–decoder pela tarefa.", "Conte K e V armazenados durante a geração.", "Compare janela local, compartilhamento de KV e destilação.", "Use tarefa, memória e latência para justificar a escolha."],
    9: ["Construa entradas e alvos deslocados de um token.", "Confira dimensões e projeções de cada cabeça.", "Oculte posições futuras antes do softmax.", "Combine atenção, FFN, normalizações e residuais.", "Meça entropia cruzada e atualize pesos no treino.", "Avalie em dados separados e gere token por token."],
    10: ["Relacione parâmetros, tokens e orçamento de treino.", "Roteie tokens para alguns especialistas e meça carga.", "Leia os scores de saída antes da seleção.", "Compare greedy, beam e amostragem com filtros.", "Expresse tarefa, contexto e exemplos na entrada.", "Separe gargalos de prefill, decode e memória."],
    11: ["Fixe candidatos e scores para uma comparação justa.", "Reescale os logits e observe a concentração.", "Restrinja candidatos por quantidade ou massa.", "Use uma semente e registre o token selecionado.", "Varie instruções e exemplos mantendo os testes.", "Compare qualidade, diversidade e custo de saída."],
    12: ["Selecione, filtre e deduplique os dados.", "O próximo token do próprio texto fornece o alvo.", "Relacione tamanho do modelo, tokens e FLOPs.", "Some pesos, ativações, gradientes e otimizador.", "Distribua dados, tensores ou estágios conforme o gargalo.", "Valide o completador e registre os limites do treino."],
    13: ["Defina o comportamento que precisa mudar.", "Formate diálogos e selecione os tokens supervisionados.", "Compare capacidade e formato em dados separados.", "Treine uma atualização de baixo posto sobre a base.", "Separe a base quantizada dos adaptadores treináveis.", "Avalie se adaptação resolve o problema observado."],
    14: ["Verifique memória e registre a configuração.", "Salve respostas do modelo antes da adaptação.", "Separe treino, validação e conjunto de controle.", "Configure matrizes de baixo posto e pesos congelados.", "Acompanhe perda e gradientes durante o ajuste.", "Compare antes/depois e empacote base, adaptador e dados."],
    15: ["Colete pares de respostas preferida e rejeitada.", "No RLHF, aprenda um sinal de preferência aproximado.", "Ajuste a distribuição de respostas usando esse sinal.", "Controle o afastamento da política de referência.", "Investigue otimização do proxy e reward hacking.", "Compare a rota direta de DPO com a rota de RLHF."],
    16: ["Gere várias soluções para o mesmo problema.", "Distinga acerto em uma tentativa e em um conjunto.", "Separe gerar candidatos de escolher a resposta final.", "Use critérios externos para conferir candidatos.", "Compare recompensas dentro do grupo para o treino.", "Declare custo, correlação e limites do verificador."],
    17: ["Revise tokenização e representação vetorial.", "Reconstrua scores, máscara e mistura de valores.", "Explique como logits se tornam uma sequência.", "Relacione dados, objetivo, memória e orçamento.", "Diferencie SFT, adaptadores e preferências.", "Defenda um diagnóstico com um teste e sua evidência."],
    18: ["Selecione fontes e preserve identidade e versão.", "Fragmente com tamanho, sobreposição e metadados.", "Represente fragmentos no espaço de embeddings.", "Armazene vetores associados aos textos de origem.", "Represente a consulta e recupere candidatos relevantes.", "Monte contexto, gere e confira o suporte das citações."],
    19: ["Identifique termos exatos e intenção da pergunta.", "Recupere candidatos por correspondência lexical.", "Recupere outros candidatos por proximidade vetorial.", "Combine rankings por posição, como no RRF.", "Reordene o conjunto recuperado com consulta e documento.", "Meça recall, precisão e qualidade da ordem."],
    20: ["Fragmente o corpus preservando metadados.", "Indexe embeddings e teste a busca densa.", "Adicione busca lexical e funda os rankings.", "Reordene candidatos e conte o trabalho extra.", "Responda com os trechos selecionados e suas fontes.", "Compare estratégias nas mesmas consultas e reporte falhas."],
    21: ["Reconheça quando a tarefa requer uma ferramenta.", "Descreva nome, parâmetros e restrições no schema.", "O modelo propõe nome e argumentos para a chamada.", "O host valida, autoriza e executa a função.", "A observação retorna ao contexto do modelo.", "No MCP, separe os papéis de host, cliente e servidor."],
    22: ["Faça schemas e registro de funções concordarem.", "Trate JSON malformado e argumentos inválidos.", "Execute chamadas e devolva observações ao modelo.", "Limite passos, custo e crescimento do contexto.", "Inicialize, descubra e chame ferramentas no servidor.", "Entregue uma integração que possa ser reproduzida."],
    23: ["Defina resultado esperado e critério de sucesso.", "Decomponha a tarefa usando o estado observado.", "Valide e execute uma ação por ferramenta.", "Registre observações úteis para a próxima decisão.", "Confira o resultado com evidência externa.", "Finalize por sucesso, limite ou falta de condição."],
    24: ["Caracterize a tarefa e o limite de um único agente.", "Separe responsabilidades com entradas e saídas claras.", "Escolha orquestrador, pipeline, debate ou painel.", "Some trabalho e identifique o caminho de maior latência.", "Verifique resultados e propagação de erro.", "Compare com uma arquitetura mais simples sob o mesmo teste."],
    25: ["Defina formato de ação, observação e resposta final.", "Valide a proposta antes de selecionar uma função.", "Integre busca e cálculo com contratos explícitos.", "Mantenha estado e orçamento entre iterações.", "Registre chamadas, erros, observações e custos.", "Compare implementação manual e framework nos mesmos casos."],
    26: ["Identifique pedido legítimo e conteúdo externo.", "Recupere evidências preservando sua origem.", "Separe dados consultados das instruções do sistema.", "Verifique escopo, reversibilidade e autorização da ação.", "Registre a execução e localize a primeira divergência.", "Meça sucesso, falhas e consequências por etapa."],
    27: ["Localize a camada que está sendo avaliada.", "Fixe casos, categorias e tamanho da amostra.", "Defina critérios observáveis e seus níveis.", "Aplique avaliação humana ou automatizada.", "Compare com humanos e teste ordem e vieses.", "Escolha com incerteza, custo e restrições explícitos."],
    28: ["Conecte o sistema por uma interface de entrada e saída.", "Construa casos que exponham diferenças e falhas.", "Meça o conjunto recuperado antes da resposta.", "Aplique critérios separados à saída do sistema.", "Confira concordância com julgamentos de referência.", "Reporte por categoria e priorize correções reproduzíveis."],
    29: ["Relacione as peças construídas ao longo do curso.", "Compare representações de texto e imagem.", "Investigue o compromisso entre compressão e fidelidade.", "Compare geração causal e revelação de posições.", "Observe o efeito de dados sintéticos sobre a cauda.", "Meça roteamento, tráfego de memória e qualidade final."],
    30: ["Apresente o usuário e o problema concreto.", "Vincule cada componente a uma decisão justificada.", "Mostre uma execução e sua evidência.", "Reporte resultados com denominadores e protocolo.", "Declare uma falha que afete o uso do sistema.", "Entregue artefatos e sustente suas escolhas na discussão."],
}


def node(title, text, branches=(), note=""):
    return {"title": title, "text": text, "branches": list(branches), "note": note}


def chart(title, lead, stages, output):
    return {"title": title, "lead": lead, "stages": stages, "output": output}


# These diagrams are manually authored; matching only chooses where to show them.
MECHANISMS = {
    "bpe": chart("BPE: aprender e depois aplicar", "Duas fases distintas compartilham um vocabulário e uma ordem de fusões.", [
        node("Preparar o corpus", "Normalize conforme o tokenizador e forme as unidades iniciais."),
        node("Contar pares", "Conte ocorrências de unidades adjacentes no corpus de treino."),
        node("Fundir o par escolhido", "Registre a fusão e atualize a segmentação.", note="↺ Enquanto houver orçamento de vocabulário, volte à contagem de pares."),
        node("Congelar o tokenizador", "Guarde vocabulário, regras de normalização e lista ordenada de merges."),
        node("Aplicar a um texto novo", "Use as regras aprendidas para segmentar o texto e produzir IDs.")
    ], "Saída: sequência de IDs; a aplicação não aprende novas fusões."),
    "attention": chart("Self-attention: da entrada ao contexto", "Fluxo de dados de uma cabeça de atenção; a máscara depende da arquitetura.", [
        node("Projetar a entrada X", "Três projeções aprendidas operam sobre os mesmos vetores.", ["Q = XWq · consultas", "K = XWk · chaves", "V = XWv · valores"]),
        node("Comparar Q com K", "Calcule QKᵀ e divida por √dₖ para controlar a escala dos scores."),
        node("Aplicar a máscara", "Em atenção causal, posições futuras recebem −∞ antes da normalização."),
        node("Normalizar por linha", "Softmax converte scores permitidos em pesos que somam 1."),
        node("Combinar valores", "Multiplique os pesos por V; cada posição recebe uma mistura contextual.")
    ], "Saída: representações contextuais. Multi-head concatena várias cabeças e aplica uma projeção."),
    "block": chart("Bloco Transformer com pré-normalização", "Duas transformações com caminhos residuais; esta é uma variante específica do bloco.", [
        node("Receber X", "A representação de posição deve estar incorporada à entrada ou à atenção."),
        node("Normalizar e atender", "A atenção lê a versão normalizada; o residual preserva X.", ["Atenção(Norm(X))", "Atalho: X"]),
        node("Primeira soma", "H = X + Atenção(Norm(X))."),
        node("Normalizar e transformar", "A FFN opera em cada posição; outro residual preserva H.", ["FFN(Norm(H))", "Atalho: H"]),
        node("Segunda soma", "Y = H + FFN(Norm(H)); envie Y ao próximo bloco.")
    ], "Saída: vetores com a mesma dimensão residual, prontos para a próxima camada."),
    "decode": chart("Geração autorregressiva", "Um passo escolhe um token; a sequência nasce da repetição controlada.", [
        node("Processar o contexto", "Tokenize o prompt e calcule representações; quando disponível, mantenha K e V em cache."),
        node("Obter logits", "A projeção de saída produz um score para cada token do vocabulário."),
        node("Escolher a estratégia", "A estratégia determina como os scores viram uma escolha.", ["Greedy: maior score", "Amostragem: temperatura e filtros"]),
        node("Acrescentar o token", "Anexe o token escolhido ao contexto e atualize o estado de geração."),
        node("Verificar a parada", "O token de fim ou o limite de saída foi atingido?", ["Sim → devolver sequência", "Não → próximo passo do modelo"], "↺ Sem parada, volte a obter os logits para a próxima posição.")
    ], "Saída: continuação gerada. Parâmetros de amostragem não atualizam os pesos."),
    "training": chart("Treinamento por próximo token", "O texto fornece os alvos; validação e teste permanecem separados do treino.", [
        node("Preparar dados e partições", "Filtre e deduplique; separe documentos antes de construir exemplos sobrepostos."),
        node("Deslocar o alvo", "Entrada: tokens até t. Alvo correspondente: token em t + 1."),
        node("Executar o modelo", "A máscara causal impede acesso aos tokens futuros."),
        node("Calcular perda e gradientes", "Compare logits com alvos por entropia cruzada e aplique backpropagation."),
        node("Atualizar pesos", "O otimizador usa os gradientes; confira desempenho em validação.", note="↺ Repita com novos lotes até o critério de parada; teste fica para a avaliação final.")
    ], "Saída: pesos ajustados e métricas em dados separados."),
    "lora": chart("LoRA: dois caminhos, uma saída", "A base preserva seus pesos; o caminho de baixo posto aprende uma atualização.", [
        node("Receber a ativação x", "A mesma entrada alimenta dois caminhos.", ["Base congelada: Wx", "Adaptador: B(Ax) · α/r"]),
        node("Somar as contribuições", "y = Wx + (α/r)B(Ax). O posto r limita a dimensão intermediária."),
        node("Calcular a perda da tarefa", "No SFT, supervisione os tokens definidos pelo template e pela máscara de loss."),
        node("Atualizar os adaptadores", "Os gradientes ajustam A e B; W permanece congelada.", note="↺ Repita por lotes; compare com a base nos mesmos casos de avaliação."),
        node("Salvar e avaliar", "Registre adaptador, identificação da base e configuração de inferência.")
    ], "QLoRA mantém a base quantizada e adaptações treináveis; armazenamento e cálculo têm papéis distintos."),
    "preference": chart("Preferências: duas rotas de ajuste", "RLHF e DPO usam comparações de respostas, mas organizam o treinamento de formas diferentes.", [
        node("Coletar comparações", "Para cada prompt, registre uma resposta preferida e uma rejeitada."),
        node("Escolher a rota", "Os caminhos abaixo são alternativas, não etapas consecutivas.", ["RLHF → treinar modelo de recompensa → otimizar política com referência", "DPO → otimizar diretamente os pares em relação à referência"]),
        node("Avaliar o comportamento", "Teste qualidade, capacidade e desvios em casos separados dos pares de treino."),
        node("Investigar efeitos do sinal", "Confira se o modelo aprendeu o comportamento desejado ou explorou o critério.")
    ], "Saída: política ajustada; melhorar o objetivo de preferência não garante todos os critérios de qualidade."),
    "rag": chart("RAG: do acervo à resposta com fontes", "A preparação do acervo acontece antes da consulta; os pesos do gerador podem permanecer fixos.", [
        node("Preparar as fontes", "Filtre o acervo e preserve ID, seção e versão dos documentos."),
        node("Construir o índice", "Divida em chunks e associe texto, metadados e embeddings."),
        node("Receber uma pergunta", "Represente a consulta e recupere candidatos no índice."),
        node("Selecionar contexto", "Reordene quando necessário e respeite o orçamento de contexto."),
        node("Verificar evidência disponível", "Há trechos suficientes para sustentar a resposta?", ["Sim → gerar resposta e indicar fontes", "Não → declarar a limitação ou buscar mais evidência"]),
        node("Conferir o suporte", "Compare afirmações e citações com os trechos realmente recuperados.")
    ], "Saída: resposta verificável ou limitação explícita. Recuperar uma fonte não garante uso correto."),
    "hybrid": chart("Busca híbrida: ramificar, fundir, reordenar", "Dois recuperadores buscam candidatos de formas complementares.", [
        node("Receber a consulta", "Use a mesma pergunta nos dois caminhos.", ["Busca lexical · BM25", "Busca densa · embeddings"]),
        node("Fundir os rankings", "RRF combina posições, evitando somar scores de escalas incompatíveis."),
        node("Reordenar candidatos", "Um cross-encoder pode avaliar consulta e documento juntos; só reordena o que chegou."),
        node("Selecionar top-k", "Envie os trechos escolhidos ao contexto do gerador."),
        node("Medir cada estágio", "Recall mede cobertura; precisão e nDCG ajudam a avaliar seleção e ordem.")
    ], "Se um documento não entrou no conjunto candidato, o reranker não consegue recuperá-lo."),
    "tools": chart("Tool calling: proposta, execução e retorno", "Modelo, host e ferramenta têm responsabilidades diferentes.", [
        node("Apresentar ferramentas", "O host fornece schemas e contexto ao modelo."),
        node("Propor uma chamada", "O modelo emite nome e argumentos estruturados."),
        node("Validar no host", "Confira formato, tipos, função registrada e permissões.", ["Inválida → observação de erro; não executar", "Válida → executar a função autorizada"]),
        node("Devolver a observação", "Anexe resultado ou erro à conversa com identificação da chamada."),
        node("Decidir o próximo passo", "O modelo usa a observação para responder ou solicitar outra chamada.", note="↺ Nova chamada volta à validação, respeitando orçamento e condições de parada.")
    ], "A ferramenta é executada pelo host; texto produzido pelo modelo não é prova de execução."),
    "agent": chart("Agente: um ciclo com verificação e parada", "Cada volta combina estado, decisão, ação e evidência.", [
        node("Ler objetivo e estado", "Defina sucesso, permissões e limites de passos, tempo ou custo."),
        node("Planejar a próxima ação", "Use observações anteriores para escolher uma ação ou finalizar."),
        node("Validar e executar", "O host confere argumentos e permissão antes de chamar a ferramenta."),
        node("Registrar a observação", "Atualize a memória com o que aconteceu, incluindo erros."),
        node("Verificar o resultado", "O objetivo foi atendido e há evidência suficiente?", ["Sim → finalizar com evidências", "Não, há orçamento → revisar o plano", "Não, limite atingido → encerrar com limitações"], "↺ Uma nova tentativa retorna ao planejamento, usando a observação obtida.")
    ], "Saída: resultado acompanhado da trajetória ou uma parada justificada."),
    "multi": chart("Orquestrador e trabalhadores", "Só tarefas independentes podem avançar em paralelo; dependências precisam ser respeitadas.", [
        node("Decompor a tarefa", "O orquestrador define responsabilidades, contratos e orçamento compartilhado."),
        node("Distribuir trabalho independente", "Cada trabalhador recebe o contexto necessário.", ["Trabalhador A → resultado A", "Trabalhador B → resultado B", "Trabalhador C → resultado C"]),
        node("Reunir e verificar", "Cheque consistência, origem e suficiência dos resultados antes de compor."),
        node("Resolver lacunas", "Se houver falha, replaneje dentro do orçamento; caso contrário, finalize.", note="↺ Repetições também consomem o orçamento compartilhado."),
        node("Comparar arquiteturas", "Meça qualidade, custo total e caminho crítico contra uma solução de referência.")
    ], "Custo soma trabalho; latência depende de paralelismo, dependências e coordenação."),
    "evaluation": chart("Avaliação: do caso à decisão", "Meça a camada responsável e mantenha o protocolo visível.", [
        node("Fixar casos e critérios", "Defina categorias, referências, rubrica e restrições do uso."),
        node("Executar e registrar", "Guarde entradas, respostas, fontes e trajetória quando houver ferramentas."),
        node("Medir por camada", "Evite atribuir ao gerador uma falha anterior de recuperação.", ["Recuperação → cobertura e ordem", "Resposta → critérios da rubrica", "Ações → sucesso, custo e falhas"]),
        node("Calibrar o julgamento", "Compare com humanos; confira concordância e vieses de ordem quando usar juiz automatizado."),
        node("Decidir e repetir", "Reporte denominadores e incerteza; priorize uma correção e reexecute os mesmos casos.", note="↺ Após a correção, volte à execução para medir regressões e ganhos.")
    ], "Saída: comparação reproduzível, com limites e prioridades de melhoria."),
}

MECHANISMS.update({
    "seq2seq": chart("Encoder–decoder: dois caminhos se encontram", "A fonte e o prefixo do alvo têm representações próprias; a cross-attention liga os caminhos.", [
        node("Representar as entradas", "Converta tokens em embeddings e incorpore posição.", ["Fonte → entrada do encoder", "Prefixo do alvo → entrada do decoder"]),
        node("Codificar a fonte", "A pilha encoder combina posições da fonte e fornece representações contextuais."),
        node("Processar o prefixo", "Self-attention causal no decoder só consulta posições permitidas do alvo."),
        node("Consultar a fonte", "Na cross-attention, Q vem do decoder; K e V vêm das representações do encoder.", ["Decoder → queries", "Encoder → keys e values"]),
        node("Produzir o próximo token", "O decoder transforma os estados; a cabeça de saída produz logits sobre o vocabulário.", note="↺ Na geração, acrescente o token ao prefixo e repita no decoder. Reutilize a fonte codificada.")
    ], "A fonte representada informa a previsão; o encoder não entrega uma tradução pronta ao decoder."),
    "postblock": chart("Bloco encoder com pós-normalização", "Ordem do bloco do Transformer original: atenção e FFN têm residuais e normalizações próprios.", [
        node("Receber X e calcular atenção", "A entrada também segue pelo caminho residual.", ["MultiHead(X)", "Atalho: X"]),
        node("Somar e normalizar", "H = LayerNorm(X + MultiHead(X))."),
        node("Aplicar a FFN", "Transforme cada posição e preserve H para o segundo residual.", ["FFN(H)", "Atalho: H"]),
        node("Somar e normalizar novamente", "Y = LayerNorm(H + FFN(H))."),
        node("Passar à próxima camada", "A pilha repete a estrutura com parâmetros próprios de cada camada.")
    ], "Pré-normalização muda a ordem das operações; compare as fórmulas antes de misturar as variantes."),
    "classification": chart("Classificação: das previsões à métrica", "Uma taxa só pode ser interpretada junto da tarefa, da amostra e do custo dos erros.", [
        node("Fixar casos e referências", "Use um conjunto com rótulos conhecidos e descreva a distribuição das classes."),
        node("Produzir previsões", "Aplique o modelo e o limiar escolhido aos mesmos casos."),
        node("Cruzar previsão e referência", "Conte cada caso em uma das quatro situações.", ["VP e VN → acertos", "FP → alarme indevido", "FN → caso positivo perdido"]),
        node("Calcular as métricas", "Precisão = VP/(VP+FP); revocação = VP/(VP+FN). Confira denominadores nulos antes de calcular."),
        node("Escolher pelo uso", "Compare acurácia e F₁ com a distribuição de classes e com o custo de FP e FN.")
    ], "Saída: uma decisão justificada; acurácia alta pode esconder uma classe ignorada."),
    "embeddings": chart("Embeddings: aprender relações e buscar vizinhos", "O treinamento aprende a representação; a busca usa os vetores resultantes.", [
        node("Extrair janelas do corpus", "A proximidade no texto cria exemplos de contexto."),
        node("Definir a tarefa-proxy", "CBOW e skip-gram organizam a previsão em sentidos diferentes.", ["CBOW: contexto → palavra central", "Skip-gram: palavra central → contexto"]),
        node("Aprender vetores", "Calcule a perda da tarefa e atualize representações; amostragem negativa compara pares observados com negativos.", note="↺ Repita em exemplos do corpus; frequência e cobertura influenciam o espaço."),
        node("Comparar representações", "Use cosseno ou outra medida compatível com os vetores."),
        node("Inspecionar vizinhos", "Ordene similaridades e teste palavras ambíguas, analogias e falhas.")
    ], "Saída: vizinhança vetorial; proximidade não é garantia de verdade nem de um único sentido."),
    "recurrence": chart("Recorrência e acesso por atenção", "O estado percorre a sequência; a atenção permite consultar estados anteriores diretamente.", [
        node("Receber xₜ e hₜ₋₁", "O próximo estado depende da entrada atual e do estado anterior."),
        node("Atualizar a memória", "Na RNN simples, hₜ = f(Wxₜ + Uhₜ₋₁). No LSTM, portas controlam um caminho aditivo.", note="↺ Repita para o próximo token; o gradiente atravessa essas dependências no treino."),
        node("Preservar estados do encoder", "Com atenção, mantenha representações das posições de origem."),
        node("Consultar a origem", "O estado do decoder gera scores de alinhamento; softmax produz pesos."),
        node("Combinar e prever", "A soma ponderada dos estados fornece um contexto para o passo do decoder.")
    ], "Atenção reduz o gargalo de um contexto fixo; uma rede recorrente ainda tem dependência sequencial."),
    "rope": chart("RoPE: posição dentro do score", "A posição modifica queries e keys em pares de componentes.", [
        node("Projetar Q e K", "Produza os vetores a partir das representações de entrada."),
        node("Formar pares de componentes", "Cada par usa uma frequência de rotação."),
        node("Rotacionar pela posição", "Aplique ângulos proporcionais à posição de cada token.", ["Query na posição m → Rₘq", "Key na posição n → Rₙk"]),
        node("Calcular o produto interno", "As rotações introduzem a distância relativa m−n na interação entre Q e K."),
        node("Continuar a atenção", "Aplique escala, máscara, softmax e combinação de V.")
    ], "A fórmula aceita posições adicionais; isso não garante desempenho além do contexto de treinamento."),
    "moe": chart("MoE: rotear e combinar especialistas", "Uma camada esparsa ativa apenas parte dos especialistas por token.", [
        node("Receber representações", "Cada token chega à camada com seu vetor de ativação."),
        node("Calcular pesos de roteamento", "O roteador atribui scores aos especialistas disponíveis."),
        node("Selecionar top-k", "Despache o token aos especialistas escolhidos, respeitando a política de capacidade.", ["Especialista escolhido A → FFN A", "Especialista escolhido B → FFN B"]),
        node("Combinar saídas", "Use os pesos do roteador para reunir as contribuições dos especialistas ativos."),
        node("Medir carga e custo", "Confira desequilíbrio, capacidade e trabalho realmente ativado.")
    ], "Parâmetros totais e parâmetros ativos são medidas distintas; mais especialistas não significa ativar todos."),
    "kv": chart("KV cache: reutilizar o passado", "O cache evita recalcular keys e values antigos na geração causal.", [
        node("Prefill do prompt", "Processe os tokens iniciais e armazene K e V de cada camada."),
        node("Processar um novo token", "Calcule Q, K e V para a nova posição."),
        node("Acrescentar K e V ao cache", "Preserve o histórico que permanece dentro da política de contexto."),
        node("Atender ao contexto disponível", "A nova query consulta as keys e values armazenadas."),
        node("Escolher o próximo token", "Produza logits e aplique a estratégia de decodificação.", note="↺ Se a geração continuar, volte ao processamento do novo token.")
    ], "O cache cresce com posições, camadas, cabeças KV e tamanho dos elementos; MQA/GQA reduzem cabeças KV."),
    "reasoning": chart("Tentativas, seleção e recompensa verificável", "Gerar uma solução correta e conseguir selecioná-la são problemas diferentes.", [
        node("Definir problema e verificação", "Escolha um critério externo, como testes executáveis ou resposta conferível."),
        node("Gerar um grupo de respostas", "Use o mesmo problema e registre custo e configuração de cada tentativa.", ["Tentativa 1", "Tentativa 2", "Tentativa … k"]),
        node("Verificar e atribuir sinal", "Avalie candidatos pelo critério escolhido; o verificador também pode falhar."),
        node("Distinguir seleção de treino", "As rotas têm finalidades diferentes.", ["Inferência → selecionar uma resposta pelos sinais disponíveis", "GRPO → comparar recompensas no grupo e ajustar a política"]),
        node("Medir o resultado entregue", "Reporte acerto, orçamento e limitações; pass@k não é a taxa de acerto do seletor.")
    ], "Mais tentativas aumentam trabalho; candidatos correlacionados e critérios frágeis limitam o ganho."),
    "mcp": chart("MCP: conectar, descobrir e chamar", "Papéis e troca de mensagens em uma integração com ferramentas.", [
        node("Abrir a conexão", "O host usa um cliente para se comunicar com o servidor MCP.", ["Host → cliente MCP", "Cliente MCP ↔ servidor MCP"]),
        node("Inicializar a sessão", "Cliente e servidor estabelecem capacidades da conexão."),
        node("Descobrir ferramentas", "O cliente obtém nomes, descrições e schemas expostos pelo servidor."),
        node("Solicitar uma chamada", "O host valida a decisão e o cliente envia nome e argumentos ao servidor."),
        node("Retornar o resultado", "O servidor executa a ferramenta; o resultado volta pelo cliente ao host.")
    ], "O protocolo conecta componentes; autorização e uso do resultado continuam sendo responsabilidades do sistema."),
    "security": chart("Entrada externa até uma ação autorizada", "Cada transição preserva a diferença entre conteúdo consultado e instrução válida.", [
        node("Identificar a origem", "Distinga pedido do usuário, documentos recuperados e respostas de ferramentas."),
        node("Interpretar como evidência", "Conteúdo externo pode informar a tarefa; ordens dentro dele não ganham autoridade."),
        node("Validar a ação proposta", "Confira argumentos, destino, escopo e permissões no host."),
        node("Aplicar a política de execução", "A decisão depende das permissões e do impacto da ação.", ["Fora do escopo → bloquear", "Exige revisão → aguardar decisão humana", "Autorizada → executar e registrar"]),
        node("Auditar a trajetória", "Localize a primeira divergência e avalie consequências, não apenas a resposta final.")
    ], "Defesas reduzem riscos em camadas; delimitar texto por si só não garante isolamento."),
    "multimodal": chart("Uma imagem como sequência de representações", "Este percurso ilustra o uso de patches em um encoder visual.", [
        node("Preparar a imagem", "Fixe resolução e pré-processamento usados pelo modelo."),
        node("Dividir em patches", "Separe regiões de tamanho definido; a resolução influencia a quantidade."),
        node("Projetar os patches", "Transforme cada região em um vetor e represente sua posição."),
        node("Processar no encoder", "Atenção combina informações entre as representações visuais."),
        node("Adaptar à tarefa", "Use uma cabeça de tarefa ou uma interface com o modelo de linguagem, conforme a arquitetura.")
    ], "Patches não equivalem diretamente a tokens de texto; compare custo e fidelidade na arquitetura escolhida."),
    "lab": chart("Laboratório: da hipótese à evidência", "Um protocolo de comparação que pode ser reproduzido.", [
        node("Definir hipótese e critério", "Escreva o que espera observar e o que contrariaria sua hipótese."),
        node("Preparar dados e ambiente", "Registre versões, configuração e partições usadas."),
        node("Executar uma referência", "Guarde o resultado inicial antes de alterar o sistema."),
        node("Alterar uma condição", "Compare sobre os mesmos casos e registre a variável alterada."),
        node("Conferir e relatar", "Apresente resultados, falhas e limites com os arquivos necessários para repetir.", note="↺ Se a comparação não responder à hipótese, revise o experimento e execute novamente.")
    ], "Entregável: configuração, evidências e interpretação; seguir checkpoints não substitui analisar o resultado."),
    "project": chart("Projeto: do problema à defesa", "Conecte a necessidade do usuário à evidência apresentada.", [
        node("Delimitar o problema", "Escolha usuário, escopo e critério de sucesso."),
        node("Justificar a arquitetura", "Explique a função de cada componente e a necessidade de fontes ou ferramentas."),
        node("Demonstrar uma execução", "Mostre entradas, evidências e resultado em um caso relevante."),
        node("Apresentar avaliação", "Declare casos, métricas, rubrica, denominadores e limitações."),
        node("Defender e permitir reprodução", "Relacione escolhas aos resultados e entregue os artefatos pedidos.")
    ], "Uma apresentação convincente permite conferir como o resultado foi obtido."),
})

# Lesson-scoped title fragments, deliberately excluding teacher-only answers.
RULES = [
    ("classification", {1, 27}, ("confusao", "matriz", "acuracia", "precisao", "revocacao", "f₁", "f1", "harmonica", "fraude")),
    ("embeddings", {3, 4}, ("vetor", "vetores", "embedding", "word2vec", "cbow", "skip-gram", "amostragem negativa", "contextos", "vizinhos", "geometr", "cosseno", "one-hot", "distribucional", "pca", "t-sne", "analogia")),
    ("recurrence", {5}, ("recorr", "estado", "gradiente", "lstm", "contexto fixo", "compressao", "memoria", "esquece", "resumo", "sequencial")),
    ("rope", {7}, ("rope", "rotac", "rotacion", "gire", "distancia relativa", "dentro do score")),
    ("seq2seq", {6, 8}, ("encoder-decoder", "encoder–decoder", "encoder, decoder", "cross-attention", "entrada e saida separadas")),
    ("moe", {10}, ("moe", "especialista", "rotea", "carga", "parametros totais", "parametros ativos")),
    ("kv", {6, 8, 10}, ("kv cache", "kv-cache", "mqa", "gqa", "compartilhe k", "trabalho repetido")),
    ("reasoning", {16}, ("tentativa", "pass@", "consenso", "verific", "recompensa", "grpo", "grupo", "seletor", "candidatos", "receita", "comprimento", "independencia")),
    ("mcp", {21, 22}, ("mcp", "host, cliente", "inicializar", "descoberta", "protocolo", "n×m", "integracoes")),
    ("security", {19, 26}, ("injec", "envenen", "exfiltra", "irrevers", "mitiga", "permiss", "fronteira", "instruc", "documento", "revisao humana", "recuperar nao")),
    ("multimodal", {29}, ("imagem", "patch", "vit", "pixels", "ocr", "encoder comprime")),
    ("project", {18, 22, 26, 30}, ("projeto", "entrega", "arquitetura", "criterios", "defender", "defesa", "reproduzivel", "problema", "limitacao", "doze minutos", "execucao")),
    ("bpe", {2, 4}, ("bpe", "merge", "fusao", "pares adjacentes")),
    ("attention", {5, 6, 9, 17}, ("q, k", "qkv", "atencao", "attention", "scores", "mascara", "softmax", "misture", "soma de cada linha")),
    ("block", {6, 7, 9}, ("bloco", "residual", "norma", "ffn", "pesos")),
    ("decode", {6, 8, 9, 10, 11, 17, 29}, ("geracao", "gerar", "decod", "logits", "temperatura", "top-k", "top-p", "amostr", "greedy", "beam", "autorregress", "cache", "token por token")),
    ("training", {9, 12, 17}, ("trein", "alvo", "corpus", "supervis", "loss", "perda", "gradiente")),
    ("lora", {13, 14, 17}, ("lora", "adaptador", "baixo posto", "atualizacao", "quantiz", "gradiente", "treinaveis", "fusao")),
    ("preference", {15, 17}, ("preferencia", "recompensa", "rlhf", "dpo", "ppo", "politica", "proxy", "objetivo")),
    ("rag", {18, 20}, ("rag", "fonte", "chunk", "fragment", "contexto", "respost", "cita", "corpus", "ingest")),
    ("hybrid", {19, 20}, ("bm25", "lexical", "denso", "densa", "hibrid", "fusao", "rrf", "rerank", "reorden", "encoder", "recall", "ranking")),
    ("tools", {21, 22, 25}, ("chamada", "schema", "valid", "parsing", "parser", "despacho", "ferramenta", "loop", "host", "resultado")),
    ("agent", {23, 25, 26}, ("loop", "ciclo", "plano", "planej", "memoria", "observa", "acao", "parada", "trajetoria", "while", "verifica", "autocorrec")),
    ("multi", {24}, ("orquestra", "trabalhador", "coorden", "paralel", "custo", "contexto", "orcamento")),
    ("evaluation", {26, 27, 28, 30}, ("avalia", "metric", "rubrica", "juiz", "calibr", "kappa", "concord", "denominador", "relatorio", "camada", "categor", "numeros")),
    ("lab", {0, 4, 9, 11, 14, 20, 22, 25, 28}, ("setup", "ambiente", "hipotese", "checkpoint", "contrato", "comparacao", "relatorio", "evidencia", "entregavel", "reproduz", "configuracao", "como estudar", "plano observavel")),
]


def normalized(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.casefold()) if not unicodedata.combining(c))


def mechanism_for(lesson_id, title):
    # Projection/setup scheduling notes are not the subject of a slide.
    title = normalized(title).split(" · projetado")[0]
    return next((key for key, ids, fragments in RULES if lesson_id in ids and any(f in title for f in fragments)), None)


def overview(lesson_id):
    if lesson_id == 6:
        labels = ["Entrada", "Q, K e V", "Scores e máscara", "Atenção", "Bloco", "Saída"]
    else:
        data = json.loads((ROOT / "demos" / "lessons" / f"{lesson_id:02d}.json").read_text(encoding="utf-8"))
        labels = data["nodes"]
    return chart("O percurso desta aula", "As setas indicam a ordem de estudo. Abra cada etapa para entender sua função.",
                 [node(label, description) for label, description in zip(labels, PHASES[lesson_id], strict=True)],
                 "Conecte as etapas: explique como uma decisão afeta o que você observa em seguida.")


def lesson_mechanisms(lesson_id):
    keys = [key for key, ids, _ in RULES if lesson_id in ids]
    if lesson_id == 6:
        keys.insert(0, "postblock")
    return keys


def chart_html(data, focus=None, navigable=False):
    parts = ['<figure class="learning-flow" aria-label="' + escape(data["title"], quote=True) + '">',
             '<figcaption><span class="lf-kicker">FLUXOGRAMA</span><h3>' + escape(data["title"]) + '</h3><p>' + escape(data["lead"]) + '</p></figcaption><ol class="lf-stages">']
    for i, stage in enumerate(data["stages"]):
        active = i == focus
        parts.append('<li class="lf-stage' + (' lf-active' if active else '') + '"><details' + (' open' if active or focus is None else '') + '><summary><span class="lf-number">' + str(i + 1) + '</span><span>' + escape(stage["title"]) + '</span>' + ('<span class="lf-current">Nesta etapa</span>' if active else '') + '</summary><p>' + escape(stage["text"]) + '</p></details>')
        if stage["branches"]:
            parts.append('<ul class="lf-branches">' + ''.join('<li>' + escape(b) + '</li>' for b in stage["branches"]) + '</ul>')
        if stage["note"]:
            parts.append('<p class="lf-loop">' + escape(stage["note"]) + '</p>')
        if navigable:
            parts.append(f'<button type="button" class="lf-jump" data-flow-focus="{i}">Explorar {escape(stage["title"])}</button>')
        parts.append('</li>')
    parts.append('</ol><p class="lf-output">' + escape(data["output"]) + '</p></figure>')
    return ''.join(parts)


def css():
    return (ROOT / "demos" / "flowcharts.css").read_text(encoding="utf-8")


def standalone_html(data):
    return '<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + escape(data["title"]) + '</title><style>body{margin:0;padding:16px;background:#fffdf8;font:16px/1.5 system-ui,sans-serif}*{box-sizing:border-box}' + css() + '</style>' + chart_html(data) + '</html>'


def transformer_flowcharts(html):
    """Integrate maps into the original player without changing its source files."""
    keys = ["seq2seq", None, None, "attention", "attention", "attention", "attention", "attention",
            "postblock", "postblock", "postblock", "postblock", "training", "seq2seq", "seq2seq",
            "decode", "decode", "training", "block", "kv"]
    maps = {key: chart_html(MECHANISMS[key]) for key in set(keys) if key}
    maps["overview"] = chart_html(overview(6))
    serialized = json.dumps({"keys": keys, "maps": maps}, ensure_ascii=False).replace("<", "\\u003c")
    panel = '<details class="demo-flow" id="flowchart-box"><summary>Fluxograma desta explicação · abrir para acompanhar</summary><div id="flowchart"></div></details>'
    anchor = '<div class="visual" id="visual">'
    render_anchor = 'answer.open=false;renderVisual()}'
    if anchor not in html or render_anchor not in html:
        raise ValueError("O player da aula 06 mudou; revise a integração dos fluxogramas.")
    html = html.replace('</style>', css() + '</style>', 1).replace(anchor, panel + anchor, 1)
    html = html.replace(render_anchor, 'answer.open=false;renderVisual();window.renderTransformerFlow?.()}', 1)
    script = '<script>(()=>{const data=' + serialized + ';window.renderTransformerFlow=()=>{const index=window.lessonSnapshot.step;document.getElementById("flowchart").innerHTML=data.maps[data.keys[index]||"overview"];};window.renderTransformerFlow();})();</script>'
    return html.replace('</body>', script + '</body>', 1)


COURSE_MAP = chart("Do texto ao sistema avaliado", "Um mapa para localizar as peças construídas ao longo do curso.", [
    node("Representar texto · aulas 01–04", "Tarefas e métricas, tokens, embeddings e primeiro laboratório."),
    node("Construir o modelo · aulas 05–11", "Recorrência, atenção, Transformer, mini-GPT e decodificação."),
    node("Treinar e adaptar · aulas 12–17", "Pré-treinamento, SFT, LoRA, preferências, raciocínio e revisão."),
    node("Conectar fontes e ações · aulas 18–22", "RAG, recuperação híbrida, tool calling e MCP."),
    node("Coordenar e verificar · aulas 23–28", "Agentes, orquestração, segurança e avaliação por camada."),
    node("Consolidar e apresentar · aulas 29–30", "Recapitulação, fronteiras da área e defesa do projeto.")
], "Comece pela recepção (aula 00) para conhecer materiais, ambiente e organização do curso.")

STUDY_MAP = chart("Uma sessão de estudo no portal", "Um ciclo curto para transformar leitura em uma explicação própria.", [
    node("Escolher uma aula", "Use o catálogo, a busca ou Navegar pelo curso."),
    node("Localizar o mecanismo", "Abra Fluxogramas para ver as partes e suas conexões."),
    node("Prever e experimentar", "Na demonstração, antecipe um resultado e altere um controle."),
    node("Conferir a explicação", "Compare o observado com o Passo a passo e com Conferir raciocínio.", ["Entendi → registrar a conclusão", "Ainda há dúvida → voltar ao mecanismo e testar outra hipótese"]),
    node("Guardar seu percurso", "Anote em Meu caderno, marque a conclusão e baixe o JSON.")
], "Na próxima sessão, restaure o JSON para continuar com suas anotações e conclusões.")
