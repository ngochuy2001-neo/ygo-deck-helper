"use client";

import type { CardSearchFilters } from "@/types/cardSearch";

interface CardFilterChipsProps {
  filters: CardSearchFilters;
  onRemove: (patch: Partial<CardSearchFilters>) => void;
  onClearAll: () => void;
}

function formatStat(label: string, stat?: { min?: number | null; max?: number | null } | null) {
  if (!stat || (stat.min == null && stat.max == null)) return null;
  if (stat.min != null && stat.max != null) return `${label} ${stat.min}–${stat.max}`;
  if (stat.min != null) return `${label} ≥${stat.min}`;
  return `${label} ≤${stat.max}`;
}

export function CardFilterChips({ filters, onRemove, onClearAll }: CardFilterChipsProps) {
  const chips: { key: string; label: string; clear: Partial<CardSearchFilters> }[] = [];

  if (filters.passcode) {
    chips.push({
      key: "passcode",
      label: `#${filters.passcode}`,
      clear: { passcode: null, q: "" },
    });
  } else {
    if (filters.q?.trim()) {
      chips.push({ key: "q", label: `"${filters.q}"`, clear: { q: "" } });
    }
    if (filters.card_group && filters.card_group !== "all") {
      chips.push({
        key: "group",
        label: filters.card_group,
        clear: { card_group: "all" },
      });
    }
    filters.attributes?.forEach((a) =>
      chips.push({
        key: `attr-${a}`,
        label: a,
        clear: { attributes: filters.attributes?.filter((x) => x !== a) },
      }),
    );
    filters.frame_types?.forEach((f) =>
      chips.push({
        key: `frame-${f}`,
        label: f,
        clear: { frame_types: filters.frame_types?.filter((x) => x !== f) },
      }),
    );
    const levelLabel = formatStat("Level", filters.level);
    if (levelLabel) chips.push({ key: "level", label: levelLabel, clear: { level: null } });
    const atkLabel = formatStat("ATK", filters.atk);
    if (atkLabel) chips.push({ key: "atk", label: atkLabel, clear: { atk: null } });
    const defLabel = formatStat("DEF", filters.def);
    if (defLabel) chips.push({ key: "def", label: defLabel, clear: { def: null } });
    const scaleLabel = formatStat("Scale", filters.scale);
    if (scaleLabel) chips.push({ key: "scale", label: scaleLabel, clear: { scale: null } });
    const linkLabel = formatStat("Link", filters.linkval);
    if (linkLabel) chips.push({ key: "linkval", label: linkLabel, clear: { linkval: null } });
    if (filters.archetype?.trim()) {
      chips.push({
        key: "arch",
        label: filters.archetype,
        clear: { archetype: "" },
      });
    }
    filters.banlist_tcg?.forEach((b) =>
      chips.push({
        key: `ban-${b}`,
        label: b,
        clear: { banlist_tcg: filters.banlist_tcg?.filter((x) => x !== b) },
      }),
    );
  }

  if (chips.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5 border-b border-zinc-200 px-3 py-2 dark:border-zinc-800">
      {chips.map((chip) => (
        <button
          key={chip.key}
          type="button"
          onClick={() => onRemove(chip.clear)}
          className="inline-flex items-center gap-1 rounded-full bg-zinc-200 px-2 py-0.5 text-[10px] font-medium text-zinc-800 hover:bg-zinc-300 dark:bg-zinc-800 dark:text-zinc-200 dark:hover:bg-zinc-700"
        >
          {chip.label}
          <span aria-hidden>×</span>
        </button>
      ))}
      <button
        type="button"
        onClick={onClearAll}
        className="text-[10px] text-zinc-500 underline hover:text-zinc-800 dark:hover:text-zinc-200"
      >
        Xóa tất cả
      </button>
    </div>
  );
}
