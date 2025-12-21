import { useEffect, useState } from "react";
import {
  listEmailRecipients,
  createEmailRecipient,
  deleteEmailRecipient,
  toggleEmailRecipient,
  type EmailRecipient,
} from "../services/email.service";

export default function NotificationsPage() {
  const [list, setList] = useState<EmailRecipient[]>([]);
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [togglingId, setTogglingId] = useState<number | null>(null);

  const fetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listEmailRecipients();
      // Ensure we always set an array
      setList(Array.isArray(res) ? res : []);
    } catch (e) {
      console.error(e);
      setError("Gagal memuat data. Pastikan backend sudah berjalan.");
      setList([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
  }, []);

  const handleAdd = async () => {
    if (!email) return;
    try {
      await createEmailRecipient({ email, active: true });
      setEmail("");
      fetch();
    } catch (e) {
      console.error("Failed to add email:", e);
      alert("Gagal menambah email");
    }
  };

  const handleToggle = async (id: number, active: boolean) => {
    try {
      setTogglingId(id);
      const updated = await toggleEmailRecipient(id, !active);
      // Update state berdasarkan row terbaru dari backend
      setList((prev) => prev.map((r) => (r.id === id ? updated : r)));
    } catch (e) {
      console.error("Failed to toggle:", e);
      alert("Gagal mengubah status");
    } finally {
      setTogglingId((current) => (current === id ? null : current));
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Hapus email ini?")) return;
    try {
      await deleteEmailRecipient(id);
      setList(list.filter((r) => r.id !== id));
    } catch (e) {
      console.error("Failed to delete:", e);
      alert("Gagal menghapus email");
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Notifikasi Email</h1>

      <div className="flex gap-3">
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="email@example.com"
          className="p-2 border rounded flex-1"
        />
        <button
          onClick={handleAdd}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Tambah
        </button>
      </div>

      {loading && <p>Memuat...</p>}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {list.length === 0 && !loading && !error && (
        <p className="text-slate-500 text-center py-6">
          Belum ada penerima email terdaftar
        </p>
      )}

      <div className="space-y-2">
        {list.map((r) => (
          <div
            key={r.id}
            className="p-3 bg-white border rounded flex items-center justify-between"
          >
            <div className="flex-1">
              <div className="font-semibold">{r.email}</div>
              <div className="mt-1">
                <span
                  className={
                    r.active
                      ? "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700"
                      : "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-200 text-gray-600"
                  }
                >
                  {r.active ? "Aktif" : "Non-aktif"}
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => handleToggle(r.id, r.active)}
                disabled={togglingId === r.id}
                className="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {r.active ? "Matikan" : "Aktifkan"}
              </button>

              <button
                onClick={() => handleDelete(r.id)}
                className="px-3 py-1 border border-red-500 text-red-500 rounded hover:bg-red-50"
              >
                Hapus
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
