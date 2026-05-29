"""Tool truy vấn database lá bài — PostgreSQL (ygo_cards)."""

from __future__ import annotations

import json
import os
from typing import Any

import asyncpg


def _database_url() -> str:
    """Dựng DSN từ biến môi trường (đồng bộ với backend/.env)."""
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "2001")
    database = os.getenv("POSTGRES_DB", "ygo-helper")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


async def query_card_database(
    card_name: str,
    include_rulings: bool = False,
) -> str:
    """
    Tra cứu thông tin lá bài Yu-Gi-Oh! từ database nội bộ (YGOPRODeck sync).

    Dùng khi Agent cần ATK/DEF, type, effect text, banlist status của một lá bài.

    Args:
        card_name: Tên lá bài (tiếng Anh hoặc một phần tên; tìm ILIKE).
        include_rulings: Nếu True, bao gồm banlist_info từ DB.

    Returns:
        Chuỗi JSON mô tả lá bài. Trả về thông báo lỗi dạng string nếu không tìm
        thấy hoặc DB lỗi để Agent có thể thử lại với tên khác.
    """
    if not card_name.strip():
        return "Lỗi: card_name không được để trống."

    try:
        conn = await asyncpg.connect(_database_url())
    except Exception as exc:  # noqa: BLE001
        return f"Lỗi kết nối PostgreSQL: {exc}"

    try:
        rows = await conn.fetch(
            """
            SELECT
                c.passcode,
                c.name,
                c.type,
                c.frame_type,
                c.desc,
                c.atk,
                c.def,
                c.level,
                c.race,
                c.attribute,
                c.archetype,
                c.banlist_info,
                (
                    SELECT json_agg(
                        json_build_object(
                            'set_name', s.set_name,
                            'set_code', s.set_code,
                            'set_rarity', s.set_rarity
                        )
                    )
                    FROM ygo_card_sets s
                    WHERE s.card_passcode = c.passcode
                ) AS card_sets,
                (
                    SELECT json_agg(
                        json_build_object(
                            'image_passcode', i.image_passcode,
                            'local_path', i.local_path
                        )
                    )
                    FROM ygo_card_images i
                    WHERE i.card_passcode = c.passcode
                ) AS card_images
            FROM ygo_cards c
            WHERE c.name ILIKE $1
            ORDER BY c.name
            LIMIT 5
            """,
            f"%{card_name.strip()}%",
        )
    except Exception as exc:  # noqa: BLE001
        return f"Lỗi truy vấn database: {exc}"
    finally:
        await conn.close()

    if not rows:
        return (
            f"Không tìm thấy lá bài khớp '{card_name}'. "
            "Hãy thử tên tiếng Anh chính thức hoặc yêu cầu đồng bộ DB từ Dashboard."
        )

    results: list[dict[str, Any]] = []
    for row in rows:
        item: dict[str, Any] = {
            "passcode": row["passcode"],
            "name": row["name"],
            "type": row["type"],
            "frame_type": row["frame_type"],
            "desc": row["desc"],
            "atk": row["atk"],
            "def": row["def"],
            "level": row["level"],
            "race": row["race"],
            "attribute": row["attribute"],
            "archetype": row["archetype"],
            "card_sets": row["card_sets"],
            "card_images": row["card_images"],
        }
        if include_rulings and row["banlist_info"]:
            raw = row["banlist_info"]
            if isinstance(raw, str):
                item["banlist_info"] = json.loads(raw)
            else:
                item["banlist_info"] = raw
        results.append(item)

    return json.dumps({"cards": results, "count": len(results)}, ensure_ascii=False)
