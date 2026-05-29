import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="flex flex-1 flex-col px-6 py-12">
      <main className="mx-auto w-full max-w-3xl">
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
            Dashboard
          </h1>
          <div className="flex gap-4 text-sm">
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
        <p className="text-zinc-600 dark:text-zinc-400">
          Giao diện chính sau khi đăng nhập — sẽ được bổ sung deck builder và
          agent monitor ở các bước tiếp theo.
        </p>
      </main>
    </div>
  );
}
