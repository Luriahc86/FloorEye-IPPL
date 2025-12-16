import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function listCameras() {
  const res = await axios.get(`${API_BASE}/cameras`);
  return res.data;
}

export async function createCamera(payload: {
  nama: string;
  lokasi?: string;
  link: string;
  aktif?: boolean;
}) {
  const res = await axios.post(`${API_BASE}/cameras`, payload);
  return res.data;
}

export async function deleteCamera(id: number) {
  const res = await axios.delete(`${API_BASE}/cameras/${id}`);
  return res.data;
}

export async function updateCameraStatus(id: number, aktif: boolean) {
  const res = await axios.patch(`${API_BASE}/cameras/${id}`, { aktif });
  return res.data;
}

export default {
  listCameras,
  createCamera,
  deleteCamera,
  updateCameraStatus,
};
