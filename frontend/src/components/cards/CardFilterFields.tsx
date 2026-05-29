"use client";

import { StatRangeControl } from "@/components/cards/StatRangeControl";
import {
  filterChipClass,
  filterChipCompactClass,
  filterInputClass,
  filterSectionLabel,
  filterSelectClass,
} from "@/components/cards/filterChipStyles";
import {
  CARD_GROUP_OPTIONS,
  MONSTER_FRAME_OPTIONS,
  levelFilterLabel,
  resolveApplicability,
  selectionFromFilters,
} from "@/lib/ygo/cardFilterRules";
import type { CardFilterOptions, CardSearchFilters } from "@/types/cardSearch";

interface CardFilterFieldsProps {
  filters: CardSearchFilters;
  options: CardFilterOptions | null;
  onChange: (patch: Partial<CardSearchFilters>) => void;
  archetypeListId?: string;
}

function toggleInList(list: string[] | undefined, value: string): string[] {
  const set = new Set(list ?? []);
  if (set.has(value)) set.delete(value);
  else set.add(value);
  return [...set];
}

const chipWrap = "flex flex-wrap gap-2";

export function CardFilterFields({
  filters,
  options,
  onChange,
  archetypeListId = "card-filter-archetype-list",
}: CardFilterFieldsProps) {
  const selection = selectionFromFilters(filters);
  const app = resolveApplicability(selection);
  const levelLabel = levelFilterLabel(selection);

  const patch = (partial: Partial<CardSearchFilters>) => {
    onChange(partial);
  };

  return (
    <div className="space-y-6">
      <div>
        <p className={filterSectionLabel}>Nhóm lá</p>
        <div className={chipWrap}>
          {CARD_GROUP_OPTIONS.map((opt) => {
            const active = (filters.card_group ?? "all") === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => patch({ card_group: opt.value })}
                className={filterChipClass(active)}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      </div>

      {app.frame_types.enabled && (
        <div>
          <p className={filterSectionLabel}>Frame (Monster)</p>
          <div className={chipWrap}>
            {MONSTER_FRAME_OPTIONS.map((opt) => {
              const active = filters.frame_types?.includes(opt.value);
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() =>
                    patch({
                      frame_types: toggleInList(filters.frame_types, opt.value),
                    })
                  }
                  className={filterChipCompactClass(!!active)}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {app.attribute.enabled && options && (
        <div>
          <p className={filterSectionLabel}>Attribute</p>
          <div className={chipWrap}>
            {options.attributes.map((attr) => {
              const active = filters.attributes?.includes(attr);
              return (
                <button
                  key={attr}
                  type="button"
                  onClick={() =>
                    patch({ attributes: toggleInList(filters.attributes, attr) })
                  }
                  className={filterChipClass(!!active)}
                >
                  {attr}
                </button>
              );
            })}
          </div>
        </div>
      )}

      <StatRangeControl
        label={levelLabel}
        value={filters.level}
        disabled={!app.level.enabled}
        disabledReason={app.level.reason}
        onChange={(level) => patch({ level })}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <StatRangeControl
          label="ATK"
          value={filters.atk}
          disabled={!app.atk.enabled}
          disabledReason={app.atk.reason}
          min={0}
          max={5000}
          onChange={(atk) => patch({ atk })}
        />
        <StatRangeControl
          label="DEF"
          value={filters.def}
          disabled={!app.def.enabled}
          disabledReason={app.def.reason}
          min={0}
          max={5000}
          onChange={(def) => patch({ def })}
        />
      </div>

      {app.scale.enabled && (
        <StatRangeControl
          label="Pendulum Scale"
          value={filters.scale}
          disabled={!app.scale.enabled}
          disabledReason={app.scale.reason}
          min={0}
          max={13}
          onChange={(scale) => patch({ scale })}
        />
      )}

      {app.linkval.enabled && (
        <StatRangeControl
          label="Link Rating"
          value={filters.linkval}
          disabled={!app.linkval.enabled}
          disabledReason={app.linkval.reason}
          min={1}
          max={8}
          onChange={(linkval) => patch({ linkval })}
        />
      )}

      {app.linkmarkers.enabled && options && (
        <div>
          <p className={filterSectionLabel}>Link markers</p>
          <div className={chipWrap}>
            {options.linkmarkers.map((m) => {
              const active = filters.linkmarkers?.includes(m);
              return (
                <button
                  key={m}
                  type="button"
                  onClick={() =>
                    patch({ linkmarkers: toggleInList(filters.linkmarkers, m) })
                  }
                  className={filterChipCompactClass(!!active)}
                >
                  {m}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {app.races.enabled && options && (
        <div>
          <p className={filterSectionLabel}>Race (Monster)</p>
          <select
            className={filterInputClass}
            value=""
            onChange={(e) => {
              if (!e.target.value) return;
              patch({ races: toggleInList(filters.races, e.target.value) });
            }}
          >
            <option value="">+ Thêm race</option>
            {options.monster_races.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
          {filters.races && filters.races.length > 0 && (
            <p className="mt-2 text-sm text-zinc-500">{filters.races.join(", ")}</p>
          )}
        </div>
      )}

      {app.spell_races.enabled && options && (
        <div>
          <p className={filterSectionLabel}>Loại Spell</p>
          <div className={chipWrap}>
            {options.spell_races.map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => patch({ spell_races: toggleInList(filters.spell_races, r) })}
                className={filterChipClass(!!filters.spell_races?.includes(r))}
              >
                {r}
              </button>
            ))}
          </div>
        </div>
      )}

      {app.trap_races.enabled && options && (
        <div>
          <p className={filterSectionLabel}>Loại Trap</p>
          <div className={chipWrap}>
            {options.trap_races.map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => patch({ trap_races: toggleInList(filters.trap_races, r) })}
                className={filterChipClass(!!filters.trap_races?.includes(r))}
              >
                {r}
              </button>
            ))}
          </div>
        </div>
      )}

      <div>
        <p className={filterSectionLabel}>Archetype</p>
        <input
          type="text"
          list={archetypeListId}
          value={filters.archetype ?? ""}
          onChange={(e) => patch({ archetype: e.target.value })}
          placeholder="Blue-Eyes..."
          className={filterInputClass}
        />
        {options && (
          <datalist id={archetypeListId}>
            {options.archetypes_sample.map((a) => (
              <option key={a} value={a} />
            ))}
          </datalist>
        )}
      </div>

      {options && (
        <div>
          <p className={filterSectionLabel}>Banlist TCG</p>
          <div className={chipWrap}>
            {options.banlist_tcg_values.map((b) => (
              <button
                key={b}
                type="button"
                onClick={() =>
                  patch({ banlist_tcg: toggleInList(filters.banlist_tcg, b) })
                }
                className={filterChipClass(!!filters.banlist_tcg?.includes(b))}
              >
                {b}
              </button>
            ))}
          </div>
        </div>
      )}

      <div>
        <p className={filterSectionLabel}>Sắp xếp</p>
        <div className="flex flex-col gap-3 sm:flex-row">
          <select
            className={filterSelectClass}
            value={filters.sort ?? "name"}
            onChange={(e) =>
              patch({ sort: e.target.value as CardSearchFilters["sort"] })
            }
          >
            <option value="name">Tên</option>
            <option value="atk">ATK</option>
            <option value="def">DEF</option>
            <option value="level">Level</option>
            <option value="linkval">Link</option>
            <option value="passcode">Passcode</option>
          </select>
          <select
            className={`${filterSelectClass} sm:max-w-[10rem]`}
            value={filters.order ?? "asc"}
            onChange={(e) =>
              patch({ order: e.target.value as CardSearchFilters["order"] })
            }
          >
            <option value="asc">Tăng</option>
            <option value="desc">Giảm</option>
          </select>
        </div>
      </div>
    </div>
  );
}
