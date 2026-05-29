"""Cắt markdown Rulebook thành chunk RAG theo từng tiêu đề ##."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RulebookChunk:
    chunk_id: str
    title: str
    description: str
    content: str
    source_headings: list[str]


_MIN_CHUNK_CHARS = 40
_SKIP_HEADING_PATTERN = re.compile(r"^[\d!\.\s]+$")


def _parse_heading(line: str) -> str | None:
    """Lấy tiêu đề từ dòng `## ...` (không gồm ###)."""
    if line.startswith("###"):
        return None
    if line.startswith("## "):
        return line[3:].strip()
    if line.startswith("##"):
        return line[2:].strip()
    return None


def _should_skip_heading(title: str) -> bool:
    """Bỏ tiêu đề nhiễu (chỉ số trang, dấu chấm, quá ngắn)."""
    cleaned = title.strip()
    if len(cleaned) < 2:
        return True
    if _SKIP_HEADING_PATTERN.match(cleaned):
        return True
    if cleaned.isdigit() and len(cleaned) <= 4:
        return True
    return False


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return (slug[:56] or "section").strip("_")


def _unique_chunk_id(title: str, used: dict[str, int]) -> str:
    base = _slugify(title)
    count = used.get(base, 0)
    used[base] = count + 1
    if count == 0:
        return base
    return f"{base}_{count + 1}"


def extract_rulebook_chunks(
    text: str,
    *,
    min_chars: int = _MIN_CHUNK_CHARS,
) -> list[RulebookChunk]:
    """
    Tách file markdown thành các chunk: mỗi dòng bắt đầu bằng `##` (không phải ###)
    mở một section mới; nội dung section gồm tiêu đề và text tới section kế tiếp.
    """
    lines = text.splitlines()
    if not lines:
        return []

    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in lines:
        heading = _parse_heading(line)
        if heading is not None:
            if _should_skip_heading(heading):
                # Tiêu đề nhiễu (bullet, số trang) — gộp vào section hiện tại, không tách chunk.
                if current_title is not None:
                    current_lines.append(line)
                continue
            if current_title is not None:
                sections.append((current_title, current_lines))
            current_title = heading
            current_lines = [line]
        elif current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections.append((current_title, current_lines))

    chunks: list[RulebookChunk] = []
    used_ids: dict[str, int] = {}

    for title, section_lines in sections:
        if _should_skip_heading(title):
            continue

        content = "\n".join(section_lines).strip()
        if len(content) < min_chars:
            continue

        chunk_id = _unique_chunk_id(title, used_ids)
        preview = content.replace("\n", " ")[:120]
        description = preview + ("…" if len(content) > 120 else "")

        chunks.append(
            RulebookChunk(
                chunk_id=chunk_id,
                title=title,
                description=description,
                content=content,
                source_headings=[title],
            )
        )

    return chunks
