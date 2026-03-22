# -*- coding: utf-8 -*-
"""从环境变量读取配置；`.env` 由 load_project_dotenv() 统一加载（幂等）。"""
from __future__ import annotations

import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_DOTENV_DONE = False


def load_project_dotenv() -> None:
    """从项目根目录加载 `.env`；不覆盖进程中已存在的环境变量。"""
    global _DOTENV_DONE
    if _DOTENV_DONE:
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(_ROOT / ".env")
    except ImportError:
        pass
    _DOTENV_DONE = True


def env_bool(key: str, default: bool) -> bool:
    """
    读取布尔环境变量。未设置或空字符串时返回 default。
    真值：1, true, yes, on, y（不区分大小写）；假值：0, false, no, off, n。
    其它字符串则回退为 default。
    """
    raw = os.environ.get(key)
    if raw is None:
        return default
    s = str(raw).strip().lower()
    if s == "":
        return default
    if s in ("1", "true", "yes", "on", "y"):
        return True
    if s in ("0", "false", "no", "off", "n"):
        return False
    return default


def env_str(key: str, default: str) -> str:
    raw = os.environ.get(key)
    if raw is None:
        return default
    s = str(raw).strip()
    return default if s == "" else s


def env_int(key: str, default: int) -> int:
    raw = os.environ.get(key)
    if raw is None:
        return default
    s = str(raw).strip()
    if s == "":
        return default
    return int(s, 10)
