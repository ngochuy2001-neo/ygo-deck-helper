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
  const loadGenRef = useRef(0);

  const apiFilters = useMemo(() => {
    const merged: CardSearchFilters = {
      ...filters,
      q: debouncedQ || undefined,
    };
    return sanitizeFilters(merged);
  }, [filters, debouncedQ]);

  const apiFiltersKey = useMemo(() => JSON.stringify(apiFilters), [apiFilters]);

  const setFilters = useCallback((updater: CardSearchFilters | ((prev: CardSearchFilters) => CardSearchFilters)) => {
    setFiltersState((prev) => {
      const next = typeof updater === "function" ? updater(prev) : updater;
      return sanitizeFilters(next);
    });
  }, []);

  const resetFilters = useCallback(() => {
    setFiltersState(DEFAULT_CARD_SEARCH_FILTERS);
  }, []);

  useEffect(() => {
    void getCardFilterOptions()
      .then(setFilterOptions)
      .catch(() => setFilterOptions(null));
  }, []);

  const fetchPage = useCallback(
    async (reset: boolean) => {
      const gen = ++loadGenRef.current;
      const offset = reset ? 0 : offsetRef.current;

      if (reset) {
        setListLoading(true);
        setListError(null);
      } else {
        setLoadingMore(true);
      }

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
        setItems((prev) => (reset ? data.items : [...prev, ...data.items]));
      } catch (err) {
        if (gen !== loadGenRef.current) return;
        setListError(err instanceof Error ? err.message : "Không tải được danh sách");
      } finally {
        if (gen === loadGenRef.current) {
          setListLoading(false);
          setLoadingMore(false);
        }
      }
    },
    [apiFiltersKey],
  );

  useEffect(() => {
    offsetRef.current = 0;
    void fetchPage(true);
  }, [fetchPage]);

  const loadMore = useCallback(() => {
    if (hasMore && !listLoading && !loadingMore) {
      void fetchPage(false);
    }
  }, [fetchPage, hasMore, listLoading, loadingMore]);

  return {
    filters,
    setFilters,
    resetFilters,
    filterOptions,
    apiFilters,
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
