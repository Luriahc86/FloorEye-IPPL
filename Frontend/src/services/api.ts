import axios from "axios";
export const API_BASE = "https://flooreye-ippl-production.up.railway.app";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});
