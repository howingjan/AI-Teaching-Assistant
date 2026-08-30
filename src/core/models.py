"""
Core data models for the AI tutoring system.

Defines Document, Chunk, SearchResult and other fundamental structures
that ensure metadata (document_id, page numbers, source) is preserved
throughout the pipeline.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    MARKDOWN = "markdown"
    TEXT = "text"
    DOCX = "docx"


class ParseQuality(str, Enum):
    """Quality assessment of parsed content."""
    GOOD = "good"  # Text extracted successfully
    PARTIAL = "partial"  # Some text extracted; may contain OCR or formatting issues
    SCANNED = "scanned"  # Appears to be a scanned image; no text extracted
    EMPTY = "empty"  # Page contains no text
    ERROR = "error"  # Parse error occurred


@dataclass
class Document:
    """
    Represents a course material document (PDF, slide, notes, etc.).
    
    Attributes:
        document_id: Unique identifier for this document
        file_name: Original file name
        file_path: Local file path
        document_type: Type of document (PDF, Markdown, etc.)
        total_pages: Total number of pages (if applicable)
        metadata: Custom metadata (title, author, upload_date, etc.)
        parse_quality: Overall quality of text extraction
        created_at: Timestamp when document was indexed
    """
    document_id: str
    file_name: str
    file_path: str
    document_type: DocumentType
    total_pages: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    parse_quality: ParseQuality = ParseQuality.GOOD
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate document structure."""
        if not self.document_id or not self.file_name:
            raise ValueError("document_id and file_name are required")


@dataclass
class Page:
    """
    Represents a single page or section within a document.
    
    Attributes:
        document_id: Reference to parent document
        page_number: Page number (0-indexed)
        text: Extracted text content
        quality: Quality of text extraction for this page
        sections: Named sections/chapters on this page (optional)
        has_tables: Whether page contains tables
        has_images: Whether page contains images
        has_code: Whether page contains code blocks
    """
    document_id: str
    page_number: int
    text: str
    quality: ParseQuality = ParseQuality.GOOD
    sections: Optional[List[str]] = None
    has_tables: bool = False
    has_images: bool = False
    has_code: bool = False
    
    def __post_init__(self):
        if not self.text or not self.text.strip():
            self.quality = ParseQuality.EMPTY
        if not self.sections:
            self.sections = []


@dataclass
class Chunk:
    """
    Represents a semantic chunk of text extracted from a document.
    
    Maintained source information to enable accurate citation.
    
    Attributes:
        chunk_id: Unique chunk identifier
        document_id: Reference to source document
        page_number: Starting page number (0-indexed)
        section: Section/chapter name if available
        text: The actual text content
        char_start: Character position in source page
        char_end: Character position in source page
        estimated_tokens: Estimated token count for cost tracking
        order_in_doc: Sequential position for context reconstruction
    """
    chunk_id: str
    document_id: str
    page_number: int
    text: str
    char_start: int = 0
    char_end: int = 0
    section: Optional[str] = None
    estimated_tokens: int = 0
    order_in_doc: int = 0
    
    def __post_init__(self):
        if not self.text or not self.text.strip():
            raise ValueError("Chunk text cannot be empty")
        if self.char_end == 0:
            self.char_end = len(self.text)
    
    def get_citation(self) -> str:
        """Generate a citation string for this chunk."""
        return f"[doc_id: {self.document_id}, page: {self.page_number}]"


@dataclass
class SearchResult:
    """
    Represents a single search result returned by the retriever.
    
    Attributes:
        chunk: The retrieved chunk
        score: Relevance score (0-1)
        rank: Position in search results
        reasoning: Why this chunk was selected (for debugging)
    """
    chunk: Chunk
    score: float
    rank: int
    reasoning: Optional[str] = None
    
    def __post_init__(self):
        if not 0 <= self.score <= 1:
            raise ValueError(f"Score must be between 0 and 1, got {self.score}")


