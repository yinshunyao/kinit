#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2023/5/6 9:29
# @File           : task.py
# @IDE            : PyCharm
# @desc           : 任务基础类

import pymysql
from sqlalchemy.engine.url import make_url

from application.settings import SQLALCHEMY_DATABASE_URL
from core.logger import logger


class DBGetter:

    def __init__(self):
        self.mysql_cursor = None
        self.mysql_conn = None

    def conn_mysql(self) -> None:
        """
        连接系统中配置的 mysql 数据库
        """
        try:
            u = make_url(SQLALCHEMY_DATABASE_URL)
            self.mysql_conn = pymysql.connect(
                host=u.host,
                port=int(u.port or 3306),
                user=u.username or "",
                password=u.password or "",
                database=u.database or "",
            )
            self.mysql_cursor = self.mysql_conn.cursor()
        except pymysql.err.OperationalError as e:
            logger.error(f"数据库连接失败，{e}")
            raise ValueError("数据库连接失败！")
        except AttributeError as e:
            logger.error(f"数据库链接解析失败，{e}")
            raise ValueError("数据库链接解析失败！")

    def close_mysql(self) -> None:
        """
        关闭 mysql 链接
        """
        try:
            self.mysql_cursor.close()
            self.mysql_conn.close()
        except AttributeError as e:
            logger.error(f"未连接数据库，无需关闭！，{e}")
            raise ValueError("未连接数据库，无需关闭！")


if __name__ == '__main__':
    t = DBGetter()
    t.conn_mysql()
    t.close_mysql()
