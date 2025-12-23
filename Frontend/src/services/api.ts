/**
 * Centralized Axios instance for FloorEye API.
 * 
 * Configuration:
 * - Uses VITE_API_BASE environment variable for baseURL
 * - Falls back to production Railway URL if not set
 * - Enforces HTTPS to prevent Mixed Content errors
 * - Includes request/response interceptors for error handling
 * - No authentication layer (as per spec)
 */
import axios, { type AxiosError, type InternalAxiosRequestConfig, type AxiosResponse } from "axios";

// Production backend URL (Railway)
const PRODUCTION_API = "https://flooreye-ippl-production.up.railway.app";

/**
 * Sanitize API URL to enforce HTTPS and remove trailing slash.
 * Prevents Mixed Content errors when deployed on HTTPS (Vercel).
 */
function sanitizeApiUrl(url: string): string {
  let sanitized = url.trim();
  
  // Remove trailing slash
  if (sanitized.endsWith("/")) {
    sanitized = sanitized.slice(0, -1);
  }
  
  // Enforce HTTPS (fix common misconfiguration)
  if (sanitized.startsWith("http://") && !sanitized.includes("localhost") && !sanitized.includes("127.0.0.1")) {
    console.warn("[API] Converting HTTP to HTTPS to prevent Mixed Content errors:", sanitized);
    sanitized = sanitized.replace("http://", "https://");
  }
  
  return sanitized;
}

// API base URL from environment variable, fallback to production
const rawApiBase = import.meta.env.VITE_API_BASE || PRODUCTION_API;
const API_BASE = sanitizeApiUrl(rawApiBase);

// Log the API configuration (helps debug Mixed Content issues)
console.log("[API] Configuration:", {
  raw: rawApiBase,
  sanitized: API_BASE,
  env: import.meta.env.MODE,
});

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000, // 30 second timeout
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for logging and URL debugging
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Construct full URL for debugging
    const fullUrl = config.baseURL 
      ? `${config.baseURL}${config.url?.startsWith('/') ? '' : '/'}${config.url}`
      : config.url;
    
    // ALWAYS log the full URL to debug Mixed Content issues
    console.log(`[API] ${config.method?.toUpperCase()} ${fullUrl}`);
    console.log("[API] Request config:", { 
      baseURL: config.baseURL, 
      url: config.url,
      fullUrl: fullUrl
    });
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    // Network error (no response)
    if (!error.response) {
      console.error("[API] Network error:", error.message);
      return Promise.reject(new Error("Network error. Please check your connection."));
    }

    const status = error.response.status;
    const data = error.response.data as { detail?: string; error?: string };
    const message = data?.detail || data?.error || error.message;

    // Handle common HTTP errors
    switch (status) {
      case 400:
        console.error("[API] Bad request:", message);
        break;
      case 404:
        console.error("[API] Not found:", message);
        break;
      case 500:
        console.error("[API] Server error:", message);
        break;
      case 503:
        console.error("[API] Service unavailable:", message);
        break;
      default:
        console.error(`[API] Error ${status}:`, message);
    }

    return Promise.reject(error);
  }
);

export { API_BASE };
export default api;
