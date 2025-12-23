/**
 * History Service - Detection history API operations.
 * 
 * Backend endpoints:
 * - GET /history?limit=&offset=
 * - GET /history/{event_id}/image
 */
import api, { API_BASE } from "./api";

// Types matching backend HistoryItem model
export interface HistoryItem {
  id: number;
  source: string;
  is_dirty: boolean;
  confidence: number | null;
  notes: string | null;
  created_at: string;
}

export interface FetchHistoryParams {
  limit?: number;
  offset?: number;
}

/**
 * Fetch detection history with pagination.
 * @param params - Pagination parameters (limit, offset)
 * @returns Array of history items
 */
export async function fetchHistory(
  params: FetchHistoryParams = {}
): Promise<HistoryItem[]> {
  const { limit = 50, offset = 0 } = params;
  
  const res = await api.get<HistoryItem[]>("/history", {
    params: { limit, offset },
  });
  
  return res.data;
}

/**
 * Get image URL for a specific event.
 * Returns the full URL to fetch the image directly.
 * @param eventId - The event ID
 * @returns Full URL string for the image
 */
export function getImageUrl(eventId: number): string {
  return `${API_BASE}/history/${eventId}/image`;
}

/**
 * Fetch image blob for a specific event.
 * Use this when you need the actual image data (e.g., for canvas manipulation).
 * @param eventId - The event ID
 * @returns Blob of the image
 */
export async function fetchImageBlob(eventId: number): Promise<Blob> {
  const res = await api.get(`/history/${eventId}/image`, {
    responseType: "blob",
  });
  
  return res.data;
}

export default {
  fetchHistory,
  getImageUrl,
  fetchImageBlob,
};
