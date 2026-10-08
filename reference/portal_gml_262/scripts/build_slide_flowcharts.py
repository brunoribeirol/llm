"""Add self-contained diagram specifications to V2 slide briefs, then package them.

Only managed sections are regenerated; original slide text and numbering survive.
Run from the workspace or portal folder. No network or credentials are involved.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

PORTAL = Path(__file__).resolve().parents[1]
SOURCE = PORTAL.parent / "v2" / "aulas"
sys.path.insert(0, str(PORTAL))
from flowcharts import MECHANISMS, STUDY_MAP, chart, mechanism_for, node, normalized, overview


# Explicit graph topology: alternatives are not sequential stages, and loops
# return to their actual decision point. Detailed copy comes from the portal.
GRAPHS = {
    "bpe": '''A["Corpus e unidades iniciais"] --> B["Contar pares adjacentes"]
B --> C["Escolher e registrar uma fusão"]
C --> D{"Ainda há orçamento de vocabulário?"}
D -->|Sim| B
D -->|Não| E["Congelar vocabulário e ordem dos merges"]
T["Texto novo"] --> F["Aplicar as regras aprendidas"]
E --> F
F --> G["Peças e IDs"]''',
    "attention": '''X["Entrada X"] --> Q["Q = XWq"]
X --> K["K = XWk"]
X --> V["V = XWv"]
Q --> S["QKᵀ / √dₖ"]
K --> S
S --> M["Máscara conforme a arquitetura"]
M --> P["Softmax por linha"]
P --> C["Soma ponderada dos values"]
V --> C
C --> O["Representações contextuais"]''',
    "block": '''X["X"] --> N1["Norma"] --> A["Atenção"] --> S1["Soma: H = X + Atenção(Norm(X))"]
X -->|Residual| S1
S1 --> N2["Norma"] --> F["FFN"] --> S2["Soma: Y = H + FFN(Norm(H))"]
S1 -->|Residual| S2
S2 --> O["Próximo bloco"]''',
    "postblock": '''X["X"] --> A["Multi-head attention"] --> S1["Somar"] --> N1["LayerNorm: H"]
X -->|Residual| S1
N1 --> F["FFN"] --> S2["Somar"] --> N2["LayerNorm: Y"]
N1 -->|Residual| S2
N2 --> O["Próxima camada"]''',
    "decode": '''P["Prompt tokenizado"] --> M["Passagem do modelo"] --> L["Logits"]
L --> D{"Estratégia de escolha"}
D -->|Greedy| G["Maior score"]
D -->|Amostragem| A["Temperatura, filtros e sorteio"]
G --> T["Acrescentar token ao prefixo"]
A --> T
T --> F{"EOS ou limite atingido?"}
F -->|Não| M
F -->|Sim| O["Devolver sequência"]''',
    "training": '''D["Dados filtrados e deduplicados"] --> P["Separar treino, validação e teste"]
P --> B["Lote de treino: entrada e alvo deslocado"]
B --> M["Modelo com máscara causal"] --> L["Entropia cruzada"] --> G["Backpropagation"] --> U["Atualizar pesos"]
U --> V["Medir validação sem atualizar pesos"] --> F{"Critério de parada?"}
F -->|Não| B
F -->|Sim| T["Avaliar no teste reservado"]''',
    "lora": '''X["Entrada x"] --> W["Base congelada: Wx"]
X --> A["A: reduzir para posto r"] --> B["B: retornar à dimensão de saída"] --> E["Escalar por α/r"]
W --> S["Somar contribuições"]
E --> S
S --> L["Calcular perda"] --> G["Gradientes apenas dos adaptadores"]
G -. Atualizar A e B .-> A
G --> O["Salvar adaptador e avaliar contra a base"]''',
    "preference": '''D["Prompt + resposta preferida + rejeitada"] --> R{"Rota de ajuste"}
R -->|RLHF| RM["Treinar modelo de recompensa"] --> PPO["Otimizar política com sinal de recompensa"]
R -->|DPO| DP["Otimizar diretamente os pares"]
REF["Política de referência"] -. Regularização .-> PPO
REF -. Razões de probabilidade .-> DP
PPO --> E["Avaliar comportamento em casos separados"]
DP --> E
E --> F["Investigar exploração do sinal e regressões"]''',
    "rag": '''D["Documentos e metadados"] --> C["Chunks"] --> E["Embeddings e índice"]
Q["Pergunta"] --> R["Recuperar candidatos"]
E --> R
R --> S["Selecionar contexto dentro do orçamento"] --> V{"Há evidência suficiente?"}
V -->|Sim| G["Gerar resposta com fontes"] --> A["Conferir suporte das afirmações"]
V -->|Não| N["Declarar limitação ou reformular busca"]
N -. Se houver nova busca .-> R''',
    "hybrid": '''Q["Consulta"] --> B["BM25: busca lexical"]
Q --> D["Busca densa"]
B --> F["Fusão por posição: RRF"]
D --> F
F --> R["Reranking dos candidatos"] --> K["Selecionar top-k"] --> C["Contexto do gerador"]
F -. Cobertura dos candidatos .-> M["Medir recall, precisão e ordem"]
K -. Seleção e ordem .-> M''',
    "tools": '''H["Host fornece contexto e schemas"] --> M["Modelo propõe nome e argumentos"]
M --> V{"Host: formato e permissão válidos?"}
V -->|Não| E["Devolver erro sem executar"]
V -->|Sim| T["Executar ferramenta autorizada"]
T --> O["Anexar resultado à conversa"]
E --> O
O --> D{"Responder ou pedir nova chamada?"}
D -->|Resposta final| F["Finalizar"]
D -->|Nova chamada e orçamento disponível| M
D -->|Limite atingido| L["Encerrar com limitação"]''',
    "agent": '''G["Objetivo, permissões e orçamento"] --> P["Planejar a próxima ação"]
P --> A["Validar e executar ferramenta"] --> O["Registrar observação na memória"]
O --> V{"Objetivo verificado?"}
V -->|Sim| F["Finalizar com evidências"]
V -->|Não| B{"Há orçamento e condição de continuar?"}
B -->|Sim: usar a observação| P
B -->|Não| L["Parar e declarar limitações"]''',
    "multi": '''T["Tarefa e orçamento compartilhado"] --> O["Orquestrador decompõe"]
O --> A["Trabalhador A"]
O --> B["Trabalhador B"]
O --> C["Trabalhador C"]
A --> V["Reunir e verificar resultados"]
B --> V
C --> V
V --> D{"Resultados suficientes?"}
D -->|Sim| F["Compor resultado"]
D -->|Não, há orçamento| O
D -->|Não, limite atingido| L["Encerrar com lacunas explícitas"]''',
    "evaluation": '''C["Casos, referências e critérios"] --> E["Executar e registrar entradas e saídas"]
E --> R["Medir recuperação"]
E --> S["Avaliar resposta por rubrica"]
E --> A["Avaliar ações e trajetória"]
R --> J["Consolidar métricas; calibrar julgamentos com humanos"]
S --> J
A --> J
J --> D["Reportar por camada com denominadores e limites"]
D --> P["Priorizar correção"]
P -. Reexecutar os mesmos casos .-> E''',
    "classification": '''D["Casos rotulados"] --> P["Modelo e limiar fixados"] --> C["Comparar previsão e referência"]
C --> A["VP e VN: acertos"]
C --> B["FP: alarme indevido"]
C --> F["FN: positivo perdido"]
A --> M["Calcular métricas com denominadores válidos"]
B --> M
F --> M
M --> E["Decidir pelo custo dos erros e distribuição das classes"]''',
    "embeddings": '''C["Corpus e janelas de contexto"] --> T{"Tarefa-proxy"}
T -->|CBOW| B["Contexto prevê palavra central"]
T -->|Skip-gram| S["Palavra central prevê contexto"]
B --> L["Calcular perda e atualizar vetores"]
S --> L
L -. Novos exemplos de treino .-> T
L --> V["Vetores aprendidos"] --> R["Medir similaridade e ordenar vizinhos"] --> A["Inspecionar sentidos e falhas"]''',
    "recurrence": '''X["Token atual e estado anterior"] --> H["Atualizar estado recorrente"]
H -. Próximo token .-> X
H --> E["Guardar estados do encoder"]
D["Estado do decoder"] --> S["Calcular alinhamento"]
E --> S
S --> P["Softmax dos scores"] --> C["Combinar estados da origem"]
E --> C
C --> O["Contexto para o passo do decoder"]''',
    "rope": '''X["Representações de entrada"] --> Q["Projetar Q"]
X --> K["Projetar K"]
Q --> RQ["Rotacionar pares pela posição m"]
K --> RK["Rotacionar pares pela posição n"]
RQ --> S["Produto interno incorpora distância relativa"]
RK --> S
S --> A["Escala, máscara, softmax e combinação de V"]''',
    "moe": '''X["Representação do token"] --> R["Roteador calcula scores"] --> K["Selecionar especialistas top-k"]
K --> A["Especialista ativo A"]
K --> B["Especialista ativo B"]
A --> C["Combinar com pesos do roteador"]
B --> C
C --> O["Saída da camada"]
K -. Monitorar .-> M["Carga, capacidade e custo ativo"]''',
    "kv": '''P["Prefill do prompt"] --> C["Cache de K e V por camada"]
T["Novo token"] --> Q["Calcular Q, K e V da nova posição"]
Q --> U["Acrescentar K e V ao cache"]
C --> U
Q --> A["Nova query consulta o contexto"]
U --> A
A --> L["Logits e escolha do token"] --> D{"Continuar geração?"}
D -->|Sim| T
D -->|Não| F["Devolver sequência"]''',
    "reasoning": '''P["Problema e critério externo"] --> G["Gerar grupo de candidatos"]
G --> V["Verificar e atribuir recompensas"] --> R{"Finalidade"}
R -->|Inferência| S["Selecionar resposta pelos sinais disponíveis"] --> E["Medir a resposta entregue"]
R -->|Treinamento GRPO| A["Comparar recompensas no grupo"] --> U["Ajustar política"]
U -. Próximo grupo .-> G
S -. Custo e limitações .-> L["Reportar orçamento e confiabilidade do verificador"]
U -. Custo e limitações .-> L''',
    "mcp": '''H["Host com cliente MCP"] --> I["Inicializar conexão com servidor"]
I --> D["Descobrir ferramentas e schemas"] --> V["Host valida nome, argumentos e permissão"]
V --> C["Cliente envia chamada"] --> S["Servidor executa ferramenta"]
S --> R["Resultado retorna pelo cliente"] --> O["Host usa a observação"]''',
    "security": '''O["Identificar origem do conteúdo"] --> D["Tratar conteúdo externo como dados"]
D --> A["Host valida ação proposta"] --> P{"Política de execução"}
P -->|Fora do escopo| B["Bloquear"]
P -->|Requer revisão| H["Aguardar decisão humana"]
P -->|Autorizada| E["Executar"]
H --> V{"Aprovada?"}
V -->|Sim| E
V -->|Não| B
E --> T["Auditar trajetória e consequência"]
B --> T''',
    "multimodal": '''I["Imagem com resolução definida"] --> P["Dividir em patches"] --> E["Projetar em vetores e representar posição"]
E --> V["Encoder visual combina representações"] --> T{"Interface da tarefa"}
T -->|Tarefa visual| C["Cabeça de tarefa"]
T -->|Modelo de linguagem| A["Adaptar representações para a arquitetura multimodal"]''',
    "lab": '''H["Hipótese e critério de comparação"] --> D["Dados e ambiente registrados"] --> B["Executar referência"]
B --> V["Alterar uma condição"] --> M["Medir nos mesmos casos"] --> C{"A evidência responde à hipótese?"}
C -->|Não| H
C -->|Sim| R["Relatar configuração, resultados e limites"]''',
    "project": '''P["Problema e usuário"] --> A["Arquitetura justificada"] --> D["Execução com evidências"]
D --> M["Avaliação com casos e critérios"] --> L["Limitações que afetam o uso"] --> R["Defesa e artefatos reproduzíveis"]''',
    "seq2seq": '''F["Tokens da fonte"] --> E["Embeddings, posição e encoder"]
T["Prefixo do alvo"] --> D["Embeddings, posição e atenção causal"]
E -->|K e V| C["Cross-attention"]
D -->|Q| C
C --> B["Restante do decoder"] --> L["Logits e escolha do próximo token"]
L --> S{"Parada?"}
S -->|Não: acrescentar ao prefixo| T
S -->|Sim| O["Sequência de saída"]''',
}

SPECIAL = {
    "exam": chart("Realização da avaliação", "Fluxo operacional; não mostrar conteúdo avaliado.", [
        node("Conferir regras e identificação", "Prova individual, escrita, sem consulta e sem IA."),
        node("Planejar o tempo", "Distribua o trabalho na janela de 100 minutos; os tempos sugeridos somam 85."),
        node("Realizar a prova", "Acompanhe os avisos e o prazo informado pelo professor."),
        node("Revisar e reunir folhas", "Confira identificação e todas as folhas da avaliação."),
        node("Entregar ao professor", "Aguarde a conferência do recolhimento.")], "Não incluir perguntas, fórmulas nem pistas de resposta."),
    "handover": chart("Conferência e entrega", "Procedimento de recolhimento da avaliação.", [
        node("Reunir as folhas", "Junte as folhas da avaliação para a entrega."),
        node("Conferir identificação", "Verifique se a identificação solicitada foi preenchida."),
        node("Confirmar completude", "Se faltar identificação ou uma folha, faça a correção antes de entregar."),
        node("Entregar e conferir", "O professor recolhe e confere folha por folha.")], "A entrega encerra a realização da avaliação."),
    "session": chart("Operação das apresentações finais", "Fluxo de sessão, com os horários definidos na grade do slide 2.", [
        node("Abertura", "Anuncie regras, ordem e critérios."),
        node("Apresentações do bloco A", "Cada slot tem 12 minutos de apresentação e 3 de perguntas e troca."),
        node("Pausa técnica", "Use a janela prevista para preparar o bloco seguinte."),
        node("Apresentações do bloco B", "Mantenha a mesma organização de slots."),
        node("Encerramento", "Recolha os registros e apresente a devolutiva da sessão.")], "O deck do instrutor aparece nas transições; durante a apresentação, projete o deck da equipe."),
    "study": STUDY_MAP,
    "course_layers": chart("As sete camadas do curso", "Ordem de estudo com o endereço de cada construção.", [
        node("Token e representação", "Aulas 2–3; Lab 1 na aula 4."),
        node("Atenção e Transformer", "Aulas 5–8; Lab 2 na aula 9."),
        node("Escala e decodificação", "Aulas 10–12; Lab 3 na aula 11."),
        node("Adaptação e alinhamento", "Aulas 13–16; Lab 4 na aula 14."),
        node("Recuperação", "Aulas 18–19; Lab 5 na aula 20."),
        node("Ferramentas e agentes", "Aulas 21–26; Labs 6 e 7."),
        node("Avaliação", "Aula 27; Lab 8 na aula 28.")], "Apresentar como mapa curricular, sem introduzir uma aula técnica na recepção."),
    "sft": chart("SFT: dados de diálogo até o comportamento", "O objetivo continua sendo próximo token, com dados e supervisão definidos para a tarefa.", [
        node("Selecionar exemplos", "Prepare instruções e respostas de qualidade; separe treino e avaliação."),
        node("Aplicar template de chat", "Marque papéis, delimitadores e turnos como o modelo espera."),
        node("Definir tokens supervisionados", "A máscara de loss determina quais posições contribuem para a perda."),
        node("Ajustar os pesos treináveis", "Calcule entropia cruzada e atualize os parâmetros selecionados."),
        node("Avaliar formato e capacidade", "Compare tarefas alvo e conjunto de controle com a base.")], "Acertar o formato não demonstra preservação de todas as capacidades."),
}
GRAPHS["handover"] = '''F["Reunir folhas"] --> I["Conferir identificação"] --> C{"Tudo identificado e reunido?"}
C -->|Não| R["Completar a conferência"] --> I
C -->|Sim| E["Entregar ao professor"] --> V["Conferência folha por folha"]'''
GRAPHS["study"] = '''A["Escolher aula"] --> M["Localizar mecanismo no mapa"] --> P["Prever e experimentar"]
P --> C["Conferir a explicação"] --> D{"Conseguiu explicar?"}
D -->|Não: testar nova hipótese| M
D -->|Sim| N["Registrar e exportar o caderno"]'''
GRAPHS["sft"] = '''D["Exemplos de instrução e resposta"] --> T["Template de chat"] --> M["Máscara dos tokens supervisionados"]
M --> F["Passagem do modelo"] --> L["Entropia cruzada"] --> U["Atualizar parâmetros treináveis"]
U -. Próximo lote .-> T
U --> E["Avaliar formato, tarefa e capacidade no controle"]'''

# Human-selected complements for slide titles that hide the actual mechanism.
# Tuple keys are the existing slide numbers; no slide is added or renumbered.
OVERRIDES = {
    0: {3: "course_layers", 7: "study", 8: "study", 11: "study"},
    2: {9: "bpe"},
    3: {8: "embeddings", 11: "embeddings", 12: "embeddings"},
    4: {2: "embeddings", 5: "lab", 6: "bpe"},
    5: {2: "recurrence", 5: "recurrence", 9: "recurrence", 10: "recurrence", 19: "recurrence", 20: "attention"},
    6: {2: "recurrence", 5: "attention", 6: "attention", 9: "attention", 15: "attention", 16: "attention", 18: "attention"},
    7: {5: "rope", 7: "rope", 8: "block", 11: "block", 20: "block"},
    8: {7: "decode"},
    9: {6: "attention", 12: "attention", 14: "training", 16: "training"},
    10: {7: "decode", 8: "decode", 9: "decode", 10: "decode", 12: "decode", 15: "kv", 19: "decode"},
    11: {4: "decode"},
    12: {3: "training", 4: "training", 5: "training", 6: "training"},
    13: {2: "sft", 3: "sft", 4: "sft", 5: "sft", 10: "lora", 17: "lora", 18: "lora", 19: "lora"},
    14: {4: "lora", 6: "sft", 8: "lora"},
    15: {3: "preference", 4: "preference", 5: "preference", 6: "preference", 7: "preference", 10: "preference", 17: "preference", 20: "preference"},
    16: {2: "reasoning", 5: "reasoning", 8: "reasoning", 18: "reasoning", 19: "reasoning"},
    17: {1: "exam", 2: "exam", 3: "exam", 4: "handover"},
    18: {2: "rag", 3: "rag", 5: "rag", 6: "rag", 8: "rag", 11: "rag"},
    19: {2: "hybrid", 3: "hybrid", 5: "hybrid", 7: "hybrid", 9: "hybrid", 12: "rag"},
    20: {4: "rag"},
    21: {1: "tools", 2: "tools", 3: "tools", 4: "tools", 6: "tools", 8: "tools", 9: "tools", 10: "mcp"},
    22: {4: "tools"},
    23: {2: "agent", 4: "agent", 8: "agent", 13: "agent", 16: "agent"},
    24: {4: "multi", 8: "multi"},
    25: {4: "tools"},
    26: {2: "security", 9: "evaluation", 10: "evaluation", 12: "agent"},
    27: {9: "evaluation", 10: "evaluation", 11: "evaluation", 12: "evaluation", 13: "evaluation", 18: "evaluation", 20: "evaluation"},
    28: {4: "evaluation"},
    29: {3: "decode", 7: "multimodal"},
    30: {2: "session", 4: "project", 5: "session"},
}

SLIDE = re.compile(r"^### Slide (\d+)\s*[—–-]\s*(.+)$", re.M)
MANAGED = re.compile(r"<!-- SLIDE-FLOW:(?:GUIDE|SLIDE|LIBRARY):BEGIN -->.*?<!-- SLIDE-FLOW:(?:GUIDE|SLIDE|LIBRARY):END -->\n*", re.S)


def managed(kind, text):
    return f"<!-- SLIDE-FLOW:{kind}:BEGIN -->\n{text.rstrip()}\n<!-- SLIDE-FLOW:{kind}:END -->\n\n"


def graph(key, data):
    if key in GRAPHS:
        return "flowchart TD\n" + GRAPHS[key]
    # Only pedagogical and operational linear paths use this fallback.
    assert key in {"overview", "exam", "session", "course_layers"}
    lines = ["flowchart TD"]
    for index, stage in enumerate(data["stages"]):
        label = stage["title"].replace('"', "#quot;")
        lines.append(f'N{index}["{index + 1}. {label}"]')
        if index:
            lines.append(f"N{index - 1} --> N{index}")
    return "\n".join(lines)


def diagram_data(key, number):
    if key == "overview":
        return overview(number)
    return SPECIAL[key] if key in SPECIAL else MECHANISMS[key]


def enrich(number, original):
    clean = MANAGED.sub("", original).rstrip() + "\n"
    slides = list(SLIDE.finditer(clean))
    if not slides:
        raise ValueError(f"Aula {number:02d}: nenhum slide encontrado.")
    main = [s for s in slides if not re.match(r"A\.\d", s[2])]
    # Reuse a roadmap or closing slide instead of adding an unrelated opening.
    roadmap = next((s for s in main if "mapa" in normalized(s[2])), None)
    closing = next((s for s in reversed(main) if any(w in normalized(s[2]) for w in ("fechamento", "encerramento"))), main[-1])
    anchor = int((roadmap or closing)[1])
    if number == 0:
        anchor = 14
    assignments = {}
    for match in slides:
        index, title = int(match[1]), match[2]
        key = OVERRIDES.get(number, {}).get(index, mechanism_for(number, title))
        if key:
            assignments[index] = [key]
    if number not in {17, 30}:
        assignments.setdefault(anchor, []).insert(0, "overview")
    else:
        anchor = 1 if number == 17 else 2
    used = list(dict.fromkeys(key for index in sorted(assignments) for key in assignments[index]))
    ids = {key: f"F{index:02d}" for index, key in enumerate(used)}
    for match in reversed(slides):
        index, title = int(match[1]), match[2]
        if index not in assignments:
            continue
        refs = "; ".join(f'**{ids[key]} — {diagram_data(key, number)["title"]}**' for key in assignments[index])
        note = f"- **Fluxograma a incorporar neste slide:** {refs}. O desenho e os rótulos completos estão no caderno de fluxogramas ao final deste arquivo.\n"
        note += "- **Composição:** integrar ao campo Visual; preservar exemplos, tabelas, fórmulas e dimensões solicitados neste slide. Destacar o trecho relacionado ao título e manter o restante em segundo plano. Os textos detalhados ficam nas notas, sem duplicar a lista de Conteúdo na tela.\n"
        if any(word in normalized(title) for word in ("exercicio", "checkpoint")):
            note += "- **Momento de exibição:** apresentar o fluxo preenchido na discussão ou conferência, depois da tentativa da turma; durante a atividade, ocultar as etapas que entregariam a solução.\n"
        if number == 17:
            note += "- **Restrição da avaliação:** projetar somente procedimentos; não incorporar nenhum mapa de conteúdo das aulas 1–16. No slide do relógio, o fluxo ocupa apenas uma faixa de apoio.\n"
        if number == 30:
            note += "- **Uso na sessão:** mostrar somente na abertura, nas perguntas ou nas trocas de equipe; o fluxograma do instrutor não permanece sobre a apresentação dos estudantes.\n"
        insertion = "\n\n" + managed("SLIDE", note)
        clean = clean[:match.end()] + insertion + clean[match.end():].lstrip("\n")

    guide = '''## Fluxogramas na produção dos slides

As orientações abaixo complementam o campo **Visual** dos slides indicados. Produzir os fluxogramas no próprio deck, como formas e conectores editáveis ou gráficos vetoriais; a biblioteca completa ao final torna esta especificação independente do portal.

- **Referência de composição:** título e propósito no topo, blocos numerados, conexões rotuladas, ramificações legíveis e uma saída identificada. Usar apenas o padrão visual da referência fornecida, sem importar seu assunto ou seus exemplos.
- **Tema do deck:** manter o fundo escuro e a paleta já especificada para a aula. Usar `#5b8cff` para o trecho ativo, tons neutros para o contexto e `#e2231a` conforme o significado definido no deck. Cor sempre acompanhada de rótulo.
- **Leitura:** entrada no topo ou à esquerda; saída na base ou à direita. Decisões em losangos, alternativas com rótulos e retornos apontando à etapa correta. Ramos paralelos convergem apenas onde seus resultados realmente são combinados.
- **Densidade:** no fluxo principal, projetar 3–6 blocos curtos por enquadramento, com corpo legível na última fileira. Um mapa maior pode ser revelado por etapas no mesmo slide. Detalhes, condições e explicações completas ficam nas notas; não reduzir a fonte para caber tudo.
- **Semântica:** mapas de percurso mostram ordem de estudo, não execução de um algoritmo. Manter separadas preparação e aplicação, treino e inferência, sequência e alternativas. Não transformar uma etapa opcional em obrigatória.
- **Integração:** o fluxograma substitui uma lista redundante ou ocupa o campo Visual; não cobre matrizes, tabelas, gráficos nem código indispensáveis. Preservar títulos, numeração, duração e referências aos apêndices.
- **Produção:** os blocos Mermaid abaixo são especificações do desenho. Renderizar/reconstruir como diagrama, nunca projetar o código Mermaid. Manter rótulos, bifurcações, retornos e limites declarados. Não transformar este caderno técnico em slides adicionais.
- **Ligação com o portal:** os mapas de mecanismo compartilham o conteúdo dos fluxogramas do portal. Em demonstrações, usar o mesmo vocabulário no deck e no controle interativo para facilitar a passagem entre os dois.
'''
    if number == 17:
        guide += "\n**Aula de avaliação:** o caderno abaixo contém apenas mapas operacionais de realização e entrega. Não usar o percurso técnico de revisão do portal enquanto a prova estiver em andamento.\n"
    if number == 30:
        guide += "\n**Aula de apresentações:** os mapas apoiam a operação da sessão e a defesa. Preservar a grade, os pesos e o relógio; não criar exposição de conteúdo durante as apresentações das equipes.\n"
    position = clean.index("## Diretrizes")
    clean = clean[:position] + managed("GUIDE", guide) + clean[position:]

    library = ["# Caderno de fluxogramas para produção", "", "As referências Fxx identificam desenhos, não novos números de slide. Cada desenho abaixo é autocontido.", "", "| Mapa | Desenho | Usar nos slides |", "| --- | --- | --- |"]
    for key in used:
        slide_numbers = [str(index) for index, keys in assignments.items() if key in keys]
        library.append(f'| {ids[key]} | {diagram_data(key, number)["title"]} | {", ".join(slide_numbers)} |')
    for key in used:
        data = diagram_data(key, number)
        library.extend(["", f'## {ids[key]} — {data["title"]}', "", data["lead"], "", "```mermaid", graph(key, data), "```", "", "**Conteúdo dos blocos e notas de montagem:**", ""])
        for i, stage in enumerate(data["stages"], 1):
            library.append(f'{i}. **{stage["title"]}:** {stage["text"]}')
            if stage["branches"]:
                library.append("   Ramos/alternativas a rotular: " + "; ".join(stage["branches"]) + ".")
            if stage["note"]:
                library.append("   " + stage["note"])
        library.extend(["", "**Saída ou limite a explicitar:** " + data["output"]])
        if key == "attention" and number == 5:
            library.extend(["", "**Recorte desta aula:** introduzir somente os papéis Q/K/V e a passagem de alinhamento aditivo para produto interno. O fluxo completo de scaled dot-product attention pertence à aula 06; não atribuí-lo à fórmula de Bahdanau."])
        if key == "rag" and number == 18:
            library.extend(["", "**Slide do pipeline em nove etapas:** o desenho agrupa operações para leitura. Desagrupar os blocos conforme as nove etapas já nomeadas no Conteúdo do slide; não alterar a contagem nem misturar indexação e consulta."])
    clean += "\n" + managed("LIBRARY", "\n".join(library))
    assert [m[0] for m in SLIDE.finditer(clean)] == [m[0] for m in slides]
    return clean, len(assignments), len(used)


def main():
    catalog_path = PORTAL / "content" / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    outputs = []
    for number in range(31):
        path = SOURCE / f"aula-{number:02d}" / "instructions-slides.md"
        original = path.read_text(encoding="utf-8")
        updated, placements, diagrams = enrich(number, original)
        # Ensure running again never duplicates markers, diagrams or slide notes.
        assert enrich(number, updated)[0] == updated, f"Aula {number}: geração não idempotente."
        data = updated.encode("utf-8")
        relative = f"aula-{number:02d}/instructions-slides.md"
        lesson = next(item for item in catalog["lessons"] if item["id"] == number)
        material = next((m for m in lesson["materials"] if m["path"] == relative), None)
        if material is None:
            material = {"name": "Especificação dos slides", "label": "Especificação dos slides", "mime": "text/markdown", "path": relative, "role": "teacher"}
            lesson["materials"].append(material)
        assert material["role"] == "teacher"
        material.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        outputs.append((path, PORTAL / "content" / relative, data, placements, diagrams))
    # All lessons are checked before writing any of them.
    for source, target, data, _, _ in outputs:
        source.write_bytes(data)
        target.write_bytes(data)
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = ["# Fluxogramas nas instruções de slides", "", "Fonte vigente: `v2/aulas/`. Cada arquivo tem orientações por slide e desenhos Mermaid completos, com cópia idêntica em `portal/content/` e download reservado ao professor.", "", "A aula 17 ganhou um deck operacional V2: realização e entrega da prova, sem mapas de conteúdo ou gabarito. As demais aulas preservam os títulos e a numeração existentes.", "", "| Aula | Slides com orientação | Desenhos incluídos |", "| --- | --- | --- |"]
    for number, (_, _, _, placements, diagrams) in enumerate(outputs):
        report.append(f"| {number:02d} | {placements} | {diagrams} |")
    report.extend(["", f"Total: **31 arquivos-fonte e 31 cópias do portal**, com **{sum(x[3] for x in outputs)} orientações por slide** e **{sum(x[4] for x in outputs)} desenhos incluídos** (há reutilização entre aulas).", "", "Para atualizar as seções gerenciadas, execute `python portal/scripts/build_slide_flowcharts.py` na raiz do projeto. O script preserva o restante das instruções, atualiza bytes/hashes do catálogo e verifica idempotência antes de gravar.", ""])
    (PORTAL / "FLUXOGRAMAS-SLIDES.md").write_text("\n".join(report), encoding="utf-8")
    print(f"31 aulas atualizadas; {sum(x[3] for x in outputs)} slides com fluxogramas; {sum(x[4] for x in outputs)} desenhos nas instruções.")


if __name__ == "__main__":
    main()
