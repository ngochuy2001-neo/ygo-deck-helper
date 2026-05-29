"use client";

import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import {
  agentChat,
  getLMStudioModels,
  getLMStudioSettings,
  getLMStudioStatus,
  updateLMStudioSettings,
} from "@/services/api";
import type { LMStudioModelInfo, LMStudioStatusResponse } from "@/types";

export default function SettingsPage() {
  const [host, setHost] = useState("127.0.0.1");
  const [port, setPort] = useState("1234");
  const [modelName, setModelName] = useState("");
  const [apiKey, setApiKey] = useState("lm-studio");
  const [models, setModels] = useState<LMStudioModelInfo[]>([]);
  const [status, setStatus] = useState<LMStudioStatusResponse | null>(null);
  const [testMessage, setTestMessage] = useState(
    "Giới thiệu ngắn về vai trò của bạn.",
  );
  const [testReply, setTestReply] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSettings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const settings = await getLMStudioSettings();
      setHost(settings.host);
      setPort(String(settings.port));
      setModelName(settings.model_name);
      setApiKey(settings.api_key);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không tải được cấu hình");
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshConnection = useCallback(async () => {
    setRefreshing(true);
    setError(null);
    try {
      const [statusResult, modelsResult] = await Promise.all([
        getLMStudioStatus(),
        getLMStudioModels().catch(() => ({ models: [] as LMStudioModelInfo[] })),
      ]);
      setStatus(statusResult);
      setModels(modelsResult.models);
    } catch (err) {
      setStatus(null);
      setModels([]);
      setError(err instanceof Error ? err.message : "Không kiểm tra được kết nối");
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void loadSettings();
  }, [loadSettings]);

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      const portNumber = Number(port);
      if (!Number.isInteger(portNumber) || portNumber < 1 || portNumber > 65535) {
        throw new Error("Port phải là số nguyên từ 1 đến 65535");
      }

      await updateLMStudioSettings({
        host: host.trim(),
        port: portNumber,
        model_name: modelName,
        api_key: apiKey.trim() || "lm-studio",
      });
      await refreshConnection();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lưu cấu hình thất bại");
    } finally {
      setSaving(false);
    }
  }

  async function handleTestAgent() {
    setTesting(true);
    setError(null);
    setTestReply("");
    try {
      const result = await agentChat({ message: testMessage.trim() });
      setTestReply(result.reply);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Thử agent thất bại");
    } finally {
      setTesting(false);
    }
  }

  const statusColor = status?.connected ? "bg-emerald-500" : "bg-red-500";

  return (
    <div className="flex-1 overflow-y-auto px-6 py-8">
      <main className="mx-auto w-full max-w-2xl">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
            Cài đặt — LM Studio
          </h1>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            Cấu hình kết nối LM Studio cho AgentScope DeckHelper agent.
          </p>
        </div>

        {loading ? (
          <p className="text-zinc-500">Đang tải cấu hình...</p>
        ) : (
          <div className="flex flex-col gap-6">
            <section className="rounded-xl border border-zinc-200 p-5 dark:border-zinc-800">
              <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-zinc-500">
                Kết nối
              </h2>
              <div className="grid gap-4 sm:grid-cols-2">
                <Input
                  label="Host / IP"
                  name="host"
                  value={host}
                  onChange={(e) => setHost(e.target.value)}
                  placeholder="127.0.0.1"
                />
                <Input
                  label="Port"
                  name="port"
                  type="number"
                  min={1}
                  max={65535}
                  value={port}
                  onChange={(e) => setPort(e.target.value)}
                  placeholder="1234"
                />
              </div>
              <div className="mt-4">
                <Input
                  label="API Key"
                  name="apiKey"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="lm-studio"
                />
              </div>
            </section>

            <section className="rounded-xl border border-zinc-200 p-5 dark:border-zinc-800">
              <div className="mb-4 flex items-center justify-between gap-3">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500">
                  Model
                </h2>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => void refreshConnection()}
                  disabled={refreshing}
                >
                  {refreshing ? "Đang kiểm tra..." : "Kiểm tra kết nối"}
                </Button>
              </div>

              {status && (
                <div className="mb-4 flex items-start gap-3 rounded-lg bg-zinc-50 p-3 dark:bg-zinc-900">
                  <span
                    className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${statusColor}`}
                  />
                  <div>
                    <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                      {status.connected ? "Đã kết nối" : "Chưa kết nối"}
                    </p>
                    <p className="mt-0.5 text-sm text-zinc-600 dark:text-zinc-400">
                      {status.message}
                    </p>
                    <p className="mt-1 text-xs text-zinc-500">
                      {status.base_url} · {status.models_count} model
                    </p>
                  </div>
                </div>
              )}

              <label htmlFor="model" className="flex flex-col gap-1.5">
                <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  Chọn model
                </span>
                <select
                  id="model"
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-500 focus:ring-2 focus:ring-zinc-200 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 dark:focus:ring-zinc-800"
                >
                  <option value="">— Chưa chọn —</option>
                  {models.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.name ?? model.id}
                    </option>
                  ))}
                </select>
              </label>
              {models.length === 0 && (
                <p className="mt-2 text-xs text-zinc-500">
                  Nhấn &quot;Kiểm tra kết nối&quot; sau khi bật LM Studio server để tải danh sách
                  model.
                </p>
              )}
            </section>

            <div className="flex gap-3">
              <Button type="button" onClick={() => void handleSave()} disabled={saving}>
                {saving ? "Đang lưu..." : "Lưu cấu hình"}
              </Button>
            </div>

            <section className="rounded-xl border border-zinc-200 p-5 dark:border-zinc-800">
              <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-zinc-500">
                Thử agent
              </h2>
              <label htmlFor="testMessage" className="flex flex-col gap-1.5">
                <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  Tin nhắn
                </span>
                <textarea
                  id="testMessage"
                  rows={3}
                  value={testMessage}
                  onChange={(e) => setTestMessage(e.target.value)}
                  className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-500 focus:ring-2 focus:ring-zinc-200 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 dark:focus:ring-zinc-800"
                />
              </label>
              <div className="mt-4">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => void handleTestAgent()}
                  disabled={testing || !modelName}
                >
                  {testing ? "Agent đang suy nghĩ..." : "Gửi thử"}
                </Button>
              </div>
              {testReply && (
                <div className="mt-4 rounded-lg bg-zinc-50 p-4 text-sm leading-relaxed text-zinc-800 dark:bg-zinc-900 dark:text-zinc-200">
                  {testReply}
                </div>
              )}
            </section>

            {error && (
              <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
                {error}
              </p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
