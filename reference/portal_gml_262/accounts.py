"""Password accounts and revocable sessions, backed by SQLite or PostgreSQL.

All writes serialize through a database transaction (SQLite IMMEDIATE or a
PostgreSQL transaction advisory lock), including login throttling and bootstrap.
No raw password or session token is ever persisted. No public registration API.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import hmac
import os
from pathlib import Path
import re
import secrets
import sqlite3
import time
from urllib.parse import unquote
import uuid

SCRYPT_N = 2**17
SCRYPT_R = 8
SCRYPT_P = 1
SESSION_SECONDS = 12 * 60 * 60
RATE_WINDOW = 15 * 60
_DUMMY_HASH = f"scrypt${SCRYPT_N}$8$1$" + "00" * 16 + "$" + "00" * 32
_LOCK_ID = 713804196


class AccountError(ValueError):
    """Safe, user-facing account operation failure."""


class AuthenticationError(AccountError):
    pass


class AuthorizationError(AccountError):
    pass


class RateLimitError(AuthenticationError):
    pass


class ConfigurationError(AccountError):
    pass


def normalize_email(value: str) -> str:
    email = str(value or "").strip().casefold()
    if len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise AccountError("Informe um e-mail válido.")
    return email


def validate_password(password: str) -> None:
    if not isinstance(password, str) or not 12 <= len(password) <= 1024:
        raise AccountError("A senha deve ter entre 12 e 1.024 caracteres.")


def hash_password(password: str) -> str:
    validate_password(password)
    salt = secrets.token_bytes(16)
    result = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P,
                            dklen=32, maxmem=256 * 1024 * 1024)
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${result.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    if not isinstance(password, str) or len(password) > 1024:
        return False
    try:
        algorithm, n, r, p, salt, digest = encoded.split("$")
        if algorithm != "scrypt" or (int(n), int(r), int(p)) != (SCRYPT_N, SCRYPT_R, SCRYPT_P):
            return False
        if len(salt) != 32 or len(digest) != 64:
            return False
        result = hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p),
                                dklen=32, maxmem=256 * 1024 * 1024)
        return hmac.compare_digest(result, bytes.fromhex(digest))
    except (TypeError, ValueError):
        return False


def _public(row) -> dict:
    return {"id": row["id"], "email": row["email"], "name": row["name"], "role": row["role"],
            "active": bool(row["active"]), "must_change_password": bool(row["must_change_password"])}


class AccountStore:
    def __init__(self, database_url: str | None = None, *, session_seconds: int = SESSION_SECONDS,
                 clock=None, environment: str | None = None):
        url = database_url if database_url is not None else os.environ.get("DATABASE_URL", "")
        production = (environment or os.environ.get("PORTAL_ENV", "")).casefold() == "production" or bool(os.environ.get("VERCEL"))
        self.postgres = url.startswith(("postgres://", "postgresql://"))
        if production and not self.postgres:
            raise ConfigurationError("Em produção, configure DATABASE_URL para um PostgreSQL persistente.")
        if url and not self.postgres and not url.startswith("sqlite:///"):
            raise ConfigurationError("DATABASE_URL deve usar postgresql:// ou sqlite:/// (somente local).")
        self.database_url = url if self.postgres else ""
        self.path = None if self.postgres else (Path(unquote(url[len("sqlite:///"):])) if url else Path(__file__).resolve().parent / ".data" / "portal.db")
        if not self.postgres:
            self.path = self.path.resolve()
            self.path.parent.mkdir(parents=True, exist_ok=True)
        if not 60 <= session_seconds <= 7 * 24 * 3600:
            raise ConfigurationError("Duração de sessão inválida.")
        self.session_seconds = session_seconds
        self.clock = clock or time.time

    @contextmanager
    def _connection(self, *, write: bool = False):
        if self.postgres:
            try:
                import psycopg
                from psycopg.rows import dict_row
            except ImportError as exc:
                raise ConfigurationError("Instale psycopg[binary] para utilizar PostgreSQL.") from exc
            connection = psycopg.connect(self.database_url, row_factory=dict_row, connect_timeout=10)
        else:
            connection = sqlite3.connect(self.path, timeout=30)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
        try:
            if write:
                if self.postgres:
                    connection.execute("SELECT pg_advisory_xact_lock(%s)", (_LOCK_ID,))
                else:
                    connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _sql(self, connection, sql, params=()):
        return connection.execute(sql.replace("?", "%s") if self.postgres else sql, params)

    def initialize(self) -> None:
        with self._connection(write=True) as con:
            for statement in (
                "CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, name TEXT NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('teacher','student')), active INTEGER NOT NULL DEFAULT 1, must_change_password INTEGER NOT NULL DEFAULT 1, version INTEGER NOT NULL DEFAULT 1, created_at DOUBLE PRECISION NOT NULL)",
                "CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), version INTEGER NOT NULL, expires_at DOUBLE PRECISION NOT NULL, created_at DOUBLE PRECISION NOT NULL)",
                "CREATE INDEX IF NOT EXISTS sessions_user ON sessions(user_id)",
                "CREATE TABLE IF NOT EXISTS login_attempts (bucket TEXT PRIMARY KEY, window_start DOUBLE PRECISION NOT NULL, attempts INTEGER NOT NULL)",
            ):
                self._sql(con, statement)
            # Bootstrap once; restarting never overwrites existing account credentials.
            exists = self._sql(con, "SELECT id FROM users LIMIT 1").fetchone()
            email = os.environ.get("PORTAL_ADMIN_EMAIL", "")
            password = os.environ.get("PORTAL_ADMIN_PASSWORD", "")
            if not exists and (email or password):
                if not email or not password:
                    raise ConfigurationError("Configure PORTAL_ADMIN_EMAIL e PORTAL_ADMIN_PASSWORD para criar o primeiro professor.")
                self._insert_user(con, email, os.environ.get("PORTAL_ADMIN_NAME", "Professor"), password, "teacher")
            self._sql(con, "DELETE FROM sessions WHERE expires_at <= ?", (self.clock(),))
            self._sql(con, "DELETE FROM login_attempts WHERE window_start < ?", (self.clock() - RATE_WINDOW * 2,))

    def has_users(self) -> bool:
        with self._connection() as con:
            return self._sql(con, "SELECT id FROM users LIMIT 1").fetchone() is not None

    def _insert_user(self, con, email, name, password, role):
        email = normalize_email(email)
        if role not in {"student", "teacher"}:
            raise AccountError("Perfil inválido.")
        name = str(name or "").strip()
        if not name or len(name) > 120:
            raise AccountError("Informe um nome com até 120 caracteres.")
        if self._sql(con, "SELECT id FROM users WHERE email = ?", (email,)).fetchone():
            raise AccountError("Já existe uma conta com esse e-mail.")
        identifier = str(uuid.uuid4())
        self._sql(con, "INSERT INTO users(id,email,name,password_hash,role,active,must_change_password,version,created_at) VALUES(?,?,?,?,?,1,1,1,?)",
                  (identifier, email, name, hash_password(password), role, self.clock()))
        return _public(self._sql(con, "SELECT * FROM users WHERE id = ?", (identifier,)).fetchone())

    def _throttle(self, con, email: str, client_key: str):
        now = self.clock()
        buckets = [("email:" + hashlib.sha256(email.encode()).hexdigest(), 5)]
        if client_key:
            buckets.append(("client:" + hashlib.sha256(str(client_key).encode()).hexdigest(), 30))
        for bucket, limit in buckets:
            row = self._sql(con, "SELECT * FROM login_attempts WHERE bucket = ?", (bucket,)).fetchone()
            if row and row["window_start"] > now - RATE_WINDOW and row["attempts"] >= limit:
                raise RateLimitError("Não foi possível entrar. Aguarde alguns minutos e tente novamente.")
        for bucket, _ in buckets:
            row = self._sql(con, "SELECT * FROM login_attempts WHERE bucket = ?", (bucket,)).fetchone()
            if row and row["window_start"] > now - RATE_WINDOW:
                self._sql(con, "UPDATE login_attempts SET attempts = attempts + 1 WHERE bucket = ?", (bucket,))
            else:
                self._sql(con, "INSERT INTO login_attempts(bucket,window_start,attempts) VALUES(?,?,1) ON CONFLICT(bucket) DO UPDATE SET window_start=excluded.window_start, attempts=1", (bucket, now))

    def _new_session(self, con, row):
        token = secrets.token_urlsafe(32)
        now = self.clock()
        self._sql(con, "INSERT INTO sessions(token_hash,user_id,version,expires_at,created_at) VALUES(?,?,?,?,?)",
                  (hashlib.sha256(token.encode()).hexdigest(), row["id"], row["version"], now + self.session_seconds, now))
        return {"token": token, "user": _public(row)}

    def authenticate(self, email: str, password: str, client_key: str = "") -> dict:
        # Invalid and unknown e-mails follow the same expensive verification path.
        normalized = str(email or "").strip().casefold()[:1024]
        result = None
        with self._connection(write=True) as con:
            self._throttle(con, normalized, client_key)
            row = self._sql(con, "SELECT * FROM users WHERE email = ?", (normalized,)).fetchone()
            valid = verify_password(password, row["password_hash"] if row else _DUMMY_HASH)
            if valid and row and row["active"]:
                self._sql(con, "DELETE FROM login_attempts WHERE bucket = ?", ("email:" + hashlib.sha256(normalized.encode()).hexdigest(),))
                if client_key:
                    # A classroom may share one public IP. Successful logins do
                    # not consume the client's failed-attempt budget.
                    self._sql(con, "UPDATE login_attempts SET attempts=CASE WHEN attempts>0 THEN attempts-1 ELSE 0 END WHERE bucket=?",
                              ("client:" + hashlib.sha256(str(client_key).encode()).hexdigest(),))
                result = self._new_session(con, row)
        # Raise outside the transaction so failed attempts remain persisted.
        if result is None:
            raise AuthenticationError("E-mail ou senha inválidos.")
        return result

    def _session_user(self, con, token: str):
        if not isinstance(token, str) or not 40 <= len(token) <= 128:
            return None
        row = self._sql(con, "SELECT u.* FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.token_hash=? AND s.expires_at>? AND s.version=u.version AND u.active=1",
                        (hashlib.sha256(token.encode()).hexdigest(), self.clock())).fetchone()
        return row

    def resolve_session(self, token: str) -> dict | None:
        with self._connection() as con:
            row = self._session_user(con, token)
            return _public(row) if row else None

    def logout(self, token: str) -> None:
        if not isinstance(token, str):
            return
        with self._connection(write=True) as con:
            self._sql(con, "DELETE FROM sessions WHERE token_hash=?", (hashlib.sha256(token.encode()).hexdigest(),))

    def _actor(self, con, token, *, teacher=False):
        row = self._session_user(con, token)
        if not row:
            raise AuthenticationError("Sua sessão expirou. Entre novamente.")
        if teacher and (row["role"] != "teacher" or row["must_change_password"]):
            raise AuthorizationError("Esta ação exige uma conta de professor com senha pessoal definida.")
        return row

    def change_password(self, token: str, current: str, new: str) -> dict:
        validate_password(new)
        with self._connection(write=True) as con:
            row = self._actor(con, token)
            if not verify_password(current, row["password_hash"]):
                raise AuthenticationError("A senha atual está incorreta.")
            if hmac.compare_digest(current.encode(), new.encode()):
                raise AccountError("Escolha uma senha diferente da senha atual.")
            self._sql(con, "UPDATE users SET password_hash=?, must_change_password=0, version=version+1 WHERE id=?", (hash_password(new), row["id"]))
            self._sql(con, "DELETE FROM sessions WHERE user_id=?", (row["id"],))
            updated = self._sql(con, "SELECT * FROM users WHERE id=?", (row["id"],)).fetchone()
            return self._new_session(con, updated)

    def create_user(self, actor_token: str, email: str, name: str, password: str, role: str = "student") -> dict:
        with self._connection(write=True) as con:
            self._actor(con, actor_token, teacher=True)
            return self._insert_user(con, email, name, password, role)

    def list_users(self, actor_token: str) -> list[dict]:
        with self._connection() as con:
            self._actor(con, actor_token, teacher=True)
            return [_public(row) for row in self._sql(con, "SELECT * FROM users ORDER BY name,email").fetchall()]

    def set_active(self, actor_token: str, user_id: str, active: bool) -> None:
        if not isinstance(active, bool):
            raise AccountError("Estado da conta inválido.")
        with self._connection(write=True) as con:
            actor = self._actor(con, actor_token, teacher=True)
            row = self._sql(con, "SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            if not row:
                raise AccountError("Conta não encontrada.")
            if not active and row["id"] == actor["id"]:
                raise AccountError("Você não pode bloquear sua própria conta.")
            if not active and row["role"] == "teacher" and row["active"]:
                count = self._sql(con, "SELECT COUNT(*) AS n FROM users WHERE role='teacher' AND active=1").fetchone()["n"]
                if count <= 1:
                    raise AccountError("Mantenha pelo menos um professor ativo.")
            self._sql(con, "UPDATE users SET active=?, version=version+1 WHERE id=?", (int(active), user_id))
            self._sql(con, "DELETE FROM sessions WHERE user_id=?", (user_id,))

    def reset_password(self, actor_token: str, user_id: str, temporary: str) -> None:
        validate_password(temporary)
        with self._connection(write=True) as con:
            actor = self._actor(con, actor_token, teacher=True)
            row = self._sql(con, "SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            if not row:
                raise AccountError("Conta não encontrada.")
            if row["id"] == actor["id"]:
                raise AccountError("Para sua própria conta, use a opção de trocar senha.")
            self._sql(con, "UPDATE users SET password_hash=?, must_change_password=1, version=version+1 WHERE id=?", (hash_password(temporary), user_id))
            self._sql(con, "DELETE FROM sessions WHERE user_id=?", (user_id,))
