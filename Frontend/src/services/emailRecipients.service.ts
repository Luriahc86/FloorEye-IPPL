import api from "./api";

export interface EmailRecipient {
  id: number;
  email: string;
  active: boolean;
}

export const getEmailRecipients = async () => {
  const res = await api.get<EmailRecipient[]>("/email-recipients");
  return res.data;
};

export const createEmailRecipient = async (email: string) => {
  const res = await api.post("/email-recipients", {
    email,
    active: true,
  });
  return res.data;
};

export const updateEmailRecipient = async (
  id: number,
  active: boolean
) => {
  const res = await api.patch(`/email-recipients/${id}`, { active });
  return res.data;
};

export const deleteEmailRecipient = async (id: number) => {
  const res = await api.delete(`/email-recipients/${id}`);
  return res.data;
};

export const testEmailRecipients = async () => {
  const res = await api.get("/email-recipients/test");
  return res.data;
};
