import { useEffect, useState } from "react";
import {
  listCctv,
  createCctv,
  deleteCctv,
  updateCctvStatus,
} from "../services/cctv.service";

export default function CamerasPage() {
  const [cams, setCams] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState("");
  const [link, setLink] = useState("");
  const [lokasi, setLokasi] = useState("");

  const fetch = async () => {
    setLoading(true);
    try {
      const res = await listCctv();
      setCams(res || []);
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
    if (!name || !link) return;
    await createCctv({ nama: name, lokasi, link, aktif: true });
    setName("");
    setLink("");
    setLokasi("");
    fetch();
  };

  const handleDelete = async (id: number) => {
    await deleteCctv(id);
    fetch();
  };

  const handleToggle = async (id: number, aktif: boolean) => {
    await updateCctvStatus(id, !aktif);
    fetch();
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Kelola CCTV</h1>

      <div className="grid grid-cols-3 gap-3">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nama"
          className="p-2 border rounded"
        />
        <input
          value={lokasi}
          onChange={(e) => setLokasi(e.target.value)}
          placeholder="Lokasi"
          className="p-2 border rounded"
        />
        <input
          value={link}
          onChange={(e) => setLink(e.target.value)}
          placeholder="RTSP / URL"
          className="p-2 border rounded"
        />
      </div>
      <div>
        <button
          onClick={handleAdd}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Tambah CCTV
        </button>
      </div>

      {loading && <p>Memuat...</p>}

      <div className="space-y-3">
        {cams.map((c) => (
          <div
            key={c.id}
            className="p-3 bg-white border rounded flex items-center justify-between"
          >
            <div>
              <div className="font-semibold">{c.nama}</div>
              <div className="text-xs text-slate-600">
                {c.lokasi} • {c.link}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleToggle(c.id, c.aktif)}
                className="px-3 py-1 border rounded"
              >
                {c.aktif ? "Nonaktifkan" : "Aktifkan"}
              </button>
              <button
                onClick={() => handleDelete(c.id)}
                className="px-3 py-1 bg-red-600 text-white rounded"
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
