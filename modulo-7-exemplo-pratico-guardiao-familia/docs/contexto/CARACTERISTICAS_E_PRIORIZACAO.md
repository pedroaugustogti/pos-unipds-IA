# Guardião Família — Características do Projeto e Insumos para Priorização

**Gerado em:** 2026-08-19  
**Local:** `modulo-7-exemplo-pratico-guardiao-familia/docs/contexto/`  
**Fontes:** repos em `Documents/guardiao-familia`, GitHub Project #1, issues, commits e docs em `guardiao-familia-api/docs/`.

Documentos temáticos: [README](./README.md) · [01 Visão](./01-visao-e-produto.md) · [02 Arquitetura](./02-arquitetura-tecnica.md) · [03 Maturidade](./03-estado-e-maturidade.md) · [04 Board](./04-board-github-e-backlog.md) · [05 Épicos/OKRs](./05-priorizacao-epicos-okrs.md)

---

## 1. Resumo executivo

O **Guardião Família** é uma plataforma de **segurança e vínculo familiar** composta por:

- **App dos pais** — localização, mapa, cercas, SOS, tempo de tela, assistente IA, família
- **App da criança** — pareamento, ping de localização, SOS, tempo de tela, gamificação
- **API central** — NestJS com dezenas de domínios (localização, SOS, compliance LGPD, pagamentos, IA)
- **Backoffice** — suporte ao vivo, dashboard, fiscal, leads
- **Site institucional** — landing, chatbot, páginas legais (Cloudflare Pages)

Há um plano estratégico paralelo de **reposicionamento de marca** para **Vínculo / Vínculo Família** (domínio, INPI, migração), documentado em `guardiao-familia-api/docs/`.

