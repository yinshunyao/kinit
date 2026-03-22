# -*- coding: utf-8 -*-
"""从环境变量读取配置（与 .env 配合，由 settings 先 load_dotenv）。"""
from __future__ import annotations

import os


def env_bool(key: str, default: bool) -> bool:
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
