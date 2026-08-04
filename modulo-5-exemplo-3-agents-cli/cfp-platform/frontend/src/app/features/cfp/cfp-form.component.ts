import { Component, computed, inject, signal } from '@angular/core';
import { SpeakerDTO } from '@cfp-platform/shared-types';
import { CfpService } from './cfp.service';

type CfpFormModel = Omit<SpeakerDTO, 'id'>;

const EMPTY_FORM: CfpFormModel = {
  name: '',
  email: '',
  talkTitle: '',
  isGDE: false,
};

@Component({
  selector: 'app-cfp-form',
  standalone: true,
  templateUrl: './cfp-form.component.html',
  styleUrl: './cfp-form.component.css',
})
export class CfpFormComponent {
  private readonly cfpService = inject(CfpService);

  readonly form = signal<CfpFormModel>({ ...EMPTY_FORM });
  readonly submitError = signal<string | null>(null);
  readonly submitSuccess = signal(false);
  readonly isSubmitting = signal(false);

  readonly isFormValid = computed(() => {
    const current = this.form();
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return (
      current.name.trim().length > 0 &&
      emailPattern.test(current.email.trim()) &&
      current.talkTitle.trim().length > 0
    );
  });

  readonly isSubmitDisabled = computed(
    () => !this.isFormValid() || this.isSubmitting(),
  );

  updateField<K extends keyof CfpFormModel>(
    field: K,
    value: CfpFormModel[K],
  ): void {
    this.form.update((current) => ({ ...current, [field]: value }));
    this.submitError.set(null);
    this.submitSuccess.set(false);
  }

  onSubmit(): void {
    if (this.isSubmitDisabled()) {
      return;
    }

    const payload: SpeakerDTO = {
      id: crypto.randomUUID(),
      ...this.form(),
    };

    this.isSubmitting.set(true);
    this.submitError.set(null);
    this.submitSuccess.set(false);

    this.cfpService.submit(payload).subscribe({
      next: () => {
        this.submitSuccess.set(true);
        this.form.set({ ...EMPTY_FORM });
        this.isSubmitting.set(false);
      },
      error: () => {
        this.submitError.set(
          'Não foi possível enviar a proposta. Verifique os dados e tente novamente.',
        );
        this.isSubmitting.set(false);
      },
    });
  }
}
