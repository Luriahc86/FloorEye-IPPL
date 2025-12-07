import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white shadow-lg border-r h-full p-6">
      <h1 className="text-2xl font-bold text-blue-600 mb-6">FloorEye</h1>

      <nav className="space-y-3">
        <NavLink
          to="/upload"
          className={({ isActive }) =>
            `block px-4 py-2 rounded-lg ${
              isActive ? "bg-blue-600 text-white" : "hover:bg-blue-50"
            }`
          }
        >
          Upload Gambar
        </NavLink>

        <NavLink
          to="/live"
          className={({ isActive }) =>
            `block px-4 py-2 rounded-lg ${
              isActive ? "bg-blue-600 text-white" : "hover:bg-blue-50"
            }`
          }
        >
          Live Camera
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) =>
            `block px-4 py-2 rounded-lg ${
              isActive ? "bg-blue-600 text-white" : "hover:bg-blue-50"
            }`
          }
        >
          Riwayat Deteksi
        </NavLink>


        <NavLink
          to="/notifications"
          className={({ isActive }) =>
            `block px-4 py-2 rounded-lg ${
              isActive ? "bg-blue-600 text-white" : "hover:bg-blue-50"
            }`
          }
        >
          Notifikasi
        </NavLink>
      </nav>
    </aside>
  );
}
