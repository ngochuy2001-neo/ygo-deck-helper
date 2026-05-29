/**
 * Quy tắc bộ lọc lá bài YGO — mirror backend/app/domain/card_filter_rules.py
 */

import type { CardGroup, CardSearchFilters } from "@/types/cardSearch";

export type FilterField =
  | "attribute"
  | "level"
  | "atk"
  | "def"
  | "scale"
  | "linkval"
  | "linkmarkers"
  | "races"
  | "spell_races"
  | "trap_races"
  | "frame_types"
  | "archetype"
  | "banlist";

export interface Applicability {
  enabled: boolean;
  reason?: string;
}

const PENDULUM_FRAMES = new Set([
  "normal_pendulum",
  "effect_pendulum",
  "ritual_pendulum",
  "fusion_pendulum",
  "synchro_pendulum",
  "xyz_pendulum",
]);

export interface FilterSelection {
  card_group?: CardGroup | null;
  frame_types?: string[];
}

function effectiveGroup(selection: FilterSelection): CardGroup | null {
  const g = selection.card_group;
  if (!g || g === "all") return null;
  return g;
}

function frameSet(selection: FilterSelection): Set<string> {
  return new Set((selection.frame_types ?? []).map((f) => f.toLowerCase()));
}

function onlyLinkFrames(frames: Set<string>): boolean {
  return frames.size > 0 && [...frames].every((f) => f === "link");
}

function hasXyzFrame(frames: Set<string>): boolean {
  return frames.has("xyz") || frames.has("xyz_pendulum");
}

function hasPendulumFrame(frames: Set<string>): boolean {
  return [...frames].some((f) => PENDULUM_FRAMES.has(f));
}

function hasLinkFrame(frames: Set<string>): boolean {
  return frames.has("link");
}

export function resolveApplicability(
  selection: FilterSelection,
): Record<FilterField, Applicability> {
  const group = effectiveGroup(selection);
  const frames = frameSet(selection);

  const on = (): Applicability => ({ enabled: true });
  const off = (reason: string): Applicability => ({ enabled: false, reason });

  const base: Record<FilterField, Applicability> = {
    attribute: on(),
    level: on(),
    atk: on(),
    def: on(),
    scale: off("Chỉ áp dụng cho lá Pendulum"),
    linkval: off("Chỉ áp dụng cho Link Monster"),
    linkmarkers: off("Chỉ áp dụng cho Link Monster"),
    races: on(),
    spell_races: off("Chỉ áp dụng cho Spell"),
    trap_races: off("Chỉ áp dụng cho Trap"),
    frame_types: on(),
    archetype: on(),
    banlist: on(),
  };

  if (group === "spell") {
    return {
      ...base,
      attribute: off("Spell không có Attribute"),
      level: off("Spell không có Level/Hạng"),
      atk: off("Spell không có ATK"),
      def: off("Spell không có DEF"),
      scale: off("Spell không có Scale"),
      linkval: off("Spell không có Link Rating"),
      linkmarkers: off("Spell không có Link markers"),
      races: off("Dùng loại Spell thay cho Race quái"),
      spell_races: on(),
      trap_races: off("Chỉ áp dụng cho Trap"),
      frame_types: off("Chọn nhóm Spell"),
    };
  }

  if (group === "trap") {
    return {
      ...base,
      attribute: off("Trap không có Attribute"),
      level: off("Trap không có Level/Hạng"),
      atk: off("Trap không có ATK"),
      def: off("Trap không có DEF"),
      scale: off("Trap không có Scale"),
      linkval: off("Trap không có Link Rating"),
      linkmarkers: off("Trap không có Link markers"),
      races: off("Dùng loại Trap thay cho Race quái"),
      spell_races: off("Chỉ áp dụng cho Spell"),
      trap_races: on(),
      frame_types: off("Chọn nhóm Trap"),
    };
  }

  if (group === "token" || group === "skill") {
    return {
      ...base,
      attribute: off("Không áp dụng cho nhóm này"),
      level: off("Không áp dụng cho nhóm này"),
      atk: off("Không áp dụng cho nhóm này"),
      def: off("Không áp dụng cho nhóm này"),
      scale: off("Không áp dụng cho nhóm này"),
      linkval: off("Không áp dụng cho nhóm này"),
      linkmarkers: off("Không áp dụng cho nhóm này"),
      races: off("Không áp dụng cho nhóm này"),
      frame_types: off("Không áp dụng cho nhóm này"),
    };
  }

  const result = { ...base };
  if (group === "monster" || group === null) {
    if (hasPendulumFrame(frames)) result.scale = on();
    if (hasLinkFrame(frames) || onlyLinkFrames(frames)) {
      result.linkval = on();
      result.linkmarkers = on();
      result.level = off("Link Monster dùng Link Rating, không dùng Level");
      result.def = off("Link Monster không có DEF");
    }
    if (frames.size > 0 && onlyLinkFrames(frames)) {
      result.level = off("Link Monster dùng Link Rating, không dùng Level");
      result.def = off("Link Monster không có DEF");
    }
  }
  return result;
}

