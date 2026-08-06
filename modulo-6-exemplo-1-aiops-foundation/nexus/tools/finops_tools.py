import json
from pathlib import Path

from crewai.tools import tool

NEXUS_ROOT = Path(__file__).resolve().parent.parent

# Fallback quando rightsized_cost_per_month não está no inventário (us-east-1, referência didática)
RIGHTSIZED_COST_BY_TYPE = {
    "m5.4xlarge": ("m5.large", 70.00),
    "m5.2xlarge": ("m5.large", 70.00),
    "m5.xlarge": ("m5.large", 70.00),
}

CPU_RIGHTSIZING_THRESHOLD = 10.0  # % média — abaixo disso, candidato a rightsizing


def _parse_cpu_percent(value: str | float | int | None) -> float:
    if value is None:
        return 100.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace("%", "").strip() or "100")


def audit_cloud_inventory(payload: dict) -> dict:
    """Auditoria determinística: zumbis (economia total) + rightsizing (economia parcial)."""
    zombies: list[dict] = []
    rightsizing: list[dict] = []

    for resource in payload.get("resources", []):
        resource_type = resource.get("type", "")
        status = (resource.get("status") or "").lower()
        cost = float(resource.get("cost_per_month", 0))

        if resource_type == "EBS Volume" and status == "available":
            zombies.append(
                {
                    "id": resource.get("id"),
                    "category": "EBS órfão",
                    "action": "Snapshot opcional + DeleteVolume",
                    "savings_monthly": cost,
                }
            )
            continue

        if resource_type == "Elastic IP" and status == "unassociated":
            zombies.append(
                {
                    "id": resource.get("id"),
                    "category": "Elastic IP solto",
                    "action": "ReleaseAddress",
                    "savings_monthly": cost,
                }
            )
            continue

        if resource_type != "EC2 Instance":
            continue

        cpu = _parse_cpu_percent(resource.get("avg_cpu_utilization"))
        current_type = resource.get("instance_type", "unknown")

        if resource.get("rightsized_cost_per_month") is not None:
            target_type = resource.get("recommended_instance_type", "menor instância")
            target_cost = float(resource["rightsized_cost_per_month"])
        elif cpu < CPU_RIGHTSIZING_THRESHOLD and current_type in RIGHTSIZED_COST_BY_TYPE:
            target_type, target_cost = RIGHTSIZED_COST_BY_TYPE[current_type]
        else:
            continue

        if cost <= target_cost:
            continue

        rightsizing.append(
            {
                "id": resource.get("id"),
                "current_type": current_type,
                "recommended_type": target_type,
                "cpu_avg": f"{cpu:.1f}%",
                "current_cost_monthly": cost,
                "rightsized_cost_monthly": target_cost,
                "savings_monthly": round(cost - target_cost, 2),
                "action": f"ModifyInstanceAttribute / stop + change type → {target_type}",
            }
        )

    zombie_total = round(sum(item["savings_monthly"] for item in zombies), 2)
    rightsizing_total = round(sum(item["savings_monthly"] for item in rightsizing), 2)
    total_savings = round(zombie_total + rightsizing_total, 2)

    return {
        "account_id": payload.get("account_id"),
        "region": payload.get("region"),
        "zombies": zombies,
        "rightsizing": rightsizing,
        "zombie_savings_monthly": zombie_total,
        "rightsizing_savings_monthly": rightsizing_total,
        "total_savings_monthly": total_savings,
    }


def _format_audit_report(audit: dict) -> str:
    lines = [
        f"Conta: {audit.get('account_id')} | Região: {audit.get('region')}",
        "",
        "=== ZUMBIS (economia = custo integral — delete/release) ===",
    ]

    if audit["zombies"]:
        for z in audit["zombies"]:
            lines.append(
                f"- {z['id']} [{z['category']}]: ${z['savings_monthly']:.2f}/mês → {z['action']}"
            )
    else:
        lines.append("- Nenhum zumbi detectado.")

    lines.append(f"Subtotal zumbis: ${audit['zombie_savings_monthly']:.2f}/mês")
    lines.append("")
    lines.append("=== RIGHTSIZING (economia = custo atual − custo após downsize) ===")

    if audit["rightsizing"]:
        for r in audit["rightsizing"]:
            lines.append(
                f"- {r['id']} {r['current_type']} (CPU {r['cpu_avg']}): "
                f"${r['current_cost_monthly']:.2f} → {r['recommended_type']} "
                f"${r['rightsized_cost_monthly']:.2f} | economia ${r['savings_monthly']:.2f}/mês"
            )
    else:
        lines.append("- Nenhum rightsizing necessário.")

    lines.append(f"Subtotal rightsizing: ${audit['rightsizing_savings_monthly']:.2f}/mês")
    lines.append("")
    lines.append(f"ECONOMIA TOTAL ESTIMADA: ${audit['total_savings_monthly']:.2f}/mês")
    lines.append(
        f"(Zumbis ${audit['zombie_savings_monthly']:.2f} + Rightsizing ${audit['rightsizing_savings_monthly']:.2f})"
    )
    return "\n".join(lines)


@tool("analyze_cloud_costs")
def analyze_cloud_costs(file_path: str) -> str:
    """
    Reads a cloud inventory JSON and returns a FinOps audit with pre-calculated savings.
    Zombies: full monthly cost recoverable. Rightsizing: current cost minus rightsized target cost.
    """
    path = Path(file_path)
    if not path.exists():
        return f"❌ File '{file_path}' not found."

    payload = json.loads(path.read_text(encoding="utf-8"))
    audit = audit_cloud_inventory(payload)
    return _format_audit_report(audit)
