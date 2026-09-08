"""
RAG generation pipeline (Phase 2 + Phase 3).

Orchestrates: retrieve -> prompt -> LLM generate -> parse structured output ->
validate & resolve citations -> export.

Phase 2 implements the weekly lesson (备课包) task; Phase 3 adds problem
solving (讲题), plus a unified dispatch generate_task().
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.config import Config
from src.core.models import (
    Chunk,
    Citation,
    Example,
    Exercise,
    GeneratedLesson,
    GeneratedProblemSolution,
    KnowledgePoint,
    LayeredHint,
    ProblemStep,
    RubricCriterion,
    TeachingTask,
    TermDefinition,
)
from src.prompts.teaching_templates import (
    build_lesson_messages,
    build_problem_solution_messages,
    format_context,
)
from src.rag.citation_validator import CitationValidator
from src.rag.llm_client import LLMClient, parse_json_response
from src.eval.monitor import UsageMonitor

logger = logging.getLogger(__name__)


def _clean_text(value: Any) -> str:
    """Coerce a raw model value to a trimmed string."""
    if value is None:
        return ""
    return str(value).strip()


def _list_of_strings(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [_clean_text(v) for v in value if _clean_text(v)]


def _list_of_dicts(value: Any) -> List[dict]:
    if not isinstance(value, list):
        return []
    return [v for v in value if isinstance(v, dict)]


def _parse_citations(raw_list: Any) -> List[Citation]:
    """Parse a list of {document_id, page, chunk_id} dicts into Citation objects."""
    citations = []
    for item in _list_of_dicts(raw_list):
        doc_id = _clean_text(item.get("document_id"))
        if not doc_id:
            continue
        try:
            page = int(item.get("page", 0))
        except (TypeError, ValueError):
            page = 0
        chunk_id = _clean_text(item.get("chunk_id")) or None
        citations.append(Citation(document_id=doc_id, page=page, chunk_id=chunk_id))
    return citations


class RAGPipeline:
    """
    End-to-end generation pipeline for teaching tasks.

    Args:
        retriever: Retriever instance exposing .search() and .chunks.
        documents: document_id -> Document mapping (for display/citation).
        llm_client: LLMClient-like object exposing .generate(messages, json_mode).
    """

    def __init__(
        self,
        retriever,
        documents: dict,
        llm_client: Optional[LLMClient] = None,
        monitor: Optional["UsageMonitor"] = None,
    ):
        self.retriever = retriever
        self.documents = documents
        self.llm_client = llm_client or LLMClient()
        # Cost/latency monitor (Phase 4). Optional; records every generation.
        self.monitor = monitor
        chunks: List[Chunk] = getattr(retriever, "chunks", [])
        self.validator = CitationValidator(chunks, documents)

    # ------------------------------------------------------------------
    # Generation helper (wraps LLM call with usage monitoring)
    # ------------------------------------------------------------------

    def _generate(self, messages: List[dict], task_name: str) -> str:
        """Call the LLM, timing the call and recording usage when a monitor is set."""
        import time

        start = time.perf_counter()
        raw = self.llm_client.generate(messages, json_mode=True)
        latency = time.perf_counter() - start

        if self.monitor is not None:
            prompt_text = "\n".join(
                str(m.get("content", "")) for m in messages if m.get("role") == "user"
            )
            self.monitor.record(
                task=task_name,
                model=getattr(self.llm_client, "model", "unknown"),
                mode="real",
                latency_s=latency,
                prompt_text=prompt_text,
                completion_text=raw,
            )
        return raw

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------

    def _retrieve(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
    ) -> List[Chunk]:
        """Run retrieval and return the top chunks (or empty list)."""
        try:
            results = self.retriever.search(
                query,
                top_k=top_k,
                document_ids=document_ids,
            )
        except TypeError:
            # Some retrievers don't accept document_ids; fall back gracefully.
            results = self.retriever.search(query, top_k=top_k)
        return [r.chunk for r in results]

    def _build_context(
        self,
        chunks: List[Chunk],
        max_chars: Optional[int] = None,
    ) -> str:
        if not chunks:
            return "（没有检索到相关课程资料。如果无法回答，请明确说明资料不足，不要编造内容。）"
        limit = max_chars or getattr(Config.retriever, "max_context_chars", 3000)
        return format_context(chunks, self.documents, max_chars=limit)

    def _chunks_in_order(self, document_ids: Optional[List[str]] = None) -> List[Chunk]:
        """Return the chunks of the given documents in reading order.

        备课不再依赖关键词检索，而是把所选（或全部）资料的片段按
        文档 + 页内顺序整体取回，确保模型能覆盖资料的全部知识点。
        """
        wanted = set(document_ids) if document_ids is not None else None
        chunks = [
            c
            for c in getattr(self.retriever, "chunks", [])
            if wanted is None or c.document_id in wanted
        ]
        # 文档按首次出现顺序、片段按文档内顺序排列。
        order: Dict[str, int] = {}
        for c in chunks:
            order.setdefault(c.document_id, len(order))
        chunks.sort(key=lambda c: (order.get(c.document_id, 0), c.order_in_doc, c.page_number))
        return chunks

    def _build_lesson_context(self, chunks: List[Chunk], max_chars: int = 45000) -> str:
        """Render the selected chunks (reading order) as the lesson context.

        单节课件（约 11–20K 字符）可完整装入，避免“只见开头、不见结尾”；
        当所选资料整体超过预算时，保留开头约 60% + 结尾约 40%，
        让模型仍能看到课程的后半部分（如深入主题与练习），而不是只截掉尾巴。
        """
        if not chunks:
            return "（所选资料为空：没有可用于备课的课程内容。）"

        blocks = []
        for chunk in chunks:
            doc = self.documents.get(chunk.document_id)
            name = doc.file_name if doc else chunk.document_id
            header = (
                f"[{name} | page {chunk.page_number} | "
                f"doc_id={chunk.document_id} | chunk_id={chunk.chunk_id}]"
            )
            blocks.append(f"{header}\n{chunk.text}")

        def join(bs: List[str]) -> str:
            return "\n\n".join(bs)

        if len(join(blocks)) <= max_chars:
            return join(blocks)

        head_budget = int(max_chars * 0.6)
        tail_budget = max_chars - head_budget

        head: List[str] = []
        used = 0
        for b in blocks:
            cost = len(b) + (2 if head else 0)
            if used + cost > head_budget:
                break
            head.append(b)
            used += cost

        tail: List[str] = []
        used = 0
        for b in reversed(blocks):
            cost = len(b) + (2 if tail else 0)
            if used + cost > tail_budget:
                break
            tail.append(b)
            used += cost
        tail.reverse()

        marker = (
            "\n\n……（所选资料较长，中间部分已省略，仅保留开头与结尾。"
            "若生成的备课内容仍不完整，请缩小资料范围后重新生成）\n\n"
        )
        return join(head) + marker + join(tail)

    # ------------------------------------------------------------------
    # Citation handling
    # ------------------------------------------------------------------

    def _validate_citations(self, citations: List[Citation]) -> tuple:
        """
        Validate citations against the corpus.

        Returns:
            (valid_citations, review_notes)
        """
        if not citations:
            return [], []

        validation = self.validator.validate(citations)
        review_notes: List[str] = []
        valid: List[Citation] = []

        missing = set(validation.missing_documents)
        out_of_range = set(validation.out_of_range_pages)
        invalid_chunks = set(validation.invalid_chunks)

        for citation in citations:
            if citation.document_id in missing:
                if citation.document_id not in [n for n in review_notes if citation.document_id in n]:
                    review_notes.append(f"引用不存在的文档：{citation.document_id}")
                continue
            if citation.chunk_id and citation.chunk_id in invalid_chunks:
                review_notes.append(
                    f"引用片段不存在：{citation.document_id} 的 chunk_id={citation.chunk_id}"
                )
                continue
            if (citation.document_id, citation.page) in out_of_range:
                review_notes.append(
                    f"引用页码超出范围：{citation.document_id} 第 {citation.page} 页"
                )
                continue
            valid.append(citation)

        # Resolve chunk_id / snippet for display and export.
        return self.validator.resolve_citations(valid), review_notes

    # ------------------------------------------------------------------
    # Phase 2: lesson generation
    # ------------------------------------------------------------------

    def generate_lesson(
        self,
        topic: str = "",
        student_level: str = "初学者",
        duration: str = "1 小时",
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        cover_all: bool = True,
        scope_names: Optional[List[str]] = None,
        cover_max_chars: int = 45000,
        extra: str = "",
    ) -> GeneratedLesson:
        """Generate a teaching handout / lesson package (备课包 / 期末复习).

        依据所选资料的**完整内容**备课：不再依赖「本周主题」关键词检索，
        而是把选中（或全部）资料的 chunks 按阅读顺序整体放入上下文，
        让模型覆盖资料中的全部知识点、给出详实讲义并生成约 3 道习题。
        当选中全部课程资料时，该材料即相当于整学期期末复习材料。
        """
        if cover_all:
            chunks = self._chunks_in_order(document_ids)
            context = self._build_lesson_context(chunks, max_chars=cover_max_chars)
        else:
            chunks = self._retrieve(topic, top_k=top_k, document_ids=document_ids)
            context = self._build_context(chunks)
        messages = build_lesson_messages(
            topic=topic,
            context=context,
            student_level=student_level,
            duration=duration,
            scope_names=scope_names,
            extra=extra,
        )
        raw = self._generate(messages, "lesson")
        data = parse_json_response(raw)

        citations = _parse_citations(data.get("citations"))
        valid_citations, review_notes = self._validate_citations(citations)

        needs_review = _list_of_strings(data.get("needs_review"))
        needs_review.extend(review_notes)

        lesson = GeneratedLesson(
            topic=_clean_text(data.get("topic")) or topic,
            learning_objectives=_list_of_strings(data.get("learning_objectives")),
            prerequisites=_list_of_strings(data.get("prerequisites")),
            core_explanation=_clean_text(data.get("core_explanation")),
            terminology=[
                TermDefinition(
                    term=_clean_text(t.get("term")),
                    explanation=_clean_text(t.get("explanation")),
                )
                for t in _list_of_dicts(data.get("terminology"))
            ],
            examples=[
                Example(
                    title=_clean_text(e.get("title")),
                    content=_clean_text(e.get("content")),
                )
                for e in _list_of_dicts(data.get("examples"))
            ],
            misconceptions=_list_of_strings(data.get("misconceptions")),
            discussion_questions=_list_of_strings(data.get("discussion_questions")),
            exercises=[
                Exercise(
                    question=_clean_text(e.get("question")),
                    hint=_clean_text(e.get("hint")),
                    reference_answer=_clean_text(e.get("reference_answer")),
                )
                for e in _list_of_dicts(data.get("exercises"))
            ],
            citations=valid_citations,
            needs_review=needs_review,
            insufficient_material=bool(not chunks),
            raw_output=raw,
        )
        return lesson

    # ------------------------------------------------------------------
    # Phase 3: problem solving (讲题)
    # ------------------------------------------------------------------

    def generate_problem_solution(
        self,
        problem_text: str,
        goal: str = "讲解解题思路，不代写答案",
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        extra: str = "",
    ) -> GeneratedProblemSolution:
        """Generate a tutoring-mode problem explanation (作业/真题讲题)."""
        query = problem_text[:300]
        chunks = self._retrieve(query, top_k=top_k, document_ids=document_ids)
        context = self._build_context(chunks)
        messages = build_problem_solution_messages(
            problem_text=problem_text,
            context=context,
            goal=goal,
            extra=extra,
        )
        raw = self._generate(messages, "problem_solving")
        data = parse_json_response(raw)

        citations = _parse_citations(data.get("citations"))
        valid_citations, review_notes = self._validate_citations(citations)

        needs_review = _list_of_strings(data.get("needs_review"))
        needs_review.extend(review_notes)

        # Normalize layered hints to integers and sort by level.
        layered_hints = []
        for h in _list_of_dicts(data.get("layered_hints")):
            try:
                level = int(h.get("level", 1))
            except (TypeError, ValueError):
                level = 1
            hint_text = _clean_text(h.get("hint"))
            if hint_text:
                layered_hints.append(LayeredHint(level=level, hint=hint_text))
        layered_hints.sort(key=lambda h: h.level)

        result = GeneratedProblemSolution(
            problem_summary=_clean_text(data.get("problem_summary")) or problem_text[:80],
            knowledge_points=[
                KnowledgePoint(
                    name=_clean_text(k.get("name")),
                    explanation=_clean_text(k.get("explanation")),
                )
                for k in _list_of_dicts(data.get("knowledge_points"))
            ],
            prerequisites=_list_of_strings(data.get("prerequisites")),
            steps=[
                ProblemStep(
                    description=_clean_text(s.get("description")),
                    hint=_clean_text(s.get("hint")),
                    answer_progress=_clean_text(s.get("answer_progress")),
                )
                for s in _list_of_dicts(data.get("steps"))
            ],
            layered_hints=layered_hints,
            common_errors=_list_of_strings(data.get("common_errors")),
            rubric_mapping=[
                RubricCriterion(
                    criterion=_clean_text(r.get("criterion")),
                    how_to_earn=_clean_text(r.get("how_to_earn")),
                )
                for r in _list_of_dicts(data.get("rubric_mapping"))
            ],
            reference_direction=_clean_text(data.get("reference_direction")),
            citations=valid_citations,
            needs_review=needs_review,
            insufficient_material=bool(not chunks),
            raw_output=raw,
        )
        return result

    # ------------------------------------------------------------------
    # Generic dispatch
    # ------------------------------------------------------------------

    def generate_task(
        self,
        task: TeachingTask,
        inputs: Dict[str, Any],
        **kwargs,
    ) -> Any:
        """
        Unified entry point for a teaching task.

        Args:
            task: TeachingTask (or its string value).
            inputs: Task-specific inputs dict, e.g.
                lesson:          {"student_level", "duration", "extra", ...}
                problem_solving: {"problem_text", "goal", "extra", ...}

        Returns:
            The structured result dataclass for the task.
        """
        if isinstance(task, str):
            task = TeachingTask(task)

        if task == TeachingTask.LESSON:
            return self.generate_lesson(
                topic=inputs.get("topic", ""),
                student_level=inputs.get("student_level", "初学者"),
                duration=inputs.get("duration", "1 小时"),
                top_k=kwargs.get("top_k", 5),
                document_ids=kwargs.get("document_ids"),
                cover_all=kwargs.get("cover_all", True),
                scope_names=kwargs.get("scope_names"),
                cover_max_chars=kwargs.get("cover_max_chars", 45000),
                extra=inputs.get("extra", ""),
            )
        if task == TeachingTask.PROBLEM_SOLVING:
            return self.generate_problem_solution(
                problem_text=inputs.get("problem_text", ""),
                goal=inputs.get("goal", "讲解解题思路，不代写答案"),
                top_k=kwargs.get("top_k", 5),
                document_ids=kwargs.get("document_ids"),
                extra=inputs.get("extra", ""),
            )
        raise ValueError(f"Unsupported task: {task}")

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    # ---- lesson ----

    def export_markdown(self, lesson: GeneratedLesson) -> str:
        """Render a GeneratedLesson as Markdown."""
        lines = [f"# 本周备课包：{lesson.topic or '（未命名）'}", ""]

        if lesson.insufficient_material:
            lines.append("> ⚠️ 资料不足：检索结果较少，请老师核对补充。")
            lines.append("")

        def section(title, items):
            out = [f"## {title}", ""]
            if items:
                for i, item in enumerate(items, 1):
                    out.append(f"{i}. {item}")
            else:
                out.append("_（暂无内容）_")
            return out

        lines += section("学习目标", lesson.learning_objectives)
        lines += section("前置知识", lesson.prerequisites)

        if lesson.core_explanation:
            lines += ["## 课程精讲（讲义正文）", "", lesson.core_explanation, ""]

        if lesson.terminology:
            lines += ["## 英文专业术语", "", "| 术语 | 解释 |", "|------|------|"]
            for t in lesson.terminology:
                lines.append(f"| {t.term} | {t.explanation} |")
            lines.append("")

        if lesson.examples:
            lines.append("## 简单例子")
            lines.append("")
            for e in lesson.examples:
                title = e.title if getattr(e, "title", "") else "例子"
                lines.append(f"### {title}")
                lines.append("")
                lines.append(e.content)
                lines.append("")

        lines += section("常见误区", lesson.misconceptions)
        lines += section("课堂互动问题", lesson.discussion_questions)

        if lesson.exercises:
            lines.append("## 课后习题")
            lines.append("")
            for i, ex in enumerate(lesson.exercises, 1):
                lines.append(f"### 练习 {i}")
                lines.append("")
                lines.append(f"**题目**：{ex.question}")
                if ex.hint:
                    lines.append(f"**提示**：{ex.hint}")
                if ex.reference_answer:
                    lines.append(f"**参考答案**：{ex.reference_answer}")
                lines.append("")

        lines += self._format_citations(lesson.citations)
        lines += self._format_needs_review(lesson.needs_review)
        return "\n".join(lines).strip() + "\n"

    def export_json(self, lesson: GeneratedLesson) -> str:
        """Render a GeneratedLesson as an indented JSON string."""
        return json.dumps(lesson.to_dict(), ensure_ascii=False, indent=2)

    def save_lesson(
        self,
        lesson: GeneratedLesson,
        output_format: str = "markdown",
        subdir: str = "lesson_plans",
    ) -> Path:
        """Save a lesson to data/output/<subdir> and return the path."""
        name = self._safe_name(lesson.topic) or "lesson"
        if output_format == "json":
            content = self.export_json(lesson)
            suffix = ".json"
        else:
            content = self.export_markdown(lesson)
            suffix = ".md"
        return self._save(subdir, f"{name}_lesson{suffix}", content)

    # ---- generic save ----

    def save_result(
        self,
        result: Any,
        subdir: str,
        filename: str,
        output_format: str = "markdown",
    ) -> Path:
        """Save any structured result (md or json) and return the path."""
        if output_format == "json":
            content = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
            suffix = ".json"
        else:
            content = self._render_markdown(result)
            suffix = ".md"
        return self._save(subdir, f"{filename}{suffix}", content)

    # ---- Phase 4: HTML export ----

    def render_markdown_html(self, markdown_text: str, title: str = "") -> str:
        """Render Markdown to a self-contained, print-friendly HTML document.

        Uses the `markdown` library with the `tables` extension. Falls back to
        an escaped <pre> block if the library is unavailable.
        """
        body = markdown_text
        try:
            import markdown as md

            body = md.markdown(markdown_text, extensions=["tables", "fenced_code"])
        except ImportError:  # pragma: no cover - graceful degradation
            import html

            body = f"<pre>{html.escape(markdown_text)}</pre>"

        heading = f"<h1>{title}</h1>" if title else ""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{title or 'AI 教学助手'}</title>
<style>
  body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
         max-width: 820px; margin: 24px auto; padding: 0 20px; color: #1f2328; line-height: 1.7; }}
  h1, h2, h3 {{ color: #0b3b5c; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
  th, td {{ border: 1px solid #d0d7de; padding: 6px 10px; font-size: 14px; }}
  th {{ background: #f6f8fa; }}
  blockquote {{ border-left: 4px solid #d4a72c; background: #fff8e1; margin: 8px 0;
               padding: 6px 12px; }}
  pre, code {{ background: #f6f8fa; border-radius: 4px; }}
  pre {{ padding: 10px; overflow-x: auto; }}
  @media print {{ body {{ margin: 0; }} }}
</style>
</head>
<body>
{heading}
{body}
<hr>
<p style="color:#888;font-size:12px">由 AI 教学助手生成（草稿，需老师审核）</p>
</body>
</html>
"""

    def export_html(self, result: Any) -> str:
        """Render any structured result as a standalone HTML document."""
        markdown_text = self.export_markdown(result) if isinstance(result, GeneratedLesson) else self._render_markdown(result)
        title = self._safe_name(getattr(result, "topic", "") or getattr(result, "title", "") or getattr(result, "scope", "") or "teaching_material")
        return self.render_markdown_html(markdown_text, title=title)

    def save_html(self, result: Any, subdir: str, filename: str) -> Path:
        """Save any structured result as HTML and return the path."""
        return self._save(subdir, f"{filename}.html", self.export_html(result))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _render_markdown(self, result: Any) -> str:
        """Render a problem-solving result as Markdown."""
        if getattr(result, "task_type", None) == TeachingTask.PROBLEM_SOLVING:
            return self._export_problem_solution_markdown(result)
        return str(result)

    def _export_problem_solution_markdown(self, r: GeneratedProblemSolution) -> str:
        lines = [f"# 作业/真题讲题：{r.problem_summary or '（未命名）'}", ""]
        if r.insufficient_material:
            lines.append("> ⚠️ 资料不足，请老师核对补充。")
            lines.append("")

        lines += ["## 题目概括", "", r.problem_summary or "（未提供）", ""]

        if r.knowledge_points:
            lines += ["## 考查的知识点", ""]
            for k in r.knowledge_points:
                lines.append(f"- **{k.name}** — {k.explanation}")
            lines.append("")

        lines += self._numbered("前置知识", r.prerequisites)

        if r.steps:
            lines.append("## 分步解题思路")
            lines.append("")
            for i, step in enumerate(r.steps, 1):
                lines.append(f"### 第 {i} 步：{step.description}")
                lines.append("")
                if step.hint:
                    lines.append(f"**提示**：{step.hint}")
                if step.answer_progress:
                    lines.append(f"**这一步的中间结果**：{step.answer_progress}")
                lines.append("")

        if r.layered_hints:
            lines.append("## 分层提示")
            lines.append("")
            for h in r.layered_hints:
                lines.append(f"- **Level {h.level}**：{h.hint}")
            lines.append("")

        lines += self._numbered("常见错误", r.common_errors)

        if r.rubric_mapping:
            lines += ["## 与评分标准的对应", "", "| 评分标准 | 如何满足 |", "|----------|----------|"]
            for m in r.rubric_mapping:
                lines.append(f"| {m.criterion} | {m.how_to_earn} |")
            lines.append("")

        if r.reference_direction:
            lines += ["## 参考解题方向（不代写）", "", r.reference_direction, ""]

        lines += self._format_citations(r.citations)
        lines += self._format_needs_review(r.needs_review)
        return "\n".join(lines).strip() + "\n"

    def _format_citations(self, citations: List[Citation]) -> List[str]:
        if not citations:
            return []
        lines = ["## 来源引用", ""]
        for c in citations:
            doc = self.documents.get(c.document_id)
            name = doc.file_name if doc else c.document_id
            lines.append(f"- {name}（第 {c.page} 页）")
        lines.append("")
        return lines

    def _format_needs_review(self, needs_review: List[str]) -> List[str]:
        if not needs_review:
            return []
        lines = ["## 需要老师确认", ""]
        for note in needs_review:
            lines.append(f"- ⚠️ {note}")
        lines.append("")
        return lines

    @staticmethod
    def _numbered(title: str, items: List[str]) -> List[str]:
        out = [f"## {title}", ""]
        if items:
            for i, item in enumerate(items, 1):
                out.append(f"{i}. {item}")
        else:
            out.append("_（暂无内容）_")
        out.append("")
        return out

    @staticmethod
    def _safe_name(text: str) -> str:
        """Turn a topic string into a safe file name."""
        name = re.sub(r"[^\w\u4e00-\u9fff]+", "_", text)
        return name.strip("_")[:60]

    def _save(self, subdir: str, filename: str, content: str) -> Path:
        path = Config.get_output_path(filename, subdir=subdir)
        path.write_text(content, encoding="utf-8")
        logger.info(f"Saved output to {path}")
        return path
