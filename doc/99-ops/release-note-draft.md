# 发布草稿（kinit）

## 2025-03-22

- kinit-api / kinit-task：`MONGO_DB_ENABLE` 可在项目根 `.env` 中设置（如 `false`），覆盖 `application/config/*.py` 默认值（`application/env_config.env_bool`）。
- kinit-api：支持 `MONGO_DB_ENABLE=False` 时操作审计与定时任务数据落 MySQL；新增表及 Alembic 迁移 `mongo_off_mysql_01`；操作日志中间件在关闭 Mongo 时仍可按 `OPERATION_LOG_RECORD` 写入。
- kinit-task：同配置下使用 `SQLAlchemyJobStore` 与 MySQL 读写任务定义及调度记录；依赖增加 SQLAlchemy、PyMySQL。
- 运行要求：与 API 相同设置 `KINIT_DATABASE_URL`；关闭 Mongo 时 API 与 task 进程须同时配置 `MONGO_DB_ENABLE=False` 并执行迁移。
