import axios, { type InternalAxiosRequestConfig } from "axios";

const sanitizeUrl = (url: string | undefined): string => {
  if (!url) return "";
  
  let clean = url.trim();
  
  if (clean.startsWith("http://")) {
    clean = clean.replace("http://", "https://");
  }
  
  if (clean.endsWith("/")) {
    clean = clean.slice(0, -1);
  }
  
  return clean;
};

const RAW_URL = "https://flooreye-ippl-production.up.railway.app";
export const API_BASE = sanitizeUrl(RAW_URL);

console.log("[API] Final baseURL:", API_BASE);

if (!API_BASE.startsWith("https://")) {
  console.error("[API] CRITICAL: API_BASE is not HTTPS!", API_BASE);
}

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (config.baseURL) {
      config.baseURL = sanitizeUrl(config.baseURL);
    }

    if (config.url && config.url.startsWith("http://")) {
      config.url = config.url.replace("http://", "https://");
    }

    const fullUrl = `${config.baseURL || ""}${config.url || ""}`;
    console.log(`[API] ${config.method?.toUpperCase()} ${fullUrl}`);

    return config;
  },
  (error) => Promise.reject(error)
);

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
