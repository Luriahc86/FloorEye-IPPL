import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

/** Ambil daftar penerima email */
export async function listEmailRecipients() {
  const res = await axios.get(`${API_BASE}/email-recipients`);
  return res.data;
}

/** Tambah penerima email */
export async function createEmailRecipient(payload: { 
  email: string; 
  active?: boolean; 
}) {
  const res = await axios.post(`${API_BASE}/email-recipients`, payload);
  return res.data;
}

/** Aktif/nonaktifkan email */
export async function toggleEmailRecipient(id: number, active: boolean) {
  const res = await axios.patch(`${API_BASE}/email-recipients/${id}`, {
    active,
  });
  return res.data;
}

/** Hapus email */
export async function deleteEmailRecipient(id: number) {
  const res = await axios.delete(`${API_BASE}/email-recipients/${id}`);
  return res.data;
}

export default {
  listEmailRecipients,
  createEmailRecipient,
  toggleEmailRecipient,
  deleteEmailRecipient,
};
