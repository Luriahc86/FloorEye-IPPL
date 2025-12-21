/**
 * Detection Service - Frame detection API operations.
 * 
 * Backend endpoint:
 * - POST /detect/frame
 */
import api from "./api";

export interface DetectionResult {
  is_dirty: boolean;
  confidence: number;
  message?: string;
}

/**
 * Send camera frame for detection.
 * @param imageBase64 - Base64 encoded image
 * @param notes - Optional notes for the detection
 * @returns Detection result
 */
export async function detectFromCameraFrame(
  imageBase64: string,
  notes?: string
): Promise<DetectionResult> {
  const res = await api.post<DetectionResult>("/detect/frame", {
    image_base64: imageBase64,
    notes,
  });

  return res.data;
}

export default {
  detectFromCameraFrame,
};
