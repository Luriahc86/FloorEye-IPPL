/**
 * @deprecated Use emailRecipients.service.ts instead.
 * This file is kept for backward compatibility.
 */
export {
  listRecipients as listEmailRecipients,
  createRecipient as createEmailRecipient,
  toggleRecipient as toggleEmailRecipient,
  deleteRecipient as deleteEmailRecipient,
  type EmailRecipient,
} from "./emailRecipients.service";

export { default } from "./emailRecipients.service";

