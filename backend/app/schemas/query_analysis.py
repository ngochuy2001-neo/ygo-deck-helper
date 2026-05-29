"""Schema phản hồi phân tích câu hỏi (QueryAnalyzer)."""

from pydantic import BaseModel, Field


class QueryAnalysisBrief(BaseModel):
    """Kết quả phân tích hiển thị trên UI / debug."""

    intent: str
    rag_scope: str = ""
    language: str = "vi"
    entities: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    clarified_question: str
    rag_search_queries: list[str] = Field(default_factory=list)
    answer_focus: str = ""
    do_not_assume: list[str] = Field(default_factory=list)
