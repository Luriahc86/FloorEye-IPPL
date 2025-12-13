import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

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
