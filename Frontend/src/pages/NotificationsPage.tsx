import { useEffect, useState } from "react";
import {
  listEmailRecipients,
  createEmailRecipient,
  deleteEmailRecipient,
} from "../services/email.service";

export default function NotificationsPage() {
  const [list, setList] = useState<any[]>([]);
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const fetch = async () => {
    setLoading(true);
    try {
      const res = await listEmailRecipients();
      setList(res || []);
    } catch (e) {
      console.error(e);
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

      {list.length === 0 && !loading && (
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
            <div>
              <div className="font-semibold">{r.email}</div>
            </div>

            <button
              onClick={() => handleDelete(r.id)}
              className="px-3 py-1 border border-red-500 text-red-500 rounded hover:bg-red-50"
            >
              Hapus
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
