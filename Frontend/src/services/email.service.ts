import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface EmailRecipient {
  id: number;
  email: string;
  active: boolean;
}

/** Ambil daftar penerima email */
export async function listEmailRecipients(): Promise<EmailRecipient[]> {
  const res = await axios.get<EmailRecipient[]>(`${API_BASE}/email-recipients`);
  return res.data;
}

/** Tambah penerima email */
export async function createEmailRecipient(payload: {
  email: string;
  active?: boolean;
}): Promise<{ message: string }> {
  const res = await axios.post<{ message: string }>(
    `${API_BASE}/email-recipients`,
    payload
  );
  return res.data;
}

/** Aktif/nonaktifkan email: mengembalikan row penerima terbaru */
export async function toggleEmailRecipient(
  id: number,
  active: boolean
): Promise<EmailRecipient> {
  const res = await axios.patch<EmailRecipient>(
    `${API_BASE}/email-recipients/${id}`,
    {
      active,
    }
  );
  return res.data;
}

/** Hapus email */
export async function deleteEmailRecipient(
  id: number
): Promise<{ message: string }> {
  const res = await axios.delete<{ message: string }>(
    `${API_BASE}/email-recipients/${id}`
  );
  return res.data;
}

export default {
  listEmailRecipients,
  createEmailRecipient,
  toggleEmailRecipient,
  deleteEmailRecipient,
};
