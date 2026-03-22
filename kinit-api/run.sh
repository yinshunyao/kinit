#!/usr/bin/env bash
# 一键启动：首次在脚本所在目录创建 .venv、安装依赖、按 settings.DEBUG 对齐执行数据初始化，然后启动服务。
# 若 .venv 已存在但库被清空（表不存在），启动前会自动再次执行 init（迁移 + 种子数据）。
# 跳过自动修复：export KINIT_SKIP_AUTO_INIT=1
# 关键配置均在项目根目录 .env（见 .env.example）：数据库、Redis、HTTP 绑定 KINIT_BIND_HOST / KINIT_BIND_PORT 等。
# 前置：已创建空数据库；MySQL 连接信息已注入环境。
#
# Apple Silicon：请用 arm64 的 Python 创建 .venv；若 asyncmy 报 incompatible architecture，请删 .venv 后指定
#   PYTHON=/opt/homebrew/bin/python3.10 ./run.sh
#
# venv 的版本 = 用于执行「python -m venv」的那条解释器，不会自动跟「你以为的系统 python」对齐。
# macOS 上 /usr/bin/python3 多为 Apple 自带的 3.9，与 PATH 里的 Homebrew python3 不是同一个；勿混用。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
export KINIT_RUN_ROOT="$ROOT"

VENV="$ROOT/.venv"
HOST_ARCH="$(uname -m)"

# 在 arm64 Mac 上优先选用 arm64 解释器，避免 pip 装上 x86_64 的 asyncmy 等扩展导致 dlopen 失败。
resolve_base_python() {
  if [[ -n "${PYTHON:-}" ]]; then
    printf '%s\n' "$PYTHON"
    return
  fi
  if [[ "$HOST_ARCH" == "arm64" ]]; then
    local c mach
    for c in /opt/homebrew/bin/python3.10 /opt/homebrew/bin/python3; do
      if [[ -x "$c" ]]; then
        mach="$("$c" -c "import platform; print(platform.machine())" 2>/dev/null || true)"
        if [[ "$mach" == "arm64" ]]; then
          printf '%s\n' "$c"
          return
        fi
      fi
    done
    for c in python3.10 python3; do
      if command -v "$c" &>/dev/null; then
        local full
        full="$(command -v "$c")"
        mach="$("$full" -c "import platform; print(platform.machine())" 2>/dev/null || true)"
        if [[ "$mach" == "arm64" ]]; then
          printf '%s\n' "$full"
          return
        fi
      fi
    done
    echo "[run.sh] 警告：本机为 arm64，但未找到 arm64 的 python3；虚拟环境可能装上 x86_64 的 asyncmy。建议安装 Homebrew Python 并执行: export PYTHON=/opt/homebrew/bin/python3.10" >&2
  fi
  if command -v python3.10 &>/dev/null; then
    command -v python3.10
  else
    command -v python3
  fi
}

PY="$(resolve_base_python)"

ensure_asyncmy() {
  local err
  if err=$(python -c "import asyncmy" 2>&1); then
    return 0
  fi
  echo "$err" >&2
  if echo "$err" | grep -q 'incompatible architecture'; then
    echo "[run.sh] asyncmy 与当前 CPU 架构不一致（常见于 Rosetta/x86_64 Python 建的 venv）。" >&2
    echo "[run.sh] 请删除虚拟环境后用 arm64 Python 重建，例如：" >&2
    echo "  rm -rf \"$VENV\" && PYTHON=/opt/homebrew/bin/python3.10 \"$ROOT/run.sh\"" >&2
  elif echo "$err" | grep -qE 'No module named|ModuleNotFoundError'; then
    echo "[run.sh] 当前 python 未安装依赖或未激活 .venv。请在项目根目录执行：" >&2
    echo "  source \"$VENV/bin/activate\" && pip install -r \"$ROOT/requirements.txt\"" >&2
    echo "[run.sh] 或删除 .venv 后重新执行 ./run.sh 完成安装。" >&2
  fi
  exit 1
}

require_database_url() {
  python -c "
import os, sys
from pathlib import Path
root = Path(os.environ['KINIT_RUN_ROOT'])
os.chdir(root)
sys.path.insert(0, str(root))
try:
    from application.database_url import get_database_url_raw
    get_database_url_raw()
except Exception as e:
    print('[run.sh] 数据库配置无效或未配置：', e, file=sys.stderr)
    print('[run.sh] 请在 .env 中设置 KINIT_DATABASE_URL 或分项变量（见 .env.example）。', file=sys.stderr)
    sys.exit(1)
"
}

# 退出码：0 核心表已存在；3 可连库但缺表（需 init）；其它 连接/配置失败
check_core_tables_present() {
  python <<'PY'
import os
import sys
from pathlib import Path

root = Path(os.environ["KINIT_RUN_ROOT"])
os.chdir(root)
sys.path.insert(0, str(root))

try:
    from application.database_url import resolve_alembic_sync_url
    from sqlalchemy.engine.url import make_url

    import pymysql
except Exception as e:
    print("[run.sh] 无法导入依赖以检查数据表：", e, file=sys.stderr)
    sys.exit(1)

try:
    u = make_url(resolve_alembic_sync_url())
    conn = pymysql.connect(
        host=u.host,
        port=int(u.port or 3306),
        user=u.username or "",
        password=u.password or "",
        database=u.database or "",
    )
except Exception as e:
    print("[run.sh] 连接数据库失败，无法检查表：", e, file=sys.stderr)
    sys.exit(1)

try:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = %s AND table_name = %s LIMIT 1",
            (u.database, "vadmin_system_settings_tab"),
        )
        sys.exit(0 if cur.fetchone() is not None else 3)
finally:
    conn.close()
PY
}

run_db_init() {
  echo "[run.sh] 初始化数据库与种子数据（须与 application/settings.py 中 DEBUG 一致；空库或缺表时执行，见 README）"
  local env_name
  env_name="$(python -c "from application.settings import DEBUG; print('dev' if DEBUG else 'pro')")"
  if [[ "$env_name" == "dev" ]]; then
    python main.py init --env dev
  else
    python main.py init
  fi
}

ensure_db_schema_before_run() {
  if [[ -n "${KINIT_SKIP_AUTO_INIT:-}" ]]; then
    echo "[run.sh] 已设置 KINIT_SKIP_AUTO_INIT，跳过缺表自动初始化"
    return 0
  fi
  local rc=0
  check_core_tables_present || rc=$?
  if [[ "$rc" -eq 0 ]]; then
    return 0
  fi
  if [[ "$rc" -eq 3 ]]; then
    echo "[run.sh] 检测到核心数据表缺失（例如数据库已清空），正在执行迁移与种子数据初始化…"
    run_db_init
    return 0
  fi
  exit "$rc"
}

bootstrap() {
  echo "[run.sh] 使用解释器创建虚拟环境: $PY ($("$PY" -V 2>&1))"
  echo "[run.sh] 创建虚拟环境: $VENV"
  "$PY" -m venv "$VENV"
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
  python -m pip install --upgrade pip setuptools wheel
  pip install -r "$ROOT/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/

  ensure_asyncmy

  require_database_url

  run_db_init
}

if [[ ! -d "$VENV" ]]; then
  bootstrap
else
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
  ensure_asyncmy
fi

require_database_url

ensure_db_schema_before_run

exec python main.py run
