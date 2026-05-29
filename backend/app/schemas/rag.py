"""Pydantic schemas cho RAG Rulebook."""

from pydantic import BaseModel, Field


class RulebookChunkPreview(BaseModel):
    chunk_id: str
    title: str
    description: str
    content: str
    char_count: int
    source_headings: list[str]


class RulebookChunkPreviewResponse(BaseModel):
    filename: str
    chunks: list[RulebookChunkPreview]


class RulebookIngestResponse(BaseModel):
    filename: str
    embedding_model: str
    chunks_ingested: int
    chunks: list[RulebookChunkPreview]


class RulebookRagStatsResponse(BaseModel):
    total_chunks: int
    embedding_model: str | None
    source_filenames: list[str]
    chunk_ids: list[str]


class RulebookSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    limit: int = Field(default=4, ge=1, le=20)
    rag_scope: str | None = Field(
        default=None,
        description="chain_interaction | card_text_resolution | general_rulebook",
    )


class RulebookSearchHit(BaseModel):
    chunk_id: str
    title: str
    description: str
    content: str
    distance: float
    source_filename: str = ""


class RulebookSearchResponse(BaseModel):
    query: str
    hits: list[RulebookSearchHit]
