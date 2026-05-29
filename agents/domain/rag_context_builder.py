"""Gói RAG có cấu trúc — tách official / PSCT / conjunction cho prompt injection."""

from __future__ import annotations

import json
from dataclasses import dataclass

from domain.rule_rag_intent import (
    RuleRagIntent,
    is_conjunction_chunk,
    is_conjunction_source,
    _matches_patterns,
    SOURCE_CORE_PATTERNS,
    SOURCE_PSCT_PATTERNS,
)


@dataclass(frozen=True)
class StructuredRagContext:
    official_rulebook_rule: str
    psct_rule: str
    conjunction_rule: str

    def to_dict(self) -> dict[str, str]:
        return {
            "official_rulebook_rule": self.official_rulebook_rule,
            "psct_rule": self.psct_rule,
            "conjunction_rule": self.conjunction_rule,
        }


def _bucket_hit(
    title: str,
    content: str,
    source_filename: str,
) -> str:
    """Trả về bucket: official | psct | conjunction."""
    if is_conjunction_source(source_filename) or is_conjunction_chunk(title, content):
        return "conjunction"
    if _matches_patterns(source_filename, SOURCE_PSCT_PATTERNS):
        return "psct"
    if _matches_patterns(source_filename, SOURCE_CORE_PATTERNS):
        return "official"

    hay = f"{title} {content[:400]}".lower()
    if any(
        k in hay
        for k in ("conjunction", "and then", "also", "if you do", "semicolon")
    ):
        return "conjunction"
    if any(k in hay for k in ("psct", "semi-colon", "semicolon", "colon", "activation cost")):
        return "psct"
    if any(k in hay for k in ("chain", "spell speed", "destroy", "continuous", "field spell")):
        return "official"
    return "official"


def build_structured_rag_context(
    hits: list[object],
    intent: RuleRagIntent,
    *,
    max_chars_per_bucket: int = 2400,
) -> StructuredRagContext:
    buckets: dict[str, list[str]] = {
        "official": [],
        "psct": [],
        "conjunction": [],
    }

    for hit in hits:
        title = str(getattr(hit, "title", "") or "")
        content = str(getattr(hit, "content", "") or getattr(hit, "excerpt", "") or "")
        source = str(getattr(hit, "source_filename", "") or "")
        chunk_id = str(getattr(hit, "chunk_id", "") or "")
        bucket = _bucket_hit(title, content, source)
        block = f"[{chunk_id}] {title}\n{content[:1200]}"
        buckets[bucket].append(block)

    def join_bucket(key: str) -> str:
        text = "\n\n---\n\n".join(buckets[key])
        if len(text) > max_chars_per_bucket:
            return text[: max_chars_per_bucket - 1] + "…"
        return text

    official = join_bucket("official")
    psct = join_bucket("psct")
    conjunction = join_bucket("conjunction")

    if intent == RuleRagIntent.CHAIN_INTERACTION:
        conjunction = ""
    elif intent == RuleRagIntent.CARD_TEXT_RESOLUTION and not conjunction:
        conjunction = "(Không retrieve được đoạn Conjunctions — gọi tool nếu cần.)"

    if not official and psct:
        official = "(Xem psct_rule.)"
    if not official and not psct:
        official = "(Chưa có đoạn Rulebook phù hợp trong RAG.)"

    return StructuredRagContext(
        official_rulebook_rule=official,
        psct_rule=psct or "(Không có đoạn PSCT trong lần retrieve này.)",
        conjunction_rule=conjunction,
    )


JUDGE_LAB_TASK_INSTRUCTIONS = """\
Task: Act as Head Judge. Use rag_context as your legal knowledge base.

Ground every inference in rag_context — do not invent rules.
Apply extracted principles to user_query step by step; do not answer by repeating chunks verbatim.
Use query_analysis.entities, answer_focus, and ambiguities (if present) as reasoning anchors.
For yes/no or permission questions: first line MUST be **ĐƯỢC PHÉP (YES)**: or **KHÔNG ĐƯỢC PHÉP (NO)**: or **TÙY LOẠI BÀI (DEPENDS)**: — never bare "Có." / "Không." alone.
The explanation must match the label (no contradictory opening).
Reference [chunk_id] briefly when citing a source — never paste long rag_context blocks.
If rag_context is insufficient, call search_official_rulebook or query_card_database.\
"""


def format_judge_lab_user_payload(
    *,
    user_query: str,
    rag_context: StructuredRagContext,
    analysis_brief: dict[str, object] | None = None,
) -> str:
    """
    Payload gửi agent: hướng dẫn suy luận + JSON context.
    """
    payload: dict[str, object] = {
        "rag_context": rag_context.to_dict(),
        "user_query": user_query,
    }
    if analysis_brief:
        payload["query_analysis"] = analysis_brief

    return (
        f"{JUDGE_LAB_TASK_INSTRUCTIONS}\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )
