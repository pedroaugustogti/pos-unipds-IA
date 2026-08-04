import { Route } from '@angular/router';

export const appRoutes: Route[] = [
  {
    path: 'cfp',
    loadComponent: () =>
      import('./features/cfp/cfp-form.component').then(
        (m) => m.CfpFormComponent,
      ),
  },
];
