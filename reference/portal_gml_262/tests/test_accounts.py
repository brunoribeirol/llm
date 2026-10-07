"""Account invariants, including storage, revocation and competing operations."""
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import sqlite3
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from accounts import (AccountError, AccountStore, AuthenticationError, AuthorizationError,
                      ConfigurationError, RateLimitError, SCRYPT_N, hash_password, verify_password)

INITIAL = "Temporaria-forte-2026"
PERSONAL = "Senha-pessoal-unica-2026"
STUDENT = "Temporaria-aluno-2026"


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.setenv("PORTAL_ENV", "development")
    monkeypatch.setenv("PORTAL_ADMIN_EMAIL", "professor@example.edu")
    monkeypatch.setenv("PORTAL_ADMIN_PASSWORD", INITIAL)
    monkeypatch.setenv("PORTAL_ADMIN_NAME", "Professor")
    clock = [1_800_000_000.0]
    database = AccountStore("sqlite:///" + str(tmp_path / "accounts.db"), clock=lambda: clock[0])
    database.test_clock = clock
    database.initialize()
    return database


@pytest.fixture
def teacher(store):
    initial = store.authenticate("professor@example.edu", INITIAL)
    return store.change_password(initial["token"], INITIAL, PERSONAL)


def test_hashes_are_salted_and_use_required_work_factor():
    first, second = hash_password(INITIAL), hash_password(INITIAL)
    assert SCRYPT_N >= 2**17
    assert first != second
    assert INITIAL not in first
    assert verify_password(INITIAL, first)
    assert not verify_password("wrong", first)
    assert not verify_password(INITIAL, "malformed")
    with pytest.raises(AccountError):
        hash_password("short")


def test_bootstrap_is_idempotent_and_never_resets_existing_password(store, monkeypatch):
    assert store.has_users()
    monkeypatch.setenv("PORTAL_ADMIN_PASSWORD", "Outro-segredo-forte-2026")
    store.initialize()
    assert store.authenticate("professor@example.edu", INITIAL)["user"]["must_change_password"]
    with pytest.raises(AuthenticationError):
        store.authenticate("professor@example.edu", "Outro-segredo-forte-2026")


def test_first_login_must_change_password_before_admin_actions(store):
    login = store.authenticate("  PROFESSOR@example.edu ", INITIAL)
    assert login["user"]["must_change_password"]
    with pytest.raises(AuthorizationError):
        store.create_user(login["token"], "student@example.edu", "Aluno", STUDENT)
    changed = store.change_password(login["token"], INITIAL, PERSONAL)
    assert not changed["user"]["must_change_password"]
    assert store.resolve_session(login["token"]) is None
    assert store.resolve_session(changed["token"])["role"] == "teacher"


def test_create_accounts_enforces_role_and_keeps_hashes_private(store, teacher):
    student = store.create_user(teacher["token"], " Student@example.edu ", "Aluno", STUDENT)
    assert student["email"] == "student@example.edu"
    assert student["role"] == "student"
    assert student["must_change_password"]
    login = store.authenticate(student["email"], STUDENT)
    for operation in (
        lambda: store.list_users(login["token"]),
        lambda: store.create_user(login["token"], "x@example.edu", "Intruso", STUDENT, "teacher"),
        lambda: store.set_active(login["token"], teacher["user"]["id"], False),
        lambda: store.reset_password(login["token"], teacher["user"]["id"], STUDENT),
    ):
        with pytest.raises(AuthorizationError):
            operation()
    assert all("password_hash" not in user and "version" not in user for user in store.list_users(teacher["token"]))
    with pytest.raises(AccountError):
        store.create_user(teacher["token"], "student@example.edu", "Duplicado", STUDENT)


def test_database_never_contains_raw_password_or_session_token(store, teacher):
    data = store.path.read_bytes()
    assert INITIAL.encode() not in data
    assert PERSONAL.encode() not in data
    assert teacher["token"].encode() not in data
    with sqlite3.connect(store.path) as con:
        token_hash = con.execute("SELECT token_hash FROM sessions").fetchone()[0]
        assert len(token_hash) == 64
        assert con.execute("SELECT password_hash FROM users").fetchone()[0].startswith("scrypt$")


def test_logout_expiration_and_version_are_checked_on_every_resolve(store, teacher):
    second = store.authenticate("professor@example.edu", PERSONAL)
    store.logout(second["token"])
    assert store.resolve_session(second["token"]) is None
    assert store.resolve_session(teacher["token"])
    with sqlite3.connect(store.path) as con:
        con.execute("UPDATE users SET version=version+1")
    assert store.resolve_session(teacher["token"]) is None
    fresh = store.authenticate("professor@example.edu", PERSONAL)
    store.test_clock[0] += store.session_seconds + 1
    assert store.resolve_session(fresh["token"]) is None
    assert store.resolve_session("invalid") is None


