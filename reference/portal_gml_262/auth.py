"""Email/password login, teacher-managed accounts and server-side sessions."""
from __future__ import annotations

import streamlit as st

from accounts import AccountStore, AccountError

TOKEN_KEY = "portal_session_token"


@st.cache_resource
def get_store() -> AccountStore:
    store = AccountStore()
    store.initialize()
    return store


def _login_header() -> None:
    st.markdown('<div class="course-kicker">GRANDES MODELOS DE LINGUAGEM</div>', unsafe_allow_html=True)
    st.title("Do Transformer aos Agentes de IA")
    st.markdown('<p class="course-lead">Aulas, experimentos e demonstrações para explorar o curso, passo a passo.</p>', unsafe_allow_html=True)


def _clear_identity() -> None:
    st.session_state.clear()


def require_user() -> dict:
    """Stop before course rendering until login and any mandatory change succeed."""
    try:
        store = get_store()
        token = st.session_state.get(TOKEN_KEY)
        user = store.resolve_session(token) if token else None
        has_users = store.has_users()
    except Exception:
        _login_header()
        st.error("O acesso está temporariamente indisponível. O responsável precisa verificar a configuração do portal.")
        st.stop()
    if token and user is None:
        _clear_identity()
        st.info("Sua sessão terminou. Entre novamente para continuar.")
    if not has_users:
        _login_header()
        st.info("O responsável está preparando o acesso da turma.")
        with st.expander("Orientações para o responsável"):
            st.write("Para configurar o primeiro professor neste computador, execute `python setup_admin.py` na pasta do portal. Para publicação, siga README-AUTENTICACAO.md.")
        st.stop()
    if user is None:
        _login_header()
        with st.container(border=True):
            st.subheader("Entre para continuar")
            st.write("Use o e-mail e a senha cadastrados pelo professor.")
            with st.form("portal_login", clear_on_submit=True):
                email = st.text_input("E-mail", max_chars=254, key="login_email")
                password = st.text_input("Senha", type="password", max_chars=1024, key="login_password")
                submitted = st.form_submit_button("Entrar", type="primary", width="stretch")
            if submitted:
                try:
                    result = store.authenticate(email, password, client_key=st.context.ip_address or "")
                except AccountError as exc:
                    st.error(str(exc))
                except Exception:
                    st.error("Não foi possível entrar agora. Tente novamente em alguns instantes.")
                else:
                    _clear_identity()
                    st.session_state[TOKEN_KEY] = result["token"]
                    st.rerun()
            st.caption("Não há cadastro público. Para receber acesso ou redefinir sua senha, contate o professor.")
        st.stop()
    if user["must_change_password"]:
        _login_header()
        st.info("Antes de acessar o curso, substitua a senha temporária por uma senha pessoal.")
        _password_form(store)
        logout_button()
        st.stop()
    return user


def logout_button() -> None:
    if st.button("Sair", key="portal_logout", width="stretch"):
        token = st.session_state.get(TOKEN_KEY)
        if token:
            try:
                get_store().logout(token)
            except Exception:
                pass
        _clear_identity()
        st.query_params.clear()
        st.rerun()


def _password_form(store: AccountStore) -> None:
    with st.form("portal_change_password", clear_on_submit=True):
        current = st.text_input("Senha atual", type="password", max_chars=1024)
        new = st.text_input("Nova senha", type="password", max_chars=1024, help="Use no mínimo 12 caracteres. Prefira uma frase longa e exclusiva.")
        confirm = st.text_input("Confirme a nova senha", type="password", max_chars=1024)
        submitted = st.form_submit_button("Salvar nova senha", type="primary")
    if submitted:
        if new != confirm:
            st.error("As novas senhas não coincidem.")
            return
        try:
            result = store.change_password(st.session_state.get(TOKEN_KEY, ""), current, new)
        except AccountError as exc:
            st.error(str(exc))
        except Exception:
            st.error("Não foi possível alterar a senha agora. Tente novamente.")
        else:
            st.session_state[TOKEN_KEY] = result["token"]
            st.session_state["password_changed_notice"] = True
            st.rerun()


