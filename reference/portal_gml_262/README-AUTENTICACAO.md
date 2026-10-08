# Contas da turma e publicação na Vercel

O portal usa **e-mail e senha**, com contas criadas pelo professor. Não há cadastro público, senha padrão, login Google nem envio automático de e-mails. O professor cria cada conta e entrega uma senha temporária por um canal privado; a pessoa precisa trocá-la antes de acessar as aulas.

Os perfis são **Estudante** e **Professor**. Só professores podem criar contas, bloquear/desbloquear acessos e redefinir senhas. Essas permissões são verificadas no servidor e no banco de dados, inclusive quando uma função de administração é chamada diretamente.

## Executar localmente e criar o primeiro professor

No PowerShell, a partir da pasta `portal`:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python setup_admin.py
.\.venv\Scripts\python start.py
```

`setup_admin.py` solicita nome, e-mail e senha sem mostrar a senha digitada. Ela não precisa aparecer em argumentos de comando nem no histórico do terminal. Use **pelo menos 12 caracteres**; prefira uma frase longa, exclusiva e difícil de adivinhar.

Abra `http://localhost:8501`, entre como professor e substitua a senha temporária. O bootstrap funciona apenas enquanto o banco está vazio. Executá-lo novamente não altera a senha de uma conta existente.

No desenvolvimento local, as contas ficam em `portal/.data/portal.db` (SQLite). Essa pasta e os arquivos de banco são excluídos do Git, da imagem Docker e do envio à Vercel. Não apague esse arquivo se quiser conservar as contas locais. Sem o primeiro professor, o portal mantém as aulas bloqueadas e exibe orientações de configuração.

## Cadastrar e administrar a turma

Depois de entrar e trocar a primeira senha:

1. Abra **Gerenciar turma** na barra lateral.
2. Preencha nome, e-mail, senha temporária e perfil. O padrão é Estudante.
3. Clique **Criar conta** e entregue a senha temporária por um canal privado. O portal não envia mensagens.
4. Para revogar acesso, selecione a pessoa e clique **Bloquear acesso**. As sessões da conta são encerradas.
5. Para recuperar acesso, use **Redefinir senha e encerrar sessões**. Entregue a nova senha temporária; a troca será obrigatória no próximo login.

Em **Minha conta**, qualquer pessoa autenticada pode alterar a própria senha, informando a senha atual. A alteração encerra suas outras sessões. Não existe recuperação pública por e-mail; quem esqueceu a senha deve procurar o professor. Mantenha um segundo professor responsável para recuperação administrativa, se necessário.

## Banco persistente para produção

Na Vercel, as contas, sessões e limites de tentativas precisam de um **PostgreSQL externo e persistente**. Configure a conexão em `DATABASE_URL`, usando as credenciais do seu serviço de banco. O aplicativo cria suas tabelas na primeira inicialização; a conta do banco precisa dessas permissões.

```text
postgresql://USUARIO:SENHA@HOST/BANCO?sslmode=require
```

Use a URL de conexão recomendada pelo provedor para aplicações. Mantenha TLS habilitado. Não publique a URL nem a coloque em materiais da aula. SQLite é recusado quando `PORTAL_ENV=production` ou `VERCEL` está definido: uma imagem em nuvem não deve receber contas em um disco temporário.

O armazenamento das **contas** é persistente. O **caderno de estudo** continua sendo uma ferramenta da sessão, com exportação/importação em JSON; anotações não são gravadas no banco de contas.

## Publicar na Vercel

