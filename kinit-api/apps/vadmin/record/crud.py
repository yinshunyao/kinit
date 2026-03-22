#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2021/10/18 22:18
# @File           : crud.py
# @IDE            : PyCharm
# @desc           : 数据库 增删改查操作

import random
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy import false
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas
from core.crud import DalBase
from core.mongo_manage import MongoManage
from core.mongo_mysql_aux import dumps_tags


class LoginRecordDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(LoginRecordDal, self).__init__()
        self.db = db
        self.model = models.VadminLoginRecord
        self.schema = schemas.LoginRecordSimpleOut

    async def get_user_distribute(self) -> list[dict]:
        """
        获取用户登录分布情况
        高德经纬度查询：https://lbs.amap.com/tools/picker

        {
            name: '北京',
            center: [116.407394, 39.904211],
            total: 20
        }

        :return: List[dict]
        """
        result = [{
                    "name": '北京',
                    "center": [116.407394, 39.904211],
                },
                {
                    "name": '重庆',
                    "center": [106.551643, 29.562849],
                },
                {
                    "name": '郑州',
                    "center": [113.778584, 34.759197],
                },
                {
                    "name": '南京',
                    "center": [118.796624, 32.059344],
                },
                {
                    "name": '武汉',
                    "center": [114.304569, 30.593354],
                },
                {
                    "name": '乌鲁木齐',
                    "center": [87.616824, 43.825377],
                },
                {
                    "name": '新乡',
                    "center": [113.92679, 35.303589],
                }]
        for data in result:
            assert isinstance(data, dict)
            data["total"] = random.randint(2, 80)
        return result


class SMSSendRecordDal(DalBase):

    def __init__(self, db: AsyncSession):
        super(SMSSendRecordDal, self).__init__()
        self.db = db
        self.model = models.VadminSMSSendRecord
        self.schema = schemas.SMSSendRecordSimpleOut


class OperationRecordDal(MongoManage):

    def __init__(self, db: AsyncIOMotorDatabase):
        super(OperationRecordDal, self).__init__()
        self.db = db
        self.collection = db["operation_record"]
        self.schema = schemas.OperationRecordSimpleOut
        self.is_object_id = True


class OperationRecordSqlDal(DalBase):
    """操作审计：MONGO_DB_ENABLE=False 时使用。"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, models.VadminOperationRecord, schemas.OperationRecordSimpleOut)

    async def get_count(self, **kwargs) -> int:
        return await super().get_count(v_where=[self.model.is_delete == false()], **kwargs)

    async def create_middleware_row(self, document: dict) -> None:
        data = {}
        for key in (
            "process_time",
            "telephone",
            "user_id",
            "user_name",
            "request_api",
            "client_ip",
            "system",
            "browser",
            "request_method",
            "api_path",
            "summary",
            "description",
            "route_name",
            "status_code",
            "content_length",
            "params",
        ):
            if key in document:
                data[key] = document[key]
        data["tags"] = dumps_tags(document.get("tags"))
        obj = self.model(**data)
        await self.flush(obj)
