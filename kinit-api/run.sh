#!/usr/bin/env bash
# 一键启动：首次在脚本所在目录创建 .venv、安装依赖、按 settings.DEBUG 对齐执行数据初始化，然后启动服务。
# 数据库连接：环境变量 KINIT_DATABASE_URL 或项目根目录 .env（见 .env.example），勿在配置文件中写死密码。
# Redis：若启用（REDIS_DB_ENABLE 未关闭），须在 .env 中配置 KINIT_REDIS_URL；无密码可用 redis://127.0.0.1:6379/0，有密码见 .env.example。
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
try:
    from dotenv import load_dotenv
    load_dotenv(root / '.env')
except ImportError:
    pass
has_url = bool((os.environ.get('KINIT_DATABASE_URL') or '').strip())
has_parts = all(
    (os.environ.get(k) or '').strip()
    for k in ('KINIT_DATABASE_HOST', 'KINIT_DATABASE_NAME', 'KINIT_DATABASE_USER')
)
if not has_url and not has_parts:
    print('[run.sh] 未配置数据库：请设置 KINIT_DATABASE_URL，或分项设置 KINIT_DATABASE_HOST/NAME/USER（见 .env.example）。', file=sys.stderr)
    sys.exit(1)
"
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

  echo "[run.sh] 初始化数据库与种子数据（须与 application/settings.py 中 DEBUG 一致，数据库须为空，见 README）"
  env_name="$(python -c "from application.settings import DEBUG; print('dev' if DEBUG else 'pro')")"
  if [[ "$env_name" == "dev" ]]; then
    python main.py init --env dev
  else
    python main.py init
  fi
}

if [[ ! -d "$VENV" ]]; then
  bootstrap
else
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
  ensure_asyncmy
fi

require_database_url

exec python main.py run "$@"
