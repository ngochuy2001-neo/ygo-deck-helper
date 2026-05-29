import type { CardSearchFilters, StatRange } from "@/types/cardSearch";
import { DEFAULT_CARD_SEARCH_FILTERS } from "@/types/cardSearch";

function hasStatRange(stat?: StatRange | null): boolean {
  return stat?.min != null || stat?.max != null;
}

/** Sao chép filters để chỉnh trong modal (draft). */
export function cloneFilters(filters: CardSearchFilters): CardSearchFilters {
  return {
    ...filters,
    frame_types: [...(filters.frame_types ?? [])],
    attributes: [...(filters.attributes ?? [])],
    races: [...(filters.races ?? [])],
    spell_races: [...(filters.spell_races ?? [])],
    trap_races: [...(filters.trap_races ?? [])],
    linkmarkers: [...(filters.linkmarkers ?? [])],
    banlist_tcg: [...(filters.banlist_tcg ?? [])],
    level: filters.level ? { ...filters.level } : null,
    atk: filters.atk ? { ...filters.atk } : null,
    def: filters.def ? { ...filters.def } : null,
    scale: filters.scale ? { ...filters.scale } : null,
    linkval: filters.linkval ? { ...filters.linkval } : null,
  };
}

/** Giữ ô tìm kiếm, reset phần bộ lọc modal. */
export function clearModalFilters(
  current: CardSearchFilters,
): CardSearchFilters {
  return {
    ...DEFAULT_CARD_SEARCH_FILTERS,
    q: current.q,
    passcode: current.passcode,
  };
}

/** Đếm số tiêu chí lọc đang bật (không tính q/passcode). */
export function countActiveModalFilters(filters: CardSearchFilters): number {
  let count = 0;
  if (filters.card_group && filters.card_group !== "all") count += 1;
  count += filters.frame_types?.length ?? 0;
  count += filters.attributes?.length ?? 0;
  count += filters.races?.length ?? 0;
  count += filters.spell_races?.length ?? 0;
  count += filters.trap_races?.length ?? 0;
  count += filters.linkmarkers?.length ?? 0;
  count += filters.banlist_tcg?.length ?? 0;
  if (filters.archetype?.trim()) count += 1;
  if (hasStatRange(filters.level)) count += 1;
  if (hasStatRange(filters.atk)) count += 1;
  if (hasStatRange(filters.def)) count += 1;
  if (hasStatRange(filters.scale)) count += 1;
  if (hasStatRange(filters.linkval)) count += 1;
  if (filters.sort && filters.sort !== "name") count += 1;
  if (filters.order === "desc") count += 1;
  return count;
}
