#!/usr/bin/env bash
# ============================================================
# AI 教学助手 - 一键启动（macOS / Linux）
# 用法：  ./scripts/run.sh [额外 streamlit 参数]
# ============================================================
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  echo "❌ 尚未安装，请先运行： ./scripts/setup.sh"
  exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate

exec streamlit run app.py "$@"
