import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { PixReceiptComponent } from './pix-receipt.component';

@Component({
  selector: 'app-receipt-preview',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PixReceiptComponent],
  template: `
    <app-pix-receipt
      [valor]="150"
      nome="Erick S."
      dataHora="2023-10-24T14:30:00"
      instituicao="Nubank S.A."
      transactionId="E00000000202310241430abcd1234efgh"
      (voltarInicio)="goHome()"
    />
  `,
})
export class ReceiptPreview {
  private readonly router = inject(Router);

  goHome() {
    void this.router.navigate(['/pix']);
  }
}
