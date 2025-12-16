import { createBrowserRouter } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";

import LiveCameraPage from "../pages/LiveCameraPage";
import HistoryPage from "../pages/HistoryPage";
import NotificationsPage from "../pages/NotificationsPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { path: "", element: <LiveCameraPage /> },
      { path: "live", element: <LiveCameraPage /> },
      { path: "notifications", element: <NotificationsPage /> },
      { path: "history", element: <HistoryPage /> },
    ],
  },
]);

export default router;