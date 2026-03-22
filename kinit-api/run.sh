#!/usr/bin/env bash
# 一键启动：首次在脚本所在目录创建 .venv、安装依赖、按 settings.DEBUG 对齐执行数据初始化，然后启动服务。
# 数据库连接：环境变量 KINIT_DATABASE_URL 或项目根目录 .env（见 .env.example），勿在配置文件中写死密码。
# 前置：已创建空数据库；MySQL 连接信息已注入环境。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
export KINIT_RUN_ROOT="$ROOT"

VENV="$ROOT/.venv"

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
if not (os.environ.get('KINIT_DATABASE_URL') or '').strip():
    print('[run.sh] 未配置 KINIT_DATABASE_URL：请在项目根目录创建 .env（参考 .env.example）或 export 该变量。', file=sys.stderr)
    sys.exit(1)
"
}

if command -v python3.10 &>/dev/null; then
  PY="${PYTHON:-python3.10}"
else
  PY="${PYTHON:-python3}"
fi

bootstrap() {
  echo "[run.sh] 创建虚拟环境: $VENV"
  "$PY" -m venv "$VENV"
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
  python -m pip install --upgrade pip
  pip install -r "$ROOT/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/

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
fi

require_database_url

exec python main.py run "$@"
