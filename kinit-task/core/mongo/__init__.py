from application.settings import MONGO_DB_ENABLE

if MONGO_DB_ENABLE:
    from .mongo_manage import MongoManage

    _db: MongoManage | None = MongoManage()
else:
    _db = None


def set_database(impl) -> None:
    global _db
    _db = impl


def get_database():
    if _db is None:
        raise RuntimeError("数据存储未初始化：请先调用 start_mongo 或 start_sql")
    return _db
