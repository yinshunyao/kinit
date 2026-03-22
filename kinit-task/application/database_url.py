# -*- coding: utf-8 -*-
"""与 kinit-api 一致：从环境变量读取 MySQL URL（同步 pymysql 用于调度进程）。"""
from __future__ import annotations

import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

KINIT_DATABASE_URL_ENV = "KINIT_DATABASE_URL"


def get_database_url_raw() -> str:
    url = (os.environ.get(KINIT_DATABASE_URL_ENV) or "").strip()
    if not url:
        raise RuntimeError(
            f"未配置数据库：请设置环境变量 {KINIT_DATABASE_URL_ENV}，"
            f"或在项目根目录创建 .env。须为 mysql+pymysql:// 或 mysql+asyncmy:// 开头。"
        )
    return url


def resolve_alembic_sync_url() -> str:
    url = get_database_url_raw()
    if url.startswith("mysql+pymysql://"):
        return url
    if url.startswith("mysql+asyncmy://"):
        return "mysql+pymysql://" + url[len("mysql+asyncmy://") :]
    raise ValueError(
        f"{KINIT_DATABASE_URL_ENV} 须以 mysql+pymysql:// 或 mysql+asyncmy:// 开头"
    )
