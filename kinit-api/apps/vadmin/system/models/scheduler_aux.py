# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, LargeBinary, String, Table, Text, Unicode, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from db.db_base import BaseModel


class VadminSystemTask(Base):
    """定时任务主表（无 Mongo 时使用；主键兼容原 BSON ObjectId 字符串）。"""

    __tablename__ = "vadmin_system_task"
    __table_args__ = {"comment": "定时任务定义（MySQL）"}

    task_id: Mapped[str] = mapped_column(String(24), primary_key=True, comment="任务编号")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="任务名称")
    group: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True, comment="分组")
    job_class: Mapped[str] = mapped_column(Text, nullable=False, comment="任务类路径")
    exec_strategy: Mapped[str] = mapped_column(String(32), nullable=False, comment="执行策略")
    expression: Mapped[str] = mapped_column(String(512), nullable=False, comment="表达式")
    remark: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="备注")
    start_date: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="开始时间")
    end_date: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="结束时间")
    task_disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="调度失败等标记")
    create_datetime: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    update_datetime: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )


class VadminSchedulerTaskGroup(BaseModel):
    __tablename__ = "vadmin_system_task_group"
    __table_args__ = {"comment": "定时任务分组（MySQL）"}

    value: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, comment="分组值")


class VadminSchedulerTaskRecord(BaseModel):
    __tablename__ = "scheduler_task_record"
    __table_args__ = {"comment": "定时任务执行记录（MySQL）"}

    job_id: Mapped[str] = mapped_column(String(191), nullable=False, index=True, comment="任务编号")
    job_class: Mapped[str | None] = mapped_column(String(512), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    group: Mapped[str | None] = mapped_column(String(255), nullable=True)
    exec_strategy: Mapped[str | None] = mapped_column(String(32), nullable=True)
    expression: Mapped[str | None] = mapped_column(String(512), nullable=True)
    start_time: Mapped[str | None] = mapped_column(String(32), nullable=True)
    end_time: Mapped[str | None] = mapped_column(String(32), nullable=True)
    process_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    retval: Mapped[str | None] = mapped_column(Text, nullable=True)
    exception: Mapped[str | None] = mapped_column(Text, nullable=True)
    traceback: Mapped[str | None] = mapped_column(Text, nullable=True)


# APScheduler SQLAlchemyJobStore 官方表结构（与 3.10.x 一致）
apscheduler_jobs = Table(
    "apscheduler_jobs",
    Base.metadata,
    Column("id", Unicode(191), primary_key=True),
    Column("next_run_time", Float(25), nullable=True),
    Column("job_state", LargeBinary(length=2**31 - 1), nullable=False),
)
