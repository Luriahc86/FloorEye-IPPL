import { useRef, useState, useEffect } from "react";
import api from "../services/api";

interface DetectionResponse {
  is_dirty: boolean;
  confidence: number;
  count: number;
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

  const [isActive, setIsActive] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [autoDetect, setAutoDetect] = useState(false);
  const [facingMode, setFacingMode] =
    useState<"user" | "environment">("environment");

  /* =========================
     CAMERA CONTROL
  ========================= */

  const startCamera = async (mode?: "user" | "environment") => {
    try {
      const currentMode = mode || facingMode;

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 1280,
          height: 720,
          facingMode: currentMode,
        },
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setIsActive(true);
      setFacingMode(currentMode);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Tidak dapat mengakses kamera.");
    }
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;

    if (videoRef.current) videoRef.current.srcObject = null;

    setIsActive(false);
    setAutoDetect(false);

    if (detectIntervalRef.current) {
      clearInterval(detectIntervalRef.current);
      detectIntervalRef.current = null;
    }
  };

  const switchCamera = async () => {
    if (!isActive) return;

    stopCamera();
    const nextMode = facingMode === "user" ? "environment" : "user";
    await startCamera(nextMode);
  };

  /* =========================
     CAPTURE FRAME → BLOB
  ========================= */

  const captureFrame = (): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      const video = videoRef.current;
      const canvas = canvasRef.current;

      if (!video || !canvas) {
        reject("Camera not ready");
        return;
      }

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const ctx = canvas.getContext("2d");
      if (!ctx) {
        reject("Canvas error");
        return;
      }

      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(
        (blob) => {
          if (!blob) reject("Blob error");
          else resolve(blob);
        },
        "image/jpeg",
        0.9
      );
    });
  };

  /* =========================
     SEND FRAME TO BACKEND
  ========================= */

  const sendFrame = async () => {
    try {
      setIsDetecting(true);
      setError(null);

      const blob = await captureFrame();

      const formData = new FormData();
      formData.append("file", blob, "frame.jpg");

      const res = await api.post(
        "/detect/frame",
        formData
      );

      setResult(res.data);
      onResult?.(res.data);
    } catch (err) {
      console.error(err);
      setError("Gagal mengirim frame ke backend.");
    } finally {
      setIsDetecting(false);
    }
  };

  /* =========================
     AUTO DETECT (5 DETIK)
  ========================= */

  useEffect(() => {
    if (!autoDetect || !isActive || isDetecting) return;

    detectIntervalRef.current = setInterval(
      sendFrame,
      autoDetectInterval
    );

    return () => {
      if (detectIntervalRef.current) {
        clearInterval(detectIntervalRef.current);
        detectIntervalRef.current = null;
      }
    };
  }, [autoDetect, isActive, autoDetectInterval]);

  /* =========================
     UI
  ========================= */

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
            >
              🔄 Ganti Kamera
            </button>

            <button
              onClick={sendFrame}
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
      />

      <canvas ref={canvasRef} className="hidden" />

      {error && <p className="text-red-600">{error}</p>}
    </div>
  );
}
