#!/usr/bin/env python
"""
Phase 3 演示脚本 - 作业讲题 / 期末复习 / 速查表 / 真题映射 + 统一评测

用法：
    # 运行全部四个 Phase 3 任务
    python examples/demo_phase3.py --course COMP5310

    # 只运行一个任务（并导出）
    python examples/demo_phase3.py --task problem_solving --export
    python examples/demo_phase3.py --task review --export
    python examples/demo_phase3.py --task cheatsheet --export
    python examples/demo_phase3.py --task exam_mapping --export

    # 自定义输入
    python examples/demo_phase3.py --task problem_solving --problem "你的题目文本"

    # 运行统一任务评测（内置问题集 + 资料外拒答测试）
    python examples/demo_phase3.py --evaluate --export-eval

说明：
- 需要配置 DEEPSEEK_API_KEY（.env）才能生成真实内容；
- 未配置时自动进入 mock 模式，用于演示完整流程。
"""

import sys
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.document.document_loader import DocumentLoader
from src.retrieval.retriever import RetrieverFactory
from src.rag.pipeline import RAGPipeline
from src.rag.llm_client import LLMClient
from src.core.config import Config
from src.core.models import TeachingTask
from src.eval.evaluator import TaskEvaluator, EvaluationCase
from src.eval.case_sets import build_standard_cases

DEFAULT_PROBLEM = (
    "Assignment 1 asks you to explore the hotel booking dataset: identify the "
    "data types, detect missing values, and explain how you would clean the "
    "data before analysis. Guide the student through the reasoning."
)
DEFAULT_REVIEW_SCOPE = "data exploration, ETL and data cleaning"
DEFAULT_CHEATSHEET_SCOPE = "data exploration, data types and ETL"
DEFAULT_EXAM_TOPIC = (
    "What are the four levels of data measurement (nominal, ordinal, interval, "
    "ratio) and why do they matter for choosing statistics and charts?"
)

TASK_LABELS = {
    "lesson": "📖 本周备课",
    "problem_solving": "✏️ 作业讲题",
    "review": "🎓 期末复习",
    "cheatsheet": "📋 速查表",
    "exam_mapping": "🗺️ 真题映射",
}


def load_course(course_name: str):
    """Load (or build) the course index and return (loader, retriever)."""
    course_path = PROJECT_ROOT / "data" / course_name
    if not course_path.exists():
        print(f"❌ 找不到课程目录：{course_path}")
        sys.exit(1)

    loader = DocumentLoader(index_name=course_name)
    if not loader.chunks:
        print(f"⏳ 建立索引：{course_path}")
        loader.load_documents_from_directory(str(course_path))
        loader.save_index()
    else:
        print(f"✅ 已加载现有索引：{len(loader.chunks)} 个知识点")

    retriever = RetrieverFactory.create("tfidf", loader.chunks, loader.documents)
    return loader, retriever


def make_pipeline(loader, retriever):
    llm = LLMClient()
    if not llm.available:
        print("⚠️  未检测到 DEEPSEEK_API_KEY，将使用 mock 模式演示流程。\n")
    return RAGPipeline(retriever=retriever, documents=loader.documents, llm_client=llm)


