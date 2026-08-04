## Why

O monorepo `cfp-platform` precisa de um fluxo de **Call for Papers (CFP)** para que palestrantes enviem propostas de palestras de forma padronizada. Hoje existe apenas o contrato `SpeakerDTO` em `shared-types`, sem endpoint nem interface de submissão.

## What Changes

- Novo endpoint REST na API NestJS para receber submissões de palestras
- Validação estrita de payload com `class-validator` (rejeição `400 Bad Request` para dados inválidos)
- Novo formulário Angular standalone com Signals para estado reativo e atributos WAI-ARIA
- Consumo do contrato `SpeakerDTO` exportado por `@cfp-platform/shared-types` em frontend e backend
- Testes unitários obrigatórios (Jest) cobrindo validação da API e estado inicial do formulário Angular
- Rota e integração via proxy existente (`/api`)

## Capabilities

### New Capabilities

- `cfp-submission`: Submissão de proposta de palestra (formulário frontend + endpoint backend + validação + testes)

### Modified Capabilities

_(nenhuma — não há specs principais existentes em `openspec/specs/`)_

## Impact

| Área | Impacto |
|------|---------|
| `api/` | Novo módulo/controller/DTO de CFP; dependência de `shared-types` e `class-validator` |
| `frontend/` | Novo componente standalone, rota `/cfp`, serviço HTTP; dependência de `shared-types` |
| `shared-types/` | Sem alteração — `SpeakerDTO` já existe e será consumido |
| `frontend/proxy.conf.json` | Sem alteração — proxy `/api` já configurado |
| Testes | Novos specs Jest em `api` e `frontend` |
