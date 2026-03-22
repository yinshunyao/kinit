# -*- coding: utf-8 -*-
from application.env_config import env_int, env_str


def test_env_str_default(monkeypatch):
    monkeypatch.delenv("KINIT_ENV_STR_TEST", raising=False)
    assert env_str("KINIT_ENV_STR_TEST", "default") == "default"


def test_env_str_strips(monkeypatch):
    monkeypatch.setenv("KINIT_ENV_STR_TEST", "  v  ")
    assert env_str("KINIT_ENV_STR_TEST", "default") == "v"


def test_env_str_empty_uses_default(monkeypatch):
    monkeypatch.setenv("KINIT_ENV_STR_TEST", "   ")
    assert env_str("KINIT_ENV_STR_TEST", "default") == "default"


def test_env_int_default(monkeypatch):
    monkeypatch.delenv("KINIT_ENV_INT_TEST", raising=False)
    assert env_int("KINIT_ENV_INT_TEST", 9000) == 9000


def test_env_int_value(monkeypatch):
    monkeypatch.setenv("KINIT_ENV_INT_TEST", "8080")
    assert env_int("KINIT_ENV_INT_TEST", 9000) == 8080


def test_env_int_empty_uses_default(monkeypatch):
    monkeypatch.setenv("KINIT_ENV_INT_TEST", "")
    assert env_int("KINIT_ENV_INT_TEST", 9000) == 9000
