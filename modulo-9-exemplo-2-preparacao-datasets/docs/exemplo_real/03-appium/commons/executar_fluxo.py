"""Executa um flow_id no emulador parent.

A sessão Appium fica aberta no fim: outro fluxo pode continuar dela.
O critério de sucesso é o caminho concluído. resultado e prompt_context
são o texto que descreve o que essa sequência deveria ter alcançado.
"""

from __future__ import annotations

import subprocess
import time
import urllib.error
import urllib.request

try:
    from .montar_fluxo import montar_passos
    from .seed import resolver
    from .sessao_appium import SessaoAppium, criar_sessao
    from .variaveis_parent import ACTIVITY, APPIUM_URL, METRO, PACKAGE, SERIAL
except ImportError:
    from montar_fluxo import montar_passos
    from seed import resolver
    from sessao_appium import SessaoAppium, criar_sessao
    from variaveis_parent import ACTIVITY, APPIUM_URL, METRO, PACKAGE, SERIAL

# Activities e textos que ficam na frente do app e escondem os testID.
_OVERLAY_DEV = (
    "DevLauncherActivity",
    "DevMenuActivity",
    "expo.modules.devmenu",
    "devsupport",
    "Element inspector",
    "JS debugger",
    "Performance monitor",
)


def adb_texto(*args: str) -> str:
    """Saída do adb. Não interrompe se o comando só consultar o aparelho."""
    comando = ["adb", "-s", SERIAL, *args]
    try:
        feito = subprocess.run(comando, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise SystemExit(f"adb nao encontrado no PATH. serial={SERIAL}") from exc
    return (feito.stdout or "") + (feito.stderr or "")


def adb(*args: str) -> None:
    """Roda um comando adb no emulador definido em variaveis_parent."""
    comando = ["adb", "-s", SERIAL, *args]
    try:
        feito = subprocess.run(comando, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise SystemExit(f"adb nao encontrado no PATH. serial={SERIAL}") from exc
    if feito.returncode != 0:
        detalhe = feito.stderr.strip() or feito.stdout.strip()
        raise SystemExit(f"{' '.join(comando)} falhou: {detalhe}")


def emulador_pronto() -> None:
    """O serial parent precisa estar em estado device."""
    estado = adb_texto("get-state").strip().splitlines()
    if not any(linha.strip() == "device" for linha in estado):
        raise SystemExit(f"emulador {SERIAL} nao esta pronto: {estado}")


def metro_pronto() -> None:
    """Expo pronto: o packager do Metro responde running."""
    url = f"http://127.0.0.1:{METRO}/status"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            corpo = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SystemExit(f"metro :{METRO} nao esta pronto: {exc}") from exc
    if "running" not in corpo.lower():
        raise SystemExit(f"metro :{METRO} sem packager running: {corpo[:120]}")


def appium_pronto() -> None:
    """A sessão do script só abre se o servidor Appium responder."""
    try:
        with urllib.request.urlopen(f"{APPIUM_URL}/status", timeout=3) as resp:
            ok = resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SystemExit(f"appium {APPIUM_URL} nao esta pronto: {exc}") from exc
    if not ok:
        raise SystemExit(f"appium {APPIUM_URL} sem status 200")


def foco_atual() -> str:
    """Linha mCurrentFocus. É o ponto em que se vê o que está na frente do app."""
    janela = adb_texto("shell", "dumpsys", "window")
    for linha in janela.splitlines():
        if "mCurrentFocus" in linha:
            return linha.strip()
    return ""


def texto_da_ui() -> str:
    """Dump da hierarquia para achar overlay de dev dentro da mesma activity."""
    adb_texto("shell", "uiautomator", "dump", "/sdcard/_gf_ready.xml")
    return adb_texto("shell", "cat", "/sdcard/_gf_ready.xml")


def app_sem_overlay(foco: str, ui: str) -> bool:
    """Pronto quando o foco é a MainActivity do parent e a UI não tem menu de dev."""
    if PACKAGE not in foco or "MainActivity" not in foco:
        return False
    return not any(marca in foco or marca in ui for marca in _OVERLAY_DEV)


def esperar_app_sem_overlay(timeout_s: float = 20) -> str:
    """Espera o Expo entregar o bundle e a activity do app ficar sem overlay."""
    limite = time.time() + timeout_s
    ultimo = ""
    while time.time() < limite:
        ultimo = foco_atual()
        if PACKAGE in ultimo and "MainActivity" in ultimo:
            ui = texto_da_ui()
            if app_sem_overlay(ultimo, ui):
                return ultimo
        time.sleep(1)
    raise SystemExit(
        "app nao esta aberto sem overlay de dev. "
        f"foco={ultimo or 'desconhecido'}"
    )


def ambiente_pronto() -> None:
    """Emulador, Metro e Appium respondem antes de abrir o app."""
    emulador_pronto()
    metro_pronto()
    appium_pronto()


def abrir_app() -> None:
    """Limpa o parent e abre a activity do APK instalado, sem o cliente Expo."""
    adb("shell", "pm", "clear", PACKAGE)
    adb("shell", "am", "start", "-n", f"{PACKAGE}/{ACTIVITY}")


def executar_toque(driver: SessaoAppium, componente: dict) -> None:
    """Espera o intervalo e toca o test_id."""
    time.sleep(int(componente.get("intervalo_ms") or 0) / 1000)
    elemento = driver.find(componente["test_id"], timeout_s=20)
    driver.click(elemento)


def executar_preenchimento(driver: SessaoAppium, componente: dict) -> None:
    """Troca seed.<chave> pelo valor de commons/seed.py e digita."""
    time.sleep(int(componente.get("intervalo_ms") or 0) / 1000)
    texto = componente.get("preenchimento")
    if not texto:
        raise SystemExit(f"preenchimento ausente em {componente['test_id']}")
    elemento = driver.find(componente["test_id"], timeout_s=20)
    driver.fill(elemento, resolver(str(texto)))


def executar_espera(componente: dict) -> None:
    """Ação wait só consome o intervalo. Não procura elemento."""
    time.sleep(int(componente.get("intervalo_ms") or 0) / 1000)


def executar_componente(driver: SessaoAppium, componente: dict) -> None:
    """Despacha tap, fill ou wait a partir do campo acao."""
    acao = componente.get("acao")
    if acao == "tap":
        executar_toque(driver, componente)
    elif acao == "fill":
        executar_preenchimento(driver, componente)
    elif acao == "wait":
        executar_espera(componente)
    else:
        raise SystemExit(f"acao nao suportada em {componente.get('test_id')}: {acao}")
    print(f"ordem {componente['ordem']} {acao} {componente.get('test_id')}")


def executar_api(passo: dict) -> None:
    """O catálogo só registra o endpoint. O Appium não chama a API."""
    print(f"ordem {passo['ordem']} api {passo.get('method')} {passo.get('url')}")


def eh_welcome_onboarding(passo: dict) -> bool:
    """A tela de slides é WelcomeOnboardingScreen, view_id welcome-onboarding-screen."""
    arquivo = str(passo.get("screen_file") or "")
    return passo.get("view_id") == "welcome-onboarding-screen" or "WelcomeOnboardingScreen" in arquivo


def executar_tela(driver: SessaoAppium, passo: dict) -> None:
    """Confirma a view e percorre os componentes já ordenados.

    Se WelcomeOnboardingScreen não aparecer, espera 5s e segue para o próximo passo.
    """
    try:
        driver.find(passo["view_id"], timeout_s=45)
    except SystemExit as exc:
        if not eh_welcome_onboarding(passo) or "nao apareceu" not in str(exc):
            raise
        print(f"WelcomeOnboardingScreen ausente no passo {passo['ordem']}. Espera 5s e segue.")
        time.sleep(5)
        return
    print(f"tela {passo['ordem']} {passo['view_id']} ({passo['screen_file']})")
    for componente in passo["componentes"]:
        executar_componente(driver, componente)


def verificar_resultado(fluxo: dict) -> None:
    """O caminho terminou. O texto do fluxo é o critério que essa sequência cobre."""
    print(f"resultado: {fluxo['resultado']}")
    print(f"prompt_context: {fluxo['prompt_context']}")


def executar(flow_id: str) -> None:
    """Abre o app, cria a sessão e roda a sequência achatada desse flow_id."""
    fluxo, passos = montar_passos(flow_id)
    print(fluxo["consulta"])
    ambiente_pronto()
    abrir_app()
    print(f"ambiente pronto: {esperar_app_sem_overlay()}")
    driver = criar_sessao()
    for passo in passos:
        if passo.get("url"):
            executar_api(passo)
            continue
        executar_tela(driver, passo)
    verificar_resultado(fluxo)
    print(f"sessao aberta: {driver.session}")
    print(f"app permanece em {PACKAGE}")
