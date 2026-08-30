"""
Teaching prompt templates (Phase 2 + Phase 3).

Provides:
  - SYSTEM_PROMPT and per-task templates (lesson / problem solving / review /
    cheatsheet / exam mapping).
  - format_context(): render retrieved chunks with document + page metadata.
  - build_*_messages(): assemble chat messages for each teaching task.

Phase 3 adds the structured-output schemas (JSON field lists) so the LLM can
return machine-parseable teaching materials that map directly onto the dataclasses
in src/core/models.py.
"""

from typing import List, Optional

from src.core.models import (
    Chunk,
    Document,
    TeachingTask,
)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "你是资深大学讲师，负责给海外院校的中文补习班学生讲解课程内容。"
    "你只根据【课程资料】回答问题，绝不编造资料中没有的内容。"
    "所有事实性结论都必须标注来源。当资料不足以回答时，明确说明资料不足，"
    "并指出哪些内容需要老师补充，而不是猜测。"
)

# ---------------------------------------------------------------------------
# Task templates (Phase 2)
# ---------------------------------------------------------------------------

LESSON_TEMPLATE = """\
任务：为本周课程生成一份中文「备课包」。

【本周主题】{topic}
【学生水平】{student_level}
【课堂时长】{duration}

【课程资料】
{context}

【输出要求】只输出一个 JSON 对象（不要输出多余文字），字段如下：
{{
  "topic": "本周主题（中文）",
  "learning_objectives": ["2-4 条学习目标"],
  "prerequisites": ["学生需要的前置知识"],
  "core_explanation": "中文基础讲解（覆盖主题，可引用资料）",
  "terminology": [{{"term": "英文术语", "explanation": "中文解释"}}],
  "examples": [{{"title": "例子标题", "content": "例子内容"}}],
  "misconceptions": ["常见误区"],
  "discussion_questions": ["课堂互动问题"],
  "exercises": [{{"question": "题目", "hint": "提示", "reference_answer": "参考答案"}}],
  "citations": [{{"document_id": "真实存在的文档ID", "page": 页码}}],
  "needs_review": ["需要老师确认或补充的内容，没有则留空数组"]
}}

【重要】
- 只使用【课程资料】中的内容；citations 必须引用真实存在的 document_id 和页码。
- 如果资料不足，请在 needs_review 中说明，并把字段留空而不是编造。
"""

PROBLEM_SOLVING_TEMPLATE = """\
任务：讲解一道作业题或真题，采用「教学辅导模式」。
注意：你是在教学生怎么做，不是替学生完成作业。不要直接给出可提交的完整答案。

【题目】
{problem_text}

【讲解目标】{goal}

【课程资料】
{context}

【输出要求】只输出一个 JSON 对象（不要输出多余文字），字段如下：
{{
  "problem_summary": "用中文一句话概括题意",
  "knowledge_points": [{{"name": "知识点名称", "explanation": "为什么这道题用到它"}}],
  "prerequisites": ["解题需要的前置知识"],
  "steps": [
    {{
      "description": "这一步做什么",
      "hint": "分层提示：不给答案，引导学生思考",
      "answer_progress": "做到这一步应该得到什么中间结果（不写完整答案）"
    }}
  ],
  "layered_hints": [
    {{"level": 1, "hint": "最小提示：只提醒思路方向"}},
    {{"level": 2, "hint": "中间提示：给出更具体的线索"}},
    {{"level": 3, "hint": "接近答案：点出关键公式或判定依据"}}
  ],
  "common_errors": ["学生容易犯的错误"],
  "rubric_mapping": [{{"criterion": "评分标准条目", "how_to_earn": "如何满足这条标准"}}],
  "reference_direction": "解题方向与验证方法（不直接代写）",
  "citations": [{{"document_id": "真实存在的文档ID", "page": 页码}}],
  "needs_review": ["需要老师确认或补充的内容，没有则留空数组"]
}}

【重要】
- 分层提示从 Level 1 到 Level 3 逐步接近答案，但始终不直接给出最终可提交答案。
- citations 必须引用真实存在的 document_id 和页码；资料不足时在 needs_review 说明。
"""

