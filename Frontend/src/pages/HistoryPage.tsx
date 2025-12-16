import { useEffect, useState } from "react";
import axios from "axios";
import HistoryItem from "../components/HistoryItem";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

interface HistoryType {
  id: number;
  source: string;
  is_dirty: boolean;
  confidence?: number | null;
  notes?: string | null;
  created_at: string;
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const loadHistory = async () => {
      try {
        setLoading(true);
        setError(null);

        const res = await axios.get(`${API_BASE}/history`);
        const data = res.data as unknown;

        if (!Array.isArray(data)) {
          throw new Error("Invalid history payload (not an array)");
        }

        const sanitized = data.filter(
          (item): item is HistoryType =>
            !!item &&
            typeof item.id === "number" &&
            typeof item.source === "string" &&
            typeof item.is_dirty === "boolean" &&
            typeof item.created_at === "string"
        );

        if (!cancelled) {
          setHistory(sanitized);
        }
      } catch (err) {
        if (!cancelled) {
          const message =
            err instanceof Error
              ? err.message
              : "Unknown error while loading history";
          setError(message);
          setHistory([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadHistory();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-semibold">Riwayat Deteksi</h1>

      {loading && <p>Loading...</p>}

      {!loading && error && (
        <p className="text-red-500">Gagal memuat riwayat: {error}</p>
      )}

      {!loading && !error && history.length === 0 && (
        <p className="text-slate-500">Belum ada data.</p>
      )}

      {!loading && !error && history.length > 0 && (
        <div className="space-y-3">
          {history.map((item) => (
            <HistoryItem key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
