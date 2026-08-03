import { Injectable } from '@angular/core';
import { Contact, ScheduledPix } from './models';
import { PixApiError } from './pix-api.error';

const CONTACTS: Contact[] = [
  { id: 'c1', name: 'Maria Silva', pixKey: 'maria@email.com' },
  { id: 'c2', name: 'João Santos', pixKey: '11987654321' },
  { id: 'c3', name: 'Ana Costa', pixKey: 'ana.costa@banco.com' },
];

const STORAGE_KEY = 'pix_schedules_angular_v1';

@Injectable({ providedIn: 'root' })
export class MockPixApiService {
  private delay(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async fetchContacts(empty = false): Promise<Contact[]> {
    await this.delay(600);
    return empty ? [] : [...CONTACTS];
  }

  async resolvePixKey(key: string): Promise<Contact> {
    await this.delay(300);
    const normalized = key.trim().toLowerCase();
    if (!normalized || normalized === 'invalid@pix') {
      throw new PixApiError('SCHEDULE_PIX_DESTINATION_NOT_FOUND');
    }
    const found = CONTACTS.find((c) => c.pixKey.toLowerCase() === normalized);
    if (found) return found;
    return {
      id: `manual-${Date.now()}`,
      name: normalized.split('@')[0] || 'Destinatário',
      pixKey: key.trim(),
    };
  }

  async createSchedule(
    draft: { contact: Contact; amount: number; date: string },
    idempotencyKey: string,
    balance: number,
  ): Promise<ScheduledPix> {
    await this.delay(1000);
    const all = this.readSchedules();
    const existing = all.find((s) => s.id === idempotencyKey);
    if (existing) return existing;

    if (draft.amount > balance) {
      throw new PixApiError('SCHEDULE_PIX_INSUFFICIENT_FUNDS');
    }
    if (draft.amount >= 4999.99) {
      throw new PixApiError('SCHEDULE_PIX_CONNECTION_ERROR');
    }

    const item: ScheduledPix = {
      id: idempotencyKey,
      contact: draft.contact,
      amount: draft.amount,
      date: draft.date,
      status: 'scheduled',
      createdAt: new Date().toISOString(),
    };
    this.writeSchedules([item, ...all]);
    return item;
  }

  async listSchedules(): Promise<ScheduledPix[]> {
    await this.delay(400);
    return this.readSchedules();
  }

  async cancelSchedule(id: string): Promise<void> {
    await this.delay(500);
    const all = this.readSchedules();
    const item = all.find((s) => s.id === id);
    if (!item) throw new PixApiError('SCHEDULE_PIX_UNEXPECTED_ERROR');
    if (item.status === 'processing') {
      throw new PixApiError('SCHEDULE_PIX_CANT_CANCEL_TODAY');
    }
    this.writeSchedules(all.filter((s) => s.id !== id));
  }

  seedProcessingDemo(): void {
    const all = this.readSchedules();
    if (all.length > 0 && all[0].status === 'scheduled') {
      all[0] = { ...all[0], status: 'processing' };
      this.writeSchedules(all);
    }
  }

  private readSchedules(): ScheduledPix[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? (JSON.parse(raw) as ScheduledPix[]) : [];
    } catch {
      return [];
    }
  }

  private writeSchedules(items: ScheduledPix[]) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }
}
