#!/usr/bin/env python3
"""CLI: cắt markdown Rulebook theo tiêu đề ## và in preview."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Cho phép chạy từ repo root: python backend/scripts/chunk_rulebook.py
_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.domain.rulebook_chunker import extract_rulebook_chunks  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Chunk SD Rulebook theo tiêu đề ##")
    parser.add_argument(
        "input",
        nargs="?",
        default=str(_REPO_ROOT / "SD_RuleBook_EN_10.md"),
        help="Đường dẫn file markdown Rulebook",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Xuất JSON thay vì text preview",
    )
    args = parser.parse_args()

    path = Path(args.input)
    if not path.is_file():
        print(f"Không tìm thấy file: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    chunks = extract_rulebook_chunks(text)

    if not chunks:
        print("Không trích được chunk nào — kiểm tra định dạng file.", file=sys.stderr)
        return 1

    if args.json:
        payload = [
            {
                "chunk_id": c.chunk_id,
                "title": c.title,
                "description": c.description,
                "char_count": len(c.content),
                "source_headings": c.source_headings,
                "content": c.content,
            }
            for c in chunks
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n{'=' * 72}")
        print(f"Chunk {index}: {chunk.title} [{chunk.chunk_id}]")
        print(f"Mô tả: {chunk.description}")
        print(f"Ký tự: {len(chunk.content):,}")
        print(f"Tiêu đề nguồn: {', '.join(chunk.source_headings)}")
        print("-" * 72)
        preview = chunk.content[:600]
        print(preview)
        if len(chunk.content) > 600:
            print(f"\n... (+{len(chunk.content) - 600} ký tự)")

    print(f"\nTổng: {len(chunks)} chunk.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
