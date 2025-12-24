import api from "./api";

export const getHistory = async () => {
  const res = await api.get("/history");
  return res.data;
};
