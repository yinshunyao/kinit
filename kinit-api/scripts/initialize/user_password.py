#!/usr/bin/python
# -*- coding: utf-8 -*-
"""初始化用户表行：Excel 明文 password → bcrypt（与 VadminUser 使用相同 passlib 配置）。"""

from __future__ import annotations

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Excel 表头常见别名（首列命中即用）
_PASSWORD_HEADER_ALIASES = ("password", "Password", "PASSWORD", "密码", "用户密码")


def _looks_like_bcrypt(value: str) -> bool:
    s = value.strip()
    if len(s) < 59:
        return False
    return s.startswith("$2a$") or s.startswith("$2b$") or s.startswith("$2y$")


def _cell_to_password_str(pw) -> str | None:
    """将 Excel 单元格（数字、字符串等）规范为待处理密码字符串。"""
    if pw is None:
        return None
    if isinstance(pw, bool):
        return None
    if isinstance(pw, float):
        if pw.is_integer():
            pw = int(pw)
        else:
            return str(pw).strip() or None
    if isinstance(pw, int):
        return str(pw)
    s = str(pw).strip()
    return s or None


def _merge_password_column(row: dict) -> dict:
    """统一写入键 password，并移除表头别名列，避免重复列干扰 ORM 插入。"""
    r = dict(row)
    raw_pw = None
    for key in _PASSWORD_HEADER_ALIASES:
        if key not in r:
            continue
        if _cell_to_password_str(r[key]) is not None:
            raw_pw = r[key]
            break
    for key in _PASSWORD_HEADER_ALIASES:
        r.pop(key, None)
    if raw_pw is not None:
        r["password"] = raw_pw
    return r


def prepare_vadmin_auth_user_rows(rows: list) -> list:
    if not rows:
        return rows
    out = []
    for row in rows:
        r = _merge_password_column(row)
        pw = r.get("password")
        s = _cell_to_password_str(pw)
        if s is None:
            r["password"] = None
            out.append(r)
            continue
        if _looks_like_bcrypt(s):
            r["password"] = s
        else:
            r["password"] = _pwd_context.hash(s)
        out.append(r)
    return out
