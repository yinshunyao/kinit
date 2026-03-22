# -*- coding: utf-8 -*-
import pytest

from application.redis_config import resolve_redis_db_url


def test_resolve_disabled():
    assert resolve_redis_db_url(False) == ""


def test_resolve_enabled_missing(monkeypatch):
    monkeypatch.delenv("KINIT_REDIS_URL", raising=False)
    with pytest.raises(RuntimeError, match="KINIT_REDIS_URL"):
        resolve_redis_db_url(True)


def test_resolve_ok(monkeypatch):
    monkeypatch.setenv("KINIT_REDIS_URL", "redis://localhost:6379/0")
    assert resolve_redis_db_url(True) == "redis://localhost:6379/0"


def test_resolve_strips_whitespace(monkeypatch):
    monkeypatch.setenv("KINIT_REDIS_URL", "  redis://127.0.0.1:6379/1  ")
    assert resolve_redis_db_url(True) == "redis://127.0.0.1:6379/1"


def test_resolve_with_password_in_url(monkeypatch):
    monkeypatch.setenv("KINIT_REDIS_URL", "redis://:secret@127.0.0.1:6379/1")
    assert resolve_redis_db_url(True) == "redis://:secret@127.0.0.1:6379/1"


def test_resolve_rediss(monkeypatch):
    monkeypatch.setenv("KINIT_REDIS_URL", "rediss://user:pass@example.com:6380/0")
    assert resolve_redis_db_url(True).startswith("rediss://")


def test_invalid_scheme(monkeypatch):
    monkeypatch.setenv("KINIT_REDIS_URL", "http://localhost:6379")
    with pytest.raises(ValueError, match="redis://"):
        resolve_redis_db_url(True)
