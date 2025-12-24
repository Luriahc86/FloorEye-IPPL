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
 * 
 * CRITICAL: This function MUST ensure HTTPS for all non-localhost URLs
 * to prevent Mixed Content blocking in production.
 */
function sanitizeApiUrl(url: string): string {
  let sanitized = url.trim();
  
  // Remove trailing slash
  while (sanitized.endsWith("/")) {
    sanitized = sanitized.slice(0, -1);
  }
  
  // Check if running in browser on HTTPS (production)
  const isSecureContext = typeof window !== "undefined" && window.location.protocol === "https:";
  const isLocalhost = sanitized.includes("localhost") || sanitized.includes("127.0.0.1");
  
  // ALWAYS enforce HTTPS for non-localhost URLs when in secure context
  if (sanitized.startsWith("http://") && !isLocalhost) {
    console.warn("[API] ⚠️ Converting HTTP to HTTPS to prevent Mixed Content errors:", sanitized);
    sanitized = sanitized.replace("http://", "https://");
  }
  
  // Double-check: if we're on HTTPS and URL is HTTP (non-localhost), force HTTPS
  if (isSecureContext && !isLocalhost && !sanitized.startsWith("https://")) {
    console.warn("[API] ⚠️ Forcing HTTPS for secure context:", sanitized);
    sanitized = sanitized.replace(/^http:\/\//, "https://");
    if (!sanitized.startsWith("https://")) {
      sanitized = "https://" + sanitized.replace(/^https?:\/\//, "");
    }
  }
  
  return sanitized;
}

// Get API base URL - prioritize env var, fallback to hardcoded production URL
const rawApiBase = import.meta.env.VITE_API_BASE || PRODUCTION_API;

// CRITICAL: Always sanitize to ensure HTTPS
const API_BASE = sanitizeApiUrl(rawApiBase);

// Log the API configuration (helps debug Mixed Content issues)
console.log("[API] Configuration:", {
  raw: rawApiBase,
  sanitized: API_BASE,
  env: import.meta.env.MODE,
  isSecureContext: typeof window !== "undefined" ? window.location.protocol : "N/A",
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