def test_reset_and_block_revoke_all_sessions_and_require_fresh_password(store, teacher):
    student = store.create_user(teacher["token"], "aluno@example.edu", "Aluno", STUDENT)
    first = store.authenticate(student["email"], STUDENT)
    second = store.authenticate(student["email"], STUDENT)
    reset = "Nova-temporaria-segura-2026"
    store.reset_password(teacher["token"], student["id"], reset)
    assert store.resolve_session(first["token"]) is None
    assert store.resolve_session(second["token"]) is None
    with pytest.raises(AuthenticationError):
        store.authenticate(student["email"], STUDENT)
    current = store.authenticate(student["email"], reset)
    assert current["user"]["must_change_password"]
    store.set_active(teacher["token"], student["id"], False)
    assert store.resolve_session(current["token"]) is None
    with pytest.raises(AuthenticationError, match="E-mail ou senha inválidos"):
        store.authenticate(student["email"], reset)
    store.set_active(teacher["token"], student["id"], True)
    assert store.resolve_session(current["token"]) is None
    assert store.authenticate(student["email"], reset)


def test_cannot_lock_or_reset_self(store, teacher):
    with pytest.raises(AccountError):
        store.set_active(teacher["token"], teacher["user"]["id"], False)
    with pytest.raises(AccountError):
        store.reset_password(teacher["token"], teacher["user"]["id"], STUDENT)
    assert store.resolve_session(teacher["token"])


def test_unknown_and_wrong_password_errors_match_and_sql_injection_fails(store):
    messages = []
    for email, password in [("unknown@example.edu", INITIAL), ("professor@example.edu", "wrong"), ("' OR 1=1 --", INITIAL)]:
        with pytest.raises(AuthenticationError) as error:
            store.authenticate(email, password)
        messages.append(str(error.value))
    assert len(set(messages)) == 1


def test_throttle_is_persistent_atomic_across_concurrent_attempts(store):
    def attempt(_):
        try:
            store.authenticate("professor@example.edu", "wrong-password")
        except RateLimitError:
            return "limited"
        except AuthenticationError:
            return "failed"
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(attempt, range(8)))
    assert results.count("failed") == 5
    assert results.count("limited") == 3
    second_process = AccountStore("sqlite:///" + str(store.path), clock=store.clock)
    with pytest.raises(RateLimitError):
        second_process.authenticate("professor@example.edu", INITIAL)
    store.test_clock[0] += 901
    assert second_process.authenticate("professor@example.edu", INITIAL)


def test_simultaneous_teacher_blocks_cannot_remove_both_teachers(store, teacher):
    another = store.create_user(teacher["token"], "outro@example.edu", "Outro professor", STUDENT, "teacher")
    login = store.authenticate(another["email"], STUDENT)
    other = store.change_password(login["token"], STUDENT, PERSONAL)
    def block(pair):
        token, user_id = pair
        try:
            store.set_active(token, user_id, False)
            return True
        except AccountError:
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(block, [(teacher["token"], another["id"]), (other["token"], teacher["user"]["id"])]))
    assert sum(results) == 1
    with sqlite3.connect(store.path) as con:
        assert con.execute("SELECT COUNT(*) FROM users WHERE role='teacher' AND active=1").fetchone()[0] == 1


def test_production_never_falls_back_to_sqlite(monkeypatch, tmp_path):
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.setenv("PORTAL_ENV", "production")
    for url in ["", "sqlite:///" + str(tmp_path / "unsafe.db")]:
        with pytest.raises(ConfigurationError):
            AccountStore(url)
    monkeypatch.setenv("PORTAL_ENV", "development")
    monkeypatch.setenv("VERCEL", "1")
    with pytest.raises(ConfigurationError):
        AccountStore("")


def test_concurrent_initialization_creates_only_one_bootstrap_user(store):
    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(lambda _: store.initialize(), range(5)))
    with sqlite3.connect(store.path) as con:
        assert con.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1


def test_shared_classroom_ip_allows_many_successful_logins_and_still_limits_failures(store):
    # More than a complete class can authenticate behind one NAT address.
    for _ in range(32):
        assert store.authenticate("professor@example.edu", INITIAL, "classroom-ip")
    for i in range(30):
        with pytest.raises(AuthenticationError) as error:
            store.authenticate(f"unknown-{i}@example.edu", INITIAL, "classroom-ip")
        assert not isinstance(error.value, RateLimitError)
    with pytest.raises(RateLimitError):
        store.authenticate("different@example.edu", INITIAL, "classroom-ip")