REVIEW_TEMPLATE = """\
任务：为期末复习生成一份「期末复习包」。

【复习范围】{scope}
【学生水平】{student_level}

【课程资料】
{context}

【输出要求】只输出一个 JSON 对象（不要输出多余文字），字段如下：
{{
  "scope": "复习范围（中文）",
  "knowledge_map": [
    {{
      "name": "知识点",
      "chapter": "所属章节",
      "core_idea": "核心概念（1-2 句）",
      "prerequisite_of": ["该知识点支撑的后续知识点"],
      "depends_on": ["该知识点依赖的前置知识点"]
    }}
  ],
  "core_concepts": [{{"chapter": "章节", "concepts": ["核心概念"]}}],
  "confusion_points": [{{"a": "概念 A", "b": "概念 B", "difference": "如何区分"}}],
  "self_test_questions": [{{"question": "自测题", "hint": "提示", "reference_answer": "参考答案要点"}}],
  "exam_mapping": [{{"exam_topic": "真题/考点", "knowledge_points": ["对应知识点"]}}],
  "priority_advice": ["复习优先级建议"],
  "citations": [{{"document_id": "真实存在的文档ID", "page": 页码}}],
  "needs_review": ["需要老师确认或补充的内容，没有则留空数组"]
}}

【重要】
- knowledge_map 应覆盖复习范围内的主要章节，并尽量给出知识点之间的依赖关系。
- citations 必须引用真实存在的 document_id 和页码；资料不足时在 needs_review 说明。
"""

CHEATSHEET_TEMPLATE = """\
任务：生成一份考场用的「两页 cheat sheet」草稿。

【考试范围】{scope}
【篇幅限制】{page_limit}
【允许携带】{allowed}

【课程资料】
{context}

【输出要求】只输出一个 JSON 对象（不要输出多余文字），字段如下：
{{
  "title": "cheat sheet 标题",
  "scope": "覆盖的考试范围",
  "sections": [
    {{
      "heading": "区块标题",
      "items": [
        {{"type": "definition|formula|step|comparison|example",
          "label": "条目名（如 Mean）",
          "content": "尽量简短的内容或公式",
          "source": {{"document_id": "真实存在的文档ID", "page": 页码}}}}
      ]
    }}
  ],
  "layout_notes": ["排版建议：如何用两页布局、字号、分区"],
  "compression_advice": ["超出篇幅时的压缩建议"],
  "within_page_limit": true,
  "citations": [{{"document_id": "真实存在的文档ID", "page": 页码}}],
  "needs_review": ["需要老师确认或补充的内容，没有则留空数组"]
}}

【重要】
- 内容必须短小精悍，适合考场快速查找；公式和定义优先。
- within_page_limit 表示按当前内容量是否估计能放进 {page_limit} 页。
- citations 必须引用真实存在的 document_id 和页码；资料不足时在 needs_review 说明。
"""

EXAM_MAPPING_TEMPLATE = """\
任务：分析一道真题/考点，映射到课程知识点。

【真题/考点】{exam_topic}
【课程资料】
{context}

【输出要求】只输出一个 JSON 对象（不要输出多余文字），字段如下：
{{
  "exam_topic": "真题/考点描述",
  "knowledge_points": [
    {{
      "name": "知识点",
      "chapter": "所属章节",
      "relevance": "为什么真题会考到这个知识点（依据资料）",
      "evidence_chunks": [{{"document_id": "真实存在的文档ID", "page": 页码}}]
    }}
  ],
  "coverage_gap": "资料中未覆盖的考点，若全部覆盖则为空字符串",
  "needs_review": ["需要老师确认或补充的内容，没有则留空数组"]
}}

【重要】
- 只使用【课程资料】中的内容；evidence_chunks 必须引用真实存在的 document_id 和页码。
- 资料中没有的考点必须放进 coverage_gap，而不是编造。
"""

# ---------------------------------------------------------------------------
# Template registry
# ---------------------------------------------------------------------------

_TEMPLATES = {
    TeachingTask.LESSON: LESSON_TEMPLATE,
    TeachingTask.PROBLEM_SOLVING: PROBLEM_SOLVING_TEMPLATE,
    TeachingTask.REVIEW: REVIEW_TEMPLATE,
    TeachingTask.CHEATSHEET: CHEATSHEET_TEMPLATE,
    TeachingTask.EXAM_MAPPING: EXAM_MAPPING_TEMPLATE,
}


