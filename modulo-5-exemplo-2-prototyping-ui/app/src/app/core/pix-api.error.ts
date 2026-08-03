import { MessageKey } from './models';

export class PixApiError extends Error {
  constructor(public readonly code: MessageKey) {
    super(code);
    this.name = 'PixApiError';
  }
}

export function isPixApiError(error: unknown): error is PixApiError {
  return error instanceof PixApiError;
}