**GitHub Project:** [Guardião Família](https://github.com/orgs/guardiaofamilia/projects/1) — **238 itens** organizados por **Ondas** (0–10).

---

## 2. Ecossistema de repositórios

| Repositório | Papel | Stack | Branch principal | Issues abertas* |
|-------------|-------|-------|------------------|-----------------|
| `guardiao-familia-api` | Backend, regras de negócio, infra docs | NestJS, TypeScript, PostgreSQL, Redis, AWS | `main` | 9 |
| `guardiao-familia-parent` | App responsáveis | Expo, React Native, Mapbox | `master` | 10 |
| `guardiao-familia-child` | App criança | Expo, React Native | `master` | 7 |
| `guardiao-familia-site` | Site + chatbot | HTML estático, Cloudflare | `main` | 25 |
| `guardiao-familia-backoffice` | Admin interno | Next.js | `master` | 25 |
| `campanha` | Marketing / mídias | JS | `main` | 0 |

\*Contagem via GitHub em ago/2026.

---

## 3. Proposta de valor e público

### Problema

Pais e responsáveis precisam **saber onde estão os filhos**, reagir a **emergências (SOS)**, definir **limites digitais (tempo de tela)** e manter **comunicação segura** — com conformidade para **dados de menores** (LGPD).

### Personas

| Persona | Superfície | Necessidades principais |
|---------|------------|-------------------------|
| Responsável legal | App parent | Mapa, alertas, geofences, SOS, tempo de tela, IA, gestão família |
| Criança/adolescente | App child | Pareamento simples, SOS discreto, rotina, conquistas |
| Operações / suporte | Backoffice | Tickets, chat, métricas, moderação |
| Visitante / lead | Site | Entender produto, pré-lançamento, chatbot |
| DPO / jurídico | API docs + compliance | RIPD, ROPA, consentimento parental |

### Diferenciais técnicos já presentes no código

- Localização com **rotas Mapbox**, sync offline de trajetos, geofences
- **SOS** com áudio, push FCM/APNs, canais críticos iOS, escalação
- **Tempo de tela** com pedido de tempo extra e decisão do responsável
- **Gamificação** (conquistas) no app criança
- **Assistente IA** e chatbot (site + suporte)
- **Compliance LGPD** — exportação, purge, retenção, consentimentos
- **Pagamentos** (Stripe + contexto fiscal/backoffice)
- **Infra AWS** documentada (Terraform, CI/CD, Sentry)

---

## 4. Arquitetura funcional (API)

Módulos NestJS identificados em `guardiao-familia-api/src/`:

| Domínio | Responsabilidade |
|---------|------------------|
| `auth`, `users`, `devices` | Autenticação, perfis, tokens push, sessões |
| `families`, `children`, `pairing`, `family-access` | Grupos familiares, pareamento pai↔criança |
| `location`, `maps`, `geofences` | GPS, histórico, rotas, reverse geocode, cercas |
| `sos`, `escalation`, `notifications` | Alertas emergência, push, e-mail, escalação |
| `screen-time` | Regras, uso, pedido de tempo extra |
| `gamification` | Conquistas e engajamento criança |
| `family-messages`, `community` | Comunicação familiar / comunidade |
| `ai`, `chatbot`, `support` | IA pais, bot site, suporte ao vivo |
| `payments`, `accounting`, `referral` | Assinatura, fiscal, indicação |
| `compliance` | LGPD, retenção, eliminação, consentimentos |
| `content`, `tutorials`, `pre-launch` | Conteúdo educativo, onboarding, lista espera |
| `analytics`, `monitoring`, `metrics`, `admin` | Métricas, admin, operação |
| `email`, `storage`, `realtime` | SES/SMTP, S3, tempo real |
| `client-config`, `system-config`, `i18n` | Config dinâmica, i18n |

Integrações externas recorrentes nos docs/código: **Mapbox**, **FCM/APNs**, **AWS (S3, RDS, Redis, SES)**, **Stripe**, **Sentry**, **Cloudflare**.

---

## 5. Apps mobile

### App pais (`guardiao-familia-parent`)

**Bundle:** `com.guardiaofamilia.parent` · **Versão recente:** 1.5.x (commits TestFlight/EAS)

Telas / áreas principais (`screens/`):

- Autenticação e onboarding (`AuthScreen`, `RegisterOnboardingScreen`, `WelcomeOnboardingScreen`)
- Mapa e localização (`MapTab`, `MapMain`, rotas matched)
- Família e pareamento (`FamilySetupWizardScreen`, `PairingCodesScreen`, `ManageChildrenSheet`, `ManageGuardiansSheet`)
- Alertas e SOS (`ParentAlertsTab`, `SosHistorySheet`)
- Tempo de tela (`ChildScreenTimeSheet`, `AppUsageSheet`)
- Assistente IA (`ParentAssistantTab`)
- Suporte (`SupportChatSheet`)
- Configuração e planos (`ParentConfigTab`, `UpgradePlanScreen` — paywall desabilitado em commits recentes)

### App criança (`guardiao-familia-child`)

**Bundle:** `com.guardiaofamilia.child` · **Versão:** 2.0.0+ (TestFlight/build iOS)

Fluxos (`screens/`):

- Pré-pareamento e permissões (`PrePairingScreen`, `PermissionsOnboardingScreen`)
- Home + SOS (`ChildHome`, `ChildHomeV2` — hold 3s, acessibilidade)
- Mapa / família (`MapMain`, estados em `childFamily.state.ts`)
- Tempo de tela (`childScreenTime.state.ts`)
- Conquistas (`childAchievements.state.ts`)
- Dashboard (`ChildDashboard`)

---

## 6. Site e backoffice

### Site (`guardiao-familia-site`)

- Landing institucional, páginas `pais.html` / `crianca.html`
- Chatbot (`chatbot.js`)
- Termos, privacidade, pré-lançamento
- Deploy **Cloudflare Pages** (`wrangler.toml`)
- CI GitHub Actions, Dependabot

### Backoffice (`guardiao-familia-backoffice`)

Evolução recente (commits):

- Board de **suporte ao vivo** com áudio
- Dashboard com **Cloudflare analytics**, latência por serviço
- Leads, fiscal (CPC), menu por **role**
- Deploy via SSM (sa-east-1)

---

## 7. Compliance e governança

Documentos de referência em `guardiao-familia-api/docs/`:

| Documento | Conteúdo |
|-----------|----------|
| `ripd-guardiao-familia.md` | RIPD — impacto LGPD, crianças, localização, SOS, IA |
| `ropa.md` | Registro de operações de tratamento |
| `incident-response-plan.md` | Resposta a incidentes |
| `plano-acao-por-fase-executivo.md` | Fases 1–4: legal, backend, site/BO, apps |
| `fase-1-decisao-executiva-aprovada.md` | Estratégia híbrida Vínculo Família → Vínculo |
| `fase-1-addendum-dominio-critico.md` | Domínios, redirects guardiao → vinculo |

Tratamentos sensíveis: localização contínua, SOS com áudio, tempo de tela, dados de menores, pagamentos, analytics.

---

## 8. Estratégia de produto / marca (contexto)

Decisão executiva (abr/2026): lançar como **Vínculo Família** (`vinculofamilia.com.br`) e migrar depois para **Vínculo** (`vinculo.com.br`) se handles `@vinculo` forem obtidos.

Implicações para backlog:

- Redirects DNS do domínio antigo
- Rebrand site + apps + stores
- Comunicação a usuários existentes
- INPI e materiais de marketing (`campanha/`)

---

## 9. Estado atual (evidências de commits — mai/2026)

### API — temas recentes

- Rotas Mapbox matched / recovery offline
- Hardening infra + suporte IA
- LGPD flows, SOS/device sync
- Revogação sessão ao desvincular criança
- Pedido tempo extra + notificações e-mail

### Parent app

- Rotas no mapa, release 1.5.3, CI iOS EAS
- Paywall assinatura **desabilitado** (commit `c64e9f4`)
- Features tempo de tela pendentes ocultas

### Child app

- TestFlight, offline route samples, SOS/nudge localização
- Privacy compliance App Store

### Site / backoffice / campanha

- CNPJ em páginas legais
- Suporte live + analytics Cloudflare
- Campanha 30 dias estruturada

---

## 10. GitHub Project #1 — Ondas de entrega

Export: [`../referencias/github-project-1.json`](../referencias/github-project-1.json)

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

Épicos visíveis no board: pedido tempo extra, apps criança/pais, backoffice, LGPD, pagamentos, SMS/WhatsApp.

---

## 11. Issues abertas relevantes

**54 issues abertas** na org. Gap crítico: **sons push nativos nos apps** (API pronta, apps pendentes).

Volume por repo: site (25), backoffice (25), parent (10), api (9), child (7).

---

## 12. Matriz de capacidades vs. maturidade

| Capacidade | API | Parent | Child | Site | BO | Maturidade estimada |
|------------|-----|--------|-------|------|----|---------------------|
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

\*Gap conhecido: sons push nativos nos apps.

---

## 13–14. Priorização, épicos e OKRs

Detalhamento completo em [`05-priorizacao-epicos-okrs.md`](./05-priorizacao-epicos-okrs.md): critérios RICE, mapeamento Ondas→Épicos, OKRs sugeridos e backlog P0–P3.

---

## 15. Como manter atualizado

```powershell
cd C:\Users\pedro\Documents\guardiao-familia
.\scripts\setup-workspace.ps1
Copy-Item docs\referencias\github-project-1.json `
  C:\Users\pedro\Documents\pos-unipds\pos-unipds-IA\modulo-7-exemplo-pratico-guardiao-familia\docs\referencias\
```

---

## 16. Referências rápidas

| Recurso | Caminho / URL |
|---------|----------------|
| Project board | https://github.com/orgs/guardiaofamilia/projects/1 |
| Plano por fases | `guardiao-familia-api/docs/plano-acao-por-fase-executivo.md` |
| RIPD | `guardiao-familia-api/docs/ripd-guardiao-familia.md` |
| Export project JSON | `docs/referencias/github-project-1.json` |
| Workspace repos | `C:\Users\pedro\Documents\guardiao-familia` |

---

*Documento para base de criação e priorização de atividades no GitHub Project e sprints de desenvolvimento.*
