# Portal público no GitHub Pages

**Site:** https://victorhwfreire.github.io/portal_gml_262/

A pasta `docs/` contém a edição estática para estudantes: catálogo de 31 aulas,
busca, filtros por módulo, demonstrações interativas, passo a passo, guias,
downloads e caderno local com exportação/importação JSON.

O Pages publica `main`, pasta `/docs`. Cada push que atualiza essa pasta dispara
a publicação automática do GitHub Pages.

## Atualizar o site

Depois de editar os conteúdos ou as demonstrações:

```powershell
python -m pip install -r requirements-pages.txt
python scripts/build_pages.py
python tests/check_pages_browser.py
git add .
git commit -m "Atualiza aulas do portal"
git push
```

O teste de navegador requer as dependências de `requirements-dev.txt` e o
Microsoft Edge. O gerador utiliza apenas Python, PyYAML e Markdown, sem servidor,
contas, banco de dados ou dependência do acervo externo à pasta do portal.
O CSS e o JavaScript da navegação ficam em `pages/`. Os arquivos em `docs/`
são gerados; faça as alterações nas fontes e execute o gerador novamente.

## Diferenças da aplicação Streamlit

- A edição Pages é pública e não tem login, cadastro, permissões de professor
  nem gestão de turma. Esses recursos continuam na aplicação `app.py`, que
  precisa de hospedagem com Python e banco de dados.
- As demonstrações HTML mantêm seus controles e fluxogramas. Os experimentos
  Python adicionais de `experiments.py` continuam disponíveis no Streamlit.
- O caderno fica no armazenamento local do navegador, separado por aula.
  Não sincroniza entre dispositivos. Exporte o JSON para fazer uma cópia.
- A publicação inclui apenas materiais marcados como `student`, e as
  demonstrações são exportadas pelo renderizador existente no perfil estudante.
  Isso não restringe o acesso ao código-fonte: este repositório público também
  contém os materiais docentes originais do projeto.
- A renderização de fórmulas na leitura usa MathJax via CDN. As demonstrações
  baixadas continuam autônomas, conforme o portal original.

Dados locais de contas (`.data/`), bancos, segredos, caches e registros de
verificação são ignorados pelo Git e não fazem parte da publicação.
