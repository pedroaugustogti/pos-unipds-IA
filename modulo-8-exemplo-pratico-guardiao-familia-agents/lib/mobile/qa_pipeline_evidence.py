"""qa_pipeline_evidence — monta scenario_pipeline (meta + steps) para evidência.

Camada entre `qa_init_suite_mobile` e `qa_generate_evidence`.
Só gera pipeline quando `apps_ready_ok=true`.

Action é amarrada a test_id / feature step tipado — sem heurística de prosa.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from lib.mobile.mobile_runtime_config import (
    METRO_EMULATOR_HOST,
    stack,
)
from lib.mobile.mobile_task import resolve_appium_feature_from_ticket, resolve_suites_mobile
from lib.orchestrator.phase_context import load_actuation, task_from_ctx

_DEFAULT_FIELD_DELAY_MS = 300
_DEFAULT_STEP_DELAY_MS = 1000

_GREETING_RE = re.compile(r"^greeting-(morning|afternoon|evening)-(\d{1,2})h$", re.IGNORECASE)
_GREETING_LABEL = {
    "morning": "Bom dia",
    "afternoon": "Boa tarde",
    "evening": "Boa noite",
}

_ALLOWED_ACTIONS = frozenset(
    {
        "launch",
        "fill",
        "tap",
        "wait",
        "set_clock",
        "capture",
        "record_start",
        "record_stop",
    }
)

# test_id → action canônica (única fonte além de action explícita tipada)
_STEP_CATALOG: dict[str, dict[str, Any]] = {
    "pairing-code-input": {"action": "fill"},
    "pairing-submit": {"action": "tap"},
    "pairing-help": {"action": "tap"},
    "pairing-help-dismiss": {"action": "tap"},
    "permissions-continue": {"action": "tap"},
    "permissions-continue-limited": {"action": "tap"},
    "permissions-header": {"action": "wait"},
    "pre-pairing-screen": {"action": "wait"},
    "permissions-onboarding-screen": {"action": "wait"},
    "child-home-v2": {"action": "wait"},
    "greeting-title": {"action": "capture"},
    "sos-button": {"action": "tap"},
    "login-email": {"action": "fill"},
    "login-password": {"action": "fill"},
    "auth-submit": {"action": "tap"},
    "auth-screen": {"action": "wait"},
    "parent-home": {"action": "wait"},
}

# view = nome do componente/screen no repo (nunca label do ticket)
_REPO_VIEW_FILES: dict[str, str] = {
    "PrePairingScreen": "screens/PrePairingScreen.tsx",
    "PermissionsOnboardingScreen": "screens/PermissionsOnboardingScreen.tsx",
    "ChildHomeV2": "screens/ChildHomeV2.tsx",
    "ChildHome": "screens/ChildHome.tsx",
    "SplashScreen": "screens/SplashScreen.tsx",
    "AuthScreen": "screens/AuthScreen.tsx",
    "ParentHome": "screens/ParentHome.tsx",
    "PairingCodeInput": "components/pairing/PairingCodeInput.tsx",
}

_VIEW_FROM_TESTID: dict[str, str] = {
    "pre-pairing-screen": "PrePairingScreen",
    "pairing-code-input": "PrePairingScreen",
    "pairing-submit": "PrePairingScreen",
    "pairing-help": "PrePairingScreen",
    "pairing-help-dismiss": "PrePairingScreen",
    "permissions-onboarding-screen": "PermissionsOnboardingScreen",
    "permissions-header": "PermissionsOnboardingScreen",
    "permissions-continue": "PermissionsOnboardingScreen",
    "permissions-continue-limited": "PermissionsOnboardingScreen",
    "child-home-v2": "ChildHomeV2",
    "greeting-title": "ChildHomeV2",
    "sos-button": "ChildHomeV2",
    "screen-time-entry": "ChildHomeV2",
    "safe-areas-entry": "ChildHomeV2",
    "request-more-time": "ChildHomeV2",
    "auth-screen": "AuthScreen",
    "login-email": "AuthScreen",
    "login-password": "AuthScreen",
    "auth-submit": "AuthScreen",
    "parent-home": "ParentHome",
}

_KNOWN_REPO_VIEWS = frozenset(_REPO_VIEW_FILES.keys())


def _tid(test_id: str) -> str:
    tid = str(test_id or "").strip()
    if tid.lower().startswith("testid:"):
        return f"testID:{tid.split(':', 1)[1].strip()}"
    return f"testID:{tid}"


def _field(
    name: str,
    test_id: str,
    *,
    value_from: str = "",
    value: str = "",
    delay_ms: int = _DEFAULT_FIELD_DELAY_MS,
    input_mode: str = "",
    input_target: str = "",
    focus_test_id: str = "",
    expected_length: int | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": name,
        "test_id": test_id,
        "locator": _tid(test_id),
        "value_from": value_from,
        "value": value,
        "delay_ms": delay_ms,
    }
    if input_mode:
        out["input_mode"] = input_mode
    if input_target:
        out["input_target"] = input_target
    if focus_test_id:
        out["focus_test_id"] = focus_test_id
    if expected_length is not None:
        out["expected_length"] = int(expected_length)
    return out


# Pipelines canônicos — action + testID explícitos (feature step id).
_FEATURE_PIPELINES: dict[str, list[dict[str, Any]]] = {
    "pairing": [
        {
            "feature_step_id": "pairing.launch",
            "view": "",
            "view_testid": "",
            "action": "launch",
            "fields": [],
            "delay_ms_after": 2000,
            "exit_condition": {
                "type": "visible_any",
                "test_ids": [
                    "pre-pairing-screen",
                    "permissions-onboarding-screen",
                    "child-home-v2",
                ],
            },
            "hooks": ["dismiss_expo", "grant_os_perms"],
            "note": "Abrir app child no emulador",
            "file": "appium/pairing/paste_code_parent/child-launch.mjs",
        },
        {
            "feature_step_id": "pairing.fill_code",
            "view": "PrePairingScreen",
            "view_testid": "pre-pairing-screen",
            "action": "fill",
            # required: pm_clear + seed exigem digitar; skip só se view PrePairing ausente (optionalShouldSkip)
            "optional": False,
            "fields": [
                _field(
                    "pairing_code",
                    "pairing-code-input",
                    value_from="seed.pairing_code",
                    value="{{seed.pairing_code}}",
                    delay_ms=60,
                    input_mode="addValue_per_char",
                    # Pressable tem o testID; TextInput real é android.widget.EditText oculto
                    input_target="android_edit_text",
                    focus_test_id="pairing-code-input",
                    expected_length=6,
                ),
            ],
            "delay_ms_after": 1200,
            # onComplete auto-submete → permissões/home (pairing-submit pode sumir)
            "exit_condition": {
                "type": "visible_any",
                "test_ids": [
                    "permissions-onboarding-screen",
                    "child-home-v2",
                ],
            },
            "note": "Digitar 6 dígitos do seed no EditText (não no Pressable) — auto-submit ao completar",
            "file": "components/pairing/PairingCodeInput.tsx",
        },
        {
            "feature_step_id": "pairing.submit",
            "view": "PrePairingScreen",
            "view_testid": "pre-pairing-screen",
            "action": "tap",
            "optional": True,
            "fields": [_field("submit_pairing", "pairing-submit", delay_ms=200)],
            "delay_ms_after": 1500,
            "exit_condition": {
                "type": "visible_any",
                "test_ids": ["permissions-onboarding-screen", "child-home-v2"],
            },
            "note": "Confirmar pareamento se botão ainda visível (skip se auto-submit já avançou)",
            "file": "screens/PrePairingScreen.tsx",
        },
        {
            "feature_step_id": "pairing.permissions",
            "view": "PermissionsOnboardingScreen",
            "view_testid": "permissions-onboarding-screen",
            "action": "tap",
            "optional": True,
            "fields": [_field("allow_permissions", "permissions-continue", delay_ms=400)],
            "delay_ms_after": 1200,
            "exit_condition": {"type": "visible", "test_id": "child-home-v2"},
            "note": "Continuar permissões (skip se já na home)",
            "file": "screens/PermissionsOnboardingScreen.tsx",
        },
        {
            "feature_step_id": "pairing.wait_home",
            "view": "ChildHomeV2",
            "view_testid": "child-home-v2",
            "action": "wait",
            "fields": [_field("home_anchor", "child-home-v2")],
            "delay_ms_after": 1500,
            "exit_condition": {"type": "visible", "test_id": "greeting-title"},
            "note": "Aguardar home do filho",
            "file": "screens/ChildHomeV2.tsx",
        },
    ],
    "login": [
        {
            "feature_step_id": "login.launch",
            "view": "",
            "view_testid": "",
            "action": "launch",
            "fields": [],
            "delay_ms_after": 2000,
            "exit_condition": {"type": "visible", "test_id": "auth-screen"},
            "hooks": ["dismiss_expo", "grant_os_perms"],
            "note": "Abrir app parent no emulador",
            "file": "",
        },
        {
            "feature_step_id": "login.fill",
            "view": "AuthScreen",
            "view_testid": "auth-screen",
            "action": "fill",
            "fields": [
                _field(
                    "email",
                    "login-email",
                    value_from="seed.parent_email",
                    value="{{seed.parent_email}}",
                ),
                _field(
                    "password",
                    "login-password",
                    value_from="seed.parent_password",
                    value="{{seed.parent_password}}",
                ),
            ],
            "delay_ms_after": 600,
            "exit_condition": {"type": "visible", "test_id": "auth-submit"},
            "note": "Preencher credenciais",
            "file": "screens/AuthScreen.tsx",
        },
        {
            "feature_step_id": "login.submit",
            "view": "AuthScreen",
            "view_testid": "auth-screen",
            "action": "tap",
            "fields": [_field("submit_login", "auth-submit", delay_ms=200)],
            "delay_ms_after": 1500,
            "exit_condition": {"type": "visible", "test_id": "parent-home"},
            "note": "Entrar",
            "file": "screens/AuthScreen.tsx",
        },
        {
            "feature_step_id": "login.wait_home",
            "view": "ParentHome",
            "view_testid": "parent-home",
            "action": "wait",
            "fields": [_field("home_anchor", "parent-home")],
            "delay_ms_after": 1200,
            "exit_condition": {"type": "visible", "test_id": "parent-home"},
            "note": "Aguardar home do parent",
            "file": "screens/ParentHome.tsx",
        },
    ],
    "go_to_home_child": [
        {
            "feature_step_id": "home.launch",
            "view": "",
            "view_testid": "",
            "action": "launch",
            "fields": [],
            "delay_ms_after": 2000,
            "exit_condition": {
                "type": "visible_any",
                "test_ids": ["child-home-v2", "pre-pairing-screen"],
            },
            "note": "Abrir app child",
            "file": "",
        },
        {
            "feature_step_id": "home.wait",
            "view": "ChildHomeV2",
            "view_testid": "child-home-v2",
            "action": "wait",
            "fields": [_field("home_anchor", "child-home-v2")],
            "delay_ms_after": 1500,
            "exit_condition": {"type": "visible", "test_id": "greeting-title"},
            "note": "Aguardar ChildHomeV2",
            "file": "screens/ChildHomeV2.tsx",
        },
    ],
}


def _load_stacks_json() -> dict[str, Any]:
    """Fonte canônica mobile-setup/env/stacks.json — sem inventar valores."""
    try:
        from lib.mobile.mobile_setup_client import setup_root

        path = setup_root() / "env" / "stacks.json"
        if not path.is_file():
            return {}
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def build_device_context(app: str, *, launch_exit_test_id: str = "") -> dict[str, Any]:
    """Objeto device irmão de scenario_pipeline — dados só de stack/stacks.json."""
    app_id = app if app in ("parent", "child") else "child"
    s = stack(app_id)
    stacks = _load_stacks_json()
    app_json = stacks.get(app_id) if isinstance(stacks.get(app_id), dict) else {}
    api_json = stacks.get("api") if isinstance(stacks.get("api"), dict) else {}

    serial = str(app_json.get("emulator") or s["emulator"]).strip()
    avd = str(app_json.get("avd") or s["avd"]).strip()
    bundle_id = str(app_json.get("bundle_id") or s["bundle_id"]).strip()
    activity_raw = str(app_json.get("activity") or s["activity"]).strip()
    # stacks.json usa ".MainActivity"; runtime_config usa "pkg/.MainActivity"
    if activity_raw.startswith("."):
        activity_short = activity_raw
        activity_full = f"{bundle_id}/{activity_raw}"
    elif "/" in activity_raw:
        activity_full = activity_raw
        activity_short = activity_raw.split("/", 1)[-1]
        if not activity_short.startswith("."):
            activity_short = f".{activity_short.split('.')[-1]}"
    else:
        activity_short = activity_raw if activity_raw.startswith(".") else f".{activity_raw}"
        activity_full = f"{bundle_id}/{activity_short}"

    metro_port = int(app_json.get("metro_port") or s["metro_port"])
    metro_host = METRO_EMULATOR_HOST
    metro_url = f"http://{metro_host}:{metro_port}"
    schemes = tuple(app_json.get("deep_link_schemes") or s["deep_link_schemes"])
    dev_client_url = str(app_json.get("dev_client_url") or "").strip()
    if not dev_client_url and schemes:
        dev_client_url = f"{schemes[0]}://expo-development-client/?url={metro_url}"
    candidates = [
        f"{scheme}://expo-development-client/?url={metro_url}" for scheme in schemes
    ]
    # preferir URL canônica do stacks.json no topo
    if dev_client_url and dev_client_url not in candidates:
        candidates = [dev_client_url, *candidates]

    adb_port = app_json.get("port")
    if adb_port is None and serial.startswith("emulator-"):
        try:
            adb_port = int(serial.replace("emulator-", "", 1))
        except ValueError:
            adb_port = None

    api_base = str(
        app_json.get("api_base_url")
        or s.get("api_base_url")
        or api_json.get("emulator_base")
        or "http://10.0.2.2:3000/api/v1"
    ).rstrip("/")

    appium_host = str(api_json.get("appium_host") or "127.0.0.1").strip()
    appium_port = int(api_json.get("appium_port") or 4723)

    exit_tid = launch_exit_test_id or (
        "auth-screen" if app_id == "parent" else "pre-pairing-screen"
    )

    return {
        "app": app_id,
        "repo": s["repo"],
        "label": str(app_json.get("label") or s["label"]),
        "serial": serial,
        "avd": avd,
        "adb_port": adb_port,
        "bundle_id": bundle_id,
        "activity": activity_short,
        "activity_full": activity_full,
        "metro_port": metro_port,
        "metro_host_emulator": metro_host,
        "metro_url": metro_url,
        "deep_link_schemes": list(schemes),
        "dev_client_url": dev_client_url,
        "deep_link_candidates": candidates,
        "api_base_url": api_base,
        "appium": {
            "host": appium_host,
            "port": appium_port,
        },
        "adb_reverse_ports": [metro_port, 3000],
        "launch": {
            "mode": "dev_client",
            "require_metro": True,
            "hard_stop": False,
            "pm_clear_before_launch": False,
            "dismiss_expo_overlay": True,
            "use_dev_client_url": True,
            "grant_os_permissions": True,
            "dismiss_os_permission_dialogs": True,
            "reload_after_set_clock": True,
            "stabilize_between_steps": True,
            "exit_test_id": exit_tid,
            "exit_locator": f"testID:{exit_tid}",
        },
    }


def _resolve_app_for_pipeline(task: dict[str, Any], suites: dict[str, bool], feature: str) -> str:
    want_parent = bool(suites.get("parent")) and not bool(suites.get("child"))
    return "parent" if want_parent or feature == "login" else "child"


def _qa_evidence(task: dict[str, Any]) -> dict[str, Any]:
    qa = task.get("qa") if isinstance(task.get("qa"), dict) else {}
    evidence = qa.get("evidence") if isinstance(qa.get("evidence"), dict) else {}
    return evidence


def _resolve_scenario_id(task: dict[str, Any], scenario_id: str) -> str:
    sid = str(scenario_id or "").strip()
    if sid:
        return sid
    qa = task.get("qa") if isinstance(task.get("qa"), dict) else {}
    scenarios = [str(s).strip() for s in (qa.get("scenarios") or []) if str(s).strip()]
    return scenarios[0] if scenarios else ""


def _description_for_scenario(
    scenario_id: str,
    *,
    suites: dict[str, bool],
    screenshot: bool,
    video_record: bool,
    user_flow: dict[str, Any] | None = None,
) -> str:
    sid = scenario_id.strip()
    app = "child" if suites.get("child") and not suites.get("parent") else (
        "parent" if suites.get("parent") and not suites.get("child") else "mobile"
    )
    target = ""
    if isinstance(user_flow, dict):
        target = str(user_flow.get("target_element") or user_flow.get("target_screen") or "").strip()

    m = _GREETING_RE.match(sid)
    if m:
        label = _GREETING_LABEL.get(m.group(1).lower(), "saudação")
        hour = m.group(2)
        base = (
            f"Deve-se tirar um print da saudação na home do app {app} "
            f"com {label} (cenário {sid}, horário ~{hour}h)"
        )
        if target:
            base += f" — alvo: {target}"
        if video_record:
            base += "; gravar vídeo do fluxo até a home"
        return base

    if sid:
        parts = [f"Cenário de teste `{sid}` no app {app}"]
        if screenshot:
            parts.append("capturar screenshot no ponto de evidência")
        if video_record:
            parts.append("gravar vídeo do fluxo")
        if target:
            parts.append(f"alvo: {target}")
        return " — ".join(parts) + "."

    parts = [f"Executar evidência no app {app}"]
    if screenshot:
        parts.append("com screenshot")
    if video_record:
        parts.append("e gravação de vídeo")
    return " ".join(parts) + "."


def _slug(text: str, fallback: str = "step") -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return s or fallback


def _extract_test_id(*candidates: Any) -> str:
    for raw in candidates:
        text = str(raw or "").strip()
        if not text:
            continue
        m = re.match(r"^(?:testID|testid|test_id)\s*[:=]\s*(.+)$", text, re.I)
        if m:
            return m.group(1).strip()
        if re.match(r"^(accessibility_id|id|xpath|android|~)\s*[:=]", text, re.I):
            rest = re.split(r"[:=]", text, maxsplit=1)[-1].strip().lstrip("~")
            if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", rest):
                return rest
            continue
        if re.fullmatch(r"[a-z0-9]+(?:[_:-][a-z0-9]+)+", text) or re.fullmatch(r"[a-z0-9]+", text):
            return text
    return ""


def _normalize_exit_condition(raw: Any) -> dict[str, Any] | str:
    if isinstance(raw, dict):
        out = dict(raw)
        tid = _extract_test_id(out.get("test_id"), out.get("testID"), out.get("locator"))
        if tid:
            out["test_id"] = tid
            out["locator"] = _tid(tid)
        tids = out.get("test_ids")
        if isinstance(tids, list):
            cleaned = [_extract_test_id(x) for x in tids]
            out["test_ids"] = [t for t in cleaned if t]
            out["locators"] = [_tid(t) for t in out["test_ids"]]
        return out
    # prosa do ticket não vira exit executável
    return ""


def _normalize_fields(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for i, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            continue
        tid = _extract_test_id(
            item.get("test_id"),
            item.get("testID"),
            item.get("locator"),
            item.get("accessibility_id"),
        )
        field: dict[str, Any] = {
            "order": int(item.get("order") or i),
            "name": str(
                item.get("name")
                or item.get("field")
                or (tid.replace("-", "_") if tid else f"field_{i}")
            ),
            "test_id": tid,
            "locator": _tid(tid) if tid else "",
            "value_from": str(item.get("value_from") or ""),
            "value": item.get("value") if item.get("value") is not None else "",
            "delay_ms": int(item.get("delay_ms") or _DEFAULT_FIELD_DELAY_MS),
        }
        if item.get("input_mode"):
            field["input_mode"] = str(item.get("input_mode"))
        if item.get("input_target"):
            field["input_target"] = str(item.get("input_target")).strip()
        if item.get("focus_test_id"):
            field["focus_test_id"] = _extract_test_id(item.get("focus_test_id")) or str(
                item.get("focus_test_id") or ""
            ).strip()
        if item.get("expected_length") is not None:
            try:
                field["expected_length"] = int(item.get("expected_length"))
            except (TypeError, ValueError):
                pass
        out.append(field)
    out.sort(key=lambda f: int(f["order"]))
    for i, f in enumerate(out, start=1):
        f["order"] = i
    return out


def _field_has_value(field: dict[str, Any]) -> bool:
    val = field.get("value")
    vf = str(field.get("value_from") or "").strip()
    if vf:
        return True
    if val is None:
        return False
    text = str(val).strip()
    return bool(text)


def _primary_test_id(fields: list[dict[str, Any]], view_testid: str = "") -> str:
    for f in fields:
        tid = str(f.get("test_id") or "").strip()
        if tid:
            return tid
    return str(view_testid or "").strip()


def _resolve_action(
    *,
    raw_action: str,
    primary_test_id: str,
    view_testid: str,
    feature_step_id: str = "",
) -> tuple[str, str | None]:
    """Action explícita tipada > catálogo[test_id] > catálogo[view_testid]. Sem prosa."""
    action = str(raw_action or "").strip().lower()
    if action in _ALLOWED_ACTIONS:
        return action, None
    # legado / ticket: navigate e vazios não contam
    for key in (primary_test_id, view_testid):
        cat = _STEP_CATALOG.get(key)
        if cat and cat.get("action") in _ALLOWED_ACTIONS:
            return str(cat["action"]), None
    if feature_step_id:
        return "", f"UNBOUND_ACTION:feature_step={feature_step_id}"
    return "", f"UNBOUND_ACTION:test_id={primary_test_id or view_testid or '(none)'}"


def _validate_field_action_matrix(action: str, fields: list[dict[str, Any]]) -> str | None:
    """Retorna código de violação ou None."""
    if action not in _ALLOWED_ACTIONS:
        return "INVALID_ACTION"
    if action == "launch":
        return None
    if action == "fill":
        if not fields:
            return "MATRIX:fill_requires_fields"
        if not all(f.get("test_id") for f in fields):
            return "MATRIX:fill_requires_test_id"
        if not any(_field_has_value(f) for f in fields):
            return "MATRIX:fill_requires_value"
        return None
    if action == "tap":
        if not fields:
            return "MATRIX:tap_requires_fields"
        if not all(f.get("test_id") for f in fields):
            return "MATRIX:tap_requires_test_id"
        if any(_field_has_value(f) for f in fields):
            return "MATRIX:tap_forbids_value"
        return None
    if action == "wait":
        if fields and not all(f.get("test_id") for f in fields):
            return "MATRIX:wait_fields_need_test_id"
        return None
    if action == "set_clock":
        if not fields:
            return "MATRIX:set_clock_requires_field"
        if not any(_field_has_value(f) for f in fields):
            return "MATRIX:set_clock_requires_value"
        return None
    if action == "capture":
        if not fields or not fields[0].get("test_id"):
            return "MATRIX:capture_requires_test_id"
        return None
    if action in ("record_start", "record_stop"):
        return None
    return "MATRIX:unknown"


def _guess_view_testid(view: str) -> str:
    if view in _KNOWN_REPO_VIEWS:
        meta_tid = next((tid for tid, v in _VIEW_FROM_TESTID.items() if v == view), "")
        # prefer screen root testids
        for preferred in (
            "pre-pairing-screen",
            "permissions-onboarding-screen",
            "child-home-v2",
            "auth-screen",
            "parent-home",
        ):
            if _VIEW_FROM_TESTID.get(preferred) == view:
                return preferred
        return meta_tid
    guess = re.sub(r"(?<!^)(?=[A-Z0-9])", "-", view).replace("_", "-").lower()
    guess = re.sub(r"-{2,}", "-", guess).strip("-")
    if guess in _STEP_CATALOG:
        return guess
    return ""


def _normalize_repo_file(file_path: str) -> str:
    text = str(file_path or "").replace("\\", "/").strip()
    if not text:
        return ""
    for prefix in ("screens/", "components/"):
        idx = text.find(prefix)
        if idx >= 0:
            return text[idx:]
    return text if text.endswith((".tsx", ".ts", ".mjs", ".js")) else ""


def _view_from_repo_file(file_path: str) -> str:
    norm = _normalize_repo_file(file_path)
    if not norm.startswith(("screens/", "components/")):
        return ""
    stem = Path(norm).stem
    if stem in _KNOWN_REPO_VIEWS:
        return stem
    # PairingCodeInput etc.
    if stem in _REPO_VIEW_FILES:
        return stem
    return ""


def _resolve_repo_view(
    *,
    view_testid: str = "",
    file_path: str = "",
    fields: list[dict[str, Any]] | None = None,
    exit_condition: Any = None,
) -> tuple[str, str]:
    """Retorna (view_component, file_repo). Nunca usa label do ticket."""
    fields = fields or []
    file_norm = _normalize_repo_file(file_path)
    view_from_file = _view_from_repo_file(file_norm)
    if view_from_file:
        return view_from_file, file_norm or _REPO_VIEW_FILES.get(view_from_file, "")

    candidates: list[str] = []
    if view_testid:
        candidates.append(view_testid)
    for f in fields:
        tid = str(f.get("test_id") or "").strip()
        if tid:
            candidates.append(tid)
    if isinstance(exit_condition, dict):
        tid = str(exit_condition.get("test_id") or "").strip()
        if tid:
            candidates.append(tid)
        for t in exit_condition.get("test_ids") or []:
            t = str(t or "").strip()
            if t:
                candidates.append(t)

    for tid in candidates:
        view = _VIEW_FROM_TESTID.get(tid)
        if view:
            return view, _REPO_VIEW_FILES.get(view, file_norm)

    return "", file_norm


_ALLOWED_HOOKS = frozenset({"dismiss_expo", "force_reload", "grant_os_perms", "stabilize"})
# Overlay Expo / reload / grants — defaults por action (genérico para qualquer cenário).
_ACTIONS_DEFAULT_DISMISS_EXPO = frozenset({"launch", "set_clock"})
_ACTIONS_DEFAULT_FORCE_RELOAD = frozenset({"set_clock"})
_ACTIONS_DEFAULT_GRANT_OS = frozenset({"launch", "set_clock"})


def _normalize_hooks(raw: Any, action: str) -> list[str]:
    hooks: list[str] = []
    if isinstance(raw, list):
        for h in raw:
            name = str(h or "").strip().lower()
            if name in _ALLOWED_HOOKS and name not in hooks:
                hooks.append(name)
    if action in _ACTIONS_DEFAULT_DISMISS_EXPO and "dismiss_expo" not in hooks:
        hooks.append("dismiss_expo")
    if action in _ACTIONS_DEFAULT_FORCE_RELOAD and "force_reload" not in hooks:
        hooks.append("force_reload")
    if action in _ACTIONS_DEFAULT_GRANT_OS and "grant_os_perms" not in hooks:
        hooks.append("grant_os_perms")
    return hooks


def _chain_steps(raw_steps: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    steps: list[dict[str, Any]] = []
    violations: list[dict[str, str]] = []
    for i, raw in enumerate(raw_steps, start=1):
        feature_step_id = str(raw.get("feature_step_id") or "").strip()
        fields = _normalize_fields(raw.get("fields"))
        file_path = str(raw.get("file") or "")
        exit_raw = raw.get("exit_condition")
        if not isinstance(exit_raw, dict):
            exit_raw = {}

        # view_testid só de campos tipados / feature — nunca de screen label do ticket
        view_testid = _extract_test_id(raw.get("view_testid"), raw.get("view_test_id"))
        if not view_testid:
            view_testid = _primary_test_id(fields, "")

        action_hint = str(raw.get("action") or "").strip().lower()
        # launch não herda view do exit_condition (ainda não está na screen)
        if action_hint != "launch" and not view_testid and isinstance(exit_raw, dict):
            view_testid = _extract_test_id(exit_raw.get("test_id")) or ""
            if not view_testid:
                tids = exit_raw.get("test_ids") or []
                if tids:
                    view_testid = _extract_test_id(tids[0])

        # Se feature já trouxe view canônica do repo, usar só como hint de file/testid
        feature_view_hint = str(raw.get("view") or "").strip()
        if feature_view_hint in _KNOWN_REPO_VIEWS and not view_testid:
            view_testid = _guess_view_testid(feature_view_hint)
            if not file_path:
                file_path = _REPO_VIEW_FILES.get(feature_view_hint, "")

        if action_hint == "launch":
            view, file_resolved = "", _normalize_repo_file(file_path)
            view_testid = ""
        else:
            view, file_resolved = _resolve_repo_view(
                view_testid=view_testid,
                file_path=file_path,
                fields=fields,
                exit_condition=exit_raw,
            )
            if view and not view_testid:
                view_testid = _guess_view_testid(view)

        step_id = str(raw.get("step_id") or feature_step_id or f"s{i}_{_slug(view or 'step')}")
        primary = _primary_test_id(fields, view_testid)
        action, action_err = _resolve_action(
            raw_action=str(raw.get("action") or ""),
            primary_test_id=primary,
            view_testid=view_testid,
            feature_step_id=feature_step_id,
        )
        if action_err:
            violations.append({"step_id": step_id, "reason": action_err})
        matrix_err = _validate_field_action_matrix(action, fields) if action else "UNBOUND_ACTION"
        if matrix_err and action:
            violations.append({"step_id": step_id, "reason": matrix_err})
        if action not in ("launch", "record_start", "record_stop") and not view:
            # steps de UI precisam de view do repo
            if action in _ALLOWED_ACTIONS:
                violations.append({"step_id": step_id, "reason": "UNBOUND_VIEW:no_repo_screen"})

        note = str(raw.get("note") or "").strip()
        prose = str(raw.get("user_action") or raw.get("system_behavior") or "").strip()
        if prose and prose not in note:
            note = f"{note}; {prose}".strip("; ").strip() if note else prose

        hooks = _normalize_hooks(raw.get("hooks"), action)
        optional = bool(raw.get("optional"))
        assert_text = str(raw.get("assert_text") or "").strip()

        view_gate = None
        if action not in ("launch", "set_clock", "record_start", "record_stop") and view_testid:
            view_gate = {
                "test_id": view_testid,
                "required": True,
                "timeout_ms": 25_000,
            }

        steps.append(
            {
                "step_id": step_id,
                "feature_step_id": feature_step_id,
                "order": int(raw.get("order") or i),
                "view": view,
                "view_testid": view_testid if view else "",
                "view_gate": view_gate,
                "action": action,
                "fields": fields,
                "delay_ms_after": int(
                    raw.get("delay_ms_after") or raw.get("delay_ms") or _DEFAULT_STEP_DELAY_MS
                ),
                "next_step": "",
                "exit_condition": _normalize_exit_condition(exit_raw),
                "hooks": hooks,
                "optional": optional,
                "assert_text": assert_text,
                "note": note,
                "file": file_resolved or _normalize_repo_file(file_path),
            }
        )
    steps.sort(key=lambda s: int(s["order"]))
    for i, step in enumerate(steps):
        step["order"] = i + 1
        step["next_step"] = steps[i + 1]["step_id"] if i + 1 < len(steps) else ""
    return steps, violations


def _greeting_prepare_steps(scenario_id: str, start_order: int) -> list[dict[str, Any]]:
    m = _GREETING_RE.match(scenario_id.strip())
    if not m:
        return []
    period, hour = m.group(1).lower(), m.group(2)
    clock = f"{int(hour):02d}:00"
    return [
        {
            "feature_step_id": f"greeting.set_clock.{period}",
            "order": start_order,
            "view": "ChildHomeV2",
            "view_testid": "child-home-v2",
            "action": "set_clock",
            "fields": [
                _field(
                    "device_time",
                    "child-home-v2",
                    value_from="scenario.clock",
                    value=clock,
                    delay_ms=0,
                ),
            ],
            "delay_ms_after": 500,
            "exit_condition": {"type": "visible", "test_id": "greeting-title"},
            "hooks": ["dismiss_expo", "force_reload", "grant_os_perms"],
            "note": f"Ajustar relógio do emulador para {clock} ({_GREETING_LABEL.get(period, period)}) + force reload",
            "file": "screens/childHome.state.ts",
        }
    ]


def _capture_steps(
    *,
    scenario_id: str,
    target_element: str,
    start_order: int,
    screenshot: bool,
    app: str,
) -> list[dict[str, Any]]:
    if not screenshot:
        return []
    sid = scenario_id.strip() or "evidence"
    tid = _extract_test_id(target_element) or (
        "greeting-title" if _GREETING_RE.match(sid) else ("parent-home" if app == "parent" else "child-home-v2")
    )
    view = _VIEW_FROM_TESTID.get(tid) or ("ParentHome" if app == "parent" else "ChildHomeV2")
    root_by_view = {
        "ChildHomeV2": "child-home-v2",
        "ParentHome": "parent-home",
        "PrePairingScreen": "pre-pairing-screen",
        "PermissionsOnboardingScreen": "permissions-onboarding-screen",
        "AuthScreen": "auth-screen",
    }
    view_tid = root_by_view.get(view, "")
    assert_text = ""
    gm = _GREETING_RE.match(sid)
    if gm:
        assert_text = _GREETING_LABEL.get(gm.group(1).lower(), "")
    return [
        {
            "feature_step_id": f"capture.{sid}",
            "order": start_order,
            "view": view,
            "view_testid": view_tid,
            "action": "capture",
            "fields": [
                {
                    "order": 1,
                    "name": "target_element",
                    "test_id": tid,
                    "locator": _tid(tid),
                    "value_from": "",
                    "value": "",
                    "delay_ms": 500,
                }
            ],
            "delay_ms_after": 800,
            "assert_text": assert_text,
            "note": (
                f"Captura PNG cenário {sid} (testID {tid}"
                + (f", texto {assert_text}" if assert_text else "")
                + ")"
            ),
            "file": _REPO_VIEW_FILES.get(view, ""),
            "exit_condition": {
                "type": "assert_before_capture",
                "test_id": tid,
                "locator": _tid(tid),
            },
        }
    ]


def _typed_steps_from_user_flow(user_flow: dict[str, Any]) -> list[dict[str, Any]]:
    """Só aceita steps tipados (action no enum e/ou fields com test_id).

    `view`/`screen` do ticket são ignorados — view resolve pelo repo (file/test_id).
    """
    raw = user_flow.get("steps") if isinstance(user_flow.get("steps"), list) else []
    if not raw:
        return []
    mapped: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        action = str(item.get("action") or "").strip().lower()
        fields = _normalize_fields(item.get("fields"))
        view_testid = _extract_test_id(item.get("view_testid"), item.get("test_id"))
        file_path = _normalize_repo_file(str(item.get("file") or ""))
        # file do ticket só vale se for path de screens/components do app
        if file_path and not file_path.startswith(("screens/", "components/")):
            file_path = ""
        has_tid = bool(view_testid) or any(f.get("test_id") for f in fields)
        if action not in _ALLOWED_ACTIONS and not has_tid and not _view_from_repo_file(file_path):
            return []  # prosa / sem amarração de repo → feature pipeline
        mapped.append(
            {
                "order": item.get("order"),
                "feature_step_id": str(item.get("feature_step_id") or ""),
                "view": "",  # resolvido depois via file/test_id
                "view_testid": view_testid,
                "action": action if action in _ALLOWED_ACTIONS else "",
                "fields": fields,
                "delay_ms_after": item.get("delay_ms_after")
                or item.get("delay_ms")
                or _DEFAULT_STEP_DELAY_MS,
                "exit_condition": item.get("exit_condition")
                if isinstance(item.get("exit_condition"), dict)
                else {},
                "file": file_path,
                "note": str(item.get("note") or item.get("user_action") or ""),
            }
        )
    return mapped


def _ticket_notes_from_user_flow(user_flow: dict[str, Any]) -> list[str]:
    """Prosa do ticket vira só notes (não action)."""
    notes: list[str] = []
    for item in user_flow.get("steps") or []:
        if not isinstance(item, dict):
            continue
        for key in ("user_action", "system_behavior", "note"):
            text = str(item.get(key) or "").strip()
            if text and text not in notes:
                notes.append(text)
    return notes


def _resolve_user_flow(ctx: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    ticket = ctx.get("ticket") if isinstance(ctx.get("ticket"), dict) else {}
    for candidate in (
        ticket.get("user_flow"),
        ctx.get("user_flow"),
        (task.get("refinement") or {}).get("user_flow") if isinstance(task.get("refinement"), dict) else None,
        task.get("user_flow"),
    ):
        if isinstance(candidate, dict) and candidate:
            return candidate
    return {}


def build_scenario_pipeline(
    *,
    task: dict[str, Any],
    scenario_id: str,
    ctx: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Monta scenario_pipeline: meta + steps até captura do scenario_id."""
    ctx = ctx or {}
    suites = resolve_suites_mobile(task)
    evidence = _qa_evidence(task)
    screenshot = bool(evidence.get("screenshot_png", True))
    video_record = bool(evidence.get("video_mp4", True))
    if evidence.get("screenshot_scope"):
        screenshot = True
    if evidence.get("video_scope") or evidence.get("greeting_video"):
        video_record = True

    user_flow = _resolve_user_flow(ctx, task)
    feature = resolve_appium_feature_from_ticket(task)
    app = _resolve_app_for_pipeline(task, suites, feature)
    feature_key = feature if feature in _FEATURE_PIPELINES else ("login" if app == "parent" else "pairing")

    typed = _typed_steps_from_user_flow(user_flow)
    source = "user_flow_typed" if typed else f"feature:{feature_key}"
    nav_raw = typed if typed else [dict(s) for s in _FEATURE_PIPELINES.get(feature_key, _FEATURE_PIPELINES["pairing"])]
    ticket_notes = _ticket_notes_from_user_flow(user_flow) if not typed else []

    # target_element: só test_id; target_screen do ticket nunca vira view
    target_element = _extract_test_id(user_flow.get("target_element")) or (
        "greeting-title"
        if _GREETING_RE.match(scenario_id.strip())
        else ("parent-home" if app == "parent" else "child-home-v2")
    )

    greeting_raw = _greeting_prepare_steps(scenario_id, start_order=len(nav_raw) + 1)
    capture_raw = _capture_steps(
        scenario_id=scenario_id,
        target_element=target_element,
        start_order=len(nav_raw) + len(greeting_raw) + 1,
        screenshot=screenshot,
        app=app,
    )
    steps, violations = _chain_steps([*nav_raw, *greeting_raw, *capture_raw])

    description = _description_for_scenario(
        scenario_id,
        suites=suites,
        screenshot=screenshot,
        video_record=video_record,
        user_flow=user_flow or None,
    )

    binding_ok = not violations
    qa = task.get("qa") if isinstance(task.get("qa"), dict) else {}
    return {
        "suites_mobile": {
            "parent": bool(suites.get("parent")),
            "child": bool(suites.get("child")),
        },
        "screenshot": screenshot,
        "video_record": video_record,
        "description": description,
        "steps": steps,
        "appium_feature": feature_key,
        "ticket_qa": {
            "test_suite": qa.get("test_suite"),
            "scenarios": list(qa.get("scenarios") or []),
            "evidence": dict(qa.get("evidence") or {}) if isinstance(qa.get("evidence"), dict) else {},
            "db_seed": dict(qa.get("db_seed") or {}) if isinstance(qa.get("db_seed"), dict) else {},
            "appium_scope": qa.get("appium_scope"),
            "evidence_pipeline": (
                dict(qa.get("evidence_pipeline") or {})
                if isinstance(qa.get("evidence_pipeline"), dict)
                else {}
            ),
        },
        "binding": {
            "ok": binding_ok,
            "source": source,
            "violations": violations,
            "ticket_notes": ticket_notes,
        },
        "_app": app,
    }


