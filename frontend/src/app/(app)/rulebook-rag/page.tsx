import { RulebookRagPanel } from "@/components/rulebook-rag/RulebookRagPanel";

export default function RulebookRagPage() {
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="shrink-0 border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Rulebook RAG
        </h1>
        <p className="mt-0.5 text-sm text-zinc-500">
          Upload SD Rulebook, cắt chunk theo tiêu đề ##, embed LM Studio và lưu
          PostgreSQL pgvector cho Agent.
        </p>
      </div>
      <RulebookRagPanel />
    </div>
  );
}
