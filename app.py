"""
AI 教学助手 - Streamlit 教师工作台（Phase 4 UI）

产品规划第 5 节定义的本地面板，包含三大区域：

  📚 资料库   - 查看/上传课程资料、索引统计、检索结果可视化
  🎯 教学任务 - 五个常用教学任务入口（本周备课/作业讲题/期末复习/速查表/真题映射）
  📄 生成结果 - 结构化展示、来源引用、需确认项、老师编辑与导出（MD/JSON/HTML）
  📊 评测与失败 - 自动化评测报告与失败案例库（Phase 4 可靠性交付物）

启动：
    source AIvenv312/bin/activate
    streamlit run app.py

需要配置 DEEPSEEK_API_KEY（.env）才能真实生成；未配置时自动进入 mock 模式。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import Config
from src.core.models import TeachingTask
from src.document.document_loader import DocumentLoader
from src.eval.failure_library import FailureLibrary
from src.eval.monitor import UsageMonitor
from src.rag.llm_client import LLMClient
from src.rag.pipeline import RAGPipeline
from src.retrieval.retriever import RetrieverFactory

# ---------------------------------------------------------------------------
# 页面配置与全局状态
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI 教学助手",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

TASK_LABELS = {
    "lesson": "📖 本周备课",
    "problem_solving": "✏️ 作业讲题",
    "review": "🎓 期末复习",
    "cheatsheet": "📋 速查表",
    "exam_mapping": "🗺️ 真题映射",
}

COURSES = [d.name for d in (Config.DATA_DIR).iterdir() if d.is_dir()] or ["COMP5310"]


def _init_state() -> None:
    """Initialize persistent session state."""
    defaults = {
        "course": "COMP5310" if "COMP5310" in COURSES else COURSES[0],
        "retriever_type": "tfidf",
        "reload_token": 0,
        "last_result": None,
        "last_md": "",
        "last_usage": None,
        "last_task": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_state()


@st.cache_resource(show_spinner="加载课程知识库…")
def get_knowledge_base(course: str, retriever_type: str, reload_token: int = 0):
    """Load (or build) the course index and create the selected retriever."""
    loader = DocumentLoader(index_name=course)
    if not loader.chunks:
        course_path = Config.DATA_DIR / course
        if course_path.exists():
            loader.load_documents_from_directory(str(course_path))
            loader.save_index()

    if retriever_type == "embedding":
        retriever = RetrieverFactory.create(
            "embedding",
            loader.chunks,
            loader.documents,
            cache_path=str(Config.get_embedding_cache_path(course)),
        )
    else:
        retriever = RetrieverFactory.create("tfidf", loader.chunks, loader.documents)
    return loader, retriever


def get_pipeline(loader, retriever, monitor: UsageMonitor) -> RAGPipeline:
    llm = LLMClient()
    return RAGPipeline(
        retriever=retriever,
        documents=loader.documents,
        llm_client=llm,
        monitor=monitor,
    )


def api_status() -> str:
    return "🟢 真实生成" if LLMClient().available else "🟡 mock 模式（未配置 API key）"


def doc_name(documents: dict, doc_id: str) -> str:
    doc = documents.get(doc_id)
    return doc.file_name if doc else doc_id


# ---------------------------------------------------------------------------
# 侧边栏
# ---------------------------------------------------------------------------

def render_sidebar() -> str:
    st.sidebar.title("🎓 AI 教学助手")
    st.sidebar.caption("课程资料驱动的中文备课工作台")

    with st.sidebar.expander("⚙️ 全局设置", expanded=True):
        course = st.selectbox("课程", COURSES, index=COURSES.index(st.session_state.course) if st.session_state.course in COURSES else 0)
        retriever_type = st.radio(
            "检索方式",
            ["tfidf", "embedding"],
            index=0,
            format_func=lambda x: "🔤 TF-IDF（快，精确匹配）" if x == "tfidf" else "🧠 Embedding（跨语言语义）",
        )
        st.session_state.course = course
        st.session_state.retriever_type = retriever_type

    st.sidebar.divider()
    st.sidebar.markdown(f"**模型状态**：{api_status()}")
    st.sidebar.caption("· API key 存放在 .env，不会写入代码、日志或导出材料")

    page = st.sidebar.radio(
        "功能导航",
        ["📚 资料库", "🎯 教学任务", "📄 生成结果", "📊 评测与失败案例"],
        key="nav",
    )
    st.sidebar.divider()
    st.sidebar.caption("Phase 1-3 核心 + Phase 4 UI / 评测 / 失败案例库")
    return page


# ---------------------------------------------------------------------------
# 页面 1：资料库
# ---------------------------------------------------------------------------

def page_library(loader, retriever) -> None:
    st.subheader("📚 资料库")
    stats = loader.get_index_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("课程文档", stats["total_documents"])
    c2.metric("知识片段（chunks）", stats["total_chunks"])
    c3.metric("索引更新时间", stats["last_updated"][:16])

    tab_docs, tab_search, tab_upload = st.tabs(["📁 文档清单", "🔍 检索可视化", "⬆️ 上传资料"])

    # ---- 文档清单 ----
    with tab_docs:
        rows = []
        for doc_id, doc in loader.documents.items():
            info = loader.get_document_info(doc_id)
            rows.append({
                "文件": doc.file_name,
                "类型": doc.document_type.value,
                "页数": doc.total_pages or 1,
                "解析质量": doc.parse_quality.value,
                "片段数": info["total_chunks"],
                "ID": doc_id,
            })
        if rows:
            st.dataframe(rows, width="stretch", hide_index=True)
            st.caption("解析质量：good=正常 · partial=部分 · scanned=扫描页 · empty=空页")
        else:
            st.info("知识库为空。请到「⬆️ 上传资料」页面上传课件 PDF / Markdown / 文本。")

        st.markdown("##### 文档内部结构")
        doc_id = st.selectbox(
            "选择文档查看章节结构",
            list(loader.documents.keys()),
            format_func=lambda d: doc_name(loader.documents, d),
        )
        if doc_id:
            structure = loader.get_document_structure(doc_id)
            st.json({
                "sections": structure["sections"],
                "parse_quality": structure["parse_quality"],
                "total_chunks": structure["total_chunks"],
            })

    # ---- 检索可视化 ----
    with tab_search:
        st.markdown("输入任意问题（中英文均可），查看系统会检索到哪些课件片段。")
        q_col, k_col, b_col = st.columns([4, 1, 1])
        query = q_col.text_input("查询", placeholder="例如：missing value / 数据探索 / 缺失值")
        top_k = k_col.slider("Top-K", 1, 10, 5)
        do_search = b_col.button("检索", type="primary", width="stretch")

        if do_search and query.strip():
            results = retriever.search(query, top_k=top_k)
            if not results:
                st.warning("没有检索到相关片段。可以尝试换成英文/关键词，或切换到 Embedding 检索。")
            for r in results:
                with st.expander(
                    f"{doc_name(loader.documents, r.chunk.document_id)} · 第 {r.chunk.page_number} 页 · 相似度 {r.score:.3f}"
                ):
                    st.caption(r.reasoning or "")
                    st.write(r.chunk.text)

    # ---- 上传 ----
    with tab_upload:
        st.markdown("支持 **PDF / Markdown / 纯文本**，上传后自动解析并重建索引。")
        uploaded = st.file_uploader(
            "选择课程资料文件",
            type=["pdf", "md", "txt", "markdown"],
        )
        if uploaded is not None and st.button("解析并加入知识库", type="primary"):
            upload_dir = Config.DATA_DIR / st.session_state.course / "uploads"
            upload_dir.mkdir(parents=True, exist_ok=True)
            dest = upload_dir / uploaded.name
            dest.write_bytes(uploaded.getbuffer())

            try:
                # Build a temp loader to parse without disturbing cache state,
                # then force a full reload by bumping the reload token.
                temp_loader = DocumentLoader(index_name=st.session_state.course)
                doc, chunks = temp_loader.load_document(str(dest))
                st.session_state.reload_token += 1
                get_knowledge_base.clear()
                st.success(f"✅ 已解析 {doc.file_name}（{len(chunks)} 个片段）。知识库已重建。")
            except Exception as exc:  # noqa: BLE001
                st.error(f"解析失败：{exc}")
                st.caption("该文件可能已损坏，或格式暂不支持。详见失败案例库。")
                lib = FailureLibrary()
                lib.add(
                    "parse_error",
                    f"上传解析失败：{uploaded.name}",
                    description=str(exc),
                    how_detected="UI 上传流程捕获异常",
                    root_cause="待分析：文件损坏 / 扫描件 / 不支持格式",
                    resolution="检查文件；扫描件需先做 OCR",
                    course=st.session_state.course,
                    evidence_path=str(dest),
                )
                lib.save()


# ---------------------------------------------------------------------------
# 页面 2：教学任务
# ---------------------------------------------------------------------------

def page_tasks(pipeline) -> None:
    st.subheader("🎯 教学任务")
    st.caption("不要从空白聊天框开始——直接选择老师最常用的教学任务。")

    task = st.segmented_control(
        "选择任务",
        list(TASK_LABELS.keys()),
        format_func=lambda t: TASK_LABELS[t],
        default="lesson",
        label_visibility="collapsed",
    )

    if task == "lesson":
        inputs = {
            "topic": st.text_input("本周主题", value="data exploration / 数据探索"),
            "student_level": st.selectbox("学生水平", ["初学者", "有一定基础", "考前冲刺"], index=0),
            "duration": st.selectbox("课堂时长", ["45 分钟", "1 小时", "1.5 小时", "2 小时"], index=1),
        }
    elif task == "problem_solving":
        inputs = {
            "problem_text": st.text_area(
                "题目文本（作业/真题）",
                value=(
                    "Assignment 1 asks you to explore the hotel booking dataset: identify "
                    "the data types, detect missing values, and explain how you would clean "
                    "the data before analysis."
                ),
                height=140,
            ),
            "goal": st.text_input("讲解目标", value="讲解解题思路，不代写答案"),
        }
    elif task == "review":
        inputs = {
            "scope": st.text_input("复习范围", value="data exploration, ETL and data cleaning"),
            "student_level": st.selectbox("学生水平", ["初学者", "有一定基础", "考前冲刺"], index=2),
        }
    elif task == "cheatsheet":
        inputs = {
            "scope": st.text_input("速查表范围", value="data exploration, data types and ETL"),
            "page_limit": st.selectbox("篇幅限制", ["两页", "一页", "三页"], index=0),
            "allowed": st.text_input("允许携带内容", value="允许携带课程讲义与公式表"),
        }
    else:  # exam_mapping
        inputs = {
            "exam_topic": st.text_area(
                "真题 / 考点",
                value=(
                    "What are the four levels of data measurement (nominal, ordinal, "
                    "interval, ratio) and why do they matter for choosing statistics and charts?"
                ),
                height=100,
            )
        }

    if st.button("🚀 生成教学材料", type="primary", width="stretch"):
        with st.spinner("正在检索课程资料并生成…"):
            try:
                result = pipeline.generate_task(TeachingTask(task), inputs)
            except Exception as exc:  # noqa: BLE001
                st.error(f"生成失败：{exc}")
                lib = FailureLibrary()
                lib.add(
                    "pipeline_error",
                    f"生成失败：{TASK_LABELS[task]}",
                    description=str(exc),
                    how_detected="UI 生成流程捕获异常",
                    root_cause="待分析",
                    resolution="重试；检查 API key 与网络",
                    course=st.session_state.course,
                    task=task,
                )
                lib.save()
                return

        st.session_state.last_result = result
        st.session_state.last_task = task
        st.session_state.last_usage = getattr(pipeline.monitor, "last_record", None)
        st.session_state.last_md = pipeline.export_markdown(result) if task == "lesson" else pipeline._render_markdown(result)

        st.success("✅ 生成完成！请到「📄 生成结果」页审核、编辑与导出。")
        if st.button("前往生成结果页 👉"):
            st.session_state.nav = "📄 生成结果"
            st.rerun()

        _preview_result(result, pipeline)


# ---------------------------------------------------------------------------
# 页面 3：生成结果
# ---------------------------------------------------------------------------

def _preview_result(result, pipeline) -> None:
    """Inline structured preview used right after generation."""
    if getattr(result, "insufficient_material", False):
        st.warning("⚠️ 资料不足：检索到的课程内容较少，请老师核对补充后再使用。")
    for note in getattr(result, "needs_review", []) or []:
        st.warning(f"⚠️ {note}")
    st.markdown(st.session_state.last_md, unsafe_allow_html=False)


def page_result(pipeline) -> None:
    st.subheader("📄 生成结果")
    result = st.session_state.get("last_result")
    if result is None:
        st.info("还没有生成结果。请先到「🎯 教学任务」页生成一份教学材料。")
        return

    task = st.session_state.get("last_task", "")
    st.caption(f"任务：{TASK_LABELS.get(task, task)}")

    # 成本与延迟（Phase 4 监控）
    usage = st.session_state.get("last_usage")
    if usage is not None:
        mode = "🟢 真实" if usage.mode == "real" else "🟡 mock"
        cols = st.columns(4)
        cols[0].metric("模式", mode)
        cols[1].metric("耗时", f"{usage.latency_s:.2f}s")
        cols[2].metric("Tokens", usage.total_tokens)
        cols[3].metric("预估成本", f"${usage.cost_usd:.6f}")

    if getattr(result, "insufficient_material", False):
        st.warning("⚠️ 资料不足：检索结果较少，请老师核对补充。")
    for note in getattr(result, "needs_review", []) or []:
        st.warning(f"⚠️ {note}")

    tab_view, tab_edit = st.tabs(["👁️ 预览", "✏️ 编辑"])

    with tab_view:
        st.markdown(st.session_state.last_md)

    with tab_edit:
        edited = st.text_area(
            "老师可以直接修改内容（Markdown）",
            value=st.session_state.last_md,
            height=420,
        )
        st.session_state.last_md = edited
        st.caption("修改后使用下方按钮导出。最终内容由老师审核后用于课堂。")

    # 来源引用（可展开查看原文片段）
    citations = getattr(result, "citations", []) or []
    if citations:
        with st.expander(f"🔗 来源引用（{len(citations)} 条，点击展开原文）"):
            for c in citations:
                snippet = getattr(c, "snippet", None) or ""
                st.markdown(
                    f"**{doc_name(pipeline.documents, c.document_id)}** · 第 {c.page} 页"
                )
                if snippet:
                    st.caption(snippet[:220])
                st.divider()

    # 导出
    st.markdown("##### 📤 导出")
    filename = pipeline._safe_name(
        getattr(result, "topic", "") or getattr(result, "title", "") or getattr(result, "scope", "") or "teaching_material"
    ) or "teaching_material"
    md_bytes = st.session_state.last_md.encode("utf-8")
    json_bytes = json.dumps(result.to_dict(), ensure_ascii=False, indent=2).encode("utf-8")
    html_bytes = pipeline.render_markdown_html(st.session_state.last_md, title=filename).encode("utf-8")

    col_a, col_b, col_c = st.columns(3)
    col_a.download_button("⬇️ 导出 Markdown", md_bytes, file_name=f"{filename}.md", width="stretch")
    col_b.download_button("⬇️ 导出 HTML", html_bytes, file_name=f"{filename}.html", width="stretch")
    col_c.download_button("⬇️ 导出 JSON", json_bytes, file_name=f"{filename}.json", width="stretch")


# ---------------------------------------------------------------------------
# 页面 4：评测与失败案例
# ---------------------------------------------------------------------------

def page_quality(loader, retriever) -> None:
    st.subheader("📊 评测与失败案例（Phase 4 可靠性）")

    tab_report, tab_failures, tab_run = st.tabs(["📈 最新评测报告", "🗂️ 失败案例库", "▶️ 运行评测"])

    with tab_report:
        report_path = Config.get_output_path("phase4_evaluation_report.md", subdir="eval")
        if report_path.exists():
            st.markdown(report_path.read_text(encoding="utf-8"))
        else:
            st.info("还没有评测报告。到「▶️ 运行评测」标签页生成。")

    with tab_failures:
        lib = FailureLibrary()
        st.markdown(f"**当前共 {len(lib.records)} 条失败案例**（产品规划 7.3：必须保留失败案例）")
        st.markdown(lib.to_markdown())

    with tab_run:
        st.markdown(
            "运行标准评测问题集（7 个用例，含资料外拒答测试）。"
            "需要调用 LLM，未配置 API key 时以 mock 模式运行。"
        )
        if st.button("🚀 运行评测", type="primary"):
            from src.eval.case_sets import build_standard_cases
            from src.eval.evaluator import TaskEvaluator

            monitor = UsageMonitor()
            pipeline = get_pipeline(loader, retriever, monitor)
            with st.spinner("正在运行评测（约需数分钟）…"):
                evaluator = TaskEvaluator(documents=loader.documents, chunks=loader.chunks)
                report = evaluator.evaluate(pipeline, build_standard_cases())

            md_path = Config.get_output_path("phase4_evaluation_report.md", subdir="eval")
            js_path = Config.get_output_path("phase4_evaluation_report.json", subdir="eval")
            md_path.write_text(report.to_markdown() + "\n## 成本与延迟明细\n\n" + monitor.to_markdown() + "\n", encoding="utf-8")
            data = report.to_dict()
            data["usage"] = monitor.aggregate().to_dict()
            js_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

            st.success(f"评测完成！报告已保存：\n`{md_path}`")
            st.markdown(report.to_markdown())


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main() -> None:
    page = render_sidebar()

    loader, retriever = get_knowledge_base(
        st.session_state.course,
        st.session_state.retriever_type,
        st.session_state.reload_token,
    )

    if page == "📚 资料库":
        page_library(loader, retriever)
    elif page == "🎯 教学任务":
        monitor = UsageMonitor(persist_path=None)  # UI 内不持久化，仅展示
        pipeline = get_pipeline(loader, retriever, monitor)
        page_tasks(pipeline)
    elif page == "📄 生成结果":
        monitor = UsageMonitor(persist_path=None)
        pipeline = get_pipeline(loader, retriever, monitor)
        page_result(pipeline)
    else:
        page_quality(loader, retriever)

    st.sidebar.caption("---")
    st.sidebar.caption("隐私说明：原始资料仅保存在本地 data/ 目录，可随时删除。")


if __name__ == "__main__":
    main()