@dataclass
class IndexMetadata:
    """
    Metadata about the document index for serialization and cache validation.
    
    Attributes:
        index_version: Version of index format
        created_at: When index was created
        last_updated: Last modification time
        total_documents: Number of documents in index
        total_chunks: Number of chunks in index
        document_ids: List of document IDs in index
    """
    index_version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    total_documents: int = 0
    total_chunks: int = 0
    document_ids: List[str] = field(default_factory=list)


# Type aliases for clarity
DocumentStore = Dict[str, Document]  # document_id -> Document
ChunkStore = List[Chunk]  # Ordered list of chunks
PageStore = Dict[str, List[Page]]  # document_id -> List[Page]


# ---------------------------------------------------------------------------
# Phase 2: structured output models for teaching generation
# ---------------------------------------------------------------------------

class TeachingTask(str, Enum):
    """Supported teaching tasks."""
    LESSON = "lesson"  # 本周备课包
    PROBLEM_SOLVING = "problem_solving"  # 作业与真题讲题
    REVIEW = "review"  # 期末复习包
    CHEATSHEET = "cheatsheet"  # 两页 cheat sheet
    EXAM_MAPPING = "exam_mapping"  # 真题知识点映射


@dataclass
class Citation:
    """
    A source citation bound to a real chunk in the corpus.
    
    Attributes:
        document_id: Source document ID
        page: Page number (0-indexed, matches Chunk.page_number)
        chunk_id: Optional chunk ID if the citation maps to a specific chunk
        snippet: Optional quoted text from the source
    """
    document_id: str
    page: int
    chunk_id: Optional[str] = None
    snippet: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "page": self.page,
            "chunk_id": self.chunk_id,
            "snippet": self.snippet,
        }


@dataclass
class TermDefinition:
    """An English technical term with a Chinese explanation."""
    term: str
    explanation: str = ""


@dataclass
class Example:
    """A worked example with title and content."""
    title: str = ""
    content: str = ""


@dataclass
class Exercise:
    """A practice exercise with hint and reference answer."""
    question: str = ""
    hint: str = ""
    reference_answer: str = ""


@dataclass
class CitationValidation:
    """
    Result of validating citations against the document corpus.
    
    Attributes:
        valid: Whether all citations reference real documents/pages
        citations: The original citations
        missing_documents: document_ids that don't exist in the corpus
        out_of_range_pages: (document_id, page) pairs where page exceeds document pages
        valid_count: Number of valid citations
        invalid_count: Number of invalid citations
    """
    citations: List[Citation] = field(default_factory=list)
    missing_documents: List[str] = field(default_factory=list)
    out_of_range_pages: List[tuple] = field(default_factory=list)
    
    @property
    def valid_count(self) -> int:
        return len(self.citations) - len(self.missing_documents) - len(self.out_of_range_pages)
    
    @property
    def invalid_count(self) -> int:
        return len(self.missing_documents) + len(self.out_of_range_pages)
    
    @property
    def valid(self) -> bool:
        return self.invalid_count == 0


