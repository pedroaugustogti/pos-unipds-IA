"""Carrega `crew/.env` e herda LangSmith/LangChain dos outros módulos do monorepo."""

from __future__ import annotations

import os
from pathlib import Path

from lib.paths import MODULE_ROOT, REPO_ROOT

_LOADED = False

# Mesmo padrão de modulo-3-exemplo-9 / exemplo-2
_SHARED_ENV_KEYS = (
    "LANGSMITH_API_KEY",
    "LANGCHAIN_API_KEY",
    "LANGCHAIN_TRACING_V2",
    "LANGCHAIN_ENDPOINT",
    "LANGSMITH_ENDPOINT",
    "LANGSMITH_TRACING",
)

_SHARED_ENV_FILES = (
    REPO_ROOT / "modulo-3-exemplo-9-mcp-langchain" / ".env",
    REPO_ROOT / "modulo-3-exemplo-2-google-trends-agent" / ".env",
)


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    raw_text = None
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            raw_text = path.read_text(encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    if raw_text is None:
        raw_text = path.read_text(encoding="utf-8", errors="replace")

    out: dict[str, str] = {}
    for raw in raw_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if key:
            out[key] = val
    return out


def _apply_vars(data: dict[str, str], *, override: bool = False, only: set[str] | None = None) -> None:
    for key, val in data.items():
        if only is not None and key not in only:
            continue
        if not val:
            continue
        if override or key not in os.environ or not str(os.environ.get(key) or "").strip():
            os.environ[key] = val


def _alias_langsmith_langchain() -> None:
    """LangChain aceita LANGCHAIN_API_KEY; outros módulos usam LANGSMITH_API_KEY."""
    ls = (os.environ.get("LANGSMITH_API_KEY") or "").strip()
    lc = (os.environ.get("LANGCHAIN_API_KEY") or "").strip()
    if ls and not lc:
        os.environ["LANGCHAIN_API_KEY"] = ls
    if lc and not ls:
        os.environ["LANGSMITH_API_KEY"] = lc
    if not (os.environ.get("LANGCHAIN_TRACING_V2") or "").strip() and ls:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    if not (os.environ.get("LANGCHAIN_PROJECT") or "").strip():
        os.environ.setdefault("LANGCHAIN_PROJECT", "guardiao-familia-agents")


def inherit_langsmith_from_monorepo(*, override: bool = False) -> list[str]:
    """Preenche keys LangSmith ausentes a partir dos .env dos módulos 3."""
    used: list[str] = []
    only = set(_SHARED_ENV_KEYS)
    for path in _SHARED_ENV_FILES:
        before = {k: (os.environ.get(k) or "").strip() for k in only}
        _apply_vars(_read_env_file(path), override=override, only=only)
        after = {k: (os.environ.get(k) or "").strip() for k in only}
        if any(after[k] and after[k] != before[k] for k in only):
            used.append(str(path.relative_to(REPO_ROOT)))
    _alias_langsmith_langchain()
    return used


def ensure_ssl_certs() -> Path | None:
    """Garante cacert.pem do projeto, env SSL_* e truststore (CA do Windows)."""
    certs_dir = MODULE_ROOT / "certs"
    cacert = certs_dir / "cacert.pem"
    try:
        if not cacert.exists() or cacert.stat().st_size < 1000:
            import certifi
            import shutil

            certs_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(certifi.where(), cacert)
    except Exception:
        if not cacert.exists():
            return None

    path = str(cacert.resolve())
    for key in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"):
        if not (os.environ.get(key) or "").strip():
            os.environ[key] = path

    # Usa o store do SO (necessário com proxy/CA corporativa no Windows)
    try:
        import truststore

        truststore.inject_into_ssl()
    except Exception:
        pass
    return cacert


def load_dotenv(override: bool = False) -> Path | None:
    """
    Lê chave=valor de crew/.env (preferido) ou .env na raiz do módulo.
    Depois herda LANGSMITH_* / LANGCHAIN_* dos outros módulos se ainda vazias.
    Nao sobrescreve variaveis ja definidas, salvo override=True.
    """
    global _LOADED
    candidates = (
        MODULE_ROOT / "crew" / ".env",
        MODULE_ROOT / ".env",
    )
    path = next((p for p in candidates if p.exists()), None)
    if path is not None:
        _apply_vars(_read_env_file(path), override=override)

    inherit_langsmith_from_monorepo(override=False)
    ensure_ssl_certs()
    _LOADED = True
    return path


def ensure_env() -> None:
    if not _LOADED:
        load_dotenv()
