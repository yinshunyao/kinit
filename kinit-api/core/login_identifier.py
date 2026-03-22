#!/usr/bin/python
# -*- coding: utf-8 -*-
"""登录标识：密码登录支持手机号或 name（账号，须含字母）。"""
from __future__ import annotations

from typing import Literal

from core.validator import vali_telephone

LoginLookupKind = Literal["telephone", "name"]


def is_china_mobile(value: str) -> bool:
    try:
        vali_telephone(value)
        return True
    except ValueError:
        return False


def validate_password_login_identifier(raw: str) -> str:
    """
    密码登录标识校验（Pydantic / 接口层）：通过则返回 strip 后的字符串。
    """
    s = (raw or "").strip()
    if not s:
        raise ValueError("请输入手机号或账号")
    if is_china_mobile(s):
        return s
    if any(c.isalpha() for c in s):
        if len(s) > 50:
            raise ValueError("账号过长")
        return s
    if s.isdigit() and len(s) == 11:
        raise ValueError("请输入正确手机号")
    raise ValueError("账号须包含字母")


def classify_password_login_identifier(raw: str) -> tuple[LoginLookupKind, str]:
    """
    将已校验的标识分为按 telephone 或 name 查询。
    """
    s = validate_password_login_identifier(raw)
    if is_china_mobile(s):
        return ("telephone", s)
    return ("name", s)
