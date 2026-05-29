export type CardGroup = "all" | "monster" | "spell" | "trap" | "token" | "skill";

export type CardSortField = "name" | "atk" | "def" | "level" | "linkval" | "passcode";

export type SortOrder = "asc" | "desc";

export interface StatRange {
  min?: number | null;
  max?: number | null;
}

export interface CardSearchFilters {
  q?: string;
  passcode?: number | null;
  card_group?: CardGroup | null;
  frame_types?: string[];
  attributes?: string[];
  races?: string[];
  spell_races?: string[];
  trap_races?: string[];
  level?: StatRange | null;
  atk?: StatRange | null;
  def?: StatRange | null;
  scale?: StatRange | null;
  linkval?: StatRange | null;
  linkmarkers?: string[];
  archetype?: string;
  banlist_tcg?: string[];
  sort?: CardSortField;
  order?: SortOrder;
}

export interface CardFilterOptions {
  attributes: string[];
  monster_races: string[];
  spell_races: string[];
  trap_races: string[];
  linkmarkers: string[];
  frame_types: string[];
  archetypes_sample: string[];
  banlist_tcg_values: string[];
}

export const DEFAULT_CARD_SEARCH_FILTERS: CardSearchFilters = {
  card_group: "all",
  frame_types: [],
  attributes: [],
  races: [],
  spell_races: [],
  trap_races: [],
  linkmarkers: [],
  banlist_tcg: [],
  sort: "name",
  order: "asc",
};
