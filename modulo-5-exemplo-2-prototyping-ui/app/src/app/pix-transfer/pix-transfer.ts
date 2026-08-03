import {
  ChangeDetectionStrategy,
  Component,
  computed,
  effect,
  ElementRef,
  HostListener,
  inject,
  signal,
  ViewChild,
} from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule } from '@angular/forms';
import { startWith } from 'rxjs';
import { ErrorModal } from '../components/error-modal/error-modal';
import { PixReceiptComponent } from '../features/receipt/pix-receipt.component';
import { ACCOUNT_BALANCE, DAILY_LIMIT, MFA_PIN, MESSAGES } from '../core/messages';
import { isToday, tomorrowIso } from '../core/date.utils';
import { MessageKey } from '../core/models';
import { isPixApiError } from '../core/pix-api.error';
import { MockPixApiService } from '../core/mock-pix-api.service';
import { PixStateService } from '../core/pix-state.service';

@Component({
  selector: 'app-pix-transfer',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ReactiveFormsModule, ErrorModal, PixReceiptComponent],
  templateUrl: './pix-transfer.html',
  styleUrl: './pix-transfer.css',
})
export class PixTransfer {
  private readonly api = inject(MockPixApiService);
  private readonly state = inject(PixStateService);
  private readonly fb = inject(NonNullableFormBuilder);

  readonly errorModal = signal<{ title: string; message: string } | null>(null);
  readonly mfaOpen = signal(false);
  readonly mfaError = signal(false);
  readonly processing = signal(false);
  readonly showInstantPix = signal(false);
  readonly minDate = tomorrowIso();

  readonly receipt = computed(() => this.state.lastReceipt());

  readonly transferForm = this.fb.group({
    pixKey: this.fb.control(''),
    amount: this.fb.control(''),
    date: this.fb.control(tomorrowIso()),
  });

  readonly mfaForm = this.fb.group({
    pin: this.fb.control(''),
  });

  private readonly formValues = toSignal(
    this.transferForm.valueChanges.pipe(startWith(this.transferForm.getRawValue())),
    { initialValue: this.transferForm.getRawValue() },
  );

  readonly amount = computed(() => {
    const raw = this.formValues()?.amount ?? '';
    return parseFloat(String(raw).replace(',', '.')) || 0;
  });

  readonly dateInput = computed(() => this.formValues()?.date ?? tomorrowIso());

  @ViewChild('mfaPinInput') mfaPinInput?: ElementRef<HTMLInputElement>;
  @ViewChild('instantDialog') instantDialog?: ElementRef<HTMLElement>;

  constructor() {
    effect(() => {
      if (this.mfaOpen()) {
        queueMicrotask(() => this.mfaPinInput?.nativeElement.focus());
      }
      if (this.showInstantPix()) {
        queueMicrotask(() => this.instantDialog?.nativeElement.focus());
      }
    });
  }

  @HostListener('document:keydown.escape')
  onEscape() {
    if (this.mfaOpen()) {
      this.mfaOpen.set(false);
      return;
    }
    if (this.showInstantPix()) {
      this.showInstantPix.set(false);
    }
  }

  async onSubmit() {
    if (this.amount() > DAILY_LIMIT) {
      const msg = MESSAGES.SCHEDULE_PIX_VALUE_TOO_HIGH;
      this.errorModal.set({ title: msg.title, message: msg.message });
      return;
    }
    if (this.amount() <= 0) return;

    if (isToday(this.dateInput())) {
      this.showInstantPix.set(true);
      return;
    }

    const pixKey = this.transferForm.controls.pixKey.value.trim();
    if (!pixKey) return;

    try {
      const contact = await this.api.resolvePixKey(pixKey);
      this.state.setContact(contact);
      this.state.setAmountDate(this.amount(), this.dateInput());
      this.openMfa();
    } catch (error) {
      if (isPixApiError(error)) {
        const msg = MESSAGES[error.code];
        this.errorModal.set({ title: msg.title, message: msg.message });
      }
    }
  }

  openMfa() {
    this.mfaOpen.set(true);
    this.mfaError.set(false);
    this.mfaForm.reset();
  }

  async confirmSchedule() {
    const pin = this.mfaForm.controls.pin.value;
    if (pin !== MFA_PIN) {
      this.mfaError.set(true);
      return;
    }
    this.mfaOpen.set(false);
    const draft = this.state.completeDraft();
    if (!draft) return;

    this.processing.set(true);
    this.errorModal.set(null);
    try {
      const id = crypto.randomUUID();
      const result = await this.api.createSchedule(draft, id, ACCOUNT_BALANCE);
      this.state.lastReceipt.set(result);
    } catch (error) {
      if (isPixApiError(error)) {
        const msg = MESSAGES[error.code];
        this.errorModal.set({ title: msg.title, message: msg.message });
      } else {
        const msg = MESSAGES.SCHEDULE_PIX_UNEXPECTED_ERROR;
        this.errorModal.set({ title: msg.title, message: msg.message });
      }
    } finally {
      this.processing.set(false);
    }
  }

  resetFlow() {
    this.state.reset();
    this.errorModal.set(null);
    this.showInstantPix.set(false);
    this.transferForm.reset({ pixKey: '', amount: '', date: tomorrowIso() });
  }

  messageFor(code: MessageKey) {
    return MESSAGES[code];
  }
}