export function levelFilterLabel(selection: FilterSelection): string {
  if (hasXyzFrame(frameSet(selection))) return "Hạng (Rank)";
  return "Level";
}

export function selectionFromFilters(filters: CardSearchFilters): FilterSelection {
  return {
    card_group: filters.card_group,
    frame_types: filters.frame_types,
  };
}

function clearStat(
  filters: CardSearchFilters,
  key: "level" | "atk" | "def" | "scale" | "linkval",
): void {
  filters[key] = null;
}

/** Xóa các field không hợp lệ khỏi state UI trước khi gọi API. */
export function sanitizeFilters(filters: CardSearchFilters): CardSearchFilters {
  const next: CardSearchFilters = {
    ...filters,
    frame_types: [...(filters.frame_types ?? [])],
    attributes: [...(filters.attributes ?? [])],
    races: [...(filters.races ?? [])],
    spell_races: [...(filters.spell_races ?? [])],
    trap_races: [...(filters.trap_races ?? [])],
    linkmarkers: [...(filters.linkmarkers ?? [])],
    banlist_tcg: [...(filters.banlist_tcg ?? [])],
  };

  if (next.passcode) {
    return {
      passcode: next.passcode,
      sort: next.sort ?? "name",
      order: next.order ?? "asc",
    };
  }

  const app = resolveApplicability(selectionFromFilters(next));
  if (!app.attribute.enabled) next.attributes = [];
  if (!app.level.enabled) clearStat(next, "level");
  if (!app.atk.enabled) clearStat(next, "atk");
  if (!app.def.enabled) clearStat(next, "def");
  if (!app.scale.enabled) clearStat(next, "scale");
  if (!app.linkval.enabled) clearStat(next, "linkval");
  if (!app.linkmarkers.enabled) next.linkmarkers = [];
  if (!app.races.enabled) next.races = [];
  if (!app.spell_races.enabled) next.spell_races = [];
  if (!app.trap_races.enabled) next.trap_races = [];
  if (!app.frame_types.enabled) next.frame_types = [];

  const group = effectiveGroup(selectionFromFilters(next));
  if (group === "spell" || group === "trap" || group === "token" || group === "skill") {
    next.frame_types = [];
  }

  return next;
}

export const MONSTER_FRAME_OPTIONS = [
  { value: "normal", label: "Normal" },
  { value: "effect", label: "Effect" },
  { value: "ritual", label: "Ritual" },
  { value: "fusion", label: "Fusion" },
  { value: "synchro", label: "Synchro" },
  { value: "xyz", label: "Xyz" },
  { value: "link", label: "Link" },
  { value: "normal_pendulum", label: "Normal Pendulum" },
  { value: "effect_pendulum", label: "Effect Pendulum" },
  { value: "ritual_pendulum", label: "Ritual Pendulum" },
  { value: "fusion_pendulum", label: "Fusion Pendulum" },
  { value: "synchro_pendulum", label: "Synchro Pendulum" },
  { value: "xyz_pendulum", label: "Xyz Pendulum" },
] as const;

export const CARD_GROUP_OPTIONS = [
  { value: "all" as const, label: "Tất cả" },
  { value: "monster" as const, label: "Monster" },
  { value: "spell" as const, label: "Spell" },
  { value: "trap" as const, label: "Trap" },
];
