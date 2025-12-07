import { useEffect, useState } from "react";
import {
  listCameras,
  createCamera,
  deleteCamera,
  updateCameraStatus,
} from "../services/camera.service";

export default function CamerasPage() {
  const [cameras, setCameras] = useState<any[]>([]);
  const [nama, setNama] = useState("");
  const [lokasi, setLokasi] = useState("");
  const [link, setLink] = useState("");
  const [loading, setLoading] = useState(false);

  const fetch = async () => {
    setLoading(true);
    try {
      const res = await listCameras();
      setCameras(res || []);
    } catch (e) {
      console.error(e);
      alert("Gagal memuat data kamera");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
  }, []);

  const handleAdd = async () => {
    if (!nama || !link) {
      alert("Nama dan link RTSP wajib diisi");
      return;
    }
    try {
      await createCamera({
        nama,
        lokasi,
        link,
        aktif: true,
      });
      setNama("");
      setLokasi("");
      setLink("");
      fetch();
    } catch (e) {
      console.error("Failed to add camera:", e);
      alert("Gagal menambah kamera");
    }
  };

  const handleToggle = async (id: number, aktif: boolean) => {
    try {
      await updateCameraStatus(id, !aktif);
      // Optimistic update: ubah state langsung tanpa refetch
      setCameras(
        cameras.map((cam) => (cam.id === id ? { ...cam, aktif: !aktif } : cam))
      );
    } catch (e) {
      console.error("Failed to toggle camera:", e);
      alert("Gagal mengubah status kamera");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Hapus kamera ini?")) return;
    try {
      await deleteCamera(id);
      // Optimistic update: hapus dari state langsung
      setCameras(cameras.filter((cam) => cam.id !== id));
    } catch (e) {
      console.error("Failed to delete camera:", e);
      alert("Gagal menghapus kamera");
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Kelola Kamera RTSP</h1>

      {/* Form Tambah Kamera */}
      <div className="bg-white border rounded p-4 space-y-3">
        <h2 className="font-semibold">Tambah Kamera Baru</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input
            value={nama}
            onChange={(e) => setNama(e.target.value)}
            placeholder="Nama kamera (mis: Ruang Tamu)"
            className="p-2 border rounded"
          />
          <input
            value={lokasi}
            onChange={(e) => setLokasi(e.target.value)}
            placeholder="Lokasi (opsional)"
            className="p-2 border rounded"
          />
        </div>
        <input
          value={link}
          onChange={(e) => setLink(e.target.value)}
          placeholder="RTSP URL (mis: rtsp://192.168.1.100:554/stream)"
          className="p-2 border rounded w-full"
        />
        <button
          onClick={handleAdd}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Tambah Kamera
        </button>
      </div>

      {loading && <p className="text-slate-500">Memuat...</p>}

      {cameras.length === 0 && !loading && (
        <p className="text-slate-500 text-center py-6">
          Belum ada kamera terdaftar
        </p>
      )}

      {/* Daftar Kamera */}
      <div className="space-y-3">
        {cameras.map((cam) => (
          <div
            key={cam.id}
            className={`p-4 border rounded ${
              cam.aktif ? "bg-blue-50 border-blue-300" : "bg-gray-50"
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="font-semibold text-lg">{cam.nama}</div>
                <div className="text-sm text-slate-600 mt-1">
                  📍 {cam.lokasi || "Lokasi tidak ditentukan"}
                </div>
                <div className="text-sm text-slate-600 mt-1 break-all">
                  🔗 {cam.link}
                </div>
                <div className="text-xs text-slate-500 mt-2">
                  {cam.aktif
                    ? "✅ Aktif - Kamera sedang dimonitor"
                    : "❌ Non-aktif"}
                </div>
              </div>

              <div className="flex gap-2 ml-4">
                <button
                  onClick={() => handleToggle(cam.id, cam.aktif)}
                  className={`px-4 py-2 rounded font-medium transition ${
                    cam.aktif
                      ? "bg-orange-500 text-white hover:bg-orange-600"
                      : "bg-green-500 text-white hover:bg-green-600"
                  }`}
                >
                  {cam.aktif ? "Matikan" : "Aktifkan"}
                </button>

                <button
                  onClick={() => handleDelete(cam.id)}
                  className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 font-medium"
                >
                  Hapus
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
