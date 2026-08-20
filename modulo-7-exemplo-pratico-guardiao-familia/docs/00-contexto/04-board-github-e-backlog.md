# 04 — GitHub Project e backlog

## GitHub Project #1 — Ondas de entrega

**Board:** https://github.com/orgs/guardiaofamilia/projects/1  
**Export JSON:** [`../referencias/github-project-1.json`](../referencias/github-project-1.json)

**Total de itens:** 238 · **Campos:** Status (Todo / In Progress / Done), **Onda** (0–10)

| Onda | Foco | Qtd (amostra) |
|------|------|---------------|
| Onda 0 | Fundação (infra, DB, CI/CD) | 15 |
| Onda 1 | Auth / Pairing | 3 |
| Onda 2 | Real-time | 4 |
| Onda 3 | GPS / Geofences | 6 |
| Onda 4 | SOS / Emergência | 2 |
| Onda 5 | Screen Time | 5 |
| Onda 6 | Gamificação | 2 |
| Onda 7 | AI / Conteúdo | 2 |
| Onda 8 | Família / Comunidade | 6 |
| Onda 9 | Pagamentos / Admin | 9 |
| Onda 10 | Polish / Release | 6 |

### Épicos visíveis no board

- Implementar pedido de tempo extra
- App criança: Home+SOS, Mapa+Família, Tempo de Tela+Conquistas
- App pais: Chat IA + Relatórios
- Backoffice: Dashboard, Moderação, Analytics
- LGPD, Stripe+Asaas, SMS/WhatsApp escalação

> Export GraphQL retorna 100 itens/página. Atualize via script em `Documents/guardiao-familia/scripts/`.

---

## Issues abertas (ago/2026)

**54 issues abertas** na org.

| Repo | Issues |
|------|--------|
| site | 25 |
| backoffice | 25 |
| parent | 10 |
| api | 9 |
| child | 7 |

### Gap crítico

**Push / sons nativos nos apps** — API envia payloads FCM com sons customizados (`sos_alert`, `geofence_alert`) e expõe `GET /notifications/config`, mas apps precisam bundlar `.wav` no APK/IPA.