@dataclass
class GeneratedLesson:
    """
    Structured output for the "本周备课包" (weekly lesson package) task.
    
    Maps directly to the product plan's MVP output schema (section 3.3 A).
    """
    task_type: TeachingTask = TeachingTask.LESSON
    topic: str = ""
    learning_objectives: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    core_explanation: str = ""
    terminology: List[TermDefinition] = field(default_factory=list)
    examples: List[Example] = field(default_factory=list)
    misconceptions: List[str] = field(default_factory=list)
    discussion_questions: List[str] = field(default_factory=list)
    exercises: List[Exercise] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    needs_review: List[str] = field(default_factory=list)
    insufficient_material: bool = False
    raw_output: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "task_type": self.task_type.value,
            "topic": self.topic,
            "learning_objectives": self.learning_objectives,
            "prerequisites": self.prerequisites,
            "core_explanation": self.core_explanation,
            "terminology": [{"term": t.term, "explanation": t.explanation} for t in self.terminology],
            "examples": [{"title": e.title, "content": e.content} for e in self.examples],
            "misconceptions": self.misconceptions,
            "discussion_questions": self.discussion_questions,
            "exercises": [{"question": e.question, "hint": e.hint, "reference_answer": e.reference_answer} for e in self.exercises],
            "citations": [c.to_dict() for c in self.citations],
            "needs_review": self.needs_review,
            "insufficient_material": self.insufficient_material,
        }
    
    def completeness(self) -> Dict[str, bool]:
        """Report which structured fields are populated (for evaluation)."""
        checks = {
            "topic": bool(self.topic),
            "learning_objectives": bool(self.learning_objectives),
            "prerequisites": bool(self.prerequisites),
            "core_explanation": bool(self.core_explanation),
            "terminology": bool(self.terminology),
            "examples": bool(self.examples),
            "misconceptions": bool(self.misconceptions),
            "discussion_questions": bool(self.discussion_questions),
            "exercises": bool(self.exercises),
        }
        checks["complete"] = all(checks.values())
        return checks


# ---------------------------------------------------------------------------
# Phase 3: structured output models for the extended teaching tasks
# ---------------------------------------------------------------------------

@dataclass
class ProblemStep:
    """One step of a worked solution (tutoring mode: hints, not full answers)."""
    description: str = ""
    hint: str = ""
    answer_progress: str = ""


@dataclass
class LayeredHint:
    """A tiered hint: Level 1 is subtle, higher levels approach the answer."""
    level: int = 1
    hint: str = ""


@dataclass
class RubricCriterion:
    """A rubric (评分标准) criterion and how to satisfy it."""
    criterion: str = ""
    how_to_earn: str = ""


@dataclass
class KnowledgePoint:
    """A knowledge point used by a problem/exam topic."""
    name: str = ""
    explanation: str = ""


@dataclass
class GeneratedProblemSolution:
    """
    Structured output for the '作业与真题讲题' task (Phase 3).

    Maps directly to the product plan's MVP schema (section 3.3 B), using a
    tutoring mode: steps and layered hints guide the student without providing
    a directly-submittable answer.
    """
    task_type: TeachingTask = TeachingTask.PROBLEM_SOLVING
    problem_summary: str = ""
    knowledge_points: List[KnowledgePoint] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    steps: List[ProblemStep] = field(default_factory=list)
    layered_hints: List[LayeredHint] = field(default_factory=list)
    common_errors: List[str] = field(default_factory=list)
    rubric_mapping: List[RubricCriterion] = field(default_factory=list)
    reference_direction: str = ""
    citations: List[Citation] = field(default_factory=list)
    needs_review: List[str] = field(default_factory=list)
    insufficient_material: bool = False
    raw_output: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type.value,
            "problem_summary": self.problem_summary,
            "knowledge_points": [{"name": k.name, "explanation": k.explanation} for k in self.knowledge_points],
            "prerequisites": self.prerequisites,
            "steps": [
                {"description": s.description, "hint": s.hint, "answer_progress": s.answer_progress}
                for s in self.steps
            ],
            "layered_hints": [{"level": h.level, "hint": h.hint} for h in self.layered_hints],
            "common_errors": self.common_errors,
            "rubric_mapping": [{"criterion": r.criterion, "how_to_earn": r.how_to_earn} for r in self.rubric_mapping],
            "reference_direction": self.reference_direction,
            "citations": [c.to_dict() for c in self.citations],
            "needs_review": self.needs_review,
            "insufficient_material": self.insufficient_material,
        }

    def completeness(self) -> Dict[str, bool]:
        checks = {
            "problem_summary": bool(self.problem_summary),
            "knowledge_points": bool(self.knowledge_points),
            "prerequisites": bool(self.prerequisites),
            "steps": bool(self.steps),
            "layered_hints": bool(self.layered_hints),
            "common_errors": bool(self.common_errors),
            "rubric_mapping": bool(self.rubric_mapping),
            "reference_direction": bool(self.reference_direction),
        }
        # Tutoring check: layered hints must have at least 2 distinct levels.
        levels = {h.level for h in self.layered_hints}
        checks["layered_hints_are_tiered"] = len(levels) >= 2
        checks["complete"] = all(checks.values())
        return checks


