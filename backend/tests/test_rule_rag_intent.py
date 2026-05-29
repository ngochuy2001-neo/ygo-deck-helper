"""Tests phân loại intent RAG — không gọi LLM."""

from __future__ import annotations

import sys
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[2] / "agents"
sys.path.insert(0, str(AGENTS_DIR))

from domain.rule_rag_intent import (  # noqa: E402
    RuleRagIntent,
    classify_rule_rag_intent,
    filter_hits_by_intent,
    is_conjunction_chunk,
)


class _Hit:
    def __init__(self, title: str, content: str, source_filename: str = "") -> None:
        self.title = title
        self.content = content
        self.source_filename = source_filename


def test_destroy_chain_not_conjunction() -> None:
    q = (
        "Một lá bài khi kích hoạt hiệu ứng, nếu có lá khác phá hủy lá đó, "
        "hiệu ứng có tiếp tục thực hiện không?"
    )
    intent = classify_rule_rag_intent(q)
    assert intent == RuleRagIntent.CHAIN_INTERACTION


def test_then_also_is_card_text() -> None:
    q = "Chữ Then và Also trên lá bài — thứ tự resolve thế nào?"
    intent = classify_rule_rag_intent(q)
    assert intent == RuleRagIntent.CARD_TEXT_RESOLUTION


def test_filter_drops_conjunction_chunk_on_chain() -> None:
    hits = [
        _Hit("Spell Speed", "Chain rules", "ygo_core_rulebook_summary.md"),
        _Hit(
            "Conjunctions: And Then",
            "Destroy A, then do B",
            "ygo_advanced_conjunctions.md",
        ),
    ]
    filtered = filter_hits_by_intent(hits, RuleRagIntent.CHAIN_INTERACTION)
    assert len(filtered) == 1
    assert filtered[0].title == "Spell Speed"


def test_is_conjunction_chunk_marker() -> None:
    assert is_conjunction_chunk("PSCT", "If you do, also destroy")
    assert not is_conjunction_chunk("Chain", "Spell Speed 2")


def test_psct_cost_negate_is_card_text_not_chain() -> None:
    q = (
        'You can banish 1 card from your hand; target 1 face-up card; destroy it. '
        "If negated by Counter Trap on Chain, is cost returned?"
    )
    intent = classify_rule_rag_intent(
        q,
        rag_scope="chain_interaction",
    )
    assert intent == RuleRagIntent.CARD_TEXT_RESOLUTION


def test_segoc_is_general_rulebook() -> None:
    q = "SEGOC mandatory optional turn player chain link order"
    intent = classify_rule_rag_intent(q, rag_scope="chain_interaction")
    assert intent == RuleRagIntent.GENERAL_RULEBOOK
