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

import hashlib
import json
import logging
import sys
import uuid
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import Config
from src.core.models import TeachingTask
from src.core.runtime import build_knowledge_base, build_pipeline
from src.course_update.graph import build_course_update_graph
from src.course_update.library_update import (
    list_replacement_backups,
    replace_library_document,
    restore_library_backup,
)
from src.course_update.pdf_export import detect_pdf_converter, export_docx_to_pdf
from src.eval.monitor import UsageMonitor
from src.rag.llm_client import LLMClient
from src.rag.pipeline import RAGPipeline

logger = logging.getLogger(__name__)

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
    """Load (or build) the course index and create the configured retriever."""
    return build_knowledge_base(course)


def get_pipeline(loader, retriever, monitor: UsageMonitor) -> RAGPipeline:
    return build_pipeline(loader, retriever, monitor)


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


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
        ["📚 资料库", "🎯 教学任务", "🆕 新旧课件比对"],
        key="nav",
    )
    st.sidebar.divider()
    st.sidebar.caption(
        "常规资料保存在本地；课件比对功能会将文本发送到配置的 LLM API。"
    )
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

    st.divider()
    st.markdown("##### ↩️ 资料库版本回滚")
    backups = list_replacement_backups(st.session_state.course)
    if not backups:
        st.caption("尚无课件替换备份。")
        return
    backup_by_id = {backup["backup_id"]: backup for backup in backups}
    selected_backup = st.selectbox(
        "选择要恢复的旧版本",
        options=list(backup_by_id),
        format_func=lambda backup_id: (
            f"{backup_by_id[backup_id]['file_name']} · "
            f"{backup_by_id[backup_id]['created_at'][:19]}"
        ),
        key=f"library_rollback_choice_{st.session_state.course}",
    )
    selected = backup_by_id[selected_backup]
    st.caption(
        f"备份 SHA-256：`{selected['sha256']}`。恢复会重新解析文件、"
        "重建索引并使 embedding 缓存失效。"
    )
    confirmed = st.checkbox(
        "我确认将所选旧版本恢复到当前课程资料库。",
        key=f"library_rollback_confirm_{st.session_state.course}_{selected_backup}",
    )
    if st.button(
        "恢复所选备份",
        disabled=not confirmed,
        key=f"library_rollback_{st.session_state.course}_{selected_backup}",
    ):
        try:
            restore_library_backup(
                loader,
                st.session_state.course,
                selected_backup,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Course-library rollback failed")
            st.error(f"恢复失败：{exc}")
            return
        refresh_knowledge_base("已恢复备份版本，课程索引和检索缓存已刷新。")


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


def _render_course_update_report(state: dict) -> None:
    """Render evidence-linked comparison results and reviewed revision actions."""
    st.subheader("📊 覆盖度报告")
    report = state.get("coverage_report", [])
    status_labels = {
        "covered": "✅ 已覆盖",
        "partial": "🟡 部分覆盖",
        "missing": "🔴 未发现",
        "conflict": "🟠 可能冲突",
        "uncertain": "⚪ 需人工确认",
    }
    counts = {
        status: sum(item["coverage"] == status for item in report)
        for status in status_labels
    }
    st.write(" · ".join(
        f"{status_labels[key]}：{count}" for key, count in counts.items()
    ))
    st.warning(
        "这是 AI 辅助审核结果，不代表完全覆盖证明。请逐项核对课件原文；"
        "证据只用于支持审核，不应跳过教师判断。"
    )

    for item in report:
        with st.expander(
            f"{status_labels[item['coverage']]} · {item['topic_id']} {item['topic']}"
        ):
            st.markdown(item["description"] or "学校课件未提供额外描述。")
            st.markdown(f"**差异：** {item['gap'] or '模型未指出明确差异'}")
            st.markdown(
                f"**建议：** {item['recommendation'] or '请教师自行判断是否需要补充'}"
            )
            st.caption(f"置信度（仅供排序参考）：{item['confidence']:.2f}")
            st.markdown("**最新学校课件证据**")
            for source in item["school_sources"]:
                st.caption(
                    f"{source['file_name']} · 第 {source['page']} 页 · "
                    f"{source['chunk_id']}"
                )
                st.write(source["excerpt"])
            st.markdown("**往期补习课件检索证据**")
            if item["tutoring_sources"]:
                for source in item["tutoring_sources"]:
                    position = (
                        f"第 {source['page']} 页"
                        if source["page"] is not None
                        else source["section"] or "DOCX 片段"
                    )
                    st.caption(
                        f"{source['file_name']} · {position} · {source['chunk_id']}"
                    )
                    st.write(source["excerpt"])
            else:
                st.info("没有找到可引用的补习课件证据。")

    report_json = Path(state["report_json_path"]).read_bytes()
    report_markdown = Path(state["report_markdown_path"]).read_bytes()
    col_json, col_markdown = st.columns(2)
    col_json.download_button(
        "⬇️ 下载覆盖报告 JSON",
        report_json,
        file_name="coverage_report.json",
        mime="application/json",
        use_container_width=True,
    )
    col_markdown.download_button(
        "⬇️ 下载覆盖报告 Markdown",
        report_markdown,
        file_name="coverage_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

    recommendations = [
        item for item in report
        if item["coverage"] != "covered" and item["recommendation"].strip()
    ]
    if not recommendations:
        st.info("当前报告没有可供自动生成修订内容的建议。")
        return

    st.divider()
    st.markdown("##### ✍️ 选择建议，生成修订版 DOCX")
    st.caption("原始补习课件保持不变；系统仅在本地输出目录生成新副本。")
    selected_ids = st.multiselect(
        "选择要采纳的建议",
        options=[item["topic_id"] for item in recommendations],
        format_func=lambda topic_id: next(
            f"{item['topic_id']} · {item['topic']}"
            for item in recommendations
            if item["topic_id"] == topic_id
        ),
        key=f"course_update_selected_{state['task_id']}",
    )
    if st.button(
        "生成修订版 DOCX 副本",
        type="primary",
        disabled=not selected_ids,
        key=f"course_update_revise_{state['task_id']}",
    ):
        revision_state = {
            **state,
            "action": "revise",
            "selected_recommendation_ids": selected_ids,
        }
        try:
            with st.spinner("正在生成并校验 DOCX 副本…"):
                revised = build_course_update_graph(LLMClient()).invoke(revision_state)
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "Course revision generation failed for task %s",
                state.get("task_id"),
            )
            st.error(f"修订版生成失败：{exc}")
            return
        st.session_state.course_update_state = revised
        st.success("修订版 DOCX 副本已生成，原文件未被修改。")

    current = st.session_state.get("course_update_state", {})
    revision_path = current.get("revision_docx_path")
    if revision_path and Path(revision_path).is_file():
        st.download_button(
            "⬇️ 下载修订版 DOCX",
            Path(revision_path).read_bytes(),
            file_name=Path(revision_path).name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
        with st.expander("可选：将修订版 DOCX 导出为 PDF"):
            converter = detect_pdf_converter()
            if converter is None:
                st.caption(
                    "修订版 DOCX 已生成，可直接下载。PDF 转换是独立的可选功能；"
                    "当前未安装 LibreOffice，因此不影响 DOCX 生成或下载。"
                )
                st.code("brew install --cask libreoffice", language="bash")
                st.caption(
                    "安装后重启应用，即可在此处使用 PDF 导出。"
                )
            else:
                st.caption(f"本地 PDF 转换器：`{converter}`。")
                pdf_path = Path(revision_path).with_suffix(".pdf")
                if st.button(
                    "转换修订版为 PDF",
                    key=f"course_update_pdf_{current['task_id']}",
                ):
                    try:
                        exported = export_docx_to_pdf(revision_path, pdf_path)
                        st.session_state[
                            f"course_update_pdf_path_{current['task_id']}"
                        ] = str(exported)
                        st.success("PDF 已转换并通过文件校验；DOCX 原件保留。")
                    except Exception as exc:  # noqa: BLE001
                        logger.exception(
                            "Course PDF export failed for task %s",
                            current.get("task_id"),
                        )
                        st.error(f"PDF 导出失败：{exc}")
                saved_pdf = st.session_state.get(
                    f"course_update_pdf_path_{current['task_id']}"
                )
                if saved_pdf and Path(saved_pdf).is_file():
                    st.download_button(
                        "⬇️ 下载修订版 PDF",
                        Path(saved_pdf).read_bytes(),
                        file_name=Path(saved_pdf).name,
                        mime="application/pdf",
                        key=f"course_update_pdf_download_{current['task_id']}",
                        use_container_width=True,
                    )


def _render_library_replacement(loader, state: dict) -> None:
    """Offer a separately confirmed, reversible same-name library replacement."""
    school_path = Path(state["school_pdf_path"])
    candidates = [
        (doc_id, doc)
        for doc_id, doc in loader.documents.items()
        if doc.file_name.casefold() == state["school_file_name"].casefold()
    ]
    if not candidates:
        st.info("资料库没有同名课件；本次比较不会自动新增资料库文档。")
        return

    st.divider()
    st.markdown("##### 🔁 可选：替换资料库中的同名课件")
    st.warning(
        "替换会影响后续检索。旧 PDF 会保留为可恢复备份；"
        "系统将先构建候选索引，再原子替换文件和索引，并清除 embedding 缓存。"
    )
    labels = {
        doc_id: f"{doc.file_name} · {doc.file_path}"
        for doc_id, doc in candidates
    }
    selected_id = st.selectbox(
        "选择要替换的资料库版本",
        options=[doc_id for doc_id, _ in candidates],
        format_func=lambda doc_id: labels[doc_id],
        key=f"course_update_library_target_{state['task_id']}",
    )
    selected_doc = loader.documents[selected_id]
    current_path = Path(selected_doc.file_path)
    current_hash = _sha256_file(current_path)
    new_hash = _sha256_file(school_path)
    st.caption(f"资料库 SHA-256：`{current_hash}`")
    st.caption(f"新课件 SHA-256：`{new_hash}`")
    if current_hash == new_hash:
        st.success("资料库中的同名课件与本次上传内容一致，无需替换。")
        return

    confirmed = st.checkbox(
        f"我确认以本次上传的「{state['school_file_name']}」替换所选资料，并保留旧版本备份。",
        key=f"course_update_library_confirm_{state['task_id']}_{selected_id}",
    )
    if st.button(
        "确认替换课程资料库",
        type="primary",
        disabled=not confirmed,
        key=f"course_update_library_replace_{state['task_id']}_{selected_id}",
    ):
        try:
            result = replace_library_document(
                loader,
                state["course_id"],
                selected_id,
                school_path,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "Course-library replacement failed for task %s",
                state.get("task_id"),
            )
            st.error(f"资料库替换失败：{exc}")
            st.caption("请检查错误详情；若回滚也失败，备份目录会保留用于恢复。")
            return
        refresh_knowledge_base(str(result["message"]))


def page_course_update(loader) -> None:
    """Compare new school materials with a prior tutoring handout."""
    st.subheader("🆕 新旧课件比对与更新")
    st.caption(
        "分析最新学校课件与往期补习课件的知识点覆盖情况；"
        "审核后可生成一个独立的 DOCX 修订副本。"
    )
    st.info(
        "比对和 DOCX 修订不会自动修改资料库。比对完成后，可单独确认替换同名课件；"
        "替换会保留可回滚备份。DOCX→PDF 为可选本地转换。"
    )
    st.warning(
        "隐私提示：文件会先暂存在本机；知识点抽取、比对和修订内容生成会将"
        "相关文本发送到当前配置的 DeepSeek API。请勿上传不适合发送给第三方服务的资料。"
    )
    llm_available = LLMClient().available
    if not llm_available:
        st.error("未配置 DEEPSEEK_API_KEY，当前无法运行课件比对和修订生成。")

    school_upload = st.file_uploader(
        "最新学校课件（PDF）",
        type=["pdf"],
        max_upload_size=50,
        key="course_update_school_upload",
    )
    tutoring_upload = st.file_uploader(
        "往期补习课件（DOCX 或 PDF）",
        type=["docx", "pdf"],
        max_upload_size=50,
        key="course_update_tutoring_upload",
    )
    if school_upload is not None:
        collisions = [
            doc.file_name
            for doc in loader.documents.values()
            if doc.file_name.casefold() == Path(school_upload.name).name.casefold()
        ]
        if collisions:
            st.warning(
                f"资料库中已有同名文件：{', '.join(collisions)}。"
                "比对不会自动覆盖；报告完成后可另行确认替换并保留旧版本备份。"
            )
    consent = st.checkbox(
        "我已阅读隐私提示，并确认允许将本次课件文本发送到配置的 DeepSeek API。",
        key="course_update_privacy_consent",
    )
    if st.button(
        "开始比对",
        type="primary",
        disabled=not (
            llm_available and school_upload and tutoring_upload and consent
        ),
        key="course_update_start",
    ):
        task_id = uuid.uuid4().hex
        school_bytes = school_upload.getvalue()
        tutoring_bytes = tutoring_upload.getvalue()
        max_upload_bytes = 50 * 1024 * 1024
        if len(school_bytes) > max_upload_bytes or len(tutoring_bytes) > max_upload_bytes:
            st.error("单个课件大小不能超过 50 MB。")
            return
        tutoring_suffix = Path(tutoring_upload.name).suffix.lower()
        if tutoring_suffix not in {".docx", ".pdf"}:
            st.error("往期补习课件仅支持 DOCX 或 PDF。")
            return
        task_dir = Config.DATA_DIR / "course_updates" / task_id
        staging_dir = task_dir / "staging"
        staging_dir.mkdir(parents=True, exist_ok=False)
        school_path = staging_dir / "school.pdf"
        tutoring_path = staging_dir / f"tutoring{tutoring_suffix}"
        school_path.write_bytes(school_bytes)
        tutoring_path.write_bytes(tutoring_bytes)
        initial_state = {
            "task_id": task_id,
            "course_id": st.session_state.course,
            "school_pdf_path": str(school_path),
            "school_file_name": Path(school_upload.name).name,
            "tutoring_file_path": str(tutoring_path),
            "tutoring_file_name": Path(tutoring_upload.name).name,
            "selected_recommendation_ids": [],
            "status": "started",
        }
        st.session_state.course_update_state = None
        try:
            with st.spinner(
                "正在解析课件、抽取知识点并检索补习课件证据…"
            ):
                result = build_course_update_graph(LLMClient()).invoke(initial_state)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Course comparison failed for task %s", task_id)
            st.error(f"比对失败：{exc}")
            st.caption("原始课件和课程资料库未被修改。请检查文件是否可解析后重试。")
            return

        st.session_state.course_update_state = result
        st.success("比对报告已完成；接下来请逐项审核证据与建议。")

    state = st.session_state.get("course_update_state")
    if state:
        _render_course_update_report(state)
        report_school_path = Path(state["school_pdf_path"])
        if (
            school_upload is not None
            and report_school_path.is_file()
            and _sha256_file(report_school_path)
            == state.get("school_sha256")
            and hashlib.sha256(school_upload.getvalue()).hexdigest()
            == state.get("school_sha256")
        ):
            _render_library_replacement(loader, state)
        else:
            st.caption(
                "资料库替换仅对当前报告对应的学校课件开放；"
                "请重新选择生成此报告时使用的同一文件。"
            )


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
    elif page == "🆕 新旧课件比对":
        page_course_update(loader)
    else:
        monitor = UsageMonitor(persist_path=None)  # UI 内不持久化，仅展示
        pipeline = get_pipeline(loader, retriever, monitor)
        page_tasks(pipeline, loader)


if __name__ == "__main__":
    main()
