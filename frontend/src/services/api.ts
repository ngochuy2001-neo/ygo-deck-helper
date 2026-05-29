import type {
  AgentChatRequest,
  AgentChatResponse,
  CardStats,
  CardSyncJob,
  CardSyncRequest,
  HealthResponse,
  LMStudioModelsResponse,
  LMStudioSettings,
  LMStudioSettingsUpdate,
  LMStudioStatusResponse,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function fetchApi<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // giữ statusText nếu body không phải JSON
    }
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

/** Kiểm tra backend FastAPI có đang chạy không. */
export async function getHealth(): Promise<HealthResponse> {
  return fetchApi<HealthResponse>("/health");
}

/** Lấy cấu hình LM Studio hiện tại. */
export async function getLMStudioSettings(): Promise<LMStudioSettings> {
  return fetchApi<LMStudioSettings>("/api/v1/settings/lm-studio");
}

/** Cập nhật cấu hình LM Studio. */
export async function updateLMStudioSettings(
  payload: LMStudioSettingsUpdate,
): Promise<LMStudioSettings> {
  return fetchApi<LMStudioSettings>("/api/v1/settings/lm-studio", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

/** Kiểm tra trạng thái kết nối LM Studio. */
export async function getLMStudioStatus(): Promise<LMStudioStatusResponse> {
  return fetchApi<LMStudioStatusResponse>(
    "/api/v1/settings/lm-studio/status",
  );
}

/** Lấy danh sách model từ LM Studio. */
export async function getLMStudioModels(): Promise<LMStudioModelsResponse> {
  return fetchApi<LMStudioModelsResponse>(
    "/api/v1/settings/lm-studio/models",
  );
}

/** Gửi tin nhắn thử tới DeckHelper agent. */
export async function agentChat(
  payload: AgentChatRequest,
): Promise<AgentChatResponse> {
  return fetchApi<AgentChatResponse>("/api/v1/agent/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** Thống kê lá bài trong database. */
export async function getCardStats(): Promise<CardStats> {
  return fetchApi<CardStats>("/api/v1/cards/stats");
}

/** Bắt đầu đồng bộ lá bài từ YGOPRODeck. */
export async function startCardSync(
  payload: CardSyncRequest,
): Promise<CardSyncJob> {
  return fetchApi<CardSyncJob>("/api/v1/cards/sync", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** Lấy trạng thái job đồng bộ. */
export async function getCardSyncJob(jobId: number): Promise<CardSyncJob> {
  return fetchApi<CardSyncJob>(`/api/v1/cards/sync/${jobId}`);
}

/** Job đồng bộ gần nhất. */
export async function getLatestCardSync(): Promise<CardSyncJob | null> {
  return fetchApi<CardSyncJob | null>("/api/v1/cards/sync/latest");
}
