import { computed, Injectable, signal } from '@angular/core';
import { Contact, ScheduleDraft, ScheduledPix } from './models';

@Injectable({ providedIn: 'root' })
export class PixStateService {
  readonly draft = signal<Partial<ScheduleDraft>>({});
  readonly lastReceipt = signal<ScheduledPix | null>(null);

  readonly completeDraft = computed(() => {
    const d = this.draft();
    if (d.contact && d.amount && d.date) {
      return d as ScheduleDraft;
    }
    return null;
  });

  setContact(contact: Contact) {
    this.draft.update((current) => ({ ...current, contact }));
  }

  setAmountDate(amount: number, date: string) {
    this.draft.update((current) => ({ ...current, amount, date }));
  }

  reset() {
    this.draft.set({});
    this.lastReceipt.set(null);
  }
}