A Vercel oferece [containers em beta](https://vercel.com/docs/functions/container-images) e [WebSockets em beta](https://vercel.com/docs/functions/websockets). O portal está preparado para esse caminho, com `Dockerfile.vercel`, servidor HTTP do Streamlit na porta 80 e Fluid Compute habilitado. É necessário validar o funcionamento no projeto real após a publicação.

1. Crie/importe o projeto com **Root Directory = `portal`**. Ao enviar somente esta pasta, ela própria é a raiz. A Vercel detecta `Dockerfile.vercel` e encaminha as requisições ao container.
2. Configure as variáveis privadas abaixo no ambiente de produção. Nunca envie os valores em arquivos versionados. Use um banco e credenciais separados para previews de teste.
3. Gere o segredo de cookies com `python -c "import secrets; print(secrets.token_hex(32))"` e guarde o resultado nas variáveis privadas. Ele precisa ser o mesmo para todas as instâncias daquela implantação.
4. Faça o deploy pelo repositório conectado ou pela CLI, executada dentro da pasta `portal`: `npx vercel@latest --prod`. É necessário estar autenticado na conta Vercel; se precisar, execute `npx vercel@latest login` no seu terminal e conclua o acesso no navegador.
5. Entre com o primeiro professor e troque a senha. Depois de confirmar a criação, remova as três variáveis `PORTAL_ADMIN_*` do projeto e faça novo deploy. As contas existentes permanecem no PostgreSQL.

| Variável | Valor |
|---|---|
| `PORT` | `80` |
| `PORTAL_ENV` | `production` |
| `DATABASE_URL` | Conexão privada PostgreSQL com TLS |
| `STREAMLIT_SERVER_COOKIE_SECRET` | Segredo aleatório forte, no mínimo 32 caracteres |
| `PORTAL_ADMIN_EMAIL` | E-mail do primeiro professor; apenas no bootstrap |
| `PORTAL_ADMIN_NAME` | Nome do primeiro professor; apenas no bootstrap |
| `PORTAL_ADMIN_PASSWORD` | Senha temporária exclusiva, mínimo 12 caracteres; apenas no bootstrap |

As variáveis de bootstrap só criam uma conta quando o banco ainda não tem nenhuma. Reiniciar o container ou mudar essas variáveis não redefine senhas existentes. A inclusão de outros professores é feita em **Gerenciar turma**.

`.env.example` documenta os nomes; o aplicativo não carrega esse arquivo automaticamente. `start.py` valida porta, banco de produção e segredo compartilhado antes de iniciar. O segredo de cookies protege mecanismos do próprio Streamlit; a autenticação do curso usa os tokens de sessão descritos abaixo.

## Sessões e proteção de credenciais

- Senhas são armazenadas com **scrypt**, salt aleatório por senha e parâmetros de custo definidos no backend. O banco nunca recebe a senha em texto puro.
- Cada login cria um token aleatório. O banco armazena apenas seu hash. A interface guarda o token na sessão do Streamlit, sem colocá-lo em URLs, cookies de autenticação próprios ou arquivos de conteúdo.
- Toda execução da interface consulta a sessão no banco. Bloqueio, redefinição ou mudança de senha invalidam tokens anteriores. Uma sessão também expira após 12 horas.
- O limite de tentativas é persistente e transacional: cinco falhas por e-mail em 15 minutos e um limite adicional por cliente quando seu endereço está disponível. Mensagens de falha de login não revelam se o e-mail existe.
- Senhas temporárias obrigam uma troca antes de liberar o conteúdo ou operações administrativas. Não há atalho de autenticação nem credencial de demonstração em produção.
- Sair remove o token e o estado da sessão local, incluindo o caderno em memória. Exporte suas anotações antes de sair.

O login não é lembrado entre novas sessões do navegador. Uma atualização completa da página, reconexão em outra instância ou reinício pode exigir novo login. As contas permanecem no banco; os valores de controles e o caderno em memória podem ser reiniciados.

## Arquivos, sessões e limites da hospedagem

Os downloads são enviados pela sessão autenticada e convertidos em arquivos no navegador por links `data:`. Materiais docentes não recebem URLs públicas em `/media`. A restauração do caderno usa texto JSON na própria interface, sem endpoint separado de upload. Isso evita depender de afinidade de instância para esses arquivos, conforme as [restrições de arquitetura do Streamlit](https://docs.streamlit.io/develop/concepts/architecture/architecture). Uma pessoa autorizada ainda pode compartilhar um arquivo que baixou.

O conteúdo estático do curso pode estar em cache compartilhado; identidade e anotações não são guardadas nesse cache. A conexão WebSocket da Vercel está sujeita ao limite de duração da função e pode reconectar em outra instância. Exporte seu caderno para conservar as anotações. Entregas, notas e resultados avaliativos não devem ser guardados apenas no estado da sessão.

Containers e WebSockets são recursos beta. O Docker local é opcional para executar Python, mas é necessário para `vercel dev` com containers. O deploy só está validado após testar na URL implantada.

## Conferência após a publicação

- Sem login: nenhuma aula, arquivo docente ou administração deve aparecer.
- Primeiro professor: entrar, trocar a senha e criar uma conta de estudante.
- Estudante: trocar a senha temporária e acessar as aulas, sem **Gerenciar turma** nem materiais exclusivos do professor.
- Professor: bloquear o estudante; sua próxima interação deve exigir novo login e negar acesso enquanto bloqueado.
- Redefinir senha: a antiga deve falhar e a nova deve exigir troca.
- Reiniciar/reimplantar: contas existentes devem continuar válidas e senhas não devem voltar ao bootstrap.
- Exportar/importar caderno e permanecer conectado por alguns minutos: conferir a experiência de reconexão do projeto Vercel.

Referências de hospedagem verificadas em 17/09/2026: [containers](https://vercel.com/docs/functions/container-images), [WebSockets](https://vercel.com/docs/functions/websockets) e [arquitetura do Streamlit](https://docs.streamlit.io/develop/concepts/architecture/architecture).
