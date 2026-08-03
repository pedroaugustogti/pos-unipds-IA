# UI States Checklist — Pix Agendado

> **Status:** Artefato de saída do refinamento — ver `PIPELINE.md`.

Checklist para o desenvolvedor front-end derivado de `edge-cases.md`.

## Entrada de dados e validação

- [ ] `DatePicker` — dias passados e hoje desabilitados (cinza)
- [ ] `AmountInput` — valor > R$ 5.000 desabilita Continuar + helper text
- [ ] `InsufficientFundsWarning` — aviso soft se valor > saldo atual
- [ ] `ContactListLoading` — skeleton durante carregamento
- [ ] `ContactListEmpty` — ilustração + CTA buscar chave manualmente
- [ ] `InvalidPixKey` — feedback se destinatário não encontrado

## Revisão e segurança

- [ ] `ReviewScreen` — resumo contato, valor, data
- [ ] `BiometricPinModal` — MFA antes do POST
- [ ] `MfaError` — senha incorreta, retry sem perder contexto
- [ ] `ProcessingOverlay` — "Registrando agendamento..."

## Respostas da API

- [ ] `ScheduleSuccess` — comprovante com share/print
- [ ] `ErrorLimitExceeded` — limite diário
- [ ] `ErrorNightLimit` — limite noturno na data de execução
- [ ] `ErrorInsufficientFunds` — 403 saldo
- [ ] `ErrorServer` — instabilidade Bacen
- [ ] `ErrorTimeout` — verificar extrato + tentar novamente
- [ ] `SuggestInstantPix` — data = hoje → CTA Pix imediato

## Lista e cancelamento

- [ ] `ScheduleListEmpty` — sem agendamentos
- [ ] `ScheduleListItem` — status, data, valor
- [ ] `CancelLoading` — loading no item (evitar double-click)
- [ ] `CancelSuccess` — toast confirmação
- [ ] `CancelLocked` — já em processamento, não cancelável
- [ ] `InvalidKeyAlert` — chave inválida antes da execução

## Acessibilidade e resiliência

- [ ] Date picker navegável por teclado
- [ ] Anúncio de screen reader para transação futura
- [ ] Error Boundary no fluxo de confirmação (evitar tela branca)
- [ ] Idempotency key no header do POST
