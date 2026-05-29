"""Gọi QueryAnalyzer agent từ backend."""

from __future__ import annotations

import sys
from pathlib import Path

from app.core.config import settings
from app.schemas.query_analysis import QueryAnalysisBrief

AGENTS_DIR = Path(__file__).resolve().parents[3] / "agents"
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from config.lm_studio import LMStudioConfig  # noqa: E402
from domain.query_analysis import QueryAnalysis  # noqa: E402
from workflows.query_analyzer_agent import (  # noqa: E402
    AnalyzerDomain,
    analyze_user_query,
)


def _to_brief(analysis: QueryAnalysis) -> QueryAnalysisBrief:
    return QueryAnalysisBrief(
        intent=analysis.intent.value,
        rag_scope=analysis.rag_scope,
        language=analysis.language,
        entities=analysis.entities,
        ambiguities=analysis.ambiguities,
        clarified_question=analysis.clarified_question,
        rag_search_queries=analysis.rag_search_queries,
        answer_focus=analysis.answer_focus,
        do_not_assume=analysis.do_not_assume,
    )


async def run_query_analysis(
    message: str,
    config: LMStudioConfig,
    *,
    domain: AnalyzerDomain,
    enabled: bool = True,
) -> QueryAnalysis:
    """Phân tích câu hỏi; bỏ qua khi tắt trong settings hoặc theo request."""
    question = message.strip()
    if not enabled or not settings.QUERY_ANALYZER_ENABLED:
        return QueryAnalysis(
            clarified_question=question,
            rag_search_queries=[question] if question else [],
        )
    return await analyze_user_query(message, config, domain=domain)


def analysis_to_brief(analysis: QueryAnalysis) -> QueryAnalysisBrief:
    return _to_brief(analysis)
