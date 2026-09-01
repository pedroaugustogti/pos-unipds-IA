"""Stack local E2E: Docker API + emuladores Android + Appium (Guardião Família)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from lib.mobile.mobile_runtime_config import (
    CHILD_METRO_PORT,
    PARENT_METRO_PORT,
    appium_env,
    metro_env_for,
)
from lib.core.repo_paths import resolve_repo_path

DEFAULT_API_BASE = "http://127.0.0.1:3000/api/v1"
DEFAULT_PARENT_EMAIL = "admin@guardiao.local"
DEFAULT_PARENT_PASSWORD = "GuardiaoDev2026!"

ANDROID_HOME_CANDIDATES = (
    os.environ.get("ANDROID_HOME"),
    os.environ.get("ANDROID_SDK_ROOT"),
    str(Path(os.environ.get("LOCALAPPDATA", "")) / "Android" / "Sdk"),
    str(Path.home() / "AppData" / "Local" / "Android" / "Sdk"),
    r"C:\Android\Sdk",
)


def resolve_android_home() -> Path | None:
    for raw in ANDROID_HOME_CANDIDATES:
        if not raw:
            continue
        root = Path(raw)
        adb = root / "platform-tools" / "adb.exe"
        if adb.is_file():
            return root
    return None


def api_repo() -> Path:
    path = resolve_repo_path("guardiao-familia-api")
    if not path:
        raise FileNotFoundError("Repo guardiao-familia-api não encontrado (GUARDAO_API_PATH).")
    return path


def parent_repo() -> Path:
    path = resolve_repo_path("guardiao-familia-parent")
    if not path:
        raise FileNotFoundError("Repo guardiao-familia-parent não encontrado.")
    return path


def child_repo() -> Path:
    path = resolve_repo_path("guardiao-familia-child")
    if not path:
        raise FileNotFoundError("Repo guardiao-familia-child não encontrado.")
    return path


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
    shell: bool = False,
) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    use_shell = shell or (os.name == "nt" and cmd and cmd[0] in {"npm", "npx"})
    run_cmd: str | list[str] = " ".join(cmd) if use_shell else cmd
    return subprocess.run(
        run_cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=merged,
        timeout=timeout,
        shell=use_shell,
    )


def ensure_api_env_files(api: Path | None = None) -> dict[str, Any]:
    """Garante .env e .env.docker mínimos para docker-compose.dev.yml."""
    api = api or api_repo()
    env_path = api / ".env"
    docker_env_path = api / ".env.docker"
    example = api / ".env.example"
    created: list[str] = []

    if not env_path.is_file() and example.is_file():
        shutil.copyfile(example, env_path)
        created.append(".env")

    if not docker_env_path.is_file():
        docker_env_path.write_text(
            "# Overrides Docker Compose (opcional)\n# DATABASE_URL e REDIS_URL vêm do compose.\n",
            encoding="utf-8",
        )
        created.append(".env.docker")

    return {"ok": True, "api": str(api), "created": created}


def docker_daemon_ready(timeout_sec: int = 120) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            proc = _run(["docker", "info"], timeout=20)
        except subprocess.TimeoutExpired:
            time.sleep(3)
            continue
        if proc.returncode == 0:
            return True
        time.sleep(3)
    return False


def start_docker_desktop() -> bool:
    candidates = (
        Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
        / "Docker"
        / "Docker"
        / "Docker Desktop.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
        / "Docker"
        / "Docker"
        / "Docker Desktop.exe",
    )
    for exe in candidates:
        if exe.is_file():
            subprocess.Popen([str(exe)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    return False


def docker_compose_up(*, build: bool = True, api: Path | None = None) -> dict[str, Any]:
    """Sobe Postgres+Redis; API em container só se imagem existir, senão host."""
    api = api or api_repo()
    ensure_api_env_files(api)
    proc = _run(
        ["docker", "compose", "-f", "docker-compose.dev.yml", "up", "-d", "postgres", "redis"],
        cwd=api,
        timeout=300,
    )
    if proc.returncode != 0:
        return {
            "ok": False,
            "stdout": (proc.stdout or "")[-4000:],
            "stderr": (proc.stderr or "")[-4000:],
            "returncode": proc.returncode,
        }
    has_image = _run(["docker", "image", "inspect", "guardiao-familia-api:dev"], timeout=15)
    if has_image.returncode == 0:
        api_proc = _run(
            ["docker", "compose", "-f", "docker-compose.dev.yml", "up", "-d", "api"],
            cwd=api,
            timeout=300,
        )
        return {
            "ok": api_proc.returncode == 0,
            "mode": "docker-api",
            "stdout": (api_proc.stdout or "")[-2000:],
            "stderr": (api_proc.stderr or "")[-2000:],
        }
    return {"ok": True, "mode": "postgres-redis-only", "note": "API via host (npm run start:dev)"}


def wait_api_health(
    base_url: str = DEFAULT_API_BASE,
    *,
    timeout_sec: int = 180,
    path: str = "/health",
) -> dict[str, Any]:
    url = base_url.rstrip("/") + path
    deadline = time.time() + timeout_sec
    last_error = ""
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                body = resp.read(4096).decode("utf-8", errors="replace")
                if resp.status == 200:
                    return {"ok": True, "url": url, "body": body[:500]}
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = str(exc)
        time.sleep(2)
    return {"ok": False, "url": url, "error": last_error}


def run_migrations(api: Path | None = None) -> dict[str, Any]:
    api = api or api_repo()
    env = {
        "DATABASE_URL": "postgresql://guardiao_admin:password@127.0.0.1:5432/guardiao_familia",
    }
    proc = _run(["npm", "run", "migration:run"], cwd=api, env=env, timeout=300)
    ok = proc.returncode == 0
    return {
        "ok": ok,
        "stdout": (proc.stdout or "")[-3000:],
        "stderr": (proc.stderr or "")[-3000:],
    }


def run_seed(api: Path | None = None) -> dict[str, Any]:
    api = api or api_repo()
    env = {
        "DATABASE_URL": "postgresql://guardiao_admin:password@127.0.0.1:5432/guardiao_familia",
    }
    proc = _run(["npm", "run", "seed"], cwd=api, env=env, timeout=120)
    return {
        "ok": proc.returncode == 0,
        "stdout": (proc.stdout or "")[-2000:],
        "stderr": (proc.stderr or "")[-2000:],
    }


def run_api_pairing_smoke(
    *,
    api: Path | None = None,
    api_base_url: str = DEFAULT_API_BASE,
    timeout_sec: int = 120,
) -> dict[str, Any]:
    """Smoke pareamento: tenta task36 (npm); fallback Python puro."""
    py = run_pairing_smoke_python(api_base_url=api_base_url)
    if py.get("ok"):
        return py

    api = api or api_repo()
    env = {
        "GF_API_BASE_URL": api_base_url,
        "GF_PARENT_EMAIL": DEFAULT_PARENT_EMAIL,
        "GF_PARENT_PASSWORD": DEFAULT_PARENT_PASSWORD,
    }
    proc = _run(
        ["npm", "run", "test:prototipo_v2:task36"],
        cwd=api,
        env=env,
        timeout=timeout_sec,
    )
    report = _extract_json_report((proc.stdout or "") + (proc.stderr or ""))
    ok = proc.returncode == 0
    if isinstance(report, dict):
        scenarios = report.get("scenarios")
        if isinstance(scenarios, list):
            required = [s for s in scenarios if not s.get("manual_required")]
            if required:
                ok = all(bool(s.get("ok")) for s in required)
    if ok:
        return {
            "ok": True,
            "suite": "task36-prototipo-v2",
            "returncode": proc.returncode,
            "report": report,
            "mode": "npm",
        }
    py["npm_fallback_failed"] = {
        "returncode": proc.returncode,
        "stderr_tail": (proc.stderr or "")[-800:],
    }
    return py


def _http_json(
    url: str,
    *,
    method: str = "GET",
    token: str | None = None,
    body: dict[str, Any] | None = None,
    timeout: int = 15,
    retries: int = 5,
) -> tuple[int, Any]:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")

    last_exc: Exception | None = None
    for attempt in range(max(1, retries)):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                try:
                    return resp.status, json.loads(raw) if raw else None
                except json.JSONDecodeError:
                    return resp.status, raw
        except urllib.error.HTTPError as exc:
            last_exc = exc
            if exc.code in (429, 502, 503) and attempt + 1 < retries:
                time.sleep(min(2**attempt, 30))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_exc = exc
            if attempt + 1 < retries:
                time.sleep(min(2**attempt, 15))
                continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError("_http_json: retries esgotados")


def run_pairing_smoke_python(
    *,
    api_base_url: str = DEFAULT_API_BASE,
    parent_email: str = DEFAULT_PARENT_EMAIL,
    parent_password: str = DEFAULT_PARENT_PASSWORD,
    family_name: str = "Familia E2E Local Smoke",
    child_name: str = "Filho E2E Local Smoke",
) -> dict[str, Any]:
    """Cenarios S0, S0.1 e 1 via HTTP (sem npm)."""
    base = api_base_url.rstrip("/")
    report: dict[str, Any] = {
        "suite": "pairing-smoke-python",
        "apiBaseUrl": base,
        "scenarios": [],
    }
    try:
        _, login = _http_json(
            f"{base}/auth/login",
            method="POST",
            body={"email": parent_email, "password": parent_password},
        )
        token = (login or {}).get("access_token") if isinstance(login, dict) else None
        if not token:
            raise RuntimeError("login sem access_token")
        report["scenarios"].append({"id": "S0", "name": "Parent login", "ok": True})

        _, families = _http_json(f"{base}/families", token=token)
        fam_list = families if isinstance(families, list) else []
        family_name = family_name or "Familia E2E Local Smoke"
        child_name = child_name or "Filho E2E Local Smoke"
        family = next((f for f in fam_list if f.get("name") == family_name), None)
        if not family:
            _, family = _http_json(
                f"{base}/families",
                method="POST",
                token=token,
                body={"name": family_name},
            )
        family_id = (family or {}).get("id")
        _, children = _http_json(f"{base}/children?include_latest_location=true", token=token)
        child_list = children if isinstance(children, list) else []
        child = next(
            (c for c in child_list if c.get("family_group_id") == family_id and c.get("name") == child_name),
            None,
        )
        if not child:
            _, child = _http_json(
                f"{base}/children",
                method="POST",
                token=token,
                body={"family_group_id": family_id, "name": child_name},
            )
        child_id = (child or {}).get("id")
        report["scenarios"].append(
            {
                "id": "S0.1",
                "name": "Ensure family and child",
                "ok": bool(child_id),
                "childId": child_id,
            }
        )

        _, code_resp = _http_json(
            f"{base}/children/{child_id}/pairing-code",
            method="POST",
            token=token,
            body={},
        )
        code = str((code_resp or {}).get("pairing_code") or "").strip()
        _, pair_resp = _http_json(
            f"{base}/pairing/validate",
            method="POST",
            body={
                "code": code,
                "device_name": "Python E2E Smoke",
                "platform": "android",
            },
        )
        ok_pair = bool((pair_resp or {}).get("access_token") if isinstance(pair_resp, dict) else False)
        report["scenarios"].append(
            {"id": "1", "name": "Valid pairing code", "ok": ok_pair, "childId": child_id}
        )
        ok = all(s.get("ok") for s in report["scenarios"])
        return {"ok": ok, "suite": report["suite"], "report": report, "mode": "python"}
    except Exception as exc:  # noqa: BLE001
        report["error"] = str(exc)
        return {"ok": False, "suite": report["suite"], "report": report, "mode": "python", "error": str(exc)}


def _extract_json_report(text: str) -> dict[str, Any] | list[Any] | None:
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line.startswith("{") and ("scenarios" in line or "suite" in line):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    start = text.rfind('{"suite"')
    if start >= 0:
        try:
            return json.loads(text[start:])
        except json.JSONDecodeError:
            pass
    return None


def adb_devices(android_home: Path | None = None) -> list[str]:
    home = android_home or resolve_android_home()
    if not home:
        return []
    adb = home / "platform-tools" / "adb.exe"
    if not adb.is_file():
        return []
    proc = _run([str(adb), "devices"], timeout=30)
    serials: list[str] = []
    for line in (proc.stdout or "").splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            serials.append(parts[0])
    return serials


def start_emulators(*, single: bool = False, api: Path | None = None) -> dict[str, Any]:
    from lib.mobile.mobile_setup_client import appium_root, setup_root, start_emulators_script

    _ = api
    script = start_emulators_script()
    if not script.is_file():
        return {"ok": False, "error": f"Script não encontrado: {script}"}
    args = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-WaitBoot",
    ]
    if single:
        args.append("-Single")
    proc = _run(args, cwd=setup_root(), timeout=300)
    devices = adb_devices()
    return {
        "ok": proc.returncode == 0 and len(devices) >= (1 if single else 2),
        "devices": devices,
        "script": str(script),
        "cwd": str(setup_root()),
        "stdout": (proc.stdout or "")[-2000:],
        "stderr": (proc.stderr or "")[-2000:],
    }


def metro_env(*, repo: str) -> dict[str, str]:
    return metro_env_for("parent" if repo == "parent" else "child")


def api_repo_real() -> Path:
    """Path físico do API repo (evita compose project `a` via junction)."""
    src = os.environ.get("GF_SOURCE_API", "").strip()
    if src:
        p = Path(src)
        if (p / "docker-compose.dev.yml").is_file():
            return p
    return api_repo()


def ensure_validation_stack(*, api: Path | None = None, start_api_host: bool = True) -> dict[str, Any]:
    """Docker Postgres/Redis + API health + migrations/seed para E2E completo."""
    api = api_repo_real() if api is None else Path(api)
    report: dict[str, Any] = {"api": str(api)}

    if not docker_daemon_ready(timeout_sec=15):
        report["docker_desktop_start"] = start_docker_desktop()
        if not docker_daemon_ready(timeout_sec=180):
            return {**report, "ok": False, "error": "docker_daemon_unavailable"}

    report["compose"] = docker_compose_up(build=False, api=api)
    if not report["compose"].get("ok"):
        revive = _run(
            ["docker", "start", "guardiao-postgres-dev", "guardiao-redis-dev"],
            timeout=60,
        )
        report["compose_revive"] = {
            "ok": revive.returncode == 0,
            "stderr": (revive.stderr or "")[-500:],
        }
        if not report["compose_revive"]["ok"]:
            return {**report, "ok": False, "error": "docker_compose_failed"}

    health = wait_api_health(timeout_sec=20)
    report["api_health_initial"] = health

    api_proc: subprocess.Popen[str] | None = None
    if not health.get("ok") and start_api_host:
        api_proc = subprocess.Popen(
            "npm run start:dev",
            cwd=str(api),
            shell=True,
            env={
                **os.environ,
                "DATABASE_URL": "postgresql://guardiao_admin:password@127.0.0.1:5432/guardiao_familia",
            },
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        report["api_host_pid"] = api_proc.pid
        health = wait_api_health(timeout_sec=180)
        report["api_health"] = health

    if not health.get("ok"):
        if api_proc:
            api_proc.terminate()
        return {**report, "ok": False, "error": "api_health_failed"}

    report["migrations"] = run_migrations(api)
    report["seed"] = run_seed(api)
    report["pairing_smoke"] = run_api_pairing_smoke(api=api)
    report["ok"] = bool(report["migrations"].get("ok") and report["seed"].get("ok"))
    return report


def ensure_metro_servers(*, parent: Path | None = None, child: Path | None = None) -> dict[str, Any]:
    """Garante Metro parent:8082 e child:9090 (dev client)."""
    parent_src = os.environ.get("GF_SOURCE_PARENT", "").strip()
    child_src = os.environ.get("GF_SOURCE_CHILD", "").strip()
    parent = Path(parent_src) if parent_src else (parent or parent_repo())
    child = Path(child_src) if child_src else (child or child_repo())
    out: dict[str, Any] = {"parent_port": PARENT_METRO_PORT, "child_port": CHILD_METRO_PORT}

    def _metro_up(port: int) -> bool:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/status", timeout=3) as resp:
                return resp.status == 200
        except (urllib.error.URLError, TimeoutError, OSError):
            return False

    procs: list[subprocess.Popen[str]] = []
    if not _metro_up(PARENT_METRO_PORT):
        procs.append(
            subprocess.Popen(
                f"npx expo start --port {PARENT_METRO_PORT} --dev-client",
                cwd=str(parent),
                shell=True,
                env={**os.environ, **metro_env(repo="parent")},
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        )
    if not _metro_up(CHILD_METRO_PORT):
        procs.append(
            subprocess.Popen(
                f"npx expo start --port {CHILD_METRO_PORT} --dev-client",
                cwd=str(child),
                shell=True,
                env={**os.environ, **metro_env(repo="child")},
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        )

    deadline = time.time() + 90
    while time.time() < deadline:
        if _metro_up(PARENT_METRO_PORT) and _metro_up(CHILD_METRO_PORT):
            out["ok"] = True
            out["pids"] = [p.pid for p in procs]
            return out
        time.sleep(2)

    out["ok"] = False
    out["error"] = "metro_timeout"
    out["pids"] = [p.pid for p in procs]
    return out


def run_appium_pairing(
    *,
    api: Path | None = None,
    single_emulator: bool = False,
    api_base_url: str = DEFAULT_API_BASE,
    timeout_sec: int = 900,
) -> dict[str, Any]:
    from lib.mobile.mobile_setup_client import run_pairing

    _ = api
    if api_base_url and api_base_url != DEFAULT_API_BASE:
        import os

        os.environ["GF_API_BASE_URL"] = api_base_url.rstrip("/")
    return run_pairing(single_emulator=single_emulator, timeout_sec=timeout_sec)


def check_prerequisites(*, require_android: bool = False) -> dict[str, Any]:
    api = resolve_repo_path("guardiao-familia-api")
    parent = resolve_repo_path("guardiao-familia-parent")
    child = resolve_repo_path("guardiao-familia-child")
    mobile_setup = resolve_repo_path("guardiao-familia-mobile-setup")
    android = resolve_android_home()
    docker_ok = _run(["docker", "info"], timeout=15).returncode == 0
    node_ok = shutil.which("npm") is not None
    appium_deps = False
    if mobile_setup:
        try:
            from lib.mobile.mobile_setup_client import has_appium_deps

            appium_deps = has_appium_deps()
        except Exception:
            appium_deps = False
    checks = {
        "api_repo": bool(api),
        "parent_repo": bool(parent),
        "child_repo": bool(child),
        "mobile_setup_repo": bool(mobile_setup),
        "docker": docker_ok,
        "npm": node_ok,
        "android_sdk": bool(android),
        "adb_devices": adb_devices(android) if android else [],
        "mobile_setup_appium_deps": appium_deps,
    }
    ok = checks["api_repo"] and checks["mobile_setup_repo"] and checks["docker"] and checks["npm"]
    if require_android:
        ok = ok and checks["android_sdk"] and len(checks["adb_devices"]) >= 1
    checks["ok"] = ok
    checks["android_home"] = str(android) if android else None
    return checks


def bootstrap_api_stack(*, seed: bool = True) -> dict[str, Any]:
    """Sobe Postgres/Redis, migrations, seed; API no host se imagem Docker indisponível."""
    result: dict[str, Any] = {"steps": []}
    if not docker_daemon_ready(timeout_sec=5):
        started = start_docker_desktop()
        result["docker_desktop_started"] = started
        if not docker_daemon_ready(timeout_sec=120):
            result["ok"] = False
            result["error"] = "Docker daemon indisponível"
            return result

    env_info = ensure_api_env_files()
    result["steps"].append({"ensure_env": env_info})

    compose = docker_compose_up()
    result["steps"].append({"compose": compose})
    if not compose["ok"]:
        result["ok"] = False
        return result

    api = api_repo()
    if not (api / "node_modules").is_dir():
        npm_ci = _run(["npm", "ci"], cwd=api, timeout=900)
        result["steps"].append({"npm_ci": {"ok": npm_ci.returncode == 0}})
        if npm_ci.returncode != 0:
            result["ok"] = False
            return result

    mig = run_migrations()
    result["steps"].append({"migrations": mig})
    if seed:
        sd = run_seed()
        result["steps"].append({"seed": sd})

    health = wait_api_health(timeout_sec=10)
    if not health["ok"]:
        host_api = _start_api_on_host(api)
        result["steps"].append({"host_api": host_api})
        health = wait_api_health(timeout_sec=120)
        result["steps"].append({"health": health})
    else:
        result["steps"].append({"health": health})

    pairing = run_api_pairing_smoke()
    result["steps"].append({"api_pairing_smoke": pairing})
    result["ok"] = health["ok"] and pairing["ok"]
    return result


def _start_api_on_host(api: Path) -> dict[str, Any]:
    env = {
        "DATABASE_URL": "postgresql://guardiao_admin:password@127.0.0.1:5432/guardiao_familia",
        "REDIS_URL": "redis://127.0.0.1:6379",
        "PORT": "3000",
    }
    proc = subprocess.Popen(
        ["npm", "run", "start:dev"],
        cwd=str(api),
        env={**os.environ, **env},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return {"ok": True, "pid": proc.pid, "mode": "host"}
