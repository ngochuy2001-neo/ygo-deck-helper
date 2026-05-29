"use client";

interface CardSearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onPasscodeDetected?: (passcode: number) => void;
}

const PASSCODE_RE = /^\d{8}$/;

export function CardSearchBar({
  value,
  onChange,
  onPasscodeDetected,
}: CardSearchBarProps) {
  return (
    <input
      type="search"
      value={value}
      onChange={(e) => {
        const v = e.target.value;
        onChange(v);
        if (PASSCODE_RE.test(v.trim()) && onPasscodeDetected) {
          onPasscodeDetected(Number(v.trim()));
        }
      }}
      placeholder="Tìm tên hoặc passcode 8 chữ số..."
      autoComplete="off"
      className="w-full min-h-11 rounded-lg border border-zinc-300 bg-white px-3 py-2.5 text-base outline-none focus:border-zinc-500 focus:ring-2 focus:ring-zinc-200 dark:border-zinc-700 dark:bg-zinc-950 dark:focus:ring-zinc-800"
    />
  );
}
