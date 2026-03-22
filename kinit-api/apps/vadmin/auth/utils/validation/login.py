#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

# @version        : 1.0
# @Create Time    : 2022/11/9 10:15 
# @File           : login.py
# @IDE            : PyCharm
# @desc           : 登录验证装饰器

from fastapi import Request
from pydantic import BaseModel, model_validator
from sqlalchemy.ext.asyncio import AsyncSession
from application.settings import DEFAULT_AUTH_ERROR_MAX_NUMBER, DEMO, REDIS_DB_ENABLE
from apps.vadmin.auth import crud, schemas
from core.database import redis_getter
from core.validator import vali_telephone
from core.login_identifier import validate_password_login_identifier
from utils.count import Count


class LoginForm(BaseModel):
    telephone: str
    password: str
    method: str = '0'  # 认证方式，0：密码登录，1：短信登录，2：微信一键登录
    platform: str = '0'  # 登录平台，0：PC端管理系统，1：移动端管理系统

    @model_validator(mode='after')
    def normalize_login_identifier(self):
        raw = (self.telephone or '').strip()
        if not raw:
            raise ValueError('请输入手机号或账号')
        if self.method == '1':
            self.telephone = vali_telephone(raw)
        elif self.method == '0':
            self.telephone = validate_password_login_identifier(raw)
        else:
            self.telephone = raw
        return self


class WXLoginForm(BaseModel):
    telephone: str | None = None
    code: str
    method: str = '2'  # 认证方式，0：密码登录，1：短信登录，2：微信一键登录
    platform: str = '1'  # 登录平台，0：PC端管理系统，1：移动端管理系统


class LoginResult(BaseModel):
    status: bool | None = False
    user: schemas.UserPasswordOut | None = None
    msg: str | None = None

    class Config:
        arbitrary_types_allowed = True


class LoginValidation:

    """
    验证用户登录时提交的数据是否有效
    """

    def __init__(self, func):
        self.func = func

    async def __call__(self, data: LoginForm, db: AsyncSession, request: Request) -> LoginResult:
        self.result = LoginResult()
        if data.platform not in ["0", "1"] or data.method not in ["0", "1"]:
            self.result.msg = "无效参数"
            return self.result
        user = await crud.UserDal(db).get_user_for_login(data.telephone, data.method)
        if not user:
            self.result.msg = "该手机号不存在！" if data.method == "1" else "账号或密码错误"
            return self.result

        result = await self.func(self, data=data, user=user, request=request)

        if REDIS_DB_ENABLE:
            count_key = f"{data.telephone}_password_auth" if data.method == '0' else f"{data.telephone}_sms_auth"
            count = Count(redis_getter(request), count_key)
        else:
            count = None

        if not result.status:
            self.result.msg = result.msg
            if not DEMO and count:
                number = await count.add(ex=86400)
                if number >= DEFAULT_AUTH_ERROR_MAX_NUMBER:
                    await count.reset()
                    # 如果等于最大次数，那么就将用户 is_active=False
                    user.is_active = False
                    await db.flush()
        elif not user.is_active:
            self.result.msg = "此账号已被冻结！"
        elif data.platform in ["0", "1"] and not user.is_staff:
            self.result.msg = "此账号无权限！"
        else:
            if not DEMO and count:
                await count.delete()
            self.result.msg = "OK"
            self.result.status = True
            self.result.user = schemas.UserPasswordOut.model_validate(user)
            await crud.UserDal(db).update_login_info(user, request.client.host)
        return self.result
