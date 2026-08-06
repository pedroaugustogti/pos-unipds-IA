"""Limites compartilhados para reduzir TPM na Groq e concluir os labs."""

import os
import time
from typing import Any

# Limites de agente / crew (sobrescrevíveis via .env)
AGENT_MAX_ITER = int(os.getenv("NEXUS_AGENT_MAX_ITER", "3"))
AGENT_MAX_RPM = int(os.getenv("NEXUS_AGENT_MAX_RPM", "4"))
CREW_MAX_RPM = int(os.getenv("NEXUS_CREW_MAX_RPM", "4"))

# Pausa entre rodadas do loop IaC ou entre tasks K8s
ROUND_DELAY_SECONDS = int(os.getenv("NEXUS_ROUND_DELAY_SECONDS", "25"))

# Retentativas quando a Groq retorna rate limit / TPM
GROQ_RETRY_ATTEMPTS = int(os.getenv("NEXUS_GROQ_RETRY_ATTEMPTS", "3"))
GROQ_RETRY_DELAY_SECONDS = int(os.getenv("NEXUS_GROQ_RETRY_DELAY_SECONDS", "30"))

# Máximo de falhas Checkov no feedback enviado ao LLM
MAX_AUDIT_FEEDBACK_ITEMS = int(os.getenv("NEXUS_MAX_AUDIT_FEEDBACK_ITEMS", "8"))


def nexus_crew_kwargs(**overrides: Any) -> dict[str, Any]:
    """Defaults de Crew alinhados à economia de tokens."""
    defaults: dict[str, Any] = {
        "verbose": True,
        "max_rpm": CREW_MAX_RPM,
    }
    defaults.update(overrides)
    return defaults


def _is_rate_limit_error(error: BaseException) -> bool:
    name = type(error).__name__.lower()
    if "ratelimit" in name or "rate_limit" in name:
        return True
    message = str(error).lower()
    return (
        "rate_limit" in message
        or "rate limit" in message
        or "tpm" in message
        or "tokens per minute" in message
        or "too many requests" in message
    )


def kickoff_with_retry(crew: Any, *, label: str = "crew") -> Any:
    """Executa crew.kickoff() com backoff em falhas de quota TPM/RPM da Groq."""
    last_error: BaseException | None = None

    for attempt in range(1, GROQ_RETRY_ATTEMPTS + 1):
        try:
            return crew.kickoff()
        except Exception as error:
            last_error = error
            if not _is_rate_limit_error(error) or attempt >= GROQ_RETRY_ATTEMPTS:
                raise
            wait = GROQ_RETRY_DELAY_SECONDS * attempt
            print(
                f"\n⏳ Rate limit na Groq ({label}) — "
                f"aguardando {wait}s (tentativa {attempt}/{GROQ_RETRY_ATTEMPTS})...\n"
            )
            time.sleep(wait)

    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Falha ao executar {label}")
