"""Refinamento de tasks: contexto, arquivos sugeridos e hints de implementação."""

from __future__ import annotations

import re
from typing import Any

REPOS_BASE = r"C:\Users\pedro\Documents\guardiao-familia"

# Módulos/pastas base por épico (repo relativo)
EPIC_PATHS: dict[str, list[str]] = {
    "E-P01": ["src/auth", "src/users", "src/devices", "src/pairing", "src/families"],
    "E-P02": ["src/location", "src/maps", "src/modules/mapbox"],
    "E-P03": ["src/geofences", "src/notifications", "src/location"],
    "E-P04": ["src/sos", "src/escalation", "src/notifications", "src/storage"],
    "E-P05": ["src/notifications", "src/devices", "assets/sounds", "app.config.js"],
    "E-P06": ["src/screen-time", "src/notifications", "src/email"],
    "E-P07": ["src/gamification", "app/(tabs)", "components/achievements"],
    "E-P08": ["src/families", "src/family-messages", "src/family-access"],
    "E-P09": ["app/(tabs)/map", "app/(tabs)/reports", "src/ai", "components/map"],
    "E-P10": ["app", "components", "hooks", "services/api"],
    "E-P11": ["src/compliance", "src/users", "docs/lgpd"],
    "E-P12": ["app", "components", "pages/api", "lib"],
    "E-P13": ["public", "pages", "chatbot", "index.html"],
    "E-I01": ["infra/terraform", "terraform/ecs", "docker", "docs/runbooks"],
    "E-I02": [".github/workflows", "scripts/deploy", "eas.json"],
    "E-I03": ["src/monitoring", "src/metrics", "sentry.config", ".github/workflows"],
    "E-I04": ["src/migrations", "src/database", "prisma", "docker-compose.yml"],
    "E-I05": ["infra/terraform/waf", "infra/secrets", "src/config"],
    "E-I06": ["infra/terraform/environments", "docs/runbooks", ".env.example"],
    "E-S01": ["app.config.js", "ios", "eas.json", "docs/store/apple-parent"],
    "E-S02": ["app.config.js", "ios", "eas.json", "docs/store/apple-child"],
    "E-S03": ["app.config.js", "android", "eas.json", "docs/store/google-parent"],
    "E-S04": ["app.config.js", "android", "eas.json", "docs/store/google-child"],
    "E-S05": ["docs/release", "CHANGELOG.md", ".github/workflows/release"],
}

# Keywords -> paths adicionais (qualquer épico)
KEYWORD_PATHS: list[tuple[re.Pattern, list[str]]] = [
    (re.compile(r"terraform|vpc|ecs|fargate|alb|ecr|route53|acm", re.I),
     ["infra/terraform", "terraform/modules"]),
    (re.compile(r"migration|postgres|rds|redis|schema", re.I),
     ["src/migrations", "src/database"]),
    (re.compile(r"CI/?CD|pipeline|workflow|github actions|deploy", re.I),
     [".github/workflows", "scripts/ci"]),
    (re.compile(r"teste|test|e2e|spec", re.I),
     ["test", "tests", "__tests__", "e2e"]),
    (re.compile(r"push|fcm|apns|notifica", re.I),
     ["src/notifications", "src/devices", "services/push"]),
    (re.compile(r"mapbox|mapa|rota|location|gps", re.I),
     ["src/location", "src/maps", "components/map", "services/location"]),
    (re.compile(r"geofence|cerca", re.I),
     ["src/geofences", "components/geofence"]),
    (re.compile(r"\bsos\b|emerg", re.I),
     ["src/sos", "src/escalation", "components/sos"]),
    (re.compile(r"auth|login|jwt|token|sess", re.I),
     ["src/auth", "services/auth", "contexts/AuthContext"]),
    (re.compile(r"pareamento|pairing|qr", re.I),
     ["src/pairing", "app/pairing", "screens/Pairing"]),
    (re.compile(r"tempo de tela|screen.?time|extra.?time", re.I),
     ["src/screen-time", "app/screen-time"]),
    (re.compile(r"store|app store|google play|submit|release", re.I),
     ["eas.json", "app.config.js", "docs/store", "fastlane"]),
    (re.compile(r"backoffice|admin", re.I),
     ["app/admin", "components/admin", "pages"]),
    (re.compile(r"chatbot|site|landing", re.I),
     ["chatbot", "public", "index.html"]),
    (re.compile(r"LGPD|compliance|privacidade", re.I),
     ["src/compliance", "docs/lgpd", "privacy"]),
    (re.compile(r"sentry|observ|monitor|alert", re.I),
     ["src/monitoring", "sentry.config.js", ".github/workflows"]),
    (re.compile(r"iOS|apple", re.I),
     ["ios", "app.config.js"]),
    (re.compile(r"android", re.I),
     ["android", "app.config.js"]),
]