def get_template(task) -> str:
    """
    Return the prompt template for a teaching task.

    Args:
        task: TeachingTask or its string value.

    Returns:
        The template string, or LESSON_TEMPLATE if unknown.
    """
    if isinstance(task, str):
        try:
            task = TeachingTask(task)
        except ValueError:
            return LESSON_TEMPLATE
    return _TEMPLATES.get(task, LESSON_TEMPLATE)


# ---------------------------------------------------------------------------
# Context formatting
# ---------------------------------------------------------------------------

def format_context(
    chunks: List[Chunk],
    documents: dict,
    max_chars: Optional[int] = None,
) -> str:
    """
    Render retrieved chunks into a context block for the LLM prompt.

    Each chunk is prefixed with its document file name and page number so the
    model can cite real sources (and so the teacher can verify).

    Args:
        chunks: Retrieved chunks (ordered by relevance).
        documents: document_id -> Document mapping.
        max_chars: Optional hard cap on total rendered length. When truncating,
            the first chunk header is always kept so at least one source anchor
            survives.

    Returns:
        Rendered context string.
    """
    blocks = []
    for chunk in chunks:
        doc = documents.get(chunk.document_id)
        doc_name = doc.file_name if doc else chunk.document_id
        header = f"[{doc_name} | page {chunk.page_number} | doc_id={chunk.document_id}]"
        blocks.append(f"{header}\n{chunk.text}")

    full = "\n\n".join(blocks)

    if max_chars and len(full) > max_chars:
        # Keep the first block's header (source anchor) plus as much text as fits.
        first_header = blocks[0].split("\n", 1)[0]
        budget = max(max_chars - len(first_header) - len("\n\n...\n"), 0)
        truncated_body = ""
        for block in blocks:
            body = block.split("\n", 1)[1] if "\n" in block else block
            if len(truncated_body) + len(body) + 2 > budget:
                break
            truncated_body += body + "\n\n"
        full = first_header + "\n" + truncated_body.strip() + "\n\n...（上下文已截断）"

    return full


# ---------------------------------------------------------------------------
# Message builders
# ---------------------------------------------------------------------------

def _user_prompt(template: str, **kwargs) -> str:
    """Render a template with keyword args, tolerating unused keys."""
    return template.format(**{k: kwargs.get(k, "") for k in _template_keys(template)})


def _template_keys(template: str) -> set:
    """Extract {placeholder} names from a template string."""
    keys = set()
    start = 0
    while True:
        open_idx = template.find("{", start)
        if open_idx == -1:
            break
        close_idx = template.find("}", open_idx)
        if close_idx == -1:
            break
        key = template[open_idx + 1:close_idx]
        if key and not key.startswith("{"):
            keys.add(key)
        start = close_idx + 1
    return keys


def build_lesson_messages(
    topic: str,
    context: str,
    student_level: str = "初学者",
    duration: str = "1 小时",
) -> List[dict]:
    """Build chat messages for the lesson (备课包) task."""
    user = LESSON_TEMPLATE.format(
        topic=topic,
        student_level=student_level,
        duration=duration,
        context=context,
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def build_problem_solution_messages(
    problem_text: str,
    context: str,
    goal: str = "讲解解题思路，不代写答案",
) -> List[dict]:
    """Build chat messages for the problem-solving (讲题) task."""
    user = PROBLEM_SOLVING_TEMPLATE.format(
        problem_text=problem_text,
        goal=goal,
        context=context,
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def build_review_messages(
    scope: str,
    context: str,
    student_level: str = "初学者",
) -> List[dict]:
    """Build chat messages for the final review (期末复习) task."""
    user = REVIEW_TEMPLATE.format(
        scope=scope,
        student_level=student_level,
        context=context,
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def build_cheatsheet_messages(
    scope: str,
    context: str,
    page_limit: str = "两页",
    allowed: str = "允许携带课程讲义与公式表",
) -> List[dict]:
    """Build chat messages for the cheat sheet task."""
    user = CHEATSHEET_TEMPLATE.format(
        scope=scope,
        page_limit=page_limit,
        allowed=allowed,
        context=context,
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def build_exam_mapping_messages(
    exam_topic: str,
    context: str,
) -> List[dict]:
    """Build chat messages for the exam-question knowledge mapping task."""
    user = EXAM_MAPPING_TEMPLATE.format(
        exam_topic=exam_topic,
        context=context,
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
