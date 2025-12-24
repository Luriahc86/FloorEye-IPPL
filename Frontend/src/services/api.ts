/**
 * Centralized Axios instance for FloorEye API.
 * 
 * PRODUCTION-SAFE CONFIGURATION:
 * - HARDCODED HTTPS URL - NO environment variable dependency
 * - This eliminates ALL possible Mixed Content issues
 */
import axios, { type AxiosError, type InternalAxiosRequestConfig, type AxiosResponse } from "axios";

// ============================================================
// 🔴 HARDCODED HTTPS - DO NOT CHANGE TO HTTP
// ============================================================
const API_BASE = "https://flooreye-ippl-production.up.railway.app";

// Log configuration for debugging
console.log("[API] Using hardcoded HTTPS baseURL:", API_BASE);

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor - logging only, NO URL modification
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const fullUrl = `${config.baseURL}${config.url}`;
    console.log(`[API] ${config.method?.toUpperCase()} ${fullUrl}`);
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response interceptor - error handling only
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (!error.response) {
      console.error("[API] Network error:", error.message);
      return Promise.reject(new Error("Network error. Please check your connection."));
    }

    const status = error.response.status;
    const data = error.response.data as { detail?: string; error?: string };
    const message = data?.detail || data?.error || error.message;

    console.error(`[API] Error ${status}:`, message);
    return Promise.reject(error);
  }
);

export { API_BASE };
export default api;
