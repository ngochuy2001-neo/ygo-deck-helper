"use client";

import { useEffect, useRef, useState } from "react";

import { CardFilterChips } from "@/components/cards/CardFilterChips";
import { CardFilterModal } from "@/components/cards/CardFilterModal";
import { CardImageModal } from "@/components/cards/CardImageModal";
import { clearModalFilters, countActiveModalFilters } from "@/lib/ygo/cardFilterUtils";
import { CardSearchBar } from "@/components/cards/CardSearchBar";
import { useCardSearch } from "@/hooks/useCardSearch";
import { cardStaticUrl } from "@/lib/cardImages";
import { getCardDetail } from "@/services/api";
import type { CardDetail } from "@/types";
function statLine(label: string, value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") return null;
  return (
    <div className="flex justify-between gap-4 text-sm">
      <dt className="text-zinc-500">{label}</dt>
      <dd className="font-medium text-zinc-900 dark:text-zinc-100">{value}</dd>
    </div>
  );
}

export function CardBrowser() {
  const {
    filters,
    setFilters,
    filterOptions,
    items,
    total,
    listLoading,
    loadingMore,
    listError,
    loadMore,
    hasMore,
    isSearchPending,
  } = useCardSearch();

  const [selectedPasscode, setSelectedPasscode] = useState<number | null>(null);
  const [detail, setDetail] = useState<CardDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [imageModalOpen, setImageModalOpen] = useState(false);
  const [filterModalOpen, setFilterModalOpen] = useState(false);

  const activeFilterCount = countActiveModalFilters(filters);

  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const searchValue = filters.passcode
    ? String(filters.passcode)
    : (filters.q ?? "");

  useEffect(() => {
    if (listLoading) return;
    if (items.length > 0) {
      setSelectedPasscode((current) => {
        if (current && items.some((c) => c.passcode === current)) return current;
        return items[0].passcode;
      });
    } else {
      setSelectedPasscode(null);
      setDetail(null);
    }
  }, [items, listLoading]);

  useEffect(() => {
    setImageModalOpen(false);
  }, [selectedPasscode]);

  useEffect(() => {
    if (!selectedPasscode) {
      setDetail(null);
      return;
    }

    let cancelled = false;
    setDetailLoading(true);

    void getCardDetail(selectedPasscode)
      .then((data) => {
        if (!cancelled) setDetail(data);
      })
      .catch(() => {
        if (!cancelled) setDetail(null);
      })
      .finally(() => {
        if (!cancelled) setDetailLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedPasscode]);

  useEffect(() => {
    const el = sentinelRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) loadMore();
      },
      { root: el.parentElement, rootMargin: "200px", threshold: 0 },
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [loadMore]);

  const defaultImg =
    detail?.images.find((i) => i.is_default) ?? detail?.images[0];
  const fullImageUrl = cardStaticUrl(
    detail?.image_path ?? defaultImg?.image_path ?? detail?.image_small_path,
  );
  const croppedArtworkUrl = cardStaticUrl(defaultImg?.image_cropped_path);

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex shrink-0 items-center justify-between border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Thư viện lá bài
        </h1>
        <span className="text-sm text-zinc-500">
          {total.toLocaleString("vi-VN")} lá
        </span>
      </div>

      <div className="flex min-h-0 flex-1 divide-x divide-zinc-200 dark:divide-zinc-800">
        <aside className="flex w-1/2 min-w-0 flex-col">
          <div className="flex gap-2 border-b border-zinc-200 p-3 dark:border-zinc-800">
            <div className="min-w-0 flex-1">
              <CardSearchBar
                value={searchValue}
                onChange={(v) => {
                  setFilters((prev) => ({
                    ...prev,
                    q: v,
                    passcode: null,
                  }));
                }}
                onPasscodeDetected={(passcode) => {
                  setFilters((prev) => ({
                    ...prev,
                    passcode,
                    q: undefined,
                  }));
                }}
              />
            </div>
            <button
              type="button"
              onClick={() => setFilterModalOpen(true)}
              className="relative flex min-h-11 shrink-0 items-center justify-center rounded-lg border border-zinc-300 px-4 text-base font-medium text-zinc-800 touch-manipulation hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-200 dark:hover:bg-zinc-900"
            >
              Bộ lọc
              {activeFilterCount > 0 && (
                <span className="absolute -right-1.5 -top-1.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-zinc-900 px-1 text-xs font-bold text-white dark:bg-zinc-100 dark:text-zinc-900">
                  {activeFilterCount > 9 ? "9+" : activeFilterCount}
                </span>
              )}
            </button>
          </div>

          <CardFilterModal
            open={filterModalOpen}
            appliedFilters={filters}
            options={filterOptions}
            onClose={() => setFilterModalOpen(false)}
            onApply={(next) => setFilters(next)}
          />

          <CardFilterChips
            filters={filters}
            onRemove={(patch) => setFilters((prev) => ({ ...prev, ...patch }))}
            onClearAll={() => setFilters((prev) => clearModalFilters(prev))}
          />

          <div className="min-h-0 flex-1 overflow-y-auto p-3">
            {listError && (
              <p className="mb-3 text-sm text-red-600 dark:text-red-400">{listError}</p>
            )}

            {(listLoading || isSearchPending) && items.length === 0 ? (
              <p className="text-center text-sm text-zinc-500">Đang tải...</p>
            ) : items.length === 0 && !listLoading && !isSearchPending ? (
              <p className="text-center text-sm text-zinc-500">
                Không có lá bài phù hợp. Thử đổi bộ lọc hoặc đồng bộ từ Dashboard.
              </p>
            ) : (
              <div className="relative">
                {(listLoading || isSearchPending) && items.length > 0 && (
                  <div className="pointer-events-none absolute inset-0 z-10 bg-white/50 dark:bg-zinc-950/50" />
                )}
              <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 lg:grid-cols-5">
                {items.map((card) => {
                  const thumb = cardStaticUrl(card.image_small_path);
                  const selected = card.passcode === selectedPasscode;
                  return (
                    <button
                      key={card.passcode}
                      type="button"
                      onClick={() => setSelectedPasscode(card.passcode)}
                      className={`flex flex-col overflow-hidden rounded-lg border text-left transition-colors ${
                        selected
                          ? "border-zinc-900 ring-2 ring-zinc-900 dark:border-zinc-100 dark:ring-zinc-100"
                          : "border-zinc-200 hover:border-zinc-400 dark:border-zinc-800 dark:hover:border-zinc-600"
                      }`}
                    >
                      <div className="relative aspect-[3/4] w-full bg-zinc-100 dark:bg-zinc-900">
                        {thumb ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={thumb}
                            alt={card.name}
                            loading="lazy"
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          <div className="flex h-full items-center justify-center text-xs text-zinc-400">
                            No img
                          </div>
                        )}
                      </div>
                      <p className="line-clamp-2 px-1.5 py-1 text-[10px] leading-tight font-medium text-zinc-800 dark:text-zinc-200">
                        {card.name}
                      </p>
                    </button>
                  );
                })}
              </div>
              </div>
            )}

            <div ref={sentinelRef} className="h-8" />
            {loadingMore && (
              <p className="py-2 text-center text-xs text-zinc-500">Đang tải thêm...</p>
            )}
            {!listLoading && hasMore && items.length > 0 && !loadingMore && (
              <p className="py-1 text-center text-[10px] text-zinc-400">Cuộn để tải thêm</p>
            )}
          </div>
        </aside>

        <section className="flex w-1/2 min-w-0 flex-col overflow-y-auto p-6">
          {!selectedPasscode ? (
            <p className="text-sm text-zinc-500">Chọn một lá bài để xem chi tiết.</p>
          ) : detailLoading ? (
            <p className="text-sm text-zinc-500">Đang tải chi tiết...</p>
          ) : !detail ? (
            <p className="text-sm text-zinc-500">Không tải được thông tin lá bài.</p>
          ) : (
            <div className="mx-auto flex w-full max-w-md flex-col gap-6">
              <button
                type="button"
                onClick={() => setImageModalOpen(true)}
                disabled={!croppedArtworkUrl}
                className="group w-full overflow-hidden rounded-xl border border-zinc-200 bg-zinc-50 text-left transition hover:border-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-400 disabled:cursor-default disabled:opacity-60 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-600 dark:focus:ring-zinc-600"
                title="Nhấn để xem artwork"
              >
                {fullImageUrl ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={fullImageUrl}
                    alt={detail.name}
                    className="mx-auto max-h-[420px] w-auto object-contain transition group-hover:scale-[1.02]"
                  />
                ) : (
                  <div className="flex h-64 items-center justify-center text-zinc-400">
                    Chưa có ảnh full
                  </div>
                )}
                {croppedArtworkUrl && (
                  <p className="border-t border-zinc-200 py-2 text-center text-xs text-zinc-500 group-hover:text-zinc-700 dark:border-zinc-800 dark:group-hover:text-zinc-300">
                    Nhấn để xem artwork
                  </p>
                )}
              </button>

              {imageModalOpen && (
                <CardImageModal
                  detail={detail}
                  open={imageModalOpen}
                  onClose={() => setImageModalOpen(false)}
                />
              )}

              <div>
                <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">
                  {detail.name}
                </h2>
                <p className="mt-1 text-sm text-zinc-500">
                  {detail.type}
                  {detail.archetype ? ` · ${detail.archetype}` : ""}
                </p>
                <p className="mt-0.5 font-mono text-xs text-zinc-400">
                  #{detail.passcode}
                </p>
              </div>

              <dl className="space-y-2 rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
                {statLine("ATK", detail.atk)}
                {statLine("DEF", detail.def)}
                {statLine("Level/Rank", detail.level)}
                {statLine("Attribute", detail.attribute)}
                {statLine("Race/Type", detail.race)}
                {statLine("Scale", detail.scale)}
                {statLine("Link", detail.linkval)}
                {detail.linkmarkers && detail.linkmarkers.length > 0 && (
                  <div className="flex justify-between gap-4 text-sm">
                    <dt className="text-zinc-500">Link markers</dt>
                    <dd className="text-right font-medium text-zinc-900 dark:text-zinc-100">
                      {detail.linkmarkers.join(", ")}
                    </dd>
                  </div>
                )}
              </dl>

              {detail.desc && (
                <div>
                  <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-zinc-500">
                    Hiệu ứng
                  </h3>
                  <p className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
                    {detail.desc}
                  </p>
                </div>
              )}

              {detail.banlist_info && Object.keys(detail.banlist_info).length > 0 && (
                <div>
                  <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-zinc-500">
                    Banlist
                  </h3>
                  <ul className="space-y-1 text-sm text-zinc-700 dark:text-zinc-300">
                    {Object.entries(detail.banlist_info).map(([key, val]) => (
                      <li key={key}>
                        <span className="font-medium">{key}:</span> {val}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {detail.card_sets.length > 0 && (
                <div>
                  <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-zinc-500">
                    Bộ bài ({detail.card_sets.length})
                  </h3>
                  <ul className="max-h-40 space-y-1 overflow-y-auto text-xs text-zinc-600 dark:text-zinc-400">
                    {detail.card_sets.slice(0, 20).map((s, i) => (
                      <li key={`${s.set_code}-${i}`}>
                        {s.set_name}
                        {s.set_code ? ` (${s.set_code})` : ""}
                        {s.set_rarity ? ` — ${s.set_rarity}` : ""}
                      </li>
                    ))}
                    {detail.card_sets.length > 20 && (
                      <li className="text-zinc-400">
                        +{detail.card_sets.length - 20} bộ khác...
                      </li>
                    )}
                  </ul>
                </div>
              )}

              {detail.ygoprodeck_url && (
                <a
                  href={detail.ygoprodeck_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-zinc-600 underline hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  Xem trên YGOPRODeck →
                </a>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
