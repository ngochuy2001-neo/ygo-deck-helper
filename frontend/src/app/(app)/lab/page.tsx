import { LabExperimentPanel } from "@/components/lab/LabExperimentPanel";

export default function LabPage() {
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="shrink-0 border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Thử nghiệm
        </h1>
        <p className="mt-0.5 text-sm text-zinc-500">
          AgentScope + Rulebook RAG +{" "}
          <span className="font-mono text-xs">google/gemma-4-e4b</span> trên LM
          Studio.
        </p>
      </div>
      <LabExperimentPanel />
    </div>
  );
}