def run_single(args, pipeline, loader):
    task = args.task
    label = TASK_LABELS.get(task, task)
    print("\n" + "=" * 80)
    print(f"{label}（{task}）")
    print("=" * 80)

    if task == "problem_solving":
        problem = args.problem or DEFAULT_PROBLEM
        print(f"\n📝 题目：{problem}\n")
        result = pipeline.generate_problem_solution(
            problem_text=problem,
            goal=args.goal,
            top_k=args.top_k,
        )
        filename = args.out_name or "assignment1_problem_solution"
        _print_problem_solution(result, loader.documents)
        _maybe_export(args, pipeline, result, "problem_solutions", filename)

    elif task == "review":
        scope = args.scope or DEFAULT_REVIEW_SCOPE
        print(f"\n🎯 复习范围：{scope}\n")
        result = pipeline.generate_review(
            scope=scope,
            student_level=args.level,
            top_k=args.top_k,
        )
        filename = args.out_name or "final_review"
        _print_review(result, loader.documents)
        _maybe_export(args, pipeline, result, "reviews", filename)

    elif task == "cheatsheet":
        scope = args.scope or DEFAULT_CHEATSHEET_SCOPE
        print(f"\n📋 速查表范围：{scope}（{args.page_limit}）\n")
        result = pipeline.generate_cheatsheet(
            scope=scope,
            page_limit=args.page_limit,
            top_k=args.top_k,
        )
        filename = args.out_name or "two_page_cheatsheet"
        _print_cheatsheet(result, loader.documents)
        _maybe_export(args, pipeline, result, "cheat_sheets", filename)

    elif task == "exam_mapping":
        exam_topic = args.exam or DEFAULT_EXAM_TOPIC
        print(f"\n🗺️ 真题/考点：{exam_topic}\n")
        result = pipeline.generate_exam_mapping(
            exam_topic=exam_topic,
            top_k=args.top_k,
        )
        filename = args.out_name or "exam_knowledge_mapping"
        _print_exam_mapping(result, loader.documents)
        _maybe_export(args, pipeline, result, "exam_mappings", filename)

    else:  # lesson (Phase 2, included for completeness)
        topic = args.topic or DEFAULT_REVIEW_SCOPE
        result = pipeline.generate_lesson(topic=topic, student_level=args.level)
        filename = args.out_name or "phase3_lesson"
        _maybe_export(args, pipeline, result, "lesson_plans", filename)
        print(f"\n📖 已生成备课包：{result.topic}")


def _maybe_export(args, pipeline, result, subdir, filename):
    if args.export:
        md = pipeline.save_result(result, subdir, filename, output_format="markdown")
        js = pipeline.save_result(result, subdir, filename, output_format="json")
        print(f"\n💾 已导出 Markdown：{md}")
        print(f"💾 已导出 JSON：{js}")


def run_evaluation(args, pipeline, loader):
    """Run the built-in evaluation question set."""
    print("\n" + "=" * 80)
    print("🧪 统一任务评测（内置问题集 + 资料外拒答测试）")
    print("=" * 80)

    cases = build_standard_cases()

    evaluator = TaskEvaluator(documents=loader.documents, chunks=loader.chunks)
    report = evaluator.evaluate(pipeline, cases)

    print(report.to_markdown())

    if args.export_eval:
        md_path = Config.get_output_path("phase3_evaluation_report.md", subdir="eval")
        md_path.write_text(report.to_markdown(), encoding="utf-8")
        js_path = Config.get_output_path("phase3_evaluation_report.json", subdir="eval")
        js_path.write_text(report.to_json(), encoding="utf-8")
        print(f"💾 已导出评测报告：\n  {md_path}\n  {js_path}")

    return report


# ---------------------------------------------------------------------------
# Pretty printers
# ---------------------------------------------------------------------------

def _print_problem_solution(r, documents):
    print(f"📌 题目概括：{r.problem_summary}")
    if r.insufficient_material:
        print("⚠️  资料不足，请老师核对补充。")

    if r.knowledge_points:
        print("\n【考查的知识点】")
        for k in r.knowledge_points:
            print(f"  • {k.name} — {k.explanation}")

    if r.steps:
        print("\n【分步解题思路】")
        for i, s in enumerate(r.steps, 1):
            print(f"  第 {i} 步：{s.description}")
            if s.hint:
                print(f"     提示：{s.hint}")

    if r.layered_hints:
        print("\n【分层提示】")
        for h in r.layered_hints:
            print(f"  Level {h.level}：{h.hint}")

    if r.rubric_mapping:
        print("\n【与评分标准的对应】")
        for m in r.rubric_mapping:
            print(f"  • {m.criterion} → {m.how_to_earn}")

    if r.reference_direction:
        print(f"\n【参考解题方向】\n{r.reference_direction}")

    _print_citations(r, documents)
    _print_needs_review(r)


