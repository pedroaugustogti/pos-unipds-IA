"""Guia de evidências mobile — levantamento LLM + seed RAG (Fase 1, sem HITL)."""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from lib.mobile.mobile_flow_discovery import APP_CONFIG, PARENT_NAV, _repo_root
from lib.mobile.mobile_user_flow_db import connect, db_path, stats
from lib.paths import MOBILE_GUIDES_DIR, REPORTS_DIR

GUIDE_PARENT = MOBILE_GUIDES_DIR / "mobile_evidence_guide_parent.json"
GUIDE_CHILD = MOBILE_GUIDES_DIR / "mobile_evidence_guide_child.json"
GUIDE_GATES = MOBILE_GUIDES_DIR / "mobile_evidence_guide_app_gates.json"
GUIDE_MERGED = MOBILE_GUIDES_DIR / "mobile_evidence_guide_merged.json"
REPORT_MD = MOBILE_GUIDES_DIR / "MOBILE_EVIDENCE_MAP_REPORT.md"

P0_SCREEN_NAMES = frozenset({
    "ParentSplashScreen",
    "AuthScreen",
    "PairingCodesScreen",
    "FamilyDetailPairingSheet",
    "FamilyPairingSelector",
    "PrePairingScreen",
    "SplashScreen",
    "ChildHome",
    "ChildHomeV2",
    "ChildDashboard",
})

P0_FLOW_KEYWORDS = (
    "splash",
    "login",
    "auth",
    "pair",
    "pareamento",
    "prepairing",
    "pairing",
    "tagline",
)


class ElementField(BaseModel):
    kind: str = ""
    label: str = ""
    test_id: str | None = None
    accessibility: str | None = None
    file: str = ""
    line_hint: int | None = None


class EvidencePlan(BaseModel):
    screenshot_at_step: int = 1
    video_full_flow: bool = False
    png_per_ac: bool = True
    assertions: list[str] = Field(default_factory=list)
    appium_selectors: list[dict[str, str]] = Field(default_factory=list)


class ScreenEvidenceGuide(BaseModel):
    screen_id: str
    app_id: str
    component_name: str
    priority: Literal["P0", "P1", "P2"] = "P2"
    functionality_summary: str = ""
    entry_conditions: list[str] = Field(default_factory=list)
    dependencies: dict[str, Any] = Field(default_factory=dict)
    fields_and_elements: list[ElementField] = Field(default_factory=list)
    user_flow_steps: list[dict[str, Any]] = Field(default_factory=list)
    evidence_plan: EvidencePlan = Field(default_factory=EvidencePlan)
    related_flows: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"] = "medium"
    gaps: list[str] = Field(default_factory=list)
    discovery_source: str = "llm_survey_phase1"


class ScreenGuideBatch(BaseModel):
    screens: list[ScreenEvidenceGuide]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _priority_for(component: str, app_id: str) -> str:
    name = component.replace(f"{app_id}:", "")
    if name in P0_SCREEN_NAMES or any(k in name.lower() for k in P0_FLOW_KEYWORDS):
        return "P0"
    if app_id == "parent" and name in PARENT_NAV:
        return "P1"
    return "P2"


def _video_full_flow(priority: str, component: str) -> bool:
    if priority != "P0":
        return False
    low = component.lower()
    return any(k in low for k in ("pair", "pareamento", "prepairing", "pairing"))


