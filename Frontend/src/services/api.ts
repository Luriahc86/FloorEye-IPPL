import axios from "axios";

// PRODUCTION URL - Must use HTTPS!
export const API_BASE = "https://flooreye-ippl-production.up.railway.app";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// =======================================
// REQUEST INTERCEPTOR - Force HTTPS
// =======================================
api.interceptors.request.use(
  (config) => {
    // Force HTTPS on baseURL
    if (config.baseURL && config.baseURL.startsWith("http://")) {
      config.baseURL = config.baseURL.replace("http://", "https://");
    }

    // Force HTTPS on full URL
    if (config.url && config.url.startsWith("http://")) {
      config.url = config.url.replace("http://", "https://");
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// =======================================
// RESPONSE INTERCEPTOR - Error handling
// =======================================
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      console.error("[API] Network error:", error.message);
    } else {
      console.error(`[API] Error ${error.response.status}:`, error.response.data);
    }
    return Promise.reject(error);
  }
);

export { api };
export default api;
