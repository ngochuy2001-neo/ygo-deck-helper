"""Unit tests cho quy tắc lọc lá bài YGO."""

from app.domain.card_filter_rules import (
    CardFilterSelection,
    CardGroup,
    FilterField,
    MonsterFrame,
    resolve_applicability,
    sanitize_search_params,
)
from app.schemas.card_search import CardSearchParams, StatRange, finalize_card_search


def test_trap_disables_level_attribute_atk() -> None:
    app = resolve_applicability(
        CardFilterSelection(card_group=CardGroup.TRAP),
    )
    assert not app[FilterField.LEVEL].enabled
    assert not app[FilterField.ATTRIBUTE].enabled
    assert not app[FilterField.ATK].enabled
    assert not app[FilterField.DEF].enabled
    assert app[FilterField.TRAP_RACES].enabled
    assert not app[FilterField.RACES].enabled


def test_spell_disables_monster_stats() -> None:
    app = resolve_applicability(
        CardFilterSelection(card_group=CardGroup.SPELL),
    )
    assert not app[FilterField.LEVEL].enabled
    assert app[FilterField.SPELL_RACES].enabled


def test_link_frame_disables_level_enables_linkval() -> None:
    app = resolve_applicability(
        CardFilterSelection(
            card_group=CardGroup.MONSTER,
            frame_types=[MonsterFrame.LINK.value],
        ),
    )
    assert not app[FilterField.LEVEL].enabled
    assert app[FilterField.LINKVAL].enabled
    assert app[FilterField.LINKMARKERS].enabled
    assert not app[FilterField.DEF].enabled


def test_pendulum_enables_scale() -> None:
    app = resolve_applicability(
        CardFilterSelection(
            card_group=CardGroup.MONSTER,
            frame_types=[MonsterFrame.EFFECT_PENDULUM.value],
        ),
    )
    assert app[FilterField.SCALE].enabled


def test_sanitize_trap_strips_level() -> None:
    raw = {
        "card_group": "trap",
        "level": {"min": 4, "max": 8},
        "attributes": ["DARK"],
        "trap_races": ["Counter"],
    }
    cleaned = sanitize_search_params(raw)
    assert cleaned["level"] is None
    assert cleaned["attributes"] is None
    assert cleaned["trap_races"] == ["Counter"]


def test_sanitize_link_strips_level_keeps_linkval() -> None:
    raw = {
        "card_group": "monster",
        "frame_types": ["link"],
        "level": {"min": 4},
        "linkval": {"min": 2, "max": 2},
    }
    cleaned = sanitize_search_params(raw)
    assert cleaned["level"] is None
    assert cleaned["linkval"] == {"min": 2, "max": 2}


def test_card_search_params_trap_level_stripped() -> None:
    params = finalize_card_search(
        CardSearchParams(
            card_group=CardGroup.TRAP,
            level=StatRange(min=4, max=8),
            trap_races=["Counter"],
        ),
    )
    assert params.level is None
    assert params.trap_races == ["Counter"]


def test_passcode_search_clears_other_filters() -> None:
    params = finalize_card_search(
        CardSearchParams(
            passcode=89631139,
            q="dragon",
            level=StatRange(min=8),
        ),
    )
    assert params.q is None
    assert params.level is None
    assert params.passcode == 89631139
