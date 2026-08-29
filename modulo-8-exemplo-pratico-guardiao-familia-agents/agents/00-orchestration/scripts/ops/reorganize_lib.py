#!/usr/bin/env python3
"""Reorganiza lib/ em subpacotes por domínio + shims de compatibilidade."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import shutil
import textwrap
from pathlib import Path

from lib.paths import MODULE_ROOT as ROOT  # noqa: E402
# ROOT
LIB = MODULE_ROOT / "lib"

# Raiz lib: apenas bootstrap
KEEP_AT_ROOT = {"paths.py", "env_load.py", "__init__.py", "README.md"}

# pacote -> módulos (sem .py)
LAYOUT: dict[str, list[str]] = {
    "core": [
        "repo_paths",
        "agent_paths",
        "agent_registry",
        "dependencies",
        "openrouter_client",
        "model_tier",
        "react_policy",
    ],
    "board": [
        "local_board",
        "board_client",
        "task_router",
        "task_status_workflow",
        "task_action_history",
        "issue_task_body",
        "project_status_sync",
        "status_labels",
        "reviewer_pairs",
        "infra_policy",
    ],
    "gateway": [
        "gateway",
        "hitl_gates",
        "event_schema",
        "event_contract",
        "handoff",
    ],
    "orchestrator": [
        "event_orchestrator",
        "claim_lock",
        "outbox",
        "worker_jobs",
        "dispatch_adapter",
        "complete_dispatch",
        "pilot",
    ],
    "observability": ["observability"],
    "ci": ["ci_signals", "ci_state"],
    "mobile": [
        "mobile_runtime_config",
        "mobile_build_paths",
        "mobile_setup_client",
        "mobile_flow_discovery",
        "mobile_flow_rag",
        "mobile_user_flow_db",
        "mobile_evidence_guide",
        "mobile_golden_flow",
        "mobile_work",
        "mobile_e2e_seed",
        "local_e2e",
        "qa_mobile",
        "qa_mobile_setup_evidence",
        "qa_mobile_mcp",
        "qa_playwright",
    ],
    "site": ["site_hero_work"],
}

EXTRA_ASSETS: dict[str, list[str]] = {
    "observability": ["dashboard_live.html"],
}

SHIM = '''\
"""Compat shim — preferir `lib.{pkg}.{mod}`."""
from lib.{pkg}.{mod} import *  # noqa: F403
'''

PKG_INIT = '''\
"""Pacote `{pkg}` — ver `lib/README.md`."""
'''


def _module_to_pkg(mod: str) -> str:
    for pkg, mods in LAYOUT.items():
        if mod in mods:
            return pkg
    return ""


def _build_import_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for pkg, mods in LAYOUT.items():
        for mod in mods:
            mapping[mod] = f"lib.{pkg}.{mod}"
    return mapping


def _rewrite_imports(text: str, imp_map: dict[str, str]) -> str:
    out = text
    # longest module names first (mobile_evidence_guide before mobile_)
    for mod in sorted(imp_map, key=len, reverse=True):
        new = imp_map[mod]
        for old in (f"from lib.{mod} import", f"import lib.{mod}"):
            new_line = old.replace(f"lib.{mod}", new)
            out = out.replace(old, new_line)
    return out


def main() -> int:
    imp_map = _build_import_map()
    moved: list[str] = []

    for pkg, mods in LAYOUT.items():
        pkg_dir = LIB / pkg
        pkg_dir.mkdir(parents=True, exist_ok=True)
        init = pkg_dir / "__init__.py"
        if not init.exists():
            init.write_text(PKG_INIT.format(pkg=pkg), encoding="utf-8")

        for mod in mods:
            src = LIB / f"{mod}.py"
            if not src.is_file():
                continue
            dest = pkg_dir / f"{mod}.py"
            if dest.is_file():
                continue
            content = _rewrite_imports(src.read_text(encoding="utf-8"), imp_map)
            dest.write_text(content, encoding="utf-8")
            src.unlink()
            moved.append(f"{mod}.py -> {pkg}/{mod}.py")

        for asset in EXTRA_ASSETS.get(pkg, []):
            src = LIB / asset
            if src.is_file():
                dest = pkg_dir / asset
                if not dest.exists():
                    shutil.move(str(src), str(dest))
                    moved.append(f"{asset} -> {pkg}/{asset}")

    # gateway package: reexport API principal no __init__
    gw_init = LIB / "gateway" / "__init__.py"
    if (LIB / "gateway" / "gateway.py").is_file():
        gw_init.write_text(
            textwrap.dedent(
                '''\
                """Gateway de status, handoff e eventos."""
                from lib.gateway.gateway import *  # noqa: F403
                from lib.gateway.handoff import load_handoff, write_handoff
                from lib.gateway.hitl_gates import *  # noqa: F403
                '''
            ),
            encoding="utf-8",
        )

    obs_init = LIB / "observability" / "__init__.py"
    if (LIB / "observability" / "observability.py").is_file():
        obs_init.write_text(
            '"""Observabilidade do fluxo de agentes."""\n'
            "from lib.observability.observability import *  # noqa: F403\n",
            encoding="utf-8",
        )

    # Remove root gateway.py shim if conflita — usamos pacote lib.gateway
    root_gw_shim = LIB / "gateway.py"
    if root_gw_shim.is_file() and (LIB / "gateway" / "gateway.py").is_file():
        root_gw_shim.unlink()

    root_obs_shim = LIB / "observability.py"
    if root_obs_shim.is_file() and (LIB / "observability" / "observability.py").is_file():
        root_obs_shim.unlink()

    print(f"Reorganize lib: {len(moved)} itens")
    for line in moved:
        print(f"  - {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
