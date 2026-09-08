"""
Teaching prompt templates (Phase 2 + Phase 3).

Provides:
  - SYSTEM_PROMPT and per-task templates (lesson / problem solving).
  - format_context(): render retrieved chunks with document + page metadata.
  - build_*_messages(): assemble chat messages for each teaching task.

Phase 3 adds the structured-output schemas (JSON field lists) so the LLM can
return machine-parseable teaching materials that map directly onto the dataclasses
in src/core/models.py.
"""

import re
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
    "\n\n引用格式（必读）：课程资料每条开头标注了 [文件名 | page 页码 | chunk_id]。"
    "输出 citations 时必须带真实存在的 chunk_id，格式示例："
    "{\"citations\": [{\"document_id\": \"真实存在的文档ID\", \"page\": 0, \"chunk_id\": \"对应chunk\"}]}。"
    "不要引用资料中未出现的 chunk_id 或页码。"
)

# ---------------------------------------------------------------------------
# Task templates (Phase 2)
# ---------------------------------------------------------------------------

LESSON_TEMPLATE = """\
任务：根据【课程资料】为老师撰写一份**中文教学讲义（备课包）**，对标高质量补习班讲义的风格与深度：
内容详尽、结构清晰、例题与代码/命令丰富、重视易错点与记忆技巧。

【学生水平】{student_level}
【课堂时长】{duration}
【内容规模】{detail_guide}
【主题/侧重】{topic}
【资料范围】{scope_names}

【课程资料】
{context}

【输出要求】只输出一个 JSON 对象（不要输出多余文字），字段如下：
{{
  "topic": "本课主题（中文，精炼且有区分度，如：Week5 SQL 查询与数据汇总）",
  "learning_objectives": ["3-5 条可衡量的学习目标，如：能够写出…/解释…/区分…"],
  "prerequisites": ["前置知识清单"],
  "core_explanation": "整篇讲义的正文（Markdown，字数与详尽度以【内容规模】为准，详见【正文写作规范】）",
  "terminology": [{{"term": "英文术语", "explanation": "中文解释"}}],
  "examples": [{{"title": "例子标题", "content": "例子内容（可含代码）"}}],
  "misconceptions": ["2-4 个学生高频误区，要具体"],
  "discussion_questions": ["2-3 个课堂互动/思考题"],
  "exercises": [{{"question": "题干", "hint": "分步提示", "reference_answer": "参考答案"}}],
  "citations": [{{"document_id": "真实存在的文档ID", "page": 页码, "chunk_id": "该资料头部的chunk_id"}}],
  "needs_review": ["需要老师确认/补充的内容，没有则留空数组"]
}}

【正文写作规范】(core_explanation 使用 Markdown，换行用 \\n)
1. 开头先给「📋 本周内容预览」：编号列出本课将讲的主要知识点（像目录一样）。
2. 然后按知识点分节（### / #### 小节标题），逐点精讲，每个知识点尽量做到“四件套”：
   a. 定义/作用：1-2 句中英文说明，点出别称或英文术语；
   b. 关键点：用表格 / 步骤列表 / 流程图 / 执行顺序表达，必要时给速查表；
   c. 例子：给 1-2 个贴近本课资料的具体例子，命令/代码放 ``` 代码块并说明结果；
      例子必须与资料中的真实用法一致，不要发明资料里没有的 API 或语法；
   d. 易错与提示：用 ⚠️ / 💡 标注易错点、边界情况（NULL、默认值、截断等）、
      性能提示或记忆技巧，可用类比帮助理解（如“p 值像法庭证据”）。
3. 重点/难点可单独用 #### 强调，段落之间要有衔接，避免罗列名词。
4. 覆盖【课程资料】中的**全部知识点**；若资料过长已被截断，则把“已出现”的内容讲透，
   并在 needs_review 注明可能遗漏的部分，绝不编造。

【习题规范】(exercises)
- 生成 **3 道**围绕本课核心知识点的练习题，题型尽量多样（选择/判断/填空/简答/写代码/综合案例任选组合）；
- question：给真实场景题干（尽量具体：给定字段、数据、要求，参考“部门-员工”式可落地的题）；
- hint：分步提示，不给最终答案；
- reference_answer：清晰参考答案或要点。

【重要】
- 只使用【课程资料】中的内容；citations 必须引用真实存在的 document_id 与页码/chunk_id。
- 只有当【课程资料】里出现了“省略/截断”之类的明确标记时，才在 needs_review 说明资料缺失；
  资料完整时不要写“资料被截断/可能缺失”这类提示。
- 内容宁详勿略：写出能直接上讲台、可当讲义打印的详细程度。
- 如果资料不足，请在 needs_review 中说明并把字段留空，而不是编造。
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
  "citations": [{{"document_id": "真实存在的文档ID", "page": 页码, "chunk_id": "该资料头部的chunk_id"}}],
  "needs_review": ["需要老师确认或补充的内容，没有则留空数组"]
}}

【重要】
- 分层提示从 Level 1 到 Level 3 逐步接近答案，但始终不直接给出最终可提交答案。
- citations 必须引用真实存在的 document_id 和页码；资料不足时在 needs_review 说明。
"""

