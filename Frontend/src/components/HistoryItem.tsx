const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

interface HistoryItemData {
  id: number;
  source: string;
  is_dirty: boolean;
  confidence?: number | null;
  notes?: string | null;
  created_at: string;
}

interface Props {
  item?: HistoryItemData | null;
}

export default function HistoryItem({ item }: Props) {
  // Defensive guard: jika item tidak valid, jangan render apa pun
  if (!item || typeof item.id !== "number") {
    return null;
  }

  const imageUrl = `${API_BASE}/history/${item.id}/image`;

  return (
    <div className="p-4 bg-white shadow rounded-lg flex gap-4">
      <img
        src={imageUrl}
        alt="History"
        className="w-32 h-32 object-cover rounded"
        loading="lazy"
        onError={(e) => {
          // Sembunyikan gambar jika backend mengembalikan 404 / error lain
          e.currentTarget.style.visibility = "hidden";
        }}
      />

      <div>
        <p className="font-semibold text-lg">
          {item.is_dirty ? "KOTOR ❌" : "BERSIH ✅"}
        </p>
        <p className="text-sm text-slate-700">Sumber: {item.source}</p>
        <p className="text-sm text-slate-700">Waktu: {item.created_at}</p>

        {item.notes && (
          <p className="text-sm text-slate-600 mt-1">Catatan: {item.notes}</p>
        )}
      </div>
    </div>
  );
}
