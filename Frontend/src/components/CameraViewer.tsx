import { useRef, useState, useEffect } from "react";

export default function CameraViewer({ onResult, autoDetectInterval = 5000 }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const detectIntervalRef = useRef(null);

  const [isActive, setIsActive] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [autoDetect, setAutoDetect] = useState(false);
  const [detectionHistory, setDetectionHistory] = useState([]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 },
      });

      streamRef.current = stream;
      videoRef.current.srcObject = stream;

      await videoRef.current.play();
      setIsActive(true);
    } catch (err) {
      console.error("Camera error:", err);
      setError("Tidak dapat mengakses kamera.");
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    videoRef.current.srcObject = null;
    setIsActive(false);
    setAutoDetect(false);

    // Stop auto-detect interval
    if (detectIntervalRef.current) {
      clearInterval(detectIntervalRef.current);
      detectIntervalRef.current = null;
    }
  };

  // Auto-detect effect
  useEffect(() => {
    if (autoDetect && isActive && !isDetecting) {
      const runDetection = async () => {
        try {
          setIsDetecting(true);
          const base64Frame = captureFrame();

          const response = await fetch("http://localhost:8000/detect/frame", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              image_base64: base64Frame,
              notes: "live-camera-auto-detect",
            }),
          });

          const data = await response.json();
          setResult(data);

          // Add to history
          setDetectionHistory((prev) =>
            [{ ...data, timestamp: new Date().toISOString() }, ...prev].slice(
              0,
              10
            )
          ); // Keep last 10

          if (onResult) onResult(data);
        } catch (err) {
          console.error("Auto-detect error:", err);
        } finally {
          setIsDetecting(false);
        }
      };

      detectIntervalRef.current = setInterval(runDetection, autoDetectInterval);

      return () => {
        if (detectIntervalRef.current) {
          clearInterval(detectIntervalRef.current);
        }
      };
    }
  }, [autoDetect, isActive, isDetecting, autoDetectInterval, onResult]);

  const captureFrame = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = 1280;
    canvas.height = 720;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL("image/jpeg", 0.95); // kualitas tinggi
  };

  const sendToDetectAPI = async () => {
    try {
      setIsDetecting(true);
      setError(null);

      const base64Frame = captureFrame();

      const response = await fetch("http://localhost:8000/detect/frame", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_base64: base64Frame,
          notes: "live-camera-frame",
        }),
      });

      const data = await response.json();
      setResult(data);

      if (onResult) onResult(data);
    } catch (err) {
      console.error(err);
      setError("Gagal mengirim frame ke backend.");
    } finally {
      setIsDetecting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-3 flex-wrap">
        {!isActive ? (
          <button
            onClick={startCamera}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Aktifkan Kamera
          </button>
        ) : (
          <>
            <button
              onClick={stopCamera}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Matikan Kamera
            </button>

            <button
              onClick={sendToDetectAPI}
              disabled={isDetecting}
              className="px-4 py-2 bg-green-600 text-white rounded-lg disabled:opacity-50 hover:bg-green-700"
            >
              {isDetecting ? "Mendeteksi..." : "Deteksi Sekarang"}
            </button>

            <button
              onClick={() => setAutoDetect(!autoDetect)}
              className={`px-4 py-2 rounded-lg text-white font-semibold transition ${
                autoDetect
                  ? "bg-orange-600 hover:bg-orange-700"
                  : "bg-purple-600 hover:bg-purple-700"
              }`}
            >
              {autoDetect ? "⏹️ Stop Auto-Deteksi" : "▶️ Auto-Deteksi"}
            </button>
          </>
        )}
      </div>

      {/* Status Live */}
      {result && isActive && (
        <div
          className={`p-4 rounded-lg border-2 text-center font-bold text-xl ${
            result.is_dirty
              ? "bg-red-100 border-red-500 text-red-700"
              : "bg-green-100 border-green-500 text-green-700"
          }`}
        >
          {result.is_dirty ? "🚨 KOTOR TERDETEKSI" : "✅ LANTAI BERSIH"}
          {autoDetect && (
            <p className="text-sm mt-1">⏱️ Auto-deteksi berjalan</p>
          )}
        </div>
      )}

      <video
        ref={videoRef}
        autoPlay
        playsInline
        className="w-full h-80 bg-gray-200 rounded-lg object-cover border-2 border-gray-300"
      ></video>

      <canvas ref={canvasRef} className="hidden"></canvas>

      {error && <p className="text-red-600 font-semibold">⚠️ {error}</p>}

      {/* Detection Result */}
      {result && (
        <div
          className={`p-4 rounded-lg border ${
            result.is_dirty
              ? "bg-red-50 border-red-300"
              : "bg-green-50 border-green-300"
          }`}
        >
          <h3 className="font-bold mb-2">
            {result.is_dirty
              ? "🚨 Hasil Deteksi: KOTOR"
              : "✅ Hasil Deteksi: BERSIH"}
          </h3>
          <div className="text-sm space-y-1 text-gray-700">
            <p>
              <strong>Confidence:</strong>{" "}
              {(result.confidence * 100).toFixed(1)}%
            </p>
            <p>
              <strong>ID Event:</strong> {result.id}
            </p>
            <p>
              <strong>Waktu:</strong>{" "}
              {new Date(result.created_at).toLocaleString("id-ID")}
            </p>
          </div>
        </div>
      )}

      {/* Detection History */}
      {detectionHistory.length > 0 && (
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-300">
          <h3 className="font-bold mb-3">📊 Riwayat Deteksi (10 Terakhir)</h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {detectionHistory.map((item, idx) => (
              <div
                key={idx}
                className={`p-2 rounded text-sm ${
                  item.is_dirty
                    ? "bg-red-100 text-red-800"
                    : "bg-green-100 text-green-800"
                }`}
              >
                <div className="flex justify-between">
                  <span className="font-semibold">
                    {item.is_dirty ? "🚨 KOTOR" : "✅ BERSIH"}
                  </span>
                  <span className="text-xs">
                    {(item.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="text-xs text-gray-600">
                  {new Date(item.timestamp).toLocaleTimeString("id-ID")}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
