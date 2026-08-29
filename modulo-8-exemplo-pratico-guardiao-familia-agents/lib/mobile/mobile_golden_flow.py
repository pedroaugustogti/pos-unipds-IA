"""Golden path Appium → SQLite + pgvector (cadastro parent + pairing child)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lib.mobile.mobile_runtime_config import APP_STACKS, appium_env
from lib.mobile.mobile_user_flow_db import upsert_app, upsert_flow

GOLDEN_FLOW_ID = "golden:parent_register_child_pairing"
DEFAULT_TRAIL_REL = "test/appium/reports/golden-parent-register-child-pairing.json"


def default_trail_path(*, api_repo: Path | None = None) -> Path:
    from lib.mobile.mobile_setup_client import handoff_path

    return handoff_path()


def handoff_to_golden_trail(data: dict[str, Any]) -> dict[str, Any]:
    last = data.get("lastStep") or ""
    steps = [
        {
            "order": 1,
            "phase": "parent",
            "screen": "AuthScreen",
            "user_action": "Cadastro + wizard família",
            "system_behavior": f"email={data.get('email')}",
            "appium_hint": "mobile-setup/create_account+config_family",
        },
        {
            "order": 2,
            "phase": "parent",
            "screen": "PairingCodesScreen",
            "user_action": "Copiar código pairing",
            "system_behavior": f"code={data.get('pairingCode')}",
            "appium_hint": "mobile-setup/copy_code_pairing",
        },
        {
            "order": 3,
            "phase": "child",
            "screen": "PrePairingScreen",
            "user_action": "Colar código no child",
            "system_behavior": "Vínculo confirmado",
            "appium_hint": "mobile-setup/paste_code_parent",
        },
        {
            "order": 4,
            "phase": "parent",
            "screen": "ParentHome",
            "user_action": "Login parent + home",
            "system_behavior": f"lastStep={last}",
            "appium_hint": "mobile-setup/go_to_home_parent",
        },
    ]
    return {
        "flow_id": GOLDEN_FLOW_ID,
        "script": "guardiao-familia-mobile-setup/appium/run-all.mjs",
        "ok": last == "go_to_home_parent" or data.get("parentHome") is True,
        "generated_at": data.get("updated_at"),
        "parent_emulator": None,
        "child_emulator": None,
        "parent_email": data.get("email"),
        "steps": steps,
    }


def load_golden_trail(path: Path | None = None) -> dict[str, Any]:
    p = path or default_trail_path()
    if not p.is_file():
        raise FileNotFoundError(f"Golden trail não encontrado: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    if p.name == "stage-handoff.json":
        return handoff_to_golden_trail(raw)
    return raw


def trail_to_sqlite_steps(data: dict[str, Any]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for raw in data.get("steps") or []:
        steps.append(
            {
                "order": int(raw.get("order", len(steps))),
                "screen_id": f"{raw.get('phase', 'app')}:{raw.get('screen', 'unknown')}",
                "user_action": str(raw.get("user_action", "")),
                "system_behavior": str(raw.get("system_behavior", "")),
                "navigation_file": str(raw.get("appium_hint") or data.get("script") or ""),
                "route_condition": str(raw.get("handoff") or raw.get("at") or ""),
            }
        )
    return steps


def ingest_golden_trail_to_sqlite(data: dict[str, Any]) -> dict[str, Any]:
    parent = APP_STACKS["parent"]
    child = APP_STACKS["child"]
    upsert_app(
        "parent",
        repo=parent["repo"],
        bundle_id=parent["bundle_id"],
        metro_port=int(parent["metro_port"]),
        emulator=data.get("parent_emulator") or parent["emulator"],
    )
    upsert_app(
        "child",
        repo=child["repo"],
        bundle_id=child["bundle_id"],
        metro_port=int(child["metro_port"]),
        emulator=data.get("child_emulator") or child["emulator"],
    )

    steps = trail_to_sqlite_steps(data)
    qa = [
        f"python guardiao-familia-mobile-setup/appium/run_all.py",
        f"parent={data.get('parent_emulator')} child={data.get('child_emulator')}",
        f"email={data.get('parent_email', '(gerado)')}",
    ]
    mermaid = "\n".join(
        [
            "flowchart LR",
            "  A[Cadastro parent LGPD] --> B[Wizard família + filho]",
            "  B --> C[Login parent]",
            "  C --> D[Código pairing UI]",
            "  D --> E[Child PrePairing]",
            "  E --> F[Child Home]",
        ]
    )
    upsert_flow(
        GOLDEN_FLOW_ID,
        app_id="parent",
        entry_point="cold_start_parent",
        target_screen_id="child:ChildHome:runtime",
        flow_name="[golden] Cadastro parent + pairing child (Appium)",
        preconditions=[
            "Docker API :3000 + Postgres",
            "Metro parent :8082 e child :9090",
            "Emuladores dual isolados (5554/5556)",
            "Apps dev-client instalados",
        ],
        qa_repro_steps=qa,
        mermaid=mermaid,
        discovery_source="appium_golden",
        steps=steps,
    )
    return {
        "ok": bool(data.get("ok")),
        "flow_id": GOLDEN_FLOW_ID,
        "steps": len(steps),
        "generated_at": data.get("generated_at"),
    }


def iter_golden_trail_chunks(data: dict[str, Any]) -> list[dict[str, Any]]:
    steps = data.get("steps") or []
    lines = [
        f"Flow ID: {GOLDEN_FLOW_ID}",
        f"Script: {data.get('script')}",
        f"OK: {data.get('ok')}",
        f"Gerado: {data.get('generated_at')}",
        f"Parent emulator: {data.get('parent_emulator')}",
        f"Child emulator: {data.get('child_emulator')}",
        f"Email cadastro: {data.get('parent_email')}",
        "",
        "Passos cronológicos (cadastro → pairing):",
    ]
    for s in steps:
        lines.append(
            f"  {s.get('order')}. [{s.get('phase')}/{s.get('screen')}] "
            f"{s.get('user_action')} → {s.get('system_behavior')} "
            f"(appium: {s.get('appium_hint', '-')})"
        )
    full_content = "\n".join(lines)
    chunks: list[dict[str, Any]] = [
        {
            "chunk_id": f"golden_flow:{GOLDEN_FLOW_ID}",
            "flow_id": GOLDEN_FLOW_ID,
            "app_id": "parent",
            "chunk_type": "golden_flow",
            "title": "Golden path: cadastro parent + pairing child",
            "content": full_content,
            "metadata": {
                "script": data.get("script"),
                "ok": data.get("ok"),
                "step_count": len(steps),
                "generated_at": data.get("generated_at"),
            },
        }
    ]
    for s in steps:
        order = s.get("order", 0)
        phase = s.get("phase", "app")
        screen = s.get("screen", "?")
        chunk_id = f"golden_step:{GOLDEN_FLOW_ID}:{order:02d}"
        content = (
            f"Golden step {order} — {phase}/{screen}\n"
            f"Ação: {s.get('user_action')}\n"
            f"Sistema: {s.get('system_behavior')}\n"
            f"Appium: {s.get('appium_hint', '-')}\n"
            f"Handoff: {s.get('handoff', '-')}\n"
            f"Script: {data.get('script')}"
        )
        chunks.append(
            {
                "chunk_id": chunk_id,
                "flow_id": GOLDEN_FLOW_ID,
                "app_id": phase if phase in ("parent", "child") else "parent",
                "chunk_type": "golden_step",
                "title": f"Step {order}: {screen}",
                "content": content,
                "metadata": {
                    "order": order,
                    "phase": phase,
                    "screen": screen,
                    "handoff": s.get("handoff"),
                },
            }
        )
    return chunks


def ingest_golden_trail(*, trail_path: Path | None = None, use_fake_embed: bool = False) -> dict[str, Any]:
    from lib.mobile.mobile_flow_rag import stats_pg, upsert_chunks

    data = load_golden_trail(trail_path)
    sqlite_result = ingest_golden_trail_to_sqlite(data)
    chunks = iter_golden_trail_chunks(data)
    rag_result = upsert_chunks(chunks, use_fake_embed=use_fake_embed)
    return {
        **sqlite_result,
        "rag_upserted": rag_result.get("upserted", 0),
        "chunks_total": len(chunks),
        "pgvector": stats_pg(),
    }


def appium_env_for_golden(*, dual_emulator: bool = True) -> dict[str, str]:
    """Env para subprocess mobile-setup (legado — preferir run_golden())."""
    from lib.mobile.mobile_runtime_config import appium_env

    env = appium_env(dual_emulator=dual_emulator)
    from lib.mobile.mobile_setup_client import handoff_path

    env["GF_STAGE_HANDOFF_PATH"] = str(handoff_path())
    return env
