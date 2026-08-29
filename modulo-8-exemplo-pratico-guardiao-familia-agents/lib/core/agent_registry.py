"""Registro de agentes, repos, stack e roteamento (LangGraph + TASK_AGENT_MAP)."""

from __future__ import annotations

import re
from typing import Any

from lib.core.repo_paths import DEFAULT_PATHS, REPO_ENV, github_repo_url, resolve_repo_path
from board_automation.board.reviewer_pairs import LEGACY_QA_ROLE, normalize_creator_role

GUARDAO_ROOT = r"C:\Users\pedro\Documents\guardiao-familia"

QA_PATTERN = re.compile(r"\b(teste|test|e2e|spec|qa|coverage)\b", re.I)
DB_PATTERN = re.compile(r"\b(migration|postgres|redis|schema|rds|elasticache)\b", re.I)
DEVOPS_PATTERN = re.compile(
    r"\b(ci/?cd|pipeline|github actions|sentry|observabilidade|workflow|alertas|ecr|ecs fargate)\b",
    re.I,
)
TERRAFORM_PATTERN = re.compile(r"\b(terraform|vpc|alb|route53|acm|waf|fargate)\b", re.I)

DEVOPS_EPICS = {"E-I02", "E-I03"}
DB_EPIC = "E-I04"
INFRA_EPICS = {"E-I01", "E-I05", "E-I06"}

MOBILE_REPOS = frozenset({"guardiao-familia-parent", "guardiao-familia-child"})
WEB_REPOS = frozenset({"guardiao-familia-backoffice", "guardiao-familia-site"})
API_REPO = "guardiao-familia-api"

# Perfis: repos primários, tracks, stack resumida
AGENT_PROFILES: dict[str, dict[str, Any]] = {
    "backend": {
        "label": "Backend API",
        "repos": {API_REPO},
        "tracks": {"produto"},
        "stack": "NestJS, TypeScript, Node 22, PostgreSQL, Redis, TypeORM, Swagger",
        "path_hint": f"{GUARDAO_ROOT}\\guardiao-familia-api",
        "branch": "main",
    },
    "frontend-mobile": {
        "label": "Mobile Expo/RN",
        "repos": MOBILE_REPOS,
        "tracks": {"produto"},
        "stack": "Expo, React Native, TypeScript, Mapbox, FCM/APNs, Appium E2E",
        "path_hint": f"{GUARDAO_ROOT}\\guardiao-familia-{{parent|child}}",
        "branch": "master",
    },
    "frontend-web": {
        "label": "Web backoffice + site",
        "repos": WEB_REPOS,
        "tracks": {"produto"},
        "stack": "Next.js (backoffice), HTML/JS (site), Cloudflare Pages, Playwright",
        "path_hint": f"{GUARDAO_ROOT}\\guardiao-familia-{{backoffice|site}}",
        "branch": "master|main",
    },
    "cloud-infra": {
        "label": "Cloud AWS / Terraform",
        "repos": {API_REPO},
        "tracks": {"infraestrutura"},
        "paths": ["infra/terraform", "infra/environments", "infra/modules"],
        "stack": "Terraform, ECS Fargate, VPC, ALB, ECR, Route53, ACM, Secrets Manager",
        "path_hint": f"{GUARDAO_ROOT}\\guardiao-familia-api\\infra",
        "branch": "main",
    },
    "database": {
        "label": "PostgreSQL / Redis / migrations",
        "repos": {API_REPO},
        "tracks": {"produto", "infraestrutura"},
        "paths": ["src/database", "migrations"],
        "stack": "PostgreSQL 15 + pgvector, Redis 7, TypeORM migrations",
        "path_hint": f"{GUARDAO_ROOT}\\guardiao-familia-api",
        "branch": "main",
    },
    "devops-cicd": {
        "label": "CI/CD e observabilidade",
        "repos": {API_REPO, *MOBILE_REPOS, *WEB_REPOS},
        "tracks": {"infraestrutura", "produto"},
        "paths": [".github/workflows"],
        "stack": "GitHub Actions, OIDC AWS, ECR, ECS deploy, Sentry, PagerDuty, OTel",
        "path_hint": "workflows em cada repo; foco API",
        "branch": "main|master",
    },
    "qa-author": {
        "label": "Autor de testes (harness/specs)",
        "repos": {API_REPO, *MOBILE_REPOS, *WEB_REPOS},
        "tracks": {"produto", "infraestrutura", "stores"},
        "stack": "Jest/Supertest (API), Appium (mobile), Playwright (web)",
        "path_hint": "guardiao-familia-mobile-setup/appium/ (GUARDAO_MOBILE_SETUP_PATH)",
        "branch": "main|master",
    },
    "qa-gate": {
        "label": "QA gate (pipeline)",
        "repos": {API_REPO, *MOBILE_REPOS, *WEB_REPOS},
        "tracks": set(),
        "stack": "Playwright, Appium, smoke API — evidências na issue",
        "path_hint": "lib/qa_playwright.py, lib/qa_mobile.py (orquestrador)",
        "branch": "n/a",
        "pipeline_only": True,
    },
    "stores-release": {
        "label": "App Store / Google Play",
        "repos": MOBILE_REPOS | {API_REPO},
        "tracks": {"stores"},
        "stack": "EAS, Fastlane, App Store Connect, Play Console",
        "path_hint": f"{GUARDAO_ROOT}\\guardiao-familia-{{parent|child}}",
        "branch": "master",
    },
}

