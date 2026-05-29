"""
Phân loại intent RAG luật YGO — tránh "RAG poisoning" (vd. Conjunctions khi hỏi Chain/Destroy).

Intent 1 (chain_interaction): Chain, Spell Speed, destroy vs negate — KHÔNG lấy Conjunctions.
Intent 2 (card_text_resolution): PSCT nội tại lá — Then/Also/And — được phép Conjunctions.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Protocol, TypeVar


class RuleRagIntent(str, Enum):
    CHAIN_INTERACTION = "chain_interaction"
    CARD_TEXT_RESOLUTION = "card_text_resolution"
    GENERAL_RULEBOOK = "general_rulebook"


# Pattern khớp source_filename (ILIKE %pattern%)
SOURCE_CORE_PATTERNS = (
    "ygo_core_rulebook_summary",
    "core_rulebook",
    "sd_rulebook",
    "rulebook",
)
SOURCE_PSCT_PATTERNS = ("ygo_advanced_psct", "advanced_psct", "psct")
SOURCE_CONJUNCTIONS_PATTERNS = (
    "ygo_advanced_conjunctions",
    "advanced_conjunctions",
    "conjunction",
)

_CHAIN_VI = (
    r"xích",
    r"chain",
    r"spell\s*speed",
    r"phản công",
    r"counter",
    r"negate",
    r"phủ nhận",
    r"tranh chấp",
    r"kích hoạt.*phá hủy",
    r"phá hủy.*(kích hoạt|chain|xích|hiệu ứng)",
    r"destroy.*(chain|activate|activation|negat)",
    r"khi đang chain",
    r"link \d",
    r"đang resolve",
)
_CHAIN_EN = (
    r"spell speed",
    r"chain link",
    r"in response",
    r"still resolve",
    r"destroy.*activat",
    r"negat.*activat",
)

_CONJUNCTION_VI = (
    r"từ nối",
    r"thì sau",
    r"\bthen\b",
    r"\balso\b",
    r"and if you do",
    r"trước hay sau",
    r"dấu hai chấm",
    r"dấu chấm phẩy",
    r"chữ trước.*:",
    r";\s*",
)
_CONJUNCTION_EN = (
    r"conjunction",
    r"\bthen\b",
    r"\balso\b",
    r"and if you do",
    r"semicolon",
    r"colon.*semicolon",
    r"psct.*text",
    r"resolve.*order",
)

_CHAIN_COMPILED = re.compile(
    "|".join(_CHAIN_VI + _CHAIN_EN),
    re.IGNORECASE,
)
_CONJUNCTION_COMPILED = re.compile(
    "|".join(_CONJUNCTION_VI + _CONJUNCTION_EN),
    re.IGNORECASE,
)

_SEGOC_COMPILED = re.compile(
    r"segoc|simultaneous effects go on chain|mandatory.*optional|"
    r"bắt buộc.*(tùy chọn|tự nguyện)|phân bậc.*chain|category \d",
    re.IGNORECASE,
)
_PSCT_STRUCTURE_COMPILED = re.compile(
    r"banish.*;\s*target|;\s*destroy|semi-?colon|chấm phẩy|dấu hai chấm|"
    r"activation cost|chi phí|cost.*activation|psct|colon.*semicolon|"
    r"targeting at activation|chỉ định.*kích hoạt",
    re.IGNORECASE,
)
_NON_ACTIVATED_COMPILED = re.compile(
    r"non-activated|continuous effect|hiệu ứng liên tục|không kích hoạt|"
    r"không có dấu|lose \d+ atk|lose 500|tự động.*(sân|field)|"
    r"negate the activation of a monster effect",
    re.IGNORECASE,
)

# Chunk title/content markers (khi ingest 1 file lớn)
_CONJUNCTION_CHUNK_MARKERS = (
    "conjunction",
    "and then",
    "if you do",
    "also:",
    "semicolon",
    "colon and",
)


class RagHitLike(Protocol):
    title: str
    content: str
    source_filename: str


def _matches_patterns(filename: str, patterns: tuple[str, ...]) -> bool:
    lowered = (filename or "").lower()
    return any(pattern in lowered for pattern in patterns)


def is_conjunction_source(filename: str) -> bool:
    return _matches_patterns(filename, SOURCE_CONJUNCTIONS_PATTERNS)


def is_conjunction_chunk(title: str, content: str) -> bool:
    hay = f"{title}\n{content[:800]}".lower()
    return any(marker in hay for marker in _CONJUNCTION_CHUNK_MARKERS)


def classify_rule_rag_intent(
    message: str,
    *,
    rag_scope: str | None = None,
    clarified_question: str | None = None,
) -> RuleRagIntent:
    """
    Phân loại intent RAG: tín hiệu mạnh → rag_scope QueryAnalyzer → heuristic regex.
    """
    text = f"{message} {clarified_question or ''}".strip()

    if _SEGOC_COMPILED.search(text):
        return RuleRagIntent.GENERAL_RULEBOOK
    if _PSCT_STRUCTURE_COMPILED.search(text):
        return RuleRagIntent.CARD_TEXT_RESOLUTION
    if _NON_ACTIVATED_COMPILED.search(text):
        return RuleRagIntent.CARD_TEXT_RESOLUTION

    if rag_scope:
        normalized = rag_scope.strip().lower()
        for intent in RuleRagIntent:
            if intent.value == normalized:
                return intent

    has_chain = bool(_CHAIN_COMPILED.search(text))
    has_conj = bool(_CONJUNCTION_COMPILED.search(text))

    if has_conj and not has_chain:
        return RuleRagIntent.CARD_TEXT_RESOLUTION
    if has_chain and not has_conj:
        return RuleRagIntent.CHAIN_INTERACTION
    if has_chain and has_conj:
        # Destroy trên Chain — không nhầm với PSCT cost/semicolon (đã lọc ở trên).
        if re.search(r"phá hủy|destroy", text, re.I):
            return RuleRagIntent.CHAIN_INTERACTION
        return RuleRagIntent.CARD_TEXT_RESOLUTION

    # Mặc định: câu về destroy/effect thường là chain — không kéo Conjunctions
    if re.search(
        r"phá hủy|destroy|negat|tiếp tục.*(hiệu ứng|thực hiện)|still resolve|resolve",
        text,
        re.I,
    ):
        return RuleRagIntent.CHAIN_INTERACTION

    return RuleRagIntent.GENERAL_RULEBOOK


def source_filename_allowed(filename: str, intent: RuleRagIntent) -> bool:
    """Lọc theo file nguồn khi DB có nhiều file ingest."""
    if intent == RuleRagIntent.CHAIN_INTERACTION:
        if is_conjunction_source(filename):
            return False
        return (
            _matches_patterns(filename, SOURCE_CORE_PATTERNS)
            or _matches_patterns(filename, SOURCE_PSCT_PATTERNS)
            or not _matches_patterns(filename, SOURCE_CONJUNCTIONS_PATTERNS)
        )

    if intent == RuleRagIntent.CARD_TEXT_RESOLUTION:
        return (
            _matches_patterns(filename, SOURCE_CONJUNCTIONS_PATTERNS)
            or _matches_patterns(filename, SOURCE_PSCT_PATTERNS)
            or _matches_patterns(filename, SOURCE_CORE_PATTERNS)
        )

    return not is_conjunction_source(filename)


T = TypeVar("T", bound=RagHitLike)


def filter_hits_by_intent(hits: list[T], intent: RuleRagIntent) -> list[T]:
    """Lọc chunk sau vector search (an toàn khi 1 file Rulebook lớn)."""
    filtered: list[T] = []
    for hit in hits:
        filename = getattr(hit, "source_filename", "") or ""
        title = getattr(hit, "title", "") or ""
        content = getattr(hit, "content", "") or ""

        if not source_filename_allowed(filename, intent):
            continue
        if intent == RuleRagIntent.CHAIN_INTERACTION and is_conjunction_chunk(
            title, content
        ):
            continue
        if intent == RuleRagIntent.CARD_TEXT_RESOLUTION:
            # Ưu tiên conjunction/psct; vẫn cho core nếu không có marker conjunction
            pass
        filtered.append(hit)
    return filtered


def rag_search_queries_for_intent(
    intent: RuleRagIntent,
    base_queries: list[str],
    original: str,
) -> list[str]:
    """Bổ sung truy vấn embedding theo intent (tiếng Anh PSCT)."""
    extras: list[str] = []
    if intent == RuleRagIntent.CHAIN_INTERACTION:
        extras = [
            "Spell Speed Chain activated effect resolve destroy",
            "Continuous Spell Trap must remain on field to resolve",
            "destroy does not negate activated effect",
        ]
    elif intent == RuleRagIntent.CARD_TEXT_RESOLUTION:
        extras = [
            "PSCT colon semicolon conjunction then also if you do",
            "effect resolution order card text",
        ]
    elif intent == RuleRagIntent.GENERAL_RULEBOOK:
        extras = [
            "SEGOC simultaneous mandatory optional turn player chain order",
            "Spell Speed 1 activated at same time mandatory optional",
            "colon semicolon cost targeting activation PSCT",
        ]

    seen: set[str] = set()
    ordered: list[str] = []
    for q in [*base_queries, *extras, original]:
        key = q.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        ordered.append(q.strip())
    return ordered[:5]
