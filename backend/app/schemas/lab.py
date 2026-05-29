"""Schemas cho tab thử nghiệm Agent + RAG."""

from pydantic import BaseModel, Field

from app.schemas.query_analysis import QueryAnalysisBrief


class LabChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    use_rag: bool = Field(
        default=True,
        description="Tự retrieve Rulebook chunk trước khi gọi agent (hiển thị trên UI).",
    )
    use_query_analyzer: bool = Field(
        default=True,
        description="Chạy QueryAnalyzer trước để chuẩn hóa câu hỏi và truy vấn RAG.",
    )
    rag_limit: int = Field(default=3, ge=1, le=8)


class LabRagHitBrief(BaseModel):
    chunk_id: str
    title: str
    description: str
    distance: float
    excerpt: str


class LabChatResponse(BaseModel):
    reply: str
    model_name: str
    embedding_model: str
    rag_used: bool
    rag_hits: list[LabRagHitBrief]
    query_analysis: QueryAnalysisBrief | None = None
    rag_scope: str = Field(
        default="",
        description="chain_interaction | card_text_resolution | general_rulebook",
    )


class LabInfoResponse(BaseModel):
    chat_model: str
    embedding_model: str
    rag_chunks_in_db: int
    rag_ready: bool
    lm_studio_connected: bool
    message: str
