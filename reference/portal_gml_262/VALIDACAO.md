# Validação da entrega

## Fluxogramas nas instruções dos slides — 21/09/2026

- 31 especificações V2 e 31 cópias idênticas no portal; 332 slides com orientações e 99 desenhos incluídos nas seções de fluxogramas. Cobertura em [FLUXOGRAMAS-SLIDES.md](FLUXOGRAMAS-SLIDES.md).
- Preservados os títulos e a numeração dos decks existentes. Criado o arquivo V2 ausente da aula 17 com quatro slides operacionais baseados no plano vigente, sem respostas ou mapas de conteúdo da prova.
- 13 testes de conteúdo e empacotamento aprovados. Conferidos bytes, SHA-256, igualdade fonte/cópia, acesso exclusivo do professor e regeneração idempotente em todas as aulas.
- Os 136 diagramas Mermaid presentes nos arquivos finais (99 incluídos e 37 preexistentes) renderizaram no Edge com Mermaid 11.4.1, sem erro. Registro: `verification/slide-flowcharts.json`.
- O catálogo foi sincronizado para disponibilizar **Especificação dos slides** em **Materiais**, inclusive na aula 17. O rebuild normal do conteúdo mantém os arquivos, pois a alteração está nas fontes V2.

## Fluxogramas e guia de uso — 21/09/2026

- 60 mapas: 31 percursos de aula, 27 mecanismos e 2 mapas de orientação. O relatório [FLUXOGRAMAS.md](FLUXOGRAMAS.md) registra 191 inserções de mecanismos nos textos e 196 nas demonstrações. As demais etapas visuais oferecem o percurso da aula.
- Guia [COMO-USAR.md](COMO-USAR.md) disponível no menu, no catálogo e para download, cobrindo acesso, navegação, recursos, estudo, uso offline, caderno e perfil docente.
- Suíte completa: **293 testes aprovados em 383,18 segundos**, incluindo conteúdo, separação de perfis, todas as áreas de fluxogramas, navegação do guia, associações entre títulos e mecanismos, serialização, contas, experimentos e caderno.
- Fluxo autenticado no Edge aprovado com contas descartáveis: acesso ao guia e download, seleção e download de fluxogramas, navegação nas demonstrações, perfis, caderno e bloqueio de acesso. Registro: `verification/browser-result.json`; prévias em `verification/como-usar.png` e `verification/fluxogramas-portal.png`.
- As 381 etapas das 31 demonstrações foram percorridas no Edge, com os novos mapas presentes. Também foram conferidos saltos entre fases pelos botões do fluxograma, preservação dos controles, perfis, projeção e mapas expandidos a 390 px, sem erros JavaScript. Registro: `verification/demos-browser.json`.
- Revisão visual de mapas expandidos em desktop e celular. Os HTMLs incluem estilos e conteúdo sem depender de bibliotecas ou serviços externos.
- A aula 06 mantém seu player original; mapas acompanham as etapas, incluindo a distinção entre pós-normalização e pré-normalização. O adaptador é aplicado ao gerar o HTML, sem modificar os materiais-fonte.

## Demonstrações completas — 17/09/2026

- **31 demonstrações e 381 etapas visuais**, incluindo as 20 etapas originais do Transformer.
- **63 testes de conteúdo e separação de perfis aprovados**: cobertura, controles válidos, falas/quadros removidos dos dados estudantis, serialização segura e HTML sem dependências de scripts externos.
- **67 testes da interface aprovados em 100,91 segundos**: catálogo, etapas, todas as demonstrações no Streamlit, acesso docente e restauração do caderno.
- Após remover um aviso de estado inicial do seletor, um teste adicional confirmou abertura, troca e retorno às aulas sempre na demonstração completa (**1 aprovado em 16,88 segundos**).
- **6.041 renderizações dos simuladores aprovadas**, incluindo valores iniciais, extremos dos controles, alternativas, texto vazio e HTML não confiável. Todas as novas aulas têm pelo menos cinco visualizações diferentes e cinco etapas cujos resultados reagem aos controles.
- Invariantes numéricos conferidos: normalização de probabilidades, máscara causal sem acesso ao futuro, dimensões, redução da perda com SGD, fusão LoRA, delta nulo, KL nula para distribuições iguais, vantagens do grupo, pass@k e preservação dos candidatos no reranking.
- **Todas as 381 etapas percorridas no Edge**, sem erros JavaScript. Controles, restauração, projeção, notas do professor e largura de celular verificados nas 31 aulas. Registro em `verification/demos-browser.json`; capturas `verification/demo-*.png`.
- **Fluxo autenticado no Edge aprovado**, usando banco SQLite temporário: login, troca obrigatória de senha, criação de estudante, perfis, catálogo, BPE, Transformer, RAG, download de HTML, exportação/importação do caderno, bloqueio e revogação. Registro em `verification/browser-result.json`.
- Revisão visual das capturas em desktop e celular. A navegação traz o título da nova etapa à vista; valores zero não recebem barras visíveis artificiais.

As simulações são didáticas e declaram seus limites. Há operações numéricas reais em escala pequena; vetores manuais, cenários roteirizados e estimativas sintéticas não são apresentados como inferências de modelos treinados ou benchmarks de produtos.

## Verificações anteriores e correções

A suíte anterior aprovou 161 testes de contas, autenticação, cálculos, conteúdo, navegação e caderno. Esse número descreve a versão anterior, não uma execução integral da suíte atual. Na ampliação, foram executadas as verificações dirigidas listadas acima, além do fluxo completo no navegador.

O reteste de restauração do caderno que estava pendente foi concluído: passou em AppTest e no navegador. A importação atualiza o texto e a lista de aulas concluídas. Também foi retirado o carregamento antecipado dos experimentos Python complementares: suas dependências são importadas apenas quando esse recurso é aberto.

## Reproduzir

Execute na pasta `portal/`, com as dependências de desenvolvimento instaladas e o Edge disponível:

```powershell
python -m pytest tests -q
node tests/check_demo_simulators.js
python tests/check_demos_browser.py
python tests/check_browser.py
```

O teste autenticado usa a porta local 18541 e contas descartáveis. Não altera o banco do professor em 8501. Capturas e dados privados locais não são enviados na configuração de publicação.

## Publicação e integrações externas

**O portal não foi publicado na Vercel.** A validação desta alteração é local. A publicação ainda depende da conta/projeto Vercel, do PostgreSQL de produção e dos segredos do primeiro administrador. A integração com PostgreSQL real e o container na hospedagem precisam de verificação própria; veja `README-AUTENTICACAO.md`.
