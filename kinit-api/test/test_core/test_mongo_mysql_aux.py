# -*- coding: utf-8 -*-
import pytest
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from core.exception import CustomException
from core.mongo_mysql_aux import mongo_filter_to_sql_conditions


class _M(DeclarativeBase):
    pass


class _Task(_M):
    __tablename__ = "t_task_sql_aux_test"
    task_id: Mapped[str] = mapped_column(String(24), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))


def test_mongo_filter_like():
    conds = mongo_filter_to_sql_conditions(_Task, name=("like", "ab"))
    assert len(conds) == 1


def test_mongo_filter_objectid_ok():
    conds = mongo_filter_to_sql_conditions(_Task, field_map={"_id": "task_id"}, _id=("ObjectId", "507f1f77bcf86cd799439011"))
    assert len(conds) == 1


def test_mongo_filter_objectid_invalid():
    with pytest.raises(CustomException):
        mongo_filter_to_sql_conditions(_Task, field_map={"_id": "task_id"}, _id=("ObjectId", "not-an-id"))
