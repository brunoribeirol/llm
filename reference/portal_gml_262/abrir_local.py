"""Start the local portal and bootstrap a teacher only if the local DB is empty."""
from pathlib import Path
import argparse
import os
import secrets
import socket
import subprocess
import sys
import time
from urllib.request import urlopen
import webbrowser

ROOT = Path(__file__).resolve().parent
PORT = 8501


def main():
    parser = argparse.ArgumentParser(description="Iniciar o portal local preservando as contas existentes.")
    parser.add_argument("--port", type=int, default=PORT, help="Porta local (padrão: 8501).")
    parser.add_argument("--no-browser", action="store_true", help="Iniciar sem abrir o navegador.")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("A porta deve estar entre 1 e 65535.")
    port = args.port
    url = f"http://localhost:{port}"
    os.chdir(ROOT)
    with socket.socket() as connection:
        connection.settimeout(1)
        occupied = connection.connect_ex(("127.0.0.1", port)) == 0
    if occupied:
        print(f"A porta {port} ja esta em uso. Nenhum processo ou conta foi alterado.", flush=True)
        return 1

    # This launcher always uses a local database and never a production account.
    os.environ.pop("VERCEL", None)
    for key in ("PORTAL_ADMIN_EMAIL", "PORTAL_ADMIN_NAME", "PORTAL_ADMIN_PASSWORD"):
        os.environ.pop(key, None)
    os.environ["PORTAL_ENV"] = "development"
    os.environ["DATABASE_URL"] = "sqlite:///" + str(ROOT / ".data" / "portal.db")
    from accounts import AccountStore

    store = AccountStore()
    store.initialize()
    if not store.has_users():
        email = "professor@portal.local"
        password = secrets.token_urlsafe(18)
        os.environ.update(PORTAL_ADMIN_EMAIL=email, PORTAL_ADMIN_NAME="Professor local", PORTAL_ADMIN_PASSWORD=password)
        store.initialize()
        # Confirm the credentials before handing them to the user.
        session = store.authenticate(email, password)
        store.logout(session["token"])
        for key in ("PORTAL_ADMIN_EMAIL", "PORTAL_ADMIN_NAME", "PORTAL_ADMIN_PASSWORD"):
            os.environ.pop(key, None)
        print(f"CONTA_LOCAL={email}\nSENHA_TEMPORARIA={password}", flush=True)
        print("Troque a senha no primeiro acesso. A senha temporaria nao foi salva em arquivo.", flush=True)
    else:
        print("As contas locais existentes foram preservadas.", flush=True)

    flags = 0
    if sys.platform == "win32":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    log_path = ROOT / ".data" / "servidor-local.log"
    with log_path.open("a", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.address=127.0.0.1", f"--server.port={port}", "--server.headless=true"],
            cwd=ROOT, env=dict(os.environ), stdin=subprocess.DEVNULL, stdout=log, stderr=log,
            creationflags=flags, start_new_session=sys.platform != "win32",
        )
    (ROOT / ".data" / "servidor-local.pid").write_text(str(process.pid), encoding="ascii")
    print(f"PROCESSO={process.pid}\nENDERECO={url}", flush=True)
    for _ in range(90):
        if process.poll() is not None:
            print(f"O servidor encerrou. Consulte {log_path}", flush=True)
            return 1
        try:
            with urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1) as response:
                if response.status == 200:
                    print("SERVIDOR_PRONTO", flush=True)
                    if not args.no_browser:
                        webbrowser.open(url)
                    return 0
        except OSError:
            pass
        time.sleep(1)
    print(f"Servidor iniciado, mas a verificacao demorou. Consulte {log_path}", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
