import { useEffect, useState } from "react";
import {
  listEmailRecipients,
  createEmailRecipient,
  toggleEmailRecipient,
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
    await createEmailRecipient({ email, active: true });
    setEmail("");
    fetch();
  };

  const handleToggle = async (id: number, active: boolean) => {
    await toggleEmailRecipient(id, !active);
    fetch();
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Hapus email ini?")) return;
    await deleteEmailRecipient(id);
    fetch();
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
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Tambah
        </button>
      </div>

      {loading && <p>Memuat...</p>}

      <div className="space-y-2">
        {list.map((r) => (
          <div
            key={r.id}
            className="p-3 bg-white border rounded flex items-center justify-between"
          >
            <div>
              <div className="font-semibold">{r.email}</div>
              <div className="text-xs text-slate-600">
                {r.active ? "Aktif" : "Non-aktif"}
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => handleToggle(r.id, r.active)}
                className="px-3 py-1 border rounded"
              >
                {r.active ? "Matikan" : "Aktifkan"}
              </button>

              <button
                onClick={() => handleDelete(r.id)}
                className="px-3 py-1 border border-red-500 text-red-500 rounded"
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
