# Runbook: Saturação de Conexões no PostgreSQL

## 🚨 Sintoma
- Alerta: `PostgresqlTooManyConnections`
- Erro na aplicação: "FATAL: remaining connection slots are reserved for non-replication superuser connections"
- Latência de escrita > 500ms.

## 🔍 Diagnóstico (Troubleshooting)
O Engenheiro de SRE deve verificar a contagem de processos ativos e seu estado:
```sql
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
```

## 🛠️ Remediação

### Limpar conexões ociosas (> 5 minutos)
Executar com cautela em produção — requer aprovação do plantão (ChatOps / guardrails):

```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < now() - interval '5 minutes'
  AND pid <> pg_backend_pid();
```

### Verificar alívio
```sql
SELECT count(*) AS total_connections FROM pg_stat_activity;
```

## 🔁 Prevenção
- Revisar pool de conexões da aplicação (HikariCP, PgBouncer)
- Configurar `idle_in_transaction_session_timeout`
- Escalar conexões (`max_connections`) somente após análise de capacidade

## 📝 Post-mortem (template)
- **Incidente:** Saturação de conexões PostgreSQL
- **Impacto:** Latência > 500ms / erros FATAL na aplicação
- **Causa raiz:** (preencher — ex.: pool sem limite, deploy com leak)
- **Ação:** SQL de limpeza de conexões idle conforme seção Remediação
- **Follow-up:** Ajustar pool + monitorar `pg_stat_activity`
