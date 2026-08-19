# 02 — Arquitetura técnica

## Ecossistema de repositórios

| Repositório | Papel | Stack | Branch principal | Issues abertas* |
|-------------|-------|-------|------------------|-----------------|
| `guardiao-familia-api` | Backend, regras de negócio, infra docs | NestJS, TypeScript, PostgreSQL, Redis, AWS | `main` | 9 |
| `guardiao-familia-parent` | App responsáveis | Expo, React Native, Mapbox | `master` | 10 |
| `guardiao-familia-child` | App criança | Expo, React Native | `master` | 7 |
| `guardiao-familia-site` | Site + chatbot | HTML estático, Cloudflare | `main` | 25 |
| `guardiao-familia-backoffice` | Admin interno | Next.js | `master` | 25 |
| `campanha` | Marketing / mídias | JS | `main` | 0 |

\*Contagem via GitHub em ago/2026.

Clone local: `C:\Users\pedro\Documents\guardiao-familia`

---

## Arquitetura funcional (API)

Módulos NestJS em `guardiao-familia-api/src/`:

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

Integrações: **Mapbox**, **FCM/APNs**, **AWS (S3, RDS, Redis, SES)**, **Stripe**, **Sentry**, **Cloudflare**.

---

## Apps mobile

### App pais (`guardiao-familia-parent`)

**Bundle:** `com.guardiaofamilia.parent` · **Versão recente:** 1.5.x

Telas principais: autenticação/onboarding, mapa, família/pareamento, alertas/SOS, tempo de tela, assistente IA, suporte, configuração/planos.

### App criança (`guardiao-familia-child`)

**Bundle:** `com.guardiaofamilia.child` · **Versão:** 2.0.0+

Fluxos: pré-pareamento, home+SOS (hold 3s), mapa/família, tempo de tela, conquistas, dashboard.

---

## Site e backoffice

### Site (`guardiao-familia-site`)

Landing, páginas pais/criança, chatbot, termos/privacidade, pré-lançamento. Deploy **Cloudflare Pages**.

### Backoffice (`guardiao-familia-backoffice`)

Suporte ao vivo com áudio, dashboard Cloudflare analytics, leads, fiscal (CPC), menu por role. Deploy via SSM (sa-east-1).
