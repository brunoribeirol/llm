"""Container/local entrypoint. Secrets are read from environment, never printed."""
from __future__ import annotations

import os
from pathlib import Path
import sys


def validate_runtime(environ: dict) -> str:
    port = environ.get("PORT", "8501")
    if not port.isascii() or not port.isdecimal() or not 1 <= int(port) <= 65535:
        raise ValueError("PORT precisa ser uma porta TCP válida.")
    production = bool(environ.get("VERCEL")) or environ.get("PORTAL_ENV") == "production"
    if production:
        database = environ.get("DATABASE_URL", "")
        if not database.startswith(("postgres://", "postgresql://")):
            raise ValueError("Configure DATABASE_URL com PostgreSQL persistente para publicar o portal.")
        if len(environ.get("STREAMLIT_SERVER_COOKIE_SECRET", "")) < 32:
            raise ValueError("Configure STREAMLIT_SERVER_COOKIE_SECRET com um segredo aleatório de pelo menos 32 caracteres.")
    return port


def main() -> None:
    os.chdir(Path(__file__).resolve().parent)
    try:
        port = validate_runtime(dict(os.environ))
    except ValueError as exc:
        sys.exit(str(exc))
    os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", f"--server.port={port}"])


if __name__ == "__main__":
    main()
