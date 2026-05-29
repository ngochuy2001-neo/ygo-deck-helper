"""Tests gói RAG context và payload Judge Lab — không gọi LLM."""

from __future__ import annotations

import sys
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[2] / "agents"
sys.path.insert(0, str(AGENTS_DIR))

from domain.rag_context_builder import (  # noqa: E402
    JUDGE_LAB_TASK_INSTRUCTIONS,
    StructuredRagContext,
    format_judge_lab_user_payload,
)

_RULEBOOK_LAB_AGENT_PATH = AGENTS_DIR / "workflows" / "rulebook_lab_agent.py"


def test_judge_lab_task_instructions_emphasize_reasoning() -> None:
    lowered = JUDGE_LAB_TASK_INSTRUCTIONS.lower()
    assert "apply" in lowered
    assert "do not answer by repeating chunks" in lowered
    assert "step by step" in lowered
    assert "chunk_id" in lowered


def test_format_judge_lab_user_payload_includes_instructions_and_query() -> None:
    rag = StructuredRagContext(
        official_rulebook_rule="[c1] Chain\nSpell Speed rules…",
        psct_rule="(Không có đoạn PSCT trong lần retrieve này.)",
        conjunction_rule="",
    )
    payload = format_judge_lab_user_payload(
        user_query="Quick Effect khác Ignition Effect thế nào?",
        rag_context=rag,
        analysis_brief={
            "answer_focus": "So sánh Spell Speed và timing kích hoạt",
            "entities": ["Quick Effect", "Ignition Effect"],
        },
    )

    assert JUDGE_LAB_TASK_INSTRUCTIONS in payload
    assert "Quick Effect khác Ignition Effect" in payload
    assert "answer_focus" in payload
    assert "using only the rag_context buckets" not in payload.lower()
    assert "không được phép (no)" in JUDGE_LAB_TASK_INSTRUCTIONS.lower()


def test_system_prompt_requires_explicit_ruling_labels() -> None:
    source = _RULEBOOK_LAB_AGENT_PATH.read_text(encoding="utf-8")
    assert "KHÔNG ĐƯỢC PHÉP (NO)" in source
    assert "ĐƯỢC PHÉP (YES)" in source
    assert 'NEVER write "Có."' in source or "never bare" in source.lower()
