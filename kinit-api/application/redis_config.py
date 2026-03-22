# -*- coding: utf-8 -*-
"""从环境变量注入 Redis 连接串，避免在仓库配置文件中写死口令。"""

from __future__ import annotations

import os

from application.env_config import load_project_dotenv

load_project_dotenv()

KINIT_REDIS_URL_ENV = "KINIT_REDIS_URL"


def resolve_redis_db_url(enabled: bool) -> str:
    """
    当 REDIS_DB_ENABLE 为 True 时，必须设置 KINIT_REDIS_URL。
    无密码示例：redis://127.0.0.1:6379/0
    有密码示例：redis://:密码@127.0.0.1:6379/0（或 rediss:// 用于 TLS）
    """
    if not enabled:
        return ""
    url = (os.environ.get(KINIT_REDIS_URL_ENV) or "").strip()
    if not url:
        raise RuntimeError(
            f"已启用 Redis（REDIS_DB_ENABLE=true）但未配置环境变量 {KINIT_REDIS_URL_ENV}。"
            "请在 .env 中设置，例如：\n"
            "  无密码: KINIT_REDIS_URL=redis://127.0.0.1:6379/0\n"
            "  有密码: KINIT_REDIS_URL=redis://:你的密码@127.0.0.1:6379/0"
        )
    if not (url.startswith("redis://") or url.startswith("rediss://")):
        raise ValueError(
            f"{KINIT_REDIS_URL_ENV} 须以 redis:// 或 rediss:// 开头，当前前缀无效"
        )
    return url
