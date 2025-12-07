import { useState } from "react";
import CameraViewer from "../components/CameraViewer";

export default function LiveCameraPage() {
  const [detectionResult, setDetectionResult] = useState<any>(null);
  const [notifications, setNotifications] = useState<any[]>([]);

  const handleDetectionResult = (result: any) => {
    setDetectionResult(result);

    // Jika deteksi kotor, tambah ke notifikasi
    if (result.is_dirty) {
      setNotifications((prev) =>
        [
          {
            id: result.id,
            message: `🚨 Lantai KOTOR terdeteksi (${(
              result.confidence * 100
            ).toFixed(0)}%)`,
            timestamp: new Date().toLocaleTimeString("id-ID"),
            type: "dirty",
          },
          ...prev,
        ].slice(0, 10)
      );
    }
  };

  return (
    <div className="p-6 space-y-5">
      <h1 className="text-3xl font-bold">📹 Live Camera - Deteksi Real-time</h1>

      <div className="bg-blue-50 border border-blue-300 p-4 rounded-lg">
        <p className="text-sm text-blue-800">
          💡 <strong>Fitur Baru:</strong> Klik tombol "▶️ Auto-Deteksi" untuk
          menjalankan deteksi otomatis setiap 5 detik. Sistem akan secara
          otomatis memeriksa apakah lantai bersih atau kotor.
        </p>
      </div>

      <CameraViewer
        onResult={handleDetectionResult}
        autoDetectInterval={5000}
      />

      {/* Notifikasi Deteksi */}
      {notifications.length > 0 && (
        <div className="p-4 bg-yellow-50 border border-yellow-300 rounded-lg">
          <h3 className="font-bold mb-3 text-yellow-800">
            🔔 Notifikasi Deteksi
          </h3>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {notifications.map((notif, idx) => (
              <div
                key={idx}
                className="p-3 bg-white border-l-4 border-yellow-400 rounded shadow-sm"
              >
                <p className="font-semibold text-yellow-800">{notif.message}</p>
                <p className="text-xs text-gray-500 mt-1">{notif.timestamp}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Current Detection */}
      {detectionResult && (
        <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-purple-300 rounded-lg">
          <h3 className="font-bold mb-2">ℹ️ Status Deteksi Terakhir</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Status</p>
              <p className="font-bold text-lg">
                {detectionResult.is_dirty ? "🚨 KOTOR" : "✅ BERSIH"}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Confidence</p>
              <p className="font-bold text-lg">
                {(detectionResult.confidence * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="text-gray-600">Event ID</p>
              <p className="font-mono text-sm">{detectionResult.id}</p>
            </div>
            <div>
              <p className="text-gray-600">Waktu</p>
              <p className="text-xs">
                {new Date(detectionResult.created_at).toLocaleTimeString(
                  "id-ID"
                )}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
