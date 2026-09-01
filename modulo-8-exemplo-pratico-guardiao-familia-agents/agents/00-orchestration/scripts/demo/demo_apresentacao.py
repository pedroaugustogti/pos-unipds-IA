#!/usr/bin/env python3
"""Demo acadêmica paced: reset → claim → implement+commit → pipeline até In Pull Request."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.paths import DEMO_DIR  # noqa: E402
from lib.env_load import ensure_env  # noqa: E402
from lib.orchestrator.event_orchestrator import load_runtime, save_runtime, set_agent_state  # noqa: E402
from lib.gateway import approve_hitl, emit_status_event  # noqa: E402
from board_automation.board.local_board import get_local_status, update_local_status  # noqa: E402
from lib.runtime_log import log_workflow_event  # noqa: E402


def build_snapshot() -> dict:
    return {"demo": True}


def write_dashboard(_snap: dict | None = None) -> None:
    return None

from board_automation.board.reviewer_pairs import normalize_creator_role, reviewer_for  # noqa: E402
from board_automation.board.task_action_history import (  # noqa: E402
    append_task_action,
    build_agent_observation,
    clear_task_history,
)
from board_automation.board.task_router import load_tasks  # noqa: E402
from board_automation.board.task_status_workflow import EVENT_TARGET  # noqa: E402
from lib.orchestrator.claim_lock import load_locks, release_lock, save_locks  # noqa: E402

ensure_env()

DEMO_WS = DEMO_DIR / "workspace"
REPORT_PATH = DEMO_DIR / "demo_apresentacao_report.json"
DEFAULT_TASK = "T-P05-005"

# claim -> implement -> review -> QA -> Done (merge_pr com HITL; narrado como validacao QA)
PIPELINE: list[tuple[str, str]] = [
    ("claim", "creator"),
    ("__implement__", "creator"),
    ("open_pr", "creator"),
    ("start_review", "reviewer"),
    ("approve_review", "reviewer"),
    ("start_test", "qa-gate"),
    ("test_passed", "qa-gate"),
    ("merge_pr", "qa-gate"),
]

# Raciocinio didatico por evento (thought / action / observation / executed)
# Campos opcionais: deliverables, test_scenarios, findings
DEMO_ACTIONS: dict[str, dict[str, Any]] = {
    "claim": {
        "thought": (
            "A task T-P05-005 (Configurar APNs production certificates) esta em Todo, "
            "sem depends_on pendente no mapa. O parent app precisa de certificados APNs "
            "de producao para push confiavel (SOS/alertas familiares). Vou claimar com o "
            "role frontend-mobile, adquirir lock WIP e comecar pela matriz de certificados "
            "e bundle id antes de qualquer commit."
        ),
        "action": (
            "Validar elegibilidade (WIP/depends_on), emitir claim no gateway e mover o card "
            "para In Progress com lock do creator."
        ),
        "observation": (
            "Board local em In Progress; agente frontend-mobile busy; historico da task aberto "
            "para registrar o restante do ciclo."
        ),
        "executed": [
            "check_claim_allowed(frontend-mobile)",
            "dependencies_satisfied(T-P05-005)",
            "emit_status_event(claim)",
            "update_local_status(In Progress)",
            "acquire_lock WIP",
        ],
    },
    "__implement__": {
        "thought": (
            "Com a task claimada, preciso entregar evidencia didatica de implementacao APNs "
            "production sem depender do SDK Cursor ao vivo.\n\n"
            "Plano de implementacao:\n"
            "1) Documentar ambiente production (nao sandbox) e bundle id do parent app.\n"
            "2) Descrever o fluxo de certificado: Apple Developer → Key/Certificate → "
            "export .p12/.p8 → configuracao no provedor de push (Expo/FCM bridge / APNs direto).\n"
            "3) Listar riscos: certificado expirado, ambiente errado (sandbox vs prod), "
            "mismatch de bundle id, token device invalido.\n"
            "4) Gerar artefato local commitavel (IMPLEMENTACAO.md + metricas) para o reviewer "
            "e o QA terem evidencia concreta no historico.\n\n"
            "Decisao: manter o trabalho no demo_workspace da task (escopo academico), com "
            "commit git apenas desses arquivos — suficiente para narrar claim→implement→PR."
        ),
        "action": (
            "Escrever IMPLEMENTACAO.md com matriz APNs (ambiente, bundle, certs, validacoes) "
            "e agent_metrics.json; git add + git commit local desses paths."
        ),
        "observation": (
            "Artefatos gravados em agents/00-runtime/output/demo/workspace/T-P05-005/; commit local criado; "
            "pronto para open_pr simbolico com react_trace."
        ),
        "executed": [
            "mkdir demo_workspace/T-P05-005",
            "escrever matriz APNs em IMPLEMENTACAO.md",
            "escrever agent_metrics.json (agent_role, demo=true)",
            "git add (apenas paths da task)",
            "git commit (author demo local)",
        ],
        "deliverables": [
            {
                "path": "IMPLEMENTACAO.md",
                "what": (
                    "Matriz didatica APNs production: ambiente, bundle id, tipo de chave "
                    "(Auth Key .p8 ou certificado .p12), checklist de configuracao no parent app "
                    "e notas de validacao de push."
                ),
            },
            {
                "path": "agent_metrics.json",
                "what": "Metadados do passo (task_id, agent_role, timestamp) para auditoria no dashboard.",
            },
        ],
    },
    "open_pr": {
        "thought": (
            "Implementacao local commitada. Preciso abrir PR simbolica para o board avançar "
            "a Ready for Code Review e entregar handoff com react_trace ao reviewer "
            "(politica ReAct exige trace no open_pr)."
        ),
        "action": (
            "emit open_pr com branch demo/t-p05-005, pr_url de exemplo e react_trace "
            "descrevendo a matriz APNs commitada; liberar lock de claim."
        ),
        "observation": "Status Ready for Code Review; lock liberado; handoff aponta para frontend-mobile-reviewer.",
        "executed": [
            "montar react_trace da implementacao",
            "emit_status_event(open_pr)",
            "write_handoff → reviewer",
            "release_lock(T-P05-005)",
        ],
        "deliverables": [
            {
                "path": "PR simbolica",
                "what": "https://example.com/demo/T-P05-005 — evidencia de entrega para CR (demo academica).",
            }
        ],
    },
    "start_review": {
        "thought": (
            "Como frontend-mobile-reviewer, entro em Code Review focando: (a) ambiente production "
            "declarado, (b) bundle id coerente, (c) tipo de credencial APNs documentado, "
            "(d) riscos de mismatch sandbox/prod e expiracao de cert."
        ),
        "action": "Carregar handoff da task e emitir start_review (In Code Review).",
        "observation": "Status In Code Review; reviewer busy no dashboard.",
        "executed": [
            "load_handoff(T-P05-005)",
            "ler IMPLEMENTACAO.md / react_trace",
            "emit_status_event(start_review)",
        ],
    },
    "approve_review": {
        "thought": (
            "Checklist de CR APNs:\n"
            "- Ambiente: production (ok)\n"
            "- Bundle id / team documentados no artefato (ok)\n"
            "- Fluxo de chave/cert descrito com riscos (ok)\n"
            "- Evidencia de commit local presente (ok)\n\n"
            "Nao ha blocker de seguranca no escopo didatico. Proponho approve; se HITL "
            "estiver em propose_only, o humano confirma e a fila segue para qa-gate."
        ),
        "action": "emit approve_review (+ approve_hitl se necessario) → Ready for Test.",
        "observation": "Status Ready for Test; handoff segue para QA.",
        "executed": [
            "checklist CR APNs",
            "emit_status_event(approve_review)",
            "HITL confirm se propose_only",
        ],
        "findings": [
            {"severity": "pass", "item": "Ambiente APNs production declarado"},
            {"severity": "pass", "item": "Bundle id / escopo parent app documentado"},
            {"severity": "pass", "item": "Riscos sandbox vs prod e expiracao de cert citados"},
            {"severity": "pass", "item": "Commit local de evidencia presente"},
        ],
    },
    "start_test": {
        "thought": (
            "Sou o qa-gate. Vou montar o plano de testes de aceite para APNs production "
            "com base no artefato do creator e no veredito do reviewer. O objetivo e "
            "provar (didaticamente) que a configuracao cobre os caminhos criticos de push "
            "antes de liberar In Pull Request / Done."
        ),
        "action": (
            "emit start_test e registrar o plano formal de cenarios (matriz de aceite) "
            "no historico da task."
        ),
        "observation": "Status In Test; plano de cenarios publicado no detalhe da task.",
        "executed": [
            "ler criterios de aceite da task",
            "montar matriz de cenarios QA",
            "emit_status_event(start_test)",
        ],
        "test_scenarios": [
            {
                "id": "QA-APNS-01",
                "name": "Certificado/Auth Key production carregado",
                "type": "config",
                "steps": (
                    "Verificar no artefato se o ambiente e production e se o tipo de "
                    "credencial (.p8 Auth Key ou .p12) esta definido."
                ),
                "expected": "Ambiente production + credencial documentada sem ambiguidade.",
                "result": "planned",
            },
            {
                "id": "QA-APNS-02",
                "name": "Bundle id do parent app coerente",
                "type": "config",
                "steps": "Confrontar bundle id citado na IMPLEMENTACAO com o escopo do parent app.",
                "expected": "Bundle id alinhado; sem referencia a target de sandbox/dev.",
                "result": "planned",
            },
            {
                "id": "QA-APNS-03",
                "name": "Push foreground (app aberto)",
                "type": "funcional",
                "steps": (
                    "Simular recebimento de notificacao com app em foreground; validar que "
                    "o handler de notificacao esta previsto na documentacao."
                ),
                "expected": "Caminho foreground descrito; sem erro de ambiente sandbox.",
                "result": "planned",
            },
            {
                "id": "QA-APNS-04",
                "name": "Push background / app morto",
                "type": "funcional",
                "steps": "Simular push com app em background ou killed; checar expectativa de delivery APNs prod.",
                "expected": "Cenario background documentado como coberto pela config production.",
                "result": "planned",
            },
            {
                "id": "QA-APNS-05",
                "name": "Falha controlada: cert expirado / ambiente errado",
                "type": "negativo",
                "steps": (
                    "Validar se o artefato lista sintoma e mitigacao para certificado expirado "
                    "ou uso acidental de sandbox em prod."
                ),
                "expected": "Riscos e mitigacoes presentes (reemissao / troca de ambiente).",
                "result": "planned",
            },
            {
                "id": "QA-APNS-06",
                "name": "Regressao SOS / alerta familiar (smoke)",
                "type": "smoke",
                "steps": (
                    "Checar se a documentacao conecta APNs prod ao fluxo de alerta critico "
                    "do Guardião Família (smoke de aceite)."
                ),
                "expected": "Trilha critica mencionada; sem regressao de escopo.",
                "result": "planned",
            },
        ],
    },
    "test_passed": {
        "thought": (
            "Executei a matriz de aceite contra o artefato e o handoff. Todos os cenarios "
            "planejados passaram no escopo didatico (evidencia documental + checklist). "
            "Posso emitir test_passed e mover para In Pull Request."
        ),
        "action": "Registrar resultados PASS da matriz e emitir test_passed.",
        "observation": "Status In Pull Request; evidencia de QA no historico da task.",
        "executed": [
            "executar QA-APNS-01..06 contra artefato",
            "marcar resultados PASS",
            "emit_status_event(test_passed)",
        ],
        "test_scenarios": [
            {
                "id": "QA-APNS-01",
                "name": "Certificado/Auth Key production carregado",
                "type": "config",
                "steps": "Conferir ambiente production + tipo de credencial no artefato.",
                "expected": "Production + credencial clara.",
                "result": "PASS",
                "notes": "IMPLEMENTACAO.md declara production e fluxo de chave/cert.",
            },
            {
                "id": "QA-APNS-02",
                "name": "Bundle id do parent app coerente",
                "type": "config",
                "steps": "Validar bundle id / escopo parent.",
                "expected": "Sem mismatch sandbox/dev.",
                "result": "PASS",
                "notes": "Escopo parent app e bundle citados na matriz.",
            },
            {
                "id": "QA-APNS-03",
                "name": "Push foreground (app aberto)",
                "type": "funcional",
                "steps": "Simular aceite foreground via checklist documentado.",
                "expected": "Caminho foreground coberto.",
                "result": "PASS",
                "notes": "Checklist de validacao de push inclui foreground.",
            },
            {
                "id": "QA-APNS-04",
                "name": "Push background / app morto",
                "type": "funcional",
                "steps": "Simular aceite background via checklist.",
                "expected": "Delivery APNs prod esperado.",
                "result": "PASS",
                "notes": "Cenario background listado nas notas de validacao.",
            },
            {
                "id": "QA-APNS-05",
                "name": "Falha controlada: cert expirado / ambiente errado",
                "type": "negativo",
                "steps": "Conferir riscos e mitigacoes no artefato.",
                "expected": "Riscos documentados.",
                "result": "PASS",
                "notes": "Risco sandbox vs prod e expiracao de cert presentes.",
            },
            {
                "id": "QA-APNS-06",
                "name": "Regressao SOS / alerta familiar (smoke)",
                "type": "smoke",
                "steps": "Smoke de trilha critica Guardião Família.",
                "expected": "Sem regressao de escopo.",
                "result": "PASS",
                "notes": "Contexto SOS/alertas familiares amarrado a APNs prod.",
            },
        ],
    },
    "merge_pr": {
        "thought": (
            "Validacao final do QA: matriz QA-APNS-01..06 em PASS, CR aprovado, evidencia "
            "de commit local. Com HITL humano no merge, defino a task como Done — "
            "encerrando o ciclo academico completo."
        ),
        "action": "emit merge_pr (HITL) — QA + humano marcam Done.",
        "observation": "Status Done. Historico completo permanece em tasks/T-P05-005.html.",
        "executed": [
            "revisar matriz QA PASS",
            "HITL approve merge (se block_until_human)",
            "emit_status_event(merge_pr)",
            "update_local_status(Done)",
        ],
    },
}


# Overrides por task (senão usa DEMO_ACTIONS genérico de APNs / default)
TASK_DEMO_OVERRIDES: dict[str, dict[str, dict[str, Any]]] = {
    "T-P05-006": {
        "claim": {
            "thought": (
                "Task T-P05-006 (Configurar FCM data messages SOS) elegivel no Project #2 "
                "(Status Todo, sem depends_on). Preciso claimar frontend-mobile para "
                "documentar data messages FCM do fluxo SOS."
            ),
            "action": "emit claim + lock WIP frontend-mobile (Project #2 + board local)",
            "observation": "In Progress no board local; sync Project via gateway/gh.",
            "executed": [
                "check_claim_allowed",
                "dependencies_satisfied",
                "emit claim",
                "update Project Status In Progress",
            ],
        },
        "__implement__": {
            "thought": (
                "Plano FCM data messages SOS:\n"
                "1) Distinguir notification vs data message no parent.\n"
                "2) Payload minimo SOS (type, childId, lat/lng, ts).\n"
                "3) Handler em foreground/background sem perder data.\n"
                "4) Evidencia didatica commitavel para CR/QA."
            ),
            "action": "Escrever IMPLEMENTACAO.md (matriz FCM SOS) + metrics + git commit",
            "observation": "Artefato local pronto; Project ainda In Progress ate open_pr.",
            "executed": [
                "mkdir demo_workspace/T-P05-006",
                "matriz FCM data message SOS",
                "git commit paths da task",
            ],
            "deliverables": [
                {
                    "path": "IMPLEMENTACAO.md",
                    "what": "Matriz FCM data messages SOS: payload, handlers, riscos, criterios QA.",
                },
                {
                    "path": "agent_metrics.json",
                    "what": "Metadados do passo para auditoria.",
                },
            ],
        },
        "start_test": {
            "thought": "QA-gate: plano de aceite FCM data messages SOS contra o artefato.",
            "action": "emit start_test + registrar cenarios QA-FCM-01..06",
            "observation": "In Test; matriz de cenarios no historico.",
            "executed": ["montar matriz QA FCM", "emit start_test"],
            "test_scenarios": [
                {
                    "id": "QA-FCM-01",
                    "name": "Data message vs notification message",
                    "type": "config",
                    "steps": "Conferir documentacao da diferenca data/notification no artefato.",
                    "expected": "Data message SOS documentada.",
                    "result": "planned",
                },
                {
                    "id": "QA-FCM-02",
                    "name": "Payload minimo SOS",
                    "type": "contrato",
                    "steps": "Validar campos type/childId/coords/ts.",
                    "expected": "Campos obrigatorios listados.",
                    "result": "planned",
                },
                {
                    "id": "QA-FCM-03",
                    "name": "Handler foreground",
                    "type": "funcional",
                    "steps": "Checklist recebimento com app aberto.",
                    "expected": "Handler foreground descrito.",
                    "result": "planned",
                },
                {
                    "id": "QA-FCM-04",
                    "name": "Handler background / killed",
                    "type": "funcional",
                    "steps": "Checklist data message em background.",
                    "expected": "Caminho background coberto.",
                    "result": "planned",
                },
                {
                    "id": "QA-FCM-05",
                    "name": "Falha: payload incompleto",
                    "type": "negativo",
                    "steps": "Riscos de campos ausentes / parse.",
                    "expected": "Mitigacao documentada.",
                    "result": "planned",
                },
                {
                    "id": "QA-FCM-06",
                    "name": "Smoke latencia SOS (KR O1)",
                    "type": "smoke",
                    "steps": "Amarrar data message ao KR <30s.",
                    "expected": "Trilha critica citada.",
                    "result": "planned",
                },
            ],
        },
        "test_passed": {
            "thought": "Matriz QA-FCM-01..06 PASS no escopo didatico. Liberar In Pull Request.",
            "action": "Registrar PASS e emit test_passed",
            "observation": "In Pull Request no board; sync Project.",
            "executed": ["executar QA-FCM-01..06", "emit test_passed"],
            "test_scenarios": [
                {
                    "id": "QA-FCM-01",
                    "name": "Data message vs notification message",
                    "type": "config",
                    "steps": "Conferir artefato.",
                    "expected": "Data message documentada.",
                    "result": "PASS",
                    "notes": "Matriz FCM distingue data vs notification.",
                },
                {
                    "id": "QA-FCM-02",
                    "name": "Payload minimo SOS",
                    "type": "contrato",
                    "steps": "Campos obrigatorios.",
                    "expected": "Contrato presente.",
                    "result": "PASS",
                    "notes": "type/childId/coords/ts listados.",
                },
                {
                    "id": "QA-FCM-03",
                    "name": "Handler foreground",
                    "type": "funcional",
                    "steps": "Checklist foreground.",
                    "expected": "Coberto.",
                    "result": "PASS",
                    "notes": "Handler foreground no artefato.",
                },
                {
                    "id": "QA-FCM-04",
                    "name": "Handler background / killed",
                    "type": "funcional",
                    "steps": "Checklist background.",
                    "expected": "Coberto.",
                    "result": "PASS",
                    "notes": "Background/killed descritos.",
                },
                {
                    "id": "QA-FCM-05",
                    "name": "Falha: payload incompleto",
                    "type": "negativo",
                    "steps": "Riscos.",
                    "expected": "Mitigacao.",
                    "result": "PASS",
                    "notes": "Riscos de parse documentados.",
                },
                {
                    "id": "QA-FCM-06",
                    "name": "Smoke latencia SOS (KR O1)",
                    "type": "smoke",
                    "steps": "KR O1.",
                    "expected": "Trilha critica.",
                    "result": "PASS",
                    "notes": "Amarrado ao SOS <30s.",
                },
            ],
        },
        "merge_pr": {
            "thought": (
                "QA valida FCM SOS no Project #2: cenarios PASS + HITL. "
                "Marco Done no board local e Project."
            ),
            "action": "emit merge_pr (HITL) → Done no Project #2",
            "observation": "Done local + remoto (ou outbox se gh falhar).",
            "executed": ["HITL merge", "emit merge_pr", "Project Status Done"],
        },
    },
}


def _demo_for(task_id: str, event: str) -> dict[str, Any]:
    base = dict(DEMO_ACTIONS.get(event) or {})
    over = (TASK_DEMO_OVERRIDES.get(task_id) or {}).get(event) or {}
    merged = {**base, **over}
    return merged


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _task(task_id: str) -> dict[str, Any]:
    t = next((x for x in load_tasks() if x["id"] == task_id), None)
    if not t:
        raise SystemExit(f"Task {task_id} nao encontrada no mapa")
    return t


def _role(task: dict[str, Any], who: str) -> str:
    creator = normalize_creator_role(task.get("agent_role") or "frontend-mobile")
    if who == "creator":
        return creator
    if who == "reviewer":
        return reviewer_for(creator)
    return "qa-gate"


def _pause(seconds: float, label: str) -> None:
    print(f"\n>>> PAUSA {seconds:.0f}s - olhe o dashboard ({label}) <<<\n", flush=True)
    time.sleep(seconds)


def _announce(msg: str) -> None:
    print(f"\n{'='*60}\n{msg}\n{'='*60}", flush=True)


def reset_task(task_id: str) -> None:
    """Volta task ao zero: Todo, sem lock, sem HITL/jobs da task."""
    update_local_status(task_id, "Todo")
    release_lock(task_id)
    clear_task_history(task_id)
    locks = load_locks()
    by_role = locks.get("by_role") or {}
    for role, ids in list(by_role.items()):
        by_role[role] = [t for t in ids if t != task_id]
    save_locks(locks)

    rt = load_runtime()
    rt["hitl_queue"] = [
        h for h in (rt.get("hitl_queue") or []) if h.get("task_id") != task_id
    ]
    rt["dispatch_queue"] = [
        d for d in (rt.get("dispatch_queue") or []) if d.get("task_id") != task_id
    ]
    # Limpa idempotencia da task (senão claim/open_pr voltam duplicate sem mudar Status)
    idem = rt.get("idempotency") or {}
    rt["idempotency"] = {
        k: v
        for k, v in idem.items()
        if task_id not in k and (not isinstance(v, dict) or v.get("task_id") != task_id)
    }
    for name, meta in (rt.get("agents") or {}).items():
        if meta.get("task_id") == task_id:
            meta["state"] = "idle"
            meta["task_id"] = None
            meta["updated_at"] = _now()
    save_runtime(rt)
    write_dashboard(build_snapshot())
    _announce(f"RESET {task_id} -> Todo (locks/HITL limpos)")


def _emit(task_id: str, event: str, role: str, *, force_hitl: bool = False) -> dict[str, Any]:
    demo = _demo_for(task_id, event)
    kwargs: dict[str, Any] = {
        "from_agent": role,
        "summary": f"demo_apresentacao · {role} · {event}",
        "dry_run": False,
        "react_trace": [
            {
                "thought": demo.get("thought") or f"Executar {event}",
                "action": demo.get("action") or event,
                "observation": demo.get("observation") or "",
            }
        ],
    }
    if event == "open_pr":
        kwargs["pr_url"] = f"https://example.com/demo/{task_id}"
        kwargs["branch"] = f"demo/{task_id.lower()}"
    if force_hitl:
        kwargs["force_hitl_approved"] = True
    try:
        return emit_status_event(task_id, event, **kwargs)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "status": "error"}


def _record_history(
    task_id: str,
    *,
    event: str,
    role: str,
    before: str | None,
    after: str | None,
    ok: bool,
    extra: dict[str, Any] | None = None,
) -> None:
    demo = _demo_for(task_id, event)
    task = _task(task_id)
    hist_extra = dict(extra or {})
    hist_extra.setdefault(
        "focus",
        str(demo.get("focus") or f"evento `{event}` ({before} → {after})"),
    )
    hist_extra.setdefault("model", hist_extra.get("model") or "demo/scripted")
    hist_extra.setdefault("purpose", hist_extra.get("purpose") or "demo_apresentacao")
    observation = build_agent_observation(
        str(hist_extra["focus"]),
        extra=hist_extra,
        detail=str(demo.get("observation") or ""),
        ok=ok,
    )
    append_task_action(
        task_id,
        agent=role,
        event=event,
        from_status=before,
        to_status=after,
        thought=str(demo.get("thought") or f"Passo {event}"),
        action=str(demo.get("action") or event),
        observation=observation,
        executed=list(demo.get("executed") or []),
        deliverables=list(demo.get("deliverables") or []) or None,
        test_scenarios=list(demo.get("test_scenarios") or []) or None,
        findings=list(demo.get("findings") or []) or None,
        title=str(task.get("title") or task_id),
        ok=ok,
        extra=hist_extra,
    )


def _step_ok(out: dict[str, Any], after: str | None, event: str) -> bool:
    expected = EVENT_TARGET.get(event)
    if out.get("duplicate") and expected and after != expected:
        return False
    if expected and after == expected:
        return True
    if out.get("ok") and not out.get("duplicate"):
        return True
    if out.get("status") in ("applied", "propose_only") and expected and after == expected:
        return True
    return False


def run_event_step(
    task_id: str,
    event: str,
    who: str,
    *,
    auto_hitl: bool,
) -> dict[str, Any]:
    task = _task(task_id)
    role = _role(task, who)
    before = get_local_status(task_id)
    set_agent_state(role, "busy", task_id)
    write_dashboard(build_snapshot())

    out = _emit(task_id, event, role)
    hitl_resolved = False
    if auto_hitl and out.get("ok") and out.get("status") in ("awaiting_human", "propose_only"):
        hitl = approve_hitl(task_id, event, dry_run=False)
        hitl_resolved = bool(hitl.get("ok"))
        if hitl.get("status") != "applied":
            out = _emit(task_id, event, role, force_hitl=True)
        else:
            out = hitl

    after = get_local_status(task_id)
    ok = _step_ok(out, after, event)
    if event == "open_pr" and ok:
        release_lock(task_id)

    set_agent_state(role, "idle", None)
    log_workflow_event(
        "demo_step",
        task_id=task_id,
        agent=role,
        event=event,
        from_status=before,
        to_status=after,
        summary=f"demo {who}/{role}",
        extra={"ok": ok, "hitl_resolved": hitl_resolved},
    )
    _record_history(
        task_id,
        event=event,
        role=role,
        before=before,
        after=after,
        ok=ok,
        extra={"hitl_resolved": hitl_resolved, "gateway_status": out.get("status")},
    )
    write_dashboard(build_snapshot())
    return {
        "task_id": task_id,
        "event": event,
        "role": role,
        "who": who,
        "before": before,
        "after": after,
        "ok": ok,
        "status": out.get("status"),
        "error": out.get("error"),
        "hitl_resolved": hitl_resolved,
        "detail_url": f"tasks/{task_id}.html",
        "at": _now(),
    }


def implement_and_commit(task_id: str) -> dict[str, Any]:
    """Simula implementação do creator: artefato local + git commit."""
    task = _task(task_id)
    role = _role(task, "creator")
    set_agent_state(role, "busy", task_id)
    write_dashboard(build_snapshot())

    ws = DEMO_WS / task_id
    ws.mkdir(parents=True, exist_ok=True)
    readme = ws / "IMPLEMENTACAO.md"
    if task_id == "T-P05-006":
        body = [
            f"# Implementacao — `{task_id}`",
            "",
            f"**Titulo:** {task.get('title')}",
            f"**Agente:** {role}",
            f"**Repo alvo (mapa):** {task.get('repo')}",
            f"**Gerado em:** {_now()}",
            f"**Fonte board:** GitHub Project #2 (guardiaofamilia)",
            "",
            "## Raciocinio do developer",
            "",
            "SOS no Android/parent depende de **FCM data messages** (nao so notification message)",
            "para o app processar payload mesmo em background. Esta entrega documenta o contrato",
            "data message + handlers, com evidencia commitavel alinhada ao Project #2.",
            "",
            "## O que foi implementado (didatico)",
            "",
            "1. Distincao notification vs data message.",
            "2. Payload minimo SOS (type, childId, lat/lng, ts).",
            "3. Handlers foreground / background / killed.",
            "4. Riscos (payload incompleto, token FCM invalido) e criterios QA-FCM.",
            "",
            "## Matriz FCM data message SOS",
            "",
            "| Item | Valor / decisao |",
            "|------|-----------------|",
            "| Canal | FCM data message |",
            "| App | Parent Guardião Família |",
            "| Payload | type=sos, childId, lat, lng, ts |",
            "| Prioridade | high (SOS) |",
            "| Segredo | server key / SA fora do git |",
            "",
            "## Checklist",
            "",
            "- [ ] Servidor envia data-only (ou data+notification) conforme contrato",
            "- [ ] Parent registra handler data message",
            "- [ ] Foreground nao descarta payload",
            "- [ ] Background/killed acorda fluxo SOS",
            "- [ ] Telemetria de latencia alinhada ao KR O1 (<30s)",
            "",
            "## Riscos",
            "",
            "| Risco | Mitigacao |",
            "|-------|-----------|",
            "| So notification message | Forcar data payload |",
            "| Campos ausentes | Validar schema no client |",
            "| Token FCM expirado | Re-registro device |",
            "",
            "## Validacao QA",
            "",
            "QA-FCM-01..06 (ver historico da task no dashboard)",
            "",
            "## Pipeline",
            "",
            "claim → implement → open_pr → review → QA → Done (Project #2)",
            "",
        ]
    else:
        body = [
            f"# Implementacao — `{task_id}`",
            "",
            f"**Titulo:** {task.get('title')}",
            f"**Agente:** {role}",
            f"**Repo alvo (mapa):** {task.get('repo')}",
            f"**Gerado em:** {_now()}",
            "",
            "## Raciocinio do developer",
            "",
            "Push no Guardião Família (SOS/alertas) depende de APNs **production** no parent app.",
            "Sandbox mascara falhas de certificado e bundle. Esta entrega documenta a matriz",
            "de configuracao e os riscos, com evidencia commitavel para CR e QA.",
            "",
            "## O que foi implementado (didatico)",
            "",
            "1. Matriz APNs production (ambiente, credencial, bundle).",
            "2. Checklist de configuracao no parent app / provedor de push.",
            "3. Riscos e mitigacoes (sandbox vs prod, cert expirado, token invalido).",
            "4. Criterios de validacao que o QA usara (foreground/background/smoke).",
            "",
            "## Matriz APNs",
            "",
            "| Item | Valor / decisao |",
            "|------|-----------------|",
            "| Ambiente | **production** (nao sandbox) |",
            "| App | Parent app Guardião Família |",
            "| Bundle id | Documentar o bundle de producao do parent (mapa da task) |",
            "| Credencial | Auth Key `.p8` (preferencial) ou certificado `.p12` |",
            "| Provedor | Expo Notifications / bridge FCM-APNs / APNs direto |",
            "| Segredo | Fora do git; apenas referencia no runbook |",
            "",
            "## Checklist de configuracao",
            "",
            "- [ ] Criar/renovar chave ou certificado no Apple Developer (production)",
            "- [ ] Associar Team ID + Key ID (ou cert) ao provedor de push",
            "- [ ] Confirmar bundle id do target de producao",
            "- [ ] Remover/ignorar credencial sandbox no profile de release",
            "- [ ] Registrar data de expiracao / rotacao da chave",
            "",
            "## Riscos e mitigacoes",
            "",
            "| Risco | Sintoma | Mitigacao |",
            "|-------|---------|-----------|",
            "| Ambiente sandbox em release | Push falha so em TestFlight/App Store | Travar profile production |",
            "| Certificado expirado | 403/InvalidProviderToken | Renovar `.p8`/`.p12` e rotacionar |",
            "| Bundle mismatch | Device nao registra token | Alinhar bundle id parent |",
            "| Token device invalido | Silent fail no destinatario | Re-opt-in notificacoes |",
            "",
            "## Validacao sugerida (QA)",
            "",
            "- QA-APNS-01 credencial production",
            "- QA-APNS-02 bundle id coerente",
            "- QA-APNS-03 push foreground",
            "- QA-APNS-04 push background / killed",
            "- QA-APNS-05 falha controlada (cert/ambiente)",
            "- QA-APNS-06 smoke SOS / alerta familiar",
            "",
            "## Pipeline da demo",
            "",
            "claim → implement/commit → open_pr → review → QA → Done (HITL)",
            "",
        ]
    readme.write_text("\n".join(body), encoding="utf-8")
    meta = ws / "agent_metrics.json"
    meta.write_text(
        json.dumps(
            {
                "task_id": task_id,
                "agent_role": role,
                "demo": True,
                "at": _now(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    rel = [
        str((ws / "IMPLEMENTACAO.md").relative_to(REPO_ROOT)).replace("\\", "/"),
        str((ws / "agent_metrics.json").relative_to(REPO_ROOT)).replace("\\", "/"),
    ]
    commit_hash = None
    commit_ok = False
    err = None
    try:
        subprocess.run(
            ["git", "add", "--", *rel],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        msg = f"demo(agents): implementacao local {task_id} (apresentacao live)"
        # Identidade so neste processo (nao altera git config)
        commit_env = os.environ.copy()
        commit_env.setdefault("GIT_AUTHOR_NAME", "Demo Apresentacao")
        commit_env.setdefault("GIT_AUTHOR_EMAIL", "demo-apresentacao@local.invalid")
        commit_env.setdefault("GIT_COMMITTER_NAME", commit_env["GIT_AUTHOR_NAME"])
        commit_env.setdefault("GIT_COMMITTER_EMAIL", commit_env["GIT_AUTHOR_EMAIL"])
        r = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env=commit_env,
        )
        if r.returncode != 0 and "nothing to commit" in (r.stdout + r.stderr):
            commit_ok = True
            commit_hash = "unchanged"
        elif r.returncode != 0:
            err = (r.stderr or r.stdout or "commit failed").strip()
        else:
            commit_ok = True
            h = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                check=True,
            )
            commit_hash = (h.stdout or "").strip()
    except Exception as exc:  # noqa: BLE001
        err = str(exc)

    status_now = get_local_status(task_id)
    set_agent_state(role, "idle", None)
    log_workflow_event(
        "demo_implement",
        task_id=task_id,
        agent=role,
        event="implement",
        from_status=status_now,
        to_status=status_now,
        summary=f"commit local {commit_hash or 'falhou'}",
        extra={"paths": rel, "commit": commit_hash, "ok": commit_ok, "error": err},
    )
    ok = commit_ok and status_now == "In Progress"
    _record_history(
        task_id,
        event="__implement__",
        role=role,
        before=status_now,
        after=status_now,
        ok=ok,
        extra={"commit": commit_hash, "paths": rel},
    )
    write_dashboard(build_snapshot())
    return {
        "task_id": task_id,
        "event": "__implement__",
        "role": role,
        "who": "creator",
        "before": status_now,
        "after": status_now,
        "ok": ok,
        "commit": commit_hash,
        "paths": rel,
        "error": err or (None if status_now == "In Progress" else f"status inesperado: {status_now}"),
        "detail_url": f"tasks/{task_id}.html",
        "at": _now(),
    }


def run_demo(
    task_id: str,
    *,
    delay: float,
    from_zero: bool,
    auto_hitl: bool,
) -> dict[str, Any]:
    delay = max(5.0, float(delay))
    log: list[dict[str, Any]] = []

    if from_zero:
        reset_task(task_id)
        _pause(delay, "apos reset - card deve estar em Todo")

    for event, who in PIPELINE:
        if event == "__implement__":
            _announce(f"IMPLEMENTAR ({_role(_task(task_id), 'creator')})")
            row = implement_and_commit(task_id)
            log.append(row)
            print(json.dumps(row, ensure_ascii=False, indent=2), flush=True)
            if not row.get("ok"):
                break
            _pause(delay, "apos implement/commit - timeline demo_implement")
            continue

        _announce(f"EVENTO {event} · papel={who} · agente={_role(_task(task_id), who)}")
        row = run_event_step(task_id, event, who, auto_hitl=auto_hitl)
        log.append(row)
        print(json.dumps(row, ensure_ascii=False, indent=2), flush=True)
        if not row.get("ok"):
            break
        _pause(delay, f"apos {event} -> {row.get('after')}")

    final = get_local_status(task_id)
    report = {
        "ok": final == "Done" and all(x.get("ok") for x in log),
        "task_id": task_id,
        "final_status": final,
        "delay_seconds": delay,
        "merge_attempted": True,
        "detail_url": f"tasks/{task_id}.html",
        "log": log,
        "finished_at": _now(),
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(REPORT_PATH)
    write_dashboard(build_snapshot())
    return report


def main() -> int:
    p = argparse.ArgumentParser(description="Demo apresentacao live (paced)")
    p.add_argument("--task", default=DEFAULT_TASK)
    p.add_argument("--delay", type=float, default=6.0, help="Segundos entre passos (min 5)")
    p.add_argument("--from-zero", action="store_true", help="Reset Todo + limpar estado da task")
    p.add_argument("--no-auto-hitl", action="store_true")
    p.add_argument("--reset-only", action="store_true")
    args = p.parse_args()

    if args.reset_only:
        reset_task(args.task)
        print(json.dumps({"ok": True, "status": get_local_status(args.task)}, indent=2))
        return 0

    report = run_demo(
        args.task,
        delay=args.delay,
        from_zero=args.from_zero,
        auto_hitl=not args.no_auto_hitl,
    )
    # --from-zero: um retry embutido se a 1a passagem falhar
    if args.from_zero and not report.get("ok"):
        print("\n*** DEMO falhou; retry unico com reset --from-zero ***\n", flush=True)
        report = run_demo(
            args.task,
            delay=args.delay,
            from_zero=True,
            auto_hitl=not args.no_auto_hitl,
        )
    print(json.dumps({
        "ok": report.get("ok"),
        "task_id": report.get("task_id"),
        "final_status": report.get("final_status"),
        "steps_ok": sum(1 for x in report.get("log") or [] if x.get("ok")),
        "steps_total": len(report.get("log") or []),
        "merge_attempted": report.get("merge_attempted"),
        "detail_url": report.get("detail_url"),
        "report_path": report.get("report_path"),
        "commit": next(
            (x.get("commit") for x in (report.get("log") or []) if x.get("event") == "__implement__"),
            None,
        ),
    }, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
