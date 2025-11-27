import { useRef, useState } from "react";

export default function CameraViewer() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);   // FIX!!

  const [isActive, setIsActive] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [result, setResult] = useState(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });

      streamRef.current = stream; // SIMPAN STREAM
      videoRef.current.srcObject = stream;

      await videoRef.current.play();  // PENTING!

      setIsActive(true);
    } catch (error) {
      console.error("Camera error:", error);
      alert("Tidak dapat mengakses kamera. Periksa izin browser.");
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setIsActive(false);
    setIsDetecting(false);
  };

  const captureFrame = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    return canvas;
  };

  const sendToDetectAPI = async () => {
    try {
      setIsDetecting(true);

      const canvas = captureFrame();
      const blob = await new Promise((resolve) =>
        canvas.toBlob(resolve, "image/jpeg", 0.9)
      );

      const formData = new FormData();
      formData.append("image", blob, "frame.jpg");

      const response = await fetch("http://localhost:5000/api/detect", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Detect API error:", error);
    } finally {
      setIsDetecting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-3">
        {!isActive && (
          <button
            onClick={startCamera}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            Aktifkan Kamera
          </button>
        )}

        {isActive && (
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
        playsInline        // FIX UNTUK MOBILE
        className="w-full h-80 bg-gray-200 rounded-lg"
      ></video>

      <canvas ref={canvasRef} className="hidden"></canvas>

      {result && (
        <div className="p-4 bg-gray-100 border rounded-lg">
          <h3 className="font-bold mb-2">Hasil Deteksi:</h3>
          <pre className="text-sm">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