@dataclass
class ReviewKnowledgeNode:
    """A knowledge node in the final-review knowledge map."""
    name: str = ""
    chapter: str = ""
    core_idea: str = ""
    prerequisite_of: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)


@dataclass
class ChapterConcepts:
    """Core concepts grouped by chapter."""
    chapter: str = ""
    concepts: List[str] = field(default_factory=list)


@dataclass
class ConfusionPoint:
    """A commonly confused pair of concepts and how to tell them apart."""
    a: str = ""
    b: str = ""
    difference: str = ""


@dataclass
class SelfTestQuestion:
    """A self-test question with hint and answer key."""
    question: str = ""
    hint: str = ""
    reference_answer: str = ""


@dataclass
class ExamMappingEntry:
    """Maps an exam topic to the course knowledge points it tests."""
    exam_topic: str = ""
    knowledge_points: List[str] = field(default_factory=list)


@dataclass
class GeneratedReview:
    """
    Structured output for the '期末复习包' task (Phase 3).

    Maps to the product plan's MVP schema (section 3.3 C): knowledge map,
    per-chapter core concepts, dependencies, confusion points, self-tests,
    exam mapping and priority advice.
    """
    task_type: TeachingTask = TeachingTask.REVIEW
    scope: str = ""
    knowledge_map: List[ReviewKnowledgeNode] = field(default_factory=list)
    core_concepts: List[ChapterConcepts] = field(default_factory=list)
    confusion_points: List[ConfusionPoint] = field(default_factory=list)
    self_test_questions: List[SelfTestQuestion] = field(default_factory=list)
    exam_mapping: List[ExamMappingEntry] = field(default_factory=list)
    priority_advice: List[str] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    needs_review: List[str] = field(default_factory=list)
    insufficient_material: bool = False
    raw_output: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type.value,
            "scope": self.scope,
            "knowledge_map": [
                {
                    "name": n.name,
                    "chapter": n.chapter,
                    "core_idea": n.core_idea,
                    "prerequisite_of": n.prerequisite_of,
                    "depends_on": n.depends_on,
                }
                for n in self.knowledge_map
            ],
            "core_concepts": [{"chapter": c.chapter, "concepts": c.concepts} for c in self.core_concepts],
            "confusion_points": [{"a": c.a, "b": c.b, "difference": c.difference} for c in self.confusion_points],
            "self_test_questions": [
                {"question": q.question, "hint": q.hint, "reference_answer": q.reference_answer}
                for q in self.self_test_questions
            ],
            "exam_mapping": [
                {"exam_topic": e.exam_topic, "knowledge_points": e.knowledge_points}
                for e in self.exam_mapping
            ],
            "priority_advice": self.priority_advice,
            "citations": [c.to_dict() for c in self.citations],
            "needs_review": self.needs_review,
            "insufficient_material": self.insufficient_material,
        }

    def completeness(self) -> Dict[str, bool]:
        checks = {
            "scope": bool(self.scope),
            "knowledge_map": bool(self.knowledge_map),
            "core_concepts": bool(self.core_concepts),
            "confusion_points": bool(self.confusion_points),
            "self_test_questions": bool(self.self_test_questions),
            "exam_mapping": bool(self.exam_mapping),
            "priority_advice": bool(self.priority_advice),
        }
        # Knowledge-map check: at least one node should express dependencies.
        has_dependency = any(
            n.depends_on or n.prerequisite_of for n in self.knowledge_map
        )
        checks["knowledge_map_has_dependencies"] = has_dependency
        checks["complete"] = all(checks.values())
        return checks


