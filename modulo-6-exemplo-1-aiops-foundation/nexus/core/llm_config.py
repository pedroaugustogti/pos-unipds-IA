import os

try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

# Groq não suporta cache_breakpoint enviado pelo CrewAI 1.15+ via LiteLLM
try:
    import litellm

    litellm.drop_params = True
    litellm.num_retries = int(os.getenv("NEXUS_LITELLM_NUM_RETRIES", "2"))
    _litellm_completion = litellm.completion

    def _completion_without_cache_breakpoint(*args, **kwargs):
        messages = kwargs.get("messages")
        if messages:
            for message in messages:
                if isinstance(message, dict):
                    message.pop("cache_breakpoint", None)
        return _litellm_completion(*args, **kwargs)

    litellm.completion = _completion_without_cache_breakpoint
except ImportError:
    pass

# Centraliza a inteligência do projeto
nexus_llm = LLM(
    model=os.getenv("GROQ_MODEL", "groq/llama-3.1-8b-instant"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=float(os.getenv("GROQ_TEMPERATURE", "0.2")),
    max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "1024")),
)