# Evidências de Aceite — Exemplo 1 (Nexus Foundation)

Validação executada em **2026-08-05**.

## Stack validada

| Tecnologia | Artefato |
|------------|----------|
| **CrewAI** | `nexus/labs/modulo1_foundation.py` |
| **Groq** | `nexus/core/llm_config.py` → `groq/llama-3.1-8b-instant` |
| **LiteLLM** | Bridge CrewAI → Groq (`litellm.drop_params` + strip `cache_breakpoint`) |
| **truststore** | SSL Windows para tiktoken/LiteLLM |
| **Agent** | `get_architect()` em `nexus/core/agents.py` |
| **Tool** | `check_compliance_rules` em `nexus/tools/policy_rag.py` |
| **Monorepo** | Base UNIPDS em `nexus/` (67 arquivos) |

## Comandos executados

```powershell
cd nexus
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install crewai "crewai[tools]" langchain-groq python-dotenv litellm truststore
copy .env.example .env
# GROQ_API_KEY=...

python labs/modulo1_foundation.py
```

## Checklist

| Critério | Status | Evidência |
|----------|--------|-----------|
| Base UNIPDS em `nexus/` | ✅ | monorepo com `labs/`, `core/`, `tools/` |
| `venv` + dependências | ✅ | CrewAI 1.15 + litellm + truststore |
| `GROQ_API_KEY` em `.env` | ✅ | `.env` no `.gitignore` |
| `modulo1_foundation.py` executa | ✅ | exit code 0 |
| Agente consulta compliance | ✅ | `check_compliance_rules` 2x; bucket `nexus-logs-us-east-1` |
| README e docs didáticos | ✅ | esta pasta |

## Registro de execução

| Lab | Comando | Resultado |
|-----|---------|-----------|
| Setup | venv + pip install | ✅ Python 3.12 |
| Lab 1 | `python labs/modulo1_foundation.py` | ✅ plano + HCL Terraform |
| Fix `agents.py` | syntax error UNIPDS | ✅ corrigido |
| Fix `llm_config.py` | SSL + cache_breakpoint Groq | ✅ truststore + patch LiteLLM |

## Saída validada

```
Plano detalhado:
- Nome do bucket: nexus-logs-us-east-1
- Região de compliance: us-east-1
- Tipo de bucket: privado
```

Regras de compliance respeitadas:

- Prefixo `nexus-`
- Região `us-east-1`
- Bucket S3 privado
