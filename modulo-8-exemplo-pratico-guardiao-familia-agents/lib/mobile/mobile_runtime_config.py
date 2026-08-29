"""Stacks mobile isolados: parent e child sem emulador/Metro/scheme compartilhados."""

from __future__ import annotations

import os
from typing import Any

PARENT_METRO_PORT = int(os.environ.get("GF_PARENT_METRO_PORT", "8082"))
CHILD_METRO_PORT = int(os.environ.get("GF_CHILD_METRO_PORT", "9090"))

PARENT_EMULATOR = os.environ.get("GF_PARENT_EMULATOR_SERIAL", "emulator-5554").strip()
CHILD_EMULATOR = os.environ.get("GF_CHILD_EMULATOR_SERIAL", "emulator-5556").strip()

PARENT_AVD = os.environ.get("GF_PARENT_AVD", "Pixel_6_API34_Stable").strip()
CHILD_AVD = os.environ.get("GF_CHILD_AVD", "Pixel_6_API34_Child").strip()

# Host visto pelo emulador (cada AVD tem 10.0.2.2 próprio → host).
# Com adb reverse, 127.0.0.1 no emulador também alcança o Metro do host.
METRO_EMULATOR_HOST = os.environ.get("GF_METRO_EMULATOR_HOST", "10.0.2.2").strip()

APP_STACKS: dict[str, dict[str, Any]] = {
    "parent": {
        "app_id": "parent",
        "repo": "guardiao-familia-parent",
        "label": "Guardiao Pais",
        "bundle_id": "com.guardiaofamilia.parent",
        "activity": "com.guardiaofamilia.parent/.MainActivity",
        "metro_port": PARENT_METRO_PORT,
        "emulator": PARENT_EMULATOR,
        "avd": PARENT_AVD,
        "screens_dir": "screens",
        "app_tsx": "App.tsx",
        # Schemes exclusivos do parent (nunca expo-dev-launcher compartilhado).
        "deep_link_schemes": (
            "exp+guardiao-familia-parent",
            "guardiao-pai",
        ),
        "api_base_url": "http://10.0.2.2:3000/api/v1",
        "peer_metro_ports": (CHILD_METRO_PORT,),
    },
    "child": {
        "app_id": "child",
        "repo": "guardiao-familia-child",
        "label": "Guardião Filho",
        "bundle_id": "com.guardiofilho",
        "activity": "com.guardiofilho/.MainActivity",
        "metro_port": CHILD_METRO_PORT,
        "emulator": CHILD_EMULATOR,
        "avd": CHILD_AVD,
        "screens_dir": "screens",
        "app_tsx": "App.tsx",
        # Schemes exclusivos do child — NÃO usar expo-dev-launcher (compartilhado com parent).
        # guardiao-filho é injetado no AndroidManifest pelo install_mobile_dev_clients.ps1
        "deep_link_schemes": (
            "guardiao-filho",
            "exp+guardiao-familia-child",
            "guardiaofamilia",
        ),
        "api_base_url": "http://10.0.2.2:3000/api/v1",
        "peer_metro_ports": (PARENT_METRO_PORT,),
    },
}


def stack(app_id: str) -> dict[str, Any]:
    if app_id not in APP_STACKS:
        raise KeyError(f"app_id desconhecido: {app_id}")
    return APP_STACKS[app_id]


def app_config_compat() -> dict[str, dict[str, Any]]:
    """Formato legado APP_CONFIG usado por discovery/runtime."""
    out: dict[str, dict[str, Any]] = {}
    for app_id, s in APP_STACKS.items():
        out[app_id] = {
            "repo": s["repo"],
            "bundle_id": s["bundle_id"],
            "metro_port": s["metro_port"],
            "emulator": s["emulator"],
            "avd": s["avd"],
            "screens_dir": s["screens_dir"],
            "app_tsx": s["app_tsx"],
            "activity": s["activity"],
            "label": s["label"],
            "deep_link_schemes": s["deep_link_schemes"],
            "peer_metro_ports": s["peer_metro_ports"],
            "api_base_url": s["api_base_url"],
        }
    return out


def metro_url_for(app_id: str, *, host: str | None = None) -> str:
    s = stack(app_id)
    h = host or METRO_EMULATOR_HOST
    return f"http://{h}:{s['metro_port']}"


def deep_link_candidates(app_id: str, *, host: str | None = None) -> list[str]:
    """URLs de deep link só com schemes do próprio app (sem chooser compartilhado)."""
    manifest = metro_url_for(app_id, host=host)
    return [
        f"{scheme}://expo-development-client/?url={manifest}"
        for scheme in stack(app_id)["deep_link_schemes"]
    ]


def appium_env(*, dual_emulator: bool = True) -> dict[str, str]:
    """Env Appium com serials/packages/Metro isolados por app."""
    p = stack("parent")
    c = stack("child")
    parent_emu = p["emulator"]
    child_emu = c["emulator"] if dual_emulator else p["emulator"]
    parent_url = metro_url_for("parent")
    child_url = metro_url_for("child")
    return {
        "GF_PARENT_EMULATOR_SERIAL": parent_emu,
        "GF_CHILD_EMULATOR_SERIAL": child_emu,
        "GF_PARENT_APP_PACKAGE": p["bundle_id"],
        "GF_PARENT_APP_ACTIVITY": p["activity"].split("/")[-1],
        "GF_CHILD_APP_PACKAGE": c["bundle_id"],
        "GF_CHILD_APP_ACTIVITY": c["activity"].split("/")[-1],
        "GF_PARENT_METRO_PORT": str(p["metro_port"]),
        "GF_CHILD_METRO_PORT": str(c["metro_port"]),
        "GF_PARENT_DEV_CLIENT_URL": deep_link_candidates("parent")[0],
        "GF_CHILD_DEV_CLIENT_URL": deep_link_candidates("child")[0],
        "GF_PARENT_METRO_URL": parent_url,
        "GF_CHILD_METRO_URL": child_url,
    }


def metro_env_for(app_id: str) -> dict[str, str]:
    """Env Expo/Metro isolado — sem variáveis do peer."""
    s = stack(app_id)
    port = str(s["metro_port"])
    api = s["api_base_url"]
    # Hostname do packager = o que o *manifest* Expo embute. Com dual AVD,
    # 10.0.2.2 aponta para o host de cada emulador (portas distintas no host).
    host = METRO_EMULATOR_HOST
    base = {
        "CI": "1",
        "RCT_METRO_PORT": port,
        "EXPO_METRO_PORT": port,
        "REACT_NATIVE_PACKAGER_HOSTNAME": host,
        "EXPO_PUBLIC_API_BASE_URL": api,
        "EXPO_PUBLIC_API_BASE_URL_EMULATOR": api,
    }
    if app_id == "child":
        # Child em host machine às vezes usa localhost; emulador usa 10.0.2.2.
        base["EXPO_PUBLIC_API_BASE_URL"] = "http://localhost:3000/api/v1"
    return base
