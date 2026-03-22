# -*- coding: utf-8 -*-
"""从环境变量注入 MySQL 连接串，避免在仓库配置文件中写死账号密码。"""

from __future__ import annotations

import os

from application.env_config import load_project_dotenv

load_project_dotenv()

KINIT_DATABASE_URL_ENV = "KINIT_DATABASE_URL"


def _compose_database_url_from_parts() -> str | None:
    """
    分项环境变量组装连接串，密码可含 @、:、% 等，无需手工 URL 编码。
    需要：KINIT_DATABASE_HOST、KINIT_DATABASE_NAME、KINIT_DATABASE_USER；
    可选：KINIT_DATABASE_PORT（默认 3306）、KINIT_DATABASE_PASSWORD（未设置视为空密码）。
    """
    host = (os.environ.get("KINIT_DATABASE_HOST") or "").strip()
    name = (os.environ.get("KINIT_DATABASE_NAME") or "").strip()
    user = (os.environ.get("KINIT_DATABASE_USER") or "").strip()
    if not (host and name and user):
        return None
    password = os.environ.get("KINIT_DATABASE_PASSWORD")
    if password is None:
        password = ""
    port = (os.environ.get("KINIT_DATABASE_PORT") or "3306").strip() or "3306"
    from urllib.parse import quote

    u = quote(user, safe="")
    p = quote(password, safe="")
    return f"mysql+pymysql://{u}:{p}@{host}:{port}/{name}"


def get_database_url_raw() -> str:
    direct = (os.environ.get(KINIT_DATABASE_URL_ENV) or "").strip()
    if direct:
        return direct
    composed = _compose_database_url_from_parts()
    if composed:
        return composed
    raise RuntimeError(
        f"未配置数据库：请设置 {KINIT_DATABASE_URL_ENV}，"
        f"或在项目根目录创建 .env（参考 .env.example）。"
        "也支持分项：KINIT_DATABASE_HOST、KINIT_DATABASE_PORT、KINIT_DATABASE_NAME、"
        "KINIT_DATABASE_USER、KINIT_DATABASE_PASSWORD（密码可含特殊字符，无需 URL 编码）。"
        "连接串须以 mysql+pymysql:// 或 mysql+asyncmy:// 开头。"
    )


def resolve_sqlalchemy_async_url() -> str:
    """应用异步引擎（asyncmy）使用的 URL。"""
    url = get_database_url_raw()
    if url.startswith("mysql+asyncmy://"):
        return url
    if url.startswith("mysql+pymysql://"):
        return "mysql+asyncmy://" + url[len("mysql+pymysql://") :]
    raise ValueError(
        f"{KINIT_DATABASE_URL_ENV} 须以 mysql+pymysql:// 或 mysql+asyncmy:// 开头，当前前缀无效"
    )


def resolve_alembic_sync_url() -> str:
    """Alembic 迁移使用的同步 URL（pymysql）。"""
    url = get_database_url_raw()
    if url.startswith("mysql+pymysql://"):
        return url
    if url.startswith("mysql+asyncmy://"):
        return "mysql+pymysql://" + url[len("mysql+asyncmy://") :]
    raise ValueError(
        f"{KINIT_DATABASE_URL_ENV} 须以 mysql+pymysql:// 或 mysql+asyncmy:// 开头，当前前缀无效"
    )
