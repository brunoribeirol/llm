# LLM por dentro — portal interativo

**[Abrir o portal online](https://victorhwfreire.github.io/portal_gml_262/)** ·
[Publicação e atualização do GitHub Pages](README-PAGES.md)

O GitHub Pages oferece uma edição pública estática das 31 aulas. A aplicação
Streamlit completa, com autenticação e gestão de turma, continua neste projeto.

Portal Streamlit do curso **Grandes Modelos de Linguagem: do Transformer aos Agentes de IA**. Inclui a recepção e as 30 aulas da versão 2, com uma demonstração visual completa por encontro, além das 552 etapas de estudo e dos materiais do professor.

Veja o [mapa das demonstrações completas e seus roteiros](DEMONSTRACOES.md), o [mapa das aulas e dos experimentos](MAPA-DAS-AULAS.md) e a [prévia do catálogo](verification/catalogo.png).

Para estudantes e professores, consulte o [guia de uso do portal](COMO-USAR.md), também disponível no menu **Como usar o portal**. Todas as aulas têm a área **Fluxogramas**, com mapas de percurso e mecanismos; os mapas correspondentes aparecem junto às explicações e nas demonstrações. Cada mapa pode ser baixado em HTML para uso offline. O [mapa de cobertura dos fluxogramas](FLUXOGRAMAS.md) registra as inserções por aula.

As **Especificações dos slides**, disponíveis em **Materiais** para professores nas 31 aulas, também incluem orientações por slide e os desenhos Mermaid completos. Consulte a [cobertura dos fluxogramas nas instruções de slides](FLUXOGRAMAS-SLIDES.md). Os arquivos-fonte estão em `../v2/aulas/`; `python scripts/build_slide_flowcharts.py` atualiza suas seções de fluxogramas, as cópias do portal e os metadados de download.

O [registro de validação](VALIDACAO.md) distingue os testes realizados e as configurações externas necessárias para publicar.

## O que há no portal

- Catálogo por módulo e busca por assunto.
- Roteiros originais organizados em etapas, com navegação anterior/próxima e links de aula.
- Demonstrações HTML completas em todas as aulas: percurso visual, controles, cálculos, perguntas e fala docente por etapa, seguindo o formato da aula 06.
- Experimentos Python específicos para cada encontro, disponíveis como complementos.
- Download das demonstrações para uso sem internet e de um roteiro separado por aula para o professor.
- Modo de apresentação para projetar em sala, área docente e materiais para download.
- Notebooks e scripts originais empacotados por aula; soluções em arquivos exclusivos do professor.
- Caderno de anotações e conclusão de aulas, exportável e importável em JSON.
- Autenticação por e-mail e senha, com contas criadas pelo professor e perfis de professor/aluno.
- Administração da turma: criação de contas, bloqueio de acesso e redefinição de senha temporária.

As demonstrações executam os cálculos no navegador; os experimentos complementares executam no servidor. Não consomem APIs de modelos nem executam código arbitrário digitado pelo visitante. Os números de exemplos simulados não representam medições de modelos comerciais.

## Executar

No PowerShell, dentro desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe setup_admin.py
.\.venv\Scripts\python.exe start.py
```

Abra `http://localhost:8501`. A aplicação exige a criação do primeiro professor antes de liberar o curso. Não há senha padrão nem chave de acesso embutida.

Com as dependências instaladas, `python abrir_local.py` inicia o servidor local em segundo plano e abre o navegador. Se o banco local estiver vazio, gera uma senha temporária aleatória para o primeiro professor e a mostra no terminal. Contas existentes são preservadas.

Se a porta padrão estiver ocupada por outro aplicativo, use `python abrir_local.py --port 8502`. A opção `--no-browser` inicia o servidor sem abrir uma janela do navegador.

Consulte [Autenticação e hospedagem](README-AUTENTICACAO.md) para criar o primeiro professor, configurar o banco de produção e cadastrar os estudantes.

## Conduzir uma aula

1. Entre com uma conta autorizada e abra uma aula no catálogo.
2. A aula abre na **Demonstração interativa**. Use o percurso lateral e os botões Voltar/Avançar para acompanhar o mecanismo completo.
3. Peça uma previsão antes de alterar um controle. Compare a previsão com o resultado calculado e abra a explicação da pergunta.
4. Use **Modo apresentação** no portal ou **Modo projeção** dentro da demonstração para ampliar a leitura e esconder as notas docentes.
5. Consulte **Passo a passo** para o texto original e **Materiais** para baixar o HTML e, no perfil docente, o roteiro de fala da demonstração.
6. Registre observações em **Meu caderno** e baixe o JSON ao final. Para restaurar as anotações em outra sessão, abra esse arquivo em um editor e cole seu conteúdo no campo de importação.

O caderno não é um registro acadêmico nem um banco de notas. Não há persistência no servidor: ele permanece na sessão até ser exportado. Esse desenho permite utilizar hospedagem com instâncias temporárias sem prometer armazenamento que não existe.

## Publicar na Vercel

O projeto inclui um `Dockerfile.vercel`: utiliza o suporte atual da Vercel a containers e WebSockets. A publicação precisa de uma conta/projeto Vercel, de um banco PostgreSQL externo e dos dados privados do primeiro administrador. Veja as instruções completas em [README-AUTENTICACAO.md](README-AUTENTICACAO.md).

Defina **esta pasta `portal/` como raiz do projeto**. Ela contém uma cópia dos materiais utilizados; o restante do acervo local não precisa ser enviado à hospedagem. Não publique `.streamlit/secrets.toml`, ambientes virtuais ou arquivos `.env`.

Após publicar, verifique: login e logout; recusa de credenciais inválidas; criação e bloqueio de aluno; troca da senha inicial; diferença entre professor e estudante; controles de uma demonstração; navegação por etapas; download de materiais. Verifique também a reconexão após o limite de duração de uma conexão WebSocket definido pela plataforma.

## Atualizar o conteúdo

As fontes continuam em `../v2/aulas/`. Para reconstruir o pacote depois de editar essas fontes:

```powershell
python scripts/build_content.py
```

Isso atualiza o conteúdo empacotado, sem alterar os documentos originais. Reinicie o portal depois da atualização. O código da interface está em `app.py`; os experimentos estão em `experiments.py`; o acesso é controlado em `auth.py` e `accounts.py`.

As demonstrações completas têm autoria própria em `demos/lessons/` e simuladores em `demos/simulators-*.js`. Após editar esse conteúdo, execute `python scripts/build_demo_scripts.py` para atualizar os roteiros separados e o mapa. Reinicie o portal para renovar o cache. O rebuild dos roteiros originais não substitui essa autoria visual.

Os fluxogramas são definidos em `flowcharts.py` e estilizados em `demos/flowcharts.css`. As regras de associação usam o número da aula e trechos dos títulos das etapas; ao renomear uma etapa, confira sua associação. O guia mostrado no portal e seu download usam a mesma fonte, `COMO-USAR.md`. Esses arquivos não são substituídos pelo rebuild dos materiais.

## Verificar

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

Os testes cobrem catálogo, cálculos didáticos, autorização, caderno e interface. Os testes da interface usam identidades simuladas apenas no processo de teste. Não há um modo de acesso sem autenticação na aplicação.

`python tests/check_browser.py` verifica também o navegador Edge com contas reais em um banco SQLite temporário: login, troca de senha, cadastro, bloqueio, demonstrações e downloads. O servidor de teste atende apenas em localhost e é encerrado ao final. As capturas ficam em `verification/` e não são enviadas à Vercel.

`node tests/check_demo_simulators.js` percorre os cálculos de todas as novas demonstrações com valores iniciais e extremos. `python tests/check_demos_browser.py` navega por todas as etapas no Edge e verifica controles, perfis e largura de celular, sem usar as contas locais do professor.

As contas usam SQLite na execução local e PostgreSQL na produção. A validação final da hospedagem depende de uma publicação com o banco e os segredos configurados; testes locais não substituem essa verificação externa.
