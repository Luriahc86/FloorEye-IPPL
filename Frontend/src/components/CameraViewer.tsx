import { useRef, useState } from "react";

export default function CameraViewer({ onResult }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const [isActive, setIsActive] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

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
  };

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
      <div className="flex gap-3">
        {!isActive ? (
          <button
            onClick={startCamera}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            Aktifkan Kamera
          </button>
        ) : (
          <>
            <button
              onClick={stopCamera}
              className="px-4 py-2 bg-red-600 text-white rounded-lg"
            >
              Matikan Kamera
            </button>

            <button
              onClick={sendToDetectAPI}
              disabled={isDetecting}
              className="px-4 py-2 bg-green-600 text-white rounded-lg disabled:opacity-50"
            >
              {isDetecting ? "Mendeteksi..." : "Deteksi Sekarang"}
            </button>
          </>
        )}
      </div>

      <video
        ref={videoRef}
        autoPlay
        playsInline
        className="w-full h-80 bg-gray-200 rounded-lg object-cover"
      ></video>

      <canvas ref={canvasRef} className="hidden"></canvas>

      {error && <p className="text-red-600">{error}</p>}

      {result && (
        <div className="p-4 bg-gray-100 border rounded-lg">
          <h3 className="font-bold mb-2">Hasil Deteksi:</h3>
          <pre className="text-sm">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
