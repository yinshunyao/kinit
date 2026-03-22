# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.db_base import BaseModel


class VadminOperationRecord(BaseModel):
    __tablename__ = "vadmin_record_operation"
    __table_args__ = {"comment": "操作审计（Mongo 关闭时）"}

    telephone: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True, comment="手机号")
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="用户ID")
    user_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="用户名")
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="HTTP 状态码")
    client_ip: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="客户端 IP")
    request_method: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True, comment="HTTP 方法")
    api_path: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="路由 path")
    system: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="操作系统")
    browser: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="浏览器")
    summary: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True, comment="接口摘要")
    route_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="路由 name")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="接口描述")
    tags: Mapped[str | None] = mapped_column(Text, nullable=True, comment="标签 JSON 数组")
    process_time: Mapped[float | None] = mapped_column(Float, nullable=True, comment="处理耗时(秒)")
    params: Mapped[str | None] = mapped_column(Text, nullable=True, comment="请求参数 JSON")
    request_api: Mapped[str | None] = mapped_column(Text, nullable=True, comment="完整请求 URL")
    content_length: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="Content-Length")