def _device_from_pipeline(pipeline: dict[str, Any]) -> dict[str, Any]:
    app = str(pipeline.pop("_app", "") or "").strip()
    if not app:
        suites = pipeline.get("suites_mobile") if isinstance(pipeline.get("suites_mobile"), dict) else {}
        app = "parent" if suites.get("parent") and not suites.get("child") else "child"
    exit_tid = ""
    exit_tids: list[str] = []
    for st in pipeline.get("steps") or []:
        if not isinstance(st, dict):
            continue
        if str(st.get("action") or "") == "launch":
            ec = st.get("exit_condition")
            if isinstance(ec, dict):
                exit_tid = str(ec.get("test_id") or "").strip()
                for t in ec.get("test_ids") or []:
                    t = str(t or "").strip()
                    if t and t not in exit_tids:
                        exit_tids.append(t)
                if exit_tid and exit_tid not in exit_tids:
                    exit_tids.insert(0, exit_tid)
                if not exit_tid and exit_tids:
                    exit_tid = exit_tids[0]
            break
    device = build_device_context(app, launch_exit_test_id=exit_tid)
    if exit_tids:
        launch = dict(device.get("launch") or {})
        launch["exit_test_ids"] = exit_tids
        launch["exit_locators"] = [f"testID:{t}" for t in exit_tids]
        device["launch"] = launch
    return device


