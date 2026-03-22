
# 使用

## 环境配置
参见文档 "kinit-api/.env.example"，启动后端程序需要复制 .env.example 为 .env，并修改相关配置

## 简单一键启动方式
环境配置好了之后，一键启动会安装依赖和初始化数据库
```shell
# 不指定python
./run.sh
# 指定python
PYTHON=/usr/local/bin/python3 ./run.sh
```

# 开发者功能
## 数据初始化

```shell
# 初始化
python main.py init

# 开发环境
python main.py init --env dev
```

## 依赖环境如果有问题，可以直接删除

```shell
# 删除环境
rm -rf .venv
# 重新运行启动
PYTHON=/opt/homebrew/bin/python3.10 ./run.sh
```

## 帮助文档

在线文档地址（在配置文件里面设置路径或者关闭；端口与 `KINIT_BIND_PORT` 一致）

```
http://127.0.0.1:9000/docs
```


## 新的数据迁移

- 新建模型：
  - 在你的app目录下新建一个models目录，`__init__.py`导入你需要迁移的models
  ```python
  # app/.../your_app/models/__init__.py
  from .your_model import YourModel,YourModel2
  
  ```
  ```python
  # app/.../your_app/models/your_model.py
  from db.db_base import BaseModel
  
  class YourModel(BaseModel):
    # 定义你的model
    ...
  
  class YourModel2(BaseModel):
    # 定义你的model
    ...
  ```
- 根据模型配置你的alembic：
  ```
  # alembic.ini
  [dev]
  ...
  sqlalchemy.url = mysql+pymysql://your_username:password@ip:port/kinit
  ...
  ```
  ```python
  # alembic/env.py
  # 导入项目中的基本映射类，与 需要迁移的 ORM 模型
  from apps.vadmin.auth.models import *
  ...
  from apps.xxx.your_app.models import *
  ```
- 执行数据库迁移命令（终端执行执行脚本）：
  ```shell
  # 执行命令（生产环境）：
  python main.py migrate
  
  # 执行命令（开发环境）：
  python main.py migrate --env dev
  
  # 手工执行时须先让库追上已有迁移，再 autogenerate（否则可能报 Target database is not up to date）
  alembic --name dev upgrade head
  alembic --name dev revision --autogenerate -m 2.0
  alembic --name dev upgrade head
  ```

生成迁移文件后，会在alembic迁移目录中的version目录中多个迁移文件

## 新的CRUD

- 新的模型文件已经建好（上一步迁移时必须）
- 在 scripts/crud_generate/main.py 添加执行命令

```python
# scripts/crud_generate/main.py
if __name__ == '__main__':
    from apps.xxx.your_app.models import YourModel

    crud = CrudGenerate(YourModel, "中文名", "en_name")
    # 只打印代码，不执行创建写入
    crud.generate_codes()
    # 创建并写入代码
    crud.main()
```

- 生成后会自动创建crud, params,schema, views

## 新的路由配置

```python
# application/urls.py

from apps.xxx.your_app.views import app as your_app

urlpatterns = [
    ...,
    {"ApiRouter": your_app, "prefix": "/your_router", "tags": ["your_tag"]},
]
```

完成后在 http://127.0.0.1:9000/docs 验证生成的接口


# 项目结构

使用的是仿照 Django 项目结构：

- alembic：数据库迁移配置目录
  - versions_dev：开发环境数据库迁移文件目录
  - versions_pro：生产环境数据库迁移文件目录
  - env.py：映射类配置文件
- application：主项目配置目录，也存放了主路由文件
  - config：基础环境配置文件
    - development.py：开发环境
    - production.py：生产环境
  - settings.py：主项目配置文件
  - urls.py：主路由文件
- apps：项目的app存放目录
  - vadmin：基础服务
    - auth：用户 - 角色 - 菜单接口服务
      - models：ORM 模型目录
      - params：查询参数依赖项目录
      - schemas：pydantic 模型，用于数据库序列化操作目录
      - utils：登录认证功能接口服务
      - curd.py：数据库操作
      - views.py：视图函数
- core：核心文件目录
  - crud.py：关系型数据库操作核心封装
  - database.py：关系型数据库核心配置
  - data_types.py：自定义数据类型
  - exception.py：异常处理
  - logger：日志处理核心配置
  - middleware.py：中间件核心配置
  - dependencies.py：常用依赖项
  - event.py：全局事件
  - mongo_manage.py：mongodb 数据库操作核心封装
  - validator.py：pydantic 模型重用验证器
- db：ORM模型基类
- logs：日志目录
- static：静态资源存放目录
- utils：封装的一些工具类目录
- main.py：主程序入口文件
- alembic.ini：数据库迁移配置文件

# 开发环境

开发语言：Python 3.10

开发框架：Fastapi 0.101.1

ORM 框架：SQLAlchemy 2.0.20

## 开发工具

Pycharm 2022.3.2

推荐插件：Chinese (Simplified) Language Pack / 中文语言包

代码样式配置：

![image-20230315194534959](https://ktianc.oss-cn-beijing.aliyuncs.com/kinit/public/images/image-20230315194534959.png)


# 参考信息

fastapi Github：https://github.com/tiangolo/fastapi

fastapi 官方文档：https://fastapi.tiangolo.com/zh/

fastapi 更新说明：https://fastapi.tiangolo.com/zh/release-notes/

pydantic 官方文档：https://pydantic-docs.helpmanual.io/

pydantic 数据模型代码生成器官方文档 （Json -> Pydantic）：https://koxudaxi.github.io/datamodel-code-generator/

SQLAlchemy-Utils：https://sqlalchemy-utils.readthedocs.io/en/latest/

alembic 中文文档：https://hellowac.github.io/alembic_doc/zh/_front_matter.html

Typer 官方文档：https://typer.tiangolo.com/

SQLAlchemy 2.0 （官方）: https://docs.sqlalchemy.org/en/20/intro.html#installation

SQLAlchemy 1.4 迁移到 2.0 （官方）：https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#whatsnew-20-orm-declarative-typing

PEP 484 语法（官方）：https://peps.python.org/pep-0484/

