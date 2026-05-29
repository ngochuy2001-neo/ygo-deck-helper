"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/cards", label: "Thư viện lá bài" },
  { href: "/import-ydk", label: "Import YDK" },
  { href: "/rulebook-rag", label: "Rulebook RAG" },
  { href: "/lab", label: "Rulebook Lab" },
  { href: "/settings", label: "Cài đặt" },
] as const;

function navLinkClass(active: boolean): string {
  return active
    ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
    : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100";
}

export function AppNav() {
  const pathname = usePathname();

  return (
    <header className="shrink-0 border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
      <div className="mx-auto flex h-14 max-w-[1600px] items-center gap-6 px-4 sm:px-6">
        <Link
          href="/dashboard"
          className="shrink-0 text-base font-bold tracking-tight text-zinc-900 dark:text-zinc-50"
        >
          YGO Deck Helper
        </Link>

        <nav className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto">
          {NAV_ITEMS.map((item) => {
            const active =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(`${item.href}/`));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition-colors ${navLinkClass(active)}`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
