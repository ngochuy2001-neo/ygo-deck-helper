/** Class dùng chung cho chip/nút trong bộ lọc — đủ lớn để bấm trên màn hình cảm ứng. */

export const filterSectionLabel =
  "mb-2 text-sm font-semibold text-zinc-600 dark:text-zinc-400";

export const filterChipBase =
  "inline-flex min-h-11 items-center justify-center rounded-lg px-3.5 py-2 text-sm font-medium transition-colors touch-manipulation active:scale-[0.98]";

export function filterChipClass(active: boolean): string {
  return active
    ? `${filterChipBase} bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900`
    : `${filterChipBase} bg-zinc-100 text-zinc-800 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-100 dark:hover:bg-zinc-700`;
}

/** Chip nhỏ hơn một chút cho danh sách frame dài. */
export function filterChipCompactClass(active: boolean): string {
  const base =
    "inline-flex min-h-10 items-center justify-center rounded-lg px-3 py-2 text-sm font-medium transition-colors touch-manipulation active:scale-[0.98]";
  return active
    ? `${base} bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900`
    : `${base} bg-zinc-100 text-zinc-800 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-100 dark:hover:bg-zinc-700`;
}

export const filterInputClass =
  "w-full min-h-11 rounded-lg border border-zinc-300 bg-white px-3 py-2.5 text-base dark:border-zinc-700 dark:bg-zinc-950";

export const filterSelectClass =
  "min-h-11 flex-1 rounded-lg border border-zinc-300 bg-white px-3 py-2.5 text-base dark:border-zinc-700 dark:bg-zinc-950";
