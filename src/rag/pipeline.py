"""
RAG generation pipeline (Phase 2 + Phase 3).

Orchestrates: retrieve -> prompt -> LLM generate -> parse structured output ->
validate & resolve citations -> export.

Phase 2 implements the weekly lesson (备课包) task; Phase 3 adds problem
solving (讲题), final review (期末复习), cheat sheet (速查表) and exam-topic
knowledge mapping (真题知识点映射), plus a unified dispatch generate_task().
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
    ChapterConcepts,
    CheatsheetItem,
    CheatsheetSection,
    ConfusionPoint,
    ExamKnowledgeMapping,
    ExamMappingEntry,
    Example,
    Exercise,
    GeneratedCheatsheet,
    GeneratedLesson,
    GeneratedProblemSolution,
    GeneratedReview,
    KnowledgePoint,
    LayeredHint,
    MappedKnowledgePoint,
    ProblemStep,
    ReviewKnowledgeNode,
    RubricCriterion,
    SelfTestQuestion,
    TeachingTask,
    TermDefinition,
)
from src.prompts.teaching_templates import (
    build_cheatsheet_messages,
    build_exam_mapping_messages,
    build_lesson_messages,
    build_problem_solution_messages,
    build_review_messages,
    format_context,
    get_template,
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
    """Parse a list of {document_id, page} dicts into Citation objects."""
    citations = []
    for item in _list_of_dicts(raw_list):
        doc_id = _clean_text(item.get("document_id"))
        if not doc_id:
            continue
        try:
            page = int(item.get("page", 0))
        except (TypeError, ValueError):
            page = 0
        citations.append(Citation(document_id=doc_id, page=page))
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
                mode="real" if getattr(self.llm_client, "available", False) else "mock",
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

        for citation in citations:
            if citation.document_id in missing:
                if citation.document_id not in [n for n in review_notes if citation.document_id in n]:
                    review_notes.append(f"引用不存在的文档：{citation.document_id}")
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
        topic: str,
        student_level: str = "初学者",
        duration: str = "1 小时",
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
    ) -> GeneratedLesson:
        """Generate a weekly lesson package (本周备课包)."""
        chunks = self._retrieve(topic, top_k=top_k, document_ids=document_ids)
        context = self._build_context(chunks)
        messages = build_lesson_messages(
            topic=topic,
            context=context,
            student_level=student_level,
            duration=duration,
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
    ) -> GeneratedProblemSolution:
        """Generate a tutoring-mode problem explanation (作业/真题讲题)."""
        query = problem_text[:300]
        chunks = self._retrieve(query, top_k=top_k, document_ids=document_ids)
        context = self._build_context(chunks)
        messages = build_problem_solution_messages(
            problem_text=problem_text,
            context=context,
            goal=goal,
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
    # Phase 3: final review (期末复习)
    # ------------------------------------------------------------------

    def generate_review(
        self,
        scope: str,
        student_level: str = "初学者",
        top_k: int = 8,
        document_ids: Optional[List[str]] = None,
    ) -> GeneratedReview:
        """Generate a final-review package (期末复习包)."""
        chunks = self._retrieve(scope, top_k=top_k, document_ids=document_ids)
        context = self._build_context(chunks, max_chars=5000)
        messages = build_review_messages(
            scope=scope,
            context=context,
            student_level=student_level,
        )
        raw = self._generate(messages, "review")
        data = parse_json_response(raw)

        citations = _parse_citations(data.get("citations"))
        valid_citations, review_notes = self._validate_citations(citations)

        needs_review = _list_of_strings(data.get("needs_review"))
        needs_review.extend(review_notes)

        result = GeneratedReview(
            scope=_clean_text(data.get("scope")) or scope,
            knowledge_map=[
                ReviewKnowledgeNode(
                    name=_clean_text(n.get("name")),
                    chapter=_clean_text(n.get("chapter")),
                    core_idea=_clean_text(n.get("core_idea")),
                    prerequisite_of=_list_of_strings(n.get("prerequisite_of")),
                    depends_on=_list_of_strings(n.get("depends_on")),
                )
                for n in _list_of_dicts(data.get("knowledge_map"))
            ],
            core_concepts=[
                ChapterConcepts(
                    chapter=_clean_text(c.get("chapter")),
                    concepts=_list_of_strings(c.get("concepts")),
                )
                for c in _list_of_dicts(data.get("core_concepts"))
            ],
            confusion_points=[
                ConfusionPoint(
                    a=_clean_text(c.get("a")),
                    b=_clean_text(c.get("b")),
                    difference=_clean_text(c.get("difference")),
                )
                for c in _list_of_dicts(data.get("confusion_points"))
            ],
            self_test_questions=[
                SelfTestQuestion(
                    question=_clean_text(q.get("question")),
                    hint=_clean_text(q.get("hint")),
                    reference_answer=_clean_text(q.get("reference_answer")),
                )
                for q in _list_of_dicts(data.get("self_test_questions"))
            ],
            exam_mapping=[
                ExamMappingEntry(
                    exam_topic=_clean_text(e.get("exam_topic")),
                    knowledge_points=_list_of_strings(e.get("knowledge_points")),
                )
                for e in _list_of_dicts(data.get("exam_mapping"))
            ],
            priority_advice=_list_of_strings(data.get("priority_advice")),
            citations=valid_citations,
            needs_review=needs_review,
            insufficient_material=bool(not chunks),
            raw_output=raw,
        )
        return result

    # ------------------------------------------------------------------
    # Phase 3: cheat sheet (速查表)
    # ------------------------------------------------------------------

    def generate_cheatsheet(
        self,
        scope: str,
        page_limit: str = "两页",
        allowed: str = "允许携带课程讲义与公式表",
        top_k: int = 10,
        document_ids: Optional[List[str]] = None,
    ) -> GeneratedCheatsheet:
        """Generate a two-page cheat sheet draft (速查表草稿)."""
        chunks = self._retrieve(scope, top_k=top_k, document_ids=document_ids)
        context = self._build_context(chunks, max_chars=6000)
        messages = build_cheatsheet_messages(
            scope=scope,
            context=context,
            page_limit=page_limit,
            allowed=allowed,
        )
        raw = self._generate(messages, "cheatsheet")
        data = parse_json_response(raw)

        citations = _parse_citations(data.get("citations"))
        valid_citations, review_notes = self._validate_citations(citations)

        needs_review = _list_of_strings(data.get("needs_review"))
        needs_review.extend(review_notes)

        sections = []
        for sec in _list_of_dicts(data.get("sections")):
            items = []
            for it in _list_of_dicts(sec.get("items")):
                source = None
                src = it.get("source")
                if isinstance(src, dict):
                    src_doc = _clean_text(src.get("document_id"))
                    if src_doc:
                        try:
                            src_page = int(src.get("page", 0))
                        except (TypeError, ValueError):
                            src_page = 0
                        source = Citation(document_id=src_doc, page=src_page)
                items.append(
                    CheatsheetItem(
                        item_type=_clean_text(it.get("type")) or "definition",
                        label=_clean_text(it.get("label")),
                        content=_clean_text(it.get("content")),
                        source=source,
                    )
                )
            if items:
                sections.append(CheatsheetSection(
                    heading=_clean_text(sec.get("heading")),
                    items=items,
                ))

        within = data.get("within_page_limit")
        result = GeneratedCheatsheet(
            title=_clean_text(data.get("title")) or scope,
            scope=_clean_text(data.get("scope")) or scope,
            sections=sections,
            layout_notes=_list_of_strings(data.get("layout_notes")),
            compression_advice=_list_of_strings(data.get("compression_advice")),
            within_page_limit=bool(within) if isinstance(within, bool) else True,
            citations=valid_citations,
            needs_review=needs_review,
            insufficient_material=bool(not chunks),
            raw_output=raw,
        )
        return result

    # ------------------------------------------------------------------
    # Phase 3: exam-topic knowledge mapping (真题知识点映射)
    # ------------------------------------------------------------------

    def generate_exam_mapping(
        self,
        exam_topic: str,
        top_k: int = 6,
        document_ids: Optional[List[str]] = None,
    ) -> ExamKnowledgeMapping:
        """Map an exam topic/question to course knowledge points."""
        chunks = self._retrieve(exam_topic, top_k=top_k, document_ids=document_ids)
        context = self._build_context(chunks)
        messages = build_exam_mapping_messages(
            exam_topic=exam_topic,
            context=context,
        )
        raw = self._generate(messages, "exam_mapping")
        data = parse_json_response(raw)

        knowledge_points = []
        for k in _list_of_dicts(data.get("knowledge_points")):
            evidence = _parse_citations(k.get("evidence_chunks") or k.get("evidence"))
            evidence, _ = self._validate_citations(evidence)
            knowledge_points.append(
                MappedKnowledgePoint(
                    name=_clean_text(k.get("name")),
                    chapter=_clean_text(k.get("chapter")),
                    relevance=_clean_text(k.get("relevance")),
                    evidence=evidence,
                )
            )

        needs_review = _list_of_strings(data.get("needs_review"))
        coverage_gap = _clean_text(data.get("coverage_gap"))
        if coverage_gap:
            needs_review.append(f"资料未覆盖的考点：{coverage_gap}")

        result = ExamKnowledgeMapping(
            exam_topic=_clean_text(data.get("exam_topic")) or exam_topic,
            knowledge_points=knowledge_points,
            coverage_gap=coverage_gap,
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
        Unified entry point for any teaching task (used by the evaluator).

        Args:
            task: TeachingTask (or its string value).
            inputs: Task-specific inputs dict, e.g.
                lesson:      {"topic": ...}
                problem_solving: {"problem_text": ...}
                review:      {"scope": ...}
                cheatsheet:  {"scope": ...}
                exam_mapping: {"exam_topic": ...}

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
            )
        if task == TeachingTask.PROBLEM_SOLVING:
            return self.generate_problem_solution(
                problem_text=inputs.get("problem_text", ""),
                goal=inputs.get("goal", "讲解解题思路，不代写答案"),
                top_k=kwargs.get("top_k", 5),
                document_ids=kwargs.get("document_ids"),
            )
        if task == TeachingTask.REVIEW:
            return self.generate_review(
                scope=inputs.get("scope", ""),
                student_level=inputs.get("student_level", "初学者"),
                top_k=kwargs.get("top_k", 8),
                document_ids=kwargs.get("document_ids"),
            )
        if task == TeachingTask.CHEATSHEET:
            return self.generate_cheatsheet(
                scope=inputs.get("scope", ""),
                page_limit=inputs.get("page_limit", "两页"),
                allowed=inputs.get("allowed", "允许携带课程讲义与公式表"),
                top_k=kwargs.get("top_k", 10),
                document_ids=kwargs.get("document_ids"),
            )
        if task == TeachingTask.EXAM_MAPPING:
            return self.generate_exam_mapping(
                exam_topic=inputs.get("exam_topic", ""),
                top_k=kwargs.get("top_k", 6),
                document_ids=kwargs.get("document_ids"),
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
            lines += ["## 中文基础讲解", "", lesson.core_explanation, ""]

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
            lines.append("## 课后练习题")
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
        """Render a Phase 3 structured result as Markdown."""
        task = getattr(result, "task_type", None)
        if task == TeachingTask.PROBLEM_SOLVING:
            return self._export_problem_solution_markdown(result)
        if task == TeachingTask.REVIEW:
            return self._export_review_markdown(result)
        if task == TeachingTask.CHEATSHEET:
            return self._export_cheatsheet_markdown(result)
        if isinstance(result, ExamKnowledgeMapping):
            return self._export_exam_mapping_markdown(result)
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

    def _export_review_markdown(self, r: GeneratedReview) -> str:
        lines = [f"# 期末复习包：{r.scope or '（未命名）'}", ""]
        if r.insufficient_material:
            lines.append("> ⚠️ 资料不足，请老师核对补充。")
            lines.append("")

        if r.knowledge_map:
            lines += ["## 课程知识点地图", ""]
            for n in r.knowledge_map:
                deps = ""
                if n.depends_on:
                    deps += f" 依赖：{', '.join(n.depends_on)}"
                if n.prerequisite_of:
                    deps += f" 支撑：{', '.join(n.prerequisite_of)}"
                lines.append(f"- **{n.name}**（{n.chapter or '未标注章节'}）— {n.core_idea}{deps}")
            lines.append("")

        if r.core_concepts:
            lines.append("## 按章节的核心概念")
            lines.append("")
            for c in r.core_concepts:
                lines.append(f"### {c.chapter or '未标注章节'}")
                for concept in c.concepts:
                    lines.append(f"- {concept}")
                lines.append("")

        if r.confusion_points:
            lines += ["## 高频混淆点", ""]
            for c in r.confusion_points:
                lines.append(f"- **{c.a}** vs **{c.b}**：{c.difference}")
            lines.append("")

        if r.self_test_questions:
            lines.append("## 自测题")
            lines.append("")
            for i, q in enumerate(r.self_test_questions, 1):
                lines.append(f"### 自测 {i}")
                lines.append("")
                lines.append(f"**题目**：{q.question}")
                if q.hint:
                    lines.append(f"**提示**：{q.hint}")
                if q.reference_answer:
                    lines.append(f"**参考答案要点**：{q.reference_answer}")
                lines.append("")

        if r.exam_mapping:
            lines += ["## 真题对应知识点", ""]
            for e in r.exam_mapping:
                lines.append(f"- **{e.exam_topic}**：{', '.join(e.knowledge_points)}")
            lines.append("")

        lines += self._numbered("复习优先级建议", r.priority_advice)
        lines += self._format_citations(r.citations)
        lines += self._format_needs_review(r.needs_review)
        return "\n".join(lines).strip() + "\n"

    def _export_cheatsheet_markdown(self, r: GeneratedCheatsheet) -> str:
        lines = [f"# 速查表：{r.title or '（未命名）'}", ""]
        lines.append(f"> 覆盖范围：{r.scope or '（未指定）'}")
        if not r.within_page_limit:
            lines.append("> ⚠️ 当前内容可能超出篇幅限制，请参考压缩建议。")
        lines.append("")

        for sec in r.sections:
            lines.append(f"## {sec.heading}")
            lines.append("")
            lines.append("| 类型 | 条目 | 内容 | 来源 |")
            lines.append("|------|------|------|------|")
            for item in sec.items:
                src = ""
                if item.source:
                    doc = self.documents.get(item.source.document_id)
                    name = doc.file_name if doc else item.source.document_id
                    src = f"{name} p.{item.source.page}"
                content = item.content.replace("|", "\\|").replace("\n", " ")
                lines.append(f"| {item.item_type} | {item.label} | {content} | {src} |")
            lines.append("")

        lines += self._numbered("排版建议", r.layout_notes)
        lines += self._numbered("压缩建议", r.compression_advice)
        lines += self._format_citations(r.citations)
        lines += self._format_needs_review(r.needs_review)
        return "\n".join(lines).strip() + "\n"

    def _export_exam_mapping_markdown(self, r: ExamKnowledgeMapping) -> str:
        lines = [f"# 真题知识点映射：{r.exam_topic or '（未命名）'}", ""]
        if r.knowledge_points:
            lines += ["## 对应的知识点", ""]
            for k in r.knowledge_points:
                ev = ", ".join(
                    f"{self.documents.get(c.document_id).file_name if self.documents.get(c.document_id) else c.document_id} p.{c.page}"
                    for c in k.evidence
                )
                lines.append(f"- **{k.name}**（{k.chapter or '未标注章节'}）— {k.relevance}")
                if ev:
                    lines.append(f"  - 依据：{ev}")
            lines.append("")
        if r.coverage_gap:
            lines += ["## 资料未覆盖的考点", "", r.coverage_gap, ""]
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
