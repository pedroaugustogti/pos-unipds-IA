# 05 — Priorização, épicos e OKRs

Insumos para definir **épicos**, **OKRs** e **divisão de atividades** no GitHub Project e sprints.

---

## Critérios de priorização

Ordem sugerida ao criar/refinar cards:

1. **Segurança da criança** — SOS, push confiável, localização, escalação
2. **Conformidade LGPD** — consentimento, menores, RIPD pendências
3. **Fluxo ponta a ponta** — feature só conta se API + app relevante + push
4. **Bloqueio de release** — TestFlight/Play, privacy, assets nativos
5. **Monetização** — reativar paywall quando fluxo estável
6. **Rebrand Vínculo** — após estabilidade operacional
7. **Polish / Onda 10** — performance, UX, analytics

### Framework RICE

| Fator | Pergunta |
|-------|----------|
| **Reach** | Quantas famílias/crianças afeta? |
| **Impact** | Reduz risco (SOS) ou churn? |
| **Confidence** | API pronta? Apps consomem? |
| **Effort** | Quantos repos (API+parent+child)? |

---

## Sugestão de épicos (mapeamento Ondas → épicos)

| Épico | Onda(s) | Escopo | Repos |
|-------|---------|--------|-------|
| E1 — Fundação e release | 0, 10 | CI/CD, infra, polish release | api, todos |
| E2 — Identidade e família | 1, 8 | Auth, pairing, gestão família | api, parent, child |
| E3 — Localização e cercas | 2, 3 | GPS, geofences, tempo real | api, parent |
| E4 — SOS e emergência | 4 | SOS E2E, push, escalação | api, parent, child |
| E5 — Tempo de tela | 5 | Regras, pedido extra, UX | api, parent, child |
| E6 — Engajamento criança | 6 | Gamificação, conquistas | api, child |
| E7 — IA e conteúdo | 7 | Assistente pais, chatbot site | api, parent, site |
| E8 — Monetização e admin | 9 | Stripe, backoffice fiscal | api, parent, backoffice |
| E9 — Compliance LGPD | transversal | RIPD, consentimentos, purge | api, apps, site |
| E10 — Rebrand Vínculo | estratégico | Domínio, copy, stores | site, campanha, apps |

---

## OKRs sugeridos (exemplo trimestre)

### O1 — Garantir segurança confiável da criança

| KR | Meta |
|----|------|
| KR1 | SOS E2E validado (criança → push → pai) em iOS e Android |
| KR2 | Geofence alert E2E com notificação em < 30s |
| KR3 | Sons push nativos bundlados e validados nos dois apps |

### O2 — Conformidade e prontidão para escala

| KR | Meta |
|----|------|
| KR1 | Fluxos LGPD críticos auditados (consentimento parental, purge) |
| KR2 | Builds publicáveis nas stores (privacy, assets, CI verde) |
| KR3 | Backoffice suporte live estável em produção |

### O3 — Experiência familiar completa

| KR | Meta |
|----|------|
| KR1 | Pedido tempo extra E2E (criança pede → pai decide) |
| KR2 | App criança Onda 5/6 com UX polida |
| KR3 | App pais com relatórios + assistente IA utilizável |

---

## Backlog priorizado (P0–P3)

### P0 — Crítico (1–2 sprints)

1. Bundling sons push nos apps parent/child
2. Validação E2E SOS
3. Geofence alert E2E
4. Pedido tempo extra E2E

### P1 — Alto (2–4 sprints)

5. App criança — polish Onda 5/6
6. App pais — relatórios + IA
7. Backoffice suporte — estabilizar board live
8. Release stores (Play + App Store)

### P2 — Médio

9. Reativar monetização (paywall parent)
10. Site — reduzir 25 issues (SEO, CWV, Vínculo)
11. SMS/WhatsApp escalação
12. Rebrand Vínculo Fase 1

### P3 — Estratégico

13. Comunidade familiar (Onda 8)
14. Educação digital / trilhas
15. Microserviços Java/K8s (exploratório)

---

## Divisão de atividades (template)

Ao quebrar um épico em stories/tasks:

| Campo | Pergunta |
|-------|----------|
| Repo | api / parent / child / site / backoffice |
| Onda | 0–10 do Project |
| Tipo | feature / bug / compliance / infra |
| E2E? | Precisa validar fluxo completo? |
| Bloqueia release? | Sim/Não |
| Dependência | Issue/card upstream |

Exemplo — *Bundling sons push*:

- **parent:** adicionar `.wav` ao bundle, testar FCM payload
- **child:** idem
- **api:** já pronta — apenas validação integrada
- **Critério de done:** SOS e geofence disparam som customizado no dispositivo físico
