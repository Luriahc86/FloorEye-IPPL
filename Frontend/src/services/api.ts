import axios from "axios";

// =================================================================
// PRODUCTION SAFE: Use environment variable with fallback
// =================================================================
const API_BASE = import.meta.env.VITE_API_BASE || 
                 "https://flooreye-ippl-production.up.railway.app";

console.log("[API Config] Base URL:", API_BASE);

// Verify HTTPS
if (!API_BASE.startsWith("https://")) {
  console.error("[API Config] ⚠️ WARNING: API_BASE is not HTTPS!");
  console.error("[API Config] Current value:", API_BASE);
}

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const fullUrl = `${config.baseURL}${config.url}`;
    console.log(`[API] ${config.method?.toUpperCase()} ${fullUrl}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      console.error("[API] Network error:", error.message);
      return Promise.reject(new Error("Network error. Please check your connection."));
    }

    const status = error.response.status;
    const data = error.response.data;
    const message = data?.detail || data?.error || error.message;

    console.error(`[API] Error ${status}:`, message);
    return Promise.reject(error);
  }
);

export { API_BASE };
export default api;