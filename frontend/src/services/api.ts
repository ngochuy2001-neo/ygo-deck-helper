import type {
  AgentChatRequest,
  AgentChatResponse,
  CardDetail,
  CardListResponse,
  CardStats,
  CardSyncJob,
  CardSyncRequest,
  HealthResponse,
  LMStudioModelsResponse,
  LMStudioSettings,
  LMStudioSettingsUpdate,
  LMStudioStatusResponse,
} from "@/types";
import type { CardFilterOptions, CardSearchFilters, StatRange } from "@/types/cardSearch";

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

function appendStatRange(
  search: URLSearchParams,
  prefix: string,
  range?: StatRange | null,
): void {
  if (!range) return;
  if (range.min != null) search.set(`${prefix}_min`, String(range.min));
  if (range.max != null) search.set(`${prefix}_max`, String(range.max));
}

function appendList(search: URLSearchParams, key: string, values?: string[]): void {
  if (values && values.length > 0) search.set(key, values.join(","));
}

/** Metadata bộ lọc (distinct values). */
export async function getCardFilterOptions(): Promise<CardFilterOptions> {
  return fetchApi<CardFilterOptions>("/api/v1/cards/filter-options");
}

/** Danh sách lá bài (phân trang + tìm kiếm + bộ lọc YGO). */
export async function listCards(
  filters: CardSearchFilters & { offset?: number; limit?: number },
): Promise<CardListResponse> {
  const search = new URLSearchParams();
  if (filters.passcode) {
    search.set("passcode", String(filters.passcode));
  } else {
    if (filters.q?.trim()) search.set("q", filters.q.trim());
    if (filters.card_group && filters.card_group !== "all") {
      search.set("card_group", filters.card_group);
    }
    appendList(search, "frame_types", filters.frame_types);
    appendList(search, "attributes", filters.attributes);
    appendList(search, "races", filters.races);
    appendList(search, "spell_races", filters.spell_races);
    appendList(search, "trap_races", filters.trap_races);
    appendStatRange(search, "level", filters.level);
    appendStatRange(search, "atk", filters.atk);
    appendStatRange(search, "def", filters.def);
    appendStatRange(search, "scale", filters.scale);
    appendStatRange(search, "linkval", filters.linkval);
    appendList(search, "linkmarkers", filters.linkmarkers);
    if (filters.archetype?.trim()) search.set("archetype", filters.archetype.trim());
    appendList(search, "banlist_tcg", filters.banlist_tcg);
  }
  if (filters.sort) search.set("sort", filters.sort);
  if (filters.order) search.set("order", filters.order);
  search.set("offset", String(filters.offset ?? 0));
  search.set("limit", String(filters.limit ?? 40));
  return fetchApi<CardListResponse>(`/api/v1/cards?${search.toString()}`);
}

/** Chi tiết một lá bài. */
export async function getCardDetail(passcode: number): Promise<CardDetail> {
  return fetchApi<CardDetail>(`/api/v1/cards/${passcode}`);
}
