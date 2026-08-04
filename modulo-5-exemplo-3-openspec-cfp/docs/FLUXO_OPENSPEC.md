# Fluxo OpenSpec — CFP Platform

Guia das fases 0–7 para construir o `cfp-platform` com OpenSpec (alinhado ao [UNIPDS modulo-03](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-03/cfp-platform)).

## Fases

| Fase | Entregável |
|------|------------|
| 0 | Scaffold Nx (`api`, `frontend`, `shared-types`) |
| 1 | `openspec init` + `config.yaml` |
| 2–5 | Changes propostas, aplicadas e arquivadas |
| 6 | Nav global, redirect, remover `nx-welcome` |
| 7 | CSS dark mode (`prompts/openspec-ui-styling.md`) |

## Workflows

```
/opsx:propose add-cfp-feature
/opsx:apply add-cfp-feature
/opsx:archive add-cfp-feature
```

## Archives de referência

- `openspec/changes/archive/2026-03-31-add-cfp-feature/`
- `openspec/changes/archive/2026-03-31-add-cfp-dashboard/`
- `openspec/changes/archive/2026-03-31-add-cypress-e2e/` (preparado para Ex. 4)

## Princípio

OpenSpec implementa **comportamento**. UI pixel-perfect exige contexto no `config.yaml` ou passo de styling (Fase 7).
