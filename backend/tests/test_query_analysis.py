"""Unit test parser QueryAnalyzer (không gọi LLM)."""

from __future__ import annotations

import sys
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[2] / "agents"
sys.path.insert(0, str(AGENTS_DIR))

from domain.query_analysis import (  # noqa: E402
    QueryIntent,
    parse_query_analysis,
    rag_queries_for_search,
)


def test_parse_json_fence() -> None:
    raw = """```json
{
  "intent": "rule_question",
  "language": "vi",
  "entities": ["Quick Effect"],
  "ambiguities": [],
  "clarified_question": "Quick Effect khác Ignition thế nào?",
  "rag_search_queries": ["Quick Effect", "Ignition Effect"],
  "answer_focus": "So sánh timing và chain",
  "do_not_assume": ["deck cụ thể"]
}
```"""
    analysis = parse_query_analysis(raw, fallback_question="gốc")
    assert analysis.intent == QueryIntent.RULE_QUESTION
    assert analysis.clarified_question.startswith("Quick Effect")
    assert len(analysis.rag_search_queries) == 2


def test_parse_fallback_on_invalid() -> None:
    analysis = parse_query_analysis("không phải json", fallback_question="câu gốc")
    assert analysis.intent == QueryIntent.UNCLEAR
    assert analysis.clarified_question == "câu gốc"


def test_rag_queries_dedupe() -> None:
    from domain.query_analysis import QueryAnalysis

    analysis = QueryAnalysis(
        clarified_question="A",
        rag_search_queries=["A", "B"],
    )
    queries = rag_queries_for_search(analysis, "A")
    assert queries == ["A", "B"]
