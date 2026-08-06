import json
from pathlib import Path

from crewai.tools import tool

NEXUS_ROOT = Path(__file__).resolve().parent.parent

REMEDIATED_DOCKERFILE = NEXUS_ROOT / "Dockerfile.remediated"
REMEDIATED_TRIVY = NEXUS_ROOT / "data" / "trivy-remediated.json"
SOURCE_TRIVY = NEXUS_ROOT / "data" / "trivy.json"

REMEDIATED_DOCKERFILE_CONTENT = """\
# Remediated by Nexus DevSecOps — CVE-2024-3094 (liblzma5 backdoor) patched
FROM python:3.11-slim-bookworm

RUN apt-get update \\
    && apt-get install -y --no-install-recommends liblzma5 \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["python", "labs/modulo12_projeto_final.py"]
"""


def _build_remediated_trivy_report() -> dict:
    payload = json.loads(SOURCE_TRIVY.read_text(encoding="utf-8"))
    payload["ArtifactName"] = "nexus-api:remediated"

    for result in payload.get("Results", []):
        vulns = result.get("Vulnerabilities", [])
        result["Vulnerabilities"] = [
            v for v in vulns if v.get("VulnerabilityID") != "CVE-2024-3094"
        ]

    return payload


def _summarize_trivy(payload: dict) -> str:
    """Compact Trivy summary to keep Groq TPM usage low."""
    lines = [f"Artifact: {payload.get('ArtifactName', 'unknown')}"]
    for result in payload.get("Results", []):
        target = result.get("Target", "?")
        for vuln in result.get("Vulnerabilities", []):
            fixed = vuln.get("FixedVersion") or "n/a"
            title = (vuln.get("Title") or "")[:100]
            lines.append(
                f"- {vuln.get('VulnerabilityID')} | {vuln.get('Severity')} | "
                f"{target}/{vuln.get('PkgName')} {vuln.get('InstalledVersion')} "
                f"-> fix {fixed} | {title}"
            )
    if len(lines) == 1:
        lines.append("- Nenhuma vulnerabilidade encontrada.")
    return "\n".join(lines)


@tool("read_trivy_report")
def read_trivy_report(file_path: str) -> str:
    """Reads a Trivy JSON report and returns a compact summary of CVE findings."""
    path = Path(file_path)
    if not path.exists():
        return f"❌ File '{file_path}' not found."
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _summarize_trivy(payload)


@tool("apply_cve_remediation")
def apply_cve_remediation(cve_id: str, output_dockerfile: str = "Dockerfile.remediated") -> str:
    """
    Applies a deterministic remediation playbook for a known CVE.
    Writes the patched Dockerfile and a post-fix Trivy report without the resolved CVE.
    """
    normalized = (cve_id or "").strip().upper()
    if normalized != "CVE-2024-3094":
        return (
            f"❌ Playbook de remediação indisponível para '{cve_id}'. "
            "Suportado neste lab: CVE-2024-3094 (backdoor liblzma5)."
        )

    dockerfile_path = NEXUS_ROOT / output_dockerfile
    dockerfile_path.write_text(REMEDIATED_DOCKERFILE_CONTENT, encoding="utf-8")

    remediated_report = _build_remediated_trivy_report()
    REMEDIATED_TRIVY.write_text(
        json.dumps(remediated_report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    remaining = sum(
        len(r.get("Vulnerabilities", [])) for r in remediated_report.get("Results", [])
    )

    return (
        "✅ REMEDIATION APPLIED — CVE-2024-3094\n"
        f"- Dockerfile: {dockerfile_path.name} (base bookworm + liblzma5 atualizado)\n"
        f"- Re-scan simulado: {REMEDIATED_TRIVY.relative_to(NEXUS_ROOT).as_posix()}\n"
        f"- CVEs restantes no relatório: {remaining} (P0 removida)\n"
        "- Próximo passo CI: docker build -f Dockerfile.remediated -t nexus-api:remediated ."
    )
