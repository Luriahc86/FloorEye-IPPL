import axios, { type InternalAxiosRequestConfig } from "axios";

// =======================================
// URL SANITIZER - ALWAYS FORCE HTTPS
// =======================================
const sanitizeUrl = (url: string | undefined): string => {
  if (!url) return "";
  
  // Remove any whitespace
  let clean = url.trim();
  
  // Force HTTPS
  if (clean.startsWith("http://")) {
    clean = clean.replace("http://", "https://");
  }
  
  // Remove trailing slash
  if (clean.endsWith("/")) {
    clean = clean.slice(0, -1);
  }
  
  return clean;
};

// =======================================
// API BASE URL - FORCE HTTPS NO MATTER WHAT
// =======================================
const RAW_URL = "https://flooreye-ippl-production.up.railway.app";
export const API_BASE = sanitizeUrl(RAW_URL);

// Debug log
console.log("[API] Final baseURL:", API_BASE);

// Validate
if (!API_BASE.startsWith("https://")) {
  console.error("[API] CRITICAL: API_BASE is not HTTPS!", API_BASE);
}

// =======================================
// AXIOS INSTANCE
// =======================================
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// =======================================
// REQUEST INTERCEPTOR - FORCE HTTPS
// =======================================
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // FORCE HTTPS on baseURL
    if (config.baseURL) {
      config.baseURL = sanitizeUrl(config.baseURL);
    }

    // FORCE HTTPS on URL
    if (config.url && config.url.startsWith("http://")) {
      config.url = config.url.replace("http://", "https://");
    }

    // Debug
    const fullUrl = `${config.baseURL || ""}${config.url || ""}`;
    console.log(`[API] ${config.method?.toUpperCase()} ${fullUrl}`);

    return config;
  },
  (error) => Promise.reject(error)
);

// =======================================
// RESPONSE INTERCEPTOR - ERROR HANDLING
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
