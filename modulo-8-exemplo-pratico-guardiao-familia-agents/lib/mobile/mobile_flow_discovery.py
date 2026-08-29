"""Scan estático TSX + discovery Appium (opcional) → mobile_user_flows.db."""

from __future__ import annotations

import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from lib.mobile.local_e2e import resolve_android_home
from lib.mobile.mobile_runtime_config import app_config_compat
from lib.mobile.mobile_user_flow_db import (
    finish_discovery_run,
    flow_to_refinement_user_flow,
    find_flows_for_task,
    get_flow,
    start_discovery_run,
    stats,
    upsert_app,
    upsert_element,
    upsert_flow,
    upsert_screen,
)
from lib.core.repo_paths import resolve_repo_path

APP_CONFIG = app_config_compat()

# Grafo conhecido cold-start → telas (expandível pelo QA agent)
PARENT_NAV = {
    "ParentSplashScreen": {
        "route_condition": "App.tsx ~791: if (!startupSplashDone)",
        "file": "App.tsx",
        "after": ["WelcomeOnboardingScreen", "AuthScreen"],
    },
    "WelcomeOnboardingScreen": {
        "route_condition": "App.tsx: welcomeOnboarding ativo pós-splash",
        "file": "App.tsx",
        "after": ["AuthScreen", "RegisterOnboardingScreen"],
    },
    "AuthScreen": {
        "route_condition": "App.tsx: !session autenticada",
        "file": "App.tsx",
        "after": ["ParentHome", "FamilySetupWizardScreen"],
    },
    "PairingCodesScreen": {
        "route_condition": "App.tsx: fluxo pareamento pós-login/onboarding",
        "file": "App.tsx",
        "after": [],
    },
}

