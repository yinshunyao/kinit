# 关联文档

| 类型 | 文档路径 |
|:---|:---|
| 原始需求 | `kinit/doc/01-or/【kinit-api】MongoDB关闭时MySQL兼容适配.md` |
| 测试设计 | `kinit/doc/03-tr/01 MongoDB关闭时MySQL适配测试设计.md` |

# 功能设计

## 配置开关

- 沿用 `application.config.*` 中的默认 `MONGO_DB_ENABLE`；**可被项目根目录 `.env`（或进程环境变量）中的 `MONGO_DB_ENABLE` 覆盖**（如 `false` / `0` / `no`，见 `application/env_config.py` 的 `env_bool`）。
- kinit-api 与 kinit-task 均须在关闭 Mongo 时保持同一取值；task 侧 `application/settings.py` 已 `load_dotenv` 后再解析该变量。
- `MONGO_DB_ENABLE = False` 时：不注册 Mongo 连接事件；操作审计与定时任务相关读写全部走 MySQL（与主业务相同的异步 SQLAlchemy 会话）。
- `OPERATION_LOG_RECORD = True` 时，无论 Mongo 是否开启，均注册操作审计中间件；中间件在 Mongo 关闭时写入 MySQL。

## 操作审计（operation_record）

- MySQL 表：`vadmin_record_operation`（ORM：`VadminOperationRecord`），字段覆盖原 Mongo 文档中的路径、用户、UA、耗时、状态码、请求摘要及 `params` JSON 文本等。
- 列表接口仍为 `GET /vadmin/record/operations`，查询参数（summary / telephone / request_method 等）语义与 Mongo 版一致（like 模糊匹配）。
- 响应仍通过 `OperationRecordSimpleOut`；`tags` 在库中以 JSON 文本存储，返回前解析为列表。

## 定时任务

- MySQL 表：
  - `vadmin_system_task`：任务主表，主键 `task_id`（24 位十六进制字符串，与 BSON ObjectId 形态一致，便于 API `_id` 兼容）。
  - `vadmin_system_task_group`：分组，字段 `value` 唯一。
  - `scheduler_task_record`：调度执行记录，字段与 kinit-task 监听器写入结构一致。
  - `apscheduler_jobs`：APScheduler `SQLAlchemyJobStore` 使用的作业持久化表（与官方 schema 一致），用于判断任务是否已加入调度器（等价于原 `scheduler_task_jobs` 集合存在性）。
- kinit-api 中 `TaskSqlDal` 等实现原 `TaskDal` / `TaskGroupDal` / `TaskRecordDal` / `SchedulerTaskJobsDal` 的对外行为：列表聚合 `is_active`、`last_run_datetime` 通过 SQL 子查询/EXISTS 实现。
- kinit-task：当 `MONGO_DB_ENABLE = False` 时，使用同步 `mysql+pymysql` 连接与 `SQLAlchemyJobStore`；任务定义与执行记录读写上述 MySQL 表，Redis 订阅协议不变。

## 数据迁移

- 自 Mongo 迁出不在本迭代强制工具化；设计与运维上要求新环境可直接空表 + Alembic 迁移建表。历史数据迁移单独窗口执行（可导出导入脚本，未随仓库交付）。

# 数据模型（摘要）

| 表 | 说明 |
|:---|:---|
| `vadmin_record_operation` | 操作审计，含软删除字段（与项目 BaseModel 一致） |
| `vadmin_system_task` | 定时任务定义，`task_id` PK |
| `vadmin_system_task_group` | 任务分组 |
| `scheduler_task_record` | 调度执行日志 |
| `apscheduler_jobs` | APScheduler 作业存储 |

# 约束与边界

- Mongo 与 MySQL 双开并存不在此设计范围；运行期以 `MONGO_DB_ENABLE` 二选一。
- 关闭 Mongo 时 kinit-task 必须同步配置为 MySQL，否则仅 API 落库无法与调度器联动。
