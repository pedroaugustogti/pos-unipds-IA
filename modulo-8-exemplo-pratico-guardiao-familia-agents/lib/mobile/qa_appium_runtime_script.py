"""Gera e executa script Appium (Node/WDIO) a partir de scenario_pipeline.steps.

Todos os locators são testID do app RN (resourceId / ~testid).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.mobile.mobile_runtime_config import stack
from lib.mobile.mobile_setup_client import appium_root, handoff_path, setup_root
from lib.ticket_output import qa_evidence_dir, resolve_agent_cycle

_LOCATOR_RE = re.compile(
    r"^(testID|testid|test_id|accessibility_id|id|xpath|android|~)\s*[:=]\s*(.+)$",
    re.I,
)


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _resolve_seed_values() -> dict[str, str]:
    hp = handoff_path()
    if not hp.is_file():
        return {}
    try:
        data = json.loads(hp.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {
        "seed.pairing_code": str(data.get("pairingCode") or data.get("pairing_code") or ""),
        "seed.parent_email": str(data.get("email") or data.get("parent_email") or ""),
        "seed.parent_password": str(data.get("password") or data.get("parent_password") or ""),
        "seed.child_name": str(data.get("childName") or data.get("child_name") or ""),
    }


def _resolve_value(field: dict[str, Any], seed: dict[str, str]) -> str:
    raw = field.get("value")
    if raw is None:
        raw = ""
    text = str(raw)
    vf = str(field.get("value_from") or "").strip()
    if vf and seed.get(vf):
        return seed[vf]
    text = re.sub(r"\{\{\s*([^}]+)\s*\}\}", lambda m: seed.get(m.group(1).strip(), m.group(0)), text)
    if text in ("", "{{seed.pairing_code}}") and vf:
        return seed.get(vf, text)
    return text


def _extract_testid_token(locator: str) -> str:
    loc = (locator or "").strip()
    m = _LOCATOR_RE.match(loc)
    if m and m.group(1).lower() in ("testid", "test_id"):
        return m.group(2).strip()
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", loc):
        return loc
    return ""


def _testid_selectors(test_id: str) -> list[str]:
    tid = test_id.strip()
    if not tid:
        return []
    esc = tid.replace('"', '\\"')
    # Preferência: 2 seletores estáveis (resourceIdMatches + accessibility) —
    # evita loop de 4× find por poll no Appium.
    return [
        f'android=new UiSelector().resourceIdMatches(".*{re.escape(tid)}$")',
        f"~{tid}",
        f'android=new UiSelector().resourceId("{esc}")',
        f'android=new UiSelector().description("{esc}")',
    ]


def _testid_selectors_compact(test_id: str) -> list[str]:
    """Gatilho de view / poll de navegação — só 2 strategies."""
    return _testid_selectors(test_id)[:2]


def _selector_js(locator: str) -> str:
    loc = (locator or "").strip()
    if not loc:
        return 'android=new UiSelector().className("android.widget.EditText")'
    tid = _extract_testid_token(loc)
    if tid:
        return _testid_selectors(tid)[0]
    m = _LOCATOR_RE.match(loc)
    if m:
        kind, rest = m.group(1).lower(), m.group(2).strip()
        if kind in ("accessibility_id", "~"):
            return f"~{rest}"
        if kind == "id":
            return f"id:{rest}"
        if kind == "xpath":
            return rest if rest.startswith("//") or rest.startswith("(") else f"//{rest}"
        if kind == "android":
            return rest if rest.startswith("android=") else f"android={rest}"
    if loc.startswith("~") or loc.startswith("id:") or loc.startswith("android=") or loc.startswith("//"):
        return loc
    token = loc.replace('"', '\\"')
    return f'android=new UiSelector().descriptionContains("{token}")'


def _field_selectors(field: dict[str, Any]) -> list[str]:
    tid = str(field.get("test_id") or _extract_testid_token(str(field.get("locator") or ""))).strip()
    if tid:
        return _testid_selectors(tid)
    sel = _selector_js(str(field.get("locator") or ""))
    return [sel] if sel else []


def _exit_selectors(step: dict[str, Any], *, compact: bool = True) -> list[str]:
    """Seletores de saída — compactos por padrão para reduzir polls Appium."""
    pick = _testid_selectors_compact if compact else _testid_selectors
    ec = step.get("exit_condition")
    out: list[str] = []
    if isinstance(ec, dict):
        tid = str(ec.get("test_id") or "").strip()
        if tid:
            out.extend(pick(tid))
        for t in ec.get("test_ids") or []:
            t = str(t or "").strip()
            if t:
                out.extend(pick(t))
        # locators explícitos só se não houver test_id
        if not out:
            for loc in ec.get("locators") or []:
                out.append(_selector_js(str(loc)))
    view_tid = str(step.get("view_testid") or "").strip()
    if view_tid and not out:
        out.extend(pick(view_tid))
    seen: set[str] = set()
    uniq: list[str] = []
    for s in out:
        if s and s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq


def _view_gate_payload(step: dict[str, Any]) -> dict[str, Any] | None:
    """Gatilho por view: script só escaneia fields depois que a view carregou."""
    action = str(step.get("action") or "").lower()
    if action in ("launch", "set_clock", "record_start", "record_stop"):
        return None
    view_tid = str(step.get("view_testid") or "").strip()
    if not view_tid:
        return None
    return {
        "test_id": view_tid,
        "selectors": _testid_selectors_compact(view_tid),
        "required": True,
        "timeout_ms": 25_000,
    }


def build_appium_script_source(
    *,
    pipeline: dict[str, Any],
    task_id: str,
    scenario_id: str,
    app: str,
    evidence_dir: Path,
    seed_values: dict[str, str] | None = None,
    device: dict[str, Any] | None = None,
) -> str:
    """Gera fonte ESM Node que executa steps via WebdriverIO + _shared do mobile-setup."""
    seed = seed_values or _resolve_seed_values()
    app_id = app if app in ("parent", "child") else "child"
    s = stack(app_id)
    dev = device if isinstance(device, dict) and device else {}
    if not dev:
        from lib.mobile.qa_pipeline_evidence import build_device_context

        exit_tid = ""
        for st in pipeline.get("steps") or []:
            if isinstance(st, dict) and str(st.get("action") or "") == "launch":
                ec = st.get("exit_condition")
                if isinstance(ec, dict):
                    exit_tid = str(ec.get("test_id") or "").strip()
                break
        dev = build_device_context(app_id, launch_exit_test_id=exit_tid)

    steps = list(pipeline.get("steps") or [])
    video = bool(pipeline.get("video_record"))
    screenshot = bool(pipeline.get("screenshot"))

    runtime_steps: list[dict[str, Any]] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        fields_out: list[dict[str, Any]] = []
        for f in step.get("fields") or []:
            if not isinstance(f, dict):
                continue
            # Fields: compact first (2); full list só se precisar de fallback no runtime
            selectors = _field_selectors(f)
            compact = selectors[:2] if selectors else []
            fields_out.append(
                {
                    "order": f.get("order"),
                    "name": f.get("name"),
                    "test_id": f.get("test_id") or _extract_testid_token(str(f.get("locator") or "")),
                    "locator": f.get("locator") or "",
                    "selector": compact[0] if compact else (selectors[0] if selectors else ""),
                    "selectors": compact or selectors,
                    "selectors_fallback": selectors[2:] if len(selectors) > 2 else [],
                    "value": _resolve_value(f, seed),
                    "value_from": str(f.get("value_from") or ""),
                    "delay_ms": int(f.get("delay_ms") or 300),
                    "input_mode": str(f.get("input_mode") or ""),
                    "input_target": str(f.get("input_target") or ""),
                    "focus_test_id": str(f.get("focus_test_id") or ""),
                    "expected_length": int(f["expected_length"])
                    if f.get("expected_length") is not None
                    else None,
                }
            )
        view_gate = _view_gate_payload(step)
        ec = step.get("exit_condition") if isinstance(step.get("exit_condition"), dict) else {}
        runtime_steps.append(
            {
                "step_id": step.get("step_id"),
                "order": step.get("order"),
                "view": step.get("view"),
                "view_testid": step.get("view_testid") or "",
                "view_gate": view_gate,
                "action": str(step.get("action") or "navigate").lower(),
                "fields": fields_out,
                "delay_ms_after": int(step.get("delay_ms_after") or 1000),
                "exit_condition": {
                    "type": str(ec.get("type") or ""),
                    "test_id": str(ec.get("test_id") or ""),
                    "test_ids": [str(t) for t in (ec.get("test_ids") or []) if str(t).strip()],
                },
                "exit_selectors": _exit_selectors(step, compact=True),
                "hooks": [
                    str(h).strip().lower()
                    for h in (step.get("hooks") or [])
                    if str(h).strip().lower()
                    in ("dismiss_expo", "force_reload", "grant_os_perms", "stabilize")
                ],
                "optional": bool(step.get("optional")),
                "assert_text": str(step.get("assert_text") or "").strip(),
                "note": step.get("note") or "",
            }
        )

    launch_cfg = dev.get("launch") if isinstance(dev.get("launch"), dict) else {}
    appium_cfg = dev.get("appium") if isinstance(dev.get("appium"), dict) else {}
    payload = {
        "task_id": task_id,
        "scenario_id": scenario_id,
        "app": str(dev.get("app") or app_id),
        "serial": str(dev.get("serial") or s["emulator"]),
        "bundle_id": str(dev.get("bundle_id") or s["bundle_id"]),
        "activity": str(dev.get("activity_full") or dev.get("activity") or s["activity"]),
        "metro_port": int(dev.get("metro_port") or s["metro_port"]),
        "metro_url": str(dev.get("metro_url") or ""),
        "dev_client_url": str(dev.get("dev_client_url") or ""),
        "deep_link_candidates": list(dev.get("deep_link_candidates") or []),
        "adb_reverse_ports": list(dev.get("adb_reverse_ports") or []),
        "appium_host": str(appium_cfg.get("host") or "127.0.0.1"),
        "appium_port": int(appium_cfg.get("port") or 4723),
        "launch": {
            "mode": str(launch_cfg.get("mode") or "dev_client"),
            "require_metro": bool(launch_cfg.get("require_metro", True)),
            "hard_stop": bool(launch_cfg.get("hard_stop", False)),
            "pm_clear_before_launch": bool(launch_cfg.get("pm_clear_before_launch", False)),
            "dismiss_expo_overlay": bool(launch_cfg.get("dismiss_expo_overlay", True)),
            "use_dev_client_url": bool(launch_cfg.get("use_dev_client_url", True)),
            "grant_os_permissions": bool(launch_cfg.get("grant_os_permissions", True)),
            "dismiss_os_permission_dialogs": bool(
                launch_cfg.get("dismiss_os_permission_dialogs", True)
            ),
            "reload_after_set_clock": bool(launch_cfg.get("reload_after_set_clock", True)),
            "stabilize_between_steps": bool(launch_cfg.get("stabilize_between_steps", True)),
            "exit_test_id": str(launch_cfg.get("exit_test_id") or ""),
            "exit_locator": str(launch_cfg.get("exit_locator") or ""),
            "exit_test_ids": list(launch_cfg.get("exit_test_ids") or []),
            "exit_locators": list(launch_cfg.get("exit_locators") or []),
        },
        "video_record": video,
        "screenshot": screenshot,
        "evidence_dir": str(evidence_dir),
        "description": pipeline.get("description") or "",
        "steps": runtime_steps,
    }
    embedded = json.dumps(payload, ensure_ascii=False, indent=2)

    return f'''#!/usr/bin/env node
/**
 * Auto-generated by qa_generate_evidence — NÃO editar à mão.
 * task={task_id} scenario={scenario_id}
 * Locators: testID only.
 */
import {{ mkdir, writeFile }} from 'node:fs/promises';
import path from 'node:path';
import {{ setTimeout as sleep }} from 'node:timers/promises';
import {{
  activateApp,
  createDriver,
  forceStop,
}} from '../_shared/driver.mjs';
import {{ adb, adbOk }} from '../_shared/adb.mjs';
import {{
  dismissPermissionControllerAdb,
  grantChildPermissionsAdb,
}} from '../_shared/child-permissions.mjs';
import {{ dismissExpoDevOverlay, dismissExpoDevOverlayAdb }} from '../_shared/expo-overlay.mjs';
import {{ startFlowVideo, stopFlowVideo }} from '../_shared/evidence.mjs';
import {{ assertMetroReady }} from '../_shared/metro.mjs';
import {{ findVisible, tapCenter, waitEditTexts, waitVisible }} from '../_shared/ui.mjs';

const PIPE = {embedded};

/** View atualmente confirmada — evita re-scan da mesma tela. */
let READY_VIEW = '';

function log(...args) {{
  console.log('[runtime-pipeline]', ...args);
}}

async function delay(ms) {{
  if (ms > 0) await sleep(ms);
}}

function sels(field) {{
  const list = Array.isArray(field?.selectors) && field.selectors.length
    ? field.selectors
    : (field?.selector ? [field.selector] : []);
  return list;
}}

function selsWithFallback(field) {{
  const primary = sels(field);
  const fb = Array.isArray(field?.selectors_fallback) ? field.selectors_fallback : [];
  return primary.concat(fb.filter((s) => s && !primary.includes(s)));
}}

function stepHooks(step) {{
  return Array.isArray(step?.hooks) ? step.hooks : [];
}}

function stepWants(step, name) {{
  return stepHooks(step).includes(name);
}}

function invalidateViewGate(reason) {{
  if (READY_VIEW) log('view_gate invalidate', READY_VIEW, reason || '');
  READY_VIEW = '';
}}

async function runDismissExpo(driver, serial) {{
  await dismissExpoDevOverlayAdb(serial).catch(() => undefined);
  if (driver) await dismissExpoDevOverlay(driver, serial).catch(() => undefined);
}}

/** Grants OS perms (child: location/notif; parent: notifications) — genérico. */
async function grantOsPermissions(serial, appPackage, appLabel) {{
  if (String(appLabel || PIPE.app) === 'parent') {{
    await adbOk(serial, 'shell', 'pm', 'grant', appPackage, 'android.permission.POST_NOTIFICATIONS').catch(() => undefined);
    log('grant_os_perms parent notifications');
    return;
  }}
  const result = await grantChildPermissionsAdb(serial, appPackage).catch((e) => {{
    log('grant_os_perms fail', String(e?.message || e));
    return null;
  }});
  log('grant_os_perms child', result || 'done');
}}

/** Estabiliza UI: diálogos SO + overlay Expo opcional. */
async function stabilizeUi(driver, serial, {{ dismissExpo = false }} = {{}}) {{
  if (PIPE.launch?.dismiss_os_permission_dialogs !== false) {{
    for (let i = 0; i < 3; i += 1) {{
      const hit = await dismissPermissionControllerAdb(serial).catch(() => false);
      if (!hit) break;
      await delay(250);
    }}
  }}
  if (dismissExpo) await runDismissExpo(driver, serial);
}}

async function forceReloadApp(driver, serial, appPackage, appActivity, label) {{
  log('force_reload');
  invalidateViewGate('force_reload');
  await forceStop(serial, appPackage).catch(() => undefined);
  await delay(900);
  await openDevClient(serial, appPackage, appActivity, label);
  await delay(1200);
  await runDismissExpo(driver, serial);
}}

/**
 * Gatilho por view: só depois que a view raiz está visível o script escaneia fields.
 * Reusa READY_VIEW para não re-pollar a mesma tela.
 */
async function awaitViewGate(driver, step, serial, {{ soft = false }} = {{}}) {{
  const gate = step.view_gate;
  const tid = String(gate?.test_id || step.view_testid || '').trim();
  if (!tid || gate?.required === false) return true;

  const selectors = Array.isArray(gate?.selectors) && gate.selectors.length
    ? gate.selectors
    : testIdSelectors(tid).slice(0, 2);

  if (READY_VIEW === tid) {{
    const quick = await findVisible(driver, selectors);
    if (quick) return true;
    invalidateViewGate('stale');
  }}

  log('view_gate wait', tid, step.step_id);
  const timeoutMs = Number(gate?.timeout_ms || 25_000);
  const deadline = Date.now() + timeoutMs;
  let tick = 0;
  while (Date.now() < deadline) {{
    tick += 1;
    // stabilize só a cada 3 polls — evita loop adb/Appium pesado
    if (tick === 1 || tick % 3 === 0) {{
      await stabilizeUi(driver, serial, {{ dismissExpo: stepWants(step, 'dismiss_expo') }});
    }}
    const el = await findVisible(driver, selectors);
    if (el) {{
      READY_VIEW = tid;
      log('view_gate ready', tid);
      await delay(200);
      return true;
    }}
    await delay(400);
  }}

  const msg = `view_gate timeout view=${{tid}} step=${{step.step_id}}`;
  if (soft || step.optional) {{
    log(msg, '(optional)');
    return false;
  }}
  throw new Error(msg);
}}

async function findFieldElement(driver, field, timeoutMs = 8_000) {{
  const primary = sels(field);
  let el = await waitVisible(driver, primary, timeoutMs, field.name || field.test_id || 'field');
  if (el) return el;
  const fb = Array.isArray(field.selectors_fallback) ? field.selectors_fallback : [];
  if (fb.length) {{
    el = await waitVisible(driver, fb, Math.min(timeoutMs, 5_000), field.name || 'field-fallback');
  }}
  return el;
}}

function wantsEditTextInput(field) {{
  const target = String(field.input_target || '').toLowerCase();
  if (target === 'android_edit_text' || target === 'edit_text') return true;
  const name = String(field.name || '').toLowerCase();
  const vf = String(field.value_from || '').toLowerCase();
  return name === 'pairing_code' || vf === 'seed.pairing_code';
}}

/** Foca Pressable/testID e digita no EditText real (PairingCodeInput oculto). */
async function findEditableTextInput(driver, field, timeoutMs = 10_000) {{
  const focusTid = String(field.focus_test_id || field.test_id || '').trim();
  if (focusTid) {{
    const focusEl = await waitVisible(
      driver,
      compactTestIdSelectors(focusTid),
      Math.min(timeoutMs, 8_000),
      `focus:${{focusTid}}`,
    );
    if (focusEl) {{
      await focusEl.click().catch(() => undefined);
      await delay(120);
    }}
  }}
  const edits = await waitEditTexts(driver, 1, timeoutMs);
  if (!edits.length) {{
    throw new Error(`EditText não encontrado para ${{field.name || field.test_id}}`);
  }}
  return edits[0];
}}

async function runFill(driver, field) {{
  const rawVal = String(field.value ?? '');
  const isPairing = wantsEditTextInput(field);
  const val = isPairing ? rawVal.replace(/\\D/g, '') : rawVal;
  if (val.includes('{{{{') && val.includes('}}}}')) {{
    throw new Error(`seed placeholder não resolvido: ${{val}}`);
  }}
  if (!val && String(field.value_from || '').startsWith('seed.')) {{
    throw new Error(`seed vazio para ${{field.value_from || field.name}}`);
  }}
  const expected = Number(field.expected_length || 0);
  if (expected > 0 && val.length !== expected) {{
    throw new Error(`pairing code length=${{val.length}} esperado=${{expected}} value=${{val}}`);
  }}

  let el;
  if (isPairing) {{
    el = await findEditableTextInput(driver, field, 12_000);
  }} else {{
    el = await findFieldElement(driver, field, 8_000);
  }}
  if (!el) throw new Error(`field not found: ${{field.name}} testID=${{field.test_id}}`);

  if (val) {{
    await el.click().catch(() => undefined);
    await el.clearValue?.().catch(() => undefined);
    await delay(80);
    if (field.input_mode === 'addValue_per_char' || isPairing) {{
      for (const ch of val) {{
        await el.addValue(ch);
        await delay(Number(field.delay_ms) || 60);
      }}
      log('fill ok', field.name || field.test_id, `len=${{val.length}} via=${{isPairing ? 'EditText' : 'testID'}}`);
      await delay(Number(field.delay_ms) || 300);
      return;
    }}
    await el.setValue(val);
  }}
  await delay(Number(field.delay_ms) || 300);
}}

async function runTap(driver, field) {{
  const el = await findFieldElement(driver, field, 8_000);
  if (!el) throw new Error(`tap target not found: ${{field.name}} testID=${{field.test_id}}`);
  await tapCenter(driver, el);
  await delay(Number(field.delay_ms) || 200);
}}

/**
 * Espera exit_condition (próxima view / âncora).
 * Poll enxuto: seletores compactos + stabilize intercalado.
 */
async function waitExit(driver, step, serial, {{ soft = false }} = {{}}) {{
  const list = Array.isArray(step.exit_selectors) ? step.exit_selectors : [];
  const dismiss = stepWants(step, 'dismiss_expo');
  if (!list.length) {{
    if (dismiss) await runDismissExpo(driver, serial);
    return true;
  }}
  const deadline = Date.now() + 25_000;
  let tick = 0;
  while (Date.now() < deadline) {{
    tick += 1;
    if (dismiss && (tick === 1 || tick % 3 === 0)) {{
      await stabilizeUi(driver, serial, {{ dismissExpo: true }});
    }}
    const el = await findVisible(driver, list);
    if (el) {{
      // Se exit aponta para um único test_id de view, marca como ready
      const ec = step.exit_condition || {{}};
      const nextTid = String(ec.test_id || (Array.isArray(ec.test_ids) && ec.test_ids.length === 1 ? ec.test_ids[0] : '') || '').trim();
      if (nextTid) READY_VIEW = nextTid;
      return true;
    }}
    await delay(400);
  }}
  const msg = `exit_condition timeout step=${{step.step_id}} testID=${{step.view_testid || '?'}}`;
  if (soft || step.optional) {{
    log(msg, '(optional — skip)');
    return false;
  }}
  throw new Error(msg);
}}

async function stepTargetsVisible(driver, step) {{
  const fields = step.fields || [];
  for (const field of fields) {{
    const list = sels(field);
    if (!list.length) continue;
    const el = await findVisible(driver, list);
    if (el) return true;
  }}
  if (step.view_testid) {{
    const anchors = [
      `android=new UiSelector().resourceId("${{step.view_testid}}")`,
      `~${{step.view_testid}}`,
      `android=new UiSelector().description("${{step.view_testid}}")`,
    ];
    if (await findVisible(driver, anchors)) return true;
  }}
  return false;
}}

/** Settle + view_gate antes de skip optional (sem loop de field search cego). */
async function optionalShouldSkip(driver, step) {{
  if (!step.optional) return false;
  if (step.view_gate || step.view_testid) {{
    const gateOk = await awaitViewGate(driver, step, serialRef(), {{ soft: true }});
    if (!gateOk) return true;
    await delay(250);
    if (await stepTargetsVisible(driver, step)) return false;
    await delay(400);
    return !(await stepTargetsVisible(driver, step));
  }}
  await delay(400);
  await stabilizeUi(driver, serialRef());
  for (let i = 0; i < 3; i += 1) {{
    if (await stepTargetsVisible(driver, step)) return false;
    await delay(350);
  }}
  return true;
}}

function serialRef() {{
  return PIPE.serial;
}}

function testIdSelectors(tid) {{
  const t = String(tid || '').trim();
  if (!t) return [];
  const esc = t.replace(/"/g, '\\\\"');
  // compact: 2 strategies — mesmo padrão do view_gate
  return [
    `android=new UiSelector().resourceIdMatches(".*${{t}}$")`,
    `~${{t}}`,
    `android=new UiSelector().resourceId("${{esc}}")`,
    `android=new UiSelector().description("${{esc}}")`,
  ];
}}

function compactTestIdSelectors(tid) {{
  return testIdSelectors(tid).slice(0, 2);
}}

async function elementTextBlob(el) {{
  const parts = [];
  for (const getter of [
    () => el.getText(),
    () => el.getAttribute('contentDescription'),
    () => el.getAttribute('text'),
    () => el.getAttribute('content-desc'),
  ]) {{
    try {{
      const v = await getter();
      if (v) parts.push(String(v));
    }} catch {{
      /* ignore */
    }}
  }}
  return parts.join(' | ');
}}

async function assertElementText(el, want, label) {{
  const needle = String(want || '').trim();
  if (!needle) return;
  const blob = await elementTextBlob(el);
  if (!blob.includes(needle)) {{
    throw new Error(`assert_text failed ${{label || ''}} want="${{needle}}" got="${{blob}}"`);
  }}
}}

/** Se pós-reload voltou ao PrePairing, reexecuta fill+submit (+permissions) do pipeline. */
async function rePairIfNeeded(driver, serial, appPackage, appActivity) {{
  const homeHit = await findVisible(driver, [
    ...compactTestIdSelectors('greeting-title'),
    ...compactTestIdSelectors('child-home-v2'),
    ...compactTestIdSelectors('parent-home'),
    ...compactTestIdSelectors('auth-screen'),
  ]);
  if (homeHit) {{
    log('re_pair: already on home/auth — skip');
    return false;
  }}
  const preHit = await findVisible(driver, [
    ...compactTestIdSelectors('pre-pairing-screen'),
    ...compactTestIdSelectors('pairing-code-input'),
  ]);
  if (!preHit) {{
    log('re_pair: not on pre-pairing — skip');
    return false;
  }}
  log('re_pair: PrePairing após reload — reexecutando fill/submit/permissions');
  invalidateViewGate('re_pair');
  const actions = ['fill', 'tap'];
  for (const step of PIPE.steps || []) {{
    const action = String(step.action || '').toLowerCase();
    if (!actions.includes(action)) continue;
    if (!(step.fields || []).length) continue;
    const sid = String(step.step_id || '');
    if (!(
      sid.includes('fill') ||
      sid.includes('submit') ||
      sid.includes('permissions') ||
      sid.includes('login')
    )) continue;
    try {{
      await awaitViewGate(driver, step, serial, {{ soft: true }});
      if (action === 'fill') {{
        for (const field of step.fields || []) await runFill(driver, field);
      }} else {{
        const visible = await stepTargetsVisible(driver, step);
        if (!visible) {{
          log('re_pair skip', sid, 'target ausente');
          continue;
        }}
        for (const field of step.fields || []) await runTap(driver, field);
      }}
      await delay(step.delay_ms_after || 800);
      await waitExit(driver, step, serial, {{ soft: true }});
    }} catch (e) {{
      log('re_pair step fail', sid, String(e?.message || e));
    }}
  }}
  await stabilizeUi(driver, serial, {{ dismissExpo: true }});
  return true;
}}

async function setClock(serial, hhmm) {{
  const m = String(hhmm || '').match(/^(\\d{{1,2}}):(\\d{{2}})$/);
  if (!m) return;
  const hh = m[1].padStart(2, '0');
  const mm = m[2];
  await adb(serial, 'shell', 'settings', 'put', 'global', 'auto_time', '0').catch(() => undefined);
  await adb(serial, 'shell', 'settings', 'put', 'global', 'auto_time_zone', '0').catch(() => undefined);
  let ok = false;
  await adb(serial, 'shell', 'su', '0', 'date', `${{hh}}${{mm}}`).then(() => {{ ok = true; }}).catch(() => undefined);
  if (!ok) {{
    await adb(serial, 'shell', 'date', `${{hh}}${{mm}}00`).then(() => {{ ok = true; }}).catch(() => undefined);
  }}
  if (!ok) {{
    const now = new Date();
    now.setHours(Number(hh), Number(mm), 0, 0);
    const epoch = Math.floor(now.getTime() / 1000);
    await adb(serial, 'shell', 'su', '0', 'date', '@' + String(epoch)).catch(() => undefined);
  }}
  log('set_clock', `${{hh}}:${{mm}}`);
}}

async function capturePng(driver, outDir, name) {{
  await mkdir(outDir, {{ recursive: true }});
  const png = path.join(outDir, `${{name}}.png`);
  await driver.saveScreenshot(png);
  return png;
}}

async function openDevClient(serial, appPackage, appActivity, label) {{
  const urls = [];
  if (PIPE.launch?.use_dev_client_url && PIPE.dev_client_url) urls.push(PIPE.dev_client_url);
  for (const u of (PIPE.deep_link_candidates || [])) {{
    if (u && !urls.includes(u)) urls.push(u);
  }}
  for (const url of urls) {{
    try {{
      await adb(serial, 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', url);
      log('dev_client_url', url);
      return;
    }} catch (e) {{
      log('dev_client_url fail', url, String(e?.message || e));
    }}
  }}
  await activateApp({{ serial, appPackage, appActivity, label }});
}}

async function applyStepHooksBefore(driver, step, serial, appPackage, appActivity) {{
  if (stepWants(step, 'grant_os_perms') || PIPE.launch?.grant_os_permissions) {{
    await grantOsPermissions(serial, appPackage, PIPE.app);
  }}
  await stabilizeUi(driver, serial, {{ dismissExpo: stepWants(step, 'dismiss_expo') }});
}}

async function main() {{
  const host = process.env.APPIUM_HOST || PIPE.appium_host || '127.0.0.1';
  const port = Number(process.env.APPIUM_PORT || PIPE.appium_port || 4723);
  const serial = PIPE.serial;
  const appPackage = PIPE.bundle_id;
  const outDir = PIPE.evidence_dir;
  await mkdir(outDir, {{ recursive: true }});

  let driver = null;
  const timeline = [];
  const artifacts = {{ screenshots: [], video: null, script_meta: path.join(outDir, 'runtime-pipeline.json') }};
  await writeFile(artifacts.script_meta, JSON.stringify(PIPE, null, 2), 'utf8');

  try {{
    if (PIPE.launch?.require_metro && PIPE.metro_port) {{
      await assertMetroReady(Number(PIPE.metro_port));
    }}
    for (const p of (PIPE.adb_reverse_ports || [])) {{
      await adb(serial, 'reverse', `tcp:${{p}}`, `tcp:${{p}}`).catch(() => undefined);
    }}
    if (PIPE.launch?.pm_clear_before_launch) {{
      log('pm clear', appPackage);
      await adb(serial, 'shell', 'pm', 'clear', appPackage).catch(() => undefined);
      await delay(1500);
    }} else if (PIPE.launch?.hard_stop) {{
      await forceStop(serial, appPackage).catch(() => undefined);
    }}
    if (PIPE.launch?.grant_os_permissions !== false) {{
      await grantOsPermissions(serial, appPackage, PIPE.app);
    }}
    driver = await createDriver({{
      serial,
      appPackage,
      appActivity: PIPE.activity,
      host,
      port,
    }});

    if (PIPE.video_record) {{
      process.env.GF_APPIUM_FLOW_VIDEO = '1';
      await startFlowVideo(driver);
    }}

    for (const step of PIPE.steps) {{
      const action = String(step.action || 'navigate').toLowerCase();
      log(`step ${{step.order}} ${{step.step_id}} action=${{action}} view=${{step.view || '-'}} gate=${{step.view_testid || '-'}} hooks=${{(step.hooks || []).join(',') || '-'}} optional=${{!!step.optional}}`);
      timeline.push({{ step_id: step.step_id, action, view_testid: step.view_testid, view_gate: step.view_gate || null, hooks: step.hooks || [], optional: !!step.optional, at: new Date().toISOString() }});

      if (action === 'launch' || (action === 'navigate' && Number(step.order) === 1)) {{
        invalidateViewGate('launch');
        await applyStepHooksBefore(driver, step, serial, appPackage, PIPE.activity);
        if (stepWants(step, 'dismiss_expo')) {{
          await runDismissExpo(driver, serial);
          await runDismissExpo(driver, serial);
        }}
        await openDevClient(serial, appPackage, PIPE.activity, PIPE.app);
        await delay(step.delay_ms_after || 1000);
        await waitExit(driver, step, serial);
        continue;
      }}

      if (await optionalShouldSkip(driver, step)) {{
        log(`skip optional step ${{step.step_id}} — view/target ausente após settle`);
        timeline[timeline.length - 1].skipped = true;
        continue;
      }}

      if (action === 'fill') {{
        await applyStepHooksBefore(driver, step, serial, appPackage, PIPE.activity);
        if (!(await awaitViewGate(driver, step, serial, {{ soft: !!step.optional }}))) {{
          if (step.optional) continue;
          throw new Error(`view_gate required for ${{step.step_id}}`);
        }}
        try {{
          for (const field of step.fields || []) await runFill(driver, field);
        }} catch (e) {{
          if (step.optional) {{ log(`skip optional fill ${{step.step_id}}`, String(e?.message || e)); continue; }}
          throw e;
        }}
        await delay(step.delay_ms_after || 800);
        await waitExit(driver, step, serial, {{ soft: !!step.optional }});
        continue;
      }}

      if (action === 'tap') {{
        await applyStepHooksBefore(driver, step, serial, appPackage, PIPE.activity);
        if (!(await awaitViewGate(driver, step, serial, {{ soft: !!step.optional }}))) {{
          if (step.optional) continue;
          throw new Error(`view_gate required for ${{step.step_id}}`);
        }}
        try {{
          for (const field of step.fields || []) await runTap(driver, field);
        }} catch (e) {{
          if (step.optional) {{ log(`skip optional tap ${{step.step_id}}`, String(e?.message || e)); continue; }}
          throw e;
        }}
        await delay(step.delay_ms_after || 800);
        await waitExit(driver, step, serial, {{ soft: !!step.optional }});
        continue;
      }}

      if (action === 'set_clock') {{
        const clockField = (step.fields || [])[0] || {{}};
        await setClock(serial, clockField.value || '08:00');
        const doReload =
          stepWants(step, 'force_reload') || PIPE.launch?.reload_after_set_clock !== false;
        if (stepWants(step, 'grant_os_perms') || PIPE.launch?.grant_os_permissions !== false) {{
          await grantOsPermissions(serial, appPackage, PIPE.app);
        }}
        if (doReload) {{
          await forceReloadApp(driver, serial, appPackage, PIPE.activity, PIPE.app);
          await rePairIfNeeded(driver, serial, appPackage, PIPE.activity);
        }} else {{
          if (stepWants(step, 'dismiss_expo')) await runDismissExpo(driver, serial);
          await openDevClient(serial, appPackage, PIPE.activity, PIPE.app);
        }}
        await delay(step.delay_ms_after || 800);
        await waitExit(driver, step, serial);
        continue;
      }}

      if (action === 'wait' || action === 'navigate') {{
        await applyStepHooksBefore(driver, step, serial, appPackage, PIPE.activity);
        await awaitViewGate(driver, step, serial);
        await waitExit(driver, step, serial);
        await delay(step.delay_ms_after || 1000);
        continue;
      }}

      if (action === 'capture') {{
        await awaitViewGate(driver, step, serial);
        await stabilizeUi(driver, serial);
        const assertField = (step.fields || [])[0];
        if (assertField) {{
          const el = await findFieldElement(driver, assertField, 12_000);
          if (!el) throw new Error(`capture assert failed testID=${{assertField.test_id}}`);
          await assertElementText(el, step.assert_text, assertField.test_id || 'capture');
        }}
        if (PIPE.screenshot) {{
          const name = `capture_${{PIPE.scenario_id || step.step_id}}`.replace(/[^a-zA-Z0-9._-]+/g, '_');
          const png = await capturePng(driver, outDir, name);
          artifacts.screenshots.push(png);
          log('CAPTURE_OK', png);
        }}
        await delay(step.delay_ms_after || 500);
        continue;
      }}

      log(`ação desconhecida: ${{action}} — ignorada`);
      await delay(step.delay_ms_after || 500);
    }}

    if (PIPE.video_record && driver) {{
      const mp4 = await stopFlowVideo(driver, {{ featureId: PIPE.scenario_id || 'pipeline' }});
      if (mp4) artifacts.video = mp4;
    }}

    const result = {{
      ok: true,
      task_id: PIPE.task_id,
      scenario_id: PIPE.scenario_id,
      artifacts,
      timeline,
      evidence_dir: outDir,
    }};
    await writeFile(path.join(outDir, 'runtime-result.json'), JSON.stringify(result, null, 2), 'utf8');
    console.log(JSON.stringify(result));
    process.exitCode = 0;
  }} catch (err) {{
    const msg = err instanceof Error ? err.message : String(err);
    const fail = {{
      ok: false,
      error: msg,
      task_id: PIPE.task_id,
      scenario_id: PIPE.scenario_id,
      timeline,
      artifacts,
    }};
    try {{
      if (driver && PIPE.screenshot) {{
        const png = await capturePng(driver, outDir, 'capture_FAIL');
        artifacts.screenshots.push(png);
      }}
      if (PIPE.video_record && driver) {{
        const mp4 = await stopFlowVideo(driver, {{ featureId: 'fail' }});
        if (mp4) artifacts.video = mp4;
      }}
    }} catch {{ /* ignore */ }}
    await writeFile(path.join(outDir, 'runtime-result.json'), JSON.stringify(fail, null, 2), 'utf8').catch(() => undefined);
    console.log(JSON.stringify(fail));
    process.exitCode = 1;
  }} finally {{
    if (driver) {{
      try {{ await driver.deleteSession(); }} catch {{ /* ignore */ }}
    }}
  }}
}}

await main();
'''


def write_runtime_script(
    *,
    pipeline: dict[str, Any],
    task_id: str,
    scenario_id: str,
    app: str,
    evidence_dir: Path | None = None,
    device: dict[str, Any] | None = None,
    seed_values: dict[str, str] | None = None,
) -> dict[str, Any]:
    root = appium_root()
    runtime_dir = root / "_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    cycle = resolve_agent_cycle(None, "qa-gate")
    out_dir = evidence_dir or qa_evidence_dir(task_id, cycle=cycle)
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = _now_stamp()
    safe_sid = re.sub(r"[^a-zA-Z0-9._-]+", "_", scenario_id or "scenario")
    script_path = runtime_dir / f"gen_{task_id}_{safe_sid}_{stamp}.mjs"
    source = build_appium_script_source(
        pipeline=pipeline,
        task_id=task_id,
        scenario_id=scenario_id,
        app=app,
        evidence_dir=out_dir,
        device=device,
        seed_values=seed_values,
    )
    script_path.write_text(source, encoding="utf-8")
    (out_dir / "generated-appium-script.mjs").write_text(source, encoding="utf-8")
    return {
        "ok": True,
        "script_path": str(script_path),
        "evidence_dir": str(out_dir),
        "source_bytes": len(source.encode("utf-8")),
    }


def run_runtime_script(
    script_path: str | Path,
    *,
    timeout_sec: int = 900,
    video_record: bool = False,
    evidence_dir: str = "",
) -> dict[str, Any]:
    root = appium_root()
    script = Path(script_path)
    if not script.is_file():
        return {"ok": False, "error": f"script ausente: {script}"}

    from lib.mobile.local_e2e import resolve_android_home

    env = {
        **os.environ,
        "GF_APPIUM_EVIDENCE_DIR": evidence_dir or str(Path(script).parent),
    }
    android_home = resolve_android_home()
    if android_home:
        env["ANDROID_HOME"] = str(android_home)
        env["ANDROID_SDK_ROOT"] = str(android_home)
        platform_tools = android_home / "platform-tools"
        path_prefix = str(platform_tools)
        cur_path = env.get("PATH") or env.get("Path") or ""
        if path_prefix and path_prefix not in cur_path:
            env["PATH"] = path_prefix + os.pathsep + cur_path
            env["Path"] = env["PATH"]
    if video_record:
        env["GF_APPIUM_FLOW_VIDEO"] = "1"
        env.setdefault("GF_APPIUM_FLOW_VIDEO_SEC", "600")

    proc = subprocess.run(
        ["node", str(script)],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_sec,
    )
    stdout = (proc.stdout or "") + (proc.stderr or "")
    payload: dict[str, Any] | None = None
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and '"ok"' in line:
            try:
                payload = json.loads(line)
                break
            except json.JSONDecodeError:
                continue

    ok = proc.returncode == 0
    if isinstance(payload, dict) and "ok" in payload:
        ok = bool(payload.get("ok"))

    return {
        "ok": ok,
        "engine": "runtime-generated-appium",
        "script_path": str(script),
        "returncode": proc.returncode,
        "result": payload or {},
        "stdout_tail": stdout[-5000:],
        "setup_root": str(setup_root()),
    }


def generate_and_run_from_pipeline(
    *,
    pipeline: dict[str, Any],
    task_id: str,
    scenario_id: str,
    app: str = "child",
    timeout_sec: int = 900,
    dry_run: bool = False,
    device: dict[str, Any] | None = None,
    seed_values: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Gera script Appium em runtime a partir do pipeline e executa."""
    written = write_runtime_script(
        pipeline=pipeline,
        task_id=task_id,
        scenario_id=scenario_id,
        app=app,
        device=device,
        seed_values=seed_values,
    )
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "generated": written,
            "would_execute": written.get("script_path"),
        }
    executed = run_runtime_script(
        written["script_path"],
        timeout_sec=timeout_sec,
        video_record=bool(pipeline.get("video_record")),
        evidence_dir=str(written.get("evidence_dir") or ""),
    )
    return {
        "ok": bool(executed.get("ok")),
        "generated": written,
        "execution": executed,
        "package_dir": written.get("evidence_dir"),
        "suite_ok": bool(executed.get("ok")),
        "evidence_ok": bool(executed.get("ok"))
        and (
            not pipeline.get("screenshot")
            or bool((executed.get("result") or {}).get("artifacts", {}).get("screenshots"))
            or bool(list(Path(str(written.get("evidence_dir") or ".")).glob("*.png")))
        ),
        "appium_ran": True,
        "blocking_reason": None
        if executed.get("ok")
        else (executed.get("result") or {}).get("error") or "RUNTIME_APPIUM_FAIL",
    }
