#!/usr/bin/env bash
# ============================================================
# AI 教学助手 - 一键本地安装脚本（macOS / Linux）
#
# 用法：  ./scripts/setup.sh
# 作用：  建 venv -> 装依赖 -> 预下载检索模型 -> 生成 .env
# 之后：  ./scripts/run.sh    （或 source .venv/bin/activate && streamlit run app.py）
# ============================================================
set -euo pipefail
cd "$(dirname "$0")/.."

echo ">>> 检测 Python（需要 3.11 / 3.12）"
PY=""
for c in python3.12 python3.11 python3; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
# Homebrew 常见安装路径兜底
if [ -z "$PY" ] && [ -x "/usr/local/opt/python@3.12/bin/python3.12" ]; then
  PY="/usr/local/opt/python@3.12/bin/python3.12"
fi
if [ -z "$PY" ]; then
  echo "❌ 未找到 Python 3.11/3.12，请先安装：https://www.python.org/downloads/"
  exit 1
fi
VER="$("$PY" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
echo "   使用 Python: $PY ($VER)"
case "$VER" in
  3.11|3.12) ;;
  *) echo "⚠️  建议使用 Python 3.12（3.11/3.13 也可能兼容；3.14 不受支持）";;
esac

echo ">>> 创建虚拟环境 .venv"
"$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo ">>> 升级 pip 并安装依赖（torch 较大，首次约需 2-3 GB / 数分钟，请耐心）"
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ">>> 预下载/核对检索模型（首次需联网访问 HuggingFace，之后可离线）"
python scripts/download_embedding_model.py

if [ ! -f .env ]; then
  echo ">>> 生成 .env（模板）"
  cp .env.example .env
  echo "   ✅ 已生成 .env —— 请务必编辑填入 DEEPSEEK_API_KEY"
else
  echo ">>> 检测到已有 .env，跳过"
fi

echo
echo "============================================================"
echo " ✅ 安装完成！接下来："
echo "   1) 编辑 .env，填入你的 DEEPSEEK_API_KEY"
echo "   2) ./scripts/run.sh"
echo "   3) 浏览器打开 http://localhost:8501"
echo "      在「📚 资料库」上传你的课程 PDF 即可开始备课"
echo "============================================================"
