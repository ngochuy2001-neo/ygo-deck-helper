const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** URL ảnh local đã sync (path dạng `{passcode}/{id}_small.jpg`). */
export function cardStaticUrl(localPath: string | null | undefined): string | null {
  if (!localPath) return null;
  return `${API_BASE_URL}/static/cards/${localPath}`;
}
