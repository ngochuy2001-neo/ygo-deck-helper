"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { LabMarkdownMessage } from "@/components/lab/LabMarkdownMessage";
import { Button } from "@/components/ui/Button";
import { getLabInfo, labChat } from "@/services/api";
import type { LabInfoResponse, LabRagHitBrief, QueryAnalysisBrief } from "@/types";

interface ChatTurn {
  role: "user" | "assistant";
  content: string;
  ragHits?: LabRagHitBrief[];
  queryAnalysis?: QueryAnalysisBrief | null;
  ragScope?: string;
  modelName?: string;
}

const EXAMPLE_PROMPTS = [
  "Quick Effect khác Ignition Effect thế nào? Dùng được lúc nào?",
  "Chữ trước dấu hai chấm (:) và chấm phẩy (;) trên lá bài nghĩa là gì?",
  "Lá bài bị Tribute có được coi là bị Destroy không?",
  "Synchro Summon cần những điều kiện gì về Level?",
] as const;

export function LabExperimentPanel() {
  const [info, setInfo] = useState<LabInfoResponse | null>(null);
  const [input, setInput] = useState("");
  const [useRag, setUseRag] = useState(true);
  const [useQueryAnalyzer, setUseQueryAnalyzer] = useState(true);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingInfo, setLoadingInfo] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const refreshInfo = useCallback(async () => {
    setLoadingInfo(true);
    try {
      const data = await getLabInfo();
      setInfo(data);
    } catch (err: unknown) {
      setInfo(null);
      setError(err instanceof Error ? err.message : "Không tải trạng thái lab");
    } finally {
      setLoadingInfo(false);
    }
  }, []);

  useEffect(() => {
    void refreshInfo();
  }, [refreshInfo]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [turns, loading]);

  const sendMessage = async (text: string) => {
    const message = text.trim();
    if (!message || loading) return;

    setLoading(true);
    setError(null);
    setTurns((prev) => [...prev, { role: "user", content: message }]);

    try {
      const result = await labChat({
        message,
        use_rag: useRag,
        use_query_analyzer: useQueryAnalyzer,
        rag_limit: 3,
      });
      setTurns((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.reply,
          ragHits: result.rag_hits,
          queryAnalysis: result.query_analysis,
          ragScope: result.rag_scope,
          modelName: result.model_name,
        },
      ]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Lab chat thất bại");
      setTurns((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const statusOk = info?.lm_studio_connected && info?.rag_ready;

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 p-4 sm:p-6">
      <section className="shrink-0 rounded-xl border border-amber-200/80 bg-amber-50/80 p-4 dark:border-amber-900/50 dark:bg-amber-950/20">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-amber-900 dark:text-amber-200">
              Rulebook Lab (thử nghiệm)
            </h2>
            <p className="mt-1 text-sm text-amber-800/90 dark:text-amber-300/90">
              AgentScope ReAct · Chat{" "}
              <code className="text-xs">{info?.chat_model ?? "google/gemma-4-e4b"}</code> ·
              RAG{" "}
              <code className="text-xs">
                {info?.embedding_model ?? "text-embedding-embeddinggamma-300m-qat"}
              </code>
            </p>
          </div>
          <Button
            type="button"
            variant="secondary"
            className="shrink-0"
            onClick={() => void refreshInfo()}
            disabled={loadingInfo}
          >
            {loadingInfo ? "…" : "Làm mới"}
          </Button>
        </div>

        {info && (
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
            <span
              className={`rounded-full px-2 py-0.5 font-medium ${
                info.lm_studio_connected
                  ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300"
                  : "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300"
              }`}
            >
              LM Studio {info.lm_studio_connected ? "OK" : "OFF"}
            </span>
            <span
              className={`rounded-full px-2 py-0.5 font-medium ${
                info.rag_ready
                  ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300"
                  : "bg-zinc-200 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
              }`}
            >
              RAG {info.rag_chunks_in_db} chunk
            </span>
            <span className="text-zinc-600 dark:text-zinc-400">{info.message}</span>
          </div>
        )}

        {!loadingInfo && !statusOk && (
          <p className="mt-2 text-xs text-amber-700 dark:text-amber-400">
            Cần LM Studio (load Gemma) + Rulebook đã ingest. Host/port lấy từ Settings.
          </p>
        )}
      </section>

      <div
        ref={scrollRef}
        className="flex min-h-[240px] flex-1 flex-col gap-3 overflow-y-auto rounded-xl border border-zinc-200 bg-zinc-50/50 p-4 dark:border-zinc-800 dark:bg-zinc-900/30"
      >
        {turns.length === 0 && (
          <p className="text-center text-sm text-zinc-500">
            Hỏi về luật YGO — agent sẽ dùng Rulebook RAG và có thể tra DB lá bài.
          </p>
        )}

        {turns.map((turn, index) => (
          <div
            key={`${turn.role}-${index}`}
            className={`flex flex-col gap-2 ${
              turn.role === "user" ? "items-end" : "items-start"
            }`}
          >
            <div
              className={`max-w-[92%] rounded-2xl px-4 py-2.5 ${
                turn.role === "user"
                  ? "bg-zinc-800 text-zinc-50"
                  : "border border-zinc-200 bg-white text-zinc-800 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-200"
              }`}
            >
              <LabMarkdownMessage
                content={turn.content}
                variant={turn.role === "user" ? "user" : "assistant"}
              />
            </div>

            {turn.role === "assistant" &&
              turn.content.toLowerCase().includes("waiting for tool calls") && (
                <p className="max-w-[92%] text-xs text-amber-700 dark:text-amber-400">
                  Agent dừng sớm — hãy restart backend. Nếu vẫn lỗi, thử gửi lại câu hỏi.
                </p>
              )}

            {turn.role === "assistant" && turn.queryAnalysis && (
              <details className="max-w-[92%] rounded-lg border border-sky-200 bg-sky-50/80 px-3 py-2 dark:border-sky-900/50 dark:bg-sky-950/30">
                <summary className="cursor-pointer text-xs font-medium text-sky-800 dark:text-sky-300">
                  Phân tích câu hỏi (QueryAnalyzer)
                </summary>
                <div className="mt-2 space-y-1 text-xs text-sky-900/90 dark:text-sky-200/90">
                  <p>
                    <span className="font-medium">Ý định:</span> {turn.queryAnalysis.intent}
                    {turn.ragScope && (
                      <>
                        {" "}
                        · <span className="font-medium">RAG:</span> {turn.ragScope}
                      </>
                    )}
                  </p>
                  <p>
                    <span className="font-medium">Câu chuẩn hóa:</span>{" "}
                    {turn.queryAnalysis.clarified_question}
                  </p>
                  {turn.queryAnalysis.rag_search_queries.length > 0 && (
                    <p>
                      <span className="font-medium">Truy vấn RAG:</span>{" "}
                      {turn.queryAnalysis.rag_search_queries.join(" · ")}
                    </p>
                  )}
                  {turn.queryAnalysis.answer_focus && (
                    <p>
                      <span className="font-medium">Trọng tâm:</span>{" "}
                      {turn.queryAnalysis.answer_focus}
                    </p>
                  )}
                </div>
              </details>
            )}

            {turn.role === "assistant" && turn.ragHits && turn.ragHits.length > 0 && (
              <details className="max-w-[92%] rounded-lg border border-violet-200 bg-violet-50/80 px-3 py-2 dark:border-violet-900/50 dark:bg-violet-950/30">
                <summary className="cursor-pointer text-xs font-medium text-violet-800 dark:text-violet-300">
                  Nguồn RAG ({turn.ragHits.length} chunk) — tham khảo
                </summary>
                <ul className="mt-2 space-y-2">
                  {turn.ragHits.map((hit) => (
                    <li key={hit.chunk_id} className="text-xs text-violet-900/90 dark:text-violet-200/90">
                      <span className="font-medium">{hit.title}</span>
                      <span className="text-violet-600 dark:text-violet-400">
                        {" "}
                        · {hit.chunk_id} · d={hit.distance.toFixed(3)}
                      </span>
                      <p className="mt-1 line-clamp-3 text-violet-800/80 dark:text-violet-300/80">
                        {hit.excerpt}
                      </p>
                    </li>
                  ))}
                </ul>
              </details>
            )}

            {turn.role === "assistant" && turn.modelName && (
              <span className="text-[10px] text-zinc-400">model: {turn.modelName}</span>
            )}
          </div>
        ))}

        {loading && (
          <p className="text-sm text-zinc-500 animate-pulse">
            QueryAnalyzer + RAG + Rulebook Lab…
          </p>
        )}
      </div>

      <section className="shrink-0 space-y-3">
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              disabled={loading}
              onClick={() => {
                setInput(prompt);
                void sendMessage(prompt);
              }}
              className="rounded-full border border-zinc-200 bg-white px-3 py-1 text-xs text-zinc-600 transition hover:border-zinc-400 hover:text-zinc-900 disabled:opacity-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
            >
              {prompt.length > 48 ? `${prompt.slice(0, 48)}…` : prompt}
            </button>
          ))}
        </div>

        <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
          <label className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400">
            <input
              type="checkbox"
              checked={useQueryAnalyzer}
              onChange={(e) => setUseQueryAnalyzer(e.target.checked)}
              className="rounded border-zinc-300"
            />
            QueryAnalyzer (chuẩn hóa câu hỏi trước)
          </label>
          <label className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400">
            <input
              type="checkbox"
              checked={useRag}
              onChange={(e) => setUseRag(e.target.checked)}
              className="rounded border-zinc-300"
            />
            Prefetch Rulebook RAG (hiển thị context)
          </label>
        </div>

        <div className="flex gap-2">
          <textarea
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Hỏi về luật, timing effect, Synchro…"
            className="min-h-[44px] flex-1 resize-none rounded-xl border border-zinc-300 bg-white px-3 py-2 text-sm outline-none focus:border-zinc-500 focus:ring-2 focus:ring-zinc-200 dark:border-zinc-700 dark:bg-zinc-950 dark:focus:ring-zinc-800"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void sendMessage(input);
                setInput("");
              }
            }}
          />
          <Button
            type="button"
            disabled={loading || !input.trim()}
            onClick={() => {
              void sendMessage(input);
              setInput("");
            }}
          >
            Gửi
          </Button>
        </div>

        {error && (
          <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
            {error}
          </p>
        )}
      </section>
    </div>
  );
}
