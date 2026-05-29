"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import {
  getCardStats,
  getCardSyncJob,
  getLatestCardSync,
  startCardSync,
} from "@/services/api";
import type { CardStats, CardSyncJob } from "@/types";

const POLL_MS = 2000;
const ACTIVE_STATUSES = new Set(["pending", "processing"]);
const TERMINAL_STATUSES = new Set(["completed", "failed", "skipped"]);

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("vi-VN");
}

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    pending: "Đang chờ",
    processing: "Đang đồng bộ",
    completed: "Hoàn tất",
    failed: "Thất bại",
    skipped: "Đã bỏ qua",
  };
  return map[status] ?? status;
}

function computeProgress(job: CardSyncJob): number {
  if (TERMINAL_STATUSES.has(job.status)) {
    return 100;
  }
  const total = job.total_expected ?? 0;
  if (total <= 0 || job.total_fetched <= 0) {
    return 0;
  }
  return Math.min(99, Math.round((job.total_fetched / total) * 100));
}

export function CardSyncPanel() {
  const [stats, setStats] = useState<CardStats | null>(null);
  const [job, setJob] = useState<CardSyncJob | null>(null);
  const [force, setForce] = useState(false);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadStats = useCallback(async () => {
    const data = await getCardStats();
    setStats(data);
  }, []);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const refreshJob = useCallback(
    async (jobId: number) => {
      const updated = await getCardSyncJob(jobId);
      setJob(updated);

      if (!ACTIVE_STATUSES.has(updated.status)) {
        stopPolling();
        setSyncing(false);
        await loadStats();
      }

      return updated;
    },
    [loadStats, stopPolling],
  );

  const startPolling = useCallback(
    (jobId: number) => {
      stopPolling();
      void refreshJob(jobId);
      pollRef.current = setInterval(() => {
        void refreshJob(jobId).catch((err: unknown) => {
          setError(err instanceof Error ? err.message : "Lỗi polling");
          setSyncing(false);
          stopPolling();
        });
      }, POLL_MS);
    },
    [refreshJob, stopPolling],
  );

  useEffect(() => {
    async function init() {
      setLoading(true);
      setError(null);
      try {
        await loadStats();
        const latest = await getLatestCardSync();
        if (latest) {
          setJob(latest);
          if (ACTIVE_STATUSES.has(latest.status)) {
            setSyncing(true);
            startPolling(latest.id);
          } else {
            setSyncing(false);
            stopPolling();
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Không tải được dữ liệu");
      } finally {
        setLoading(false);
      }
    }
    void init();
    return () => stopPolling();
  }, [loadStats, startPolling, stopPolling]);

  async function handleSync() {
    setSyncing(true);
    setError(null);
    try {
      const newJob = await startCardSync({ force });
      setJob(newJob);
      startPolling(newJob.id);
    } catch (err) {
      setSyncing(false);
      setError(err instanceof Error ? err.message : "Không khởi chạy được sync");
    }
  }

  const isProcessing = job != null && ACTIVE_STATUSES.has(job.status);
  const progressPercent = job ? computeProgress(job) : 0;
  const progressLabel =
    job && job.total_expected
      ? `${job.total_fetched.toLocaleString("vi-VN")} / ${job.total_expected.toLocaleString("vi-VN")} lá`
      : job && job.total_fetched > 0
        ? `${job.total_fetched.toLocaleString("vi-VN")} lá`
        : null;

  return (
    <section className="rounded-xl border border-zinc-200 p-5 dark:border-zinc-800">
      <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-zinc-500">
        Cơ sở dữ liệu lá bài
      </h2>
      <p className="mb-4 text-sm text-zinc-600 dark:text-zinc-400">
        Đồng bộ toàn bộ lá bài từ YGOPRODeck API v7 vào PostgreSQL (kèm tải ảnh).
      </p>

      {loading ? (
        <p className="text-sm text-zinc-500">Đang tải...</p>
      ) : (
        <>
          <div className="mb-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-900">
              <p className="text-xs text-zinc-500">Tổng lá trong DB</p>
              <p className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
                {stats?.total_cards.toLocaleString("vi-VN") ?? "—"}
              </p>
            </div>
            <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-900">
              <p className="text-xs text-zinc-500">Lần sync cuối</p>
              <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                {formatDate(stats?.last_sync_at ?? null)}
              </p>
            </div>
            <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-900">
              <p className="text-xs text-zinc-500">API DB version</p>
              <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                {stats?.api_db_version ?? "—"}
              </p>
            </div>
          </div>

          <label className="mb-4 flex items-center gap-2 text-sm text-zinc-700 dark:text-zinc-300">
            <input
              type="checkbox"
              checked={force}
              onChange={(e) => setForce(e.target.checked)}
              disabled={syncing}
              className="rounded border-zinc-300"
            />
            Bắt buộc sync lại (bỏ qua kiểm tra version)
          </label>

          <Button
            type="button"
            onClick={() => void handleSync()}
            disabled={syncing || stats?.sync_in_progress}
          >
            {syncing || stats?.sync_in_progress
              ? "Đang đồng bộ..."
              : "Đồng bộ lá bài từ YGOPRODeck"}
          </Button>

          {job && (
            <div className="mt-5 space-y-3 rounded-lg bg-zinc-50 p-4 dark:bg-zinc-900">
              <div className="flex items-center justify-between gap-2 text-sm">
                <span className="font-medium text-zinc-800 dark:text-zinc-200">
                  Job #{job.id} — {statusLabel(job.status)}
                </span>
                {isProcessing && progressLabel && (
                  <span className="shrink-0 text-zinc-500">
                    {progressLabel} ({progressPercent}%)
                  </span>
                )}
                {job.status === "completed" && (
                  <span className="shrink-0 text-emerald-600 dark:text-emerald-400">
                    100%
                  </span>
                )}
              </div>

              {isProcessing && (
                <div className="h-2 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800">
                  <div
                    className="h-full bg-zinc-900 transition-all duration-500 dark:bg-zinc-100"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              )}

              {job.status === "completed" && (
                <div className="h-2 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800">
                  <div className="h-full w-full bg-emerald-600 dark:bg-emerald-500" />
                </div>
              )}

              <dl className="grid grid-cols-2 gap-2 text-xs text-zinc-600 dark:text-zinc-400 sm:grid-cols-4">
                <div>
                  <dt>Đã xử lý</dt>
                  <dd className="font-medium text-zinc-900 dark:text-zinc-100">
                    {job.total_fetched.toLocaleString("vi-VN")}
                    {job.total_expected
                      ? ` / ${job.total_expected.toLocaleString("vi-VN")}`
                      : ""}
                  </dd>
                </div>
                <div>
                  <dt>Thêm mới</dt>
                  <dd className="font-medium text-zinc-900 dark:text-zinc-100">
                    {job.inserted.toLocaleString("vi-VN")}
                  </dd>
                </div>
                <div>
                  <dt>Cập nhật</dt>
                  <dd className="font-medium text-zinc-900 dark:text-zinc-100">
                    {job.updated.toLocaleString("vi-VN")}
                  </dd>
                </div>
                <div>
                  <dt>Ảnh tải</dt>
                  <dd className="font-medium text-zinc-900 dark:text-zinc-100">
                    {job.images_downloaded.toLocaleString("vi-VN")}
                  </dd>
                </div>
              </dl>

              {job.errors_count > 0 && (
                <p className="text-xs text-amber-700 dark:text-amber-400">
                  Lỗi: {job.errors_count} lá
                </p>
              )}

              {job.error_message && (
                <p className="text-xs text-zinc-600 dark:text-zinc-400">
                  {job.error_message}
                </p>
              )}
            </div>
          )}
        </>
      )}

      {error && (
        <p className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          {error}
        </p>
      )}
    </section>
  );
}
