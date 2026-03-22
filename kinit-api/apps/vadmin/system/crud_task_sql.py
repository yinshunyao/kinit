# -*- coding: utf-8 -*-
"""定时任务相关：MONGO_DB_ENABLE=False 时走 MySQL。"""
from __future__ import annotations

import json
from enum import Enum
from typing import Any

from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from sqlalchemy import delete, false, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from application.settings import SUBSCRIBE
from apps.vadmin.system import models, schemas
from core.crud import DalBase
from core.exception import CustomException
from core.mongo_manage import MongoManage
from core.mongo_mysql_aux import mongo_filter_to_sql_conditions
from utils import status


def _fmt_dt(value) -> str | None:
    if value is None:
        return None
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _task_row_to_dict(
    row: models.VadminSystemTask,
    *,
    is_active: bool,
    last_run_datetime,
) -> dict:
    return {
        "_id": row.task_id,
        "name": row.name,
        "group": row.group,
        "job_class": row.job_class,
        "exec_strategy": row.exec_strategy,
        "expression": row.expression,
        "remark": row.remark,
        "start_date": row.start_date,
        "end_date": row.end_date,
        "create_datetime": _fmt_dt(row.create_datetime),
        "update_datetime": _fmt_dt(row.update_datetime),
        "is_active": is_active,
        "last_run_datetime": _fmt_dt(last_run_datetime),
    }


