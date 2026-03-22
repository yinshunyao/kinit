# 发布草稿（kinit）

## 2025-03-22

- kinit-api：登录 `/login` 密码方式支持「手机号或账号（`vadmin_auth_user.name`，须含字母）」，字段名仍为 `telephone`；短信登录仍为手机号；`/api/login`（OAuth2）同步；密码登录用户不存在与密码错误统一提示「账号或密码错误」；初始化脚本对 `vadmin_auth_user` 表中非 `$2` 前缀的 `password` 自动 bcrypt。详见 `doc/02-dr/02 登录认证与初始化.md`。
- kinit-api（修复）：初始化用户密码未哈希问题——支持 Excel `密码` 等表头别名、数字型密码单元格；`init.xlsx` sheet 名可与表名去分隔符后匹配。见 `doc/91-qa/【登录认证】初始化用户密码仍为明文.md`。
- kinit-api（修复）：`InitializeData.migrate_model` / `main.py init|migrate` 中 Alembic 顺序改为先 `upgrade head` 再 `revision --autogenerate` 再 `upgrade head`，避免库未追上已有迁移时出现 `Target database is not up to date`。
- kinit-api（修复）：密码登录账号标识除匹配 `name` 外，增加对 `nickname` 的匹配（与常见种子数据中 `admin` 落在昵称字段一致）。
- kinit-admin / kinit-uni：登录页去掉默认演示账号密码；密码登录占位与标签改为「手机号或账号」。
- kinit-api / kinit-task：`MONGO_DB_ENABLE` 可在项目根 `.env` 中设置（如 `false`），覆盖 `application/config/*.py` 默认值（`application/env_config.env_bool`）。
- kinit-api：支持 `MONGO_DB_ENABLE=False` 时操作审计与定时任务数据落 MySQL；新增表及 Alembic 迁移 `mongo_off_mysql_01`；操作日志中间件在关闭 Mongo 时仍可按 `OPERATION_LOG_RECORD` 写入。
- kinit-task：同配置下使用 `SQLAlchemyJobStore` 与 MySQL 读写任务定义及调度记录；依赖增加 SQLAlchemy、PyMySQL。
- 运行要求：与 API 相同设置 `KINIT_DATABASE_URL`；关闭 Mongo 时 API 与 task 进程须同时配置 `MONGO_DB_ENABLE=False` 并执行迁移。
