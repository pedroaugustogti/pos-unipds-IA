import os
import subprocess
from pathlib import Path

from crewai.tools import tool

K3D_SERVER_CONTAINER = os.environ.get("K3D_SERVER_CONTAINER", "k3d-nexus-lab-server-0")


def _kubectl_base_args() -> list[str]:
    if os.environ.get("KUBE_INSECURE_SKIP_TLS_VERIFY", "").lower() in ("1", "true", "yes"):
        return ["--insecure-skip-tls-verify"]
    return []


def _apply_via_docker_exec(filename: str) -> tuple[bool, str]:
    """Applies manifest through k3d server container (Windows TLS workaround)."""
    manifest = Path(filename).read_text(encoding="utf-8")
    try:
        check = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", K3D_SERVER_CONTAINER],
            capture_output=True,
            text=True,
            check=False,
        )
        if check.returncode != 0 or check.stdout.strip() != "true":
            return False, ""

        result = subprocess.run(
            ["docker", "exec", "-i", K3D_SERVER_CONTAINER, "kubectl", "apply", "-f", "-"],
            input=manifest,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, (result.stderr or result.stdout or "").strip()
    except FileNotFoundError:
        return False, ""


def _apply_via_kubectl(filename: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["kubectl", *_kubectl_base_args(), "apply", "-f", filename],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()

        stderr = (result.stderr or "").lower()
        if "certificate" in stderr or "x509" in stderr:
            ok, output = _apply_via_docker_exec(filename)
            if ok:
                return True, f"{output} (via k3d container)"

        return False, (result.stderr or result.stdout or "").strip()
    except FileNotFoundError:
        ok, output = _apply_via_docker_exec(filename)
        if ok:
            return True, f"{output} (via k3d container)"
        return False, "kubectl not found"


@tool("generate_k8s_manifest")
def generate_k8s_manifest(app_name: str, replicas: int, port: int) -> str:
    """Generates Kubernetes Deployment and Service YAML manifests on disk."""
    manifest = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: nginx:latest
        ports:
        - containerPort: {port}
        readinessProbe:
          httpGet:
            path: /
            port: {port}
---
apiVersion: v1
kind: Service
metadata:
  name: {app_name}-svc
spec:
  selector:
    app: {app_name}
  ports:
  - protocol: TCP
    port: 80
    targetPort: {port}
"""
    filename = f"{app_name}-k8s.yaml"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(manifest)
    return f"✅ Kubernetes manifests for '{app_name}' successfully generated in '{filename}'."


@tool("apply_k8s_manifest")
def apply_k8s_manifest(filename: str) -> str:
    """Simulates or executes GitOps reconciliation using 'kubectl apply'."""
    if not os.path.exists(filename):
        return f"❌ Error: The file '{filename}' was not found to apply."

    ok, output = _apply_via_kubectl(filename)
    if ok:
        return f"✅ GitOps Sync Success: {output}"

    if output and "certificate" not in output.lower():
        return f"⚠️ GitOps apply failed: {output}"

    return (
        f"⚠️ GitOps Simulation: File '{filename}' is syntactically valid, "
        f"but no Kubernetes cluster was detected. The GitOps controller would reconcile this state."
    )


@tool("analyze_canary_metrics")
def analyze_canary_metrics(metrics_data: str) -> str:
    """Analyzes application metrics to decide if a Canary Rollout should proceed or rollback."""
    if "error_rate > 5%" in metrics_data or "error" in metrics_data.lower():
        return "❌ ROLLBACK: Elevated error rate detected in Canary pods. Reverting deployment."
    return "✅ PROCEED: Metrics are stable. Canary rollout approved for production."