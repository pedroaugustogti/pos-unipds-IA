import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { CurrencyPipe, DatePipe } from '@angular/common';

@Component({
  selector: 'app-pix-receipt',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CurrencyPipe, DatePipe],
  templateUrl: './pix-receipt.component.html',
  styleUrl: './pix-receipt.component.css',
})
export class PixReceiptComponent {
  readonly valor = input.required<number>();
  readonly nome = input.required<string>();
  readonly dataHora = input.required<string>();
  readonly instituicao = input<string>('');
  readonly transactionId = input<string>('');
  readonly voltarInicio = output<void>();
}
