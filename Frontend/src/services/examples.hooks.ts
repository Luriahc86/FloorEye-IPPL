import api from "./api";

export const examplePing = async () => {
  const res = await api.get("/health");
  return res.data;
};