REPO_DEFAULTS: dict[str, list[str]] = {
    "guardiao-familia-api": ["src", "test", "infra"],
    "guardiao-familia-parent": ["app", "components", "services", "assets"],
    "guardiao-familia-child": ["app", "components", "services", "assets"],
    "guardiao-familia-backoffice": ["app", "components", "lib", "pages"],
    "guardiao-familia-site": ["public", "pages", "chatbot"],
}

OKR_CONTEXT = {
    "O1": "Confiabilidade em tempo real: localização, SOS, push e geofences para pais.",
    "O2": "Fundação produção: infra AWS, compliance, stores e operação.",
    "O3": "Experiência familiar: auth, tempo de tela, gamificação e engajamento.",
}

TRACK_CONTEXT = {
    "produto": "Feature E2E — alterações em API e/ou apps conforme repo.",
    "infraestrutura": "AWS, CI/CD, banco, observabilidade — priorizar IaC e runbooks.",
    "stores": "Publicação App Store / Google Play — versões, review notes, checklist.",
}

EPIC_BLOCKER_REASON: dict[str, str] = {
    "E-I01": "Fundação AWS (VPC, ECS, ALB, DNS/TLS) bloqueia deploy produção da API e validação E2E real.",
    "E-I04": "Plataforma de dados (RDS + Redis + backups) é pré-requisito para staging/prod e fluxos produto.",
    "E-I05": "Segurança pré-release (pen test) é gate obrigatório antes de submit nas stores.",
    "E-I06": "Cutover produção depende de infra + dados + checklist operacional completo.",
    "E-P03": "E2E geofence depende de push nativo (E-P05) e localização (E-P02) estáveis.",
    "E-P04": "SOS <30s é KR O1 — requer push nativo configurado e infra prod.",
    "E-P05": "Push com sons customizados é upstream de SOS E2E, geofences e alertas críticos.",
    "E-P11": "DPO sign-off LGPD é gate legal antes de publicação nas stores.",
    "E-S01": "Submit App Store parent exige compliance, push, SOS e review notes aprovados.",
    "E-S02": "Submit App Store child exige parental gate, polish e dependências produto.",
    "E-S03": "Production Google Play parent depende de data safety, testes e infra prod.",
    "E-S04": "Production Google Play child depende de families policy e testes internos.",
    "E-S05": "Coordenação release — checklist consolidado e sync de versões bloqueiam go-live.",
}

TITLE_BLOCKER_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"version sync|rollback store", re.I),
     "Matriz de versão e plano de rollback são obrigatórios para release coordenado das 4 apps."),
    (re.compile(r"checklist release blocker", re.I),
     "Consolida todos os release blockers técnicos e de compliance antes do go-live."),
    (re.compile(r"submit production|production rollout", re.I),
     "Publicação nas stores — rejeição ou delay bloqueia receita e KR O2."),
    (re.compile(r"review notes", re.I),
     "Apple rejeita apps com background location sem review notes adequadas."),
    (re.compile(r"push.*SOS|SOS.*<30", re.I),
     "KR O1: notificação SOS ao responsável em menos de 30 segundos."),
    (re.compile(r"geofence.*E2E|cerca E2E|entrada/saída cerca", re.I),
     "KR O1: alerta entrada/saída de cerca validado ponta a ponta."),
    (re.compile(r"sons push|Bundlar sons|push SOS som", re.I),
     "Upstream: apps precisam de assets de som no bundle antes dos testes E2E push."),
    (re.compile(r"DPO sign", re.I),
     "Gate legal LGPD — obrigatório antes de release público."),
    (re.compile(r"Pen test", re.I),
     "Checklist segurança pré-release exigido pela política O2."),
    (re.compile(r"cutover", re.I),
     "Migração staging→prod — erro causa downtime ou perda de dados."),
    (re.compile(r"Terraform|ECS|ALB|Route53|ACM|ECR|Secrets Manager", re.I),
     "Componente crítico da fundação AWS — sem ele não há ambiente prod confiável."),
    (re.compile(r"RDS|Redis|Backup|PITR|Migration strategy|Índices performance", re.I),
     "Capacidade de dados em prod — bloqueia cutover e testes de carga reais."),
]


def is_release_blocker(item: dict) -> bool:
    f = item.get("fields", {})
    if f.get("Release Blocker") == "yes":
        return True
    return bool(item.get("release_blocker"))


def blocker_reason(item: dict) -> str:
    if not is_release_blocker(item):
        return ""
    title = item.get("title", "")
    for pattern, reason in TITLE_BLOCKER_PATTERNS:
        if pattern.search(title):
            return reason
    epic_id = _epic_id_from_item(item)
    return EPIC_BLOCKER_REASON.get(
        epic_id,
        "Critério bloqueante para release produção (KR O1/O2).",
    )


def _epic_id_from_item(item: dict) -> str:
    epic = item.get("fields", {}).get("Epic", "") or item.get("epic_id", "")
    m = re.match(r"(E-[A-Z0-9]+)", str(epic))
    return m.group(1) if m else ""


