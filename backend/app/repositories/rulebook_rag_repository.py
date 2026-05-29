"""Truy vấn PostgreSQL + pgvector cho Rulebook RAG."""

from __future__ import annotations

import hashlib
import json

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.rulebook_chunker import RulebookChunk
from app.models.rag import RulebookChunkEmbedding


class RulebookRagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def content_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def replace_all_chunks(
        self,
        *,
        chunks: list[RulebookChunk],
        embeddings: list[list[float]],
        embedding_model: str,
        source_filename: str,
    ) -> int:
        """Xóa chunk của một source_filename và chèn bộ mới (giữ file khác trong DB)."""
        await self._session.execute(
            delete(RulebookChunkEmbedding).where(
                RulebookChunkEmbedding.source_filename == source_filename
            )
        )

        for chunk, vector in zip(chunks, embeddings, strict=True):
            row = RulebookChunkEmbedding(
                chunk_id=chunk.chunk_id,
                title=chunk.title,
                description=chunk.description,
                content=chunk.content,
                source_headings=json.dumps(chunk.source_headings, ensure_ascii=False),
                embedding_model=embedding_model,
                source_filename=source_filename,
                content_hash=self.content_hash(chunk.content),
                embedding=vector,
            )
            self._session.add(row)

        await self._session.commit()
        return len(chunks)

    async def get_stats(self) -> dict[str, object]:
        total = await self._session.scalar(
            select(func.count()).select_from(RulebookChunkEmbedding)
        )
        model = await self._session.scalar(
            select(RulebookChunkEmbedding.embedding_model)
            .order_by(RulebookChunkEmbedding.updated_at.desc())
            .limit(1)
        )
        filenames = (
            await self._session.scalars(
                select(RulebookChunkEmbedding.source_filename).distinct()
            )
        ).all()
        chunk_ids = (
            await self._session.scalars(
                select(RulebookChunkEmbedding.chunk_id).order_by(RulebookChunkEmbedding.id)
            )
        ).all()
        return {
            "total_chunks": int(total or 0),
            "embedding_model": model,
            "source_filenames": list(filenames),
            "chunk_ids": list(chunk_ids),
        }

    async def similarity_search(
        self,
        query_vector: list[float],
        *,
        limit: int = 4,
        include_source_patterns: list[str] | None = None,
        exclude_source_patterns: list[str] | None = None,
        fetch_limit: int | None = None,
    ) -> list[tuple[RulebookChunkEmbedding, float]]:
        """
        Tìm chunk gần nhất theo cosine distance (pgvector <=>).

        include/exclude_source_patterns: substring khớp ILIKE trên source_filename.
        fetch_limit: lấy dư để lọc chunk-level sau (mặc định = limit).
        """
        vector_literal = "[" + ",".join(str(value) for value in query_vector) + "]"
        take = fetch_limit if fetch_limit is not None else limit
        include_patterns = [p.strip() for p in (include_source_patterns or []) if p.strip()]
        exclude_patterns = [p.strip() for p in (exclude_source_patterns or []) if p.strip()]

        where_parts = ["1=1"]
        params: dict[str, object] = {
            "query_vec": vector_literal,
            "limit_val": take,
        }

        if include_patterns:
            include_clauses = " OR ".join(
                f"source_filename ILIKE :inc_{index}"
                for index in range(len(include_patterns))
            )
            where_parts.append(f"({include_clauses})")
            for index, pattern in enumerate(include_patterns):
                params[f"inc_{index}"] = f"%{pattern}%"

        if exclude_patterns:
            for index, pattern in enumerate(exclude_patterns):
                where_parts.append(f"source_filename NOT ILIKE :exc_{index}")
                params[f"exc_{index}"] = f"%{pattern}%"

        where_sql = " AND ".join(where_parts)
        sql = text(
            f"""
            SELECT id, chunk_id, title, description, content, source_headings,
                   embedding_model, source_filename, content_hash,
                   created_at, updated_at,
                   (embedding <=> CAST(:query_vec AS vector)) AS distance
            FROM rulebook_chunk_embeddings
            WHERE {where_sql}
            ORDER BY embedding <=> CAST(:query_vec AS vector)
            LIMIT :limit_val
            """
        )
        result = await self._session.execute(sql, params)
        hits: list[tuple[RulebookChunkEmbedding, float]] = []
        for row in result.mappings():
            entity = RulebookChunkEmbedding(
                id=row["id"],
                chunk_id=row["chunk_id"],
                title=row["title"],
                description=row["description"],
                content=row["content"],
                source_headings=row["source_headings"],
                embedding_model=row["embedding_model"],
                source_filename=row["source_filename"],
                content_hash=row["content_hash"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                embedding=query_vector,
            )
            hits.append((entity, float(row["distance"])))
        return hits
