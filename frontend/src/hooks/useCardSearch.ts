"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { sanitizeFilters } from "@/lib/ygo/cardFilterRules";
import { getCardFilterOptions, listCards } from "@/services/api";
import type { CardListItem } from "@/types";
import {
  DEFAULT_CARD_SEARCH_FILTERS,
  type CardFilterOptions,
  type CardSearchFilters,
} from "@/types/cardSearch";

const PAGE_SIZE = 48;
const TEXT_DEBOUNCE_MS = 300;

function dedupeByPasscode(cards: CardListItem[]): CardListItem[] {
  const seen = new Set<number>();
  return cards.filter((card) => {
    if (seen.has(card.passcode)) return false;
    seen.add(card.passcode);
    return true;
  });
}

function mergeCardPages(prev: CardListItem[], next: CardListItem[]): CardListItem[] {
  return dedupeByPasscode([...prev, ...next]);
}

export function useCardSearch() {
  const [filters, setFiltersState] = useState<CardSearchFilters>(
    DEFAULT_CARD_SEARCH_FILTERS,
  );
  const [filterOptions, setFilterOptions] = useState<CardFilterOptions | null>(
    null,
  );

  const debouncedQ = useDebouncedValue(filters.q ?? "", TEXT_DEBOUNCE_MS);

  const [items, setItems] = useState<CardListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [listLoading, setListLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [listError, setListError] = useState<string | null>(null);

  const offsetRef = useRef(0);
  /** Tăng khi bộ lọc/API params đổi — hủy fetch cũ (kể cả loadMore). */
  const loadGenRef = useRef(0);

  const apiFilters = useMemo(() => {
    const merged: CardSearchFilters = {
      ...filters,
      q: debouncedQ.trim() ? debouncedQ.trim() : undefined,
    };
    return sanitizeFilters(merged);
  }, [filters, debouncedQ]);

  const apiFiltersKey = useMemo(() => JSON.stringify(apiFilters), [apiFilters]);

  const isSearchPending =
    (filters.q ?? "").trim() !== debouncedQ.trim();

  const setFilters = useCallback(
    (updater: CardSearchFilters | ((prev: CardSearchFilters) => CardSearchFilters)) => {
      setFiltersState((prev) => {
        const next = typeof updater === "function" ? updater(prev) : updater;
        return sanitizeFilters(next);
      });
    },
    [],
  );

  const resetFilters = useCallback(() => {
    setFiltersState(DEFAULT_CARD_SEARCH_FILTERS);
  }, []);

  useEffect(() => {
    void getCardFilterOptions()
      .then(setFilterOptions)
      .catch(() => setFilterOptions(null));
  }, []);

  /** Tải lại từ đầu khi bộ lọc API thay đổi. */
  useEffect(() => {
    const gen = ++loadGenRef.current;
    offsetRef.current = 0;
    setItems([]);
    setHasMore(false);
    setListLoading(true);
    setLoadingMore(false);
    setListError(null);

    void (async () => {
      try {
        const parsed = JSON.parse(apiFiltersKey) as CardSearchFilters;
        const data = await listCards({
          ...parsed,
          offset: 0,
          limit: PAGE_SIZE,
        });

        if (gen !== loadGenRef.current) return;

        setTotal(data.total);
        setHasMore(data.has_more);
        offsetRef.current = data.items.length;
        setItems(dedupeByPasscode(data.items));
      } catch (err) {
        if (gen !== loadGenRef.current) return;
        setListError(
          err instanceof Error ? err.message : "Không tải được danh sách",
        );
      } finally {
        if (gen === loadGenRef.current) {
          setListLoading(false);
          setLoadingMore(false);
        }
      }
    })();
  }, [apiFiltersKey]);

  const loadMore = useCallback(() => {
    if (!hasMore || listLoading || loadingMore || offsetRef.current <= 0) {
      return;
    }

    const gen = loadGenRef.current;
    const offset = offsetRef.current;
    setLoadingMore(true);

    void (async () => {
      try {
        const parsed = JSON.parse(apiFiltersKey) as CardSearchFilters;
        const data = await listCards({
          ...parsed,
          offset,
          limit: PAGE_SIZE,
        });

        if (gen !== loadGenRef.current) return;

        setTotal(data.total);
        setHasMore(data.has_more);
        offsetRef.current = offset + data.items.length;
        setItems((prev) => mergeCardPages(prev, data.items));
      } catch (err) {
        if (gen !== loadGenRef.current) return;
        setListError(
          err instanceof Error ? err.message : "Không tải được danh sách",
        );
      } finally {
        if (gen === loadGenRef.current) {
          setLoadingMore(false);
        }
      }
    })();
  }, [apiFiltersKey, hasMore, listLoading, loadingMore]);

  return {
    filters,
    setFilters,
    resetFilters,
    filterOptions,
    apiFilters,
    isSearchPending,
    items,
    setItems,
    total,
    hasMore,
    listLoading,
    loadingMore,
    listError,
    loadMore,
    pageSize: PAGE_SIZE,
  };
}
