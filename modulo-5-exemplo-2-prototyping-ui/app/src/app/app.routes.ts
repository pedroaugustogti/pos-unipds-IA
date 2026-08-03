import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: '/pix', pathMatch: 'full' },
  {
    path: 'pix',
    loadComponent: () => import('./pix-transfer/pix-transfer').then((m) => m.PixTransfer),
  },
  {
    path: 'extrato',
    loadComponent: () =>
      import('./pix-history/pix-history.component').then((m) => m.PixHistoryComponent),
  },
  {
    path: 'agendamentos',
    loadComponent: () =>
      import('./pix-schedules/pix-schedules.component').then((m) => m.PixSchedulesComponent),
  },
  {
    path: 'comprovante',
    loadComponent: () =>
      import('./features/receipt/receipt-preview').then((m) => m.ReceiptPreview),
  },
  { path: '**', redirectTo: '/pix' },
];