TEXT_RE = re.compile(
    r"<Text[^>]*>([^<{]+)</Text>|"
    r"<Text[^>]*>\{['\"]([^'\"]+)['\"]\}</Text>|"
    r"styles\.(\w+)[^>]*>\s*\{?['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)
TESTID_RE = re.compile(r"testID=[\"']([^\"']+)[\"']")
A11Y_RE = re.compile(r"accessibilityLabel=[\"']([^\"']+)[\"']")
SCREEN_EXPORT_RE = re.compile(r"export default function (\w+)")


def _repo_root(app_id: str) -> Path:
    cfg = APP_CONFIG[app_id]
    root = resolve_repo_path(cfg["repo"])
    if not root:
        raise FileNotFoundError(f"Repo não encontrado: {cfg['repo']}")
    return Path(root)


def scan_screen_file(app_id: str, screen_path: Path) -> dict[str, Any]:
    text = screen_path.read_text(encoding="utf-8", errors="replace")
    component = SCREEN_EXPORT_RE.search(text)
    name = component.group(1) if component else screen_path.stem
    screen_id = f"{app_id}:{name}"
    rel = str(screen_path.as_posix()).split("/")[-2:] if "/" in str(screen_path) else screen_path.name
    rel_path = "/".join(rel) if isinstance(rel, list) else f"screens/{screen_path.name}"

    nav = PARENT_NAV.get(name, {}) if app_id == "parent" else {}
    upsert_screen(
        screen_id,
        app_id=app_id,
        component_name=name,
        file_path=f"screens/{screen_path.name}",
        route_condition=nav.get("route_condition", ""),
    )

    elements: list[dict[str, Any]] = []
    seen: set[str] = set()

    for m in TESTID_RE.finditer(text):
        tid = m.group(1)
        eid = f"{screen_id}:testid:{tid}"
        if eid in seen:
            continue
        seen.add(eid)
        upsert_element(
            eid,
            screen_id=screen_id,
            element_kind="testID",
            test_id=tid,
            file_path=f"screens/{screen_path.name}",
            line_hint=text[: m.start()].count("\n") + 1,
        )
        elements.append({"element_id": eid, "kind": "testID", "text": tid})

    for m in A11Y_RE.finditer(text):
        label = m.group(1)
        eid = f"{screen_id}:a11y:{label[:40].replace(' ', '_')}"
        if eid in seen:
            continue
        seen.add(eid)
        upsert_element(
            eid,
            screen_id=screen_id,
            element_kind="accessibilityLabel",
            accessibility_label=label,
            file_path=f"screens/{screen_path.name}",
            line_hint=text[: m.start()].count("\n") + 1,
        )
        elements.append({"element_id": eid, "kind": "a11y", "text": label})

    # Text literals in JSX
    for i, line in enumerate(text.splitlines(), 1):
        for pat in (
            re.compile(r"<Text[^>]*style=\{styles\.(\w+)\}[^>]*>([^<{]+)</Text>"),
            re.compile(r"<Text[^>]*style=\{styles\.(\w+)\}[^>]*>\{['\"]([^'\"]+)['\"]\}</Text>"),
            re.compile(r"<Text[^>]*>([A-Za-zÀ-ú0-9][^<{]{2,80})</Text>"),
        ):
            for m in pat.finditer(line):
                groups = m.groups()
                style_key = groups[0] if len(groups) > 1 and groups[0] and groups[0][0].isalpha() and groups[0] in line else ""
                label = (groups[-1] or "").strip()
                if not label or label.startswith("{") or len(label) < 2:
                    continue
                slug = re.sub(r"[^a-zA-Z0-9]+", "_", label[:30]).strip("_").lower()
                eid = f"{screen_id}:text:{style_key or slug}"
                if eid in seen:
                    continue
                seen.add(eid)
                upsert_element(
                    eid,
                    screen_id=screen_id,
                    element_kind="Text",
                    label_text=label,
                    style_key=style_key,
                    file_path=f"screens/{screen_path.name}",
                    line_hint=i,
                )
                elements.append({"element_id": eid, "kind": "Text", "text": label, "style_key": style_key})

    return {"screen_id": screen_id, "component": name, "elements": elements}


def _cold_start_steps(app_id: str, screen_id: str, screen_name: str, element: dict[str, Any]) -> list[dict[str, Any]]:
    cfg = APP_CONFIG[app_id]
    nav = PARENT_NAV.get(screen_name, {}) if app_id == "parent" else {}
    steps: list[dict[str, Any]] = [
        {
            "order": 1,
            "screen_id": f"{app_id}:launcher",
            "screen": "(launcher)",
            "user_action": "Tocar ícone do app",
            "system_behavior": "Processo inicia",
            "file": "android/",
            "route_condition": f"LAUNCHER · {cfg['bundle_id']}",
        },
        {
            "order": 2,
            "screen_id": f"{app_id}:bootstrap",
            "screen": cfg["app_tsx"],
            "user_action": "(automático)",
            "system_behavior": "Bootstrap fonts, remote config, gates",
            "file": cfg["app_tsx"],
            "route_condition": "App.tsx mount",
        },
    ]
    if screen_name == "ParentSplashScreen":
        steps.append(
            {
                "order": 3,
                "screen_id": screen_id,
                "screen": screen_name,
                "user_action": "Aguardar splash (~2s)",
                "system_behavior": "Splash animado visível",
                "file": f"screens/{screen_name}.tsx",
                "route_condition": nav.get("route_condition", "App.tsx splash gate"),
            }
        )
        order = 4
    else:
        steps.append(
            {
                "order": 3,
                "screen_id": f"{app_id}:ParentSplashScreen",
                "screen": "ParentSplashScreen",
                "user_action": "(automático) splash",
                "system_behavior": "Transição pós-splash",
                "file": "App.tsx",
                "route_condition": "startupSplashDone=true",
            }
        )
        order = 4

    steps.append(
        {
            "order": order,
            "screen_id": screen_id,
            "screen": screen_name,
            "user_action": f"Localizar: {element.get('text', element.get('element_id', ''))}",
            "system_behavior": "Elemento/label visível (alvo da task)",
            "file": element.get("file_path", f"screens/{screen_name}.tsx"),
            "route_condition": nav.get("route_condition", ""),
        }
    )
    return steps


def seed_flows_for_screen(app_id: str, scan: dict[str, Any]) -> int:
    cfg = APP_CONFIG[app_id]
    screen_id = scan["screen_id"]
    screen_name = scan["component"]
    count = 0
    for el in scan["elements"]:
        eid = el["element_id"]
        slug = eid.split(":")[-1]
        flow_id = f"{app_id}:{screen_name}:{slug}"
        label = el.get("text") or slug
        steps = _cold_start_steps(app_id, screen_id, screen_name, {**el, "file_path": f"screens/{screen_name}.tsx"})
        pre = [
            f"Emulador {cfg['emulator']} booted",
            f"Metro port {cfg['metro_port']}",
            f"Dev client {cfg['bundle_id']} instalado",
        ]
        qa = [
            f"adb -s {cfg['emulator']} shell am force-stop {cfg['bundle_id']}",
            f"adb -s {cfg['emulator']} shell am start -n {cfg['activity']}",
            f"Seguir passos 1–{len(steps)} até visualizar: {label}",
        ]
        nodes = " → ".join([s["screen"] for s in steps[:4]])
        mermaid = f"flowchart LR\n  launch[Abrir app] --> boot[Bootstrap]\n  boot --> target[{screen_name}]\n  target --> el[{label[:24]}]"
        upsert_flow(
            flow_id,
            app_id=app_id,
            entry_point="Cold start — app fechado",
            target_screen_id=screen_id,
            target_element_id=eid,
            flow_name=f"{screen_name}: {label}",
            preconditions=pre,
            qa_repro_steps=qa,
            mermaid=mermaid,
            discovery_source="static",
            steps=steps,
        )
        count += 1
    return count


def scan_app_static(app_id: str) -> dict[str, Any]:
    cfg = APP_CONFIG[app_id]
    root = _repo_root(app_id)
    upsert_app(
        app_id,
        repo=cfg["repo"],
        bundle_id=cfg["bundle_id"],
        metro_port=cfg["metro_port"],
        emulator=cfg["emulator"],
    )
    screens_dir = root / cfg["screens_dir"]
    if not screens_dir.is_dir():
        return {"app_id": app_id, "screens": 0, "elements": 0, "flows": 0}

    total_el = 0
    total_flows = 0
    screen_count = 0
    for path in sorted(screens_dir.glob("*.tsx")):
        if path.name.endswith(".test.tsx"):
            continue
        scan = scan_screen_file(app_id, path)
        screen_count += 1
        total_el += len(scan["elements"])
        total_flows += seed_flows_for_screen(app_id, scan)
    return {"app_id": app_id, "screens": screen_count, "elements": total_el, "flows": total_flows}


def discover_appium_snapshot(app_id: str, *, emulator: str | None = None) -> dict[str, Any]:
    """Dump UIAutomator no emulador — enriquece elements com source=appium."""
    cfg = APP_CONFIG[app_id]
    emu = emulator or cfg["emulator"]
    sdk = resolve_android_home()
    if not sdk:
        return {"ok": False, "error": "ANDROID_HOME não configurado", "elements": 0}

    adb = sdk / "platform-tools" / "adb.exe"
    if not adb.is_file():
        return {"ok": False, "error": "adb não encontrado", "elements": 0}

    remote = "/sdcard/qa_ui_dump.xml"
    from lib.paths import MOBILE_DUMPS_DIR

    local = MOBILE_DUMPS_DIR / f"ui_dump_{app_id}.xml"
    local.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run([str(adb), "-s", emu, "shell", "uiautomator", "dump", remote], capture_output=True, timeout=30)
    pull = subprocess.run([str(adb), "-s", emu, "pull", remote, str(local)], capture_output=True, timeout=30)
    if pull.returncode != 0 or not local.is_file():
        return {"ok": False, "error": (pull.stderr or b"").decode()[:200], "elements": 0}

    try:
        tree = ET.parse(local)
    except ET.ParseError as e:
        return {"ok": False, "error": str(e), "elements": 0}

    count = 0
    screen_id = f"{app_id}:appium_snapshot"
    upsert_screen(screen_id, app_id=app_id, component_name="AppiumSnapshot", file_path="(runtime)", route_condition=f"emulator {emu}")

    for node in tree.iter("node"):
        text = (node.attrib.get("text") or "").strip()
        desc = (node.attrib.get("content-desc") or "").strip()
        rid = (node.attrib.get("resource-id") or "").strip()
        if not text and not desc:
            continue
        label = text or desc
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", label[:40]).strip("_").lower() or "node"
        eid = f"{screen_id}:appium:{slug}"
        upsert_element(
            eid,
            screen_id=screen_id,
            element_kind="appium_visible",
            label_text=text,
            accessibility_label=desc,
            test_id=rid,
            discovery_source="appium",
        )
        count += 1
    return {"ok": True, "elements": count, "dump_path": str(local)}


def run_discovery(
    apps: list[str] | None = None,
    *,
    appium: bool = False,
    appium_p0: bool = False,
) -> dict[str, Any]:
    apps = apps or ["parent", "child"]
    summary: dict[str, Any] = {"apps": {}, "stats": {}}
    p0_runtime: dict[str, Any] = {}
    if appium_p0:
        from lib.mobile.mobile_setup_client import run_phase2

        p0_runtime = run_phase2(start_emu=True, single_emulator=False)
        summary["phase2_p0"] = p0_runtime

    for app_id in apps:
        run_id = start_discovery_run(app_id, notes="qa_discover_mobile_flows")
        try:
            static = scan_app_static(app_id)
            if appium_p0:
                appium_result = {"ok": True, "skipped": False, "note": "see phase2_p0"}
            elif appium:
                appium_result = discover_appium_snapshot(app_id)
            else:
                appium_result = {"ok": False, "skipped": True}
            finish_discovery_run(
                run_id,
                status="ok",
                elements_found=static["elements"] + int(appium_result.get("elements") or 0),
                flows_seeded=static["flows"],
                notes=str(appium_result),
            )
            summary["apps"][app_id] = {**static, "appium": appium_result}
        except Exception as e:  # noqa: BLE001
            finish_discovery_run(run_id, status="error", elements_found=0, flows_seeded=0, notes=str(e))
            summary["apps"][app_id] = {"error": str(e)}
    summary["stats"] = stats()
    return summary


def resolve_user_flow_for_task(task: dict[str, Any]) -> dict[str, Any] | None:
    """Lookup DB para preencher ticket frontend-mobile."""
    if task.get("agent_role") != "frontend-mobile":
        return None

    ref = task.get("refinement") or {}
    if ref.get("user_flow") and ref["user_flow"].get("steps"):
        return ref["user_flow"]

    repo = (task.get("repo") or "").lower()
    app_id = "parent" if "parent" in repo else "child" if "child" in repo else ""

    flow_id = ref.get("user_flow_id") or task.get("user_flow_id")
    if flow_id:
        flow = get_flow(str(flow_id))
        if flow:
            return flow_to_refinement_user_flow(flow)

    files = ref.get("suggested_files") or []
    file_hint = files[0] if files else ""
    screen_hint = ""
    if file_hint:
        stem = Path(file_hint).stem
        screen_hint = stem

    title = task.get("title") or ""
    label_hint = ""
    for token in ("tagline", "label", "splash", "pareamento", "pairing", "login", "botão", "botao"):
        if token in title.lower():
            label_hint = token
            break

    flows = find_flows_for_task(
        app_id=app_id,
        screen_hint=screen_hint,
        file_hint=file_hint,
        label_hint=label_hint or title,
    )
    if not flows and screen_hint:
        flows = find_flows_for_task(app_id=app_id, screen_hint=screen_hint)
    if flows:
        return flow_to_refinement_user_flow(flows[0])

    # Fallback: RAG pgvector (Postgres)
    try:
        from lib.mobile.mobile_flow_rag import search, search_to_user_flow

        q = " ".join(
            x
            for x in (
                title,
                screen_hint,
                file_hint,
                label_hint,
                " ".join(ref.get("acceptance_hints") or [])[:200],
            )
            if x
        )
        hits = search(q, app_id=app_id, top_k=3)
        uf = search_to_user_flow(hits)
        if uf:
            return uf
    except Exception:  # noqa: BLE001
        pass
    return None
