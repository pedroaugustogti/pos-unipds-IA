# Setup Groq — Nexus AI-Ops

O projeto Nexus usa **Groq** como provedor LLM padrão (`groq/llama-3.1-8b-instant`).

## 1. Obter chave

1. Acesse [console.groq.com](https://console.groq.com/)
2. Crie uma API key
3. Copie o valor (`gsk_...`)

## 2. Configurar `.env`

```powershell
cd modulo-6-exemplo-1-aiops-foundation/nexus
copy .env.example .env
```

Edite `.env`:

```env
GROQ_API_KEY=gsk_sua_chave_aqui
```

## 3. Validar

```powershell
.\venv\Scripts\Activate.ps1
python labs/modulo1_foundation.py
```

Se a chave estiver ausente, CrewAI/Groq retorna erro de autenticação.

## Modelo configurado

Arquivo: `nexus/core/llm_config.py`

```python
nexus_llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2
)
```

## Solução de problemas

| Erro | Causa | Solução |
|------|-------|---------|
| `ModuleNotFoundError: crewai` | venv não ativado | `.\venv\Scripts\Activate.ps1` |
| Auth / API key | `.env` ausente | Copiar `.env.example` e preencher |
| Python 3.14 | Incompatibilidade CrewAI | Usar Python 3.11 ou 3.12 |
