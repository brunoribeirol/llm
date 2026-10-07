from pathlib import Path
import sys
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from accounts import AccountStore
from start import validate_runtime


@pytest.fixture
def store(tmp_path, monkeypatch):
    for key in ("VERCEL", "PORTAL_ENV", "DATABASE_URL", "PORTAL_ADMIN_EMAIL", "PORTAL_ADMIN_PASSWORD", "PORTAL_ADMIN_NAME"):
        monkeypatch.delenv(key, raising=False)
    db = AccountStore(f"sqlite:///{tmp_path / 'auth-tests.db'}")
    db.initialize()
    return db


def auth_app():
    return AppTest.from_string("from auth import require_user\nimport streamlit as st\nuser = require_user()\nst.write('PROTECTED_CONTENT')", default_timeout=15)


def test_unconfigured_portal_stops_before_course_content(store):
    app = auth_app()
    with patch("auth.get_store", return_value=store):
        app.run()
    assert not app.exception
    assert len(app.info) == 1
    assert not any("PROTECTED_CONTENT" in str(item.value) for item in app.markdown)


def test_first_login_forces_password_change_before_course(store, monkeypatch):
    monkeypatch.setenv("PORTAL_ADMIN_EMAIL", "professor@example.edu")
    monkeypatch.setenv("PORTAL_ADMIN_PASSWORD", "SenhaTemporaria-123")
    monkeypatch.setenv("PORTAL_ADMIN_NAME", "Professor")
    store.initialize()
    app = auth_app()
    with patch("auth.get_store", return_value=store):
        app.run()
        app.text_input(key="login_email").set_value("professor@example.edu")
        app.text_input(key="login_password").set_value("SenhaTemporaria-123")
        app.button[0].click().run()
        assert not app.exception
        assert any(widget.label == "Nova senha" for widget in app.text_input)
        assert not any("PROTECTED_CONTENT" in str(item.value) for item in app.markdown)
        for widget in app.text_input:
            if widget.label == "Senha atual":
                widget.set_value("SenhaTemporaria-123")
            else:
                widget.set_value("MinhaNovaSenha-456")
        next(button for button in app.button if button.label == "Salvar nova senha").click().run()
    assert not app.exception
    assert any("PROTECTED_CONTENT" in str(item.value) for item in app.markdown)


def test_unavailable_account_database_fails_closed_without_details():
    app = auth_app()
    with patch("auth.get_store", side_effect=RuntimeError("DATABASE_PASSWORD_DO_NOT_EXPOSE")):
        app.run()
    assert not app.exception
    assert app.error
    assert "DATABASE_PASSWORD" not in str(app.error[0].value)
    assert not any("PROTECTED_CONTENT" in str(item.value) for item in app.markdown)


@pytest.mark.parametrize("port", ["0", "65536", "abc", "80; echo bad", "１２３"])
def test_start_rejects_invalid_ports(port):
    with pytest.raises(ValueError):
        validate_runtime({"PORT": port})


def test_production_requires_persistent_database_and_shared_cookie_secret():
    assert validate_runtime({}) == "8501"
    with pytest.raises(ValueError, match="PostgreSQL"):
        validate_runtime({"PORTAL_ENV": "production"})
    with pytest.raises(ValueError, match="COOKIE_SECRET"):
        validate_runtime({"VERCEL": "1", "DATABASE_URL": "postgresql://example/test"})
    assert validate_runtime({"PORT": "80", "PORTAL_ENV": "production", "DATABASE_URL": "postgresql://example/test", "STREAMLIT_SERVER_COOKIE_SECRET": "x" * 64}) == "80"
