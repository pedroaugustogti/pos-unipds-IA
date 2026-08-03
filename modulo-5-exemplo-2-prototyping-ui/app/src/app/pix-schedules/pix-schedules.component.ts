import { ChangeDetectionStrategy, Component, inject, resource, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MESSAGES } from '../core/messages';
import { formatCurrency, formatDateBr } from '../core/date.utils';
import { MessageKey } from '../core/models';
import { isPixApiError } from '../core/pix-api.error';
import { MockPixApiService } from '../core/mock-pix-api.service';
import { ErrorModal } from '../components/error-modal/error-modal';

@Component({
  selector: 'app-pix-schedules',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, ErrorModal],
  templateUrl: './pix-schedules.component.html',
  styleUrl: './pix-schedules.component.css',
})
export class PixSchedulesComponent {
  private readonly api = inject(MockPixApiService);

  readonly cancelingId = signal<string | null>(null);
  readonly errorModal = signal<{ title: string; message: string } | null>(null);
  readonly toast = signal<string | null>(null);

  readonly schedulesResource = resource({
    loader: () => this.api.listSchedules(),
  });

  readonly formatCurrency = formatCurrency;
  readonly formatDateBr = formatDateBr;

  async cancel(id: string) {
    this.cancelingId.set(id);
    this.errorModal.set(null);
    try {
      await this.api.cancelSchedule(id);
      this.toast.set(MESSAGES.SCHEDULE_PIX_CANCEL_SUCCESS.message);
      this.schedulesResource.reload();
    } catch (err) {
      if (isPixApiError(err)) {
        const msg = MESSAGES[err.code as MessageKey];
        this.errorModal.set({ title: msg.title, message: msg.message });
      }
    } finally {
      this.cancelingId.set(null);
    }
  }

  demoProcessing() {
    this.api.seedProcessingDemo();
    this.schedulesResource.reload();
  }
}