class SchedulerTaskJobsSqlDal:
    """等价于原 Mongo 集合 scheduler_task_jobs（现为 APScheduler SQL 表）。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def delete_data(self, _id: str) -> bool:
        await self.db.execute(delete(models.apscheduler_jobs).where(models.apscheduler_jobs.c.id == _id))
        await self.db.flush()
        return True


class TaskGroupSqlDal(DalBase):
    def __init__(self, db: AsyncSession):
        super().__init__(db, models.VadminSchedulerTaskGroup, None)

    async def get_datas(self, **kwargs) -> list[dict]:
        """与 Mongo 分组文档形态对齐（含 _id）。"""
        kwargs = {**kwargs, "v_return_objs": True}
        objs = await super().get_datas(**kwargs)
        out = []
        for o in objs:
            out.append(
                {
                    "_id": str(o.id),
                    "value": o.value,
                    "create_datetime": _fmt_dt(o.create_datetime),
                    "update_datetime": _fmt_dt(o.update_datetime),
                }
            )
        return out


class TaskRecordSqlDal(DalBase):
    def __init__(self, db: AsyncSession):
        super().__init__(db, models.VadminSchedulerTaskRecord, None)

    async def get_datas(self, **kwargs) -> list[dict]:
        page = kwargs.get("page", 1)
        limit = kwargs.get("limit", 10)
        v_order = kwargs.get("v_order")
        v_order_field = kwargs.get("v_order_field") or "create_datetime"
        filter_kw = {k: v for k, v in kwargs.items() if k not in ("page", "limit", "v_order", "v_order_field", "v_schema", "v_return_objs")}
        conds = mongo_filter_to_sql_conditions(self.model, **filter_kw)
        conds.append(self.model.is_delete == false())
        order_col = getattr(self.model, v_order_field, self.model.create_datetime)
        if v_order in MongoManage.ORDER_FIELD:
            stmt = select(self.model).where(*conds).order_by(order_col.desc(), self.model.id.desc())
        else:
            stmt = select(self.model).where(*conds).order_by(order_col, self.model.id)
        if limit:
            stmt = stmt.offset((page - 1) * limit).limit(limit)
        res = await self.db.scalars(stmt)
        rows = list(res.all())
        out = []
        for r in rows:
            d = {c.key: getattr(r, c.key) for c in r.__table__.columns}
            d["_id"] = str(d.pop("id"))
            for tkey in ("create_datetime", "update_datetime", "delete_datetime"):
                if d.get(tkey) is not None and hasattr(d[tkey], "strftime"):
                    d[tkey] = d[tkey].strftime("%Y-%m-%d %H:%M:%S")
            out.append(d)
        return out

    async def get_count(self, **kwargs) -> int:
        filter_kw = {k: v for k, v in kwargs.items() if k not in ("page", "limit", "v_order", "v_order_field")}
        conds = mongo_filter_to_sql_conditions(self.model, **filter_kw)
        conds.append(self.model.is_delete == false())
        stmt = select(func.count(self.model.id)).where(*conds)
        return (await self.db.execute(stmt)).scalar_one()


class TaskSqlDal:
    ORDER_FIELD = MongoManage.ORDER_FIELD

    class JobOperation(Enum):
        add = "add_job"

    def __init__(self, db: AsyncSession):
        self.db = db
        self.schema = schemas.TaskSimpleOut

    def _base_task_stmt(self) -> Select:
        sub_last = (
            select(
                models.VadminSchedulerTaskRecord.job_id.label("jid"),
                func.max(models.VadminSchedulerTaskRecord.create_datetime).label("last_run"),
            )
            .where(models.VadminSchedulerTaskRecord.is_delete == false())
            .group_by(models.VadminSchedulerTaskRecord.job_id)
        ).subquery()
        return (
            select(
                models.VadminSystemTask,
                sub_last.c.last_run,
                models.apscheduler_jobs.c.id.label("job_pk"),
            )
            .outerjoin(sub_last, sub_last.c.jid == models.VadminSystemTask.task_id)
            .outerjoin(models.apscheduler_jobs, models.apscheduler_jobs.c.id == models.VadminSystemTask.task_id)
        )

    def _apply_filters(self, stmt: Select, **kwargs) -> Select:
        conds = mongo_filter_to_sql_conditions(
            models.VadminSystemTask,
            field_map={"_id": "task_id"},
            **kwargs,
        )
        if conds:
            stmt = stmt.where(*conds)
        return stmt

    def _apply_order(self, stmt: Select, v_order: str | None, v_order_field: str | None) -> Select:
        field = v_order_field or "create_datetime"
        col = getattr(models.VadminSystemTask, field, models.VadminSystemTask.create_datetime)
        if v_order in self.ORDER_FIELD:
            return stmt.order_by(col.desc(), models.VadminSystemTask.task_id.desc())
        return stmt.order_by(col, models.VadminSystemTask.task_id)

    async def get_task(
        self,
        _id: str = None,
        v_return_none: bool = False,
        v_schema: Any = None,
        **kwargs,
    ) -> dict | None:
        if _id:
            kwargs["_id"] = ("ObjectId", _id)
        stmt = self._apply_filters(self._base_task_stmt(), **kwargs)
        stmt = self._apply_order(stmt, None, None).limit(1)
        row = (await self.db.execute(stmt)).first()
        if not row:
            if v_return_none:
                return None
            raise CustomException("未查找到对应数据", code=status.HTTP_404_NOT_FOUND)
        t, last_run, job_pk = row[0], row[1], row[2]
        data = _task_row_to_dict(t, is_active=job_pk is not None, last_run_datetime=last_run)
        if v_schema:
            return jsonable_encoder(v_schema(**data))
        return data

    async def get_tasks(
        self,
        page: int = 1,
        limit: int = 10,
        v_schema: Any = None,
        v_order: str = None,
        v_order_field: str = None,
        **kwargs,
    ) -> tuple:
        count_stmt = select(func.count()).select_from(models.VadminSystemTask)
        count_stmt = self._apply_filters(count_stmt, **kwargs)
        total = (await self.db.execute(count_stmt)).scalar_one()
        if total == 0:
            return [], 0
        stmt = self._apply_filters(self._base_task_stmt(), **kwargs)
        stmt = self._apply_order(stmt, v_order, v_order_field)
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        rows = (await self.db.execute(stmt)).all()
        datas = []
        for t, last_run, job_pk in rows:
            data = _task_row_to_dict(t, is_active=job_pk is not None, last_run_datetime=last_run)
            if v_schema:
                datas.append(jsonable_encoder(v_schema(**data)))
            elif self.schema:
                datas.append(jsonable_encoder(self.schema(**data)))
            else:
                datas.append(data)
        return datas, total

    async def add_task(self, rd: Redis, data: dict) -> int:
        exec_strategy = data.get("exec_strategy")
        job_params = {
            "name": data.get("_id"),
            "job_class": data.get("job_class"),
            "expression": data.get("expression"),
        }
        if exec_strategy == "interval" or exec_strategy == "cron":
            job_params["start_date"] = data.get("start_date")
            job_params["end_date"] = data.get("end_date")
        message = {
            "operation": self.JobOperation.add.value,
            "task": {"exec_strategy": data.get("exec_strategy"), "job_params": job_params},
        }
        return await rd.publish(SUBSCRIBE, json.dumps(message).encode("utf-8"))

    async def create_task(self, rd: Redis, data: schemas.Task) -> dict:
        data_dict = data.model_dump()
        is_active = data_dict.pop("is_active")
        task_id = str(ObjectId())
        row = models.VadminSystemTask(
            task_id=task_id,
            name=data_dict["name"],
            group=data_dict.get("group"),
            job_class=data_dict["job_class"],
            exec_strategy=data_dict["exec_strategy"],
            expression=data_dict["expression"],
            remark=data_dict.get("remark"),
            start_date=data_dict.get("start_date"),
            end_date=data_dict.get("end_date"),
            task_disabled=False,
        )
        self.db.add(row)
        await self.db.flush()
        obj = await self.get_task(task_id, v_schema=schemas.TaskSimpleOut)
        group = await TaskGroupSqlDal(self.db).get_data(value=data.group, v_return_none=True)
        if not group:
            await TaskGroupSqlDal(self.db).create_data(data={"value": data.group})
        result = {"subscribe_number": 0, "is_active": is_active}
        if is_active:
            result["subscribe_number"] = await self.add_task(rd, obj)
        return result

    async def put_task(self, rd: Redis, _id: str, data: schemas.Task) -> dict:
        data_dict = data.model_dump()
        is_active = data_dict.pop("is_active")
        await self.put_data(_id, data_dict)
        obj = await self.get_task(_id, v_schema=schemas.TaskSimpleOut)
        group = await TaskGroupSqlDal(self.db).get_data(value=data.group, v_return_none=True)
        if not group:
            await TaskGroupSqlDal(self.db).create_data(data={"value": data.group})
        try:
            await SchedulerTaskJobsSqlDal(self.db).delete_data(_id)
        except Exception:
            pass
        result = {"subscribe_number": 0, "is_active": is_active}
        if is_active:
            result["subscribe_number"] = await self.add_task(rd, obj)
        return result

    async def put_data(self, _id: str, data: dict | Any) -> None:
        payload = jsonable_encoder(data) if not isinstance(data, dict) else dict(data)
        payload.pop("is_active", None)
        stmt = (
            update(models.VadminSystemTask)
            .where(models.VadminSystemTask.task_id == _id)
            .values(
                name=payload.get("name"),
                group=payload.get("group"),
                job_class=payload.get("job_class"),
                exec_strategy=payload.get("exec_strategy"),
                expression=payload.get("expression"),
                remark=payload.get("remark"),
                start_date=payload.get("start_date"),
                end_date=payload.get("end_date"),
            )
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def delete_task(self, _id: str) -> bool:
        await self.db.execute(delete(models.VadminSystemTask).where(models.VadminSystemTask.task_id == _id))
        await self.db.flush()
        try:
            await SchedulerTaskJobsSqlDal(self.db).delete_data(_id)
        except Exception:
            pass
        return True

    async def run_once_task(self, rd: Redis, _id: str) -> int:
        obj: dict = await self.get_data(_id, v_schema=schemas.TaskSimpleOut)
        message = {
            "operation": self.JobOperation.add.value,
            "task": {
                "exec_strategy": "once",
                "job_params": {"name": obj.get("_id"), "job_class": obj.get("job_class")},
            },
        }
        return await rd.publish(SUBSCRIBE, json.dumps(message).encode("utf-8"))

    async def get_data(self, _id: str, v_schema: Any = None, **kwargs) -> dict:
        return await self.get_task(_id, v_schema=v_schema, **kwargs)
