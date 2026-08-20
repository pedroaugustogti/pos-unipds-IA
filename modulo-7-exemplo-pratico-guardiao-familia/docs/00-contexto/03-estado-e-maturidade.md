# 03 — Estado atual e maturidade

## Evidências de commits (mai/2026)

### API

- Rotas Mapbox matched / recovery offline
- Hardening infra + suporte IA
- LGPD flows, SOS/device sync
- Revogação sessão ao desvincular criança
- Pedido tempo extra + notificações e-mail

### Parent app

- Rotas no mapa, release 1.5.3, CI iOS EAS
- Paywall assinatura **desabilitado**
- Features tempo de tela pendentes ocultas

### Child app

- TestFlight, offline route samples, SOS/nudge localização
- Privacy compliance App Store

### Site / backoffice / campanha

- CNPJ em páginas legais
- Suporte live + analytics Cloudflare
- Campanha 30 dias estruturada

---

## Compliance e governança

Documentos em `guardiao-familia-api/docs/`:

| Documento | Conteúdo |
|-----------|----------|
| `ripd-guardiao-familia.md` | RIPD — impacto LGPD, crianças, localização, SOS, IA |
| `ropa.md` | Registro de operações de tratamento |
| `incident-response-plan.md` | Resposta a incidentes |
| `plano-acao-por-fase-executivo.md` | Fases 1–4: legal, backend, site/BO, apps |

Tratamentos sensíveis: localização contínua, SOS com áudio, tempo de tela, dados de menores, pagamentos, analytics.

---

## Matriz de capacidades vs. maturidade

| Capacidade | API | Parent | Child | Site | BO | Maturidade |
|------------|-----|--------|-------|------|----|------------|
| Auth / família | ✅ | ✅ | ✅ | — | parcial | Alta |
| Localização / mapa | ✅ | ✅ | ✅ | — | ✅ | Alta |
| Geofences | ✅ | parcial | — | — | — | Média |
| SOS + push | ✅ | parcial | ✅ | — | ✅ | Média* |
| Tempo de tela + extra | ✅ | parcial | ✅ | — | — | Média |
| Gamificação | ✅ | — | ✅ | — | — | Média |
| IA / chat | ✅ | ✅ | — | ✅ | ✅ | Média |
| Pagamentos | ✅ | desabilitado UI | — | — | fiscal | Média |
| LGPD / compliance | ✅ | parcial | parcial | ✅ | parcial | Média-alta |
| Rebrand Vínculo | docs | — | — | parcial | — | Baixa |
| Loja / release | CI | TestFlight | TestFlight | prod | prod | Média |

\*Gap conhecido: **sons push nativos nos apps** — API pronta, apps pendentes.
