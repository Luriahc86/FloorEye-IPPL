import { API_BASE } from "../services/api";

interface HistoryItemData {
  id: number;
  source?: string | null;
  is_dirty: boolean;
  confidence?: number | null;
  notes?: string | null;
  created_at: string;
}

export default function HistoryItem({ item }: { item?: HistoryItemData | null }) {
  if (!item || typeof item.id !== "number") return null;

  const imageUrl = `${API_BASE}/history/${item.id}/image`;
  const time = new Date(item.created_at).toLocaleString("id-ID", {
    dateStyle: "medium", timeStyle: "short",
  });

  return (
    <div className="p-4 bg-white shadow rounded-lg flex gap-4">
      <img
        src={imageUrl}
        className="w-32 h-32 object-cover rounded bg-slate-100"
        onError={(e) => (e.currentTarget.style.display = "none")}
      />
      <div className="space-y-1">
        <div className="font-semibold text-lg">
          {item.is_dirty ? "KOTOR ❌" : "BERSIH ✅"}
        </div>
        {item.confidence != null && (
          <div className="text-sm">Confidence: {(item.confidence * 100).toFixed(1)}%</div>
        )}
        <div className="text-sm">Sumber: {item.source || "Live Camera"}</div>
        <div className="text-sm">Waktu: {time}</div>
        {item.notes && <div className="text-sm">Catatan: {item.notes}</div>}
      </div>
    </div>
  );
}
