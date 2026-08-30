#!/usr/bin/env bash
# =============================================================================
# AI 教学助手 - 可重复的全流程演示脚本（Phase 0-4）
#
# 一条命令跑完整个产品闭环：检索 -> 备课 -> 讲题/复习/速查表/真题映射
# -> 统一评测（含成本/延迟）-> 失败案例库。
#
# 用法：
#   source AIvenv312/bin/activate
#   bash examples/run_all.sh [course]
#
# 需要 DEEPSEEK_API_KEY（.env）才会生成真实内容；否则自动进入 mock 模式。
# =============================================================================

set -euo pipefail

COURSE="${1:-COMP5310}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=============================================================="
echo "🎓 AI 教学助手 - 全流程演示（课程：$COURSE）"
echo "开始时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo "=============================================================="

run() {
    echo
    echo ">>> $*"
    python "$@"
}

# 1) Phase 1 - 可引用知识库与检索（中英文查询）
run examples/demo_phase1.py --course "$COURSE" --query "data exploration"
run examples/demo_phase1.py --course "$COURSE" --query "缺失值"

# 2) Phase 2 - 一键备课
run examples/demo_phase2.py --course "$COURSE" --topic "missing value" --export

# 3) Phase 3 - 作业讲题 / 期末复习 / 速查表 / 真题映射
run examples/demo_phase3.py --course "$COURSE" --task problem_solving --export
run examples/demo_phase3.py --course "$COURSE" --task review --export
run examples/demo_phase3.py --course "$COURSE" --task cheatsheet --export
run examples/demo_phase3.py --course "$COURSE" --task exam_mapping --export

# 4) Phase 4 - 自动化评测（含成本/延迟） + 失败案例库
run examples/demo_phase4.py --course "$COURSE" --export

echo
echo "=============================================================="
echo "✅ 全流程演示完成。"
echo "   - 输出目录：data/output/"
echo "   - 评测报告：data/output/eval/phase4_evaluation_report.md"
echo "   - 失败案例库：data/output/failures/failures.md"
echo "   - 使用记录：logs/usage.jsonl"
echo "   - 启动 UI：streamlit run app.py"
echo "=============================================================="
