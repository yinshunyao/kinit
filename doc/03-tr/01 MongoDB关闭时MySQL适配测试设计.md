# 关联文档

| 类型 | 文档路径 |
|:---|:---|
| 原始需求 | `kinit/doc/01-or/【kinit-api】MongoDB关闭时MySQL兼容适配.md` |
| 开发设计 | `kinit/doc/02-dr/01 MongoDB关闭时MySQL适配.md` |

# 测试范围

- `MONGO_DB_ENABLE=False` 时操作审计中间件写入路径（SQL 分支可调用）。
- `mongo_filter_to_sql_conditions` 对 `like` / `ObjectId` 等元组的解析行为。
- （可选）集成测试需在具备 MySQL 与迁移的环境下手工或 CI 执行；本仓库自动化以无外部依赖的单元测试为主。

# 测试用例

| 编号 | 前置条件 | 操作步骤 | 预期结果 | 自动化 |
|:---|:---|:---|:---|:---|
| TC-01 | 无 | 调用 `mongo_filter_to_sql_conditions`，传入 `name=("like","test")` | 生成一条 `LIKE %test%` 条件 | pytest |
| TC-02 | 无 | 传入 `_id=("ObjectId","507f1f77bcf86cd799439011")` | 得到等值条件且字段为 `task_id` | pytest |
| TC-03 | 无 | 传入无效 ObjectId 字符串 | 抛出 `CustomException` | pytest |

# 自动化测试标识

- 框架：pytest。
- 代码路径：`kinit/kinit-api/test/test_core/test_mongo_mysql_aux.py`。
