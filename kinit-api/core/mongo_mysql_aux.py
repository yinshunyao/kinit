# -*- coding: utf-8 -*-
"""Mongo 风格查询参数 → SQLAlchemy 条件（用于 MONGO_DB_ENABLE=False 分支）。"""
from __future__ import annotations

import json
import re
from typing import Any

from sqlalchemy import ColumnElement
from sqlalchemy.orm import DeclarativeBase

from core.exception import CustomException
from utils import status

_OBJECT_ID_HEX_RE = re.compile(r"^[a-fA-F0-9]{24}$")


def mongo_filter_to_sql_conditions(
    model: type[DeclarativeBase],
    *,
    field_map: dict[str, str] | None = None,
    **kwargs: Any,
) -> list[ColumnElement[bool]]:
    """
    将 MongoManage.filter_condition 风格的 kwargs 转为 SQLAlchemy where 片段。
    field_map: 查询参数名 → ORM 属性名（如 {\"_id\": \"task_id\"}）。
    """
    field_map = field_map or {}
    conditions: list[ColumnElement[bool]] = []
    for k, v in kwargs.items():
        if not v:
            continue
        col_name = field_map.get(k, k)
        if not hasattr(model, col_name):
            continue
        attr = getattr(model, col_name)
        if isinstance(v, tuple):
            if v[0] == "like" and v[1]:
                conditions.append(attr.like(f"%{v[1]}%"))
            elif v[0] == "between" and len(v[1]) == 2:
                conditions.append(attr.between(f"{v[1][0]} 00:00:00", f"{v[1][1]} 23:59:59"))
            elif v[0] == "ObjectId" and v[1]:
                if not _OBJECT_ID_HEX_RE.match(str(v[1])):
                    raise CustomException("任务编号格式不正确！", code=status.HTTP_404_NOT_FOUND)
                conditions.append(attr == v[1])
        else:
            conditions.append(attr == v)
    return conditions


def dumps_tags(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)
