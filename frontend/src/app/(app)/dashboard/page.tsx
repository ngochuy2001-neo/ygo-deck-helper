import { CardSyncPanel } from "@/components/card-sync/CardSyncPanel";

export default function DashboardPage() {
  return (
    <div className="flex-1 overflow-y-auto px-6 py-8">
      <main className="mx-auto w-full max-w-3xl space-y-8">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
            Dashboard
          </h1>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Đồng bộ dữ liệu lá bài từ YGOPRODeck và quản lý thư viện.
          </p>
        </div>

        <CardSyncPanel />
      </main>
    </div>
  );
}
