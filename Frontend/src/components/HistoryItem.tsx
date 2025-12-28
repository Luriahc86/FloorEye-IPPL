import { API_BASE } from "../services/api";

interface HistoryItemData {
  id: number;
  source?: string | null;
  is_dirty: boolean;
  confidence?: number | null;
  notes?: string | null;
  created_at: string;
}

interface Props {
  item?: HistoryItemData | null;
}

export default function HistoryItem({ item }: Props) {
  if (!item || typeof item.id !== "number") {
    return null;
  }

  const imageUrl = `${API_BASE}/history/${item.id}/image`;

  const formattedTime = new Date(item.created_at).toLocaleString("id-ID", {
    dateStyle: "medium",
    timeStyle: "short",
  });

  return (
    <div className="p-4 bg-white shadow rounded-lg flex gap-4">
      <img
        src={imageUrl}
        alt="History"
        className="w-32 h-32 object-cover rounded bg-slate-100"
        loading="lazy"
        onError={(e) => {
          e.currentTarget.style.display = "none";
        }}
      />

      <div className="space-y-1">
        <p className="font-semibold text-lg">
          {item.is_dirty ? "KOTOR ❌" : "BERSIH ✅"}
        </p>

        {item.confidence != null && (
          <p className="text-sm text-slate-700">
            Confidence: {(item.confidence * 100).toFixed(1)}%
          </p>
        )}

        <p className="text-sm text-slate-700">
          Sumber: {item.source || "Live Camera"}
        </p>

        <p className="text-sm text-slate-700">
          Waktu: {formattedTime}
        </p>

        {item.notes && (
          <p className="text-sm text-slate-600 mt-1">
            Catatan: {item.notes}
          </p>
        )}
      </div>
    </div>
  );
}
