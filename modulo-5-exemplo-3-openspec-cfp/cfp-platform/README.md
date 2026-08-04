# CFP Platform — Nx Monorepo

Monorepo **Call for Papers** gerado com Nx + OpenSpec. Código alinhado ao [cfp-platform UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-03/cfp-platform).

Guia completo do fluxo OpenSpec (fases 0–7): [`../docs/FLUXO_OPENSPEC.md`](../docs/FLUXO_OPENSPEC.md)

## Apps

| Projeto | Stack | Porta |
|---------|-------|-------|
| `api` | NestJS 11 | 3000 |
| `frontend` | Angular 21 standalone | 4200 |
| `shared-types` | TypeScript lib | — |

## Comandos

```bash
npm install

# Testes
npx nx test api
npx nx test frontend

# Desenvolvimento (API + frontend)
npx nx run-many -t serve -p api frontend

# Build
npx nx build api
npx nx build frontend
```

## Rotas (frontend)

| Rota | Componente |
|------|------------|
| `/dashboard` | `CfpDashboardComponent` (home) |
| `/talks/new` | `CfpSubmissionComponent` |
| `/event/new` | `EventRegistrationComponent` |

## API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/speakers` | Submeter palestra |
| `GET` | `/api/speakers` | Listar submissões |
| `POST` | `/api/events` | Cadastrar evento |

## OpenSpec

```bash
openspec list                    # changes ativas
openspec list --specs            # specs canônicas
```

Estrutura:

```
openspec/
├── config.yaml                  # contexto do projeto (rotas, nomes, UI)
├── specs/
│   ├── cfp-submission/spec.md
│   └── cfp-dashboard/spec.md
└── changes/archive/             # histórico de changes implementadas
```

Workflows do agente: `.agent/workflows/` (`opsx-propose`, `opsx-apply`, `opsx-archive`)

Config MCP Nx: `.cursor/mcp.json`

## OpenSpec — reproduzir uma change

1. Abrir workspace em `cfp-platform`
2. `/opsx:propose <nome-change>`
3. Revisar `proposal.md`, `design.md`, `tasks.md`
4. `/opsx:apply <nome-change>`
5. `/opsx:archive <nome-change>`

Referência de artefatos: `openspec/changes/archive/2026-03-31-add-cfp-feature/`

## UI

O formulário em `/talks/new` usa dark mode + glassmorphism. O CSS não vem automaticamente do `apply` — ver Fase 7 em [`../docs/FLUXO_OPENSPEC.md`](../docs/FLUXO_OPENSPEC.md) e `../prompts/openspec-ui-styling.md`.
