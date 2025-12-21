/**
 * Email Recipients Service - Email recipient management API operations.
 * 
 * Backend endpoints:
 * - GET    /email-recipients
 * - POST   /email-recipients
 * - PATCH  /email-recipients/{id}
 * - DELETE /email-recipients/{id}
 */
import api from "./api";

// Types matching backend EmailRecipient model
export interface EmailRecipient {
  id: number;
  email: string;
  active: boolean;
}

export interface CreateRecipientPayload {
  email: string;
  active?: boolean;
}

export interface ToggleRecipientPayload {
  active: boolean;
}

/**
 * List all email recipients.
 * @returns Array of email recipients
 */
export async function listRecipients(): Promise<EmailRecipient[]> {
  const res = await api.get<EmailRecipient[]>("/email-recipients");
  return res.data;
}

/**
 * Add a new email recipient.
 * @param payload - Email and optional active status
 * @returns Success message
 */
export async function createRecipient(
  payload: CreateRecipientPayload
): Promise<{ message: string }> {
  const res = await api.post<{ message: string }>("/email-recipients", payload);
  return res.data;
}

/**
 * Toggle recipient active status.
 * @param id - Recipient ID
 * @param active - New active status
 * @returns Updated recipient object
 */
export async function toggleRecipient(
  id: number,
  active: boolean
): Promise<EmailRecipient> {
  const res = await api.patch<EmailRecipient>(`/email-recipients/${id}`, {
    active,
  });
  return res.data;
}

/**
 * Delete an email recipient.
 * @param id - Recipient ID
 * @returns Success message
 */
export async function deleteRecipient(
  id: number
): Promise<{ message: string }> {
  const res = await api.delete<{ message: string }>(`/email-recipients/${id}`);
  return res.data;
}

export default {
  listRecipients,
  createRecipient,
  toggleRecipient,
  deleteRecipient,
};
