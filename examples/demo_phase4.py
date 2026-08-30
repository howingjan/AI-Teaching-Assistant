#!/usr/bin/env python
"""
Phase 4 演示脚本 - 可靠性与展示版本（portfolio 质量）

覆盖产品规划 Phase 4 的交付物：

  1. 自动化评测报告（含成本与延迟监控）
  2. 引用校验（独立复算引用准确率）
  3. 失败案例库（自动收集 + 历史案例）
  4. 可重复的 demo 脚本

用法：
    # 完整可靠性与评测演示（推荐）
    python examples/demo_phase4.py --course COMP5310 --export

    # 只运行评测，不更新失败案例库
    python examples/demo_phase4.py --evaluate-only

    # 运行单个任务并展示耗时/成本
    python examples/demo_phase4.py --task lesson --topic "missing value"
    python examples/demo_phase4.py --task problem_solving --problem "你的题目"

说明：
- 需要配置 DEEPSEEK_API_KEY（.env）才能生成真实内容；
- 未配置时自动进入 mock 模式，成本/耗时按 mock 记录，便于离线演示。
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.document.document_loader import DocumentLoader
from src.retrieval.retriever import RetrieverFactory
from src.rag.pipeline import RAGPipeline
from src.rag.llm_client import LLMClient
from src.core.config import Config
from src.core.models import TeachingTask
from src.eval.evaluator import TaskEvaluator
from src.eval.case_sets import build_standard_cases
from src.eval.monitor import UsageMonitor
from src.eval.failure_library import FailureLibrary

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


def make_pipeline(loader, retriever, monitor: UsageMonitor):
    llm = LLMClient()
    if not llm.available:
        print("⚠️  未检测到 DEEPSEEK_API_KEY，将使用 mock 模式演示流程。\n")
    return RAGPipeline(
        retriever=retriever,
        documents=loader.documents,
        llm_client=llm,
        monitor=monitor,
    )


# ---------------------------------------------------------------------------
# Failure collection
# ---------------------------------------------------------------------------

def collect_failures(report, loader, cases, evidence_path: str) -> FailureLibrary:
    """Auto-collect failures observed during the evaluation run."""
    library = FailureLibrary()
    course = loader.index_name

    for case_result in report.cases:
        # 1. Pipeline / LLM errors
        if not case_result.success:
            library.add(
                failure_type="pipeline_error",
                title=f"用例执行失败：{case_result.case_name}",
                description=case_result.error,
                how_detected="评测流程捕获到异常（generate_task 抛错）",
                root_cause="需要结合日志分析；可能是 LLM 超时或输出格式异常",
                resolution="重试该用例；检查 LLMClient 重试与 mock 回退逻辑",
                course=course,
                task=case_result.task_type,
                evidence_path=evidence_path,
            )
            continue

        # 2. Citation errors (independent re-validation)
        has_citation_failure = False
        if (
            case_result.citation_accuracy is not None
            and case_result.citation_accuracy < 1.0
            and case_result.citation_count > 0
        ):
            invalid = case_result.citation_count - case_result.valid_citation_count
            library.add(
                failure_type="citation_error",
                title=f"引用不准确：{case_result.case_name}",
                description=(
                    f"模型提出了 {case_result.citation_count} 条引用，其中 "
                    f"{invalid} 条指向不存在的文档或超出范围的页码。"
                ),
                how_detected="TaskEvaluator 对模型原始输出独立复算引用准确率",
                root_cause="模型在上下文不足时猜测页码/文档；页码索引偏差",
                resolution="引用校验丢弃无效引用并写入 needs_review，提示老师核对",
                course=course,
                task=case_result.task_type,
                evidence_path=evidence_path,
            )
            has_citation_failure = True

        # 3. Out-of-scope questions not refused
        if case_result.out_of_scope and case_result.refused_correctly is False:
            library.add(
                failure_type="out_of_scope",
                title=f"资料外问题未被拒答：{case_result.case_name}",
                description="课程资料不覆盖该问题，但系统仍给出了内容。",
                how_detected="评测用例标记 out_of_scope=True，检查 insufficient_material 与 needs_review",
                root_cause="检索返回了低相关片段，模型未识别资料不足",
                resolution="强化资料不足检测：空检索直接拒答 + 提示词要求显式声明",
                course=course,
                task=case_result.task_type,
                evidence_path=evidence_path,
            )

        # 4. needs_review notes signalling material gaps (non-out-of-scope).
        #    Skip when this case already produced a citation_error above, so the
        #    same underlying failure is not double-counted.
        for note in case_result.needs_review:
            if "引用" in note and ("超出范围" in note or "不存在" in note):
                if has_citation_failure:
                    continue
                library.add(
                    failure_type="citation_error",
                    title=f"需人工确认的引用问题：{case_result.case_name}",
                    description=note,
                    how_detected="needs_review 中携带引用校验告警",
                    root_cause="模型引用超出实际资料范围",
                    resolution="由 CitationValidator 过滤并提示老师",
                    course=course,
                    task=case_result.task_type,
                    evidence_path=evidence_path,
                )
    return library


def seed_historical_failures(library: FailureLibrary, course: str) -> None:
    """Seed curated historical failure cases (portfolio evidence)."""
    library.add(
        failure_type="citation_error",
        title="期末复习把结论引到第 59 页（超出文档范围）",
        description=(
            "生成期末复习包时，模型对知识地图中的一条结论引用了第 59 页，"
            "而该文档总页数不足 59 页。"
        ),
        how_detected="CitationValidator 检测到 out_of_range_pages",
        root_cause="检索上下文充足但模型仍猜测页码，页码索引存在 0/1 偏差",
        resolution="引用校验丢弃无效引用；同时评估输出改为 0 基页码并在提示词中强调",
        course=course,
        task="review",
    )
    library.add(
        failure_type="retrieval_error",
        title="跨语言检索：中文『缺失值』最初检索不到英文课件",
        description=(
            "Phase 1 早期使用 TF-IDF，中文查询『缺失值』无法匹配英文课件中的 "
            "missing value，导致备课包检索为空。"
        ),
        how_detected="Phase 1 检索演示中跨语言查询返回空结果",
        root_cause="TF-IDF 基于精确词匹配，无法跨语言桥接",
        resolution="引入多语言 embedding 检索（multilingual-e5-small），保留 TF-IDF 作为基线",
        course=course,
        task="lesson",
    )


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def save_report(report, monitor: UsageMonitor) -> dict:
    """Persist the Phase 4 evaluation report (md + json)."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = Config.get_output_path("phase4_evaluation_report.md", subdir="eval")
    js_path = Config.get_output_path("phase4_evaluation_report.json", subdir="eval")

    md_content = report.to_markdown()
    md_content += "\n## 成本与延迟明细\n\n" + monitor.to_markdown() + "\n"
    md_path.write_text(md_content, encoding="utf-8")

    data = report.to_dict()
    data["usage"] = monitor.aggregate().to_dict()
    data["report_created"] = stamp
    js_path.write_text(
        __import__("json").dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"markdown": md_path, "json": js_path}


