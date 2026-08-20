# Perguntas estratégicas e valores de scoring

Cada task recebe scores via respostas às perguntas abaixo (aplicadas por épico + baseline commits).

## Reach (1–10) — Quantos usuários/famílias impacta?

| Pergunta | Sim → valor |
|----------|-------------|
| Afeta 100% das famílias ativas? | 10 |
| Afeta fluxo crítico segurança (SOS/geofence)? | 9–10 |
| Afeta apenas um app (parent ou child)? | 6–7 |
| Afeta apenas backoffice/operações? | 4–5 |
| Afeta site/marketing? | 3–4 |

## Impact (0.5–3) — Quanto muda o resultado?

| Pergunta | Valor |
|----------|-------|
| Falha causa risco físico/emergência? | 3 |
| Bloqueia publicação nas stores? | 3 |
| Bloqueia compliance LGPD legal? | 3 |
| Melhora retenção/UX significativa? | 2 |
| Polish / nice-to-have? | 0.5–1 |

## Confidence (0–1) — Quão certo estamos?

| Pergunta | Valor |
|----------|-------|
| Código já mergeado (`done`)? | 0.85–0.95 |
| Parcialmente implementado (`partial`)? | 0.7–0.8 |
| Greenfield sem spike (`todo`)? | 0.5–0.65 |
| Dependência externa (Apple review)? | −0.1 |

## Effort — Story Points (Fibonacci)

| Pergunta | SP |
|----------|-----|
| Config/copy < 1 dia? | 1 |
| CRUD/tela isolada 1–2 dias? | 2–3 |
| Feature cross-layer 3–5 dias? | 5 |
| E2E cross-repo + 2 plataformas? | 8 |
| > 8 SP? | Quebrar task |

## Cost of Delay (1–13)

| Pergunta | CoD |
|----------|-----|
| Release blocker explícito? | 11–13 |
| Segurança criança sem workaround? | 10–12 |
| Infra prod sem alternativa? | 9–11 |
| Compliance mandatório? | 8–10 |
| Feature O3 com workaround? | 3–6 |
| Backlog v2? | 1–2 |

## PERT (dias)

| Tipo | O | M | P |
|------|---|---|---|
| Task pequena | 0.25 | 0.75 | 2 |
| Task média | 0.5 | 1.5 | 3 |
| Feature | 1 | 2.5 | 5 |
| Infra/AWS | 2 | 4 | 8 |

## Matriz decisão trilha

| Pergunta | Trilha |
|----------|--------|
| Usuário final vê a mudança? | produto |
| Só AWS/CI/monitoring? | infraestrutura |
| Metadata, submit, review store? | stores |

## Exemplo aplicado — T-P05-001 (Bundlar sons push iOS parent)

| Dimensão | Valor | Pergunta respondida |
|----------|-------|---------------------|
| Reach | 10 | 100% famílias — alertas SOS/geofence |
| Impact | 3 | Falha SOS silencioso = risco |
| Confidence | 0.7 | API pronta; app pendente |
| Effort | 3 SP | Bundle + teste ~1.5d |
| CoD | 11 | Blocker KR3 O1 |
| Release blocker | yes | Sem som nativo, review reprova |
