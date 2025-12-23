import { useRef, useState, useEffect } from "react";
import { API_BASE } from "../services/api";

interface DetectionResponse {
  id: number;
  is_dirty: boolean;
  confidence: number;
  created_at: string;
}

interface CameraViewerProps {
  onResult?: (result: DetectionResponse) => void;
  autoDetectInterval?: number;
}

export default function CameraViewer({
  onResult,
  autoDetectInterval = 5000,
}: CameraViewerProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const detectIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const [isActive, setIsActive] = useState<boolean>(false);
  const [isDetecting, setIsDetecting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [autoDetect, setAutoDetect] = useState<boolean>(false);
  const [facingMode, setFacingMode] = useState<"user" | "environment">("environment");

  /** 🔵 Start Camera */
  const startCamera = async (mode?: "user" | "environment") => {
    try {
      const currentMode = mode || facingMode;
      
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: 1280, 
          height: 720,
          facingMode: currentMode
        },
      });

      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      await videoRef.current?.play();

      setIsActive(true);
      setFacingMode(currentMode);
      setError(null);
    } catch (err) {
      console.error("Camera error:", err);
      setError("Tidak dapat mengakses kamera.");
    }
  };

  /** 🔴 Stop Camera */
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }

    if (videoRef.current) videoRef.current.srcObject = null;
    setIsActive(false);
    setAutoDetect(false);

    if (detectIntervalRef.current) {
      clearInterval(detectIntervalRef.current);
      detectIntervalRef.current = null;
    }
  };

  /** � Switch Camera (Front/Rear) */
  const switchCamera = async () => {
    if (!isActive) return;
    
    try {
      // Stop current stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }

      // Toggle facingMode
      const newMode = facingMode === "user" ? "environment" : "user";
      
      // Start camera with new mode
      await startCamera(newMode);
    } catch (err) {
      console.error("Switch camera error:", err);
      setError("Gagal mengganti kamera.");
    }
  };

  /** �📸 Capture Frame */
  const captureFrame = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return "";

    canvas.width = 1280;
    canvas.height = 720;

    const ctx = canvas.getContext("2d");
    if (!ctx) return "";

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL("image/jpeg", 0.95);
  };

  /** 🟢 Auto Detect */
  useEffect(() => {
    if (autoDetect && isActive && !isDetecting) {
      const runDetect = async () => {
        try {
          setIsDetecting(true);
          const base64 = captureFrame();

          const res = await fetch(`${API_BASE}/detect/frame`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              image_base64: base64,
              notes: "live-camera-auto",
            }),
          });

          const data: DetectionResponse = await res.json();
          setResult(data);
          onResult?.(data);
        } catch (err) {
          console.error(err);
        } finally {
          setIsDetecting(false);
        }
      };

      detectIntervalRef.current = setInterval(runDetect, autoDetectInterval);

      return () => {
        if (detectIntervalRef.current)
          clearInterval(detectIntervalRef.current);
      };
    }
  }, [autoDetect, isActive, isDetecting, autoDetectInterval, onResult]);

  /** 🟡 Manual Detect */
  const sendToDetectAPI = async () => {
    try {
      setIsDetecting(true);
      setError(null);

      const base64 = captureFrame();

      const res = await fetch(`${API_BASE}/detect/frame`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_base64: base64, notes: "manual-detect" }),
      });

      const data: DetectionResponse = await res.json();
      setResult(data);
      onResult?.(data);
    } catch (err) {
      console.error(err);
      setError("Gagal mengirim frame ke backend.");
    } finally {
      setIsDetecting(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* BUTTONS */}
      <div className="flex gap-3 flex-wrap">
        {!isActive ? (
          <button
            onClick={() => startCamera()}
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
              onClick={switchCamera}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg"
              title="Toggle Kamera Depan/Belakang"
            >
              🔄 {facingMode === "user" ? "Ke Belakang" : "Ke Depan"}
            </button>

            <button
              onClick={sendToDetectAPI}
              disabled={isDetecting}
              className="px-4 py-2 bg-green-600 text-white rounded-lg disabled:opacity-50"
            >
              {isDetecting ? "Mendeteksi..." : "Deteksi Sekarang"}
            </button>

            <button
              onClick={() => setAutoDetect(!autoDetect)}
              className={`px-4 py-2 text-white rounded-lg ${
                autoDetect ? "bg-orange-600" : "bg-purple-600"
              }`}
            >
              {autoDetect ? "⛔ Stop Auto" : "▶️ Auto-Deteksi"}
            </button>
          </>
        )}
      </div>

      {result && isActive && (
        <div
          className={`p-4 rounded-lg border-2 text-center font-bold text-xl ${
            result.is_dirty
              ? "bg-red-200 border-red-600 text-red-800"
              : "bg-green-200 border-green-600 text-green-800"
          }`}
        >
          {result.is_dirty ? "🚨 LANTAI KOTOR" : "✅ LANTAI BERSIH"}
        </div>
      )}

      <video
        ref={videoRef}
        autoPlay
        playsInline
        className="w-full h-80 rounded-lg object-cover bg-gray-200"
      ></video>

      <canvas ref={canvasRef} className="hidden"></canvas>

      {error && <p className="text-red-600">{error}</p>}
    </div>
  );
}
