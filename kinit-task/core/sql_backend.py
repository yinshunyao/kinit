# -*- coding: utf-8 -*-
"""MONGO_DB_ENABLE=False 时，任务定义与调度日志走 MySQL。"""
from __future__ import annotations

import datetime as dt
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from application.settings import SCHEDULER_TASK, SCHEDULER_TASK_RECORD


class SqlTaskBackend:
    def __init__(self, engine: Engine):
        self.engine = engine

    def close_database_connection(self) -> None:
        self.engine.dispose()

    def connect_to_database(self, *_args, **_kwargs) -> None:
        """与 MongoManage 接口对齐，无操作（引擎已创建）。"""
        return None

    def create_data(self, collection: str, data: dict) -> Any:
        now = dt.datetime.now()
        if collection != SCHEDULER_TASK_RECORD:
            raise ValueError(f"不支持的集合: {collection}")
        row = {**data, "create_datetime": now, "update_datetime": now, "is_delete": 0}
        cols = [
            "job_id",
            "job_class",
            "name",
            "group",
            "exec_strategy",
            "expression",
            "start_time",
            "end_time",
            "process_time",
            "retval",
            "exception",
            "traceback",
            "create_datetime",
            "update_datetime",
            "is_delete",
        ]
        payload = {c: row.get(c) for c in cols}
        col_sql = ", ".join("`group`" if c == "group" else c for c in cols)
        placeholders = ", ".join(f":{c}" for c in cols)
        sql = text(f"INSERT INTO scheduler_task_record ({col_sql}) VALUES ({placeholders})")
        with self.engine.begin() as conn:
            conn.execute(sql, payload)
        return True

    def get_data(
        self,
        collection: str,
        _id: str | None = None,
        v_return_none: bool = False,
        v_schema: Any = None,
        is_object_id: bool = False,
        **kwargs,
    ) -> dict | None:
        if collection != SCHEDULER_TASK:
            raise ValueError(f"不支持的集合: {collection}")
        tid = _id
        sql = text(
            "SELECT task_id, name, `group`, job_class, exec_strategy, expression, remark, "
            "start_date, end_date, task_disabled, create_datetime, update_datetime "
            "FROM vadmin_system_task WHERE task_id = :tid LIMIT 1"
        )
        with self.engine.connect() as conn:
            r = conn.execute(sql, {"tid": tid}).mappings().first()
        if not r:
            if v_return_none:
                return None
            raise ValueError("查询单个数据失败，未找到匹配的数据")
        d = dict(r)
        d["_id"] = d["task_id"]
        return d

    def put_data(self, collection: str, _id: str, data: dict, is_object_id: bool = False) -> Any:
        if collection != SCHEDULER_TASK:
            raise ValueError(f"不支持的集合: {collection}")
        if data.get("is_active") is False:
            sql = text(
                "UPDATE vadmin_system_task SET task_disabled = 1, update_datetime = :u WHERE task_id = :tid"
            )
            with self.engine.begin() as conn:
                conn.execute(sql, {"tid": _id, "u": dt.datetime.now()})
            return True
        sets = []
        params: dict[str, Any] = {"tid": _id, "u": dt.datetime.now()}
        for k, v in data.items():
            if k == "is_active":
                continue
            if k in ("name", "group", "job_class", "exec_strategy", "expression", "remark", "start_date", "end_date"):
                sets.append(f"`{k}` = :{k}")
                params[k] = v
        if not sets:
            sql = text("UPDATE vadmin_system_task SET update_datetime = :u WHERE task_id = :tid")
        else:
            sql = text(
                "UPDATE vadmin_system_task SET " + ", ".join(sets) + ", update_datetime = :u WHERE task_id = :tid"
            )
        with self.engine.begin() as conn:
            r = conn.execute(sql, params)
        if r.rowcount == 0:
            raise ValueError("更新数据失败，未找到匹配的数据")
        return True
