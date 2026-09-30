"""Automatiza parent.welcome_onboarding_screen no emulador Android.

As acoes saem de rag-fluxo-parent.jsonl, na ordem de componentes.
O arquivo da tela esta em pre_requisitos.screen_file.
"""

from __future__ import annotations

import subprocess
import sys
import time

from commons.extrair_flow import extrair_flow
from commons.sessao_appium import SessaoAppium, criar_sessao
from commons.variaveis_parent import DEV_URL, PACKAGE, SERIAL

FLOW_ID = "parent.welcome_onboarding_screen"
LOGIN_VIEW_ID = "auth-screen"


def adb(*args: str) -> None:
    cmd = ["adb", "-s", SERIAL, *args]
    done = subprocess.run(cmd, capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"{' '.join(cmd)} falhou: {done.stderr.strip() or done.stdout.strip()}")


def open_parent() -> None:
    adb("shell", "pm", "clear", PACKAGE)
    adb(
        "shell",
        "am",
        "start",
        "-a",
        "android.intent.action.VIEW",
        "-d",
        DEV_URL,
    )


def executar_componente(driver: SessaoAppium, componente: dict) -> None:
    time.sleep(int(componente.get("intervalo_ms") or 0) / 1000)
    acao = componente.get("acao")
    test_id = componente["test_id"]
    element = driver.find(test_id, timeout_s=20)
    if acao == "tap":
        driver.click(element)
    elif acao == "fill":
        texto = componente.get("preenchimento")
        if not texto or str(texto).startswith("seed."):
            raise SystemExit(f"preenchimento ausente para {test_id}")
        driver.fill(element, str(texto))
    elif acao == "wait":
        return
    else:
        raise SystemExit(f"acao nao suportada em {test_id}: {acao}")
    print(f"ordem {componente['ordem']} {acao} {test_id}")


def main() -> None:
    flow = extrair_flow(FLOW_ID)
    print(flow["consulta"])
    print(f"resultado esperado: {LOGIN_VIEW_ID}")

    open_parent()
    driver = criar_sessao()
    for pre in sorted(flow["pre_requisitos"], key=lambda item: item["ordem"]):
        if pre.get("flow_id"):
            raise SystemExit(f"{FLOW_ID} nao deve depender de outro flow_id neste script")
        driver.find(pre["view_id"], timeout_s=45)
        print(f"tela aberta: {pre['view_id']} ({pre['screen_file']})")
        for componente in sorted(pre["componentes"], key=lambda item: item["ordem"]):
            executar_componente(driver, componente)
    driver.find(LOGIN_VIEW_ID, timeout_s=20)
    print(f"ok: {flow['resultado']}")
    print(f"sessao aberta: {driver.session}")
    print(f"app permanece em {PACKAGE}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
