## 1. Dependências e configuração

- [x] 1.1 Adicionar `class-validator` e `class-transformer` ao projeto `api`
- [x] 1.2 Habilitar `ValidationPipe` global em `api/src/main.ts` com `whitelist: true` e `forbidNonWhitelisted: true`
- [x] 1.3 Verificar que `api` e `frontend` resolvem `@cfp-platform/shared-types` via path alias

## 2. Backend — módulo CFP (`api/`)

- [x] 2.1 Criar `CreateSpeakerDto` em `api/src/app/cfp/` com decorators `class-validator` espelhando `SpeakerDTO`
- [x] 2.2 Criar `CfpService` com armazenamento em memória (`Map<string, SpeakerDTO>`)
- [x] 2.3 Criar `CfpController` com `POST /cfp` usando `@Body()` tipado com `CreateSpeakerDto`
- [x] 2.4 Registrar `CfpModule` e importar em `AppModule`
- [x] 2.5 Importar tipo `SpeakerDTO` de `@cfp-platform/shared-types` no service

## 3. Backend — testes unitários (Jest)

- [x] 3.1 Criar `cfp.controller.spec.ts` com cenário de payload inválido retornando `400 Bad Request`
- [x] 3.2 Criar `cfp.controller.spec.ts` com cenário de payload válido retornando `201 Created`
- [x] 3.3 Executar `nx test api` e garantir que todos os testes passam

## 4. Frontend — componente CFP (`frontend/`)

- [x] 4.1 Criar `CfpFormComponent` standalone em `frontend/src/app/features/cfp/`
- [x] 4.2 Implementar Signals: `form` (modelo `SpeakerDTO`) e `computed` para `isSubmitDisabled`
- [x] 4.3 Implementar template com campos: `name`, `email`, `talkTitle`, `isGDE` (gerar `id` no submit)
- [x] 4.4 Adicionar atributos WAI-ARIA: `aria-label`, `aria-required`, `aria-invalid`, `role="alert"`, `aria-live`
- [x] 4.5 Criar `CfpService` HTTP para `POST /api/cfp` via proxy
- [x] 4.6 Adicionar rota `/cfp` em `app.routes.ts`
- [x] 4.7 Importar `SpeakerDTO` de `@cfp-platform/shared-types`

## 5. Frontend — testes unitários (Vitest-Angular)

- [x] 5.1 Criar `cfp-form.component.spec.ts` verificando estado inicial do Signal
- [x] 5.2 Criar teste verificando que botão de envio está desabilitado com formulário vazio/inválido
- [x] 5.3 Executar `nx test frontend` e garantir que todos os testes passam

## 6. Validação final

- [x] 6.1 Executar `nx build shared-types`, `nx build api`, `nx build frontend`
- [x] 6.2 Executar `nx lint api` e `nx lint frontend`
- [x] 6.3 Testar fluxo manual: acessar `http://localhost:4200/cfp`, submeter proposta válida e inválida
- [x] 6.4 Executar `openspec validate add-cfp-feature`
