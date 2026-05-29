"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import {
  getRulebookRagStats,
  ingestRulebookChunks,
  previewRulebookChunks,
  searchRulebookRag,
} from "@/services/api";
import type {
  RulebookChunkPreview,
  RulebookRagStats,
  RulebookSearchHit,
} from "@/types";

const EMBEDDING_MODEL = "text-embedding-embeddinggamma-300m-qat";

export function RulebookRagPanel() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [previews, setPreviews] = useState<RulebookChunkPreview[]>([]);
  const [stats, setStats] = useState<RulebookRagStats | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchHits, setSearchHits] = useState<RulebookSearchHit[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadStats = useCallback(async () => {
    try {
      const data = await getRulebookRagStats();
      setStats(data);
    } catch {
      setStats(null);
    }
  }, []);

  useEffect(() => {
    void loadStats();
  }, [loadStats]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
    setPreviews([]);
    setError(null);
    setSuccess(null);
  };

  const handlePreview = async () => {
    if (!file) {
      setError("Chọn file .md trước.");
      return;
    }
    setLoadingPreview(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await previewRulebookChunks(file);
      setPreviews(result.chunks);
      setExpandedId(result.chunks[0]?.chunk_id ?? null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Lỗi xem trước chunk");
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleIngest = async () => {
    if (!file) {
      setError("Chọn file .md trước.");
      return;
    }
    setIngesting(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await ingestRulebookChunks(file);
      setPreviews(result.chunks);
      setSuccess(
        `Đã lưu ${result.chunks_ingested} chunk với model ${result.embedding_model}.`,
      );
      await loadStats();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Lỗi ingest RAG");
    } finally {
      setIngesting(false);
    }
  };

  const handleSearch = async () => {
    const q = searchQuery.trim();
    if (!q) return;
    if (!stats?.total_chunks) {
      setError("Chưa có chunk trong database — hãy ingest trước.");
      return;
    }
    setSearching(true);
    setError(null);
    try {
      const result = await searchRulebookRag(q, 4);
      setSearchHits(result.hits);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Lỗi tìm kiếm");
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto p-4 sm:p-6">
      <section className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
          Upload Rulebook
        </h2>
        <p className="mt-1 text-sm text-zinc-500">
          File mẫu: <code className="text-xs">SD_RuleBook_EN_10.md</code> — cắt
          theo từng tiêu đề ##, embed qua LM Studio (
          <code className="text-xs">{EMBEDDING_MODEL}</code>, 768d) và lưu
          pgvector.
        </p>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <input
            ref={fileInputRef}
            type="file"
            accept=".md,text/markdown"
            className="max-w-full text-sm text-zinc-600 file:mr-3 file:rounded-lg file:border-0 file:bg-zinc-100 file:px-3 file:py-2 file:text-sm file:font-medium dark:text-zinc-400 dark:file:bg-zinc-800"
            onChange={handleFileChange}
          />
          <Button
            type="button"
            variant="secondary"
            disabled={!file || loadingPreview}
            onClick={() => void handlePreview()}
          >
            {loadingPreview ? "Đang cắt…" : "Xem trước chunk"}
          </Button>
          <Button
            type="button"
            disabled={!file || ingesting}
            onClick={() => void handleIngest()}
          >
            {ingesting ? "Đang embed…" : "Ingest vào database"}
          </Button>
        </div>

        {file && (
          <p className="mt-2 text-xs text-zinc-500">
            Đã chọn: {file.name} ({(file.size / 1024).toFixed(1)} KB)
          </p>
        )}

        {error && (
          <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300">
            {error}
          </p>
        )}
        {success && (
          <p className="mt-3 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">
            {success}
          </p>
        )}
      </section>

      <section className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
          Trạng thái RAG
        </h2>
        <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-zinc-500">Số chunk</dt>
            <dd className="font-medium text-zinc-900 dark:text-zinc-100">
              {stats?.total_chunks ?? 0}
            </dd>
          </div>
          <div>
            <dt className="text-zinc-500">Model embedding</dt>
            <dd className="font-medium text-zinc-900 dark:text-zinc-100">
              {stats?.embedding_model ?? "—"}
            </dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-zinc-500">Chunk IDs</dt>
            <dd className="font-mono text-xs text-zinc-700 dark:text-zinc-300">
              {stats?.chunk_ids?.length
                ? stats.chunk_ids.join(", ")
                : "—"}
            </dd>
          </div>
        </dl>
      </section>

      {previews.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
            Preview ({previews.length} chunk)
          </h2>
          {previews.map((chunk) => {
            const open = expandedId === chunk.chunk_id;
            return (
              <article
                key={chunk.chunk_id}
                className="rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950"
              >
                <button
                  type="button"
                  className="flex w-full items-start justify-between gap-3 px-4 py-3 text-left"
                  onClick={() =>
                    setExpandedId(open ? null : chunk.chunk_id)
                  }
                >
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                      {chunk.title}
                    </h3>
                    <p className="mt-0.5 text-xs text-zinc-500">
                      {chunk.chunk_id} · {chunk.char_count.toLocaleString()} ký
                      tự
                    </p>
                    <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                      {chunk.description}
                    </p>
                  </div>
                  <span className="shrink-0 text-xs text-zinc-400">
                    {open ? "Thu gọn" : "Mở rộng"}
                  </span>
                </button>
                {open && (
                  <pre className="max-h-80 overflow-auto border-t border-zinc-100 bg-zinc-50 px-4 py-3 text-xs whitespace-pre-wrap text-zinc-800 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-200">
                    {chunk.content}
                  </pre>
                )}
              </article>
            );
          })}
        </section>
      )}

      <section className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
          Thử tìm kiếm semantic
        </h2>
        <div className="mt-3 flex flex-wrap gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="VD: Quick Effect dùng lúc nào?"
            className="min-w-[200px] flex-1 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            onKeyDown={(e) => {
              if (e.key === "Enter") void handleSearch();
            }}
          />
          <Button
            type="button"
            variant="secondary"
            disabled={searching || !searchQuery.trim()}
            onClick={() => void handleSearch()}
          >
            {searching ? "Đang tìm…" : "Tìm chunk"}
          </Button>
        </div>

        {searchHits.length > 0 && (
          <ul className="mt-4 space-y-3">
            {searchHits.map((hit) => (
              <li
                key={hit.chunk_id}
                className="rounded-lg border border-zinc-100 bg-zinc-50 p-3 dark:border-zinc-800 dark:bg-zinc-900"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
                    {hit.title}
                  </span>
                  <span className="text-xs text-zinc-500">
                    distance {hit.distance.toFixed(4)}
                  </span>
                </div>
                <p className="mt-2 line-clamp-4 text-xs text-zinc-600 dark:text-zinc-400">
                  {hit.content.slice(0, 400)}
                  {hit.content.length > 400 ? "…" : ""}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
