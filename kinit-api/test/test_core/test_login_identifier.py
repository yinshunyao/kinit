# -*- coding: utf-8 -*-
import pytest

from core.login_identifier import (
    classify_password_login_identifier,
    is_china_mobile,
    validate_password_login_identifier,
)
from scripts.initialize.user_password import prepare_vadmin_auth_user_rows


def test_is_china_mobile_ok():
    assert is_china_mobile("13800138000") is True


def test_is_china_mobile_bad_segment():
    assert is_china_mobile("12800138000") is False


def test_validate_password_login_mobile():
    assert validate_password_login_identifier(" 13800138000 ") == "13800138000"


def test_validate_password_login_name():
    assert validate_password_login_identifier("admin") == "admin"


def test_validate_password_login_11_digit_invalid():
    with pytest.raises(ValueError, match="请输入正确手机号"):
        validate_password_login_identifier("12800138000")


def test_validate_password_login_no_letter_short():
    with pytest.raises(ValueError, match="账号须包含字母"):
        validate_password_login_identifier("12345")


def test_classify_telephone():
    assert classify_password_login_identifier("13800138000") == ("telephone", "13800138000")


def test_classify_name():
    assert classify_password_login_identifier("kinitAdmin") == ("name", "kinitAdmin")


def test_prepare_vadmin_auth_user_rows_plaintext():
    rows = [{"name": "a", "password": "plain-secret"}]
    out = prepare_vadmin_auth_user_rows(rows)
    assert out[0]["password"].startswith("$2")
    assert out[0]["password"] != "plain-secret"


def test_prepare_vadmin_auth_user_rows_already_bcrypt():
    hashed = "$2b$12$Ce7eSUKIIl8DMKeDyNHyr.Dp4aesQCM70RePigRVEny1Eql31R0Cq"
    rows = [{"name": "a", "password": hashed}]
    out = prepare_vadmin_auth_user_rows(rows)
    assert out[0]["password"] == hashed


def test_prepare_vadmin_auth_user_rows_excel_integer_password():
    rows = [{"name": "a", "password": 12345678}]
    out = prepare_vadmin_auth_user_rows(rows)
    assert out[0]["password"].startswith("$2")
    assert "12345678" not in out[0]["password"]


def test_prepare_vadmin_auth_user_rows_password_header_chinese():
    rows = [{"name": "a", "密码": "plain-secret"}]
    out = prepare_vadmin_auth_user_rows(rows)
    assert "密码" not in out[0]
    assert out[0]["password"].startswith("$2")


def test_prepare_vadmin_auth_user_rows_float_integer_password():
    rows = [{"name": "a", "password": 12345.0}]
    out = prepare_vadmin_auth_user_rows(rows)
    assert out[0]["password"].startswith("$2")
