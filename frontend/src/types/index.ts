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
