# 01 — Visão e produto

## Resumo executivo

O **Guardião Família** é uma plataforma de **segurança e vínculo familiar** composta por:

- **App dos pais** — localização, mapa, cercas, SOS, tempo de tela, assistente IA, família
- **App da criança** — pareamento, ping de localização, SOS, tempo de tela, gamificação
- **API central** — NestJS com dezenas de domínios (localização, SOS, compliance LGPD, pagamentos, IA)
- **Backoffice** — suporte ao vivo, dashboard, fiscal, leads
- **Site institucional** — landing, chatbot, páginas legais (Cloudflare Pages)

Há um plano estratégico paralelo de **reposicionamento de marca** para **Vínculo / Vínculo Família** (domínio, INPI, migração), documentado em `guardiao-familia-api/docs/`.

**GitHub Project:** [Guardião Família](https://github.com/orgs/guardiaofamilia/projects/1) — **238 itens** organizados por **Ondas** (0–10).

---

## Proposta de valor e público

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

## Estratégia de produto / marca

Decisão executiva (abr/2026): lançar como **Vínculo Família** (`vinculofamilia.com.br`) e migrar depois para **Vínculo** (`vinculo.com.br`) se handles `@vinculo` forem obtidos.

Implicações para backlog:

- Redirects DNS do domínio antigo
- Rebrand site + apps + stores
- Comunicação a usuários existentes
- INPI e materiais de marketing (`campanha/`)

**Referências:** `guardiao-familia-api/docs/fase-1-decisao-executiva-aprovada.md`, `fase-1-addendum-dominio-critico.md`
