"use client";

import { useEffect, useState } from "react";

/** Trì hoãn giá trị để giảm số lần gọi API khi gõ tìm kiếm. */
export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}
