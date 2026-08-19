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
    }


def format_refinement_markdown(item: dict, refinement: dict | None = None) -> str:
    r = refinement or refine_item(item)
    files_md = "\n".join(f"- `{p}`" for p in r["suggested_files"])
    hints_md = "\n".join(f"- {h}" for h in r["acceptance_hints"])
    return f"""## Refinamento

{r["context_summary"]}

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
    if item.get("commit_evidence"):
        body += f"**Commit:** `{item['commit_evidence']}`\n"
    body += "\n---\n\n"
    body += format_refinement_markdown(item)
    return body
