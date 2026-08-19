#!/usr/bin/env python3
"""Gera board Guardião Família v2 — OKRs, tasks granulares, priorização e JSON."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path
from typing import Literal

from task_refinement import refine_item, format_refinement_markdown

ROOT = Path(__file__).resolve().parents[1]
PLANILHAS = ROOT / "07-planilhas"
BOARD = ROOT / "08-board"
COMMITS = ROOT / "06-analise-commits"
REPOS_BASE = Path(r"C:\Users\pedro\Documents\guardiao-familia")

Track = Literal["produto", "infraestrutura", "stores"]
Status = Literal["done", "partial", "todo"]

@dataclass
class Task:
    id: str
    title: str
    epic_id: str
    epic_name: str
    track: Track
    repo: str
    okr: str
    sprint: int
    reach: int
    impact: float
    confidence: float
    effort_sp: int
    cod: int
    pert_o: float
    pert_m: float
    pert_p: float
    status_baseline: Status
    commit_evidence: str = ""
    labels: list[str] = field(default_factory=list)
    rice: float = 0.0
    wsjf: float = 0.0
    pert_expected: float = 0.0
    priority_rank: int = 0
    release_blocker: bool = False

    def calc(self) -> None:
        self.rice = round((self.reach * self.impact * self.confidence) / max(self.effort_sp, 1), 2)
        self.wsjf = round(self.cod / max(self.effort_sp, 1), 2)
        self.pert_expected = round((self.pert_o + 4 * self.pert_m + self.pert_p) / 6, 2)

EPICS = [
    # produto
    ("E-P01", "Auth, sessão e pareamento", "produto", "O3", "guardiao-familia-api"),
    ("E-P02", "Localização e rotas Mapbox", "produto", "O1", "guardiao-familia-api"),
    ("E-P03", "Geofences e alertas", "produto", "O1", "guardiao-familia-api"),
    ("E-P04", "SOS e emergência", "produto", "O1", "guardiao-familia-api"),
    ("E-P05", "Push notifications nativas", "produto", "O1", "guardiao-familia-api"),
    ("E-P06", "Tempo de tela e pedido extra", "produto", "O3", "guardiao-familia-api"),
    ("E-P07", "Gamificação e engajamento child", "produto", "O3", "guardiao-familia-child"),
    ("E-P08", "Família, mensagens e acesso", "produto", "O3", "guardiao-familia-api"),
    ("E-P09", "App parent — mapa, relatórios, IA", "produto", "O3", "guardiao-familia-parent"),
    ("E-P10", "App child — UX e estabilidade", "produto", "O3", "guardiao-familia-child"),
    ("E-P11", "LGPD e compliance produto", "produto", "O2", "guardiao-familia-api"),
    ("E-P12", "Backoffice operacional release", "produto", "O2", "guardiao-familia-backoffice"),
    ("E-P13", "Site institucional e campanha", "produto", "O3", "guardiao-familia-site"),
    # infra
    ("E-I01", "AWS ECS Fargate foundation", "infraestrutura", "O2", "guardiao-familia-api"),
    ("E-I02", "CI/CD multi-repo", "infraestrutura", "O2", "guardiao-familia-api"),
    ("E-I03", "Observabilidade e alertas", "infraestrutura", "O2", "guardiao-familia-api"),
    ("E-I04", "PostgreSQL, Redis e migrations", "infraestrutura", "O2", "guardiao-familia-api"),
    ("E-I05", "Segurança, secrets e WAF", "infraestrutura", "O2", "guardiao-familia-api"),
    ("E-I06", "Ambientes staging e produção", "infraestrutura", "O2", "guardiao-familia-api"),
    # stores
    ("E-S01", "Apple App Store parent", "stores", "O2", "guardiao-familia-parent"),
    ("E-S02", "Apple App Store child", "stores", "O2", "guardiao-familia-child"),
    ("E-S03", "Google Play parent", "stores", "O2", "guardiao-familia-parent"),
    ("E-S04", "Google Play child", "stores", "O2", "guardiao-familia-child"),
    ("E-S05", "Coordenação release e beta", "stores", "O2", "guardiao-familia-api"),
]

def _t(tid, title, epic, repo, okr, sprint, reach, impact, conf, sp, cod, o, m, p, status, commit="", labels=None, blocker=False):
    eid, ename, track, _, _ = next(e for e in EPICS if e[0] == epic)
    return Task(tid, title, eid, ename, track, repo, okr, sprint, reach, impact, conf, sp, cod, o, m, p, status, commit, labels or [], release_blocker=blocker)

def build_tasks() -> list[Task]:
    T: list[Task] = []

    # --- E-P01 Auth ---
    auth_tasks = [
        ("T-P01-001", "Revisar fluxo login parent refresh token persistente", "partial", "b535706"),
        ("T-P01-002", "Revisar fluxo login child remember device", "partial", "26c519e"),
        ("T-P01-003", "Validar revogação sessão child ao desvincular", "done", "0ff10dc"),
        ("T-P01-004", "Testes E2E pareamento QR parent-child", "todo", ""),
        ("T-P01-005", "Documentar política supersession device", "partial", "f39c9c6"),
        ("T-P01-006", "Hardening rate-limit auth 429 falsos positivos", "done", "5821a0a"),
        ("T-P01-007", "Auditar expiração JWT e refresh em todos clients", "todo", ""),
        ("T-P01-008", "Fluxo recuperação conta responsável", "partial", ""),
        ("T-P01-009", "Validar onboarding profile API + parent", "partial", ""),
        ("T-P01-010", "Checklist segurança pareamento child sem guardian", "done", "26c519e"),
    ]
    for i, (tid, title, st, commit) in enumerate(auth_tasks):
        T.append(_t(tid, title, "E-P01", "guardiao-familia-api", "O3", 2, 8, 2, 0.9 if st != "todo" else 0.7, 3, 6, 0.5, 1, 2, st, commit))

    # --- E-P02 Location ---
    loc = [
        ("T-P02-001", "Validar Mapbox road-matched routes API", "done", "cb9a003"),
        ("T-P02-002", "Validar sync offline batch idempotente", "done", "b6702bf"),
        ("T-P02-003", "Persist tracking mode offline routes", "done", "83156e6"),
        ("T-P02-004", "Parent render matched routes no mapa", "done", "94559c0"),
        ("T-P02-005", "Child sample quality offline routes", "done", "0dbbc08"),
        ("T-P02-006", "Recovery route quando Mapbox indisponível", "done", "a16df36"),
        ("T-P02-007", "Histórico trajetos parent UI paginado", "partial", "7d4995d"),
        ("T-P02-008", "Battery policy child location background", "done", "ed373a3"),
        ("T-P02-009", "Nudge refresh location child", "done", "df2b0ac"),
        ("T-P02-010", "Testes integração ping batch location", "partial", ""),
        ("T-P02-011", "Documentar SLA ping P95", "todo", ""),
        ("T-P02-012", "Fallback quando GPS desligado child", "partial", ""),
    ]
    for tid, title, st, commit in loc:
        T.append(_t(tid, title, "E-P02", "guardiao-familia-api", "O1", 4, 10, 3, 0.85, 3, 9, 0.5, 1.5, 3, st, commit))

    # --- E-P03 Geofences ---
    geo = [
        ("T-P03-001", "Avaliar geofence em batch pings API", "done", "aa7a914"),
        ("T-P03-002", "Melhorar delivery alerta geofence push", "partial", "18d2dbf"),
        ("T-P03-003", "Parent UI criar/editar cerca circular", "partial", ""),
        ("T-P03-004", "Parent UI criar/editar cerca poligonal", "todo", ""),
        ("T-P03-005", "Notificação entrada/saída cerca E2E iOS", "todo", "", True),
        ("T-P03-006", "Notificação entrada/saída cerca E2E Android", "todo", "", True),
        ("T-P03-007", "Testes carga geofence 100 cercas/família", "todo", ""),
        ("T-P03-008", "Documentar regras tolerância stale ping", "done", "aa7a914"),
    ]
    for tid, title, st, commit, *rest in geo:
        blk = bool(rest and rest[0])
        T.append(_t(tid, title, "E-P03", "guardiao-familia-api", "O1", 6, 9, 3, 0.8, 5, 10, 1, 2, 4, st, commit, blocker=blk))

    # --- E-P04 SOS ---
    sos = [
        ("T-P04-001", "API SOS create/update/attach audio", "done", ""),
        ("T-P04-002", "Presign upload áudio SOS S3", "done", ""),
        ("T-P04-003", "Parent histórico SOS error handling", "partial", "f339651"),
        ("T-P04-004", "Child trigger SOS UI discreto", "partial", ""),
        ("T-P04-005", "Push SOS parent em <30s iOS", "todo", "", True),
        ("T-P04-006", "Push SOS parent em <30s Android", "todo", "", True),
        ("T-P04-007", "Escalation rules SOS sem ack", "partial", ""),
        ("T-P04-008", "Backoffice visualizar áudio SOS", "partial", "b870fd6"),
        ("T-P04-009", "Testes E2E SOS com mock push", "todo", ""),
        ("T-P04-010", "Runbook operacional incidente SOS", "todo", ""),
    ]
    for tid, title, st, commit, *rest in sos:
        blk = bool(rest and rest[0])
        T.append(_t(tid, title, "E-P04", "guardiao-familia-api", "O1", 5, 10, 3, 0.75, 5, 12, 1, 2.5, 5, st, commit, blocker=blk))

    # --- E-P05 Push nativo ---
    push = [
        ("T-P05-001", "Bundlar sons push iOS parent", "todo", "", True),
        ("T-P05-002", "Bundlar sons push iOS child", "todo", "", True),
        ("T-P05-003", "Bundlar sons push Android parent", "todo", "", True),
        ("T-P05-004", "Bundlar sons push Android child", "todo", "", True),
        ("T-P05-005", "Configurar APNs production certificates", "partial", ""),
        ("T-P05-006", "Configurar FCM data messages SOS", "partial", ""),
        ("T-P05-007", "API mapear soundId por tipo alerta", "done", ""),
        ("T-P05-008", "Testes push geofence som customizado", "todo", ""),
        ("T-P05-009", "Testes push SOS som emergência", "todo", "", True),
        ("T-P05-010", "Documentar matriz som x evento", "todo", ""),
    ]
    for tid, title, st, commit, *rest in push:
        blk = bool(rest and rest[0])
        T.append(_t(tid, title, "E-P05", "guardiao-familia-parent", "O1", 3, 10, 3, 0.7, 3, 11, 0.5, 1.5, 3, st, commit, blocker=blk))

    # --- E-P06 Screen time ---
    st_tasks = [
        ("T-P06-001", "API regras tempo de tela CRUD", "done", ""),
        ("T-P06-002", "API pedido tempo extra create/decide", "done", ""),
        ("T-P06-003", "Parent UI pedido tempo extra", "partial", "bfb44c7"),
        ("T-P06-004", "Child UI status tempo de tela", "partial", ""),
        ("T-P06-005", "Notificação push pedido extra", "todo", ""),
        ("T-P06-006", "E-mail notificação pedido extra", "done", ""),
        ("T-P06-007", "Relatório uso apps child", "partial", ""),
        ("T-P06-008", "Política extra-time applies date", "done", ""),
        ("T-P06-009", "Testes E2E pedido extra aprovado", "todo", ""),
        ("T-P06-010", "Testes E2E pedido extra negado", "todo", ""),
        ("T-P06-011", "Exibir features ST ocultas parent", "todo", "bfb44c7"),
    ]
    for tid, title, st, commit in st_tasks:
        T.append(_t(tid, title, "E-P06", "guardiao-familia-api", "O3", 7, 7, 2, 0.8, 3, 5, 0.5, 1.5, 3, st, commit))

    # --- E-P07 Gamification ---
    for tid, title, st in [
        ("T-P07-001", "API conquistas e pontos child", "done"),
        ("T-P07-002", "Child UI lista conquistas", "partial"),
        ("T-P07-003", "Animação unlock conquista", "todo"),
        ("T-P07-004", "Tutorial gamificação onboarding", "partial"),
        ("T-P07-005", "Testes regressão gamification", "todo"),
    ]:
        T.append(_t(tid, title, "E-P07", "guardiao-familia-child", "O3", 9, 5, 1.5, 0.75, 2, 3, 0.5, 1, 2, st))

    # --- E-P08 Family ---
    fam = [
        ("T-P08-001", "API family members CRUD", "done"),
        ("T-P08-002", "API family messages", "done"),
        ("T-P08-003", "API family access invites", "done"),
        ("T-P08-004", "Parent UI gestão família", "partial"),
        ("T-P08-005", "Parent UI mensagens família", "partial"),
        ("T-P08-006", "Referral rewards API", "done"),
        ("T-P08-007", "Community module backlog only", "todo"),
    ]
    for tid, title, st in fam:
        T.append(_t(tid, title, "E-P08", "guardiao-familia-api", "O3", 8, 6, 2, 0.8, 3, 4, 0.5, 1.5, 3, st))

    # --- E-P09 Parent app ---
    parent = [
        ("T-P09-001", "Mapa rotas matched estabilidade", "done", "f5047fa"),
        ("T-P09-002", "Offline route refresh seguro", "done", "aef5509"),
        ("T-P09-003", "Assistente IA chat parent MVP", "partial", ""),
        ("T-P09-004", "Relatórios localização semanal", "todo", ""),
        ("T-P09-005", "Dashboard home widgets", "partial", ""),
        ("T-P09-006", "Deep link push notification", "todo", ""),
        ("T-P09-007", "Acessibilidade VoiceOver mapa", "todo", ""),
        ("T-P09-008", "Localização permissões UX iOS", "partial", ""),
        ("T-P09-009", "Localização permissões UX Android", "partial", ""),
        ("T-P09-010", "Remover URL plan config stale", "done", "dbabadf"),
        ("T-P09-011", "Jest release checks estáveis", "done", "d9529ab"),
        ("T-P09-012", "Paywall permanece desabilitado release", "done", "c64e9f4"),
    ]
    for tid, title, st, *c in parent:
        T.append(_t(tid, title, "E-P09", "guardiao-familia-parent", "O3", 10, 7, 2, 0.85 if st == "done" else 0.7, 3, 5, 0.5, 1.5, 3, st, c[0] if c else ""))

    # --- E-P10 Child app ---
    child = [
        ("T-P10-001", "Pairing help simplificado", "done", "fd9882d"),
        ("T-P10-002", "App name PT-BR copy", "done", "fd94887"),
        ("T-P10-003", "Privacy compliance App Store", "done", "f26520e"),
        ("T-P10-004", "Background location hardening", "done", "3d58268"),
        ("T-P10-005", "Invalid session reset", "done", "1f9c28f"),
        ("T-P10-006", "Release 2.0.0 estabilização", "done", "b099a45"),
        ("T-P10-007", "SOS button acessível", "partial", ""),
        ("T-P10-008", "Indicador conexão offline", "todo", ""),
        ("T-P10-009", "Tutorial primeiro uso child", "partial", ""),
        ("T-P10-010", "Testes dispositivos Android baixo RAM", "todo", ""),
    ]
    for tid, title, st, *c in child:
        T.append(_t(tid, title, "E-P10", "guardiao-familia-child", "O3", 9, 7, 2, 0.85, 2, 5, 0.5, 1, 2, st, c[0] if c else ""))

    # --- E-P11 LGPD ---
    lgpd = [
        ("T-P11-001", "Fluxos exportação dados titular", "partial", "4c0102b"),
        ("T-P11-002", "Fluxos exclusão conta menor", "partial", "4c0102b"),
        ("T-P11-003", "Consentimento parental registrado", "partial", ""),
        ("T-P11-004", "Atualizar RIPD com SOS áudio", "todo", ""),
        ("T-P11-005", "Atualizar ROPA localização contínua", "todo", ""),
        ("T-P11-006", "Incident response drill Q3", "todo", ""),
        ("T-P11-007", "Parent UI privacy settings", "partial", ""),
        ("T-P11-008", "Child UI privacy mínima", "partial", ""),
        ("T-P11-009", "DPO sign-off release", "todo", "", True),
        ("T-P11-010", "Audit log acesso dados sensíveis", "partial", ""),
    ]
    for tid, title, st, *rest in lgpd:
        blk = "sign-off" in title
        commit = rest[0] if rest and isinstance(rest[0], str) else ""
        T.append(_t(tid, title, "E-P11", "guardiao-familia-api", "O2", 8, 8, 3, 0.75, 5, 10, 1, 2, 4, st, commit, blocker=blk))

    # --- E-P12 Backoffice ---
    bo = [
        ("T-P12-001", "Live support board produção", "done", "ff7ba8a"),
        ("T-P12-002", "Support audio playback", "done", "b870fd6"),
        ("T-P12-003", "Cloudflare analytics dashboard", "done", "bf172e8"),
        ("T-P12-004", "Role-based menu sidebar", "done", "c69f117"),
        ("T-P12-005", "Leads listing overview", "done", "afa0057"),
        ("T-P12-006", "Runbook suporte release", "todo", ""),
        ("T-P12-007", "Alertas erro API no dashboard", "partial", ""),
        ("T-P12-008", "Moderação mínima tickets SOS", "todo", ""),
    ]
    for tid, title, st, *c in bo:
        T.append(_t(tid, title, "E-P12", "guardiao-familia-backoffice", "O2", 11, 5, 2, 0.85, 2, 4, 0.5, 1, 2, st, c[0] if c else ""))

    # --- E-P13 Site ---
    site = [
        ("T-P13-001", "CNPJ páginas legais", "done", "8928a7e"),
        ("T-P13-002", "Chatbot widget site", "done", "637dd2a"),
        ("T-P13-003", "Links download pré-lançamento", "done", "a6fac08"),
        ("T-P13-004", "Campanha 30 dias estrutura", "done", "2556642"),
        ("T-P13-005", "SEO meta tags release", "todo", ""),
        ("T-P13-006", "Página status incidentes", "todo", ""),
        ("T-P13-007", "Atualizar screenshots apps release", "todo", ""),
    ]
    for tid, title, st, *c in site:
        T.append(_t(tid, title, "E-P13", "guardiao-familia-site", "O3", 12, 4, 1.5, 0.8, 2, 2, 0.25, 0.5, 1, st, c[0] if c else ""))

    # --- INFRA E-I01 ECS ---
    ecs = [
        ("T-I01-001", "Terraform VPC subnets multi-AZ", "partial"),
        ("T-I01-002", "ECS cluster Fargate", "partial"),
        ("T-I01-003", "Task definition API container", "partial"),
        ("T-I01-004", "ALB + target group health checks", "partial"),
        ("T-I01-005", "ECR repository e lifecycle", "todo"),
        ("T-I01-006", "Service autoscaling CPU/mem", "todo"),
        ("T-I01-007", "Secrets Manager env injection", "todo"),
        ("T-I01-008", "Route53 DNS api.guardiaofamilia", "todo"),
        ("T-I01-009", "ACM cert TLS", "todo"),
        ("T-I01-010", "Documentar runbook deploy ECS", "todo"),
    ]
    for tid, title, st in ecs:
        T.append(_t(tid, title, "E-I01", "guardiao-familia-api", "O2", 1, 10, 3, 0.6, 5, 12, 2, 4, 8, st, blocker=True))

    # --- E-I02 CI/CD ---
    cicd = [
        ("T-I02-001", "Pipeline API build test deploy", "partial", "5821a0a"),
        ("T-I02-002", "Gate deploy por branch main", "done", "5821a0a"),
        ("T-I02-003", "Automate cache purge Cloudflare", "done", "5821a0a"),
        ("T-I02-004", "EAS update workflow parent", "done", "3ead192"),
        ("T-I02-005", "EAS submit iOS parent", "done", "ce8728d"),
        ("T-I02-006", "EAS build child production", "partial", "d787da9"),
        ("T-I02-007", "Backoffice SSM deploy sa-east-1", "done", "c23d55c"),
        ("T-I02-008", "Dependabot todos repos", "partial", ""),
        ("T-I02-009", "Template PR org-wide", "partial", "9f3a1c3"),
        ("T-I02-010", "Smoke test pós-deploy API", "todo", ""),
    ]
    for tid, title, st, *c in cicd:
        T.append(_t(tid, title, "E-I02", "guardiao-familia-api", "O2", 2, 9, 2.5, 0.8, 3, 8, 0.5, 1.5, 3, st, c[0] if c else ""))

    # --- E-I03 Observability ---
    obs = [
        ("T-I03-001", "CloudWatch logs structured API", "partial", ""),
        ("T-I03-002", "Metrics custom SOS latency", "todo", ""),
        ("T-I03-003", "Dashboard Grafana/BO integrado", "partial", "bf172e8"),
        ("T-I03-004", "Alertas PagerDuty/on-call", "todo", ""),
        ("T-I03-005", "Tracing OpenTelemetry API", "todo", ""),
        ("T-I03-006", "SLO error rate API 99.5%", "todo", ""),
    ]
    for tid, title, st, commit in obs:
        T.append(_t(tid, title, "E-I03", "guardiao-familia-api", "O2", 3, 8, 2, 0.65, 3, 7, 1, 2, 4, st, commit))

    # --- E-I04 DB ---
    db = [
        ("T-I04-001", "RDS PostgreSQL multi-AZ staging", "partial"),
        ("T-I04-002", "RDS PostgreSQL multi-AZ prod", "todo"),
        ("T-I04-003", "Redis ElastiCache session", "partial"),
        ("T-I04-004", "Backup automático PITR", "todo"),
        ("T-I04-005", "Migration strategy zero-downtime", "todo"),
        ("T-I04-006", "Índices performance geofence/location", "todo"),
    ]
    for tid, title, st in db:
        T.append(_t(tid, title, "E-I04", "guardiao-familia-api", "O2", 2, 9, 3, 0.6, 5, 10, 2, 4, 6, st, blocker=True))

    # --- E-I05 Security ---
    sec = [
        ("T-I05-001", "WAF ALB rules OWASP", "todo", ""),
        ("T-I05-002", "Rotate secrets quarterly", "todo", ""),
        ("T-I05-003", "IAM least privilege ECS tasks", "todo", ""),
        ("T-I05-004", "S3 bucket policies SOS audio", "partial", ""),
        ("T-I05-005", "Pen test checklist pré-release", "todo", "", True),
    ]
    for tid, title, st, commit, *rest in sec:
        blk = bool(rest)
        T.append(_t(tid, title, "E-I05", "guardiao-familia-api", "O2", 4, 9, 3, 0.6, 5, 9, 1, 3, 6, st, commit, blocker=blk))

    # --- E-I06 Environments ---
    env = [
        ("T-I06-001", "Staging mirror prod config", "partial", ""),
        ("T-I06-002", "Prod cutover checklist", "todo", "", True),
        ("T-I06-003", "Feature flags system-config", "partial", ""),
        ("T-I06-004", "Rollback procedure documentado", "todo", ""),
        ("T-I06-005", "Load test staging 1k famílias", "todo", ""),
    ]
    for tid, title, st, commit, *rest in env:
        blk = bool(rest)
        T.append(_t(tid, title, "E-I06", "guardiao-familia-api", "O2", 12, 10, 3, 0.65, 5, 11, 1, 3, 5, st, commit, blocker=blk))

    # --- STORES ---
    store_apple_parent = [
        ("T-S01-001", "App Store Connect metadata parent PT", "partial"),
        ("T-S01-002", "Screenshots 6.7 e 5.5 parent", "todo"),
        ("T-S01-003", "Privacy nutrition labels parent", "partial"),
        ("T-S01-004", "TestFlight external beta 50 users", "partial", "c1bb681"),
        ("T-S01-005", "Review notes location background", "todo", True),
        ("T-S01-006", "Submit production parent", "todo", True),
    ]
    for tid, title, st, *rest in store_apple_parent:
        blk = bool(rest and rest[-1] == True if rest else False)
        T.append(_t(tid, title, "E-S01", "guardiao-familia-parent", "O2", 11, 10, 3, 0.7, 3, 11, 0.5, 1.5, 3, st, rest[0] if rest and rest[0] != True else "", blocker=blk))

    store_apple_child = [
        ("T-S02-001", "Metadata child PT minors", "partial"),
        ("T-S02-002", "Screenshots child", "todo"),
        ("T-S02-003", "Parental gate App Store", "partial", "f26520e"),
        ("T-S02-004", "TestFlight child beta", "partial", "badaa4e"),
        ("T-S02-005", "Submit production child", "todo", True),
    ]
    for tid, title, st, *rest in store_apple_child:
        blk = "Submit" in title
        T.append(_t(tid, title, "E-S02", "guardiao-familia-child", "O2", 11, 10, 3, 0.7, 3, 11, 0.5, 1.5, 3, st, rest[0] if rest else "", blocker=blk))

    store_gp_parent = [
        ("T-S03-001", "Play Console listing parent", "todo"),
        ("T-S03-002", "Data safety form parent", "todo"),
        ("T-S03-003", "Content rating questionnaire", "todo"),
        ("T-S03-004", "Internal testing track parent", "todo"),
        ("T-S03-005", "Production rollout parent", "todo", True),
    ]
    for tid, title, st, *rest in store_gp_parent:
        blk = "Production" in title
        T.append(_t(tid, title, "E-S03", "guardiao-familia-parent", "O2", 12, 10, 3, 0.65, 3, 10, 0.5, 2, 4, st, blocker=blk))

    store_gp_child = [
        ("T-S04-001", "Play listing child designed for families", "todo"),
        ("T-S04-002", "Data safety child location", "todo"),
        ("T-S04-003", "Validate GP submit secret CI", "done", "3e37e38"),
        ("T-S04-004", "Internal testing child", "todo"),
        ("T-S04-005", "Production rollout child", "todo", True),
    ]
    for tid, title, st, *rest in store_gp_child:
        blk = "Production" in title
        T.append(_t(tid, title, "E-S04", "guardiao-familia-child", "O2", 12, 10, 3, 0.65, 3, 10, 0.5, 2, 4, st, rest[0] if rest and rest[0] != True else "", blocker=blk))

    release = [
        ("T-S05-001", "Checklist release blocker consolidado", "todo", True),
        ("T-S05-002", "Beta fechado 100 famílias", "todo"),
        ("T-S05-003", "Beta aberto child polish gate", "todo"),
        ("T-S05-004", "Comunicado lançamento site+campanha", "todo"),
        ("T-S05-005", "Monitoramento 72h pós-release", "todo"),
        ("T-S05-006", "Retrospectiva e backlog v2", "todo"),
    ]
    for tid, title, st, *rest in release:
        blk = bool(rest and rest[0] == True)
        T.append(_t(tid, title, "E-S05", "guardiao-familia-api", "O2", 13, 10, 3, 0.7, 5, 12, 1, 2, 4, st, blocker=blk))

    # --- Expansão granular: módulos API (commits + cobertura código) ---
    api_modules = [
        ("notifications", "push token register/unregister", "partial"),
        ("realtime", "websocket gateway reconnect policy", "partial"),
        ("escalation", "SOS escalation timer config", "partial"),
        ("chatbot", "site chatbot intent routing", "done"),
        ("ai", "support classifier rollout", "done", "e2c6ea8"),
        ("ai", "disable placeholder provider default", "done", "1fc606d"),
        ("payments", "Stripe webhook idempotency audit", "partial"),
        ("payments", "paywall feature flag off prod", "done", "c64e9f4"),
        ("analytics", "event schema child location", "partial"),
        ("metrics", "Prometheus endpoint scrape ECS", "todo"),
        ("monitoring", "health check deep dependencies", "partial"),
        ("email", "template SOS parent notification", "partial"),
        ("email", "template extra-time request", "done"),
        ("content", "tutorial CMS API CRUD", "done"),
        ("tutorials", "parent onboarding tutorial fetch", "partial"),
        ("client-config", "remote config parent minimum version", "partial"),
        ("pre-launch", "waitlist lead capture API", "done"),
        ("accounting", "CPC fiscal endpoints BO", "done"),
        ("admin", "admin audit actions log", "partial"),
        ("cache", "Redis cache invalidation pairing", "partial"),
        ("maps", "Mapbox token rotation procedure", "todo"),
        ("devices", "device supersession integration test", "done", "f39c9c6"),
        ("children", "child profile avatar presign", "partial"),
        ("pairing", "QR code expiry policy", "partial"),
        ("families", "multi-guardian permission matrix", "partial"),
        ("family-messages", "message read receipt", "todo"),
        ("family-access", "invite link deep link", "todo"),
        ("referral", "referral reward fulfillment", "partial"),
        ("gamification", "badge criteria documentation", "partial"),
        ("community", "community feed out-of-scope flag", "todo"),
        ("compliance", "data export job async worker", "partial", "4c0102b"),
        ("compliance", "account deletion cascade order", "partial", "4c0102b"),
        ("support", "support ticket SLA metrics", "partial", "97946a2"),
        ("support", "admin reply push notification", "todo"),
        ("storage", "SOS audio MIME validation", "done"),
        ("system-config", "feature toggle geofence v2", "partial"),
        ("i18n", "PT-BR string audit parent", "partial"),
        ("i18n", "PT-BR string audit child", "partial"),
        ("health", "readiness vs liveness split", "partial"),
    ]
    n = 0
    for mod, desc, st, *c in api_modules:
        n += 1
        commit = c[0] if c else ""
        epic = "E-P11" if mod == "compliance" else "E-P02" if mod in ("maps", "location") else "E-P04" if mod in ("escalation", "email") and "SOS" in desc else "E-P08" if mod.startswith("family") or mod in ("families", "referral") else "E-P07" if mod == "gamification" else "E-P09" if mod in ("ai", "tutorials", "client-config") else "E-P12" if mod == "support" else "E-I03" if mod in ("metrics", "monitoring", "analytics") else "E-P01" if mod in ("devices", "pairing", "children") else "E-P05" if mod == "notifications" else "E-P13" if mod == "chatbot" else "E-P06" if mod == "payments" else "E-P02"
        T.append(_t(f"T-P14-{n:03d}", f"API {mod}: {desc}", epic, "guardiao-familia-api", "O2" if mod == "compliance" else "O3", 8 if mod == "compliance" else 6, 6, 2, 0.8 if st != "todo" else 0.65, 2, 4, 0.25, 0.75, 2, st, commit))

    # Parent app granular
    parent_extra = [
        "Mapbox style tokens produção", "Safe area insets iPhone notch", "Tablet layout responsivo",
        "Biometria login Face ID", "Biometria login fingerprint Android", "Share sheet convite família",
        "Push permission prompt timing", "Settings toggles notificações por tipo", "SOS histórico filtros data",
        "Geofence list empty state UX", "Loading skeleton mapa", "Error boundary tela mapa",
        "Offline banner sem rede", "Analytics screen view mapa", "Crash reporting Sentry parent",
    ]
    for i, desc in enumerate(parent_extra, 1):
        T.append(_t(f"T-P09-{12+i:03d}", f"Parent: {desc}", "E-P09", "guardiao-familia-parent", "O3", 10, 5, 1.5, 0.7, 2, 3, 0.25, 0.75, 2, "todo"))

    # Child app granular
    child_extra = [
        "Ícone app adaptive Android", "Splash screen animada", "Haptic feedback SOS",
        "Low power mode location degrade", "Permissão câmera QR pairing", "Feedback visual ping enviado",
        "Modo escuro child", "Font scaling acessibilidade", "Crash reporting Sentry child",
        "Analytics evento SOS triggered", "Widget SOS Android backlog doc", "App shortcuts SOS Android",
    ]
    for i, desc in enumerate(child_extra, 1):
        T.append(_t(f"T-P10-{10+i:03d}", f"Child: {desc}", "E-P10", "guardiao-familia-child", "O3", 9, 5, 1.5, 0.7, 2, 3, 0.25, 0.75, 2, "todo"))

    # Infra granular
    infra_extra = [
        ("E-I01", "NAT Gateway HA cost review", 1),
        ("E-I01", "Fargate Spot mix staging", 1),
        ("E-I02", "OIDC GitHub Actions AWS role", 2),
        ("E-I02", "Branch protection rules 6 repos", 2),
        ("E-I03", "Log retention 90d compliance", 3),
        ("E-I04", "Connection pool tuning API", 2),
        ("E-I05", "Security group least ingress", 4),
        ("E-I06", "Blue/green deploy ECS eval", 12),
    ]
    for i, (epic, desc, sprint) in enumerate(infra_extra, 1):
        T.append(_t(f"T-I07-{i:03d}", f"Infra: {desc}", epic, "guardiao-familia-api", "O2", sprint, 7, 2, 0.6, 3, 6, 0.5, 1.5, 3, "todo", blocker="cutover" in desc.lower() or "production" in desc.lower()))

    # Stores granular checklist
    store_extra = [
        ("E-S01", "Apple: export compliance encryption doc", 11),
        ("E-S01", "Apple: age rating 4+ questionnaire", 11),
        ("E-S02", "Apple child: COPPA parental consent copy", 11),
        ("E-S03", "Google: target API level 34 parent", 12),
        ("E-S04", "Google: target API level 34 child", 12),
        ("E-S03", "Google: in-app permissions declaration", 12),
        ("E-S04", "Google: designed for families program", 12),
        ("E-S05", "Release: version sync matrix 4 apps", 13),
        ("E-S05", "Release: rollback store version plan", 13),
    ]
    for i, (epic, desc, sprint) in enumerate(store_extra, 1):
        blk = "rollback" in desc or "version sync" in desc
        repo = "guardiao-familia-parent" if "parent" in desc.lower() or epic == "E-S01" or epic == "E-S03" else "guardiao-familia-child" if "child" in desc.lower() or epic == "E-S02" or epic == "E-S04" else "guardiao-familia-api"
        T.append(_t(f"T-S06-{i:03d}", desc, epic, repo, "O2", sprint, 8, 2.5, 0.65, 2, 8, 0.25, 0.75, 2, "todo", blocker=blk))

    for task in T:
        task.calc()
    return T


def analyze_commits() -> dict:
    repos = [
        "guardiao-familia-api", "guardiao-familia-parent", "guardiao-familia-child",
        "guardiao-familia-site", "guardiao-familia-backoffice", "campanha",
    ]
    out = {}
    for repo in repos:
        path = REPOS_BASE / repo
        if not path.exists():
            out[repo] = {"error": "path not found", "commits": []}
            continue
        try:
            log = subprocess.run(
                ["git", "-C", str(path), "log", "--oneline", "-50"],
                capture_output=True, text=True, timeout=30,
            )
            lines = [l.strip() for l in log.stdout.strip().split("\n") if l.strip()]
            out[repo] = {"commits": lines, "count": len(lines)}
        except Exception as e:
            out[repo] = {"error": str(e), "commits": []}
    return out


def rank_tasks(tasks: list[Task]) -> list[Task]:
    def score(t: Task) -> float:
        base = t.wsjf * 0.6 + t.rice * 0.4
        if t.release_blocker:
            base += 50
        if t.status_baseline == "done":
            base -= 100
        elif t.status_baseline == "partial":
            base += 5
        okr_boost = {"O1": 15, "O2": 12, "O3": 5}.get(t.okr, 0)
        return base + okr_boost

    ranked = sorted(tasks, key=score, reverse=True)
    for i, t in enumerate(ranked, 1):
        t.priority_rank = i
    return ranked


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def task_row(t: Task) -> dict:
    d = asdict(t)
    d["labels"] = ";".join(t.labels)
    return d


def item_to_json(t: Task) -> dict:
    ref = refine_item({
        "id": t.id, "title": t.title, "repository": t.repo,
        "fields": {
            "Epic": f"{t.epic_id} {t.epic_name}", "Trilha": t.track, "OKR": t.okr,
            "Sprint": t.sprint, "Baseline": t.status_baseline,
            "Release Blocker": "yes" if t.release_blocker else "no",
        },
        "commit_evidence": t.commit_evidence,
        "release_blocker": t.release_blocker,
    })
    blocker_motivo = ref.get("blocker_reason", "")
    refinamento_text = ref["context_summary"]
    if len(refinamento_text) > 900:
        refinamento_text = refinamento_text[:897] + "..."
    return {
        "id": t.id,
        "title": t.title,
        "repository": t.repo,
        "type": "draft_issue",
        "fields": {
            "Status": "Done" if t.status_baseline == "done" else "Todo",
            "Trilha": t.track,
            "OKR": t.okr,
            "Epic": f"{t.epic_id} {t.epic_name}",
            "Sprint": t.sprint,
            "Story Points": t.effort_sp,
            "RICE Score": t.rice,
            "WSJF": t.wsjf,
            "Reach": t.reach,
            "Impact": t.impact,
            "Confidence": t.confidence,
            "CoD": t.cod,
            "PERT (d)": t.pert_expected,
            "Baseline": t.status_baseline,
            "Release Blocker": "yes" if t.release_blocker else "no",
            "Blocker Motivo": blocker_motivo,
            "Priority Rank": t.priority_rank,
            "Repo alvo": t.repo,
            "Refinamento": refinamento_text,
        },
        "labels": t.labels + [t.track, t.okr, t.epic_id],
        "commit_evidence": t.commit_evidence,
        "refinement": ref,
    }


def build_json_board(tasks: list[Task]) -> dict:
    return {
        "version": "2.0",
        "generated": date.today().isoformat(),
        "organization": "guardiaofamilia",
        "project": {
            "title": "Guardião Família v2",
            "number": 2,
            "url": "https://github.com/orgs/guardiaofamilia/projects/2",
            "description": "Board replanejado — OKRs, RICE/WSJF, trilhas produto/infra/stores",
            "visibility": "PUBLIC",
            "template": "Board",
        },
        "fields": [
            {"name": "Status", "type": "single_select", "options": ["Todo", "In Progress", "Done"]},
            {"name": "Trilha", "type": "single_select", "options": ["produto", "infraestrutura", "stores"]},
            {"name": "OKR", "type": "single_select", "options": ["O1", "O2", "O3"]},
            {"name": "Epic", "type": "text"},
            {"name": "Sprint", "type": "number"},
            {"name": "Story Points", "type": "number"},
            {"name": "RICE Score", "type": "number"},
            {"name": "WSJF", "type": "number"},
            {"name": "Reach", "type": "number"},
            {"name": "Impact", "type": "number"},
            {"name": "Confidence", "type": "number"},
            {"name": "CoD", "type": "number"},
            {"name": "PERT (d)", "type": "number"},
            {"name": "Baseline", "type": "single_select", "options": ["done", "partial", "todo"]},
            {"name": "Release Blocker", "type": "single_select", "options": ["yes", "no"]},
            {"name": "Blocker Motivo", "type": "text"},
            {"name": "Priority Rank", "type": "number"},
            {"name": "Repo alvo", "type": "text"},
            {"name": "Refinamento", "type": "text"},
        ],
        "epics": [{"id": e[0], "name": e[1], "track": e[2], "okr": e[3], "repo": e[4]} for e in EPICS],
        "items": [item_to_json(t) for t in tasks],
    }


def main() -> None:
    PLANILHAS.mkdir(parents=True, exist_ok=True)
    BOARD.mkdir(parents=True, exist_ok=True)
    COMMITS.mkdir(parents=True, exist_ok=True)

    commit_data = analyze_commits()
    (COMMITS / "commits_por_repo.json").write_text(
        json.dumps(commit_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    tasks = rank_tasks(build_tasks())

    # CSVs individuais
    rice_rows = [{"task_id": t.id, "title": t.title, "reach": t.reach, "impact": t.impact,
                  "confidence": t.confidence, "effort_sp": t.effort_sp, "rice_score": t.rice} for t in tasks]
    write_csv(PLANILHAS / "calc_rice.csv", rice_rows,
              ["task_id", "title", "reach", "impact", "confidence", "effort_sp", "rice_score"])

    wsjf_rows = [{"task_id": t.id, "title": t.title, "cost_of_delay": t.cod,
                  "job_size_sp": t.effort_sp, "wsjf": t.wsjf} for t in tasks]
    write_csv(PLANILHAS / "calc_wsjf.csv", wsjf_rows,
              ["task_id", "title", "cost_of_delay", "job_size_sp", "wsjf"])

    pert_rows = [{"task_id": t.id, "title": t.title, "optimistic_d": t.pert_o,
                  "most_likely_d": t.pert_m, "pessimistic_d": t.pert_p, "expected_d": t.pert_expected} for t in tasks]
    write_csv(PLANILHAS / "calc_pert.csv", pert_rows,
              ["task_id", "title", "optimistic_d", "most_likely_d", "pessimistic_d", "expected_d"])

    sp_rows = [{"task_id": t.id, "title": t.title, "effort_sp": t.effort_sp, "sprint": t.sprint} for t in tasks]
    write_csv(PLANILHAS / "calc_story_points.csv", sp_rows, ["task_id", "title", "effort_sp", "sprint"])

    epic_rows = [{"epic_id": e[0], "name": e[1], "track": e[2], "okr": e[3], "repo": e[4],
                  "task_count": sum(1 for t in tasks if t.epic_id == e[0]),
                  "total_sp": sum(t.effort_sp for t in tasks if t.epic_id == e[0]),
                  "total_pert_d": round(sum(t.pert_expected for t in tasks if t.epic_id == e[0]), 1)}
                 for e in EPICS]
    write_csv(PLANILHAS / "calc_epicos_resumo.csv", epic_rows,
              ["epic_id", "name", "track", "okr", "repo", "task_count", "total_sp", "total_pert_d"])

    final_rows = [task_row(t) for t in tasks]
    write_csv(PLANILHAS / "BACKLOG_PRIORIZADO_FINAL.csv", final_rows,
              list(final_rows[0].keys()) if final_rows else [])

    ref_rows = []
    for t in tasks:
        item = {"id": t.id, "title": t.title, "repository": t.repo,
                "fields": {"Epic": f"{t.epic_id} {t.epic_name}", "Trilha": t.track,
                           "OKR": t.okr, "Sprint": t.sprint, "Baseline": t.status_baseline,
                           "Release Blocker": "yes" if t.release_blocker else "no"},
                "commit_evidence": t.commit_evidence}
        ref = refine_item(item)
        ref_rows.append({
            "id": t.id, "title": t.title, "repo": t.repo,
            "suggested_files": ";".join(ref["suggested_files"]),
            "context_summary": ref["context_summary"].replace("\n", " ")[:500],
            "acceptance_hints": ";".join(ref["acceptance_hints"]),
            "blocker_reason": ref.get("blocker_reason", ""),
        })
    write_csv(PLANILHAS / "REFINAMENTO_TASKS.csv", ref_rows,
              ["id", "title", "repo", "suggested_files", "context_summary", "acceptance_hints", "blocker_reason"])

    board = build_json_board(tasks)
    (BOARD / "github-project-2-import.json").write_text(
        json.dumps(board, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    summary = {
        "total_tasks": len(tasks),
        "total_sp": sum(t.effort_sp for t in tasks),
        "total_pert_d": round(sum(t.pert_expected for t in tasks), 1),
        "by_track": {},
        "by_status": {},
        "release_blockers": sum(1 for t in tasks if t.release_blocker),
        "epics": len(EPICS),
    }
    for tr in ("produto", "infraestrutura", "stores"):
        summary["by_track"][tr] = sum(1 for t in tasks if t.track == tr)
    for st in ("done", "partial", "todo"):
        summary["by_status"][st] = sum(1 for t in tasks if t.status_baseline == st)
    (ROOT / "RESUMO_GERACAO.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

    import subprocess
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_backlog_dashboard.py")], check=False)


if __name__ == "__main__":
    main()
