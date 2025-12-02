import { createBrowserRouter } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";

import UploadPage from "../pages/UploadPage";
import LiveCameraPage from "../pages/LiveCameraPage";
import HistoryPage from "../pages/HistoryPage";
import CamerasPage from "../pages/CamerasPage";
import NotificationsPage from "../pages/NotificationsPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { path: "", element: <UploadPage /> },
      { path: "upload", element: <UploadPage /> },
      { path: "live", element: <LiveCameraPage /> },
      { path: "cameras", element: <CamerasPage /> },
      { path: "notifications", element: <NotificationsPage /> },
      { path: "history", element: <HistoryPage /> },
    ],
  },
]);

export default router;
