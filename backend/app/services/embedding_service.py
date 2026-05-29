"""Gọi LM Studio OpenAI-compatible /v1/embeddings."""

from __future__ import annotations

import httpx

from app.core.config import settings
from app.schemas.lm_studio import LMStudioSettings
from app.services.lm_studio_service import load_lm_studio_settings


class EmbeddingServiceError(Exception):
    """Lỗi khi tạo embedding qua LM Studio."""


async def create_embeddings(
    texts: list[str],
    *,
    model: str | None = None,
    lm_config: LMStudioSettings | None = None,
) -> list[list[float]]:
    """
    Tạo vector embedding cho danh sách văn bản.

    Model mặc định: settings.RAG_EMBEDDING_MODEL
    (text-embedding-embeddinggamma-300m-qat, 768 chiều).
    """
    if not texts:
        return []

    cfg = lm_config or load_lm_studio_settings()
    embed_model = model or settings.RAG_EMBEDDING_MODEL
    url = f"{cfg.base_url}/embeddings"

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {cfg.api_key}"},
            json={"model": embed_model, "input": texts},
        )

    if response.status_code >= 400:
        raise EmbeddingServiceError(
            f"LM Studio embeddings lỗi {response.status_code}: {response.text[:500]}"
        )

    data = response.json()
    items = data.get("data", [])
    if len(items) != len(texts):
        raise EmbeddingServiceError(
            f"Số embedding trả về ({len(items)}) khác số input ({len(texts)})."
        )

    vectors: list[list[float]] = []
    for item in sorted(items, key=lambda row: row.get("index", 0)):
        vector = item.get("embedding")
        if not isinstance(vector, list) or not vector:
            raise EmbeddingServiceError("Phản hồi thiếu trường embedding.")
        dim = len(vector)
        expected = settings.RAG_EMBEDDING_DIMENSION
        if dim != expected:
            raise EmbeddingServiceError(
                f"Vector {dim} chiều, cấu hình RAG_EMBEDDING_DIMENSION={expected}. "
                "Cập nhật .env hoặc chọn model embedding đúng."
            )
        vectors.append([float(value) for value in vector])

    return vectors
