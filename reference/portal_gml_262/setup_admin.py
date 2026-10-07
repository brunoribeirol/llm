"""Create the first teacher locally without putting passwords in shell history."""
from __future__ import annotations

from getpass import getpass
import os
import sys

from accounts import AccountStore, AccountError


def main() -> int:
    try:
        store = AccountStore()
        store.initialize()
        if store.has_users():
            print("O banco já possui contas. Entre como professor e use Gerenciar turma; o bootstrap não altera senhas existentes.")
            return 1
        print("Criar o primeiro professor. A senha não será exibida nem enviada por e-mail.")
        name = input("Nome: ").strip()
        email = input("E-mail: ").strip()
        password = getpass("Senha temporária (mínimo de 12 caracteres): ")
        if password != getpass("Confirme a senha: "):
            print("As senhas não coincidem. Nenhuma conta foi criada.")
            return 1
        values = {"PORTAL_ADMIN_EMAIL": email, "PORTAL_ADMIN_NAME": name, "PORTAL_ADMIN_PASSWORD": password}
        old = {key: os.environ.get(key) for key in values}
        try:
            os.environ.update(values)
            store.initialize()
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        print("Professor criado. Execute python start.py, entre e substitua a senha temporária no primeiro acesso.")
        return 0
    except AccountError as exc:
        print(str(exc))
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nConfiguração cancelada.")
        return 1
    except Exception:
        print("Não foi possível configurar a conta. Verifique o acesso ao banco e README-AUTENTICACAO.md.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
