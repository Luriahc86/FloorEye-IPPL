import { useState } from "react";

interface Props {
  onImageSelected: (file: File) => void;
  onDetect: () => void;
  loading: boolean;
}

export default function ImageUploader({ onImageSelected, onDetect, loading }: Props) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (loading) return;

    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      onImageSelected(file);
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-white shadow space-y-3">
      <label className="block text-sm font-medium">Pilih Gambar</label>

      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={loading}
        className={`w-full ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
      />

      <button
        onClick={() => !loading && onDetect()}
        disabled={!selectedFile || loading}
        className={`px-4 py-2 rounded-md text-white w-full transition
          ${
            !selectedFile || loading
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }
        `}
      >
        {loading ? "Mendeteksi..." : "Deteksi Gambar"}
      </button>
    </div>
  );
}
