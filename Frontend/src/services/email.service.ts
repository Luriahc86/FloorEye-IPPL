import api from "./api";

export const sendTestEmail = async () => {
  const res = await api.get("/email-recipients/test");
  return res.data;
};
