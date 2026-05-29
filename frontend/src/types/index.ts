export interface HealthResponse {
  status: string;
  database?: string;
}

export interface LMStudioSettings {
  host: string;
  port: number;
  model_name: string;
  api_key: string;
}

export interface LMStudioSettingsUpdate {
  host?: string;
  port?: number;
  model_name?: string;
  api_key?: string;
}

export interface LMStudioModelInfo {
  id: string;
  name?: string | null;
}

export interface LMStudioModelsResponse {
  models: LMStudioModelInfo[];
}

export interface LMStudioStatusResponse {
  connected: boolean;
  base_url: string;
  model_name: string;
  message: string;
  models_count: number;
}

export interface AgentChatRequest {
  message: string;
}

export interface AgentChatResponse {
  reply: string;
  model_name: string;
}

export interface CardSyncRequest {
  force: boolean;
}

export interface CardSyncJob {
  id: number;
  status: string;
  force: boolean;
  api_db_version_before: string | null;
  api_db_version_after: string | null;
  total_expected: number | null;
  total_fetched: number;
  inserted: number;
  updated: number;
  images_downloaded: number;
  errors_count: number;
  error_message: string | null;
  started_at: string;
  finished_at: string | null;
}

export interface CardStats {
  total_cards: number;
  last_sync_at: string | null;
  api_db_version: string | null;
  sync_in_progress: boolean;
}
