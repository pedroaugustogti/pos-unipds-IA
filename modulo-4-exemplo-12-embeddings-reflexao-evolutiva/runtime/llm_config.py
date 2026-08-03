"""Configuracao centralizada da LLM e embeddings (OpenRouter ou OpenAI)."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        pass

load_dotenv(Path(__file__).parent / ".env")

try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass


def _criar_cliente_openai(api_key: str, base_url: str | None = None, headers: dict | None = None):
    from openai import OpenAI

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    if headers:
        kwargs["default_headers"] = headers

    try:
        import certifi
        import httpx

        kwargs["http_client"] = httpx.Client(verify=certifi.where(), timeout=120.0)
    except ImportError:
        pass

    return OpenAI(**kwargs)


def get_llm_client_and_model():
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if openrouter_key:
        return (
            _criar_cliente_openai(
                openrouter_key,
                base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                headers={
                    "HTTP-Referer": os.environ.get(
                        "OPENROUTER_HTTP_REFERER",
                        "https://github.com/pedroaugustogti/pos-unipds-IA",
                    ),
                    "X-Title": os.environ.get(
                        "OPENROUTER_X_TITLE", "POS UNIPDS - Embeddings Reflexao"
                    ),
                },
            ),
            os.environ.get("OPENROUTER_MODEL", "openrouter/free"),
        )

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        return _criar_cliente_openai(openai_key), os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    return None, None


def get_embedding_client_and_model(default_model: str = "text-embedding-3-small"):
    """Cliente para embeddings — OpenRouter usa prefixo openai/."""
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    modelo = os.environ.get(
        "OPENROUTER_EMBEDDING_MODEL",
        os.environ.get("EMBEDDING_MODEL", f"openai/{default_model}"),
    )
    if openrouter_key:
        return (
            _criar_cliente_openai(
                openrouter_key,
                base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                headers={
                    "HTTP-Referer": os.environ.get(
                        "OPENROUTER_HTTP_REFERER",
                        "https://github.com/pedroaugustogti/pos-unipds-IA",
                    ),
                    "X-Title": os.environ.get(
                        "OPENROUTER_X_TITLE", "POS UNIPDS - Embeddings Reflexao"
                    ),
                },
            ),
            modelo,
        )

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        return _criar_cliente_openai(openai_key), default_model

    return None, default_model