def run_qa_pipeline_evidence(
    actuation_context: dict[str, Any] | str | None = None,
    *,
    apps_ready_ok: bool = False,
    scenario_id: str = "",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Gera scenario_pipeline só se apps_ready_ok=true."""
    if actuation_context is None or actuation_context == "":
        return {
            "ok": False,
            "tool": "qa_pipeline_evidence",
            "apps_ready_ok": bool(apps_ready_ok),
            "scenario_id": str(scenario_id or ""),
            "blocking_reason": "MISSING_ACTUATION_CONTEXT",
            "scenario_pipeline": None,
            "device": None,
        }

    try:
        ctx = load_actuation(actuation_context)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "tool": "qa_pipeline_evidence",
            "apps_ready_ok": bool(apps_ready_ok),
            "scenario_id": str(scenario_id or ""),
            "blocking_reason": "INVALID_ACTUATION_CONTEXT",
            "error": str(exc),
            "scenario_pipeline": None,
            "device": None,
        }

    task = task_from_ctx(ctx)
    tid = str(task.get("id") or "").strip()
    ticket = ctx.get("ticket") if isinstance(ctx.get("ticket"), dict) else {}
    if isinstance(ticket.get("user_flow"), dict):
        task["user_flow"] = ticket["user_flow"]
    elif ctx.get("user_flow"):
        task["user_flow"] = ctx["user_flow"]
    if isinstance(ticket.get("qa"), dict):
        merged_qa = dict(task.get("qa") or {})
        merged_qa.update(ticket["qa"])
        task["qa"] = merged_qa
    if isinstance(ticket.get("refinement"), dict) and not task.get("refinement"):
        task["refinement"] = ticket["refinement"]

    resolved_sid = _resolve_scenario_id(task, scenario_id)
    base = {
        "tool": "qa_pipeline_evidence",
        "task_id": tid,
        "apps_ready_ok": bool(apps_ready_ok),
        "scenario_id": resolved_sid,
    }

    if not apps_ready_ok:
        return {
            **base,
            "ok": False,
            "blocking_reason": "APPS_NOT_READY",
            "scenario_pipeline": None,
            "device": None,
            "note": "Pipeline só é gerado quando apps_ready_ok=true",
        }

    if not resolved_sid:
        return {
            **base,
            "ok": False,
            "blocking_reason": "MISSING_SCENARIO_ID",
            "scenario_pipeline": None,
            "device": None,
            "note": "Informe scenario_id ou configure qa.scenarios no ticket",
        }

    pipeline = build_scenario_pipeline(task=task, scenario_id=resolved_sid, ctx=ctx)
    device = _device_from_pipeline(pipeline)
    binding = pipeline.get("binding") if isinstance(pipeline.get("binding"), dict) else {}
    if not binding.get("ok", True):
        return {
            **base,
            "ok": False,
            "blocking_reason": "UNBOUND_ACTION",
            "scenario_pipeline": pipeline,
            "device": device,
            "note": "Action/test_id inválidos — corrija catálogo ou steps tipados",
        }

    if dry_run:
        return {
            **base,
            "ok": True,
            "dry_run": True,
            "would_build": {
                "suites_mobile": pipeline.get("suites_mobile"),
                "screenshot": pipeline.get("screenshot"),
                "video_record": pipeline.get("video_record"),
                "steps": len(pipeline.get("steps") or []),
                "source": binding.get("source"),
                "device_serial": device.get("serial"),
                "dev_client_url": device.get("dev_client_url"),
            },
            "scenario_pipeline": pipeline,
            "device": device,
        }

    return {
        **base,
        "ok": True,
        "scenario_pipeline": pipeline,
        "device": device,
        "blocking_reason": None,
    }