def render_password_settings() -> None:
    user = require_user()
    st.subheader("Minha conta")
    st.write(f'{user["name"]} · {user["email"]}')
    if st.session_state.pop("password_changed_notice", False):
        st.success("Senha alterada. As outras sessões desta conta foram encerradas.")
    st.caption("A nova senha encerra as outras sessões da sua conta. Ela não é enviada por e-mail.")
    _password_form(get_store())


def render_account_admin() -> None:
    user = require_user()
    if user["role"] != "teacher":
        st.error("Este recurso é exclusivo do professor.")
        return
    store = get_store()
    token = st.session_state[TOKEN_KEY]
    st.subheader("Gerenciar turma")
    if notice := st.session_state.pop("accounts_notice", None):
        st.success(notice)
    st.write("Cadastre os alunos e entregue a senha temporária por um canal privado. Cada pessoa deverá alterá-la no primeiro acesso.")
    with st.expander("Cadastrar conta", expanded=True):
        with st.form("portal_create_account", clear_on_submit=True):
            name = st.text_input("Nome", max_chars=100)
            email = st.text_input("E-mail da nova conta", max_chars=254)
            password = st.text_input("Senha temporária", type="password", max_chars=1024, help="Mínimo de 12 caracteres. Não use uma senha compartilhada pela turma.")
            role = st.selectbox("Perfil", ["student", "teacher"], format_func=lambda x: "Estudante" if x == "student" else "Professor")
            create = st.form_submit_button("Criar conta", type="primary")
        if create:
            try:
                store.create_user(token, email, name, password, role=role)
            except AccountError as exc:
                st.error(str(exc))
            except Exception:
                st.error("Não foi possível cadastrar a conta agora.")
            else:
                st.session_state["accounts_notice"] = "Conta criada. Entregue a senha temporária à pessoa cadastrada; o portal não envia mensagens."
                st.rerun()
    try:
        users = store.list_users(token)
    except Exception:
        st.error("Não foi possível consultar a turma agora.")
        return
    st.dataframe([{ "Nome": account["name"], "E-mail": account["email"], "Perfil": "Professor" if account["role"] == "teacher" else "Estudante", "Acesso": "Ativo" if account["active"] else "Bloqueado", "Troca pendente": "Sim" if account["must_change_password"] else "Não"} for account in users], hide_index=True, width="stretch")
    if not users:
        return
    selected_id = st.selectbox("Conta a gerenciar", [account["id"] for account in users], format_func=lambda value: next(f'{a["name"]} · {a["email"]}' for a in users if a["id"] == value))
    selected = next(account for account in users if account["id"] == selected_id)
    if selected["id"] == user["id"]:
        st.caption("Para alterar sua própria senha, use Minha conta. Sua conta não pode ser bloqueada por esta tela.")
        return
    action = "Bloquear acesso" if selected["active"] else "Desbloquear acesso"
    if st.button(action, key="toggle_account_active"):
        try:
            store.set_active(token, selected_id, not selected["active"])
        except AccountError as exc:
            st.error(str(exc))
        except Exception:
            st.error("Não foi possível atualizar o acesso agora.")
        else:
            st.session_state["accounts_notice"] = "Acesso atualizado. O bloqueio encerra as sessões da conta."
            st.rerun()
    with st.form("portal_reset_password", clear_on_submit=True):
        temporary = st.text_input("Nova senha temporária", type="password", max_chars=1024, help="Mínimo de 12 caracteres.")
        reset = st.form_submit_button("Redefinir senha e encerrar sessões")
    if reset:
        try:
            store.reset_password(token, selected_id, temporary)
        except AccountError as exc:
            st.error(str(exc))
        except Exception:
            st.error("Não foi possível redefinir a senha agora.")
        else:
            st.session_state["accounts_notice"] = "Senha temporária redefinida. A pessoa deverá alterá-la ao entrar novamente."
            st.rerun()
