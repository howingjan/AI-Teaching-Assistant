#!/usr/bin/env python
"""
Phase 1 演示脚本 - 检索（支持 TF-IDF 和 embedding）

检索方式由 Config.retriever.retriever_type 控制，默认 "embedding"
（多语言语义检索，支持中文查询英文课件）。

用法：
    python examples/demo_phase1.py --course COMP5310 --query "data exploration"
    python examples/demo_phase1.py --course COMP5310 --query "数据探索"   # 跨语言
    python examples/demo_phase1.py --course COMP5310 --interactive
"""

import sys
from pathlib import Path
import argparse

# 添加项目根目录到 sys.path，使脚本从任意目录运行都能 import src
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.document.document_loader import DocumentLoader
from src.retrieval.retriever import RetrieverFactory
from src.core.config import Config


def demo_load_course(course_name: str, data_dir: str = None):
    """加载真实课程数据并演示检索。"""
    if data_dir is None:
        data_dir = str(PROJECT_ROOT / "data")
    
    print("\n" + "=" * 80)
    print(f"🎓 AI 教学助手 - 真实数据演示（{course_name}）")
    print("=" * 80)
    print()
    
    course_path = Path(data_dir) / course_name
    
    # 检查课程目录
    if not course_path.exists():
        print(f"❌ 错误：找不到课程目录 {course_path}")
        print(f"\n💡 建议：")
        print(f"   1. 创建目录：mkdir -p {course_path}")
        print(f"   2. 添加 PDF：cp your_pdf.pdf {course_path}/")
        print(f"   3. 重新运行本脚本")
        return False
    
    # 加载课程资料（增量：已索引的文件会自动跳过）
    # 注意：DocumentLoader.__init__ 已经加载了磁盘上的现有索引，
    # 这里只需增量扫描目录，把新增的 PDF 补进索引。
    print(f"📂 加载课程路径：{course_path}")
    loader = DocumentLoader(index_name=course_name)
    
    try:
        new_docs, new_chunks = loader.load_documents_from_directory(str(course_path))
        
        if new_chunks:
            loader.save_index()
            print(f"✅ 新增 {len(new_chunks)} 个知识点，索引已更新")
        else:
            print(f"✅ 已加载现有索引（{len(loader.chunks)} 个知识点），无新增文件")
    except Exception as e:
        print(f"❌ 加载失败：{e}")
        return False
    
    # 显示统计信息
    print()
    stats = loader.get_index_stats()
    print(f"📊 索引统计：")
    print(f"   • 文档数：{stats['total_documents']}")
    print(f"   • 知识点数：{stats['total_chunks']}")
    print()
    
    # 创建检索器（默认 embedding，可通过 Config.retriever.retriever_type 切换）
    try:
        retriever = RetrieverFactory.create(
            Config.retriever.retriever_type,
            loader.chunks,
            loader.documents,
            model_name=Config.retriever.embedding_model,
            cache_path=str(Config.get_embedding_cache_path(course_name)),
        )
        print(f"🔍 检索器类型：{Config.retriever.retriever_type}")
    except Exception as e:
        print(f"❌ 创建检索器失败：{e}")
        return False
    
    return loader, retriever


def demo_search(loader, retriever, queries: list = None):
    """执行搜索演示。"""
    
    if queries is None:
        queries = [
            "这门课的核心概念是什么？",
            "有什么重要的算法吗？",
            "给我讲解本课程的关键内容",
        ]
    
    print()
    print("🔍 检索演示：")
    print("-" * 80)
    
    for i, query in enumerate(queries, 1):
        print(f"\n【查询 {i}】{query}")
        print()
        
        try:
            results = retriever.search(query, top_k=3)
            
            if not results:
                print("   ❌ 未找到相关内容")
                continue
            
            for rank, result in enumerate(results, 1):
                chunk = result.chunk
                doc = loader.documents.get(chunk.document_id)
                
                print(f"   📍 结果 {rank}（相关度: {result.score:.2f}）")
                print(f"      📄 文档：{doc.file_name if doc else 'Unknown'}")
                print(f"      📌 位置：第 {chunk.page_number} 页")
                if chunk.section:
                    print(f"      🏷️  小节：{chunk.section}")
                print(f"      📝 摘录：{chunk.text[:100]}...")
                print(f"      🔗 引用：[{chunk.document_id}, page {chunk.page_number}]")
                print()
        
        except Exception as e:
            print(f"   ❌ 搜索失败：{e}")
            import traceback
            traceback.print_exc()
    
    print("-" * 80)


def interactive_search(loader, retriever):
    """交互式搜索。"""
    
    print()
    print("💬 交互模式（输入 'quit' 退出）：")
    print()
    
    while True:
        query = input("🎯 输入你的查询：").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        print()
        results = retriever.search(query, top_k=3)
        
        if not results:
            print("❌ 未找到相关内容\n")
            continue
        
        for rank, result in enumerate(results, 1):
            chunk = result.chunk
            doc = loader.documents.get(chunk.document_id)
            
            print(f"【结果 {rank}】相关度 {result.score:.2f}")
            print(f"  📄 {doc.file_name if doc else 'Unknown'}")
            print(f"  📌 第 {chunk.page_number} 页")
            print(f"  📝 {chunk.text[:150]}...")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="AI 教学助手 - 真实数据演示",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 基本演示
  python examples/demo_phase1.py --course COMP5310
  
  # 自定义查询
  python examples/demo_phase1.py --course COMP5310 --query "递归算法" --query "动态规划"
  
  # 交互模式
  python examples/demo_phase1.py --course COMP5310 --interactive
        """
    )
    
    parser.add_argument(
        "--course",
        type=str,
        default="COMP5310",
        help="课程名称（对应 data/ 中的目录）"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="课程数据目录（默认 data）"
    )
    
    parser.add_argument(
        "--query",
        type=str,
        action="append",
        help="自定义查询（可指定多次）"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="进入交互模式"
    )
    
    args = parser.parse_args()
    
    # 加载课程
    result = demo_load_course(args.course, args.data_dir)
    if result is False:
        sys.exit(1)
    
    loader, retriever = result
    
    # 演示搜索
    if args.query:
        demo_search(loader, retriever, args.query)
    else:
        demo_search(loader, retriever)
    
    # 交互模式
    if args.interactive:
        interactive_search(loader, retriever)
    
    print()
    print("=" * 80)
    print("✅ 演示完成！")
    print()
    print("📝 下一步：")
    print("  1. 检查检索结果是否相关")
    print("  2. 如果质量不够好，运行：python -m pytest tests/ -v")
    print("  3. 准备 Phase 2 的 RAG 管道开发")
    print()
    print("📚 更多信息：")
    print("  • 使用指南：docs/README_CN.md")
    print("  • 架构设计：docs/ARCHITECTURE.md")
    print("  • 目录结构：docs/DIRECTORY_GUIDE.md")
    print("=" * 80)


if __name__ == "__main__":
    main()