def _print_review(r, documents):
    print(f"🎯 复习范围：{r.scope}")
    if r.insufficient_material:
        print("⚠️  资料不足，请老师核对补充。")

    if r.knowledge_map:
        print("\n【课程知识点地图】")
        for n in r.knowledge_map:
            print(f"  • {n.name}（{n.chapter or '未标注章节'}）— {n.core_idea}")
            if n.depends_on:
                print(f"     依赖：{', '.join(n.depends_on)}")

    if r.confusion_points:
        print("\n【高频混淆点】")
        for c in r.confusion_points:
            print(f"  • {c.a} vs {c.b}：{c.difference}")

    if r.self_test_questions:
        print("\n【自测题】")
        for q in r.self_test_questions:
            print(f"  • {q.question}")

    if r.exam_mapping:
        print("\n【真题对应知识点】")
        for e in r.exam_mapping:
            print(f"  • {e.exam_topic} → {', '.join(e.knowledge_points)}")

    if r.priority_advice:
        print("\n【复习优先级建议】")
        for p in r.priority_advice:
            print(f"  • {p}")

    _print_citations(r, documents)
    _print_needs_review(r)


def _print_cheatsheet(r, documents):
    print(f"📋 标题：{r.title}")
    print(f"   覆盖范围：{r.scope}")
    print(f"   篇幅估算：{'在限制内' if r.within_page_limit else '⚠️ 可能超出限制'}")

    for sec in r.sections:
        print(f"\n【{sec.heading}】")
        for item in sec.items:
            src = ""
            if item.source:
                doc = documents.get(item.source.document_id)
                name = doc.file_name if doc else item.source.document_id
                src = f"（{name} p.{item.source.page}）"
            print(f"  [{item.item_type}] {item.label}：{item.content} {src}")

    if r.layout_notes:
        print("\n【排版建议】")
        for note in r.layout_notes:
            print(f"  • {note}")

    _print_needs_review(r)


def _print_exam_mapping(r, documents):
    print(f"🗺️ 真题/考点：{r.exam_topic}")
    if r.knowledge_points:
        print("\n【对应的知识点】")
        for k in r.knowledge_points:
            ev = ", ".join(
                f"{documents.get(c.document_id).file_name if documents.get(c.document_id) else c.document_id} p.{c.page}"
                for c in k.evidence
            )
            print(f"  • {k.name}（{k.chapter or '未标注章节'}）— {k.relevance}")
            if ev:
                print(f"     依据：{ev}")
    if r.coverage_gap:
        print(f"\n⚠️  资料未覆盖的考点：{r.coverage_gap}")
    _print_needs_review(r)


def _print_citations(r, documents):
    if getattr(r, "citations", None):
        print("\n【来源引用】")
        for c in r.citations:
            doc = documents.get(c.document_id)
            name = doc.file_name if doc else c.document_id
            print(f"  • {name}（第 {c.page} 页）")


def _print_needs_review(r):
    if getattr(r, "needs_review", None):
        print("\n【需要老师确认】")
        for note in r.needs_review:
            print(f"  ⚠️  {note}")


def main():
    parser = argparse.ArgumentParser(description="AI 教学助手 - Phase 3 演示")
    parser.add_argument("--course", default="COMP5310")
    parser.add_argument(
        "--task",
        choices=["lesson", "problem_solving", "review", "cheatsheet", "exam_mapping"],
        default="problem_solving",
        help="要运行的教学任务（默认 problem_solving）",
    )
    parser.add_argument("--problem", default=None, help="作业/真题题目文本")
    parser.add_argument("--scope", default=None, help="复习/速查表范围")
    parser.add_argument("--exam", default=None, help="真题/考点")
    parser.add_argument("--topic", default=None, help="备课主题")
    parser.add_argument("--goal", default="讲解解题思路，不代写答案", help="讲题目标")
    parser.add_argument("--level", default="初学者", help="学生水平")
    parser.add_argument("--page-limit", default="两页", help="速查表篇幅限制")
    parser.add_argument("--top-k", type=int, default=None, help="检索片段数")
    parser.add_argument("--out-name", default=None, help="导出文件名（不含扩展名）")
    parser.add_argument("--export", action="store_true", help="导出 Markdown/JSON")
    parser.add_argument("--evaluate", action="store_true", help="运行统一任务评测")
    parser.add_argument("--export-eval", action="store_true", help="导出评测报告")
    args = parser.parse_args()

    loader, retriever = load_course(args.course)
    pipeline = make_pipeline(loader, retriever)

    if args.evaluate:
        run_evaluation(args, pipeline, loader)
    else:
        run_single(args, pipeline, loader)

    print("\n✅ Phase 3 演示完成。")


if __name__ == "__main__":
    main()
