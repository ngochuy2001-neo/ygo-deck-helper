"""Tool tra cứu Official Rulebook qua pgvector RAG (có lọc intent)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import asyncpg
import httpx

from config.lm_studio import load_config

_AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(_AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_DIR))

from domain.rule_rag_intent import (  # noqa: E402
    classify_rule_rag_intent,
    filter_hits_by_intent,
    is_conjunction_chunk,
)

_EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "text-embedding-embeddinggamma-300m-qat",
)


def _database_url() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "2001")
    database = os.getenv("POSTGRES_DB", "ygo-helper")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def _sql_exclude_patterns(intent_value: str) -> list[str]:
    if intent_value == "card_text_resolution":
        return []
    return ["conjunction", "ygo_advanced_conjunctions"]


async def _embed_query(query: str) -> list[float]:
    cfg = load_config()
    url = f"{cfg.base_url()}/embeddings"
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {cfg.api_key}"},
            json={"model": _EMBEDDING_MODEL, "input": [query]},
        )
        response.raise_for_status()
        data = response.json()
    items = data.get("data", [])
    if not items:
        raise ValueError("LM Studio không trả embedding.")
    vector = items[0].get("embedding")
    if not isinstance(vector, list):
        raise ValueError("Phản hồi embedding không hợp lệ.")
    return [float(value) for value in vector]


def _build_exclude_sql(exclude_patterns: list[str]) -> tuple[str, list[str]]:
    if not exclude_patterns:
        return "", []
    clauses = []
    args: list[str] = []
    for index, pattern in enumerate(exclude_patterns):
        clauses.append(f"source_filename NOT ILIKE ${index + 2}")
        args.append(f"%{pattern}%")
    return " AND " + " AND ".join(clauses), args


async def search_official_rulebook(query: str, limit: int = 3) -> str:
    """
    Tìm đoạn luật chính thức (SD Rulebook) liên quan tới câu hỏi.

    Tự phân loại intent: câu Chain/destroy KHÔNG lấy chunk Conjunctions.

    Args:
        query: Câu hỏi hoặc từ khóa (tiếng Việt hoặc Anh).
        limit: Số chunk tối đa (1–5).

    Returns:
        JSON string gồm các đoạn rulebook kèm chunk_id, title, distance, rag_scope.
    """
    cleaned = query.strip()
    if not cleaned:
        return "Lỗi: query không được để trống."

    limit = max(1, min(limit, 5))
    intent = classify_rule_rag_intent(cleaned)
    exclude_patterns = _sql_exclude_patterns(intent.value)

    try:
        vector = await _embed_query(cleaned)
    except Exception as exc:  # noqa: BLE001
        return f"Lỗi tạo embedding (LM Studio): {exc}"

    vector_literal = "[" + ",".join(str(value) for value in vector) + "]"

    try:
        conn = await asyncpg.connect(_database_url())
    except Exception as exc:  # noqa: BLE001
        return f"Lỗi kết nối PostgreSQL: {exc}"

    try:
        count = await conn.fetchval("SELECT COUNT(*) FROM rulebook_chunk_embeddings")
        if not count:
            return (
                "Chưa có dữ liệu Rulebook RAG. Hãy ingest các file .md "
                "(ygo_core_rulebook_summary, ygo_advanced_psct, ygo_advanced_conjunctions) "
                "tại trang Rulebook RAG."
            )

        exclude_sql, exclude_args = _build_exclude_sql(exclude_patterns)
        fetch_limit = max(limit * 4, 12)
        sql = f"""
            SELECT chunk_id, title, description, content, source_filename,
                   (embedding <=> $1::vector) AS distance
            FROM rulebook_chunk_embeddings
            WHERE 1=1{exclude_sql}
            ORDER BY embedding <=> $1::vector
            LIMIT ${len(exclude_args) + 2}
            """
        rows = await conn.fetch(sql, vector_literal, *exclude_args, fetch_limit)
    except Exception as exc:  # noqa: BLE001
        return f"Lỗi truy vấn Rulebook RAG: {exc}"
    finally:
        await conn.close()

    class _Row:
        def __init__(self, row: asyncpg.Record) -> None:
            self.chunk_id = row["chunk_id"]
            self.title = row["title"]
            self.content = row["content"] or ""
            self.source_filename = row["source_filename"] or ""

    filtered_rows = filter_hits_by_intent([_Row(row) for row in rows], intent)
    if intent.value == "chain_interaction":
        filtered_rows = [
            row
            for row in filtered_rows
            if not is_conjunction_chunk(row.title, row.content)
        ]

    hits: list[dict[str, Any]] = []
    for row in filtered_rows[:limit]:
        content = row.content or ""
        hits.append(
            {
                "chunk_id": row.chunk_id,
                "title": row.title,
                "description": "",
                "distance": 0.0,
                "content": content[:3500],
                "source_filename": row.source_filename,
            }
        )

    return json.dumps(
        {
            "query": cleaned,
            "rag_scope": intent.value,
            "hits": hits,
            "count": len(hits),
        },
        ensure_ascii=False,
    )
