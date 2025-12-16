import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function detectFromCameraFrame(
  imageBase64: string,
  notes?: string
) {
  const res = await axios.post(`${API_BASE}/detect/frame`, {
    image_base64: imageBase64,
    notes,
  });

  return res.data;
}
