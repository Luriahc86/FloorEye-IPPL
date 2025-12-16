import { NavLink } from "react-router-dom";

interface SidebarProps {
  variant?: "desktop" | "mobile";
  /** Dipanggil saat user memilih menu (untuk nutup drawer mobile) */
  onNavigate?: () => void;
}

export default function Sidebar({
  variant = "desktop",
  onNavigate,
}: SidebarProps) {
  const handleNavigate = () => {
    if (onNavigate) onNavigate();
  };

  return (
    <aside className="flex h-full w-64 flex-col bg-white border-r shadow-sm overflow-y-auto">
      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 text-sm font-medium text-slate-700">
        <NavLink
          to="/live"
          onClick={handleNavigate}
          className={({ isActive }) =>
            `flex items-center rounded-md px-3 py-2 transition ${
              isActive
                ? "bg-blue-50 text-blue-700"
                : "hover:bg-slate-50 text-slate-700 hover:text-slate-900"
            }`
          }
        >
          Live Camera
        </NavLink>

        <NavLink
          to="/history"
          onClick={handleNavigate}
          className={({ isActive }) =>
            `flex items-center rounded-md px-3 py-2 transition ${
              isActive
                ? "bg-blue-50 text-blue-700"
                : "hover:bg-slate-50 text-slate-700 hover:text-slate-900"
            }`
          }
        >
          Riwayat Deteksi
        </NavLink>

        <NavLink
          to="/notifications"
          onClick={handleNavigate}
          className={({ isActive }) =>
            `flex items-center rounded-md px-3 py-2 transition ${
              isActive
                ? "bg-blue-50 text-blue-700"
                : "hover:bg-slate-50 text-slate-700 hover:text-slate-900"
            }`
          }
        >
          Notifikasi Email
        </NavLink>
      </nav>
    </aside>
  );
}
