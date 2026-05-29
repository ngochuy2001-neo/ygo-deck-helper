"use client";

import { useEffect, useRef, useState } from "react";

import { CardFilterFields } from "@/components/cards/CardFilterFields";
import { sanitizeFilters } from "@/lib/ygo/cardFilterRules";
import { clearModalFilters, cloneFilters } from "@/lib/ygo/cardFilterUtils";
import type { CardFilterOptions, CardSearchFilters } from "@/types/cardSearch";

interface CardFilterModalProps {
  open: boolean;
  appliedFilters: CardSearchFilters;
  options: CardFilterOptions | null;
  onClose: () => void;
  onApply: (filters: CardSearchFilters) => void;
}

const actionBtn =
  "min-h-12 rounded-xl px-4 text-base font-medium touch-manipulation active:scale-[0.98]";

export function CardFilterModal({
  open,
  appliedFilters,
  options,
  onClose,
  onApply,
}: CardFilterModalProps) {
  const applyRef = useRef<HTMLButtonElement>(null);
  const [draft, setDraft] = useState<CardSearchFilters>(() =>
    cloneFilters(appliedFilters),
  );

  useEffect(() => {
    if (open) setDraft(cloneFilters(appliedFilters));
  }, [open, appliedFilters]);

  useEffect(() => {
    if (!open) return;

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", onKeyDown);
    applyRef.current?.focus();

    return () => {
      document.body.style.overflow = "";
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open, onClose]);

  const patchDraft = (partial: Partial<CardSearchFilters>) => {
    setDraft((prev) => sanitizeFilters({ ...prev, ...partial }));
  };

  const handleApply = () => {
    onApply(
      sanitizeFilters({
        ...draft,
        q: appliedFilters.q,
        passcode: appliedFilters.passcode,
      }),
    );
    onClose();
  };

  /** Chỉ reset draft trong modal; danh sách đổi khi bấm Áp dụng. */
  const handleClearAll = () => {
    setDraft(clearModalFilters(appliedFilters));
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-stretch justify-center p-0 sm:items-center sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby="card-filter-modal-title"
    >
      <button
        type="button"
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        aria-label="Đóng"
        onClick={onClose}
      />

      <div className="relative z-10 flex h-full w-full max-w-3xl flex-col overflow-hidden border-zinc-200 bg-white shadow-2xl sm:h-[min(90vh,880px)] sm:rounded-2xl sm:border dark:border-zinc-800 dark:bg-zinc-950">
        <div className="shrink-0 border-b border-zinc-200 px-5 py-4 sm:px-6 dark:border-zinc-800">
          <h2
            id="card-filter-modal-title"
            className="text-lg font-semibold text-zinc-900 dark:text-zinc-50"
          >
            Bộ lọc lá bài
          </h2>
          <p className="mt-1 text-sm text-zinc-500">
            Chọn tiêu chí rồi bấm Áp dụng
          </p>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-5 sm:px-6 sm:py-6">
          <CardFilterFields
            filters={draft}
            options={options}
            onChange={patchDraft}
          />
        </div>

        <div className="shrink-0 space-y-3 border-t border-zinc-200 bg-zinc-50 p-4 sm:px-6 dark:border-zinc-800 dark:bg-zinc-900">
          <button
            ref={applyRef}
            type="button"
            onClick={handleApply}
            className={`${actionBtn} w-full bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200`}
          >
            Áp dụng
          </button>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={onClose}
              className={`${actionBtn} border border-zinc-300 bg-white text-zinc-800 hover:bg-zinc-100 dark:border-zinc-600 dark:bg-zinc-950 dark:text-zinc-200 dark:hover:bg-zinc-800`}
            >
              Hủy
            </button>
            <button
              type="button"
              onClick={handleClearAll}
              className={`${actionBtn} text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/50`}
            >
              Xóa tất cả
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
