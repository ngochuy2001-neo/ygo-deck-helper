"""Orchestration: chunk Rulebook → embed LM Studio → lưu pgvector."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

AGENTS_DIR = Path(__file__).resolve().parents[3] / "agents"
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from domain.rule_rag_intent import (  # noqa: E402
    RuleRagIntent,
    classify_rule_rag_intent,
    filter_hits_by_intent,
)
from app.domain.rulebook_chunker import RulebookChunk, extract_rulebook_chunks
from app.repositories.rulebook_rag_repository import RulebookRagRepository
from app.schemas.rag import (
    RulebookChunkPreview,
    RulebookChunkPreviewResponse,
    RulebookIngestResponse,
    RulebookRagStatsResponse,
    RulebookSearchHit,
    RulebookSearchResponse,
)
from app.services.embedding_service import EmbeddingServiceError, create_embeddings


def _sql_patterns_for_intent(
    intent: RuleRagIntent,
) -> tuple[list[str], list[str]]:
    """Pattern ILIKE cho source_filename trước vector search."""
    if intent == RuleRagIntent.CHAIN_INTERACTION:
        return [], ["conjunction", "ygo_advanced_conjunctions"]
    if intent == RuleRagIntent.CARD_TEXT_RESOLUTION:
        return ["conjunction", "psct", "ygo_advanced", "core_rulebook", "sd_rulebook"], []
    return [], ["conjunction", "ygo_advanced_conjunctions"]


class RulebookRagService:
    MAX_UPLOAD_BYTES = 5 * 1024 * 1024

    async def read_upload(self, file: UploadFile) -> tuple[str, str]:
        if not file.filename or not file.filename.lower().endswith(".md"):
            raise ValueError("Chỉ chấp nhận file markdown (.md).")

        raw = await file.read()
        if len(raw) > self.MAX_UPLOAD_BYTES:
            raise ValueError(f"File quá lớn (tối đa {self.MAX_UPLOAD_BYTES // 1024 // 1024} MB).")

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("File phải mã hóa UTF-8.") from exc

        if not text.strip():
            raise ValueError("File trống.")

        return file.filename, text

    @staticmethod
    def _to_previews(chunks: list[RulebookChunk]) -> list[RulebookChunkPreview]:
        return [
            RulebookChunkPreview(
                chunk_id=chunk.chunk_id,
                title=chunk.title,
                description=chunk.description,
                content=chunk.content,
                char_count=len(chunk.content),
                source_headings=chunk.source_headings,
            )
            for chunk in chunks
        ]

    def preview(self, filename: str, text: str) -> RulebookChunkPreviewResponse:
        chunks = extract_rulebook_chunks(text)
        if not chunks:
            raise ValueError(
                "Không trích được chunk — file cần có các tiêu đề markdown ##."
            )
        return RulebookChunkPreviewResponse(
            filename=filename,
            chunks=self._to_previews(chunks),
        )

    async def ingest(
        self,
        repo: RulebookRagRepository,
        filename: str,
        text: str,
    ) -> RulebookIngestResponse:
        chunks = extract_rulebook_chunks(text)
        if not chunks:
            raise ValueError("Không trích được chunk từ file.")

        texts = [f"{chunk.title}\n\n{chunk.content}" for chunk in chunks]
        model = settings.RAG_EMBEDDING_MODEL

        try:
            vectors = await create_embeddings(texts, model=model)
        except EmbeddingServiceError as exc:
            raise ValueError(str(exc)) from exc

        count = await repo.replace_all_chunks(
            chunks=chunks,
            embeddings=vectors,
            embedding_model=model,
            source_filename=filename,
        )

        return RulebookIngestResponse(
            filename=filename,
            embedding_model=model,
            chunks_ingested=count,
            chunks=self._to_previews(chunks),
        )

    async def get_stats(self, repo: RulebookRagRepository) -> RulebookRagStatsResponse:
        data = await repo.get_stats()
        return RulebookRagStatsResponse.model_validate(data)

    async def search(
        self,
        repo: RulebookRagRepository,
        query: str,
        *,
        limit: int = 4,
        rag_scope: str | None = None,
        clarified_question: str | None = None,
    ) -> RulebookSearchResponse:
        intent = classify_rule_rag_intent(
            query,
            rag_scope=rag_scope,
            clarified_question=clarified_question,
        )
        include_patterns, exclude_patterns = _sql_patterns_for_intent(intent)

        try:
            vectors = await create_embeddings([query])
        except EmbeddingServiceError as exc:
            raise ValueError(str(exc)) from exc

        fetch_limit = max(limit * 4, 12)
        hits_raw = await repo.similarity_search(
            vectors[0],
            limit=limit,
            include_source_patterns=include_patterns or None,
            exclude_source_patterns=exclude_patterns or None,
            fetch_limit=fetch_limit,
        )
        if not hits_raw and include_patterns:
            hits_raw = await repo.similarity_search(
                vectors[0],
                limit=limit,
                exclude_source_patterns=exclude_patterns or None,
                fetch_limit=fetch_limit,
            )
        hits = [
            RulebookSearchHit(
                chunk_id=row.chunk_id,
                title=row.title,
                description=row.description,
                content=row.content,
                distance=distance,
                source_filename=row.source_filename or "",
            )
            for row, distance in hits_raw
        ]
        hits = filter_hits_by_intent(hits, intent)[:limit]
        return RulebookSearchResponse(query=query, hits=hits)
