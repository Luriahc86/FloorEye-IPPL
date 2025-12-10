import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

import { RouterProvider, createBrowserRouter } from "react-router-dom";

import MainLayout from "./layouts/MainLayout";
import UploadPage from "./pages/UploadPage";
import LiveCameraPage from "./pages/LiveCameraPage";
import HistoryPage from "./pages/HistoryPage";
import NotificationsPage from "./pages/NotificationsPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { index: true, element: <UploadPage /> },
      { path: "upload", element: <UploadPage /> },
      { path: "live", element: <LiveCameraPage /> },
      { path: "history", element: <HistoryPage /> },
      { path: "notifications", element: <NotificationsPage /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
