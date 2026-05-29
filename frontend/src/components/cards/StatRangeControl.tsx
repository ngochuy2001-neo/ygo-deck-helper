"use client";

import { filterInputClass, filterSectionLabel } from "@/components/cards/filterChipStyles";
import type { StatRange } from "@/types/cardSearch";

interface StatRangeControlProps {
  label: string;
  value?: StatRange | null;
  disabled?: boolean;
  disabledReason?: string;
  min?: number;
  max?: number;
  onChange: (value: StatRange | null) => void;
}

function RangeInput({
  placeholder,
  value,
  min,
  max,
  onChange,
}: {
  placeholder: string;
  value?: number | null;
  min: number;
  max: number;
  onChange: (v: number | undefined) => void;
}) {
  if (max - min > 20) {
    return (
      <input
        type="number"
        min={min}
        max={max}
        placeholder={placeholder}
        value={value ?? ""}
        onChange={(e) => {
          const v = e.target.value;
          onChange(v === "" ? undefined : Number(v));
        }}
        className={filterInputClass}
      />
    );
  }
  return (
    <select
      className={filterInputClass}
      value={value ?? ""}
      onChange={(e) => {
        const v = e.target.value;
        onChange(v === "" ? undefined : Number(v));
      }}
    >
      <option value="">{placeholder}</option>
      {Array.from({ length: max - min + 1 }, (_, i) => min + i).map((n) => (
        <option key={`${placeholder}-${n}`} value={n}>
          {n}
        </option>
      ))}
    </select>
  );
}

export function StatRangeControl({
  label,
  value,
  disabled,
  disabledReason,
  min = 0,
  max = 12,
  onChange,
}: StatRangeControlProps) {
  const update = (nextMin?: number, nextMax?: number) => {
    if (nextMin == null && nextMax == null) onChange(null);
    else onChange({ min: nextMin, max: nextMax });
  };

  return (
    <fieldset
      className="space-y-2"
      disabled={disabled}
      title={disabled ? disabledReason : undefined}
    >
      <legend className={filterSectionLabel}>{label}</legend>
      <div className="flex items-center gap-3">
        <RangeInput
          placeholder="Min"
          value={value?.min}
          min={min}
          max={max}
          onChange={(nextMin) => update(nextMin, value?.max ?? undefined)}
        />
        <span className="shrink-0 text-sm text-zinc-400">–</span>
        <RangeInput
          placeholder="Max"
          value={value?.max}
          min={min}
          max={max}
          onChange={(nextMax) => update(value?.min ?? undefined, nextMax)}
        />
      </div>
    </fieldset>
  );
}