# Template registry
# ---------------------------------------------------------------------------

_TEMPLATES = {
    TeachingTask.LESSON: LESSON_TEMPLATE,
    TeachingTask.PROBLEM_SOLVING: PROBLEM_SOLVING_TEMPLATE,
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
        header = f"[{doc_name} | page {chunk.page_number} | doc_id={chunk.document_id} | chunk_id={chunk.chunk_id}]"
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


def _duration_hours(duration: str) -> float:
    """Extract hours from a duration string like '1.5 小时' or '90 分钟'."""
    m = re.search(r"(\d+(?:\.\d+)?)", duration or "")
    if not m:
        return 1.5
    val = float(m.group(1))
    if "分钟" in duration:
        return val / 60
    return val


def _duration_guide(duration: str) -> str:
    """Return a length/detail directive scaled to the classroom hours."""
    hours = _duration_hours(duration)
    if hours <= 1.0:
        return (
            "精简版课堂（≤1 小时）：只讲最核心知识点，每个知识点定义+1 个例子即可，"
            "正文约 1500–3000 字，练习题 2 道。"
        )
    if hours <= 1.5:
        return (
            "适中课堂（约 1–1.5 小时）：每个知识点做到定义+关键点+例子，"
            "正文约 3000–4500 字，练习题 3 道。"
        )
    if hours <= 2.5:
        return (
            "详实课堂（约 1.5–2.5 小时，常规）：每个知识点做到定义/表格/真实例子/易错提示四件套，"
            "正文约 4500–7500 字，练习题 3 道。"
        )
    return (
        "超详版课堂（>2.5 小时）：在四件套基础上为每个重点多给 1-2 个进阶/对比例子与扩展，"
        "正文约 7500–11000 字，讨论问题 4-5 个，练习题可 4 道。"
    )


def build_lesson_messages(
    topic: str,
    context: str,
    student_level: str = "初学者",
    duration: str = "1 小时",
    scope_names: Optional[List[str]] = None,
    extra: str = "",
) -> List[dict]:
    """Build chat messages for the lesson (备课包 / 期末复习) task."""
    scope_text = "、".join(scope_names) if scope_names else "（见下方资料标注）"
    user = LESSON_TEMPLATE.format(
        topic=topic,
        student_level=student_level,
        duration=duration,
        detail_guide=_duration_guide(duration),
        context=context,
        scope_names=scope_text,
    )
    if extra and extra.strip():
        user += (
            "\n\n【老师对本课的附加要求】在不改变上方 JSON 字段结构的前提下尽量满足；"
            "与课程资料冲突时以资料为准并说明。\n" + extra.strip()
        )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def build_problem_solution_messages(
    problem_text: str,
    context: str,
    goal: str = "讲解解题思路，不代写答案",
    extra: str = "",
) -> List[dict]:
    """Build chat messages for the problem-solving (讲题) task."""
    user = PROBLEM_SOLVING_TEMPLATE.format(
        problem_text=problem_text,
        goal=goal,
        context=context,
    )
    if extra and extra.strip():
        user += (
            "\n\n【老师附加要求】在不改变上方 JSON 字段结构的前提下尽量满足；"
            "与课程资料冲突时以资料为准并说明。\n" + extra.strip()
        )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
