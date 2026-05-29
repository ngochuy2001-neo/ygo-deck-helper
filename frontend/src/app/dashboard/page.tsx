import Link from "next/link";

import { CardSyncPanel } from "@/components/card-sync/CardSyncPanel";

export default function DashboardPage() {
  return (
    <div className="flex flex-1 flex-col px-6 py-12">
      <main className="mx-auto w-full max-w-3xl space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
              Dashboard
            </h1>
            <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
              Quản lý dữ liệu lá bài và truy cập các công cụ khác.
            </p>
          </div>
          <div className="flex gap-4 text-sm">
            <Link
              href="/cards"
              className="text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
            >
              Thư viện lá bài
            </Link>
            <Link
              href="/settings"
              className="text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
            >
              Settings
            </Link>
            <Link
              href="/"
              className="text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
            >
              ← Trang chủ
            </Link>
          </div>
        </div>

        <CardSyncPanel />
      </main>
    </div>
  );
}
