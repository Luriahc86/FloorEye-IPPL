import api from "./api";

export interface EmailRecipient {
  id: number;
  email: string;
  active: boolean;
}

// GET all recipients
export const getEmailRecipients = async () => {
  const res = await api.get<EmailRecipient[]>("/email-recipients");
  return res.data;
};

// POST add recipient
export const createEmailRecipient = async (email: string) => {
  const res = await api.post("/email-recipients", {
    email,
    active: true,
  });
  return res.data;
};

// PATCH toggle active
export const updateEmailRecipient = async (
  id: number,
  active: boolean
) => {
  const res = await api.patch(`/email-recipients/${id}`, { active });
  return res.data;
};

// DELETE recipient
export const deleteEmailRecipient = async (id: number) => {
  const res = await api.delete(`/email-recipients/${id}`);
  return res.data;
};

// TEST email
export const testEmailRecipients = async () => {
  const res = await api.get("/email-recipients/test");
  return res.data;
};
