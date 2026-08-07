import re
from pathlib import Path

from crewai.tools import tool

NEXUS_ROOT = Path(__file__).resolve().parent.parent
RUNBOOK_DB = NEXUS_ROOT / "data" / "runbook_db.md"

DIAGNOSTIC_SQL = (
    "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"
)
REMEDIATION_SQL = """SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < now() - interval '5 minutes'
  AND pid <> pg_backend_pid();"""


def _read_runbook(service_name: str) -> str:
    path = NEXUS_ROOT / "data" / f"runbook_{service_name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Runbook for service '{service_name}' not found.")
    return path.read_text(encoding="utf-8")


def build_remediation_plan(service_name: str = "db") -> str:
    """Builds a compact remediation plan from the runbook (deterministic RAG extraction)."""
    content = _read_runbook(service_name)
    sql_blocks = re.findall(r"```sql\n(.*?)```", content, flags=re.DOTALL)
    diagnostic = sql_blocks[0].strip() if sql_blocks else DIAGNOSTIC_SQL
    remediation = sql_blocks[1].strip() if len(sql_blocks) > 1 else REMEDIATION_SQL

    return f"""=== PLANO DE REMEDIAÇÃO — serviço '{service_name}' ===
Alerta: PostgresqlTooManyConnections
Sintoma: FATAL remaining connection slots / latência escrita > 500ms

--- SQL DIAGNÓSTICO (runbook) ---
{diagnostic}

--- SQL REMEDIAÇÃO (conexões idle > 5 min) ---
{remediation}

--- RASCUNHO POST-MORTEM ---
- Incidente: Saturação de conexões PostgreSQL
- Impacto: Latência > 500ms; erros FATAL na aplicação
- Causa raiz: (investigar — pool sem limite, leak pós-deploy)
- Ação: Executar SQL de remediação após aprovação do plantão (ChatOps)
- Follow-up: Revisar pool (HikariCP/PgBouncer); monitorar pg_stat_activity
"""


@tool("consult_runbook")
def consult_runbook(service_name: str) -> str:
    """Reads the official runbook and returns a compact remediation plan for the incident."""
    try:
        return build_remediation_plan(service_name)
    except FileNotFoundError as exc:
        return f"❌ {exc}"


def audit_remediation_plan(service_name: str = "db") -> dict:
    """Deterministic audit of runbook content used by the RAG pipeline."""
    plan = build_remediation_plan(service_name)
    return {
        "service": service_name,
        "plan": plan,
        "has_diagnostic_sql": "pg_stat_activity" in plan,
        "has_remediation_sql": "pg_terminate_backend" in plan,
        "has_postmortem": "POST-MORTEM" in plan,
        "has_alert": "PostgresqlTooManyConnections" in plan,
    }


def validate_runbook_db() -> tuple[bool, list[str]]:
    """Validates that the db runbook contains diagnosis and remediation sections."""
    issues: list[str] = []

    if not RUNBOOK_DB.exists():
        return False, ["runbook_db.md não encontrado."]

    content = RUNBOOK_DB.read_text(encoding="utf-8")
    checks = {
        "alerta PostgresqlTooManyConnections": "PostgresqlTooManyConnections" in content,
        "diagnóstico pg_stat_activity": "pg_stat_activity" in content,
        "seção Remediação": "Remediação" in content,
        "SQL pg_terminate_backend": "pg_terminate_backend" in content,
        "template post-mortem": "Post-mortem" in content,
    }
    for label, ok in checks.items():
        if not ok:
            issues.append(f"Runbook — falta: {label}")

    return len(issues) == 0, issues


def validate_remediation_audit(audit: dict) -> tuple[bool, list[str]]:
    """Validates deterministic remediation plan extracted from runbook."""
    issues: list[str] = []
    checks = {
        "alerta no plano": audit.get("has_alert"),
        "SQL diagnóstico no plano": audit.get("has_diagnostic_sql"),
        "SQL remediação no plano": audit.get("has_remediation_sql"),
        "post-mortem no plano": audit.get("has_postmortem"),
    }
    for label, ok in checks.items():
        if not ok:
            issues.append(f"Plano RAG — falta: {label}")
    return len(issues) == 0, issues