def suggest_files(item: dict) -> list[str]:
    epic_id = _epic_id_from_item(item)
    repo = item.get("repository") or item.get("repo", "")
    title = item.get("title", "")
    paths: list[str] = []

    paths.extend(EPIC_PATHS.get(epic_id, []))
    for pattern, extras in KEYWORD_PATHS:
        if pattern.search(title):
            paths.extend(extras)

    if not paths:
        paths.extend(REPO_DEFAULTS.get(repo, ["src"]))

    # prefixo repo
    seen: set[str] = set()
    out: list[str] = []
    for p in paths:
        full = f"{repo}/{p}" if repo and not p.startswith(repo) else p
        if full not in seen:
            seen.add(full)
            out.append(full)
    return out[:8]


def context_summary(item: dict) -> str:
    f = item.get("fields", {})
    epic = f.get("Epic", item.get("epic_name", ""))
    trilha = f.get("Trilha", item.get("track", ""))
    okr = f.get("OKR", item.get("okr", ""))
    sprint = f.get("Sprint", item.get("sprint", ""))
    baseline = f.get("Baseline", item.get("status_baseline", "todo"))
    blocker = f.get("Release Blocker", "no")
    repo = item.get("repository") or item.get("repo", "")
    title = item.get("title", "")
    commit = item.get("commit_evidence", "")

    parts = [
        f"**Objetivo:** {title}",
        f"**Épico:** {epic} · **Trilha:** {trilha} · **OKR {okr}** — {OKR_CONTEXT.get(okr, '')}",
        f"**Sprint {sprint}** · Repo `{repo}` · Baseline `{baseline}`"
        + (" · **Release blocker**" if blocker == "yes" or item.get("release_blocker") else ""),
    ]
    if commit:
        parts.append(f"**Evidência código:** commit `{commit}` — revisar diff como ponto de partida.")
    reason = blocker_reason(item)
    if reason:
        parts.append(f"**Motivo blocker:** {reason}")
    if baseline == "partial":
        parts.append("**Refinamento:** implementação parcial existente — completar gaps e testes.")
    elif baseline == "done":
        parts.append("**Refinamento:** baseline done — validar regressão ou documentar.")
    else:
        parts.append(f"**Refinamento:** {TRACK_CONTEXT.get(trilha, 'Implementar do zero conforme critérios.')}")

    return "\n".join(parts)


def acceptance_hints(item: dict) -> list[str]:
    title = (item.get("title") or "").lower()
    hints: list[str] = []
    if "e2e" in title or "teste" in title:
        hints.append("Cobertura reproduzível em CI; documentar comando de execução.")
    if "document" in title or "runbook" in title:
        hints.append("Entregável em markdown no repo; linkar no PR.")
    if "ios" in title:
        hints.append("Validar em simulador/dispositivo iOS; permissoes no Info.plist.")
    if "android" in title:
        hints.append("Validar em emulador/dispositivo Android; data safety se stores.")
    if item.get("fields", {}).get("Release Blocker") == "yes":
        hints.append("Critério bloqueante release — exigir review + testes antes merge.")
    if not hints:
        hints.append("PR com estrategia, arquivos alterados e duvidas (template 10-agents).")
    return hints


def refine_item(item: dict) -> dict[str, Any]:
    files = suggest_files(item)
    return {
        "context_summary": context_summary(item),
        "suggested_files": files,
        "acceptance_hints": acceptance_hints(item),
        "blocker_reason": blocker_reason(item),
    }


def format_refinement_markdown(item: dict, refinement: dict | None = None) -> str:
    r = refinement or refine_item(item)
    files_md = "\n".join(f"- `{p}`" for p in r["suggested_files"])
    hints_md = "\n".join(f"- {h}" for h in r["acceptance_hints"])
    blocker_md = ""
    if r.get("blocker_reason"):
        blocker_md = f"\n### Motivo release blocker\n- {r['blocker_reason']}\n"
    return f"""## Refinamento

{r["context_summary"]}
{blocker_md}
### Arquivos sugeridos
{files_md}

### Critérios de aceite
{hints_md}
"""


def build_issue_body(item: dict) -> str:
    f = item.get("fields", {})
    body = (
        f"**Task ID:** {item['id']}\n"
        f"**Trilha:** {f.get('Trilha', '')}\n"
        f"**OKR:** {f.get('OKR', '')}\n"
        f"**Epic:** {f.get('Epic', '')}\n"
        f"**Sprint:** S{f.get('Sprint', '')}\n"
        f"**SP:** {f.get('Story Points', '')} | RICE: {f.get('RICE Score', '')} | WSJF: {f.get('WSJF', '')}\n"
        f"**Baseline:** {f.get('Baseline', '')} | Blocker: {f.get('Release Blocker', '')}\n"
        f"**Repo:** {item.get('repository', '')}\n"
    )
    reason = f.get("Blocker Motivo") or blocker_reason(item)
    if reason and f.get("Release Blocker") == "yes":
        body += f"**Motivo blocker:** {reason}\n"
    if item.get("commit_evidence"):
        body += f"**Commit:** `{item['commit_evidence']}`\n"
    body += "\n---\n\n"
    body += format_refinement_markdown(item)
    return body
