import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export async function listWARecipients() {
  const res = await axios.get(`${API_BASE}/wa-recipients`);
  return res.data;
}

export async function createWARecipient(payload: {
  phone: string;
  active?: boolean;
}) {
  const res = await axios.post(`${API_BASE}/wa-recipients`, payload);
  return res.data;
}

export async function toggleWARecipient(id: number, active: boolean) {
  const res = await axios.patch(`${API_BASE}/wa-recipients/${id}`, {
    active,
  });
  return res.data;
}

export default {
  listWARecipients,
  createWARecipient,
  toggleWARecipient,
};
