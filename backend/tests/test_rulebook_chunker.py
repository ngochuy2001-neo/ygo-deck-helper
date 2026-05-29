"""Tests cắt chunk Rulebook."""

from pathlib import Path

from app.domain.rulebook_chunker import extract_rulebook_chunks

_REPO_ROOT = Path(__file__).resolve().parents[2]
RULEBOOK = _REPO_ROOT / "SD_RuleBook_EN_10.md"


def test_split_by_h2_headings() -> None:
    text = """# Doc
## Section Alpha
Line one.
More alpha.

## 1
tiny

## Section Beta
Beta content here with enough characters to pass the filter.
"""
    chunks = extract_rulebook_chunks(text, min_chars=20)

    assert len(chunks) == 2
    assert chunks[0].title == "Section Alpha"
    assert "Line one" in chunks[0].content
    assert chunks[1].title == "Section Beta"
    assert "Beta content" in chunks[1].content


def test_bullet_headings_do_not_split_section() -> None:
    """Tiêu đề bullet ## \\uf06e không tách mất nội dung giữa các section."""
    text = """## Public Knowledge
## \uf06e
For cases like targeting simultaneously.
If effects of Spell Speed 1 cards are activated at
the same time, they will be resolved in a special Chain. This Chain is
made starting with the turn player's mandatory effects.
"""
    chunks = extract_rulebook_chunks(text, min_chars=40)
    assert len(chunks) == 1
    assert "mandatory effects" in chunks[0].content


def test_sample_rulebook_produces_many_chunks() -> None:
    if not RULEBOOK.is_file():
        return

    chunks = extract_rulebook_chunks(RULEBOOK.read_text(encoding="utf-8"))
    assert len(chunks) > 10

    titles = {chunk.title for chunk in chunks}
    assert "WHAT IS A MONSTER CARD?" in titles
    assert "HOW TO SYNCHRO SUMMON" in titles

    for chunk in chunks:
        assert chunk.content.startswith("## ")
        assert chunk.chunk_id
        assert chunk.source_headings == [chunk.title]
