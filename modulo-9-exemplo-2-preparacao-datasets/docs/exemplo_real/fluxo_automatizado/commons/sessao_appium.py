"""Cria e encerra a sessao Appium compartilhada entre os fluxos.

O id fica em sessao_appium.json. criar_sessao reaproveita o arquivo
se a sessao ainda responde. encerrar_sessao apaga a sessao e o arquivo.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

try:
    from .variaveis_parent import ACTIVITY, APPIUM_URL, PACKAGE, SERIAL, SESSAO_PATH
except ImportError:
    from variaveis_parent import ACTIVITY, APPIUM_URL, PACKAGE, SERIAL, SESSAO_PATH


class AppiumError(RuntimeError):
    def __init__(self, code: int, detail: str) -> None:
        super().__init__(f"Appium {code} {detail}")
        self.code = code


class SessaoAppium:
    def __init__(self, session: str = "") -> None:
        self.session = session

    def _call(self, method: str, path: str, body: dict | None = None) -> dict:
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{APPIUM_URL}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise AppiumError(exc.code, f"{method} {path} {detail}") from exc
        return json.loads(raw) if raw else {}

    def viva(self) -> bool:
        if not self.session:
            return False
        try:
            self._call("GET", f"/session/{self.session}/timeouts")
            return True
        except AppiumError:
            return False

    def criar(self) -> None:
        created = self._call(
            "POST",
            "/session",
            {
                "capabilities": {
                    "alwaysMatch": {
                        "platformName": "Android",
                        "appium:automationName": "UiAutomator2",
                        "appium:udid": SERIAL,
                        "appium:deviceName": SERIAL,
                        "appium:appPackage": PACKAGE,
                        "appium:appActivity": ACTIVITY,
                        "appium:noReset": True,
                        "appium:dontStopAppOnReset": True,
                        "appium:shouldTerminateApp": False,
                        "appium:autoGrantPermissions": True,
                        "appium:newCommandTimeout": 0,
                    }
                }
            },
        )
        self.session = created["value"]["sessionId"]
        _gravar(self.session)

    def encerrar(self) -> None:
        if self.session:
            try:
                self._call("DELETE", f"/session/{self.session}")
            except AppiumError as exc:
                if exc.code != 404:
                    raise
            self.session = ""
        if SESSAO_PATH.exists():
            SESSAO_PATH.unlink()

    def find(self, test_id: str, timeout_s: float) -> str:
        selectors = [
            f'new UiSelector().resourceId("{test_id}")',
            f'new UiSelector().resourceIdMatches(".*{test_id}$")',
            f'new UiSelector().description("{test_id}")',
        ]
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            for value in selectors:
                try:
                    found = self._call(
                        "POST",
                        f"/session/{self.session}/element",
                        {"using": "-android uiautomator", "value": value},
                    )
                    element = (found.get("value") or {}).get("ELEMENT") or (
                        found.get("value") or {}
                    ).get("element-6066-11e4-a52e-4f735466cecf")
                    if element:
                        return element
                except AppiumError as exc:
                    if exc.code != 404:
                        raise
            time.sleep(0.4)
        raise SystemExit(f"testID nao apareceu: {test_id}")

    def click(self, element_id: str) -> None:
        self._call("POST", f"/session/{self.session}/element/{element_id}/click", {})

    def fill(self, element_id: str, text: str) -> None:
        self._call("POST", f"/session/{self.session}/element/{element_id}/clear", {})
        self._call(
            "POST",
            f"/session/{self.session}/element/{element_id}/value",
            {"text": text},
        )


def _gravar(session_id: str) -> None:
    SESSAO_PATH.write_text(
        json.dumps(
            {
                "session_id": session_id,
                "appium_url": APPIUM_URL,
                "serial": SERIAL,
                "package": PACKAGE,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _ler() -> dict | None:
    if not SESSAO_PATH.exists():
        return None
    data = json.loads(SESSAO_PATH.read_text(encoding="utf-8"))
    if not data.get("session_id"):
        return None
    return data


def criar_sessao() -> SessaoAppium:
    salva = _ler()
    if salva:
        atual = SessaoAppium(salva["session_id"])
        if atual.viva():
            return atual
    nova = SessaoAppium()
    nova.criar()
    return nova


def encerrar_sessao() -> None:
    salva = _ler()
    sessao = SessaoAppium(salva["session_id"] if salva else "")
    sessao.encerrar()


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"criar", "encerrar"}:
        raise SystemExit("uso: python sessao_appium.py criar|encerrar")
    if sys.argv[1] == "criar":
        sessao = criar_sessao()
        print(f"sessao aberta: {sessao.session}")
        return
    encerrar_sessao()
    print("sessao encerrada")


if __name__ == "__main__":
    main()
