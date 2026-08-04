## Context

Monorepo Nx em `cfp-platform/` com:

| Projeto | Pasta | Stack |
|---------|-------|-------|
| API | `api/` | NestJS + Webpack, prefixo `/api`, porta 3000 |
| Frontend | `frontend/` | Angular standalone + esbuild, porta 4200, proxy `/api` |
| Shared | `shared-types/` | `@cfp-platform/shared-types` com `SpeakerDTO` |

O grafo Nx ainda não declara dependência de `api`/`frontend` em `shared-types` — será adicionada na implementação.

## Goals / Non-Goals

**Goals:**

- Endpoint `POST /api/cfp` recebendo `SpeakerDTO` com validação `class-validator`
- Formulário standalone em `frontend/` com Signals, rota `/cfp`, acessível (WAI-ARIA)
- Ambos os lados importam `SpeakerDTO` de `@cfp-platform/shared-types`
- Testes Jest: API retorna 400 para payload inválido; Angular valida Signal inicial e botão desabilitado

**Non-Goals:**

- Persistência em banco de dados (submissões podem ficar em memória nesta fase)
- Autenticação/autorização de palestrantes
- Painel administrativo de revisão de propostas
- Testes E2E (Playwright) — apenas unitários nesta change

## Decisions

### 1. Estrutura de pastas (ajuste ao prompt)

O prompt referencia `apps/frontend` e `apps/api`, mas o workspace Nx usa `frontend/` e `api/` na raiz. **Decisão:** seguir a estrutura real do monorepo.

### 2. DTO de validação no backend

**Decisão:** criar `CreateSpeakerDto` em `api/` que implementa/estende os campos de `SpeakerDTO` com decorators `class-validator` (`@IsString`, `@IsEmail`, `@IsBoolean`, `@IsNotEmpty`).

**Alternativa descartada:** validar manualmente no controller — menos declarativo e mais difícil de testar.

### 3. Geração de `id` no frontend

**Decisão:** gerar `id` com `crypto.randomUUID()` no momento do submit, mantendo o contrato `SpeakerDTO` intacto.

**Alternativa descartada:** `id` gerado no backend — exigiria alterar o contrato ou aceitar `id` opcional.

### 4. Estado do formulário com Signals

**Decisão:** usar `signal()` para o modelo do formulário e `computed()` para `isFormValid` e `isSubmitDisabled`.

```typescript
// Padrão esperado (não implementar ainda)
form = signal<SpeakerDTO>({ ... });
isSubmitDisabled = computed(() => !this.isFormValid());
```

### 5. Acessibilidade WAI-ARIA

**Decisão:**

- `<label for="...">` em todos os inputs
- `aria-required="true"` em campos obrigatórios
- `aria-invalid="true"` + `role="alert"` para erros de validação
- `aria-live="polite"` na região de feedback de sucesso/erro

### 6. Armazenamento temporário

**Decisão:** `CfpService` em memória (`Map<string, SpeakerDTO>`) no NestJS.

**Alternativa futura:** migrar para TypeORM/Prisma quando houver persistência.

### 7. Dependências Nx

**Decisão:** adicionar `shared-types` como dependência implícita de `api` e `frontend` via imports TypeScript + path alias já configurado em `tsconfig.base.json`:

```json
"@cfp-platform/shared-types": ["./shared-types/src/index.ts"]
```

### 8. Testes

| Camada | Framework | O que testar |
|--------|-----------|--------------|
| API | Jest (`api/src/...spec.ts`) | Controller rejeita payload inválido com 400 |
| Frontend | Vitest-Angular (`frontend/src/...spec.ts`) | Signal inicial + botão submit desabilitado |

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| `class-validator` não instalado no `api` | Adicionar `class-validator` + `class-transformer` e habilitar `ValidationPipe` global |
| Path alias não resolve no build Webpack da API | Configurar `webpack.config.js` ou importar via build de `shared-types` |
| Versão Angular no workspace é 22, prompt menciona 21 | Padrões (standalone, Signals) são compatíveis; sem breaking changes esperados |
| Submissões em memória se perdem ao reiniciar | Aceitável para MVP; documentar em Non-Goals |

## Migration Plan

1. Implementar backend (`api/`) com endpoint e testes
2. Implementar frontend (`frontend/`) com rota e testes
3. Validar com `nx test api`, `nx test frontend`, `nx build api`, `nx build frontend`
4. Testar manualmente com `nx run-many -t serve -p api frontend`

Rollback: remover módulo CFP, rota e arquivos de teste — sem migração de dados.

## Open Questions

_(nenhuma — escopo suficientemente definido para implementação)_