def run_evaluation(args, loader, retriever, monitor: UsageMonitor):
    print("\n" + "=" * 80)
    print("🧪 Phase 4 自动化评测（标准问题集 + 成本/延迟监控）")
    print("=" * 80)

    pipeline = make_pipeline(loader, retriever, monitor)
    cases = build_standard_cases()
    evaluator = TaskEvaluator(documents=loader.documents, chunks=loader.chunks)
    report = evaluator.evaluate(pipeline, cases)

    print(report.to_markdown())
    print("\n--- 成本与延迟明细 ---\n")
    print(monitor.to_markdown())

    report_paths = save_report(report, monitor) if args.export else None
    if report_paths:
        print(f"\n💾 已导出评测报告：\n  {report_paths['markdown']}\n  {report_paths['json']}")

    if not args.evaluate_only:
        evidence = str(report_paths["markdown"]) if report_paths else ""
        library = collect_failures(report, loader, cases, evidence_path=evidence)
        if not library.records:
            seed_historical_failures(library, loader.index_name)
        paths = library.save()
        print(f"\n📁 失败案例库已更新（{len(library.records)} 条）：\n"
              f"  {paths['json']}\n  {paths['markdown']}")
        print(library.to_markdown())

    return report


def run_single_task(args, loader, retriever, monitor: UsageMonitor):
    pipeline = make_pipeline(loader, retriever, monitor)
    task = args.task
    print("\n" + "=" * 80)
    print(f"{TASK_LABELS.get(task, task)}（{task}）")
    print("=" * 80)

    if task == "lesson":
        result = pipeline.generate_lesson(topic=args.topic or "data exploration",
                                          student_level=args.level)
        print(f"\n📖 主题：{result.topic}")
    elif task == "problem_solving":
        result = pipeline.generate_problem_solution(
            problem_text=args.problem or "请解释如何清洗含缺失值的酒店预订数据集",
            top_k=args.top_k,
        )
        print(f"\n📝 题目概括：{result.problem_summary}")
    elif task == "review":
        result = pipeline.generate_review(scope=args.scope or "data exploration and ETL",
                                          student_level=args.level)
        print(f"\n🎯 复习范围：{result.scope}")
    elif task == "cheatsheet":
        result = pipeline.generate_cheatsheet(scope=args.scope or "data types and ETL",
                                              page_limit=args.page_limit)
        print(f"\n📋 速查表：{result.title}")
    elif task == "exam_mapping":
        result = pipeline.generate_exam_mapping(exam_topic=args.exam or "four levels of measurement")
        print(f"\n🗺️ 真题/考点：{result.exam_topic}")
    else:
        print(f"❌ 未知任务：{task}")
        return

    record = monitor.last_record
    if record:
        mode = "真实" if record.mode == "real" else "mock"
        print(f"\n⚡ 耗时 {record.latency_s:.2f}s（{mode}），"
              f"输入 {record.prompt_tokens} / 输出 {record.completion_tokens} tokens，"
              f"预估成本 ${record.cost_usd:.6f}")

    if args.export:
        md = pipeline.save_result(result, "output_phase4", f"{task}_result", output_format="markdown")
        js = pipeline.save_result(result, "output_phase4", f"{task}_result", output_format="json")
        print(f"💾 已导出：\n  {md}\n  {js}")


def main():
    parser = argparse.ArgumentParser(description="AI 教学助手 - Phase 4 可靠性与展示")
    parser.add_argument("--course", default="COMP5310")
    parser.add_argument("--task", choices=list(TASK_LABELS.keys()), default=None,
                        help="运行单个任务（不运行评测）")
    parser.add_argument("--topic", default=None)
    parser.add_argument("--problem", default=None)
    parser.add_argument("--scope", default=None)
    parser.add_argument("--exam", default=None)
    parser.add_argument("--level", default="初学者")
    parser.add_argument("--page-limit", default="两页")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--evaluate-only", action="store_true",
                        help="只评测，不更新失败案例库")
    parser.add_argument("--export", action="store_true", help="导出报告/结果")
    args = parser.parse_args()

    loader, retriever = load_course(args.course)
    monitor = UsageMonitor()  # persists to logs/usage.jsonl

    if args.task:
        run_single_task(args, loader, retriever, monitor)
    else:
        run_evaluation(args, loader, retriever, monitor)

    print("\n✅ Phase 4 演示完成。")


if __name__ == "__main__":
    main()
