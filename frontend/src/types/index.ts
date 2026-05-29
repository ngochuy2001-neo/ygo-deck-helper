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

export interface CardListItem {
  passcode: number;
  name: string;
  type: string;
  atk?: number | null;
  def?: number | null;
  level?: number | null;
  attribute?: string | null;
  race?: string | null;
  image_small_path?: string | null;
}

export interface CardListResponse {
  items: CardListItem[];
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

export interface CardImageDto {
  image_passcode: number;
  image_path?: string | null;
  image_small_path?: string | null;
  image_cropped_path?: string | null;
  is_default: boolean;
}

export interface CardSetDto {
  set_name: string;
  set_code?: string | null;
  set_rarity?: string | null;
  set_price?: string | null;
}

export interface CardPriceDto {
  cardmarket_price?: string | null;
  tcgplayer_price?: string | null;
  ebay_price?: string | null;
  amazon_price?: string | null;
  coolstuffinc_price?: string | null;
}

export interface CardDetail {
  passcode: number;
  name: string;
  type: string;
  frame_type?: string | null;
  desc?: string | null;
  atk?: number | null;
  def?: number | null;
  level?: number | null;
  race?: string | null;
  attribute?: string | null;
  scale?: number | null;
  linkval?: number | null;
  linkmarkers?: string[] | null;
  archetype?: string | null;
  ygoprodeck_url?: string | null;
  banlist_info?: Record<string, string> | null;
  synced_at?: string | null;
  image_path?: string | null;
  image_small_path?: string | null;
  images: CardImageDto[];
  card_sets: CardSetDto[];
  prices?: CardPriceDto | null;
}
