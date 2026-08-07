# Evidências de Execução — Lab 10 (RAG & Auto-Remediação)

Validação executada em **2026-08-07**.

**Relatório didático:** [`RELATORIO_DIDATICO_MODULO10.md`](./RELATORIO_DIDATICO_MODULO10.md)

---

## Objetivo do lab

Pipeline CrewAI com **RAG sobre runbook corporativo** e validação programática do plano de remediação:

1. **Engenheiro SRE de Resposta a Incidentes** — invoca `consult_runbook`
2. Tool lê `runbook_db.md` e retorna plano compacto (diagnóstico + remediação + post-mortem)
3. Script valida runbook e plano extraído deterministicamente
4. Plano determinístico é exibido ao operador (fonte de verdade do RAG)

Script: `nexus/labs/modulo10_remediation.py`  
Tool: `nexus/tools/runbook_tools.py`  
Runbook: `nexus/data/runbook_db.md`

---

## Ambiente

| Item | Valor |
|------|-------|
| Python | 3.12.10 (venv) |
| CrewAI | 1.15.11 |
| LLM | Groq `llama-3.1-8b-instant` |
| Entrada | `nexus/data/runbook_db.md` |
| Incidente simulado | `PostgresqlTooManyConnections` |
| Data | 2026-08-07 |
| Duração | **~9 s** |
| Exit code | **0** ✅ |

### Comando

```powershell
cd modulo-6-exemplo-1-aiops-foundation/nexus
.\venv\Scripts\Activate.ps1
python labs/modulo10_remediation.py
```

---

## Resultado da execução

| Métrica | Valor |
|---------|-------|
| **Exit code** | `0` ✅ |
| **Tasks concluídas** | **1/1** |
| **Tool calls** | **1** (`consult_runbook`) |
| **Pré-validação runbook** | **Passou** ✅ |
| **Auditoria plano RAG** | **Passou** ✅ |

---

## Ajustes implementados (antes da execução)

| Item | Ação |
|------|------|
| `runbook_db.md` incompleto | Adicionadas seções **Remediação**, **Prevenção** e **Post-mortem** |
| Tool inline no script | Extraída para `tools/runbook_tools.py` |
| Runbook bruto na tool | `consult_runbook` retorna **plano compacto** (menos tokens, SQL explícito) |
| Validação | `validate_runbook_db()` + `audit_remediation_plan()` determinísticos |
| Saída ao operador | Plano RAG impresso após o crew (fonte de verdade, independente do LLM) |

---

## Runbook completado (`runbook_db.md`)

### SQL de diagnóstico

```sql
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
```

### SQL de remediação (conexões idle > 5 min)

```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < now() - interval '5 minutes'
  AND pid <> pg_backend_pid();
```

### Template post-mortem

- **Incidente:** Saturação de conexões PostgreSQL
- **Impacto:** Latência > 500ms / erros FATAL
- **Ação:** SQL de limpeza após aprovação do plantão (ChatOps)
- **Follow-up:** Ajustar pool + monitorar `pg_stat_activity`

---

## Saída da tool (plano RAG compacto)

```
=== PLANO DE REMEDIAÇÃO — serviço 'db' ===
Alerta: PostgresqlTooManyConnections
Sintoma: FATAL remaining connection slots / latência escrita > 500ms

--- SQL DIAGNÓSTICO (runbook) ---
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

--- SQL REMEDIAÇÃO (conexões idle > 5 min) ---
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < now() - interval '5 minutes'
  AND pid <> pg_backend_pid();

--- RASCUNHO POST-MORTEM ---
- Incidente: Saturação de conexões PostgreSQL
- Impacto: Latência > 500ms; erros FATAL na aplicação
- Causa raiz: (investigar — pool sem limite, leak pós-deploy)
- Ação: Executar SQL de remediação após aprovação do plantão (ChatOps)
- Follow-up: Revisar pool (HikariCP/PgBouncer); monitorar pg_stat_activity
```

---

## Resposta do agente (LLM)

O agente executou **1 tool call** corretamente, mas o **Final Answer** do Llama 3.1 8B foi genérico (nota em inglês sobre connection pool, sem repetir os SQLs).

> **Mitigação didática:** o script imprime o **plano determinístico** extraído do runbook após o crew — mesmo padrão do Lab 9 (cálculo na tool, não no LLM).

---

## Validação programática (pós-execução)

```
📋 Pré-validação do runbook_db.md:
   ✅ Runbook completo (diagnóstico + remediação + post-mortem template)

📋 Auditoria determinística do plano RAG:
   ✅ Plano extraído com SQL diagnóstico, remediação e post-mortem

✅ RAG Runbook — runbook completo e plano de remediação validado.
```

| Verificação | Resultado |
|-------------|-----------|
| Alerta `PostgresqlTooManyConnections` no runbook | ✅ |
| SQL diagnóstico `pg_stat_activity` | ✅ |
| SQL remediação `pg_terminate_backend` | ✅ |
| Template post-mortem | ✅ |
| Tool `consult_runbook` (1×) | ✅ |
| Plano RAG auditável | ✅ |

---

## Critérios de aceite

- [x] Execução sem erro Groq
- [x] Runbook `runbook_db.md` completo (diagnóstico + remediação + post-mortem)
- [x] Tool `consult_runbook` (1×)
- [x] SQL diagnóstico e remediação presentes no plano RAG
- [x] Validação automática no script
- [x] Plano determinístico exibido ao operador

---

## Conclusão

O Lab 10 demonstra **RAG de runbooks** para incidentes de banco:

- O conhecimento institucional vive em `runbook_db.md` (não no prompt)
- A tool `consult_runbook` recupera e estrutura o plano no momento do alerta
- A validação programática garante que diagnóstico, remediação e post-mortem estão presentes
- O operador recebe o plano completo mesmo quando o LLM resume demais a resposta final

---

## Próximo passo

Lab 11 — Guardrails: [`modulo11_guardrails.py`](../nexus/labs/modulo11_guardrails.py)

---

## Referências

| Recurso | Caminho |
|---------|---------|
| Script | [`nexus/labs/modulo10_remediation.py`](../nexus/labs/modulo10_remediation.py) |
| Tool Runbook | [`nexus/tools/runbook_tools.py`](../nexus/tools/runbook_tools.py) |
| Runbook DB | [`nexus/data/runbook_db.md`](../nexus/data/runbook_db.md) |
| Relatório didático | [`RELATORIO_DIDATICO_MODULO10.md`](./RELATORIO_DIDATICO_MODULO10.md) |
