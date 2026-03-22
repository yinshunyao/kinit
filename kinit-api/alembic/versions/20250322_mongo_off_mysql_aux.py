"""mongo off: operation log, scheduler tasks, apscheduler_jobs

Revision ID: mongo_off_mysql_01
Revises:
Create Date: 2025-03-22
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "mongo_off_mysql_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "vadmin_record_operation",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, comment="主键ID"),
        sa.Column("create_datetime", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"),
        sa.Column("update_datetime", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间"),
        sa.Column("delete_datetime", sa.DateTime(), nullable=True, comment="删除时间"),
        sa.Column("is_delete", sa.Boolean(), nullable=False, server_default=sa.text("0"), comment="是否软删除"),
        sa.Column("telephone", sa.String(32), nullable=True, comment="手机号"),
        sa.Column("user_id", sa.Integer(), nullable=True, comment="用户ID"),
        sa.Column("user_name", sa.String(255), nullable=True, comment="用户名"),
        sa.Column("status_code", sa.Integer(), nullable=True, comment="HTTP 状态码"),
        sa.Column("client_ip", sa.String(64), nullable=True, comment="客户端 IP"),
        sa.Column("request_method", sa.String(16), nullable=True, comment="HTTP 方法"),
        sa.Column("api_path", sa.String(512), nullable=True, comment="路由 path"),
        sa.Column("system", sa.String(128), nullable=True, comment="操作系统"),
        sa.Column("browser", sa.String(128), nullable=True, comment="浏览器"),
        sa.Column("summary", sa.String(255), nullable=True, comment="接口摘要"),
        sa.Column("route_name", sa.String(128), nullable=True, comment="路由 name"),
        sa.Column("description", sa.Text(), nullable=True, comment="接口描述"),
        sa.Column("tags", sa.Text(), nullable=True, comment="标签 JSON"),
        sa.Column("process_time", sa.Float(), nullable=True, comment="处理耗时(秒)"),
        sa.Column("params", sa.Text(), nullable=True, comment="请求参数 JSON"),
        sa.Column("request_api", sa.Text(), nullable=True, comment="完整请求 URL"),
        sa.Column("content_length", sa.String(32), nullable=True, comment="Content-Length"),
        mysql_charset="utf8mb4",
        comment="操作审计（Mongo 关闭时）",
    )
    op.create_index("ix_vadmin_record_operation_telephone", "vadmin_record_operation", ["telephone"])
    op.create_index("ix_vadmin_record_operation_request_method", "vadmin_record_operation", ["request_method"])
    op.create_index("ix_vadmin_record_operation_summary", "vadmin_record_operation", ["summary"])

    op.create_table(
        "vadmin_system_task",
        sa.Column("task_id", sa.String(24), primary_key=True, comment="任务编号"),
        sa.Column("name", sa.String(255), nullable=False, comment="任务名称"),
        sa.Column("group", sa.String(255), nullable=True, comment="分组"),
        sa.Column("job_class", sa.Text(), nullable=False, comment="任务类路径"),
        sa.Column("exec_strategy", sa.String(32), nullable=False, comment="执行策略"),
        sa.Column("expression", sa.String(512), nullable=False, comment="表达式"),
        sa.Column("remark", sa.String(512), nullable=True, comment="备注"),
        sa.Column("start_date", sa.String(32), nullable=True, comment="开始时间"),
        sa.Column("end_date", sa.String(32), nullable=True, comment="结束时间"),
        sa.Column("task_disabled", sa.Boolean(), nullable=False, server_default=sa.text("0"), comment="调度失败等标记"),
        sa.Column("create_datetime", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"),
        sa.Column("update_datetime", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间"),
        mysql_charset="utf8mb4",
        comment="定时任务定义（MySQL）",
    )
    op.create_index("ix_vadmin_system_task_group", "vadmin_system_task", ["group"])

    op.create_table(
        "vadmin_system_task_group",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, comment="主键ID"),
        sa.Column("create_datetime", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"),
        sa.Column("update_datetime", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间"),
        sa.Column("delete_datetime", sa.DateTime(), nullable=True, comment="删除时间"),
        sa.Column("is_delete", sa.Boolean(), nullable=False, server_default=sa.text("0"), comment="是否软删除"),
        sa.Column("value", sa.String(255), nullable=False, unique=True, comment="分组值"),
        mysql_charset="utf8mb4",
        comment="定时任务分组（MySQL）",
    )

    op.create_table(
        "scheduler_task_record",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, comment="主键ID"),
        sa.Column("create_datetime", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), comment="创建时间"),
        sa.Column("update_datetime", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间"),
        sa.Column("delete_datetime", sa.DateTime(), nullable=True, comment="删除时间"),
        sa.Column("is_delete", sa.Boolean(), nullable=False, server_default=sa.text("0"), comment="是否软删除"),
        sa.Column("job_id", sa.String(191), nullable=False, comment="任务编号"),
        sa.Column("job_class", sa.String(512), nullable=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("group", sa.String(255), nullable=True),
        sa.Column("exec_strategy", sa.String(32), nullable=True),
        sa.Column("expression", sa.String(512), nullable=True),
        sa.Column("start_time", sa.String(32), nullable=True),
        sa.Column("end_time", sa.String(32), nullable=True),
        sa.Column("process_time", sa.Float(), nullable=True),
        sa.Column("retval", sa.Text(), nullable=True),
        sa.Column("exception", sa.Text(), nullable=True),
        sa.Column("traceback", sa.Text(), nullable=True),
        mysql_charset="utf8mb4",
        comment="定时任务执行记录（MySQL）",
    )
    op.create_index("ix_scheduler_task_record_job_id", "scheduler_task_record", ["job_id"])
    op.create_index("ix_scheduler_task_record_name", "scheduler_task_record", ["name"])

    op.create_table(
        "apscheduler_jobs",
        sa.Column("id", sa.String(191), primary_key=True),
        sa.Column("next_run_time", sa.Float(25), nullable=True),
        sa.Column("job_state", sa.LargeBinary(length=2**31 - 1), nullable=False),
        mysql_charset="utf8mb4",
    )


def downgrade():
    op.drop_table("apscheduler_jobs")
    op.drop_table("scheduler_task_record")
    op.drop_table("vadmin_system_task_group")
    op.drop_table("vadmin_system_task")
    op.drop_table("vadmin_record_operation")
