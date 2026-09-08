"""
AI 教学助手 - Streamlit 教师工作台（扁平化版）

两个页面：

  📚 资料库   - 查看课程资料、上传/刷新 PDF、重建索引
  🎯 教学任务 - 多选资料范围，生成「备课 / 期末复习」或「作业讲题」，
                结果内联展示、编辑与导出（MD/JSON/HTML）

启动：
    source AIvenv312/bin/activate
    streamlit run app.py

真实生成必须配置 DEEPSEEK_API_KEY（.env）；未配置时生成会报错提示。
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
    "lesson": "📖 备课 / 期末复习",
    "problem_solving": "✏️ 作业讲题",
}

# 只把 data/ 下的课程目录当作可选课程，过滤 index/output 等系统目录
COURSES = [
    d.name
    for d in Config.DATA_DIR.iterdir()
    if d.is_dir() and d.name not in {Config.INDEX_DIR.name, Config.OUTPUT_DIR.name}
] or ["COMP5310"]


def _init_state() -> None:
    """Initialize persistent session state."""
    defaults = {
        "course": "COMP5310" if "COMP5310" in COURSES else COURSES[0],
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
def get_knowledge_base(course: str, reload_token: int = 0):
    """Load (or build) the course index and create the embedding retriever."""
    loader = DocumentLoader(index_name=course)
    course_path = Config.DATA_DIR / course
    if not loader.chunks:
        # 首次构建：整目录解析并落盘索引
        if course_path.exists():
            loader.load_documents_from_directory(str(course_path))
            loader.save_index()
    else:
        # 索引已存在：把磁盘上新增的课件（含 uploads/）合并进索引。
        # 用 getattr 做保护：若长驻进程加载的是旧版模块（无 sync_directory），
        # 退化为仅从磁盘索引加载，避免 AttributeError 中断页面。
        sync = getattr(loader, "sync_directory", None)
        if callable(sync) and course_path.exists():
            added_docs, _ = sync(str(course_path))
            if added_docs:
                loader.save_index()

    retriever = RetrieverFactory.create(
        "embedding",
        loader.chunks,
        loader.documents,
        cache_path=str(Config.get_embedding_cache_path(course)),
    )
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
    return "🟢 真实生成" if LLMClient().available else "❌ 未配置 API key（需先配置才能生成）"


def refresh_knowledge_base(message: str = "") -> None:
    """Force a full rebuild of the knowledge base and re-render the page."""
    st.session_state.reload_token += 1
    get_knowledge_base.clear()
    if message:
        st.session_state["_toast"] = message
    st.rerun()


def doc_name(documents: dict, doc_id: str) -> str:
    doc = documents.get(doc_id)
    return doc.file_name if doc else doc_id


# ---------------------------------------------------------------------------
# 侧边栏
# ---------------------------------------------------------------------------

def render_sidebar() -> str:
    st.sidebar.title("🎓 AI 教学助手")
    st.sidebar.caption("课程资料驱动的中文备课工作台")

    # 课程标签与下拉框直接放在标题下方（不再使用「全局设置」折叠框）
    st.sidebar.markdown("**课程**")
    course = st.sidebar.selectbox(
        "选择课程",
        COURSES,
        index=COURSES.index(st.session_state.course) if st.session_state.course in COURSES else 0,
        label_visibility="collapsed",
    )
    st.session_state.course = course

    st.sidebar.divider()
    st.sidebar.markdown(f"**模型状态**：{api_status()}")
    st.sidebar.caption(f"· 真实生成使用 {Config.llm.model}；API key 存放在 .env")

    page = st.sidebar.radio(
        "功能导航",
        ["📚 资料库", "🎯 教学任务"],
        key="nav",
    )
    st.sidebar.divider()
    st.sidebar.caption("隐私说明：原始资料仅保存在本地 data/ 目录，可随时删除。")
    return page


# ---------------------------------------------------------------------------
# 页面 1：资料库
# ---------------------------------------------------------------------------

def page_library(loader) -> None:
    st.subheader("📚 资料库")

    toast = st.session_state.pop("_toast", None)
    if toast:
        st.success(toast)

    stats = loader.get_index_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("课程文档", stats["total_documents"])
    c2.metric("知识片段（chunks）", stats["total_chunks"])
    c3.metric("索引更新时间", stats["last_updated"][:16])

    header_col, refresh_col = st.columns([6, 1])
    header_col.markdown("##### 📁 文档清单")
    if refresh_col.button("🔄 刷新", help="重新扫描 data/ 目录并刷新文档清单", use_container_width=True):
        refresh_knowledge_base()

    rows = []
    for doc_id, doc in loader.documents.items():
        info = loader.get_document_info(doc_id)
        rows.append({
            "文件": doc.file_name,
            "类型": doc.document_type.value,
            "页数": doc.total_pages or 1,
            "解析质量": doc.parse_quality.value,
            "片段数": info["total_chunks"],
        })
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
        st.caption("解析质量：good=正常 · partial=部分 · scanned=扫描页 · empty=空页")
    else:
        st.info("知识库为空。请上传课件 PDF。")

    st.markdown("##### ⬆️ 上传资料（仅 PDF）")
    uploaded = st.file_uploader("选择课程资料 PDF", type=["pdf"])
    if uploaded is not None and st.button("解析并加入知识库", type="primary"):
        upload_dir = Config.DATA_DIR / st.session_state.course / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        dest = upload_dir / uploaded.name
        dest.write_bytes(uploaded.getbuffer())

        try:
            # 直接加入当前已加载的 loader 并落盘索引，再整体重建知识库，
            # 这样新文档会立即出现在文档清单中，检索与引用也可用。
            doc, chunks = loader.load_document(str(dest))
            loader.save_index()
            refresh_knowledge_base(f"✅ 已解析 {doc.file_name}（{len(chunks)} 个片段），知识库已刷新。")
        except Exception as exc:  # noqa: BLE001
            st.error(f"解析失败：{exc}")
            st.caption("该文件可能已损坏，或不是可解析的 PDF。")


# ---------------------------------------------------------------------------
# 页面 2：教学任务
# ---------------------------------------------------------------------------

def page_tasks(pipeline, loader) -> None:
    st.subheader("🎯 教学任务")
    st.caption("先多选「资料范围」再选任务。备课会覆盖所选资料的完整知识点；期末复习只需勾选全选全部资料。")

    docs = list(loader.documents.values())
    if not docs:
        st.info("知识库为空。请先在「📚 资料库」上传 PDF。")
        return

    doc_by_name = {d.file_name: d for d in docs}
    # 文件按文件名排序；默认预选最后一个文件（如最新的课件）
    all_names = sorted((d.file_name for d in docs), key=lambda s: s.casefold())

    # ---- 资料范围：可多选；期末复习 = 全选全部资料 ----
    review_all = st.toggle(
        "🎓 期末复习（全选全部资料，覆盖整学期）",
        value=False,
        help="期末复习已并入备课：勾选后自动选中全部课件，生成覆盖整学期知识点的复习/备课材料。",
    )
    if review_all:
        chosen_names = list(all_names)
        document_ids = [d.document_id for d in docs]
        st.caption(f"期末复习模式：已全选 {len(all_names)} 份资料。")
    else:
        chosen_names = st.multiselect(
            "📚 资料范围（可多选；生成将覆盖所选资料的完整知识点）",
            all_names,
            default=[all_names[-1]] if all_names else [],
        )
        document_ids = [doc_by_name[n].document_id for n in chosen_names] or None
        st.caption(f"已选 {len(chosen_names)} 份资料作为本次内容范围。")

    task = st.segmented_control(
        "选择任务",
        list(TASK_LABELS.keys()),
        format_func=lambda t: TASK_LABELS[t],
        default="lesson",
        label_visibility="collapsed",
    )

    if task == "lesson":
        # 不再需要「本周主题」：内容与主题完全由所选资料决定
        duration_h = st.number_input(
            "课堂时长（小时）",
            min_value=0.5,
            max_value=12.0,
            value=2.0,
            step=0.5,
            help="课堂时长越长，生成的讲义内容越详实。",
        )
        inputs = {
            "topic": "",
            "student_level": st.selectbox("学生水平", ["初学者", "有一定基础", "考前冲刺"], index=0),
            "duration": f"{duration_h:g} 小时",
        }
    else:  # problem_solving
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

    # ---- 自定义输出要求（可选）----
    customize = st.checkbox(
        "✍️ 自定义输出结果（可选）",
        help="勾选后可在下方输入你对生成结果的额外指令，系统会把它附加到提示词中一起发给模型。",
    )
    custom_prompt = ""
    if customize:
        custom_prompt = st.text_area(
            "自定义输出指令",
            placeholder="例如：重点讲清 JOIN 的底层代价并多用中文类比；或者：先给反例再讲正确做法……",
            height=120,
        ).strip()
    inputs["extra"] = custom_prompt

    if st.button("🚀 生成教学材料", type="primary", width="stretch"):
        if not document_ids:
            st.warning("请选择至少一份资料，或勾选「期末复习（全选全部资料）」。")
            return
        with st.spinner("正在整理所选资料并真实生成…"):
            try:
                result = pipeline.generate_task(
                    TeachingTask(task),
                    inputs,
                    document_ids=document_ids,
                    scope_names=chosen_names if task == "lesson" else None,
                )
            except Exception as exc:  # noqa: BLE001
                st.error(f"生成失败：{exc}")
                return

        st.session_state.last_result = result
        st.session_state.last_task = task
        st.session_state.last_usage = getattr(pipeline.monitor, "last_record", None)
        st.session_state.last_md = pipeline.export_markdown(result) if task == "lesson" else pipeline._render_markdown(result)

        st.success("✅ 生成完成！结果见下方。")

    _render_result(pipeline)


# ---------------------------------------------------------------------------
# 内联生成结果：预览 / 编辑 / 来源引用 / 导出
# ---------------------------------------------------------------------------

def _render_result(pipeline) -> None:
    """Inline result preview/edit/export shown right below the task form."""
    result = st.session_state.get("last_result")
    if result is None:
        return

    task = st.session_state.get("last_task", "")
    st.divider()
    st.subheader("📄 生成结果")
    st.caption(f"任务：{TASK_LABELS.get(task, task)}")

    usage = st.session_state.get("last_usage")
    if usage is not None:
        cols = st.columns(3)
        cols[0].metric("耗时", f"{usage.latency_s:.2f}s")
        cols[1].metric("Tokens", usage.total_tokens)
        cols[2].metric("预估成本", f"${usage.cost_usd:.6f}")

    if getattr(result, "insufficient_material", False):
        st.warning("⚠️ 资料不足：检索结果较少，请老师核对补充。")
    for note in getattr(result, "needs_review", []) or []:
        st.warning(f"⚠️ {note}")

    edit_mode = st.checkbox("✏️ 编辑模式（直接修改 Markdown）")
    if edit_mode:
        st.session_state.last_md = st.text_area(
            "老师可以直接修改内容（Markdown）",
            value=st.session_state.last_md,
            height=420,
        )
        st.caption("修改后使用下方按钮导出。最终内容由老师审核后用于课堂。")
    else:
        st.markdown(st.session_state.last_md, unsafe_allow_html=False)

    citations = getattr(result, "citations", []) or []
    if citations:
        with st.expander(f"🔗 来源引用（{len(citations)} 条，点击展开原文）"):
            for c in citations:
                snippet = getattr(c, "snippet", None) or ""
                chunk_tag = f" · 片段 `{c.chunk_id}`" if getattr(c, "chunk_id", None) else ""
                st.markdown(f"**{doc_name(pipeline.documents, c.document_id)}** · 第 {c.page} 页{chunk_tag}")
                if snippet:
                    st.caption(snippet[:220])
                st.divider()

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
# 主入口
# ---------------------------------------------------------------------------

def main() -> None:
    page = render_sidebar()

    loader, retriever = get_knowledge_base(
        st.session_state.course,
        st.session_state.reload_token,
    )

    if page == "📚 资料库":
        page_library(loader)
    else:
        monitor = UsageMonitor(persist_path=None)  # UI 内不持久化，仅展示
        pipeline = get_pipeline(loader, retriever, monitor)
        page_tasks(pipeline, loader)


if __name__ == "__main__":
    main()
