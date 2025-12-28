import axios from "axios";

export const API_BASE = "https://flooreye-ippl-production.up.railway.app";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export { api };
export default api;
