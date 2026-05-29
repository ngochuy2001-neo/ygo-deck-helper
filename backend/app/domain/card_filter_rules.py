"""
Quy tắc bộ lọc lá bài Yu-Gi-Oh! — áp dụng cho UI (disable) và API (strip tham số).
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

NON_MONSTER_FRAMES = frozenset({"spell", "trap", "token", "skill"})

PENDULUM_FRAMES = frozenset(
    {
        "normal_pendulum",
        "effect_pendulum",
        "ritual_pendulum",
        "fusion_pendulum",
        "synchro_pendulum",
        "xyz_pendulum",
    }
)

MONSTER_FRAME_VALUES = frozenset(
    {
        "normal",
        "effect",
        "ritual",
        "fusion",
        "synchro",
        "xyz",
        "link",
        *PENDULUM_FRAMES,
    }
)


class CardGroup(str, Enum):
    ALL = "all"
    MONSTER = "monster"
    SPELL = "spell"
    TRAP = "trap"
    TOKEN = "token"
    SKILL = "skill"


class MonsterFrame(str, Enum):
    NORMAL = "normal"
    EFFECT = "effect"
    RITUAL = "ritual"
    FUSION = "fusion"
    SYNCHRO = "synchro"
    XYZ = "xyz"
    LINK = "link"
    NORMAL_PENDULUM = "normal_pendulum"
    EFFECT_PENDULUM = "effect_pendulum"
    RITUAL_PENDULUM = "ritual_pendulum"
    FUSION_PENDULUM = "fusion_pendulum"
    SYNCHRO_PENDULUM = "synchro_pendulum"
    XYZ_PENDULUM = "xyz_pendulum"


class FilterField(str, Enum):
    ATTRIBUTE = "attribute"
    LEVEL = "level"
    ATK = "atk"
    DEF = "def"
    SCALE = "scale"
    LINKVAL = "linkval"
    LINKMARKERS = "linkmarkers"
    RACES = "races"
    SPELL_RACES = "spell_races"
    TRAP_RACES = "trap_races"
    FRAME_TYPES = "frame_types"
    ARCHETYPE = "archetype"
    BANLIST = "banlist"
    PASSCODE = "passcode"


@dataclass
class Applicability:
    enabled: bool
    reason: str | None = None


@dataclass
class CardFilterSelection:
    card_group: CardGroup | None = None
    frame_types: list[str] = field(default_factory=list)


def _effective_group(selection: CardFilterSelection) -> CardGroup | None:
    if selection.card_group and selection.card_group != CardGroup.ALL:
        return selection.card_group
    return None


def _frame_set(selection: CardFilterSelection) -> set[str]:
    return {f.lower() for f in selection.frame_types if f}


def _only_link_frames(frames: set[str]) -> bool:
    return bool(frames) and frames <= {"link"}


def _has_xyz_frame(frames: set[str]) -> bool:
    return bool(frames & {"xyz", "xyz_pendulum"})


def _has_pendulum_frame(frames: set[str]) -> bool:
    return bool(frames & PENDULUM_FRAMES)


def _has_link_frame(frames: set[str]) -> bool:
    return "link" in frames


def resolve_applicability(selection: CardFilterSelection) -> dict[FilterField, Applicability]:
    """Trả về trạng thái bật/tắt từng filter theo nhóm lá và frame đã chọn."""
    group = _effective_group(selection)
    frames = _frame_set(selection)

    def on(reason: str | None = None) -> Applicability:
        return Applicability(enabled=True, reason=reason)

    def off(reason: str) -> Applicability:
        return Applicability(enabled=False, reason=reason)

    # Mặc định: mọi filter monster có thể dùng (khi chưa chọn nhóm spell/trap)
    result: dict[FilterField, Applicability] = {
        FilterField.ATTRIBUTE: on(),
        FilterField.LEVEL: on(),
        FilterField.ATK: on(),
        FilterField.DEF: on(),
        FilterField.SCALE: off("Chỉ áp dụng cho lá Pendulum"),
        FilterField.LINKVAL: off("Chỉ áp dụng cho Link Monster"),
        FilterField.LINKMARKERS: off("Chỉ áp dụng cho Link Monster"),
        FilterField.RACES: on(),
        FilterField.SPELL_RACES: off("Chỉ áp dụng cho Spell"),
        FilterField.TRAP_RACES: off("Chỉ áp dụng cho Trap"),
        FilterField.FRAME_TYPES: on(),
        FilterField.ARCHETYPE: on(),
        FilterField.BANLIST: on(),
        FilterField.PASSCODE: on(),
    }

    if group == CardGroup.SPELL:
        return {
            **result,
            FilterField.ATTRIBUTE: off("Spell không có Attribute"),
            FilterField.LEVEL: off("Spell không có Level/Hạng"),
            FilterField.ATK: off("Spell không có ATK"),
            FilterField.DEF: off("Spell không có DEF"),
            FilterField.SCALE: off("Spell không có Scale"),
            FilterField.LINKVAL: off("Spell không có Link Rating"),
            FilterField.LINKMARKERS: off("Spell không có Link markers"),
            FilterField.RACES: off("Dùng loại Spell thay cho Race quái"),
            FilterField.SPELL_RACES: on(),
            FilterField.TRAP_RACES: off("Chỉ áp dụng cho Trap"),
            FilterField.FRAME_TYPES: off("Chọn nhóm Spell"),
        }

    if group == CardGroup.TRAP:
        return {
            **result,
            FilterField.ATTRIBUTE: off("Trap không có Attribute"),
            FilterField.LEVEL: off("Trap không có Level/Hạng"),
            FilterField.ATK: off("Trap không có ATK"),
            FilterField.DEF: off("Trap không có DEF"),
            FilterField.SCALE: off("Trap không có Scale"),
            FilterField.LINKVAL: off("Trap không có Link Rating"),
            FilterField.LINKMARKERS: off("Trap không có Link markers"),
            FilterField.RACES: off("Dùng loại Trap thay cho Race quái"),
            FilterField.SPELL_RACES: off("Chỉ áp dụng cho Spell"),
            FilterField.TRAP_RACES: on(),
            FilterField.FRAME_TYPES: off("Chọn nhóm Trap"),
        }

    if group in (CardGroup.TOKEN, CardGroup.SKILL):
        return {
            **result,
            FilterField.ATTRIBUTE: off("Không áp dụng cho nhóm này"),
            FilterField.LEVEL: off("Không áp dụng cho nhóm này"),
            FilterField.ATK: off("Không áp dụng cho nhóm này"),
            FilterField.DEF: off("Không áp dụng cho nhóm này"),
            FilterField.SCALE: off("Không áp dụng cho nhóm này"),
            FilterField.LINKVAL: off("Không áp dụng cho nhóm này"),
            FilterField.LINKMARKERS: off("Không áp dụng cho nhóm này"),
            FilterField.RACES: off("Không áp dụng cho nhóm này"),
            FilterField.FRAME_TYPES: off("Không áp dụng cho nhóm này"),
        }

    # Monster hoặc All (chưa chọn nhóm spell/trap)
    if group == CardGroup.MONSTER or group is None:
        if _has_pendulum_frame(frames):
            result[FilterField.SCALE] = on()
        if _has_link_frame(frames) or _only_link_frames(frames):
            result[FilterField.LINKVAL] = on()
            result[FilterField.LINKMARKERS] = on()
            result[FilterField.LEVEL] = off("Link Monster dùng Link Rating, không dùng Level")
            result[FilterField.DEF] = off("Link Monster không có DEF")

        if frames and _only_link_frames(frames):
            result[FilterField.LEVEL] = off("Link Monster dùng Link Rating, không dùng Level")
            result[FilterField.DEF] = off("Link Monster không có DEF")

    return result


def level_filter_label(selection: CardFilterSelection) -> str:
    """Nhãn UI: Level vs Rank (Xyz)."""
    frames = _frame_set(selection)
    if _has_xyz_frame(frames):
        return "Hạng (Rank)"
    return "Level"


def selection_from_params(params: dict[str, Any]) -> CardFilterSelection:
    raw_group = params.get("card_group")
    group: CardGroup | None = None
    if raw_group is not None:
        if isinstance(raw_group, CardGroup):
            group = raw_group
        else:
            try:
                group = CardGroup(str(raw_group).lower())
            except ValueError:
                group = None

    frame_types: list[str] = []
    raw_frames = params.get("frame_types")
    if raw_frames:
        frame_types = [str(f).lower() for f in raw_frames]

    return CardFilterSelection(card_group=group, frame_types=frame_types)


def _clear_field(params: dict[str, Any], key: str) -> None:
    params[key] = None


def _clear_stat_range(params: dict[str, Any], prefix: str) -> None:
    params[prefix] = None
    params[f"{prefix}_min"] = None
    params[f"{prefix}_max"] = None


def sanitize_search_params(params: dict[str, Any]) -> dict[str, Any]:
    """
    Loại bỏ tham số lọc không hợp lệ theo quy tắc YGO.
    Hoạt động trên dict phẳng (query params / CardSearchParams.model_dump).
    """
    cleaned = deepcopy(params)
    selection = selection_from_params(cleaned)
    app = resolve_applicability(selection)

    if not app[FilterField.ATTRIBUTE].enabled:
        cleaned["attributes"] = None
    if not app[FilterField.LEVEL].enabled:
        _clear_stat_range(cleaned, "level")
    if not app[FilterField.ATK].enabled:
        _clear_stat_range(cleaned, "atk")
    if not app[FilterField.DEF].enabled:
        _clear_stat_range(cleaned, "def")
    if not app[FilterField.SCALE].enabled:
        _clear_stat_range(cleaned, "scale")
    if not app[FilterField.LINKVAL].enabled:
        _clear_stat_range(cleaned, "linkval")
    if not app[FilterField.LINKMARKERS].enabled:
        cleaned["linkmarkers"] = None
    if not app[FilterField.RACES].enabled:
        cleaned["races"] = None
    if not app[FilterField.SPELL_RACES].enabled:
        cleaned["spell_races"] = None
    if not app[FilterField.TRAP_RACES].enabled:
        cleaned["trap_races"] = None
    if not app[FilterField.FRAME_TYPES].enabled:
        cleaned["frame_types"] = None

    group = _effective_group(selection)
    if group in (CardGroup.SPELL, CardGroup.TRAP, CardGroup.TOKEN, CardGroup.SKILL):
        cleaned["frame_types"] = None

    return cleaned
