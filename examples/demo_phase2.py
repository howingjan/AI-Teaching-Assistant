#!/usr/bin/env python
"""
Phase 2 演示脚本 - 一键备课流程（本周备课包）

用法：
    python examples/demo_phase2.py --course COMP5310 --topic "data exploration"
    python examples/demo_phase2.py --course COMP5310 --topic "ETL" --level 进阶 --duration "2 小时"
    python examples/demo_phase2.py --course COMP5310 --interactive

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


def load_course(course_name: str) -> tuple:
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


def print_lesson(lesson, documents):
    """Pretty-print a generated lesson."""
    print("\n" + "=" * 80)
    print(f"📖 本周备课包：{lesson.topic or '(未命名)'}")
    print("=" * 80)

    if lesson.insufficient_material:
        print("\n⚠️  资料不足：检索结果较少，请老师核对补充。")

    def show(title, items):
        if items:
            print(f"\n【{title}】")
            for i, item in enumerate(items, 1):
                print(f"  {i}. {item}")

    show("学习目标", lesson.learning_objectives)
    show("前置知识", lesson.prerequisites)

    if lesson.core_explanation:
        print(f"\n【中文基础讲解】\n{lesson.core_explanation}")

    if lesson.terminology:
        print("\n【英文专业术语】")
        for t in lesson.terminology:
            print(f"  • {t.term} — {t.explanation}")

    if lesson.examples:
        print("\n【简单例子】")
        for e in lesson.examples:
            title = f"（{e.title}）" if e.title else ""
            print(f"  • {title} {e.content}")

    show("常见误区", lesson.misconceptions)
    show("课堂互动问题", lesson.discussion_questions)

    if lesson.exercises:
        print("\n【课后练习题】")
        for i, ex in enumerate(lesson.exercises, 1):
            print(f"  {i}. {ex.question}")
            if ex.hint:
                print(f"     提示：{ex.hint}")
            if ex.reference_answer:
                print(f"     参考答案：{ex.reference_answer}")

    if lesson.citations:
        print("\n【来源引用】")
        for c in lesson.citations:
            doc = documents.get(c.document_id)
            name = doc.file_name if doc else c.document_id
            print(f"  • {name}（第 {c.page} 页）")

    if lesson.needs_review:
        print("\n【需要老师确认】")
        for r in lesson.needs_review:
            print(f"  ⚠️  {r}")

    print("\n" + "=" * 80)


def run(args):
    loader, retriever = load_course(args.course)

    llm = LLMClient()
    if not llm.available:
        print("⚠️  未检测到 DEEPSEEK_API_KEY，将使用 mock 模式演示流程。\n")

    pipeline = RAGPipeline(retriever=retriever, documents=loader.documents, llm_client=llm)

    topics = args.topic if args.topic else ["data exploration"]
    for topic in topics:
        print(f"\n🎯 生成备课包：{topic}")
        lesson = pipeline.generate_lesson(
            topic=topic,
            student_level=args.level,
            duration=args.duration,
            top_k=args.top_k,
        )
        print_lesson(lesson, loader.documents)

        # Export
        if args.export:
            md_path = pipeline.save_lesson(lesson, output_format="markdown")
            json_path = pipeline.save_lesson(lesson, output_format="json")
            print(f"💾 已导出 Markdown：{md_path}")
            print(f"💾 已导出 JSON：{json_path}")


def interactive(args):
    loader, retriever = load_course(args.course)
    llm = LLMClient()
    pipeline = RAGPipeline(retriever=retriever, documents=loader.documents, llm_client=llm)

    print("\n💬 一键备课（输入 'quit' 退出）")
    while True:
        topic = input("\n🎯 本周主题：").strip()
        if topic.lower() in ("quit", "exit", "q"):
            break
        if not topic:
            continue
        lesson = pipeline.generate_lesson(
            topic=topic,
            student_level=args.level,
            duration=args.duration,
        )
        print_lesson(lesson, loader.documents)


def main():
    parser = argparse.ArgumentParser(description="AI 教学助手 - Phase 2 一键备课")
    parser.add_argument("--course", default="COMP5310", help="课程名称")
    parser.add_argument("--topic", action="append", help="备课主题（可多次指定）")
    parser.add_argument("--level", default="初学者", help="学生水平")
    parser.add_argument("--duration", default="1 小时", help="课堂时长")
    parser.add_argument("--top-k", type=int, default=None, help="检索片段数")
    parser.add_argument("--export", action="store_true", help="导出 Markdown/JSON")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    args = parser.parse_args()

    if args.interactive:
        interactive(args)
    else:
        run(args)


if __name__ == "__main__":
    main()