# Mapa legado CSV qa -> qa-author
AGENT_PROFILES["qa"] = AGENT_PROFILES["qa-author"]

REDIRECT_HINTS: dict[str, str] = {
    "backend": "API NestJS, endpoints, services, webhooks",
    "frontend-mobile": "apps parent/child Expo",
    "frontend-web": "backoffice Next.js ou site estático",
    "cloud-infra": "Terraform/AWS (sem apply OKR)",
    "database": "migrations PostgreSQL/Redis",
    "devops-cicd": "GitHub Actions, deploy ECR/ECS",
    "qa-author": "specs, harness, cobertura de testes",
    "qa-gate": "gate Ready for Test / In Test",
    "stores-release": "submit stores, metadata, rollout",
}


def _task_field(task: dict[str, Any], *keys: str, default: str = "") -> str:
    fields = task.get("fields") if isinstance(task.get("fields"), dict) else {}
    for key in keys:
        val = task.get(key) or fields.get(key)
        if val:
            return str(val).strip()
    return default


def classify_task(task: dict[str, Any]) -> tuple[str, str, str]:
    """Classifica task → (agent_role, secondary, reason). Mesma lógica do TASK_AGENT_MAP."""
    track = _task_field(task, "track", "Track")
    epic = _task_field(task, "epic_id", "Epic")
    repo = _task_field(task, "repo", "repository", "Repo alvo")
    title = _task_field(task, "title", default=task.get("id") or "")

    if track == "stores":
        sec = "frontend-mobile" if repo in MOBILE_REPOS else ""
        return "stores-release", sec, f"track=stores,repo={repo}"

    if QA_PATTERN.search(title):
        if repo in MOBILE_REPOS:
            return "qa", "frontend-mobile", f"qa+mobile,repo={repo}"
        if repo == API_REPO:
            return "qa", "backend", f"qa+api,repo={repo}"
        return "qa", "", f"qa,repo={repo}"

    if epic == DB_EPIC or DB_PATTERN.search(title):
        sec = "cloud-infra" if track == "infraestrutura" else "backend"
        return "database", sec, f"db,epic={epic}"

    if epic in DEVOPS_EPICS or DEVOPS_PATTERN.search(title):
        return "devops-cicd", "", f"devops,epic={epic}"

    if track == "infraestrutura" or epic in INFRA_EPICS:
        sec = "database" if DB_PATTERN.search(title) else ""
        return "cloud-infra", sec, f"infra,epic={epic}"

    if repo in MOBILE_REPOS:
        sec = "qa" if QA_PATTERN.search(title) else ""
        return "frontend-mobile", sec, f"mobile,repo={repo}"

    if repo in WEB_REPOS:
        return "frontend-web", "", f"web,repo={repo}"

    if repo == API_REPO and track == "produto":
        sec = "qa" if "integração" in title.lower() or "integracao" in title.lower() else ""
        return "backend", sec, f"api produto"

    return "backend", "", "default api/backend"