def list_screens_from_db(app_id: str = "") -> list[dict[str, Any]]:
    with connect() as conn:
        if app_id:
            rows = conn.execute(
                "SELECT * FROM mobile_screens WHERE app_id = ? ORDER BY component_name",
                (app_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM mobile_screens ORDER BY app_id, component_name").fetchall()
        return [dict(r) for r in rows]


def extract_app_tsx_gates(app_id: str) -> dict[str, Any]:
    cfg = APP_CONFIG[app_id]
    root = _repo_root(app_id)
    app_tsx = root / cfg["app_tsx"]
    text = app_tsx.read_text(encoding="utf-8", errors="replace")
    imports = re.findall(r"import (\w+) from '\./screens/(\w+)'", text)
    gates: list[dict[str, str]] = []
    patterns = [
        (r"if \(!startupSplashDone\)", "Cold start splash gate"),
        (r"if \(!.*session", "Auth/session gate"),
        (r"onboarding", "Onboarding gate"),
        (r"maintenance", "Maintenance remote gate"),
        (r"paywall", "Paywall/subscription gate"),
        (r"PairingCodes", "Pairing codes route"),
        (r"WelcomeOnboarding", "Welcome onboarding"),
        (r"FamilySetupWizard", "Family setup wizard"),
        (r"PrePairing", "Child pre-pairing gate"),
        (r"SplashScreen", "Child splash gate"),
    ]
    for pat, label in patterns:
        if re.search(pat, text, re.I):
            gates.append({"pattern": pat, "label": label})
    return {
        "screen_id": f"{app_id}:App.tsx:gates",
        "app_id": app_id,
        "component_name": "App.tsx",
        "file_path": cfg["app_tsx"],
        "route_condition": "; ".join(g["label"] for g in gates),
        "imported_screens": [f"{app_id}:{name}" for name, _ in imports],
        "gates": gates,
        "excerpt_lines": len(text.splitlines()),
    }


def _elements_for_screen(screen_id: str) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM mobile_elements WHERE screen_id = ? ORDER BY element_kind, label_text",
            (screen_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def _flows_for_screen(screen_id: str, limit: int = 5) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT flow_id, flow_name, target_element_id, entry_point
            FROM mobile_user_flows
            WHERE target_screen_id = ?
            ORDER BY flow_name LIMIT ?
            """,
            (screen_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def _flow_steps_sample(flow_id: str) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT step_order, screen_id, user_action, system_behavior, navigation_file, route_condition
            FROM mobile_flow_steps WHERE flow_id = ? ORDER BY step_order
            """,
            (flow_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def build_static_context(screen: dict[str, Any]) -> dict[str, Any]:
    sid = screen["screen_id"]
    app_id = screen["app_id"]
    cfg = APP_CONFIG.get(app_id, {})
    elements = _elements_for_screen(sid)
    flows = _flows_for_screen(sid)
    steps_sample: list[dict[str, Any]] = []
    if flows:
        steps_sample = _flow_steps_sample(flows[0]["flow_id"])

    tsx_excerpt = ""
    if screen.get("file_path") and ":App.tsx:" not in sid:
        try:
            root = _repo_root(app_id)
            fp = root / screen["file_path"]
            if fp.is_file():
                lines = fp.read_text(encoding="utf-8", errors="replace").splitlines()
                tsx_excerpt = "\n".join(lines[:120])
                if len(lines) > 120:
                    tsx_excerpt += f"\n... ({len(lines) - 120} linhas omitidas)"
        except FileNotFoundError:
            tsx_excerpt = ""

    if ":App.tsx:gates" in sid:
        gate_data = extract_app_tsx_gates(app_id)
        tsx_excerpt = ""
        try:
            root = _repo_root(app_id)
            text = (root / cfg["app_tsx"]).read_text(encoding="utf-8", errors="replace")
            tsx_excerpt = "\n".join(text.splitlines()[:150])
        except FileNotFoundError:
            pass
        screen = {**screen, **gate_data}

    return {
        "screen": screen,
        "elements": elements[:40],
        "flows": flows,
        "steps_sample": steps_sample,
        "tsx_excerpt": tsx_excerpt[:6000],
        "metro_port": cfg.get("metro_port"),
        "emulator": cfg.get("emulator"),
        "bundle_id": cfg.get("bundle_id"),
    }


def _static_guide_entry(ctx: dict[str, Any]) -> ScreenEvidenceGuide:
    screen = ctx["screen"]
    sid = screen["screen_id"]
    app_id = screen["app_id"]
    comp = screen.get("component_name") or sid.split(":")[-1]
    priority = _priority_for(comp, app_id)

    fields = []
    for el in ctx.get("elements") or []:
        fields.append(
            ElementField(
                kind=el.get("element_kind") or "",
                label=el.get("label_text") or el.get("accessibility_label") or el.get("test_id") or "",
                test_id=el.get("test_id"),
                accessibility=el.get("accessibility_label"),
                file=el.get("file_path") or screen.get("file_path") or "",
                line_hint=el.get("line_hint"),
            )
        )

    steps = []
    for s in ctx.get("steps_sample") or []:
        steps.append(
            {
                "order": s["step_order"],
                "screen": (s["screen_id"] or "").split(":")[-1],
                "user_action": s["user_action"],
                "expected": s["system_behavior"],
                "file": s.get("navigation_file") or "",
                "route_condition": s.get("route_condition") or "",
            }
        )

    pre = []
    if ctx.get("emulator"):
        pre.append(f"Emulador {ctx['emulator']} booted")
    if ctx.get("metro_port"):
        pre.append(f"Metro porta {ctx['metro_port']}")
    if priority == "P0" and "pair" in comp.lower():
        pre.append("API Docker :3000 + seed admin@guardiao.local")
    if priority == "P0" and comp == "AuthScreen":
        pre.append("Sessão não autenticada")

    assertions = []
    selectors = []
    for el in fields[:8]:
        if el.label:
            assertions.append(f"Texto/label '{el.label}' visível")
        if el.test_id:
            selectors.append({"strategy": "accessibility id", "value": el.test_id})
        elif el.accessibility:
            selectors.append({"strategy": "accessibility id", "value": el.accessibility})

    return ScreenEvidenceGuide(
        screen_id=sid,
        app_id=app_id,
        component_name=comp,
        priority=priority,  # type: ignore[arg-type]
        functionality_summary=f"Tela {comp} — {len(fields)} elementos mapeados (static)",
        entry_conditions=pre or [screen.get("route_condition") or "Ver App.tsx"],
        dependencies={
            "api": priority == "P0" and "pair" in comp.lower(),
            "auth_session": comp == "AuthScreen",
            "metro_port": ctx.get("metro_port"),
            "emulator": ctx.get("emulator"),
            "bundle_id": ctx.get("bundle_id"),
        },
        fields_and_elements=fields,
        user_flow_steps=steps,
        evidence_plan=EvidencePlan(
            screenshot_at_step=max(1, len(steps)),
            video_full_flow=_video_full_flow(priority, comp),
            png_per_ac=True,
            assertions=assertions[:6],
            appium_selectors=selectors[:6],
        ),
        related_flows=[f["flow_id"] for f in ctx.get("flows") or []],
        confidence="high" if fields else "medium",
        gaps=[] if fields else ["Nenhum elemento estático — validar Appium Fase 2"],
        discovery_source="static_fallback",
    )


def _prompt_batch(contexts: list[dict[str, Any]]) -> str:
    blocks = []
    for ctx in contexts:
        sc = ctx["screen"]
        blocks.append(
            json.dumps(
                {
                    "screen_id": sc["screen_id"],
                    "component": sc.get("component_name"),
                    "file": sc.get("file_path"),
                    "route": sc.get("route_condition"),
                    "elements_count": len(ctx.get("elements") or []),
                    "elements_sample": (ctx.get("elements") or [])[:12],
                    "flows": ctx.get("flows"),
                    "steps_sample": ctx.get("steps_sample"),
                    "tsx_excerpt": (ctx.get("tsx_excerpt") or "")[:3500],
                },
                ensure_ascii=False,
            )
        )
    rules = """
Regras Fase 1 (sem HITL):
- priority P0 apenas: splash, login/auth, pareamento (parent+child)
- evidence_plan.png_per_ac = true sempre
- evidence_plan.video_full_flow = true SOMENTE fluxos P0 de pareamento
- Liste fields_and_elements a partir dos dados fornecidos
- user_flow_steps: passos 0→N reproduzíveis
- gaps: incertezas honestas (ex. gate dinâmico App.tsx)
- confidence: high se elementos+passos claros
"""
    return (
        "Gere guias de evidência E2E mobile para cada tela abaixo.\n"
        f"{rules}\n"
        "Telas JSON (uma por linha):\n" + "\n".join(blocks)
    )


def survey_batch_llm(contexts: list[dict[str, Any]], *, use_llm: bool = True) -> list[ScreenEvidenceGuide]:
    if not use_llm:
        return [_static_guide_entry(c) for c in contexts]

    try:
        from langgraph_app.llm import invoke_text

        prompt = (
            _prompt_batch(contexts)
            + "\n\nResponda APENAS JSON válido: {\"screens\": [ ... ]} "
            "seguindo os campos: screen_id, app_id, component_name, priority (P0|P1|P2), "
            "functionality_summary, entry_conditions[], dependencies{}, fields_and_elements[], "
            "user_flow_steps[], evidence_plan{screenshot_at_step, video_full_flow, png_per_ac, assertions[], appium_selectors[]}, "
            "related_flows[], confidence (high|medium|low), gaps[]."
        )
        text, _, _ = invoke_text(
            {"title": "mobile evidence survey", "agent_role": "qa"},
            prompt,
            purpose="implement_low",
        )
        start = text.find("{")
        end = text.rfind("}") + 1
        if start < 0 or end <= start:
            raise ValueError("JSON não encontrado na resposta LLM")
        payload = json.loads(text[start:end])
        parsed = ScreenGuideBatch.model_validate(payload)
        by_id = {g.screen_id: g for g in parsed.screens}
        out: list[ScreenEvidenceGuide] = []
        for ctx in contexts:
            sid = ctx["screen"]["screen_id"]
            if sid in by_id:
                g = by_id[sid]
                comp = ctx["screen"].get("component_name") or sid.split(":")[-1]
                if g.priority == "P2":
                    g.priority = _priority_for(comp, ctx["screen"]["app_id"])  # type: ignore[assignment]
                g.evidence_plan.png_per_ac = True
                if not _video_full_flow(g.priority, comp):
                    g.evidence_plan.video_full_flow = False
                g.discovery_source = "llm_survey_phase1"
                out.append(g)
            else:
                out.append(_static_guide_entry(ctx))
        return out
    except Exception:
        return [_static_guide_entry(c) for c in contexts]


def list_survey_targets(app_filter: str = "") -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    apps = ["parent", "child"] if app_filter in ("", "both") else [app_filter]
    for app_id in apps:
        targets.extend(list_screens_from_db(app_id))
        targets.append(
            {
                "screen_id": f"{app_id}:App.tsx:gates",
                "app_id": app_id,
                "component_name": "App.tsx",
                "file_path": APP_CONFIG[app_id]["app_tsx"],
                "route_condition": "Navigation gates (App.tsx)",
            }
        )
    return targets


def run_survey(
    *,
    app: str = "both",
    batch_size: int = 6,
    use_llm: bool = True,
) -> dict[str, Any]:
    MOBILE_GUIDES_DIR.mkdir(parents=True, exist_ok=True)
    targets = list_survey_targets(app)
    contexts = [build_static_context(t) for t in targets]
    guides: list[ScreenEvidenceGuide] = []

    for i in range(0, len(contexts), batch_size):
        batch = contexts[i : i + batch_size]
        guides.extend(survey_batch_llm(batch, use_llm=use_llm))

    by_app: dict[str, list[dict[str, Any]]] = {"parent": [], "child": []}
    for g in guides:
        by_app.setdefault(g.app_id, []).append(g.model_dump())

    merged = {
        "generated_at": _now(),
        "phase": "1",
        "hitl": False,
        "stats": {
            "total_screens": len(guides),
            "parent": len(by_app.get("parent", [])),
            "child": len(by_app.get("child", [])),
            "p0": sum(1 for g in guides if g.priority == "P0"),
            "p1": sum(1 for g in guides if g.priority == "P1"),
            "p2": sum(1 for g in guides if g.priority == "P2"),
            "video_flows": sum(1 for g in guides if g.evidence_plan.video_full_flow),
            "sqlite": stats(),
        },
        "screens": [g.model_dump() for g in guides],
    }

    GUIDE_MERGED.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    GUIDE_PARENT.write_text(
        json.dumps({"generated_at": merged["generated_at"], "screens": by_app.get("parent", [])}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    GUIDE_CHILD.write_text(
        json.dumps({"generated_at": merged["generated_at"], "screens": by_app.get("child", [])}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    gate_screens = [g.model_dump() for g in guides if ":App.tsx:gates" in g.screen_id]
    GUIDE_GATES.write_text(
        json.dumps({"generated_at": merged["generated_at"], "gates": gate_screens}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    REPORT_MD.write_text(build_report_markdown(merged), encoding="utf-8")

    return {
        "ok": True,
        "guides": len(guides),
        "paths": {
            "merged": str(GUIDE_MERGED),
            "report": str(REPORT_MD),
        },
        "stats": merged["stats"],
    }


def guide_entry_to_chunk(entry: dict[str, Any]) -> dict[str, Any]:
    ep = entry.get("evidence_plan") or {}
    lines = [
        f"Tipo: evidence_guide Fase 1",
        f"App: {entry.get('app_id')}",
        f"Tela: {entry.get('screen_id')}",
        f"Componente: {entry.get('component_name')}",
        f"Prioridade: {entry.get('priority')}",
        f"Funcionalidade: {entry.get('functionality_summary')}",
        f"Confiança: {entry.get('confidence')}",
        "Entry conditions: " + "; ".join(entry.get("entry_conditions") or []),
        f"Dependencies: {json.dumps(entry.get('dependencies') or {}, ensure_ascii=False)}",
        "Campos e elementos:",
    ]
    for f in entry.get("fields_and_elements") or []:
        lines.append(
            f"  - [{f.get('kind')}] {f.get('label')} testID={f.get('test_id')} a11y={f.get('accessibility')}"
        )
    lines.append("Passos usuário 0→N:")
    for s in entry.get("user_flow_steps") or []:
        lines.append(
            f"  {s.get('order')}. {s.get('screen')} — {s.get('user_action')} → {s.get('expected')}"
        )
    lines.append("Plano evidências:")
    lines.append(f"  PNG por AC: {ep.get('png_per_ac', True)}")
    lines.append(f"  Screenshot passo: {ep.get('screenshot_at_step', 1)}")
    lines.append(f"  Vídeo fluxo completo: {ep.get('video_full_flow', False)}")
    for a in ep.get("assertions") or []:
        lines.append(f"  Assert: {a}")
    for g in entry.get("gaps") or []:
        lines.append(f"Gap: {g}")
    if entry.get("related_flows"):
        lines.append("Flows relacionados: " + ", ".join(entry["related_flows"][:8]))

    content = "\n".join(lines)
    return {
        "chunk_id": f"evidence_guide:{entry['screen_id']}",
        "flow_id": (entry.get("related_flows") or [None])[0],
        "app_id": entry["app_id"],
        "chunk_type": "evidence_guide",
        "title": f"{entry.get('component_name')} [{entry.get('priority')}]",
        "content": content,
        "metadata": {
            "screen_id": entry["screen_id"],
            "priority": entry.get("priority"),
            "confidence": entry.get("confidence"),
            "video_full_flow": ep.get("video_full_flow", False),
            "png_per_ac": ep.get("png_per_ac", True),
            "element_count": len(entry.get("fields_and_elements") or []),
            "step_count": len(entry.get("user_flow_steps") or []),
            "phase": 1,
        },
    }


def iter_evidence_guide_chunks(guide_path: str | Path | None = None) -> list[dict[str, Any]]:
    path = Path(guide_path) if guide_path else GUIDE_MERGED
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [guide_entry_to_chunk(s) for s in data.get("screens") or []]


def ingest_guides_to_pgvector(*, guide_path: str = "", use_fake_embed: bool = False) -> dict[str, Any]:
    from lib.mobile.mobile_flow_rag import ensure_schema, stats_pg, upsert_chunks

    chunks = iter_evidence_guide_chunks(guide_path or GUIDE_MERGED)
    ensure_schema()
    result = upsert_chunks(chunks, use_fake_embed=use_fake_embed)
    result["pgvector"] = stats_pg()
    result["chunk_type"] = "evidence_guide"
    return result


def build_report_markdown(merged: dict[str, Any]) -> str:
    st = merged.get("stats") or {}
    lines = [
        "# Mapa de funcionalidades mobile — Fase 1 (seed RAG)",
        "",
        f"**Gerado:** {merged.get('generated_at', '')} · **HITL:** não (Fase 2 melhorias)",
        "",
        "## Resumo",
        "",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Telas + gates App.tsx | **{st.get('total_screens', 0)}** |",
        f"| Parent | {st.get('parent', 0)} |",
        f"| Child | {st.get('child', 0)} |",
        f"| Prioridade P0 | {st.get('p0', 0)} |",
        f"| Prioridade P1 | {st.get('p1', 0)} |",
        f"| Prioridade P2 | {st.get('p2', 0)} |",
        f"| Fluxos com vídeo (MP4) | {st.get('video_flows', 0)} |",
        "",
        "## Regras de evidência",
        "",
        "- **PNG:** todo AC (`png_per_ac: true`)",
        "- **MP4:** somente quando `video_full_flow: true` (P0 pareamento)",
        "- **SDK/Appium:** Fase 2 (runtime reconcile)",
        "",
        "## P0 — splash, login, pareamento",
        "",
        "| screen_id | funcionalidade | PNG passo | MP4 | confiança |",
        "|-----------|----------------|-----------|-----|-----------|",
    ]
    for s in merged.get("screens") or []:
        if s.get("priority") != "P0":
            continue
        ep = s.get("evidence_plan") or {}
        lines.append(
            f"| `{s.get('screen_id')}` | {(s.get('functionality_summary') or '')[:60]} | "
            f"{ep.get('screenshot_at_step', '-')} | {'sim' if ep.get('video_full_flow') else 'não'} | {s.get('confidence')} |"
        )

    lines.extend(["", "## Catálogo completo", "", "| Prioridade | Tela | Elementos | Passos | Gaps |", "|------------|------|-------------|--------|------|"])
    for s in sorted(merged.get("screens") or [], key=lambda x: (x.get("priority", "Z"), x.get("screen_id", ""))):
        gaps = len(s.get("gaps") or [])
        lines.append(
            f"| {s.get('priority')} | `{s.get('screen_id')}` | "
            f"{len(s.get('fields_and_elements') or [])} | {len(s.get('user_flow_steps') or [])} | {gaps} |"
        )

    lines.extend(
        [
            "",
            "## Artefatos",
            "",
            f"- `{GUIDE_MERGED.name}` — JSON completo",
            f"- pgvector chunk_type `evidence_guide`",
            f"- SQLite fluxos: `{db_path()}`",
            "",
            "## Fase 2 (melhorias)",
            "",
            "1. HITL opcional por task",
            "2. Appium reconcile (labels runtime)",
            "3. Instalação Android SDK + evidências PNG/MP4",
        ]
    )
    return "\n".join(lines)
