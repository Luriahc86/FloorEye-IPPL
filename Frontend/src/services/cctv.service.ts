import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export async function listCctv() {
  const res = await axios.get(`${API_BASE}/cctv`);
  return res.data;
}

export async function createCctv(payload: {
  nama: string;
  lokasi?: string;
  link: string;
  aktif?: boolean;
}) {
  const res = await axios.post(`${API_BASE}/cctv`, payload);
  return res.data;
}

export async function deleteCctv(id: number) {
  const res = await axios.delete(`${API_BASE}/cctv/${id}`);
  return res.data;
}

export async function updateCctvStatus(id: number, aktif: boolean) {
  const res = await axios.patch(`${API_BASE}/cctv/${id}`, { aktif });
  return res.data;
}

export default { listCctv, createCctv, deleteCctv, updateCctvStatus };