def agent_handles_repo(role: str, repo: str) -> bool:
    role = normalize_creator_role(role)
    profile = AGENT_PROFILES.get(role)
    if not profile or profile.get("pipeline_only"):
        return False
    repos = profile.get("repos") or set()
    if not repo:
        return True
    return repo in repos


def agent_handles_task(role: str, task: dict[str, Any]) -> bool:
    role = normalize_creator_role(role)
    if role == "qa-gate":
        return True

    classified, secondary, _ = classify_task(task)
    classified = normalize_creator_role(classified)
    secondary_n = normalize_creator_role(secondary) if secondary else ""
    if role in (classified, secondary_n):
        return True

    profile = AGENT_PROFILES.get(role)
    if not profile or profile.get("pipeline_only"):
        return False

    repo = _task_field(task, "repo", "repository", "Repo alvo")
    track = _task_field(task, "track", "Track")
    repos = profile.get("repos") or set()
    tracks = profile.get("tracks") or set()

    if repo and repo not in repos:
        return False
    if tracks and track and track not in tracks:
        if role not in ("devops-cicd", "qa-author", "database"):
            return False
    return True


def resolve_agent_for_task(task: dict[str, Any]) -> dict[str, Any]:
    """
    Resolve agente criador para a task. Corrige mismatch CSV vs escopo real.
    Usado em route_task (LangGraph).
    """
    csv_role = normalize_creator_role(str(task.get("agent_role") or "backend"))

    classified, secondary, reason = classify_task(task)
    classified = normalize_creator_role(classified)
    secondary = normalize_creator_role(secondary) if secondary else secondary

    csv_ok = agent_handles_task(csv_role, task)
    if csv_ok:
        return {
            "agent_role": csv_role,
            "agent_role_secondary": task.get("agent_role_secondary") or secondary,
            "in_scope": True,
            "redirected": False,
            "match_reason": task.get("match_reason") or reason,
            "repo": _task_field(task, "repo", "repository", "Repo alvo"),
            "repo_path": repo_local_path(_task_field(task, "repo", "repository", "Repo alvo")),
        }

    return {
        "agent_role": classified,
        "agent_role_secondary": secondary,
        "in_scope": False,
        "redirected": True,
        "from_role": csv_role,
        "to_role": classified,
        "reason": (
            f"Task fora do escopo de `{csv_role}` "
            f"(repo={_task_field(task, 'repo', 'repository', 'Repo alvo')}, "
            f"track={_task_field(task, 'track', 'Track')}). "
            f"Reclassificado: `{classified}` ({reason})"
        ),
        "match_reason": reason,
        "repo": _task_field(task, "repo", "repository", "Repo alvo"),
        "repo_path": repo_local_path(_task_field(task, "repo", "repository", "Repo alvo")),
    }


def repo_local_path(repo: str) -> str | None:
    if not repo:
        return None
    p = resolve_repo_path(repo)
    if p:
        return str(p)
    base = DEFAULT_PATHS.get(repo)
    return str(base) if base else None


def redirect_comment(resolved: dict[str, Any], task_id: str) -> str:
    if not resolved.get("redirected"):
        return ""
    to_role = resolved.get("agent_role") or resolved.get("to_role")
    hint = REDIRECT_HINTS.get(str(to_role), "")
    return (
        f"## Roteamento de agente — {task_id}\n\n"
        f"- **De:** `{resolved.get('from_role')}`\n"
        f"- **Para:** `{to_role}`\n"
        f"- **Motivo:** {resolved.get('reason')}\n"
        f"- **Repo local:** `{resolved.get('repo_path') or 'n/a'}`\n"
        f"- **Escopo alvo:** {hint}\n\n"
        f"Reatribuir label `agent:{to_role}` e skill `agents/{to_role}/SKILL.md`."
    )


def profile_for_role(role: str) -> dict[str, Any]:
    role = normalize_creator_role(role)
    return dict(AGENT_PROFILES.get(role) or {})
