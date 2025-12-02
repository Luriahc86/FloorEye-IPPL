import { useEffect, useState } from "react";
import {
  listWARecipients,
  createWARecipient,
  toggleWARecipient,
} from "../services/wa.service";

export default function NotificationsPage() {
  const [list, setList] = useState<any[]>([]);
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(false);

  const fetch = async () => {
    setLoading(true);
    try {
      const res = await listWARecipients();
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
    if (!phone) return;
    if (!phone.startsWith("62"))
      return alert("Nomor harus format internasional. Contoh: 6281234567890");

    await createWARecipient({ phone, active: true });
    setPhone("");
    fetch();
  };

  const handleToggle = async (id: number, active: boolean) => {
    await toggleWARecipient(id, !active);
    fetch();
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Notifikasi WhatsApp</h1>

      <div className="flex gap-3">
        <input
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="Contoh: 6281234567890"
          className="p-2 border rounded flex-1"
        />
        <button
          onClick={handleAdd}
          className="px-4 py-2 bg-green-600 text-white rounded"
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
              <div className="font-semibold">{r.phone}</div>
              <div className="text-xs text-slate-600">
                {r.active ? "Aktif" : "Non-aktif"}
              </div>
            </div>
            <div>
              <button
                onClick={() => handleToggle(r.id, r.active)}
                className="px-3 py-1 border rounded"
              >
                {r.active ? "Matikan" : "Aktifkan"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