@dataclass
class CheatsheetItem:
    """A single cheat-sheet entry (definition/formula/step/comparison/example)."""
    item_type: str = "definition"  # definition|formula|step|comparison|example
    label: str = ""
    content: str = ""
    source: Optional[Citation] = None


@dataclass
class CheatsheetSection:
    """A headed section of a cheat sheet."""
    heading: str = ""
    items: List[CheatsheetItem] = field(default_factory=list)


@dataclass
class GeneratedCheatsheet:
    """
    Structured output for the '两页 cheat sheet' task (Phase 3).

    Maps to the product plan's MVP schema (section 3.3 D): structured two-page
    content, layout notes, compression advice and a within_page_limit flag.
    """
    task_type: TeachingTask = TeachingTask.CHEATSHEET
    title: str = ""
    scope: str = ""
    sections: List[CheatsheetSection] = field(default_factory=list)
    layout_notes: List[str] = field(default_factory=list)
    compression_advice: List[str] = field(default_factory=list)
    within_page_limit: bool = True
    citations: List[Citation] = field(default_factory=list)
    needs_review: List[str] = field(default_factory=list)
    insufficient_material: bool = False
    raw_output: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type.value,
            "title": self.title,
            "scope": self.scope,
            "sections": [
                {
                    "heading": s.heading,
                    "items": [
                        {
                            "type": i.item_type,
                            "label": i.label,
                            "content": i.content,
                            "source": i.source.to_dict() if i.source else None,
                        }
                        for i in s.items
                    ],
                }
                for s in self.sections
            ],
            "layout_notes": self.layout_notes,
            "compression_advice": self.compression_advice,
            "within_page_limit": self.within_page_limit,
            "citations": [c.to_dict() for c in self.citations],
            "needs_review": self.needs_review,
            "insufficient_material": self.insufficient_material,
        }

    def completeness(self) -> Dict[str, bool]:
        checks = {
            "title": bool(self.title),
            "scope": bool(self.scope),
            "sections": bool(self.sections),
            "layout_notes": bool(self.layout_notes),
            "compression_advice": bool(self.compression_advice),
        }
        checks["complete"] = all(checks.values())
        return checks


@dataclass
class MappedKnowledgePoint:
    """A knowledge point matched to an exam topic, with evidence."""
    name: str = ""
    chapter: str = ""
    relevance: str = ""
    evidence: List[Citation] = field(default_factory=list)


@dataclass
class ExamKnowledgeMapping:
    """
    Structured output for the '真题知识点映射' task (Phase 3).

    Maps an exam question/考点 to course knowledge points and flags any gap
    that the course materials do not cover.
    """
    task_type: TeachingTask = TeachingTask.EXAM_MAPPING
    exam_topic: str = ""
    knowledge_points: List[MappedKnowledgePoint] = field(default_factory=list)
    coverage_gap: str = ""
    needs_review: List[str] = field(default_factory=list)
    insufficient_material: bool = False
    raw_output: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type.value,
            "exam_topic": self.exam_topic,
            "knowledge_points": [
                {
                    "name": k.name,
                    "chapter": k.chapter,
                    "relevance": k.relevance,
                    "evidence": [c.to_dict() for c in k.evidence],
                }
                for k in self.knowledge_points
            ],
            "coverage_gap": self.coverage_gap,
            "needs_review": self.needs_review,
            "insufficient_material": self.insufficient_material,
        }

    def completeness(self) -> Dict[str, bool]:
        checks = {
            "exam_topic": bool(self.exam_topic),
            "knowledge_points": bool(self.knowledge_points),
        }
        has_evidence = any(k.evidence for k in self.knowledge_points)
        checks["has_evidence"] = has_evidence
        checks["complete"] = all(checks.values())
        return checks
