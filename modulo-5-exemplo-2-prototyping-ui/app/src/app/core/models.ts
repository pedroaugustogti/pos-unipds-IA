export type MessageKey =
  | 'SCHEDULE_PIX_INITIAL_LOAD_ERROR'
  | 'SCHEDULE_PIX_INVALID_DATE'
  | 'SCHEDULE_PIX_VALUE_TOO_HIGH'
  | 'SCHEDULE_PIX_INSUFFICIENT_FUNDS'
  | 'SCHEDULE_PIX_DESTINATION_NOT_FOUND'
  | 'SCHEDULE_PIX_CONNECTION_ERROR'
  | 'SCHEDULE_PIX_AUTHENTICATION_ERROR'
  | 'SCHEDULE_PIX_UNEXPECTED_ERROR'
  | 'SCHEDULE_PIX_CANT_CANCEL_TODAY'
  | 'SCHEDULE_PIX_SUCCESS'
  | 'SCHEDULE_PIX_CANCEL_SUCCESS'
  | 'SCHEDULE_PIX_INSTANT_TRANSFER_PROMPT';

export interface UiMessage {
  title: string;
  message: string;
  action_label: string;
}

export interface Contact {
  id: string;
  name: string;
  pixKey: string;
}

export interface ScheduleDraft {
  contact: Contact;
  amount: number;
  date: string;
}

export type ScheduleStatus = 'scheduled' | 'processing';

export interface ScheduledPix {
  id: string;
  contact: Contact;
  amount: number;
  date: string;
  status: ScheduleStatus;
  createdAt: string;
}
